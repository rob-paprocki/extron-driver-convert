from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack, pack


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
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.SetRegAspectRatio = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7})')
            self.SetRegAudioMute = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{5})')
            self.SetRegAutoImage = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{6})')
            self.SetRegFreeze = re.compile(b'(\xA1[\x00-\xFF]{7})|(\x21[\x00-\xFF]{6})')
            self.SetRegInput = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{6})')
            self.SetRegLampMode = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7})')
            self.SetRegMenuNavigation = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{6})')
            self.SetRegOnScreenDisplay = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{5})')
            self.SetRegPower = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{5})')
            self.SetRegPictureMute = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{5})')
            self.SetRegVolume = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7})')

            self.GetRegAspectRatio = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{18})')
            self.GetRegDeviceStatus = re.compile(b'(\xA0[\x00-\xFF]{7})|(\x20[\x00-\xFF]{17})')
            self.GetRegFilterUsage = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{103})')
            self.GetRegLampMode = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7})')
            self.GetRegLampUsage = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{21})')
            self.GetRegPower = re.compile(b'(\xA0[\x00-\xFF]{7})|(\x20[\x00-\xFF]{21})')
            self.GetRegVolume = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{18})')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x00\x00\x30',
            '4:3 Fill': b'\x04\x00\x34',
            'Letterbox': b'\x01\x00\x31',
            '16:9/Widescreen': b'\x02\x00\x32',
            'Zoom': b'\x03\x00\x33',
            '5:4': b'\x0B\x00\x3B',
            '16:10': b'\x0C\x00\x3C',
            '15:9': b'\x0D\x00\x3D'
        }

        AspectRatioCmdString = b'\x03\x10\x00\x00\x05\x18\x00\x00' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
           b'\x00': '4:3',
           b'\x04': '4:3 Fill',
           b'\x01': 'Letterbox',
           b'\x02': '16:9/Widescreen',
           b'\x03': 'Zoom',
           b'\x0B': '5:4',
           b'\x0C': '16:10',
           b'\x0D': '15:9',
           }

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = AspectRatioState[res[12:13]]
                    self.WriteStatus('AspectRatio', value, None)
                else:
                    print('Invalid Command for UpdateAspectRatio')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

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

        ValueStateValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error',
            b'\x10\x00\x00\x00': 'Fan Error',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Error',
            b'\x08\x00\x00\x00': 'Lamp Life Expired',
            b'\x00\x01\x00\x00': 'Lamp Life Expired',
            b'\x00\x02\x00\x00': 'Format Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Failure',
            b'\x00\x00\x08\x00': 'Lamp Housing Error',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'High Temperature',
            b'\x00\x00\x00\x08': 'Sensor Error',
            b'\x00\x00\x00\x10': 'Pump Error',
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                    self.WriteStatus('DeviceStatus', value, qualifier)
                else:
                    print('Invalid Command for UpdateDeviceStatus')
            except IndexError:
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            if len(res) == 104:
                try:
                    value = unpack('<I', res[91:95])[0] / 3600
                    self.WriteStatus('FilterUsage', int(value), qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateFilterUsage')

                try:
                    value1 = unpack('<I', res[99:103])[0] / 3600
                    self.WriteStatus('OperationHours', int(value1), qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for OperationHours')
            else:
                print('Invalid Command for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x9B',
            'Off': b'\x02\x9C'
        }

        FreezeCmdString = b'\x01\x98\x00\x00\x01' + ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': b'\x01\x09',
            'Computer 2': b'\x02\x0A',
            'HDMI': b'\x1A\x22',
            'Video': b'\x06\x0E',
            'S-Video': b'\x0B\x13',
            'Viewer': b'\x1F\x27',
            'LAN': b'\x20\x28'
        }

        InputCmdString = b'\x02\x03\x00\x00\x02\x01' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': b'\x01\xBE',
            'Normal': b'\x00\xBD'
        }

        LampModeCmdString = b'\x03\xB1\x00\x00\x02\x07' + ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Eco',
            b'\x00': 'Normal'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 8:
                    value = ValueStateValues[res[6:7]]
                    self.WriteStatus('LampMode', value, qualifier)
                else:
                    print('Invalid Command for UpdateLampMode')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x8C\x00\x00\x00\x8F'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    normal = unpack('<I', res[5:9])[0] / 3600
                    eco = unpack('<I', res[9:13])[0] / 3600
                    value = normal + eco
                    self.WriteStatus('LampUsage', int(value), qualifier)
                else:
                    print('Invalid Command for UpdateLampUsage')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x07\x00\x1A',
            'Down': b'\x08\x00\x1B',
            'Left': b'\x0A\x00\x1D',
            'Right': b'\x09\x00\x1C',
            'Enter': b'\x0B\x00\x1E',
            'Menu': b'\x06\x00\x19',
            'Cancel': b'\x0C\x00\x1F'
        }

        MenuNavigationCmdString = b'\x02\x0F\x00\x00\x02' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x14\x00\x00\x00\x16',
            'Off': b'\x02\x15\x00\x00\x00\x17'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPictureMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        PictureMuteCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMute', PictureMuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            b'\x04': 'On',
            b'\x00': 'Off',
            b'\x06': 'Off',
            b'\x02': 'Warming Up',
            b'\x03': 'Warming Up',
            b'\x05': 'Cooling Down'
        }

        AudioMuteState = {
           b'\x01': 'On',
           b'\x00': 'Off'
        }

        InputState = {
           b'\x01\x01': 'Computer 1',
           b'\x02\x01': 'Computer 2',
           b'\x01\x06': 'HDMI',
           b'\x01\x02': 'Video',
           b'\x01\x03': 'S-Video',
           b'\x01\x07': 'Viewer',
           b'\x02\x07': 'LAN'
        }

        PictureMuteState = {
           b'\x01': 'On',
           b'\x00': 'Off'
        }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            if len(res) == 22:
                try:
                    powerValue = PowerState[res[6:7]]
                    self.WriteStatus('Power', powerValue, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

                try:
                    audioValue = AudioMuteState[res[12:13]]
                    self.WriteStatus('AudioMute', audioValue, None)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

                try:
                    inputValue = InputState[res[8:10]]
                    self.WriteStatus('Input', inputValue, None)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

                try:
                    PictureMuteValue = PictureMuteState[res[11:12]]
                    self.WriteStatus('PictureMute', PictureMuteValue, None)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')
            else:
                print('Invalid Command for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = (0x1D + value) & 0xFF
            VolumeCmdString = pack('>8sBBB', b'\x03\x10\x00\x00\x05\x05\x00\x00', value, 0x00, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = res[12]
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    print('Invalid Command for UpdateVolume')
            except (KeyError, IndexError):
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
            b'\x02\x07': 'No Signal.',
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
        if response[5:7] in DEVICE_ERROR_CODES and response[0:1] in (b'\xA0', b'\xA1', b'\xA2', b'\xA3'):
            print(command + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]])
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        SetDelim = {
            'AspectRatio': self.SetRegAspectRatio,
            'AudioMute': self.SetRegAudioMute,
            'AutoImage': self.SetRegAutoImage,
            'Freeze': self.SetRegFreeze,
            'Input': self.SetRegInput,
            'LampMode': self.SetRegLampMode,
            'MenuNavigation': self.SetRegMenuNavigation,
            'OnScreenDisplay': self.SetRegOnScreenDisplay,
            'PictureMute': self.SetRegPictureMute,
            'Power': self.SetRegPower,
            'Volume': self.SetRegVolume
            }

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            regex = SetDelim[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        UpdateDelim = {
            'AspectRatio': self.GetRegAspectRatio,
            'DeviceStatus': self.GetRegDeviceStatus,
            'FilterUsage': self.GetRegFilterUsage,
            'LampMode': self.GetRegLampMode,
            'LampUsage': self.GetRegLampUsage,
            'Power': self.GetRegPower,
            'Volume': self.GetRegVolume
            }

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            regex = UpdateDelim[command]
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
