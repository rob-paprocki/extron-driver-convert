from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AssignName': {'Parameters': ['Address'], 'Status': {}},
            'Close': {'Parameters': ['Address'], 'Status': {}},
            'CurrentPosition': {'Parameters': ['Address', 'State'], 'Status': {}},
            'ExecuteScene': {'Parameters': ['Address'], 'Status': {}},
            'MotorAction': {'Parameters': ['Address'], 'Status': {}},
            'MovetoPosition': {'Parameters': ['Address'], 'Status': {}},
            'Open': {'Parameters': ['Address'], 'Status': {}},
            'SceneSetting': {'Parameters': ['Address', 'Scene'], 'Status': {}},
            'Stop': {'Parameters': ['Address'], 'Status': {}},
            'TravelTime': {'Parameters': ['Address'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!([0-9A-Z]{3})(r|>|<)([0-9]{2});'), self.__MatchCurrentPosition, None)
            self.AddMatchString(re.compile(b'!([0-9A-Z]{3})pM([0-9A-F]{2});'), self.__MatchMotorAction, None)
            self.AddMatchString(re.compile(b'!([0-9A-Z]{3})d([0-9A-Za-z])([0-9A-Z]{2});'), self.__MatchSceneSetting, None)
            self.AddMatchString(re.compile(b'!([0-9A-Z]{3})pT([0-9]{3});'), self.__MatchTravelTime, None)
            self.AddMatchString(re.compile(b'![0-9A-Z]{3}(E(bz|nc|ml)|U);'), self.__MatchError, None)

 
    def SetAssignName(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3 and len(value) <= 16:
            AssignNameCmdString = '!{0}N{1};'.format(address, value)
            self.__SetHelper('AssignName', AssignNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAssignName')

    def SetClose(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            CloseCmdString = '!{0}c;'.format(address)
            self.__SetHelper('Close', CloseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClose')

    def UpdateCurrentPosition(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            CurrentPositionCmdString = '!{0}r?;'.format(address)
            self.__UpdateHelper('CurrentPosition', CurrentPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCurrentPosition')

    def __MatchCurrentPosition(self, match, tag):

        StateStates = {
            'r': 'Not Moving',
            '>': 'Increasing',
            '<': 'Decreasing'
        }

        qualifier = {}
        qualifier['Address'] = match.group(1).decode()
        qualifier['State'] = StateStates[match.group(2).decode()]
        value = match.group(3).decode()
        if 0 <= int(value) <= 99:
            self.WriteStatus('CurrentPosition', value, qualifier)

    def SetExecuteScene(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            ExecuteSceneCmdString = '!{0}g{1};'.format(address, value)
            self.__SetHelper('ExecuteScene', ExecuteSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecuteScene')


    def SetMotorAction(self, value, qualifier):

        ActionStateValues = {
            'Factory Default': '00',
            'CLOS': '10',
            'FAST': '40',
            'CLOS + FAST': '50',
            'SOBR': '80',
            'CLOS + SOBR': '90',
            'FAST + SOBR': 'C0',
            'CLOS + FAST + SOBR': 'D0',
            'MOM': '01',
            'REV': '02',
            'MOM + REV': '03',
            'NOALL': '04',
            'MOM + NOALL': '05',
            'REV + NOALL': '06',
            'MOM + REV + NOALL': '07',
            'CLOS + MOM': '11',
            'CLOS + REV': '12',
            'CLOS + MOM + REV': '13',
            'CLOS + NOALL': '14',
            'CLOS + MOM + NOALL': '15',
            'CLOS + REV + NOALL': '16',
            'CLOS + MOM + REV + NOALL': '17',
            'FAST + MOM': '41',
            'FAST + REV': '42',
            'FAST + MOM + REV': '43',
            'FAST + NOALL': '44',
            'FAST + MOM + NOALL': '45',
            'FAST + REV + NOALL': '46',
            'FAST + MOM + REV + NOALL': '47',
            'CLOS + FAST + MOM': '51',
            'CLOS + FAST + REV': '52',
            'CLOS + FAST + MOM + REV': '53',
            'CLOS + FAST + NOALL': '54',
            'CLOS + FAST + MOM + NOALL': '55',
            'CLOS + FAST + REV + NOALL': '56',
            'CLOS + FAST + MOM + REV + NOALL': '57',
            'SOBR + MOM': '81',
            'SOBR + REV': '82',
            'SOBR + MOM + REV': '83',
            'SOBR + NOALL': '84',
            'SOBR + MOM + NOALL': '85',
            'SOBR + REV + NOALL': '86',
            'SOBR + MOM + REV + NOALL': '87',
            'CLOS + SOBR + MOM': '91',
            'CLOS + SOBR + REV': '92',
            'CLOS + SOBR + MOM + REV': '93',
            'CLOS + SOBR + NOALL': '94',
            'CLOS + SOBR + MOM + NOALL': '95',
            'CLOS + SOBR + REV + NOALL': '96',
            'CLOS + SOBR + MOM + REV + NOALL': '97',
            'FAST + SOBR + MOM': 'C1',
            'FAST + SOBR + REV': 'C2',
            'FAST + SOBR + MOM + REV': 'C3',
            'FAST + SOBR + NOALL': 'C4',
            'FAST + SOBR + MOM + NOALL': 'C5',
            'FAST + SOBR + REV + NOALL': 'C6',
            'FAST + SOBR + MOM + REV + NOALL': 'C7',
            'CLOS + FAST + SOBR + MOM ': 'D1',
            'CLOS + FAST + SOBR + REV': 'D2',
            'CLOS + FAST + SOBR + MOM + REV': 'D3',
            'CLOS + FAST + SOBR + NOALL': 'D4',
            'CLOS + FAST + SOBR + MOM + NOALL': 'D5',
            'CLOS + FAST + SOBR + REV + NOALL': 'D6',
            'CLOS + FAST + SOBR + MOM + REV + NOALL': 'D7'
        }

        address = qualifier['Address']
        if len(address) == 3:
            MotorActionCmdString = '!{0}pM{1};'.format(address, ActionStateValues[value])
            self.__SetHelper('MotorAction', MotorActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotorAction')

    def UpdateMotorAction(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            MotorActionCmdString = '!{0}pM?;'.format(address)
            self.__UpdateHelper('MotorAction', MotorActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMotorAction')

    def __MatchMotorAction(self, match, tag):

        ActionStateValues = {
            '00': 'Factory Default',
            '10': 'CLOS',
            '40': 'FAST',
            '50': 'CLOS + FAST',
            '80': 'SOBR',
            '90': 'CLOS + SOBR',
            'C0': 'FAST + SOBR',
            'D0': 'CLOS + FAST + SOBR',
            '01': 'MOM',
            '02': 'REV',
            '03': 'MOM + REV',
            '04': 'NOALL',
            '05': 'MOM + NOALL',
            '06': 'REV + NOALL',
            '07': 'MOM + REV + NOALL',
            '11': 'CLOS + MOM',
            '12': 'CLOS + REV',
            '13': 'CLOS + MOM + REV',
            '14': 'CLOS + NOALL',
            '15': 'CLOS + MOM + NOALL',
            '16': 'CLOS + REV + NOALL',
            '17': 'CLOS + MOM + REV + NOALL',
            '19': 'CLOS + MOM + LMTS',
            '1A': 'CLOS + REV + LMTS',
            '1B': 'CLOS + MOM + REV + LMTS',
            '1C': 'CLOS + NOALL + LMTS',
            '1D': 'CLOS + MOM + NOALL + LMTS',
            '1E': 'CLOS + REV + NOALL + LMTS',
            '1F': 'CLOS + MOM + REV + NOALL + LMTS',
            '41': 'FAST + MOM',
            '42': 'FAST + REV',
            '43': 'FAST + MOM + REV',
            '44': 'FAST + NOALL',
            '45': 'FAST + MOM + NOALL',
            '46': 'FAST + REV + NOALL',
            '47': 'FAST + MOM + REV + NOALL',
            '51': 'CLOS + FAST + MOM',
            '52': 'CLOS + FAST + REV',
            '53': 'CLOS + FAST + MOM + REV',
            '54': 'CLOS + FAST + NOALL',
            '55': 'CLOS + FAST + MOM + NOALL',
            '56': 'CLOS + FAST + REV + NOALL',
            '57': 'CLOS + FAST + MOM + REV + NOALL',
            '81': 'SOBR + MOM',
            '82': 'SOBR + REV',
            '83': 'SOBR + MOM + REV',
            '84': 'SOBR + NOALL',
            '85': 'SOBR + MOM + NOALL',
            '86': 'SOBR + REV + NOALL',
            '87': 'SOBR + MOM + REV + NOALL',
            '91': 'CLOS + SOBR + MOM',
            '92': 'CLOS + SOBR + REV',
            '93': 'CLOS + SOBR + MOM + REV',
            '94': 'CLOS + SOBR + NOALL',
            '95': 'CLOS + SOBR + MOM + NOALL',
            '96': 'CLOS + SOBR + REV + NOALL',
            '97': 'CLOS + SOBR + MOM + REV + NOALL',
            'C1': 'FAST + SOBR + MOM',
            'C2': 'FAST + SOBR + REV',
            'C3': 'FAST + SOBR + MOM + REV',
            'C4': 'FAST + SOBR + NOALL',
            'C5': 'FAST + SOBR + MOM + NOALL',
            'C6': 'FAST + SOBR + REV + NOALL',
            'C7': 'FAST + SOBR + MOM + REV + NOALL',
            'D1': 'CLOS + FAST + SOBR + MOM ',
            'D2': 'CLOS + FAST + SOBR + REV',
            'D3': 'CLOS + FAST + SOBR + MOM + REV',
            'D4': 'CLOS + FAST + SOBR + NOALL',
            'D5': 'CLOS + FAST + SOBR + MOM + NOALL',
            'D6': 'CLOS + FAST + SOBR + REV + NOALL',
            'D7': 'CLOS + FAST + SOBR + MOM + REV + NOALL'
        }

        qualifier = {}
        qualifier['Address'] = match.group(1).decode()
        value = ActionStateValues[match.group(2).decode()]
        self.WriteStatus('MotorAction', value, qualifier)

    def SetMovetoPosition(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3 and 0 <= value <= 99:
            MovetoPositionCmdString = '!{0}m{1:02d};'.format(address, value)
            self.__SetHelper('MovetoPosition', MovetoPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMovetoPosition')

    def SetOpen(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            OpenCmdString = '!{0}o;'.format(address)
            self.__SetHelper('Open', OpenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpen')

    def SetSceneSetting(self, value, qualifier):

        ValueStateValues = {
            '00': '00',
            '01': '01',
            '02': '02',
            '03': '03',
            '04': '04',
            '05': '05',
            '06': '06',
            '07': '07',
            '08': '08',
            '09': '09',
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
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25',
            '26': '26',
            '27': '27',
            '28': '28',
            '29': '29',
            '30': '30',
            '31': '31',
            '32': '32',
            '33': '33',
            '34': '34',
            '35': '35',
            '36': '36',
            '37': '37',
            '38': '38',
            '39': '39',
            '40': '40',
            '41': '41',
            '42': '42',
            '43': '43',
            '44': '44',
            '45': '45',
            '46': '46',
            '47': '47',
            '48': '48',
            '49': '49',
            '50': '50',
            '51': '51',
            '52': '52',
            '53': '53',
            '54': '54',
            '55': '55',
            '56': '56',
            '57': '57',
            '58': '58',
            '59': '59',
            '60': '60',
            '61': '61',
            '62': '62',
            '63': '63',
            '64': '64',
            '65': '65',
            '66': '66',
            '67': '67',
            '68': '68',
            '69': '69',
            '70': '70',
            '71': '71',
            '72': '72',
            '73': '73',
            '74': '74',
            '75': '75',
            '76': '76',
            '77': '77',
            '78': '78',
            '79': '79',
            '80': '80',
            '81': '81',
            '82': '82',
            '83': '83',
            '84': '84',
            '85': '85',
            '86': '86',
            '87': '87',
            '88': '88',
            '89': '89',
            '90': '90',
            '91': '91',
            '92': '92',
            '93': '93',
            '94': '94',
            '95': '95',
            '96': '96',
            '97': '97',
            '98': '98',
            '99': '99',
            'Not Act on this Scene': 'NS',
            'Clear All Scenes': '-'
        }

        address = qualifier['Address']
        if len(address) == 3:
            if value == 'Clear All Scenes':
                SceneSettingCmdString = '!{0}d-;'.format(address)
                self.__SetHelper('SceneSetting', SceneSettingCmdString, value, qualifier)
            elif len(qualifier['Scene']) != 0:
                SceneSettingCmdString = '!{0}d{1}{2};'.format(address, qualifier['Scene'], ValueStateValues[value])
                self.__SetHelper('SceneSetting', SceneSettingCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetSceneSetting')
        else:
            self.Discard('Invalid Command for SetSceneSetting')

    def UpdateSceneSetting(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            SceneSettingCmdString = '!{0}d{1}?;'.format(address, qualifier['Scene'])
            self.__UpdateHelper('SceneSetting', SceneSettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSceneSetting')

    def __MatchSceneSetting(self, match, tag):

        ValueStateValues = {
            '00': '00',
            '01': '01',
            '02': '02',
            '03': '03',
            '04': '04',
            '05': '05',
            '06': '06',
            '07': '07',
            '08': '08',
            '09': '09',
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
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25',
            '26': '26',
            '27': '27',
            '28': '28',
            '29': '29',
            '30': '30',
            '31': '31',
            '32': '32',
            '33': '33',
            '34': '34',
            '35': '35',
            '36': '36',
            '37': '37',
            '38': '38',
            '39': '39',
            '40': '40',
            '41': '41',
            '42': '42',
            '43': '43',
            '44': '44',
            '45': '45',
            '46': '46',
            '47': '47',
            '48': '48',
            '49': '49',
            '50': '50',
            '51': '51',
            '52': '52',
            '53': '53',
            '54': '54',
            '55': '55',
            '56': '56',
            '57': '57',
            '58': '58',
            '59': '59',
            '60': '60',
            '61': '61',
            '62': '62',
            '63': '63',
            '64': '64',
            '65': '65',
            '66': '66',
            '67': '67',
            '68': '68',
            '69': '69',
            '70': '70',
            '71': '71',
            '72': '72',
            '73': '73',
            '74': '74',
            '75': '75',
            '76': '76',
            '77': '77',
            '78': '78',
            '79': '79',
            '80': '80',
            '81': '81',
            '82': '82',
            '83': '83',
            '84': '84',
            '85': '85',
            '86': '86',
            '87': '87',
            '88': '88',
            '89': '89',
            '90': '90',
            '91': '91',
            '92': '92',
            '93': '93',
            '94': '94',
            '95': '95',
            '96': '96',
            '97': '97',
            '98': '98',
            '99': '99',
            'NS': 'Not Act on this Scene',
        }

        qualifier = {}
        qualifier['Address'] = match.group(1).decode()
        qualifier['Scene'] = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('SceneSetting', value, qualifier)

    def SetStop(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            StopCmdString = '!{0}s;'.format(address)
            self.__SetHelper('Stop', StopCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStop')

    def UpdateTravelTime(self, value, qualifier):

        address = qualifier['Address']
        if len(address) == 3:
            TravelTimeCmdString = '!{0}pT?;'.format(address)
            self.__UpdateHelper('TravelTime', TravelTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTravelTime')

    def __MatchTravelTime(self, match, tag):

        qualifier = {}
        qualifier['Address'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('TravelTime', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Address'] == '000':
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

        ErrorStateValues = {
            'bz': 'Error: Busy',
            'nc': 'Error: Limits are not set',
            'ml': 'Error: Message lost'
        }

        err = match.group(1).decode()
        value = match.group(2).decode()
        if err == 'E':
            self.Error([ErrorStateValues[value]])
        elif err == 'U':
            self.Error(['Undefined / Bad Message'])

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
