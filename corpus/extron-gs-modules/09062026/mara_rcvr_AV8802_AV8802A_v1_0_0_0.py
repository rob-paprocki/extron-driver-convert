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
            'AspectRatio': { 'Status': {}},
            'ChannelVolume': {'Parameters':['Channel'], 'Status': {}},
            'Input': { 'Status': {}},
            'MainZonePower': { 'Status': {}},
            'MasterVolume': { 'Status': {}},
            'MenuControl': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OutputMute': { 'Status': {}},
            'PanelLock': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RemoteLock': { 'Status': {}},
            'SurroundMode': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone2Mute': { 'Status': {}},
            'Zone2Power': { 'Status': {}},
            'Zone2PresetRecall': { 'Status': {}},
            'Zone2PresetSave': { 'Status': {}},
            'Zone2Volume': { 'Status': {}},
            'Zone3Input': { 'Status': {}},
            'Zone3Mute': { 'Status': {}},
            'Zone3Power': { 'Status': {}},
            'Zone3PresetRecall': { 'Status': {}},
            'Zone3PresetSave': { 'Status': {}},
            'Zone3Volume': { 'Status': {}},
            'Zone4Input': { 'Status': {}},
            'Zone4Power': { 'Status': {}},
            }

        self.__LastChannelUpdate = 0




        self.AddMatchString(re.compile(b'VSASP(NRM|FUL)\r'), self.__MatchAspectRatio, None)
        self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SW2|SL|SR|SBL|SBR|SB|FHL|FHR|FWL|FWR|TFL|TFR|TML|TMR|TRL|TRR|RHL|RHR|FDL|FDR|SDL|SDR|BDL|BDR) ([0-9]{2})\r'), self.__MatchChannelVolume, None)
        self.AddMatchString(re.compile(b'SI(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|FLICKR|IRADIO|SERVER|FAVORITES|AUX1|AUX2|AUX3|AUX4|AUX5|AUX6|AUX7|NET|BT|USB/IPOD|USB|IPD|IRP|FVP)\r'), self.__MatchInput, None)
        self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
        self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
        self.AddMatchString(re.compile(b'MNMEN (ON|OFF)\r'), self.__MatchMenuControl, None)
        self.AddMatchString(re.compile(b'(MU|Z2MU|Z3MU)(ON|OFF)\r'), self.__MatchOutputMute, None)
        self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
        self.AddMatchString(re.compile(b'MS([\s\S]+)\r'), self.__MatchSurroundMode, None)
        self.AddMatchString(re.compile(b'Z2(ON|OFF)\rZ2(CD|AUX3|AUX4|AUX5|AUX6|AUX7|BT|USB/IPOD|USB|IPD|IRP|FVP)\rZ2([0-9]{2})\r'), self.__MatchZone2Power, None)
        self.AddMatchString(re.compile(b'Z3(ON|OFF)\rZ3(CD|AUX3|AUX4|AUX5|AUX6|AUX7|BT|USB/IPOD|USB|IPD|IRP|FVP)\rZ3([0-9]{2})\r'), self.__MatchZone3Power, None)
        self.AddMatchString(re.compile(b'Z4(ON|OFF)\rZ4(CD|AUX3|AUX4|AUX5|AUX6|AUX7)\r'), self.__MatchZone4Power, None)



    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 'VSASPNRM\r', 
            'Full'   : 'VSASPFUL\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'VSASP ?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'NRM' : 'Normal', 
            'FUL' : 'Full'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left'           : 'CVFL', 
            'Front Right'          : 'CVFR', 
            'Center'               : 'CVC', 
            'Subwoofer'            : 'CVSW', 
            'Subwoofer 2'          : 'CVSW2', 
            'Surround Left'        : 'CVSL', 
            'Surround Right'       : 'CVSR', 
            'Surround Back Left'   : 'CVSBL', 
            'Surround Back Right'  : 'CVSBR', 
            'Surround Back'        : 'CVSB', 
            'Front Height Left'    : 'CVFHL', 
            'Front Height Right'   : 'CVFHR', 
            'Front Wide Left'      : 'CVFWL', 
            'Front Wide Right'     : 'CVFWR', 
            'Top Front Left'       : 'CVTFL', 
            'Top Front Right'      : 'CVTFR', 
            'Top Middle Left'      : 'CVTML', 
            'Top Middle Right'     : 'CVTMR', 
            'Top Rear Left'        : 'CVTRL', 
            'Top Rear Right'       : 'CVTRR', 
            'Rear Height Left'     : 'CVRHL', 
            'Rear Height Right'    : 'CVRHR', 
            'Front Dolby Left'     : 'CVFDL', 
            'Front Dolby Right'    : 'CVFDR', 
            'Surround Dolby Left'  : 'CVSDL', 
            'Surround Dolby Right' : 'CVSDR', 
            'Back Dolby Left'      : 'CVBDL', 
            'Back Dolby Right'     : 'CVBDR'
        }

        ValueConstraints = {
            'Min' : -12,
            'Max' : 12
            }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel in ChannelStates:
            ChannelVolumeCmdString = '{0} {1:02}\r'.format(ChannelStates[channel], value + 50)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelVolume')
    def UpdateChannelVolume(self, value, qualifier):

        
        ChannelVolumeCmdString = 'CV?\r'
        self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)


    def __MatchChannelVolume(self, match, tag):

        ChannelStates = {
             'FL'  : 'Front Left', 
             'FR'  : 'Front Right' , 
             'C'   : 'Center', 
             'SW'  : 'Subwoofer', 
             'SW2' : 'Subwoofer 2', 
             'SL'  : 'Surround Left', 
             'SR'  : 'Surround Right', 
             'SBL' : 'Surround Back Left', 
             'SBR' : 'Surround Back Right',   
             'SB'  : 'Surround Back',         
             'FHL' : 'Front Height Left',     
             'FHR' : 'Front Height Right',    
             'FWL' : 'Front Wide Left',       
             'FWR' : 'Front Wide Right',      
             'TFL' : 'Top Front Left',        
             'TFR' : 'Top Front Right',       
             'TML' : 'Top Middle Left',       
             'TMR' : 'Top Middle Right',      
             'TRL' : 'Top Rear Left',         
             'TRR' : 'Top Rear Right',        
             'RHL' : 'Rear Height Left',      
             'RHR' : 'Rear Height Right',     
             'FDL' : 'Front Dolby Left',      
             'FDR' : 'Front Dolby Right',     
             'SDL' : 'Surround Dolby Left',   
             'SDR' : 'Surround Dolby Right',  
             'BDL' : 'Back Dolby Left',       
             'BDR' : 'Back Dolby Right',      
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode()) - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Phono'                          : 'SIPHONO\r', 
            'CD'                             : 'SICD\r', 
            'DVD'                            : 'SIDVD\r', 
            'BD'                             : 'SIBD\r', 
            'TV'                             : 'SITV\r', 
            'SAT/CBL'                        : 'SISAT/CBL\r', 
            'Media Player'                   : 'SIMPLAY\r', 
            'Game'                           : 'SIGAME\r', 
            'Flickr'                         : 'SIFLICKR\r', 
            'Internet Radio'                 : 'SIIRADIO\r', 
            'Server'                         : 'SISERVER\r', 
            'Favorites'                      : 'SIFAVORITES\r', 
            'AUX 1'                          : 'SIAUX1\r', 
            'AUX 2'                          : 'SIAUX2\r', 
            'AUX 3'                          : 'SIAUX3\r', 
            'AUX 4'                          : 'SIAUX4\r', 
            'AUX 5'                          : 'SIAUX5\r', 
            'AUX 6'                          : 'SIAUX6\r', 
            'AUX 7'                          : 'SIAUX7\r', 
            'NET'                            : 'SINET\r', 
            'Bluetooth'                      : 'SIBT\r', 
            'USB/iPod'                       : 'SIUSB/IPOD\r', 
            'USB'                            : 'SIUSB\r', 
            'iPod'                           : 'SIIPD\r', 
            'Internet Radio and Recent Play' : 'SIIRP\r', 
            'Network and Favorites Play'     : 'SIFVP\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'PHONO'     : 'Phono', 
            'CD'        : 'CD', 
            'DVD'       : 'DVD', 
            'BD'        : 'BD', 
            'TV'        : 'TV', 
            'SAT/CBL'   : 'SAT/CBL', 
            'MPLAY'     : 'Media Player', 
            'GAME'      : 'Game', 
            'FLICKR'    : 'Flickr', 
            'IRADIO'    : 'Internet Radio', 
            'SERVER'    : 'Server', 
            'FAVORITES' : 'Favorites', 
            'AUX1'      : 'AUX 1', 
            'AUX2'      : 'AUX 2', 
            'AUX3'      : 'AUX 3', 
            'AUX4'      : 'AUX 4', 
            'AUX5'      : 'AUX 5', 
            'AUX6'      : 'AUX 6', 
            'AUX7'      : 'AUX 7', 
            'NET'       : 'NET', 
            'BT'        : 'Bluetooth', 
            'USB/IPOD'  : 'USB/iPod', 
            'USB'       : 'USB', 
            'IPD'       : 'iPod', 
            'IRP'       : 'Internet Radio and Recent Play', 
            'FVP'       : 'Network and Favorites Play'
        }

        value = ValueStateValues[match.group(1).decode()]
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

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
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

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MNMEN ON\r', 
            'Off' : 'MNMEN OFF\r'
        }

        MenuControlCmdString = ValueStateValues[value]
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)
    def UpdateMenuControl(self, value, qualifier):

        MenuControlCmdString = 'MNMEN?\r'
        self.__UpdateHelper('MenuControl', MenuControlCmdString, value, qualifier)

    def __MatchMenuControl(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MenuControl', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'     : 'MNCUP\r', 
            'Down'   : 'MNCDN\r', 
            'Left'   : 'MNCLT\r', 
            'Right'  : 'MNCRT\r', 
            'Enter'  : 'MNENT\r', 
            'Return' : 'MNRTN\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUON\r', 
            'Off' : 'MUOFF\r'
        }

        OutputMuteCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'MU?\r'
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
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

    def SetPanelLock(self, value, qualifier):

        ValueStateValues = {
            'On'                      : 'SYPANEL LOCK ON\r',  
            'Off'                     : 'SYPANEL LOCK OFF\r', 
            'On except Master Volume' : 'SYPANEL+V LOCK ON\r'
        }

        PanelLockCmdString = ValueStateValues[value]
        self.__SetHelper('PanelLock', PanelLockCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PWON\r', 
            'Off' : 'PWSTANDBY\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

            
        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON'      : 'On', 
            'STANDBY' : 'Off'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : 'MSSMART1\r', 
            '2' : 'MSSMART2\r', 
            '3' : 'MSSMART3\r', 
            '4' : 'MSSMART4\r', 
            '5' : 'MSSMART5\r'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : 'MSSMART1 MEMORY\r', 
            '2' : 'MSSMART2 MEMORY\r', 
            '3' : 'MSSMART3 MEMORY\r', 
            '4' : 'MSSMART4 MEMORY\r', 
            '5' : 'MSSMART5 MEMORY\r'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'SYREMOTE LOCK ON\r', 
            'Off' : 'SYREMOTE LOCK OFF\r'
        }

        RemoteLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)


    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Movie'             : 'MSMOVIE\r', 
            'Music'             : 'MSMUSIC\r', 
            'Game'              : 'MSGAME\r', 
            'Direct'            : 'MSDIRECT\r', 
            'Pure Direct'       : 'MSPURE DIRECT\r', 
            'Stereo'            : 'MSSTEREO\r', 
            'Auto'              : 'MSAUTO\r', 
            'Dolby Digital'     : 'MSDOLBY DIGITAL\r', 
            'Dolby Surround'    : 'MSDOLBY SURROUND\r', 
            'Dolby Atmos'       : 'MSDOLBY ATMOS\r', 
            'Dolby D+DS'        : 'MSDOLBY D+DS\r', 
            'Dolby D+NEO:X C'   : 'MSDOLBY D+NEO:X C\r', 
            'Dolby D+NEO:X M'   : 'MSDOLBY D+NEO:X M\r', 
            'Dolby D+NEO:X G'   : 'MSDOLBY D+NEO:X G\r', 
            'Dolby D+'          : 'MSDOLBY D+\r', 
            'Dolby D+ +DS'      : 'MSDOLBY D+ +DS\r', 
            'Dolby D+ +NEO:X C' : 'MSDOLBY D+ +NEO:X C\r', 
            'Dolby D+ +NEO:X M' : 'MSDOLBY D+ +NEO:X M\r', 
            'Dolby D+ +NEO:X G' : 'MSDOLBY D+ +NEO:X G\r', 
            'Dolby HD'          : 'MSDOLBY HD\r', 
            'Dolby HD+EX'       : 'MSDOLBY HD+EX\r', 
            'Dolby HD+PL2X C'   : 'MSDOLBY HD+PL2X C\r', 
            'Dolby HD+PL2X M'   : 'MSDOLBY HD+PL2X M\r', 
            'Dolby HD+PL2Z H'   : 'MSDOLBY HD+PL2Z H\r', 
            'Dolby HD+DS'       : 'MSDOLBY HD+DS\r', 
            'Dolby HD+NEO:X C'  : 'MSDOLBY HD+NEO:X C\r', 
            'Dolby HD+NEO:X M'  : 'MSDOLBY HD+NEO:X M\r', 
            'Dolby HD+NEO:X G'  : 'MSDOLBY HD+NEO:X G\r', 
            'DTS Surround'      : 'MSDTS SURROUND\r', 
            'DTS NEO:X C'       : 'MSDTS NEO:X C\r', 
            'DTS NEO:X M'       : 'MSDTS NEO:X M\r', 
            'DTS NEO:X G'       : 'MSDTS NEO:X G\r', 
            'DTS ES DSCRT6.1'   : 'MSDTS ES DSCRT6.1\r', 
            'DTS ES MTRX6.1'    : 'MSDTS ES MTRX6.1\r', 
            'DTS+DS'            : 'MSDTS+DS\r', 
            'DTS+NEO:X C'       : 'MSDTS+NEO:X C\r', 
            'DTS+NEO:X M'       : 'MSDTS+NEO:X M\r', 
            'DTS+NEO:X G'       : 'MSDTS+NEO:X G\r', 
            'DTS96/24'          : 'MSDTS96/24\r', 
            'DTS96 ES MTRX'     : 'MSDTS96 ES MTRX\r', 
            'DTS HD'            : 'MSDTS HD\r', 
            'DTS HD MSTR'       : 'MSDTS HD MSTR\r', 
            'DTS HD+DS'         : 'MSDTS HD+DS\r', 
            'DTS HD+NEO:X C'    : 'MSDTS HD+NEO:X C\r', 
            'DTS HD+NEO:X M'    : 'MSDTS HD+NEO:X M\r', 
            'DTS HD+NEO:X G'    : 'MSDTS HD+NEO:X G\r', 
            'DTS Express'       : 'MSDTS EXPRESS\r', 
            'DTS ES 8CH DSCRT'  : 'MSDTS ES 8CH DSCRT\r', 
            'Multi CH IN'       : 'MSMULTI CH IN\r', 
            'M CH IN+DS'        : 'MSM CH IN+DS\r', 
            'M CH IN+NEO:X C'   : 'MSM CH IN+NEO:X C\r', 
            'M CH IN+NEO:X M'   : 'MSM CH IN+NEO:X M\r', 
            'M CH IN+NEO:X G'   : 'MSM CH IN+NEO:X G\r', 
            'Multi CH IN 7.1'   : 'MSMULTI CH IN 7.1\r', 
            'Audyssey DSX'      : 'MSAUDYSSEY DSX\r', 
            'MCH Stereo'        : 'MSMCH STEREO\r', 
            'Virtual'           : 'MSVIRTUAL\r', 
            'Left'              : 'MSLEFT\r', 
            'Right'             : 'MSRIGHT\r'
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)
    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'MOVIE'             : 'Movie', 
            'MUSIC'             : 'Music', 
            'GAME'              : 'Game', 
            'DIRECT'            : 'Direct', 
            'PURE DIRECT'       : 'Pure Direct', 
            'STEREO'            : 'Stereo', 
            'AUTO'              : 'Auto', 
            'DOLBY DIGITAL'     : 'Dolby Digital', 
            'DOLBY SURROUND'    : 'Dolby Surround', 
            'DOLBY ATMOS'       : 'Dolby Atmos', 
            'DOLBY D+DS'        : 'Dolby D+DS', 
            'DOLBY D+NEO:X C'   : 'Dolby D+NEO:X C', 
            'DOLBY D+NEO:X M'   : 'Dolby D+NEO:X M', 
            'DOLBY D+NEO:X G'   : 'Dolby D+NEO:X G', 
            'DOLBY D+'          : 'Dolby D+', 
            'DOLBY D+ +DS'      : 'Dolby D+ +DS', 
            'DOLBY D+ +NEO:X C' : 'Dolby D+ +NEO:X C', 
            'DOLBY D+ +NEO:X M' : 'Dolby D+ +NEO:X M', 
            'DOLBY D+ +NEO:X G' : 'Dolby D+ +NEO:X G', 
            'DOLBY HD'          : 'Dolby HD', 
            'DOLBY HD+EX'       : 'Dolby HD+EX', 
            'DOLBY HD+PL2X C'   : 'Dolby HD+PL2X C', 
            'DOLBY HD+PL2X M'   : 'Dolby HD+PL2X M', 
            'DOLBY HD+PL2Z H'   : 'Dolby HD+PL2Z H', 
            'DOLBY HD+DS'       : 'Dolby HD+DS', 
            'DOLBY HD+NEO:X C'  : 'Dolby HD+NEO:X C', 
            'DOLBY HD+NEO:X M'  : 'Dolby HD+NEO:X M', 
            'DOLBY HD+NEO:X G'  : 'Dolby HD+NEO:X G', 
            'DTS SURROUND'      : 'DTS Surround', 
            'DTS NEO:X C'       : 'DTS NEO:X C', 
            'DTS NEO:X M'       : 'DTS NEO:X M', 
            'DTS NEO:X G'       : 'DTS NEO:X G', 
            'DTS ES DSCRT6.1'   : 'DTS ES DSCRT6.1', 
            'DTS ES MTRX6.1'    : 'DTS ES MTRX6.1', 
            'DTS+DS'            : 'DTS+DS', 
            'DTS+NEO:X C'       : 'DTS+NEO:X C', 
            'DTS+NEO:X M'       : 'DTS+NEO:X M', 
            'DTS+NEO:X G'       : 'DTS+NEO:X G', 
            'DTS96/24'          : 'DTS96/24', 
            'DTS96 ES MTRX'     : 'DTS96 ES MTRX', 
            'DTS HD'            : 'DTS HD', 
            'DTS HD MSTR'       : 'DTS HD MSTR', 
            'DTS HD+DS'         : 'DTS HD+DS', 
            'DTS HD+NEO:X C'    : 'DTS HD+NEO:X C', 
            'DTS HD+NEO:X M'    : 'DTS HD+NEO:X M', 
            'DTS HD+NEO:X G'    : 'DTS HD+NEO:X G', 
            'DTS EXPRESS'       : 'DTS Express', 
            'DTS ES 8CH DSCRT'  : 'DTS ES 8CH DSCRT', 
            'MULTI CH IN'       : 'Multi CH IN', 
            'M CH IN+DS'        : 'M CH IN+DS', 
            'M CH IN+NEO:X C'   : 'M CH IN+NEO:X C', 
            'M CH IN+NEO:X M'   : 'M CH IN+NEO:X M', 
            'M CH IN+NEO:X G'   : 'M CH IN+NEO:X G', 
            'MULTI CH IN 7.1'   : 'Multi CH IN 7.1', 
            'AUDYSSEY DSX'      : 'Audyssey DSX', 
            'MCH STEREO'        : 'MCH Stereo', 
            'VIRTUAL'           : 'Virtual', 
            'LEFT'              : 'Left', 
            'RIGHT'             : 'Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'CD'                             : 'Z2CD\r', 
            'AUX 3'                          : 'Z2AUX3\r', 
            'AUX 4'                          : 'Z2AUX4\r', 
            'AUX 5'                          : 'Z2AUX5\r', 
            'AUX 6'                          : 'Z2AUX6\r', 
            'AUX 7'                          : 'Z2AUX7\r', 
            'Bluetooth'                      : 'Z2BT\r', 
            'USB/iPod'                       : 'Z2USB/IPOD\r', 
            'USB'                            : 'Z2USB\r', 
            'iPod'                           : 'Z2IPD\r', 
            'Internet Radio and Recent Play' : 'Z2IRP\r', 
            'Network and Favorites Play'     : 'Z2FVP\r'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z2MUON\r', 
            'Off' : 'Z2MUOFF\r'
        }

        Zone2MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)
    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z2ON\r', 
            'Off' : 'Z2OFF\r'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        PowerStates = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        InputStates = {
            'CD'        : 'CD', 
            'AUX3'      : 'AUX 3', 
            'AUX4'      : 'AUX 4', 
            'AUX5'      : 'AUX 5', 
            'AUX6'      : 'AUX 6', 
            'AUX7'      : 'AUX 7', 
            'BT'        : 'Bluetooth', 
            'USB/IPOD'  : 'USB/iPod', 
            'USB'       : 'USB', 
            'IPD'       : 'iPod', 
            'IRP'       : 'Internet Radio and Recent Play', 
            'FVP'       : 'Network and Favorites Play'
        }

        PowerValue = PowerStates[match.group(1).decode()]
        self.WriteStatus('Zone2Power', PowerValue, None)

        InputValue = InputStates[match.group(2).decode()]
        self.WriteStatus('Zone2Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone2Volume', VolValue, None)

    def SetZone2PresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Z2SMART1\r', 
            '2' : 'Z2SMART2\r', 
            '3' : 'Z2SMART3\r', 
            '4' : 'Z2SMART4\r', 
            '5' : 'Z2SMART5\r'
        }

        Zone2PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2PresetRecall', Zone2PresetRecallCmdString, value, qualifier)


    def SetZone2PresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Z2SMART1 MEMORY\r', 
            '2' : 'Z2SMART2 MEMORY\r', 
            '3' : 'Z2SMART3 MEMORY\r', 
            '4' : 'Z2SMART4 MEMORY\r', 
            '5' : 'Z2SMART5 MEMORY\r'
        }

        Zone2PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2PresetSave', Zone2PresetSaveCmdString, value, qualifier)


    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = 'Z2{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')
    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'CD'                             : 'Z3CD\r', 
            'AUX 3'                          : 'Z3AUX3\r', 
            'AUX 4'                          : 'Z3AUX4\r', 
            'AUX 5'                          : 'Z3AUX5\r', 
            'AUX 6'                          : 'Z3AUX6\r', 
            'AUX 7'                          : 'Z3AUX7\r', 
            'Bluetooth'                      : 'Z3BT\r', 
            'USB/iPod'                       : 'Z3USB/IPOD\r', 
            'USB'                            : 'Z3USB\r', 
            'iPod'                           : 'Z3IPD\r', 
            'Internet Radio and Recent Play' : 'Z3IRP\r', 
            'Network and Favorites Play'     : 'Z3FVP\r'
        }

        Zone3InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)
    def SetZone3Mute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z3MUON\r', 
            'Off' : 'Z3MUOFF\r'
        }

        Zone3MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)
    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = 'Z3MU?\r'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def SetZone3Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z3ON\r', 
            'Off' : 'Z3OFF\r'
        }

        Zone3PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)
    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        PowerStates = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        InputStates = {
            'CD'        : 'CD', 
            'AUX3'      : 'AUX 3', 
            'AUX4'      : 'AUX 4', 
            'AUX5'      : 'AUX 5', 
            'AUX6'      : 'AUX 6', 
            'AUX7'      : 'AUX 7', 
            'BT'        : 'Bluetooth', 
            'USB/IPOD'  : 'USB/iPod', 
            'USB'       : 'USB', 
            'IPD'       : 'iPod', 
            'IRP'       : 'Internet Radio and Recent Play', 
            'FVP'       : 'Network and Favorites Play'
        }

        PowerValue = PowerStates[match.group(1).decode()]
        self.WriteStatus('Zone3Power', PowerValue, None)

        InputValue = InputStates[match.group(2).decode()]
        self.WriteStatus('Zone3Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone3Volume', VolValue, None)

    def SetZone3PresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Z3SMART1\r', 
            '2' : 'Z3SMART2\r', 
            '3' : 'Z3SMART3\r', 
            '4' : 'Z3SMART4\r', 
            '5' : 'Z3SMART5\r'
        }

        Zone3PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3PresetRecall', Zone3PresetRecallCmdString, value, qualifier)


    def SetZone3PresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Z3SMART1 MEMORY\r', 
            '2' : 'Z3SMART2 MEMORY\r', 
            '3' : 'Z3SMART3 MEMORY\r', 
            '4' : 'Z3SMART4 MEMORY\r', 
            '5' : 'Z3SMART5 MEMORY\r'
        }

        Zone3PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3PresetSave', Zone3PresetSaveCmdString, value, qualifier)


    def SetZone3Volume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone3VolumeCmdString = 'Z3{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')
    def SetZone4Input(self, value, qualifier):

        ValueStateValues = {
            'CD'    : 'Z4CD\r', 
            'AUX 3' : 'Z4AUX3\r', 
            'AUX 4' : 'Z4AUX4\r', 
            'AUX 5' : 'Z4AUX5\r', 
            'AUX 6' : 'Z4AUX6\r', 
            'AUX 7' : 'Z4AUX7\r', 
        }

        Zone4InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone4Input', Zone4InputCmdString, value, qualifier)
    def SetZone4Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z4ON\r', 
            'Off' : 'Z4OFF\r'
        }

        Zone4PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone4Power', Zone4PowerCmdString, value, qualifier)
    def UpdateZone4Power(self, value, qualifier):

        Zone4PowerCmdString = 'Z4?\r'
        self.__UpdateHelper('Zone4Power', Zone4PowerCmdString, value, qualifier)

    def __MatchZone4Power(self, match, tag):

        PowerStates = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        InputStates = {
            'CD'   : 'CD', 
            'AUX3' : 'AUX 3', 
            'AUX4' : 'AUX 4', 
            'AUX5' : 'AUX 5', 
            'AUX6' : 'AUX 6', 
            'AUX7' : 'AUX 7', 
        }

        PowerValue = PowerStates[match.group(1).decode()]
        self.WriteStatus('Zone4Power', PowerValue, None)

        InputValue = InputStates[match.group(2).decode()]
        self.WriteStatus('Zone4Input', InputValue, None)

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

        self.__LastChannelUpdate = 0
        

    
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

