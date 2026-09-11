from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'AudioFollow': { 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Parameters': ['Output'], 'Status': {}},
            'EffectDuration': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Output', 'Type'], 'Status': {}},
            'InputNameCommand': {'Parameters':['Input'], 'Status': {}},
            'InputNameStatus': {'Parameters':['Input'], 'Status': {}},
            'InputPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'LayoutPresetRecall': { 'Status': {}},
            'Logo': {'Parameters': ['Output'], 'Status': {}},
            'OutputScalerRate': { 'Status': {}},
            'PIPPresetRecall': { 'Status': {}},
            'PreviewSwitchMode': { 'Status': {}},
            'SwitchEffect': { 'Status': {}},
            'SwitchTake': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'VideoKeyEffect': { 'Status': {}},
            'VideoKeyEffectLevel': {'Parameters': ['Effect'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'WipeEffect': { 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aflw([23])\r\n'), self.__MatchAudioFollow, None)
            self.AddMatchString(re.compile(b'Amt([1256])\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Edur(\d+)\r\n'), self.__MatchEffectDuration, None)
            self.AddMatchString(re.compile(b'Exe([0-3])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Frz([12])\*([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Out([12]) In([0-8]+) (All|Vid|Aud)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Nmi0([1-8]),(.*)\r\n'), self.__MatchInputNameStatus, None)
            self.AddMatchString(re.compile(b'In00 ([01\*]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'LogoE([12])\*(\d+)\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Rate(\d+)\r\n'), self.__MatchOutputScalerRate, None)
            self.AddMatchString(re.compile(b'Pswm([01])\r\n'), self.__MatchPreviewSwitchMode, None)
            self.AddMatchString(re.compile(b'SwefO1\*([0-4])\r\n'), self.__MatchSwitchEffect, None)
            self.AddMatchString(re.compile(b'Test0([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'Vkef([1-3])\r\n'), self.__MatchVideoKeyEffect, None)
            self.AddMatchString(re.compile(b'Vkey([0-4])\*(\d+)\r\n'), self.__MatchVideoKeyEffectLevel, None)
            self.AddMatchString(re.compile(b'Vmt([12])\*([012])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Wipe([1-8])\r\n'), self.__MatchWipeEffect, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False
    
    def SetAudioFollow(self, value, qualifier):

        ValueStateValues = {
            'Main': '2',
            'PIP':  '3'
        }

        if value in ValueStateValues:
            AudioFollowCmdString = 'w{}AFLW\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioFollow', AudioFollowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFollow')

    def UpdateAudioFollow(self, value, qualifier):

        AudioFollowCmdString = 'wAFLW\r'
        self.__UpdateHelper('AudioFollow', AudioFollowCmdString, value, qualifier)

    def __MatchAudioFollow(self, match, qualifier):

        ValueStateValues = {
            '2': 'Main',
            '3': 'PIP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioFollow', value, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Program Analog Audio': '6',
            'Preview Analog Audio': '5',
            'Program HDMI Audio':   '2',
            'Preview HDMI Audio':   '1'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Program Analog Audio': '6',
            'Preview Analog Audio': '5',
            'Program HDMI Audio':   '2',
            'Preview HDMI Audio':   '1'
        }

        output = qualifier['Output']

        if output in OutputStates:
            AudioMuteCmdString = '{}*Z'.format(OutputStates[output])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):

        OutputStates = {
            '6': 'Program Analog Audio',
            '5': 'Preview Analog Audio',
            '2': 'Program HDMI Audio', 
            '1': 'Preview HDMI Audio'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'Auto-Image':           '0',
            'Auto-Image & Fill':    '1',
            'Auto-Image & Follow':  '2'
        }

        if output in OutputStates and value in ValueStateValues:
            AutoImageCmdString = '{}*{}A'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetEffectDuration(self, value, qualifier):

        if 0.1 <= value <= 5.0:
            EffectDurationCmdString = 'w{}EDUR\r'.format(int(value * 10))
            self.__SetHelper('EffectDuration', EffectDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEffectDuration')

    def UpdateEffectDuration(self, value, qualifier):

        EffectDurationCmdString = 'wEDUR\r'
        self.__UpdateHelper('EffectDuration', EffectDurationCmdString, value, qualifier)

    def __MatchEffectDuration(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 50:
            self.WriteStatus('EffectDuration', value / 10, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1':   '1',
            'Mode 2':   '2',
            'Mode 3':   '3',
            'Off':      '0'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):
            
        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3',
            '0': 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in OutputStates and value in ValueStateValues:
            FreezeCmdString = '{}*{}F'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1',
        }

        output = qualifier['Output']

        if output in OutputStates:
            FreezeCmdString = '{}F'.format(OutputStates[output])
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, qualifier):

        OutputStates = {
            '2': 'Program',
            '1': 'Preview'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, qualifier)

    def SetInput(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }
        output = qualifier['Output']

        TypeStates = {
            'Audio':        '$',
            'Video':        '%',
            'Audio/Video':  '!'
        }
        type_ = qualifier['Type']

        if output in OutputStates and type_ in TypeStates and 1 <= int(value) <= 8:
            InputCmdString = '{}*{}{}'.format(int(value), OutputStates[output], TypeStates[type_])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        TypeStates = {
            'Audio':        '$',
            'Video':        '%',
            'Audio/Video':  '!'
        }

        type_ = qualifier['Type']

        if output in OutputStates and type_ in TypeStates:
            for t in type_.split('/'):
                InputCmdString = '{}{}'.format(OutputStates[output], TypeStates[t])
                self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        OutputStates = {
            '2': 'Program',
            '1': 'Preview',
        }

        TypeStates = {
            'All': 'Audio/Video',
            'Vid': 'Video',
            'Aud': 'Audio'
        }

        output = OutputStates[match.group(1).decode()]
        type_ = TypeStates[match.group(3).decode()]

        qualifier = {
            'Output':   output,
            'Type':     type_
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 8:
            value = str(value)

            self.WriteStatus('Input', value, qualifier)

            if type_ == 'Audio/Video':
                self.WriteStatus('Input', value, {'Output': output, 'Type': 'Audio'})
                self.WriteStatus('Input', value, {'Output': output, 'Type': 'Video'})
                return

            if self.ReadStatus('Input', {'Output': output, 'Type': 'Audio'}) and self.ReadStatus('Input', {'Output': output, 'Type': 'Video'}):
                op_type = 'Video' if type_ == 'Audio' else 'Audio'

                if self.ReadStatus('Input', {'Output': output, 'Type': op_type}) != value:
                    self.WriteStatus('Input', '0', {'Output': output, 'Type': 'Audio/Video'})
                else:
                    self.WriteStatus('Input', value, {'Output': output, 'Type': 'Audio/Video'})
    
    def SetInputNameCommand(self, value, qualifier):

        inputName = value
        if 1 <= int(qualifier['Input']) <= 8 and inputName:
            InputNameCommandCmdString = 'w0{0},{1}NI\r'.format(qualifier['Input'], inputName)
            self.__SetHelper('InputNameCommand', InputNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputNameCommand')

    def UpdateInputNameStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 8:
            InputNameStatusCmdString = 'w0{}NI\r'.format(qualifier['Input'])
            self.__UpdateHelper('InputNameStatus', InputNameStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputNameStatus')

    def __MatchInputNameStatus(self, match, tag):

        qualifier = {'Input' : match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('InputNameStatus', value, qualifier)

    def SetInputPresetRecall(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 128:
            InputPresetRecallCmdString = '2*{}*{}.'.format(OutputStates[output], int(value))
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def UpdateInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 8:
            InputSignalStatusCmdString = 'w0LS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        for input_, value in enumerate(match.group(1).decode().split('*'), 1):
            qualifier = {
                'Input': str(input_)
            }

            value = ValueStateValues[value]
            self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetLayoutPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            LayoutPresetRecallCmdString = '1*1*{}.'.format(int(value))
            self.__SetHelper('LayoutPresetRecall', LayoutPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayoutPresetRecall')

    def SetLogo(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        if output in OutputStates and value in [str(i) for i in range(1, 17)] + ['Off']:
            if value != 'Off':
                LogoCmdString = 'wE{}*{}LOGO\r'.format(OutputStates[output], value)
            else:
                LogoCmdString = 'wE{}*0LOGO\r'.format(OutputStates[output])

            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        if output in OutputStates:
            LogoCmdString = 'wE{}LOGO\r'.format(OutputStates[output])
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):

        OutputStates = {
            '2': 'Program',
            '1': 'Preview'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 16:
            if value == 0:
                value = 'Off'

            self.WriteStatus('Logo', str(value), qualifier)

    def SetOutputScalerRate(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)':       '10',
            '800x600 (60Hz)':       '11',
            '1024x768 (60Hz)':      '12',
            '1280x768 (60Hz)':      '13',
            '1280x800 (60Hz)':      '14',
            '1280x1024 (60Hz)':     '15',
            '1360x768 (60Hz)':      '16',
            '1366x768 (60Hz)':      '17',
            '1440x900 (60Hz)':      '18',
            '1400x1050 (60Hz)':     '19',
            '1600x900 (60Hz)':      '20',
            '1680x1050 (60Hz)':     '21',
            '1600x1200 (60Hz)':     '22',
            '1920x1200 (60Hz)':     '23',
            '480p (59.94Hz)':       '24',
            '480p (60Hz)':          '25',
            '576p (50Hz)':          '26',
            '720p (25Hz)':          '29',
            '720p (29.97Hz)':       '30',
            '720p (30Hz)':          '31',
            '720p (50Hz)':          '32',
            '720p (59.94Hz)':       '33',
            '720p (60Hz)':          '34',
            '1080i (50Hz)':         '35',
            '1080i (59.94Hz)':      '36',
            '1080i (60Hz)':         '37',
            '1080p (23.98Hz)':      '38',
            '1080p (24Hz)':         '39',
            '1080p (25Hz)':         '40',
            '1080p (29.97Hz)':      '41',
            '1080p (30Hz)':         '42',
            '1080p (50Hz)':         '43',
            '1080p (59.94Hz)':      '44',
            '1080p (60Hz)':         '45',
            '2048x1080 (23.98Hz)':  '46',
            '2048x1080 (24Hz)':     '47',
            '2048x1080 (25Hz)':     '48',
            '2048x1080 (29.97Hz)':  '49',
            '2048x1080 (30Hz)':     '50',
            '2048x1080 (50Hz)':     '51',
            '2048x1080 (59.94Hz)':  '52',
            '2048x1080 (60Hz)':     '53',
            '2048x1200 (60Hz)':     '54',
            '2048x1536 (60Hz)':     '55',
            '2560x1080 (60Hz)':     '56',
            '2560x1440 (60Hz)':     '57',
            '2560x1600 (60Hz)':     '58',
            '3840x2160 (23.98Hz)':  '59',
            '3840x2160 (24Hz)':     '60',
            '3840x2160 (25Hz)':     '61',
            '3840x2160 (29.97Hz)':  '62',
            '3840x2160 (30Hz)':     '63',
            '3840x2160 (50Hz)':     '64',
            '3840x2160 (59.94Hz)':  '65',
            '3840x2160 (60Hz)':     '66',
            '4096x2160 (23.98Hz)':  '69',
            '4096x2160 (24Hz)':     '70',
            '4096x2160 (25Hz)':     '71',
            '4096x2160 (29.97Hz)':  '72',
            '4096x2160 (30Hz)':     '73',
            '4096x2160 (50Hz)':     '74',
            '4096x2160 (59.94Hz)':  '75',
            '4096x2160 (60Hz)':     '76',
            'Custom 1':             '201',
            'Custom 2':             '202',
            'Custom 3':             '203',
            'Custom 4':             '204',
            'Custom 5':             '205',
            'Custom 6':             '206',
            'Custom 7':             '207',
            'Custom 8':             '208',
            'Custom 9':             '209',
            'Custom 10':            '210'
        }

        if value in ValueStateValues:
            OutputScalerRateCmdString = 'w{}RATE\r'.format(ValueStateValues[value])
            self.__SetHelper('OutputScalerRate', OutputScalerRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputScalerRate')

    def UpdateOutputScalerRate(self, value, qualifier):

        OutputScalerRateCmdString = 'wRATE\r'
        self.__UpdateHelper('OutputScalerRate', OutputScalerRateCmdString, value, qualifier)

    def __MatchOutputScalerRate(self, match, tag):

        ValueStateValues = {
            '10':   '640x480 (60Hz)',
            '11':   '800x600 (60Hz)',
            '12':   '1024x768 (60Hz)',
            '13':   '1280x768 (60Hz)',
            '14':   '1280x800 (60Hz)',
            '15':   '1280x1024 (60Hz)',
            '16':   '1360x768 (60Hz)',
            '17':   '1366x768 (60Hz)',
            '18':   '1440x900 (60Hz)',
            '19':   '1400x1050 (60Hz)',
            '20':   '1600x900 (60Hz)',
            '21':   '1680x1050 (60Hz)',
            '22':   '1600x1200 (60Hz)',
            '23':   '1920x1200 (60Hz)',
            '24':   '480p (59.94Hz)',
            '25':   '480p (60Hz)',
            '26':   '576p (50Hz)',
            '29':   '720p (25Hz)',
            '30':   '720p (29.97Hz)',
            '31':   '720p (30Hz)',
            '32':   '720p (50Hz)',
            '33':   '720p (59.94Hz)',
            '34':   '720p (60Hz)',
            '35':   '1080i (50Hz)',
            '36':   '1080i (59.94Hz)',
            '37':   '1080i (60Hz)',
            '38':   '1080p (23.98Hz)',
            '39':   '1080p (24Hz)',
            '40':   '1080p (25Hz)',
            '41':   '1080p (29.97Hz)',
            '42':   '1080p (30Hz)',
            '43':   '1080p (50Hz)',
            '44':   '1080p (59.94Hz)',
            '45':   '1080p (60Hz)',
            '46':   '2048x1080 (23.98Hz)',
            '47':   '2048x1080 (24Hz)',
            '48':   '2048x1080 (25Hz)',
            '49':   '2048x1080 (29.97Hz)',
            '50':   '2048x1080 (30Hz)',
            '51':   '2048x1080 (50Hz)',
            '52':   '2048x1080 (59.94Hz)',
            '53':   '2048x1080 (60Hz)',
            '54':   '2048x1200 (60Hz)',
            '55':   '2048x1536 (60Hz)',
            '56':   '2560x1080 (60Hz)',
            '57':   '2560x1440 (60Hz)',
            '58':   '2560x1600 (60Hz)',
            '59':   '3840x2160 (23.98Hz)',
            '60':   '3840x2160 (24Hz)',
            '61':   '3840x2160 (25Hz)',
            '62':   '3840x2160 (29.97Hz)',
            '63':   '3840x2160 (30Hz)',
            '64':   '3840x2160 (50Hz)',
            '65':   '3840x2160 (59.94Hz)',
            '66':   '3840x2160 (60Hz)',
            '69':   '4096x2160 (23.98Hz)',
            '70':   '4096x2160 (24Hz)',
            '71':   '4096x2160 (25Hz)',
            '72':   '4096x2160 (29.97Hz)',
            '73':   '4096x2160 (30Hz)',
            '74':   '4096x2160 (50Hz)',
            '75':   '4096x2160 (59.94Hz)',
            '76':   '4096x2160 (60Hz)',
            '201':  'Custom 1',
            '202':  'Custom 2',
            '203':  'Custom 3',
            '204':  'Custom 4',
            '205':  'Custom 5',
            '206':  'Custom 6',
            '207':  'Custom 7',
            '208':  'Custom 8',
            '209':  'Custom 9',
            '210':  'Custom 10',
        }

        value = str(int(match.group(1).decode()))
        if value in ValueStateValues:
            self.WriteStatus('OutputScalerRate', ValueStateValues[value], None)

    def SetPIPPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PIPPresetRecallCmdString = '3*1*{}.'.format(int(value))
            self.__SetHelper('PIPPresetRecall', PIPPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPresetRecall')

    def SetPreviewSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Swap': '0',
            'Stay': '1'
        }
        
        if value in ValueStateValues:
            PreviewSwitchModeCmdString = 'w{}PSWM\r'.format(ValueStateValues[value])
            self.__SetHelper('PreviewSwitchMode', PreviewSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreviewSwitchMode')

    def UpdatePreviewSwitchMode(self, value, qualifier):

        PreviewSwitchModeCmdString = 'wPSWM\r'
        self.__UpdateHelper('PreviewSwitchMode', PreviewSwitchModeCmdString, value, qualifier)

    def __MatchPreviewSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Swap',
            '1': 'Stay'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PreviewSwitchMode', value, None)

    def SetSwitchEffect(self, value, qualifier):

        ValueStateValues = {
            'Cut':          '0',
            'Dissolve':     '1',
            'Wipe':         '2',
            'PIP':          '3',
            'Video Key':    '4'
        }
        
        if value in ValueStateValues:
            SwitchEffectCmdString = 'wO1*{}SWEF\r'.format(ValueStateValues[value])
            self.__SetHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchEffect')

    def UpdateSwitchEffect(self, value, qualifier):

        SwitchEffectCmdString = 'wO1SWEF\r'
        self.__UpdateHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)

    def __MatchSwitchEffect(self, match, tag):

        ValueStateValues = {
            '0': 'Cut',
            '1': 'Dissolve',
            '2': 'Wipe',
            '3': 'PIP',
            '4': 'Video Key'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SwitchEffect', value, None)

    def SetSwitchTake(self, value, qualifier):

        SwitchTakeCmdString = '%'
        self.__SetHelper('SwitchTake', SwitchTakeCmdString, value, qualifier)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Off':                  '0',
            'Crop':                 '1',
            'Alternating Pixels':   '2',
            'Crosshatch':           '3',
            'Color Bars':           '4',
            'Grayscale':            '5',
            'Audio Test':           '6'
        }

        if value in ValueStateValues:
            TestPatternCmdString = 'w{}TEST\r'.format(ValueStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'wTEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)
        
    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Crop',
            '2': 'Alternating Pixels',
            '3': 'Crosshatch',
            '4': 'Color Bars',
            '5': 'Grayscale',
            '6': 'Audio Test',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetVideoKeyEffect(self, value, qualifier):

        ValueStateValues = {
            'Transparency': '1',
            'Level Key':    '3',
            'RGB Key':      '2'
        }

        if value in ValueStateValues:
            VideoKeyEffectCmdString = 'w{}VKEF\r'.format(ValueStateValues[value])
            self.__SetHelper('VideoKeyEffect', VideoKeyEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoKeyEffect')

    def UpdateVideoKeyEffect(self, value, qualifier):

        VideoKeyEffectCmdString = 'wVKEF\r'
        self.__UpdateHelper('VideoKeyEffect', VideoKeyEffectCmdString, value, qualifier)

    def __MatchVideoKeyEffect(self, match, tag):

        ValueStateValues = {
            '1': 'Transparency',
            '3': 'Level Key',
            '2': 'RGB Key'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoKeyEffect', value, None)

    def SetVideoKeyEffectLevel(self, value, qualifier):

        EffectStates = {
            'Transparency':     '0',
            'Red of RGB Key':   '1',
            'Green of RGB Key': '2',
            'Blue of RGB Key':  '3',
            'Level Key':        '4'
        }

        effect = qualifier['Effect']

        if effect in EffectStates and 0 <= value <= 255:
            VideoKeyEffectLevelCmdString = 'w{}*{}VKEY\r'.format(EffectStates[effect], value)
            self.__SetHelper('VideoKeyEffectLevel', VideoKeyEffectLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoKeyEffectLevel')

    def UpdateVideoKeyEffectLevel(self, value, qualifier):

        EffectStates = {
            'Transparency':     '0',
            'Red of RGB Key':   '1',
            'Green of RGB Key': '2',
            'Blue of RGB Key':  '3',
            'Level Key':        '4'
        }
        effect = qualifier['Effect']

        if effect in EffectStates:
            VideoKeyEffectLevelCmdString = 'w{}VKEY\r'.format(EffectStates[effect])
            self.__UpdateHelper('VideoKeyEffectLevel', VideoKeyEffectLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoKeyEffectLevel')

    def __MatchVideoKeyEffectLevel(self, match, tag):

        EffectStates = {
            '0': 'Transparency',
            '1': 'Red of RGB Key',
            '2': 'Green of RGB Key',
            '3': 'Blue of RGB Key',
            '4': 'Level Key',
        }

        qualifier = {
            'Effect': EffectStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 255:
            self.WriteStatus('VideoKeyEffectLevel', value, qualifier)

    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On':               '1',
            'Video and Sync':   '2',
            'Off':              '0'
        }

        if output in OutputStates and value in ValueStateValues:
            VideoMuteCmdString = '{}*{}B'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '2',
            'Preview': '1'
        }

        output = qualifier['Output']

        if output in OutputStates:
            VideoMuteCmdString = '{}B'.format(OutputStates[output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        OutputStates = {
            '2': 'Program',
            '1': 'Preview'
        }

        ValueStateValues = {
            '1': 'On',
            '2': 'Video and Sync',
            '0': 'Off'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

    def SetWipeEffect(self, value, qualifier):

        ValueStateValues = {
            'Soft Up':      '1',
            'Soft Down':    '2',
            'Soft Right':   '3',
            'Soft Left':    '4',
            'Hard Up':      '5',
            'Hard Down':    '6',
            'Hard Right':   '7',
            'Hard Left':    '8'
        }
        
        if value in ValueStateValues:
            WipeEffectCmdString = 'w{}WIPE\r'.format(ValueStateValues[value])
            self.__SetHelper('WipeEffect', WipeEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWipeEffect')

    def UpdateWipeEffect(self, value, qualifier):

        WipeEffectCmdString = 'wWIPE\r'
        self.__UpdateHelper('WipeEffect', WipeEffectCmdString, value, qualifier)

    def __MatchWipeEffect(self, match, tag):

        ValueStateValues = {
            '1': 'Soft Up',
            '2': 'Soft Down',
            '3': 'Soft Right',
            '4': 'Soft Left',
            '5': 'Hard Up',
            '6': 'Hard Down',
            '7': 'Hard Right',
            '8': 'Hard Left'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WipeEffect', value, None)

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

    def __MatchError(self, match, qualifier):

        self.counter = 0

        error_map = {
            1:  'Invalid input number',
            10: 'Invalid command',
            11: 'Invalid preset number',
            12: 'Invalid port or output number',
            13: 'Invalid parameter',
            14: 'Invalid for this configuration',
            17: 'Invalid command for signal type',
            22: 'Busy',
            24: 'Privilege violation',
            25: 'Device not present',
            26: 'Maximum number of connections exceeded',
            28: 'Bad Filename / File not Found',
        }

        error = int(match.group(1).decode())
        self.Error(['An error occurred: {}: {}.'.format(error, error_map.get(error, 'Unknown error'))])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()