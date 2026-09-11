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
            'ChannelVolume': {'Parameters': ['Channel'], 'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteLock': {'Status': {}},
            'SurroundBackVolume': {'Status': {}},
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
            self.AddMatchString(re.compile(b'^CV(FL|FR|C|SW|SL|SR|SBL|SBR) ([0-9]{2})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'^SI(PHONO|CD|TUNER|DVD|VDP|TV|DBS|VCR-1|VCR-2|VCR-3|V.AUX|CDR/TAPE)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'^ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'^MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'^MU(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'^PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'^CVSB ([0-9]{2})\r'), self.__MatchSurroundBackVolume, None)
            self.AddMatchString(re.compile(b'^MS(.*)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z2MU(ON|OFF)\r'), self.__MatchZone2AudioMute, None)
            self.AddMatchString(re.compile(b'Z2(PHONO|CD|TUNER|DVD|VDP|TV|DBS|VCR-1|VCR-2|V.AUX|CDR/TAPE)\r'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{2})\r'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'Z3(ON|OFF)\r'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'Z3MU(ON|OFF)\r'), self.__MatchZone3AudioMute, None)
            self.AddMatchString(re.compile(b'Z3(PHONO|CD|TUNER|DVD|VDP|TV|DBS|VCR-1|VCR-2|V.AUX|CDR/TAPE)\r'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'Z3([0-9]{2})\r'), self.__MatchZone3Volume, None)

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'CVFL',
            'Front Right': 'CVFR',
            'Center': 'CVC',
            'Subwoofer': 'CVSW',
            'Surround Left': 'CVSL',
            'Surround Right': 'CVSR',
            'Surround Back Left': 'CVSBL',
            'Surround Back Right': 'CVSBR'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            valuex = value + 50
            ChannelVolumeCmdString = '{0}{1:02}\r'.format(ChannelStates[qualifier['Channel']], valuex)
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
             'SBR': 'Surround Back Right'
        }

        ChannelQual = ChannelStates[match.group(1).decode()]
        qualifier = {'Channel': ChannelQual}
        valuex = int(match.group(2).decode())
        value = valuex - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CD': 'SICD\r',
            'Tuner': 'SITUNER\r',
            'DVD': 'SIDVD\r',
            'VDP': 'SIVDP\r',
            'TV': 'SITV\r',
            'DBS': 'SIDBS\r',
            'VCR 1': 'SIVCR-1\r',
            'VCR 2': 'SIVCR-2\r',
            'VCR 3': 'SIVCR-3\r',
            'V Aux': 'SIV.AUX\r',
            'CDR/Tape': 'SICDR/TAPE\r',
            'Phono': 'SIPHONO\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'VDP': 'VDP',
            'TV': 'TV',
            'DBS': 'DBS',
            'VCR-1': 'VCR 1',
            'VCR-2': 'VCR 2',
            'VCR-3': 'VCR 3',
            'V.AUX': 'V Aux',
            'CDR/TAPE': 'CDR/Tape',
            'PHONO': 'Phono'
        }

        value = ValueStateValues[match.group(1).decode()]
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
            valuex = value + 80
            MasterVolumeCmdString = 'MV{0:02}\r'.format(valuex)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
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

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputMute', value, None)

    def SetPanelLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYPANEL LOCK ON\r',
            'Off': 'SYPANEL LOCK OFF\r',
            'On with Master Volume Control Lock On': 'SYPANEL+V LOCK ON\r'
        }

        PanelLockCmdString = ValueStateValues[value]
        self.__SetHelper('PanelLock', PanelLockCmdString, value, qualifier)

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

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
        }

        RemoteLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def SetSurroundBackVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            valuex = value + 80
            SurroundBackVolumeCmdString = 'CVSB {0:02}\r'.format(valuex)
            self.__SetHelper('SurroundBackVolume', SurroundBackVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurroundBackVolume')

    def UpdateSurroundBackVolume(self, value, qualifier):

        SurroundBackVolumeCmdString = 'CV?\r'
        self.__UpdateHelper('SurroundBackVolume', SurroundBackVolumeCmdString, value, qualifier)

    def __MatchSurroundBackVolume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
        self.WriteStatus('SurroundBackVolume', value, None)

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO',
            'Multi CH IN': 'MSMULTI CH IN\r',
            'Multi CH Direct': 'MSMULTI CH DIRECT\r',
            'Multi CH Pure D': 'MSMULTI CH PURE D\r',
            'Dolby Pro Logic': 'MSDOLBY PRO LOGIC\r',
            'Dolby PL2': 'MSDOLBY PL2\r',
            'Dolby PL2x': 'MSDOLBY PL2X\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'Dolby D EX': 'MSDOLBY D EX\r',
            'DTS NEO : 6': 'MSDTS NEO:6\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'DTS ES DSCRT 6.1': 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX 6.1': 'MSDTS ES MTRX6.1\r',
            'Dolby H/P': 'MSDOLBY H/P\r',
            'DTS+Dolby H/P': 'MSDTS+DOLBY H/P\r',
            'Home THX Cinema': 'MSHOME THX CINEMA\r',
            'THX 5.1': 'MSTHX 5.1\r',
            'THX U2 Cinema': 'MSTHX U2 CINEMA\r',
            'THX Music Mode': 'MSTHX MUSIC MODE\r',
            'THX Games Mode': 'MSTHX GAMES MODE\r',
            'THX 6.1': 'MSTHX 6.1\r',
            'THX Surround EX': 'MSTHX SURROUND EX\r',
            'Wide Screen': 'MSWIDE SCREEN\r',
            '5ch Stereo': 'MS5CH STEREO\r',
            '7ch Stereo': 'MS7CH STEREO\r',
            '9ch Stereo': 'MS9CH STEREO\r',
            'Super Stadium': 'MSSUPER STADIUM\r',
            'Rock Arena': 'MSROCK ARENA\r',
            'Jazz Club': 'MSJAZZ CLUB\r',
            'Classic Concert': 'MSCLASSIC CONCERT\r',
            'Mono Movie': 'MSMONO MOVIE\r',
            'Matrix': 'MSMATRIX\r',
            'Video Game': 'MSVIDEO GAME\r',
            'Virtual': 'MSVIRTUAL\r',
            'MPEG2 AAC': 'MSMPEG2 AAC\r',
            'AAC+Dolby EX': 'MSAAC+DOLBY EX\r',
            'User 1': 'MSUSER1\r',
            'User 2': 'MSUSER2\r',
            'User 3': 'MSUSER3\r',
            'User 1 Memory': 'MSUSER1 MEMORY\r',
            'User 2 Memory': 'MSUSER2 MEMORY\r',
            'User 3 Memory': 'MSUSER3 MEMORY\r'
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'MULTI CH IN': 'Multi CH IN',
            'MULTI CH DIRECT': 'Multi CH Direct',
            'MULTI CH PURE D': 'Multi CH Pure D',
            'DOLBY PRO LOGIC': 'Dolby Pro Logic',
            'DOLBY PL2': 'Dolby PL2',
            'DOLBY PL2X': 'Dolby PL2x',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DOLBY D EX': 'Dolby D EX',
            'DTS NEO:6': 'DTS NEO : 6',
            'DTS SURROUND': 'DTS Surround',
            'DTS ES DSCRT6.1': 'DTS ES DSCRT 6.1',
            'DTS ES MTRX6.1': 'DTS ES MTRX 6.1',
            'DOLBY H/P': 'Dolby H/P',
            'DTS+DOLBY H/P': 'DTS+Dolby H/P',
            'HOME THX CINEMA': 'Home THX Cinema',
            'THX 5.1': 'THX 5.1',
            'THX U2 CINEMA': 'THX U2 Cinema',
            'THX MUSIC MODE': 'THX Music Mode',
            'THX GAMES MODE': 'THX Games Mode',
            'THX 6.1': 'THX 6.1',
            'THX SURROUND EX': 'THX Surround EX',
            'WIDE SCREEN': 'Wide Screen',
            '5CH STEREO': '5ch Stereo',
            '7CH STEREO': '7ch Stereo',
            '9CH STEREO': '9ch Stereo',
            'SUPER STADIUM': 'Super Stadium',
            'ROCK ARENA': 'Rock Arena',
            'JAZZ CLUB': 'Jazz Club',
            'CLASSIC CONCERT': 'Classic Concert',
            'MONO MOVIE': 'Mono Movie',
            'MATRIX': 'Matrix',
            'VIDEO GAME': 'Video Game',
            'VIRTUAL': 'Virtual',
            'MPEG2 AAC': 'MPEG2 AAC',
            'AAC+DOLBY EX': 'AAC+Dolby EX',
            'USER1': 'User 1',
            'USER2': 'User 2',
            'USER3': 'User 3',
            'USER1 MEMORY': 'User 1 Memory',
            'USER2 MEMORY': 'User 2 Memory',
            'USER3 MEMORY': 'User 3 Memory'
        }

        value = ValueStateValues[match.group(1).decode()]
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

    def __MatchZone2AudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2AudioMute', value, None)

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
            'CDR/Tape': 'Z2CDR/TAPE\r',
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
            'CDR/TAPE': 'CDR/Tape',
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
            'On': 'Z3ON\r',
            'Off': 'Z3OFF\r'
        }

        Zone3PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = 'Z3?\r'
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
            'On': 'Z3MUON\r',
            'Off': 'Z3MUOFF\r'
        }

        Zone3AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)

    def UpdateZone3AudioMute(self, value, qualifier):

        Zone3AudioMuteCmdString = 'Z3MU?\r'
        self.__UpdateHelper('Zone3AudioMute', Zone3AudioMuteCmdString, value, qualifier)

    def __MatchZone3AudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3AudioMute', value, None)

    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z3CD\r',
            'Tuner': 'Z3TUNER\r',
            'DVD': 'Z3DVD\r',
            'VDP': 'Z3VDP\r',
            'TV': 'Z3TV\r',
            'DBS': 'Z3DBS\r',
            'VCR 1': 'Z3VCR-1\r',
            'VCR 2': 'Z3VCR-2\r',
            'V Aux': 'Z3V.AUX\r',
            'CDR/Tape': 'Z3CDR/TAPE\r',
            'Phono': 'Z3PHONO\r'
        }

        Zone3InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = 'Z3?\r'
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
            'CDR/TAPE': 'CDR/Tape',
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
            Zone3VolumeCmdString = 'Z3{0:02}\r'.format(valuex)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = 'Z3?\r'
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

