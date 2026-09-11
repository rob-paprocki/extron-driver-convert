from extronlib.interface import SerialInterface, EthernetClientInterface


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
            'LM55P1': self.mits_10_1117_P1,
            'LM46P1': self.mits_10_1117_P1,
            'LM55P2': self.mits_10_1117_P2,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'InputResolution': {'Status': {}},
            'PictureReset': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'TilingFrameComp': {'Status': {}},
            'TilingHMonitor': {'Status': {}},
            'TilingMode': {'Status': {}},
            'TilingPosition': {'Status': {}},
            'TilingVMonitor': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self._DeviceID = b'0A'

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'0*'
        elif 1 <= int(value) <= 104:
            value = int(value)
            first = 0
            while value > 26:
                first += 1
                value -= 26
            firstChr = first + 0x30
            secondChr = value + 0x40
            self._DeviceID = '{0}{1}'.format(chr(firstChr), chr(secondChr)).encode()

    def CalculateCheckSum(self, buffer):
        checksum = 0
        for i in buffer:
            checksum ^= i
        return checksum

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Real': b'0E0A\x0202CE0001\x03',
            'Custom': b'0E0A\x0202CE0002\x03',
            'Dynamic': b'0E0A\x0202CE0005\x03',
            'Normal': b'0E0A\x0202CE0006\x03',
            'Full': b'0E0A\x0202CE0007\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        AspectRatioCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Real',
            b'2': 'Custom',
            b'5': 'Dynamic',
            b'6': 'Normal',
            b'7': 'Full'
        }

        buffer = self._DeviceID + b'0C06\x0202CE\x03'
        checksum = self.CalculateCheckSum(buffer)

        AspectRatioCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Audio 1(PC)': b'0E0A\x02022E0001\x03',
            'Audio 2': b'0E0A\x02022E0002\x03',
            'HDMI': b'0E0A\x02022E0004\x03',
            'Display Port': b'0E0A\x02022E0005\x03',
            'Option(OPS Analog)': b'0E0A\x02022E0007\x03',
            'Option(OPS Digital)': b'0E0A\x02022E0008\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        AudioInputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Audio 1(PC)',
            b'2': 'Audio 2',
            b'4': 'HDMI',
            b'5': 'Display Port',
            b'7': 'Option(OPS Analog)',
            b'8': 'Option(OPS Digital)'
        }
        buffer = self._DeviceID + b'0C06\x02022E\x03'
        checksum = self.CalculateCheckSum(buffer)

        AudioInputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('AudioInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioInput')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x02008D0001\x03',
            'Off': b'0E0A\x02008D0002\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        AudioMuteCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'2': 'Off'
        }

        buffer = self._DeviceID + b'0C06\x02008D\x03'
        checksum = self.CalculateCheckSum(buffer)

        AudioMuteCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        buffer = self._DeviceID + b'0E0A\x02001E\x03'
        checksum = self.CalculateCheckSum(buffer)

        AutoImageCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Disable(Off)': b'0E0A\x0202FD0000\x03',
            'CC1': b'0E0A\x0202FD0001\x03',
            'CC2': b'0E0A\x0202FD0002\x03',
            'CC3': b'0E0A\x0202FD0003\x03',
            'CC4': b'0E0A\x0202FD0004\x03',
            'TT1': b'0E0A\x0202FD0005\x03',
            'TT2': b'0E0A\x0202FD0006\x03',
            'TT3': b'0E0A\x0202FD0007\x03',
            'TT4': b'0E0A\x0202FD0008\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        ClosedCaptionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Disable(Off)',
            b'1': 'CC1',
            b'2': 'CC2',
            b'3': 'CC3',
            b'4': 'CC4',
            b'5': 'TT1',
            b'6': 'TT2',
            b'7': 'TT3',
            b'8': 'TT4'
        }
        buffer = self._DeviceID + b'0C06\x0202FD\x03'
        checksum = self.CalculateCheckSum(buffer)

        ClosedCaptionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            80: 'Cooling Fan-1 Abnormality',
            81: 'Cooling Fan-2 Abnormality',
            90: 'Panel Backlight Driver Error',
            161: 'Cooling Abnormality both Fans',
            170: 'Cooling Fan-1 Abnormality and Panel Backlight Driver Error',
            171: 'Cooling Fan-2 Abnormality and Panel Backlight Driver Error',
            251: 'Cooling Abnormality both Fans and Panel Backlight Driver Error'
        }
        buffer = self._DeviceID + b'0A04\x02B1\x03'
        checksum = self.CalculateCheckSum(buffer)

        DeviceStatusCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[10:-3].decode()
                matchResult = True
                if len(value) == 2:
                    value = int(value)
                elif len(value) == 4:
                    value = int(value[0:2]) + int(value[2:4])
                elif len(value) == 6:
                    value = int(value[0:2]) + int(value[2:4]) + int(value[4:6])
                else:
                    matchResult = False

                if matchResult and (value in ValueStateValues.keys()):
                    self.WriteStatus('DeviceStatus', ValueStateValues[value], qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'0E0A\x0200600000\x03',
            'D-SUB': b'0E0A\x0200600001\x03',
            'HDMI': b'0E0A\x0200600003\x03',
            'DVI-D': b'0E0A\x0200600004\x03',
            'YPbPr': b'0E0A\x020060000C\x03',
            'Video(Composite)': b'0E0A\x0200600005\x03',
            'Option': b'0E0A\x0200600008\x03',
            'Display Port': b'0E0A\x0200600009\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        InputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'0': 'No Mean',
            b'1': 'D-SUB',
            b'3': 'HDMI',
            b'4': 'DVI-D',
            b'C': 'YPbPr',
            b'5': 'Video(Composite)',
            b'8': 'Option',
            b'9': 'Display Port'
        }
        buffer = self._DeviceID + b'0C06\x020060\x03'
        checksum = self.CalculateCheckSum(buffer)

        InputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetInputResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'0E0A\x0202DA0001\x03',
            '1024*768': b'0E0A\x0202DA0002\x03',
            '1280*768': b'0E0A\x0202DA0003\x03',
            '1360*768': b'0E0A\x0202DA0004\x03',
            '1400*1050': b'0E0A\x0202DA0005\x03',
            '1680*1050': b'0E0A\x0202DA0006\x03',
            '1600*1200': b'0E0A\x0202DA0007\x03',
            '1920*1200': b'0E0A\x0202DA0008\x03',
            '1366*768': b'0E0A\x0202DA0009\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        InputResolutionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('InputResolution', InputResolutionCmdString, value, qualifier)

    def UpdateInputResolution(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Auto',
            b'2': '1024*768',
            b'3': '1280*768',
            b'4': '1360*768',
            b'5': '1400*1050',
            b'6': '1680*1050',
            b'7': '1600*1200',
            b'8': '1920*1200',
            b'9': '1366*768'
        }

        buffer = self._DeviceID + b'0C06\x0202DA\x03'
        checksum = self.CalculateCheckSum(buffer)

        InputResolutionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('InputResolution', InputResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('InputResolution', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInputResolution')

    def SetPictureReset(self, value, qualifier):

        buffer = self._DeviceID + b'0E0A\x020008\x03'
        checksum = self.CalculateCheckSum(buffer)

        PictureResetCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PictureReset', PictureResetCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        buffer = self._DeviceID + self.PIPInputValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PIPInputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x020273\x03'
        checksum = self.CalculateCheckSum(buffer)

        PIPInputCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPInputNames[res[-4:-3]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        buffer = self._DeviceID + self.PIPModeValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PIPModeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x020272\x03'
        checksum = self.CalculateCheckSum(buffer)

        PIPModeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPModeNames[res[-4:-3]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': b'0E0A\x0202710001\x03',
            'Middle': b'0E0A\x0202710002\x03',
            'Large': b'0E0A\x0202710003\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PIPSizeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Small',
            b'2': 'Middle',
            b'3': 'Large'
        }
        buffer = self._DeviceID + b'0C06\x020271\x03'
        checksum = self.CalculateCheckSum(buffer)

        PIPSizeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'0A0C\x02C203D60001\x03',
            'Off': b'0A0C\x02C203D60004\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PowerCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'4': 'Off',
            b'F': 'Off'
        }
        buffer = self._DeviceID + b'0A06\x0201D6\x03'
        checksum = self.CalculateCheckSum(buffer)

        PowerCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '2': b'0E0A\x0202A30002\x03',
            '3': b'0E0A\x0202A30003\x03',
            '4': b'0E0A\x0202A30004\x03',
            '5': b'0E0A\x0202A30005\x03',
            '6': b'0E0A\x0202A30006\x03',
            '7': b'0E0A\x0202A30007\x03',
            '8': b'0E0A\x0202A30008\x03',
            '9': b'0E0A\x0202A30009\x03',
            '10': b'0E0A\x0202A30010\x03',
            '11': b'0E0A\x0202A30011\x03',
            '12': b'0E0A\x0202A30012\x03',
            '13': b'0E0A\x0202A30013\x03',
            '14': b'0E0A\x0202A30014\x03',
            '15': b'0E0A\x0202A30015\x03',
            '16': b'0E0A\x0202A30016\x03',
            '17': b'0E0A\x0202A30017\x03',
            '18': b'0E0A\x0202A30018\x03',
            '19': b'0E0A\x0202A30019\x03',
            '20': b'0E0A\x0202A30020\x03',
            '21': b'0E0A\x0202A30021\x03',
            '22': b'0E0A\x0202A30022\x03',
            '23': b'0E0A\x0202A30023\x03',
            '24': b'0E0A\x0202A30024\x03',
            '25': b'0E0A\x0202A30025\x03',
            '26': b'0E0A\x0202A30026\x03',
            '27': b'0E0A\x0202A30027\x03',
            '28': b'0E0A\x0202A30028\x03',
            '29': b'0E0A\x0202A30029\x03',
            '30': b'0E0A\x0202A30030\x03',
            '31': b'0E0A\x0202A30031\x03',
            '32': b'0E0A\x0202A30032\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PresetRecallCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x0202A3\x03'
        checksum = self.CalculateCheckSum(buffer)

        PresetRecallCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        if res:
            try:
                value = str(int(res[-5:-3], 16))
                self.WriteStatus('PresetRecall', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdatePresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '2': b'0E0A\x0202A20002\x03',
            '3': b'0E0A\x0202A20003\x03',
            '4': b'0E0A\x0202A20004\x03',
            '5': b'0E0A\x0202A20005\x03',
            '6': b'0E0A\x0202A20006\x03',
            '7': b'0E0A\x0202A20007\x03',
            '8': b'0E0A\x0202A20008\x03',
            '9': b'0E0A\x0202A20009\x03',
            '10': b'0E0A\x0202A20010\x03',
            '11': b'0E0A\x0202A20011\x03',
            '12': b'0E0A\x0202A20012\x03',
            '13': b'0E0A\x0202A20013\x03',
            '14': b'0E0A\x0202A20014\x03',
            '15': b'0E0A\x0202A20015\x03',
            '16': b'0E0A\x0202A20016\x03',
            '17': b'0E0A\x0202A20017\x03',
            '18': b'0E0A\x0202A20018\x03',
            '19': b'0E0A\x0202A20019\x03',
            '20': b'0E0A\x0202A20020\x03',
            '21': b'0E0A\x0202A20021\x03',
            '22': b'0E0A\x0202A20022\x03',
            '23': b'0E0A\x0202A20023\x03',
            '24': b'0E0A\x0202A20024\x03',
            '25': b'0E0A\x0202A20025\x03',
            '26': b'0E0A\x0202A20026\x03',
            '27': b'0E0A\x0202A20027\x03',
            '28': b'0E0A\x0202A20028\x03',
            '29': b'0E0A\x0202A20029\x03',
            '30': b'0E0A\x0202A20030\x03',
            '31': b'0E0A\x0202A20031\x03',
            '32': b'0E0A\x0202A20032\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        PresetSaveCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def UpdatePresetSave(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x0202A2\x03'
        checksum = self.CalculateCheckSum(buffer)

        PresetSaveCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        if res:
            try:
                value = str(int(res[-5:-3], 16))
                self.WriteStatus('PresetSave', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdatePresetSave')

    def SetTilingFrameComp(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0202D50002\x03',
            'Off': b'0E0A\x0202D50001\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        TilingFrameCompCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('TilingFrameComp', TilingFrameCompCmdString, value, qualifier)

    def UpdateTilingFrameComp(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'1': 'Off'
        }
        buffer = self._DeviceID + b'0C06\x0202D5\x03'
        checksum = self.CalculateCheckSum(buffer)

        TilingFrameCompCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('TilingFrameComp', TilingFrameCompCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('TilingFrameComp', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTilingFrameComp')

    def SetTilingHMonitor(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 5,
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            result = value.encode()
            buffer = b''.join([self._DeviceID, b'0E0A\x0202D0000', result, b'\x03'])
            checksum = self.CalculateCheckSum(buffer)

            TilingHMonitorCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
            self.__SetHelper('TilingHMonitor', TilingHMonitorCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilingHMonitor')

    def UpdateTilingHMonitor(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 5,
        }
        buffer = self._DeviceID + b'0C06\x0202D0\x03'
        checksum = self.CalculateCheckSum(buffer)

        TilingHMonitorCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('TilingHMonitor', TilingHMonitorCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-3])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('TilingHMonitor', str(value), qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTilingHMonitor')

    def SetTilingMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0202D30002\x03',
            'Off': b'0E0A\x0202D30001\x03'
        }
        buffer = self._DeviceID + ValueStateValues[value]
        checksum = self.CalculateCheckSum(buffer)

        TilingModeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        self.__SetHelper('TilingMode', TilingModeCmdString, value, qualifier)

    def UpdateTilingMode(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'1': 'Off'
        }
        buffer = self._DeviceID + b'0C06\x0202D3\x03'
        checksum = self.CalculateCheckSum(buffer)

        TilingModeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('TilingMode', TilingModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('TilingMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTilingMode')

    def SetTilingPosition(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 65535
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = '{:04X}'.format(value).encode()
            buffer = b''.join([self._DeviceID, b'0E0A\x0202D2', result, b'\x03'])
            checksum = self.CalculateCheckSum(buffer)

            TilingPositionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
            self.__SetHelper('TilingPosition', TilingPositionCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilingPosition')

    def UpdateTilingPosition(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x0202D2\x03'
        checksum = self.CalculateCheckSum(buffer)

        TilingPositionCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('TilingPosition', TilingPositionCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-7:-3], 16)
                self.WriteStatus('TilingPosition', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTilingPosition')

    def SetTilingVMonitor(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 5,
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            result = value.encode()
            buffer = b''.join([self._DeviceID, b'0E0A\x0202D1000', result, b'\x03'])
            checksum = self.CalculateCheckSum(buffer)

            TilingVMonitorCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
            self.__SetHelper('TilingVMonitor', TilingVMonitorCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilingVMonitor')

    def UpdateTilingVMonitor(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 5,
        }
        buffer = self._DeviceID + b'0C06\x0202D1\x03'
        checksum = self.CalculateCheckSum(buffer)

        TilingVMonitorCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('TilingVMonitor', TilingVMonitorCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-3])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('TilingVMonitor', str(value), qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTilingVMonitor')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = '{:02X}'.format(value).encode()
            buffer = b''.join([self._DeviceID, b'0E0A\x02006200', result, b'\x03'])
            checksum = self.CalculateCheckSum(buffer)

            VolumeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        buffer = self._DeviceID + b'0C06\x020062\x03'
        checksum = self.CalculateCheckSum(buffer)

        VolumeCmdString = b''.join([b'\x01', buffer, checksum.to_bytes(1, 'big'), b'\r'])
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-5:-3], 16)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) == 7:
            print('{0} : Error Occured'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == b'0*':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'0*':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

    def mits_10_1117_P2(self):

        self.PIPModeValues = {
            'Off': b'0E0A\x0202720001\x03',
            'PIP': b'0E0A\x0202720002\x03'
        }
        self.PIPModeNames = {
            b'1': 'Off',
            b'2': 'PIP'
        }
        self.PIPInputValues = {
            'No mean': b'0E0A\x0202730000\x03',
            'D-SUB': b'0E0A\x0202730001\x03',
            'HDMI': b'0E0A\x0202730003\x03',
            'DVI-D': b'0E0A\x0202730004\x03',
            'Option': b'0E0A\x0202730008\x03',
            'Display Port': b'0E0A\x0202730009\x03'
        }
        self.PIPInputNames = {
            b'0': 'No mean',
            b'1': 'D-SUB',
            b'3': 'HDMI',
            b'4': 'DVI-D',
            b'8': 'Option',
            b'9': 'Display Port'
        }

    def mits_10_1117_P1(self):

        self.PIPModeValues = {
            'Off': b'0E0A\x0202720001\x03',
            'PIP': b'0E0A\x0202720002\x03',
            'POP': b'0E0A\x0202720003\x03',
            'SBS Aspect': b'0E0A\x0202720005\x03',
            'SBS Full': b'0E0A\x0202720006\x03'
        }
        self.PIPModeNames = {
            b'1': 'Off',
            b'2': 'PIP',
            b'3': 'POP',
            b'5': 'SBS Aspect',
            b'6': 'SBS Full'
        }
        self.PIPInputValues = {
            'No mean': b'0E0A\x0202730000\x03',
            'D-SUB': b'0E0A\x0202730001\x03',
            'HDMI': b'0E0A\x0202730003\x03',
            'DVI-D': b'0E0A\x0202730004\x03',
            'Video(Composite)': b'0E0A\x0202730005\x03',
            'Option': b'0E0A\x0202730008\x03',
            'Display Port': b'0E0A\x0202730009\x03'
        }
        self.PIPInputNames = {
            b'0': 'No mean',
            b'1': 'D-SUB',
            b'3': 'HDMI',
            b'4': 'DVI-D',
            b'5': 'Video(Composite)',
            b'8': 'Option',
            b'9': 'Display Port'
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
