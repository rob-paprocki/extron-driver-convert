from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack

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
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }


        self.SetRegAspectRatio = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')
        self.SetRegAutoImage = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
        self.SetRegFreeze = re.compile(b'([\xA1][\x00-\xFF]{7})|([\x21][\x00-\xFF]{6})')
        self.SetRegInput = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
        self.SetRegLampMode = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')
        self.SetRegMenuNavigation = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
        self.SetRegOnScreenDisplay = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
        self.SetRegPower = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')
        self.SetRegVideoMute = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')

        self.GetRegDeviceStatus = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{17})')
        self.GetRegLampMode = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')
        self.GetRegLampUsage = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{11})')
        self.GetRegPower = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{21})')

        self.SetDelim = {
            'AspectRatio': self.SetRegAspectRatio,
            'AutoImage': self.SetRegAutoImage,
            'Freeze': self.SetRegFreeze,
            'Input': self.SetRegInput,
            'LampMode': self.SetRegLampMode,
            'MenuNavigation': self.SetRegMenuNavigation,
            'OnScreenDisplay': self.SetRegOnScreenDisplay,
            'Power': self.SetRegPower,
            'VideoMute': self.SetRegVideoMute
        }

        self.UpdateDelim = {
            'DeviceStatus': self.GetRegDeviceStatus,
            'LampMode': self.GetRegLampMode,
            'LampUsage': self.GetRegLampUsage,
            'Power': self.GetRegPower
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3 Window': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            'Wide 16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            'Full': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            '5:4': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0B\x00\x3B',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x10\x00\x40',
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0F\x00\x3F'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp Cover Error',
            b'\x02\x00\x00\x00': 'Temperature Error',
            b'\x10\x00\x00\x00': 'Fan Failure',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Error',
            b'\x80\x00\x00\x00': 'Lamp Life Expired',
            b'\x00\x01\x00\x00': 'Lamp Beyond Limit',
            b'\x00\x02\x00\x00': 'Format Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Failure',
            b'\x00\x00\x08\x00': 'Lamp Housing Error',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'High Temperature',
            b'\x00\x00\x00\x08': 'Sensor Error',
            b'\x00\x00\x00\x10': 'Pump Error'
            }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusState.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Device Status: Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'HDMI': b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'Display Port': b'\x02\x03\x00\x00\x02\x01\xA6\xAE',
            'BNC': b'\x02\x03\x00\x00\x02\x01\x02\x0A',
            'BNC (CV)': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'BNC (Y/C)': b'\x02\x03\x00\x00\x02\x01\x0B\x13',
            'Computer': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'HDBaseT': b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'Slot': b'\x02\x03\x00\x00\x02\x01\xAB\xB3'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            0x00: 'Normal',
            0x02: 'Eco 1',
            0x03: 'Eco 2'
            }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[int(res[6])]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, ValueError, IndexError):
                print('Lamp Mode: Invalid/Unexpected Response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                lampHour = int(unpack('>I', res[10:11] + res[9:10] + res[8:9] + res[7:8])[0] / 3600)
                self.WriteStatus('LampUsage', lampHour, qualifier)
            except (ValueError, IndexError):
                print('Lamp Usage: Invalid/Unexpected Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Exit': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F',
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayState = {
            'On': b'\x02\x15\x00\x00\x00\x17',
            'Off': b'\x02\x14\x00\x00\x00\x16'
            }

        OnScreenDisplayCmdString = OnScreenDisplayState[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03',
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
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

        InputState = {
            b'\x01\x21': 'HDMI',
            b'\x01\x22': 'Display Port',
            b'\x02\x01': 'BNC',
            b'\x01\x02': 'BNC (CV)',
            b'\x01\x03': 'BNC (Y/C)',
            b'\x01\x01': 'Computer',
            b'\x01\x27': 'HDBaseT',
            b'\x01\x23': 'Slot'
            }

        FreezeState = {
            0x01: 'On',
            0x00: 'Off'
            }

        VideoMuteState = {
            0x01: 'On',
            0x00: 'Off'
            }

        OnScreenDisplayState = {
            0x00: 'On',
            0x01: 'Off'
            }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerState[int(res[6])]
                self.WriteStatus('Power', PowerValue, None)
            except (KeyError, ValueError, IndexError):
                print('Invalid/Unexpected Response for Power')

            try:
                InputValue = InputState[res[8:10]]
                self.WriteStatus('Input', InputValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Input')

            try:
                FreezeValue = FreezeState[int(res[14])]
                self.WriteStatus('Freeze', FreezeValue, None)
            except (KeyError, ValueError, IndexError):
                print('Invalid/Unexpected Response for Freeze')

            try:
                VideoMuteValue = VideoMuteState[int(res[11])]
                self.WriteStatus('VideoMute', VideoMuteValue, None)
            except (KeyError, ValueError, IndexError):
                print('Invalid/Unexpected Response for VideoMute')

            try:
                OSDValue = OnScreenDisplayState[int(res[13])]
                self.WriteStatus('OnScreenDisplay', OSDValue, None)
            except (KeyError, ValueError, IndexError):
                print('Invalid/Unexpected Response for OnScreenDisplay')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
            }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __CheckResponseForErrors(self, command, response):

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
            b'\x02\x08': 'A test pattern of filer is destroyed',
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

        if (response[0:1] == b'\xA0' or response[0:1] == b'\xA1' or response[0:1] == b'\xA2' or response[0:1] == b'\xA3') and response[5:7] in DEVICE_ERROR_CODES:
            errorstring = command + ' Error: ' + DEVICE_ERROR_CODES[response[5:7]]
            response = ''
            print(errorstring)
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command in 'UserDefinedCommand':
            self.Send(commandstring)
            res = ''
        else:
            SetRegex = self.SetDelim[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=SetRegex)
            if not res:
                print('No Response or Invalid/Unexpected Response for Set{}'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            regex = self.UpdateDelim[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
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
            print(command, 'does not exist in the module')

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
