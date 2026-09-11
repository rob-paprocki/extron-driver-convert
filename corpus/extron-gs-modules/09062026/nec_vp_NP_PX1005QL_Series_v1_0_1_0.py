from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from struct import unpack
import re

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensProfile': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'ReferenceLensMemoryControl': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.set_regex = {
            'AspectRatio': re.compile(b'(\x23\x10[\x00-\xFF]{6}|\xA3\x10[\x00-\xFF]{6})'),
            'AutoImage': re.compile(b'(\x22\x0F[\x00-\xFF]{5}|\xA2\x0F[\x00-\xFF]{6})'),
            'Freeze': re.compile(b'(\x21\x98[\x00-\xFF]{5}|\xA1\x98[\x00-\xFF]{6})'),
            'Input': re.compile(b'(\x22\x03[\x00-\xFF]{5}|\xA2\x03[\x00-\xFF]{6})'),
            'LampMode': re.compile(b'(\x23\xB1[\x00-\xFF]{6}|\xA3\xB1[\x00-\xFF]{6})'),
            'LensProfile': re.compile(b'(\x22\x27[\x00-\xFF]{6}|\xA2\x27[\x00-\xFF]{6})'),
            'MenuNavigation': re.compile(b'(\x22\x0F[\x00-\xFF]{5}|\xA2\x0F[\x00-\xFF]{6})'),
            'OnScreenDisplay': re.compile(b'(\x22[\x14\x15][\x00-\xFF]{4}|\xA2[\x14\x15][\x00-\xFF]{6})'),
            'Power': re.compile(b'(\x22[\x00\x01][\x00-\xFF]{4}|\xA2[\x00\x01][\x00-\xFF]{6})'),
            'ReferenceLensMemoryControl': re.compile(b'(\x22\x1F[\x00-\xFF]{6}|\xA2\x1F[\x00-\xFF]{6})'),
            'VideoMute': re.compile(b'(\x22\x10[\x00-\xFF]{4}|\xA2\x10[\x00-\xFF]{6})')
        }

        self.get_regex = {
            'DeviceStatus': re.compile(b'(\x20\x88[\x00-\xFF]{16}|\xA0\x88[\x00-\xFF]{6})'),
            'LampMode': re.compile(b'(\x23\xB0[\x00-\xFF]{6}|\xA3\xB0[\x00-\xFF]{6})'),
            'LampUsage': re.compile(b'(\x23\x96[\x00-\xFF]{10}|\xA3\x96[\x00-\xFF]{6})'),
            'LensProfile': re.compile(b'(\x22\\x28[\x00-\xFF]{6}|\xA2\\x28[\x00-\xFF]{6})'),
            'Power': re.compile(b'(\x20\xBF[\x00-\xFF]{20}|\xA0\xBF[\x00-\xFF]{6})')
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0F\x00\x3F',
            'Normal': b'\x03\x10\x00\x00\x05\x18\x00\x00\x10\x00\x40',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Wide Screen / 16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            'Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            'Full': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            '5:4': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0B\x00\x3B',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error (Bi-metallic strip)',
            b'\x08\x00\x00\x00': 'Fan Error',
            b'\x10\x00\x00\x00': 'Fan Error',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Off',
            b'\x80\x00\x00\x00': 'Replace Lamp',
            b'\x00\x01\x00\x00': 'Lamp Life Expired',
            b'\x00\x02\x00\x00': 'Formatter Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Error',
            b'\x00\x00\x08\x00': 'Lamp Not Present',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'Temperature Error due to Dust',
            b'\x00\x00\x00\x08': 'Foreign Matter Sensor Error',
            b'\x00\x00\x00\x20': 'Ballast Communication Error',
            b'\x00\x00\x00\x40': 'Iris Calibration Error',
            b'\x00\x00\x00\x80': 'Lens not properly installed'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'HDMI 2': b'\x02\x03\x00\x00\x02\x01\xA2\xAA',
            'DisplayPort 1': b'\x02\x03\x00\x00\x02\x01\xA6\xAE',
            'DisplayPort 2': b'\x02\x03\x00\x00\x02\x01\xA7\xAF',
            'HDBaseT': b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'SDI 1': b'\x02\x03\x00\x00\x02\x01\xC4\xCC',
            'SDI 2': b'\x02\x03\x00\x00\x02\x01\xC5\xCD',
            'SDI 3': b'\x02\x03\x00\x00\x02\x01\xC6\xCE',
            'SDI 4': b'\x02\x03\x00\x00\x02\x01\xC7\xCF',
            'SLOT': b'\x02\x03\x00\x00\x02\x01\xAB\xB3'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
        }

        if value in ValueStateValues:
            LampModeCmdString = ValueStateValues[value]
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x02': 'Eco 1',
            b'\x03': 'Eco 2'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(unpack('<I', res[7:11])[0] / 3600)
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetLensProfile(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x02\x27\x00\x00\x01\x00\x2A',
            '2': b'\x02\x27\x00\x00\x01\x01\x2B',
        }

        if value in ValueStateValues:
            LensProfileCmdString = ValueStateValues[value]
            self.__SetHelper('LensProfile', LensProfileCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensProfile')

    def UpdateLensProfile(self, value, qualifier):

        LensProfileCmdString = b'\x02\x28\x00\x00\x00\x2A'
        res = self.__UpdateHelper('LensProfile', LensProfileCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x00': '1',
                    b'\x01': '2',
                }

                value = ValueStateValues[res[5:6]]
                self.WriteStatus('LensProfile', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Lens Profile: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Exit': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x15\x00\x00\x00\x17',
            'Off': b'\x02\x14\x00\x00\x00\x16'
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = ValueStateValues[value]
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerStates = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x0F: 'Off',
            0x10: 'Off',
            0x01: 'Warming Up',
            0x02: 'Warming Up',
            0x03: 'Warming Up',
            0x09: 'Warming Up',
            0x05: 'Cooling Down',
            0x07: 'Cooling Down'
        }

        InputStates = {
            b'\x01\x21': 'HDMI 1',
            b'\x02\x21': 'HDMI 2',
            b'\x01\x22': 'DisplayPort 1',
            b'\x02\x22': 'DisplayPort 2',
            b'\x01\x27': 'HDBaseT',
            b'\x01\x28': 'SDI 1',
            b'\x02\x28': 'SDI 2',
            b'\x03\x28': 'SDI 3',
            b'\x04\x28': 'SDI 4',
            b'\x01\x23': 'SLOT'
        }

        VideoMuteStates = {
            0x01: 'On',
            0x00: 'Off'
        }

        OnScreenDisplayStates = {
            0x00: 'On',
            0x01: 'Off'
        }

        FreezeStates = {
            0x01: 'On',
            0x00: 'Off'
        }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerStates[res[6]]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

            try:
                InputValue = InputStates[res[8:10]]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

            try:
                VideoMuteValue = VideoMuteStates[res[11]]
                self.WriteStatus('VideoMute', VideoMuteValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

            try:
                OnScreenDisplayValue = OnScreenDisplayStates[res[13]]
                self.WriteStatus('OnScreenDisplay', OnScreenDisplayValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/Unexpected Response'])

            try:
                FreezeValue = FreezeStates[res[14]]
                self.WriteStatus('Freeze', FreezeValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetReferenceLensMemoryControl(self, value, qualifier):

        ValueStateValues = {
            'Move': b'\x02\x1F\x00\x00\x01\x01\x23',
            'Store': b'\x02\x1F\x00\x00\x01\x00\x22',
            'Reset': b'\x02\x1F\x00\x00\x01\x02\x24',
        }

        if value in ValueStateValues:
            ReferenceLensMemoryControlCmdString = ValueStateValues[value]
            self.__SetHelper('ReferenceLensMemoryControl', ReferenceLensMemoryControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReferenceLensMemoryControl')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'The command cannot be recognized',
            b'\x00\x01': 'The command is not supported by the model in use',
            b'\x01\x00': 'The specified value is invalid',
            b'\x01\x01': 'The specified input terminal is invalid',
            b'\x01\x02': 'The specified language is invalid',
            b'\x02\x00': 'Memory allocation error',
            b'\x02\x02': 'Memory in use',
            b'\x02\x03': 'The specified value cannot be set',
            b'\x02\x04': 'Forced onscreen mute on',
            b'\x02\x06': 'Viewer error',
            b'\x02\x07': 'No signal',
            b'\x02\x08': 'A test pattern or filer is displayed',
            b'\x02\x09': 'No PC card is inserted',
            b'\x02\x0A': 'Memory operation error',
            b'\x02\x0C': 'An entry list is displayed',
            b'\x02\x0D': 'The command cannot be accepted because the power is off',
            b'\x02\x0E': 'The command execution failed',
            b'\x02\x0F': 'There is no authority necessary for the operation',
            b'\x03\x00': 'The specified gain number is incorrect',
            b'\x03\x01': 'The specified gain is invalid',
            b'\x03\x02': 'Adjustment failed'
        }

        if b'\xA0' <= response[0:1] <= b'\xA3' and response[5:7] in DEVICE_ERROR_CODES:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[5:7]])])
            return ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex[command])
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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