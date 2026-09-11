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
            'SceneStatus': {'Parameters': ['Address', 'Room', 'Group', 'Type', 'Number'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02(TLR[0-9]{1,2})?(R[0-9]{1,2})?(G[0-9]{1,2})?T(2|3|4|5|6|7|8|9|10|12|30|31|39|64|65)S([0-9]{1,2})W([0-9]{1,3})E([0-9]{1,5})\x03'), self.__MatchSceneStatus, None)
            self.AddMatchString(re.compile(b'\x02V(\d\.\d\d)L([0-3])BMS.*?\x03'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'\x02NAK(1|2|3|4|5|6|8|10|11|12|13|14)!\x03'), self.__MatchError, None)

    def SetAdjustmentValue(self, value, qualifier):

        TypeStates = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '30', '31', '39', '64', '65']

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')
        Type = qualifier['Type']
        if (Type in TypeStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']
                and addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing'):
            AdjustmentValueCmdString = '\x02{0}{1}{2}T{3}W{4}!\x03'.format(addr_val, room_val, group_val, Type, value)
            self.__SetHelper('AdjustmentValue', AdjustmentValueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAdjustmentValue')

    def SetDaylightAutomation(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')

        if addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing':
            DaylightAutomationCmdString = '\x02{0}{1}{2}T1TLA{3}\x03'.format(addr_val, room_val, group_val, ValueStateValues[value])
            self.__SetHelper('DaylightAutomation', DaylightAutomationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDaylightAutomation')

    def SetDimmer(self, value, qualifier):

        ValueStateValues = {
            'Up': 'DP',
            'Down': 'DM',
            'Stop': 'DS'
        }

        DimmerCmdString = ''
        temp = int(qualifier['Type'])
        temp1 = qualifier['Time']
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')

        if ((1 < temp < 13) or (29 < temp < 40) or (63 < temp < 66)) and addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing':
            if value == 'Stop':
                DimmerCmdString = '\x02{0}{1}{2}T{3}DS\x03'.format(addr_val, room_val, group_val, temp)
            else:
                if 0 <= temp1 <= 255:
                    DimmerCmdString = '\x02{0}{1}{2}T{3}{4}{5}\x03'.format(addr_val, room_val, group_val, temp, ValueStateValues[value], temp1)
                else:
                    DimmerCmdString = ''
                    self.Discard('Invalid Command for SetDimmer')

            if DimmerCmdString:
                self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDimmer')
        else:
            self.Discard('Invalid Command for SetDimmer')

    def SetFade(self, value, qualifier):

        ValueStateValues = {
            'Slow': 'FADE',
            'Fast': 'OFF'
        }
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')

        if addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing':
            FadeCmdString = '\x02{0}{1}{2}T1{3}\x03'.format(addr_val, room_val, group_val, ValueStateValues[value])
            self.__SetHelper('Fade', FadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFade')

    def SetFadeRateSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing':
            FadeRateSelectCmdString = '\x02{0}{1}{2}T1FADE!{3}\x03'.format(addr_val, room_val, group_val, value)
            self.__SetHelper('FadeRateSelect', FadeRateSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFadeRateSelect')

    def UpdateFirmwareVersion(self, value, qualifier):
        FirmwareVersionCmdString = '\x02VERSION?\x03'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetSceneRecall(self, value, qualifier):

        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')

        if 0 <= int(value) <= 20 and addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing':
            SceneRecallCmdString = '\x02{0}{1}{2}T1S{3}!\x03'.format(addr_val, room_val, group_val, value)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

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
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')

        if addr_val != 'Missing' and room_val != 'Missing':
            SceneSaveCmdString = '\x02{0}{1}PROGS{2}\x03'.format(addr_val, room_val, ValueStateValues[value])
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSave')

    def UpdateSceneStatus(self, value, qualifier):

        TypeStates = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '30', '31', '39', '64', '65']
        addr_val = '' if qualifier['Address'] == 'None' else ('TLR{}'.format(qualifier['Address']) if 1 <= int(qualifier['Address']) <= 99 else 'Missing')
        room_val = '' if qualifier['Room'] == 'None' else ('R{}'.format(qualifier['Room']) if 1 <= int(qualifier['Room']) <= 99 else 'Missing')
        group_val = '' if qualifier['Group'] == 'None' else ('G{}'.format(qualifier['Group']) if 1 <= int(qualifier['Group']) <= 99 else 'Missing')
        Type = qualifier['Type']
        num_val = qualifier['Number']
        if Type in TypeStates and addr_val != 'Missing' and room_val != 'Missing' and group_val != 'Missing' and 0 <= int(num_val) <= 20:
            SceneStatusCmdString = '\x02{0}{1}{2}T{3}AUTO1!\x03'.format(addr_val, room_val, group_val, Type)  # 1 shot polling for unsolicited data
            self.__UpdateHelper('SceneStatus', SceneStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSceneStatus')

    def __MatchSceneStatus(self, match, tag):

        if (0 <= int(match.group(5).decode()) <= 20) and 0 <= int(match.group(6).decode()) <= 255:
            qualifier = {}
            qualifier['Address'] = match.group(1).decode()[3:] if match.group(1) else 'None'
            qualifier['Room'] = match.group(2).decode()[1:] if match.group(2) else 'None'
            qualifier['Group'] = match.group(3).decode()[1:] if match.group(3) else 'None'
            qualifier['Type'] = match.group(4).decode()
            qualifier['Number'] = match.group(5).decode()
            value = int(match.group(6).decode())
            self.WriteStatus('SceneStatus', value, qualifier)
        else:
            self.Error(['Scene Status: Invalid/unexpected response'])

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

        self.Error(['Error: {0}'.format(DEVICE_ERROR_CODES[match.group(1).decode()])])

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=7, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
