from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'SR5004': self.mara_27_3573_SR5004,
            'SR6004': self.mara_27_3573_SR6004,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMode': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Bass': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDMIOutputSelection': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Treble': {'Status': {}},
            'TunerFrequency': {'Status': {}},
            'TunerPreset': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Speaker': {'Status': {}},
            'Zone3AudioMute': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Power': {'Status': {}},
        }

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetAudioMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Analog': '1',
            'Digital': '2',
            'HDMI': '4',
        }

        if value in ValueStateValues:
            AudioModeCmdString = '@INP:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMode', AudioModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMode')

    def UpdateAudioMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Analog',
            '2': 'Digital',
            '4': 'HDMI',
        }

        AudioModeCmdString = '@INP:?\r'
        res = self.__UpdateHelper('AudioMode', AudioModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AudioMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mode: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '@AMT:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        AudioMuteCmdString = '@AMT:?\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max': 6,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            BassCmdString = '@TOB:0{0:{1}03}\r'.format(ValueConstraints['Value'],
                                                       '+' if ValueConstraints['Value'] else '')
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '@TOB:?\r'
        res = self.__UpdateHelper('Bass', BassCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:8])
                if -6 <= value <= 6:
                    self.WriteStatus('Bass', value, qualifier)
                else:
                    raise ValueError
            except (ValueError, IndexError):
                self.Error(['Bass: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '@FKL:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        ExecutiveModeCmdString = '@FKL:?\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetHDMIOutputSelection(self, value, qualifier):

        ValueStateValues = {
            'Channel 1': '1',
            'Channel 2': '2',
        }

        if value in ValueStateValues:
            HDMIOutputSelectionCmdString = '@HDM:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('HDMIOutputSelection', HDMIOutputSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIOutputSelection')

    def UpdateHDMIOutputSelection(self, value, qualifier):

        ValueStateValues = {
            '1': 'Channel 1',
            '2': 'Channel 2',
        }

        HDMIOutputSelectionCmdString = '@HDM:?\r'
        res = self.__UpdateHelper('HDMIOutputSelection', HDMIOutputSelectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('HDMIOutputSelection', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDMI Output Selection: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        if value in self.input_states:
            InputCmdString = '@SRC:{}\r'.format(self.input_states[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '@SRC:?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.input_values[res[5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = '@OSD:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        OnScreenDisplayCmdString = '@OSD:?\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected result'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            PowerCmdString = '@PWR:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        PowerCmdString = '@PWR:?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Stereo': '1',
            'Dolby': '2',
            'PL II Movie': '3',
            'PL II Music': '5',
            'PL II Game': '7',
            'EX/ES': 'A',
            'Neural': 'D',
            'DTS ES': 'E',
            'NEO6 Cinema': 'F',
            'NEO6 Music': 'G',
            'Multi CH. Movie': 'H',
            'CS II Cinema': 'I',
            'CS II Music': 'J',
            'CS II Mono': 'K',
            'Virtual': 'L',
            'DTS': 'M',
            'DD+PL II x Movie': 'O',
            'DD+PL II x Music': 'P',
            'Source Direct': 'T',
            'Pure Direct': 'U',
            'Dolby PLIIz': 'Z',
            'Multi CH. (Music)': 'h',
        }

        if value in ValueStateValues:
            SurroundModeCmdString = '@SUR:0{}\r'.format(ValueStateValues[value])
            self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurroundMode')

    def UpdateSurroundMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Stereo',
            '2': 'Dolby',
            '4': 'PL II Movie',
            '6': 'PL II Music',
            '8': 'PL II Game',
            'A': 'EX/ES',
            'D': 'Neural',
            'E': 'DTS ES',
            'F': 'NEO6 Cinema',
            'G': 'NEO6 Music',
            'H': 'Multi CH. Movie',
            'I': 'CS II Cinema',
            'J': 'CS II Music',
            'K': 'CS II Mono',
            'L': 'Virtual',
            'M': 'DTS',
            'O': 'DD+PL II x Movie',
            'P': 'DD+PL II x Music',
            'T': 'Source Direct',
            'U': 'Pure Direct',
            'Z': 'Dolby PLIIz',
            'h': 'Multi CH. (Music)',
            '3': 'PL II x Movie',
            '5': 'PL II x Music',
            '7': 'PL II x Game',
            '9': 'Multi CH.',
            'C': 'DD EX',
            'N': 'DTS NEO6',
            'Q': 'AAC+PL II x MOVIE',
            'R': 'AAC+PL II x MUSIC',
            'V': 'SACD',
            'X': 'Head Phone',
            'a': 'Dolby Digital Plus',
            'b': 'Dolby Digital Plus EX',
            'c': 'Dolby True HD',
            'd': 'Dolby True HD EX',
            'e': 'DTS HD MSTR',
            'f': 'DTS HD HI RES',
            'g': 'DTS HD EXPRESS',
        }

        SurroundModeCmdString = '@SUR:?\r'
        res = self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('SurroundMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Surround Mode: Invalid/unexpected response'])

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max': 6,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            TrebleCmdString = '@TOT:0{0:{1}03}'.format(ValueConstraints['Value'],
                                                       '+' if ValueConstraints['Value'] else '')
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '@TOT:?\r'
        res = self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:8])
                if -6 <= value <= 6:
                    self.WriteStatus('Treble', value, qualifier)
                else:
                    raise ValueError
            except (ValueError, IndexError):
                self.Error(['Treble: Invalid/unexpected response'])

    def SetTunerFrequency(self, value, qualifier):

        ValueStateValues = {
            'Up': '1',
            'Down': '2',
            'Scan Forward': '3',
            'Scan Reverse': '4',
        }

        if value in ValueStateValues:
            TunerFrequencyCmdString = '@TFQ:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('TunerFrequency', TunerFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTunerFrequency')

    def SetTunerPreset(self, value, qualifier):

        ValueStateValues = {
            'Up': '1',
            'Down': '2',
        }

        if value in ValueStateValues:
            TunerPresetCmdString = '@TPR:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTunerPreset')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '@VMT:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        VideoMuteCmdString = '@VMT:?\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -71,
            'Max': 18,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            VolumeCmdString = '@VOL:0{1}{0:02}\r'.format(abs(ValueConstraints['Value']),
                                                         '+' if ValueConstraints['Value'] > 0 else '-')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '@VOL:?\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res and 'ZZ' not in res:
            try:
                value = int(res[5:8])
                if -71 <= value <= 18:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    raise ValueError
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            Zone2AudioMuteCmdString = '@MSM:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2AudioMute')

    def UpdateZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        Zone2AudioMuteCmdString = '@MSM:?\r'
        res = self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone2AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 2 Audio Mute: Invalid/unexpected response'])

    def SetZone2Input(self, value, qualifier):

        if value in self.input_states:
            Zone2InputCmdString = '@SSC:{}\r'.format(self.input_states[value])
            self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Input')

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '@MSC:?\r'
        res = self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
        if res:
            try:
                value = self.input_values[res[5]]
                self.WriteStatus('Zone2Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 2 Input: Invalid/unexpected response'])

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            Zone2PowerCmdString = '@MPW:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Power')

    def UpdateZone2Power(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        Zone2PowerCmdString = '@MPW:?\r'
        res = self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone2Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 2 Power: Invalid/unexpected response'])

    def SetZone2Speaker(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            Zone2SpeakerCmdString = '@MSP:{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone2Speaker', Zone2SpeakerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Speaker')

    def UpdateZone2Speaker(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        Zone2SpeakerCmdString = '@MSP:?\r'
        res = self.__UpdateHelper('Zone2Speaker', Zone2SpeakerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone2Speaker', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 2 Speaker: Invalid/unexpected response'])

    def SetZone3AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            Zone3AudioMuteCmdString = '@MAM={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3AudioMute')

    def UpdateZone3AudioMute(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        Zone3AudioMuteCmdString = '@MAM=?\r'
        res = self.__UpdateHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone3AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 3 Audio Mute: Invalid/unexpected response'])

    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'TV': '1',
            'DVD': '2',
            'VCR 1': '3',
            'VCR 2': '4',
            'DSS': '5',
            'AUX': '9',
            'CD/CD-R': 'C',
            'Sirius': 'K',
            'BD': 'M',
            'M-XPort': 'N',
        }

        if value in ValueStateValues:
            Zone3InputCmdString = '@MSC={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Input')

    def UpdateZone3Input(self, value, qualifier):

        ValueStateValues = {
            '1': 'TV',
            '2': 'DVD',
            '3': 'VCR 1',
            '4': 'VCR 2',
            '5': 'DSS',
            '9': 'AUX',
            'C': 'CD/CD-R',
            'K': 'Sirius',
            'M': 'BD',
            'N': 'M-XPort',
        }

        Zone3InputCmdString = '@MSC=?\r'
        res = self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone3Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 3 Input: Invalid/unexpected response'])

    def SetZone3Power(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
        }

        if value in ValueStateValues:
            Zone3PowerCmdString = '@MPW={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Power')

    def UpdateZone3Power(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
        }

        Zone3PowerCmdString = '@MPW=?\r'
        res = self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Zone3Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zone 3 Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response == '@\x15\r':
                self.Error(['{0}: {1}'.format(sourceCmdName, 'Received incorrect Command data')])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
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
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def mara_27_3573_SR5004(self):
        self.input_states = {
            'TV':      '1',
            'DVD':     '2',
            'VCR 1':   '3',
            'VCR 2':   '4',
            'DSS':     '5',
            'AUX':     '9',
            'CD/CD-R': 'C',
            'Tuner':   'F',
            'FM':      'G',
            'AM':      'H',
            'XM':      'J',
            'Sirius':  'K',
            'BD':      'M',
            'M-XPort': 'N',
        }

        self.input_values = {
            '1': 'TV',
            '2': 'DVD',
            '3': 'VCR 1',
            '4': 'VCR 2',
            '5': 'DSS',
            '9': 'AUX',
            'C': 'CD/CD-R',
            'F': 'Tuner',
            'G': 'FM',
            'H': 'AM',
            'J': 'XM',
            'K': 'Sirius',
            'M': 'BD',
            'N': 'M-XPort',
        }


    def mara_27_3573_SR6004(self):
        self.input_states = {
            'TV':      '1',
            'DVD':     '2',
            'VCR 1':   '3',
            'VCR 2':   '4',
            'DSS':     '5',
            'USB':     '7',
            'AUX':     '9',
            'CD/CD-R': 'C',
            'Tuner':   'F',
            'FM':      'G',
            'AM':      'H',
            'XM':      'J',
            'Sirius':  'K',
            'BD':      'M',
            'M-XPort': 'N',
        }

        self.input_values = {
            '1': 'TV',
            '2': 'DVD',
            '3': 'VCR 1',
            '4': 'VCR 2',
            '5': 'DSS',
            '7': 'USB',
            '9': 'AUX',
            'C': 'CD/CD-R',
            'F': 'Tuner',
            'G': 'FM',
            'H': 'AM',
            'J': 'XM',
            'K': 'Sirius',
            'M': 'BD',
            'N': 'M-XPort',
        }
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

