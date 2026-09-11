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
            'AudioLevel': {'Parameters': ['Direction', 'Port Type', 'Port Number', 'Channel Number'], 'Status': {}},
            'AudioMute': {'Parameters': ['Direction', 'Port Type', 'Port Number', 'Channel Number'], 'Status': {}},
            'DSPPostLevel': {'Parameters': ['Port Type', 'Port Number'], 'Status': {}},
            'DSPPostMute': {'Parameters': ['Port Type', 'Port Number'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Route': {'Parameters': ['Input Port Type', 'Input Port Number', 'Input Signal Type', 'Input Channel Number', 'Output Port Type', 'Output Port Number', 'Output Signal Type', 'Output Channel Number'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            direction = b'(IN|OUT)'
            port = b'(HDMI_AUDIO|ANALOG_(?:AUDIO|STEREO)|USB_B|GENERATOR)'
            var_part1 = br'\.'.join([direction, port, b'([1-5])', b'AUDIO', b'([12])'])
            range_part1 = br',(-(?:60|[3-5]\d)|-?(?:30|[12]\d|\d))'
            self.AddMatchString(re.compile(b''.join([b'~.*?@X-AUD-LVL ', var_part1, range_part1, b'\r\n'])), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b''.join([b'~.*?@X-MUTE ', var_part1, b',(ON|OFF)\r\n']), re.I), self.__MatchAudioMute, None)
            var_part2 = br'\.'.join([b'IN', b'(ANALOG_(?:AUDIO|STEREO)|USB_B)', b'([1-5])', b'AUDIO', b'1'])
            range_part2 = br',(-(?:100|[1-9]\d?)|1[0-5]|\d)'
            self.AddMatchString(re.compile(b''.join([b'~.*?@DSP-POST level,', var_part2, range_part2, b'\r\n'])), self.__MatchDSPPostLevel, None)
            self.AddMatchString(re.compile(b''.join([b'~.*?@DSP-POST mute,', var_part2, b',([01])\r\n'])), self.__MatchDSPPostMute, None)
            self.AddMatchString(re.compile(br'~.*?@VERSION ([\d.]{5,}?)\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(br'~.*?@ERR (\d+)\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(br'~.*?@\S+ ERR (\d+)\r'), self.__MatchError, None)

    def SetAudioLevel(self, value, qualifier):

        DirectionStates = ('In', 'Out')

        PortTypeStates = {
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
            'Generator':     'GENERATOR',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ChannelNumberStates = ('1', '2')

        ValueConstraints = {
            'Min': -60,
            'Max': 30,
        }

        direction = qualifier['Direction']
        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        channel_number = qualifier['Channel Number']
        if (direction in DirectionStates and port_type in PortTypeStates and port_number in PortNumberStates and
                channel_number in ChannelNumberStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            AudioLevelCmdString = '#X-AUD-LVL {}.{}.{}.AUDIO.{},{}\r'.format(direction.upper(),
                                                                             PortTypeStates[port_type],
                                                                             port_number, channel_number, value)
            self.__SetHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioLevel')

    def UpdateAudioLevel(self, value, qualifier):

        DirectionStates = ('In', 'Out')

        PortTypeStates = {
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
            'Generator':     'GENERATOR',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ChannelNumberStates = ('1', '2')

        direction = qualifier['Direction']
        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        channel_number = qualifier['Channel Number']
        if (direction in DirectionStates and port_type in PortTypeStates and port_number in PortNumberStates and
                channel_number in ChannelNumberStates):
            AudioLevelCmdString = '#X-AUD-LVL? {}.{}.{}.AUDIO.{}\r'.format(direction.upper(), PortTypeStates[port_type],
                                                                           port_number, channel_number)
            self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioLevel')

    def __MatchAudioLevel(self, match, tag):

        PortTypeStates = {
            'HDMI_AUDIO':    'HDMI Audio',
            'ANALOG_AUDIO':  'Analog Audio',
            'ANALOG_STEREO': 'Analog Stereo',
            'USB_B':         'USB-B',
            'GENERATOR':     'Generator',
        }

        qualifier = {
            'Direction': match.group(1).decode().title(),
            'Port Type': PortTypeStates[match.group(2).decode()],
            'Port Number': match.group(3).decode(),
            'Channel Number': match.group(4).decode(),
        }
        value = int(match.group(5).decode())
        self.WriteStatus('AudioLevel', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        DirectionStates = ('In', 'Out')

        PortTypeStates = {
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
            'Generator':     'GENERATOR',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ChannelNumberStates = ('1', '2')

        ValueStateValues = ('On', 'Off')

        direction = qualifier['Direction']
        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        channel_number = qualifier['Channel Number']
        if (direction in DirectionStates and port_type in PortTypeStates and port_number in PortNumberStates and
                channel_number in ChannelNumberStates and value in ValueStateValues):
            AudioMuteCmdString = '#X-MUTE {}.{}.{}.AUDIO.{},{}\r'.format(direction.upper(), PortTypeStates[port_type],
                                                                         port_number, channel_number, value.upper())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        DirectionStates = ('In', 'Out')

        PortTypeStates = {
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
            'Generator':     'GENERATOR',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ChannelNumberStates = ('1', '2')

        direction = qualifier['Direction']
        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        channel_number = qualifier['Channel Number']
        if (direction in DirectionStates and port_type in PortTypeStates and port_number in PortNumberStates and
                channel_number in ChannelNumberStates):
            AudioMuteCmdString = '#X-MUTE? {}.{}.{}.AUDIO.{}\r'.format(direction.upper(), PortTypeStates[port_type],
                                                                       port_number, channel_number)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        PortTypeStates = {
            'HDMI_AUDIO':    'HDMI Audio',
            'ANALOG_AUDIO':  'Analog Audio',
            'ANALOG_STEREO': 'Analog Stereo',
            'USB_B':         'USB-B',
            'GENERATOR':     'Generator',
        }

        qualifier = {
            'Direction': match.group(1).decode().title(),
            'Port Type': PortTypeStates[match.group(2).decode()],
            'Port Number': match.group(3).decode(),
            'Channel Number': match.group(4).decode(),
        }
        value = match.group(5).decode().title()
        self.WriteStatus('AudioMute', value, qualifier)

    def SetDSPPostLevel(self, value, qualifier):

        PortTypeStates = {
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ValueConstraints = {
            'Min': -100,
            'Max': 15,
        }

        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        if (port_type in PortTypeStates and port_number in PortNumberStates and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            DSPPostLevelCmdString = '#DSP-POST level,IN.{}.{}.AUDIO.1,{}\r'.format(PortTypeStates[port_type],
                                                                                   port_number, value)
            self.__SetHelper('DSPPostLevel', DSPPostLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDSPPostLevel')

    def UpdateDSPPostLevel(self, value, qualifier):

        PortTypeStates = {
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        if port_type in PortTypeStates and port_number in PortNumberStates:
            DSPPostLevelCmdString = '#DSP-POST? level,IN.{}.{}.AUDIO.1\r'.format(PortTypeStates[port_type], port_number)
            self.__UpdateHelper('DSPPostLevel', DSPPostLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDSPPostLevel')

    def __MatchDSPPostLevel(self, match, tag):

        PortTypeStates = {
            'ANALOG_AUDIO':  'Analog Audio',
            'ANALOG_STEREO': 'Analog Stereo',
            'USB_B':         'USB-B',
        }

        qualifier = {
            'Port Type': PortTypeStates[match.group(1).decode()],
            'Port Number': match.group(2).decode(),
        }
        value = int(match.group(3).decode())
        self.WriteStatus('DSPPostLevel', value, qualifier)

    def SetDSPPostMute(self, value, qualifier):

        PortTypeStates = {
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        if port_type in PortTypeStates and port_number in PortNumberStates and value in ValueStateValues:
            DSPPostMuteCmdString = '#DSP-POST mute,IN.{}.{}.AUDIO.1,{}\r'.format(PortTypeStates[port_type],
                                                                                 port_number, ValueStateValues[value])
            self.__SetHelper('DSPPostMute', DSPPostMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDSPPostMute')

    def UpdateDSPPostMute(self, value, qualifier):

        PortTypeStates = {
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
        }

        PortNumberStates = ('1', '2', '3', '4', '5')

        port_type = qualifier['Port Type']
        port_number = qualifier['Port Number']
        if port_type in PortTypeStates and port_number in PortNumberStates:
            DSPPostMuteCmdString = '#DSP-POST? mute,IN.{}.{}.AUDIO.1\r'.format(PortTypeStates[port_type], port_number)
            self.__UpdateHelper('DSPPostMute', DSPPostMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDSPPostMute')

    def __MatchDSPPostMute(self, match, tag):

        PortTypeStates = {
            'ANALOG_AUDIO':  'Analog Audio',
            'ANALOG_STEREO': 'Analog Stereo',
            'USB_B':         'USB-B',
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = {
            'Port Type': PortTypeStates[match.group(1).decode()],
            'Port Number': match.group(2).decode()
        }
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('DSPPostMute', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):


        FirmwareVersionCmdString = '#VERSION? \r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):


        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetRoute(self, value, qualifier):

        InputPortTypeStates = {
            'HDMI':          'HDMI',
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
            'Generator':     'GENERATOR',
        }

        InputPortNumberStates = ('1', '2', '3', '4', '5')

        SignalTypeStates = ('Audio', 'Video')

        ChannelNumberStates = ('1', '2')

        OutputPortTypeStates = {
            'HDMI':          'HDMI',
            'HDMI Audio':    'HDMI_AUDIO',
            'Analog Audio':  'ANALOG_AUDIO',
            'Analog Stereo': 'ANALOG_STEREO',
            'USB-B':         'USB_B',
        }

        OutputPortNumberStates = ('1', '2')

        input_port_type = qualifier['Input Port Type']
        input_port_number = qualifier['Input Port Number']
        input_signal_type = qualifier['Input Signal Type']
        input_channel_number = qualifier['Input Channel Number']
        output_port_type = qualifier['Output Port Type']
        output_port_number = qualifier['Output Port Number']
        output_signal_type = qualifier['Output Signal Type']
        output_channel_number = qualifier['Output Channel Number']
        if (input_port_type in InputPortTypeStates and input_port_number in InputPortNumberStates and
                input_signal_type in SignalTypeStates and input_channel_number in ChannelNumberStates and
                output_port_type in OutputPortTypeStates and output_port_number in OutputPortNumberStates and
                output_signal_type in SignalTypeStates and output_channel_number in ChannelNumberStates):
            RouteCmdString = '#X-ROUTE OUT.{}.{}.{}.{},IN.{}.{}.{}.{}\r'.format(OutputPortTypeStates[output_port_type],
                                                                                output_port_number,
                                                                                output_signal_type.upper(),
                                                                                output_channel_number,
                                                                                InputPortTypeStates[input_port_type],
                                                                                input_port_number,
                                                                                input_signal_type.upper(),
                                                                                input_channel_number)
            self.__SetHelper('Route', RouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoute')

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

        error_map = {
            '0': 'P3K_NO_ERROR',
            '1': 'ERR_PROTOCOL_SYNTAX',
            '2': 'ERR_COMMAND_NOT_AVAILABLE',
            '3': 'ERR_PARAMETER_OUT_OF_RANGE',
            '4': 'ERR_UNAUTHORIZED_ACCESS',
            '5': 'ERR_INTERNAL_FW_ERROR',
            '6': 'ERR_BUSY',
            '7': 'ERR_WRONG_CRC',
            '8': 'ERR_TIMEDOUT',
            '9': 'ERR_RESERVED',
            '10': 'ERR_FW_NOT_ENOUGH_SPACE',
            '11': 'ERR_FS_NOT_ENOUGH_SPACE',
            '12': 'ERR_FS_FILE_NOT_EXISTS',
            '13': 'ERR_FS_FILE_CANT_CREATED',
            '14': 'ERR_FS_FILE_CANT_OPEN',
            '15': 'ERR_FEATURE_NOT_SUPPORTED',
            '16': 'ERR_RESERVED_2',
            '17': 'ERR_RESERVED_3',
            '18': 'ERR_RESERVED_4',
            '19': 'ERR_RESERVED_5',
            '20': 'ERR_RESERVED_6',
            '21': 'ERR_PACKET_CRC',
            '22': 'ERR_PACKET_MISSED',
            '23': 'ERR_PACKET_SIZE',
            '24': 'ERR_RESERVED_7',
            '25': 'ERR_RESERVED_8',
            '26': 'ERR_RESERVED_9',
            '27': 'ERR_RESERVED_10',
            '28': 'ERR_RESERVED_11',
            '29': 'ERR_RESERVED_12',
            '30': 'ERR_EDID_CORRUPTED',
            '31': 'ERR_NON_LISTED',
            '32': 'ERR_SAME_CRC',
            '33': 'ERR_WRONG_MODE',
            '34': 'ERR_NOT_CONFIGURED'
        }
        code = match.group(1).decode().lstrip('0')
        self.Error(['An error occurred: {}.'.format(error_map.get(code, 'Unknown Error: {}'.format(code)))])

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