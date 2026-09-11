from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack

class DeviceSerialClass:

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
        self.Models = {
            'VPL-CH375': self.sony_1_899_70_Models,
            'VPL-CH350': self.sony_1_899_50_Models,
            'VPL-CH370': self.sony_1_899_70_Models,
            'VPL-CH355': self.sony_1_899_50_Models,
            'VPL-CH353': self.sony_1_899_50_Models,
            'VPL-CH358': self.sony_1_899_50_Models,
            'VPL-CH373': self.sony_1_899_70_Models,
            'VPL-CH378': self.sony_1_899_70_Models,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
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

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x00\x20\x9A',
            'Zoom': b'\x03\x23\x9A',
            '4:3': b'\x09\x29\x9A',
            '16:9': b'\x0A\x2A\x9A',
            'Normal': b'\x01\x21\x9A',
            'Full 1': b'\x07\x27\x9A',
            'Full 2': b'\x08\x28\x9A',
            'Full 3': b'\x10\x30\x9A'
        }

        AspectRatioCmdString = b'\xA9\x00\x20\x00\x00' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Full',
            b'\x03': 'Zoom',
            b'\x09': '4:3',
            b'\x0A': '16:9',
            b'\x01': 'Normal',
            b'\x07': 'Full 1',
            b'\x08': 'Full 2',
            b'\x10': 'Full 3'
        }

        AspectRatioCmdString = b'\xA9\x00\x20\x01\x00\x00\x21\x9A'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31\x9A',
            'Off': b'\x00\x31\x9A'
        }

        AudioMuteCmdString = b'\xA9\x00\x31\x00\x00' + ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\xA9\x00\x31\x01\x00\x00\x31\x9A'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xA9\x17\x7B\x00\x00\x00\x7F\x9A'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00\x3E\x9A',
            'CC1': b'\x01\x3F\x9A',
            'CC2': b'\x02\x3E\x9A',
            'CC3': b'\x03\x3F\x9A',
            'CC4': b'\x04\x3E\x9A',
            'Text 1': b'\x05\x3F\x9A',
            'Text 2': b'\x06\x3E\x9A',
            'Text 3': b'\x07\x3F\x9A',
            'Text 4': b'\x08\x3E\x9A'
        }

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x00\x00' + ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'CC1',
            b'\x02': 'CC2',
            b'\x03': 'CC3',
            b'\x04': 'CC4',
            b'\x05': 'Text 1',
            b'\x06': 'Text 2',
            b'\x07': 'Text 3',
            b'\x08': 'Text 4',
            b'\x00': 'Off'
        }

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x01\x00\x00\x3F\x9A'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'No Error',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temp Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Warning Error',
            b'\x80': 'NVM Data Error'
        }

        DeviceStatusCmdString = b'\xA9\x01\x01\x01\x00\x00\x01\x9A'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\xA9\x19\x67\x00\x00\x00\x7F\x9A'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Input A': b'\xA9\x17\x2B\x00\x00\x00\x3F\x9A',
            'Input B': b'\xA9\x17\x2C\x00\x00\x00\x3F\x9A',
            'Input C': b'\xA9\x17\x6F\x00\x00\x00\x7F\x9A',
            'Input D': b'\xA9\x17\x70\x00\x00\x00\x77\x9A',
            'USB Type B': b'\xA9\x17\x71\x00\x00\x00\x77\x9A',
            'S-Video': b'\xA9\x17\x5F\x00\x00\x00\x5F\x9A',
            'Toggle': b'\xA9\x17\x57\x00\x00\x00\x57\x9A',
            'Video': b'\xA9\x17\x2A\x00\x00\x00\x3F\x9A',
            'Network': b'\xA9\x17\x06\x00\x00\x00\x17\x9A'

        }
        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'Input A',
            b'\x03': 'Input B',
            b'\x04': 'Input C',
            b'\x05': 'Input D',
            b'\x06': 'USB Type B',
            b'\x01': 'S-Video',
            b'\x00': 'Video',
            b'\x07': 'Network'
        }

        InputCmdString = b'\xA9\x00\x01\x01\x00\x00\x01\x9A'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeCmdString = b'\xA9\x00\x40\x00\x00' + self.LampModeNames[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\xA9\x00\x40\x01\x00\x00\x41\x9A'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = self.LampModeStates[res[5:6]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xA9\x01\x13\x01\x00\x00\x13\x9A'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = res[4:6]
                value = unpack('>h', value)[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': (0x29, 0x3F),
            'Right': (0x33, 0x37),
            'Left': (0x34, 0x37),
            'Up': (0x35, 0x37),
            'Down': (0x36, 0x37),
            'Enter': (0x5A, 0x5F)
        }

        MenuNavigationCmdString = pack('>8B', 0xA9, 0x17, ValueStateValues[value][0], 0x00, 0x00, 0x00, ValueStateValues[value][1], 0x9A)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\xA9\x01\x12\x01\x00\x00\x13\x9A'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = res[4:6]
                value = unpack('>h', value)[0]
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA9\x17\x2E',
            'Off': b'\xA9\x17\x2F'
        }

        PowerValue = ValueStateValues[value]
        PowerCmdString = PowerValue + b'\x00\x00\x00\x3F\x9A'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Warming Up',
            b'\x02': 'Warming Up',
            b'\x03': 'On',
            b'\x04': 'Cooling Down',
            b'\x05': 'Cooling Down',
            b'\x06': 'Cooling Down',
            b'\x07': 'Cooling Down',
            b'\x08': 'Off'
        }

        PowerCmdString = b'\xA9\x01\x02\x01\x00\x00\x03\x9A'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31\x9A',
            'Off': b'\x00\x30\x9A'
        }

        VideoMuteCmdString = b'\xA9\x00\x30\x00\x00' + ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        VideoMuteCmdString = b'\xA9\x00\x30\x01\x00\x00\x31\x9A'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Checksum = 0x16 | value
            VolumeCmdString = pack('>8B', 0xA9, 0x00, 0x16, 0x00, 0x00, value, Checksum, 0x9A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xA9\x00\x16\x01\x00\x00\x17\x9A'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[5:6][0]
                self.WriteStatus('Volume', value, qualifier)
            except (IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x9A')
            if not res:
                self.Error(['No response received'])

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command. Unidrectional mode')
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x9A')
            if not res:
                return b''
            else:
                return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def sony_1_899_50_Models(self):

        self.LampModeStates = {
            b'\x00' : 'High', 
            b'\x01' : 'Standard', 
            b'\x02' : 'Low'
        }

        self.LampModeNames = {
            'High'      : b'\x00\x40\x9A', 
            'Standard'  : b'\x01\x41\x9A', 
            'Low'       : b'\x02\x42\x9A'
        }

    def sony_1_899_70_Models(self):

        self.LampModeStates = {
            b'\x00' : 'High', 
            b'\x01' : 'Standard', 
            b'\x02' : 'Low', 
            b'\x03' : 'Auto'
        }

        self.LampModeNames = {
            'High'      : b'\x00\x40\x9A', 
            'Standard'  : b'\x01\x41\x9A', 
            'Low'       : b'\x02\x42\x9A', 
            'Auto'      : b'\x03\x43\x9A'
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

class DeviceEthernetClass:

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
        self.Models = {
            'VPL-CH353': self.sony_1_899_50_Models,
            'VPL-CH373': self.sony_1_899_70_Models,
            'VPL-CH378': self.sony_1_899_70_Models,
            'VPL-CH358': self.sony_1_899_50_Models,
            'VPL-CH350': self.sony_1_899_50_Models,
            'VPL-CH355': self.sony_1_899_50_Models,
            'VPL-CH370': self.sony_1_899_70_Models,
            'VPL-CH375': self.sony_1_899_70_Models,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
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
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x00\x00\x20\x02\x01(\x00|\x01|\x03|\x07|\x08|\x09|\x10|\x0A)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x31\x02\x00(\x00|\x01)'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x3E\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08)'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x01\x02\x00(\x00|\x01|\x02|\x04|\x08|\x10|\x20|\x40|\x80)'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x01\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x40\x02\x00(\x00|\x01|\x02|\x03)'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x13\x02([\x00-\xFF]{2})'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x12\x02([\x00-\xFF]{2})'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x02\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x30\x02\x00(\x00|\x01)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x16\x02\x00([\x00-\x64])'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x00',
            'Zoom': b'\x03',
            '4:3': b'\x09',
            '16:9': b'\x0A',
            'Full 1': b'\x07',
            'Full 2': b'\x08',
            'Full 3': b'\x10',
            'Normal': b'\x01'
        }

        AspectRatioCmdString = b'\x02\x0ASONY\x00\x00\x20\x02\x00' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x02\x0ASONY\x01\x00\x20\x02\x00\x00'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00': 'Full',
            '\x03': 'Zoom',
            '\x09': '4:3',
            '\x0A': '16:9',
            '\x07': 'Full 1',
            '\x08': 'Full 2',
            '\x10': 'Full 3',
            '\x01': 'Normal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b'\x02\x0ASONY\x00\x00\x31\x02\x00' + ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x02\x0ASONY\x01\x00\x31\x02\x00\x00'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0ASONY\x00\x17\x7B\x02\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00',
            'CC1': b'\x01',
            'CC2': b'\x02',
            'CC3': b'\x03',
            'CC4': b'\x04',
            'Text 1': b'\x05',
            'Text 2': b'\x06',
            'Text 3': b'\x07',
            'Text 4': b'\x08'
        }

        ClosedCaptionCmdString = b'\x02\x0ASONY\x00\x00\x3E\x02\x00' + ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\x02\x0ASONY\x01\x00\x3E\x02\x00\x00'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '\x01': 'CC1',
            '\x02': 'CC2',
            '\x03': 'CC3',
            '\x04': 'CC4',
            '\x05': 'Text 1',
            '\x06': 'Text 2',
            '\x07': 'Text 3',
            '\x08': 'Text 4',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\x02\x0ASONY\x01\x01\x01\x02\x00\x00'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'No Error',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temp Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Warning Error',
            b'\x80': 'NVM Data Error'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x02\x0ASONY\x00\x19\x67\x02\x00\x00'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Input A': b'\x02\x0ASONY\x00\x17\x2B\x02\x00\x00',
            'Input B': b'\x02\x0ASONY\x00\x17\x2C\x02\x00\x00',
            'Input C': b'\x02\x0ASONY\x00\x17\x6F\x02\x00\x00',
            'Input D': b'\x02\x0ASONY\x00\x17\x70\x02\x00\x00',
            'Video': b'\x02\x0ASONY\x00\x17\x2A\x02\x00\x00',
            'S-Video': b'\x02\x0ASONY\x00\x17\x5F\x02\x00\x00',
            'Network': b'\x02\x0ASONY\x00\x00\x01\x02\x00\x07',
            'USB Type B': b'\x02\x0ASONY\x00\x17\x71\x02\x00\x00'
        }

        if value == 'Toggle':
            self.SendAndWait(b'\x02\x0ASONY\x00\x17\x57\x02\x00\x00', 0.2)  # This will bring the input toggle menu
            self.__SetHelper('Input', b'\x02\x0ASONY\x00\x17\x57\x02\x00\x00', value, qualifier)  # This will select the next input
        else:
            self.__SetHelper('Input', ValueStateValues[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02\x0ASONY\x01\x00\x01\x02\x00\x00'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x02': 'Input A',
            '\x03': 'Input B',
            '\x04': 'Input C',
            '\x05': 'Input D',
            '\x00': 'Video',
            '\x01': 'S-Video',
            '\x07': 'Network',
            '\x06': 'USB Type B'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeCmdString = b'\x02\x0ASONY\x00\x00\x40\x02\x00' + self.LampModeNames[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\x02\x0ASONY\x01\x00\x40\x02\x00\x00'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        value = self.LampModeStates[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x02\x0ASONY\x01\x01\x13\x02\x00\x00'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x29',
            'Right': b'\x33',
            'Left': b'\x34',
            'Up': b'\x35',
            'Down': b'\x36',
            'Enter': b'\x5A'
        }

        MenuNavigationCmdString = b'\x02\x0ASONY\x00\x17' + ValueStateValues[value] + b'\x02\x00\x00'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02\x0ASONY\x01\x01\x12\x02\x00\x00'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x17\x2E',
            'Off': b'\x17\x2F',
        }

        PowerCmdString = b'\x02\x0ASONY\x00' + ValueStateValues[value] + b'\x02\x00\x00'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x02\x0ASONY\x01\x01\x02\x02\x00\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x03': 'On',
            '\x00': 'Off',
            '\x08': 'Off',
            '\x01': 'Warming Up',
            '\x02': 'Warming Up',
            '\x04': 'Cooling Down',
            '\x05': 'Cooling Down',
            '\x06': 'Cooling Down',
            '\x07': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoMuteCmdString = b'\x02\x0ASONY\x00\x00\x30\x02\x00' + ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x02\x0ASONY\x01\x00\x30\x02\x00\x00'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('>12B', 0x02, 0x0A, 0x53, 0x4F, 0x4E, 0x59, 0x00, 0x00, 0x16, 0x02, 0x00, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x02\x0ASONY\x01\x00\x16\x02\x00\x00'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command. Unidirectional mode')
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

    def sony_1_899_50_Models(self):

        self.LampModeStates = {
            '\x00' : 'High', 
            '\x01' : 'Standard', 
            '\x02' : 'Low'
        }

        self.LampModeNames = {
            'High'      : b'\x00', 
            'Standard'  : b'\x01', 
            'Low'       : b'\x02'
        }

    def sony_1_899_70_Models(self):



        self.LampModeStates = {
            '\x00' : 'High', 
            '\x01' : 'Standard', 
            '\x02' : 'Low', 
            '\x03' : 'Auto'
        }

        self.LampModeNames = {
            'High'      : b'\x00', 
            'Standard'  : b'\x01', 
            'Low'       : b'\x02', 
            'Auto'      : b'\x03'
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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
        
class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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

