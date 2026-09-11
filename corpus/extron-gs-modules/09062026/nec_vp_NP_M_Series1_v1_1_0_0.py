from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self.Models = {
            'NP-M403W': self.nec_1_1791_W_H,
            'NP-M363W': self.nec_1_1791_W_H,
            'NP-M323W': self.nec_1_1791_W_H,
            'NP-M403X': self.nec_1_1791_X,
            'NP-M363X': self.nec_1_1791_X,
            'NP-M323X': self.nec_1_1791_X,
            'NP-M283X': self.nec_1_1791_X,
            'NP-M353WS': self.nec_1_1791_W_H,
            'NP-M303WS': self.nec_1_1791_W_H,
            'NP-M333XS': self.nec_1_1791_X,
            'NP-M403H': self.nec_1_1791_W_H,
            'NP-M323H': self.nec_1_1791_W_H,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.SetRegAspectRatio = re.compile(b'([\x00-\xFF]{8})')
            self.SetRegAudioMute = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')
            self.SetRegAutoImage = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
            self.SetRegFreeze = re.compile(b'([\xA1][\x00-\xFF]{7})|([\x21][\x00-\xFF]{6})')
            self.SetRegInput = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
            self.SetRegLampMode = re.compile(b'([\x00-\xFF]{8})')
            self.SetRegMenuNavigation = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
            self.SetRegPower = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')
            self.SetRegVideoMute = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')
            self.SetRegVolume = re.compile(b'([\x00-\xFF]{8})')

            self.GetRegAspectRatio = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})')
            self.GetRegDeviceStatus = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{17})')
            self.GetRegLampMode = re.compile(b'([\x00-\xFF]{8})')
            self.GetRegLampUsage = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{11})')
            self.GetRegOperationHours = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{103})')
            self.GetRegPower = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{21})')
            self.GetRegVolume = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectRatioStateNames[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = self.AspectRatioStateValues[res[12]]
                    self.WriteStatus('AspectRatio', value, None)
                else:
                    self.__CheckResponseForErrors('AspectRatio', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x12\x00\x00\x00\x14',
            'Off': b'\x02\x13\x00\x00\x00\x15'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusStateValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error',
            b'\x10\x00\x00\x00': 'Fan Error',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Error',
            b'\x80\x00\x00\x00': 'Lamp Life Expired',
            b'\x00\x01\x00\x00': 'Lamp Life Expiring',
            b'\x00\x02\x00\x00': 'Format Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Error',
            b'\x00\x00\x08\x00': 'Lamp Housing Error',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'High Temperature',
            b'\x00\x00\x00\x08': 'Foreign Object Sensor Error',
            b'\x00\x00\x00\x10': 'Pump Error'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = DeviceStatusStateValues.get(res[5:9], 'Multiple Errors')
                    self.WriteStatus('DeviceStatus', value, None)
                else:
                    self.__CheckResponseForErrors('DeviceStatus', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer': b'\x01\x09',
            'HDMI 1': b'\xA1\xA9',
            'HDMI 2': b'\xA2\xAA',
            'Video': b'\x06\x0E',
            'USB-A': b'\x1F\x27',
            'USB-B': b'\x22\x2A',
            'LAN': b'\x20\x28'
        }

        InputCmdString = b'\x02\x03\x00\x00\x02\x01' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00\xBD',
            'Auto Eco': b'\x01\xBE',
            'Normal': b'\x02\xBF',
            'Eco': b'\x03\xC0'
        }

        LampModeCmdString = b'\x03\xB1\x00\x00\x02\x07' + ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStateValues = {
            0x00: 'Off',
            0x01: 'Auto Eco',
            0x02: 'Normal',
            0x03: 'Eco'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if res[0:2] == b'\x23\xB0':
                    value = LampModeStateValues[res[6]]
                    self.WriteStatus('LampMode', value, None)
                elif res[0:2] == b'\xA3\xB0':
                    self.__CheckResponseForErrors('LampMode', res)
                else:
                    print('Invalid/Unexpected Response for UpdateLampMode')
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 12:
                    value = int(((res[10] << 24) + (res[9] << 16) + (res[8] << 8) + res[7]) / 3600)
                    self.WriteStatus('LampUsage', value, None)
                else:
                    self.__CheckResponseForErrors('LampUsage', res)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Cancel': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 104:
                    operationHoursValue = int(((res[102] << 24) + (res[101] << 16) + (res[100] << 8) + res[99]) / 3600)
                    self.WriteStatus('OperationHours', operationHoursValue, None)
                else:
                    self.__CheckResponseForErrors('OperationHours', res)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x0F: 'Off',
            0x10: 'Off',
            0x01: 'Warming Up',
            0x02: 'Warming Up',
            0x03: 'Warming Up',
            0x09: 'Warming Up',
            0x05: 'Cooling Down'
            }

        InputStateValues = {
            b'\x01\x01': 'Computer',
            b'\x01\x21': 'HDMI 1',
            b'\x02\x21': 'HDMI 2',
            b'\x01\x02': 'Video',
            b'\x01\x07': 'USB-A',
            b'\x04\x07': 'USB-B',
            b'\x02\x07': 'LAN'
        }

        VideoMuteStateValues = {
            0x00: 'Off',
            0x01: 'On'
            }

        AudioMuteStateValues = {
            0x00: 'Off',
            0x01: 'On'
            }

        FreezeStateValues = {
            0x00: 'Off',
            0x01: 'On'
            }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    try:
                        PowerValue = PowerStateValues[res[6]]
                    except (KeyError, IndexError):
                        print('Invalid/Unexpected Response for UpdatePower')
                    try:
                        InputValue = InputStateValues[res[8:10]]
                    except (KeyError, IndexError):
                        print('Invalid/Unexpected Response for UpdatePower')
                    try:
                        VideoMuteValue = VideoMuteStateValues[res[11]]
                    except (KeyError, IndexError):
                        print('Invalid/Unexpected Response for UpdatePower')
                    try:
                        AudioMuteValue = AudioMuteStateValues[res[12]]
                    except (KeyError, IndexError):
                        print('Invalid/Unexpected Response for UpdatePower')
                    try:
                        FreezeValue = FreezeStateValues[res[14]]
                    except (KeyError, IndexError):
                        print('Invalid/Unexpected Response for UpdatePower')

                    self.WriteStatus('Power', PowerValue, None)
                    self.WriteStatus('Input', InputValue, None)
                    self.WriteStatus('VideoMute', VideoMuteValue, None)
                    self.WriteStatus('AudioMute', AudioMuteValue, None)
                    self.WriteStatus('Freeze', FreezeValue, None)
                else:
                    self.__CheckResponseForErrors('Power', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

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
                else:
                    self.__CheckResponseForErrors('Volume', res)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

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
        if response[5:7] in DEVICE_ERROR_CODES:
            errorString = command + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]]
            print(errorString)
        else:
            print('Invalid/Unexpected Response')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            res = ''
        else:
            SetDelim = {
                'AspectRatio': self.SetRegAspectRatio,
                'AudioMute': self.SetRegAudioMute,
                'AutoImage': self.SetRegAutoImage,
                'Freeze': self.SetRegFreeze,
                'Input': self.SetRegInput,
                'LampMode': self.SetRegLampMode,
                'MenuNavigation': self.SetRegMenuNavigation,
                'Power': self.SetRegPower,
                'VideoMute': self.SetRegVideoMute,
                'Volume': self.SetRegVolume
            }
            regex = SetDelim[command]

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                print('No Response')
        return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        UpdateDelim = {
            'AspectRatio': self.GetRegAspectRatio,
            'DeviceStatus': self.GetRegDeviceStatus,
            'LampMode': self.GetRegLampMode,
            'LampUsage': self.GetRegLampUsage,
            'OperationHours': self.GetRegOperationHours,
            'Power': self.GetRegPower,
            'Volume': self.GetRegVolume
            }
        regex = UpdateDelim[command]

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                return ''
            else:
                return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def nec_1_1791_X(self):
        self.AspectRatioStateNames = {
            'Auto'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Wide Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            '16:9'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            'Native'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            '4:3'      : b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '15:9'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10'    : b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36'
        }

        self.AspectRatioStateValues = {
            0x00: 'Auto',
            0x01: 'Wide Zoom',
            0x02: '16:9',
            0x03: 'Native',
            0x04: '4:3',
            0x05: '15:9',
            0x06: '16:10'
        }

    def nec_1_1791_W_H(self):


        self.AspectRatioStateNames = {
            'Auto'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '16:9'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            'Native'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            '4:3'      : b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '15:9'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10'    : b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37'
        }

        self.AspectRatioStateValues = {
            0x00: 'Auto',
            0x02: '16:9',
            0x03: 'Native',
            0x04: '4:3',
            0x05: '15:9',
            0x06: '16:10',
            0x07: 'Letterbox'
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
