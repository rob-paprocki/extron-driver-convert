from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.SetDelim = {
            'AspectRatio': re.compile(b'(^[\x00-\xFF]{8}$)'),
            'AudioMute': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{5}$)'),
            'AutoImage': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{6}$)'),
            'Freeze': re.compile(b'(^[\xA1][\x00-\xFF]{7}$)|(^[\x21][\x00-\xFF]{6}$)'),
            'Input': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{6}$)'),
            'LampMode': re.compile(b'(^[\x00-\xFF]{8}$)'),
            'MenuNavigation': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{6}$)'),
            'Power': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{5}$)'),
            'VideoMute': re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{5}$)'),
            'Volume': re.compile(b'(^[\x00-\xFF]{8}$)')
            }

        self.UpdateDelim = {
            'AspectRatio': re.compile(b'(^[\xA3][\x00-\xFF]{7}$)|(^[\x23][\x00-\xFF]{18}$)'),
            'AudioMute': re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{21}$)'),
            'DeviceStatus': re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{17}$)'),
            'Input': re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{21}$)'),
            'LampMode': re.compile(b'(^[\xA3][\x00-\xFF]{7}$)|(^[\x23][\x00-\xFF]{7}$)'),
            'LampUsage': re.compile(b'(^[\xA3][\x00-\xFF]{7}$)|(^[\x23][\x00-\xFF]{21}$)'),
            'OperationHours': re.compile(b'(^[\xA3][\x00-\xFF]{7}$)|(^[\x23][\x00-\xFF]{103}$)'),
            'Power': re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{21}$)'),
            'SignalStatus': re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{21}$)'),
            'Volume': re.compile(b'(^[\xA3][\x00-\xFF]{7}$)|(^[\x23][\x00-\xFF]{18}$)')
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            'Normal': 0x00,
            'Letterbox': 0x01,
            '16:9': 0x02,
            'Wide Zoom': 0x03,
            '4:3 Fill': 0x04,
            '5:4': 0x0B,
            '16:10': 0x0C,
            '15:9': 0x0D,
            'Native': 0x0E
            }
        CKS = 0x30 + AspectRatioValues[value]
        AspectRatioCmdString = pack('>BBBBBBBBBBB', 0x03, 0x10, 0x00, 0x00, 0x05, 0x18, 0x00, 0x00, AspectRatioValues[value], 0x00, CKS)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStates = {
            0x00: 'Normal',
            0x01: 'Letterbox',
            0x02: '16:9',
            0x03: 'Wide Zoom',
            0x04: '4:3 Fill',
            0x0B: '5:4',
            0x0C: '16:10',
            0x0D: '15:9',
            0x0E: 'Native'
            }
        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = AspectRatioStates[res[12]]
                    self.WriteStatus('AspectRatio', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'Off': b'\x02\x13\x00\x00\x00\x15',
            'On': b'\x02\x12\x00\x00\x00\x14'
            }
        AudioMuteCmdString = AudioMuteValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStates = {
            0x00: 'Off',
            0x01: 'On'
            }
        VideoMuteStateNames = {
            0x00: 'Off',
            0x01: 'On'
            }

        AudioMuteCmdString = b'\x00\x85\x00\x00\x01\x03\x89'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            if len(res) == 22:
                try:
                    audioMuteValue = AudioMuteStates[res[6]]
                    self.WriteStatus('AudioMute', audioMuteValue, None)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAudioMute')

                try:
                    videoMuteValue = VideoMuteStateNames[res[5]]
                    self.WriteStatus('VideoMute', videoMuteValue, None)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusStateNames = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp cover error',
            b'\x02\x00\x00\x00': 'Temp error (bimetal)',
            b'\x10\x00\x00\x00': 'Fan error',
            b'\x20\x00\x00\x00': 'Power error',
            b'\x40\x00\x00\x00': 'Lamp 1 error',
            b'\x80\x00\x00\x00': 'Lamp 1 end of life',

            b'\x00\x01\x00\x00': 'Lamp 1 beyond limit',
            b'\x00\x02\x00\x00': 'Formatter error',
            b'\x00\x04\x00\x00': 'Lamp 2 error',

            b'\x00\x00\x02\x00': 'FPGA error',
            b'\x00\x00\x04\x00': 'Temp error (sensor)',
            b'\x00\x00\x08\x00': 'Lamp 1 housing error',
            b'\x00\x00\x10\x00': 'Lamp 1 data error',
            b'\x00\x00\x20\x00': 'Mirror cover error',
            b'\x00\x00\x40\x00': 'Lamp 2 end of life',
            b'\x00\x00\x80\x00': 'Lamp 2 beyond limit',

            b'\x00\x00\x00\x01': 'Lamp 2 housing error',
            b'\x00\x00\x00\x02': 'Lamp 2 data error',
            b'\x00\x00\x00\x04': 'High temp due to dust',
            b'\x00\x00\x00\x08': 'Foreign object sensor error',
            b'\x00\x00\x00\x10': 'Pump error',
            }
        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = DeviceStatusStateNames.get(res[5:9], 'Multiple errors')
                    self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def UpdateFilterUsage(self, value, qualifier):

        self.UpdateOperationHours(None, None)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C',
            'On': b'\x01\x98\x00\x00\x01\x01\x9B'
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'HDMI': 0x1A,
            'Computer 1': 0x01,
            'Computer 2': 0x02,
            'Computer 3': 0x03,
            'Display Port': 0x1B,
            'Video': 0x06,
            'S-Video': 0x0B,
            'USB Viewer': 0x1F,
            'Network': 0x20
            }
        CKS = 0x08 + InputStateValues[value]
        InputCmdString = pack('>BBBBBBBB', 0x02, 0x03, 0x00, 0x00, 0x02, 0x01, InputStateValues[value], CKS)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            b'\x01\x06': 'HDMI',
            b'\x01\x01': 'Computer 1',
            b'\x02\x01': 'Computer 2',
            b'\x03\x01': 'Computer 3',
            b'\x02\x06': 'Display Port',
            b'\x01\x02': 'Video',
            b'\x01\x03': 'S-Video',
            b'\x01\x07': 'USB Viewer',
            b'\x02\x07': 'Network'
            }

        InputCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    inputValue = InputStateNames[res[8:10]]
                    self.WriteStatus('Input', inputValue, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        LampModeValues = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE'
            }
        LampModeCmdString = LampModeValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStates = {
            0x00: 'Normal',
            0x01: 'Eco'
            }
        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if res[0:2] == b'\x23\xB0':
                    value = LampModeStates[res[6]]
                    self.WriteStatus('LampMode', value, None)
                else:
                    print('Invalid/unexpected response for UpdateLampMode')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x8C\x00\x00\x00\x8F'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = int(((res[8] << 24) + (res[7] << 16) + (res[6] << 8) + res[5]) / 3600)
                    self.WriteStatus('LampUsage', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Menu': 0x06,
            'Up': 0x07,
            'Down': 0x08,
            'Left': 0x0A,
            'Right': 0x09,
            'Enter': 0x0B,
            'Cancel': 0x0C
            }
        CKS = 0x13 + MenuNavigationValues[value]
        MenuNavigationCmdString = pack('>BBBBBBBB', 0x02, 0x0F, 0x00, 0x00, 0x02, MenuNavigationValues[value], 0x00, CKS)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 104:
                    operationHoursValue = int(((res[102] << 24) + (res[101] << 16) + (res[100] << 8) + res[99]) / 3600)
                    self.WriteStatus('OperationHours', operationHoursValue, None)
                    filterHoursValue = int(((res[94] << 24) + (res[93] << 16) + (res[92] << 8) + res[91]) / 3600)
                    self.WriteStatus('FilterUsage', filterHoursValue, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': b'\x02\x01\x00\x00\x00\x03',
            'On': b'\x02\x00\x00\x00\x00\x02'
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x10: 'Off',
            0x0F: 'Off',
            0x02: 'Warming Up',
            0x01: 'Warming Up',
            0x05: 'Cooling Down'
            }

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    powerValue = PowerStateNames[res[10]]
                    self.WriteStatus('Power', powerValue, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def UpdateSignalStatus(self, value, qualifier):

        SignalStatusStates = {
            0x01: 'No signal',
            0x00: 'Picture signal displaying',
            0x02: 'Viewer displaying',
            0x03: 'Test pattern displaying',
            0x04: 'LAN displaying'
            }
        SignalStatusCmdString = b'\x00\x85\x00\x00\x01\x02\x88'
        res = self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = SignalStatusStates[res[13]]
                    self.WriteStatus('SignalStatus', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSignalStatus')

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'Off': b'\x02\x11\x00\x00\x00\x13',
            'On': b'\x02\x10\x00\x00\x00\x12'
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 31
            }
        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            print('Invalid Command for SetVolume')
        else:
            CKS = 0x1D + value
            VolumeCmdString = pack('>BBBBBBBBBBB', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, CKS)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = res[12]
                    self.WriteStatus('Volume', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, command, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'Unknown command.',
            b'\x00\x01': 'This current model does not support this function.',
            b'\x01\x00': 'Invalid values specificed.',
            b'\x01\x01': 'Specified terminal is unavailable or cannot be selected.',
            b'\x01\x02': 'Selected lanugage is not available.',
            b'\x02\x00': 'Available memory reservation error.',
            b'\x02\x02': 'Operating memory.',
            b'\x02\x03': 'Setting not possible.',
            b'\x02\x04': 'On forced on-screen mute mode.',
            b'\x02\x06': 'Displaying a signal other than PC Viewer.',
            b'\x02\x07': 'No signal.',
            b'\x02\x08': 'Displaying a test pattern or PC Card fills screen.',
            b'\x02\x09': 'No PC card is inserted.',
            b'\x02\x0A': 'Memory operation failed.',
            b'\x02\x0C': 'Displaying the Entry List.',
            b'\x02\x0D': 'Power Off inhibited.',
            b'\x02\x0E': 'Execution error.',
            b'\x02\x0F': 'No operation authority.',
            b'\x03\x00': 'Specified gain number is wrong.',
            b'\x03\x01': 'Selected gain is not available.',
            b'\x03\x02': 'Adjustment failed.'
        }

        if (response[5:7] in DEVICE_ERROR_CODES) & (160 <= int(response[0]) <= 175):
            print('{0} {1}'.format(command, DEVICE_ERROR_CODES[response[5:7]]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        setRegex = self.SetDelim[command]

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=setRegex)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        updateRegex = self.UpdateDelim[command]

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=updateRegex)
            if not res:
                return b''
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
