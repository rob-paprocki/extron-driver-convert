from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'PLS200': self.away_2_1545_PLS200,
            'PLS300': self.away_2_1545_PLS300,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatioIn': {'Parameters': ['Input'], 'Status': {}},
            'AspectRatioOut': {'Parameters': ['Input'], 'Status': {}},
            'AudioLevel': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoCenter': {'Parameters': ['Input'], 'Status': {}},
            'Brightness': {'Parameters': ['Input'], 'Status': {}},
            'Color': {'Parameters': ['Input'], 'Status': {}},
            'Contrast': {'Parameters': ['Input'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Parameters': ['Input'], 'Status': {}},
            'HorizontalPosition': {'Parameters': ['Preset', 'Layer'], 'Status': {}},
            'HorizontalSize': {'Parameters': ['Preset', 'Layer'], 'Status': {}},
            'Hue': {'Parameters': ['Input'], 'Status': {}},
            'Input': {'Parameters': ['Preset', 'Layer'], 'Status': {}},
            'MasterLevel': {'Parameters': ['Output'], 'Status': {}},
            'OutputFormat': {'Parameters': ['Output'], 'Status': {}},
            'OutputRate': {'Parameters': ['Output'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetControl': {'Parameters': ['Source', 'Destination'], 'Status': {}},
            'PreviewLayer': {'Status': {}},
            'QuadraVisionLayout': {'Status': {}},
            'Take': {'Status': {}},
            'TakeStatus': {'Status': {}},
            'TestPattern': {'Parameters': ['Output'], 'Status': {}},
            'Transition': {'Parameters': ['Type', 'Output', 'Preset', 'Duration', 'Direction'], 'Status': {}},
            'VerticalPosition': {'Parameters': ['Preset', 'Layer'], 'Status': {}},
            'VerticalSize': {'Parameters': ['Preset', 'Layer'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'si([0-9]{1,2}),([0-4])\r\n'), self.__MatchAspectRatioIn, None)
            self.AddMatchString(re.compile(b'so([0-9]{1,2}),([0-3])\r\n'), self.__MatchAspectRatioOut, None)
            self.AddMatchString(re.compile(b'AL([0-9]{1,2}),([0-9]{1,3})\r\n'), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b'Au(0|1),(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Sg([0-9]{1,2}),([0-9]{1,3})\r\n'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'Sr([0-9]{1,2}),([0-9]{1,3})\r\n'), self.__MatchColor, None)
            self.AddMatchString(re.compile(b'Sc([0-9]{1,2}),([0-9]{1,3})\r\n'), self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'CK([0-6])\r\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'YK(0|1|2)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Sf([0-9]{1,2}),(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'pH([0-6]),(2|3|4|8|9),([0-9]{1,5})\r\n'), self.__MatchHorizontalPosition, None)
            self.AddMatchString(re.compile(b'pW([0-6]),(2|3|4|8|9),([0-9]{1,5})\r\n'), self.__MatchHorizontalSize, None)
            self.AddMatchString(re.compile(b'Su([0-9]{1,2}),([0-9]{1,3})\r\n'), self.__MatchHue, None)
            self.AddMatchString(re.compile(b'IN([0-6]),(2|3|4|8|9),([0-9]{1,2})\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'AV(0|1),([0-9]{1,3})\r\n'), self.__MatchMasterLevel, None)
            self.AddMatchString(re.compile(b'OF(0|1),([0-9]{1,2})\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(b'OR(0|1),([0-9]{1,2})\r\n'), self.__MatchOutputRate, None)
            self.AddMatchString(re.compile(b'wS(0|1)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'NC(2|3|4|8|9)\r\n'), self.__MatchPreviewLayer, None)
            self.AddMatchString(re.compile(b'TA(0|1)\r\n'), self.__MatchTakeStatus, None)
            self.AddMatchString(re.compile(b'OP(0|1),([0-8]{1})\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'pV([0-6]),(2|3|4|8|9),([0-9]{1,5})\r\n'), self.__MatchVerticalPosition, None)
            self.AddMatchString(re.compile(b'pS([0-6]),(2|3|4|8|9),([0-9]{1,5})\r\n'), self.__MatchVerticalSize, None)
            self.AddMatchString(re.compile(b'OB(0|1),(0|1)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E(10|11|12)\r\n'), self.__MatchError, None)

    def SetAspectRatioIn(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueStateValues = {
            '4:3 Full Screen': '0',
            '4:3 with 16:9 content and black stripes': '1',
            '4:3 with 2.35 content and black stripes': '2',
            '4:3 with 16:9 content and no black stripes': '3',
            '19:9 with 4:3 content and black stripes': '4',
        }

        Input = int(qualifier['Input'])
        if Input in InputConstraints and value in ValueStateValues:
            AspectRatioInCmdString = '{0},{1}si'.format(Input - 1, ValueStateValues[value])
            self.__SetHelper('AspectRatioIn', AspectRatioInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatioIn')

    def UpdateAspectRatioIn(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            AspectRatioInCmdString = '{0},si'.format(Input - 1)
            self.__UpdateHelper('AspectRatioIn', AspectRatioInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatioIn')

    def __MatchAspectRatioIn(self, match, tag):

        ValueStateValues = {
            '0': '4:3 Full Screen',
            '1': '4:3 with 16:9 content and black stripes',
            '2': '4:3 with 2.35 content and black stripes',
            '3': '4:3 with 16:9 content and no black stripes',
            '4': '19:9 with 4:3 content and black stripes'
        }

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatioIn', value, qualifier)

    def SetAspectRatioOut(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueStateValues = {
            'Distorted, input aspect ratio not preserved': '0',
            'Not distorted, black bands added': '1',
            'Not distorted, no black bands added': '2',
            'Not distorted and no scaling': '3'
        }
        Input = int(qualifier['Input'])
        if Input in InputConstraints and value in ValueStateValues:
            AspectRatioOutCmdString = '{0},{1}so'.format(Input - 1, ValueStateValues[value])
            self.__SetHelper('AspectRatioOut', AspectRatioOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatioOut')

    def UpdateAspectRatioOut(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            AspectRatioOutCmdString = '{0},so'.format(Input - 1)
            self.__UpdateHelper('AspectRatioOut', AspectRatioOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatioOut')

    def __MatchAspectRatioOut(self, match, tag):

        ValueStateValues = {
            '0': 'Distorted, input aspect ratio not preserved',
            '1': 'Not distorted, black bands added',
            '2': 'Not distorted, no black bands added',
            '3': 'Not distorted and no scaling'
        }

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatioOut', value, qualifier)

    def SetAudioLevel(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Input = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in InputConstraints:
            AudioLevelCmdString = '{0},{1}AL'.format(Input - 1, value)
            self.__SetHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioLevel')

    def UpdateAudioLevel(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            AudioLevelCmdString = '{0},AL'.format(Input - 1)
            self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioLevel')

    def __MatchAudioLevel(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = int(match.group(2).decode())
        self.WriteStatus('AudioLevel', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{0},{1}Au'.format(OutputStates[Output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            AudioMuteCmdString = '{0},Au'.format(OutputStates[Output])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '0': 'Main',
            '1': 'Preview'
        }
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoCenter(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            AutoCenterCmdString = '{0},1Sa'.format(Input - 1)
            self.__SetHelper('AutoCenter', AutoCenterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoCenter')

    def SetBrightness(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Input = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in InputConstraints:
            BrightnessCmdString = '{0},{1}Sg'.format(Input - 1, value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            BrightnessCmdString = '{0},Sg'.format(Input - 1)
            self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def __MatchBrightness(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = int(match.group(2).decode())
        self.WriteStatus('Brightness', value, qualifier)

    def SetColor(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Input = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in InputConstraints:
            ColorCmdString = '{0},{1}Sr'.format(Input - 1, value)
            self.__SetHelper('Color', ColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColor')

    def UpdateColor(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            ColorCmdString = '{0},Sr'.format(Input - 1)
            self.__UpdateHelper('Color', ColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateColor')

    def __MatchColor(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = int(match.group(2).decode())
        self.WriteStatus('Color', value, qualifier)

    def SetContrast(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Input = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in InputConstraints:
            ContrastCmdString = '{0},{1}Sc'.format(Input - 1, value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            ContrastCmdString = '{0},Sc'.format(Input - 1)
            self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def __MatchContrast(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = int(match.group(2).decode())
        self.WriteStatus('Contrast', value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'CK'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Status',
            '1': 'Auto Centering',
            '2': 'Auto Setting',
            '3': 'Standby',
            '4': 'Picture Recording',
            '5': 'Reset to Factory Settings',
            '6': 'Reset User Settings'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'No Lock': '0',
            'Menu Locked': '1',
            'Front Panel Locked': '2'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{0}YK'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'YK'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'No Lock',
            '1': 'Menu Locked',
            '2': 'Front Panel Locked'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Input = int(qualifier['Input'])
        if Input in InputConstraints and value in ValueStateValues:
            FreezeCmdString = '{0},{1}Sf'.format(Input - 1, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            FreezeCmdString = '{0},Sf'.format(Input - 1)
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, qualifier)

    def SetHorizontalPosition(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65535
            }

        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if (Preset in PresetStates and Layer in self.LayerStates and
            ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            HorizontalPositionCmdString = '{0},{1},{2}pH'.format(PresetStates[Preset], self.LayerStates[Layer], value)
            self.__SetHelper('HorizontalPosition', HorizontalPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalPosition')

    def UpdateHorizontalPosition(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if Preset in PresetStates and Layer in self.LayerStates:
            HorizontalPositionCmdString = '{0},{1},pH'.format(PresetStates[Preset], self.LayerStates[Layer])
            self.__UpdateHelper('HorizontalPosition', HorizontalPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHorizontalPosition')

    def __MatchHorizontalPosition(self, match, tag):

        PresetStates = {
            '0': 'Current',
            '1': 'Next',
            '2': 'Previous',
            '3': '1',
            '4': '2',
            '5': '3',
            '6': '4',
        }

        qualifier = {}
        qualifier['Preset'] = PresetStates[match.group(1).decode()]
        qualifier['Layer'] = self.LayerValues[match.group(2).decode()]
        value = int(match.group(3).decode())
        self.WriteStatus('HorizontalPosition', value, qualifier)

    def SetHorizontalSize(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65535
        }

        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if (Preset in PresetStates and Layer in self.LayerStates and
            ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            HorizontalSizeCmdString = '{0},{1},{2}pW'.format(PresetStates[Preset], self.LayerStates[Layer], value)
            self.__SetHelper('HorizontalSize', HorizontalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSize')

    def UpdateHorizontalSize(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if Preset in PresetStates and Layer in self.LayerStates:
            HorizontalSizeCmdString = '{0},{1},pW'.format(PresetStates[Preset], self.LayerStates[Layer])
            self.__UpdateHelper('HorizontalSize', HorizontalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHorizontalSize')

    def __MatchHorizontalSize(self, match, tag):

        PresetStates = {
            '0': 'Current',
            '1': 'Next',
            '2': 'Previous',
            '3': '1',
            '4': '2',
            '5': '3',
            '6': '4',
        }

        qualifier = {}
        qualifier['Preset'] = PresetStates[match.group(1).decode()]
        qualifier['Layer'] = self.LayerValues[match.group(2).decode()]
        value = int(match.group(3).decode())
        self.WriteStatus('HorizontalSize', value, qualifier)

    def SetHue(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Input = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in InputConstraints:
            HueCmdString = '{0},{1}Su'.format(Input - 1, value)
            self.__SetHelper('Hue', HueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHue')

    def UpdateHue(self, value, qualifier):

        InputConstraints = (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)

        Input = int(qualifier['Input'])
        if Input in InputConstraints:
            HueCmdString = '{0},Su'.format(Input - 1)
            self.__UpdateHelper('Hue', HueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHue')

    def __MatchHue(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        value = int(match.group(2).decode())
        self.WriteStatus('Hue', value, qualifier)

    def SetInput(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        ValueStateValues = {
            'No Input': '0',
            'Input 1': '1',
            'Input 2': '2',
            'Input 3': '3',
            'Input 4': '4',
            'Input 5': '5',
            'Input 6': '6',
            'Input 9': '9',
            'Input 10': '10',
            'Input 11': '11',
            'Input 12': '12'
        }

        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if Preset in PresetStates and Layer in self.LayerStates and value in ValueStateValues:
            InputCmdString = '{0},{1},{2}IN'.format(PresetStates[Preset], self.LayerStates[Layer], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if Preset in PresetStates and Layer in self.LayerStates:
            InputCmdString = '{0},{1},IN'.format(PresetStates[Preset], self.LayerStates[Layer])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        PresetStates = {
            '0': 'Current',
            '1': 'Next',
            '2': 'Previous',
            '3': '1',
            '4': '2',
            '5': '3',
            '6': '4',
        }
        ValueStateValues = {
            '0': 'No Input',
            '1': 'Input 1',
            '2': 'Input 2',
            '3': 'Input 3',
            '4': 'Input 4',
            '5': 'Input 5',
            '6': 'Input 6',
            '9': 'Input 9',
            '10': 'Input 10',
            '11': 'Input 11',
            '12': 'Input 12'
        }

        qualifier = {}
        qualifier['Preset'] = PresetStates[match.group(1).decode()]
        qualifier['Layer'] = self.LayerValues[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetMasterLevel(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        Output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Output in OutputStates:
            MasterLevelCmdString = '{0},{1}AV'.format(OutputStates[Output], value)
            self.__SetHelper('MasterLevel', MasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterLevel')

    def UpdateMasterLevel(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            MasterLevelCmdString = '{0},AV'.format(OutputStates[Output])
            self.__UpdateHelper('MasterLevel', MasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMasterLevel')

    def __MatchMasterLevel(self, match, tag):

        OutputStates = {
            '0': 'Main',
            '1': 'Preview'
        }
        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('MasterLevel', value, qualifier)

    def SetOutputFormat(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueStateValues = {
            'PAL': '0',
            'NTSC': '1',
            '480p': '2',
            '576p': '3',
            'SMPTE296M': '4',
            'SMPTE260M': '5',
            'SMPTE274M': '6',
            '640x480 4/3': '9',
            '848x480 16/9': '10',
            '800x600 4/3': '11',
            '1024x768 4/3': '12',
            '1360x768 16/9': '13',
            '1280x800 16/9': '14',
            '1280x1024 5/4': '15',
            '1400x1050 5/3': '16',
            '1680x1050 16/9': '17',
            '1600x1200 16/9': '18',
            '1920x1200 16/9': '19',
            '2048x1080': '20',
            '1280x720 16/9': '21',
            '1920x1080 16/9': '22',
            '1920x1080 16/9 HD': '23',
            '1920x1080 16/9 SHARP': '24',
            '1920x1080 16/9 SHARP 2': '25',
            '1440x900 16/10': '26',
            '1280x768 15/9': '27',
            '1366x800 15/9': '28',
            '1366x768 16/9': '29',
            'Computer Custom 1': '30',
            'Computer Custom 2': '31',
            'Computer Custom 3': '32',
            'Computer Custom 4': '33',
            'Computer Custom 5': '34',
            'Computer Custom 6': '35',
            'Computer Custom 7': '36',
            'Computer Custom 8': '37'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in ValueStateValues:
            OutputFormatCmdString = '{0},{1}OF'.format(OutputStates[Output], ValueStateValues[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            OutputFormatCmdString = '{0},OF'.format(OutputStates[Output])
            self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputFormat')

    def __MatchOutputFormat(self, match, tag):

        OutputStates = {
            '0': 'Main',
            '1': 'Preview'
        }
        ValueStateValues = {
            '0': 'PAL',
            '1': 'NTSC',
            '2': '480p',
            '3': '576p',
            '4': 'SMPTE296M',
            '5': 'SMPTE260M',
            '6': 'SMPTE274M',
            '7': 'SMPTE274M',
            '8': 'SMPTE274M',
            '9': '640x480 4/3',
            '10': '848x480 16/9',
            '11': '800x600 4/3',
            '12': '1024x768 4/3',
            '13': '1360x768 16/9',
            '14': '1280x800 16/9',
            '15': '1280x1024 5/4',
            '16': '1400x1050 5/3',
            '17': '1680x1050 16/9',
            '18': '1600x1200 16/9',
            '19': '1920x1200 16/9',
            '20': '2048x1080',
            '21': '1280x720 16/9',
            '22': '1920x1080 16/9',
            '23': '1920x1080 16/9 HD',
            '24': '1920x1080 16/9 SHARP',
            '25': '1920x1080 16/9 SHARP 2',
            '26': '1440x900 16/10',
            '27': '1280x768 15/9',
            '28': '1366x800 15/9',
            '29': '1366x768 16/9',
            '30': 'Computer Custom 1',
            '31': 'Computer Custom 2',
            '32': 'Computer Custom 3',
            '33': 'Computer Custom 4',
            '34': 'Computer Custom 5',
            '35': 'Computer Custom 6',
            '36': 'Computer Custom 7',
            '37': 'Computer Custom 8'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputFormat', value, qualifier)

    def SetOutputRate(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueStateValues = {
            'Custom': '0',
            '23.97 Hz': '1',
            '24 Hz': '2',
            '25 Hz': '3',
            '29.97 Hz': '4',
            '30 Hz': '5',
            '50 Hz': '6',
            '59.94 Hz': '7',
            '60 Hz': '8',
            '72 Hz': '9',
            '75 Hz': '10',
            '85 Hz': '11',
            '100 Hz': '12'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in ValueStateValues:
            OutputRateCmdString = '{0},{1}OR'.format(OutputStates[Output], ValueStateValues[value])
            self.__SetHelper('OutputRate', OutputRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputRate')

    def UpdateOutputRate(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            OutputRateCmdString = '{0},OR'.format(OutputStates[Output])
            self.__UpdateHelper('OutputRate', OutputRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputRate')

    def __MatchOutputRate(self, match, tag):

        OutputStates = {
             '0': 'Main',
             '1': 'Preview'
        }
        ValueStateValues = {
            0: 'Custom',
            1: '23.97 Hz',
            2: '24 Hz',
            3: '25 Hz',
            4: '29.97 Hz',
            5: '30 Hz',
            6: '50 Hz',
            7: '59.94 Hz',
            8: '60 Hz',
            9: '72 Hz',
            10: '75 Hz',
            11: '85 Hz',
            12: '100 Hz'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[int(match.group(2).decode())]
        self.WriteStatus('OutputRate', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        if value in ValueStateValues:
            PowerCmdString = '{0}wQ'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'wS'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetControl(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if Source in PresetStates and Destination in PresetStates:
            PresetControlCmdString = '{0}Nf{1}Nt1Nc'.format(PresetStates[Source], PresetStates[Destination])
            self.__SetHelper('PresetControl', PresetControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetControl')

    def SetPreviewLayer(self, value, qualifier):

        if value in self.LayerStates:
            PreviewLayerCmdString = '{0}NC'.format(self.LayerStates[value])
            self.__SetHelper('PreviewLayer', PreviewLayerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreviewLayer')

    def UpdatePreviewLayer(self, value, qualifier):

        PreviewLayerCmdString = 'NC'
        self.__UpdateHelper('PreviewLayer', PreviewLayerCmdString, value, qualifier)

    def __MatchPreviewLayer(self, match, tag):

        value = self.LayerValues[match.group(1).decode()]
        self.WriteStatus('PreviewLayer', value, None)

    def SetQuadraVisionLayout(self, value, qualifier):

        ValueStateValues = {
            '2 Horizontal Windows': '9',
            '2 Vertical Windows': '10',
            'Reset of Layer Properties': '13',
            'Background Live + Top Left PIP': '14',
            'Background Live + Top Right PIP': '15',
            'Background Live + Bottom Left PIP': '16',
            'Background Live + Bottom Right PIP': '17'
        }

        if value in ValueStateValues:
            QuadraVisionLayoutCmdString = '{0}NQ'.format(ValueStateValues[value])
            self.__SetHelper('QuadraVisionLayout', QuadraVisionLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetQuadraVisionLayout')

    def SetTake(self, value, qualifier):

        if self.ReadStatus('TakeStatus', None) != 'Busy':
            TakeCmdString = '1TK'
            self.__SetHelper('Take', TakeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTake')

    def UpdateTakeStatus(self, value, qualifier):

        TakeStatusCmdString = 'TA'
        self.__UpdateHelper('TakeStatus', TakeStatusCmdString, value, qualifier)

    def __MatchTakeStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Busy',
            '1': 'Ready'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TakeStatus', value, None)

    def SetTestPattern(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueStateValues = {
            'No Pattern': '0',
            'Vertical Grey Scale': '1',
            'Horizontal Grey Scale': '2',
            'Vertical Color Bar': '3',
            'Horizontal Color Bar': '4',
            'Grid': '5',
            'SMPTE': '6',
            'Burst': '7',
            'Centering': '8'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in ValueStateValues:
            TestPatternCmdString = '{0},{1}OP'.format(OutputStates[Output], ValueStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            TestPatternCmdString = '{0},OP'.format(OutputStates[Output])
            self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTestPattern')

    def __MatchTestPattern(self, match, tag):

        OutputStates = {
            '0': 'Main',
            '1': 'Preview'
        }

        ValueStateValues = {
            '0': 'No Pattern',
            '1': 'Vertical Grey Scale',
            '2': 'Horizontal Grey Scale',
            '3': 'Vertical Color Bar',
            '4': 'Horizontal Color Bar',
            '5': 'Grid',
            '6': 'SMPTE',
            '7': 'Burst',
            '8': 'Centering'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TestPattern', value, qualifier)

    def SetTransition(self, value, qualifier):

        TypeStates = {
            'Opening': 'o',
            'Closing': 'c'
        }
        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        DirectionStates = {
            'Left to Right': '0',
            'Right to Left': '1',
            'Bottom to Top': '2',
            'Top to Bottom': '3',
            'Vertical from/to Center': '4',
            'Horizontal from/to Center': '5',
            'H&V from/to Center': '6',
            'From South-West to North-East': '7',
            'From South-East to North-West': '8',
            'From North-West to South-East': '9',
            'From North-East to South-West': '10',
        }
        DurationConstraints = {
            'Min': 0,
            'Max': 255
        }

        Type = qualifier['Type']
        Output = qualifier['Output']
        Preset = qualifier['Preset']
        Direction = qualifier['Direction']
        Duration = int(qualifier['Duration'])
        if (Output in self.LayerStates and Preset in PresetStates and value in self.TransitionValues and
            Type in TypeStates and Direction in DirectionStates and
            DurationConstraints['Min'] <= Duration <= DurationConstraints['Max']):
            TransitionCmdString = '{0},{1},{4}{5}T{0},{1},{3}{5}W{0},{1},{2}{5}D'.format(PresetStates[Preset], self.LayerStates[Output], Duration, DirectionStates[Direction], self.TransitionValues[value], TypeStates[Type])
            self.__SetHelper('Transition', TransitionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransition')

    def SetVerticalPosition(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65535
        }

        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if (Preset in PresetStates and Layer in self.LayerStates and
            ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            VerticalPositionCmdString = '{0},{1},{2}pV'.format(PresetStates[Preset], self.LayerStates[Layer], value)
            self.__SetHelper('VerticalPosition', VerticalPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalPosition')

    def UpdateVerticalPosition(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        Preset = qualifier['Preset']
        Layer = qualifier['Layer']
        if Preset in PresetStates and Layer in self.LayerStates:
            VerticalPositionCmdString = '{0},{1},pV'.format(PresetStates[Preset], self.LayerStates[Layer])
            self.__UpdateHelper('VerticalPosition', VerticalPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVerticalPosition')

    def __MatchVerticalPosition(self, match, tag):

        PresetStates = {
            '0': 'Current',
            '1': 'Next',
            '2': 'Previous',
            '3': '1',
            '4': '2',
            '5': '3',
            '6': '4',
        }

        qualifier = {}
        qualifier['Preset'] = PresetStates[match.group(1).decode()]
        qualifier['Layer'] = self.LayerValues[match.group(2).decode()]
        value = int(match.group(3).decode())
        self.WriteStatus('VerticalPosition', value, qualifier)

    def SetVerticalSize(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65535
            }

        Layer = qualifier['Layer']
        Preset = qualifier['Preset']
        if (Preset in PresetStates and Layer in self.LayerStates and
            ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            VerticalSizeCmdString = '{0},{1},{2}pS'.format(PresetStates[Preset], self.LayerStates[Layer], value)
            self.__SetHelper('VerticalSize', VerticalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSize')

    def UpdateVerticalSize(self, value, qualifier):

        PresetStates = {
            'Current': '0',
            'Next': '1',
            'Previous': '2',
            '1': '3',
            '2': '4',
            '3': '5',
            '4': '6'
        }
        Layer = qualifier['Layer']
        Preset = qualifier['Preset']
        if Preset in PresetStates and Layer in self.LayerStates:
            VerticalSizeCmdString = '{0},{1},pS'.format(PresetStates[Preset], self.LayerStates[Layer])
            self.__UpdateHelper('VerticalSize', VerticalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVerticalSize')

    def __MatchVerticalSize(self, match, tag):

        PresetStates = {
            '0': 'Current',
            '1': 'Next',
            '2': 'Previous',
            '3': '1',
            '4': '2',
            '5': '3',
            '6': '4',
        }

        qualifier = {}
        qualifier['Preset'] = PresetStates[match.group(1).decode()]
        qualifier['Layer'] = self.LayerValues[match.group(2).decode()]
        value = int(match.group(3).decode())
        self.WriteStatus('VerticalSize', value, qualifier)

    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in ValueStateValues:
            VideoMuteCmdString = '{0},{1}OB'.format(OutputStates[Output], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        OutputStates = {
            'Main': '0',
            'Preview': '1'
        }
        Output = qualifier['Output']
        if Output in OutputStates:
            VideoMuteCmdString = '{0},OB'.format(OutputStates[Output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        OutputStates = {
            '0': 'Main',
            '1': 'Preview'
        }
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        Errors = {
            '10' : 'Invalid command',
            '11' : 'Index value error (index value out of range)',
            '12' : 'Index number error (too many or too few indexes)',
        }

        value = match.group(1).decode()
        self.Error([Errors[value]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def away_2_1545_PLS200(self):

        self.LayerValues = {
            '2' : 'Background Layer for Output 1',
            '3' : 'PIP 1 Layer for Output 1',
            '4' : 'Background Layer for Output 2 in Matrix Mode',
            '8' : 'Audio Output 1',
            '9' : 'Audio Output 2',
        }
        self.LayerStates = {
            'Background Layer for Output 1' : '2',
            'PIP 1 Layer for Output 1' : '3',
            'Background Layer for Output 2 in Matrix Mode' : '4',
            'Audio Output 1' : '8',
            'Audio Output 2' : '9',
        }
        self.TransitionValues = {
            'Cut' : '0', 
            'Clean Cut' : '1', 
            'Fade' : '2',
        }

    def away_2_1545_PLS300(self):

        self.LayerValues = {
            '0' : 'Background Frame for Output 1',
            '1' : 'Background Frame for Output 2 in Matrix Mode',
            '2' : 'Background Layer for Output 1',
            '3' : 'PIP 1 Layer for Output 1',
            '4' : 'Background Layer for Output 2 in Matrix Mode',
            '6' : 'Logo 1',
            '7' : 'Logo 2',
            '8' : 'Audio Output 1',
            '9' : 'Audio Output 2',
        }
        self.LayerStates = {
            'Background Frame for Output 1' : '0',
            'Background Frame for Output 2 in Matrix Mode' : '1',
            'Background Layer for Output 1' : '2',
            'PIP 1 Layer for Output 1' : '3',
            'Background Layer for Output 2 in Matrix Mode' : '4',
            'Logo 1' : '6',
            'Logo 2' : '7',
            'Audio Output 1' : '8',
            'Audio Output 2' : '9',
        }
        self.TransitionValues = {
            'Cut' : '0', 
            'Clean Cut' : '1', 
            'Fade' : '2',
            'Slide' : '3',
            'Wipe' : '4',
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

