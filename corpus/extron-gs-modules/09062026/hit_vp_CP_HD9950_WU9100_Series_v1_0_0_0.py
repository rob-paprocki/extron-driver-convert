from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'EcoMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'PbyPLeftSource': {'Status': {}},
            'PbyPRightSource': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPMainInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSubInput': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)
            self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        self.SetPassword(match, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            'Zoom': b'\xBE\xEF\x03\x06\x00\x9E\xC4\x01\x00\x08\x20\x30\x00'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native',
            b'\x30': 'Zoom'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00'
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/Unexpected Response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            'CC2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            'CC3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            'CC4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
        }

        ClosedCaptionChannelCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'CC1',
            b'\x02': 'CC2',
            b'\x03': 'CC3',
            b'\x04': 'CC4',
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/Unexpected Response'])

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
                self.Error(['Closed Caption Mode: Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temp Error',
            b'\x05': 'Air flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
            b'\x0F': 'Shutter Error',
            b'\x10': 'Lens Shift Error',
            b'\x13': 'Lamp-1 Warning',
            b'\x23': 'Lamp-2 Warning',
            b'\x41': 'Humidity Error',
            b'\x52': 'Color Wheel Error',
            b'\x53': 'Active Iris Error',
            b'\x60': 'AC Blackout Error',
            b'\x40': 'Other Error',
            b'\x42': 'Other Error',
            b'\x43': 'Other Error',
            b'\x44': 'Other Error',
            b'\x50': 'Other Error',
            b'\x51': 'Other Error',
            b'\x54': 'Other Error',
            b'\x55': 'Other Error',
            b'\x56': 'Other Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status : Invalid/Unexpected Response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString1 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'  # Higher Bytes
        res1 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString1, value, qualifier)
        FilterUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'  # Lower Bytes
        res2 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString2, value, qualifier)
        if res1 and res2:
            try:
                value = (res1[1:2][0] * 256) + (res2[1:2][0])
                self.WriteStatus('FilterUsage', value, qualifier)
            except IndexError:
                self.Error(['Filter Usage: Invalid/Unexpected Response'])

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
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'DVI-D': b'\xBE\xEF\x03\x06\x00\xAE\xD4\x01\x00\x00\x20\x09\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'SDI/Digital 1': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x00\x20\x12\x00'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x0B': 'LAN',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x09': 'DVI-D',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x12': 'SDI/Digital 1'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Eco'
        }

        EcoModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Dual': b'\xBE\xEF\x03\x06\x00\x1F\x21\x01\x00\x0B\x33\x00\x00',
            'Lamp 1': b'\xBE\xEF\x03\x06\x00\x8F\x20\x01\x00\x0B\x33\x01\x00',
            'Lamp 2': b'\xBE\xEF\x03\x06\x00\x7F\x20\x01\x00\x0B\x33\x02\x00',
            'Alternate': b'\xBE\xEF\x03\x06\x00\xDF\x2C\x01\x00\x0B\x33\x10\x00'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Dual',
            b'\x01': 'Lamp 1',
            b'\x02': 'Lamp 2',
            b'\x10': 'Alternate'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x2C\x21\x02\x00\x0B\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        resHigh = None
        resLow = None
        if 1 <= int(lamp) <= 2:
            if lamp == '1':
                Lamp1UsageCmdString = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'  # Higher Bytes
                resHigh = self.__UpdateHelper('LampUsage', Lamp1UsageCmdString, value, qualifier)
                Lamp1UsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'  # Lower Bytes
                resLow = self.__UpdateHelper('LampUsage', Lamp1UsageCmdString2, value, qualifier)
            elif lamp == '2':
                Lamp2UsageCmdString = b'\xBE\xEF\x03\x06\x00\xFE\xAF\x02\x00\x91\x11\x00\x00'  # Higher Bytes
                resHigh = self.__UpdateHelper('LampUsage', Lamp2UsageCmdString, value, qualifier)
                Lamp2UsageCmdString2 = b'\xBE\xEF\x03\x06\x00\x02\xAE\x02\x00\x90\x11\x00\x00'  # Lower Bytes
                resLow = self.__UpdateHelper('LampUsage', Lamp2UsageCmdString2, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateLampUsage')
            if resHigh and resLow:
                try:
                    value = (resHigh[1:2][0] * 256) + resLow[1:2][0]
                    self.WriteStatus('LampUsage', value, qualifier)
                except IndexError:
                    self.Error(['Lamp Usage: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PbyP': b'\xBE\xEF\x03\x06\x00\xAE\x27\x01\x00\x10\x23\x01\x00',
            'PinP': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x10\x23\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'PbyP',
            b'\x02': 'PinP',
            b'\x00': 'Off'
        }

        PIPModeCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/Unexpected Response'])

    def SetPbyPLeftSource(self, value, qualifier):

        ValueStateValues = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'DVI-D': b'\xBE\xEF\x03\x06\x00\xA2\x20\x01\x00\x15\x23\x09\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00',
            'SDI/Digital 1': b'\xBE\xEF\x03\x06\x00\x52\x2A\x01\x00\x15\x23\x12\x00'
        }

        PbyPLeftSourceCmdString = ValueStateValues[value]
        self.__SetHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)

    def UpdatePbyPLeftSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x09': 'DVI-D',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x12': 'SDI/Digital 1'
        }

        PbyPLeftSourceCmdString = b'\xBE\xEF\x03\x06\x00\xC1\x26\x02\x00\x15\x23\x00\x00'
        res = self.__UpdateHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPLeftSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Left Source: Invalid/Unexpected Response'])

    def SetPbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateValues = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'DVI-D': b'\xBE\xEF\x03\x06\x00\xD6\x21\x01\x00\x12\x23\x09\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00',
            'SDI/Digital 1': b'\xBE\xEF\x03\x06\x00\x26\x2B\x01\x00\x12\x23\x12\x00'
        }

        PbyPRightSourceCmdString = PbyPRightSourceStateValues[value]
        self.__SetHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)

    def UpdatePbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateNames = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x09': 'DVI-D',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x12': 'SDI/Digital 1'
        }

        PbyPRightSourceCmdString = b'\xBE\xEF\x03\x06\x00\xB5\x27\x02\x00\x12\x23\x00\x00'
        res = self.__UpdateHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)
        if res:
            try:
                value = PbyPRightSourceStateNames[res[1:2]]
                self.WriteStatus('PbyPRightSource', value, None)
            except (KeyError, IndexError):
                self.Error(['PIP Right Source: Invalid/Unexpected Response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\xBE\xEF\x03\x06\x00\x83\xF5\x01\x00\xBA\x30\x06\x00',
            'Natural': b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00',
            'Cinema': b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00',
            'Dynamic': b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00',
            'Board (Black)': b'\xBE\xEF\x03\x06\x00\xE3\xEF\x01\x00\xBA\x30\x20\x00',
            'Board (Green)': b'\xBE\xEF\x03\x06\x00\x73\xEE\x01\x00\xBA\x30\x21\x00',
            'Whiteboard': b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00',
            'Daytime': b'\xBE\xEF\x03\x06\x00\xE3\xC7\x01\x00\xBA\x30\x40\x00',
            'Dicom Sim': b'\xBE\xEF\x03\x06\x00\x73\xC6\x01\x00\xBA\x30\x41\x00',
            'User-1': b'\xBE\xEF\x03\x06\x00\xE3\xFB\x01\x00\xBA\x30\x10\x00',
            'User-2': b'\xBE\xEF\x03\x06\x00\x73\xFA\x01\x00\xBA\x30\x11\x00',
            'User-3': b'\xBE\xEF\x03\x06\x00\x83\xFA\x01\x00\xBA\x30\x12\x00'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'\x06': 'Standard',
            b'\x00': 'Natural',
            b'\x01': 'Cinema',
            b'\x04': 'Dynamic',
            b'\x20': 'Board (Black)',
            b'\x21': 'Board (Green)',
            b'\x22': 'Whiteboard',
            b'\x40': 'Daytime',
            b'\x41': 'Dicom Sim',
            b'\x10': 'User-1',
            b'\x11': 'User-2',
            b'\x12': 'User-3'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/Unexpected Response'])

    def SetPIPMainInput(self, value, qualifier):

        ValueStateValues = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'DVI-D': b'\xBE\xEF\x03\x06\x00\x9E\x25\x01\x00\x04\x23\x09\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00',
            'SDI/Digital 1': b'\xBE\xEF\x03\x06\x00\x6E\x2F\x01\x00\x04\x23\x12\x00'
        }

        PIPMainInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)

    def UpdatePIPMainInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x09': 'DVI-D',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x12': 'SDI/Digital 1'
        }

        PIPMainInputCmdString = b'\xBE\xEF\x03\x06\x00\xFD\x23\x02\x00\x04\x23\x00\x00'
        res = self.__UpdateHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPMainInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Main Input: Invalid/Unexpected Response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x01\x23\x02\x00',
            'Bottom Right': b'\xBE\xEF\x03\x06\x00\xF2\x23\x01\x00\x01\x23\x03\x00',
            'Top Left': b'\xBE\xEF\x03\x06\x00\x02\x23\x01\x00\x01\x23\x00\x00',
            'Top Right': b'\xBE\xEF\x03\x06\x00\x92\x22\x01\x00\x01\x23\x01\x00'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'Bottom Left',
            b'\x03': 'Bottom Right',
            b'\x00': 'Top Left',
            b'\x01': 'Top Right'
        }

        PIPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/Unexpected Response'])

    def SetPIPSubInput(self, value, qualifier):

        ValueStateValues = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'DVI-D': b'\xBE\xEF\x03\x06\x00\x16\x25\x01\x00\x02\x23\x09\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00',
            'SDI/Digital 1': b'\xBE\xEF\x03\x06\x00\xE6\x2F\x01\x00\x02\x23\x12\x00'
        }

        PIPSubInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)

    def UpdatePIPSubInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x09': 'DVI-D',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x12': 'SDI/Digital 1'
        }

        PIPSubInputCmdString = b'\xBE\xEF\x03\x06\x00\x75\x23\x02\x00\x02\x23\x00\x00'
        res = self.__UpdateHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPSubInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Sub Input: Invalid/Unexpected Response'])

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

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
                self.Error(['Power: Invalid/Unexpected Response'])

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
                self.Error(['Shutter: Invalid/Unexpected Response'])

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
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Projector Error",
            b'\x1F': "Authentication Error",
        }
        if len(response) == 8:
            self.SetPassword(res, None)
            response = ''
        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                res = ''
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
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