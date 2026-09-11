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
        self.Models = {
            'UMX-TPS-TX140': self.ltwr_2_2603_6,
            'UMX-TPS-TX120': self.ltwr_2_2603_3,
            'UMX-TPS-TX130': self.ltwr_2_2603_5,
            'WP-UMX-TPS-TX120-US': self.ltwr_2_2603_3,
            'WP-UMX-TPS-TX130-US': self.ltwr_2_2603_4,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Input': {'Parameters': ['Mode'], 'Status': {}},
            'OutputLock': {'Parameters': ['Mode'], 'Status': {}},
            'OutputMute': {'Parameters': ['Mode'], 'Status': {}},
            'Restart': {'Status': {}},
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(ALL(A|V)\s?[M|L|U]?\s?0(\d)\)\r\n', re.I), self.__MatchInput, None)
            
        self.lastInputUpdate = 0
        self.Audio = 'A'
        self.Video = 'V'      

    def SetInput(self, value, qualifier):

        Modes = {
            'Audio': 'A',
            'Video': 'V',
            'AudioVideo': 'AV'
        }

        Mode = Modes[qualifier['Mode']]

        if value in self.Inputs[Mode]:
            CmdString = '{' + self.Inputs[Mode][value] + '@1 ' + Mode + '}'
            self.__SetHelper('Input', CmdString, value, qualifier)
        else:
            print('Unavailable Input mode selected for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', '{VC AV}', value, qualifier)

    def __MatchInput(self, match, tag):

        ModeStates = {
            'A': 'Audio',
            'V': 'Video',
        }

        Mode = ModeStates[match.group(1).decode()]
        Input = self.InputStates[match.group(2).decode()]
        self.WriteStatus('Input', Input, {'Mode': Mode})

        if Mode == 'Audio':
            self.Audio = Input
        elif Mode == 'Video':
            self.Video = Input

        if self.Audio == self.Video:
            self.WriteStatus('Input', Input, {'Mode': 'AudioVideo'})
        else:
            self.WriteStatus('Input', 'Untied', {'Mode': 'AudioVideo'})

    def SetOutputLock(self, value, qualifier):

        Modes = {
            'Audio': 'A',
            'Video': 'V',
            'AudioVideo': 'AV'
        }

        States = {
            'On': '#>',
            'Off': '+<'
        }

        CmdString = '{' + States[value] + '01 ' + Modes[qualifier['Mode']] + '}'
        self.__SetHelper('OutputLock', CmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        Modes = {
            'Audio': 'A',
            'Video': 'V',
            'AudioVideo': 'AV'
        }

        States = {
            'On': '#',
            'Off': '+'
        }

        CmdString = '{' + States[value] + '01 ' + Modes[qualifier['Mode']] + '}'
        self.__SetHelper('OutputMute', CmdString, value, qualifier)

    def SetRestart(self, value, qualifier):
        self.__SetHelper('Restart', '{RST}', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.lastInputUpdate = 0

    def ltwr_2_2603_3(self):

        self.Inputs = {
            'A': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
            },

            'V': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'Test Pattern': '3',
            },

            'AV': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
            },
        }

        self.InputStates = {
            '1': 'VGA/Audio 1',
            '2': 'HDMI',
            '3': 'Test Pattern',
        }

    def ltwr_2_2603_4(self):

        self.Inputs = {
            'A': {
                'VGA/Audio 1': '1',
                'DisplayPort': '2',
                'HDMI': '3',
            },

            'V': {
                'VGA/Audio 1': '1',
                'DisplayPort': '2',
                'HDMI': '3',
                'Test Pattern': '4'
            },

            'AV': {
                'VGA/Audio 1': '1',
                'DisplayPort': '2',
                'HDMI': '3',
            },
        }

        self.InputStates = {
            '1': 'VGA/Audio 1',
            '2': 'DisplayPort',
            '3': 'HDMI',
            '4': 'Test Pattern',
        }

    def ltwr_2_2603_5(self):

        self.Inputs = {
            'A': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DVI-D': '3',
            },

            'V': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DVI-D': '3',
                'DVI-A': '4',
                'Test Pattern': '5'
            },

            'AV': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DVI-D': '3',
            },
        }

        self.InputStates = {
            '1': 'VGA/Audio 1',
            '2': 'HDMI',
            '3': 'DVI-D',
            '4': 'DVI-A',
            '5': 'Test Pattern',
        }

    def ltwr_2_2603_6(self):

        self.Inputs = {
            'A': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DisplayPort': '3',
                'DVI-D': '4',
                'DVI-A/Audio 2': '5',
            },

            'V': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DisplayPort': '3',
                'DVI-D': '4',
                'DVI-A/Audio 2': '5',
                'Test Pattern': '6'
            },

            'AV': {
                'VGA/Audio 1': '1',
                'HDMI': '2',
                'DisplayPort': '3',
                'DVI-D': '4',
                'DVI-A/Audio 2': '5',
            },
        }

        self.InputStates = {
            '1': 'VGA/Audio 1',
            '2': 'HDMI',
            '3': 'DisplayPort',
            '4': 'DVI-D',
            '5': 'DVI-A/Audio 2',
            '6': 'Test Pattern',
        }

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
