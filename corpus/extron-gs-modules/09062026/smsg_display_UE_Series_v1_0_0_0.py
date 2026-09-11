from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
        self._DeviceID = 1

        self.Models = {
            'UE46A': self.smsg_10_2594_1,
            'UE55A': self.smsg_10_2594_1,
            'UE46C': self.smsg_10_2594_0,
            'UE55C': self.smsg_10_2594_0,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'ChannelDiscrete': {'Parameters': ['Tuner Mode', 'Signal Type'], 'Status': {}},
            'ChannelStep': {'Status': {}},
            'ChannelStatus': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'SignalTypeStatus': {'Status': {}},
            'TunerModeStatus': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x15](?P<value>[\x00-\xFF])(?P<checksum>[\x00-\xFF])'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x13](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x0A][\x41][\x17](?P<country>[\x00-\xFF])(?P<signal>[\x00-\x01])(?P<aircable>[\x00-\x01])(?P<chhigh>[\x00-\xFF])(?P<chlow>[\x00-\xFF])(?P<selminor>[\x00-\x01])(?P<minorchhigh>[\x00-\xFF])(?P<minorchlow>[\x00-\xFF])(?P<checksum>[\x00-\xFF])'), self.__MatchChannelStatus, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x5F](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x14](?P<value>[\x00-\x60])(?P<checksum>[\x00-\xFF])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x70](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x40](?P<value>[\x00-\x60])(?P<checksum>[\x00-\xFF])'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x3C](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x43](?P<value>[\x01-\x04])(?P<checksum>[\x00-\xFF])'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x42](?P<value>[\x00-\x09])(?P<checksum>[\x00-\xFF])'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x11](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x5D](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x84](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\\x5C](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x41][\x12](?P<value>[\x00-\x64])(?P<checksum>[\x00-\xFF])'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'[\xAA][\xFF](?P<DeviceID>[\x00-\xFF])[\x03][\x4E](?P<command>[\x00-\xFF])(?P<error>[\x00-\xFF])(?P<checksum>[\x00-\xFF])'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = 254
        elif int(value) == 0:
            self._DeviceID = 255
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)        

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            '16:9': 0x10,
            '4:3': 0x18,
            'Auto Wide': 0x00,
            'Zoom': 0x04,
            'Zoom 1': 0x05,
            'Zoom 2': 0x06,
            'Just Scan': 0x09,
            'Wide Zoom': 0x31,
            'Wide Fit': 0x0C,
            'Custom': 0x0D,
            'Smart View 1': 0x0E,
            'Smart View 2': 0x0F,
            }
        CKS = int(hex(0x16 + self._DeviceID + AspectRatioValues[value])[-2:], 16)
        AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x15, self._DeviceID, 0x01, AspectRatioValues[value], CKS)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CKS = int(hex(0x15 + self._DeviceID)[-2:], 16)
        AspectCmdString = pack('>BBBBB', 0xAA, 0x15, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
            '\x10': '16:9',
            '\x18': '4:3',
            '\x00': 'Auto Wide',
            '\x04': 'Zoom',
            '\x05': 'Zoom 1',
            '\x06': 'Zoom 2',
            '\x09': 'Just Scan',
            '\x31': 'Wide Zoom',
            '\x0C': 'Wide Fit',
            '\x0D': 'Custom',
            '\x0E': 'Smart View 1',
            '\x0F': 'Smart View 2',
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = AspectRatioNames[match.group('value').decode()]
            self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x14 + self._DeviceID + AudioMuteValues[value])[-2:], 16)
        AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, self._DeviceID, 0x01, AudioMuteValues[value], CKS)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        CKS = int(hex(0x13 + self._DeviceID)[-2:], 16)
        AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteNames = {
            '\x00': 'Off',
            '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = AudioMuteNames[match.group('value').decode()]
            self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        CKS = int(hex(0x3E + self._DeviceID)[-2:], 16)
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, CKS)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ButtonLockValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x60 + self._DeviceID + ButtonLockValues[value])[-2:], 16)
        ButtonLockCmdString = pack('>BBBBBB', 0xAA, 0x5F, self._DeviceID, 0x01, ButtonLockValues[value], CKS)
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        CKS = int(hex(0x5F + self._DeviceID)[-2:], 16)
        ButtonLockCmdString = pack('>BBBBB', 0xAA, 0x5F, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ButtonLockNames = {
           '\x00': 'Off',
           '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = ButtonLockNames[match.group('value').decode()]
            self.WriteStatus('ButtonLock', value, None)

    def SetChannelDiscrete(self, value, qualifier):
        SignalTypeValues = {
            'Analog' : 0x00,
            'Digital' : 0x01
            }
        TunerModeValues = {
            'Air' : 0x00,
            'Cable' : 0x01
            }

        if value:
            signaltype = SignalTypeValues[qualifier['Signal Type']]
            tunermode = TunerModeValues[qualifier['Tuner Mode']]
            country = 0x01
            if '-' in value:
                selminor = 0x01
            else:
                selminor = 0x00

            if selminor:
                index = 0
                for i in value:
                    if i != '-':
                        index += 1
                    else:
                        break
                majorChannel = int(value[:index])
                minorChannel = int(value[index+1:])
            else:
                majorChannel = int(value)
                minorChannel = 0

            chhigh = majorChannel >> 8
            chlow = majorChannel % 256
            minorchhigh = minorChannel >> 8
            minorchlow = minorChannel % 256

            CKS = int(hex(0x1F + self.DeviceID + country + signaltype + tunermode + chhigh + chlow + selminor + minorchhigh + minorchlow)[-2:], 16)
            ChannelCmdString = pack('>BBBBBBBBBBBBB', 0xAA, 0x17, self.DeviceID, 0x08, country, signaltype, tunermode, chhigh, chlow, selminor, minorchhigh, minorchlow, CKS)
            self.__SetHelper('SetChannelDiscrete', ChannelCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ChannelStepValues = {
            'Up': 0x00,
            'Down': 0x01
            }
        CKS = int(hex(0x62 + self._DeviceID + ChannelStepValues[value])[-2:], 16)
        ChannelStepCmdString = pack('>BBBBBB', 0xAA, 0x61, self._DeviceID, 0x01, ChannelStepValues[value], CKS)
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def UpdateChannelStatus(self, value, qualifier):

        CKS = int(hex(0x17 + self._DeviceID)[-2:], 16)
        ChannelStatusCmdString = pack('>BBBBB', 0xAA, 0x17, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('ChannelStatus', ChannelStatusCmdString, value, qualifier)

    def __MatchChannelStatus(self, match, tag):

        SignalNames = {
            '\x00': 'Analog',
            '\x01': 'Digital'
            }
        TunerNames = {
            '\x00': 'Air',
            '\x01': 'Cable'
            }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            signalValue = SignalNames[match.group('signal').decode()]
            tunerValue = TunerNames[match.group('aircable').decode()]

            chhigh = ord(match.group('chhigh').decode('iso-8859-1'))
            chlow = ord(match.group('chlow').decode('iso-8859-1'))

            if match.group('selminor').decode() == '\x01':
                minorchhigh = ord(match.group('minorchhigh').decode('iso-8859-1'))
                minorchlow = ord(match.group('minorchlow').decode('iso-8859-1'))
                channelValue = str((chhigh << 8) + chlow) + '-' + str((minorchhigh << 8) + minorchlow)
            elif match.group('selminor').decode() == '\x00':
                channelValue = str((chhigh << 8) + chlow)

            self.WriteStatus('ChannelStatus', channelValue, None)
            self.WriteStatus('SignalTypeStatus', signalValue, None)
            self.WriteStatus('TunerModeStatus', tunerValue, None)

    def UpdateSignalTypeStatus(self, value, qualifier):
        self.UpdateChannelStatus(None, None)

    def UpdateTunerModeStatus(self, value, qualifier):
        self.UpdateChannelStatus(None, None)

    def SetInput(self, value, qualifier):

        CKS = int(hex(0x15 + self._DeviceID + self.Inputs[value])[-2:], 16)
        InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, self.Inputs[value], CKS)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CKS = int(hex(0x14 + self._DeviceID)[-2:], 16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = self.InputStates[match.group('value').decode()]
            self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x71 + self._DeviceID + OnScreenDisplayValues[value])[-2:], 16)
        OnScreenDisplayCmdString = pack('>BBBBBB', 0xAA, 0x70, self._DeviceID, 0x01, OnScreenDisplayValues[value], CKS)
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        CKS = int(hex(0x70 + self._DeviceID)[-2:], 16)
        OnScreenDisplayCmdString = pack('>BBBBB', 0xAA, 0x70, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        OnScreenDisplayNames = {
           '\x00': 'Off',
           '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = OnScreenDisplayNames[match.group('value').decode()]
            self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):

        CKS = int(hex(0x41 + self._DeviceID + self.PIPInputs[value])[-2:], 16)
        PIPInputCmdString = pack('>BBBBBB', 0xAA, 0x40, self._DeviceID, 0x01, self.PIPInputs[value], CKS)
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        CKS = int(hex(0x40 + self._DeviceID)[-2:], 16)
        PIPInputCmdString = pack('>BBBBB', 0xAA, 0x40, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = self.PIPInputStates[match.group('value').decode()]
            self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x3D + self._DeviceID + PIPModeValues[value])[-2:], 16)
        PIPModeCmdString = pack('>BBBBBB', 0xAA, 0x3C, self._DeviceID, 0x01, PIPModeValues[value], CKS)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        CKS = int(hex(0x3C + self._DeviceID)[-2:], 16)
        PIPModeCmdString = pack('>BBBBB', 0xAA, 0x3C, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeNames = {
            '\x00': 'Off',
            '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = PIPModeNames[match.group('value').decode()]
            self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionValues = {
            'Upper Left': 0x01,
            'Upper Right': 0x02,
            'Lower Right': 0x03,
            'Lower Left': 0x04
            }
        CKS = int(hex(0x44 + self._DeviceID + PIPPositionValues[value])[-2:], 16)
        PIPPositionCmdString = pack('>BBBBBB', 0xAA, 0x43, self._DeviceID, 0x01, PIPPositionValues[value], CKS)
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        CKS = int(hex(0x43 + self._DeviceID)[-2:], 16)
        PIPPositionCmdString = pack('>BBBBB', 0xAA, 0x43, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionNames = {
            '\x01': 'Upper Left',
            '\x02': 'Upper Right',
            '\x03': 'Lower Right',
            '\x04': 'Lower Left'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = PIPPositionNames[match.group('value').decode()]
            self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        PIPSizeValues = {
            'Medium': 0x06,
            'Small': 0x08,
            'Wide': 0x04,
            'Side by Side': 0x05,
            'Right Side': 0x09,
            'PIP Off': 0x00,
            }
        CKS = int(hex(0x43 + self._DeviceID + PIPSizeValues[value])[-2:], 16)
        PIPSizeCmdString = pack('>BBBBBB', 0xAA, 0x42, self._DeviceID, 0x01, PIPSizeValues[value], CKS)
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        CKS = int(hex(0x42 + self._DeviceID)[-2:], 16)
        PIPSizeCmdString = pack('>BBBBB', 0xAA, 0x42, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeNames = {
           '\x06': 'Medium',
           '\x08': 'Small',
           '\x04': 'Wide',
           '\x05': 'Side by Side',
           '\x09': 'Right Side',
           '\x00': 'PIP Off',
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = PIPSizeNames[match.group('value').decode()]
            self.WriteStatus('PIPSize', value, None)

    def SetPower(self, value, qualifier):

        PowerValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x12 + self._DeviceID + PowerValues[value])[-2:], 16)
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, PowerValues[value], CKS)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CKS = int(hex(0x11 + self._DeviceID)[-2:], 16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerNames = {
           '\x00': 'Off',
           '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = PowerNames[match.group('value').decode()]
            self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        SafetyLockValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x5E + self._DeviceID + SafetyLockValues[value])[-2:], 16)
        SafetyLockCmdString = pack('>BBBBBB', 0xAA, 0x5D, self._DeviceID, 0x01, SafetyLockValues[value], CKS)
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        CKS = int(hex(0x5D + self._DeviceID)[-2:], 16)
        SafetyLockCmdString = pack('>BBBBB', 0xAA, 0x5D, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        SafetyLockNames = {
           '\x00': 'Off',
           '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = SafetyLockNames[match.group('value').decode()]
            self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        VideoWallValues = {
            'Off': 0x00,
            'On': 0x01
            }
        CKS = int(hex(0x85 + self._DeviceID + VideoWallValues[value])[-2:], 16)
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self._DeviceID, 0x01, VideoWallValues[value], CKS)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        CKS = int(hex(0x84 + self._DeviceID)[-2:], 16)
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        VideoWallNames = {
           '\x00': 'Off',
           '\x01': 'On'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = VideoWallNames[match.group('value').decode()]
            self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        VideoWallModeValues = {
            'Natural': 0x00,
            'Full': 0x01
            }
        CKS = int(hex(0x5D + self._DeviceID + VideoWallModeValues[value])[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self._DeviceID, 0x01, VideoWallModeValues[value], CKS)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        CKS = int(hex(0x5C + self._DeviceID)[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        VideoWallModeNames = {
           '\x00': 'Natural',
           '\x01': 'Full'
           }
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = VideoWallModeNames[match.group('value').decode()]
            self.WriteStatus('VideoWallMode', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            CKS = int(hex(0x13 + self._DeviceID + value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self._DeviceID, 0x01, value, CKS)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        CKS = int(hex(0x12 + self._DeviceID)[-2:], 16)
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        if self._DeviceID == ord(match.group('DeviceID').decode()):
            value = ord(match.group('value').decode())
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        self.Send(commandstring)

    def __MatchError(self, match, tag):

        errorstring = 'DeviceID: {0}, Command: {1}, Error: {2}'.format(match.group('DeviceID'), match.group('command'), match.group('error'))
        print(errorstring)
  
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_2594_1(self):

        self.Inputs = {
            'PC'            : 0x14,
            'DVI'           : 0x18,
            'AV'            : 0x0C,
            'Component'     : 0x08,
            'MagicInfo'     : 0x20,
            'RF TV'         : 0x30,
            'DTV'           : 0x40,
            'HDMI 1'        : 0x21,
            'DisplayPort'   : 0x25,
            'MagicInfo Lite': 0x60,
            }
            
        self.InputStates = {
            '\x14' : 'PC', 
            '\x18' : 'DVI', 
            '\x1F' : 'DVI',
            '\x0C' : 'AV', 
            '\x08' : 'Component', 
            '\x20' : 'MagicInfo', 
            '\x30' : 'RF TV', 
            '\x40' : 'DTV', 
            '\x21' : 'HDMI 1',
            '\x22' : 'HDMI 1',
            '\x25' : 'DisplayPort', 
            '\x60' : 'MagicInfo Lite'
        }

        self.PIPInputs = {
            'PC'            : 0x14,
            'DVI'           : 0x18,
            'AV'            : 0x0C,
            'Component'     : 0x08,
            'RF TV'         : 0x30,
            'DTV'           : 0x40,
            'HDMI 1'        : 0x21,
            'DisplayPort'   : 0x25,
            }
            
        self.PIPInputStates = {
            '\x14' : 'PC', 
            '\x18' : 'DVI', 
            '\x1F' : 'DVI',
            '\x0C' : 'AV', 
            '\x08' : 'Component', 
            '\x30' : 'RF TV', 
            '\x40' : 'DTV', 
            '\x21' : 'HDMI 1',
            '\x22' : 'HDMI 1',
            '\x25' : 'DisplayPort', 
        }

    def smsg_10_2594_0(self):
    
        self.Inputs = {
            'PC': 0x14,
            'DVI': 0x18,
            'AV': 0x0C,
            'Component': 0x08,
            'MagicInfo': 0x20,
            'RF TV': 0x30,
            'DTV': 0x40,
            'DisplayPort': 0x25,
            'MagicInfo Lite': 0x60,
        }

        self.InputStates = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x1F': 'DVI',  # DVI_Video
            '\x0C': 'AV',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x30': 'RF TV',
            '\x40': 'DTV',
            '\x25': 'DisplayPort',
            '\x60': 'MagicInfo Lite'  # Retained from v1_0_2
        }

        self.PIPInputs = {
            'PC': 0x14,
            'DVI': 0x18,
            'AV': 0x0C,
            'Component': 0x08,
            'RF TV': 0x30,
            'DTV': 0x40,
            'DisplayPort': 0x25,
        }

        self.PIPIputStates = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x1F': 'DVI',  # DVI_Video
            '\x0C': 'AV',
            '\x08': 'Component',
            '\x30': 'RF TV',
            '\x40': 'DTV',
            '\x25': 'DisplayPort',
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