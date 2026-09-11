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
            'AdjustmentValue': {'Parameters': ['Address', 'Room', 'Group', 'Type'], 'Status': {}},
            'DaylightAutomation': {'Parameters': ['Address', 'Room', 'Group'], 'Status': {}},
            'Dimmer': {'Parameters': ['Address', 'Room', 'Group', 'Type', 'Time'], 'Status': {}},
            'Fade': {'Parameters': ['Address', 'Room', 'Group'], 'Status': {}},
            'FadeRateSelect': {'Parameters': ['Address', 'Room', 'Group'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'SceneRecall': {'Parameters': ['Address', 'Room', 'Group'], 'Status': {}},
            'SceneSave': {'Parameters': ['Address', 'Room'], 'Status': {}},
            'SceneStatus': {'Parameters': ['Address', 'Room', 'Group', 'Type', 'Scene'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02TLR([0-9]{1,2})R([0-9]{1,2})G([0-9]{1,2})T(2|3|4|5|6|7|8|9|10|12|30|31|39|64|65)S([0-9]{1,2})W([0-9]{1,3})E([0-9]{1,5})\x03'), self.__MatchSceneStatus, None)
            self.AddMatchString(re.compile(b'\x02V(\d\.\d\d)L([0-3])BMS.*?\x03'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'\x02NAK(1|2|3|4|5|6|8|10|11|12|13|14)!\x03'), self.__MatchError, None)

    def SetAdjustmentValue(self, value, qualifier):

        TypeStates = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '30', '31', '39', '64', '65']

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Address = qualifier['Address']
        Room = qualifier['Room']
        Group = qualifier['Group']
        Type = qualifier['Type']
        if (1 <= int(Address) <= 99) and (1 <= int(Room) <= 99) and (1 <= int(Group) <= 99) and (Type in TypeStates) and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AdjustmentValueCmdString = '\x02TLR{0}R{1}G{2}T{3}W{4}!\x03'.format(Address, Room, Group, Type, value)
            self.__SetHelper('AdjustmentValue', AdjustmentValueCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAdjustmentValue')

    def SetDaylightAutomation(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        Group = int(qualifier['Group'])
        if (1 <= Address <= 99) and (1 <= Room <= 99) and (1 <= Group <= 99):
            DaylightAutomationCmdString = '\x02TLR{0}R{1}G{2}T1TLA{3}\x03'.format(Address, Room, Group, ValueStateValues[value])
            self.__SetHelper('DaylightAutomation', DaylightAutomationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDaylightAutomation')

    def SetDimmer(self, value, qualifier):

        ValueStateValues = {
            'Up': 'DP',
            'Down': 'DM',
            'Stop': 'DS'
        }
        temp = int(qualifier['Type'])
        temp1 = qualifier['Time']
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        Group = int(qualifier['Group'])
        if ((1 < temp < 13) or (29 < temp < 40) or (63 < temp < 66)) and (1 <= Address <= 99) and (1 <= Room <= 99) and (1 <= Group <= 99):
            if value == 'Stop':
                DimmerCmdString = '\x02TLR{0}R{1}G{2}T{3}DS\x03'.format(Address, Room, Group, temp)
            else:
                if 0 <= temp1 <= 255:
                    DimmerCmdString = '\x02TLR{0}R{1}G{2}T{3}{4}{5}\x03'.format(Address, Room, Group, temp, ValueStateValues[value], temp1)
                else:
                    DimmerCmdString = ''
                    print('Invalid Command for SetDimmer')
            if DimmerCmdString:
                self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDimmer')
        else:
            print('Invalid Command for SetDimmer')

    def SetFade(self, value, qualifier):

        ValueStateValues = {
            'Slow': 'FADE',
            'Fast': 'OFF'
        }
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        Group = int(qualifier['Group'])
        if (1 <= Address <= 99) and (1 <= Room <= 99) and (1 <= Group <= 99):
            FadeCmdString = '\x02TLR{0}R{1}G{2}T1{3}\x03'.format(Address, Room, Group, ValueStateValues[value])
            self.__SetHelper('Fade', FadeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFade')

    def SetFadeRateSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        Group = int(qualifier['Group'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= Address <= 99) and (1 <= Room <= 99) and (1 <= Group <= 99):
            FadeRateSelectCmdString = '\x02TLR{0}R{1}G{2}T1FADE!{3}\x03'.format(Address, Room, Group, value)
            self.__SetHelper('FadeRateSelect', FadeRateSelectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFadeRateSelect')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '\x02VERSION?\x03'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetSceneRecall(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20'
        }
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        Group = int(qualifier['Group'])
        if (1 <= Address <= 99) and (1 <= Room <= 99) and (1 <= Group <= 99):
            SceneRecallCmdString = '\x02TLR{0}R{1}G{2}T1S{3}!\x03'.format(Address, Room, Group, ValueStateValues[value])
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneRecall')

    def SetSceneSave(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            'Current': '99'
        }
        Address = int(qualifier['Address'])
        Room = int(qualifier['Room'])
        if (1 <= Address <= 99) and (1 <= Room <= 99):
            SceneSaveCmdString = '\x02TLR{0}R{1}PROGS{2}\x03'.format(Address, Room, ValueStateValues[value])
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneSave')

    def UpdateSceneStatus(self, value, qualifier):

        TypeStates = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '30', '31', '39', '64', '65']
        Address = qualifier['Address']
        Room = qualifier['Room']
        Group = qualifier['Group']
        Type = qualifier['Type']
        if (1 <= int(Address) <= 99) and (1 <= int(Room) <= 99) and (1 <= int(Group) <= 99) and (Type in TypeStates):
            SceneStatusCmdString = '\x02TLR{0}R{1}G{2}T{3}AUTO1!\x03'.format(Address, Room, Group, Type)
            self.__UpdateHelper('SceneStatus', SceneStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateSceneStatus')

    def __MatchSceneStatus(self, match, tag):

        if (1 <= int(match.group(1).decode()) <= 99) and (1 <= int(match.group(2).decode()) <= 99) and (1 <= int(match.group(3).decode()) <= 99) and (0 <= int(match.group(5).decode()) <= 20) and 0 <= int(match.group(6).decode()) <= 255:
            qualifier = {}
            qualifier['Address'] = match.group(1).decode()
            qualifier['Room'] = match.group(2).decode()
            qualifier['Group'] = match.group(3).decode()
            qualifier['Type'] = match.group(4).decode()
            qualifier['Scene'] = match.group(5).decode()
            value = int(match.group(6).decode())
            self.WriteStatus('SceneStatus', value, qualifier)
        else:
            print('Invalid/unexpected response for', command)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '1': 'Unknown room number',
            '2': 'Unknown group number',
            '3': 'Unknown bus number',
            '4': 'Unknown LUXMATE type or LUXMATE type not allowed',
            '5': 'Unknown TLR number',
            '6': 'Invalid data',
            '8': 'Unknown command',
            '10': 'Group error at the use of wildcards or at names (no LUXMATE output found)',
            '11': 'Name does not exist',
            '12': 'Bus short-circuit',
            '13': 'Init state',
            '14': 'Status feedback possible'
        }

        print('Error: {0} for {1}'.format(DEVICE_ERROR_CODES[match.group(1).decode()]), command)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
