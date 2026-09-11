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

        self.Models = {
            'AVR-3805': self.deno_27_3444_AVR,
            'AVC-3890': self.deno_27_3444_AVC,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelVolume': {'Parameters': ['Channel'], 'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'OutputMute': {'Status': {}},
            'Power': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3AudioMute': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR|SB) ([0-9]{1,3})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'SI(PHONO|CD|TUNER|DVD|VDP|TV|DBS/SAT|VCR-1|VCR-2|VCR-3|V.AUX|CDR/TAPE1|MD/TAPE2)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'MV([0-9]{1,3})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'(|Z1|Z2)MU(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MS(DIRECT|PURE DIRECT|STEREO|DTS SURROUND|DTS ES DSCRT6\.1|DTS ES MTRX6\.1|DOLBY H/P|DTS\+DOLBY H/P|'
                                           b'HOME THX CINEMA|THX5\.1|THX U2 CINEMA|THX MUSIC MODE|THX6\.1|THX SURROUND EX|WIDE SCREEN|5CH STEREO|'
                                           b'7CH STEREO|SUPER STADIUM|ROCK ARENA|JAZZ CLUB|CLASSIC CONCERT|MONO MOVIE|MATRIX|VIDEO GAME|VIRTUAL|'
                                           b'MPEG2 AAC|MULTI CH IN|M CH IN\+PL2X C|M CH IN\+PL2X M|MULTI CH DIRECT|M CH DRCT\+PL2X C|M CH DRCT\+PL2X M|'
                                           b'MULTI CH PURE D|M CH PURE D\+PL2X C|M CH PURE D\+PL2X M|DOLBY PRO LOGIC|DOLBY PL2 C|DOLBY PL2 M|'
                                           b'DOLBY PL2 G|DOLBY PL2X C|DOLBY PL2X M|DOLBY PL2X G|DOLBY DIGITAL|DOLBY D EX|DOLBY D\+PL2X C|'
                                           b'DOLBY D\+PL2X M|DTS NEO:6 C|DTS NEO:6 M|DTS\+PL2X C|DTS\+PL2X M|AAC\+DOLBY EX|AAC\+PL2X C|'
                                           b'AAC\+PL2X M|)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z2(PHONO|CD|TUNER|DVD|VDP|TV|DBS|VCR-1|VCR-2|V.AUX|CDR/TAPE1)\r'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{2})\r'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'Z1(ON|OFF)\r'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'Z1(PHONO|CD|TUNER|DVD|VDP|TV|DBS|VCR-1|VCR-2|V.AUX|CDR/TAPE1)\r'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'Z1([0-9]{2})\r'), self.__MatchZone3Volume, None)

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'CVFL',
            'Front Right': 'CVFR',
            'Center': 'CVC',
            'Subwoofer': 'CVSW',
            'Surround Left': 'CVSL',
            'Surround Right': 'CVSR',
            'Surround Back Left': 'CVSBL',
            'Surround Back Right': 'CVSBR',
            'Surround Back': 'CVSB'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:

            if (value * 10) % 10 == 5:
                ChannelVolumeCmdString = '{0}{1:03.0f}\r'.format(ChannelStates[qualifier['Channel']], (value + 50) * 10)
            else:
                ChannelVolumeCmdString = '{0}{1:02.0f}\r'.format(ChannelStates[qualifier['Channel']], value + 50)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):

        ChannelVolumeCmdString = 'CV?\r'
        self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)

    def __MatchChannelVolume(self, match, tag):

        ChannelStates = {
             'FL': 'Front Left',
             'FR': 'Front Right',
             'C': 'Center',
             'SW': 'Subwoofer',
             'SL': 'Surround Left',
             'SR': 'Surround Right',
             'SBL': 'Surround Back Left',
             'SBR': 'Surround Back Right',
             'SB': 'Surround Back'
        }

        ChannelQual = ChannelStates[match.group(1).decode()]
        qualifier = {'Channel': ChannelQual}
        value = match.group(2).decode()

        if value == '00':
            value = -12.0
        elif value[-1] == '5':
            value = float(value) / 10 - 50
        else:
            value = float(value) - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZonePower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r'
        }

        MainZonePowerCmdString = ValueStateValues[value]
        self.__SetHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def UpdateMainZonePower(self, value, qualifier):

        MainZonePowerCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def __MatchMainZonePower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZonePower', value, None)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:

            if (value * 10) % 10 == 5:
                MasterVolumeCmdString = 'MV{0:03.0f}\r'.format((value + 80) * 10)
            else:
                MasterVolumeCmdString = 'MV{0:02.0f}\r'.format(value + 80)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = match.group(1).decode()

        if len(value) == 3:
            value = round((float(value) / 10) - 80, 1)
        else:
            value = int(value) - 80
        self.WriteStatus('MasterVolume', value, None)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUON\r',
            'Off': 'MUOFF\r'
        }

        OutputMuteCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'MU?\r'
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        zone = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]

        if zone == 'Z2':
            self.WriteStatus('Zone2AudioMute', value, None)
        elif zone == 'Z1':
            self.WriteStatus('Zone3AudioMute', value, None)
        else:
            self.WriteStatus('OutputMute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PWON\r',
            'Off': 'PWSTANDBY\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'STANDBY': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSurroundMode(self, value, qualifier):

        SurroundModeCmdString = self.SurroundModeStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        value = self.SurroundModeStateNames[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2ON\r',
            'Off': 'Z2OFF\r'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2MUON\r',
            'Off': 'Z2MUOFF\r'
        }

        Zone2AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def UpdateZone2AudioMute(self, value, qualifier):

        Zone2AudioMuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z2CD\r',
            'Tuner': 'Z2TUNER\r',
            'DVD': 'Z2DVD\r',
            'VDP': 'Z2VDP\r',
            'TV': 'Z2TV\r',
            'DBS': 'Z2DBS\r',
            'VCR 1': 'Z2VCR-1\r',
            'VCR 2': 'Z2VCR-2\r',
            'V Aux': 'Z2V.AUX\r',
            'CDR/Tape': 'Z2CDR/TAPE1\r',
            'Phono': 'Z2PHONO\r'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'VDP': 'VDP',
            'TV': 'TV',
            'DBS': 'DBS',
            'VCR-1': 'VCR 1',
            'VCR-2': 'VCR 2',
            'V.AUX': 'V Aux',
            'CDR/TAPE1': 'CDR/Tape',
            'PHONO': 'Phono'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            valuex = value + 80
            Zone2VolumeCmdString = 'Z2{0:02}\r'.format(valuex)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
        self.WriteStatus('Zone2Volume', value, None)

    def SetZone3Power(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z1ON\r',
            'Off': 'Z1OFF\r'
        }

        Zone3PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = 'Z1?\r'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Power', value, None)

    def SetZone3AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z1MUON\r',
            'Off': 'Z1MUOFF\r'
        }

        Zone3AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)

    def UpdateZone3AudioMute(self, value, qualifier):

        Zone3AudioMuteCmdString = 'Z1MU?\r'
        self.__UpdateHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)

    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z1CD\r',
            'Tuner': 'Z1TUNER\r',
            'DVD': 'Z1DVD\r',
            'VDP': 'Z1VDP\r',
            'TV': 'Z1TV\r',
            'DBS': 'Z1DBS\r',
            'VCR 1': 'Z1VCR-1\r',
            'VCR 2': 'Z1VCR-2\r',
            'V Aux': 'Z1V.AUX\r',
            'CDR/Tape': 'Z1CDR/TAPE1\r',
            'Phono': 'Z1PHONO\r'
        }

        Zone3InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = 'Z1?\r'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'VDP': 'VDP',
            'TV': 'TV',
            'DBS': 'DBS',
            'VCR-1': 'VCR 1',
            'VCR-2': 'VCR 2',
            'V.AUX': 'V Aux',
            'CDR/TAPE1': 'CDR/Tape',
            'PHONO': 'Phono'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Input', value, None)

    def SetZone3Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            valuex = value + 80
            Zone3VolumeCmdString = 'Z1{0:02}\r'.format(valuex)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = 'Z1?\r'
        self.__UpdateHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
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

    def deno_27_3444_AVR(self):

        self.InputStateValues = {
            'CD'       : 'SICD\r', 
            'Tuner'    : 'SITUNER\r', 
            'DVD'      : 'SIDVD\r', 
            'VDP'      : 'SIVDP\r', 
            'TV'       : 'SITV\r', 
            'DBS'      : 'SIDBS/SAT\r', 
            'VCR 1'    : 'SIVCR-1\r', 
            'VCR 2'    : 'SIVCR-2\r', 
            'V Aux'    : 'SIV.AUX\r', 
            'CDR/Tape' : 'SICDR/TAPE1\r',
            'Phono'    : 'SIPHONO\r'
        }

        self.InputStateNames = {
            'CD'       : 'CD', 
            'TUNER'    : 'Tuner', 
            'DVD'      : 'DVD', 
            'VDP'      : 'VDP', 
            'TV'       : 'TV', 
            'DBS/SAT'  : 'DBS', 
            'VCR-1'    : 'VCR 1', 
            'VCR-2'    : 'VCR 2', 
            'V.AUX'    : 'V Aux', 
            'CDR/TAPE1' : 'CDR/Tape',
            'PHONO'    : 'Phono'
        }   

        self.SurroundModeStateValues = {
            'Direct'               : 'MSDIRECT\r',
            'Pure Direct'          : 'MSPURE DIRECT\r',
            'Stereo'               : 'MSSTEREO\r',
            'Multi Channel In'     : 'MSMULTI CH IN\r',
            'Multi Channel Direct' : 'MSMULTI CH DIRECT\r', 
            'Multi Channel Pure D' : 'MSMULTI CH PURE D\r', 
            'Dolby Pro Logic'      : 'MSDOLBY PRO LOGIC\r',
            'Dolby PL2'            : 'MSDOLBY PL2\r',
            'Dolby PL2x'           : 'MSDOLBY PL2X\r',
            'Dolby Digital'        : 'MSDOLBY DIGITAL\r',
            'Dolby D EX'           : 'MSDOLBY D EX\r',
            'DTS Neo:6'            : 'MSDTS NEO:6\r',
            'DTS Surround'         : 'MSDTS SURROUND\r',
            'DTS ES DSCRT6.1'      : 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX6.1'       : 'MSDTS ES MTRX6.1\r',            
            'Wide Screen'          : 'MSWIDE SCREEN\r',
            '5CH Stereo'            : 'MS5CH STEREO\r',
            '7CH Stereo'            : 'MS7CH STEREO\r',
            'Super Stadium'        : 'MSSUPER STADIUM\r',
            'Rock Arena'           : 'MSROCK ARENA\r',
            'Jazz Club'            : 'MSJAZZ CLUB\r',
            'Classic Concert'      : 'MSCLASSIC CONCERT\r',
            'Mono Movie'           : 'MSMONO MOVIE\r',
            'Matrix'               : 'MSMATRIX\r',
            'Video Game'           : 'MSVIDEO GAME\r',
            'Virtual'              : 'MSVIRTUAL\r'        
        }

        self.SurroundModeStateNames = {
            'DIRECT'             : 'Direct',
            'PURE DIRECT'        : 'Pure Direct',
            'STEREO'             : 'Stereo',
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
            'DOLBY PL2 C'        : 'Dolby PL2 Cinema',
            'DOLBY PL2 M'        : 'Dolby PL2 Music',
            'DOLBY PL2 G'        : 'Dolby PL2 Game',
            'DOLBY PL2X C'       : 'Dolby PL2x Cinema',
            'DOLBY PL2X M'       : 'Dolby PL2x Music',
            'DOLBY PL2X G'       : 'Dolby PL2x Game',
            'DOLBY DIGITAL'      : 'Dolby Digital',
            'DOLBY D EX'         : 'Dolby D EX',
            'DOLBY D+PL2X C'     : 'Dolby D+PL2x Cinema',
            'DOLBY D+PL2X M'     : 'Dolby D+PL2x Music',
            'DTS NEO:6 C'        : 'DTS Neo:6 Cinema',
            'DTS NEO:6 M'        : 'DTS Neo:6 Music',
            'DTS+PL2X C'         : 'DTS+PL2x Cinema',
            'DTS+PL2X M'         : 'DTS+PL2x Music',
            'DTS SURROUND'       : 'DTS Surround',
            'DTS ES DSCRT6.1'    : 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1'     : 'DTS ES MTRX6.1',
            'WIDE SCREEN'        : 'Wide Screen',
            '5CH STEREO'         : '5CH Stereo',
            '7CH STEREO'         : '7CH Stereo',
            'SUPER STADIUM'      : 'Super Stadium',
            'ROCK ARENA'         : 'Rock Arena',
            'JAZZ CLUB'          : 'Jazz Club',
            'CLASSIC CONCERT'    : 'Classic Concert',
            'MONO MOVIE'         : 'Mono Movie',
            'MATRIX'             : 'Matrix',
            'VIDEO GAME'         : 'Video Game',
            'VIRTUAL'            : 'Virtual'
        }        

    def deno_27_3444_AVC(self):

        self.InputStateValues = {
            'CD'         : 'SICD\r', 
            'Tuner'      : 'SITUNER\r', 
            'DVD'        : 'SIDVD\r', 
            'VDP'        : 'SIVDP\r', 
            'TV'         : 'SITV\r', 
            'DBS/SAT'    : 'SIDBS/SAT\r', 
            'VCR 1'      : 'SIVCR-1\r', 
            'VCR 2'      : 'SIVCR-2\r', 
            'VCR 3'      : 'SIVCR-3\r', 
            'V Aux'      : 'SIV.AUX\r', 
            'CDR/Tape 1' : 'SICDR/TAPE1\r',
            'MD/Tape 2'  : 'SIMD/TAPE2\r',
            'Phono'      : 'SIPHONO\r'
        }

        self.InputStateNames = {
            'CD'       : 'CD', 
            'TUNER'    : 'Tuner', 
            'DVD'      : 'DVD', 
            'VDP'      : 'VDP', 
            'TV'       : 'TV', 
            'DBS/SAT'  : 'DBS/SAT', 
            'VCR-1'    : 'VCR 1', 
            'VCR-2'    : 'VCR 2', 
            'VCR-3'    : 'VCR 3', 
            'V.AUX'    : 'V Aux', 
            'CDR/TAPE1' : 'CDR/Tape 1',
            'MD/TAPE2'  : 'MD/Tape 2',
            'PHONO'    : 'Phono'
        }   

        self.SurroundModeStateValues = {
            'Direct'               : 'MSDIRECT\r',
            'Pure Direct'          : 'MSPURE DIRECT\r',
            'Stereo'               : 'MSSTEREO\r',
            'Multi Channel In'     : 'MSMULTI CH IN\r',
            'Multi Channel Direct' : 'MSMULTI CH DIRECT\r', 
            'Multi Channel Pure D' : 'MSMULTI CH PURE D\r', 
            'Dolby Pro Logic'      : 'MSDOLBY PRO LOGIC\r',
            'Dolby PL2'            : 'MSDOLBY PL2\r',
            'Dolby PL2x'           : 'MSDOLBY PL2X\r',
            'Dolby Digital'        : 'MSDOLBY DIGITAL\r',
            'Dolby D EX'           : 'MSDOLBY D EX\r',
            'DTS Neo:6'            : 'MSDTS NEO:6\r',
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
            '5CH Stereo'            : 'MS5CH STEREO\r',
            '7CH Stereo'            : 'MS7CH STEREO\r',
            'Super Stadium'        : 'MSSUPER STADIUM\r',
            'Rock Arena'           : 'MSROCK ARENA\r',
            'Jazz Club'            : 'MSJAZZ CLUB\r',
            'Classic Concert'      : 'MSCLASSIC CONCERT\r',
            'Mono Movie'           : 'MSMONO MOVIE\r',
            'Matrix'               : 'MSMATRIX\r',
            'Video Game'           : 'MSVIDEO GAME\r',
            'Virtual'              : 'MSVIRTUAL\r',
            'MPEG2 AAC'            : 'MSMPEG2 AAC\r',
            'AAC+Dolby EX'         : 'MSAAC+DOLBY EX\r',
        }

        self.SurroundModeStateNames = {
            'DIRECT'             : 'Direct',
            'PURE DIRECT'        : 'Pure Direct',
            'STEREO'             : 'Stereo',
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
            'DOLBY PL2 C'        : 'Dolby PL2 Cinema',
            'DOLBY PL2 M'        : 'Dolby PL2 Music',
            'DOLBY PL2 G'        : 'Dolby PL2 Game',
            'DOLBY PL2X C'       : 'Dolby PL2x Cinema',
            'DOLBY PL2X M'       : 'Dolby PL2x Music',
            'DOLBY PL2X G'       : 'Dolby PL2x Game',
            'DOLBY DIGITAL'      : 'Dolby Digital',
            'DOLBY D EX'         : 'Dolby D EX',
            'DOLBY D+PL2X C'     : 'Dolby D+PL2x Cinema',
            'DOLBY D+PL2X M'     : 'Dolby D+PL2x Music',
            'DTS NEO:6 C'        : 'DTS Neo:6 Cinema',
            'DTS NEO:6 M'        : 'DTS Neo:6 Music',
            'DTS SURROUND'       : 'DTS Surround',
            'DTS ES DSCRT6.1'    : 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1'     : 'DTS ES MTRX6.1',
            'DTS+PL2X C'         : 'DTS+PL2x Cinema',
            'DTS+PL2X M'         : 'DTS+PL2x Music',
            'DOLBY H/P'          : 'Dolby H/P',
            'DTS+DOLBY H/P'      : 'DTS+Dolby H/P',
            'HOME THX CINEMA'    : 'Home THX Cinema',
            'THX5.1'             : 'THX5.1',
            'THX U2 CINEMA'      : 'THX U2 Cinema',
            'THX MUSIC MODE'     : 'THX Music Mode',
            'THX6.1'             : 'THX6.1',
            'THX SURROUND EX'    : 'THX Surround EX',
            'WIDE SCREEN'        : 'Wide Screen',
            '5CH STEREO'         : '5CH Stereo',
            '7CH STEREO'         : '7CH Stereo',
            'SUPER STADIUM'      : 'Super Stadium',
            'ROCK ARENA'         : 'Rock Arena',
            'JAZZ CLUB'          : 'Jazz Club',
            'CLASSIC CONCERT'    : 'Classic Concert',
            'MONO MOVIE'         : 'Mono Movie',
            'MATRIX'             : 'Matrix',
            'VIDEO GAME'         : 'Video Game',
            'VIRTUAL'            : 'Virtual',
            'MPEG2 AAC'          : 'MPEG2 AAC',
            'AAC+DOLBY EX'       : 'AAC+Dolby EX',
            'AAC+PL2X C'         : 'AAC+PL2x Cinema',
            'AAC+PL2X M'         : 'AAC+PL2x Music'
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