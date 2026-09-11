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
            'Beep': {'Status': {}},
            'Dock': {'Status': {}},
            'DockStatus': {'Status': {}},
            'HomeButtonStatus': {'Status': {}},
            'Led': {'Parameters': ['Led'], 'Status': {}},
            'ProximitySensorStatus': {'Status': {}},
            'QuickAccessButtonStatus': {'Parameters': ['Button'], 'Status': {}},
            'QuickDigitalInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'Reboot': {'Status': {}},
            'Relay': {'Status': {}},
            'RelayStatus': {'Status': {}},
            'RequiredCommand': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'inf:dockingstate:(docking|undocking|docked|undocked);'), self.__MatchDockStatus, None)
            self.AddMatchString(re.compile(b'inf:led([0-8]):([0-9]{1,3});'), self.__MatchLed, None)
            self.AddMatchString(re.compile(b'evn:button0:(pushed|released);'), self.__MatchHomeButtonStatus, None)
            self.AddMatchString(re.compile(b'evn:irevent:([01]);'), self.__MatchProximitySensorStatus, None)
            self.AddMatchString(re.compile(b'evn:button([1-8]):(pushed|released);'), self.__MatchQuickAccessButtonStatus, None)
            self.AddMatchString(re.compile(b'evn:digital([0-8]):(closed|opened);'), self.__MatchQuickDigitalInputStatus, None)
            self.AddMatchString(re.compile(b'inf:relay0:(opened|closed);'), self.__MatchRelayStatus, None)
            self.AddMatchString(re.compile(b'inf:alive:1;'), self.__MatchRequiredCommand, None)

    def SetInitialize(self, value, qualifier):
        InitCmdString = 'req:infupdate:standard;'
        self.Send(InitCmdString)

    def SetBeep(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.1,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BeepCmdString = 'cmd:beep:{0};'.format(int(value * 10))
            self.__SetHelper('Beep', BeepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeep')

    def SetDock(self, value, qualifier):

        ValueStateValues = {
            'Open': 'cmd:idock:open;',
            'Close': 'cmd:idock:close;',
        }

        if value in ValueStateValues:
            DockCmdString = ValueStateValues[value]
            self.__SetHelper('Dock', DockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDock')

    def __MatchDockStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DockStatus', value.title(), None)

    def SetLed(self, value, qualifier):

        LedStates = {
            'Home': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        Led = qualifier['Led']
        if Led in LedStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LedCmdString = 'cmd:led{0}:{1};'.format(LedStates[Led], value)
            self.__SetHelper('Led', LedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLed')

    def __MatchLed(self, match, tag):

        Led = match.group(1).decode()
        if Led == '0':
            Led = 'Home'
        value = int(match.group(2).decode())
        self.WriteStatus('Led', value, {'Led': Led})

    def __MatchHomeButtonStatus(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('HomeButtonStatus', value, None)

    def __MatchProximitySensorStatus(self, match, tag):

        value = {'0': 'Idle', '1': 'Triggered'}[match.group(1).decode()]
        self.WriteStatus('ProximitySensorStatus', value, None)

    def __MatchQuickAccessButtonStatus(self, match, tag):

        value = match.group(2).decode().title()
        self.WriteStatus('QuickAccessButtonStatus', value, {'Button': match.group(1).decode()})

    def __MatchQuickDigitalInputStatus(self, match, tag):

        value = match.group(2).decode().title()
        self.WriteStatus('QuickDigitalInputStatus', value, {'Input': match.group(1).decode()})

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'req:reboot;'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRelay(self, value, qualifier):

        ValueStateValues = {
            'Open': 'cmd:relay0:open;',
            'Close': 'cmd:relay0:close;'
        }

        if value in ValueStateValues:
            RelayCmdString = ValueStateValues[value]
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def __MatchRelayStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('RelayStatus', value.title(), None)

    def UpdateRequiredCommand(self, value, qualifier):

        RequiredCommandCmdString = 'req:alive:1;'
        self.__UpdateHelper('RequiredCommand', RequiredCommandCmdString, value, qualifier)

    def __MatchRequiredCommand(self, match, tag):
        self.counter = 0

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetInitialize(None, None)

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
