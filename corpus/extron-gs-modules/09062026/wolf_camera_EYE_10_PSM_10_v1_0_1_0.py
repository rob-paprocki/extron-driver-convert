from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'FrontPanelLock': {'Status': {}},
            'Iris': {'Parameters': ['Iris Speed'], 'Status': {}},
            'MemoryRecall': {'Status': {}},
            'MemorySave': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

        self.reg = re.compile(b'(\x00\xF1[\x10-\x22][\x00-\xFF])|([\x00-\xFF]{5})')

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\x00][\xF4][\x60][\x00-\xFF][\x00-\xFF](?P<value>[\x00-\x02])(?P<checksum>[\x00-\xFF])'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'[\x00][\xF7][\x60][\x00-\xFF][\x00-\xFF][\x00-\xFF][\x00-\xFF][\x00-\xFF](?P<value>[\x00-\x07])(?P<checksum>[\x00-\xFF])'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'[\x00][\xF2][\x60](?P<value>[\x00|\x01|\x02|\x03\x04|\xFF])(?P<checksum>[\x00-\xFF])'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'([\x00][\xF1][\x10|\x11|\x12|\x20|\x21|\x22])(?P<checksum>[\x00-\xFF])'), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        AutoFocusValues = {
            'Off': 0x50,
            'One Push': 0x51,
            'Continuous': 0x52,
        }
        CKS = 0xFF - ((0xF4 + AutoFocusValues[value]) & 0xFF)
        AutoFocusCmdString = pack('>BBBBB', 0x00, 0xF2, 0x02, AutoFocusValues[value], CKS)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        CKS = 0xFF - ((0xF4 + 0x60) & 0xFF)
        AutoFocusCmdString = pack('>BBBBB', 0x00, 0xF2, 0x02, 0x60, CKS)
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        AutoFocusNames = {
            '\x00': 'Off',
            '\x02': 'One Push',
            '\x01': 'Continuous',
        }
        value = AutoFocusNames[match.group('value').decode()]
        self.WriteStatus('AutoFocus', value, None)

    def SetAutoIris(self, value, qualifier):

        AutoIrisValues = {
            'Enable': 0x51,
            'Disable': 0x50,
        }
        CKS = 0xFF - ((0xF5 + AutoIrisValues[value]) & 0xFF)
        AutoIrisCmdString = pack('>BBBBB', 0x00, 0xF2, 0x03, AutoIrisValues[value], CKS)
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateAutoIris(self, value, qualifier):

        CKS = 0xFF - ((0xF5 + 0x60) & 0xFF)
        AutoIrisCmdString = pack('>BBBBB', 0x00, 0xF2, 0x03, 0x60, CKS)
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, tag):

        AutoIrisNames = {
            0: 'Disable',
            4: 'Enable',
        }
        value = AutoIrisNames[match.group('value')[0] & 0x04]
        self.WriteStatus('AutoIris', value, None)

    def SetDigitalZoom(self, value, qualifier):

        DigitalZoomValues = {
            'Enable': 0x51,
            'Disable': 0x50,
        }
        CKS = 0xFF - ((0xF3 + DigitalZoomValues[value]) & 0xFF)
        DigitalZoomCmdString = pack('>BBBBB', 0x00, 0xF2, 0x01, DigitalZoomValues[value], CKS)
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusValues = {
            'Far': 0x31,
            'Near': 0x21,
            'Stop': 0x10,
        }
        if 1 <= int(qualifier['Focus Speed']) <= 15:
            FocusSpeed = int(qualifier['Focus Speed'])
            if value == 'Far':
                CKS = 0xFF - ((0xF5 + 0x31 + FocusSpeed) & 0xFF)
                FocusCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x02, 0x31, FocusSpeed, CKS)
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
            elif value == 'Near':
                CKS = 0xFF - ((0xF5 + FocusValues[value] + FocusSpeed) & 0xFF)
                FocusCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x02, 0x21, FocusSpeed, CKS)
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
            else:
                CKS = 0xFF - ((0xF4 + 0x10) & 0xFF)
                FocusCmdString = pack('>BBBBB', 0x00, 0xF2, 0x02, 0x10, CKS)
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        FreezeValues = {
            'On': 0x10,
            'Off': 0x11,
        }
        CKS = 0xFF - ((0xF8 + FreezeValues[value]) & 0xFF)
        FreezeCmdString = pack('>BBBBB', 0x00, 0xF2, 0x06, FreezeValues[value], CKS)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        CKS = 0xFF - ((0xF8 + 0x60) & 0xFF)
        FreezeCmdString = pack('>BBBBB', 0x00, 0xF2, 0x06, 0x60, CKS)
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeNames = {
            b'\xFF': 'On',
            b'\x00': 'Off',
            b'\x01': 'Off',
            b'\x02': 'Off',
            b'\x03': 'Off',
            b'\x04': 'Off',
        }
        value = FreezeNames[match.group('value')]
        self.WriteStatus('Freeze', value, None)

    def SetFrontPanelLock(self, value, qualifier):

        FrontPanelLockValues = {
            'On': 0x60,
            'Off': 0x61,
        }
        CKS = 0xFF - ((0xF7 + FrontPanelLockValues[value]) & 0xFF)
        FrontPanelLockCmdString = pack('>BBBBB', 0x00, 0xF2, 0x05, FrontPanelLockValues[value], CKS)
        self.__SetHelper('FrontPanelLock', FrontPanelLockCmdString, value, qualifier)

    def UpdateFrontPanelLock(self, value, qualifier):

        FrontPanelLockStateNames = {
            0x02: 'On',
            0x01: 'Off'
        }
        CKS = 0xFF - ((0xF7 + 0x62) & 0xFF)
        FrontPanelLockCmdString = pack('>BBBBB', 0x00, 0xF2, 0x05, 0x62, CKS)
        res = self.__UpdateHelperSYNC('FrontPanelLock', FrontPanelLockCmdString, value, qualifier)
        if res:
            try:
                value = FrontPanelLockStateNames[int(res[3])]
                self.WriteStatus('FrontPanelLock', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFrontPanelLock')

    def SetIris(self, value, qualifier):

        IrisSpeed = qualifier['Iris Speed']
        if IrisSpeed == 'Slow':
            irspeed = 0x01
        elif IrisSpeed == 'Fast':
            irspeed = 0x02

        IrisValues = {
            'Open': 0x21,
            'Close': 0x31,
            'Stop': 0x10,
        }
        if value == 'Open':
            CKS = 0xFF - ((0xF6 + 0x21 + irspeed) & 0xFF)
            IrisCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x03, 0x21, irspeed, CKS)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        elif value == 'Close':
            CKS = 0xFF - ((0xF6 + 0x31 + irspeed) & 0xFF)
            IrisCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x03, 0x31, irspeed, CKS)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            CKS = 0xFF - ((0xF5 + 0x10) & 0xFF)
            IrisCmdString = pack('>BBBBB', 0x00, 0xF2, 0x03, 0x10, CKS)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetMemoryRecall(self, value, qualifier):

        MemoryRecallValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
        }
        CKS = 0xFF - ((0x13A + MemoryRecallValues[value]) & 0xFF)
        MemoryRecallCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x06, 0x41, MemoryRecallValues[value], CKS)
        self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier)

    def SetMemorySave(self, value, qualifier):

        MemorySaveValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
        }
        CKS = 0xFF - ((0x139 + MemorySaveValues[value]) & 0xFF)
        MemorySaveCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x06, 0x40, MemorySaveValues[value], CKS)
        self.__SetHelper('MemorySave', MemorySaveCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerValues = {
            'On': 0x50,
            'Off': 0x51,
        }
        CKS = 0xFF - ((0xF7 + PowerValues[value]) & 0xFF)
        PowerCmdString = pack('>BBBBB', 0x00, 0xF2, 0x05, PowerValues[value], CKS)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            0x02: 'On',
            0x01: 'Off'
        }

        CKS = 0xFF - ((0xF7 + 0x52) & 0xFF)
        PowerCmdString = pack('>BBBBB', 0x00, 0xF2, 0x05, 0x52, CKS)
        res = self.__UpdateHelperSYNC('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[int(res[3])]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09
        }
        CKS = 0xFF - ((0x39 + PresetRecallValues[value]) & 0xFF)
        PresetRecallCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x05, 0x41, PresetRecallValues[value], CKS)
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09
        }
        CKS = 0xFF - ((0x138 + PresetSaveValues[value]) & 0xFF)
        PresetSaveCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x05, 0x40, PresetSaveValues[value], CKS)
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Manual': 0x50,
            'One Push': 0x51,
            'Auto Tracking': 0x52
        }
        CKS = 0xFF - ((0xF6 + ValueStateValues[value]) & 0xFF)
        WhiteBalanceCmdString = pack('>BBBBB', 0x00, 0xF2, 0x04, ValueStateValues[value], CKS)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomValues = {
            'Wide': 0x31,
            'Tele': 0x21,
            'Stop': 0x10,
        }
        if 1 <= int(qualifier['Zoom Speed']) <= 15:
            ZoomSpeed = int(qualifier['Zoom Speed'])
            if value == 'Wide':
                CKS = 0xFF - ((0xF4 + 0x31 + ZoomSpeed) & 0xFF)
                ZoomCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x01, 0x31, ZoomSpeed, CKS)
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
            elif value == 'Tele':
                CKS = 0xFF - ((0xF4 + 0x21 + ZoomSpeed) & 0xFF)
                ZoomCmdString = pack('>BBBBBB', 0x00, 0xF3, 0x01, 0x21, ZoomSpeed, CKS)
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
            else:
                CKS = 0xFF - ((0xF3 + 0x10) & 0xFF)
                ZoomCmdString = pack('>BBBBB', 0x00, 0xF2, 0x01, 0x10, CKS)
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoome')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        self.Send(commandstring)

            
    def __UpdateHelperSYNC(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.reg)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors((command), res)


    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, str):
            response = response.encode()

        ERROR_TYPES = {
            b'\x00\xF1\x10': 'Illegal Command',
            b'\x00\xF1\x11': 'Command Failed',
            b'\x00\xF1\x12': 'Parameter Wrong',
            b'\x00\xF1\x20': 'Checksum Error',
            b'\x00\xF1\x21': 'Timeout Error',
            b'\x00\xF1\x22': 'Command too long'
        }

        if response[0:3] in ERROR_TYPES:
            print(sourceCmdName + ' ' + ERROR_TYPES[response[0:3]])
            response = b''
        return response

    def __MatchError(self, match, tag):

        ErrorType = {
            b'\x00\xF1\x10': 'Illegal Command',
            b'\x00\xF1\x11': 'Command Failed',
            b'\x00\xF1\x12': 'Parameter Wrong',
            b'\x00\xF1\x20': 'Checksum Error',
            b'\x00\xF1\x21': 'Timeout Error',
            b'\x00\xF1\x22': 'Command too long'
        }

        errorString = '{0} {1}'.format(match.group(1), ErrorType[match.group(1)])
        print(errorString)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
