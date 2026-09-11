from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify
from extronlib.system import Wait, ProgramLog

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
        self.devicePassword = None
        self.Models = {}

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
            'EcoMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PbyPMainArea': {'Status': {}},
            'PbyPMainSize': {'Status': {}},
            'PbyPPIPFrameLock': {'Status': {}},
            'PbyPPIPModeSelect': {'Status': {}},
            'PbyPSource': {'Parameters': ['Area'], 'Status': {}},
            'PbyPSwap': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPMainArea': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSource': {'Parameters': ['Area'], 'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Input Type'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['Input Type'], 'Status': {}}
        }

        self.Authenticated = 'Not Needed'
        
        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)

            self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword(match, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Native': [b'\x5E\xD7', b'\x08\x00'],
            'Zoom': [b'\x9E\xC4', b'\x30\x00']
        }

        AspectRatioCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x08\x20', ValueStateValues[value][1]])
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
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\xD6\xD2', b'\x01\x00'],
            'Off': [b'\x46\xD3', b'\x00\x00']
        }

        AudioMuteCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x02\x20', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6E\xF1', b'\x01\x00'],
            'Off': [b'\xFE\xF0', b'\x00\x00']
        }

        AVMuteCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\xA0\x20', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateAVMute')

    def SetClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            '1': [b'\xD2\x62', b'\x01\x00'],
            '2': [b'\x22\x62', b'\x02\x00'],
            '3': [b'\xB2\x63', b'\x03\x00'],
            '4': [b'\x82\x61', b'\x04\x00']
        }

        ClosedCaptionsChannelCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x02\x37' + ValueStateValues[value][1]])
        self.__SetHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)

    def UpdateClosedCaptionsChannel(self, value, qualifier):

        ValueStateValues = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4'
        }

        ClosedCaptionsChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsChannel', ClosedCaptionsChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionsChannel', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateClosedCaptionsChannel')

    def SetClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\xFA\x62', b'\x00\x00'],
            'On': [b'\x6A\x63', b'\x01\x00'],
            'Auto': [b'\x9A\x63', b'\x02\x00']
        }

        ClosedCaptionsDisplayCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x00\x37', ValueStateValues[value][1]])
        self.__SetHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionsDisplay(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02': 'Auto'
        }

        ClosedCaptionsDisplayCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionsDisplay', ClosedCaptionsDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('ClosedCaptionsDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateClosedCaptionsDisplay')

    def SetClosedCaptionsMode(self, value, qualifier):

        ValueStateValues = {
            'Captions': [b'\x06\x63', b'\x00\x00'],
            'Text': [b'\x96\x62', b'\x01\x00']
        }

        ClosedCaptionsModeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x01\x37', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateClosedCaptionsMode')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temp Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
            b'\x0F': 'Shutter Error',
            b'\x60': 'AC Blackout Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': [b'\x3B\x23', b'\x00\x00'],
            'Eco': [b'\xAB\x22', b'\x01\x00']
        }

        EcoModeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x00\x33', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateEcoMode')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)

        FilterUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'
        res2 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1] * 256 + res[1]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x13\xD3', b'\x01\x00'],
            'Off': [b'\x83\xD2', b'\x00\x00']
        }

        FreezeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x02\x30', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'HDBaseT': [b'\xAE\xDE', b'\x11\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00'],
            'Computer In': [b'\xFE\xD2', b'\x00\x00']
        }

        InputCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x00\x20', ValueStateValues[value][1]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x0B': 'LAN',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video',
            b'\x00': 'Computer In'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        LampUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'
        res2 = self.__UpdateHelper('LampUsage', LampUsageCmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1] * 256 + res[1]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetPbyPMainArea(self, value, qualifier):

        ValueStateValues = {
            'Left': [b'\x7A\x26', b'\x00\x00'],
            'Right': [b'\xEA\x27', b'\x01\x00']
        }

        PbyPMainAreaCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x13\x23', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdatePbyPMainArea')

    def SetPbyPMainSize(self, value, qualifier):

        ValueStateValues = {
            'Small': [b'\xF2\x07', b'\x7F\x00'],
            'Middle': [b'\x02\x46', b'\x80\x00'],
            'Large': [b'\x92\x47', b'\x81\x00']
        }

        PbyPMainSizeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x11\x23', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdatePbyPMainSize')

    def SetPbyPPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            'Left / Primary': [b'\x4A\x27', b'\x00\x00'],
            'Right / Secondary': [b'\xDA\x26', b'\x01\x00']
        }

        PbyPPIPFrameLockCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x17\x23', ValueStateValues[value][1]])
        self.__SetHelper('PbyPPIPFrameLock', PbyPPIPFrameLockCmdString, value, qualifier)

    def UpdatePbyPPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Left / Primary',
            b'\x01': 'Right / Secondary'
        }

        PbyPPIPFrameLockCmdString = b'\xBE\xEF\x03\x06\x00\x79\x27\x02\x00\x17\x23\x00\x00'
        res = self.__UpdateHelper('PbyPPIPFrameLock', PbyPPIPFrameLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPPIPFrameLock', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePbyPPIPFrameLock')

    def SetPbyPPIPModeSelect(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\x3E\x26', b'\x00\x00'],
            'PbyP': [b'\xAE\x27', b'\x01\x00'],
            'PIP': [b'\x5E\x27', b'\x02\x00']
        }

        PbyPPIPModeSelectCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x10\x23', ValueStateValues[value][1]])
        self.__SetHelper('PbyPPIPModeSelect', PbyPPIPModeSelectCmdString, value, qualifier)

    def UpdatePbyPPIPModeSelect(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'PbyP',
            b'\x02': 'PIP'
        }

        PbyPPIPModeSelectCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyPPIPModeSelect', PbyPPIPModeSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPPIPModeSelect', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePbyPPIPModeSelect')

    def SetPbyPSource(self, value, qualifier):

        RightValue = {
            'Computer In': [b'\x86\x27', b'\x00\x00'],
            'HDMI 1': [b'\x76\x27', b'\x03\x00'],
            'HDMI 2': [b'\x16\x23', b'\x0D\x00'],
            'HDBaseT': [b'\xD6\x2B', b'\x11\x00'],
            'Video': [b'\x16\x26', b'\x01\x00']
        }

        LeftValue = {
            'Computer In': [b'\xF2\x26', b'\x00\x00'],
            'HDMI 1': [b'\x02\x26', b'\x03\x00'],
            'HDMI 2': [b'\x62\x22', b'\x0D\x00'],
            'HDBaseT': [b'\xA2\x2A', b'\x11\x00'],
            'Video': [b'\x62\x27', b'\x01\x00']
        }
        area = qualifier['Area']
        PbyPSourceCmdString = None
        if area and area == 'Left':
            PbyPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', LeftValue[value][0], b'\x01\x00\x15\x23', LeftValue[value][1]])
        elif area and area == 'Right':
            PbyPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', RightValue[value][0], b'\x01\x00\x12\x23', RightValue[value][1]])
        else:
            print('Invalid Command')
        if PbyPSourceCmdString:
            self.__SetHelper('PbyPSource', PbyPSourceCmdString, value, qualifier)

    def UpdatePbyPSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video'
        }

        AreaStates = {
            'Left': [b'\xC1\x26', b'\x15\x23'],
            'Right': [b'\xB5\x27', b'\x12\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PbyPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', area, b'\x02\x00', command, b'\x00\x00'])
        res = self.__UpdateHelper('PbyPSource', PbyPSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PbyPSource', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePbyPSource')

    def SetPbyPSwap(self, value, qualifier):

        PbyPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPSwap', PbyPSwapCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': [b'\x83\xF5', b'\x06\x00'],
            'Natural': [b'\x23\xF6', b'\x00\x00'],
            'Cinema': [b'\xB3\xF7', b'\x01\x00'],
            'Dynamic': [b'\xE3\xF4', b'\x04\x00'],
            'Board(Black)': [b'\xE3\xEF', b'\x20\x00'],
            'Board(Green)': [b'\x73\xEE', b'\x21\x00'],
            'Whiteboard': [b'\x83\xEE', b'\x22\x00'],
            'Daytime': [b'\xE3\xC7', b'\x40\x00'],
            'Dicom Sim': [b'\x73\xC6', b'\x41\x00'],
            'User-1': [b'\xE3\xFB', b'\x10\x00'],
            'User-2': [b'\x73\xFA', b'\x11\x00'],
            'User-3': [b'\x83\xFA', b'\x12\x00']
        }

        PictureModeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\xBA\x30', ValueStateValues[value][1]])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'\x06': 'Standard',
            b'\x00': 'Natural',
            b'\x01': 'Cinema',
            b'\x04': 'Dynamic',
            b'\x20': 'Board(Black)',
            b'\x21': 'Board(Green)',
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
                print('Invalid/Unexpected Response for UpdatePictureMode')

    def SetPIPMainArea(self, value, qualifier):

        ValueStateValues = {
            'Primary': [b'\x32\x22', b'\x00\x00'],
            'Secondary': [b'\xA2\x23', b'\x01\x00']
        }

        PIPMainAreaCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x05\x23', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdatePIPMainArea')

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': [b'\x02\x23', b'\x00\x00'],
            'Top Right': [b'\x92\x22', b'\x01\x00'],
            'Bottom Left': [b'\x62\x22', b'\x02\x00'],
            'Bottom Right': [b'\xF2\x23', b'\x03\x00']
        }

        PIPPositionCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x01\x23', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdatePIPPosition')

    def SetPIPSource(self, value, qualifier):

        PrimaryValue = {
            'Computer In': [b'\xCE\x23', b'\x00\x00'],
            'HDMI 1': [b'\x3E\x23', b'\x03\x00'],
            'HDMI 2': [b'\x5E\x27', b'\x0D\x00'],
            'HDBaseT': [b'\x9E\x2F', b'\x11\x00'],
            'Video': [b'\x5E\x22', b'\x01\x00']
        }

        SecondaryValue = {
            'Computer In': [b'\x46\x23', b'\x00\x00'],
            'HDMI 1': [b'\xB6\x23', b'\x03\x00'],
            'HDMI 2': [b'\xD6\x27', b'\x0D\x00'],
            'HDBaseT': [b'\x16\x2F', b'\x11\x00'],
            'Video': [b'\xD6\x22', b'\x01\x00']
        }
        area = qualifier['Area']
        PbyPSourceCmdString = None
        if area and area == 'Primary':
            PIPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', PrimaryValue[value][0], b'\x01\x00\x04\x23', PrimaryValue[value][1]])
        elif area and area == 'Secondary':
            PIPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', SecondaryValue[value][0], b'\x01\x00\x02\x23', SecondaryValue[value][1]])
        else:
            print('Invalid Command')
        if PIPSourceCmdString:
            self.__SetHelper('PIPSource', PIPSourceCmdString, value, qualifier)

    def UpdatePIPSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Computer In',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x11': 'HDBaseT',
            b'\x01': 'Video'
        }

        AreaStates = {
            'Primary': [b'\xFD\x23', b'\x04\x23'],
            'Secondary': [b'\x75\x23', b'\x02\x23']
        }

        area = AreaStates[qualifier['Area']][0]
        command = AreaStates[qualifier['Area']][1]

        PIPSourceCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', area, b'\x02\x00', command, b'\x00\x00'])
        res = self.__UpdateHelper('PIPSource', PIPSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPSource', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPSource')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\xBA\xD2', b'\x01\x00'],
            'Off': [b'\x2A\xD3', b'\x00\x00']
        }

        PowerCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x00\x60', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6B\xD9', b'\x01\x00'],
            'Off': [b'\xFB\xD8', b'\x00\x00']
        }

        VideoMuteCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value][0], b'\x01\x00\x20\x30', ValueStateValues[value][1]])
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
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        InputStatesIncrement = {
            'Computer In': b'\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'LAN': b'\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xA7\xEA\x04\x00\xD5\x20\x00\x00',
            'Video': b'\x57\xCD\x04\x00\x61\x20\x00\x00'
        }
        InputStatesDecrement = {
            'Computer In': b'\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'LAN': b'\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\x76\xEB\x05\x00\xD5\x20\x00\x00',
            'Video': b'\x86\xCC\x05\x00\x61\x20\x00\x00'
        }
        VolumeCmdString = None
        if value == 'Up':
            VolumeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', InputStatesIncrement[qualifier['Input Type']]])
        elif value == 'Down':
            VolumeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', InputStatesDecrement[qualifier['Input Type']]])
        else:
            print('Invalid Command')
        if VolumeCmdString:
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        InputTypeStates = {
            'Computer In': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'HDBaseT': b'\xBE\xEF\x03\x06\x00\xC1\xEA\x02\x00\xD5\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00'
        }

        VolumeStatusCmdString = InputTypeStates[qualifier['Input Type']]
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateVolumeStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Busy",
            b'\x1F': "Authentication Error"
        }

        if response[0:1] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]]))
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
                if not res:
                    print('No Response')
                    print('Invalid/unexpected response')
                else:
                    res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command')
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
                    if len(res) == 8:
                        self.SetPassword(res, None)
                        return ''
                    else:
                        return self.__CheckResponseForErrors(command, res)
        else:
            print('Device not Authenticated. Inappropriate Command')

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
