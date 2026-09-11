from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re
import hashlib
from binascii import hexlify

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
        self.Models = {
            'CP-WU5500': self.hit_1_1941_W0,
            'CP-WU5505': self.hit_1_1941_W5,
            'CP-X5555': self.hit_1_1941_X5,
            'CP-WX5500': self.hit_1_1941_W0,
            'CP-X5550': self.hit_1_1941_X0,
            'CP-WX5505': self.hit_1_1941_W5,
            'CP-WX5506M': self.hit_1_1941_W5,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaptionsChannel': {'Status': {}},
            'ClosedCaptionsDisplay': {'Status': {}},
            'ClosedCaptionsMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PbyPArea': {'Status': {}},
            'PbyPInput': {'Parameters': ['Area'], 'Status': {}},
            'PbyPPinP': {'Status': {}},
            'PbyPSize': {'Status': {}},
            'PbyPSwap': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PinPArea': {'Status': {}},
            'PinPInput': {'Parameters': ['Area'], 'Status': {}},
            'PinPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'VolumeLevelStatus': {'Parameters': ['Input'], 'Status': {}},
            'VolumeStep': {'Parameters': ['Input'], 'Status': {}},
        }


        if self.Unidirectional == 'False':
            self.Setregex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F\x04\x00|\x1D[\x00-\xFF]{2})')
            self.Updateregex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F\x04\x00|\x1D[\x00-\xFF]{2}|[a-f0-9]{8})')


    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetAspectRatioValues[value][0] + b'\x01\x00\x08\x20' + self.SetAspectRatioValues[value][1]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateAspectRatioValues[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\xD6\xD2', b'\x01\x00'],
            'Off': [b'\x46\xD3', b'\x00\x00']
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x20' + ValueStateValues[value][1]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6E\xF1', b'\x01\x00'],
            'Off': [b'\xFE\xF0', b'\x00\x00']
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\xA0\x20' + ValueStateValues[value][1]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xF0\x02\x00\xA0\x20\x00\x00'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/Unexpected Response'])

    def SetClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            '1': [b'\xD2\x62', b'\x01\x00'],
            '2': [b'\x22\x62', b'\x02\x00'],
            '3': [b'\xB2\x63', b'\x03\x00'],
            '4': [b'\x82\x61', b'\x04\x00']
        }

        ClosedCaptionsChannelCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)

    def UpdateClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            1: '1',
            2: '2',
            3: '3',
            4: '4'
        }

        ClosedCaptionsChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionsChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/Unexpected Response'])

    def SetClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\xFA\x62', b'\x00\x00'],
            'On': [b'\x6A\x63', b'\x01\x00'],
            'Auto': [b'\x9A\x63', b'\x02\x00']
        }

        ClosedCaptionsDisplayCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            1: 'On',
            2: 'Auto'
        }

        ClosedCaptionsDisplayCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionsDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Display: Invalid/Unexpected Response'])

    def SetClosedCaptionsMode(self, value, qualifier):

        ValueStateValues = {
            'Captions': [b'\x06\x63', b'\x00\x00'],
            'Text': [b'\x96\x62', b'\x01\x00']
        }

        ClosedCaptionsModeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x01\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaptionsMode', ClosedCaptionsModeCmdString, value, qualifier)

    def UpdateClosedCaptionsMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Captions',
            1: 'Text'
        }

        ClosedCaptionsModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsMode', ClosedCaptionsModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionsMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Captions Mode: Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Cover Error',
            2: 'Fan Error',
            3: 'Lamp Error',
            4: 'Temp Error',
            5: 'Air Flow Error',
            7: 'Cold Error',
            8: 'Filter Error',
            15: 'Shade Error',
            96: 'AC Blackout Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/Unexpected Response'])

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
            'On': [b'\x13\xD3', b'\x01\x00'],
            'Off': [b'\x83\xD2', b'\x00\x00']
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x30' + ValueStateValues[value][1]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetInputValues[value][0] + b'\x01\x00\x00\x20' + self.SetInputValues[value][1]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputValues[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': [b'\x3B\x23', b'\x00\x00'],
            'Eco': [b'\xAB\x22', b'\x01\x00']
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x33' + ValueStateValues[value][1]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Eco'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

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
            'Left': [b'\x7A\x26', b'\x00\x00'],
            'Right': [b'\xEA\x27', b'\x01\x00']
        }

        PbyPAreaCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x13\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPArea', PbyPAreaCmdString, value, qualifier)

    def UpdatePbyPArea(self, value, qualifier):

        ValueStateValues = {
            0: 'Left',
            1: 'Right'
        }

        PbyPAreaCmdString = b'\xBE\xEF\x03\x06\x00\x49\x26\x02\x00\x13\x23\x00\x00'
        res = self.__UpdateHelper('PbyPArea', PbyPAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PbyPArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Area: Invalid/Unexpected Response'])

    def SetPbyPInput(self, value, qualifier):

        AreaStates = {
            'Left': [0, b'\x15\x23'],
            'Right': [1, b'\x12\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PbyPInputCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetPIPInputValues[value]['PbyP'][area] + b'\x01\x00' + command + self.SetPIPInputValues[value]['Input']
        self.__SetHelper('PbyPInput', PbyPInputCmdString, value, qualifier)

    def UpdatePbyPInput(self, value, qualifier):

        AreaStates = {
            'Left': [b'\xC1\x26', b'\x15\x23'],
            'Right': [b'\xB5\x27', b'\x12\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PbyPInputCmdString = b'\xBE\xEF\x03\x06\x00' + area + b'\x02\x00' + command + b'\x00\x00'
        res = self.__UpdateHelper('PbyPInput', PbyPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdatePIPInputValues[res[1]]
                self.WriteStatus('PbyPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Input: Invalid/Unexpected Response'])

    def SetPbyPPinP(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\x3E\x26', b'\x00\x00'],
            'PbyP': [b'\xAE\x27', b'\x01\x00'],
            'PinP': [b'\x5E\x27', b'\x02\x00']
        }

        PbyPPinPCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x10\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPPinP', PbyPPinPCmdString, value, qualifier)

    def UpdatePbyPPinP(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            1: 'PbyP',
            2: 'PinP'
        }

        PbyPPinPCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyPPinP', PbyPPinPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PbyPPinP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyPPinP: Invalid/Unexpected Response'])

    def SetPbyPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': [b'\xF2\x07', b'\x7F\x00'],
            'Middle': [b'\x02\x46', b'\x80\x00'],
            'Large': [b'\x92\x47', b'\x81\x00']
        }

        PbyPSizeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x11\x23' + ValueStateValues[value][1]
        self.__SetHelper('PbyPSize', PbyPSizeCmdString, value, qualifier)

    def UpdatePbyPSize(self, value, qualifier):

        ValueStateValues = {
            127: 'Small',
            128: 'Middle',
            129: 'Large'
        }

        PbyPSizeCmdString = b'\xBE\xEF\x03\x06\x00\xF1\x27\x02\x00\x11\x23\x00\x00'
        res = self.__UpdateHelper('PbyPSize', PbyPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PbyPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Size: Invalid/Unexpected Response'])

    def SetPbyPSwap(self, value, qualifier):

        PbyPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPSwap', PbyPSwapCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard' 		: [b'\x83\xF5', b'\x06\x00'],
            'Natural' 		: [b'\x23\xF6', b'\x00\x00'],
            'Cinema' 		: [b'\xB3\xF7', b'\x01\x00'],
            'Dynamic' 		: [b'\xE3\xF4', b'\x04\x00'],
            'Board (Black)': [b'\xE3\xEF', b'\x20\x00'],
            'Board (Green)': [b'\x73\xEE', b'\x21\x00'],
            'Whiteboard' 	: [b'\x83\xEE', b'\x22\x00'],
            'Daytime' 		: [b'\xE3\xC7', b'\x40\x00'],
            'Dicom Sim' 	: [b'\x73\xC6', b'\x41\x00'],
            'User 1' 		: [b'\xE3\xFB', b'\x10\x00'],
            'User 2' 		: [b'\x73\xFA', b'\x11\x00'],
            'User 3' 		: [b'\x83\xFA', b'\x12\x00']
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\xBA\x30' + ValueStateValues[value][1]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            6: 'Standard',
            0: 'Natural',
            1: 'Cinema',
            4: 'Dynamic',
            32: 'Board (Black)',
            33: 'Board (Green)',
            34: 'Whiteboard',
            64: 'Daytime',
            65: 'Dicom Sim',
            16: 'User 1',
            17: 'User 2',
            18: 'User 3'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/Unexpected Response'])

    def SetPinPArea(self, value, qualifier):

        ValueStateValues = {
            'Primary' 	: [b'\x32\x22', b'\x00\x00'],
            'Secondary': [b'\xA2\x23', b'\x01\x00']
        }

        PinPAreaCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x05\x23' + ValueStateValues[value][1]
        self.__SetHelper('PinPArea', PinPAreaCmdString, value, qualifier)

    def UpdatePinPArea(self, value, qualifier):

        ValueStateValues = {
            0: 'Primary',
            1: 'Secondary'
        }

        PinPAreaCmdString = b'\xBE\xEF\x03\x06\x00\x01\x22\x02\x00\x05\x23\x00\x00'
        res = self.__UpdateHelper('PinPArea', PinPAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PinPArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Area: Invalid/Unexpected Response'])

    def SetPinPInput(self, value, qualifier):

        AreaStates = {
            'Primary': [0, b'\x04\x23'],
            'Secondary': [1, b'\x02\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PinPInputCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetPIPInputValues[value]['PinP'][area] + b'\x01\x00' + command + self.SetPIPInputValues[value]['Input']
        self.__SetHelper('PinPInput', PinPInputCmdString, value, qualifier)

    def UpdatePinPInput(self, value, qualifier):

        AreaStates = {
            'Primary': [b'\xFD\x23', b'\x04\x23'],
            'Secondary': [b'\x75\x23', b'\x02\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PinPInputCmdString = b'\xBE\xEF\x03\x06\x00' + area + b'\x02\x00' + command + b'\x00\x00'
        res = self.__UpdateHelper('PinPInput', PinPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdatePIPInputValues[res[1]]
                self.WriteStatus('PinPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Input: Invalid/Unexpected Response'])

    def SetPinPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': [b'\x02\x23', b'\x00\x00'],
            'Top Right': [b'\x92\x22', b'\x01\x00'],
            'Bottom Left': [b'\x62\x22', b'\x02\x00'],
            'Bottom Right': [b'\xF2\x23', b'\x03\x00']
        }

        PinPPositionCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x01\x23' + ValueStateValues[value][1]
        self.__SetHelper('PinPPosition', PinPPositionCmdString, value, qualifier)

    def UpdatePinPPosition(self, value, qualifier):

        ValueStateValues = {
            0: 'Top Left',
            1: 'Top Right',
            2: 'Bottom Left',
            3: 'Bottom Right'
        }

        PinPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PinPPosition', PinPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PinPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Position: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\xBA\xD2', b'\x01\x00'],
            'Off': [b'\x2A\xD3', b'\x00\x00']
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x60' + ValueStateValues[value][1]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            2: 'Cool Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Recall': [b'\x14\x20', b'\x0E\xD7', b'\x9E\xD6', b'\x6E\xD6', b'\xFE\xD7'],
            'Save': [b'\x15\x20', b'\xF2\xD6', b'\x62\xD7', b'\x92\xD7', b'\x02\xD6']
        }

        ValueStateValues = {
            '1': b'\x00\x00',
            '2': b'\x01\x00',
            '3': b'\x02\x00',
            '4': b'\x03\x00'
        }

        action = qualifier['Action']

        PresetCmdString = b'\xBE\xEF\x03\x06\x00' + ActionStates[action][int(value)] + b'\x01\x00' + ActionStates[action][0] + ValueStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6B\xD9', b'\x01\x00'],
            'Off': [b'\xFB\xD8', b'\x00\x00']
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x20\x30' + ValueStateValues[value][1]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def UpdateVolumeLevelStatus(self, value, qualifier):

        input = qualifier['Input']
        VolumeLevelStatusCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetVolumeValues[input][1] + b'\x02\x00' + self.SetVolumeValues[input][0] + b'\x00\x00'
        res = self.__UpdateHelper('VolumeLevelStatus', VolumeLevelStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[1]
                self.WriteStatus('VolumeLevelStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Volume Level Status: Invalid/Unexpected Response'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': [2, b'\x04\x00'],
            'Down': [3, b'\x05\x00']
        }

        input = qualifier['Input']

        VolumeStepCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetVolumeValues[input][ValueStateValues[value][0]] + ValueStateValues[value][1] + self.SetVolumeValues[input][0] + b'\x00\x00'
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Invalid Command Reply.',
            b'\x1C': 'Cannot Execute Command.',
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Setregex)
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Updateregex)
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

    def hit_1_1941_W0(self):

        self.SetAspectRatioValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Native': [b'\x5E\xD7', b'\x08\x00'],
            'Zoom': [b'\x9E\xC4', b'\x30\x00']
        }

        self.UpdateAspectRatioValues = {
            16: 'Normal',
            0: '4:3',
            1: '16:9',
            10: '16:10',
            9: '14:9',
            8: 'Native',
            48: 'Zoom'
        }

        self.SetInputValues = {
            'Computer In': [b'\xFE\xD2', b'\x00\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.UpdateInputValues = {
            0: 'Computer In',
            11: 'LAN',
            3: 'HDMI 1',
            13: 'HDMI 2',
            1: 'Video'
        }

        self.SetPIPInputValues = {
            'Computer In': {
                'PbyP': [b'\xF2\x26', b'\x86\x27'],
                'PinP': [b'\xCE\x23', b'\x46\x23'],
                'Input': b'\x00\x00'
            },

            'HDMI 1': {
                'PbyP': [b'\x02\x26', b'\x76\x27'],
                'PinP': [b'\x3E\x23', b'\xB6\x23'],
                'Input': b'\x03\x00'
            },

            'HDMI 2': {
                'PbyP': [b'\x62\x22', b'\x16\x23'],
                'PinP': [b'\x5E\x27', b'\xD6\x27'],
                'Input': b'\x0D\x00'
            },

            'Video': {
                'PbyP': [b'\x62\x27', b'\x16\x26'],
                'PinP': [b'\x5E\x22', b'\xD6\x22'],
                'Input': b'\x01\x00'
            }
        }

        self.UpdatePIPInputValues = {
            0: 'Computer In',
            3: 'HDMI 1',
            13: 'HDMI 2',
            1: 'Video'
        }

        self.SetVolumeValues = {
            'Computer In': [b'\x60\x20', b'\xCD\xCC', b'\xAB\xCC', b'\x7A\xCD'],
            'LAN': [b'\x6B\x20', b'\xE9\xCE', b'\x8F\xCE', b'\x5E\xCF'],
            'HDMI 1': [b'\x63\x20', b'\x89\xCC', b'\xEF\xCC', b'\x3E\xCD'],
            'HDMI 2': [b'\x6D\x20', b'\x61\xCE', b'\x07\xCE', b'\xD6\xCF'],
            'Video': [b'\x61\x20', b'\x31\xCD', b'\x57\xCD', b'\x86\xCC'],
            'All': [b'\x50\x20', b'\xCD\xC3', b'\xAB\xC3', b'\x7A\xC2']
        }

    def hit_1_1941_W5(self):

        self.SetAspectRatioValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Native': [b'\x5E\xD7', b'\x08\x00'],
            'Zoom': [b'\x9E\xC4', b'\x30\x00']
        }

        self.UpdateAspectRatioValues = {
            16: 'Normal',
            0: '4:3',
            1: '16:9',
            10: '16:10',
            9: '14:9',
            8: 'Native',
            48: 'Zoom'
        }

        self.SetInputValues = {
            'Computer In': [b'\xFE\xD2', b'\x00\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'HDBaseT': [b'\xAE\xDE', b'\x11\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.UpdateInputValues = {
            0: 'Computer In',
            11: 'LAN',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            1: 'Video'
        }

        self.SetPIPInputValues = {
            'Computer In': {
                'PbyP': [b'\xF2\x26', b'\x86\x27'],
                'PinP': [b'\xCE\x23', b'\x46\x23'],
                'Input': b'\x00\x00'
            },

            'HDMI 1': {
                'PbyP': [b'\x02\x26', b'\x76\x27'],
                'PinP': [b'\x3E\x23', b'\xB6\x23'],
                'Input': b'\x03\x00'
            },

            'HDMI 2': {
                'PbyP': [b'\x62\x22', b'\x16\x23'],
                'PinP': [b'\x5E\x27', b'\xD6\x27'],
                'Input': b'\x0D\x00'
            },

            'HDBaseT': {
                'PbyP': [b'\xA2\x2A', b'\xD6\x2B'],
                'PinP': [b'\x9E\x2F', b'\x16\x2F'],
                'Input': b'\x11\x00'
            },

            'Video': {
                'PbyP': [b'\x62\x27', b'\x16\x26'],
                'PinP': [b'\x5E\x22', b'\xD6\x22'],
                'Input': b'\x01\x00'
            }
        }

        self.UpdatePIPInputValues = {
            0: 'Computer In',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            1: 'Video'
        }

        self.SetVolumeValues = {
            'Computer In': [b'\x60\x20', b'\xCD\xCC', b'\xAB\xCC', b'\x7A\xCD'],
            'LAN': [b'\x6B\x20', b'\xE9\xCE', b'\x8F\xCE', b'\x5E\xCF'],
            'HDMI 1': [b'\x63\x20', b'\x89\xCC', b'\xEF\xCC', b'\x3E\xCD'],
            'HDMI 2': [b'\x6D\x20', b'\x61\xCE', b'\x07\xCE', b'\xD6\xCF'],
            'HDBaseT': [b'\xD5\x20', b'\xC1\xEA', b'\xA7\xEA', b'\x76\xEB'],
            'Video': [b'\x61\x20', b'\x31\xCD', b'\x57\xCD', b'\x86\xCC'],
            'All': [b'\x50\x20', b'\xCD\xC3', b'\xAB\xC3', b'\x7A\xC2']
        }

    def hit_1_1941_X0(self):

        self.SetAspectRatioValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Zoom': [b'\x9E\xC4', b'\x30\x00']
        }

        self.UpdateAspectRatioValues = {
            16: 'Normal',
            0: '4:3',
            1: '16:9',
            10: '16:10',
            9: '14:9',
            48: 'Zoom'
        }

        self.SetInputValues = {
            'Computer In': [b'\xFE\xD2', b'\x00\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.UpdateInputValues = {
            0: 'Computer In',
            11: 'LAN',
            3: 'HDMI 1',
            13: 'HDMI 2',
            1: 'Video'
        }

        self.SetPIPInputValues = {
            'Computer In': {
                'PbyP': [b'\xF2\x26', b'\x86\x27'],
                'PinP': [b'\xCE\x23', b'\x46\x23'],
                'Input': b'\x00\x00'
            },

            'HDMI 1': {
                'PbyP': [b'\x02\x26', b'\x76\x27'],
                'PinP': [b'\x3E\x23', b'\xB6\x23'],
                'Input': b'\x03\x00'
            },

            'HDMI 2': {
                'PbyP': [b'\x62\x22', b'\x16\x23'],
                'PinP': [b'\x5E\x27', b'\xD6\x27'],
                'Input': b'\x0D\x00'
            },

            'Video': {
                'PbyP': [b'\x62\x27', b'\x16\x26'],
                'PinP': [b'\x5E\x22', b'\xD6\x22'],
                'Input': b'\x01\x00'
            }
        }

        self.UpdatePIPInputValues = {
            0: 'Computer In',
            3: 'HDMI 1',
            13: 'HDMI 2',
            1: 'Video'
        }

        self.SetVolumeValues = {
            'Computer In': [b'\x60\x20', b'\xCD\xCC', b'\xAB\xCC', b'\x7A\xCD'],
            'LAN': [b'\x6B\x20', b'\xE9\xCE', b'\x8F\xCE', b'\x5E\xCF'],
            'HDMI 1': [b'\x63\x20', b'\x89\xCC', b'\xEF\xCC', b'\x3E\xCD'],
            'HDMI 2': [b'\x6D\x20', b'\x61\xCE', b'\x07\xCE', b'\xD6\xCF'],
            'Video': [b'\x61\x20', b'\x31\xCD', b'\x57\xCD', b'\x86\xCC'],
            'All': [b'\x50\x20', b'\xCD\xC3', b'\xAB\xC3', b'\x7A\xC2']
        }

    def hit_1_1941_X5(self):

        self.SetAspectRatioValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Zoom': [b'\x9E\xC4', b'\x30\x00']
        }

        self.UpdateAspectRatioValues = {
            16: 'Normal',
            0: '4:3',
            1: '16:9',
            10: '16:10',
            9: '14:9',
            48: 'Zoom'
        }

        self.SetInputValues = {
            'Computer In': [b'\xFE\xD2', b'\x00\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'HDBaseT': [b'\xAE\xDE', b'\x11\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.UpdateInputValues = {
            0: 'Computer In',
            11: 'LAN',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            1: 'Video'
        }

        self.SetPIPInputValues = {
            'Computer In': {
                'PbyP': [b'\xF2\x26', b'\x86\x27'],
                'PinP': [b'\xCE\x23', b'\x46\x23'],
                'Input': b'\x00\x00'
            },
            'HDMI 1': {
                'PbyP': [b'\x02\x26', b'\x76\x27'],
                'PinP': [b'\x3E\x23', b'\xB6\x23'],
                'Input': b'\x03\x00'
            },
            'HDMI 2': {
                'PbyP': [b'\x62\x22', b'\x16\x23'],
                'PinP': [b'\x5E\x27', b'\xD6\x27'],
                'Input': b'\x0D\x00'
            },
            'HDBaseT': {
                'PbyP': [b'\xA2\x2A', b'\xD6\x2B'],
                'PinP': [b'\x9E\x2F', b'\x16\x2F'],
                'Input': b'\x11\x00'
            },
            'Video': {
                'PbyP': [b'\x62\x27', b'\x16\x26'],
                'PinP': [b'\x5E\x22', b'\xD6\x22'],
                'Input': b'\x01\x00'
            }
        }

        self.UpdatePIPInputValues = {
            0: 'Computer In',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            1: 'Video'
        }

        self.SetVolumeValues = {
            'Computer In': [b'\x60\x20', b'\xCD\xCC', b'\xAB\xCC', b'\x7A\xCD'],
            'LAN': [b'\x6B\x20', b'\xE9\xCE', b'\x8F\xCE', b'\x5E\xCF'],
            'HDMI 1': [b'\x63\x20', b'\x89\xCC', b'\xEF\xCC', b'\x3E\xCD'],
            'HDMI 2': [b'\x6D\x20', b'\x61\xCE', b'\x07\xCE', b'\xD6\xCF'],
            'HDBaseT': [b'\xD5\x20', b'\xC1\xEA', b'\xA7\xEA', b'\x76\xEB'],
            'Video': [b'\x61\x20', b'\x31\xCD', b'\x57\xCD', b'\x86\xCC'],
            'All': [b'\x50\x20', b'\xCD\xC3', b'\xAB\xC3', b'\x7A\xC2']
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
