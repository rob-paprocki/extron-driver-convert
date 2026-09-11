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
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AspectRatio_Set =       re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')
            self.AutoImage_Set =         re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})') 
            self.ClosedCaption_Set =     re.compile(b'([\x20-\x23][\x00-\xFF]{7})|([\xA0-\xA3][\x00-\xFF]{7})')
            self.Freeze_Set =            re.compile(b'(\x21\x98[\x00-xFF]{5})|(\xA1\x98[\x00-\xFF]{6})') 
            self.Input_Set =             re.compile(b'(\x22\x03[\x00-\xFF]{5})|(\xA2\x03[\x00-\xFF]{6})')
            self.LampMode_Set =          re.compile(b'(\x23\xB1[\x00-\xFF]{6})|(\xA3\xB1[\x00-\xFF]{6})')
            self.MenuNavigation_Set =    re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
            self.PIPInput_Set =          re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA2\xB0[\x00-\xFF]{6})')
            self.PIPPosition_Set =       re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA2\xB0[\x00-\xFF]{6})')
            self.PIPMode_Set =           re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA2\xB0[\x00-\xFF]{6})')
            self.Power_Set =             re.compile(b'(\x22\x00[\x00-\xFF]{4})|(\xA2\x00[\x00-\xFF]{6})')
            self.VideoMute_Set =         re.compile(b'(\x22[\x00-\xFF]{5})|(\xA2\x10[\x00-\xFF]{6})')
            self.AspectRatio_Update =       re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})')
            self.ClosedCaption_Update =     re.compile(b'([\x20-\x23][\x00-\xFF]{7})|([\xA0-\xA3][\x00-\xFF]{7})')        
            self.DeviceStatus_Update =      re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})')
            self.FilterUsage_Update =       re.compile(b'(\x23\x8A[\x00-\xFF]{102})|(\xA3\x8A[\x00-\xFF]{6})') 
            self.Input_Update =             re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.LampMode_Update =          re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})')
            self.LampUsage_Update =         re.compile(b'(\x23\x96[\x00-\xFF]{10})|(\xA3\x96[\x00-\xFF]{6})')
            self.PIPInput_Update =          re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA3\xB0[\x00-\xFF]{6})')
            self.PIPPosition_Update =       re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA3\xB0[\x00-\xFF]{6})')
            self.PIPMode_Update =           re.compile(b'(\x23\xB0[\x00-\xFF]{7})|(\xA3\xB0[\x00-\xFF]{6})')
            self.Power_Update =             re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.VideoMute_Update =         re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Letterbox'  : b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31', 
            '16:9'       : b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32', 
            '4:3 Fill'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34', 
            '5:4'        : b'\x03\x10\x00\x00\x05\x18\x00\x00\x0B\x00\x3B', 
            'Native'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E', 
            '16:10'      : b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C', 
            '15:9'       : b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D', 
            'Auto'       : b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35', 
            'Window'     : b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30', 
            'Zoom'       : b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37', 
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'Letterbox', 
            0x02 : '16:9', 
            0x04 : '4:3 Fill', 
            0x0B : '5:4', 
            0x0E : '16:10', 
            0x0C : '15:9', 
            0x0D : 'Native', 
            0x05 : 'Auto', 
            0x00 : 'Window', 
            0x07 : 'Zoom', 
        }

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = ValueStateValues[res[12]]
                    self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Closed Caption 1' : b'\x03\xB1\x00\x00\x02\x09\x01\xC0', 
            'Closed Caption 2' : b'\x03\xB1\x00\x00\x02\x09\x02\xC1', 
            'Closed Caption 3' : b'\x03\xB1\x00\x00\x02\x09\x03\xC2', 
            'Closed Caption 4' : b'\x03\xB1\x00\x00\x02\x09\x04\xC3', 
            'Text1'            : b'\x03\xB1\x00\x00\x02\x09\x05\xC4', 
            'Text2'            : b'\x03\xB1\x00\x00\x02\x09\x06\xC5', 
            'Text3'            : b'\x03\xB1\x00\x00\x02\x09\x07\xC6', 
            'Text4'            : b'\x03\xB1\x00\x00\x02\x09\x08\xC7', 
            'Off'              : b'\x03\xB1\x00\x00\x02\x09\x00\xBF',
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'Closed Caption 1', 
            0x02 : 'Closed Caption 2', 
            0x03 : 'Closed Caption 3', 
            0x04 : 'Closed Caption 4', 
            0x05 : 'Text1', 
            0x06 : 'Text2', 
            0x07 : 'Text3', 
            0x08 : 'Text4', 
            0x00 : 'Off'
        }

        ClosedCaptionCmdString = b'\x03\xB0\x00\x00\x01\x09\xBD'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                if res[0:1] == b'\x20' or res[0:1] == b'\x21' or res[0:1] == b'\x22' or res[0:1] == b'\x23':
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ErrorStatus = {
            b'\x00\x00\x00\x00'  : 'Normal',
            b'\x01\x00\x00\x00'  : 'Lamp Cover Error', 
            b'\x02\x00\x00\x00'  : 'Temp Error (Bimetal)', 
            b'\x10\x00\x00\x00'  : 'Fan Failure', 
            b'\x20\x00\x00\x00'  : 'Power Error', 
            b'\x40\x00\x00\x00'  : 'Lamp1 Error', 
            b'\x80\x00\x00\x00'  : 'Lamp1 Life Expired', 

            b'\x00\x01\x00\x00'  : 'Lamp1 Life Limit Reached', 
            b'\x00\x02\x00\x00'  : 'Formatter Error', 
            b'\x00\x04\x00\x00'  : 'Lamp2 Error', 

            b'\x00\x00\x02\x00'  : 'FPGA error', 
            b'\x00\x00\x04\x00'  : 'Temp Error (Sensor)', 
            b'\x00\x00\x08\x00'  : 'Lamp1 Housing Error', 
            b'\x00\x00\x10\x00'  : 'Lamp1 Data Error', 
            b'\x00\x00\x20\x00'  : 'Mirror Cover Error', 
            b'\x00\x00\x40\x00'  : 'Lamp2 Life Expired', 
            b'\x00\x00\x80\x00'  : 'Lamp2 Life Limit Reached', 

            b'\x00\x00\x00\x01'  : 'Lamp2 Housing Error', 
            b'\x00\x00\x00\x02'  : 'Lamp2 Data Error', 
            b'\x00\x00\x00\x04'  : 'High Temp Due to Dust', 
            b'\x00\x00\x00\x08'  : 'Foreign Object Sensor Error', 
            b'\x00\x00\x00\x10'  : 'Pump Error', 
        }
        
        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = ErrorStatus.get(res[5:9], 'Multiple Errors')
                    self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 104:
                    filter_str = res[91:95]
                    filter_str = filter_str[::-1]
                    filter_val1 = filter_str[0]
                    filter_val2 = filter_str[1]
                    filter_val3 = filter_str[2]
                    filter_val4 = filter_str[3]
                    filter_value = round(int(hex(filter_val1) + hex(filter_val2)[2:4] + hex(filter_val3)[2:4] + hex(filter_val4)[2:4], 16) / 3600)
                    self.WriteStatus('FilterUsage', filter_value, qualifier)
                    operate_str = res[99:103]
                    operate_str = operate_str[::-1]
                    operate_val1 = operate_str[0]
                    operate_val2 = operate_str[1]
                    operate_val3 = operate_str[2]
                    operate_val4 = operate_str[3]
                    operate_value = round(int(hex(operate_val1) + hex(operate_val2)[2:4] + hex(operate_val3)[2:4] + hex(operate_val4)[2:4], 16) / 3600)
                    
                    self.WriteStatus('OperationHours', operate_value, qualifier)
                else:
                    self.__CheckResponseForErrors('FilterUsage', res)
            except (KeyError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'Off' : b'\x01\x98\x00\x00\x01\x02\x9C',
            'On'  : b'\x01\x98\x00\x00\x01\x01\x9B'
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1'   : b'\x02\x03\x00\x00\x02\x01\x01\x09', 
            'Computer 2'   : b'\x02\x03\x00\x00\x02\x01\x02\x0A', 
            'Computer 3'   : b'\x02\x03\x00\x00\x02\x01\x03\x0B', 
            'HDMI'         : b'\x02\x03\x00\x00\x02\x01\x1A\x22', 
            'Display Port' : b'\x02\x03\x00\x00\x02\x01\x1B\x23', 
            'Video'        : b'\x02\x03\x00\x00\x02\x01\x06\x0E', 
            'S-Video'      : b'\x02\x03\x00\x00\x02\x01\x0B\x13', 
            'LAN'          : b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'Slot'         : b'\x02\x03\x00\x00\x02\x01\x1C\x24',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x01\x01' : 'Computer 1', 
            b'\x02\x01' : 'Computer 2', 
            b'\x03\x01' : 'Computer 3', 
            b'\x01\x06' : 'HDMI', 
            b'\x02\x06' : 'Display Port', 
            b'\x01\x02' : 'Video', 
            b'\x01\x03' : 'S-Video', 
            b'\x02\x07' : 'LAN',
            b'\x03\x06' : 'Slot',
        }

        InputCmdString = b'\x00\x85\x00\x00\x01\x02\x88'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = ValueStateValues[res[7:9]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : b'\x03\xB1\x00\x00\x02\x07\x00\xBD', 
            'Eco'    : b'\x03\xB1\x00\x00\x02\x07\x01\xBE'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Eco',
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if res[0:2] == b'\x23\xB0':
                    value = ValueStateValues[res[6]]
                    self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampValues = {
            '1' :   0x00,
            '2' :   0x01,
        }

        lamp = qualifier['Lamp']
        chksum = 0x03 + 0x96 + 0x02 + LampValues[lamp] + 0x01
        LampUsageCmdString = pack('>8B', 0x03, 0x96, 0x00, 0x00, 0x02, LampValues[lamp], 0x01, chksum)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 12:
                    temp_usage = res[7:11]
                    temp_usage = temp_usage[::-1]
                    lamp_val1 = temp_usage[0]
                    lamp_val2 = temp_usage[1]
                    lamp_val3 = temp_usage[2]
                    lamp_val4 = temp_usage[3]
                    lamp_value = round(int(hex(lamp_val1) + hex(lamp_val2)[2:4] + hex(lamp_val3)[2:4] + hex(lamp_val4)[2:4], 16) / 3600)
            
                    self.WriteStatus('LampUsage', lamp_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'   : b'\x02\x0F\x00\x00\x02\x06\x00\x19', 
            'Up'     : b'\x02\x0F\x00\x00\x02\x07\x00\x1A', 
            'Down'   : b'\x02\x0F\x00\x00\x02\x08\x00\x1B', 
            'Left'   : b'\x02\x0F\x00\x00\x02\x0A\x00\x1D', 
            'Right'  : b'\x02\x0F\x00\x00\x02\x09\x00\x1C', 
            'Enter'  : b'\x02\x0F\x00\x00\x02\x0B\x00\x1E', 
            'Cancel' : b'\x02\x0F\x00\x00\x02\x0C\x00\x1F',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def UpdateOperationHours(self, value, qualifier):

        self.UpdateFilterUsage(value, qualifier)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'S-Video' : b'\x03\xB1\x00\x00\x03\xC5\x02\x02\x80', 
            'Video'   : b'\x03\xB1\x00\x00\x03\xC5\x02\x01\x7F', 
            'Off'     : b'\x03\xB1\x00\x00\x03\xC5\x02\x00\x7E'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'S-Video', 
            0x01 : 'Video', 
            0x00 : 'Off'
        }

        PIPInputCmdString = b'\x03\xB0\x00\x00\x02\xC5\x02\x7C'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 9:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP'          : b'\x03\xB1\x00\x00\x03\xC5\x00\x00\x7C', 
            'Side by Side' : b'\x03\xB1\x00\x00\x03\xC5\x00\x01\x7D'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'PIP', 
            0x01 : 'Side by Side'
        }

        PIPModeCmdString = b'\x03\xB0\x00\x00\x02\xC5\x00\x7A'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 9:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left'     : b'\x03\xB1\x00\x00\x03\xC5\x01\x00\x7D', 
            'Top Right'    : b'\x03\xB1\x00\x00\x03\xC5\x01\x01\x7E', 
            'Bottom Left'  : b'\x03\xB1\x00\x00\x03\xC5\x01\x02\x7F', 
            'Bottom Right' : b'\x03\xB1\x00\x00\x03\xC5\x01\x03\x80'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Top Left', 
            0x01 : 'Top Right', 
            0x02 : 'Bottom Left', 
            0x03 : 'Bottom Right'
        }

        PIPPositionCmdString = b'\x03\xB0\x00\x00\x02\xC5\x01\x7B'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 9:
                    value = ValueStateValues[res[7]]
                    self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x00\x00\x00\x00\x02', 
            'Off' : b'\x02\x01\x00\x00\x00\x03', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x04 : 'On', 
            0x00 : 'Off', 
            0x06 : 'Off',   
            0x0F : 'Off',  
            0x10 : 'Off',                    
            0x05 : 'Cooling Down',
            0x07 : 'Cooling Down',
            0x01 : 'Warming Up',
            0x02 : 'Warming Up',
            0x03 : 'Warming Up',
            0x09 : 'Warming Up',
        }

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = ValueStateValues[res[10]]
                    self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x10\x00\x00\x00\x12', 
            'Off' : b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        VideoMuteCmdString = b'\x00\x85\x00\x00\x01\x03\x89'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': "Unknown Command",
            b'\x00\x01': "The current model does not support this function.",
            b'\x01\x00': "Unvalid values specified",
            b'\x01\x01': "Specified terminal is unavailable or cannot be selected",
            b'\x01\x02': "Selected language is not available",
            b'\x02\x00': "Available memory reservation error",
            b'\x02\x02': "Operating memory",
            b'\x02\x03': "Setting not possible",
            b'\x02\x04': "On Forced on-screen mute mode",
            b'\x02\x07': "No Signal",
            b'\x02\x08': "Displaying a test pattern or PC Card Fills screen.",
            b'\x02\x0A': "Memory Operation Failed",
            b'\x02\x0D': "Power Off inhibited",
            b'\x02\x0E': "Execution error",
            b'\x02\x0F': "No operation authority",
            b'\x03\x00': "Specified gain number is wrong",
            b'\x03\x01': "Specified gain not available",
            b'\x03\x02': "Adjustment failed",
        }   
        if (response[0:1] == b'\xA0' or response[0:1] == b'\xA1' or response[0:1] == b'\xA2' or response[0:1] == b'\xA3') and response[5:7] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[-3:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        CommandDelimValues = {
            'AspectRatio'       :  self.AspectRatio_Set,
            'AutoImage'         :  self.AutoImage_Set, 
            'ClosedCaption'     :  self.ClosedCaption_Set,
            'Freeze'            : self.Freeze_Set,
            'Input'             :  self.Input_Set,
            'LampMode'          :  self.LampMode_Set,
            'MenuNavigation'    :  self.MenuNavigation_Set,
            'PIPInput'          :  self.PIPInput_Set,
            'PIPPosition'       :  self.PIPPosition_Set,
            'PIPMode'           :  self.PIPMode_Set,
            'Power'             :  self.Power_Set,
            'VideoMute'         :  self.VideoMute_Set,
        }

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
            res = b''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=CommandDelimValues[command])
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        CommandDelimValues = {
            'AspectRatio'       :  self.AspectRatio_Update,
            'ClosedCaption'     :  self.ClosedCaption_Update,        
            'DeviceStatus'      :  self.DeviceStatus_Update,
            'FilterUsage'       :  self.FilterUsage_Update, 
            'Input'             :  self.Input_Update,
            'LampMode'          :  self.LampMode_Update,
            'LampUsage'         :  self.LampUsage_Update,
            'PIPInput'          :  self.PIPInput_Update,
            'PIPPosition'       :  self.PIPPosition_Update,
            'PIPMode'           :  self.PIPMode_Update,
            'Power'             :  self.Power_Update,
            'VideoMute'         :  self.VideoMute_Update,
        }
        
            
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=CommandDelimValues[command])
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

