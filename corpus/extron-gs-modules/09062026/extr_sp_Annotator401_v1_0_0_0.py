from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):
        
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveLines': { 'Status': {}},
            'ActivePixels': { 'Status': {}},
            'AnnotationColor': {'Parameters':['Red','Green','Blue'], 'Status': {}},
            'AnnotationDisplay': { 'Status': {}},
            'AnnotationEditFunctions': { 'Status': {}},
            'AnnotationObjectFill': { 'Status': {}},
            'AnnotationType': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioFormat': { 'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'CurrentImage': { 'Status': {}},
            'CursorDisplay': { 'Status': {}},
            'DetectedInputVideoFormat': { 'Status': {}},
            'EraserHighlighterSize': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'FrontPanelCaptureButtonMode': { 'Status': {}},
            'HDCPInputAuthorization': { 'Status': {}},
            'HDCPInputStatus': { 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Output'], 'Status': {}},
            'HorizontalShift': { 'Status': {}},
            'HorizontalSize': { 'Status': {}},
            'InputEDID': { 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'InputPresetSave': { 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'LineWeight': { 'Status': {}},
            'MenuDisplay': { 'Status': {}},
            'MuteImage': { 'Status': {}},
            'OnscreenClock': { 'Status': {}},
            'OutputFormat': {'Parameters':['Output'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'Printer': { 'Status': {}},
            'PrinterQuantity': { 'Status': {}},
            'QuickCapture': { 'Status': {}},
            'RecallImageCommand': { 'Parameters':['Filename'], 'Status': {}},
            'SaveImageCommand': { 'Parameters':['Filename'], 'Status': {}},
            'ScreenSaver': { 'Status': {}},
            'ScreenSaverTimeout': { 'Status': {}},
            'SwitchingEffect': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'TextSize': { 'Status': {}},
            'TotalPixel': { 'Status': {}},
            'USBDevice': {'Parameters':['Device'], 'Status': {}},
            'VerticalShift': { 'Status': {}},
            'VerticalSize': { 'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
            'ViewSettings': { 'Status': {}},
            'WhiteboardBlackboard': { 'Status': {}},            
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Alin([0-3]{1,2})\*([0-9]{1,4})\r\n'), self.__MatchActiveLines, None)
            self.AddMatchString(re.compile(b'Apix([0-3]{1,2})\*([0-9]{1,4})\r\n'), self.__MatchActivePixels, None)
            self.AddMatchString(re.compile(b'Ashw([0-3]{1,2})\r\n'), self.__MatchAnnotationDisplay, None)
            self.AddMatchString(re.compile(b'Fill([0-3]{1,2})\r\n'), self.__MatchAnnotationObjectFill, None)
            self.AddMatchString(re.compile(b'Draw([0-9]{1,2})\r\n'), self.__MatchAnnotationType, None)
            self.AddMatchString(re.compile(b'Aspr1\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AfmtI0{0,1}1\*([023])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Amt([12])\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Imr[023]?\*(.*)\r\n|Imr\r\n'), self.__MatchCurrentImage, None)
            self.AddMatchString(re.compile(b'Cshw([0-3]{1,2})\r\n'), self.__MatchCursorDisplay, None)
            self.AddMatchString(re.compile(b'Vid01 Typ([0-3]) Amt1\*([0-1]) Amt2\*([0-1]) Vmt1\*([0-2]) Vmt2\*([0-2]) Hrt\d+.\d+ Vrt\d+.\d+\r\n'), self.__MatchDetectedInputVideoFormat, None)
            self.AddMatchString(re.compile(b'Ersr([0-9]{1,3})\r\n'), self.__MatchEraserHighlighterSize, None)
            self.AddMatchString(re.compile(b'Exe([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Frz([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Mcap([0-3])\r\n'), self.__MatchFrontPanelCaptureButtonMode, None)
            self.AddMatchString(re.compile(b'HdcpE1\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI1\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'Hdcp(O[0-3]{1,2})\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Hctr([-+]?[0-9]{1,5})\r\n'), self.__MatchHorizontalShift, None)
            self.AddMatchString(re.compile(b'Hsiz([0-9]{2,5})\r\n'), self.__MatchHorizontalSize, None)
            self.AddMatchString(re.compile(b'EdidA1\*([0-9]{1,3})\r\n'), self.__MatchInputEDID, None)
            self.AddMatchString(re.compile(b'In00 ([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Lnwt([0-9]{1,2})\r\n'), self.__MatchLineWeight, None)
            self.AddMatchString(re.compile(b'Time([0123])'), self.__MatchOnscreenClock, None)
            self.AddMatchString(re.compile(b'Vtpo([12])\*([0123579])'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(b'Rate(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'PrtrE([01])\r\n'), self.__MatchPrinter, None)
            self.AddMatchString(re.compile(b'PrtrQ(\d+)\r\n'), self.__MatchPrinterQuantity, None)
            self.AddMatchString(re.compile(b'SsavM([123])\r\n'), self.__MatchScreenSaver, None)
            self.AddMatchString(re.compile(b'SsavT([0-9]{1,3})\r\n'), self.__MatchScreenSaverTimeout, None)
            self.AddMatchString(re.compile(b'SwefU1\*([01234])\r\n'), self.__MatchSwitchingEffect, None)
            self.AddMatchString(re.compile(b'20Stat ([0-9]{1,2}\.[0-9])C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Test([0-9]{1,2})\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'Txsz([0-9]{1,2})\r\n'), self.__MatchTextSize, None)
            self.AddMatchString(re.compile(b'Tpix([0-3]{1,2})\*([0-9]{1,4})\r\n'), self.__MatchTotalPixel, None)
            self.AddMatchString(re.compile(b'Adev([0-9]{1,2})\*([01])\r\n'), self.__MatchUSBDevice, None)
            self.AddMatchString(re.compile(b'Vctr([-+]?[0-9]{1,5})\r\n'), self.__MatchVerticalShift, None)
            self.AddMatchString(re.compile(b'Vsiz([0-9]{2,5})\r\n'), self.__MatchVerticalSize, None)
            self.AddMatchString(re.compile(b'Vmt([0-3])\*([0-2]{1,2})\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Whbd([0-2])\r\n'), self.__MatchWhiteboardBlackboard, None)

            self.AddMatchString(re.compile(b'(E\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)                  
                
    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False
       
    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def UpdateActiveLines(self, value, qualifier):

        ActiveLineQueryCommand = '\x1BALIN\r'
        self.__UpdateHelper('ActiveLines', ActiveLineQueryCommand, value, qualifier)
        
    def __MatchActiveLines(self, match, tag):
        value = int(match.group(2).decode())
        self.WriteStatus('ActiveLines', value, None)

    def UpdateActivePixels(self, value, qualifier):

        ActivePixelQueryCommand = '\x1BAPIX\r'
        self.__UpdateHelper('ActivePixels', ActivePixelQueryCommand, value, qualifier)
        
    def __MatchActivePixels(self, match, tag):
        value = int(match.group(2).decode())
        self.WriteStatus('ActivePixels', value, None)

    def SetAnnotationColor(self, value, qualifier):

        Red = qualifier['Red']
        Green = qualifier['Green']
        Blue = qualifier['Blue']

        Device = 0 if value == 'All' else value
        if 0 <= int(Device) <= 32 and 0 <= Red <= 3 and 0 <= Green <= 3 and 0 <= Blue <= 3:
            ColorValue = '{0:02b}{1:02b}{2:02b}'.format(Red, Green, Blue)
            AnnotationColorCmdString = '\x1B{0}*{1}ACOL\r'.format(Device, ColorValue)
            self.__SetHelper('AnnotationColor', AnnotationColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnnotationColor')

    def SetAnnotationDisplay(self, value, qualifier):

        DisplayStates = {
            'All Outputs'           : 0,
            'Output 1 Only'         : 1,
            'Output 2 Only'         : 2,
            'None'                  : 3
        }

        AnnotationDisplayCommand = '\x1B{0}ASHW\r'.format(DisplayStates[value])
        self.__SetHelper('AnnotationDisplay', AnnotationDisplayCommand, value, qualifier)

    def UpdateAnnotationDisplay(self, value, qualifier):

        AnnotationDisplayQuery = '\x1BASHW\r'
        self.__UpdateHelper('AnnotationDisplay', AnnotationDisplayQuery, value, qualifier)
        
    def __MatchAnnotationDisplay(self, match, tag):
        AnnotationDisplay = {
            0 : 'All Outputs',
            1 : 'Output 1 Only',
            2 : 'Output 2 Only',
            3 : 'None'
        }

        value = AnnotationDisplay[int(match.group(1).decode())]
        self.WriteStatus('AnnotationDisplay', value, None)

    def SetAnnotationEditFunctions(self, value, qualifier):

        AnnotationEditStates = {
            'Clear' : 0,
            'Undo' : 1,
            'Redo' : 2
        }

        AnnotationEditCommand = '\x1B{0}EDIT\r'.format(AnnotationEditStates[value])
        self.__SetHelper('AnnotationEditFunctions', AnnotationEditCommand, value, qualifier)

    def SetAnnotationObjectFill(self, value, qualifier):

        AnnotationObjectFillStates = {
            'Off' : 0,
            'On' : 1
        }

        AnnotationObjectFillCommands = '\x1B{0}FILL\r'.format(AnnotationObjectFillStates[value])
        self.__SetHelper('AnnotationObjectFill', AnnotationObjectFillCommands, value, qualifier)

    def UpdateAnnotationObjectFill(self, value, qualifier):

        AnnotationObjectFillQuery = '\x1BFILL\r'
        self.__UpdateHelper('AnnotationObjectFill', AnnotationObjectFillQuery, value, qualifier)
        
    def __MatchAnnotationObjectFill(self, match, tag):
        AnnotationObjectFillStates = {
            0 : 'Off',
            1 : 'On'
        }

        value = AnnotationObjectFillStates[int(match.group(1).decode())]
        self.WriteStatus('AnnotationObjectFill', value, None)

    def SetAnnotationType(self, value, qualifier):

        AnnotationType = {
            'Eraser' : 0,
            'Pointer' : 1,
            'Freehand' : 2,
            'Highlighter' : 3,
            'Vector Line' : 4,
            'Arrow Line' : 5,
            'Ellipse' : 6,
            'Rectangle' : 7,
            'Text Tool' : 8,
            'Spotlight' : 9,
            'Zoom Tool' : 10,
            'Pan Tool' : 11
        }

        AnnotationTypeCommand = '\x1B{0}DRAW\r'.format(AnnotationType[value])
        self.__SetHelper('AnnotationType', AnnotationTypeCommand, value, qualifier)

    def UpdateAnnotationType(self, value, qualifier):

        AnnotationTypeQuery = '\x1BDRAW\r'
        self.__UpdateHelper('AnnotationType', AnnotationTypeQuery, value, qualifier)
                
    def __MatchAnnotationType(self, match, tag):
        AnnotationTypeStates = {
            '00' : 'Eraser',
            '01' : 'Pointer',
            '02' : 'Freehand',
            '03' : 'Highlighter',
            '04' : 'Vector Line',
            '05' : 'Arrow Line',
            '06' : 'Ellipse',
            '07' : 'Rectangle',
            '08' : 'Text Tool',
            '09' : 'Spotlight',
            '10' : 'Zoom Tool',
            '11' : 'Pan Tool'
        }
        
        value = AnnotationTypeStates[match.group(1).decode()]
        self.WriteStatus('AnnotationType', value, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            'Fill' : '1',
            'Follow' : '2'
        }

        AspectRatioCmdString = '\x1B1*{0}ASPR\r'.format(AspectRatioValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)  

    def UpdateAspectRatio(self, value, qualifier):

        self.__UpdateHelper('AspectRatio', '\x1B1ASPR\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        AspectRatioNames = {
            '1' : 'Fill',
            '2' : 'Follow'
        }
        
        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioFormat(self, value, qualifier):

        AudioInputFormatValues = {
            'None' : '0',
            'LPCM-2CH Digital' : '2',
            'MULTI-CH Digital' : '3'
        }
        self.__SetHelper('AudioFormat', '\x1BI1*{0}AFMT\r'.format(AudioInputFormatValues[value]), value, qualifier)

    def UpdateAudioFormat(self, value, qualifier):

        self.__UpdateHelper('AudioFormat', '\x1BI1AFMT\r', value, qualifier)
        
    def __MatchAudioFormat(self, match, tag):
        AudioInputFormatNames = {
            '0' : 'None',
            '2' : 'LPCM-2CH Digital',
            '3' : 'MULTI-CH Digital'
        }
        
        value = AudioInputFormatNames[match.group(1).decode()]
        self.WriteStatus('AudioFormat', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'Off' : '0',
            'On'  : '1'
        }

        self.__SetHelper('AudioMute', '{0}*{1}Z'.format(qualifier['Output'], AudioMuteValues[value]), value, qualifier)

    def __MatchAudioMute(self, match, tag):
        AudioMuteNames = {
            '0' : 'Off',
            '1' : 'On'
        }

        output = match.group(1).decode()
        value = AudioMuteNames[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, {'Output': output})

    def SetAutoImage(self, value, qualifier):

        AutoImageValues = {
            'Execute' : '1*0A',
            'Execute and Fill' : '1*1A',
            'Execute and Follow' : '1*2A'
        }

        AutoImageCommand = AutoImageValues[value]
        self.__SetHelper('AutoImage', AutoImageCommand, value, qualifier)

    def UpdateCurrentImage(self, value, qualifier):

        CurrentImageQuery = '\x1BRF\r'
        self.__UpdateHelper('CurrentImage', CurrentImageQuery, value, qualifier)
         
    def __MatchCurrentImage(self, match, tag):
        try:
            value = match.group(1).decode()
            self.WriteStatus('CurrentImage', value, None)
        except AttributeError:
            self.WriteStatus('CurrentImage', 'None', None)
    
    def SetCursorDisplay(self, value, qualifier):

        CursorStates = {
            'All Outputs' : 0,
            'Output 1 Only' : 1,
            'Output 2 Only' : 2,
            'None' : 3
        }

        CursorDisplayCommand = '\x1B{0}CSHW\r'.format(CursorStates[value])
        self.__SetHelper('CursorDisplay', CursorDisplayCommand, value, qualifier)

    def UpdateCursorDisplay(self, value, qualifier):

        CursorDisplayQuery = '\x1BCSHW\r'
        self.__UpdateHelper('CursorDisplay', CursorDisplayQuery, value, qualifier)
        
    def __MatchCursorDisplay(self, match, tag):
        CursorStates = {
            0 : 'All Outputs',
            1 : 'Output 1 Only',
            2 : 'Output 2 Only',
            3 : 'None'
        }

        value = CursorStates[int(match.group(1).decode())]
        self.WriteStatus('CursorDisplay', value, None)

    def UpdateDetectedInputVideoFormat(self, value, qualifier):

        self.__UpdateHelper('DetectedInputVideoFormat', 'i', value, qualifier)
        
    def __MatchDetectedInputVideoFormat(self, match, tag):

        DetectedInputVideoFormatNames = {
            '0' : 'No signal present',
            '2' : 'DVI',
            '1' : 'HDMI',
        }
        
        VideoMuteStates = {
            '0' : 'Off',
            '1' : 'On',
            '2' : 'On with Sync'
        }
        
        AudioMuteNames = {
            '0' : 'Off',
            '1' : 'On'
        }
        
        detectedValue = DetectedInputVideoFormatNames[match.group(1).decode()]
        self.WriteStatus('DetectedInputVideoFormat', detectedValue, None)
        
        audiomuteout1 = AudioMuteNames[match.group(2).decode()]
        audiomuteout2 = AudioMuteNames[match.group(3).decode()]
        self.WriteStatus('AudioMute', audiomuteout1, {'Output': '1'})
        self.WriteStatus('AudioMute', audiomuteout2, {'Output': '2'})
        
        videomuteout1 = VideoMuteStates[match.group(4).decode()]
        videomuteout2 = VideoMuteStates[match.group(5).decode()]
        self.WriteStatus('VideoMute', videomuteout1, {'Output': '1'})
        self.WriteStatus('VideoMute', videomuteout2, {'Output': '2'})
        if videomuteout1 == videomuteout2:
            self.WriteStatus('VideoMute', videomuteout2, {'Output': 'All Outputs'})
        
    def SetEraserHighlighterSize(self, value = 8, qualifier = None):

        if 1 <= value <= 127:
            EraserHighlighterSizeCommand = '\x1B{0}ERSR\r'.format(value)
            self.__SetHelper('EraserHighlighterSize', EraserHighlighterSizeCommand, value, qualifier)
        else:    
            self.Discard('Invalid Command for SetEraserHighlighterSize')

    def UpdateEraserHighlighterSize(self, value, qualifier):

        EraserHighlighterSizeQuery = '\x1BERSR\r'
        self.__UpdateHelper('EraserHighlighterSize', EraserHighlighterSizeQuery, value, qualifier)
        
    def __MatchEraserHighlighterSize(self, match, tag):
        
        value = int(match.group(1).decode())
        self.WriteStatus('EraserHighlighterSize', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStates = {
            'On' : '1X\r',
            'Off'    : '0X\r'
        }

        ExecutiveModeCommand = ExecutiveModeStates[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCommand, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeQueryCommand = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeQueryCommand, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ExecutiveModeStates = {
            '0' : 'Off',
            '1' : 'On',
        }

        value = ExecutiveModeStates[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeStates = {
            'On'  : '1F',
            'Off' : '0F'
        }

        FreezeCommand = FreezeStates[value]
        self.__SetHelper('Freeze', FreezeCommand, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeQueryCommand = 'F'
        self.__UpdateHelper('Freeze', FreezeQueryCommand, value, qualifier)

    def __MatchFreeze(self, match, tag):
        FreezeStates = { 
            '0' : 'Off',
            '1' : 'On'
        }
        
        value = FreezeStates[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetFrontPanelCaptureButtonMode(self, value, qualifier):

        ModeValues = {
            'Internal Memory' : '0',
            'IQC'          : '1',
            'USB Flash'       : '2',
            'Network Drive'   : '3'
        }

        CommandString = '\x1B{0}MCAP\r'.format(ModeValues[value])
        self.__SetHelper('FrontPanelCaptureButtonMode', CommandString, value, qualifier)

    def UpdateFrontPanelCaptureButtonMode(self, value, qualifier):

        FrontPanelCaptureCmdString = '\x1BMCAP\r'
        self.__UpdateHelper('FrontPanelCaptureButtonMode', FrontPanelCaptureCmdString, value, qualifier)

    def __MatchFrontPanelCaptureButtonMode(self, match, tag):
        ModeNames = {
            '0' : 'Internal Memory',
            '1' : 'IQC',
            '2' : 'USB Flash',
            '3' : 'Network Drive'
        }
        
        value = ModeNames[match.group(1).decode()]
        self.WriteStatus('FrontPanelCaptureButtonMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        HDCPInputAuthorizationCmdString = '\x1BE1*{0}HDCP\r'.format(ValueStateValues[value])
        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = '\x1BE1HDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        
    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def UpdateHDCPInputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPInputStatus', '\x1BI1HDCP\r', value, qualifier)
        
    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Device Detected', 
            '2' : 'Source Detected with HDCP', 
            '1' : 'Source Detected without HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputStatus', value, None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        PortValues = {
            '1': 'O1',
            '2': 'O2',
        }

        PortSelect = qualifier['Output']
        self.__UpdateHelper('HDCPOutputStatus', '\x1B{0}HDCP\r'.format(PortValues[PortSelect]), value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):
        HDCPStatusNames = {
            '0' : 'No Sink Device Detected', 
            '2' : 'Sink Detected with HDCP', 
            '1' : 'Sink Detected without HDCP'
        }

        PortNames = {
            'O1' : '1',
            'O2' : '2'
        }
        
        value = HDCPStatusNames[match.group(2).decode()]
        qualifier = {'Output':PortNames[match.group(1).decode()]}
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetHorizontalShift(self, value, qualifier):

        if -32768 <= value <= 32768:
            HorizontalShiftCommand = '\x1B{0}HCTR\r'.format(value)
            self.__SetHelper('HorizontalShift', HorizontalShiftCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalShift')

    def UpdateHorizontalShift(self, value, qualifier):

        HorizontalShiftQuery = '\x1BHCTR\r'
        self.__UpdateHelper('HorizontalShift', HorizontalShiftQuery, value, qualifier)

    def __MatchHorizontalShift(self, match, tag):
        
        value = int(match.group(1).decode())
        self.WriteStatus('HorizontalShift', value, None)

    def SetHorizontalSize(self, value, qualifier):

        if 10 <= value <= 32768:
            HorizontalSizeCommand = '\x1B{0}HSIZ\r'.format(value)
            self.__SetHelper('HorizontalSize', HorizontalSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSize')

    def UpdateHorizontalSize(self, value, qualifier):

        HorizontalSizeQuery = '\x1BHSIZ\r'
        self.__UpdateHelper('HorizontalSize', HorizontalSizeQuery, value, qualifier)

    def __MatchHorizontalSize(self, match, tag):
        
        value = int(match.group(1).decode())
        self.WriteStatus('HorizontalSize', value, None)

    def SetMuteImage(self, value, qualifier):

        MuteImageCommand = '\x1B0*0RF\r'
        self.__SetHelper('MuteImage', MuteImageCommand, value, qualifier)

    def SetOnscreenClock(self, value, qualifier):

        OnscreenClockStates = {
            'Date and Time' : '1',
            'Time Only'    : '2',
            'Date Only'    : '3',
            'Off'    : '0'
        }

        OnscreenClockCommand = '\x1B{0}TIME\r'.format(OnscreenClockStates[value])
        self.__SetHelper('OnscreenClock', OnscreenClockCommand, value, qualifier)

    def UpdateOnscreenClock(self, value, qualifier):

        OnscreenClockQueryCommand = '\x1BTIME\r'
        self.__UpdateHelper('OnscreenClock', OnscreenClockQueryCommand, value, qualifier)

    def __MatchOnscreenClock(self, match, tag):
        OnscreenClockStates = {
            '1': 'Date and Time',
            '2': 'Time Only',
            '3': 'Date Only',
            '0': 'Off'
        }

        value = OnscreenClockStates[match.group(1).decode()]
        self.WriteStatus('OnscreenClock', value, None)

    def SetQuickCapture(self, value, qualifier):

        QuickCaptureCommand = '\x1B0*/Graphics/temp.bmpMF\r'
        self.__SetHelper('QuickCapture', QuickCaptureCommand, value, qualifier)

    def SetInputEDID(self, value, qualifier):

        InputEDIDValues = {
            '640x480 (60Hz)': '010',
            '800x600 (60Hz)': '011',
            '1024x768 (60Hz)': '012',
            '1280x768 (60Hz)': '013',
            '1280x800 (60Hz)': '014',
            '1280x1024 (60Hz)': '015',
            '1360x768 (60Hz)': '016',
            '1366x768 (60Hz)': '017',
            '1440x900 (60Hz)': '018',
            '1400x1050 (60Hz)': '019',
            '1600x900 (60Hz)': '020',
            '1680x1050 (60Hz)': '021',
            '1600x1200 (60Hz)': '022',
            '1920x1200 (60Hz)': '023',
            '480p (59.94Hz)': '024',
            '480p (60Hz)': '025',
            '576p (50Hz)': '026',
            '720p (25Hz)': '029',
            '720p (29.97Hz)': '030',
            '720p (30Hz)': '031',
            '720p (50Hz)': '032',
            '720p (59.94Hz)': '033',
            '720p (60Hz)': '034',
            '1080i (50Hz)': '035',
            '1080i (59.94Hz)': '036',
            '1080i (60Hz)': '037',
            '1080p (23.98Hz)': '038',
            '1080p (24Hz)': '039',
            '1080p (25Hz)': '040',
            '1080p (29.97Hz)': '041',
            '1080p (30Hz)': '042',
            '1080p (50Hz)': '043',
            '1080p (59.94Hz)': '044',
            '1080p (60Hz)': '045',
            '2048x1080 (23.98Hz)': '046',
            '2048x1080 (24Hz)': '047',
            '2048x1080 (25Hz)': '048',
            '2048x1080 (29.97Hz)': '049',
            '2048x1080 (30Hz)': '050',
            '2048x1080 (50Hz)': '051',
            '2048x1080 (59.94Hz)': '052',
            '2048x1080 (60Hz)': '053',
            '2048x1200 (60Hz)': '054',
            '2048x1536 (60Hz)': '055',
            '2560x1080 (60Hz)': '056',
            '2560x1440 (60Hz)': '057',
            '2560x1600 (60Hz)': '058',
            '3840x2160 (23.98Hz)': '059',
            '3840x2160 (24Hz)': '060',
            '3840x2160 (25Hz)': '061',
            '3840x2160 (29.97Hz)': '062',
            '3840x2160 (30Hz)': '063',
            '3840x2160 (50Hz)': '064',
            '3840x2160 (59.94Hz)': '065',
            '3840x2160 (60Hz)': '066',
            '4096x2160 (23.98Hz)': '069',
            '4096x2160 (24Hz)': '070',
            '4096x2160 (25Hz)': '071',
            '4096x2160 (29.97Hz)': '072',
            '4096x2160 (30Hz)': '073',
            '4096x2160 (50Hz)': '074',
            '4096x2160 (59.94Hz)': '075',
            '4096x2160 (60Hz)': '076',
            'Custom EDID 1': '201',
            'Custom EDID 2': '202',
            'Custom EDID 3': '203',
            'Automatic': '000'
            }

        InputEDIDCmdString = '\x1BA1*{0}EDID\r'.format(InputEDIDValues[value])
        self.__SetHelper('InputEDID', InputEDIDCmdString, value, qualifier)

    def UpdateInputEDID(self, value, qualifier):

        self.__UpdateHelper('InputEDID', '\x1BA1EDID\r', value, qualifier)
        
    def __MatchInputEDID(self, match, tag):
        InputEDIDNames = {
            '010': '640x480 (60Hz)',
            '011': '800x600 (60Hz)',
            '012': '1024x768 (60Hz)',
            '013': '1280x768 (60Hz)',
            '014': '1280x800 (60Hz)',
            '015': '1280x1024 (60Hz)',
            '016': '1360x768 (60Hz)',
            '017': '1366x768 (60Hz)',
            '018': '1440x900 (60Hz)',
            '019': '1400x1050 (60Hz)',
            '020': '1600x900 (60Hz)',
            '021': '1680x1050 (60Hz)',
            '022': '1600x1200 (60Hz)',
            '023': '1920x1200 (60Hz)',
            '024': '480p (59.94Hz)',
            '025': '480p (60Hz)',
            '026': '576p (50Hz)',
            '029': '720p (25Hz)',
            '030': '720p (29.97Hz)',
            '031': '720p (30Hz)',
            '032': '720p (50Hz)',
            '033': '720p (59.94Hz)',
            '034': '720p (60Hz)',
            '035': '1080i (50Hz)',
            '036': '1080i (59.94Hz)',
            '037': '1080i (60Hz)',
            '038': '1080p (23.98Hz)',
            '039': '1080p (24Hz)',
            '040': '1080p (25Hz)',
            '041': '1080p (29.97Hz)',
            '042': '1080p (30Hz)',
            '043': '1080p (50Hz)',
            '044': '1080p (59.94Hz)',
            '045': '1080p (60Hz)',
            '046': '2048x1080 (23.98Hz)',
            '047': '2048x1080 (24Hz)',
            '048': '2048x1080 (25Hz)',
            '049': '2048x1080 (29.97Hz)',
            '050': '2048x1080 (30Hz)',
            '051': '2048x1080 (50Hz)',
            '052': '2048x1080 (59.94Hz)',
            '053': '2048x1080 (60Hz)',
            '054': '2048x1200 (60Hz)',
            '055': '2048x1536 (60Hz)',
            '056': '2560x1080 (60Hz)',
            '057': '2560x1440 (60Hz)',
            '058': '2560x1600 (60Hz)',
            '059': '3840x2160 (23.98Hz)',
            '060': '3840x2160 (24Hz)',
            '061': '3840x2160 (25Hz)',
            '062': '3840x2160 (29.97Hz)',
            '063': '3840x2160 (30Hz)',
            '064': '3840x2160 (50Hz)',
            '065': '3840x2160 (59.94Hz)',
            '066': '3840x2160 (60Hz)',
            '069': '4096x2160 (23.98Hz)',
            '070': '4096x2160 (24Hz)',
            '071': '4096x2160 (25Hz)',
            '072': '4096x2160 (29.97Hz)',
            '073': '4096x2160 (30Hz)',
            '074': '4096x2160 (50Hz)',
            '075': '4096x2160 (59.94Hz)',
            '076': '4096x2160 (60Hz)',
            '201': 'Custom EDID 1',
            '202': 'Custom EDID 2',
            '203': 'Custom EDID 3',
            '000': 'Automatic'
        }
        
        value = InputEDIDNames[match.group(1).decode()]
        self.WriteStatus('InputEDID', value, None)
    
    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetCommand = '2*{0}.'.format(value)
            self.__SetHelper('InputPresetRecall', InputPresetCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetCommand = '2*{0},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '\x1B0LS\r', value, qualifier)
       
    def __MatchInputSignalStatus(self, match, tag):
        SignalStatusNames = {
            '0' : 'Not Active',
            '1' : 'Active'
        }

        in1 = SignalStatusNames[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', in1, None)

    def SetLineWeight(self, value, qualifier):

        if 1 <= value <= 127:
            LineWeightCommand = '\x1B{0}LNWT\r'.format(value)
            self.__SetHelper('LineWeight', LineWeightCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineWeight')

    def UpdateLineWeight(self, value, qualifier):

        LineWeightQuery = '\x1BLNWT\r'
        self.__UpdateHelper('LineWeight', LineWeightQuery, value, qualifier)

    def __MatchLineWeight(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('LineWeight', value, None)

    def SetMenuDisplay(self, value, qualifier):

        Output = {
            'All Outputs'           : 0,
            'Output 1 Only'         : 1,
            'Output 2 Only'         : 2,
            'None'                  : 3
        }

        CommandString = '\x1B{0}MSHW\r'.format(Output[value])
        self.__SetHelper('MenuDisplay', CommandString, value, qualifier)

    def SetOutputFormat(self, value, qualifier):

        DigitalOutputFormatValues = {
            'Auto': '0',
            'DVI': '1',
            'HDMI RGB FULL': '2',
            'HDMI RGB LIMITED': '3',
            'HDMI YUV 444 LIMITED': '5',
            'HDMI YUV 422 LIMITED': '7',
        }

        OutputSelect = qualifier['Output']
        DigitalOutputFormatCmdString = '\x1B{0}*{1}VTPO\r'.format(OutputSelect, DigitalOutputFormatValues[value])
        self.__SetHelper('OutputFormat', DigitalOutputFormatCmdString, value, qualifier)

    def UpdateOutputFormat(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            self.__UpdateHelper('OutputFormat', '\x1b{0}VTPO\r'.format(qualifier['Output']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputFormat')

    def __MatchOutputFormat(self, match, tag):
        OutputFormatNames = {
            '0': 'Auto',
            '1': 'DVI',
            '2': 'HDMI RGB FULL',
            '3': 'HDMI RGB LIMITED',
            '5': 'HDMI YUV 444 LIMITED',
            '7': 'HDMI YUV 422 LIMITED',
        }

        output = match.group(1).decode()
        value = OutputFormatNames[match.group(2).decode()]
        self.WriteStatus('OutputFormat', value, {'Output': output})

    def SetOutputResolution(self, value, qualifier):

        OutputScalerRateValues = {
            '640x480 (60Hz)': '010',
            '800x600 (60Hz)': '011',
            '1024x768 (60Hz)': '012',
            '1280x768 (60Hz)': '013',
            '1280x800 (60Hz)': '014',
            '1280x1024 (60Hz)': '015',
            '1360x768 (60Hz)': '016',
            '1366x768 (60Hz)': '017',
            '1440x900 (60Hz)': '018',
            '1400x1050 (60Hz)': '019',
            '1600x900 (60Hz)': '020',
            '1680x1050 (60Hz)': '021',
            '1600x1200 (60Hz)': '022',
            '1920x1200 (60Hz)': '023',
            '480p (59.94Hz)': '024',
            '480p (60Hz)': '025',
            '576p (50Hz)': '026',
            '720p (25Hz)': '029',
            '720p (29.97Hz)': '030',
            '720p (30Hz)': '031',
            '720p (50Hz)': '032',
            '720p (59.94Hz)': '033',
            '720p (60Hz)': '034',
            '1080i (50Hz)': '035',
            '1080i (59.94Hz)': '036',
            '1080i (60Hz)': '037',
            '1080p (23.98Hz)': '038',
            '1080p (24Hz)': '039',
            '1080p (25Hz)': '040',
            '1080p (29.97Hz)': '041',
            '1080p (30Hz)': '042',
            '1080p (50Hz)': '043',
            '1080p (59.94Hz)': '044',
            '1080p (60Hz)': '045',
            '2048x1080 (23.98Hz)': '046',
            '2048x1080 (24Hz)': '047',
            '2048x1080 (25Hz)': '048',
            '2048x1080 (29.97Hz)': '049',
            '2048x1080 (30Hz)': '050',
            '2048x1080 (50Hz)': '051',
            '2048x1080 (59.94Hz)': '052',
            '2048x1080 (60Hz)': '053',
            '2048x1200 (60Hz)': '054',
            '2048x1536 (60Hz)': '055',
            '2560x1080 (60Hz)': '056',
            '2560x1440 (60Hz)': '057',
            '2560x1600 (60Hz)': '058',
            '3840x2160 (23.98Hz)': '059',
            '3840x2160 (24Hz)': '060',
            '3840x2160 (25Hz)': '061',
            '3840x2160 (29.97Hz)': '062',
            '3840x2160 (30Hz)': '063',
            '3840x2160 (50Hz)': '064',
            '3840x2160 (59.94Hz)': '065',
            '3840x2160 (60Hz)': '066',
            '4096x2160 (23.98Hz)': '069',
            '4096x2160 (24Hz)': '070',
            '4096x2160 (25Hz)': '071',
            '4096x2160 (29.97Hz)': '072',
            '4096x2160 (30Hz)': '073',
            '4096x2160 (50Hz)': '074',
            '4096x2160 (59.94Hz)': '075',
            '4096x2160 (60Hz)': '076',
            'Custom EDID 1': '201',
            'Custom EDID 2': '202',
            'Custom EDID 3': '203',
        }

        OutputScalerRateCmdString = '\x1B{0}RATE\r'.format(OutputScalerRateValues[value])
        self.__SetHelper('OutputResolution', OutputScalerRateCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        self.__UpdateHelper('OutputResolution', '\x1BRATE\r', value, qualifier)
        
    def __MatchOutputResolution(self, match, tag):
        OutputScalerRateNames = {
            '010': '640x480 (60Hz)',
            '011': '800x600 (60Hz)',
            '012': '1024x768 (60Hz)',
            '013': '1280x768 (60Hz)',
            '014': '1280x800 (60Hz)',
            '015': '1280x1024 (60Hz)',
            '016': '1360x768 (60Hz)',
            '017': '1366x768 (60Hz)',
            '018': '1440x900 (60Hz)',
            '019': '1400x1050 (60Hz)',
            '020': '1600x900 (60Hz)',
            '021': '1680x1050 (60Hz)',
            '022': '1600x1200 (60Hz)',
            '023': '1920x1200 (60Hz)',
            '024': '480p (59.94Hz)',
            '025': '480p (60Hz)',
            '026': '576p (50Hz)',
            '029': '720p (25Hz)',
            '030': '720p (29.97Hz)',
            '031': '720p (30Hz)',
            '032': '720p (50Hz)',
            '033': '720p (59.94Hz)',
            '034': '720p (60Hz)',
            '035': '1080i (50Hz)',
            '036': '1080i (59.94Hz)',
            '037': '1080i (60Hz)',
            '038': '1080p (23.98Hz)',
            '039': '1080p (24Hz)',
            '040': '1080p (25Hz)',
            '041': '1080p (29.97Hz)',
            '042': '1080p (30Hz)',
            '043': '1080p (50Hz)',
            '044': '1080p (59.94Hz)',
            '045': '1080p (60Hz)',
            '046': '2048x1080 (23.98Hz)',
            '047': '2048x1080 (24Hz)',
            '048': '2048x1080 (25Hz)',
            '049': '2048x1080 (29.97Hz)',
            '050': '2048x1080 (30Hz)',
            '051': '2048x1080 (50Hz)',
            '052': '2048x1080 (59.94Hz)',
            '053': '2048x1080 (60Hz)',
            '054': '2048x1200 (60Hz)',
            '055': '2048x1536 (60Hz)',
            '056': '2560x1080 (60Hz)',
            '057': '2560x1440 (60Hz)',
            '058': '2560x1600 (60Hz)',
            '059': '3840x2160 (23.98Hz)',
            '060': '3840x2160 (24Hz)',
            '061': '3840x2160 (25Hz)',
            '062': '3840x2160 (29.97Hz)',
            '063': '3840x2160 (30Hz)',
            '064': '3840x2160 (50Hz)',
            '065': '3840x2160 (59.94Hz)',
            '066': '3840x2160 (60Hz)',
            '069': '4096x2160 (23.98Hz)',
            '070': '4096x2160 (24Hz)',
            '071': '4096x2160 (25Hz)',
            '072': '4096x2160 (29.97Hz)',
            '073': '4096x2160 (30Hz)',
            '074': '4096x2160 (50Hz)',
            '075': '4096x2160 (59.94Hz)',
            '076': '4096x2160 (60Hz)',
            '201': 'Custom EDID 1',
            '202': 'Custom EDID 2',
            '203': 'Custom EDID 3',
        }

        value = OutputScalerRateNames[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetPrinter(self, value, qualifier):

        PrinterStates = {
            'Disable' : 0,
            'Enable' : 1
        }

        PrinterCommands = '\x1BE{0}PRTR\r'.format(PrinterStates[value])
        self.__SetHelper('Printer', PrinterCommands, value, qualifier)

    def UpdatePrinter(self, value, qualifier):

        PrinterQuery = '\x1BEPRTR\r'
        self.__UpdateHelper('Printer', PrinterQuery, value, qualifier)
        
    def __MatchPrinter(self, match, tag):
        PrinterStates = {
            '0' : 'Disable',
            '1' : 'Enable'
        }

        value = PrinterStates[match.group(1).decode()]
        self.WriteStatus('Printer', value, None)

    def SetPrinterQuantity(self, value, qualifier):

        PrinterQuantityStates = int(value)
        if 1 <= PrinterQuantityStates <= 50:
            PrinterQuantityCommands = '\x1BQ{0}PRTR\r'.format(value)
            self.__SetHelper('PrinterQuantity', PrinterQuantityCommands, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPrinterQuantity')

    def UpdatePrinterQuantity(self, value, qualifier):

        PrinterQuantityQuery = '\x1BQPRTR\r'
        self.__UpdateHelper('PrinterQuantity', PrinterQuantityQuery, value, qualifier)
        
    def __MatchPrinterQuantity(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('PrinterQuantity', value, None)

    def SetRecallImageCommand(self, value, qualifier):

        LocationValues = {
            'Internal Flash' : '0',
            'USB Drive' : '1',
        }

        LocationSelect = LocationValues[value]
        cmdString = qualifier['Filename']
        if cmdString and 1 <= len(cmdString) <= 4096:
            self.__SetHelper('RecallImageCommand', '\x1B{0}*{1}RF\r'.format(LocationSelect, cmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallImageCommand')

    def SetSaveImageCommand(self, value, qualifier):

        LocationValues = {
            'Internal Flash' : '0',
            'USB Drive'     : '1',
            'External'       : '0'
        }

        LocationSelect = LocationValues[value]
        cmdString = qualifier['Filename']
        if cmdString:
            if value  == 'External':
                self.__SetHelper('SaveImageCommand', '\x1B{0}*/shares/{1}MF\r'.format(LocationSelect, cmdString.replace(' ', '')), value, qualifier)
            else:
                self.__SetHelper('SaveImageCommand', '\x1B{0}*/Graphics/{1}MF\r'.format(LocationSelect, cmdString.replace(' ', '')), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveImageCommand')

    def SetScreenSaver(self, value, qualifier):

        ScreenSaverValues = {
            'Black Screen' : '1',
            'Blue Screen'  : '2',
            'User File'    : '3',
        }

        ScreenSaverCmdString = '\x1BM{0}SSAV\r'.format(ScreenSaverValues[value])
        self.__SetHelper('ScreenSaver', ScreenSaverCmdString, value, qualifier)

    def UpdateScreenSaver(self, value, qualifier):

        self.__UpdateHelper('ScreenSaver', '\x1BMSSAV\r', value, qualifier)

    def __MatchScreenSaver(self, match, tag):
        ScreenSaverNames = {
            '1' : 'Black Screen',
            '2' : 'Blue Screen',
            '3' : 'User File',
        }

        value = ScreenSaverNames[match.group(1).decode()]
        self.WriteStatus('ScreenSaver', value, None)

    def SetScreenSaverTimeout(self, value, qualifier):

        if 0 <= value <= 501:
            ScreenSaverTimeoutCmdString = '\x1BT{0}SSAV\r'.format(value)
            self.__SetHelper('ScreenSaverTimeout', ScreenSaverTimeoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverTimeout')

    def UpdateScreenSaverTimeout(self, value, qualifier):

        self.__UpdateHelper('ScreenSaverTimeout', '\x1BTSSAV\r', value, qualifier)

    def __MatchScreenSaverTimeout(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('ScreenSaverTimeout', value, None)

    def SetSwitchingEffect(self, value, qualifier):

        SwitchEffectStates = {
            'Cut'  : 0,
            'Fade' : 1,
            'Low Latency': 4
        }

        SwitchCommand = '\x1BU1*{0}SWEF\r'.format(SwitchEffectStates[value])
        self.__SetHelper('SwitchingEffect', SwitchCommand, value, qualifier)

    def UpdateSwitchingEffect(self, value, qualifier):

        SwitchEffectQuery = '\x1BU1SWEF\r'
        self.__UpdateHelper('SwitchingEffect', SwitchEffectQuery, value, qualifier)
        
    def __MatchSwitchingEffect(self, match, tag):
        SwitchEffectStates = {
            '0' : 'Cut',
            '1' : 'Fade',
            '4': 'Low Latency'
        }

        value = SwitchEffectStates[match.group(1).decode()]
        self.WriteStatus('SwitchingEffect', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureQuery = '\x1B20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureQuery, value, qualifier)

    def __MatchTemperature(self, match, tag):
        value = float(match.group(1))
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        TestPatternStates = {
            'Off' : 0,
            'Crop' : 1,
            'Alternating Pixels' : 2,
            'Crosshatch' : 3,
            'Color Bars' : 4,
            'Grayscale' : 5,
            'Audio Test' : 6
        }

        TestPatternCommand = '\x1B{0}TEST\r'.format(TestPatternStates[value])
        self.__SetHelper('TestPattern', TestPatternCommand, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternQuery = '\x1BTEST\r'
        self.__UpdateHelper('TestPattern', TestPatternQuery, value, qualifier)

    def __MatchTestPattern(self, match, tag):
        TestPatternStates = {
            0 : 'Off',
            1 : 'Crop',
            2 : 'Alternating Pixels',
            3 : 'Crosshatch',
            4 : 'Color Bars',
            5 : 'Grayscale',
            6 : 'Audio Test',
        }

        value = TestPatternStates[int(match.group(1).decode())]
        self.WriteStatus('TestPattern', value, None)

    def SetTextSize(self, value, qualifier):

        if 8 <= value <= 127:
            TextSizeCommand = '\x1B{0}TXSZ\r'.format(value)
            self.__SetHelper('TextSize', TextSizeCommand, value, qualifier)
        else:    
            self.Discard('Invalid Command for SetTextSize')

    def UpdateTextSize(self, value, qualifier):

        TextSizeQuery = '\x1BTXSZ\r'
        self.__UpdateHelper('TextSize', TextSizeQuery, value, qualifier)

    def __MatchTextSize(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('TextSize', value, None)

    def UpdateTotalPixel(self, value, qualifier):

        TotalPixelQuery = '\x1BTPIX\r'
        self.__UpdateHelper('TotalPixel', TotalPixelQuery, value, qualifier)

    def __MatchTotalPixel(self, match, tag):
        value = int(match.group(2).decode())
        self.WriteStatus('TotalPixel', value, None)

    def SetUSBDevice(self, value, qualifier):

        USBDeviceValues = {
            'Disable': '0',
            'Enable' : '1'
        }

        DeviceSelect = qualifier['Device']
        if DeviceSelect == 'All':
            DeviceSelect = '0'
        if 0 <= int(DeviceSelect) <= 32:
            USBDeviceCmdString = '\x1B{0}*{1}ADEV\r'.format(DeviceSelect, USBDeviceValues[value])
            self.__SetHelper('USBDevice', USBDeviceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBDevice')

    def UpdateUSBDevice(self, value, qualifier):

        DeviceSelect = qualifier['Device']
        if DeviceSelect == 'All':
            DeviceSelect = '0'
        if 0 <= int(DeviceSelect) <= 32:
            self.__UpdateHelper('USBDevice', '\x1B{0}ADEV\r'.format(DeviceSelect), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUSBDevice')

    def __MatchUSBDevice(self, match, tag):
        USBDeviceNames = {
            '0' : 'Disable',
            '1' : 'Enable'
        }

        value = USBDeviceNames[match.group(2).decode()]
        DeviceSelect = match.group(1).decode()
        if DeviceSelect == '0':
            DeviceSelect = 'All'
        qualifier = {'Device':DeviceSelect}
        self.WriteStatus('USBDevice', value, qualifier)

    def SetVerticalShift(self, value, qualifier):

        if -32768 <= value <= 32768:
            VerticalShiftCommand = '\x1B{0}VCTR\r'.format(value)
            self.__SetHelper('VerticalShift', VerticalShiftCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalShift')        

    def UpdateVerticalShift(self, value, qualifier):

        VerticalQuery = '\x1BVCTR\r'
        self.__UpdateHelper('VerticalShift', VerticalQuery, value, qualifier)

    def __MatchVerticalShift(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('VerticalShift', value, None)

    def SetVerticalSize(self, value, qualifier):

        if 10 <= value <= 32768:
            VerticalSizeCommand = '\x1B{0}VSIZ\r'.format(value)
            self.__SetHelper('VerticalSize', VerticalSizeCommand, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSize')

    def UpdateVerticalSize(self, value, qualifier):

        VerticalSizeQuery = '\x1BVSIZ\r'
        self.__UpdateHelper('VerticalSize', VerticalSizeQuery, value, qualifier)

    def __MatchVerticalSize(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('VerticalSize', value, None)

    def SetVideoMute(self, value, qualifier):

        OutputValues = {
            'All Outputs': '0',
            '1'         : '1',
            '2'         : '2'
        }

        VideoMuteStates = {
            'On'            : '1',
            'On with Sync'  : '2',
            'Off'           : '0'
        }

        OutputSelect = qualifier['Output']
        VideoMuteCommand = '{0}*{1}B'.format(OutputValues[OutputSelect], VideoMuteStates[value])
        self.__SetHelper('VideoMute', VideoMuteCommand, value, qualifier)
        
    def __MatchVideoMute(self, match, tag):
        VideoMuteStates = {
            '0' : 'Off',
            '1' : 'On',
            '2' : 'On with Sync'
        }

        OutputNames = {
            '0' : 'All Outputs',
            '1' : '1',
            '2' : '2'
        }

        value = VideoMuteStates[match.group(2).decode()]
        qualifier = {'Output':OutputNames[match.group(1).decode()]}
        self.WriteStatus('VideoMute', value, qualifier)

    def SetViewSettings(self, value, qualifier):

        CommandString = '\x1BMSHW\r'
        self.__SetHelper('ViewSettings', CommandString, value, qualifier)

    def SetWhiteboardBlackboard(self, value, qualifier):

        ValueStateValues = {
            'Whiteboard' : '\x1B1WHBD\r', 
            'Blackboard' : '\x1B2WHBD\r', 
            'Off' : '\x1B0WHBD\r'
        }

        WhiteboardBlackboardCmdString = ValueStateValues[value]
        self.__SetHelper('WhiteboardBlackboard', WhiteboardBlackboardCmdString, value, qualifier)

    def UpdateWhiteboardBlackboard(self, value, qualifier):

        WhiteboardBlackboardCmdString = '\x1BWHBD\r'
        self.__UpdateHelper('WhiteboardBlackboard', WhiteboardBlackboardCmdString, value, qualifier)

    def __MatchWhiteboardBlackboard(self, match, tag):

        ValueStateValues = {
            '1' : 'Whiteboard', 
            '2' : 'Blackboard', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WhiteboardBlackboard', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
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

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number',
            'E10': 'Invalid command',
            'E11': 'Invalid preset number',
            'E12': 'Invalid port number',
            'E13': 'Invalid parameter',
            'E14': 'Invalid for this configuration',
            'E17': 'Invalid command for signal type',
            'E22': 'Busy',
            'E24': 'Privilege violation',
            'E25': 'Device not present',
            'E26': 'Maximum number of connectors exceeded',
            'E28': 'Bad filename/File not found',
            'E33': 'Bad file type for logo'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ value]) 

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.EchoDisabled = True
        self.VerboseDisabled = True

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
