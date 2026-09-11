from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
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
        self.Models = {
            'MGP 464': self.extr_18_28_464_Normal,
            'MGP 464 Pro DI': self.extr_18_28_464_Pro,
            'MGP 464 Pro': self.extr_18_28_464_Pro,
            'MGP 464 HD-SDI': self.extr_18_28_464_Normal,
            'MGP 464 DI': self.extr_18_28_464_Normal,
            'MGP 462': self.extr_18_28_462_Normal,
            'MGP 462xi DI': self.extr_18_28_462_Normal,
            'MGP 462xi HD-SDI': self.extr_18_28_462_Normal,
            'MGP 464 Pro 3G-SDI': self.extr_18_28_464_Pro,
            'MGP 462 Pro': self.extr_18_28_462_Pro,
            'MGP 462 Pro DI': self.extr_18_28_462_Pro,
            'MGP 462 Pro 3G-SDI': self.extr_18_28_462_Pro,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Parameters': ['Window'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Parameters': ['Window'], 'Status': {}},
            'FreezeAllWindows': {'Status': {}},
            'HDCPSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'ImageHorizontalShift': {'Parameters': ['Window'], 'Status': {}},
            'ImageHorizontalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'ImageHorizontalSize': {'Parameters': ['Window'], 'Status': {}},
            'ImageHorizontalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
            'ImageVerticalShift': {'Parameters': ['Window'], 'Status': {}},
            'ImageVerticalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'ImageVerticalSize': {'Parameters': ['Window'], 'Status': {}},
            'ImageVerticalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
            'ImageZoom': {'Parameters': ['Window'], 'Status': {}},
            'Input': {'Parameters': ['Window'], 'Status': {}},
            'InputPresetRecall': {'Parameters': ['Window'], 'Status': {}},
            'InputPresetSave': {'Parameters': ['Window'], 'Status': {}},
            'MuteAllWindows': {'Status': {}},
            'RefreshRateStatus': {'Status': {}},
            'ResolutionAndRefreshRate': {'Parameters': ['Rate'], 'Status': {}},
            'ResolutionStatus': {'Status': {}},
            'SignalSelect': {'Parameters': ['Input'], 'Status': {}},
            'Temperature': {'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalShift': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowPresetRecall': {'Parameters': ['Type'], 'Status': {}},
            'WindowPresetSave': {'Status': {}},
            'WindowPresetRecalledStatusPro': {'Status': {}},
            'WindowPresetRecalledStatusNormal': {'Status': {}},
            'WindowVerticalShift': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowZoom': {'Parameters': ['Window'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'(\d)Frz(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'HdcpI00\*(0|1|2)(0|1|2)(0|1|2)(0|1|2)(0|1|2)\r\n'), self.__MatchHDCPSignalStatus, None)
            self.AddMatchString(compile(b'(\d)Ihp(\d{4})\r\n'), self.__MatchImageHorizontalShiftStatus, None)
            self.AddMatchString(compile(b'(\d)Ihs(\d{4})\r\n'), self.__MatchImageHorizontalSizeStatus, None)
            self.AddMatchString(compile(b'(\d)Ivp(\d{4})\r\n'), self.__MatchImageVerticalShiftStatus, None)
            self.AddMatchString(compile(b'(\d)Ivs(\d{4})\r\n'), self.__MatchImageVerticalSizeStatus, None)
            self.AddMatchString(compile(b'Out(\d) In(\d{2})\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'Rte([0-2][0-9])\*(10|11|\d)\r\n'), self.__MatchResolutionStatus, None)
            self.AddMatchString(compile(b'(\d{2})Typ([1-7])\r\n'), self.__MatchSignalSelect, None)
            self.AddMatchString(compile(b'Sts20\*(\d+\.\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Tst([01][0-9])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'(\d)Blk(0|1)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'(\d)Whp(\d{4})\r\n'), self.__MatchWindowHorizontalShiftStatus, None)
            self.AddMatchString(compile(b'(\d)Whs(\d{4})\r\n'), self.__MatchWindowHorizontalSizeStatus, None)
            self.AddMatchString(compile(b'Rpr[1-2]\*(\d{3})\r\n'), self.__MatchWindowPresetRecalledStatus, None)
            self.AddMatchString(compile(b'(\d)Wvp(\d{4})\r\n'), self.__MatchWindowVerticalShiftStatus, None)
            self.AddMatchString(compile(b'(\d)Wvs(\d{4})\r\n'), self.__MatchWindowVerticalSizeStatus, None)

            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchErrors, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

    def __MatchLoginAdmin(self, match, tag):
        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):
        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def SetVerbose(self, value, qualifier):
        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):
        self.VerboseDisabled = False
        self.OnConnected()

    def SetAutoImage(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('AutoImage', '55*{0}#'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off',
        }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1).decode()], None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'Off': '0',
            'On': '1',
        }
        window = qualifier['Window']
        if 0 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('Freeze', '{0}*{1}f'.format(window, FreezeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        window = qualifier['Window']
        if 0 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('Freeze', '{0}F'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, qualifier):
        FreezeName = {
            '0': 'Off',
            '1': 'On',
        }
        value = FreezeName[match.group(2).decode()]
        window = match.group(1).decode()
        if window == '0':
            for i in range(1, self.NumberOfWindow + 1):
                self.WriteStatus('Freeze', value, {'Window': str(i)})
        self.WriteStatus('Freeze', value, {'Window': window})

    def SetFreezeAllWindows(self, value, qualifier):

        FreezeValues = {
            'Off': '0',
            'On': '1'
        }
        self.__SetHelper('FreezeAllWindows', '0*{0}F'.format(FreezeValues[value]), value, qualifier)

    def UpdateHDCPSignalStatus(self, value, qualifier):

        HDCPSignalStatusCmdString = b'\x1BIHDCP\r\n'
        self.__UpdateHelper('HDCPSignalStatus', HDCPSignalStatusCmdString, value, qualifier)

    def __MatchHDCPSignalStatus(self, match, tag):

        InputStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
        }

        HDCPSignalStateValues = {
            '0': 'No source or sink detected',
            '1': 'Source or sink with HDCP detected',
            '2': 'No source or sink detected with HDCP'
        }

        for i in range(1, 6):
            value = HDCPSignalStateValues[match.group(i).decode()]
            self.WriteStatus('HDCPSignalStatus', value, {'Input': InputStateValues[str(i)]})

    def SetImageHorizontalShift(self, value, qualifier):

        ImageHorizontalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('ImageHorizontalShift', '2*{0}*{1}H'.format(window, ImageHorizontalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageHorizontalShift')

    def UpdateImageHorizontalShiftStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageHorizontalShiftStatus', '2*{0}H'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageHorizontalShiftStatus')

    def __MatchImageHorizontalShiftStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('ImageHorizontalShiftStatus', value, {'Window': window})

    def SetImageHorizontalSize(self, value, qualifier):

        ImageHorizontalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('ImageHorizontalSize', '2*{0}*{1}:'.format(window, ImageHorizontalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageHorizontalSize')

    def UpdateImageHorizontalSizeStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageHorizontalSizeStatus', '2*{0}:'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageHorizontalSizeStatus')

    def __MatchImageHorizontalSizeStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('ImageHorizontalSizeStatus', value, {'Window': window})

    def SetImageVerticalShift(self, value, qualifier):

        ImageVerticalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('ImageVerticalShift', '2*{0}*{1}/'.format(window, ImageVerticalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageVerticalShift')

    def UpdateImageVerticalShiftStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageVerticalShiftStatus', '2*{0}/'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageVerticalShiftStatus')

    def __MatchImageVerticalShiftStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('ImageVerticalShiftStatus', value, {'Window': window})

    def SetImageVerticalSize(self, value, qualifier):

        ImageVerticalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('ImageVerticalSize', '2*{0}*{1};'.format(window, ImageVerticalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageVerticalSize')

    def UpdateImageVerticalSizeStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageVerticalSizeStatus', '2*{0};'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageVerticalSizeStatus')

    def __MatchImageVerticalSizeStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('ImageVerticalSizeStatus', value, {'Window': window})

    def SetImageZoom(self, value, qualifier):

        ZoomValue = {
            'In': '+',
            'Out': '-',
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('ImageZoom', '2*{0}*{1}{2}'.format(window, ZoomValue[value], '{'), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageZoom')

    def SetInput(self, value, qualifier):
        WindowValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0'
        }
        window = WindowValues[qualifier['Window']]
        if 0 <= int(window) <= self.NumberOfWindow and 1 <= int(value) <= self.NumberOfInput:
            self.__SetHelper('Input', '{0}*{1}!'.format(value, window), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        WindowValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': '0'
        }
        window = WindowValues[qualifier['Window']]
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('Input', '{0}!'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, qualifier):

        WindowNames = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '0': 'All'
        }
        window = WindowNames[match.group(1).decode()]
        value = str(int(match.group(2).decode()))
        breakaway = False

        self.WriteStatus('Input', value, {'Window': WindowNames[match.group(1).decode()]})
        if window != 'All':
            for i in range(1, self.NumberOfWindow + 1):
                if str(i) not in window and self.ReadStatus('Input', {'Window': window}) != self.ReadStatus('Input', {'Window': str(i)}):
                    self.WriteStatus('Input', '0', {'Window': 'All'})
                    breakaway = True
            if not breakaway:
                self.WriteStatus('Input', value, {'Window': 'All'})
        elif window == 'All':
            for i in range(1, self.NumberOfWindow + 1):
                self.WriteStatus('Input', value, {'Window': str(i)})

    def SetInputPresetRecall(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 1 <= int(value) <= 128:
            self.__SetHelper('InputPresetRecall', '3*{0}*{1}.'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 1 <= int(value) <= 128:
            self.__SetHelper('InputPresetSave', '3*{0}*{1},'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def SetMuteAllWindows(self, value, qualifier):

        MuteAllWindowsValues = {
            'Off': '0',
            'On': '1'
        }
        self.__SetHelper('MuteAllWindows', '0*{0}B'.format(MuteAllWindowsValues[value]), value, qualifier)

    def UpdateRefreshRateStatus(self, value, qualifier):

        self.UpdateResolutionStatus(value, qualifier)

    def SetResolutionAndRefreshRate(self, value, qualifier):

        rate = qualifier['Rate']
        self.__SetHelper('ResolutionAndRefreshRate', '{0}*{1}='.format(self.ResolutionValue[value], self.RateValue[rate]), value, qualifier)

    def UpdateResolutionStatus(self, value, qualifier):

        self.__UpdateHelper('ResolutionStatus', '=', value, qualifier)

    def __MatchResolutionStatus(self, match, qualifier):

        resolution = self.ResolutionState[match.group(1).decode()]
        self.WriteStatus('ResolutionStatus', resolution, None)

        rate = self.RateState[match.group(2).decode()]
        self.WriteStatus('RefreshRateStatus', rate, None)

    def SetSignalSelect(self, value, qualifier):

        SignalSelectValue = {
            'RGB': '1"',
            'YUV-HD': '2"',
            'RGBcvS': '3"',
            'YUVi': '4"',
            'S-Video': '5"',
            'Composite Video': '6"',
            'DVI/HD-SDI': '7"',
        }
        input = qualifier['Input']
        if 1 <= int(input) <= self.NumberOfInput:
            self.__SetHelper('SignalSelect', '{0}*{1}\x5C'.format(input, SignalSelectValue[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalSelect')

    def UpdateSignalSelect(self, value, qualifier):

        input = qualifier['Input']
        if 1 <= int(input) <= self.NumberOfInput:
            self.__UpdateHelper('SignalSelect', '{0}*\x5C'.format(input), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalSelect')

    def __MatchSignalSelect(self, match, qualifier):
        SignalSelectState = {
            '1': 'RGB',
            '2': 'YUV-HD',
            '3': 'RGBcvS',
            '4': 'YUVi',
            '5': 'S-Video',
            '6': 'Composite Video',
            '7': 'DVI/HD-SDI',
        }
        self.WriteStatus('SignalSelect', SignalSelectState[match.group(2).decode()], {'Input': str(int(match.group(1).decode()))})

    def UpdateTemperature(self, value, qualifier):

        self.__UpdateHelper('Temperature', '20s', value, qualifier)

    def __MatchTemperature(self, match, qualifier):
        self.WriteStatus('Temperature', float(match.group(1).decode()), None)

    def SetTestPattern(self, value, qualifier):

        TestPatternValue = {
            'Off': '0J',
            'Color Bars': '1J',
            'Crosshatch': '2J',
            '4x4 Crosshatch': '3J',
            'Grayscale': '4J',
            'Ramp': '5J',
            'Alternating Pixels': '6J',
            'White Field': '7J',
            'Crop': '8J',
            'Side by Side': '9J',
            'Quad': '10J',
            'PIP': '11J',
            'Aspect Ratio 1.78': '12J',
            'Aspect Ratio 1.85': '13J',
            'Aspect Ratio 2.35': '14J',
        }
        self.__SetHelper('TestPattern', TestPatternValue[value], value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        self.__UpdateHelper('TestPattern', 'J', value, qualifier)

    def __MatchTestPattern(self, match, qualifier):
        TestPatternState = {
            '00': 'Off',
            '01': 'Color Bars',
            '02': 'Crosshatch',
            '03': '4x4 Crosshatch',
            '04': 'Grayscale',
            '05': 'Ramp',
            '06': 'Alternating Pixels',
            '07': 'White Field',
            '08': 'Crop',
            '09': 'Side by Side',
            '10': 'Quad',
            '11': 'PIP',
            '12': 'Aspect Ratio 1.78',
            '13': 'Aspect Ratio 1.85',
            '14': 'Aspect Ratio 2.35',
        }
        self.WriteStatus('TestPattern', TestPatternState[match.group(1).decode()], None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        window = qualifier['Window']
        if 0 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(window, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        window = qualifier['Window']
        if 0 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('VideoMute', '{0}b'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
        }
        value = VideoMuteName[match.group(2).decode()]
        window = match.group(1).decode()
        if window == '0':
            for i in range(1, self.NumberOfWindow + 1):
                self.WriteStatus('VideoMute', value, {'Window': str(i)})
        self.WriteStatus('VideoMute', value, {'Window': window})

    def SetWindowHorizontalShift(self, value, qualifier):

        WindowHorizontalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('WindowHorizontalShift', '1*{0}*{1}H'.format(window, WindowHorizontalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalShift')

    def UpdateWindowHorizontalShiftStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowHorizontalShiftStatus', '1*{0}H'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalShiftStatus')

    def __MatchWindowHorizontalShiftStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('WindowHorizontalShiftStatus', value, {'Window': window})

    def SetWindowHorizontalSize(self, value, qualifier):

        WindowHorizontalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('WindowHorizontalSize', '1*{0}*{1}:'.format(window, WindowHorizontalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalSize')

    def UpdateWindowHorizontalSizeStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowHorizontalSizeStatus', '1*{0}:'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalSizeStatus')

    def __MatchWindowHorizontalSizeStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('WindowHorizontalSizeStatus', value, {'Window': window})

    def SetWindowPresetRecall(self, value, qualifier):

        PresetType = {
            'Without Input': 1,
            'With Input': 2,
        }
        type = qualifier['Type']
        if 1 <= int(value) <= 128:
            self.__SetHelper('WindowPresetRecall', '{0}*{1}.'.format(PresetType[type], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetRecall')

    def UpdateWindowPresetRecalledStatusPro(self, value, qualifier):

        WindowPresetRecalledStatusProCmdString = '1.'
        self.__UpdateHelper('WindowPresetRecalledStatusPro', WindowPresetRecalledStatusProCmdString, value, qualifier)

    def __MatchWindowPresetRecalledStatus(self, match, tag):

        value = str(int(match.group(1).decode()))
        if self.ModelType == 'Pro':
            self.WriteStatus('WindowPresetRecalledStatusPro', value, None)
        elif self.ModelType == 'Normal':
            self.WriteStatus('WindowPresetRecalledStatusNormal', value, None)

    def SetWindowPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('WindowPresetSave', '2*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetSave')

    def SetWindowVerticalShift(self, value, qualifier):

        WindowVerticalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('WindowVerticalShift', '1*{0}*{1}/'.format(window, WindowVerticalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalShift')

    def UpdateWindowVerticalShiftStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowVerticalShiftStatus', '1*{0}/'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalShiftStatus')

    def __MatchWindowVerticalShiftStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('WindowVerticalShiftStatus', value, {'Window': window})

    def SetWindowVerticalSize(self, value, qualifier):

        WindowVerticalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('WindowVerticalSize', '1*{0}*{1};'.format(window, WindowVerticalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalSize')

    def UpdateWindowVerticalSizeStatus(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowVerticalSizeStatus', '1*{0};'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalSizeStatus')

    def __MatchWindowVerticalSizeStatus(self, match, tag):
        window = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('WindowVerticalSizeStatus', value, {'Window': window})

    def SetWindowZoom(self, value, qualifier):

        ZoomValue = {
            'In': '+',
            'Out': '-',
        }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__SetHelper('WindowZoom', '1*{0}*{1}{2}'.format(window, ZoomValue[value], '{'), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }
        ErrorCode = DEVICE_ERROR_CODES.get(match.group(1).decode(), 'Unknown error: ' + match.group(0).decode())
        self.Error([ErrorCode])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
        self.VerboseDisabled = True

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

    def extr_18_28_462_Normal(self):
        self.NumberOfWindow = 2
        self.NumberOfInput = 19
        self.ModelType = 'Normal'
        self.RateValue = {
            '50 Hz': '1',
            '60 Hz': '2',
            '72 Hz': '3',
            '96 Hz': '4',
            '100 Hz': '5',
            '120 Hz': '6',
            '24 Hz': '8',
            'DVI Background Input Refresh Rate': '7',
            '59.94 Hz': '9',
        }

        self.ResolutionValue = {
            '640x480': '1',
            '800x600': '2',
            '852x480': '3',
            '1024x768': '4',
            '1024x852': '5',
            '1024x1024': '6',
            '1280x768': '7',
            '1280x1024': '8',
            '1360x765': '9',
            '1365x768': '10',
            '1366x768': '11',
            '1365x1024': '12',
            '1400x1050': '13',
            '1600x1200': '14',
            '480p': '15',
            '576p': '16',
            '720p': '17',
            '1080i': '18',
            '1080p': '19',
            '1280x800': '21',
            '1360x768': '22',
            '1440x900': '23',
            '1680x1050': '24',
            '1920x1200': '26',
            'DVI Background Input Resolution': '20',
            '1080p Sharp': '25',
        }

        self.RateState = {
            '1': '50 Hz',
            '2': '60 Hz',
            '3': '72 Hz',
            '4': '96 Hz',
            '5': '100 Hz',
            '6': '120 Hz',
            '8': '24 Hz',
            '7': 'DVI Background Input Refresh Rate',
            '9': '59.94 Hz',
        }

        self.ResolutionState = {
            '01': '640x480',
            '02': '800x600',
            '03': '852x480',
            '04': '1024x768',
            '05': '1024x852',
            '06': '1024x1024',
            '07': '1280x768',
            '08': '1280x1024',
            '09': '1360x765',
            '10': '1365x768',
            '11': '1366x768',
            '12': '1365x1024',
            '13': '1400x1050',
            '14': '1600x1200',
            '15': '480p',
            '16': '576p',
            '17': '720p',
            '18': '1080i',
            '19': '1080p',
            '21': '1280x800',
            '22': '1360x768',
            '23': '1440x900',
            '24': '1680x1050',
            '26': '1920x1200',
            '20': 'DVI Background Input Resolution',
            '25': '1080p Sharp',
        }

    def extr_18_28_464_Normal(self):
        self.NumberOfWindow = 4
        self.NumberOfInput = 19
        self.ModelType = 'Normal'
        self.RateValue = {
            '50 Hz': '1',
            '60 Hz': '2',
            '72 Hz': '3',
            '96 Hz': '4',
            '100 Hz': '5',
            '120 Hz': '6',
            '24 Hz': '8',
            'DVI Background Input Refresh Rate': '7',
            '59.94 Hz': '9',
        }

        self.ResolutionValue = {
            '640x480': '1',
            '800x600': '2',
            '852x480': '3',
            '1024x768': '4',
            '1024x852': '5',
            '1024x1024': '6',
            '1280x768': '7',
            '1280x1024': '8',
            '1360x765': '9',
            '1365x768': '10',
            '1366x768': '11',
            '1365x1024': '12',
            '1400x1050': '13',
            '1600x1200': '14',
            '480p': '15',
            '576p': '16',
            '720p': '17',
            '1080i': '18',
            '1080p': '19',
            '1280x800': '21',
            '1360x768': '22',
            '1440x900': '23',
            '1680x1050': '24',
            '1920x1200': '26',
            'DVI Background Input Resolution': '20',
            '1080p Sharp': '25',
        }

        self.RateState = {
            '1': '50 Hz',
            '2': '60 Hz',
            '3': '72 Hz',
            '4': '96 Hz',
            '5': '100 Hz',
            '6': '120 Hz',
            '8': '24 Hz',
            '7': 'DVI Background Input Refresh Rate',
            '9': '59.94 Hz',
        }

        self.ResolutionState = {
            '01': '640x480',
            '02': '800x600',
            '03': '852x480',
            '04': '1024x768',
            '05': '1024x852',
            '06': '1024x1024',
            '07': '1280x768',
            '08': '1280x1024',
            '09': '1360x765',
            '10': '1365x768',
            '11': '1366x768',
            '12': '1365x1024',
            '13': '1400x1050',
            '14': '1600x1200',
            '15': '480p',
            '16': '576p',
            '17': '720p',
            '18': '1080i',
            '19': '1080p',
            '21': '1280x800',
            '22': '1360x768',
            '23': '1440x900',
            '24': '1680x1050',
            '26': '1920x1200',
            '20': 'DVI Background Input Resolution',
            '25': '1080p Sharp',
        }

    def extr_18_28_462_Pro(self):
        self.NumberOfWindow = 2
        self.NumberOfInput = 19
        self.ModelType = 'Pro'
        self.RateValue = {
            '50 Hz': '1',
            '60 Hz': '2',
            '72 Hz': '3',
            '96 Hz': '4',
            '100 Hz': '5',
            '120 Hz': '6',
            '24 Hz': '8',
            'Live Background Input Rate': '7',
            '59.94 Hz': '9',
            '29.97 Hz': '10',
            '30 Hz': '11'
        }

        self.ResolutionValue = {
            '640x480': '1',
            '800x600': '2',
            '852x480': '3',
            '1024x768': '4',
            '1024x852': '5',
            '1024x1024': '6',
            '1280x768': '7',
            '1280x1024': '8',
            '1360x765': '9',
            '1365x768': '10',
            '1366x768': '11',
            '1365x1024': '12',
            '1400x1050': '13',
            '1600x1200': '14',
            '480p': '15',
            '576p': '16',
            '720p': '17',
            '1080i': '18',
            '1080p': '19',
            '1280x800': '21',
            '1360x768': '22',
            '1440x900': '23',
            '1680x1050': '24',
            '1920x1200': '26',
            'Live Background Resolution': '20',
            '1080p Sharp': '25',
            '1080p CVT': '27',
            '2048x1080': '28'
        }

        self.RateState = {
            '1': '50 Hz',
            '2': '60 Hz',
            '3': '72 Hz',
            '4': '96 Hz',
            '5': '100 Hz',
            '6': '120 Hz',
            '8': '24 Hz',
            '7': 'Live Background Input Rate',
            '9': '59.94 Hz',
            '10': '29.97 Hz',
            '11': '30 Hz'
        }

        self.ResolutionState = {
            '01': '640x480',
            '02': '800x600',
            '03': '852x480',
            '04': '1024x768',
            '05': '1024x852',
            '06': '1024x1024',
            '07': '1280x768',
            '08': '1280x1024',
            '09': '1360x765',
            '10': '1365x768',
            '11': '1366x768',
            '12': '1365x1024',
            '13': '1400x1050',
            '14': '1600x1200',
            '15': '480p',
            '16': '576p',
            '17': '720p',
            '18': '1080i',
            '19': '1080p',
            '21': '1280x800',
            '22': '1360x768',
            '23': '1440x900',
            '24': '1680x1050',
            '26': '1920x1200',
            '20': 'Live Background Resolution',
            '25': '1080p Sharp',
            '27': '1080p CVT',
            '28': '2048x1080'
        }

    def extr_18_28_464_Pro(self):
        self.NumberOfWindow = 4
        self.NumberOfInput = 19
        self.ModelType = 'Pro'
        self.RateValue = {
            '50 Hz': '1',
            '60 Hz': '2',
            '72 Hz': '3',
            '96 Hz': '4',
            '100 Hz': '5',
            '120 Hz': '6',
            '24 Hz': '8',
            'Live Background Input Rate': '7',
            '59.94 Hz': '9',
            '29.97 Hz': '10',
            '30 Hz': '11'
        }

        self.ResolutionValue = {
            '640x480': '1',
            '800x600': '2',
            '852x480': '3',
            '1024x768': '4',
            '1024x852': '5',
            '1024x1024': '6',
            '1280x768': '7',
            '1280x1024': '8',
            '1360x765': '9',
            '1365x768': '10',
            '1366x768': '11',
            '1365x1024': '12',
            '1400x1050': '13',
            '1600x1200': '14',
            '480p': '15',
            '576p': '16',
            '720p': '17',
            '1080i': '18',
            '1080p': '19',
            '1280x800': '21',
            '1360x768': '22',
            '1440x900': '23',
            '1680x1050': '24',
            '1920x1200': '26',
            'Live Background Resolution': '20',
            '1080p Sharp': '25',
            '1080p CVT': '27',
            '2048x1080': '28'
        }

        self.RateState = {
            '1': '50 Hz',
            '2': '60 Hz',
            '3': '72 Hz',
            '4': '96 Hz',
            '5': '100 Hz',
            '6': '120 Hz',
            '8': '24 Hz',
            '7': 'Live Background Input Rate',
            '9': '59.94 Hz',
            '10': '29.97 Hz',
            '11': '30 Hz'
        }

        self.ResolutionState = {
            '01': '640x480',
            '02': '800x600',
            '03': '852x480',
            '04': '1024x768',
            '05': '1024x852',
            '06': '1024x1024',
            '07': '1280x768',
            '08': '1280x1024',
            '09': '1360x765',
            '10': '1365x768',
            '11': '1366x768',
            '12': '1365x1024',
            '13': '1400x1050',
            '14': '1600x1200',
            '15': '480p',
            '16': '576p',
            '17': '720p',
            '18': '1080i',
            '19': '1080p',
            '21': '1280x800',
            '22': '1360x768',
            '23': '1440x900',
            '24': '1680x1050',
            '26': '1920x1200',
            '20': 'Live Background Resolution',
            '25': '1080p Sharp',
            '27': '1080p CVT',
            '28': '2048x1080'
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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
