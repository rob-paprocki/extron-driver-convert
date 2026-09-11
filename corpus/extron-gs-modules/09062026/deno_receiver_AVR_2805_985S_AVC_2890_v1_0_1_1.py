from extronlib.interface import EthernetClientInterface, SerialInterface
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

        self.Models = {
            'AVC2890': self.deno_27_1492_AVC2890,
            'AVR-2805': self.deno_27_1492_AVR_2805,
            'AVR-985S': self.deno_27_1492_AVR_2805,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AMFrequency': {'Status': {}},
            'ChannelVolume': {'Parameters':['Mode'], 'Status': {}},
            'CinemaEqualizer': {'Status': {}},
            'DigitalInput': {'Status': {}},
            'FMFrequency': {'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RecordInput': {'Status': {}},
            'RoomEqualizer': {'Status': {}},
            'SubwooferOff': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'ToneDefeat': {'Status': {}},
            'TunerBand': {'Status': {}},
            'TunerPresetChannel': {'Status': {}},
            'VideoInput': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone1Input': {'Status': {}},
            'Zone1Power': {'Status': {}},
            'Zone1Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'TF([0-9]{1,6})\r'), self.__MatchFrequency, None)
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR|SB)[ ]?([0-9]{2,3})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'SI(PHONO|CD|TUNER|DVD|VDP|TV|DBS/SAT|VCR-1|VCR-2|VCR-3|V\.AUX|CDR/TAPE1|MD/TAPE2)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'MU(ON|OFF)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SR(PHONO|CD|TUNER|DVD|VDP|TV|DBS/SAT|VCR-1|VCR-2|VCR-3|V\.AUX|CDR/TAPE1|MD/TAPE2|SOURCE)\r'), self.__MatchRecordInput, None)
            self.AddMatchString(re.compile(b'PSROOM EQ:(NORMAL|FRONT|FLAT|MANUAL|OFF)\r'), self.__MatchRoomEqualizer, None)
            self.AddMatchString(re.compile(b'MS(DIRECT|PURE DIRECT|STEREO|DTS SURROUND|DTS ES DSCRT6\.1|DTS ES MTRX6\.1|DOLBY H/P|DTS\+DOLBY H/P|'
                                           b'HOME THX CINEMA|THX5\.1|THX U2 CINEMA|THX MUSIC MODE|THX6\.1|THX SURROUND EX|WIDE SCREEN|5CH STEREO|'
                                           b'7CH STEREO|SUPER STADIUM|ROCK ARENA|JAZZ CLUB|CLASSIC CONCERT|MONO MOVIE|MATRIX|VIDEO GAME|VIRTUAL|'
                                           b'MPEG2 AAC|MULTI CH IN|M CH IN\+PL2X C|M CH IN\+PL2X M|MULTI CH DIRECT|M CH DRCT\+PL2X C|M CH DRCT\+PL2X M|'
                                           b'MULTI CH PURE D|M CH PURE D\+PL2X C|M CH PURE D\+PL2X M|DOLBY PRO LOGIC|DOLBY PL2|DOLBY PL2 C|DOLBY PL2 M|'
                                           b'DOLBY PL2 G|DOLBY PL2X|DOLBY PL2X C|DOLBY PL2X M|DOLBY PL2X G|DOLBY DIGITAL|DOLBY D EX|DOLBY D\+PL2X C|'
                                           b'DOLBY D\+PL2X M|DTS NEO:6|DTS NEO:6 C|DTS NEO:6 M|DTS\+PL2X C|DTS\+PL2X M|AAC\+DOLBY EX|AAC\+PL2X C|'
                                           b'AAC\+PL2X M|)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'TM(AM|FM|AUTO|MANUAL)\r'), self.__MatchTunerBand, None)
            self.AddMatchString(re.compile(b'TP([0-9]{1})\r'), self.__MatchTunerPresetChannel, None)
            self.AddMatchString(re.compile(b'MV([0-9]{1,3})\r'),  self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Z1(PHONO|CD|TUNER|DVD|VDP|TV|DBS/SAT|VCR-1|VCR-2|VCR-3|V.AUX|CDR/TAPE1|MD/TAPE2|SOURCE)\r'), self.__MatchZone1Input, None)
            self.AddMatchString(re.compile(b'Z1(ON|OFF)\r'), self.__MatchZone1Power, None)
            self.AddMatchString(re.compile(b'Z1([0-9]{1,2})\r'), self.__MatchZone1Volume, None)
            self.AddMatchString(re.compile(b'Z2(PHONO|CD|TUNER|DVD|VDP|TV|DBS/SAT|VCR-1|VCR-2|VCR-3|V.AUX|CDR/TAPE1|MD/TAPE2|SOURCE)\r'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{1,2})\r'), self.__MatchZone2Volume, None)

    def SetAMFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min' : 526.50,
            'Max' : 1705.00
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AMFrequencyCmdString = 'TF{0:06}\r'.format(int(value * 100))
            self.__SetHelper('AMFrequency', AMFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAMFrequency')

    def UpdateAMFrequency(self, value, qualifier):

        AMFrequencyCmdString = 'TF?\r'
        self.__UpdateHelper('AMFrequency', AMFrequencyCmdString, value, qualifier)

    def __MatchFrequency(self, match, tag):

        AMConstraints = {
            'Min' : 526.50,
            'Max' : 1705.00
        }
        FMConstraints = {
            'Min' : 76.00,
            'Max' : 108.00
        }

        value = int(match.group(1).decode()) / 100
        if AMConstraints['Min'] <= value <= AMConstraints['Max']:
            self.WriteStatus('AMFrequency', value, None)
        elif FMConstraints['Min'] <= value <= FMConstraints['Max']:
            self.WriteStatus('FMFrequency', value, None)

    def SetChannelVolume(self, value, qualifier):

        ModeStates = {
            'Front Left' :          'CVFL', 
            'Front Right' :         'CVFR', 
            'Center' :              'CVC', 
            'Subwoofer' :           'CVSW', 
            'Surround Left' :       'CVSL', 
            'Surround Right' :      'CVSR', 
            'Surround Back Left' :  'CVSBL', 
            'Surround Back Right' : 'CVSBR', 
            'Surround Back' :       'CVSB'
        }
        ValueConstraints = {
            'Min' : -12.0,
            'Max' : 12.0
            }

        Mode = qualifier['Mode']
        if Mode in ModeStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Volume = value + 50
            if Volume % 1 == 0.5:
                ChannelVolumeCmdString = '{0} {1:03}\r'.format(ModeStates[Mode],int(Volume * 10))
            else:
                ChannelVolumeCmdString = '{0} {1:02}\r'.format(ModeStates[Mode],int(Volume))
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):

        ChannelVolumeCmdString = 'CV?\r'
        self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)

    def __MatchChannelVolume(self, match, tag):

        ModeStates = {
            'FL':  'Front Left',
            'FR':  'Front Right',
            'C' :  'Center',
            'SW':  'Subwoofer',
            'SL':  'Surround Left',
            'SR':  'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB':  'Surround Back'
        }

        qualifier = {'Mode': ModeStates[match.group(1).decode()]}
        value = match.group(2).decode()
        if value == '00':
            value = -12.0
        elif value[-1] == '5':
            value = float(value) / 10 - 50
        else:
            value = float(value) - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetCinemaEqualizer(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PSCINEMA EQ.ON\r',
            'Off' : 'PSCINEMA EQ.OFF\r'
        }

        if value in ValueStateValues:
            CinemaEqualizerCmdString = ValueStateValues[value]
            self.__SetHelper('CinemaEqualizer', CinemaEqualizerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCinemaEqualizer')



    def SetDigitalInput(self, value, qualifier):

        if value in self.DigitalInputs:
            DigitalInputCmdString = self.DigitalInputs[value]
            self.__SetHelper('DigitalInput', DigitalInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDigitalInput')



    def SetFMFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min' : 76.00,
            'Max' : 108.00
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FMFrequencyCmdString = 'TF{0:06}\r'.format(int(value * 100))
            self.__SetHelper('FMFrequency', FMFrequencyCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFMFrequency')

    def UpdateFMFrequency(self, value, qualifier):

        FMFrequencyCmdString = 'TF?\r?'
        self.__UpdateHelper('FMFrequency', FMFrequencyCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        if value in self.InputNames:
            InputCmdString = self.InputNames[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZonePower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ZMON\r',
            'Off' : 'ZMOFF\r'
        }

        MainZonePowerCmdString = ValueStateValues[value]
        self.__SetHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def UpdateMainZonePower(self, value, qualifier):

        MainZonePowerCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def __MatchMainZonePower(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZonePower', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUON\r',
            'Off' : 'MUOFF\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'MU?\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : 'PWON\r',
            'Off' : 'PWSTANDBY\r'
        }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateValues = {
            'ON'      : 'On',
            'STANDBY' : 'Off'
        }

        value = PowerStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRecordInput(self, value, qualifier):

        if value in self.RecordInputNames:
            RecordInputCmdString = self.RecordInputNames[value]
            self.__SetHelper('RecordInput', RecordInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecordInput')

    def UpdateRecordInput(self, value, qualifier):

        RecordInputCmdString = 'SR?\r'
        self.__UpdateHelper('RecordInput', RecordInputCmdString, value, qualifier)

    def __MatchRecordInput(self, match, tag):

        value = self.RecordInputValues[match.group(1).decode()]
        self.WriteStatus('RecordInput', value, None)

    def SetRoomEqualizer(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 'PSROOM EQ:NORMAL\r', 
            'Front' :  'PSROOM EQ:FRONT\r', 
            'Flat' :   'PSROOM EQ:FLAT\r', 
            'Manual' : 'PSROOM EQ:MANUAL\r', 
            'Off' :    'PSROOM EQ:OFF\r'
        }

        if value in ValueStateValues:
            RoomEqualizerCmdString = ValueStateValues[value]
            self.__SetHelper('RoomEqualizer', RoomEqualizerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRoomEqualizer')

    def UpdateRoomEqualizer(self, value, qualifier):

        RoomEqualizerCmdString = 'PS?\r'
        self.__UpdateHelper('RoomEqualizer', RoomEqualizerCmdString, value, qualifier)

    def __MatchRoomEqualizer(self, match, tag):

        ValueStateValues = {
            'NORMAL' : 'Normal', 
            'FRONT' :  'Front', 
            'FLAT' :   'Flat', 
            'MANUAL' : 'Manual', 
            'OFF' :    'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RoomEqualizer', value, None)

    def SetSubwooferOff(self, value, qualifier):

        SubwooferOffCmdString = 'CVSW 00\r'
        self.__SetHelper('SubwooferOff', SubwooferOffCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        if value in self.SurroundModeNames:
            SurroundModeCmdString = self.SurroundModeNames[value]
            self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSurroundMode')
    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        value = self.SurroundModeValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetToneDefeat(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PSTONE DEFEAT ON\r',
            'Off' : 'PSTONE DEFEAT OFF\r'
        }

        if value in ValueStateValues:
            ToneDefeatCmdString = ValueStateValues[value]
            self.__SetHelper('ToneDefeat', ToneDefeatCmdString, value, qualifier)
        else:
            print('Invalid Command for SetToneDefeat')

    def SetTunerBand(self, value, qualifier):

        ValueStateValues = {
            'AM' :     'TMAM\r', 
            'FM' :     'TMFM\r', 
            'Auto' :   'TMAUTO\r', 
            'Manual' : 'TMMANUAL\r'
        }

        if value in ValueStateValues:
            TunerBandCmdString = ValueStateValues[value]
            self.__SetHelper('TunerBand', TunerBandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTunerBand')

    def UpdateTunerBand(self, value, qualifier):

        TunerBandCmdString = 'TM?\r'
        self.__UpdateHelper('TunerBand', TunerBandCmdString, value, qualifier)

    def __MatchTunerBand(self, match, tag):

        ValueStateValues = {
            'AM' :     'AM', 
            'FM' :     'FM', 
            'AUTO' :   'Auto', 
            'MANUAL' : 'Manual'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TunerBand', value, None)

    def SetTunerPresetChannel(self, value, qualifier):

        ValueStateValues = ('1','2','3','4','5','6','7','8','9')
        if value in ValueStateValues:
            TunerPresetChannelCmdString = 'TP' + value + '\r'
            self.__SetHelper('TunerPresetChannel', TunerPresetChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTunerPresetChannel')

    def UpdateTunerPresetChannel(self, value, qualifier):

        TunerPresetChannelCmdString = 'TP?\r'
        self.__UpdateHelper('TunerPresetChannel', TunerPresetChannelCmdString, value, qualifier)

    def __MatchTunerPresetChannel(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerPresetChannel', value, None)

    def SetVideoInput(self, value, qualifier):

        if value in self.VideoInputNames:
            VideoInputCmdString = self.VideoInputNames[value]
            self.__SetHelper('VideoInput', VideoInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVideoInput')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80.5,
            'Max' : 18.0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Volume = value + 80
            if value == -80.5:
                VolumeCmdString = 'MV99\r'
            elif Volume % 1 == 0.5:
                VolumeCmdString = 'MV{0:03}\r'.format(int(Volume * 10))
            else:
                VolumeCmdString = 'MV{0:02}\r'.format(int(Volume))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'MV?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1).decode()
        if value == '99':
            value = -80.5
        elif value[-1] == '5':
            value = float(value) / 10 - 80
        else:
            value = float(value) - 80
        self.WriteStatus('Volume', value, None)

    def SetZone1Input(self, value, qualifier):

        ValueStateValues = {
            'Phono' :     'Z1PHONO\r', 
            'CD' :        'Z1CD\r', 
            'Tuner' :     'Z1TUNER\r', 
            'DVD' :       'Z1DVD\r', 
            'VDP' :       'Z1VDP\r', 
            'TV' :        'Z1TV\r', 
            'DBS/SAT' :   'Z1DBS/SAT\r', 
            'VCR-1' :     'Z1VCR-1\r', 
            'VCR-2' :     'Z1VCR-2\r', 
            'VCR-3' :     'Z1VCR-3\r', 
            'V.AUX' :     'Z1V.AUX\r', 
            'CDR/TAPE1' : 'Z1CDR/TAPE1\r', 
            'MD/TAPE2' :  'Z1MD/TAPE2\r', 
            'Cancel' :    'Z1SOURCE\r'
        }
        if value in ValueStateValues:
            Zone1InputCmdString = ValueStateValues[value]
            self.__SetHelper('Zone1Input', Zone1InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone1Input')

    def UpdateZone1Input(self, value, qualifier):

        Zone1InputCmdString = 'Z1?\r'
        self.__UpdateHelper('Zone1Input', Zone1InputCmdString, value, qualifier)

    def __MatchZone1Input(self, match, tag):

        ValueStateValues = {
            'PHONO' :     'Phono', 
            'CD' :        'CD', 
            'TUNER' :     'Tuner', 
            'DVD' :       'DVD', 
            'VDP' :       'VDP', 
            'TV' :        'TV', 
            'DBS/SAT' :   'DBS/SAT', 
            'VCR-1' :     'VCR-1', 
            'VCR-2' :     'VCR-2', 
            'VCR-3' :     'VCR-3', 
            'V.AUX' :     'V.AUX', 
            'CDR/TAPE1' : 'CDR/TAPE1', 
            'MD/TAPE2' :  'MD/TAPE2', 
            'SOURCE' :    'Cancel'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone1Input', value, None)

    def SetZone1Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z1ON\r',
            'Off' : 'Z1OFF\r'
        }
        Zone1PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone1Power', Zone1PowerCmdString, value, qualifier)

    def UpdateZone1Power(self, value, qualifier):

        Zone1PowerCmdString = 'Z1\r'
        self.__UpdateHelper('Zone1Power', Zone1PowerCmdString, value, qualifier)

    def __MatchZone1Power(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone1Power', value, None)

    def SetZone1Volume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -71,
            'Max' : 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == -71:
                Zone1VolumeCmdString = 'Z199\r'
            else:
                Zone1VolumeCmdString = 'Z1{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone1Volume', Zone1VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone1Volume')

    def UpdateZone1Volume(self, value, qualifier):

        Zone1VolumeCmdString = 'Z1?\r'
        self.__UpdateHelper('Zone1Volume', Zone1VolumeCmdString, value, qualifier)

    def __MatchZone1Volume(self, match, tag):

        value = match.group(1).decode()
        if value == '99':
            value = -71
        else:
            value = int(value) - 80
        self.WriteStatus('Zone1Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        if value in self.Zone2InputNames:
            Zone2InputCmdString = self.Zone2InputNames[value]
            self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Input')

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = self.Zone2InputValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z2ON\r',
            'Off' : 'Z2OFF\r'
        }
        if value in ValueStateValues:
            Zone2PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Power')

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -71,
            'Max' : 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == -71:
                Zone2VolumeCmdString = 'Z299\r'
            else:
                Zone2VolumeCmdString = 'Z2{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = match.group(1).decode()
        if value == '99':
            value = -71
        else:
            value = int(value) - 80
        self.WriteStatus('Zone2Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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

    def deno_27_1492_AVC2890(self):

        self.DigitalInputs = {
            'Auto'     : 'SDAUTO\r',
            'PCM'      : 'SDPCM\r',
            'DTS'      : 'SDDTS\r',
            'RF'       : 'SDRF\r',
            'Analog'   : 'SDANALOG\r',
            'Ext.In-1' : 'SDEXT.IN-1\r',
            'Ext.In-2' : 'SDEXT.IN-2\r'
        }
        self.InputNames = {
            'Phono'     : 'SIPHONO\r',
            'CD'        : 'SICD\r',
            'Tuner'     : 'SITUNER\r',
            'DVD'       : 'SIDVD\r',
            'VDP'       : 'SIVDP\r',
            'TV'        : 'SITV\r',
            'DBS/SAT'   : 'SIDBS/SAT\r',
            'VCR-1'     : 'SIVCR-1\r',
            'VCR-2'     : 'SIVCR-2\r',
            'VCR-3'     : 'SIVCR-3\r',
            'V.AUX'     : 'SIV.AUX\r',
            'CDR/TAPE1' : 'SICDR/TAPE1\r',
            'MD/TAPE2'  : 'SIMD/TAPE2\r'
        }
        self.InputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS/SAT',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'VCR-3'     : 'VCR-3',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE1',
            'MD/TAPE2'  : 'MD/TAPE2'
        }
        self.RecordInputNames = {
            'Phono'     : 'SRPHONO\r',
            'CD'        : 'SRCD\r',
            'Tuner'     : 'SRTUNER\r',
            'DVD'       : 'SRDVD\r',
            'VDP'       : 'SRVDP\r',
            'TV'        : 'SRTV\r',
            'DBS/SAT'   : 'SRDBS/SAT\r',
            'VCR-1'     : 'SRVCR-1\r',
            'VCR-2'     : 'SRVCR-2\r',
            'VCR-3'     : 'SRVCR-3\r',
            'V.AUX'     : 'SRV.AUX\r',
            'CDR/TAPE1' : 'SRCDR/TAPE1\r',
            'MD/TAPE2'  : 'SRMD/TAPE2\r',
            'Cancel'    : 'SRSOURCE\r'
        }
        self.RecordInputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS/SAT',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'VCR-3'     : 'VCR-3',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE1',
            'MD/TAPE2'  : 'MD/TAPE2',
            'SOURCE'    : 'Cancel'
        }
        self.SurroundModeNames = {
            'Direct'               : 'MSDIRECT\r',
            'Pure Direct'          : 'MSPURE DIRECT\r',
            'Stereo'               : 'MSSTEREO\r',
            'DTS Surround'         : 'MSDTS SURROUND\r',
            'DTS ES DSCRT6.1'      : 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX6.1'       : 'MSDTS ES MTRX6.1\r',
            'Dolby H/P'            : 'MSDOLBY H/P\r',
            'DTS+Dolby H/P'        : 'MSDTS+DOLBY H/P\r',
            'Home THX Cinema'      : 'MSHOME THX CINEMA\r',
            'THX5.1'               : 'MSTHX5.1\r',
            'THX U2 Cinema'        : 'MSTHX U2 CINEMA\r',
            'THX Music Mode'       : 'MSTHX MUSIC MODE\r',
            'THX6.1'               : 'MSTHX6.1\r',
            'THX Surround EX'      : 'MSTHX SURROUND EX\r',
            'Wide Screen'          : 'MSWIDE SCREEN\r',
            '5CH Audio'            : 'MS5CH STEREO\r',
            '7CH Audio'            : 'MS7CH STEREO\r',
            'Super Stadium'        : 'MSSUPER STADIUM\r',
            'Rock Arena'           : 'MSROCK ARENA\r',
            'Jazz Club'            : 'MSJAZZ CLUB\r',
            'Classic Concert'      : 'MSCLASSIC CONCERT\r',
            'Mono Movie'           : 'MSMONO MOVIE\r',
            'Matrix'               : 'MSMATRIX\r',
            'Video Game'           : 'MSVIDEO GAME\r',
            'Virtual'              : 'MSVIRTUAL\r',
            'MPEG2 AAC'            : 'MSMPEG2 AAC\r',
            'Multi Channel In'     : 'MSMULTI CH IN\r',
            'Multi Channel Direct' : 'MSMULTI CH DIRECT\r',
            'Multi Channel Pure D' : 'MSMULTI CH PURE D\r',
            'Dolby Pro Logic'      : 'MSDOLBY PRO LOGIC\r',
            'Dolby PL2'            : 'MSDOLBY PL2\r',
            'Dolby PL2x'           : 'MSDOLBY PL2X\r',
            'Dolby Digital'        : 'MSDOLBY DIGITAL\r',
            'Dolby D EX'           : 'MSDOLBY D EX\r',
            'DTS Neo:6'            : 'MSDTS NEO:6\r',
            'AAC+Dolby EX'         : 'MSAAC+DOLBY EX\r',
        }
        self.SurroundModeValues = {
            'DIRECT'             : 'Direct',
            'PURE DIRECT'        : 'Pure Direct',
            'STEREO'             : 'Stereo',
            'DTS SURROUND'       : 'DTS Surround',
            'DTS ES DSCRT6.1'    : 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1'     : 'DTS ES MTRX6.1',
            'DOLBY H/P'          : 'Dolby H/P',
            'DTS+DOLBY H/P'      : 'DTS+Dolby H/P',
            'HOME THX CINEMA'    : 'Home THX Cinema',
            'THX5.1'             : 'THX5.1',
            'THX U2 CINEMA'      : 'THX U2 Cinema',
            'THX MUSIC MODE'     : 'THX Music Mode',
            'THX6.1'             : 'THX6.1',
            'THX SURROUND EX'    : 'THX Surround EX',
            'WIDE SCREEN'        : 'Wide Screen',
            '5CH STEREO'         : '5CH Audio',
            '7CH STEREO'         : '7CH Audio',
            'SUPER STADIUM'      : 'Super Stadium',
            'ROCK ARENA'         : 'Rock Arena',
            'JAZZ CLUB'          : 'Jazz Club',
            'CLASSIC CONCERT'    : 'Classic Concert',
            'MONO MOVIE'         : 'Mono Movie',
            'MATRIX'             : 'Matrix',
            'VIDEO GAME'         : 'Video Game',
            'VIRTUAL'            : 'Virtual',
            'MPEG2 AAC'          : 'MPEG2 AAC',
            'MULTI CH IN'        : 'Multi Channel In',
            'M CH IN+PL2X C'     : 'Multi Channel In+PL2x Cinema',
            'M CH IN+PL2X M'     : 'Multi Channel In+PL2x Music',
            'MULTI CH DIRECT'    : 'Multi Channel Direct',
            'M CH DRCT+PL2X C'   : 'Multi Channel Direct+PL2x Cinema',
            'M CH DRCT+PL2X M'   : 'Multi Channel Direct+PL2x Music',
            'MULTI CH PURE D'    : 'Multi Channel Pure D',
            'M CH PURE D+PL2X C' : 'Multi Channel Pure D+PL2x Cinema',
            'M CH PURE D+PL2X M' : 'Multi Channel Pure D+PL2x Music',
            'DOLBY PRO LOGIC'    : 'Dolby Pro Logic',
            'DOLBY PL2'          : 'Dolby PL2',
            'DOLBY PL2 C'        : 'Dolby PL2 Cinema',
            'DOLBY PL2 M'        : 'Dolby PL2 Music',
            'DOLBY PL2 G'        : 'Dolby PL2 Game',
            'DOLBY PL2X'         : 'Dolby PL2x',
            'DOLBY PL2X C'       : 'Dolby PL2x Cinema',
            'DOLBY PL2X M'       : 'Dolby PL2x Music',
            'DOLBY PL2X G'       : 'Dolby PL2x Game',
            'DOLBY DIGITAL'      : 'Dolby Digital',
            'DOLBY D EX'         : 'Dolby D EX',
            'DOLBY D+PL2X C'     : 'Dolby D+PL2x Cinema',
            'DOLBY D+PL2X M'     : 'Dolby D+PL2x Music',
            'DTS NEO:6'          : 'DTS Neo:6',
            'DTS NEO:6 C'        : 'DTS Neo:6 Cinema',
            'DTS NEO:6 M'        : 'DTS Neo:6 Music',
            'DTS+PL2X C'         : 'DTS+PL2x Cinema',
            'DTS+PL2X M'         : 'DTS+PL2x Music',
            'AAC+DOLBY EX'       : 'AAC+Dolby EX',
            'AAC+PL2X C'         : 'AAC+PL2x Cinema',
            'AAC+PL2X M'         : 'AAC+PL2x Music'
        }
        self.VideoInputNames = {
            'DVD'     : 'SVDVD\r',
            'VDP'     : 'SVVDP\r',
            'TV'      : 'SVTV\r',
            'DBS/SAT' : 'SVDBS/SAT\r',
            'VCR-1'   : 'SVVCR-1\r',
            'VCR-2'   : 'SVVCR-2\r',
            'VCR-3'   : 'SVVCR-3\r',
            'V.AUX'   : 'SVV.AUX\r',
            'Cancel'  : 'SVSOURCE\r'
        }
        self.Zone2InputNames = {
            'Phono'     : 'Z2PHONO\r',
            'CD'        : 'Z2CD\r',
            'Tuner'     : 'Z2TUNER\r',
            'DVD'       : 'Z2DVD\r',
            'VDP'       : 'Z2VDP\r',
            'TV'        : 'Z2TV\r',
            'DBS/SAT'   : 'Z2DBS/SAT\r',
            'VCR-1'     : 'Z2VCR-1\r',
            'VCR-2'     : 'Z2VCR-2\r',
            'VCR-3'     : 'Z2VCR-3\r',
            'V.AUX'     : 'Z2V.AUX\r',
            'CDR/TAPE1' : 'Z2CDR/TAPE1\r',
            'MD/TAPE2'  : 'Z2MD/TAPE2\r',
            'Cancel'    : 'SVSOURCE\r'
        }
        self.Zone2InputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS/SAT',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'VCR-3'     : 'VCR-3',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE1',
            'MD/TAPE2'  : 'MD/TAPE2',
            'SOURCE'    : 'Cancel'
        }

    def deno_27_1492_AVR_2805(self):

        self.DigitalInputs = {
            'Auto'   : 'SDAUTO\r',
            'PCM'    : 'SDPCM\r',
            'DTS'    : 'SDDTS\r',
            'Analog' : 'SDANALOG\r',
            'Ext.In' : 'SDEXT.IN-1\r'
        }
        self.InputNames = {
            'Phono'    : 'SIPHONO\r',
            'CD'       : 'SICD\r',
            'Tuner'    : 'SITUNER\r',
            'DVD'      : 'SIDVD\r',
            'VDP'      : 'SIVDP\r',
            'TV'       : 'SITV\r',
            'DBS'      : 'SIDBS/SAT\r',
            'VCR-1'    : 'SIVCR-1\r',
            'VCR-2'    : 'SIVCR-2\r',
            'V.AUX'    : 'SIV.AUX\r',
            'CDR/TAPE' : 'SICDR/TAPE1\r'
        }
        self.InputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE'
        }
        self.RecordInputNames = {
            'Phono'    : 'SRPHONO\r',
            'CD'       : 'SRCD\r',
            'Tuner'    : 'SRTUNER\r',
            'DVD'      : 'SRDVD\r',
            'VDP'      : 'SRVDP\r',
            'TV'       : 'SRTV\r',
            'DBS'      : 'SRDBS/SAT\r',
            'VCR-1'    : 'SRVCR-1\r',
            'VCR-2'    : 'SRVCR-2\r',
            'V.AUX'    : 'SRV.AUX\r',
            'CDR/TAPE' : 'SRCDR/TAPE1\r',
            'Cancel'   : 'SRSOURCE\r'
        }
        self.RecordInputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE',
            'SOURCE'    : 'Cancel'
        }
        self.SurroundModeNames = {
            'Direct'          : 'MSDIRECT\r',
            'Pure Direct'     : 'MSPURE DIRECT\r',
            'Stereo'          : 'MSSTEREO\r',
            'DTS Surround'    : 'MSDTS SURROUND\r',
            'DTS ES DSCRT6.1' : 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX6.1'  : 'MSDTS ES MTRX6.1\r',
            'Wide Screen'     : 'MSWIDE SCREEN\r',
            '5CH Audio'       : 'MS5CH STEREO\r',
            '7CH Audio'       : 'MS7CH STEREO\r',
            'Super Stadium'   : 'MSSUPER STADIUM\r',
            'Rock Arena'      : 'MSROCK ARENA\r',
            'Jazz Club'       : 'MSJAZZ CLUB\r',
            'Classic Concert' : 'MSCLASSIC CONCERT\r',
            'Mono Movie'      : 'MSMONO MOVIE\r',
            'Matrix'          : 'MSMATRIX\r',
            'Video Game'      : 'MSVIDEO GAME\r',
            'Virtual'         : 'MSVIRTUAL\r',
            'Dolby Pro Logic' : 'MSDOLBY PRO LOGIC\r',
            'Dolby PL2'       : 'MSDOLBY PL2\r',
            'Dolby PL2x'      : 'MSDOLBY PL2X\r',
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r',
            'Dolby D EX'      : 'MSDOLBY D EX\r',
            'DTS Neo:6'       : 'MSDTS NEO:6\r',
        }
        self.SurroundModeValues = {
            'DIRECT'          : 'Direct',
            'PURE DIRECT'     : 'Pure Direct',
            'STEREO'          : 'Stereo',
            'DTS SURROUND'    : 'DTS Surround',
            'DTS ES DSCRT6.1' : 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1'  : 'DTS ES MTRX6.1',
            'WIDE SCREEN'     : 'Wide Screen',
            '5CH STEREO'      : '5CH Audio',
            '7CH STEREO'      : '7CH Audio',
            'SUPER STADIUM'   : 'Super Stadium',
            'ROCK ARENA'      : 'Rock Arena',
            'JAZZ CLUB'       : 'Jazz Club',
            'CLASSIC CONCERT' : 'Classic Concert',
            'MONO MOVIE'      : 'Mono Movie',
            'MATRIX'          : 'Matrix',
            'VIDEO GAME'      : 'Video Game',
            'VIRTUAL'         : 'Virtual',
            'DOLBY PRO LOGIC' : 'Dolby Pro Logic',
            'DOLBY PL2'       : 'Dolby PL2',
            'DOLBY PL2 C'     : 'Dolby PL2 Cinema',
            'DOLBY PL2 M'     : 'Dolby PL2 Music',
            'DOLBY PL2 G'     : 'Dolby PL2 Game',
            'DOLBY PL2X'      : 'Dolby PL2x',
            'DOLBY PL2X C'    : 'Dolby PL2x Cinema',
            'DOLBY PL2X M'    : 'Dolby PL2x Music',
            'DOLBY PL2X G'    : 'Dolby PL2x Game',
            'DOLBY DIGITAL'   : 'Dolby Digital',
            'DOLBY D EX'      : 'Dolby D EX',
            'DOLBY D+PL2X C'  : 'Dolby D+PL2x Cinema',
            'DOLBY D+PL2X M'  : 'Dolby D+PL2x Music',
            'DTS NEO:6'       : 'DTS Neo:6',
            'DTS NEO:6 C'     : 'DTS Neo:6 Cinema',
            'DTS NEO:6 M'     : 'DTS Neo:6 Music',
            'DTS+PL2X C'      : 'DTS+PL2x Cinema',
            'DTS+PL2X M'      : 'DTS+PL2x Music'
        }
        self.VideoInputNames = {
            'DVD'    : 'SVDVD\r',
            'VDP'    : 'SVVDP\r',
            'TV'     : 'SVTV\r',
            'DBS'    : 'SVDBS/SAT\r',
            'VCR-1'  : 'SVVCR-1\r',
            'VCR-2'  : 'SVVCR-2\r',
            'V.AUX'  : 'SVV.AUX\r',
            'Cancel' : 'SVSOURCE\r'
        }
        self.Zone2InputNames = {
            'Phono'    : 'Z2PHONO\r',
            'CD'       : 'Z2CD\r',
            'Tuner'    : 'Z2TUNER\r',
            'DVD'      : 'Z2DVD\r',
            'VDP'      : 'Z2VDP\r',
            'TV'       : 'Z2TV\r',
            'DBS'      : 'Z2DBS/SAT\r',
            'VCR-1'    : 'Z2VCR-1\r',
            'VCR-2'    : 'Z2VCR-2\r',
            'V.AUX'    : 'Z2V.AUX\r',
            'CDR/TAPE' : 'Z2CDR/TAPE1\r',
            'Cancel'   : 'Z2SOURCE\r'
        }
        self.Zone2InputValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'TUNER'     : 'Tuner',
            'DVD'       : 'DVD',
            'VDP'       : 'VDP',
            'TV'        : 'TV',
            'DBS/SAT'   : 'DBS',
            'VCR-1'     : 'VCR-1',
            'VCR-2'     : 'VCR-2',
            'V.AUX'     : 'V.AUX',
            'CDR/TAPE1' : 'CDR/TAPE',
            'SOURCE'    : 'Cancel'
        }

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

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

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