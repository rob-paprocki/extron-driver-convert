from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
import time
from struct import pack, unpack

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Status': {}},
            'FocusMode': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'VideoSystem': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = time.monotonic()

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 'Serial' in self.ConnectionType:
            if 1 <= int(value) <= 7:
                self._DeviceID = 0x80 + int(value)
            else:
                print('DeviceID Parameter is out of range.')
        else:
            self._DeviceID = 0x81

    def SetResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def IncSequenceNumber(self):
        if self.StartSequence == 0:
            ctime = time.monotonic()
            if ctime - self.LastResetTime > 15:
                self.LastResetTime = time.monotonic()
                self.SetResetSequence(None, None)
            self.PrevSequence = 1
            Sequence = b'\x00\x00\x00\x01'
        else:
            self.PrevSequence = self.PrevSequence + 1 if self.PrevSequence < 4294967295 else 0
            Sequence = pack('>L', self.PrevSequence)
        return(Sequence)

    def SetHeader(self, commandstring):
        sequence = self.IncSequenceNumber()
        commandstring = b'\x01\x00\x00' + pack('B', len(commandstring)) + sequence + b'\x81' + commandstring[1:]
        return commandstring

    def GetHeader(self, commandstring):
        sequence = self.IncSequenceNumber()
        commandstring = b'\x01\x10\x00' + pack('B', len(commandstring)) + sequence + b'\x81' + commandstring[1:]
        return commandstring

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        BacklightCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 0x02,
            'Far': 0x03,
            'Stop': 0x00
        }

        FocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0x02,
            'Manual': 0x03
        }

        FocusModeCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'Auto',
            b'\x03': 'Manual'
        }

        FocusModeCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        IrisCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03]
        }

        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 20:
            PanTiltCmdString = pack('>9B', self._DeviceID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        PowerCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 9:
            cmdValue = int(value)
            PresetString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, cmdValue, 0xFF)
            self.__SetHelper('PresetRecall', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 9:
            cmdValue = int(value)
            PresetString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, cmdValue, 0xFF)
            self.__SetHelper('PresetSave', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVideoSystem(self, value, qualifier):

        ValueStateValues = {
            '1080P60': 0,
            '1080P50': 1,
            '1080i60': 2,
            '1080i50': 3,
            '720P60': 4,
            '720P50': 5,
            '1080P30': 6,
            '1080P25': 7,
            '720P30': 8,
            '720P25': 9,
            '1080P59.94': 10,
            '1080i59.94': 11,
            '720P59.94': 12,
            '1080P29.97': 13,
            '720P29.97': 14
        }

        VideoSystemCmdString = pack('>B4s2B', self._DeviceID, b'\x01\x06\x35\x00', ValueStateValues[value], 0xFF)
        self.__SetHelper('VideoSystem', VideoSystemCmdString, value, qualifier)

    def UpdateVideoSystem(self, value, qualifier):

        ValueStateValues = {
            0: '1080P60',
            1: '1080P50',
            2: '1080i60',
            3: '1080i50',
            4: '720P60',
            5: '720P50',
            6: '1080P30',
            7: '1080P25',
            8: '720P30',
            9: '720P25',
            10: '1080P59.94',
            11: '1080i59.94',
            12: '720P59.94',
            13: '1080P29.97',
            14: '720P29.97'
        }

        VideoSystemCmdString = pack('>B4s', self._DeviceID, b'\x09\x06\x23\xFF')
        res = self.__UpdateHelper('VideoSystem', VideoSystemCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('VideoSystem', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video System: Invalid/unexpected response'])

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0,
            '3000K': 1,
            '4000K': 2,
            'One Push Mode': 3,
            '5000K': 4,
            'Manual': 5,
            '6500K': 6
        }

        WhiteBalanceCmdString = pack('>B3s2B', self._DeviceID, b'\x01\x04\x35', ValueStateValues[value], 0xFF)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            1: '3000K',
            2: '4000K',
            3: 'One Push Mode',
            4: '5000K',
            5: 'Manual',
            6: '6500K'
        }

        WhiteBalanceCmdString = pack('>B4s', self._DeviceID, b'\x09\x04\x35\xFF')
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }
        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if (errorByte == 0x60) and (errorCode == 0x02):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte == 0x61) and (errorCode == 0x41):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if 'Serial' in self.ConnectionType:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            else:
                newcommandstring = self.SetHeader(commandstring)
                res = self.SendAndWait(newcommandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                if 'Serial' in self.ConnectionType:
                    res = self.__CheckResponseForErrors(command + ':', res)
                else:
                    res = self.__CheckResponseForErrors(command + ':', res[8:12])

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

            if 'Serial' in self.ConnectionType:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            else:
                newcommandstring = self.GetHeader(commandstring)
                res = self.SendAndWait(newcommandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                if 'Power' == command:
                    self.StartSequence = 0
                return ''
            else:
                self.StartSequence = 1
                if 'Serial' in self.ConnectionType:
                    return self.__CheckResponseForErrors(command + ':', res)
                else:
                    return self.__CheckResponseForErrors(command + ':', res[8:12])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' not in self.ConnectionType:
            self.SetResetSequence(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.StartSequence = 0

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
                    except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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