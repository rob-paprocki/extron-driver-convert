from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'AspectRatio': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'IRRemote': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'OperationHours': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID', 'Unit ID'], 'Status': {}},
        }

        self.DevList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        self.UnitList = ['1', '2', '3', '4', '*']
        self.runtimeHigh = -1
        self.runtimeLow = -1

        self.value1 = ''
        self.valuelow = ''

        self.InitialResponseSwitch = {
            'A1' : 1,               'F1' : 1,               'K1' : 1,               'P1' : 1,
            'A2' : 1,               'F2' : 1,               'K2' : 1,               'P2' : 1,
            'A3' : 1,               'F3' : 1,               'K3' : 1,               'P3' : 1,
            'A4' : 1,               'F4' : 1,               'K4' : 1,               'P4' : 1,
            'B1' : 1,               'G1' : 1,               'L1' : 1,
            'B2' : 1,               'G2' : 1,               'L2' : 1,
            'B3' : 1,               'G3' : 1,               'L3' : 1,
            'B4' : 1,               'G4' : 1,               'L4' : 1,
            'C1' : 1,               'H1' : 1,               'M1' : 1,
            'C2' : 1,               'H2' : 1,               'M2' : 1,
            'C3' : 1,               'H3' : 1,               'M3' : 1,
            'C4' : 1,               'H4' : 1,               'M4' : 1,
            'D1' : 1,               'I1' : 1,               'N1' : 1,
            'D2' : 1,               'I2' : 1,               'N2' : 1,
            'D3' : 1,               'I3' : 1,               'N3' : 1,
            'D4' : 1,               'I4' : 1,               'N4' : 1,
            'E1' : 1,               'J1' : 1,               'O1' : 1,
            'E2' : 1,               'J2' : 1,               'O2' : 1,
            'E3' : 1,               'J3' : 1,               'O3' : 1,
            'E4' : 1,               'J4' : 1,               'O4' : 1,
        }

        self.InitialEolSwitch = {
            'A1' : 1,               'F1' : 1,               'K1' : 1,               'P1' : 1,
            'A2' : 1,               'F2' : 1,               'K2' : 1,               'P2' : 1,
            'A3' : 1,               'F3' : 1,               'K3' : 1,               'P3' : 1,
            'A4' : 1,               'F4' : 1,               'K4' : 1,               'P4' : 1,
            'B1' : 1,               'G1' : 1,               'L1' : 1,
            'B2' : 1,               'G2' : 1,               'L2' : 1,
            'B3' : 1,               'G3' : 1,               'L3' : 1,
            'B4' : 1,               'G4' : 1,               'L4' : 1,
            'C1' : 1,               'H1' : 1,               'M1' : 1,
            'C2' : 1,               'H2' : 1,               'M2' : 1,
            'C3' : 1,               'H3' : 1,               'M3' : 1,
            'C4' : 1,               'H4' : 1,               'M4' : 1,
            'D1' : 1,               'I1' : 1,               'N1' : 1,
            'D2' : 1,               'I2' : 1,               'N2' : 1,
            'D3' : 1,               'I3' : 1,               'N3' : 1,
            'D4' : 1,               'I4' : 1,               'N4' : 1,
            'E1' : 1,               'J1' : 1,               'O1' : 1,
            'E2' : 1,               'J2' : 1,               'O2' : 1,
            'E3' : 1,               'J3' : 1,               'O3' : 1,
            'E4' : 1,               'J4' : 1,               'O4' : 1,
        }

        self.NextOperationHoursQuery = 'High'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OP([A-P])([1-4])ASPECT=(FILL|CROP|LETTERBOX|16X9|ONE\.TO\.ONE|4X3)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'OP([A-P])([1-4])IR\.REMOTE=(ENABLE|DISABLE)\r'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'OP([A-P])([1-4])RUNTIME\.HOURS\.(HIGH|LOW)=(\d{1,5})\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'OP([A-P])([1-4])DISPLAY\.POWER=(ON|OFF)\r'), self.__MatchPower, None)

        self.responseRegex = re.compile(b'OP([A-P])([1-4])ASCII\.RESPONSE=SYMBOLIC\r')
        self.eolRegex = re.compile(b'OP([A-P])([1-4])ASCII\.EOL=CR\r')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': 'OP{0}{1}ASPECT=FILL\r',
            'Crop': 'OP{0}{1}ASPECT=CROP\r',
            'Letterbox': 'OP{0}{1}ASPECT=LETTERBOX\r',
            '16:9': 'OP{0}{1}ASPECT=16X9\r',
            'One to One': 'OP{0}{1}ASPECT=ONE.TO.ONE\r',
            '4:3': 'OP{0}{1}ASPECT=4X3\r'
        }
        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            AspectRatioCmdString = ValueStateValues[value].format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            AspectRatioCmdString = 'OP{0}{1}ASPECT?\r'.format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FILL': 'Fill',
            'CROP': 'Crop',
            'LETTERBOX': 'Letterbox',
            '16X9': '16:9',
            'ONE.TO.ONE': 'One to One',
            '4X3': '4:3'
        }
        Device = match.group(1).decode()
        Unit = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        if Device in self.DevList and Unit in self.UnitList:
            self.WriteStatus('AspectRatio', value, {'Device ID': Device, 'Unit ID': Unit})

    def SetIRRemote(self, value, qualifier):

        ValueStateValues = {
            'On': 'OP{0}{1}IR.REMOTE=ENABLE\r',
            'Off': 'OP{0}{1}IR.REMOTE=DISABLE\r'
        }
        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            IRRemoteCmdString = ValueStateValues[value].format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__SetHelper('IRRemote', IRRemoteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemote')

    def UpdateIRRemote(self, value, qualifier):

        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            IRRemoteCmdString = 'OP{0}{1}IR.REMOTE?\r'.format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__UpdateHelper('IRRemote', IRRemoteCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIRRemote')

    def __MatchIRRemote(self, match, tag):

        ValueStateValues = {
            'ENABLE': 'On',
            'DISABLE': 'Off'
        }

        Device = match.group(1).decode()
        Unit = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        if Device in self.DevList and Unit in self.UnitList:
            self.WriteStatus('IRRemote', value, {'Device ID': Device, 'Unit ID': Unit})

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Menu': 'MENU',
            'Previous': 'PREV',
            'Enter': 'ENTER',
        }
        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            MenuNavigationCmdString = 'KY {0}{1} {2}\r'.format(qualifier['Device ID'], qualifier['Unit ID'], ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def UpdateOperationHours(self, value, qualifier):

        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:

            if self.NextOperationHoursQuery == 'High':
                OperationHoursCmdString = 'OP{0}{1}RUNTIME.HOURS.HIGH?\r'.format(qualifier['Device ID'], qualifier['Unit ID'])
                self.NextOperationHoursQuery = 'Low'
            else:
                OperationHoursCmdString = 'OP{0}{1}RUNTIME.HOURS.LOW?\r'.format(qualifier['Device ID'], qualifier['Unit ID'])
                self.NextOperationHoursQuery = 'High'
            self.__UpdateHelper('OperationHours', OperationHoursCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOperationHours')

    def __MatchOperationHours(self, match, tag):

        Device = match.group(1).decode()
        Unit = match.group(2).decode()
        runtimeType = match.group(3).decode()
        if Device in self.DevList and Unit in self.UnitList:
            if runtimeType == 'HIGH':
                self.runtimeHigh = int(match.group(4).decode())
            elif runtimeType == 'LOW':
                self.runtimeLow = int(match.group(4).decode())
            if 0 <= self.runtimeHigh and 0 <= self.runtimeLow:
                value = int((self.runtimeHigh / 10000) + (self.runtimeLow % 10000))
                self.WriteStatus('OperationHours', value, {'Device ID': Device, 'Unit ID': Unit})
                self.runtimeHigh = -1
                self.runtimeLow = -1

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ky {0}{1} on\r',
            'Off': 'ky {0}{1} off\r'
        }
        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            PowerCmdString = ValueStateValues[value].format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            PowerCmdString = 'OP{0}{1}DISPLAY.POWER?\r'.format(qualifier['Device ID'], qualifier['Unit ID'])
            self.__UpdateHelper('Power', PowerCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        Device = match.group(1).decode()
        Unit = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        if Device in self.DevList and Unit in self.UnitList:
            self.WriteStatus('Power', value, {'Device ID': Device, 'Unit ID': Unit})

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 40 and qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            PresetRecallCmdString = 'OP {0}{1} SLOT.RECALL ({2})\r'.format(qualifier['Device ID'], qualifier['Unit ID'], int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 40 and qualifier['Device ID'] in self.DevList and qualifier['Unit ID'] in self.UnitList:
            PresetSaveCmdString = 'OP {0}{1} SLOT.SAVE ({2})\r'.format(qualifier['Device ID'], qualifier['Unit ID'], int(value) - 1)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def checkInitial(self, qual):
        if self.InitialResponseSwitch[qual] != 0:
            initAsciiResponse = 'OP{0}ASCII.RESPONSE=SYMBOLIC\r'.format(qual)
            res = self.SendAndWait(initAsciiResponse, 0.3, deliTag=b'\r')
            if res:
                match = re.search(self.responseRegex, res)
                if match:
                    Qual = match.group(1).decode() + match.group(2).decode()
                    self.InitialResponseSwitch[Qual] = 0

        if self.InitialEolSwitch[qual] != 0:
            initAsciiEOL = 'OP{0}ASCII.EOL=CR\r'.format(qual)
            res = self.SendAndWait(initAsciiEOL, 0.3, deliTag=b'\r')
            if res:
                match = re.search(self.eolRegex, res)
                if match:
                    Qual = match.group(1).decode() + match.group(2).decode()
                    self.InitialEolSwitch[Qual] = 0

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        qual = qualifier['Device ID'] + qualifier['Unit ID']
        self.checkInitial(qual)
        if self.InitialResponseSwitch[qual] == 0 and self.InitialEolSwitch[qual] == 0:
            self.Send(commandstring)
        else:
            self.Error(['Set Command: {} Device ID: {} Unit ID:{} initialization failed.'.format(command, qual[0], qual[1])])

    def __UpdateHelper(self, command, commandstring, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            qual = qualifier['Device ID'] + qualifier['Unit ID']
            self.checkInitial(qual)
            if self.InitialResponseSwitch[qual] == 0 and self.InitialEolSwitch[qual] == 0:
                self.Send(commandstring)
            else:
                self.Error(['Update Command: {} Device ID: {} Unit ID:{} initialization failed.'.format(command, qual[0], qual[1])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.NextOperationHoursQuery = 'High'

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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
