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
        self._DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ButtonandIRControl': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'VolumeStatus': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x77\x30\x30([0123])\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x69\x30\x30(0|1)\x0D'), self.__MatchButtonandIRControl,
                                None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x6A([01][02][012])\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x67\x30\x30(0|1)\x0D'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x6C\x30\x30([012])\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x72\x66([01][0-9]{2})\x0D'), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'\x38[0-9]{2}\x2D[\x00-\xFF]{4}\x0D'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if value == 'Broadcast':  # Broadcast
                self._DeviceID = b'\x39\x39'
            elif 0 < int(value) < 99:
                self._DeviceID = bytes('{0:02d}'.format(int(value)), 'utf-8')
            else:
                self.Error(
                    'Driver level parameter DeviceID is set to an invalid value. It should be a number between 1 to 98 or Broadcast')
        except KeyError:
            self.Error('Missing DeviceID Parameter.')
        except TypeError:
            self.Error('DeviceID Parameter is the wrong type.')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Default': b'\x30',
            '16:9': b'\x31',
            '4:3': b'\x32',
            'Auto': b'\x33',
            'Panorama Mode': b'\x34',
            'Just Scan': b'\x35',
            '14:9': b'\x36',
            'PC Mode': b'\x37'
        }

        AspectRatioCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x31\x30\x30', ValueStateValues[value], b'\x0D'])
        if value != 'Panorama Mode' or value != 'Just Scan' or value != '14:9' or value != 'PC Mode':
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b''.join([b'\x38', self.DeviceID, b'\x67\x77\x30\x30\x30\x0D'])
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x30': 'Default',
            '\x31': '16:9',
            '\x32': '4:3',
            '\x33': 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetButtonandIRControl(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x31',
            'Disable': b'\x30'
        }

        ButtonandIRControlCmdString = b''.join(
            [b'\x38', self.DeviceID, b'\x73\x43\x30\x30', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('ButtonandIRControl', ButtonandIRControlCmdString, value, qualifier)

    def UpdateButtonandIRControl(self, value, qualifier):

        ButtonandIRControlCmdString = b''.join([b'\x38', self.DeviceID, b'\x67\x69\x30\x30\x30\x0D'])
        self.__UpdateHelper('ButtonandIRControl', ButtonandIRControlCmdString, value, qualifier)

    def __MatchButtonandIRControl(self, match, tag):

        ValueStateValues = {
            '\x31': 'Enable',
            '\x30': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonandIRControl', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x21\x30\x30\x33\x0D'])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x30\x30\x30',
            'HDMI 1': b'\x30\x30\x31',
            'HDMI 2': b'\x30\x30\x32',
            'HDMI 3': b'\x30\x32\x31',
            'HDMI 4': b'\x30\x32\x32',
            'Android': b'\x31\x30\x31',
            'OPS': b'\x31\x30\x32'
        }

        InputCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x22', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b''.join([b'\x38', self.DeviceID, b'\x67\x6A\x30\x30\x30\x0D'])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x30\x30\x30': 'VGA',
            '\x30\x30\x31': 'HDMI 1',
            '\x30\x30\x32': 'HDMI 2',
            '\x30\x32\x31': 'HDMI 3',
            '\x30\x32\x32': 'HDMI 4',
            '\x31\x30\x31': 'Android',
            '\x31\x30\x32': 'OPS'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x31\x30',
            'Down': b'\x31\x31',
            'Left': b'\x31\x32',
            'Right': b'\x31\x33',
            'Ok': b'\x31\x34',
            'Menu': b'\x32\x30',
            'Exit': b'\x32\x32'
        }

        MenuNavigationCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x40\x30', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x36\x30\x30\x02\x0D'])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteStatusCmdString = b''.join([b'\x38', self.DeviceID, b'\x67\x67\x30\x30\x30\x0D'])
        self.__UpdateHelper('Mute', MuteStatusCmdString, value, qualifier)

    def __MatchMute(self, match, tag):
        ValueStateValues = {
            '\x31': 'On',
            '\x30': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30',
            'Android Off': b'\x32'
        }

        PowerCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x21\x30\x30', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b''.join([b'\x38', self.DeviceID, b'\x37\x6C\x30\x30\x30\x0D'])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x31': 'On',
            '\x30': 'Off',
            '\x32': 'Android Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = b''.join([b'\x38', self.DeviceID, b'\x67\x66\x30\x30\x30\x0D'])
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VolumeStatus', value, None)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x33',
            'Down': b'\x32'
        }

        VolumeStepCmdString = b''.join([b'\x38', self.DeviceID, b'\x73\x35', ValueStateValues[value], b'\x30\x30\x0D'])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == b'\x39\x39':
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

        self.Error(['Invalid command condition.'])

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

