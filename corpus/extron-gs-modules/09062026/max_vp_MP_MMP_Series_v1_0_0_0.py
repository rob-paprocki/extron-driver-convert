from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaptionsChannel': { 'Status': {}},
            'ClosedCaptionsDisplay': { 'Status': {}},
            'ClosedCaptionsMode': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'PbyPArea': { 'Status': {}},
            'PbyPInput': {'Parameters':['Area'], 'Status': {}},
            'PbyPPinP': { 'Status': {}},
            'PbyPSize': { 'Status': {}},
            'PbyPSwap': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PinPArea': { 'Status': {}},
            'PinPInput': {'Parameters':['Area'], 'Status': {}},
            'PinPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'VolumeLevelStatus': {'Parameters':['Input'], 'Status': {}},
            'VolumeStep': {'Parameters':['Input'], 'Status': {}},
            }
                        
        self.Setregex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F\x04\x00|\x1D[\x00-\xFF]{2})')
        self.Updateregex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F\x04\x00|\x1D[\x00-\xFF]{2}|[a-f0-9]{8})')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00', 
            '4:3'    : b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00', 
            '16:9'   : b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00', 
            '16:10'  : b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00', 
            '14:9'   : b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00', 
            'Native' : b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            'Zoom'   : b'\xBE\xEF\x03\x06\x00\x9E\xC4\x01\x00\x08\x20\x30\x00'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x10' : 'Normal', 
            b'\x00' : '4:3', 
            b'\x01' : '16:9', 
            b'\x0A' : '16:10', 
            b'\x09' : '14:9', 
            b'\x08' : 'Native',
            b'\x30' : 'Zoom'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x20\x20\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x20\x20\x00\x00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On', 
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2' : b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3' : b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4' : b'\xBE\xEF\x03\x06\x00\xD2\x82\x01\x00\x02\x37\x04\x00'
        }

        ClosedCaptionsChannelCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)

    def UpdateClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : '1', 
            b'\x02' : '2', 
            b'\x03' : '3', 
            b'\x04' : '4'
        }

        ClosedCaptionsChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionsChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Captions Channel: Invalid/unexpected response'])

    def SetClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'   : b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off'  : b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto' : b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }

        ClosedCaptionsDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x01': 'On',
            b'\x02': 'Off'
        }

        ClosedCaptionsDisplayCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionsDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Captions Display: Invalid/unexpected response'])

    def SetClosedCaptionsMode(self, value, qualifier):

        ValueStateValues = {
            'Captions' : b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text'     : b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }

        ClosedCaptionsModeCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionsMode', ClosedCaptionsModeCmdString, value, qualifier)

    def UpdateClosedCaptionsMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        ClosedCaptionsModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsMode', ClosedCaptionsModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionsMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Captions Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0  : 'Normal', 
            1  : 'Cover Error', 
            2  : 'Fan Error', 
            3  : 'Lamp Error', 
            4  : 'Temp Error', 
            5  : 'Air Flow Error', 
            7  : 'Cold Error', 
            8  : 'Filter Error', 
            15 : 'Shade Error', 
            96 : 'AC Blackout Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        
        FilterUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'
        res2 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1:2][0] * 256 + res[1:2][0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Filter Usage: Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',  
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',  
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00', 
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00', 
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'LAN'           : b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier) 

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Computer In 1', 
            b'\x04' : 'Computer In 2', 
            b'\x03' : 'HDMI 1', 
            b'\x0D' : 'HDMI 2',
            b'\x11' : 'HDBaseT', 
            b'\x01' : 'Video', 
            b'\x0B' : 'LAN'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'        : b'\xBE\xEF\x03\x06\x00\x3B\x37\x01\x00\x00\x33\x30\x00', 
            'Long Life 1'   : b'\xBE\xEF\x03\x06\x00\x6B\x20\x01\x00\x00\x33\x05\x00', 
            'Long Life 2'   : b'\xBE\xEF\x03\x06\x00\x9B\x20\x01\x00\x00\x33\x06\x00',
            'Whisper'       : b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x30' : 'Normal', 
            b'\x05' : 'Long Life 1', 
            b'\x06' : 'Long Life 2', 
            b'\x01' : 'Whisper'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        LampUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'
        res2 = self.__UpdateHelper('LampUsage', LampUsageCmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1:2][0] * 256 + res[1:2][0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetPbyPArea(self, value, qualifier):

        ValueStateValues = {
            'Left'  : [b'\x7A\x26', b'\x00\x00'], 
            'Right' : [b'\xEA\x27', b'\x01\x00']
        }

        PbyPAreaCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x13\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPArea', PbyPAreaCmdString, value, qualifier)

    def UpdatePbyPArea(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Left', 
            b'\x01' : 'Right'
        }

        PbyPAreaCmdString = b'\xBE\xEF\x03\x06\x00\x49\x26\x02\x00\x13\x23\x00\x00'
        res = self.__UpdateHelper('PbyPArea', PbyPAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Area: Invalid/unexpected response'])

    def SetPbyPInput(self, value, qualifier):

        PbyPLeftInputStateValues = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x32\x24\x01\x00\x15\x23\x04\x00',
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00'
        }
        PbyPRightInputStateValues = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x46\x25\x01\x00\x12\x23\x04\x00',
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00'
        }
        
        AreaStates = {
        	'Left'  : PbyPLeftInputStateValues,
        	'Right' : PbyPRightInputStateValues
        }       

        PbyPInputCmdString = AreaStates[qualifier['Area']][value]
        self.__SetHelper('PbyPInput', PbyPInputCmdString, value, qualifier) # No query delay is needed based on testing on device.

    def UpdatePbyPInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Computer In 1', 
            b'\x04' : 'Computer In 2', 
            b'\x03' : 'HDMI 1', 
            b'\x0D' : 'HDMI 2',
            b'\x11' : 'HDBaseT', 
            b'\x01' : 'Video' 
        }

        AreaStates = {
        	'Left'  : b'\xBE\xEF\x03\x06\x00\xC1\x26\x02\x00\x15\x23\x00\x00',
        	'Right' : b'\xBE\xEF\x03\x06\x00\xB5\x27\x02\x00\x12\x23\x00\x00'
        }

        PbyPInputCmdString = AreaStates[qualifier['Area']]
        res = self.__UpdateHelper('PbyPInput', PbyPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Input: Invalid/Unexpected Response'])

    def SetPbyPPinP(self, value, qualifier):

        ValueStateValues = {
            'Off'  : [b'\x3E\x26', b'\x00\x00'], 
            'PbyP' : [b'\xAE\x27', b'\x01\x00'], 
            'PinP' : [b'\x5E\x27', b'\x02\x00']
        }

        PbyPPinPCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x10\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPPinP', PbyPPinPCmdString, value, qualifier)

    def UpdatePbyPPinP(self, value, qualifier):

        
        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x01' : 'PbyP', 
            b'\x02' : 'PinP'
        }

        PbyPPinPCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyPPinP', PbyPPinPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPPinP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP PinP: Invalid/Unexpected Response'])

    def SetPbyPSize(self, value, qualifier):

        ValueStateValues = {
            'Small'  : [b'\xF2\x07', b'\x7F\x00'], 
            'Middle' : [b'\x02\x46', b'\x80\x00'], 
            'Large'  : [b'\x92\x47', b'\x81\x00']
        }

        PbyPSizeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x11\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPSize', PbyPSizeCmdString, value, qualifier)

    def UpdatePbyPSize(self, value, qualifier):

        ValueStateValues = {
            127 : 'Small', 
            128 : 'Middle', 
            129 : 'Large'
        }

        PbyPSizeCmdString = b'\xBE\xEF\x03\x06\x00\xF1\x27\x02\x00\x11\x23\x00\x00'
        res = self.__UpdateHelper('PbyPSize', PbyPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PbyPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Size: Invalid/unexpected response'])

    def SetPbyPSwap(self, value, qualifier):

        PbyPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPSwap', PbyPSwapCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard'      : b'\xBE\xEF\x03\x06\x00\x83\xF5\x01\x00\xBA\x30\x06\x00', 
            'Natural'       : b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00', 
            'Cinema'        : b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00', 
            'Dynamic'       : b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00', 
            'Whiteboard'    : b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00', 
            'Dicom Sim'     : b'\xBE\xEF\x03\x06\x00\x73\xC6\x01\x00\xBA\x30\x41\x00', 
            'User-1'        : b'\xBE\xEF\x03\x06\x00\xE3\xFB\x01\x00\xBA\x30\x10\x00', 
            'User-2'        : b'\xBE\xEF\x03\x06\x00\x73\xFA\x01\x00\xBA\x30\x11\x00', 
            'User-3'        : b'\xBE\xEF\x03\x06\x00\x83\xFA\x01\x00\xBA\x30\x12\x00'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'\x06' : 'Standard', 
            b'\x00' : 'Natural', 
            b'\x01' : 'Cinema', 
            b'\x04' : 'Dynamic', 
            b'\x22' : 'Whiteboard', 
            b'\x41' : 'Dicom Sim', 
            b'\x10' : 'User-1', 
            b'\x11' : 'User-2', 
            b'\x12' : 'User-3'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPinPArea(self, value, qualifier):

        ValueStateValues = {
            'Primary' 	: [b'\x32\x22', b'\x00\x00'], 
            'Secondary' : [b'\xA2\x23', b'\x01\x00']
        }

        PinPAreaCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x05\x23' + ValueStateValues[value][1]
        self.__SetHelper('PinPArea', PinPAreaCmdString, value, qualifier)

    def UpdatePinPArea(self, value, qualifier):

        
        ValueStateValues = {
            0 : 'Primary', 
            1 : 'Secondary'
        }

        PinPAreaCmdString = b'\xBE\xEF\x03\x06\x00\x01\x22\x02\x00\x05\x23\x00\x00'
        res = self.__UpdateHelper('PinPArea', PinPAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PinPArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Area: Invalid/unexpected response'])

    def SetPinPInput(self, value, qualifier):

        PinPInputPrimaryStateValues = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00', 
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x0E\x21\x01\x00\x04\x23\x04\x00', 
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00', 
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',  
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',  
            'Video'         : b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00',  
        }
        PinPInputSecondaryStateValues = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00', 
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x86\x21\x01\x00\x04\x23\x04\x00', 
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00', 
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00', 
        }
        
        AreaStates = {
            'Primary' : PinPInputPrimaryStateValues, 
            'Secondary' : PinPInputSecondaryStateValues
        }
        
        PinPInputCmdString = AreaStates[qualifier['Area']][value]
        self.__SetHelper('PinPInput', PinPInputCmdString, value, qualifier) # No query delay is needed based on testing on device.

    def UpdatePinPInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Computer In 1', 
            b'\x04' : 'Computer In 2', 
            b'\x03' : 'HDMI 1', 
            b'\x0D' : 'HDMI 2',
            b'\x11' : 'HDBaseT', 
            b'\x01' : 'Video' 
        }

        AreaStates = {
        	'Primary'   : b'\xBE\xEF\x03\x06\x00\xFD\x23\x02\x00\x04\x23\x00\x00',
        	'Secondary' : b'\xBE\xEF\x03\x06\x00\x75\x23\x02\x00\x02\x23\x00\x00'
        }

        PinPInputCmdString = AreaStates[qualifier['Area']]

        res = self.__UpdateHelper('PinPInput', PinPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PinPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Input: Invalid/unexpected response'])

    def SetPinPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left'     : b'\xBE\xEF\x03\x06\x00\x02\x23\x01\x00\x01\x23\x00\x00', 
            'Top Right'    : b'\xBE\xEF\x03\x06\x00\x92\x22\x01\x00\x01\x23\x01\x00',
            'Bottom Left'  : b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x01\x23\x02\x00', 
            'Bottom Right' : b'\xBE\xEF\x03\x06\x00\xF2\x23\x01\x00\x01\x23\x03\x00'            
        }

        PinPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PinPPosition', PinPPositionCmdString, value, qualifier)

    def UpdatePinPPosition(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Top Left', 
            b'\x01' : 'Top Right',
            b'\x02' : 'Bottom Left', 
            b'\x03' : 'Bottom Right'            
        }

        PinPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PinPPosition', PinPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PinPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Position: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00'   
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off', 
            b'\x02' : 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier) 

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def UpdateVolumeLevelStatus(self, value, qualifier):

        InputStates = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN'           : b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\xC1\xEA\x02\x00\xD5\x20\x00\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
        }

        VolumeLevelStatusCmdString = InputStates[qualifier['Input']]
        res = self.__UpdateHelper('VolumeLevelStatus', VolumeLevelStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('VolumeLevelStatus', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Volume Level Status: Invalid/unexpected response'])

    def SetVolumeStep(self, value, qualifier):

        InputIncrementStates = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'LAN'           : b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\xA7\xEA\x04\x00\xD5\x20\x00\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
        }

        InputDecrementStates = {
            'Computer In 1' : b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'Computer In 2' : b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00',
            'LAN'           : b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'HDMI 1'        : b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2'        : b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'HDBaseT'       : b'\xBE\xEF\x03\x06\x00\x76\xEA\x05\x00\xD5\x20\x00\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
        }

        if value in ['Up', 'Down']:
            if value == 'Up':
                VolumeStepCmdString = InputIncrementStates[qualifier['Input']]
            if value == 'Down':
                VolumeStepCmdString = InputDecrementStates[qualifier['Input']]
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15'    : 'Invalid Command Reply.',
            b'\x1C'    : 'Cannot Execute Command.',
        }

        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.Setregex)
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.Updateregex)
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

