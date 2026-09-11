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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'BlueScreen': {'Status': {}},
            'DissolveSpeed': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Output', 'Type'], 'Status': {}},
            'InputPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'InputPresetSave': {'Parameters': ['Output'], 'Status': {}},
            'Logo': {'Parameters': ['Logo', 'Output'], 'Status': {}},
            'PIPDurationStatus': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSubeffectDuration': {'Parameters': ['Duration'], 'Status': {}},
            'PIPSubeffectStatus': {'Status': {}},
            'RefreshRateStatus': {'Status': {}},
            'ResolutionAndRefreshRate': {'Parameters': ['Refresh'], 'Status': {}},
            'ResolutionStatus': {'Status': {}},
            'RGBDelay': {'Status': {}},
            'SwitchEffect': {'Status': {}},
            'SwitchMode': {'Status': {}},
            'TestPattern': {'Parameters': ['Output'], 'Status': {}},
            'TitleKeyThreshold': {'Status': {}},
            'Transition': {'Status': {}},
            'UserPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'UserPresetSave': {'Parameters': ['Output'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Status': {}},
            'WipeDurationStatus': {'Status': {}},
            'WipeSubeffectDuration': {'Parameters': ['Duration'], 'Status': {}},
            'WipeSubeffectStatus': {'Status': {}},
        }

        self.VerboseDisabled = True

        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In([1-6]) Aud([-+]\d+)\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'([12])Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Blu([01])\r\n'), self.__MatchBlueScreen, None)
            self.AddMatchString(re.compile(b'Exe([0-4])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'([12])Frz([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Out([12]) In([1-6]) (All|RGB|Aud)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'([12])Lbu([12])\*([01])\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Rte(\d+)\*(\d+)\r\n'), self.__MatchResolutionStatus, None)
            self.AddMatchString(re.compile(b'Dly(\d+)\r\n'), self.__MatchRGBDelay, None)
            self.AddMatchString(re.compile(b'Eff([1-4])\*(\d+)\*(\d+)\*\d+\*\d+\r\n'), self.__MatchSwitchEffect, None)
            self.AddMatchString(re.compile(b'Psm([01])\r\n'), self.__MatchSwitchMode, None)
            self.AddMatchString(re.compile(b'Tst([0-3])\*(\d+)\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'([12])Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol(\d+)\r\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            if self.devicePassword:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0
        self.SetVerbose()

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])
        self.SetVerbose()

    def SetVerbose(self):
        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioGainAttenuation(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 6 and -18 <= value <= 24:
            if value < 0:
                AudioGainAttenuationCmdString = '{}*{}g'.format(input_, value)
            else:
                AudioGainAttenuationCmdString = '{}*{}G'.format(input_, value)

            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 6:
            AudioGainAttenuationCmdString = '{}G'.format(input_)
            self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = int(match.group(2).decode())
        if -18 <= value <= 24:
            self.WriteStatus('AudioGainAttenuation', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if output in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates:
            AudioMuteCmdString = '{}*Z'.format(OutputStates[output])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview'
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

        ValueStateValues = {
            'Program': '1',
            'Preview': '2',
            'Both': '3'
        }

        if value in ValueStateValues:
            AutoImageCmdString = '14*0{}#'.format(ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBlueScreen(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            BlueScreenCmdString = '8*{}#'.format(ValueStateValues[value])
            self.__SetHelper('BlueScreen', BlueScreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlueScreen')

    def UpdateBlueScreen(self, value, qualifier):

        BlueScreenCmdString = '8#'
        self.__UpdateHelper('BlueScreen', BlueScreenCmdString, value, qualifier)

    def __MatchBlueScreen(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BlueScreen', value, None)

    def SetDissolveSpeed(self, value, qualifier):

        if 0 <= value <= 5:
            DissolveSpeedCmdString = '4*1*{}#'.format(int(value * 10))
            self.__SetHelper('DissolveSpeed', DissolveSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDissolveSpeed')

    def UpdateDissolveSpeed(self, value, qualifier):

        DissolveSpeedCmdString = '4*1#'
        self.__UpdateHelper('DissolveSpeed', DissolveSpeedCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '4',
            'Volume Free': '3',
            'Program': '1',
            'Switch Free': '2',
            'Off': '0'
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
            '4': 'On',
            '3': 'Volume Free',
            '1': 'Program',
            '2': 'Switch Free',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }
        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if output in OutputStates and value in ValueStateValues:
            FreezeCmdString = '{}*{}F'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates:
            FreezeCmdString = '{}F'.format(OutputStates[output])
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview'
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
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }
        type_ = qualifier['Type']

        if output in OutputStates and type_ in TypeStates and 1 <= int(value) <= 6:
            InputCmdString = '{}*{}{}'.format(OutputStates[output], value, TypeStates[type_])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }

        type_ = qualifier['Type']

        if output in OutputStates and type_ in TypeStates:
            InputCmdString = '{}{}'.format(OutputStates[output], TypeStates[type_])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview'
        }

        output = OutputStates[match.group(1).decode()]

        TypeStates = {
            'Aud': 'Audio',
            'RGB': 'Video',
            'All': 'Audio/Video'
        }

        type_ = TypeStates[match.group(3).decode()]

        qualifier = {
            'Output': output,
            'Type': type_
        }

        value = match.group(2).decode()
        self.WriteStatus('Input', value, qualifier)

        if type_ == 'Audio/Video':
            self.WriteStatus('Input', value, {'Output': output, 'Type': 'Audio'})
            self.WriteStatus('Input', value, {'Output': output, 'Type': 'Video'})
        elif self.ReadStatus('Input', {'Output': output, 'Type': 'Audio'}) and self.ReadStatus('Input', {'Output': output, 'Type': 'Video'}):
            op_type = 'Video' if type_ == 'Audio' else 'Audio'

            if self.ReadStatus('Input', {'Output': output, 'Type': op_type}) != value:
                self.WriteStatus('Input', '0', {'Output': output, 'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', value, {'Output': output, 'Type': 'Audio/Video'})

    def SetInputPresetRecall(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 128:
            InputPresetRecallCmdString = '1*{}*{}.'.format(OutputStates[output], int(value))
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 128:
            InputPresetSaveCmdString = '1*{}*{},'.format(OutputStates[output], int(value))
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def SetLogo(self, value, qualifier):

        logo = int(qualifier['Logo'])

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= logo <= 2 and output in OutputStates and value in ValueStateValues:
            LogoCmdString = '39*{}*{}*{}#'.format(OutputStates[output], logo, ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        logo = int(qualifier['Logo'])

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if 1 <= logo <= 2 and output in OutputStates:
            LogoCmdString = '39*{}*{}#'.format(OutputStates[output], logo)
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Logo': match.group(2).decode(),
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Logo', value, qualifier)

    def UpdatePIPDurationStatus(self, value, qualifier):

        PIPDurationStatusCmdString = '4*4#'
        self.__UpdateHelper('PIPDurationStatus', PIPDurationStatusCmdString, value, qualifier)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Up': '+/',
            'Down': '-/',
            'Left': '-H',
            'Right': '+H'
        }

        if value in ValueStateValues:
            PIPPositionCmdString = '4{}'.format(ValueStateValues[value])
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def SetPIPSubeffectDuration(self, value, qualifier):

        duration = qualifier['Duration']

        ValueStateValues = {
            'Cut': '0',
            'Dissolve': '1',
            'Soft Right': '2',
            'Soft Left': '3',
            'Soft Up': '4',
            'Soft Down': '5',
            'Soft Center In': '6',
            'Soft Center Out': '7',
            'Soft Curtain In': '8',
            'Soft Curtain Out': '9',
            'Soft Square In': '10',
            'Soft Square Out': '11',
            'Soft Plus In': '12',
            'Soft Plus Out': '13',
            'Hard Right': '14',
            'Hard Left': '15',
            'Hard Up': '16',
            'Hard Down': '17',
            'Hard Center In': '18',
            'Hard Center Out': '19',
            'Hard Curtain In': '20',
            'Hard Curtain Out': '21',
            'Hard Square In': '22',
            'Hard Square Out': '23',
            'Hard Plus In': '24',
            'Hard Plus Out': '25'
        }

        if 0 <= duration <= 5 and value in ValueStateValues:
            PIPSubeffectDurationCmdString = '4*4*{}*{}#'.format(int(duration * 10), ValueStateValues[value])
            self.__SetHelper('PIPSubeffectDuration', PIPSubeffectDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSubeffectDuration')

    def UpdatePIPSubeffectStatus(self, value, qualifier):

        self.UpdatePIPDurationStatus(value, qualifier)

    def UpdateRefreshRateStatus(self, value, qualifier):

        self.UpdateResolutionStatus(value, qualifier)

    def SetResolutionAndRefreshRate(self, value, qualifier):

        RefreshStates = {
            '50 Hz': '1',
            '60 Hz': '2',
            '72 Hz': '3',
            '96 Hz': '4',
            '100 Hz': '5',
            '120 Hz': '6',
            '24 Hz': '7',
            '25 Hz': '8',
            '30 Hz': '9',
            '59.94 Hz': '10'
        }

        refresh = qualifier['Refresh']

        ValueStateValues = {
            '640x480': '01',
            '800x600': '02',
            '852x480': '03',
            '1024x768': '04',
            '1024x852': '05',
            '1024x1024': '06',
            '1280x768': '07',
            '1280x1024': '08',
            '1360x765': '09',
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
            '1864x1050': '20',
            '1280x800': '21',
            '1440x900': '22',
            '1680x1050': '23',
            '1080p Sharp': '24',
            '1920x1200': '25'
        }

        if refresh in RefreshStates and value in ValueStateValues:
            ResolutionAndRefreshRateCmdString = '{}*{}='.format(ValueStateValues[value], RefreshStates[refresh])
            self.__SetHelper('ResolutionAndRefreshRate', ResolutionAndRefreshRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolutionAndRefreshRate')

    def UpdateResolutionStatus(self, value, qualifier):

        ResolutionStatusCmdString = '='
        self.__UpdateHelper('ResolutionStatus', ResolutionStatusCmdString, value, qualifier)

    def __MatchResolutionStatus(self, match, tag):

        RefreshRateStatus_ValueStateValues = {
            '1': '50 Hz',
            '2': '60 Hz',
            '3': '72 Hz',
            '4': '96 Hz',
            '5': '100 Hz',
            '6': '120 Hz',
            '7': '24 Hz',
            '8': '25 Hz',
            '9': '30 Hz',
            '10': '59.94 Hz'
        }

        ResolutionStatus_ValueStateValues = {
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
            '20': '1864x1050',
            '21': '1280x800',
            '22': '1440x900',
            '23': '1680x1050',
            '24': '1080p Sharp',
            '25': '1920x1200'
        }

        try:
            refresh_rate = RefreshRateStatus_ValueStateValues[match.group(2).decode()]
            self.WriteStatus('RefreshRateStatus', refresh_rate, None)
        except KeyError:
            pass

        try:
            resolution = ResolutionStatus_ValueStateValues[match.group(1).decode()]
            self.WriteStatus('ResolutionStatus', resolution, None)
        except KeyError:
            pass

    def SetRGBDelay(self, value, qualifier):

        if 0 <= value <= 5:
            RGBDelayCmdString = '3*{}#'.format(int(value * 10))
            self.__SetHelper('RGBDelay', RGBDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRGBDelay')

    def UpdateRGBDelay(self, value, qualifier):

        RGBDelayCmdString = '3#'
        self.__UpdateHelper('RGBDelay', RGBDelayCmdString, value, qualifier)

    def __MatchRGBDelay(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 50:
            self.WriteStatus('RGBDelay', value / 10, None)

    def SetSwitchEffect(self, value, qualifier):

        ValueStateValues = {
            'Dissolve': '1',
            'Wipe': '2',
            'Title': '3',
            'PIP': '4'
        }

        if value in ValueStateValues:
            SwitchEffectCmdString = '4*{}*#'.format(ValueStateValues[value])
            self.__SetHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchEffect')

    def UpdateSwitchEffect(self, value, qualifier):

        SwitchEffectCmdString = '4*0#'
        self.__UpdateHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)

    def __MatchSwitchEffect(self, match, tag):

        SwitchEffect_ValueStateValues = {
            '1': 'Dissolve',
            '2': 'Wipe',
            '3': 'Title',
            '4': 'PIP'
        }

        switch_effect = SwitchEffect_ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SwitchEffect', switch_effect, None)

        if switch_effect == 'Dissolve':
            dissolve_speed = int(match.group(2).decode())
            if 0 <= dissolve_speed <= 50:
                self.WriteStatus('DissolveSpeed', dissolve_speed / 10, None)

        elif switch_effect == 'PIP':
            pip_duration = int(match.group(2).decode())
            if 0 <= pip_duration <= 50:
                self.WriteStatus('PIPDurationStatus', pip_duration / 10, None)
            PIPSubeffectStatus_ValueStatevalues = {
                0: 'Cut',
                1: 'Dissolve',
                2: 'Soft Right',
                3: 'Soft Left',
                4: 'Soft Up',
                5: 'Soft Down',
                6: 'Soft Center In',
                7: 'Soft Center Out',
                8: 'Soft Curtain In',
                9: 'Soft Curtain Out',
                10: 'Soft Square In',
                11: 'Soft Square Out',
                12: 'Soft Plus In',
                13: 'Soft Plus Out',
                14: 'Hard Right',
                15: 'Hard Left',
                16: 'Hard Up',
                17: 'Hard Down',
                18: 'Hard Center In',
                19: 'Hard Center Out',
                20: 'Hard Curtain In',
                21: 'Hard Curtain Out',
                22: 'Hard Square In',
                23: 'Hard Square Out',
                24: 'Hard Plus In',
                25: 'Hard Plus Out'
            }
            try:
                pip_subeffect = PIPSubeffectStatus_ValueStatevalues[int(match.group(3).decode())]
                self.WriteStatus('PIPSubeffectStatus', pip_subeffect, None)
            except KeyError:
                pass

        elif switch_effect == 'Title':
            title_key_threshold = int(match.group(2).decode())
            if 0 <= title_key_threshold <= 255:
                self.WriteStatus('TitleKeyThreshold', title_key_threshold, None)

        elif switch_effect == 'Wipe':
            wipe_duration = int(match.group(2).decode())
            if 0 <= wipe_duration <= 50:
                self.WriteStatus('WipeDurationStatus', wipe_duration / 10, None)
            WipeSubeffectStatus_ValueStateValues = {
                2: 'Soft Right',
                3: 'Soft Left',
                4: 'Soft Up',
                5: 'Soft Down',
                6: 'Soft Center In',
                7: 'Soft Center Out',
                8: 'Soft Curtain In',
                9: 'Soft Curtain Out',
                10: 'Soft Square In',
                11: 'Soft Square Out',
                12: 'Soft Plus In',
                13: 'Soft Plus Out',
                14: 'Hard Right',
                15: 'Hard Left',
                16: 'Hard Up',
                17: 'Hard Down',
                18: 'Hard Center In',
                19: 'Hard Center Out',
                20: 'Hard Curtain In',
                21: 'Hard Curtain Out',
                22: 'Hard Square In',
                23: 'Hard Square Out',
                24: 'Hard Plus In',
                25: 'Hard Plus Out'
            }
            try:
                wipe_subeffect = WipeSubeffectStatus_ValueStateValues[int(match.group(3).decode())]
                self.WriteStatus('WipeSubeffectStatus', wipe_subeffect, None)
            except KeyError:
                pass

    def SetSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Swap': '0',
            'Stay': '1'
        }

        if value in ValueStateValues:
            SwitchModeCmdString = '20*{}#'.format(ValueStateValues[value])
            self.__SetHelper('SwitchMode', SwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchMode')

    def UpdateSwitchMode(self, value, qualifier):

        SwitchModeCmdString = '20#'
        self.__UpdateHelper('SwitchMode', SwitchModeCmdString, value, qualifier)

    def __MatchSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Swap',
            '1': 'Stay'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SwitchMode', value, None)

    def SetTestPattern(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2',
            'Both': '3'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'Color Bars': 0,
            'Crosshatch 4:3': 1,
            '4x4 Crosshatch': 2,
            'Split Grayscale': 3,
            'Ramp': 4,
            'Alternating Pixels': 5,
            'Crop': 6,
            'Aspect Ratio 1.33': 7,
            'Aspect Ratio 1.78': 8,
            'Aspect Ratio 1.85': 9,
            'Aspect Ratio 2.35': 10,
            'Off': None
        }

        if output in OutputStates and value in ValueStateValues:
            if value == 'Off':
                TestPatternCmdString = '0*00J'
            else:
                TestPatternCmdString = '{}*{:02d}J'.format(OutputStates[output], ValueStateValues[value])

            if TestPatternCmdString:
                self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        OutputStates = {
            'Program':  '1',
            'Preview':  '2',
            'Both':     '3'
        }

        output = qualifier['Output']

        if output in OutputStates:
            TestPatternCmdString = 'J'
            self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTestPattern')

    def __MatchTestPattern(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview',
            '3': 'Both',
            '0': 'Off'
        }

        output = OutputStates[match.group(1).decode()]

        ValueStateValues = {
            0:  'Color Bars',
            1:  'Crosshatch 4:3',
            2:  '4x4 Crosshatch',
            3:  'Split Grayscale',
            4:  'Ramp',
            5:  'Alternating Pixels',
            6:  'Crop',
            7:  'Aspect Ratio 1.33',
            8:  'Aspect Ratio 1.78',
            9:  'Aspect Ratio 1.85',
            10: 'Aspect Ratio 2.35'
        }

        try:
            value = ValueStateValues[int(match.group(2).decode())]

            if output == 'Off':
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Program'})
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Preview'})
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
            elif output == 'Program':
                self.WriteStatus('TestPattern', value, {'Output': 'Program'})
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Preview'})
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
            elif output == 'Preview':
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Program'})
                self.WriteStatus('TestPattern', value, {'Output': 'Preview'})
                self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
            elif output == 'Both':
                self.WriteStatus('TestPattern', value, {'Output': 'Program'})
                self.WriteStatus('TestPattern', value, {'Output': 'Preview'})
                self.WriteStatus('TestPattern', value, {'Output': 'Both'})
        except KeyError:
            pass

    def SetTitleKeyThreshold(self, value, qualifier):

        if 0 <= value <= 255:
            TitleKeyThresholdCmdString = '4*3*{}#'.format(value)
            self.__SetHelper('TitleKeyThreshold', TitleKeyThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTitleKeyThreshold')

    def UpdateTitleKeyThreshold(self, value, qualifier):

        TitleKeyThresholdCmdString = '4*3#'
        self.__UpdateHelper('TitleKeyThreshold', TitleKeyThresholdCmdString, value, qualifier)

    def SetTransition(self, value, qualifier):

        Transition_ValueStateValues = [
            'Cut',
            'Take'
        ]

        SwitchEffect_ValueStateValues = {
            'Dissolve': '1',
            'Wipe':     '2',
            'Title':    '3',
            'PIP':      '4'
        }

        if value in Transition_ValueStateValues:
            if value == 'Cut':
                TransitionCmdString = '1*00%'
            else:
                switch_effect = self.ReadStatus('SwitchEffect', qualifier)

                if switch_effect:
                    TransitionCmdString = '1*0{}%'.format(SwitchEffect_ValueStateValues[switch_effect])
                else:
                    self.Discard('Invalid Command for SetTransition')
                    return

            self.__SetHelper('Transition', TransitionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransition')

    def SetUserPresetRecall(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 3:
            UserPresetRecallCmdString = '{}*{}.'.format(OutputStates[output], value)
            self.__SetHelper('UserPresetRecall', UserPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetRecall')

    def SetUserPresetSave(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 3:
            UserPresetSaveCmdString = '{}*{},'.format(OutputStates[output], value)
            self.__SetHelper('UserPresetSave', UserPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetSave')
    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in OutputStates and value in ValueStateValues:
            VideoMuteCmdString = '{}*{}B'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates:
            VideoMuteCmdString = '{}*B'.format(OutputStates[output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '{}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

    def UpdateWipeDurationStatus(self, value, qualifier):

        WipeDurationStatusCmdString = '4*2#'
        self.__UpdateHelper('WipeDurationStatus', WipeDurationStatusCmdString, value, qualifier)

    def SetWipeSubeffectDuration(self, value, qualifier):

        duration = qualifier['Duration']

        ValueStateValues = {
            'Soft Right':       '02',
            'Soft Left':        '03',
            'Soft Up':          '04',
            'Soft Down':        '05',
            'Soft Center In':   '06',
            'Soft Center Out':  '07',
            'Soft Curtain In':  '08',
            'Soft Curtain Out': '09',
            'Soft Square In':   '10',
            'Soft Square Out':  '11',
            'Soft Plus In':     '12',
            'Soft Plus Out':    '13',
            'Hard Right':       '14',
            'Hard Left':        '15',
            'Hard Up':          '16',
            'Hard Down':        '17',
            'Hard Center In':   '18',
            'Hard Center Out':  '19',
            'Hard Curtain In':  '20',
            'Hard Curtain Out': '21',
            'Hard Square In':   '22',
            'Hard Square Out':  '23',
            'Hard Plus In':     '24',
            'Hard Plus Out':    '25'
        }

        if 0 <= duration <= 5 and value in ValueStateValues:
            WipeSubeffectDurationCmdString = '4*2*{}*{}#'.format(int(duration * 10), ValueStateValues[value])
            self.__SetHelper('WipeSubeffectDuration', WipeSubeffectDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWipeSubeffectDuration')

    def UpdateWipeSubeffectStatus(self, value, qualifier):

        self.UpdateWipeDurationStatus(value, qualifier)

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

    
    def __MatchError(self, match, tag):
        self.counter = 0

        error_map = {
            1:  'Invalid input channel number (too large)',
            10: 'Invalid command',
            11: 'Invalid preset number (too large)',
            12: 'Invalid output number (too large)',
            13: 'Invalid value (out of range)',
            14: 'Invalid for this configuration'
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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

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
        
        # check incoming data if it matched any expected data from device module
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