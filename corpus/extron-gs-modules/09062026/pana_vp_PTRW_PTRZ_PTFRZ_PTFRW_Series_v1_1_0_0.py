from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re
import hashlib
from binascii import hexlify

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
        self.Models = {}
        self._DeviceID = '01'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DInputFormat': {'Status': {}},
            '3DMessage': {'Status': {}},
            '3DMode': {'Status': {}},
            '3DSyncLeftRightSwap': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DLPLinkLeftRightSwap': {'Status': {}},
            'EdgeBlending': {'Status': {}},
            'EdgeBlendingLeft': {'Status': {}},
            'EdgeBlendingLower': {'Status': {}},
            'EdgeBlendingRight': {'Status': {}},
            'EdgeBlendingUpper': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SyncOutputDelay': {'Status': {}},
            'Volume': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ZZ'
        elif 1 <= int(value) <= 64:
            self._DeviceID = value.zfill(2)
        else:
            print('DeviceID is set to an invalid value. Range is from 1 to 64 or Broadcast')

    def Set3DInputFormat(self, value, qualifier):

        InputFormatStateValues = {
            'Auto': '00000',
            'Native': '00001',
            'Side by Side': '00003',
            'Top and Bottom': '00004',
            'Frame Sequential': '00006'
            }

        InputFormatString = 'AD{0};VXX:DIFI1=+{1}'.format(self._DeviceID, InputFormatStateValues[value])
        InputFormatCmdString = b''.join([pack('>B', 0x02), InputFormatString.encode(), pack('>B', 0x03)])

        self.__SetHelper('3DInputFormat', InputFormatCmdString.decode(), value, qualifier)

    def Update3DInputFormat(self, value, qualifier):

        InputFormatStateNames = {
            '0': 'Auto',
            '1': 'Native',
            '3': 'Side by Side',
            '4': 'Top and Bottom',
            '6': 'Frame Sequential'
            }

        InputFormatString = 'AD{0};QVX:DIFI1'.format(self._DeviceID)
        InputFormatCmdString = b''.join([pack('>B', 0x02), InputFormatString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('3DInputFormat', InputFormatCmdString.decode(), value, qualifier)
        if res:
            try:
                value = InputFormatStateNames[res[12]]
                self.WriteStatus('3DInputFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Input Format: Invalid/unexpected response'])

    def Set3DMessage(self, value, qualifier):

        MessageStateValues = {
            'Off': '00000',
            'On': '00001'
            }

        MessageString = 'AD{0};VXX:DMGI1=+{1}'.format(self._DeviceID, MessageStateValues[value])
        MessageCmdString = b''.join([pack('>B', 0x02), MessageString.encode(), pack('>B', 0x03)])

        self.__SetHelper('3DMessage', MessageCmdString.decode(), value, qualifier)

    def Update3DMessage(self, value, qualifier):

        MessageStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        MessageString = 'AD{0};QVX:DMGI1'.format(self._DeviceID)
        MessageCmdString = b''.join([pack('>B', 0x02), MessageString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('3DMessage', MessageCmdString.decode(), value, qualifier)
        if res:
            try:
                value = MessageStateNames[res[12]]
                self.WriteStatus('3DMessage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Message: Invalid/unexpected response'])

    def Set3DMode(self, value, qualifier):

        ModeStateValues = {
            'Off': '00000',
            'All On': '00001',
            '3D Sync': '00010',
            'DLP Link': '00011'
            }

        ModeString = 'AD{0};VXX:DMDI1=+{1}'.format(self._DeviceID, ModeStateValues[value])
        ModeCmdString = b''.join([pack('>B', 0x02), ModeString.encode(), pack('>B', 0x03)])

        self.__SetHelper('3DMode', ModeCmdString.decode(), value, qualifier)

    def Update3DMode(self, value, qualifier):

        ModeStateNames = {
            '00': 'Off',
            '01': 'All On',
            '10': '3D Sync',
            '11': 'DLP Link'
            }

        ModeString = 'AD{0};QVX:DMDI1'.format(self._DeviceID)
        ModeCmdString = b''.join([pack('>B', 0x02), ModeString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('3DMode', ModeCmdString.decode(), value, qualifier)
        if res:
            try:
                value = ModeStateNames[res[11:13]]
                self.WriteStatus('3DMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Mode: Invalid/unexpected response'])

    def Set3DSyncLeftRightSwap(self, value, qualifier):

        SyncSwapStateValues = {
            'Normal': '00000',
            'Swap': '00001'
            }

        SyncSwapString = 'AD{0};VXX:DSWI1=+{1}'.format(self._DeviceID, SyncSwapStateValues[value])
        SyncSwapCmdString = b''.join([pack('>B', 0x02), SyncSwapString.encode(), pack('>B', 0x03)])

        self.__SetHelper('3DSyncLeftRightSwap', SyncSwapCmdString.decode(), value, qualifier)

    def Update3DSyncLeftRightSwap(self, value, qualifier):

        SyncSwapStateNames = {
            '0': 'Normal',
            '1': 'Swap'
        }

        SyncSwapString = 'AD{0};QVX:DSWI1'.format(self._DeviceID)
        SyncSwapCmdString = b''.join([pack('>B', 0x02), SyncSwapString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('3DSyncLeftRightSwap', SyncSwapCmdString.decode(), value, qualifier)
        if res:
            try:
                value = SyncSwapStateNames[res[12]]
                self.WriteStatus('3DSyncLeftRightSwap', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Sync Left Right Swap: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Normal': '0',
            '4:3': '1',
            'Wide': '2',
            'Native': '5',
            'Full': '6',
            'H Fit': '9',
            'V Fit': '10'
            }

        AspectRatioString = 'AD{0};VSE:{1}'.format(self._DeviceID, AspectRatioStateValues[value])
        AspectRatioCmdString = b''.join([pack('>B', 0x02), AspectRatioString.encode(), pack('>B', 0x03)])

        self.__SetHelper('AspectRatio', AspectRatioCmdString.decode(), value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            '0': 'Normal',
            '1': '4:3',
            '2': 'Wide',
            '5': 'Native',
            '6': 'Full',
            '9': 'H Fit',
            '10': 'V Fit'
            }

        AspectRatioString = 'AD{0};QSE'.format(self._DeviceID)
        AspectRatioCmdString = b''.join([pack('>B', 0x02), AspectRatioString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString.decode(), value, qualifier)
        if res:
            try:
                if len(res) == 3:
                    value = AspectRatioStateNames[res[1]]
                else:
                    value = AspectRatioStateNames[res[1:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'Off': '0',
            'On': '1'
            }

        AVMuteString = 'AD{0};OSH:{1}'.format(self._DeviceID, AVMuteStateValues[value])
        AVMuteCmdString = b''.join([pack('>B', 0x02), AVMuteString.encode(), pack('>B', 0x03)])
        self.__SetHelper('AVMute', AVMuteCmdString.decode(), value, qualifier)

    def UpdateAVMute(self, value, qualifier):
        AVMuteStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        AVMuteString = 'AD{0};QSH'.format(self._DeviceID)
        AVMuteCmdString = b''.join([pack('>B', 0x02), AVMuteString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('AVMute', AVMuteCmdString.decode(), value, qualifier)
        if res:
            try:
                value = AVMuteStateNames[res[1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
            }

        ClosedCaptionString = 'AD{0};OCC:{1}'.format(self._DeviceID, ClosedCaptionStateValues[value])
        ClosedCaptionCmdString = b''.join([pack('>B', 0x02), ClosedCaptionString.encode(), pack('>B', 0x03)])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString.decode(), value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        ClosedCaptionStateNames = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            '0': 'Off'
            }

        ClosedCaptionString = 'AD{0};QCC'.format(self._DeviceID)
        ClosedCaptionCmdString = b''.join([pack('>B', 0x02), ClosedCaptionString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString.decode(), value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetDLPLinkLeftRightSwap(self, value, qualifier):

        DLPLinkSwapStateValues = {
            'Normal': '00000',
            'Swap': '00001'
            }

        DLPLinkSwapString = 'AD{0};VXX:DSWI2=+{1}'.format(self._DeviceID, DLPLinkSwapStateValues[value])
        DLPLinkSwapCmdString = b''.join([pack('>B', 0x02), DLPLinkSwapString.encode(), pack('>B', 0x03)])

        self.__SetHelper('DLPLinkLeftRightSwap', DLPLinkSwapCmdString.decode(), value, qualifier)

    def UpdateDLPLinkLeftRightSwap(self, value, qualifier):

        DLPLinkSwapStateNames = {
            '0': 'Normal',
            '1': 'Swap'
            }

        DLPLinkSwapString = 'AD{0};QVX:DSWI2'.format(self._DeviceID)
        DLPLinkSwapCmdString = b''.join([pack('>B', 0x02), DLPLinkSwapString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('DLPLinkLeftRightSwap', DLPLinkSwapCmdString.decode(), value, qualifier)
        if res:
            try:
                value = DLPLinkSwapStateNames[res[12]]
                self.WriteStatus('DLPLinkLeftRightSwap', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DLP Link LeftRight Swap: Invalid/unexpected response'])

    def SetEdgeBlending(self, value, qualifier):

        EdgeBlendingStateValues = {
            'Off': '00000',
            'On': '00001'
            }

        EdgeBlendingString = 'AD{0};VXX:EDBI0=+{1}'.format(self._DeviceID, EdgeBlendingStateValues[value])
        EdgeBlendingCmdString = b''.join([pack('>B', 0x02), EdgeBlendingString.encode(), pack('>B', 0x03)])
        self.__SetHelper('EdgeBlending', EdgeBlendingCmdString.decode(), value, qualifier)

    def UpdateEdgeBlending(self, value, qualifier):

        EdgeBlendingStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        EdgeBlendingString = 'AD{0};QVX:EDBI0'.format(self._DeviceID)
        EdgeBlendingCmdString = b''.join([pack('>B', 0x02), EdgeBlendingString.encode(), pack('>B', 0x03)])

        res = self.__UpdateHelper('EdgeBlending', EdgeBlendingCmdString.decode(), value, qualifier)
        if res:
            try:
                value = EdgeBlendingStateNames[res[12]]
                self.WriteStatus('EdgeBlending', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Edge Blending: Invalid/unexpected response'])

    def SetEdgeBlendingLeft(self, value, qualifier):

        EdgeBlendingLeftStateValues = {
            'Off': '0',
            'On': '1'
            }

        EdgeBlendingLeftString = 'AD{0};VGL:{1}'.format(self._DeviceID, EdgeBlendingLeftStateValues[value])
        EdgeBlendingLeftCmdString = b''.join([pack('>B', 0x02), EdgeBlendingLeftString.encode(), pack('>B', 0x03)])
        self.__SetHelper('EdgeBlendingLeft', EdgeBlendingLeftCmdString.decode(), value, qualifier)

    def UpdateEdgeBlendingLeft(self, value, qualifier):
        EdgeBlendingLeftStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        EdgeBlendingLeftString = 'AD{0};QGL'.format(self._DeviceID)
        EdgeBlendingLeftCmdString = b''.join([pack('>B', 0x02), EdgeBlendingLeftString.encode(), pack('>B', 0x03)])

        res = self.__UpdateHelper('EdgeBlendingLeft', EdgeBlendingLeftCmdString.decode(), value, qualifier)
        if res:
            try:
                value = EdgeBlendingLeftStateNames[res[1]]
                self.WriteStatus('EdgeBlendingLeft', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Edge Blending Left: Invalid/unexpected response'])

    def SetEdgeBlendingLower(self, value, qualifier):

        EdgeBlendingLowerStateValues = {
            'Off': '0',
            'On': '1'
            }

        EdgeBlendingLowerString = 'AD{0};VGB:{1}'.format(self._DeviceID, EdgeBlendingLowerStateValues[value])
        EdgeBlendingLowerCmdString = b''.join([pack('>B', 0x02), EdgeBlendingLowerString.encode(), pack('>B', 0x03)])
        self.__SetHelper('EdgeBlendingLower', EdgeBlendingLowerCmdString.decode(), value, qualifier)

    def UpdateEdgeBlendingLower(self, value, qualifier):
        EdgeBlendingLowerStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        EdgeBlendingLowerString = 'AD{0};QGB'.format(self._DeviceID)
        EdgeBlendingLowerCmdString = b''.join([pack('>B', 0x02), EdgeBlendingLowerString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('EdgeBlendingLower', EdgeBlendingLowerCmdString.decode(), value, qualifier)
        if res:
            try:
                value = EdgeBlendingLowerStateNames[res[1]]
                self.WriteStatus('EdgeBlendingLower', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Edge Blending Lower: Invalid/unexpected response'])

    def SetEdgeBlendingRight(self, value, qualifier):

        EdgeBlendingRightStateValues = {
            'Off': '0',
            'On': '1'
            }

        EdgeBlendingRightString = 'AD{0};VGR:{1}'.format(self._DeviceID, EdgeBlendingRightStateValues[value])
        EdgeBlendingRightCmdString = b''.join([pack('>B', 0x02), EdgeBlendingRightString.encode(), pack('>B', 0x03)])
        self.__SetHelper('EdgeBlendingRight', EdgeBlendingRightCmdString.decode(), value, qualifier)

    def UpdateEdgeBlendingRight(self, value, qualifier):
        EdgeBlendingRightStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        EdgeBlendingRightString = 'AD{0};QGR'.format(self._DeviceID)
        EdgeBlendingRightCmdString = b''.join([pack('>B', 0x02), EdgeBlendingRightString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('EdgeBlendingRight', EdgeBlendingRightCmdString.decode(), value, qualifier)
        if res:
            try:
                value = EdgeBlendingRightStateNames[res[1]]
                self.WriteStatus('EdgeBlendingRight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Edge Blending Right: Invalid/unexpected response'])

    def SetEdgeBlendingUpper(self, value, qualifier):

        EdgeBlendingUpperStateValues = {
            'Off': '0',
            'On': '1'
            }

        EdgeBlendingUpperString = 'AD{0};VGU:{1}'.format(self._DeviceID, EdgeBlendingUpperStateValues[value])
        EdgeBlendingUpperCmdString = b''.join([pack('>B', 0x02), EdgeBlendingUpperString.encode(), pack('>B', 0x03)])
        self.__SetHelper('EdgeBlendingUpper', EdgeBlendingUpperCmdString.decode(), value, qualifier)

    def UpdateEdgeBlendingUpper(self, value, qualifier):
        EdgeBlendingUpperStateNames = {
            '0': 'Off',
            '1': 'On'
            }

        EdgeBlendingUpperString = 'AD{0};QGU'.format(self._DeviceID)
        EdgeBlendingUpperCmdString = b''.join([pack('>B', 0x02), EdgeBlendingUpperString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('EdgeBlendingUpper', EdgeBlendingUpperCmdString.decode(), value, qualifier)
        if res:
            try:
                value = EdgeBlendingUpperStateNames[res[1]]
                self.WriteStatus('EdgeBlendingUpper', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Edge Blending Upper: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1',
            'Off': '0',
            }

        FreezeString = 'AD{0};OFZ:{1}'.format(self._DeviceID, FreezeStateValues[value])
        FreezeCmdString = b''.join([pack('>B', 0x02), FreezeString.encode(), pack('>B', 0x03)])
        self.__SetHelper('Freeze', FreezeCmdString.decode(), value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        FreezeStateNames = {
            '1': 'On',
            '0': 'Off'
            }

        FreezeString = 'AD{0};QFZ'.format(self._DeviceID)
        FreezeCmdString = b''.join([pack('>B', 0x02), FreezeString.encode(), pack('>B', 0x03)])

        res = self.__UpdateHelper('Freeze', FreezeCmdString.decode(), value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Computer': 'RG1',
            'Video': 'VID',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Digital Link': 'DL1',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link S-Video': 'DL1:SVD'
            }

        InputString = 'AD{0};IIS:{1}'.format(self._DeviceID, InputStateValues[value])
        InputCmdString = b''.join([pack('>B', 0x02), InputString.encode(), pack('>B', 0x03)])
        self.__SetHelper('Input', InputCmdString.decode(), value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputStateNames = {
            'RG1': 'Computer',
            'VID': 'Video',
            'DVI': 'DVI',
            'HD1': 'HDMI',
            'DL1': 'Digital Link',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:SVD': 'Digital Link S-Video'
            }

        InputString = 'AD{0};QIN'.format(self._DeviceID)
        InputCmdString = b''.join([pack('>B', 0x02), InputString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('Input', InputCmdString.decode(), value, qualifier)
        if res:
            try:
                if len(res) <= 5:
                    value = InputStateNames[res[1:4]]
                else:
                    value = InputStateNames[res[1:8]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal': '0',
            'Low': '1',
            'ECO Save 1': '6',
            'ECO Save 2': '7'
            }

        LampModeString = 'AD{0};OLP:{1}'.format(self._DeviceID, LampModeStateValues[value])
        LampModeCmdString = b''.join([pack('>B', 0x02), LampModeString.encode(), pack('>B', 0x03)])
        self.__SetHelper('LampMode', LampModeCmdString.decode(), value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeStateNames = {
            '0': 'Normal',
            '1': 'Low',
            '6': 'ECO Save 1',
            '7': 'ECO Save 2',
            }

        LampModeString = 'AD{0};QLP'.format(self._DeviceID)
        LampModeCmdString = b''.join([pack('>B', 0x02), LampModeString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('LampMode', LampModeCmdString.decode(), value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageString = 'AD{0};QST'.format(self._DeviceID)
        LampUsageCmdString = b''.join([pack('>B', 0x02), LampUsageString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString.decode(), value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': 'OMN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
            'Enter': 'OEN',
            'Return': 'OBK'
            }

        MenuNavigationString = 'AD{0};{1}'.format(self._DeviceID, MenuNavigationStateValues[value])
        MenuNavigationCmdString = b''.join([pack('>B', 0x02), MenuNavigationString.encode(), pack('>B', 0x03)])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString.decode(), value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On': '1',
            'Off': '0',
            }

        OnScreenDisplayString = 'AD{0};OOS:{1}'.format(self._DeviceID, OnScreenDisplayStateValues[value])
        OnScreenDisplayCmdString = b''.join([pack('>B', 0x02), OnScreenDisplayString.encode(), pack('>B', 0x03)])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString.decode(), value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayStateNames = {
            '1': 'On',
            '0': 'Off'
            }

        OnScreenDisplayString = 'AD{0};QOS'.format(self._DeviceID)
        OnScreenDisplayCmdString = b''.join([pack('>B', 0x02), OnScreenDisplayString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString.decode(), value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateNames[res[1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural': 'NAT',
            'Standard': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM': 'DIC',
            'Rec. 709': '709'
            }

        PictureModeString = 'AD{0};VPM:{1}'.format(self._DeviceID, PictureModeStateValues[value])
        PictureModeCmdString = b''.join([pack('>B', 0x02), PictureModeString.encode(), pack('>B', 0x03)])
        self.__SetHelper('PictureMode', PictureModeCmdString.decode(), value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        PictureModeStateNames = {
            'NAT': 'Natural',
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM',
            '709': 'Rec. 709'
            }

        PictureModeString = 'AD{0};QPM'.format(self._DeviceID)
        PictureModeCmdString = b''.join([pack('>B', 0x02), PictureModeString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString.decode(), value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:4]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': 'PON',
            'Off': 'POF'
            }
        PowerString = 'AD{0};{1}'.format(self._DeviceID, PowerStateValues[value])
        PowerCmdString = b''.join([pack('>B', 0x02), PowerString.encode(), pack('>B', 0x03)])

        self.__SetHelper('Power', PowerCmdString.decode(), value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down'
            }

        PowerString = 'AD{0};Q$S'.format(self._DeviceID)
        PowerCmdString = b''.join([pack('>B', 0x02), PowerString.encode(), pack('>B', 0x03)])

        res = self.__UpdateHelper('Power', PowerCmdString.decode(), value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSyncOutputDelay(self, value, qualifier):

        DelayConstraints = {
            'Min': 0,
            'Max': 25000
            }

        value = int(value)
        if DelayConstraints['Min'] <= value <= DelayConstraints['Max']:
            SyncOutputDelayString = 'AD{0};VXX:DSNI2=+{:05d}'.format(self._DeviceID, value)
            SyncOutputDelayCmdString = b''.join([pack('>B', 0x02), SyncOutputDelayString.encode(), pack('>B', 0x03)])
            self.__SetHelper('SyncOutputDelay', SyncOutputDelayCmdString.decode(), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSyncOutputDelay')

    def UpdateSyncOutputDelay(self, value, qualifier):

        SyncOutputDelayString = 'AD{0};QVX:DSNI2'.format(self._DeviceID)
        SyncOutputDelayCmdString = b''.join([pack('>B', 0x02), SyncOutputDelayString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('SyncOutputDelay', SyncOutputDelayCmdString.decode(), value, qualifier)
        if res:
            try:
                value = int(res[8:13])
                self.WriteStatus('SyncOutputDelay', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Sync Output Delay: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 63
            }

        value = int(value)
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeString = 'AD{0};AVL:{1}'.format(self._DeviceID, value)
            VolumeCmdString = b''.join([pack('>B', 0x02), VolumeString.encode(), pack('>B', 0x03)])
            self.__SetHelper('Volume', VolumeCmdString.decode(), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeString = 'AD{0};QAV'.format(self._DeviceID)
        VolumeCmdString = b''.join([pack('>B', 0x02), VolumeString.encode(), pack('>B', 0x03)])
        res = self.__UpdateHelper('Volume', VolumeCmdString.decode(), value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        DEVICE_ERROR_CODES = {'\x02ER401\x03': 'Invalid Command Reply.',
                              '\x02ER402\x03': 'Invalid Parameter.'}
        if response:
            for k, _ in DEVICE_ERROR_CODES.items():
                if k in response:
                    segments = response.split('-')
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[segments[0]])])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Unexpected/Invalid response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {}

        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DInputFormat': { 'Status': {}},
            '3DMessage': { 'Status': {}},
            '3DMode': { 'Status': {}},
            '3DSyncLeftRightSwap': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DLPLinkLeftRightSwap': { 'Status': {}},
            'EdgeBlending': { 'Status': {}},
            'EdgeBlendingLeft': { 'Status': {}},
            'EdgeBlendingLower': { 'Status': {}},
            'EdgeBlendingRight': { 'Status': {}},
            'EdgeBlendingUpper': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}}, 
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SyncOutputDelay': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
        self.md5hash = ''
        self.Security = False
        
   
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'ERR([1-5A])\r'), self.__MatchError, None)


    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def Set3DInputFormat(self, value, qualifier):

        InputFormatStateValues = {
            'Auto'              : '00000',
            'Native'            : '00001',
            'Side by Side'      : '00003',
            'Top and Bottom'    : '00004',
            'Frame Sequential'  : '00006'
            }
        
        InputFormatCmdString = '00VXX:DIFI1=+{0}\r'.format(InputFormatStateValues[value])
        
        self.__SetHelper('3DInputFormat', InputFormatCmdString, value, qualifier)
            
    def Update3DInputFormat(self, value, qualifier):        

        InputFormatStateNames = {
            '0'  : 'Auto',
            '1'  : 'Native',
            '3'  : 'Side by Side',
            '4'  : 'Top and Bottom',
            '6'  : 'Frame Sequential'
            }

        InputFormatCmdString = '00QVX:DIFI1\r'  
        res = self.__UpdateHelper('3DInputFormat', InputFormatCmdString, value, qualifier)
        if res:
            try:
                value = InputFormatStateNames[res[13]]       
                self.WriteStatus('3DInputFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Input Format: Invalid/unexpected response'])

    def Set3DMessage(self, value, qualifier):

        MessageStateValues = {
            'Off'  : '00000',
            'On'   : '00001'
            }
        
        MessageCmdString = '00VXX:DMGI1=+{0}\r'.format(MessageStateValues[value])
        
        self.__SetHelper('3DMessage', MessageCmdString, value, qualifier)
            
    def Update3DMessage(self, value, qualifier):        

        MessageStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }

        MessageCmdString = '00QVX:DMGI1\r'  
        res = self.__UpdateHelper('3DMessage', MessageCmdString, value, qualifier)
        if res:
            try:
                value = MessageStateNames[res[12]]       
                self.WriteStatus('3DMessage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Message: Invalid/unexpected response'])

    def Set3DMode(self, value, qualifier):

        ModeStateValues = {
            'Off'       : '00000',
            'All On'    : '00001',
            '3D Sync'   : '00010',
            'DLP Link'  : '00011'
            }
        
        ModeCmdString = '00VXX:DMDI1=+{0}\r'.format(ModeStateValues[value])        
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)
            
    def Update3DMode(self, value, qualifier):        

        ModeStateNames = {
            '00'  : 'Off',
            '01'  : 'All On',
            '10'  : '3D Sync',
            '11'  : 'DLP Link'
            }

        ModeCmdString = '00QVX:DMDI1\r'  
        res = self.__UpdateHelper('3DMode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ModeStateNames[res[12:14]]       
                self.WriteStatus('3DMode', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['3D Mode: Invalid/unexpected response'])

    def Set3DSyncLeftRightSwap(self, value, qualifier):

        SyncSwapStateValues = {
            'Normal'  : '00000',
            'Swap'    : '00001'
            }
        
        SyncSwapCmdString = '00VXX:DSWI1=+{0}\r'.format(SyncSwapStateValues[value])
        
        self.__SetHelper('3DSyncLeftRightSwap', SyncSwapCmdString, value, qualifier)
            
    def Update3DSyncLeftRightSwap(self, value, qualifier):        

        SyncSwapStateNames = {
            '0'  : 'Normal',
            '1'  : 'Swap'
            }

        SyncSwapCmdString = '00QVX:DSWI1\r'  
        res = self.__UpdateHelper('3DSyncLeftRightSwap', SyncSwapCmdString, value, qualifier)
        if res:
            try:
                value = SyncSwapStateNames[res[13]]       
                self.WriteStatus('3DSyncLeftRightSwap', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['3D Sync Left Right Swap: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Normal' : '0',
            '4:3'    : '1',
            'Wide'   : '2',
            'Native' : '5',
            'Full'   : '6',
            'H Fit'  : '9',
            'V Fit'  : '10'
            }
        
        AspectRatioCmdString = '00VSE:{0}\r'.format(AspectRatioStateValues[value])
        
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            
    def UpdateAspectRatio(self, value, qualifier):        

        AspectRatioStateNames = {
            '0'  : 'Normal',
            '1'  : '4:3',
            '2'  : 'Wide',
            '5'  : 'Native',
            '6'  : 'Full',
            '9'  : 'H Fit',
            '10' : 'V Fit'
            }

        AspectRatioCmdString = '00QSE\r'  
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'Off' : '0',
            'On'  : '1'
            }
        
        AVMuteCmdString = '00OSH:{0}\r'.format(AVMuteStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)  

    def UpdateAVMute(self, value, qualifier):        
        AVMuteStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        AVMuteCmdString = '00QSH\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = AVMuteStateNames[res[2]]   
                self.WriteStatus('AVMute', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'CC1' : '1',
            'CC2' : '2',
            'CC3' : '3',
            'CC4' : '4',
            'Off' : '0'
            }
        
        ClosedCaptionCmdString = '00OCC:{0}\r'.format(ClosedCaptionStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)  

    def UpdateClosedCaption(self, value, qualifier):        
        ClosedCaptionStateNames = {
            '1' : 'CC1',
            '2' : 'CC2',
            '3' : 'CC3',
            '4' : 'CC4',
            '0' : 'Off' 
            }
        
        ClosedCaptionCmdString = '00QCC\r'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[2]]   
                self.WriteStatus('ClosedCaption', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetDLPLinkLeftRightSwap(self, value, qualifier):

        DLPLinkSwapStateValues = {
            'Normal'  : '00000',
            'Swap'    : '00001'
            }
        
        DLPLinkSwapCmdString = '00VXX:DSWI2=+{0}\r'.format(DLPLinkSwapStateValues[value])
        
        self.__SetHelper('DLPLinkLeftRightSwap', DLPLinkSwapCmdString, value, qualifier)
            
    def UpdateDLPLinkLeftRightSwap(self, value, qualifier):        

        DLPLinkSwapStateNames = {
            '0'  : 'Normal',
            '1'  : 'Swap'
            }

        DLPLinkSwapCmdString = '00QVX:DSWI2\r'  
        res = self.__UpdateHelper('DLPLinkLeftRightSwap', DLPLinkSwapCmdString, value, qualifier)
        if res:
            try:
                value = DLPLinkSwapStateNames[res[13]]       
                self.WriteStatus('DLPLinkLeftRightSwap', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['DLP Link LeftRight Swap: Invalid/unexpected response'])

    def SetEdgeBlending(self, value, qualifier):

        EdgeBlendingStateValues = {
            'Off' : '00000',
            'On'  : '00001'
            }
        
        EdgeBlendingCmdString = '00VXX:EDBI0=+{0}\r'.format(EdgeBlendingStateValues[value])
        self.__SetHelper('EdgeBlending', EdgeBlendingCmdString, value, qualifier)  

    def UpdateEdgeBlending(self, value, qualifier):        

        EdgeBlendingStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        EdgeBlendingCmdString = '00QVX:EDBI0\r'

        res = self.__UpdateHelper('EdgeBlending', EdgeBlendingCmdString, value, qualifier)
        if res:
            try:
                value = EdgeBlendingStateNames[res[13]]   
                self.WriteStatus('EdgeBlending', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Edge Blending: Invalid/unexpected response'])

    def SetEdgeBlendingLeft(self, value, qualifier):

        EdgeBlendingLeftStateValues = {
            'Off' : '0',
            'On'  : '1'
            }
        
        EdgeBlendingLeftCmdString = '00VGL:{0}\r'.format(EdgeBlendingLeftStateValues[value])
        self.__SetHelper('EdgeBlendingLeft', EdgeBlendingLeftCmdString, value, qualifier)  

    def UpdateEdgeBlendingLeft(self, value, qualifier):        
        EdgeBlendingLeftStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        EdgeBlendingLeftCmdString = '00QGL\r'

        res = self.__UpdateHelper('EdgeBlendingLeft', EdgeBlendingLeftCmdString, value, qualifier)
        if res:
            try:
                value = EdgeBlendingLeftStateNames[res[2]]   
                self.WriteStatus('EdgeBlendingLeft', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Edge Blending Left: Invalid/unexpected response'])

    def SetEdgeBlendingLower(self, value, qualifier):

        EdgeBlendingLowerStateValues = {
            'Off' : '0',
            'On'  : '1'
            }
        
        EdgeBlendingLowerCmdString = '00VGB:{0}\r'.format(EdgeBlendingLowerStateValues[value])
        self.__SetHelper('EdgeBlendingLower', EdgeBlendingLowerCmdString, value, qualifier)  

    def UpdateEdgeBlendingLower(self, value, qualifier):        
        EdgeBlendingLowerStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        EdgeBlendingLowerCmdString = '00QGB\r'
        res = self.__UpdateHelper('EdgeBlendingLower', EdgeBlendingLowerCmdString, value, qualifier)
        if res:
            try:
                value = EdgeBlendingLowerStateNames[res[2]]   
                self.WriteStatus('EdgeBlendingLower', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Edge Blending Lower: Invalid/unexpected response'])

    def SetEdgeBlendingRight(self, value, qualifier):

        EdgeBlendingRightStateValues = {
            'Off' : '0',
            'On'  : '1'
            }
        
        EdgeBlendingRightCmdString = '00VGR:{0}\r'.format(EdgeBlendingRightStateValues[value])
        self.__SetHelper('EdgeBlendingRight', EdgeBlendingRightCmdString, value, qualifier)  

    def UpdateEdgeBlendingRight(self, value, qualifier):        
        EdgeBlendingRightStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        EdgeBlendingRightCmdString = '00QGR\r'
        res = self.__UpdateHelper('EdgeBlendingRight', EdgeBlendingRightCmdString, value, qualifier)
        if res:
            try:
                value = EdgeBlendingRightStateNames[res[2]]   
                self.WriteStatus('EdgeBlendingRight', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Edge Blending Right: Invalid/unexpected response'])

    def SetEdgeBlendingUpper(self, value, qualifier):

        EdgeBlendingUpperStateValues = {
            'Off' : '0',
            'On'  : '1'
            }
        
        EdgeBlendingUpperCmdString = '00VGU:{0}\r'.format(EdgeBlendingUpperStateValues[value])
        self.__SetHelper('EdgeBlendingUpper', EdgeBlendingUpperCmdString, value, qualifier)  

    def UpdateEdgeBlendingUpper(self, value, qualifier):        
        EdgeBlendingUpperStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        EdgeBlendingUpperCmdString = '00QGU\r'
        res = self.__UpdateHelper('EdgeBlendingUpper', EdgeBlendingUpperCmdString, value, qualifier)
        if res:
            try:
                value = EdgeBlendingUpperStateNames[res[2]]   
                self.WriteStatus('EdgeBlendingUpper', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Edge Blending Upper: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On'  : '1',
            'Off' : '0',
            }
        
        FreezeCmdString = '00OFZ:{0}\r'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)  

    def UpdateFreeze(self, value, qualifier):        
        FreezeStateNames = {
            '1' : 'On',
            '0' : 'Off' 
            }
        
        FreezeCmdString = '00QFZ\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[2]]   
                self.WriteStatus('Freeze', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Computer'                : 'RG1',
            'Video'                   : 'VID',           
            'DVI'                     : 'DVI',
            'HDMI'                    : 'HD1',
            'Digital Link'            : 'DL1',
            'Digital Link HDMI 1'     : 'DL1:HD1',
            'Digital Link HDMI 2'     : 'DL1:HD2',
            'Digital Link Computer 1' : 'DL1:PC1',
            'Digital Link Computer 2' : 'DL1:PC2',
            'Digital Link Video'      : 'DL1:VID',
            'Digital Link S-Video'    : 'DL1:SVD'
            }
        
        InputCmdString = '00IIS:{0}\r'.format(InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):        
        InputStateNames = {
            'RG1'     : 'Computer',
            'VID'     : 'Video',
            'DVI'     : 'DVI',
            'HD1'     : 'HDMI',
            'DL1'     : 'Digital Link',
            'DL1:HD1' : 'Digital Link HDMI 1',
            'DL1:HD2' : 'Digital Link HDMI 2',
            'DL1:PC1' : 'Digital Link Computer 1',
            'DL1:PC2' : 'Digital Link Computer 2',
            'DL1:VID' : 'Digital Link Video',
            'DL1:SVD' : 'Digital Link S-Video'
            }
        
        InputCmdString = '00QIN\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal'     : '0',
            'Low'        : '1',
            'ECO Save 1' : '6',
            'ECO Save 2' : '7'
            }
        
        LampModeCmdString = '00OLP:{0}\r'.format(LampModeStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        
    def UpdateLampMode(self, value, qualifier):        
        LampModeStateNames = {
            '0' : 'Normal',
            '1' : 'Low',
            '6' : 'ECO Save 1',
            '7' : 'ECO Save 2',
            }
        
        LampModeCmdString = '00QLP\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[2]]   
                self.WriteStatus('LampMode', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):        

        LampUsageCmdString = '00QST\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])   
                self.WriteStatus('LampUsage', value, qualifier)  
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu'   : 'OMN',
            'Up'     : 'OCU',
            'Down'   : 'OCD',
            'Left'   : 'OCL',
            'Right'  : 'OCR',
            'Enter'  : 'OEN',
            'Return' : 'OBK'
            }
        
        MenuNavigationCmdString = '00{0}\r'.format(MenuNavigationStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On'  : '1',
            'Off' : '0',
            }
        
        OnScreenDisplayCmdString = '00OOS:{0}\r'.format(OnScreenDisplayStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)  

    def UpdateOnScreenDisplay(self, value, qualifier):        
        OnScreenDisplayStateNames = {
            '1' : 'On',
            '0' : 'Off' 
            }
        
        OnScreenDisplayCmdString = '00QOS\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateNames[res[2]]   
                self.WriteStatus('OnScreenDisplay', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural'  : 'NAT',
            'Standard' : 'STD',
            'Dynamic'  : 'DYN',
            'Cinema'   : 'CIN',
            'Graphic'  : 'GRA',
            'DICOM'    : 'DIC',
            'Rec. 709' : '709'
            }
        
        PictureModeCmdString = '00VPM:{0}\r'.format(PictureModeStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)  

    def UpdatePictureMode(self, value, qualifier):        
        PictureModeStateNames = {
            'NAT' : 'Natural',
            'STD' : 'Standard',
            'DYN' : 'Dynamic',
            'CIN' : 'Cinema',
            'GRA' : 'Graphic',
            'DIC' : 'DICOM',
            '709' : 'Rec. 709' 
            }
        
        PictureModeCmdString = '00QPM\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[2:5]]   
                self.WriteStatus('PictureMode', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : 'PON',
            'Off' : 'POF'
            }
        PowerCmdString = '00{0}\r'.format(PowerStateValues[value])        
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):        

        PowerStateNames = {
            '2' : 'On',
            '0' : 'Off',
            '1' : 'Warming Up',
            '3' : 'Cooling Down'
            }

        PowerCmdString = '00Q$S\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[2]]   
                self.WriteStatus('Power', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSyncOutputDelay(self, value, qualifier):

        DelayConstraints = {
            'Min' : 0,
            'Max' : 25000
            }
        value - int(value)
        if DelayConstraints['Min'] <= value <= DelayConstraints['Max']:        
            SyncOutputDelayCmdString = '00VXX:DSNI2=+{:05d}\r'.format(value)
            self.__SetHelper('SyncOutputDelay', SyncOutputDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSyncOutputDelay')
            
    def UpdateSyncOutputDelay(self, value, qualifier):        


        SyncOutputDelayCmdString = '00QVX:DSNI2\r'  
        res = self.__UpdateHelper('SyncOutputDelay', SyncOutputDelayCmdString, value, qualifier)
        if res:
            try:
                value = int(res[9:14])       
                self.WriteStatus('SyncOutputDelay', value, qualifier)  
            except (ValueError, IndexError):
                self.Error(['Sync Output Delay: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 63
            }
  
        value = int(value)
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '00AVL:{0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):        


        VolumeCmdString = '00QAV\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])    
                self.WriteStatus('Volume', value, qualifier)  
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        
        if isinstance(response, bytes):
            response = response.decode()

        DEVICE_ERROR_CODES = {'\x02ER401\x03': 'Invalid Command Reply.',
                              '\x02ER402\x03': 'Invalid Parameter.'}   
        if response:
            for k, _ in DEVICE_ERROR_CODES.items():
                if k in response:
                    segments = response.split('-')
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[segments[0]])])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Security:
            commandstring = self.md5hash + commandstring.encode()

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Unexpected/Invalid response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            if self.Security:
                commandstring = self.md5hash + commandstring.encode()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def __MatchError(self, match, tag):

        ErrorValue = {
            '1' : 'Undefined control command',
            '2' : 'Out of parameter range',
            '3' : 'Busy state or no-acceptable period',
            '4' : 'Timeout or no-acceptable period',
            '5' : 'Wrong data length',
            'A' : 'Password mismatch',

        }
        value = match.group(1).decode()
        self.Error([ErrorValue[value]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Security = False
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
