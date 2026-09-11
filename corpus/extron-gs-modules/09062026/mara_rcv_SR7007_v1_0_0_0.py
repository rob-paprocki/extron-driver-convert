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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelButtonLock': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Mute': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'VSASP(NRM|FUL)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'SI(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|FLICKR|IRADIO|SERVER|FAVORITES|AUX1|AUX2|NET|MXPORT|USB/IPOD|USB|IPD|IRP|FVP)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'(MU|Z2MU|Z3MU)(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MS([ \S]+)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\rZ2(CD|MXPORT|USB/IPOD|USB|IPD|IRP|FVP)\rZ2([0-9]{2})\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z3(ON|OFF)\rZ3(CD|MXPORT|USB/IPOD|USB|IPD|IRP|FVP)\rZ3([0-9]{2})\r'), self.__MatchZone3Power, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': 'VSASPNRM\r',
            '16:9': 'VSASPFUL\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'VSASP?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'NRM': '4:3',
            'FUL': '16:9'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Phono': 'SIPHONO\r',
            'CD': 'SICD\r',
            'DVD': 'SIDVD\r',
            'BD': 'SIBD\r',
            'TV': 'SITV\r',
            'SAT/CBL': 'SISAT/CBL\r',
            'Media Player': 'SIMPLAY\r',
            'Game': 'SIGAME\r',
            'Flickr': 'SIFLICKR\r',
            'Internet Radio': 'SIIRADIO\r',
            'Server': 'SISERVER\r',
            'Favourites': 'SIFAVORITES\r',
            'Aux 1': 'SIAUX1\r',
            'Aux 2': 'SIAUX2\r',
            'Online Music': 'SINET\r',
            'MX Port': 'SIMXPORT\r',
            'USB/iPod': 'SIUSB/IPOD\r',
            'USB': 'SIUSB\r',
            'iPod': 'SIIPD\r',
            'Internet Radio and Recent': 'SIIRP\r',
            'Online Music and Favorites': 'SIFVP\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'PHONO': 'Phono',
            'CD': 'CD',
            'DVD': 'DVD',
            'BD': 'BD',
            'TV': 'TV',
            'SAT/CBL': 'SAT/CBL',
            'MPLAY': 'Media Player',
            'GAME': 'Game',
            'FLICKR': 'Flickr',
            'IRADIO': 'Internet Radio',
            'SERVER': 'Server',
            'FAVORITES': 'Favourites',
            'AUX1': 'Aux 1',
            'AUX2': 'Aux 2',
            'NET': 'Online Music',
            'MXPORT': 'MX Port',
            'USB/IPOD': 'USB/iPod',
            'USB': 'USB',
            'IPD': 'iPod',
            'IRP': 'Internet Radio and Recent',
            'FVP': 'Online Music and Favorites'
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

        if -80 <= value <= 18:
            MasterVolumeCmdString = 'MV{0:02}\r'.format(value + 80)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = int(match.group(1).decode()) - 80
        self.WriteStatus('MasterVolume', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'MNCUP\r',
            'Down': 'MNCDN\r',
            'Left': 'MNCLT\r',
            'Right': 'MNCRT\r',
            'Enter': 'MNENT\r',
            'Return': 'MNRTN\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

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

        if match.group(1).decode() == 'MU':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OutputMute', value, None)
        elif match.group(1).decode() == 'Z2MU':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Zone2Mute', value, None)
        elif match.group(1).decode() == 'Z3MU':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Zone3Mute', value, None)

    def SetPanelButtonLock(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': 'SYPANEL LOCK ON\r',
            'Mode 2': 'SYPANEL+V LOCK ON\r',
            'Off': 'SYPANEL LOCK OFF\r'
        }

        PanelButtonLockCmdString = ValueStateValues[value]
        self.__SetHelper('PanelButtonLock', PanelButtonLockCmdString, value, qualifier)

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

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': 'MSSMART1\r',
            '2': 'MSSMART2\r',
            '3': 'MSSMART3\r',
            '4': 'MSSMART4\r',
            '5': 'MSSMART5\r'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': 'MSSMART1 MEMORY\r',
            '2': 'MSSMART2 MEMORY\r',
            '3': 'MSSMART3 MEMORY\r',
            '4': 'MSSMART4 MEMORY\r',
            '5': 'MSSMART5 MEMORY\r'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
        }

        RemoteControlLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Movie': 'MSMOVIE\r',
            'Music': 'MSMUSIC\r',
            'Game': 'MSGAME\r',
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO\r',
            'Auto': 'MSAUTO\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'Dolby PL2 C': 'MSDOLBY PL2 C\r',
            'Dolby PL2 M': 'MSDOLBY PL2 M\r',
            'Dolby PL2 G': 'MSDOLBY PL2 G\r',
            'Dolby PL2X C': 'MSDOLBY PL2X C\r',
            'Dolby PL2X M': 'MSDOLBY PL2X M\r',
            'Dolby PL2X G': 'MSDOLBY PL2X G\r',
            'Dolby PL2Z H': 'MSDOLBY PL2Z H\r',
            'Dolby D EX': 'MSDOLBY D EX\r',
            'Dolby D+PL2X C': 'MSDOLBY D+PL2X C\r',
            'Dolby D+PL2X M': 'MSDOLBY D+PL2X M\r',
            'Dolby D+PL2Z H': 'MSDOLBY D+PL2Z H\r',
            'Dolby D+': 'MSDOLBY D+\r',
            'Dolby D+ +EX': 'MSDOLBY D+ +EX\r',
            'Dolby D+ +PL2X C': 'MSDOLBY D+ +PL2X C\r',
            'Dolby D+ +PL2X M': 'MSDOLBY D+ +PL2X M\r',
            'Dolby D+ +PL2Z H': 'MSDOLBY D+ +PL2Z H\r',
            'Dolby HD': 'MSDOLBY HD\r',
            'Dolby HD+EX': 'MSDOLBY HD+EX\r',
            'Dolby HD+PL2X C': 'MSDOLBY HD+PL2X C\r',
            'Dolby HD+PL2X M': 'MSDOLBY HD+PL2X M\r',
            'Dolby HD+PL2Z H': 'MSDOLBY HD+PL2Z H\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'DTS NEO:6 C': 'MSDTS NEO:6 C\r',
            'DTS NEO:6 M': 'MSDTS NEO:6 M\r',
            'DTS ES DSCRT6.1': 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX6.1': 'MSDTS ES MTRX6.1\r',
            'DTS+PL2X C': 'MSDTS+PL2X C\r',
            'DTS+PL2X M': 'MSDTS+PL2X M\r',
            'DTS+PL2Z H': 'MSDTS+PL2Z H\r',
            'DTS+NEO:6': 'MSDTS+NEO:6\r',
            'DTS 96/24': 'MSDTS96/24\r',
            'DTS 96 ES MTRX': 'MSDTS96 ES MTRX\r',
            'DTS HD': 'MSDTS HD\r',
            'DTS HD MSTR': 'MSDTS HD MSTR\r',
            'DTS HD+PL2X C': 'MSDTS HD+PL2X C\r',
            'DTS HD+PL2X M': 'MSDTS HD+PL2X M\r',
            'DTS HD+PL2Z H': 'MSDTS HD+PL2Z H\r',
            'DTS HD+NEO:6': 'MSDTS HD+NEO:6\r',
            'DTS Express': 'MSDTS EXPRESS\r',
            'DTS ES 8CH DSCRT': 'MSDTS ES 8CH DSCRT\r',
            'Multi Ch In': 'MSMULTI CH IN\r',
            'M Ch In+Dolby EX': 'MSM CH IN+DOLBY EX\r',
            'M Ch In+PL2X C': 'MSM CH IN+PL2X C\r',
            'M Ch In+PL2X M': 'MSM CH IN+PL2X M\r',
            'M Ch In+PL2Z H': 'MSM CH IN+PL2Z H\r',
            'Multi Ch In 7.1': 'MSMULTI CH IN 7.1\r',
            'PL2 C DSX': 'MSPL2 C DSX\r',
            'PL2 M DSX': 'MSPL2 M DSX\r',
            'PL2 G DSX': 'MSPL2 G DSX\r',
            'NEO:6 C DSX': 'MSNEO:6 C DSX\r',
            'NEO:6 M DSX': 'MSNEO:6 M DSX\r',
            'Audyssey DSX': 'MSAUDYSSEY DSX\r',
            'MCH Stereo': 'MSMCH STEREO\r',
            'Virtual': 'MSVIRTUAL\r',
            'Left': 'MSLEFT\r',
            'Right': 'MSRIGHT\r'
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'MOVIE': 'Movie',
            'MUSIC': 'Music',
            'GAME': 'Game',
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'AUTO': 'Auto',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DOLBY PL2 C': 'Dolby PL2 C',
            'DOLBY PL2 M': 'Dolby PL2 M',
            'DOLBY PL2 G': 'Dolby PL2 G',
            'DOLBY PL2X C': 'Dolby PL2X C',
            'DOLBY PL2X M': 'Dolby PL2X M',
            'DOLBY PL2X G': 'Dolby PL2X G',
            'DOLBY PL2Z H': 'Dolby PL2Z H',
            'DOLBY D EX': 'Dolby D EX',
            'DOLBY D+PL2X C': 'Dolby D+PL2X C',
            'DOLBY D+PL2X M': 'Dolby D+PL2X M',
            'DOLBY D+PL2Z H': 'Dolby D+PL2Z H',
            'DOLBY D+': 'Dolby D+',
            'DOLBY D+ +EX': 'Dolby D+ +EX',
            'DOLBY D+ +PL2X C': 'Dolby D+ +PL2X C',
            'DOLBY D+ +PL2X M': 'Dolby D+ +PL2X M',
            'DOLBY D+ +PL2Z H': 'Dolby D+ +PL2Z H',
            'DOLBY HD': 'Dolby HD',
            'DOLBY HD+EX': 'Dolby HD+EX',
            'DOLBY HD+PL2X C': 'Dolby HD+PL2X C',
            'DOLBY HD+PL2X M': 'Dolby HD+PL2X M',
            'DOLBY HD+PL2Z H': 'Dolby HD+PL2Z H',
            'DTS SURROUND': 'DTS Surround',
            'DTS NEO:6 C': 'DTS NEO:6 C',
            'DTS NEO:6 M': 'DTS NEO:6 M',
            'DTS ES DSCRT6.1': 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1': 'DTS ES MTRX6.1',
            'DTS+PL2X C': 'DTS+PL2X C',
            'DTS+PL2X M': 'DTS+PL2X M',
            'DTS+PL2Z H': 'DTS+PL2Z H',
            'DTS+NEO:6': 'DTS+NEO:6',
            'DTS96/24': 'DTS 96/24',
            'DTS96 ES MTRX': 'DTS 96 ES MTRX',
            'DTS HD': 'DTS HD',
            'DTS HD MSTR': 'DTS HD MSTR',
            'DTS HD+PL2X C': 'DTS HD+PL2X C',
            'DTS HD+PL2X M': 'DTS HD+PL2X M',
            'DTS HD+PL2Z H': 'DTS HD+PL2Z H',
            'DTS HD+NEO:6': 'DTS HD+NEO:6',
            'DTS EXPRESS': 'DTS Express',
            'DTS ES 8CH DSCRT': 'DTS ES 8CH DSCRT',
            'MULTI CH IN': 'Multi Ch In',
            'M CH IN+DOLBY EX': 'M Ch In+Dolby EX',
            'M CH IN+PL2X C': 'M Ch In+PL2X C',
            'M CH IN+PL2X M': 'M Ch In+PL2X M',
            'M CH IN+PL2Z H': 'M Ch In+PL2Z H',
            'MULTI CH IN 7.1': 'Multi Ch In 7.1',
            'PL2 C DSX': 'PL2 C DSX',
            'PL2 M DSX': 'PL2 M DSX',
            'PL2 G DSX': 'PL2 G DSX',
            'NEO:6 C DSX': 'NEO:6 C DSX',
            'NEO:6 M DSX': 'NEO:6 M DSX',
            'AUDYSSEY DSX': 'Audyssey DSX',
            'MCH STEREO': 'MCH Stereo',
            'VIRTUAL': 'Virtual',
            'LEFT': 'Left',
            'RIGHT': 'Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z2CD\r',
            'MX Port': 'Z2MXPORT\r',
            'USB/iPod': 'Z2USB/IPOD\r',
            'USB': 'Z2USB\r',
            'iPod': 'Z2IPD\r',
            'NET/USB and iRadio': 'Z2IRP\r',
            'NET/USB and Favorites': 'Z2FVP\r'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2MUON\r',
            'Off': 'Z2MUOFF\r'
        }

        Zone2MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2ON\r',
            'Off': 'Z2OFF\r'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', Zone2CmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Input', Zone2CmdString, value, qualifier)

    def UpdateZone2Volume(self, value, qualifier):

        Zone2CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Volume', Zone2CmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        Zone2PowerStates = {
            'ON': 'On',
            'OFF': 'Off'
        }

        Zone2InputStates = {
            'CD': 'CD',
            'MXPORT': 'MX Port',
            'USB/IPOD': 'USB/iPod',
            'USB': 'USB',
            'IPD': 'iPod',
            'IRP': 'NET/USB and iRadio',
            'FVP': 'NET/USB and Favorites'
        }

        PowerValue = Zone2PowerStates[match.group(1).decode()]
        self.WriteStatus('Zone2Power', PowerValue, None)

        InputValue = Zone2InputStates[match.group(2).decode()]
        self.WriteStatus('Zone2Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone2Volume', VolValue, None)

    def SetZone2Volume(self, value, qualifier):

        if -80 <= value <= 18:
            Zone2VolumeCmdString = 'Z2{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z3CD\r',
            'MX Port': 'Z3MXPORT\r',
            'USB/iPod': 'Z3USB/IPOD\r',
            'USB': 'Z3USB\r',
            'iPod': 'Z3IPD\r',
            'NET/USB and iRadio': 'Z3IRP\r',
            'NET/USB and Favorites': 'Z3FVP\r'
        }

        Zone3InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def SetZone3Mute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z3MUON\r',
            'Off': 'Z3MUOFF\r'
        }

        Zone3MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = 'Z3MU?\r'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def SetZone3Power(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z3ON\r',
            'Off': 'Z3OFF\r'
        }

        Zone3PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3CmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3Power', Zone3CmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3CmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3Input', Zone3CmdString, value, qualifier)

    def UpdateZone3Volume(self, value, qualifier):

        Zone3CmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3Volume', Zone3CmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        Zone3PowerStates = {
            'ON': 'On',
            'OFF': 'Off'
        }

        Zone3InputStates = {
            'CD': 'CD',
            'MXPORT': 'MX Port',
            'USB/IPOD': 'USB/iPod',
            'USB': 'USB',
            'IPD': 'iPod',
            'IRP': 'NET/USB and iRadio',
            'FVP': 'NET/USB and Favorites'
        }

        PowerValue = Zone3PowerStates[match.group(1).decode()]
        self.WriteStatus('Zone3Power', PowerValue, None)

        InputValue = Zone3InputStates[match.group(2).decode()]
        self.WriteStatus('Zone3Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone3Volume', VolValue, None)

    def SetZone3Volume(self, value, qualifier):

        if -80 <= value <= 18:
            Zone3VolumeCmdString = 'Z3{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

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