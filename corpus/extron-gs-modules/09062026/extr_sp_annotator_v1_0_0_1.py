from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveLines': {'Status': {}},
            'ActivePixels': {'Status': {}},
            'AnnotationDisplay': {'Status': {}},
            'AnnotatorEditFunctions': {'Status': {}},
            'AnnotatorObjectFill': {'Status': {}},
            'AnnotatorType': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Brightness': {'Status': {}},
            'Color': {'Status': {}},
            'Contrast': {'Status': {}},
            'CurrentImage': {'Status': {}},
            'CursorDisplay': {'Status': {}},
            'DropShadow': {'Status': {}},
            'EraseHighlighterSize': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'HorizontalShift': {'Status': {}},
            'HorizontalSize': {'Status': {}},
            'HorizontalStart': {'Status': {}},
            'ImageMute': {'Status': {}},
            'ImageQuickCapture': {'Status': {}},
            'ImageRecall': {'Status': {}},
            'Input': {'Status': {}},
            'InputPresets': {'Status': {}},
            'LineWeight': {'Status': {}},
            'MemoryPresets': {'Status': {}},
            'MenuDisplay': {'Status': {}},
            'OSDCapture': {'Status': {}},
            'Pan': {'Parameters': ['Pan Value'], 'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PixelPhase': {'Status': {}},
            'SaveImage': {'Status': {}},
            'Swap': {'Status': {}},
            'SwitchingEffect': {'Status': {}},
            'Temperature': {'Status': {}},
            'TestPattern': {'Status': {}},
            'TextSize': {'Status': {}},
            'Tint': {'Status': {}},
            'TotalPixel': {'Status': {}},
            'VerticalShift': {'Status': {}},
            'VerticalSize': {'Status': {}},
            'VerticalStart': {'Status': {}},
            'VideoMute': {'Status': {}},
            'ViewSettings': {'Status': {}},
            'Zoom': {'Status': {}},
        }
        self.devicePassword = None
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
        else:
            if self.devicePassword:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')
        self.Authenticated = 'None'

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def SetActiveLines(self, value, qualifier):

        ActiveLines = {
            'Min': 0,
            'Max': 4095
        }

        if ActiveLines['Min'] <= value <= ActiveLines['Max']:
            ActiveLineCommand = '\x1B{0}ALIN\r'.format(value)
            self.__SetHelper('ActiveLines', ActiveLineCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveLines')

    def UpdateActiveLines(self, value, qualifier):

        ActiveLineQueryCommand = '\x1BALIN\r'
        response = self.__UpdateHelper('ActiveLines', ActiveLineQueryCommand, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            print(response)
            if (0 < len(response) < 5) and (0 <= int(response) < 4096):
                value = int(response)
                self.WriteStatus('ActiveLines', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for ActiveLines'])

    def SetActivePixels(self, value, qualifier):

        ActivePixel = {
            'Min': 0,
            'Max': 4095
        }

        if ActivePixel['Min'] <= value <= ActivePixel['Max']:
            ActivePixelsCommand = '\x1B{0}APIX\r'.format(value)
            self.__SetHelper('ActivePixels', ActivePixelsCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActivePixels')

    def UpdateActivePixels(self, value, qualifier):

        ActivePixelQueryCommand = '\x1BAPIX\r'
        response = self.__UpdateHelper('ActivePixels', ActivePixelQueryCommand, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 5) and (0 <= int(response) < 4096):
                value = int(response)
                self.WriteStatus('ActivePixels', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for ActivePixels'])

    def SetAnnotationDisplay(self, value, qualifier):

        DisplayStates = {
            'All Output': 0,
            'Program Only': 1,
            'Preview Only': 2,
            'None': 3
        }

        AnnotationDisplayCommand = '\x1B{0}ASHW\r'.format(DisplayStates[value])
        self.__SetHelper('AnnotationDisplay', AnnotationDisplayCommand, value, qualifier)

    def UpdateAnnotationDisplay(self, value, qualifier):

        AnnotationDisplay = {
            '00': 'All Output',
            '01': 'Program Only',
            '02': 'Preview Only',
            '03': 'None'
        }

        AnnotationDisplayQuery = '\x1BASHW\r'
        response = self.__UpdateHelper('AnnotationDisplay', AnnotationDisplayQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = AnnotationDisplay[response]
                self.WriteStatus('AnnotationDisplay', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for AnnotationDisplay'])

    def SetAnnotatorEditFunctions(self, value, qualifier):

        AnnotationEditStates = {
            'Clear': 0,
            'Undo': 1,
            'Redo': 2
        }

        AnnotationEditCommand = '\x1B{0}EDIT\r'.format(AnnotationEditStates[value])
        self.__SetHelper('AnnotationEditFunctions', AnnotationEditCommand, value, qualifier)

    def SetAnnotatorObjectFill(self, value, qualifier):

        AnnotatorObjectFillStates = {
            'Off': 0,
            'On': 1
        }

        AnnotatorObjectFillCommands = '\x1B{0}FILL\r'.format(AnnotatorObjectFillStates[value])
        self.__SetHelper('AnnotatorObjectFill', AnnotatorObjectFillCommands, value, qualifier)

    def UpdateAnnotatorObjectFill(self, value, qualifier):

        AnnotatorObjectFillStates = {
            '00': 'Off',
            '01': 'On'
        }

        AnnotatorObjectFillQuery = '\x1BFILL\r'
        response = self.__UpdateHelper('AnnotatorObjectFill', AnnotatorObjectFillQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = AnnotatorObjectFillStates[response]
                self.WriteStatus('AnnotatorObjectFill', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for AnnotatorObjectFill'])

    def SetAnnotatorType(self, value, qualifier):

        AnnotatorType = {
            'Eraser': 0,
            'Pointer': 1,
            'Freehand': 2,
            'Highlighter': 3,
            'Vector Line': 4,
            'Arrow Line': 5,
            'Ellipse': 6,
            'Rectangle': 7,
            'Text Tool': 8,
            'Spotlight': 9,
            'Zoom Tool': 10,
            'Pan Tool': 11
        }

        AnnotatorTypeCommand = '\x1B{0}DRAW\r'.format(AnnotatorType[value])
        self.__SetHelper('AnnotatorType', AnnotatorTypeCommand, value, qualifier)

    def UpdateAnnotatorType(self, value, qualifier):

        AnnotatorTypeStates = {
            '00': 'Eraser',
            '01': 'Pointer',
            '02': 'Freehand',
            '03': 'Highlighter',
            '04': 'Vector Line',
            '05': 'Arrow Line',
            '06': 'Ellipse',
            '07': 'Rectangle',
            '08': 'Text Tool',
            '09': 'Spotlight',
            '10': 'Zoom Tool',
            '11': 'Pan Tool'
        }

        AnnotatorTypeQuery = '\x1BDRAW\r'
        response = self.__UpdateHelper('AnnotatorType', AnnotatorTypeQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = AnnotatorTypeStates[response]
                self.WriteStatus('AnnotatorType', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for AnnotatorType'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCommand = 'A\r'
        self.__SetHelper('AutoImage', AutoImageCommand, value, qualifier)

    def SetBrightness(self, value, qualifier):

        BrightnessConstraints = {
            'Min': 0,
            'Max': 127
        }

        if BrightnessConstraints['Min'] <= value <= BrightnessConstraints['Max']:
            BrightnessCommand = '\x1B{0}BRIT\r'.format(value)
            self.__SetHelper('Brightness', BrightnessCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessQueryCommand = '\x1BBRIT\r'
        response = self.__UpdateHelper('Brightness', BrightnessQueryCommand, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 128):
                value = int(response)
                self.WriteStatus('Brightness', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for Brightness'])

    def SetColor(self, value, qualifier):

        ColorConstraints = {
            'Min': 0,
            'Max': 127
        }

        if ColorConstraints['Min'] <= value <= ColorConstraints['Max']:
            ColorCommand = '\x1B{0}COLR\r'.format(value)
            self.__SetHelper('Color', ColorCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColor')

    def UpdateColor(self, value, qualifier):

        ColorQueryCommand = '\x1BCOLR\r'
        response = self.__UpdateHelper('Color', ColorQueryCommand, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 128):
                value = int(response)
                self.WriteStatus('Color', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for Color'])

    def SetContrast(self, value, qualifier):

        ContrastConstraints = {
            'Min': 0,
            'Max': 127
        }

        if ContrastConstraints['Min'] <= value <= ContrastConstraints['Max']:
            ContrastCommand = '\x1B{0}CONT\r'.format(value)
            self.__SetHelper('Contrast', ContrastCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastQueryCommand = '\x1BCONT\r'
        response = self.__UpdateHelper('Contrast', ContrastQueryCommand, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 128):
                value = int(response)
                self.WriteStatus('Contrast', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for Contrast'])

    def UpdateCurrentImage(self, value, qualifier):

        CurrentImageQuery = '\x1BRF\r'
        response = self.__UpdateHelper('CurrentImage', CurrentImageQuery, value, qualifier)
        if response:
            try:
                value = response[:-4]
                self.WriteStatus('CurrentImage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for CurrentImage'])

    def SetCursorDisplay(self, value, qualifier):

        CursorStates = {
            'All Outputs': 0,
            'Program Only': 1,
            'Preview Only': 2,
            'None': 3
        }

        CursorDisplayCommand = '\x1B{0}CSHW\r'.format(CursorStates[value])
        self.__SetHelper('CursorDisplay', CursorDisplayCommand, value, qualifier)

    def UpdateCursorDisplay(self, value, qualifier):

        CursorStates = {
            '00': 'All Outputs',
            '01': 'Program Only',
            '02': 'Preview Only',
            '03': 'None'
        }

        CursorDisplayQuery = '\x1BCSHW\r'
        response = self.__UpdateHelper('CursorDisplay', CursorDisplayQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = CursorStates[response]
                self.WriteStatus('CursorDisplay', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for CursorDisplay'])

    def SetDropShadow(self, value, qualifier):

        DropShadowStates = {
            'On': 1,
            'Off': 0
        }

        DropShadowCommand = '\x1B{0}SHDW\r'.format(DropShadowStates[value])
        self.__SetHelper('DropShadow', DropShadowCommand, value, qualifier)

    def UpdateDropShadow(self, value, qualifier):

        DropShadowStates = {
            '00': 'Off',
            '01': 'On'
        }

        DropShadowQuery = '\x1BSHDW\r'
        response = self.__UpdateHelper('DropShadow', DropShadowQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = DropShadowStates[response]
                self.WriteStatus('DropShadow', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for DropShadow'])

    def SetEraseHighlighterSize(self, value=8, qualifier=None):

        Constraints = {
            'Min': 1,
            'Max': 63
        }

        if Constraints['Min'] <= value <= Constraints['Max']:
            EraseHighlighterSizeCommand = '\x1B{0}ERSR\r'.format(value)
            self.__SetHelper('EraseHighlighterSize', EraseHighlighterSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEraseHighlighterSize')

    def UpdateEraseHighlighterSize(self, value, qualifier):

        EraseHighlighterSizeQuery = '\x1BERSR\r'
        response = self.__UpdateHelper('EraseHighlighterSize', EraseHighlighterSizeQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 3) and (1 <= int(response) < 64):
                value = int(response)
                self.WriteStatus('EraseHighlighterSize', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for EraseHighlighterSize'])

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStates = {
            'Mode 1': '1X\r',
            'Mode 2': '2X\r',
            'Disabled': '0X\r'
        }

        ExecutiveModeCommand = ExecutiveModeStates[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCommand, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeStates = {
            '0': 'Disabled',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        ExecutiveModeQueryCommand = 'X'
        response = self.__UpdateHelper('ExecutiveMode', ExecutiveModeQueryCommand, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = ExecutiveModeStates[response]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for ExecutiveMode'])

    def SetFreeze(self, value, qualifier):

        FreezeStates = {
            'On': '1F',
            'Off': '0F'
        }

        FreezeCommand = FreezeStates[value]
        self.__SetHelper('Freeze', FreezeCommand, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStates = {
            '00': 'Off',
            '01': 'On'
        }
        FreezeQueryCommand = 'F'
        response = self.__UpdateHelper('Freeze', FreezeQueryCommand, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = FreezeStates[response]
                self.WriteStatus('Freeze', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for Freeze'])

    def SetHorizontalShift(self, value, qualifier):

        HorizontalShift = {
            'Min': -2048,
            'Max': 2047
        }

        if HorizontalShift['Min'] <= value <= HorizontalShift['Max']:
            HorizontalShiftCommand = '\x1B{0}HCTR\r'.format(value + 2048)
            self.__SetHelper('HorizontalShift', HorizontalShiftCommand, value + 2048, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalShift')

    def UpdateHorizontalShift(self, value, qualifier):

        HorizontalShiftQuery = '\x1BHCTR\r'
        response = self.__UpdateHelper('HorizontalShift', HorizontalShiftQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 6) and (0 <= int(response) < 4096):
                value = int(response)
                value = value - 2048
                self.WriteStatus('HorizontalShift', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for HorizontalShift'])

    def SetHorizontalSize(self, value, qualifier):

        HorizontalSize = {
            'Min': 0,
            'Max': 4095
        }

        if HorizontalSize['Min'] <= value <= HorizontalSize['Max']:
            HorizontalSizeCommand = '\x1B{0}HSIZ\r'.format(value)
            self.__SetHelper('HorizontalSize', HorizontalSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSize')

    def UpdateHorizontalSize(self, value, qualifier):

        HorizontalSizeQuery = '\x1BHSIZ\r'
        response = self.__UpdateHelper('HorizontalSize', HorizontalSizeQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 5) and (0 <= int(response) < 4096):
                value = int(response)
                self.WriteStatus('HorizontalSize', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for HorizontalSize'])

    def SetHorizontalStart(self, value, qualifier):

        HorizontalStartConstraints = {
            'Min': 0,
            'Max': 255
        }

        if HorizontalStartConstraints['Min'] <= value <= HorizontalStartConstraints['Max']:
            HorizontalStartCommand = '\x1B{0}HSRT\r'.format(value)
            self.__SetHelper('HorizontalStart', HorizontalStartCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalStart')

    def UpdateHorizontalStart(self, value, qualifier):

        HorizontalStartQuery = '\x1BHSRT\r'
        response = self.__UpdateHelper('HorizontalStart', HorizontalStartQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 256):
                value = int(response)
                self.WriteStatus('HorizontalStart', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for HorizontalStart'])

    def SetImageMute(self, value, qualifier):

        ImageMuteCommand = '\x1B0*0RF\r'
        self.__SetHelper('ImageMute', ImageMuteCommand, value, qualifier)

    def SetImageRecall(self, value, qualifier):

        ValueStringLength = len(value)
        if 0 < ValueStringLength <= 16:
            ImageRecallCommand = '\x1B0*{0}.bmpRF\r'.format(value)
            self.__SetHelper('ImageRecall', ImageRecallCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageRecall')

    def SetImageQuickCapture(self, value, qualifier):

        QuickCaptureCommand = '\x1BQCAP\r'
        self.__SetHelper('ImageQuickCapture', QuickCaptureCommand, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        InputCommand = '{0}!'.format(InputStates[value])
        self.__SetHelper('Input', InputCommand, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7'
        }

        InputQueryCommand = '!'
        response = self.__UpdateHelper('Input', InputQueryCommand, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = InputStates[response]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for Input'])

    def SetInputPresets(self, value, qualifier):

        if 0 < int(value) < 129:
            InputPresetCommand = '2*{0}.'.format(value)
            self.__SetHelper('InputPreset', InputPresetCommand, value, qualifier)

    def SetLineWeight(self, value, qualifier):

        LineWeightConstraints = {
            'Min': 1,
            'Max': 63
        }

        if LineWeightConstraints['Min'] <= value <= LineWeightConstraints['Max']:
            LineWeightCommand = '\x1B{0}LNWT\r'.format(value)
            self.__SetHelper('LineWeight', LineWeightCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineWeight')

    def UpdateLineWeight(self, value, qualifier):

        LineWeightQuery = '\x1BLNWT\r'
        response = self.__UpdateHelper('LineWeight', LineWeightQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 3) and (1 <= int(response) < 64):
                value = int(response)
                self.WriteStatus('LineWeight', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for LineWeight'])

    def SetMemoryPresets(self, value, qualifier):

        if 0 < int(value) < 17:
            PresetCommand = '1*{0}.'.format(value)
            self.__SetHelper('MemoryPresets', PresetCommand, value, qualifier)

    def SetMenuDisplay(self, value, qualifier):

        Output = {
            'All Output': 0,
            'Program Only': 1,
            'Preview Only': 2,
            'None': 3
        }

        CommandString = '\x1B {0}MSHW\r'.format(Output[value])
        self.__SetHelper('MenuDisplay', CommandString, value, qualifier)

    def SetOSDCapture(self, value, qualifier):

        Mode = {
            'Internal Memory': 0,
            'External Location': 1
        }

        CommandString = '\x1B{0}MCAP\r'.format(Mode[value])
        self.__SetHelper('OSDCaputre', CommandString, value, qualifier)

    def SetPan(self, value, qualifier):

        PanDirection = {
            'Left': '+HPAN',
            'Right': '-HPAN',
            'Up': '-VPAN',
            'Down': '+VPAN'
        }

        CommandString = '\x1B{0}\r'.format(PanDirection[value])
        self.__SetHelper('Pan', CommandString, value, qualifier)

    def SetPictureInPicture(self, value, qualifier):

        PIPStates = {
            'Input 1': 1,
            'Input 2': 2,
            'Input 3': 3,
            'Input 4': 4,
            'Input 5': 5,
            'Input 6': 6,
            'Input 7': 7,
            'Off': 0
        }

        PIPCommand = '\x1B{0}PIP\r'.format(PIPStates[value])
        self.__SetHelper('PictureInPicture', PIPCommand, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureStates = {
            '00': 'Off',
            '01': 'Input 1',
            '02': 'Input 2',
            '03': 'Input 3',
            '04': 'Input 4',
            '05': 'Input 5',
            '06': 'Input 6',
            '07': 'Input 7'
        }
        PIPQuery = '\x1BPIP\r'
        response = self.__UpdateHelper('PictureInPicture', PIPQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = PictureInPictureStates[response]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for PictureInPicture'])

    def SetPixelPhase(self, value, qualifier):

        PixelPhaseConstraints = {
            'Min': 0,
            'Max': 31
        }

        if PixelPhaseConstraints['Min'] <= value <= PixelPhaseConstraints['Max']:
            PixelPhaseCommand = '\x1B{0}PHAS\r'.format(value)
            self.__SetHelper('PixelPhase', PixelPhaseCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPixelPhase')

    def UpdatePixelPhase(self, value, qualifier):

        PixelPhaseQuery = '\x1BPHAS\r'
        response = self.__UpdateHelper('PixelPhase', PixelPhaseQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 3) and (0 <= int(response) < 32):
                value = int(response)
                self.WriteStatus('PixelPhase', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for PixelPhase'])

    def SetSaveImage(self, value, qualifier):

        ValueStringLength = len(value)
        if 0 < ValueStringLength <= 16:
            SaveImageCommand = '\x1B0*{0}.bmpMF\r'.format(value)
            self.__SetHelper('SaveImage', SaveImageCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveImage')

    def SetSwap(self, value, qualifier):

        SwapCommand = '%\r'
        self.__SetHelper('Swap', SwapCommand, value, qualifier)

    def SetSwitchingEffect(self, value, qualifier):

        SwitchEffectStates = {
            'Cut': 0,
            'Fade': 1
        }

        SwitchCommand = '\x1B{0}SWEF\r'.format(SwitchEffectStates[value])
        self.__SetHelper('SwitchingEffect', SwitchCommand, value, qualifier)

    def UpdateSwitchingEffect(self, value, qualifier):

        SwitchEffectStates = {
            '00': 'Cut',
            '01': 'Fade'
        }

        SwitchEffectQuery = '\x1BSWEF\r'
        response = self.__UpdateHelper('SwitchingEffect', SwitchEffectQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = SwitchEffectStates[response]
                self.WriteStatus('SwitchingEffect', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for SwitchingEffect'])

    def UpdateTemperature(self, value, qualifier):

        TemperatureQuery = '\x1B20STAT\r'
        response = self.__UpdateHelper('Temperature', TemperatureQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = response
                self.WriteStatus('Temperature', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Temperature'])

    def SetTestPattern(self, value, qualifier):

        TestPatternStates = {
            'Off': 0,
            'Color Bars': 1,
            'Crosshatch': 2,
            '4x4 Crosshatch': 3,
            'Grayscale': 4,
            'Ramp': 5,
            'Alternating Pixel': 6,
            'White Field': 7,
            'Crop': 8,
            '1.33 Aspect Ratio': 9,
            '1.78 Aspect Ratio': 10,
            '1.85 Aspect Ratio': 11,
            '2.35 Aspect Ratio': 12,
            'Safe Area': 13,
            'Blue Mode': 14
        }

        TestPatternCommand = '\x1B{0}TEST\r'.format(TestPatternStates[value])
        self.__SetHelper('TestPattern', TestPatternCommand, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternStates = {
            '00': 'Off',
            '01': 'Color Bars',
            '02': 'Crosshatch',
            '03': '4x4 Crosshatch',
            '04': 'Grayscale',
            '05': 'Ramp',
            '06': 'Alternating Pixel',
            '07': 'White Field',
            '08': 'Crop',
            '09': '1.33 Aspect Ratio',
            '10': '1.78 Aspect Ratio',
            '11': '1.85 Aspect Ratio',
            '12': '2.35 Aspect Ratio',
            '13': 'Safe Area',
            '14': 'Blue Mode'
        }

        TestPatternQuery = '\x1BTEST\r'
        response = self.__UpdateHelper('TestPattern', TestPatternQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = TestPatternStates[response]
                self.WriteStatus('TestPattern', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for TestPattern'])

    def SetTextSize(self, value, qualifier):

        TextSizeConstraints = {
            'Min': 8,
            'Max': 63
        }

        if TextSizeConstraints['Min'] <= value <= TextSizeConstraints['Max']:
            TextSizeCommand = '\x1B{0}TXSZ\r'.format(value)
            self.__SetHelper('TextSize', TextSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTextSize')

    def UpdateTextSize(self, value, qualifier):

        TextSizeQuery = '\x1BTXSZ\r'
        response = self.__UpdateHelper('TextSize', TextSizeQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 3) and (8 <= int(response) < 64):
                value = int(response)
                self.WriteStatus('TextSize', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for TextSize'])

    def SetTint(self, value, qualifier):

        TintConstraints = {
            'Min': 0,
            'Max': 127
        }

        if TintConstraints['Min'] <= value <= TintConstraints['Max']:
            TintCommand = '\x1B{0}TINT\r'.format(value)
            self.__SetHelper('Tint', TintCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):

        TintQuery = '\x1BTINT\r'
        response = self.__UpdateHelper('Tint', TintQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 128):
                value = int(response)
                self.WriteStatus('Tint', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for Tint'])

    def SetTotalPixel(self, value, qualifier):

        TotalPixel = {
            'Min': 0,
            'Max': 4095
        }

        if TotalPixel['Min'] <= value <= TotalPixel['Max']:
            TotalPixelCommand = '\x1B{0}TPIX\r'.format(value)
            self.__SetHelper('TotalPixel', TotalPixelCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTotalPixel')

    def UpdateTotalPixel(self, value, qualifier):

        TotalPixelQuery = '\x1BTPIX\r'
        response = self.__UpdateHelper('TotalPixel', TotalPixelQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 5) and (0 <= int(response) < 4096):
                value = int(response)
                self.WriteStatus('TotalPixel', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for TotalPixel'])

    def SetVerticalShift(self, value, qualifier):

        VerticalShift = {
            'Min': -2048,
            'Max': 2047
        }

        if VerticalShift['Min'] <= value <= VerticalShift['Max']:
            VerticalShiftCommand = '\x1B{0}VCTR\r'.format(value + 2048)
            self.__SetHelper('VerticalShift', VerticalShiftCommand, value + 2048, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalShift')

    def UpdateVerticalShift(self, value, qualifier):

        VerticalQuery = '\x1BVCTR\r'
        response = self.__UpdateHelper('VerticalShift', VerticalQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 6) and (0 <= int(response) < 4096):
                value = int(response)
                value = value - 2048
                self.WriteStatus('VerticalShift', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for VerticalShift'])

    def SetVerticalSize(self, value, qualifier):

        VerticalSize = {
            'Min': 0,
            'Max': 4095
        }

        if VerticalSize['Min'] <= value <= VerticalSize['Max']:
            VerticalSizeCommand = '\x1B{0}VSIZ\r'.format(value)
            self.__SetHelper('VerticalSize', VerticalSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSize')

    def UpdateVerticalSize(self, value, qualifier):

        VerticalSizeQuery = '\x1BVSIZ\r'
        response = self.__UpdateHelper('VerticalSize', VerticalSizeQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 5) and (0 <= int(response) < 4096):
                value = int(response)
                self.WriteStatus('VerticalSize', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for VerticalShift'])

    def SetVerticalStart(self, value, qualifier):

        VerticalStartConstraints = {
            'Min': 0,
            'Max': 255
        }

        if VerticalStartConstraints['Min'] <= value <= VerticalStartConstraints['Max']:
            VerticalStartCommand = '\x1B{0}VSRT\r'.format(value)
            self.__SetHelper('VerticalStart', VerticalStartCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalStart')

    def UpdateVerticalStart(self, value, qualifier):

        VerticalStartQuery = '\x1BVSRT\r'
        response = self.__UpdateHelper('VerticalStart', VerticalStartQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (0 <= int(response) < 256):
                value = int(response)
                self.WriteStatus('VerticalStart', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for VerticalStart'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteStates = {
            'Black': '1B\r',
            'White': '2B\r',
            'Off': '0B\r'
        }

        VideoMuteCommand = VideoMuteStates[value]
        self.__SetHelper('VideoMute', VideoMuteCommand, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteStates = {
            '0': 'Off',
            '1': 'Black',
            '2': 'White'
        }

        VideoMuteQuery = 'B'
        response = self.__UpdateHelper('VideoMute', VideoMuteQuery, value, qualifier)
        if response:
            try:
                response = response.rstrip('\r\n')
                value = VideoMuteStates[response[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except KeyError:
                self.Error(['Invalid/Unexpected Response for VideoMute'])

    def SetViewSettings(self, value, qualifier):

        CommandString = '\x1BMSHW\r'
        self.__SetHelper('ViewSettings', CommandString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min': 100,
            'Max': 500
        }

        if ZoomConstraints['Min'] <= value <= ZoomConstraints['Max']:
            ZoomCommand = '\x1B{0}ZOOM\r'.format(value)
            self.__SetHelper('Zoom', ZoomCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        ZoomQuery = '\x1BZOOM\r'
        response = self.__UpdateHelper('Zoom', ZoomQuery, value, qualifier)
        if response:
            response = response.rstrip('\r\n')
            if (0 < len(response) < 4) and (99 < int(response) < 501):
                value = int(response)
                self.WriteStatus('Zoom', value, qualifier)
            else:
                self.Error(['Invalid/Unexpected Response for Zoom'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': "Invalid input channel number (out of range)",
            'E10': "Invalid command",
            'E11': "Invalid preset number",
            'E12': "Invalid output number/port number",
            'E13': "Invalid parameter (out of range)",
            'E14': "Command not available for this configuration",
            'E17': "Invalid command for this signal type",
            'E22': "Busy",
            'E24': "Privilege violation",
            'E25': "Device not present",
            'E26': "Maximum number of connections exceeded",
            'E27': "Invalid event number",
            'E28': "Bad filename/file not found"
        }

        if response:
            for k, _ in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[k])])
                    response = ''
        return response

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
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
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
