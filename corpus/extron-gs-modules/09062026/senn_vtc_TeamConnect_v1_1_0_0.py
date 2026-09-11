from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
        self.devicePassword = None
        self.deviceUsername = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'DTMFDialing': {'Parameters': ['Channel'], 'Status': {}},
            'Hook': {'Status': {}},
            'HookFlash': {'Parameters': ['Channel'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Channel'], 'Status': {}},
            'LineInputMute': {'Parameters': ['Channel'], 'Status': {}},
            'MicrophoneGain': {'Parameters': ['Channel'], 'Status': {}},
            'MicrophoneMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputGain': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'Preset': {'Status': {}},
            'ReceiveGain': {'Status': {}},
            'ReceiveMute': {'Status': {}},
            'Redial': {'Parameters': ['Channel'], 'Status': {}},
            'RingerEnable': {'Status': {}},
            'RingIndication': {'Status': {}},
            'SpeedDial': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitGain': {'Status': {}},
            'TransmitMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'user:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'pass:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'OK> #K0 AA 1 (0|1)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'OK> #K0 TE 1 (0|1)\r\n'), self.__MatchHook, None)
            self.AddMatchString(compile(b'OK> #K0 GAIN (1|2) L (-?[0-9]{1,2}\.[0-9]{1,2}).*\r\n'), self.__MatchLineInputGain, None)
            self.AddMatchString(compile(b'OK> #K0 MUTE (1|2) L (0|1)\r\n'), self.__MatchLineInputMute, None)
            self.AddMatchString(compile(b'OK> #K0 GAIN ([1-8]) M (-?[0-9]{1,2}\.[0-9]{1,2}).*\r\n'), self.__MatchMicrophoneGain, None)
            self.AddMatchString(compile(b'OK> #K0 MUTE ([1-8]) M (0|1)\r\n'), self.__MatchMicrophoneMute, None)
            self.AddMatchString(compile(b'OK> #K0 GAIN ([1-8]) O (-?[0-9]{1,2}\.[0-9]{1,2}).*\r\n'), self.__MatchOutputGain, None)
            self.AddMatchString(compile(b'OK> #K0 MUTE ([1-8]) O (0|1)\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(compile(b'OK> #K0 GAIN 1 R (-?[0-9]{1,2}\.[0-9]{1,2}).*\r\n'), self.__MatchReceiveGain, None)
            self.AddMatchString(compile(b'OK> #K0 MUTE 1 R (0|1)\r\n'), self.__MatchReceiveMute, None)
            self.AddMatchString(compile(b'OK> #K0 RING 1 (0|1)\r\n'), self.__MatchRingIndication, None)
            self.AddMatchString(compile(b'OK> #K0 RINGEREN 1 (0|1)\r\n'), self.__MatchRingerEnable, None)
            self.AddMatchString(compile(b'OK> #K0 GAIN 1 T (-?[0-9]{1,2}\.[0-9]{1,2}).*\r\n'), self.__MatchTransmitGain, None)
            self.AddMatchString(compile(b'OK> #K0 MUTE 1 T (0|1)\r\n'), self.__MatchTransmitMute, None)
            self.AddMatchString(compile(b'OK> #K0 ERROR (Memory error|No command found|Unknown command response|Not implemented|Argument error|Unknown command)\.'), self.__MatchError, None)

    def __MatchLogin(self, match, tag):
        if self.deviceUsername:
            self.Send(self.deviceUsername + '\r')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send(self.devicePassword + '\r')
        else:
            self.MissingCredentialsLog('Password')

    def SetAutoAnswer(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '#.. AA 1 {0}\r'.format(States[value])
        self.__SetHelper('AutoAnswer', CmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        self.__UpdateHelper('AutoAnswer', '#.. AA 1?\r', value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('AutoAnswer', States[match.group(1).decode()], None)

    def SetDTMFDialing(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        DialString = value

        if DialString != '' and 1 <= len(DialString) <= 44 and 1 <= Channel <= 8:
            CmdString = '#.. DIAL {0} {1}\r'.format(Channel, DialString)
            self.__SetHelper('DTMFDialing', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMFDialing')

    def SetHook(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0',
        }

        CmdString = '#.. TE 1 {0}\r'.format(States[value])
        self.__SetHelper('Hook', CmdString, value, qualifier)

    def UpdateHook(self, value, qualifier):
        self.__UpdateHelper('Hook', '#.. TE 1?\r', value, qualifier)

    def __MatchHook(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Hook', States[match.group(1).decode()], None)

    def SetHookFlash(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if 1 <= Channel <= 8:
            CmdString = '#.. Hook {0}\r'.format(Channel)
            self.__SetHelper('HookFlash', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHookFlash')

    def SetLineInputGain(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if -65 <= value <= 20 and 1 <= Channel <= 2:
            CmdString = '#.. GAIN {0} L {1:0.2f} A\r'.format(Channel, value)
            self.__SetHelper('LineInputGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 2:
            CmdString = '#.. GAIN {0} L?\r'.format(Channel)
            self.__UpdateHelper('LineInputGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineInputGain')

    def __MatchLineInputGain(self, match, tag):
        self.WriteStatus('LineInputGain', float(match.group(2)), {'Channel': match.group(1).decode()})

    def SetLineInputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        States = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= Channel <= 2:
            CmdString = '#.. MUTE {0} L {1}\r'.format(Channel, States[value])
            self.__SetHelper('LineInputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputMute')

    def UpdateLineInputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 2:
            CmdString = '#.. MUTE {0} L?\r'.format(Channel)
            self.__UpdateHelper('LineInputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineInputMute')

    def __MatchLineInputMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('LineInputMute', States[match.group(2).decode()], {'Channel': match.group(1).decode()})

    def SetMicrophoneGain(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if -65 <= value <= 20 and 1 <= Channel <= 8:
            CmdString = '#.. GAIN {0} M {1:0.2f} A\r'.format(Channel, value)
            self.__SetHelper('MicrophoneGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneGain')

    def UpdateMicrophoneGain(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if 1 <= Channel <= 8:
            CmdString = '#.. GAIN {0} M?\r'.format(Channel)
            self.__UpdateHelper('MicrophoneGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneGain')

    def __MatchMicrophoneGain(self, match, tag):
        self.WriteStatus('MicrophoneGain', float(match.group(2)), {'Channel': match.group(1).decode()})

    def SetMicrophoneMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        States = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= Channel <= 8:
            CmdString = '#.. MUTE {0} M {1}\r'.format(Channel, States[value])
            self.__SetHelper('MicrophoneMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMute')

    def UpdateMicrophoneMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if 1 <= Channel <= 8:
            CmdString = '#.. MUTE {0} M?\r'.format(Channel)
            self.__UpdateHelper('MicrophoneMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneMute')

    def __MatchMicrophoneMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('MicrophoneMute', States[match.group(2).decode()], {'Channel': match.group(1).decode()})

    def SetOutputGain(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if -65 <= value <= 20 and 1 <= Channel <= 8:
            CmdString = '#.. GAIN {0} O {1:0.2f} A\r'.format(Channel, value)
            self.__SetHelper('OutputGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):
        Channel = int(qualifier['Channel'])
        if 1 <= Channel <= 8:
            CmdString = '#.. GAIN {0} O?\r'.format(Channel)
            self.__UpdateHelper('OutputGain', CmdString, value, qualifier)

    def __MatchOutputGain(self, match, tag):
        self.WriteStatus('OutputGain', float(match.group(2)), {'Channel': match.group(1).decode()})

    def SetOutputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        States = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= Channel <= 8:
            CmdString = '#.. MUTE {0} O {1}\r'.format(Channel, States[value])
            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if 1 <= Channel <= 8:
            CmdString = '#.. MUTE {0} O?\r'.format(Channel)
            self.__UpdateHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('OutputMute', States[match.group(2).decode()], {'Channel': match.group(1).decode()})

    def SetPreset(self, value, qualifier):

        States = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        CmdString = '#.. CPRESET {0}\r'.format(States[value])
        self.__SetHelper('Preset', CmdString, value, qualifier)

    def SetReceiveGain(self, value, qualifier):

        if -65 <= value <= 20:
            CmdString = '#.. GAIN 1 R {0:0.2f} A\r'.format(value)
            self.__SetHelper('ReceiveGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReceiveGain')

    def UpdateReceiveGain(self, value, qualifier):
        self.__UpdateHelper('ReceiveGain', '#.. GAIN 1 R?\r', value, qualifier)

    def __MatchReceiveGain(self, match, tag):
        self.WriteStatus('ReceiveGain', float(match.group(1)), None)

    def SetReceiveMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '#.. MUTE 1 R {0}\r'.format(States[value])
        self.__SetHelper('ReceiveMute', CmdString, value, qualifier)

    def UpdateReceiveMute(self, value, qualifier):
        self.__UpdateHelper('ReceiveMute', '#.. MUTE 1 R?\r', value, qualifier)

    def __MatchReceiveMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('ReceiveMute', States[match.group(1).decode()], None)

    def SetRedial(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 1 <= Channel <= 8:
            CmdString = '#.. REDIAL {0}\r'.format(Channel)
            self.__SetHelper('Redial', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRedial')

    def SetRingerEnable(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '#.. RINGEREN 1 R {0}\r'.format(States[value])
        self.__SetHelper('RingerEnable', CmdString, value, qualifier)

    def UpdateRingerEnable(self, value, qualifier):
        self.__UpdateHelper('RingerEnable', '#.. RINGEREN 1 R?\r', value, qualifier)

    def __MatchRingerEnable(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('RingerEnable', States[match.group(1).decode()], None)

    def __MatchRingIndication(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('RingIndication', States[match.group(1).decode()], None)

    def SetSpeedDial(self, value, qualifier):

        Channel = int(qualifier['Channel'])
        if 1 <= int(value) <= 34 and 1 <= Channel <= 8:
            CmdString = '#.. SPEEDDIAL {0} {1}\r'.format(Channel, value)
            self.__SetHelper('SpeedDial', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedDial')

    def SetTransmitGain(self, value, qualifier):

        if -65 <= value <= 20:
            CmdString = '#.. GAIN 1 T {0:0.2f} A\r'.format(value)
            self.__SetHelper('TransmitGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitGain')

    def UpdateTransmitGain(self, value, qualifier):
        self.__UpdateHelper('TransmitGain', '#.. GAIN 1 T?\r', value, qualifier)

    def __MatchTransmitGain(self, match, tag):
        self.WriteStatus('TransmitGain', float(match.group(1)), None)

    def SetTransmitMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '#.. MUTE 1 T {0}\r'.format(States[value])
        self.__SetHelper('TransmitMute', CmdString, value, qualifier)

    def UpdateTransmitMute(self, value, qualifier):
        self.__UpdateHelper('TransmitMute', '#.. MUTE 1 T?\r', value, qualifier)

    def __MatchTransmitMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('TransmitMute', States[match.group(1).decode()], None)

    def __MatchError(self, match, tag):
        self.Error([match.group(1).decode()])

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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
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
                result = search(regexString, self._ReceiveBuffer)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
