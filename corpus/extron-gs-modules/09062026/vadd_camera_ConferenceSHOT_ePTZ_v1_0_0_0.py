from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.devicePassword = ''
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'Autoframing': {'Status': {}},
            'AutoframingPause': {'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)

    def __MatchLogin(self, match, tag):

        self.Send('admin\r\n')
        self.Send(self.devicePassword + '\r\n')

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'Internal Mic': 'internal_mic',
            'Line In': 'line_in',
            'USB Playback': 'usb_playback',
            'Line Out': 'line_out',
            'HDMI Out': 'hdmi_out',
            'IP Stream': 'ip_out',
            'USB Record': 'usb_record'
        }

        channel = qualifier['Channel']

        ValueStateValues = [
            'On',
            'Off'
        ]

        if channel in ChannelStates and value in ValueStateValues:
            AudioMuteCmdString = 'audio {} mute {}\r\n'.format(ChannelStates[channel], value.lower())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Internal Mic': 'internal_mic',
            'Line In': 'line_in',
            'USB Playback': 'usb_playback',
            'Line Out': 'line_out',
            'HDMI Out': 'hdmi_out',
            'IP Stream': 'ip_out',
            'USB Record': 'usb_record'
        }

        channel = qualifier['Channel']

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        if channel in ChannelStates:
            AudioMuteCmdString = 'audio {} mute get\r\n'.format(ChannelStates[channel])
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.strip().split()[-1]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAutoframing(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            AutoframingCmdString = 'autoframer enabled {}\r\n'.format(value.lower())
            self.__SetHelper('Autoframing', AutoframingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframing')

    def UpdateAutoframing(self, value, qualifier):

        ValueStateValues = {
            'true': 'On',
            'false': 'Off'
        }

        AutoframingCmdString = 'autoframer enabled get\r\n'
        res = self.__UpdateHelper('Autoframing', AutoframingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res.strip().split()[-1], 'On')
                self.WriteStatus('Autoframing', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Autoframing: Invalid/unexpected response'])

    def SetAutoframingPause(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            AutoframingPauseCmdString = 'autoframer paused {}\r\n'.format(value.lower())
            self.__SetHelper('AutoframingPause', AutoframingPauseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframingPause')

    def UpdateAutoframingPause(self, value, qualifier):

        ValueStateValues = {
            'true': 'On',
            'false': 'Off'
        }

        AutoframingPauseCmdString = 'autoframer paused get\r\n'
        res = self.__UpdateHelper('AutoframingPause', AutoframingPauseCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res.strip().split()[-1], 'Off')
                self.WriteStatus('AutoframingPause', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Autoframing Pause: Invalid/unexpected response'])

    def SetPan(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'Left',
            'Right',
            'Stop'
        ]

        if 1 <= speed <= 20 and value in ValueStateValues:
            if value != 'Stop':
                PanCmdString = 'camera pan {} {} no_wait\r\n'.format(value.lower(), speed)
            else:
                PanCmdString = 'camera pan stop\r\n'

            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'off',
            'Off': 'on'
        }

        if value in ValueStateValues:
            PowerCmdString = 'camera standby {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'off': 'On',
            'on': 'Off'
        }

        PowerCmdString = 'camera standby get\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split()[-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 'store',
            'Recall': 'recall'
        }

        action = qualifier['Action']

        if action in ActionStates and 1 <= value <= 16:
            PresetCmdString = 'camera preset {} {}\r\n'.format(ActionStates[action], value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTilt(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'Up',
            'Down',
            'Stop'
        ]

        if 1 <= speed <= 20 and value in ValueStateValues:
            if value != 'Stop':
                TiltCmdString = 'camera tilt {} {} no_wait\r\n'.format(value.lower(), speed)
            else:
                TiltCmdString = 'camera tilt stop\r\n'

            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            VideoMuteCmdString = 'video mute {}\r\n'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        VideoMuteCmdString = 'video mute get\r\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split()[-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ChannelStates = {
            'Internal Mic': 'internal_mic',
            'Line In': 'line_in',
            'USB Playback': 'usb_playback',
            'Line Out': 'line_out',
            'HDMI Out': 'hdmi_out',
            'IP Stream': 'ip_out',
            'USB Record': 'usb_record'
        }

        channel = qualifier['Channel']

        ValueStateValues = [
            'Up',
            'Down'
        ]

        if channel in ChannelStates and value in ValueStateValues:
            VolumeCmdString = 'audio {} volume {}\r\n'.format(ChannelStates[channel], value.lower())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def SetZoom(self, value, qualifier):

        speed = qualifier['Speed']

        ValueStateValues = [
            'In',
            'Out',
            'Stop'
        ]

        if 1 <= speed <= 7 and value in ValueStateValues:
            if value != 'Stop':
                ZoomCmdString = 'camera zoom {} {}\r\n'.format(value.lower(), speed)
            else:
                ZoomCmdString = 'camera zoom stop\r\n'

            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'login' in response:
            self.__MatchLogin(None, None)
            return ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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