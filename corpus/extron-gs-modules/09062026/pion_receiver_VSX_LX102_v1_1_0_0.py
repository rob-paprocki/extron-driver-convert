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

        self.Models = {
            'VSX-LX102': self.pion_27_3276_LX102,
            'VSX-LX103': self.pion_27_3276_LX103,
            'VSX-LX301': self.pion_27_3276_LX301,
            'VSX-LX302': self.pion_27_3276_LX302,
            'VSX-LX303': self.pion_27_3276_LX303,
            'VSX-LX503': self.pion_27_3276_LX503,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AudioSelect': { 'Status': {}},
            'FrontBass': { 'Status': {}},
            'FrontTreble': { 'Status': {}},
            'Input': { 'Status': {}},
            'ListeningMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': { 'Status': {}},
            'Resolution': { 'Status': {}},
            'TunerBand': { 'Status': {}},
            'TunerFrequencyCommand': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone2Mute': { 'Status': {}},
            'Zone2Power': { 'Status': {}},
            'Zone2Preset': { 'Status': {}},
            'Zone2Volume': { 'Status': {}},
            'Zone3Input': { 'Status': {}},
            'Zone3Mute': { 'Status': {}},
            'Zone3Power': { 'Status': {}},
            'Zone3Preset': { 'Status': {}},
            'Zone3Volume': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!1AMT(0[01])\x1A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'!1SLA(0[2457])\x1A'), self.__MatchAudioSelect, None)
            self.AddMatchString(re.compile(b'!1TFRB([\-+0][0-9A])T([\-+0][0-9A])\x1A'), self.__MatchFrontBass, None)
            self.AddMatchString(re.compile(b'!1SLI(01|02|03|10|11|12|22|23|24|25|26|29|2A|2B|2E|55|56)\x1A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'!1LMD(00|01|03|05|06|08|09|0A|0B|0C|0D|0E|0F|11|13|1F|40|80|82|83|FF)\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'!1PWR(0[01])\x1A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'!1RES(0[01])\x1A'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(b'!1MVL([0-9A-F]{2})\x1A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'!1SLZ(01|02|03|10|11|12|22|23|24|25|26|29|2A|2B|2E|80)\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'!1ZMT(0[01])\x1A'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'!1ZPW(0[01])\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'!1ZVL([0-9A-F]{2})\x1A'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'!1SL3(01|02|03|10|11|12|22|23|24|25|26|29|2A|2B|2C|2E|80)\x1A'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'!1MT3(0[01])\x1A'), self.__MatchZone3Mute, None)
            self.AddMatchString(re.compile(b'!1PW3(0[01])\x1A'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'!1VL3([0-9A-F]{2})\x1A'), self.__MatchZone3Volume, None)

        self.set_input_states = {
            'Cable/SAT':    '01',
            'Game':         '02',
            'Aux':          '03',
            'BD/DVD':       '10',
            'Strm Box':     '11',
            'TV':           '12',
            'Phono':        '22',
            'CD':           '23',
            'FM':           '24',
            'AM':           '25',
            'Tuner':        '26',
            'USB Front':    '29',
            'USB Back':     '2A',
            'Network':      '2B',
            'USB Toggle':   '2C',
            'Bluetooth':    '2E',
            'HDMI 5':       '55',
            'HDMI 6':       '56'
        }

        self.update_input_states = {
            '01': 'Cable/SAT',
            '02': 'Game',
            '03': 'Aux',
            '10': 'BD/DVD',
            '11': 'Strm Box',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'USB Front',
            '2A': 'USB Back',
            '2B': 'Network',
            '2E': 'Bluetooth',
            '55': 'HDMI 5',
            '56': 'HDMI 6'
        }

        self.set_listening_mode_states = {
            'Stereo':                       '00',
            'Direct':                       '01',
            'Film':                         '03',
            'Action':                       '05',
            'Musical':                      '06',
            'Orchestra':                    '08',
            'Unplugged':                    '09',
            'Studio-Mix':                   '0A',
            'TV Logic':                     '0B',
            'All Ch Stereo':                '0C',
            'Theater-Dimensional':          '0D',
            'Enhanced 7/Enhance':           '0E',
            'Mono':                         '0F',
            'Pure Audio':                   '11',
            'Full Mono':                    '13',
            'Whole House Mode':             '1F',
            'Straight Decode':              '40',
            'Dolby Atmos/Dolby Surround':   '80',
            'DTS:X/Neural:X':               '82',
            'Neo:6 Music/Neo:X Music':      '83',
            'Auto Surround':                'FF'
        }

        self.update_listening_mode_states = {
            '00': 'Stereo',
            '01': 'Direct',
            '03': 'Film',
            '05': 'Action',
            '06': 'Musical',
            '08': 'Orchestra',
            '09': 'Unplugged',
            '0A': 'Studio-Mix',
            '0B': 'TV Logic',
            '0C': 'All Ch Stereo',
            '0D': 'Theater-Dimensional',
            '0E': 'Enhanced 7/Enhance',
            '0F': 'Mono',
            '11': 'Pure Audio',
            '13': 'Full Mono',
            '1F': 'Whole House Mode',
            '40': 'Straight Decode',
            '80': 'Dolby Atmos/Dolby Surround',
            '82': 'DTS:X/Neural:X',
            '83': 'Neo:6 Music/Neo:X Music',
            'FF': 'Auto Surround'
        }

        self.set_zone_2_input_states = {
            'Cable/SAT':    '01',
            'Game':         '02',
            'Aux':          '03',
            'BD/DVD':       '10',
            'Strm Box':     '11',
            'TV':           '12',
            'Phono':        '22',
            'CD':           '23',
            'FM':           '24',
            'AM':           '25',
            'Tuner':        '26',
            'USB Front':    '29',
            'USB Back':     '2A',
            'Network':      '2B',
            'USB Toggle':   '2C',
            'Bluetooth':    '2E',
            'Source':       '80'
        }

        self.update_zone_2_input_states = {
            '01': 'Cable/SAT',
            '02': 'Game',
            '03': 'Aux',
            '10': 'BD/DVD',
            '11': 'Strm Box',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'USB Front',
            '2A': 'USB Back',
            '2B': 'Network',
            '2E': 'Bluetooth',
            '80': 'Source'
        }

        self.set_zone_3_input_states = {
            'Cable/SAT':    '01',
            'Game':         '02',
            'Aux':          '03',
            'DVD':          '10',
            'Strm Box':     '11',
            'TV':           '12',
            'Phono':        '22',
            'CD':           '23',
            'FM':           '24',
            'AM':           '25',
            'Tuner':        '26',
            'USB Front':    '29',
            'USB Back':     '2A',
            'Network':      '2B',
            'USB Toggle':   '2C',
            'Bluetooth':    '2E',
            'Source':       '80'
        }

        self.update_zone_3_input_states = {
            '01': 'Cable/SAT',
            '02': 'Game',
            '03': 'Aux',
            '10': 'DVD',
            '11': 'Strm Box',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'USB Front',
            '2A': 'USB Back',
            '2B': 'Network',
            '2E': 'Bluetooth',
            '80': 'Source'
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        AudioMuteCmdString = '!1AMT{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '!1AMTQSTN\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAudioSelect(self, value, qualifier):

        ValueStateValues = {
            'Analog':   '02',
            'HDMI':     '04',
            'Coax/Opt': '05',
            'Arc':      '07'
        }

        AudioSelectCmdString = '!1SLA{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AudioSelect', AudioSelectCmdString, value, qualifier)

    def UpdateAudioSelect(self, value, qualifier):

        AudioSelectCmdString = '!1SLAQSTN\r\n'
        self.__UpdateHelper('AudioSelect', AudioSelectCmdString, value, qualifier)

    def __MatchAudioSelect(self, match, tag):

        ValueStateValues = {
            '02': 'Analog',
            '04': 'HDMI',
            '05': 'Coax/Opt',
            '07': 'Arc'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioSelect', value, None)

    def SetFrontBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FrontBassCmdString = '!1TFRB{:02X}\r\n'.format(value)
            if value > 0:
                FrontBassCmdString = FrontBassCmdString[:6] + '+' + FrontBassCmdString[7:]

            self.__SetHelper('FrontBass', FrontBassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFrontBass')
    def UpdateFrontBass(self, value, qualifier):

        FrontBassCmdString = '!1TFRQSTN\r\n'
        self.__UpdateHelper('FrontBass', FrontBassCmdString, value, qualifier)

    def __MatchFrontBass(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('FrontBass', value, None)

        value = int(match.group(2).decode(), 16)
        self.WriteStatus('FrontTreble', value, None)

    def SetFrontTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FrontTrebleCmdString = '!1TFRT{:02X}\r\n'.format(value)
            if value > 0:
                FrontTrebleCmdString = FrontTrebleCmdString[:6] + '+' + FrontTrebleCmdString[7:]

            self.__SetHelper('FrontTreble', FrontTrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFrontTreble')

    def UpdateFrontTreble(self, value, qualifier):

        self.UpdateFrontBass(value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = '!1SLI{}\r\n'.format(self.set_input_states[value])
        if value != 'USB Toggle':
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!1SLIQSTN\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.update_input_states[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ListeningModeCmdString = '!1LMD{}\r\n'.format(self.set_listening_mode_states[value])
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

        ListeningModeCmdString = '!1LMDQSTN\r\n'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        value = self.update_listening_mode_states[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        if value in {'Up', 'Down', 'Right', 'Left', 'Enter', 'Exit', 'Quick Setup', 'Home'}:
            if value.startswith('Quick'):
                value = 'Quick'
            MenuNavigationCmdString = '!1OSD{}\r\n'.format(value.upper())
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        PowerCmdString = '!1PWR{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '!1PWRQSTN\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 40:
            PresetCmdString = '!1PRS{0:02X}\r\n'.format(value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            'Through':  '00',
            'Auto':     '01'
        }

        ResolutionCmdString = '!1RES{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        ResolutionCmdString = '!1RESQSTN\r\n'
        self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        ValueStateValues = {
            '00': 'Through',
            '01': 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)

    def SetTunerBand(self, value, qualifier):

        TunerBandCmdString = '!1TUNBAND\r\n'
        self.__SetHelper('TunerBand', TunerBandCmdString, value, qualifier)

    def SetTunerFrequencyCommand(self, value, qualifier):

        if value and 1 <= len(str(value)) <= 5 and str(value).isnumeric():
            TunerFrequencyCommandCmdString = '!1TUN{:05d}\r\n'.format(int(value))
            self.__SetHelper('TunerFrequencyCommand', TunerFrequencyCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTunerFrequencyCommand')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '!1MVL{:02X}\r\n'.format(int(value * 2))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '!1MVLQSTN\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16) / 2
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZ{}\r\n'.format(self.set_zone_2_input_states[value])
        if value != 'USB Toggle':
            self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZQSTN\r\n'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = self.update_zone_2_input_states[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        Zone2MuteCmdString = '!1ZMT{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = '!1ZMTQSTN\r\n'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        Zone2PowerCmdString = '!1ZPW{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = '!1ZPWQSTN\r\n'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Preset(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 40:
            Zone2PresetCmdString = '!1PRZ{:02X}\r\n'.format(value)
            self.__SetHelper('Zone2Preset', Zone2PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Preset')

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = '!1ZVL{:02X}\r\n'.format(int(value * 2))
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = '!1ZVLQSTN\r\n'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode(), 16) / 2
        self.WriteStatus('Zone2Volume', value, None)

    def SetZone3Input(self, value, qualifier):

        Zone3InputCmdString = '!1SL3{}\r\n'.format(self.set_zone_3_input_states[value])
        if value != 'USB Toggle':
            self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = '!1SL3QSTN\r\n'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):

        value = self.update_zone_3_input_states[match.group(1).decode()]
        self.WriteStatus('Zone3Input', value, None)

    def SetZone3Mute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        Zone3MuteCmdString = '!1MT3{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = '!1MT3QSTN\r\n'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def __MatchZone3Mute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Mute', value, None)

    def SetZone3Power(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        Zone3PowerCmdString = '!1PW3{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = '!1PW3QSTN\r\n'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Power', value, None)

    def SetZone3Preset(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 40:
            Zone3PresetCmdString = '!1PR3{:02X}\r\n'.format(value)
            self.__SetHelper('Zone3Preset', Zone3PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Preset')
    def SetZone3Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone3VolumeCmdString = '!1VL3{:02X}\r\n'.format(int(value * 2))
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = '!1VL3QSTN\r\n'
        self.__UpdateHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        value = int(match.group(1).decode(), 16) / 2
        self.WriteStatus('Zone3Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pion_27_3276_LX102(self):

        del self.set_input_states['HDMI 5']
        del self.set_input_states['HDMI 6']
        del self.update_input_states['55']
        del self.update_input_states['56']

        del self.set_listening_mode_states['Whole House Mode']
        del self.set_listening_mode_states['Neo:6 Music/Neo:X Music']
        del self.update_listening_mode_states['1F']
        del self.update_listening_mode_states['83']

        self.set_zone_2_input_states = {}
        self.update_zone_2_input_states = {}

        self.set_zone_3_input_states = {}
        self.update_zone_3_input_states = {}

    def pion_27_3276_LX103(self):

        del self.set_listening_mode_states['Whole House Mode']
        del self.set_listening_mode_states['Neo:6 Music/Neo:X Music']
        del self.update_listening_mode_states['1F']
        del self.update_listening_mode_states['83']

        self.set_zone_3_input_states = {}
        self.update_zone_3_input_states = {}

    def pion_27_3276_LX301(self):

        del self.set_input_states['USB Back']
        del self.update_input_states['2A']

        del self.set_listening_mode_states['Whole House Mode']
        del self.update_listening_mode_states['1F']

        del self.set_zone_2_input_states['USB Back']
        del self.set_zone_2_input_states['Source']
        del self.update_zone_2_input_states['2A']
        del self.update_zone_2_input_states['80']

        self.set_zone_3_input_states = {}
        self.update_zone_3_input_states = {}

    def pion_27_3276_LX302(self):

        del self.set_listening_mode_states['Whole House Mode']
        del self.set_listening_mode_states['Neo:6 Music/Neo:X Music']
        del self.update_listening_mode_states['1F']
        del self.update_listening_mode_states['83']

        del self.set_zone_2_input_states['Source']
        del self.update_zone_2_input_states['80']

        self.set_zone_3_input_states = {}
        self.update_zone_3_input_states = {}

    def pion_27_3276_LX303(self):

        del self.set_listening_mode_states['Whole House Mode']
        del self.set_listening_mode_states['Neo:6 Music/Neo:X Music']
        del self.update_listening_mode_states['1F']
        del self.update_listening_mode_states['83']

    def pion_27_3276_LX503(self):

        del self.set_listening_mode_states['Neo:6 Music/Neo:X Music']
        del self.update_listening_mode_states['83']

        del self.set_zone_2_input_states['Aux']
        del self.update_zone_2_input_states['03']

        del self.set_zone_3_input_states['Aux']
        del self.update_zone_3_input_states['03']

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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