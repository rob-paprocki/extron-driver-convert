from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import unpack, pack
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
        self.Models = {
            'MT1075': self.nec_1_2745_MT1,
            'MT1065': self.nec_1_2745_MT1,
            'MT1060': self.nec_1_2745_MT1,
            'MT860': self.nec_1_2745_MT8,
            'MT1060R': self.nec_1_2745_MT1,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':

            self.AspectRatio_Set =          re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})') 
            self.AudioMute_Set =            re.compile(b'(\x22[\x11|\x12][\x00-\xFF]{4})|(\xA2[\x11|\x12][\x00-\xFF]{6})') 
            self.AutoImage_Set =            re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})') 
            self.ClosedCaption_Set =        re.compile(b'(\x23\xB1[\x00-\xFF]{6}$)|(\xA3\xB1[\x00-\xFF]{6})') 
            self.Freeze_Set =               re.compile(b'(\x21\x98[\x00-xFF]{5})|(\xA1\x98[\x00-\xFF]{6})') 
            self.Input_Set =                re.compile(b'(\x22\x03[\x00-\xFF]{5})|(\xA2\x03[\x00-\xFF]{6})') 
            self.LampMode_Set =             re.compile(b'(\x23\xB1[\x00-\xFF]{6})|(\xA3\xB1[\x00-\xFF]{6})') 
            self.MenuNavigation_Set =       re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})') 
            self.OnScreenDisplay_Set =      re.compile(b'(\x22[\x14|\x15][\x00-\xFF]{4})|(\xA2[\x14|\x15][\x00-\xFF]{5})')
            self.Power_Set =                re.compile(b'(\x22[\x00|\x01][\x00-\xFF]{4})|(\xA2[\x00|\x01][\x00-\xFF]{5})') 
            self.VideoMute_Set =            re.compile(b'(\x22[\x10|\x11][\x00-\xFF]{4})|(\xA2[\x10|\x11][\x00-\xFF]{5})') 
            self.Volume_Set =               re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})') 


            self.AspectRatio_Update =       re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})') 
            self.ClosedCaption_Update =     re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})') 
            self.DeviceStatus_Update =      re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})') 
            self.FilterUsage_Update =       re.compile(b'(\x23\x8A[\x00-\xFF]{102})|(\xA3\x8A[\x00-\xFF]{6})') 
            self.LampMode_Update =          re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})') 
            self.LampUsage_Update =         re.compile(b'(\x23\x8C[\x00-\xFF]{20})|(\xA3\x8C[\x00-\xFF]{6})') 
            self.Power_Update =             re.compile(b'(\x20\xBF[\x00-\xFF]{20})|(\xA0\xBF[\x00-\xFF]{6})') 
            self.SignalStatus_Update =      re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.Volume_Update =            re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})') 

    def SetAspectRatio(self, value, qualifier):

        AspectStateValues = {
            '4:3 Window' : b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Letterbox'  : b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            'Widescreen' : b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32', 
            'Crop'       : b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            '4:3 Fill'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34'
            }
        AspectRatioCmdString = AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            b'\x00' : '4:3 Window',
            b'\x01' : 'Letterbox',
            b'\x02' : 'Widescreen',
            b'\x03' : 'Crop',
            b'\x04' : '4:3 Fill'
        }

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = AspectRatioStateValues[res[12:13]]
                    self.WriteStatus('AspectRatio', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'Off' : b'\x02\x13\x00\x00\x00\x15',
            'On'  : b'\x02\x12\x00\x00\x00\x14'
            }
        AudioMuteCmdString = AudioMuteValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\xDD\x00\xF0'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off'       : b'\x03\xB1\x00\x00\x02\x09\x00\xBF', 
            'Caption 1' : b'\x03\xB1\x00\x00\x02\x09\x01\xC0', 
            'Caption 2' : b'\x03\xB1\x00\x00\x02\x09\x02\xC1', 
            'Caption 3' : b'\x03\xB1\x00\x00\x02\x09\x03\xC2', 
            'Caption 4' : b'\x03\xB1\x00\x00\x02\x09\x04\xC3', 
            'Text 1'    : b'\x03\xB1\x00\x00\x02\x09\x05\xC4', 
            'Text 2'    : b'\x03\xB1\x00\x00\x02\x09\x06\xC5', 
            'Text 3'    : b'\x03\xB1\x00\x00\x02\x09\x07\xC6', 
            'Text 4'    : b'\x03\xB1\x00\x00\x02\x09\x08\xC7'
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x01' : 'Caption 1', 
            b'\x02' : 'Caption 2', 
            b'\x03' : 'Caption 3', 
            b'\x04' : 'Caption 4', 
            b'\x05' : 'Text 1', 
            b'\x06' : 'Text 2', 
            b'\x07' : 'Text 3', 
            b'\x08' : 'Text 4'
        }
        ClosedCaptionCmdString = b'\x03\xB0\x00\x00\x01\x09\xBD'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 8:
                    value = ValueStateValues[res[6:7]]
                    self.WriteStatus('ClosedCaption', value, qualifier)                    
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')    

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusStateNames = {
            b'\x00\x00\x00\x00' : 'Normal', 
            b'\x01\x00\x00\x00' : 'Lamp Cover Error',
            b'\x02\x00\x00\x00' : 'Temp Error',
            b'\x10\x00\x00\x00' : 'Fan Error',
            b'\x20\x00\x00\x00' : 'Power Error',
            b'\x40\x00\x00\x00' : 'Lamp Error',
            b'\x80\x00\x00\x00' : 'Lamp End of Life',
                                 
            b'\x00\x01\x00\x00' : 'Lamp Beyond Limit',
            b'\x00\x02\x00\x00' : 'Formatter Error',
 
            b'\x00\x00\x04\x00' : 'Temp Error (Sensor)',
            b'\x00\x00\x08\x00' : 'Lamp Housing Error',
            b'\x00\x00\x10\x00' : 'Lamp Data Error',
            b'\x00\x00\x20\x00' : 'Mirror Cover Error',
  
            b'\x00\x00\x00\x04' : 'High Temp (Due to Dust)',
            b'\x00\x00\x00\x08' : 'Foreign Object Sensor Error',
            b'\x00\x00\x00\x10' : 'Pump Error',
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

        FilterUsageCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<I', res[91:95])[0]/3600
                self.WriteStatus('FilterUsage', int(value), qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')
            try:            

                value1 = unpack('<I', res[99:103])[0]/3600
                self.WriteStatus('OperationHours', int(value1), qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'Off' : b'\x01\x98\x00\x00\x01\x02\x9C',
            'On'  : b'\x01\x98\x00\x00\x01\x01\x9B'
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        InputCmdString = self.SetInputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco' : b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Normal' : b'\x03\xB1\x00\x00\x02\x07\x00\xBD'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        LampModeStateValues = {
            b'\x00' : 'Normal', 
            b'\x01' : 'Eco'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateValues[res[6:7]]
                self.WriteStatus('LampMode', value, None)                    
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x8C\x00\x00\x00\x8F'    
        
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:               
                normal = int(unpack('<I', res[5:9])[0]/3600)
                eco = int(unpack('<I', res[9:13])[0]/3600)
                value = eco + normal
                self.WriteStatus('LampUsage', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')
        else:
            print('Inappropriate Command for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\x02\x0F\x00\x00\x02\x07\x00\x1A', 
            'Down'      : b'\x02\x0F\x00\x00\x02\x08\x00\x1B', 
            'Left'      : b'\x02\x0F\x00\x00\x02\x0A\x00\x1D', 
            'Right'     : b'\x02\x0F\x00\x00\x02\x09\x00\x1C', 
            'Menu'      : b'\x02\x0F\x00\x00\x02\x06\x00\x19', 
            'Enter'     : b'\x02\x0F\x00\x00\x02\x0B\x00\x1E', 
            'Cancel'    : b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayState = {
            'On' : b'\x02\x14\x00\x00\x00\x16', 
            'Off' : b'\x02\x15\x00\x00\x00\x17'
            }

        OnScreenDisplayCmdString = OnScreenDisplayState[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateOperationHours(self, value, qualifier):
        self.UpdateFilterUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off' : b'\x02\x01\x00\x00\x00\x03',
            'On'  : b'\x02\x00\x00\x00\x00\x02'
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x04 : 'On', 
            0x00 : 'Off',
            0x06 : 'Off',
            0x0F : 'Off',
            0x10 : 'Off',
            0x01 : 'Warming Up',
            0x02 : 'Warming Up',
            0x05 : 'Cooling Down'
            }

        VideoMuteState = {
            0x01 : 'On',
            0x00 : 'Off'
            }

        AudioMuteState = {
            0x01 : 'On',
            0x00 : 'Off'
            }

        OnScreenDisplayState = {
            0x01 : 'On',
            0x00 : 'Off'
            }
        
        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerState[res[6]]
                self.WriteStatus('Power', PowerValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

            try:
                InputValue = self.GetInputState[res[8:10]]
                self.WriteStatus('Input', InputValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

            try:
                VideoMuteValue = VideoMuteState[res[11]]
                self.WriteStatus('VideoMute', VideoMuteValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

            try:
                AudioMuteValue = AudioMuteState[res[12]]
                self.WriteStatus('AudioMute', AudioMuteValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

            try:
                OSDValue = OnScreenDisplayState[res[13]]
                self.WriteStatus('OnScreenDisplay', OSDValue, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateOnScreenDisplay')

    def UpdateSignalStatus(self, value, qualifier):

        SignalStatusStates = {
            0x01 : 'No Signal Present',
            0x00 : 'Signal Present',
            0x02 : 'Viewer Displaying',
            0x03 : 'Test Pattern Displaying',
            0x04 : 'LAN Displaying'
            }
        SignalStatusCmdString = b'\x00\x85\x00\x00\x01\x02\x88'
        res = self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                value = SignalStatusStates[res[13]]
                self.WriteStatus('SignalStatus', value, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateSignalStatus') 

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'Off' : b'\x02\x11\x00\x00\x00\x13',
            'On'  : b'\x02\x10\x00\x00\x00\x12'
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        res = self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 63
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
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00' : 'Unknown command.',
            b'\x00\x01' : 'This current model does not support this function.',
            b'\x01\x00' : 'Invalid values specificed.',
            b'\x01\x01' : 'Specified terminal is unavailable or cannot be selected.',
            b'\x01\x02' : 'Selected lanugage is not available.',
            b'\x02\x00' : 'Available memory reservation error.',
            b'\x02\x02' : 'Operating memory.',
            b'\x02\x03' : 'Setting not possible.',
            b'\x02\x04' : 'On forced on-screen mute mode.',
            b'\x02\x06' : 'Displaying a signal other than PC Viewer.', 
            b'\x02\x07' : 'No signal.',
            b'\x02\x08' : 'Displaying a test pattern or PC Card fills screen.',
            b'\x02\x09' : 'No PC card is inserted.',
            b'\x02\x0A' : 'Memory operation failed.',
            b'\x02\x0C' : 'Displaying the Entry List.',
            b'\x02\x0D' : 'Power Off inhibited.',
            b'\x02\x0E' : 'Execution error.',
            b'\x02\x0F' : 'No operation authority.',
            b'\x03\x00' : 'Specified gain number is wrong.',
            b'\x03\x01' : 'Selected gain is not available.',
            b'\x03\x02' : 'Adjustment failed.'
            }
        if response[5:7] in DEVICE_ERROR_CODES and (response[0:1] == b'\xA0' or response[0:1] == b'\xA1' or response[0:1] == b'\xA2' or response[0:1] == b'\xA3'):
            errorString = sourceCmdName + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]]
            print(errorString)
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        SetDelim = {
            'AspectRatio'       : self.AspectRatio_Set,
            'AudioMute'         : self.AudioMute_Set,
            'AutoImage'         : self.AutoImage_Set,
            'ClosedCaption'     : self.ClosedCaption_Set,
            'Freeze'            : self.Freeze_Set,
            'Input'             : self.Input_Set,
            'LampMode'          : self.LampMode_Set,
            'MenuNavigation'    : self.MenuNavigation_Set,
            'OnScreenDisplay'   : self.OnScreenDisplay_Set,
            'Power'             : self.Power_Set,
            'VideoMute'         : self.VideoMute_Set,
            'Volume'            : self.Volume_Set            
            }

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=SetDelim[command])
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        UpdateDelim = {
            'AspectRatio'       : self.AspectRatio_Update,
            'ClosedCaption'     : self.ClosedCaption_Update,
            'DeviceStatus'      : self.DeviceStatus_Update,
            'FilterUsage'       : self.FilterUsage_Update,
            'LampMode'          : self.LampMode_Update,
            'LampUsage'         : self.LampUsage_Update,
            'Power'             : self.Power_Update,
            'SignalStatus'      : self.SignalStatus_Update,
            'Volume'            : self.Volume_Update
            }

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=UpdateDelim[command])
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

    def nec_1_2745_MT1(self):
        self.SetInputState = {
            'RGB 1' :           b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'RGB 2' :           b'\x02\x03\x00\x00\x02\x01\x02\x0A',
            'Video' :           b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'S-Video' :         b'\x02\x03\x00\x00\x02\x01\x0B\x13',
            'DVI (Digital)' :   b'\x02\x03\x00\x00\x02\x01\x1A\x22',
            'LAN' :             b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'Viewer' :          b'\x02\x03\x00\x00\x02\x01\x1F\x27'
            }

        self.GetInputState = {
            b'\x01\x01' : 'RGB 1',
            b'\x01\x02' : 'RGB 2',
            b'\x01\x06' : 'Video',
            b'\x01\x0B' : 'S-Video',
            b'\x01\x06' : 'DVI (Digital)',
            b'\x02\x07' : 'LAN',
            b'\x04\x07' : 'Viewer'
            }
        

    def nec_1_2745_MT8(self):
        self.SetInputState = {
            'RGB 1' :           b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'RGB 2' :           b'\x02\x03\x00\x00\x02\x01\x02\x0A',
            'Video' :           b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'S-Video' :         b'\x02\x03\x00\x00\x02\x01\x0B\x13',
            'LAN' :             b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'Viewer' :          b'\x02\x03\x00\x00\x02\x01\x1F\x27'
            }

        self.GetInputState = {
            b'\x01\x01' : 'RGB 1',
            b'\x01\x02' : 'RGB 2',
            b'\x01\x06' : 'Video',
            b'\x01\x0B' : 'S-Video',
            b'\x02\x07' : 'LAN',
            b'\x04\x07' : 'Viewer'
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
