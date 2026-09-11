from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.AudioMuteRegex = re.compile('\nmute=(on|off)\r\n>')
        self.FreezeRegex = re.compile('\nvideofreeze=(on|off)\r\n>')
        self.InputRegex = re.compile('\ninput=(hdmi1|hdmi2|hdmi3|vga|ops|usbc1|usbc2|dp|android|type-c1|type-c2)\r\n>')
        self.PowerRegex = re.compile('\npowerstate=(on|ready|powersave)\r\n>')
        self.VideoMuteRegex = re.compile('\nscreenshade=(on|off)\r\n>')
        self.VolumeRegex = re.compile('\nvolume=([0-9]{1,2}|100)\r\n>')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
            }

        if value in ValueStateValues:
            AudioMuteCmdString = 'set mute={}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'get mute\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'on': 'On',
                    'off': 'Off'
                    }

                valueMatch = self.AudioMuteRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
            }

        if value in ValueStateValues:
            FreezeCmdString = 'set videofreeze={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'get videofreeze\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'on': 'On',
                    'off': 'Off'
                    }

                valueMatch = self.FreezeRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'hdmi1',
            'HDMI 2': 'hdmi2',
            'HDMI 3': 'hdmi3',
            'VGA': 'vga',
            'OPS': 'ops',
            'USB-C 1': 'usbc1',
            'USB-C 2': 'usbc2',
            'DisplayPort': 'dp',
            'Android': 'android'
            }

        if value in ValueStateValues:
            InputCmdString = 'set input={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'get input\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'hdmi1': 'HDMI 1',
                    'hdmi2': 'HDMI 2',
                    'hdmi3': 'HDMI 3',
                    'vga': 'VGA',
                    'ops': 'OPS',
                    'usbc1': 'USB-C 1',
                    'usbc2': 'USB-C 2',
                    'type-c1': 'USB-C 1',
                    'type-c2': 'USB-C 2',
                    'dp': 'DisplayPort',
                    'android': 'Android'
                    }

                valueMatch = self.InputRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Ready': 'ready',
            'Off': 'powersave'
            }

        if value in ValueStateValues:
            PowerCmdString = 'set powerstate={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'get powerstate\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'on': 'On',
                    'ready': 'Ready',
                    'powersave': 'Off'
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
            }

        if value in ValueStateValues:
            VideoMuteCmdString = 'set screenshade={}\r'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'get screenshade\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'on': 'On',
                    'off': 'Off'
                    }

                valueMatch = self.VideoMuteRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'set volume={}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.VolumeRegex.match(res)
                value = int(valueMatch.group(1))
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'invalid cmd:' in response:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, response.strip())])
            return ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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