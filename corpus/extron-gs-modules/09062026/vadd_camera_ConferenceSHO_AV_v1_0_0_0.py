from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'AudioVolume': {'Parameters': ['Channel'], 'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Home': {'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'Pan': {'Parameters': ['Pan Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Tilt': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Trigger': {'Parameters': ['Index'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auto_focus:\s+(on|off)\r\n'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'iris:?\s+([0-9]|10|11)\r\n'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'auto_iris:?\s+(on|off)\r\n'), self.__MatchIrisMode, None)
            self.AddMatchString(re.compile(b'standby:\s+(on|off)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x01\xFF\xFB\x03'), self.__MatchHandshake, None)
            self.AddMatchString(re.compile(b'ERROR\r\n'), self.__MatchError, None)

    def SetHandshake(self, value, qualifier):

        self.__SetHelper('Handshake', b'\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x01\xFF\xFE\x03', None, None)

    def __MatchHandshake(self, match, tag):

        self.SetHandshake(None, None)

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')

    def SetSendUsername(self, value, qualifier):

        self.Send(self.deviceUsername + '\r\n')

    def __MatchSendUsername(self, match, tag):

        self.SetSendUsername(None, None)
        self.SetSendPassword(None, None)

    def SetAudioMute(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['Master', 'Easy Mic 1', 'Easy Mic 2', 'USB Playback', 'Line Out 1', 'USB Record', 'IP Stream'] and value in ['On', 'Off']:
            AudioMuteCmdString = 'audio {} mute set {}\r\n'.format(channel.lower().replace(' ', '_'), value.lower())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['Master', 'Easy Mic 1', 'Easy Mic 2', 'USB Playback', 'Line Out 1', 'USB Record', 'IP Stream']:
            AudioMuteCmdString = 'audio {} mute get\r\n'.format(channel.lower().replace(' ', '_'))
            res = self.__UpdateSyncHelper('AudioMute', AudioMuteCmdString, qualifier)
            if res:
                try:
                    value = re.search('mute:\s+(on|off)\r\n', res).group(1).title()
                    self.WriteStatus('AudioMute', value, qualifier)
                except (AttributeError, IndexError):
                    self.Error(['AudioMute: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAudioVolume(self, value, qualifier):

        channel = qualifier['Channel']
        state = str(float(value))
        if channel in ['Master', 'Easy Mic 1', 'Easy Mic 2', 'USB Playback', 'Line Out 1', 'USB Record', 'IP Stream']:
            AudioVolumeCmdString = 'audio {} volume set {}\r\n'.format(channel.lower().replace(' ', '_'), state[:state.index('.') + 2])
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['Master', 'Easy Mic 1', 'Easy Mic 2', 'USB Playback', 'Line Out 1', 'USB Record', 'IP Stream']:
            AudioVolumeCmdString = 'audio {} volume get\r\n'.format(channel.lower().replace(' ', '_'))
            res = self.__UpdateSyncHelper('AudioVolume', AudioVolumeCmdString, qualifier)
            if res:
                try:
                    value = round(float(re.search('volume:?\s+(\-?\d+\.?\d+) dB\r\n', res).group(1)), 1)
                    self.WriteStatus('AudioVolume', value, qualifier)
                except (AttributeError, ValueError):
                    self.Error(['AudioVolume: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateAudioVolume')

    def SetFocus(self, value, qualifier):

        focusSpd = int(qualifier['Focus Speed'])
        if 1 <= focusSpd <= 8 and value in ['Near', 'Far', 'Stop']:
            if value == 'Stop':
                FocusCmdString = 'camera focus stop\r\n'
            else:
                FocusCmdString = 'camera focus {} {}\r\n'.format(value.lower(), focusSpd)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        if value in ['Auto', 'Manual']:
            FocusModeCmdString = 'camera focus mode {}\r\n'.format(value.lower())
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        FocusModeCmdString = 'camera focus mode get\r\n'
        self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def __MatchFocusMode(self, match, tag):

        value = {
            'on': 'Auto',
            'off': 'Manual'
        }[match.group(1).decode()]

        self.WriteStatus('FocusMode', value, None)

    def SetHome(self, value, qualifier):

        self.__SetHelper('Home', 'camera home\r\n', value, qualifier)

    def SetIris(self, value, qualifier):

        if 0 <= value <= 11:
            IrisCmdString = 'camera ccu set iris {}\r\n'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = 'camera ccu get iris\r\n'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Iris', value, None)

    def SetIrisMode(self, value, qualifier):

        state = {
            'Auto': 'on',
            'Manual': 'off'
        }[value]

        IrisModeCmdString = 'camera ccu set auto_iris {}\r\n'.format(state)
        self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def UpdateIrisMode(self, value, qualifier):

        IrisModeCmdString = 'camera ccu get auto_iris\r\n'
        self.__UpdateHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def __MatchIrisMode(self, match, tag):

        value = {
            'on': 'Auto',
            'off': 'Manual'
        }[match.group(1).decode()]

        self.WriteStatus('IrisMode', value, None)

    def SetPan(self, value, qualifier):

        panSpd = int(qualifier['Pan Speed'])
        if 1 <= panSpd <= 24 and value in ['Left', 'Right', 'Stop']:
            if value == 'Stop':
                PanCmdString = 'camera pan stop\r\n'
            else:
                PanCmdString = 'camera pan {0} {1}\r\n'.format(value.lower(), panSpd)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        powerVal = {
            'On': 'off',
            'Off': 'on'
        }[value]

        PowerCmdString = 'camera standby {0}\r\n'.format(powerVal)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'camera standby get\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = {
            'off': 'On',
            'on': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Power', value, None)

    def SetRecallPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetCmdString = 'camera preset recall {0}\r\n'.format(value)
            self.__SetHelper('RecallPreset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SavePresetCmdString = 'camera preset store {0}\r\n'.format(value)
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetTilt(self, value, qualifier):

        tiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= tiltSpd <= 20 and value in ['Up', 'Down', 'Stop']:
            if value == 'Stop':
                TiltCmdString = 'camera tilt stop\r\n'
            else:
                TiltCmdString = 'camera tilt {0} {1}\r\n'.format(value.lower(), tiltSpd)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetTrigger(self, value, qualifier):

        index = int(qualifier['Index'])
        self.__SetHelper('Trigger', 'trigger {} {}\r\n'.format(index, value.lower()), value, qualifier)

    def SetVideoMute(self, value, qualifier):

        if value in ['On', 'Off']:
            VideoMuteCmdString = 'video mute {0}\r\n'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'video mute get\r\n'
        res = self.__UpdateSyncHelper('VideoMute', VideoMuteCmdString, qualifier)
        if res:
            try:
                value = re.search('mute:\s+(on|off)\r\n', res).group(1).title()
                self.WriteStatus('VideoMute', value, qualifier)
            except (AttributeError, IndexError):
                self.Error(['VideoMute: Invalid/Unexpected Response'])

    def SetZoom(self, value, qualifier):

        zoomSpd = int(qualifier['Zoom Speed'])
        if 1 <= zoomSpd <= 7 and value in ['In', 'Out', 'Stop']:
            if value == 'Stop':
                ZoomCmdString = 'camera zoom stop\r\n'
            else:
                ZoomCmdString = 'camera zoom {0} {1}\r\n'.format(value.lower(), zoomSpd)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __UpdateSyncHelper(self, command, commandstring, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if res:
                res = res.decode()
                if res == 'ERROR':
                    self.__MatchError(None, None)
                    res = ''
            return res

    def __MatchError(self, match, tag):
        self.Error(['Error'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

        

    
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)            

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

