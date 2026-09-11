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
        self.Models = {
            'AVR-S730H': self.deno_27_2897_s730h,
            'AVR-S930H': self.deno_27_2897_s930h,
            'AVR-X1400H': self.deno_27_2897_x1400h,
            'AVR-X2400H': self.deno_27_2897_x2400h,
            'AVR-X3400H': self.deno_27_2897_x3400h,
            'AVR-X4400H': self.deno_27_2897_x64x44,
            'AVR-X6400H': self.deno_27_2897_x64x44,
            'AVR-X8500H': self.deno_27_2897_x8500h,
            'AVC-X8500H': self.deno_27_2897_x8500h,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Input': { 'Status': {}},
            'ChannelVolume': {'Parameters':['Channel'], 'Status': {}},
            'EcoMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'MainZone': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SurroundMode': { 'Status': {}},
            'VideoSelect': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zone2': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone2Mute': { 'Status': {}},
            'Zone2Volume': { 'Status': {}},
            'Zone3': { 'Status': {}},
            'Zone3Input': { 'Status': {}},
            'Zone3Mute': { 'Status': {}},
            'Zone3Volume': { 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SI(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|TUNER|AUX[1-7]|NET|BT)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR|SB|FHL|FHR|TFL|TFR|TML|TMR|FDL|FDR|SDL|SDR|ZRL|SW2|TRL|TRR|RHL|RHR|BDL|BDR|SHL|SHR|TS|FWL|FWR|CH) (\d{1,2})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'ECO(ON|OFF|AUTO)\r'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZone, None)
            self.AddMatchString(re.compile(b'(?<!(z|Z)\d)MU(ON|OFF)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PV(OFF|STD|MOV|VVD|STM|CTM|DAY|NGT)\r'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MS(.+)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'SV(DVD|BD|TV|SAT/CBL|MPLAY|GAME|AUX[1-7]|CD|ON|OFF)\r'), self.__MatchVideoSelect, None)
            self.AddMatchString(re.compile(b'MV(\d{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2, None)
            self.AddMatchString(re.compile(b'Z2(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|TUNER|AUX[1-7]|NET|BT)\r'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z2MU(ON|OFF)\r'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'Z2(\d{1,3})\r'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'Z3(ON|OFF)\r'), self.__MatchZone3, None)
            self.AddMatchString(re.compile(b'Z3(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|TUNER|AUX[1-7]|NET|BT)\r'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'Z3MU(ON|OFF)\r'), self.__MatchZone3Mute, None)
            self.AddMatchString(re.compile(b'Z3(\d{1,3})\r'), self.__MatchZone3Volume, None)

    def SetInput(self, value, qualifier):

        if value in self.InputValues:
            InputCmdString = 'SI{0}\r'.format(self.InputValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        try:
            value = self.InputStateValues[match.group(1).decode()]
            self.WriteStatus('Input', value, None)
        except KeyError:
            self.Error(['Input: Invalid/unexpected response'])

    def SetChannelVolume(self, value, qualifier):

        if qualifier['Channel'] in self.ChannelVolumeValues and -12 <= value <= 12:
            ChannelVolumeCmdString = 'CV{0} {1:02d}\r'.format(self.ChannelVolumeValues[qualifier['Channel']], value+50)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):

        if qualifier['Channel'] in self.ChannelVolumeValues:
            ChannelVolumeCmdString = 'CV{0}?\r'.format(self.ChannelVolumeValues[qualifier['Channel']])
            self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelVolume')

    def __MatchChannelVolume(self, match, tag):

        try:
            value = int(match.group(2).decode()) - 50
            self.WriteStatus('ChannelVolume', value, {'Channel': self.ChannelVolumeStateValues[match.group(1).decode()]})
        except KeyError:
            self.Error(['Channel Volume: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'ON', 
            'Off'   : 'OFF', 
            'Auto'  : 'AUTO'
        }

        if value in ValueStateValues:
            EcoModeCmdString = 'ECO{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEcoMode')

    def UpdateEcoMode(self, value, qualifier):

        EcoModeCmdString = 'ECO?\r'
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):

        ValueStateValues = {
            'ON'    : 'On', 
            'OFF'   : 'Off', 
            'AUTO'  : 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EcoMode', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Remote Control Lock On'    : 'REMOTE LOCK ON', 
            'Remote Control Lock Off'   : 'REMOTE LOCK OFF', 
            'Panel Lock With Volume'    : 'PANEL+V LOCK ON', 
            'Panel Lock Without Volume' : 'PANEL LOCK ON', 
            'Off'                       : 'PANEL LOCK OFF'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'SY{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetMainZone(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON',
            'Off' : 'OFF'
        }

        if value in ValueStateValues:
            MainZoneCmdString = 'ZM{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MainZone', MainZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainZone')

    def UpdateMainZone(self, value, qualifier):

        MainZoneCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZone', MainZoneCmdString, value, qualifier)

    def __MatchMainZone(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZone', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Cursor Up'    : 'MNCUP\r',
            'Cursor Down'  : 'MNCDN\r',
            'Cursor Left'  : 'MNCLT\r',
            'Cursor Right' : 'MNCRT\r',
            'Enter'        : 'MNENT\r',
            'Return'       : 'MNRTN\r',
            'Menu On'      : 'MNMEN ON\r',
            'Menu Off'     : 'MNMEN OFF\r'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUON\r',
            'Off' : 'MUOFF\r'
        }

        if value in ValueStateValues:
            MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'MU?\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPictureMode(self, value, qualifier):

        if value in self.PictureModeValues:
            PictureModeCmdString = 'PV{0}\r'.format(self.PictureModeValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'PV?\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        try:
            value = self.PictureModeStateValues[match.group(1).decode()]
            self.WriteStatus('PictureMode', value, None)
        except KeyError:
            self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'      : 'PWON\r',
            'Standby' : 'PWSTANDBY\r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON'      : 'On',
            'STANDBY' : 'Standby'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSurroundMode(self, value, qualifier):

        if value in self.SurroundModeValues:
            SurroundModeCmdString = 'MS{0}\r'.format(self.SurroundModeValues[value])
            self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurroundMode')

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        try:
            value = self.SurroundModeStateValues[match.group(1).decode()]
            self.WriteStatus('SurroundMode', value, None)
        except KeyError:
            self.Error(['Surround Mode: Invalid/unexpected response'])

    def SetVideoSelect(self, value, qualifier):

        if value in self.VideoSelectValues:
            VideoSelectCmdString = 'SV{0}\r'.format(self.VideoSelectValues[value])
            self.__SetHelper('VideoSelect', VideoSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoSelect')

    def UpdateVideoSelect(self, value, qualifier):

        VideoSelectCmdString = 'SV?\r'
        self.__UpdateHelper('VideoSelect', VideoSelectCmdString, value, qualifier)

    def __MatchVideoSelect(self, match, tag):

        try:
            value = self.VideoSelectStateValues[match.group(1).decode()]
            self.WriteStatus('VideoSelect', value, None)
        except KeyError:
            self.Error(['Video Select: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if -80 <= value <= 18:
            if (value * 10) % 10 == 5:
                VolumeCmdString = 'MV{0:03.0f}\r'.format((value + 80) * 10)
            else:
                VolumeCmdString = 'MV{0:02.0f}\r'.format(value + 80)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'MV?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1).decode()
        if len(value) == 3:
            value = round((float(value) / 10) - 80, 1)
        else:
            value = int(value) - 80
        self.WriteStatus('Volume', value, None)

    def SetZone2(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z2ON\r',
            'Off' : 'Z2OFF\r'
        }

        if value in ValueStateValues:
            Zone2CmdString = ValueStateValues[value]
            self.__SetHelper('Zone2', Zone2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2')

    def UpdateZone2(self, value, qualifier):

        Zone2CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2', Zone2CmdString, value, qualifier)

    def __MatchZone2(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2', value, None)

    def SetZone2Input(self, value, qualifier):

        if value in self.InputValues:
            Zone2InputCmdString = 'Z2{0}\r'.format(self.InputValues[value])
            self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Input')

    def UpdateZone2Input(self, value, qualifier):

        self.UpdateZone2(value, qualifier)

    def __MatchZone2Input(self, match, tag):

        try:
            value = self.InputStateValues[match.group(1).decode()]
            self.WriteStatus('Zone2Input', value, None)
        except KeyError:
            self.Error(['Zone 2 Input: Invalid/unexpected response'])

    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Z2MUON\r',
            'Off' : 'Z2MUOFF\r'
        }

        if value in ValueStateValues:
            Zone2MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Mute')

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Volume(self, value, qualifier):

        if -80 <= value <= 18:
            if (value * 10) % 10 == 5:
                Zone2VolumeCmdString = 'Z2{0:03.0f}\r'.format((value + 80) * 10)
            else:
                Zone2VolumeCmdString = 'Z2{0:02.0f}\r'.format(value + 80)

            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        self.UpdateZone2(value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = match.group(1).decode()
        if len(value) == 3:
            value = round((float(value) / 10) - 80, 1)
        else:
            value = int(value) - 80
        self.WriteStatus('Zone2Volume', value, None)

    def SetZone3(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z3ON\r',
            'Off': 'Z3OFF\r'
        }

        if value in ValueStateValues:
            Zone3CmdString = ValueStateValues[value]
            self.__SetHelper('Zone3', Zone3CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3')

    def UpdateZone3(self, value, qualifier):

        Zone3CmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3', Zone3CmdString, value, qualifier)

    def __MatchZone3(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3', value, None)

    def SetZone3Input(self, value, qualifier):

        if value in self.InputValues:
            Zone3InputCmdString = 'Z3{0}\r'.format(self.InputValues[value])
            self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Input')

    def UpdateZone3Input(self, value, qualifier):

        self.UpdateZone3(value, qualifier)

    def __MatchZone3Input(self, match, tag):

        try:
            value = self.InputStateValues[match.group(1).decode()]
            self.WriteStatus('Zone3Input', value, None)
        except KeyError:
            self.Error(['Zone 3 Input: Invalid/unexpected response'])

    def SetZone3Mute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z3MUON\r',
            'Off': 'Z3MUOFF\r'
        }

        if value in ValueStateValues:
            Zone3MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Mute')

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = 'Z3MU?\r'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def __MatchZone3Mute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Mute', value, None)

    def SetZone3Volume(self, value, qualifier):

        if -80 <= value <= 18:
            if (value * 10) % 10 == 5:
                Zone3VolumeCmdString = 'Z3{0:03.0f}\r'.format((value + 80) * 10)
            else:
                Zone3VolumeCmdString = 'Z3{0:02.0f}\r'.format(value + 80)

            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        self.UpdateZone3(value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        value = match.group(1).decode()
        if len(value) == 3:
            value = round((float(value) / 10) - 80, 1)
        else:
            value = int(value) - 80
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
        
    def deno_27_2897_s730h(self):

        self.InputValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux'               : 'AUX1',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'TUNER'     : 'Tuner',
            'AUX1'      : 'Aux',
            'NET'       : 'Network',
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL'
        }

        self.ChannelVolumeStateValues = {
            'FL'  : 'Front Left',
            'FR'  : 'Front Right',
            'C'   : 'Center',
            'SW'  : 'Subwoofer',
            'SL'  : 'Surround Left',
            'SR'  : 'Surround Right',
            'SBL' : 'Surround Back Left',
            'SBR' : 'Surround Back Right',
            'SB'  : 'Surround Back',
            'FHL' : 'Front Height Left',
            'FHR' : 'Front Height Right',
            'TFL' : 'Top Front Left',
            'TFR' : 'Top Front Right',
            'TML' : 'Top Middle Left',
            'TMR' : 'Top Middle Right',
            'FDL' : 'Front Dolby Left',
            'FDR' : 'Front Dolby Right',
            'SDL' : 'Surround Dolby Left',
            'SDR' : 'Surround Dolby Right',
            'ZRL' : 'Reset Levels'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE', 
            'Music' : 'MUSIC', 
            'Game' : 'GAME', 
            'Direct' : 'DIRECT', 
            'Dolby Surround' : 'DOLBY SURROUND', 
            'Dolby Atmos' : 'DOLBY ATMOS', 
            'Dolby Digital' : 'DOLBY DIGITAL', 
            'Dolby D+DS' : 'DOLBY D+DS', 
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X', 
            'DTS Surround' : 'DTS SURROUND', 
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1', 
            'DTS MTRX 6.1' : 'DTS MTRX6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS 96/24' : 'DTS96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'Dolby D+' : 'DOLBY D+', 
            'Dolby D+ +DS' : 'DOLBY D+ +DS',
            'Dolby HD+DS' : 'DOLBY HD+DS',
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X', 
            'DTS HD' : 'DTS HD',
            'DTS HD Master' : 'DTS HD MSTR',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X Master' : 'DTS:X MSTR',
            'DTS Express' : 'DTS EXPRESS',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA',
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE',
            'Matrix' : 'MATRIX',
            'Video Game' : 'VIDEO GAME',
            'Virtual' : 'VIRTUAL',
            'Left' : 'LEFT',
            'Right' : 'RIGHT',
            'All Zone Stereo' : 'ALL ZONE STEREO',
            'Auto' : 'AUTO',
            'Stereo': 'STEREO'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie', 
            'MUSIC' : 'Music', 
            'GAME' : 'Game', 
            'DIRECT' : 'Direct', 
            'DOLBY SURROUND' : 'Dolby Surround', 
            'DOLBY ATMOS' : 'Dolby Atmos', 
            'DOLBY DIGITAL' : 'Dolby Digital', 
            'DOLBY D+DS' : 'Dolby D+DS', 
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural', 
            'DTS SURROUND' : 'DTS Surround', 
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1', 
            'DTS MTRX6.1' : 'DTS MTRX 6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS96/24' : 'DTS 96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'DOLBY D+' : 'Dolby D+', 
            'DOLBY D+ +DS' : 'Dolby D+ +DS', 
            'DOLBY HD+DS' : 'Dolby HD+DS', 
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD MSTR' : 'DTS HD Master', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X MSTR' : 'DTS:X Master', 
            'DTS EXPRESS' : 'DTS Express', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT', 
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena', 
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie', 
            'MATRIX' : 'Matrix', 
            'VIDEO GAME' : 'Video Game', 
            'VIRTUAL' : 'Virtual', 
            'LEFT' : 'Left', 
            'RIGHT' : 'Right', 
            'ALL ZONE STEREO' : 'All Zone Stereo', 
            'AUTO' : 'Auto',
            'STEREO': 'Stereo'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux'               : 'AUX1',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_s930h(self):

        self.InputValues = {
            'CD'                : 'CD',
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'CD'        : 'CD', 
            'DVD'       : 'DVD', 
            'BD'        : 'BD', 
            'TV'        : 'TV', 
            'SAT/CBL'   : 'Satellite/Cable', 
            'MPLAY'     : 'Media Player', 
            'GAME'      : 'Game', 
            'TUNER'     : 'Tuner', 
            'AUX1'      : 'Aux 1', 
            'AUX2'      : 'Aux 2', 
            'NET'       : 'Network', 
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels'
        }

        self.PictureModeValues = {
            'Off'       : 'OFF', 
            'Standard'  : 'STD', 
            'Movie'     : 'MOV', 
            'Vivid'     : 'VVD', 
            'Stream'    : 'STM', 
            'Custom'    : 'CTM'
        }

        self.PictureModeStateValues = {
            'OFF' : 'Off', 
            'STD' : 'Standard', 
            'MOV' : 'Movie', 
            'VVD' : 'Vivid', 
            'STM' : 'Stream', 
            'CTM' : 'Custom'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE', 
            'Music' : 'MUSIC', 
            'Game' : 'GAME', 
            'Direct' : 'DIRECT', 
            'Pure Direct' : 'PURE DIRECT', 
            'Dolby Surround' : 'DOLBY SURROUND', 
            'Dolby Atmos' : 'DOLBY ATMOS', 
            'Dolby Digital' : 'DOLBY DIGITAL', 
            'Dolby D+DS' : 'DOLBY D+DS', 
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X', 
            'DTS Surround' : 'DTS SURROUND', 
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1', 
            'DTS MTRX 6.1' : 'DTS MTRX6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS 96/24' : 'DTS96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'Dolby D+' : 'DOLBY D+', 
            'Dolby D+ +DS' : 'DOLBY D+ +DS', 
            'Dolby HD+DS' : 'DOLBY HD+DS', 
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD Master' : 'DTS HD MSTR', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X Master' : 'DTS:X MSTR', 
            'DTS Express' : 'DTS EXPRESS', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT', 
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA', 
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE', 
            'Matrix' : 'MATRIX', 
            'Video Game' : 'VIDEO GAME', 
            'Virtual' : 'VIRTUAL', 
            'Left' : 'LEFT', 
            'Right' : 'RIGHT', 
            'All Zone Stereo' : 'ALL ZONE STEREO', 
            'Auto' : 'AUTO',
            'Stereo': 'STEREO'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie', 
            'MUSIC' : 'Music', 
            'GAME' : 'Game', 
            'DIRECT' : 'Direct', 
            'PURE DIRECT' : 'Pure Direct', 
            'DOLBY SURROUND' : 'Dolby Surround', 
            'DOLBY ATMOS' : 'Dolby Atmos', 
            'DOLBY DIGITAL' : 'Dolby Digital', 
            'DOLBY D+DS' : 'Dolby D+DS', 
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural', 
            'DTS SURROUND' : 'DTS Surround', 
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1', 
            'DTS MTRX6.1' : 'DTS MTRX 6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS96/24' : 'DTS 96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'DOLBY D+' : 'Dolby D+', 
            'DOLBY D+ +DS' : 'Dolby D+ +DS', 
            'DOLBY HD+DS' : 'Dolby HD+DS', 
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD MSTR' : 'DTS HD Master', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X MSTR' : 'DTS:X Master', 
            'DTS EXPRESS' : 'DTS Express', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT', 
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena', 
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie', 
            'MATRIX' : 'Matrix', 
            'VIDEO GAME' : 'Video Game', 
            'VIRTUAL' : 'Virtual', 
            'LEFT' : 'Left', 
            'RIGHT' : 'Right', 
            'ALL ZONE STEREO' : 'All Zone Stereo', 
            'AUTO' : 'Auto',
            'STEREO': 'Stereo'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'CD'                : 'CD',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'CD'        : 'CD',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_x1400h(self):

        self.InputValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux'               : 'AUX1',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'TUNER'     : 'Tuner',
            'AUX1'      : 'Aux',
            'NET'       : 'Network',
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE', 
            'Music' : 'MUSIC', 
            'Game' : 'GAME', 
            'Direct' : 'DIRECT', 
            'Pure Direct' : 'PURE DIRECT', 
            'Dolby Surround' : 'DOLBY SURROUND', 
            'Dolby Atmos' : 'DOLBY ATMOS', 
            'Dolby Digital' : 'DOLBY DIGITAL', 
            'Dolby D+DS' : 'DOLBY D+DS', 
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X', 
            'DTS Surround' : 'DTS SURROUND', 
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1', 
            'DTS MTRX 6.1' : 'DTS MTRX6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS 96/24' : 'DTS96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'Dolby D+' : 'DOLBY D+', 
            'Dolby D+ +DS' : 'DOLBY D+ +DS', 
            'Dolby HD+DS' : 'DOLBY HD+DS', 
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD Master' : 'DTS HD MSTR', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X Master' : 'DTS:X MSTR', 
            'DTS Express' : 'DTS EXPRESS', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA', 
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE', 
            'Matrix' : 'MATRIX', 
            'Video Game' : 'VIDEO GAME', 
            'Virtual' : 'VIRTUAL', 
            'Left' : 'LEFT', 
            'Right' : 'RIGHT', 
            'All Zone Stereo' : 'ALL ZONE STEREO', 
            'Auto' : 'AUTO',
            'Stereo': 'STEREO'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie', 
            'MUSIC' : 'Music', 
            'GAME' : 'Game', 
            'DIRECT' : 'Direct', 
            'PURE DIRECT' : 'Pure Direct', 
            'DOLBY SURROUND' : 'Dolby Surround', 
            'DOLBY ATMOS' : 'Dolby Atmos', 
            'DOLBY DIGITAL' : 'Dolby Digital', 
            'DOLBY D+DS' : 'Dolby D+DS', 
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural', 
            'DTS SURROUND' : 'DTS Surround', 
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1', 
            'DTS MTRX6.1' : 'DTS MTRX 6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS96/24' : 'DTS 96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'DOLBY D+' : 'Dolby D+', 
            'DOLBY D+ +DS' : 'Dolby D+ +DS', 
            'DOLBY HD+DS' : 'Dolby HD+DS', 
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD MSTR' : 'DTS HD Master', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X MSTR' : 'DTS:X Master', 
            'DTS EXPRESS' : 'DTS Express', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena', 
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie', 
            'MATRIX' : 'Matrix', 
            'VIDEO GAME' : 'Video Game', 
            'VIRTUAL' : 'Virtual', 
            'LEFT' : 'Left', 
            'RIGHT' : 'Right', 
            'ALL ZONE STEREO' : 'All Zone Stereo', 
            'AUTO' : 'Auto',
            'STEREO': 'Stereo'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux'               : 'AUX1',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_x2400h(self):

        self.InputValues = {
            'CD'                : 'CD',
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'CD'        : 'CD', 
            'DVD'       : 'DVD', 
            'BD'        : 'BD', 
            'TV'        : 'TV', 
            'SAT/CBL'   : 'Satellite/Cable', 
            'MPLAY'     : 'Media Player', 
            'GAME'      : 'Game', 
            'TUNER'     : 'Tuner', 
            'AUX1'      : 'Aux 1', 
            'AUX2'      : 'Aux 2', 
            'NET'       : 'Network', 
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels'
        }

        self.PictureModeValues = {
            'Off'       : 'OFF', 
            'Standard'  : 'STD', 
            'Movie'     : 'MOV', 
            'Vivid'     : 'VVD', 
            'Stream'    : 'STM', 
            'Custom'    : 'CTM', 
            'ISF Day'   : 'DAY', 
            'ISF Night' : 'NGT'
        }

        self.PictureModeStateValues = {
            'OFF' : 'Off', 
            'STD' : 'Standard', 
            'MOV' : 'Movie', 
            'VVD' : 'Vivid', 
            'STM' : 'Stream', 
            'CTM' : 'Custom', 
            'DAY' : 'ISF Day', 
            'NGT' : 'ISF Night'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE', 
            'Music' : 'MUSIC', 
            'Game' : 'GAME', 
            'Direct' : 'DIRECT', 
            'Pure Direct' : 'PURE DIRECT', 
            'Dolby Surround' : 'DOLBY SURROUND', 
            'Dolby Atmos' : 'DOLBY ATMOS', 
            'Dolby Digital' : 'DOLBY DIGITAL', 
            'Dolby D+DS' : 'DOLBY D+DS', 
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X', 
            'DTS Surround' : 'DTS SURROUND', 
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1', 
            'DTS MTRX 6.1' : 'DTS MTRX6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS 96/24' : 'DTS96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'Dolby D+' : 'DOLBY D+', 
            'Dolby D+ +DS' : 'DOLBY D+ +DS', 
            'Dolby HD+DS' : 'DOLBY HD+DS', 
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD Master' : 'DTS HD MSTR', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X Master' : 'DTS:X MSTR', 
            'DTS Express' : 'DTS EXPRESS', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA', 
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE', 
            'Matrix' : 'MATRIX', 
            'Video Game' : 'VIDEO GAME', 
            'Virtual' : 'VIRTUAL', 
            'Left' : 'LEFT', 
            'Right' : 'RIGHT', 
            'All Zone Stereo' : 'ALL ZONE STEREO', 
            'Auto' : 'AUTO',
            'Stereo': 'STEREO'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie', 
            'MUSIC' : 'Music', 
            'GAME' : 'Game', 
            'DIRECT' : 'Direct', 
            'PURE DIRECT' : 'Pure Direct', 
            'DOLBY SURROUND' : 'Dolby Surround', 
            'DOLBY ATMOS' : 'Dolby Atmos', 
            'DOLBY DIGITAL' : 'Dolby Digital', 
            'DOLBY D+DS' : 'Dolby D+DS', 
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural', 
            'DTS SURROUND' : 'DTS Surround', 
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1', 
            'DTS MTRX6.1' : 'DTS MTRX 6.1', 
            'DTS+DS' : 'DTS+DS', 
            'DTS96/24' : 'DTS 96/24', 
            'DTS+NEURAL:X' : 'DTS+NEURAL:X', 
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X', 
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X', 
            'M CH IN+DS' : 'M CH IN+DS', 
            'M CH IN+NEURAL' : 'M CH IN+NEURAL', 
            'DOLBY D+' : 'Dolby D+', 
            'DOLBY D+ +DS' : 'Dolby D+ +DS', 
            'DOLBY HD+DS' : 'Dolby HD+DS', 
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X', 
            'DTS HD' : 'DTS HD', 
            'DTS HD MSTR' : 'DTS HD Master', 
            'DTS HD+DS' : 'DTS HD+DS', 
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X', 
            'DTS:X' : 'DTS:X', 
            'DTS:X MSTR' : 'DTS:X Master', 
            'DTS EXPRESS' : 'DTS Express', 
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena', 
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie', 
            'MATRIX' : 'Matrix', 
            'VIDEO GAME' : 'Video Game', 
            'VIRTUAL' : 'Virtual', 
            'LEFT' : 'Left', 
            'RIGHT' : 'Right', 
            'ALL ZONE STEREO' : 'All Zone Stereo', 
            'AUTO' : 'Auto',
            'STEREO': 'Stereo'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'CD'                : 'CD',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'CD'        : 'CD',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_x3400h(self):

        self.InputValues = {
            'CD'                : 'CD',
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'CD'        : 'CD',
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'TUNER'     : 'Tuner',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'NET'       : 'Network',
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL',
            'Subwoofer 2' : 'SW2'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels',
            'SW2' : 'Subwoofer 2'
        }

        self.PictureModeValues = {
            'Off'       : 'OFF',
            'Standard'  : 'STD',
            'Movie'     : 'MOV',
            'Vivid'     : 'VVD',
            'Stream'    : 'STM',
            'Custom'    : 'CTM',
            'ISF Day'   : 'DAY',
            'ISF Night' : 'NGT'
        }

        self.PictureModeStateValues = {
            'OFF' : 'Off',
            'STD' : 'Standard',
            'MOV' : 'Movie',
            'VVD' : 'Vivid',
            'STM' : 'Stream',
            'CTM' : 'Custom',
            'DAY' : 'ISF Day',
            'NGT' : 'ISF Night'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE',
            'Music' : 'MUSIC',
            'Game' : 'GAME',
            'Direct' : 'DIRECT',
            'Pure Direct' : 'PURE DIRECT',
            'Dolby Surround' : 'DOLBY SURROUND',
            'Dolby Atmos' : 'DOLBY ATMOS',
            'Dolby Digital' : 'DOLBY DIGITAL',
            'Dolby D+DS' : 'DOLBY D+DS',
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X',
            'DTS Surround' : 'DTS SURROUND',
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1',
            'DTS MTRX 6.1' : 'DTS MTRX6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS 96/24' : 'DTS96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'Dolby D+' : 'DOLBY D+',
            'Dolby D+ +DS' : 'DOLBY D+ +DS',
            'Dolby HD+DS' : 'DOLBY HD+DS',
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD Master' : 'DTS HD MSTR',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X Master' : 'DTS:X MSTR',
            'DTS Express' : 'DTS EXPRESS',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA',
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE',
            'Matrix' : 'MATRIX',
            'Video Game' : 'VIDEO GAME',
            'Virtual' : 'VIRTUAL',
            'Left' : 'LEFT',
            'Right' : 'RIGHT',
            'All Zone Stereo' : 'ALL ZONE STEREO',
            'Auto' : 'AUTO',
            'Stereo' : 'STEREO'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie',
            'MUSIC' : 'Music',
            'GAME' : 'Game',
            'DIRECT' : 'Direct',
            'PURE DIRECT' : 'Pure Direct',
            'DOLBY SURROUND' : 'Dolby Surround',
            'DOLBY ATMOS' : 'Dolby Atmos',
            'DOLBY DIGITAL' : 'Dolby Digital',
            'DOLBY D+DS' : 'Dolby D+DS',
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural',
            'DTS SURROUND' : 'DTS Surround',
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1',
            'DTS MTRX6.1' : 'DTS MTRX 6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS96/24' : 'DTS 96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'DOLBY D+' : 'Dolby D+',
            'DOLBY D+ +DS' : 'Dolby D+ +DS',
            'DOLBY HD+DS' : 'Dolby HD+DS',
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD MSTR' : 'DTS HD Master',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X MSTR' : 'DTS:X Master',
            'DTS EXPRESS' : 'DTS Express',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena',
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie',
            'MATRIX' : 'Matrix',
            'VIDEO GAME' : 'Video Game',
            'VIRTUAL' : 'Virtual',
            'LEFT' : 'Left',
            'RIGHT' : 'Right',
            'ALL ZONE STEREO' : 'All Zone Stereo',
            'AUTO' : 'Auto',
            'STEREO' : 'Stereo'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'CD'                : 'CD',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'CD'        : 'CD',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_x64x44(self):

        self.InputValues = {
            'Phono'             : 'PHONO',
            'CD'                : 'CD',
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'TUNER'     : 'Tuner',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'NET'       : 'Network',
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL',
            'Subwoofer 2' : 'SW2',
            'Top Rear Left' : 'TRL',
            'Top Rear Right' : 'TRR',
            'Rear Height Left' : 'RHL',
            'Rear Height Right' : 'RHR',
            'Back Dolby Left' : 'BDL',
            'Back Dolby Right' : 'BDR',
            'Surround Height Left' : 'SHL',
            'Surround Height Right' : 'SHR',
            'Top Surround' : 'TS'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels',
            'SW2' : 'Subwoofer 2',
            'TRL' : 'Top Rear Left',
            'TRR' : 'Top Rear Right',
            'RHL' : 'Rear Height Left',
            'RHR' : 'Rear Height Right',
            'BDL' : 'Back Dolby Left',
            'BDR' : 'Back Dolby Right',
            'SHL' : 'Surround Height Left',
            'SHR' : 'Surround Height Right',
            'TS' : 'Top Surround'
        }

        self.PictureModeValues = {
            'Off'       : 'OFF',
            'Standard'  : 'STD',
            'Movie'     : 'MOV',
            'Vivid'     : 'VVD',
            'Stream'    : 'STM',
            'Custom'    : 'CTM',
            'ISF Day'   : 'DAY',
            'ISF Night' : 'NGT'
        }

        self.PictureModeStateValues = {
            'OFF' : 'Off',
            'STD' : 'Standard',
            'MOV' : 'Movie',
            'VVD' : 'Vivid',
            'STM' : 'Stream',
            'CTM' : 'Custom',
            'DAY' : 'ISF Day',
            'NGT' : 'ISF Night'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE',
            'Music' : 'MUSIC',
            'Game' : 'GAME',
            'Direct' : 'DIRECT',
            'Pure Direct' : 'PURE DIRECT',
            'Dolby Surround' : 'DOLBY SURROUND',
            'Dolby Atmos' : 'DOLBY ATMOS',
            'Dolby Digital' : 'DOLBY DIGITAL',
            'Dolby D+DS' : 'DOLBY D+DS',
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X',
            'DTS Surround' : 'DTS SURROUND',
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1',
            'DTS MTRX 6.1' : 'DTS MTRX6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS 96/24' : 'DTS96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'Dolby D+' : 'DOLBY D+',
            'Dolby D+ +DS' : 'DOLBY D+ +DS',
            'Dolby HD+DS' : 'DOLBY HD+DS',
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD Master' : 'DTS HD MSTR',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X Master' : 'DTS:X MSTR',
            'DTS Express' : 'DTS EXPRESS',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA',
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE',
            'Matrix' : 'MATRIX',
            'Video Game' : 'VIDEO GAME',
            'Virtual' : 'VIRTUAL',
            'Left' : 'LEFT',
            'Right' : 'RIGHT',
            'All Zone Stereo' : 'ALL ZONE STEREO',
            'Auto' : 'AUTO',
            'Stereo' : 'STEREO',
            'Auro 3D': 'AURO3D',
            'Auro 2D Surround': 'AURO2DSURR'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie',
            'MUSIC' : 'Music',
            'GAME' : 'Game',
            'DIRECT' : 'Direct',
            'PURE DIRECT' : 'Pure Direct',
            'DOLBY SURROUND' : 'Dolby Surround',
            'DOLBY ATMOS' : 'Dolby Atmos',
            'DOLBY DIGITAL' : 'Dolby Digital',
            'DOLBY D+DS' : 'Dolby D+DS',
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural',
            'DTS SURROUND' : 'DTS Surround',
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1',
            'DTS MTRX6.1' : 'DTS MTRX 6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS96/24' : 'DTS 96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'DOLBY D+' : 'Dolby D+',
            'DOLBY D+ +DS' : 'Dolby D+ +DS',
            'DOLBY HD+DS' : 'Dolby HD+DS',
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD MSTR' : 'DTS HD Master',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X MSTR' : 'DTS:X Master',
            'DTS EXPRESS' : 'DTS Express',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena',
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie',
            'MATRIX' : 'Matrix',
            'VIDEO GAME' : 'Video Game',
            'VIRTUAL' : 'Virtual',
            'LEFT' : 'Left',
            'RIGHT' : 'Right',
            'ALL ZONE STEREO' : 'All Zone Stereo',
            'AUTO' : 'Auto',
            'STEREO' : 'Stereo',
            'AURO3D': 'Auro 3D',
            'AURO2DSURR': 'Auro 2D Surround'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'CD'                : 'CD',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'CD'        : 'CD',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }

    def deno_27_2897_x8500h(self):

        self.InputValues = {
            'Phono'             : 'PHONO',
            'CD'                : 'CD',
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Tuner'             : 'TUNER',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Aux 3'             : 'AUX3',
            'Aux 4'             : 'AUX4',
            'Aux 5'             : 'AUX5',
            'Aux 6'             : 'AUX6',
            'Aux 7'             : 'AUX7',
            'Network'           : 'NET',
            'Bluetooth'         : 'BT'
        }

        self.InputStateValues = {
            'PHONO'     : 'Phono',
            'CD'        : 'CD',
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'TUNER'     : 'Tuner',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'AUX3'      : 'Aux 3',
            'AUX4'      : 'Aux 4',
            'AUX5'      : 'Aux 5',
            'AUX6'      : 'Aux 6',
            'AUX7'      : 'Aux 7',
            'NET'       : 'Network',
            'BT'        : 'Bluetooth'
        }

        self.ChannelVolumeValues = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Surround Back': 'SB',
            'Front Height Left': 'FHL',
            'Front Height Right': 'FHR',
            'Top Front Left': 'TFL',
            'Top Front Right': 'TFR',
            'Top Middle Left': 'TML',
            'Top Middle Right': 'TMR',
            'Front Dolby Left': 'FDL',
            'Front Dolby Right': 'FDR',
            'Surround Dolby Left': 'SDL',
            'Surround Dolby Right': 'SDR',
            'Reset Levels': 'ZRL',
            'Subwoofer 2' : 'SW2',
            'Top Rear Left' : 'TRL',
            'Top Rear Right' : 'TRR',
            'Rear Height Left' : 'RHL',
            'Rear Height Right' : 'RHR',
            'Back Dolby Left' : 'BDL',
            'Back Dolby Right' : 'BDR',
            'Surround Height Left' : 'SHL',
            'Surround Height Right' : 'SHR',
            'Top Surround' : 'TS',
            'Front Wide Left' : 'FWL',
            'Front Wide Right': 'FWR',
            'Center Height': 'CH'
        }

        self.ChannelVolumeStateValues = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back',
            'FHL': 'Front Height Left',
            'FHR': 'Front Height Right',
            'TFL': 'Top Front Left',
            'TFR': 'Top Front Right',
            'TML': 'Top Middle Left',
            'TMR': 'Top Middle Right',
            'FDL': 'Front Dolby Left',
            'FDR': 'Front Dolby Right',
            'SDL': 'Surround Dolby Left',
            'SDR': 'Surround Dolby Right',
            'ZRL': 'Reset Levels',
            'SW2' : 'Subwoofer 2',
            'TRL' : 'Top Rear Left',
            'TRR' : 'Top Rear Right',
            'RHL' : 'Rear Height Left',
            'RHR' : 'Rear Height Right',
            'BDL' : 'Back Dolby Left',
            'BDR' : 'Back Dolby Right',
            'SHL' : 'Surround Height Left',
            'SHR' : 'Surround Height Right',
            'TS' : 'Top Surround',
            'FWL' : 'Front Wide Left',
            'FWR' : 'Front Wide Right',
            'CH' : 'Center Height'
        }

        self.PictureModeValues = {
            'Off'       : 'OFF',
            'Standard'  : 'STD',
            'Movie'     : 'MOV',
            'Vivid'     : 'VVD',
            'Stream'    : 'STM',
            'Custom'    : 'CTM',
            'ISF Day'   : 'DAY',
            'ISF Night' : 'NGT'
        }

        self.PictureModeStateValues = {
            'OFF' : 'Off',
            'STD' : 'Standard',
            'MOV' : 'Movie',
            'VVD' : 'Vivid',
            'STM' : 'Stream',
            'CTM' : 'Custom',
            'DAY' : 'ISF Day',
            'NGT' : 'ISF Night'
        }

        self.SurroundModeValues = {
            'Movie' : 'MOVIE',
            'Music' : 'MUSIC',
            'Game' : 'GAME',
            'Direct' : 'DIRECT',
            'Pure Direct' : 'PURE DIRECT',
            'Dolby Surround' : 'DOLBY SURROUND',
            'Dolby Atmos' : 'DOLBY ATMOS',
            'Dolby Digital' : 'DOLBY DIGITAL',
            'Dolby D+DS' : 'DOLBY D+DS',
            'Dolby D+Neural' : 'DOLBY D+NEURAL:X',
            'DTS Surround' : 'DTS SURROUND',
            'DTS DSCRT 6.1' : 'DTS DSCRT6.1',
            'DTS MTRX 6.1' : 'DTS MTRX6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS 96/24' : 'DTS96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS+VIRTUAL:X': 'DTS+VIRTUAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'M CH IN+VIRTUAL:X': 'M CH IN+VIRTUAL:X',
            'Dolby D+' : 'DOLBY D+',
            'Dolby D+ +DS' : 'DOLBY D+ +DS',
            'Dolby HD+DS' : 'DOLBY HD+DS',
            'Dolby HD+NEURAL:X' : 'DOLBY HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD Master' : 'DTS HD MSTR',
            'DTS:X+VIRTUAL:X': 'DTS:X+VIRTUAL:X',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS HD+VIRTUAL:X': 'DTS HD+VIRTUAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X Master' : 'DTS:X MSTR',
            'DTS Express' : 'DTS EXPRESS',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH Stereo' : 'MCH STEREO',
            'Rock Arena' : 'ROCK ARENA',
            'Jazz Club' : 'JAZZ CLUB',
            'Mono Movie' : 'MONO MOVIE',
            'Matrix' : 'MATRIX',
            'Video Game' : 'VIDEO GAME',
            'Virtual' : 'VIRTUAL',
            'Left' : 'LEFT',
            'Right' : 'RIGHT',
            'All Zone Stereo' : 'ALL ZONE STEREO',
            'Auto' : 'AUTO',
            'Stereo' : 'STEREO',
            'Auro 3D': 'AURO3D',
            'Auro 2D Surround': 'AURO2DSURR'
        }

        self.SurroundModeStateValues = {
            'MOVIE' : 'Movie',
            'MUSIC' : 'Music',
            'GAME' : 'Game',
            'DIRECT' : 'Direct',
            'PURE DIRECT' : 'Pure Direct',
            'DOLBY SURROUND' : 'Dolby Surround',
            'DOLBY ATMOS' : 'Dolby Atmos',
            'DOLBY DIGITAL' : 'Dolby Digital',
            'DOLBY D+DS' : 'Dolby D+DS',
            'DOLBY D+NEURAL:X' : 'Dolby D+Neural',
            'DTS SURROUND' : 'DTS Surround',
            'DTS DSCRT6.1' : 'DTS DSCRT 6.1',
            'DTS MTRX6.1' : 'DTS MTRX 6.1',
            'DTS+DS' : 'DTS+DS',
            'DTS96/24' : 'DTS 96/24',
            'DTS+NEURAL:X' : 'DTS+NEURAL:X',
            'DTS+VIRTUAL:X' : 'DTS+VIRTUAL:X',
            'DTS ES MTRX+NEURAL:X' : 'DTS ES MTRX+NEURAL:X',
            'DTS ES DSCRT+NEURAL:X' : 'DTS ES DSCRT+NEURAL:X',
            'M CH IN+DS' : 'M CH IN+DS',
            'M CH IN+NEURAL' : 'M CH IN+NEURAL',
            'M CH IN+VIRTUAL:X' : 'M CH IN+VIRTUAL:X',
            'DOLBY D+' : 'Dolby D+',
            'DOLBY D+ +DS' : 'Dolby D+ +DS',
            'DOLBY HD+DS' : 'Dolby HD+DS',
            'DOLBY HD+NEURAL:X' : 'Dolby HD+NEURAL:X',
            'DTS HD' : 'DTS HD',
            'DTS HD MSTR' : 'DTS HD Master',
            'DTS HD+DS' : 'DTS HD+DS',
            'DTS HD+NEURAL:X' : 'DTS HD+NEURAL:X',
            'DTS HD+VIRTUAL:X': 'DTS HD+VIRTUAL:X',
            'DTS:X' : 'DTS:X',
            'DTS:X MSTR' : 'DTS:X Master',
            'DTS:X+VIRTUAL:X' : 'DTS:X+VIRTUAL:X',
            'DTS EXPRESS' : 'DTS Express',
            'DTS ES 8CH DSCRT' : 'DTS ES 8CH DSCRT',
            'MCH STEREO' : 'MCH Stereo',
            'ROCK ARENA' : 'Rock Arena',
            'JAZZ CLUB' : 'Jazz Club',
            'MONO MOVIE' : 'Mono Movie',
            'MATRIX' : 'Matrix',
            'VIDEO GAME' : 'Video Game',
            'VIRTUAL' : 'Virtual',
            'LEFT' : 'Left',
            'RIGHT' : 'Right',
            'ALL ZONE STEREO' : 'All Zone Stereo',
            'AUTO' : 'Auto',
            'STEREO' : 'Stereo',
            'AURO3D': 'Auro 3D',
            'AURO2DSURR': 'Auro 2D Surround'
        }

        self.VideoSelectValues = {
            'DVD'               : 'DVD',
            'BD'                : 'BD',
            'TV'                : 'TV',
            'Satellite/Cable'   : 'SAT/CBL',
            'Media Player'      : 'MPLAY',
            'Game'              : 'GAME',
            'Aux 1'             : 'AUX1',
            'Aux 2'             : 'AUX2',
            'Aux 3'             : 'AUX3',
            'Aux 4'             : 'AUX4',
            'Aux 5'             : 'AUX5',
            'Aux 6'             : 'AUX6',
            'Aux 7'             : 'AUX7',
            'CD'                : 'CD',
            'On'                : 'ON',
            'Off'               : 'OFF'
        }

        self.VideoSelectStateValues = {
            'DVD'       : 'DVD',
            'BD'        : 'BD',
            'TV'        : 'TV',
            'SAT/CBL'   : 'Satellite/Cable',
            'MPLAY'     : 'Media Player',
            'GAME'      : 'Game',
            'AUX1'      : 'Aux 1',
            'AUX2'      : 'Aux 2',
            'AUX3'      : 'Aux 3',
            'AUX4'      : 'Aux 4',
            'AUX5'      : 'Aux 5',
            'AUX6'      : 'Aux 6',
            'AUX7'      : 'Aux 7',
            'CD'        : 'CD',
            'ON'        : 'On',
            'OFF'       : 'Off'
        }
        
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