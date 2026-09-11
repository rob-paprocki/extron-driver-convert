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
            'VC120-12X': self.yea_12_2394_other,
            'VC120-18X': self.yea_12_2394_other,
            'VC100': self.yea_12_2394_other,
            'VC110': self.yea_12_2394_other,
            'VC400': self.yea_12_2394_other,
            'VC500': self.yea_12_2394_500_800_880,
            'VC800': self.yea_12_2394_500_800_880,
            'VC880': self.yea_12_2394_500_800_880,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddressbookNavigation': {'Status': {}},
            'AddressbookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'AddressbookSearchSet': {'Status': {}},
            'AddressbookUpdate': {'Parameters': ['Addressbook Type'], 'Status': {}},
            'Answer': {'Status': {}},
            'Buttons': {'Status': {}},
            'CameraNearMove': {'Status': {}},
            'DialCommand': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMFDialingTones': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'NumberButtons': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SystemStatus': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.StartingEntry = 1
        self.EndEntry = 0
        self.Advance = True
        self.Authenticated = 'None'
        self.devicePassword = None
        self.__NumberOfAddressbookSearch = 5
        self.nameList = []


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'donotdisturb global get (on|off)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(re.compile(b'mute near get (on|off)\r\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'sysstatus get (idle|sleeping|talking max|talking|finished|outgoing|ringing).*?\r\n'), self.__MatchSystemStatus, None)
            self.AddMatchString(re.compile(b'volume get ([0-9]{1,2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'error: (.*)\r\n'), self.__MatchError, None)

            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None) # Refer Yealink connected.JPG

        self.regex = re.compile('([0-9. ]|)')
        self.LocalAddressResponsePattern = re.compile('(?:local) \"([\S\s]+?)\" ((?:\"([0-9.]{1,})\" ?)+)')
        self.ConfAddressResponsePattern = re.compile('(?:conf) \"([\S\s]+?)\" ((?:\"([0-9.]{1,})\" ?)+)')
        self.NoPattern = re.compile('\"([0-9.]{1,})\"')

    @property
    def NumberOfAddressbookSearch(self):
        return self.__NumberOfAddressbookSearch

    @NumberOfAddressbookSearch.setter
    def NumberOfAddressbookSearch(self, value):
        if 1 <= int(value) <= 15:
            self.__NumberOfAddressbookSearch = int(value)
        else:
            print("ERROR: NumberOfAddressbookSearch parameter requires a number from range '1' to '15'")

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send(self.devicePassword)
            self.Authenticated = 'User'
        else:
            self.MissingCredentialsLog('Password')

    def SetAddressbookNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self.__NumberOfAddressbookSearch
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.Advance:
                    self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self.__NumberOfAddressbookSearch - 1

            numOfName = len(self.nameList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < numOfName and index < self.EndEntry:
                name = self.nameList[index]
                self.WriteStatus('AddressbookSearchResult', name, {'Button': int(button)})
                button = button + 1
                index = index + 1

            if button <= self.__NumberOfAddressbookSearch:
                self.Advance = False
                self.WriteStatus('AddressbookSearchResult', '***End of list***', {'Button': button})
                button = button + 1
                for i in range(button, int(self.__NumberOfAddressbookSearch) + 1):
                    self.WriteStatus('AddressbookSearchResult', '', {'Button': i})
        else:
            print('Invalid Command for SetAddressbookNavigation')

    def SetAddressbookSearchSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self.__NumberOfAddressbookSearch
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            number = self.ReadStatus('AddressbookSearchResult', {'Button': value})
            if number not in ['***Not Available***', '***End of list***']:
                number = number[number.find(' : ') + 3:]
        else:
            print('Invalid Command for SetAddressbookSearchSet')

    def SetAddressbookUpdate(self, value, qualifier):

        self.SetAddressbookUpdateHandler(value, qualifier)

    def SetAddressbookUpdateHandler(self, value, qualifier):
        bookType = qualifier['Addressbook Type']
        print(value, bookType)
        if bookType == 'Local':
            searchStr = value
            if searchStr:
                AddressbookUpdateCmdString = 'addrbook search "{}"\r\n'.format(searchStr)
            else:
                AddressbookUpdateCmdString = 'addrbook local get all\r\n'

            res = self.SendAndWait(AddressbookUpdateCmdString, 10, deliTag=b'all done!')
            if res:
                self.nameList = []
                nameList = re.findall(self.LocalAddressResponsePattern, res.decode())
                length_tot = 0
                for x in range(0, len(nameList)):
                    number_list = re.findall(self.NoPattern, nameList[x][1])
                    length_tot = length_tot + len(number_list)
                    for j in range(0, len(number_list)):
                        self.nameList.append('{0} : {1}'.format(nameList[x][0], number_list[j]))

                searchMax = len(self.nameList)
                if searchMax > self.__NumberOfAddressbookSearch:
                    searchMax = self.__NumberOfAddressbookSearch
                button = 1
                for name in range(0, searchMax):
                    name = self.nameList[button - 1]
                    self.WriteStatus('AddressbookSearchResult', name, {'Button': button})
                    button = button + 1

                if button <= self.__NumberOfAddressbookSearch:
                    self.WriteStatus('AddressbookSearchResult', '***End of list***', {'Button': button})
                    button = button + 1
                    for i in range(button, self.__NumberOfAddressbookSearch + 1):
                        self.WriteStatus('AddressbookSearchResult', '', {'Button': i})
            else:
                self.__MatchNoContact(None, None)
        elif bookType == 'Conference':
            searchStr = value
            if searchStr:
                AddressbookUpdateCmdString = 'addrbook search "{}"\r\n'.format(searchStr)
            else:
                AddressbookUpdateCmdString = 'addrbook conf get all\r\n'

            res = self.SendAndWait(AddressbookUpdateCmdString, 10, deliTag=b'all done!')
            if res:
                self.nameList = []
                nameList = re.findall(self.ConfAddressResponsePattern, res.decode())
                length_tot = 0
                for x in range(0, len(nameList)):
                    number_list = re.findall(self.NoPattern, nameList[x][1])
                    length_tot = length_tot + len(number_list)
                    namenew = '{0} : {1}'.format(nameList[x][0], number_list[0])
                    for j in range(1, len(number_list)):
                        namenew = ''.join([namenew, ' ', number_list[j]])
                    self.nameList.append(namenew)

                searchMax = len(self.nameList)
                if searchMax > self.__NumberOfAddressbookSearch:
                    searchMax = self.__NumberOfAddressbookSearch
                button = 1
                for name in range(0, searchMax):
                    name = self.nameList[button - 1]
                    self.WriteStatus('AddressbookSearchResult', name, {'Button': button})
                    button = button + 1

                if button <= self.__NumberOfAddressbookSearch:
                    self.WriteStatus('AddressbookSearchResult', '***End of list***', {'Button': button})
                    button = button + 1
                    for i in range(button, self.__NumberOfAddressbookSearch + 1):
                        self.WriteStatus('AddressbookSearchResult', '', {'Button': i})
            else:
                self.__MatchNoContact(None, None)
        else:
            self.Discard('Invalid Command')

    def __MatchNoContact(self, match, tag):
        button = 1
        self.Advance = False
        self.WriteStatus('AddressbookSearchResult', '***Not Available***', {'Button': button})
        button = button + 1
        for i in range(button, int(self.__NumberOfAddressbookSearch) + 1):
            self.WriteStatus('AddressbookSearchResult', '', {'Button': i})

    def SetAnswer(self, value, qualifier):

        ValueStateValues = {
            'Yes': 'answer yes\r\n',
            'No': 'answer no\r\n'
        }

        AnswerCmdString = ValueStateValues[value]
        self.__SetHelper('Answer', AnswerCmdString, value, qualifier)

    def SetButtons(self, value, qualifier):

        ButtonsCmdString = self.ButtonValues[value]
        self.__SetHelper('Buttons', ButtonsCmdString, value, qualifier)

    def SetCameraNearMove(self, value, qualifier):

        ValueStateValues = {
            'Up': 'camera near move up\r\n',
            'Down': 'camera near move down\r\n',
            'Left': 'camera near move left\r\n',
            'Right': 'camera near move right\r\n',
            'Zoom +': 'camera near move zoom+\r\n',
            'Zoom -': 'camera near move zoom-\r\n',
            'Stop': 'camera near move stop\r\n'
        }
        ValueStateValuesID = {
            'Up':        'camera near move_id "id:{0}" "direct:4"\r\n',
            'Down':      'camera near move_id "id:{0}" "direct:2"\r\n',
            'Left':      'camera near move_id "id:{0}" "direct:8"\r\n',
            'Right':     'camera near move_id "id:{0}" "direct:6"\r\n',
            'Stop':      'camera near move_id "id:{0}" stop\r\n',
            'Zoom +':    'camera near zoom_id "id:{0}" "direct:1"\r\n',
            'Zoom -':    'camera near zoom_id "id:{0}" "direct:0"\r\n',
            'Zoom Stop': 'camera near zoom_id "id:{0}" stop\r\n'
        }

        if qualifier and 'ID' in qualifier:
            id_val = int(qualifier['ID'])
            if 1 <= id_val <= 9:
                CameraNearMoveCmdString = ValueStateValuesID[value].format(id_val)
                self.__SetHelper('CameraNearMove', CameraNearMoveCmdString, value, qualifier)
        else:
            CameraNearMoveCmdString = ValueStateValues[value]
            self.__SetHelper('CameraNearMove', CameraNearMoveCmdString, value, qualifier)

    def SetDialCommand(self, value, qualifier):

        number = value
        if number:
            if ' ' in number:
                number_list = number.split()
                length = len(number_list)
                joined_list = number_list[0]
                for i in range(1, length):
                    joined_list = '" "'.join([joined_list, number_list[i]])
            else:
                joined_list = number

            DialCommandCmdString = 'dial auto "{0}"\r\n'.format(joined_list)
            self.__SetHelper('DialCommand', DialCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDialCommand')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': 'donotdisturb global on\r\n',
            'Off': 'donotdisturb global off\r\n'
        }

        DoNotDisturbCmdString = ValueStateValues[value]
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbCmdString = 'donotdisturb global get\r\n'
        self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMFDialingTones(self, value, qualifier):

        ValueStateValues = {
            '0': 'gendial 0\r\n', 
            '1': 'gendial 1\r\n', 
            '2': 'gendial 2\r\n', 
            '3': 'gendial 3\r\n', 
            '4': 'gendial 4\r\n', 
            '5': 'gendial 5\r\n', 
            '6': 'gendial 6\r\n', 
            '7': 'gendial 7\r\n', 
            '8': 'gendial 8\r\n', 
            '9': 'gendial 9\r\n', 
            '*': 'gendial *\r\n', 
            '#': 'gendial #\r\n'
        }

        DTMFDialingTonesCmdString = ValueStateValues[value]
        self.__SetHelper('DTMFDialingTones', DTMFDialingTonesCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Camera': 'inputsource camera\r\n',
            'PC': 'inputsource pc\r\n',
            'Camera + PC': 'inputsource share\r\n'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'mute near on\r\n',
            'Off': 'mute near off\r\n'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'mute near get\r\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetNumberButtons(self, value, qualifier):

        ValueStateValues = {
            '0': 'button 0\r\n', 
            '1': 'button 1\r\n', 
            '2': 'button 2\r\n', 
            '3': 'button 3\r\n', 
            '4': 'button 4\r\n', 
            '5': 'button 5\r\n', 
            '6': 'button 6\r\n', 
            '7': 'button 7\r\n', 
            '8': 'button 8\r\n', 
            '9': 'button 9\r\n', 
            '*': 'button *\r\n', 
            '#': 'button #\r\n'
        }

        NumberButtonsCmdString = ValueStateValues[value]
        self.__SetHelper('NumberButtons', NumberButtonsCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '0': 'preset near go 0\r\n',
            '1': 'preset near go 1\r\n',
            '2': 'preset near go 2\r\n',
            '3': 'preset near go 3\r\n',
            '4': 'preset near go 4\r\n',
            '5': 'preset near go 5\r\n',
            '6': 'preset near go 6\r\n',
            '7': 'preset near go 7\r\n',
            '8': 'preset near go 8\r\n',
            '9': 'preset near go 9\r\n'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '0': 'preset near set 0\r\n',
            '1': 'preset near set 1\r\n',
            '2': 'preset near set 2\r\n',
            '3': 'preset near set 3\r\n',
            '4': 'preset near set 4\r\n',
            '5': 'preset near set 5\r\n',
            '6': 'preset near set 6\r\n',
            '7': 'preset near set 7\r\n',
            '8': 'preset near set 8\r\n',
            '9': 'preset near set 9\r\n'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def UpdateSystemStatus(self, value, qualifier):

        SystemStatusCmdString = 'sysstatus get\r\n'
        self.__UpdateHelper('SystemStatus', SystemStatusCmdString, value, qualifier)

    def __MatchSystemStatus(self, match, tag):

        ValueStateValues = {
            'sleeping': 'Sleeping',
            'idle': 'Idle',
            'outgoing': 'Outgoing',
            'ringing': 'Ringing',
            'talking': 'Talking',
            'finished': 'Finished',
            'talking max': 'Talking Max'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SystemStatus', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'volume set {0}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume get\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User'] or 'Serial' in self.ConnectionType:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command: Authentication was not met')


    def __MatchError(self, match, tag):

        value = ''.join(['Error occurred: ', match.group(1).decode()])
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    def yea_12_2394_500_800_880(self):
        self.ButtonValues = {
            'Power': 'button power\r\n',
            'F1': 'button F1\r\n',
            'F2': 'button F2\r\n',
            'F3': 'button F3\r\n',
            'Volume +': 'button volume+\r\n',
            'Volume -': 'button volume-\r\n',
            'Zoom +': 'button zoom+\r\n',
            'Zoom -': 'button zoom-\r\n',
            'Up': 'button up\r\n',
            'Down': 'button down\r\n',
            'Left': 'button left\r\n',
            'Right': 'button right\r\n',
            'Select': 'button select\r\n',
            'Mute': 'button mute\r\n',
            'Home': 'button home\r\n',
            'Back': 'button back\r\n',
            'Call': 'button call\r\n',
            'Delete': 'button delete\r\n',
            'Hangup': 'button hangup\r\n',
            'Record Start': 'button recordstart\r\n',
            'Record Stop': 'button recordstop\r\n',
            'Screenshot': 'button screenshot\r\n'
        }

    def yea_12_2394_other(self):
        self.ButtonValues = {
            'Power': 'button power\r\n',
            'F1': 'button F1\r\n',
            'F2': 'button F2\r\n',
            'F3': 'button F3\r\n',
            'Volume +': 'button volume+\r\n',
            'Volume -': 'button volume-\r\n',
            'Zoom +': 'button zoom+\r\n',
            'Zoom -': 'button zoom-\r\n',
            'Up': 'button up\r\n',
            'Down': 'button down\r\n',
            'Left': 'button left\r\n',
            'Right': 'button right\r\n',
            'Select': 'button select\r\n',
            'Mute': 'button mute\r\n',
            'Home': 'button home\r\n',
            'Show': 'button show\r\n',
            'Call': 'button call\r\n',
            'Delete': 'button delete\r\n',
            'Hangup': 'button hangup\r\n',
            'Record Start': 'button recordstart\r\n',
            'Record Stop': 'button recordstop\r\n',
            'Screenshot': 'button screenshot\r\n'
        }


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
