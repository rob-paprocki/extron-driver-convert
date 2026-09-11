from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'innkeeper 2': self.jka_25_3109_2,
            'innkeeper 4': self.jka_25_3109_4,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Parameters': ['Line'], 'Status': {}},
            'Conference': {'Status': {}},
            'DialPhoneNumber': {'Parameters': ['Line'], 'Status': {}},
            'Escape': {'Status': {}},
            'Level': {'Parameters': ['Line', 'Type'], 'Status': {}},
            'LineControl': {'Parameters': ['Line'], 'Status': {}},
            'LineState': {'Parameters': ['Line'], 'Status': {}},
            'MasterSend': {'Parameters': ['Line'], 'Status': {}},
            'PhoneBook': {'Status': {}},
            'RingCount': {'Parameters': ['Line'], 'Status': {}},
            'Version': {'Status': {}}
        }

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        line = self.LineStates[qualifier['Line']]
        AutoAnswerCmdString = '/L{0}AA{1}\r'.format(line, ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def SetConference(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ConferenceCmdString = '/CN{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Conference', ConferenceCmdString, value, qualifier)

    def SetDialPhoneNumber(self, value, qualifier):

        line = self.LineStates[qualifier['Line']]
        DialPhoneNumberCmdString = '/L{0}DI{1}\r'.format(line, value)
        self.__SetHelper('DialPhoneNumber', DialPhoneNumberCmdString, value, qualifier)

    def SetEscape(self, value, qualifier):

        EscapeCmdString = 'Esc\r'
        self.__SetHelper('Escape', EscapeCmdString, value, qualifier)

    def SetLevel(self, value, qualifier):

        TypeStates = {
            'Send': 'S',
            'Receive': 'R'
        }

        ValueConstraints = {
            'Min': -10,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            line = self.LineStates[qualifier['Line']]
            LevelCmdString = '/L{0}{1}L{2}\r'.format(line, TypeStates[qualifier['Type']], value)
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')

    def SetLineControl(self, value, qualifier):

        ValueStateValues = {
            'Call Line': 'CL',
            'Drop Line': 'DR',
            'On Hold': 'HD1',
            'Off Hold': 'HD0'
        }

        line = self.LineStates[qualifier['Line']]
        LineControlCmdString = '/L{0}{1}\r'.format(line, ValueStateValues[value])
        self.__SetHelper('LineControl', LineControlCmdString, value, qualifier)

    def UpdateLineControl(self, value, qualifier):
        self.UpdateLineState(value, qualifier)

    def UpdateLineState(self, value, qualifier):

        ValueStateValues = {
            '0': 'On-hook',
            '1': 'Off-hook',
            '2': 'Ring',
            '3': 'Hold'
        }
        LineControlValues = {
            '0': 'Drop Line',
            '1': 'Call Line',
            '2': 'Drop Line',
            '3': 'On Hold'
        }
        line = self.LineStates[qualifier['Line']]
        LineStateCmdString = '/L{0}ST\r'.format(line)
        res = self.__UpdateHelper('LineState', LineStateCmdString, value, qualifier)
        if res:
            try:
                line = res[1]
                value = ValueStateValues[res[2]]
                control = LineControlValues[res[2]]
                self.WriteStatus('LineState', value, {'Line': line})
                self.WriteStatus('LineControl', control, {'Line': line})
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Line State')])

    def SetMasterSend(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        line = self.LineStates[qualifier['Line']]
        MasterSendCmdString = '/L{0}MS{1}\r'.format(line, ValueStateValues[value])
        self.__SetHelper('MasterSend', MasterSendCmdString, value, qualifier)

    def SetPhoneBook(self, value, qualifier):

        ValueStateValues = {
            'Download': '1',
            'Upload': '0'
        }

        PhoneBookCmdString = '/PB{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PhoneBook', PhoneBookCmdString, value, qualifier)

    def SetRingCount(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }
        line = self.LineStates[qualifier['Line']]
        RingCountCmdString = '/L{0}AR{1}\r'.format(line, ValueStateValues[value])
        self.__SetHelper('RingCount', RingCountCmdString, value, qualifier)

    def UpdateVersion(self, value, qualifier):

        VersionCmdString = '/AT\r'
        res = self.__UpdateHelper('Version', VersionCmdString, value, qualifier)
        if res:
            try:
                value = res
                self.WriteStatus('Version', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Version')])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def jka_25_3109_4(self):
        self.LineStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

    def jka_25_3109_2(self):
        self.LineStates = {
            '1': '1',
            '2': '2'
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
