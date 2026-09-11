from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PlaybackStatus': { 'Status': {}},
            'Power': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone2Mute': { 'Status': {}},
            'Zone2Power': { 'Status': {}},
            'Zone2Volume': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x21\x01\x1D\x00\x01([\x01-\x06\x08\x09\x0B\x0C\x0E\x10-\x12])\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x21\x01\x0E\x00\x01([\x00\x01])\x0D'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\x21\x01\x1C\x00\x01([\x00-\x03])'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(re.compile(b'\x21\x01\x00\x00\x01([\x00\x01])\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x21\x01\x0D\x00\x01([\x00-\x63])\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x21\x02\x1D\x00\x01([\x00-\x06\x08\x0B\x0C\x0E\x10-\x12])\x0D'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'\x21\x02\x0E\x00\x01([\x00\x01])\x0D'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'\x21\x02\x00\x00\x01([\x00\x01])\x0D'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'\x21\x02\x0D\x00\x01([\x00-\x63])\x0D'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'\x21([\x01\x02])([\x00\x08\x0D\x0E\x1C\x1D])([\x82-\x86])'), self.__MatchError, None)

    def __CommandBuilder(self, zone, cmd, data_len, data):

        command_string = [0x21, zone, cmd, data_len] + data + [0x0D]
        return bytes(command_string)
    
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CD'         : 0x76,
            'BD'         : 0x62,
            'AV'         : 0x5E,
            'SAT'        : 0x1B,
            'PVR'        : 0x60,
            'UHD'        : 0x7D,
            'AUX'        : 0x63,
            'Display'    : 0x3A,
            'Tuner (FM)' : 0x1C,
            'Tuner (DAB)': 0x48,
            'NET'        : 0x5C,
            'STB'        : 0x64,
            'Game'       : 0x61,
            'BT'         : 0x7A
        }

        if value in ValueStateValues:
            InputCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, ValueStateValues[value]])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.__CommandBuilder(zone=0x01, cmd=0x1D, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            0x01: 'CD',
            0x02: 'BD',
            0x03: 'AV',
            0x04: 'SAT',
            0x05: 'PVR',
            0x06: 'UHD',
            0x08: 'AUX',
            0x09: 'Display',
            0x0B: 'Tuner (FM)',
            0x0C: 'Tuner (DAB)',
            0x0E: 'NET',
            0x10: 'STB',
            0x11: 'Game',
            0x12: 'BT'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, int(value)])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu' : 0x52,
            'Up'   : 0x56,
            'Down' : 0x55,
            'Left' : 0x51,
            'Right': 0x50,
            'Ok'   : 0x57,
            'Home' : 0x2B
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, ValueStateValues[value]])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x1A,
            'Off': 0x78
        }

        if value in ValueStateValues:
            MuteCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, ValueStateValues[value]])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = self.__CommandBuilder(zone=0x01, cmd=0x0E, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Mute', value, None)

    def UpdatePlaybackStatus(self, value, qualifier):

        PlaybackStatusCmdString = self.__CommandBuilder(zone=0x01, cmd=0x1C, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):

        ValueStateValues = {
            0x00: 'Stopped',
            0x01: 'Transitioning',
            0x02: 'Playing',
            0x03: 'Paused'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('PlaybackStatus', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x7B,
            'Off': 0x7C
        }

        if value in ValueStateValues:
            PowerCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, ValueStateValues[value]])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = self.__CommandBuilder(zone=0x01, cmd=0x00, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Power', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'        : 0x35,
            'Pause'       : 0x30,
            'Stop'        : 0x36,
            'Rewind'      : 0x79,
            'Fast Forward': 0x34,
            'Skip Back'   : 0x21,
            'Skip Forward': 0x0B,
            'Eject'       : 0x0C,
            'Record'      : 0x5A
        }

        if value in ValueStateValues:
            TransportCmdString = self.__CommandBuilder(zone=0x01, cmd=0x08, data_len=0x02, data=[0x10, ValueStateValues[value]])
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 99:
            VolumeCmdString = self.__CommandBuilder(zone=0x01, cmd=0x0D, data_len=0x01, data=[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.__CommandBuilder(zone=0x01, cmd=0x0D, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):


        ValueStateValues = {
            'Follow Zone 1': [0x10, 0x14],
            'CD'           : [0x17, 0x06],
            'BD'           : [0x17, 0x07],
            'AV'           : [0x17, 0x09],
            'SAT'          : [0x17, 0x14],
            'PVR'          : [0x17, 0x0F],
            'UHD'          : [0x17, 0x17],
            'AUX'          : [0x17, 0x0D],
            'Tuner (FM)'   : [0x17, 0x0E],
            'Tuner (DAB)'  : [0x17, 0x10],
            'NET'          : [0x17, 0x13],
            'STB'          : [0x17, 0x08],
            'Game'         : [0x17, 0x0B],
            'BT'           : [0x17, 0x16]
        }

        if value in ValueStateValues:
            Zone2InputCmdString = self.__CommandBuilder(zone=0x02, cmd=0x08, data_len=0x02, data=ValueStateValues[value])
            self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Input')

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = self.__CommandBuilder(zone=0x02, cmd=0x1D, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            0x00: 'Follow Zone 1',
            0x01: 'CD',
            0x02: 'BD',
            0x03: 'AV',
            0x04: 'SAT',
            0x05: 'PVR',
            0x06: 'UHD',
            0x08: 'AUX',
            0x0B: 'Tuner (FM)',
            0x0C: 'Tuner (DAB)',
            0x0E: 'NET',
            0x10: 'STB',
            0x11: 'Game',
            0x12: 'BT'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x04,
            'Off': 0x05
        }

        if value in ValueStateValues:
            Zone2MuteCmdString = self.__CommandBuilder(zone=0x02, cmd=0x08, data_len=0x02, data=[0x17, ValueStateValues[value]])
            self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Mute')

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = self.__CommandBuilder(zone=0x02, cmd=0x0E, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x7B,
            'Off': 0x7C
        }

        if value in ValueStateValues:
            Zone2PowerCmdString = self.__CommandBuilder(zone=0x02, cmd=0x08, data_len=0x02, data=[0x17, ValueStateValues[value]])
            self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Power')

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = self.__CommandBuilder(zone=0x02, cmd=0x00, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        value = ValueStateValues[ord(match.group(1))]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        if 0 <= value <= 99:
            Zone2VolumeCmdString = self.__CommandBuilder(zone=0x02, cmd=0x0D, data_len=0x01, data=[value])
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = self.__CommandBuilder(zone=0x02, cmd=0x0D, data_len=0x01, data=[0xF0])
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Zone2Volume', value, None)

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

        ZONES = {
            0x01: '',
            0x02: 'Zone 2'
        }

        COMMANDS = {
            0x00: 'Power',
            0x08: 'Input/Keypad/Menu Navigation/Mute/Power/Transport/Volume',
            0x0D: 'Volume',
            0x0E: 'Mute',
            0x1C: 'Playback Status',
            0x1D: 'Input'
        }

        ERRORS = {
            0x82: 'Zone Invalid',
            0x83: 'Command not recognised',
            0x84: 'Parameter not recognised',
            0x85: 'Command invalid at this time',
            0x86: 'Invalid data length'
        }

        self.Error(['Error - {}{}: {}.'.format(ZONES[ord(match.group(1))], COMMANDS[ord(match.group(2))], ERRORS[ord(match.group(3))])])

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
        
        #check incoming data if it matched any expected data from device module
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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