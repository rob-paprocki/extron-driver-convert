from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog


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
            'AudioInput': {'Status': {}},
            'AudioInputGain': {'Parameters': ['Input'], 'Status': {}},
            'Channel': {'Status': {}},
            'FullScreenLayout': {'Status': {}},
            'MainInput': {'Status': {}},
            'OutputGain': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PowerOff': {'Status': {}},
            'Program': {'Status': {}},
            'Record': {'Status': {}},
            'RecordingPresenterCommand': {'Status': {}},
            'RecordingTitleCommand': {'Status': {}},
            'SwapInputs': {'Status': {}},
        }

        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*(.+)\n'), self.__MatchRequiredPolling, None)
            self.AddMatchString(re.compile(b'@NCast,002\n'), self.__MatchRequiredPolling, 'ID')
            self.AddMatchString(re.compile(b'&\n-(.+)\n'), self.__MatchError, 'Command')

            self.RequiredPollingCmdString = '?,'
            self.ConfiguredStatus = []
            self.IsConnected = False

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Mic': 'A1',
            'Line': 'A2',
            'XLR': 'A4'
        }

        AudioInputCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        if 'AudioInput' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'A'
            self.ConfiguredStatus.append('AudioInput')
        

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            'A1': 'Mic',
            'A2': 'Line',
            'A4': 'XLR'
        }

        value = match.split(':')
        input_ = ValueStateValues[value[0]]
        gain = int(value[1])

        self.WriteStatus('AudioInput', input_, None)
        self.WriteStatus('AudioInputGain', gain, {'Input': input_})

    def SetAudioInputGain(self, value, qualifier):

        InputStates = {
            'Mic': 'A1',
            'Line': 'A2',
            'XLR': 'A4'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioInputGainCmdString = '{0},{1}\n'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioInputGain')

    def UpdateAudioInputGain(self, value, qualifier):

        if 'AudioInput' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'A'
            self.ConfiguredStatus.append('AudioInput')

    def SetChannel(self, value, qualifier):

        if 1 <= int(value) <= 25:
            ChannelCmdString = 'C{0}\n'.format(value)
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        if 'Channel' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'C'
            self.ConfiguredStatus.append('Channel')

    def __MatchChannel(self, match, tag):

        ValueStateValues = {
            'C1': '1',
            'C2': '2',
            'C3': '3',
            'C4': '4',
            'C5': '5',
            'C6': '6',
            'C7': '7',
            'C8': '8',
            'C9': '9',
            'C10': '10',
            'C11': '11',
            'C12': '12',
            'C13': '13',
            'C14': '14',
            'C15': '15',
            'C16': '16',
            'C17': '17',
            'C18': '18',
            'C19': '19',
            'C20': '20',
            'C21': '21',
            'C22': '22',
            'C23': '23',
            'C24': '24',
            'C25': '25'
        }

        value = ValueStateValues[match]
        self.WriteStatus('Channel', value, None)

    def SetFullScreenLayout(self, value, qualifier):

        ValueStateValues = {
            'None': '0',
            'Main': '1',
            'PIP': '2'
        }

        FullScreenLayoutCmdString = 'f{0}\n'.format(ValueStateValues[value])
        self.__SetHelper('FullScreenLayout', FullScreenLayoutCmdString, value, qualifier)

    def UpdateFullScreenLayout(self, value, qualifier):

        if 'FullScreenLayout' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'f'
            self.ConfiguredStatus.append('FullScreenLayout')

    def __MatchFullScreenLayout(self, match, tag):

        ValueStateValues = {
            'f0': 'None',
            'f1': 'Main',
            'f2': 'PIP'
        }

        value = ValueStateValues[match]
        self.WriteStatus('FullScreenLayout', value, None)

    def SetMainInput(self, value, qualifier):

        ValueStateValues = {
            'Composite': 'G1',
            'S-Video': 'G2',
            'VGA': 'G3',
            'DVI': 'G4',
            'Auto Detect': 'G5',
            'DVI-A': 'G6',
            'HDMI': 'G7',
            'DisplayPort': 'G8',
            '3G-SDI': 'G9'
        }

        MainInputCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('MainInput', MainInputCmdString, value, qualifier)

    def UpdateMainInput(self, value, qualifier):

        if 'MainInput' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'G'
            self.ConfiguredStatus.append('MainInput')

    def __MatchMainInput(self, match, tag):

        ValueStateValues = {
            'G1': 'Composite',
            'G2': 'S-Video',
            'G3': 'VGA',
            'G4': 'DVI',
            'G5': 'Auto Detect',
            'G6': 'DVI-A',
            'G7': 'HDMI',
            'G8': 'DisplayPort',
            'G9': '3G-SDI'
        }

        value = ValueStateValues[match]
        self.WriteStatus('MainInput', value, None)

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGainCmdString = 'O0,{0}\n'.format(value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        if 'OutputGain' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'O0'
            self.ConfiguredStatus.append('OutputGain')

    def __MatchOutputGain(self, match, tag):

        value = match.split(':')
        self.WriteStatus('OutputGain', int(value[1]), None)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'On': 'p1',
            'Off': 'p0'
        }

        PIPCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        if 'PIP' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'p'
            self.ConfiguredStatus.append('PIP')

    def __MatchPIP(self, match, tag):

        ValueStateValues = {
            'p1': 'On',
            'p0': 'Off'
        }

        value = ValueStateValues[match]
        self.WriteStatus('PIP', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'Composite': 'V1',
            'S-Video': 'V2',
            'VGA': 'V3',
            'DVI': 'V4',
            'Auto Detect': 'V5',
            'DVI-A': 'V6',
            'HDMI': 'V7',
            'DisplayPort': 'V8',
            '3G-SDI': 'V9'
        }

        PIPInputCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        if 'PIPInput' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'V'
            self.ConfiguredStatus.append('PIPInput')

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            'V1': 'Composite',
            'V2': 'S-Video',
            'V3': 'VGA',
            'V4': 'DVI',
            'V5': 'Auto Detect',
            'V6': 'DVI-A',
            'V7': 'HDMI',
            'V8': 'DisplayPort',
            'V9': '3G-SDI'
        }

        value = ValueStateValues[match]
        self.WriteStatus('PIPInput', value, None)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'PS\n'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetProgram(self, value, qualifier):

        ValueStateValues = {
            'Begin': 'PB',
            'End': 'PE'
        }

        ProgramCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('Program', ProgramCmdString, value, qualifier)

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start': 'R1',
            'Stop': 'R0',
            'Pause': 'R2',
            'Continue': 'R3'
        }

        RecordCmdString = ValueStateValues[value] + '\n'
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def UpdateRecord(self, value, qualifier):

        if 'Record' not in self.ConfiguredStatus:
            self.RequiredPollingCmdString += 'r'
            self.ConfiguredStatus.append('Record')

    def __MatchRecord(self, match, tag):

        ValueStateValues = {
            'r1': 'Start',
            'r0': 'Stop',
            'r2': 'Pause'
        }

        value = ValueStateValues[match]
        self.WriteStatus('Record', value, None)

    def SetRecordingPresenterCommand(self, value, qualifier):

        presenterStr = value
        if presenterStr:
            RecordingPresenterCommandCmdString = 'RP,{0}\n'.format(presenterStr)
            self.__SetHelper('RecordingPresenterCommand', RecordingPresenterCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecordingPresenterCommand')

    def SetRecordingTitleCommand(self, value, qualifier):

        titleStr = value
        if titleStr:
            RecordingTitleCommandCmdString = 'RT,{0}\n'.format(titleStr)
            self.__SetHelper('RecordingTitleCommand', RecordingTitleCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecordingTitleCommand')

    def UpdateRequiredPolling(self, value, qualifier):

        RequiredPollingCmdString = self.RequiredPollingCmdString

        if self.IsConnected:

            if RequiredPollingCmdString == '?,':

                RequiredPollingCmdString = '?\n'
            else:

                RequiredPollingCmdString += '\n'
        else:

            if self.ConnectionType == 'Serial':
                self.Send('IdSerial,002\n')
            elif self.ConnectionType == 'Ethernet':
                if self.devicePassword is not None:
                    self.Send('IdTelnet,002,{0}\n'.format(self.devicePassword))
                else:
                    self.MissingCredentialsLog('Password')

        self.__UpdateHelper('RequiredPolling', RequiredPollingCmdString, value, qualifier)

    def __MatchRequiredPolling(self, match, tag):

        self.IsConnected = True

        if tag != 'ID':
            res = match.group(1).decode().split(',')
            for code in res:
                if code[0] == 'A':
                    self.__MatchAudioInput(code, None)
                elif code[0] == 'C':
                    self.__MatchChannel(code, None)
                elif code[0] == 'E':
                    if code != 'E:0':
                        self.__MatchError(code, None)
                elif code[0] == 'f':
                    self.__MatchFullScreenLayout(code, None)
                elif code[0] == 'G':
                    self.__MatchMainInput(code, None)
                elif code[0] == 'O':
                    if code[1] == '0':
                        self.__MatchOutputGain(code, None)
                elif code[0] == 'p':
                    self.__MatchPIP(code, None)
                elif code[0] == 'r':
                    self.__MatchRecord(code, None)
                elif code[0] == 'V':
                    if code[1] != ':':
                        self.__MatchPIPInput(code, None)

    def SetSwapInputs(self, value, qualifier):

        SwapInputsCmdString = 'SW\n'
        self.__SetHelper('SwapInputs', SwapInputsCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send('IdSerial,002\n')

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)



    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '1': 'Internal error',
            '2': 'Bad syntax',
            '3': 'Wrong parameters',
            '4': 'Already coordinator somewhere',
            '5': 'Conference already exists',
            '6': 'Invalid NCCP address',
            '7': 'Invalid channel nr',
            '8': 'No session',
            '9': 'No NCCP session',
            '10': 'Not coordinator',
            '11': 'Recording is running',
            '12': 'Recording is stopped',
            '13': 'Recording is paused',
            '14': 'Permission denied',
            '15': 'No space',
            '16': 'Display mode',
            '17': 'Connection failed announce',
            '18': 'Player is playing',
            '19': 'Player is stopped',
            '20': 'Player is paused',
            '21': 'Transfer failed',
            '22': 'Directory failed',
            '23': 'Canceled'
        }

        if tag == 'Command':
            print('Command has not executed properly')
        else:
            value = DEVICE_ERROR_CODES.get(match.split(':')[1])
            if value:
                print('Error: ' + value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.IsConnected = False

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
            if command != 'RequiredPolling':
                self.UpdateRequiredPolling(None, None)
        else:
            print(command, 'does not support Update.')
            
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

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
                

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
