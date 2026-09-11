from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'DiscType': {'Status': {}},
            'Eject': {'Status': {}},
            'MenuCall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberPad': {'Status': {}},
            'Power': {'Status': {}},
            'Random': {'Status': {}},
            'Repeat': {'Status': {}},
            'Transport': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9 Wide': '@ASP:2\r',
            '4:3 Pan Scan': '@ASP:0\r',
            '4:3 LetterBox': '@ASP:1\r',
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '2': '16:9 Wide',
            '0': '4:3 Pan Scan',
            '1': '4:3 LetterBox',
        }

        AspectRatioCmdString = '@ASP:?\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected response'])

    def UpdateDiscType(self, value, qualifier):

        ValueStateValues = {
            '0': 'No Disc',
            '1': 'CD',
            '2': 'VCD',
            '3': 'DVD Video',
            '4': 'DVD Audio',
            '5': 'SACD',
            '6': 'MP3,JPEG,WMA,DivX',
        }

        DiscTypeCmdString = '@KOD:?\r'
        res = self.__UpdateHelper('DiscType', DiscTypeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('DiscType', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Disc Type: Invalid/Unexpected response'])

    def SetEject(self, value, qualifier):

        ValueStateValues = {
            'Open': '@TRY:1\r',
            'Close': '@TRY:2\r',
        }

        EjectCmdString = ValueStateValues[value]
        self.__SetHelper('Eject', EjectCmdString, value, qualifier)

    def UpdateEject(self, value, qualifier):

        ValueStateValues = {
            '1': 'Open',
            '2': 'Close',
        }

        EjectCmdString = '@TRY:?\r'
        res = self.__UpdateHelper('Eject', EjectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Eject', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eject: Invalid/Unexpected response'])

    def SetMenuCall(self, value, qualifier):

        ValueStateValues = {
            'On/Off': '@MNU:0\r',
            'Top Menu': '@MN:0\r',
            'Return': '@RTN:0\r',
        }

        MenuCallCmdString = ValueStateValues[value]
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': '@CUR:3\r',
            'Right': '@CUR:2\r',
            'Up': '@CUR:0\r',
            'Down': '@CUR:1\r',
            'Enter': '@ENT:0\r',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberPad(self, value, qualifier):

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
        }

        NumberPadCmdString = '@NUM:{}\r'.format(ValueStateValues[value])
        self.__SetHelper('NumberPad', NumberPadCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '@PWR:2\r',
            'Off': '@PWR:1\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        PowerCmdString = '@PWR:?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected response'])

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'On': '@RDM:2\r',
            'Off': '@RDM:1\r',
            'Repeat': '@RDM:3\r',
        }

        RandomCmdString = ValueStateValues[value]
        self.__SetHelper('Random', RandomCmdString, value, qualifier)

    def UpdateRandom(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '3': 'Repeat',
        }

        RandomCmdString = '@RDM:?\r'
        res = self.__UpdateHelper('Random', RandomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Random', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Random: Invalid/Unexpected response'])

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Track/Chapter': '@REP:2\r',
            'Title/Group': '@REP:3\r',
            'All': '@REP:4\r',
            'Off': '@REP:1\r',
        }

        RepeatCmdString = ValueStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        ValueStateValues = {
            '2': 'Track/Chapter',
            '3': 'Title/Group',
            '4': 'All',
            '1': 'Off',
        }

        RepeatCmdString = '@REP:?\r'
        res = self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Repeat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Repeat: Invalid/Unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@PMD:3\r',
            'Pause': '@PMD:2\r',
            'Stop': '@PMD:1\r',
            'Next': '@GOT:0\r',
            'Previous': '@GOT:1\r',
            'Fast Forward': '@PMD:6\r',
            'Fast Reverse': '@PMD:7\r',
            'Resume Stop': '@PMD:0\r',
            'Slow Forward': '@PMD:4\r',
            'Slow Reverse': '@PMD:5\r',
        }
        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        ValueStateValues = {
            '3': 'Play',
            '2': 'Pause',
            '1': 'Stop',
            '6': 'Fast Forward',
            '7': 'Fast Reverse',
            '0': 'Resume Stop',
            '4': 'Slow Forward',
            '5': 'Slow Reverse',
        }

        TransportCmdString = '@PMD:?\r'
        res = self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Transport', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Transport: Invalid/Unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response == '@\x15\r':
                self.Error(['{0}: {1}'.format(sourceCmdName, 'Received incorrect Command data')])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/Unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
