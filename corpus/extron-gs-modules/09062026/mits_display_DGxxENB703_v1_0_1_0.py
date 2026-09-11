from extronlib.interface import SerialInterface, EthernetClientInterface
import re
eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'Mute': {'Status': {}},
            'MuteStatus': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
            'TouchControl': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#\*Picture zoommode is (auto|16:9|subtitle|14:9|14:9zoom|4:3|full|panaromic|cinema)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'#\*source is ([^^]+?)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'#\*MUTE (ON|OFF)\r\n'), self.__MatchMuteStatus, None)
            self.AddMatchString(re.compile(b'#\*Panel Lock is (ON|OFF)\r\n'), self.__MatchPanelLock, None)
            self.AddMatchString(re.compile(b'#\*standby (on|off)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'#\*remote state is (on|off)\r\n'), self.__MatchRemoteControlLock, None)
            self.AddMatchString(re.compile(b'#\*Touch control is (on|off)\r\n'), self.__MatchTouchControl, None)
            self.AddMatchString(re.compile(b'#\*video is (on|off)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'#\*volume level is ([0-9]{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'#\*NACK\r\n'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Auto': 'auto',
            '16:9': '16:9',
            'Subtitle': 'subtitle',
            '14:9': '14:9',
            '14:9 Zoom': '14:9zoom',
            '4:3': '4:3',
            'Full': 'full',
            'Panaromic': 'panaromic',
            'Cinema': 'cinema'
        }

        AspectRatioCmdString = 'PICTUREZOOM {0}\r\n'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'GETPICTUREZOOM\r\n'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            'auto': 'Auto',
            '16:9': '16:9',
            'subtitle': 'Subtitle',
            '14:9': '14:9',
            '14:9zoom': '14:9 Zoom',
            '4:3': '4:3',
            'full': 'Full',
            'panaromic': 'Panaromic',
            'cinema': 'Cinema'
        }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE\r\n'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'TV': '0',
            'SCART 1 (CVBS)': '1',
            'SCART 2 (CVBS)': '3',
            'FAV': '5',
            'S-Video': '6',
            'HDMI 1': '7',
            'HDMI 2': '8',
            'HDMI 3': '9',
            'HDMI 4': '10',
            'YPbPr': '11',
            'PC': '12',
            'SCART 1 (S-Video)': '16',
            'SCART 2 (S-Video)': '13',
            'DVD': '17',
            'DVI': '18',
            'DP': '19',
            'OPS': '20',
            'WIDI': '21'
        }

        InputCmdString = 'SELECTSOURCE {0}\r\n'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GETSOURCE\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            'TV': 'TV',
            'SCART 1 (CVBS)': 'SCART 1 (CVBS)',
            'SCART 2 (CVBS)': 'SCART 2 (CVBS)',
            'FAV': 'FAV',
            'S-Video': 'S-Video',
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'HDMI 4': 'HDMI 4',
            'YPbPr': 'YPbPr',
            'PC': 'PC',
            'SCART 1 (S-Video)': 'SCART 1 (S-Video)',
            'SCART 2 (S-Video)': 'SCART 2 (S-Video)',
            'DVD': 'DVD',
            'DVI': 'DVI',
            'DP': 'DP',
            'OPS': 'OPS',
            'WIDI': 'WIDI'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = 'KEY {0}\r\n'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMute(self, value, qualifier):

        MuteCmdString = 'SETMUTE\r\n'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMuteStatus(self, value, qualifier):

        MuteStatusCmdString = 'GETMUTE\r\n'
        self.__UpdateHelper('MuteStatus', MuteStatusCmdString, value, qualifier)

    def __MatchMuteStatus(self, match, tag):

        MuteState = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = MuteState[match.group(1).decode()]
        self.WriteStatus('MuteStatus', value, None)

    def SetPanelLock(self, value, qualifier):

        PanelLockState = {
            'On': 'ON',
            'Off': 'OFF'
        }

        PanelLockCmdString = 'SETPANELLOCK {0}\r\n'.format(PanelLockState[value])
        self.__SetHelper('PanelLock', PanelLockCmdString, value, qualifier)

    def UpdatePanelLock(self, value, qualifier):

        PanelLockCmdString = 'GETPANELLOCK\r\n'
        self.__UpdateHelper('PanelLock', PanelLockCmdString, value, qualifier)

    def __MatchPanelLock(self, match, tag):

        PanelLockState = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = PanelLockState[match.group(1).decode()]
        self.WriteStatus('PanelLock', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'TON 0\r\n',  # Set Volume to 0 upon powering on. Refer to pg 3
            'Off': 'TOF\r\n'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GETSTANDBY\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            'on': 'On',
            'off': 'Off'
        }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRemoteControlLock(self, value, qualifier):

        RemoteControlState = {
            'On': 'ON',
            'Off': 'OFF'
        }

        RemoteControlLockCmdString = 'SETRC {0}\r\n'.format(RemoteControlState[value])
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def UpdateRemoteControlLock(self, value, qualifier):

        RemoteControlLockCmdString = 'GETRC\r\n'
        self.__UpdateHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def __MatchRemoteControlLock(self, match, tag):

        RemoteControlState = {
            'on': 'On',
            'off': 'Off'
        }

        value = RemoteControlState[match.group(1).decode()]
        self.WriteStatus('RemoteControlLock', value, None)

    def SetTouchControl(self, value, qualifier):

        TouchControlState = {
            'On': 'on',
            'Off': 'off'
        }

        TouchControlCmdString = 'SETTOUCHCONTROL {0}\r\n'.format(TouchControlState[value])
        self.__SetHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def UpdateTouchControl(self, value, qualifier):

        TouchControlCmdString = 'GETTOUCHCONTROL\r\n'
        self.__UpdateHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def __MatchTouchControl(self, match, tag):

        TouchControlState = {
            'on': 'On',
            'off': 'Off'
        }

        value = TouchControlState[match.group(1).decode()]
        self.WriteStatus('TouchControl', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': 'VIDON\r\n',
            'Off': 'VIDOFF\r\n'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'GETVIDSTATE\r\n'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            'on': 'On',
            'off': 'Off'
        }

        value = VideoMuteState[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'STV {0}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GETVOLUME\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

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

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Error: NACK, Invalid Command.'])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
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

