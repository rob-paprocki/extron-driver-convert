# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, match, search

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

        self.Models = {
            'MGP 641': self.extr_18_5158_4K,
            'MGP 641 xi': self.extr_18_5158_4K,
            'MGP 641 xi 5K': self.extr_18_5158_5K,
            'MGP 641 xi 5K SDI': self.extr_18_5158_5K,
            'MGP 641 xi SDI': self.extr_18_5158_4K
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AESAudioChannel': {'Parameters':['Input'], 'Status': {}},
            'AESAudioGroup': {'Parameters':['Input'], 'Status': {}},
            'AnnotationColor': {'Parameters':['Red','Green','Blue'], 'Status': {}},
            'AnnotationEditFunctions': { 'Status': {}},
            'AnnotationObjectFill': { 'Status': {}},
            'AnnotationType': { 'Status': {}},
            'AudioInput': { 'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AutoImage': {'Parameters':['Window'], 'Status': {}},
            'AutoLayoutMode': { 'Status': {}},
            'BackgroundRecallCommand': {'Parameters':['Background'], 'Status': {}},
            'EraserSize': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': {'Parameters':['Window'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Output'], 'Status': {}},
            'ImageHorizontalShift': {'Parameters':['Window'], 'Status': {}},
            'ImageHorizontalSize': {'Parameters':['Window'], 'Status': {}},
            'ImageVerticalShift': {'Parameters':['Window'], 'Status': {}},
            'ImageVerticalSize': {'Parameters':['Window'], 'Status': {}},
            'InputPresetRecall': {'Parameters':['Window'], 'Status': {}},
            'InputPresetSave': {'Parameters':['Window'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'InputVideoFormat': {'Parameters':['Input'], 'Status': {}},
            'LineWeight': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'QuickCapture': { 'Status': {}},
            'SaveImageCommand': {'Parameters':['Location'], 'Status': {}},
            'ScreenSaverMode': { 'Status': {}},
            'Temperature': {'Parameters':['Scale'], 'Status': {}},
            'TestPattern': { 'Status': {}},
            'VideoMute': {'Status': {}},
            'WindowHorizontalShift': {'Parameters':['Window'], 'Status': {}},
            'WindowHorizontalSize': {'Parameters':['Window'], 'Status': {}},
            'WindowMute': {'Parameters':['Window'], 'Status': {}},
            'WindowBorderStyle': {'Parameters':['Window'], 'Status': {}},
            'WindowPresetRecall': { 'Status': {}},
            'WindowPresetSave': { 'Status': {}},
            'WindowPresetRecalledStatus': { 'Status': {}},
            'WindowPriorityCommand': {'Parameters':['Priority'], 'Status': {}},
            'WindowPriorityStatus': { 'Status': {}},
            'WindowVerticalShift': {'Parameters':['Window'], 'Status': {}},
            'WindowVerticalSize': {'Parameters':['Window'], 'Status': {}}
        }

        self.VerboseDisabled = True
        self.NumberOfWindow = 4
        self.EchoDisabled = True
        
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Aesc(\d+)\*(\d+)\r\n'), self.__MatchAESAudioChannel, None)
            self.AddMatchString(compile(b'Aesg(\d+)\*(\d+)\r\n'), self.__MatchAESAudioGroup, None)
            self.AddMatchString(compile(b'Fill([0-3]{1,2})\r\n'), self.__MatchAnnotationObjectFill, None)
            self.AddMatchString(compile(b'Draw([0-9]{1,2})\r\n'), self.__MatchAnnotationType, None)
            self.AddMatchString(compile(b'In(\d+)Aud\r\n'), self.__MatchAudioInput, None)
            self.AddMatchString(compile(b'Amt([1-3])\*(0|1)\r\n'), self.__MatchAudioMute, 'Single')
            self.AddMatchString(compile(b'Amt(0|1)\r\n'), self.__MatchAudioMute, 'All')
            self.AddMatchString(compile(b'Ausw([01])\r\n'), self.__MatchAutoLayoutMode, None)
            self.AddMatchString(compile(b'Ersr([0-9]{1,3})\r\n'), self.__MatchEraserSize, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz(\d+)\*(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'HdcpE(\d+)\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI00\*([012,]+)\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO00\*([012,]+)\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'HdcpI(\d+)\*([012])\r\n'), self.__MatchHDCPInputStatus, 'Unsolicited')
            self.AddMatchString(compile(b'HdcpO([12])\*([012])\r\n'), self.__MatchHDCPOutputStatus, 'Unsolicited')
            self.AddMatchString(compile(b'HctrI(\d+)\*([+-]?\d+)\r\n'), self.__MatchImageHorizontalShift, None)
            self.AddMatchString(compile(b'HsizI(\d+)\*(\d{5})\r\n'), self.__MatchImageHorizontalSize, None)
            self.AddMatchString(compile(b'VctrI(\d+)\*([+-]?\d+)\r\n'), self.__MatchImageVerticalShift, None)
            self.AddMatchString(compile(b'VsizI(\d+)\*(\d{5})\r\n'), self.__MatchImageVerticalSize, None)
            
            self.AddMatchString(compile(b'In00 (0|1)\*(0|1)\*(0|1)\*(0|1)\*(0|1)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Ityp(\d+)\*([1-2])\r\n'), self.__MatchInputVideoFormat, None)
            self.AddMatchString(compile(b'Lnwt([0-9]{1,2})\r\n'), self.__MatchLineWeight, None)
            self.AddMatchString(compile(b'Rate(\d{1,2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(compile(b'SsavM(1|2)\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(compile(b'20Stat ([0-9.]+)C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Test([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vmt99\*([012])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Vmt0([1-4])\*([01])\r\n'), self.__MatchWindowMute, None)

            self.AddMatchString(compile(b'WndwB(\d+)\*(\d+)\r\n'), self.__MatchWindowBorderStyle, None)
            self.AddMatchString(compile(b'HctrW(\d+)\*([+-]?\d+)\r\n'), self.__MatchWindowHorizontalShift, None)
            self.AddMatchString(compile(b'HsizW(\d+)\*(\d{5})\r\n'), self.__MatchWindowHorizontalSize, None)
            self.AddMatchString(compile(b'PrstL1\*(\d{3})\r\n'), self.__MatchWindowPresetRecalled, None)
            self.AddMatchString(compile(b'1Rpr(\d+)\r\n'), self.__MatchWindowPresetRecalled, None)
            self.AddMatchString(compile(b'Pri(([1-4])\*([1-4])\*([1-4])\*([1-4]))\r\n'), self.__MatchWindowPriorityStatus, None)
            self.AddMatchString(compile(b'VctrW(\d+)\*([+-]?\d+)\r\n'), self.__MatchWindowVerticalShift, None)
            self.AddMatchString(compile(b'VsizW(\d+)\*(\d{5})\r\n'), self.__MatchWindowVerticalSize, None)
            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)


    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetAESAudioChannel(self, value, qualifier):

        WindowValues = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            'Background': '99',
            'All': '0'
            }
        if qualifier['Input'] in WindowValues and value in ['1', '2']:
            self.__SetHelper('AESAudioChannel', 'w{0}*{1}AESC\r'.format(WindowValues[qualifier['Input']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAESAudioChannel')
            
    def UpdateAESAudioChannel(self, value, qualifier):

        WindowValues = {
                    '1'  : '1',
                    '2'  : '2',
                    '3'  : '3',
                    '4'  : '4',
                    'Background': '99',
                    'All': '0'
                    }
        if qualifier['Input'] in WindowValues:
            self.__UpdateHelper('AESAudioChannel', 'w{0}AESC\r'.format(WindowValues[qualifier['Input']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAESAudioChannel')

    def __MatchAESAudioChannel(self, match, qualifier):

        input_ = str(int(match.group(1).decode()))
        value = str(int(match.group(2).decode()))
        if 1 <= int(input_) <= 4:
            self.WriteStatus('AESAudioChannel', value, {'Input': input_})

    def SetAESAudioGroup(self, value, qualifier):

        WindowValues = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            'Background': '99',
            'All': '0'
            }
        if qualifier['Input'] in WindowValues and value in ['1', '2', '3', '4']:
            self.__SetHelper('AESAudioGroup', 'w{0}*{1}AESG\r'.format(WindowValues[qualifier['Input']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAESAudioGroup')
            
    def UpdateAESAudioGroup(self, value, qualifier):

        WindowValues = {
                    '1'  : '1',
                    '2'  : '2',
                    '3'  : '3',
                    '4'  : '4',
                    'Background': '99',
                    'All': '0'
                    }
        if qualifier['Input'] in WindowValues:
            self.__UpdateHelper('AESAudioGroup', 'w{0}AESG\r'.format(WindowValues[qualifier['Input']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAESAudioGroup')

    def __MatchAESAudioGroup(self, match, qualifier):

        input_ = str(int(match.group(1).decode()))
        value = str(int(match.group(2).decode()))
        if 1 <= int(input_) <= 4:
            self.WriteStatus('AESAudioGroup', value, {'Input': input_})

    def SetAnnotationColor(self, value, qualifier):

        Red = qualifier['Red']
        Green = qualifier['Green']
        Blue = qualifier['Blue']

        if 0 <= Red <= 3 and 0 <= Green <= 3 and 0 <= Blue <= 3:
            ColorValue = '{0:02b}{1:02b}{2:02b}'.format(Red, Green, Blue)
            AnnotationColorCmdString = '\x1B1*{0}ACOL\r'.format(ColorValue)
            self.__SetHelper('AnnotationColor', AnnotationColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnnotationColor')

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
            'Vector Line' : 4,
            'Arrow Line' : 5,
            'Ellipse' : 6,
            'Rectangle' : 7,
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
            '04' : 'Vector Line',
            '05' : 'Arrow Line',
            '06' : 'Ellipse',
            '07' : 'Rectangle',
        }
        
        value = AnnotationTypeStates[match.group(1).decode()]
        self.WriteStatus('AnnotationType', value, None)

    def SetAudioInput(self, value, qualifier):

        WindowValues = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            'Background': '99'
        }
        if value in WindowValues:
            self.__SetHelper('AudioInput', '{0}$'.format(WindowValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')
            
    def UpdateAudioInput(self, value, qualifier):

        self.__UpdateHelper('AudioInput', '$', value, qualifier)

    def __MatchAudioInput(self, match, qualifier):

        value = str(int(match.group(1).decode()))
        if value == '99':
            self.WriteStatus('AudioInput', 'Background', None)
        elif 1 <= int(value) <= 4:
            self.WriteStatus('AudioInput', value, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'HDMI' : '1', 
            'TP' : '2', 
            'Analog' : '3', 
            'All' : '99'
        }

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        output_val = qualifier['Output']
        if output_val in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputStates[output_val], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'HDMI' : '1', 
            'TP' : '2', 
            'Analog' : '3', 
        }
        output_val = qualifier['Output']
        if output_val in OutputStates:
            AudioMuteCmdString = '{}*Z'.format(OutputStates[output_val])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '1': 'HDMI', 
            '2': 'TP', 
            '3': 'Analog', 
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if tag == 'All':
            self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output' : 'HDMI'})
            self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output' : 'TP'})
            self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output' : 'Analog'})
        else:
            qualifier = {}
            qualifier['Output'] = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute': '0',
            'Execute and Follow': '2',
            'Execute and Fill': '1'
        }

        if value in ValueStateValues:
            window = qualifier['Window']
            if 1 <= int(window) <= self.NumberOfWindow:
                self.__SetHelper('AutoImage', '{0}*{1}A'.format(window, ValueStateValues[value]), value, qualifier)
            else:
                self.Discard('Invalid Command for SetAutoImage')
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetAutoLayoutMode(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if value in ValueStateValues:
            AutoLayoutModeCmdString = 'w{}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoLayoutMode', AutoLayoutModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoLayoutMode')

    def UpdateAutoLayoutMode(self, value, qualifier):

        AutoLayoutModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoLayoutMode', AutoLayoutModeCmdString, value, qualifier)

    def __MatchAutoLayoutMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Enable',
            '0' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoLayoutMode', value, None)

    def SetBackgroundRecallCommand(self, value, qualifier):

        ValueStateValues = {
            'All Windows' : '0', 
            'Window 1' : '1', 
            'Window 2' : '2', 
            'Window 3' : '3', 
            'Window 4' : '4', 
            'Foreground' : '98', 
            'Background' : '99'
        }

        logo_string = qualifier['Background']
        if value in ValueStateValues and logo_string:
            BackgroundRecallCommandCmdString = 'WE{}*{}LOGO\r'.format(ValueStateValues[value], logo_string)
            self.__SetHelper('BackgroundRecallCommand', BackgroundRecallCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundRecallCommand')

    def SetEraserSize(self, value = 8, qualifier = None):

        if 1 <= value <= 63:
            EraserSizeCommand = '\x1B{0}ERSR\r'.format(value)
            self.__SetHelper('EraserSize', EraserSizeCommand, value, qualifier)
        else:    
            self.Discard('Invalid Command for SetEraserSize')

    def UpdateEraserSize(self, value, qualifier):

        EraserSizeQuery = '\x1BERSR\r'
        self.__UpdateHelper('EraserSize', EraserSizeQuery, value, qualifier)
        
    def __MatchEraserSize(self, match, tag):
        
        value = int(match.group(1).decode())
        self.WriteStatus('EraserSize', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState={
            'Mode 1' :'1',
            'Mode 2' :'2',
            'Off'    :'0'
            }

        if value in ExecutiveModeState:
            self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName={
            '1':'Mode 1',
            '2':'Mode 2',
            '0':'Off',
            }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1).decode()], None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'Off':'0',
            'On':'1',
            }
        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and value in FreezeState:
            self.__SetHelper('Freeze', '{0}*{1}f'.format(window, FreezeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('Freeze', '{0}F'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, qualifier):

        FreezeName={
            '0':'Off',
            '1':'On',
            }
        value = FreezeName[match.group(2).decode()]
        window = str(int(match.group(1).decode()))
        if 1 <= int(window) <= 4:
            self.WriteStatus('Freeze', value, {'Window':window})

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        HDCPInputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }

        if value in ValueStateValues and qualifier['Input'] in HDCPInputStates:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(HDCPInputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }
        if qualifier['Input'] in HDCPInputStates:
            HDCPInputAuthorizationCmdString = 'wE{}HDCP\r'.format(HDCPInputStates[qualifier['Input']])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        HDCPInputValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }

        qualifier = {'Input': HDCPInputValues[str(int(match.group(1).decode()))]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Device Detected',
            '2' : 'Source Detected with HDCP',
            '1' : 'Source Detected without HDCP'
        }
        if tag == 'Unsolicited':
            inpt = match.group(1).decode()
            if inpt == '99':
                self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group(2).decode()], {'Input': 'Background'})
            elif 1 <= int(inpt) <= 4:
                self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group(2).decode()], {'Input': inpt})
        else:
            results = match.group(1).decode()
            results = results.split(',')
            for index, value in enumerate(results):
                if index == 4:
                    self.WriteStatus('HDCPInputStatus', ValueStateValues[value], {'Input': 'Background'})
                else:
                    self.WriteStatus('HDCPInputStatus', ValueStateValues[value], {'Input': str(index + 1)})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if qualifier['Output'] in ['1A', '1B']:
            HDCPOutputStatusCmdString = 'wOHDCP\r'
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Sink Device Detected',
            '2' : 'Sink Detected with HDCP',
            '1' : 'Sink Detected without HDCP'
        }

        if tag == 'Unsolicited':
            output = match.group(1).decode()
            if output == '1':
                self.WriteStatus('HDCPOutputStatus', ValueStateValues[match.group(2).decode()], {'Output': '1A'})
            else:
                self.WriteStatus('HDCPOutputStatus', ValueStateValues[match.group(2).decode()], {'Output': '1B'})
        else:        
            results = match.group(1).decode()
            results = results.split(',')
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[results[0]], {'Output': '1A'})
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[results[1]], {'Output': '1B'})

    def SetImageHorizontalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.__SetHelper('ImageHorizontalShift', 'wI{0}*{1}HCTR\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageHorizontalShift')

    def UpdateImageHorizontalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageHorizontalShift', 'wI{0}HCTR\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageHorizontalShift')

    def __MatchImageHorizontalShift(self, match, tag):

        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.WriteStatus('ImageHorizontalShift', value, {'Window':window})

    def SetImageHorizontalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.__SetHelper('ImageHorizontalSize', 'wI{0}*{1}HSIZ\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageHorizontalSize')

    def UpdateImageHorizontalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageHorizontalSize', 'wI{0}HSIZ\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageHorizontalSize')

    def __MatchImageHorizontalSize(self, match, tag):
        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.WriteStatus('ImageHorizontalSize', value, {'Window':window})

    def SetImageVerticalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.__SetHelper('ImageVerticalShift', 'wI{0}*{1}VCTR\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageVerticalShift')

    def UpdateImageVerticalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageVerticalShift', 'wI{0}VCTR\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageVerticalShift')

    def __MatchImageVerticalShift(self, match, tag):

        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.WriteStatus('ImageVerticalShift', value, {'Window':window})

    def SetImageVerticalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.__SetHelper('ImageVerticalSize', 'wI{0}*{1}VSIZ\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageVerticalSize')

    def UpdateImageVerticalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('ImageVerticalSize', 'wI{0}VSIZ\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageVerticalSize')

    def __MatchImageVerticalSize(self, match, tag):

        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.WriteStatus('ImageVerticalSize', value, {'Window':window})

    def SetInputPresetRecall(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 1 <= int(value) <= 128:
            self.__SetHelper('InputPresetRecall', '2*{0}*{1}.'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 1 <= int(value) <= 128:   
            self.__SetHelper('InputPresetSave', '2*{0}*{1},'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'W0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputStates = {
            1: '1', 
            2: '2', 
            3: '3', 
            4: '4', 
            5: 'Background'
        }

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Inactive'
        }
        
        for i in range(1,6):
            qualifier = {}
            qualifier['Input'] = InputStates[i]
            value = ValueStateValues[match.group(i).decode()]
            self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetInputVideoFormat(self, value, qualifier):

        WindowValues = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            'Background': '99',
            'All': '0'
            }
        
        ValueStateValues = {
            'HDMI/DVI': '1',
            'SDI': '2'
        }
        if qualifier['Input'] in WindowValues and value in ValueStateValues:
            self.__SetHelper('InputVideoFormat', '{0}*{1}\\'.format(WindowValues[qualifier['Input']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputVideoFormat')
            
    def UpdateInputVideoFormat(self, value, qualifier):

        WindowValues = {
                    '1'  : '1',
                    '2'  : '2',
                    '3'  : '3',
                    '4'  : '4',
                    'Background': '99',
                    'All': '0'
                    }
        if qualifier['Input'] in WindowValues:
            self.__UpdateHelper('InputVideoFormat', '{0}\\'.format(WindowValues[qualifier['Input']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputVideoFormat')

    def __MatchInputVideoFormat(self, match, qualifier):

        ValueStateValues = {
            '1': 'HDMI/DVI',
            '2': 'SDI'
        }
        input_ = str(int(match.group(1).decode()))
        value = str(int(match.group(2).decode()))
        if 1 <= int(input_) <= 4:
            self.WriteStatus('InputVideoFormat', ValueStateValues[value], {'Input': input_})

    def SetLineWeight(self, value, qualifier):

        if 1 <= value <= 63:
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

    def SetOutputResolution(self, value, qualifier):

        if value in self.OutputResolution:
            OutputResolutionCmdString = 'w{}RATE\r'.format(self.OutputResolution[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'wRATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        value = self.OutputResolutionStatus[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetQuickCapture(self, value, qualifier):

        QuickCaptureCommand = '\x1B0*/Graphics/temp.bmpMF\r'
        self.__SetHelper('QuickCapture', QuickCaptureCommand, value, qualifier)

    def SetSaveImageCommand(self, value, qualifier):

        LocationValues = {
            'Internal Flash' : '0',
            'USB Drive'     : '2',
            'External'       : '0'
        }

        LocationSelect = LocationValues[value]
        cmdString = qualifier['Location']
        if cmdString:
            if value  == 'External':
                self.__SetHelper('SaveImageCommand', '\x1B{0}*/shares/{1}MF\r'.format(LocationSelect, cmdString.replace(' ', '')), value, qualifier)
            elif value == 'USB Drive':
                self.__SetHelper('SaveImageCommand', '\x1B{0}*/{1}MF\r'.format(LocationSelect, cmdString.replace(' ', '')), value, qualifier)
            else:
                self.__SetHelper('SaveImageCommand', '\x1B{0}*/Graphics/{1}MF\r'.format(LocationSelect, cmdString.replace(' ', '')), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveImageCommand')

    def SetScreenSaverMode(self, value, qualifier):

        ValueStateValues = {
            'Black Screen': '1', 
            'Blue Screen':  '2'
        }

        if value in ValueStateValues:
            ScreenSaverModeCmdString = 'WM{}SSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverMode')

    def UpdateScreenSaverMode(self, value, qualifier):

        ScreenSaverModeCmdString = 'WMSSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Black Screen', 
            '2' : 'Blue Screen'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverMode', value, None)

    def UpdateTemperature(self, value, qualifier):

        if qualifier['Scale'] in ('Fahrenheit', 'Celsius'):
            self.__UpdateHelper('Temperature', 'w20STAT\r', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')
            
    def __MatchTemperature(self, match, qualifier):
        degrees_celsius = float(match.group(1).decode())
        self.WriteStatus('Temperature', round(9.0 / 5.0 * degrees_celsius + 32, 2), {'Scale': 'Fahrenheit'}) 
        
        self.WriteStatus('Temperature', round(degrees_celsius, 2), {'Scale': 'Celsius'})   

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0', 
            'Crop' : '1', 
            'Alternating Pixels' : '2', 
            'Crosshatch' : '3', 
            'Color Bars' : '4', 
            'Grayscale' : '5', 
            'Audio Test' : '6'
        }
        if value in ValueStateValues:
            self.__SetHelper('TestPattern', 'w{}TEST\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        self.__UpdateHelper('TestPattern', 'wTEST\r', value, qualifier)

    def __MatchTestPattern(self, match, qualifier):
        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'Crop', 
            '2' : 'Alternating Pixels', 
            '3' : 'Crosshatch', 
            '4' : 'Color Bars', 
            '5' : 'Grayscale', 
            '6' : 'Audio Test'
        }
        self.WriteStatus('TestPattern', ValueStateValues[match.group(1).decode()], None)

    def SetWindowMute(self, value, qualifier):
        window = int(qualifier['Window'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= window <= self.NumberOfWindow and value in ValueStateValues:
            WindowMuteCmdString = '{}*{}B'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowMute', WindowMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowMute')

    def UpdateWindowMute(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= self.NumberOfWindow:
            WindowMuteCmdString = '{}B'.format(window)
            self.__UpdateHelper('WindowMute', WindowMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowMute')

    def __MatchWindowMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        window = str(int(match.group(1).decode()))

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('WindowMute', value, {'Window':window})

    def SetVideoMute(self, value, qualifier):

        VideoMuteState={
            'On':           '1',
            'On with Sync': '2',
            'Off':          '0'
            }

        if value in VideoMuteState:
            self.__SetHelper('VideoMute', '99*{}B'.format(VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        self.__UpdateHelper('VideoMute', '99B', value, qualifier)

    def __MatchVideoMute(self, match, qualifier):
        
        VideoMuteName={
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
            }
        value = VideoMuteName[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetWindowBorderStyle(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= self.NumberOfWindow:
            if value == 'No Border':
                self.__SetHelper('WindowBorderStyle', 'wB{}*0WNDW\r'.format(window), value, qualifier)
            else:
                if 1 <= int(value) <= 128:
                    self.__SetHelper('WindowBorderStyle', 'wB{}*{}WNDW\r'.format(window, value), value, qualifier)
                else:
                    self.Discard('Invalid Command for SetWindowBorderStyle')
        else:
            self.Discard('Invalid Command for SetWindowBorderStyle')

    def UpdateWindowBorderStyle(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= self.NumberOfWindow:
            WindowBorderStyleCmdString = 'wB{}WNDW\r'.format(window)
            self.__UpdateHelper('WindowBorderStyle', WindowBorderStyleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowBorderStyle')

    def __MatchWindowBorderStyle(self, match, tag):

        window = int(match.group(1).decode())
        value = int(match.group(2).decode())

        if 1 <= window <= self.NumberOfWindow:
            if value == 0:
                self.WriteStatus('WindowBorderStyle', 'No Border', {'Window': str(window)})
            else:
                self.WriteStatus('WindowBorderStyle', str(value), {'Window': str(window)})

    def SetWindowHorizontalShift(self, value, qualifier):


        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.__SetHelper('WindowHorizontalShift', 'wW{0}*{1}HCTR\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalShift')
    def UpdateWindowHorizontalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowHorizontalShift', 'wW{0}HCTR\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalShift')

    def __MatchWindowHorizontalShift(self, match, tag):
        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.WriteStatus('WindowHorizontalShift', value, {'Window':window})

    def SetWindowHorizontalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.__SetHelper('WindowHorizontalSize', 'wW{0}*{1}HSIZ\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalSize')

    def UpdateWindowHorizontalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowHorizontalSize', 'wW{0}HSIZ\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalSize')

    def __MatchWindowHorizontalSize(self, match, tag):
        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.WriteStatus('WindowHorizontalSize', value, {'Window':window})

    def SetWindowPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:   
            self.__SetHelper('WindowPresetRecall', '1*{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetRecall')

    def UpdateWindowPresetRecalledStatus(self, value, qualifier):

        WindowPresetRecalledStatusCmdString = 'wL1PRST\r'
        self.__UpdateHelper('WindowPresetRecalledStatus', WindowPresetRecalledStatusCmdString, value, qualifier)

    def __MatchWindowPresetRecalled(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 128:
            self.WriteStatus('WindowPresetRecalledStatus', str(value), None)

    def SetWindowPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('WindowPresetSave', '1*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetSave')

    def SetWindowPriorityCommand(self, value, qualifier):

        priority_string = qualifier['Priority']
        if priority_string:
            WindowPriorityCommandCmdString = '{}~'.format(priority_string)
            self.__SetHelper('WindowPriorityCommand', WindowPriorityCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPriorityCommand')

    def UpdateWindowPriorityStatus(self, value, qualifier):

        WindowPriorityStatusCmdString = '~'
        self.__UpdateHelper('WindowPriorityStatus', WindowPriorityStatusCmdString, value, qualifier)

    def __MatchWindowPriorityStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('WindowPriorityStatus', value, None)

    def SetWindowVerticalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.__SetHelper('WindowVerticalShift', 'wW{0}*{1}VCTR\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalShift')

    def UpdateWindowVerticalShift(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowVerticalShift', 'wW{0}VCTR\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalShift')

    def __MatchWindowVerticalShift(self, match, tag):
        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and -32768 <= value <= 32768:
            self.WriteStatus('WindowVerticalShift', value, {'Window':window})

    def SetWindowVerticalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.__SetHelper('WindowVerticalSize', 'wW{0}*{1}VSIZ\r'.format(window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalSize')

    def UpdateWindowVerticalSize(self, value, qualifier):

        window = qualifier['Window']
        if 1 <= int(window) <= self.NumberOfWindow:
            self.__UpdateHelper('WindowVerticalSize', 'wW{0}VSIZ\r'.format(window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalSize')

    def __MatchWindowVerticalSize(self, match, tag):
        window = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        if 1 <= int(window) <= self.NumberOfWindow and 10 <= value <= 32768:
            self.WriteStatus('WindowVerticalSize', value, {'Window':window})

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

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Command not available for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found',
            '33' : 'Bad file type or size'
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
        
        self.VerboseDisabled = True
        self.EchoDisabled = True

    def extr_18_5158_4K(self):

        self.OutputResolution = {
            '640x480 (60 Hz)' : '10', 
            '800x600 (60 Hz)' : '11', 
            '1024x768 (60 Hz)' : '12', 
            '1280x768 (60 Hz)' : '13', 
            '1280x800 (60 Hz)' : '14', 
            '1280x1024 (60 Hz)' : '15', 
            '1360x768 (60 Hz)' : '16', 
            '1366x768 (60 Hz)' : '17', 
            '1440x900 (60 Hz)' : '18', 
            '1440x1050 (60 Hz)' : '19', 
            '1600x900 (60 Hz)' : '20', 
            '1680x1050 (60 Hz)' : '21', 
            '1600x1200 (60 Hz)' : '22', 
            '1920x1200 (60 Hz)' : '23', 
            '480p (59.94 Hz)' : '24', 
            '480p (60 Hz)' : '25', 
            '576p (50 Hz)' : '26', 
            '720p (25 Hz)' : '29', 
            '720p (29.97 Hz)' : '30', 
            '720p (30 Hz)' : '31', 
            '720p (50 Hz)' : '32', 
            '720p (59.94 Hz)' : '33', 
            '720p (60 Hz)' : '34', 
            '1080i (50 Hz)' : '35', 
            '1080i (59.94 Hz)' : '36', 
            '1080i (60 Hz)' : '37', 
            '1080p (23.98 Hz)' : '38', 
            '1080p (24 Hz)' : '39', 
            '1080p (25 Hz)' : '40', 
            '1080p (29.97 Hz)' : '41', 
            '1080p (30 Hz)' : '42', 
            '1080p (50 Hz)' : '43', 
            '1080p (59.94 Hz)' : '44', 
            '1080p (60 Hz)' : '45', 
            '2048x1080 (2K) (23.98 Hz)' : '46', 
            '2048x1080 (2K) (24 Hz)' : '47', 
            '2048x1080 (2K) (25 Hz)' : '48', 
            '2048x1080 (2K) (29.97 Hz)' : '49', 
            '2048x1080 (2K) (30 Hz)' : '50', 
            '2048x1080 (2K) (50 Hz)' : '51', 
            '2048x1080 (2K) (59.94 Hz)' : '52', 
            '2048x1080 (2K) (60 Hz)' : '53', 
            '2048x1200 (60 Hz)' : '54', 
            '2048x1536 (60 Hz)' : '55', 
            '2560x1080 (60 Hz)' : '56', 
            '2560x1440 (60 Hz)' : '57', 
            '2560x1600 (60 Hz)' : '58', 
            '3840x2160 (23.98 Hz)' : '59', 
            '3840x2160 (24 Hz)' : '60', 
            '3840x2160 (25 Hz)' : '61', 
            '3840x2160 (29.97 Hz)' : '62', 
            '3840x2160 (30 Hz)' : '63', 
            '3840x2160 (50 Hz)' : '64', 
            '3840x2160 (59.94 Hz)' : '65', 
            '3840x2160 (60 Hz)' : '66', 
            '4096x2160 (23.98 Hz)' : '69', 
            '4096x2160 (24 Hz)' : '70', 
            '4096x2160 (25 Hz)' : '71', 
            '4096x2160 (29.97 Hz)' : '72', 
            '4096x2160 (30 Hz)' : '73', 
            '4096x2160 (50 Hz)' : '74', 
            '4096x2160 (59.94 Hz)' : '75', 
            '4096x2160 (60 Hz)' : '76'
        }

        self.OutputResolutionStatus = {
            '10' : '640x480 (60 Hz)', 
            '11' : '800x600 (60 Hz)', 
            '12' : '1024x768 (60 Hz)', 
            '13' : '1280x768 (60 Hz)', 
            '14' : '1280x800 (60 Hz)', 
            '15' : '1280x1024 (60 Hz)', 
            '16' : '1360x768 (60 Hz)', 
            '17' : '1366x768 (60 Hz)', 
            '18' : '1440x900 (60 Hz)', 
            '19' : '1440x1050 (60 Hz)', 
            '20' : '1600x900 (60 Hz)', 
            '21' : '1680x1050 (60 Hz)', 
            '22' : '1600x1200 (60 Hz)', 
            '23' : '1920x1200 (60 Hz)', 
            '24' : '480p (59.94 Hz)', 
            '25' : '480p (60 Hz)', 
            '26' : '576p (50 Hz)', 
            '29' : '720p (25 Hz)', 
            '30' : '720p (29.97 Hz)', 
            '31' : '720p (30 Hz)', 
            '32' : '720p (50 Hz)', 
            '33' : '720p (59.94 Hz)', 
            '34' : '720p (60 Hz)', 
            '35' : '1080i (50 Hz)', 
            '36' : '1080i (59.94 Hz)', 
            '37' : '1080i (60 Hz)', 
            '38' : '1080p (23.98 Hz)', 
            '39' : '1080p (24 Hz)', 
            '40' : '1080p (25 Hz)', 
            '41' : '1080p (29.97 Hz)', 
            '42' : '1080p (30 Hz)', 
            '43' : '1080p (50 Hz)', 
            '44' : '1080p (59.94 Hz)', 
            '45' : '1080p (60 Hz)', 
            '46' : '2048x1080 (2K) (23.98 Hz)', 
            '47' : '2048x1080 (2K) (24 Hz)', 
            '48' : '2048x1080 (2K) (25 Hz)', 
            '49' : '2048x1080 (2K) (29.97 Hz)', 
            '50' : '2048x1080 (2K) (30 Hz)', 
            '51' : '2048x1080 (2K) (50 Hz)', 
            '52' : '2048x1080 (2K) (59.94 Hz)', 
            '53' : '2048x1080 (2K) (60 Hz)', 
            '54' : '2048x1200 (60 Hz)', 
            '55' : '2048x1536 (60 Hz)', 
            '56' : '2560x1080 (60 Hz)', 
            '57' : '2560x1440 (60 Hz)', 
            '58' : '2560x1600 (60 Hz)', 
            '59' : '3840x2160 (23.98 Hz)', 
            '60' : '3840x2160 (24 Hz)', 
            '61' : '3840x2160 (25 Hz)', 
            '62' : '3840x2160 (29.97 Hz)', 
            '63' : '3840x2160 (30 Hz)', 
            '64' : '3840x2160 (50 Hz)', 
            '65' : '3840x2160 (59.94 Hz)', 
            '66' : '3840x2160 (60 Hz)', 
            '69' : '4096x2160 (23.98 Hz)', 
            '70' : '4096x2160 (24 Hz)', 
            '71' : '4096x2160 (25 Hz)', 
            '72' : '4096x2160 (29.97 Hz)', 
            '73' : '4096x2160 (30 Hz)', 
            '74' : '4096x2160 (50 Hz)', 
            '75' : '4096x2160 (59.94 Hz)', 
            '76' : '4096x2160 (60 Hz)'
        }

    def extr_18_5158_5K(self):
        self.OutputResolution = {
            '640x480 (60 Hz)' : '10', 
            '800x600 (60 Hz)' : '11', 
            '1024x768 (60 Hz)' : '12', 
            '1280x768 (60 Hz)' : '13', 
            '1280x800 (60 Hz)' : '14', 
            '1280x1024 (60 Hz)' : '15', 
            '1360x768 (60 Hz)' : '16', 
            '1366x768 (60 Hz)' : '17', 
            '1440x900 (60 Hz)' : '18', 
            '1440x1050 (60 Hz)' : '19', 
            '1600x900 (60 Hz)' : '20', 
            '1680x1050 (60 Hz)' : '21', 
            '1600x1200 (60 Hz)' : '22', 
            '1920x1200 (60 Hz)' : '23', 
            '480p (59.94 Hz)' : '24', 
            '480p (60 Hz)' : '25', 
            '576p (50 Hz)' : '26', 
            '720p (25 Hz)' : '29', 
            '720p (29.97 Hz)' : '30', 
            '720p (30 Hz)' : '31', 
            '720p (50 Hz)' : '32', 
            '720p (59.94 Hz)' : '33', 
            '720p (60 Hz)' : '34', 
            '1080i (50 Hz)' : '35', 
            '1080i (59.94 Hz)' : '36', 
            '1080i (60 Hz)' : '37', 
            '1080p (23.98 Hz)' : '38', 
            '1080p (24 Hz)' : '39', 
            '1080p (25 Hz)' : '40', 
            '1080p (29.97 Hz)' : '41', 
            '1080p (30 Hz)' : '42', 
            '1080p (50 Hz)' : '43', 
            '1080p (59.94 Hz)' : '44', 
            '1080p (60 Hz)' : '45', 
            '2048x1080 (2K) (23.98 Hz)' : '46', 
            '2048x1080 (2K) (24 Hz)' : '47', 
            '2048x1080 (2K) (25 Hz)' : '48', 
            '2048x1080 (2K) (29.97 Hz)' : '49', 
            '2048x1080 (2K) (30 Hz)' : '50', 
            '2048x1080 (2K) (50 Hz)' : '51', 
            '2048x1080 (2K) (59.94 Hz)' : '52', 
            '2048x1080 (2K) (60 Hz)' : '53', 
            '2048x1200 (60 Hz)' : '54', 
            '2048x1536 (60 Hz)' : '55', 
            '2560x1080 (60 Hz)' : '56', 
            '2560x1440 (60 Hz)' : '57', 
            '2560x1600 (60 Hz)' : '58', 
            '3840x2160 (23.98 Hz)' : '59', 
            '3840x2160 (24 Hz)' : '60', 
            '3840x2160 (25 Hz)' : '61', 
            '3840x2160 (29.97 Hz)' : '62', 
            '3840x2160 (30 Hz)' : '63', 
            '3840x2160 (50 Hz)' : '64', 
            '3840x2160 (59.94 Hz)' : '65', 
            '3840x2160 (60 Hz)' : '66', 
            '4096x2160 (23.98 Hz)' : '69', 
            '4096x2160 (24 Hz)' : '70', 
            '4096x2160 (25 Hz)' : '71', 
            '4096x2160 (29.97 Hz)' : '72', 
            '4096x2160 (30 Hz)' : '73', 
            '4096x2160 (50 Hz)' : '74', 
            '4096x2160 (59.94 Hz)' : '75', 
            '4096x2160 (60 Hz)' : '76',
            '5120x1080 (30 Hz)' : '79',
            '5120x1080 (60 Hz)' : '80',
            '5120x1440 (30 Hz)' : '81',
            '5120x1440 (60 Hz)' : '82',
            '5120x2160 (30 Hz)' : '83',
            '5120x2560 (30 Hz)' : '85',
            '5120x2880 (30 Hz)' : '87' 
        }

        self.OutputResolutionStatus = {
            '10' : '640x480 (60 Hz)', 
            '11' : '800x600 (60 Hz)', 
            '12' : '1024x768 (60 Hz)', 
            '13' : '1280x768 (60 Hz)', 
            '14' : '1280x800 (60 Hz)', 
            '15' : '1280x1024 (60 Hz)', 
            '16' : '1360x768 (60 Hz)', 
            '17' : '1366x768 (60 Hz)', 
            '18' : '1440x900 (60 Hz)', 
            '19' : '1440x1050 (60 Hz)', 
            '20' : '1600x900 (60 Hz)', 
            '21' : '1680x1050 (60 Hz)', 
            '22' : '1600x1200 (60 Hz)', 
            '23' : '1920x1200 (60 Hz)', 
            '24' : '480p (59.94 Hz)', 
            '25' : '480p (60 Hz)', 
            '26' : '576p (50 Hz)', 
            '29' : '720p (25 Hz)', 
            '30' : '720p (29.97 Hz)', 
            '31' : '720p (30 Hz)', 
            '32' : '720p (50 Hz)', 
            '33' : '720p (59.94 Hz)', 
            '34' : '720p (60 Hz)', 
            '35' : '1080i (50 Hz)', 
            '36' : '1080i (59.94 Hz)', 
            '37' : '1080i (60 Hz)', 
            '38' : '1080p (23.98 Hz)', 
            '39' : '1080p (24 Hz)', 
            '40' : '1080p (25 Hz)', 
            '41' : '1080p (29.97 Hz)', 
            '42' : '1080p (30 Hz)', 
            '43' : '1080p (50 Hz)', 
            '44' : '1080p (59.94 Hz)', 
            '45' : '1080p (60 Hz)', 
            '46' : '2048x1080 (2K) (23.98 Hz)', 
            '47' : '2048x1080 (2K) (24 Hz)', 
            '48' : '2048x1080 (2K) (25 Hz)', 
            '49' : '2048x1080 (2K) (29.97 Hz)', 
            '50' : '2048x1080 (2K) (30 Hz)', 
            '51' : '2048x1080 (2K) (50 Hz)', 
            '52' : '2048x1080 (2K) (59.94 Hz)', 
            '53' : '2048x1080 (2K) (60 Hz)', 
            '54' : '2048x1200 (60 Hz)', 
            '55' : '2048x1536 (60 Hz)', 
            '56' : '2560x1080 (60 Hz)', 
            '57' : '2560x1440 (60 Hz)', 
            '58' : '2560x1600 (60 Hz)', 
            '59' : '3840x2160 (23.98 Hz)', 
            '60' : '3840x2160 (24 Hz)', 
            '61' : '3840x2160 (25 Hz)', 
            '62' : '3840x2160 (29.97 Hz)', 
            '63' : '3840x2160 (30 Hz)', 
            '64' : '3840x2160 (50 Hz)', 
            '65' : '3840x2160 (59.94 Hz)', 
            '66' : '3840x2160 (60 Hz)', 
            '69' : '4096x2160 (23.98 Hz)', 
            '70' : '4096x2160 (24 Hz)', 
            '71' : '4096x2160 (25 Hz)', 
            '72' : '4096x2160 (29.97 Hz)', 
            '73' : '4096x2160 (30 Hz)', 
            '74' : '4096x2160 (50 Hz)', 
            '75' : '4096x2160 (59.94 Hz)', 
            '76' : '4096x2160 (60 Hz)',
            '79': '5120x1080 (30 Hz)',
            '80': '5120x1080 (60 Hz)',
            '81': '5120x1440 (30 Hz)',
            '82': '5120x1440 (60 Hz)',
            '83': '5120x2160 (30 Hz)',
            '85': '5120x2560 (30 Hz)',
            '87': '5120x2880 (30 Hz)'
        }
        
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
                result = search(regexString, self.__receiveBuffer)
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