from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
from struct import pack
from struct import unpack
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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'LWU601i': self.chri_other,
            'LW651i': self.chri_other,
            'LWU701i': self.chri_701,
            'LW751i': self.chri_other,
            'LX801i': self.chri_801,
            'LWU601i-D': self.chri_other,
            'LWU720i': self.chri_701,
            'LWU620i': self.chri_other,
            'LHD720i': self.chri_701,
            'LWU720i-D': self.chri_701,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'EcoMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Mute': {'Status': {}},
            'PbyPMainArea': {'Status': {}},
            'PbyPMainSize': {'Status': {}},
            'PbyPPIPSwap': {'Status': {}},
            'PbyPSource': {'Parameters': ['Area'], 'Status': {}},
            'PIPMainArea': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSource': {'Parameters': ['Area'], 'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VolumeStatus': {'Parameters': ['Input'], 'Status': {}},
            'VolumeStep': {'Parameters': ['Input'], 'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.devicePassword = None
        self.Authenticated = 'Not Needed'
        self.DelRex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F\x04\x00)')

        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'([a-f0-9]{8})'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            inStr = match.group(1).decode()
            outStr = inStr + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest()) + b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Authenticated = 'Admin'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectStates[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.ReturnAspectStates[res[1:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6E\xF1\x01\x00\xA0\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xF0\x01\x00\xA0\x20\x00\x00'
        }

        AVMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xF0\x02\x00\xA0\x20\x00\x00'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Auto'
        }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
        }

        ClosedCaptionChannelCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4'
        }
        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption CHannel: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }

        ClosedCaptionModeCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
            b'\x0F': 'Shutter Error',
            b'\x10': 'Lens Shift Error',
            b'\x60': 'AC Blackout Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        EcoModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)

        if res:
            try:
                value = unpack('<H', res[1:3])[0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'In': b'\xBE\xEF\x03\x06\x00\x6A\x93\x04\x00\x00\x24\x00\x00',
            'Out': b'\xBE\xEF\x03\x06\x00\xBB\x92\x05\x00\x00\x24\x00\x00'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
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

        InputCmdString = self.InputStates[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.ReturnInputStates[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        if res:
            try:
                value = unpack('<H', res[1:3])[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        MuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPbyPMainArea(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\xBE\xEF\x03\x06\x00\x7A\x26\x01\x00\x13\x23\x00\x00',
            'Right': b'\xBE\xEF\x03\x06\x00\xEA\x27\x01\x00\x13\x23\x01\x00'
        }

        PbyPMainAreaCmdString = ValueStateValues[value]
        self.__SetHelper('PbyPMainArea', PbyPMainAreaCmdString, value, qualifier)

    def UpdatePbyPMainArea(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Left',
            b'\x01': 'Right'
        }

        PbyPMainAreaCmdString = b'\xBE\xEF\x03\x06\x00\x49\x26\x02\x00\x13\x23\x00\x00'
        res = self.__UpdateHelper('PbyPMainArea', PbyPMainAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPMainArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Main Area: Invalid/unexpected response'])

    def SetPbyPMainSize(self, value, qualifier):

        ValueStateValues = {
            'Small': b'\xBE\xEF\x03\x06\x00\xF2\x07\x01\x00\x11\x23\x7F\x00',
            'Middle': b'\xBE\xEF\x03\x06\x00\x02\x46\x01\x00\x11\x23\x80\x00',
            'Large': b'\xBE\xEF\x03\x06\x00\x92\x47\x01\x00\x11\x23\x81\x00'
        }

        PbyPMainSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PbyPMainSize', PbyPMainSizeCmdString, value, qualifier)

    def UpdatePbyPMainSize(self, value, qualifier):

        ValueStateValues = {
            b'\x7F': 'Small',
            b'\x80': 'Middle',
            b'\x81': 'Large'
        }

        PbyPMainSizeCmdString = b'\xBE\xEF\x03\x06\x00\xF1\x27\x02\x00\x11\x23\x00\x00'
        res = self.__UpdateHelper('PbyPMainSize', PbyPMainSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPMainSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Main Size: Invalid/unexpected response'])

    def SetPbyPPIPSwap(self, value, qualifier):

        PbyPPIPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPPIPSwap', PbyPPIPSwapCmdString, value, qualifier)

    def SetPbyPSource(self, value, qualifier):

        if qualifier['Area'] == 'Left':
            PbyPSourceCmdString = self.LeftSourceStates[value]
            self.__SetHelper('PbyPSource', PbyPSourceCmdString, value, qualifier)
        elif qualifier['Area'] == 'Right':
            PbyPSourceCmdString = self.RightSourceStates[value]
            self.__SetHelper('PbyPSource', PbyPSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPbyPSource')

    def UpdatePbyPSource(self, value, qualifier):

        AreaStates = {
            'Left': b'\xBE\xEF\x03\x06\x00\xC1\x26\x02\x00\x15\x23\x00\x00',
            'Right': b'\xBE\xEF\x03\x06\x00\xB5\x27\x02\x00\x12\x23\x00\x00'
        }
        PbyPSourceCmdString = AreaStates[qualifier['Area']]
        res = self.__UpdateHelper('PbyPSource', PbyPSourceCmdString, value, qualifier)
        if res:
            try:
                value = self.ReturnInputStates[res[1:2]]
                self.WriteStatus('PbyPSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Source: Invalid/unexpected response'])

    def SetPIPMainArea(self, value, qualifier):

        ValueStateValues = {
            'Primary': b'\xBE\xEF\x03\x06\x00\x32\x22\x01\x00\x05\x23\x00\x00',
            'Secondary': b'\xBE\xEF\x03\x06\x00\xA2\x23\x01\x00\x05\x23\x01\x00'
        }

        PIPMainAreaCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMainArea', PIPMainAreaCmdString, value, qualifier)

    def UpdatePIPMainArea(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Primary',
            b'\x01': 'Secondary'
        }

        PIPMainAreaCmdString = b'\xBE\xEF\x03\x06\x00\x01\x22\x02\x00\x05\x23\x00\x00'
        res = self.__UpdateHelper('PIPMainArea', PIPMainAreaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPMainArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Main Area: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x10\x23\x02\x00',
            'PbyP': b'\xBE\xEF\x03\x06\x00\xAE\x27\x01\x00\x10\x23\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'PIP',
            b'\x01': 'PbyP',
            b'\x00': 'Off'
        }

        PIPModeCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIPMode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': b'\xBE\xEF\x03\x06\x00\x02\x23\x01\x00\x01\x23\x00\x00',
            'Top Right': b'\xBE\xEF\x03\x06\x00\x92\x22\x01\x00\x01\x23\x01\x00',
            'Bottom Left': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x01\x23\x02\x00',
            'Bottom Right': b'\xBE\xEF\x03\x06\x00\xF2\x23\x01\x00\x01\x23\x03\x00'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Top Left',
            b'\x01': 'Top Right',
            b'\x02': 'Bottom Left',
            b'\x03': 'Bottom Right'
        }

        PIPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSource(self, value, qualifier):

        if qualifier['Area'] == 'Primary':
            PIPSourceCmdString = self.PrimarySourceStates[value]
            self.__SetHelper('PIPSource', PIPSourceCmdString, value, qualifier)
        elif qualifier['Area'] == 'Secondary':
            PIPSourceCmdString = self.SecondarySourceStates[value]
            self.__SetHelper('PIPSource', PIPSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSource')

    def UpdatePIPSource(self, value, qualifier):

        AreaStates = {
            'Primary': b'\xBE\xEF\x03\x06\x00\xFD\x23\x02\x00\x04\x23\x00\x00',
            'Secondary': b'\xBE\xEF\x03\x06\x00\x75\x23\x02\x00\x02\x23\x00\x00'
        }

        PIPSourceCmdString = AreaStates[qualifier['Area']]
        res = self.__UpdateHelper('PIPSource', PIPSourceCmdString, value, qualifier)
        if res:
            try:
                value = self.ReturnInputStates[res[1:2]]
                self.WriteStatus('PIPSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Source: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x63\x92\x01\x00\x05\x24\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xF3\x93\x01\x00\x05\x24\x00\x00'
        }

        ShutterCmdString = ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ShutterCmdString = b'\xBE\xEF\x03\x06\x00\xC0\x93\x02\x00\x05\x24\x00\x00'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = self.VolQueryStates[qualifier['Input']]
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                if 0 <= value <= 48:
                    self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Status: Invalid/unexpected response'])

    def SetVolumeStep(self, value, qualifier):

        if value == 'Increment':
            VolumeStepCmdString = self.VolIncStates[qualifier['Input']]
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        elif value == 'Decrement':
            VolumeStepCmdString = self.VolDecStates[qualifier['Input']]
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': b'\xBE\xEF\x03\x06\x00\x96\x92\x04\x00\x01\x24\x00\x00',
            'Out': b'\xBE\xEF\x03\x06\x00\x47\x93\x05\x00\x01\x24\x00\x00'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, str):
            response = response.encode()

        DEVICE_ERROR_CODES = {
            b'\x15': "NAK Reply",
            b'\x1C': "Error Reply",
        }

        if response:
            for k in DEVICE_ERROR_CODES:
                if len(response) == 8:
                    self.SetPassword(response, None)
                    response = ''
                elif response[0:1] in DEVICE_ERROR_CODES:
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
                    response = ''
                elif response[0:1] == b'\x1F':
                    self.Authenticated = 'None'
                    self.Error(['{0}: Authentication Error.'.format(sourceCmdName)])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.DelRex)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.DelRex)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)
            return ''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def chri_other(self):

        self.AspectStates = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00'
        }

        self.ReturnAspectStates = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native'
        }

        self.InputStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x00\x20\x13\x00'
        }

        self.ReturnInputStates = {
            b'\x00': 'Computer',
            b'\x0B': 'LAN',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x13': 'DisplayPort'
        }

        self.LeftSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xC2\x2B\x01\x00\x15\x23\x13\x00'
        }

        self.RightSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\x2A\x01\x00\x12\x23\x13\x00'
        }

        self.PrimarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xFE\x2E\x01\x00\x04\x23\x13\x00'
        }

        self.SecondarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x76\x2E\x01\x00\x02\x23\x13\x00'
        }

        self.VolQueryStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xC1\xEA\x02\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x01\xE1\x02\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xCD\xC3\x02\x00\x50\x20\x00\x00'
        }

        self.VolIncStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA7\xEA\x04\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x67\xE1\x04\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xAB\xC3\x04\x00\x50\x20\x00\x00'
        }

        self.VolDecStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x76\xEB\x05\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\xE0\x05\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\x7A\xC2\x05\x00\x50\x20\x00\x00'
        }

    def chri_701(self):

        self.AspectStates = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00'
        }

        self.ReturnAspectStates = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native'
        }

        self.InputStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x00\x20\x13\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x00\x20\x12\x00'
        }

        self.ReturnInputStates = {
            b'\x00': 'Computer',
            b'\x0B': 'LAN',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x13': 'DisplayPort',
            b'\x12': 'SDI'
        }

        self.LeftSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xC2\x2B\x01\x00\x15\x23\x13\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\x52\x2A\x01\x00\x15\x23\x12\x00'
        }

        self.RightSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\x2A\x01\x00\x12\x23\x13\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\x26\x2B\x01\x00\x12\x23\x12\x00'
        }

        self.PrimarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xFE\x2E\x01\x00\x04\x23\x13\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\x6E\x2F\x01\x00\x04\x23\x12\x00'
        }

        self.SecondarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x76\x2E\x01\x00\x02\x23\x13\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\xE6\x2F\x01\x00\x02\x23\x12\x00'
        }

        self.VolQueryStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xC1\xEA\x02\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x01\xE1\x02\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\xC1\xE5\x02\x00\xE5\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xCD\xC3\x02\x00\x50\x20\x00\x00'
        }

        self.VolIncStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA7\xEA\x04\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x67\xE1\x04\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xAB\xC3\x04\x00\x50\x20\x00\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\xA7\xE5\x04\x00\xE5\x20\x00\x00'
        }

        self.VolDecStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x76\xEB\x05\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\xE0\x05\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\x7A\xC2\x05\x00\x50\x20\x00\x00',
            'SDI': b'\xBE\xEF\x03\x06\x00\x76\xE4\x05\x00\xE5\x20\x00\x00'
        }

    def chri_801(self):

        self.AspectStates = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00'
        }

        self.ReturnAspectStates = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9'
        }

        self.InputStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x00\x20\x13\x00'
        }

        self.ReturnInputStates = {
            b'\x00': 'Computer',
            b'\x0B': 'LAN',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x13': 'DisplayPort'
        }

        self.LeftSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xC2\x2B\x01\x00\x15\x23\x13\x00'
        }

        self.RightSourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\x2A\x01\x00\x12\x23\x13\x00'
        }

        self.PrimarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xFE\x2E\x01\x00\x04\x23\x13\x00'
        }

        self.SecondarySourceStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x76\x2E\x01\x00\x02\x23\x13\x00'
        }

        self.VolQueryStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xC1\xEA\x02\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x01\xE1\x02\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xCD\xC3\x02\x00\x50\x20\x00\x00'
        }

        self.VolIncStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA7\xEA\x04\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\x67\xE1\x04\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xAB\xC3\x04\x00\x50\x20\x00\x00'
        }

        self.VolDecStates = {
            'Computer': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x76\xEB\x05\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
            'DisplayPort': b'\xBE\xEF\x03\x06\x00\xB6\xE0\x05\x00\xF5\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\x7A\xC2\x05\x00\x50\x20\x00\x00'
        }

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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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



