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
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'TouchInput': {'Parameters': ['Port'], 'Status': {}},
            'TouchMode': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.devicePassword = None
        self.deviceUsername = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValuesPC = {
            'Wide': '1',
            'Normal': '2',
            'Dot by Dot': '3',
            'Zoom 1': '4',
            'Zoom 2': '5'
        }

        AspectRatioValuesAV = {
            'Wide': '1',
            'Zoom 1': '2',
            'Zoom 2': '3',
            'Normal': '4',
            'Dot by Dot': '5'
        }
        Input = qualifier['Input']
        AspectRatioCmdString = ''
        if Input == 'PC':
            AspectRatioCmdString = 'WIDE   {}\r'.format(AspectRatioValuesPC[value])
        elif Input == 'AV':
            AspectRatioCmdString = 'WIDE   {}\r'.format(AspectRatioValuesAV[value])
        else:
            print('Invalid Command for SetAspectRatio')
        if AspectRatioCmdString:
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioValuesPC = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot',
            '4': 'Zoom 1',
            '5': 'Zoom 2',
        }

        AspectRatioValuesAV = {
            '1': 'Wide',
            '2': 'Zoom 1',
            '3': 'Zoom 2',
            '4': 'Normal',
            '5': 'Dot by Dot'
        }

        Input = qualifier['Input']
        if Input in ['AV', 'PC']:
            AspectRatioCmdString = 'WIDE????\r'
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    if Input == 'PC':
                        value = AspectRatioValuesPC[res[0]]
                    elif Input == 'AV':
                        value = AspectRatioValuesAV[res[0]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAspectRatio')
        else:
            print('Invalid Command')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = 'MUTE   {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AGIN   1\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB1(RGB)': '2',
            'D-SUB1(Component)': '3',
            'D-SUB1(Video)': '4',
            'HDMI 1(PC)': '10',
            'HDMI 1(AV)': '9',
            'HDMI 2(PC)': '13',
            'HDMI 2(AV)': '12',
            'HDMI 3(PC)': '18',
            'HDMI 3(AV)': '17',
            'DisplayPort': '14',
            'D-SUB2': '16'
        }

        InputCmdString = 'INPS  {:>2}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            2: 'D-SUB1(RGB)',
            3: 'D-SUB1(Component)',
            4: 'D-SUB1(Video)',
            10: 'HDMI 1(PC)',
            9: 'HDMI 1(AV)',
            13: 'HDMI 2(PC)',
            12: 'HDMI 2(AV)',
            18: 'HDMI 3(PC)',
            17: 'HDMI 3(AV)',
            14: 'DisplayPort',
            16: 'D-SUB2'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[0:-1])]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateInput')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB1(RGB)': '2',
            'D-SUB1(Component)': '3',
            'D-SUB1(Video)': '4',
            'HDMI 1(PC)': '10',
            'HDMI 1(AV)': '9',
            'HDMI 2(PC)': '13',
            'HDMI 2(AV)': '12',
            'HDMI 3(PC)': '18',
            'HDMI 3(AV)': '17',
            'DisplayPort': '14',
            'D-SUB2': '16'
        }

        PIPInputCmdString = 'MWIP  {:>2}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            2: 'D-SUB1(RGB)',
            3: 'D-SUB1(Component)',
            4: 'D-SUB1(Video)',
            10: 'HDMI 1(PC)',
            9: 'HDMI 1(AV)',
            13: 'HDMI 2(PC)',
            12: 'HDMI 2(AV)',
            18: 'HDMI 3(PC)',
            17: 'HDMI 3(AV)',
            14: 'DisplayPort',
            16: 'D-SUB2'
        }

        PIPInputCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[0:-1])]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'PIP': '1',
            'PbyP': '2',
            'PbyP 2': '3'
        }

        PIPModeCmdString = 'MWIN   {}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PbyP',
            '3': 'PbyP 2'
        }

        PIPModeCmdString = 'MWIN????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{:4}\r'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'MPSZ????\r'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = 'POWR   {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input Signal Waiting Mode'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetTouchInput(self, value, qualifier):

        PortStates = {
            'Bottom USB': 'USCB   {}\r',
            'Side USB': 'USCS   {}\r'
        }
        ValueStateValues = {
            'Input Terminal': '1',
            'DisplayPort': '2',
            'HDMI 1': '3',
            'HDMI 2': '4',
            'HDMI 3': '5',
            'D-SUB 1': '6',
            'D-SUB 2': '7'
        }
        Port = qualifier['Port']
        if Port in PortStates:
            TouchInputCmdString = PortStates[Port].format(ValueStateValues[value])
            self.__SetHelper('TouchInput', TouchInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTouchInput')

    def UpdateTouchInput(self, value, qualifier):

        PortStates = {
            'Bottom USB': 'USCB????\r',
            'Side USB': 'USCS????\r'
        }
        ValueStateValues = {
            '1': 'Input Terminal',
            '2': 'DisplayPort',
            '3': 'HDMI 1',
            '4': 'HDMI 2',
            '5': 'HDMI 3',
            '6': 'D-SUB 1',
            '7': 'D-SUB 2',
            '0': 'Invalid'
        }
        Port = qualifier['Port']
        if Port in PortStates:
            TouchInputCmdString = PortStates[Port]
            res = self.__UpdateHelper('TouchInput', TouchInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('TouchInput', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateTouchInput')
        else:
            print('Invalid Command for UpdateTouchInput')

    def SetTouchMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        TouchModeCmdString = 'GMDP   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TouchMode', TouchModeCmdString, value, qualifier)

    def UpdateTouchMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TouchModeCmdString = 'GMDP????\r'
        res = self.__UpdateHelper('TouchMode', TouchModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('TouchMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTouchMode')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{:4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                print('{0}: No Relevant Command or Command Cannot Be Executed in Current State'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n').decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
