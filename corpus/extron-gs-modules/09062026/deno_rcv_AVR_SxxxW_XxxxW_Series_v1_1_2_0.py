from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AVR-X2100W': self.deno_27_975_lessInputs,
            'AVR-S700W': self.deno_27_975_leastInputs_S700W,
            'AVR-S900W': self.deno_27_975_lessInputs,
            'AVR-X1100W': self.deno_27_975_leastInputs_X1100W,
            'AVR-X3100W': self.deno_27_975_lessInputs,
            'AVR-X4100W': self.deno_27_975_mostInputs,
            'AVR-X5200W': self.deno_27_975_allInputs,
            'AVR-X7200W': self.deno_27_975_auxinputs,
            'AVR-X7200WA': self.deno_27_975_auxinputs,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelVolume': {'Parameters': ['Channel'], 'Status': {}},
            'EcoMode': {'Status': {}},
            'Input': {'Status': {}},
            'MainZone': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RemoteLock': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Transport': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3AudioMute': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR|SB|FHL|FHR|FWL|FWR|SW2) ([0-9]{2})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'ECO(ON|OFF|AUTO)\r'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'(?P<zone>Z2|Z3|SI)(?P<input>CD|TUNER|DVD|BD|TV|SAT/CBL|MPLAY|GAME|NET|FLICKR|IRADIO|SERVER|FAVORITES|AUX1|AUX2|USB/IPOD|PANDORA|SIRIUSXM|SPOTIFY|LASTFM|HDRADIO|PHONO|AUX3|AUX4|AUX5|AUX6|AUX7)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZone, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'(?P<zone>Z2MU|Z3MU|MU)(?P<mute>ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MS(MOVIE|MUSIC|GAME|DIRECT|PURE DIRECT|STEREO|AUTO|DOLBY DIGITAL|DTS SURROUND|MCH STEREO|WIDE SCREEN|SUPER STADIUM|ROCK ARENA|JAZZ CLUB|CLASSIC CONCERT|MONO MOVIE|MATRIX|VIDEO GAME|VIRTUAL)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{2})\r'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'Z3(ON|OFF)\r'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'Z3([0-9]{2})\r'), self.__MatchZone3Volume, None)

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'CVFL',
            'Front Right': 'CVFR',
            'Center': 'CVC',
            'Subwoofer': 'CVSW',
            'Subwoofer 2': 'CVSW2',
            'Surround Left': 'CVSL',
            'Surround Right': 'CVSR',
            'Surround Back Left': 'CVSBL',
            'Surround Back Right': 'CVSBR',
            'Front Height Left': 'CVFHL',
            'Front Height Right': 'CVFHR',
            'Front Wide Left': 'CVFWL',
            'Front Wide Right': 'CVFWR'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            valuex = value + 50
            ChannelVolumeCmdString = '{0} {1}\r'.format(ChannelStates[qualifier['Channel']], valuex)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelVolume')

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
             'FHL': 'Front Height Left',
             'FHR': 'Front Height Right',
             'SW2': 'Subwoofer 2',
             'FWL': 'Front Wide Left',
             'FWR': 'Front Wide Right'
        }

        ChannelQual = ChannelStates[match.group(1).decode()]
        qualifier = {'Channel': ChannelQual}
        valuex = int(match.group(2).decode())
        value = valuex - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'ECOON\r',
            'Auto': 'ECOAUTO\r',
            'Off': 'ECOOFF\r'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        EcoModeCmdString = 'ECO?\r'
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'AUTO': 'Auto',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EcoMode', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = 'SI' + self.InputCommand[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'BD': 'Blu-Ray',
            'TV': 'TV',
            'SAT/CBL': 'SAT/CBL',
            'MPLAY': 'Media Player',
            'GAME': 'Game',
            'HDRADIO': 'HD Radio',
            'NET': 'NET',
            'PANDORA': 'Pandora',
            'SIRIUSXM': 'Sirius XM',
            'SPOTIFY': 'Spotify',
            'LASTFM': 'Last FM',
            'FLICKR': 'Flickr',
            'IRADIO': 'iRadio',
            'SERVER': 'Server',
            'FAVORITES': 'Favorites',
            'AUX1': 'Aux 1',
            'AUX2': 'Aux 2',
            'BT': 'Bluetooth',
            'USB/IPOD': 'USB/iPod',
            'PHONO': 'Phono',
            'AUX3': 'Aux 3',
            'AUX4': 'Aux 4',
            'AUX5': 'Aux 5',
            'AUX6': 'Aux 6',
            'AUX7': 'Aux 7'
        }

        input_ = ValueStateValues[match.group('input').decode()]
        zone = match.group('zone').decode()

        if input_ in self.InputCommand.keys():
            if zone == 'SI':
                self.WriteStatus('Input', input_, None)
            elif zone == 'Z2':
                self.WriteStatus('Zone2Input', input_, None)
            elif zone == 'Z3':
                self.WriteStatus('Zone3Input', input_, None)

    def SetMainZone(self, value, qualifier):

        ValueStateValues = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r'
        }

        MainZoneCmdString = ValueStateValues[value]
        self.__SetHelper('MainZone', MainZoneCmdString, value, qualifier)

    def UpdateMainZone(self, value, qualifier):

        MainZoneCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZone', MainZoneCmdString, value, qualifier)

    def __MatchMainZone(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZone', value, None)

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
            print('Invalid Command for SetMasterVolume')

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

        value = ValueStateValues[match.group('mute').decode()]

        zone = match.group('zone').decode()
        if zone == 'MU':
            self.WriteStatus('OutputMute', value, None)
        elif zone == 'Z2MU':
            self.WriteStatus('Zone2AudioMute', value, None)
        elif zone == 'Z3MU':
            self.WriteStatus('Zone3AudioMute', value, None)

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

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': 'NSB01\r',
            '2': 'NSB02\r',
            '3': 'NSB03\r',
            '4': 'NSB04\r',
            '5': 'NSB05\r',
            '6': 'NSB06\r',
            '7': 'NSB07\r',
            '8': 'NSB08\r',
            '9': 'NSB09\r',
            '10': 'NSB10\r',
            '11': 'NSB11\r',
            '12': 'NSB12\r',
            '13': 'NSB13\r',
            '14': 'NSB14\r',
            '15': 'NSB15\r',
            '16': 'NSB16\r',
            '17': 'NSB17\r',
            '18': 'NSB18\r',
            '19': 'NSB19\r',
            '20': 'NSB20\r',
            '21': 'NSB21\r',
            '22': 'NSB22\r',
            '23': 'NSB23\r',
            '24': 'NSB24\r',
            '25': 'NSB25\r',
            '26': 'NSB26\r',
            '27': 'NSB27\r',
            '28': 'NSB28\r',
            '29': 'NSB29\r',
            '30': 'NSB30\r',
            '31': 'NSB31\r',
            '32': 'NSB32\r',
            '33': 'NSB33\r',
            '34': 'NSB34\r',
            '35': 'NSB35\r'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': 'NSC01\r',
            '2': 'NSC02\r',
            '3': 'NSC03\r',
            '4': 'NSC04\r',
            '5': 'NSC05\r',
            '6': 'NSC06\r',
            '7': 'NSC07\r',
            '8': 'NSC08\r',
            '9': 'NSC09\r',
            '10': 'NSC10\r',
            '11': 'NSC11\r',
            '12': 'NSC12\r',
            '13': 'NSC13\r',
            '14': 'NSC14\r',
            '15': 'NSC15\r',
            '16': 'NSC16\r',
            '17': 'NSC17\r',
            '18': 'NSC18\r',
            '19': 'NSC19\r',
            '20': 'NSC20\r',
            '21': 'NSC21\r',
            '22': 'NSC22\r',
            '23': 'NSC23\r',
            '24': 'NSC24\r',
            '25': 'NSC25\r',
            '26': 'NSC26\r',
            '27': 'NSC27\r',
            '28': 'NSC28\r',
            '29': 'NSC29\r',
            '30': 'NSC30\r',
            '31': 'NSC31\r',
            '32': 'NSC32\r',
            '33': 'NSC33\r',
            '34': 'NSC34\r',
            '35': 'NSC35\r'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
        }

        RemoteLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        SurroundModeCmdString = self.SurroundModeCommand[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'VIRTUAL': 'Virtual',
            'MOVIE': 'Movie',
            'MUSIC': 'Music',
            'GAME': 'Game',
            'PURE DIRECT': 'Pure Direct',
            'DIRECT': 'Direct',
            'STEREO': 'Stereo',
            'AUTO': 'Auto',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DTS SURROUND': 'DTS Surround',
            'MCH STEREO': 'Mch Stereo',
            'ROCK ARENA': 'Rock Arena',
            'JAZZ CLUB': 'Jazz Club',
            'MONO MOVIE': 'Mono Movie',
            'MATRIX': 'Matrix',
            'VIDEO GAME': 'Video Game',
            'CLASSIC CONCERT': 'Classic Concert'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '9A',
            'Stop': '9C',
            'Pause': '9B',
            'Skip +': '9D',
            'Skip -': '9E',
            'Next': '9X',
            'Previous': '9Y'
        }

        TransportCmdString = 'NS{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

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

        Zone2InputCmdString = 'Z2' + self.InputCommand[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        self.UpdateZone2Power(value, qualifier)

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
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        self.UpdateZone2Power(value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
        self.WriteStatus('Zone2Volume', value, None)

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

    def SetZone3Input(self, value, qualifier):

        Zone3InputCmdString = 'Z3' + self.InputCommand[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        self.UpdateZone3Power(value, qualifier)

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
            print('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):
        self.UpdateZone3Power(value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        valuex = int(match.group(1).decode())
        value = valuex - 80
        self.WriteStatus('Zone3Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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

    def deno_27_975_auxinputs(self):

        self.InputCommand = {
            'CD'           : 'CD\r', 
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'HD Radio'     : 'HDRADIO\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r', 
            'Aux 2'        : 'AUX2\r', 
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r',
            'Phono'        : 'PHONO\r',
            'Aux 3'        : 'AUX3\r',
            'Aux 4'        : 'AUX4\r',
            'Aux 5'        : 'AUX5\r',
            'Aux 6'        : 'AUX6\r',
            'Aux 7'        : 'AUX7\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r', 
            'Pure Direct'     : 'MSPURE DIRECT\r', 
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }
        
    def deno_27_975_allInputs(self):


        self.InputCommand = {
            'CD'           : 'CD\r', 
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'HD Radio'     : 'HDRADIO\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r', 
            'Aux 2'        : 'AUX2\r', 
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r',
            'Phono'        : 'PHONO\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r', 
            'Pure Direct'     : 'MSPURE DIRECT\r', 
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }

    def deno_27_975_mostInputs(self):

        self.InputCommand = {
            'CD'           : 'CD\r', 
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r', 
            'Aux 2'        : 'AUX2\r', 
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r',
            'Phono'        : 'PHONO\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r', 
            'Pure Direct'     : 'MSPURE DIRECT\r', 
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }

    def deno_27_975_lessInputs(self):


        self.InputCommand = {
            'CD'           : 'CD\r', 
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r', 
            'Aux 2'        : 'AUX2\r', 
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r', 
            'Pure Direct'     : 'MSPURE DIRECT\r', 
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }

    def deno_27_975_leastInputs_X1100W(self):


        self.InputCommand = {
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r',
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r', 
            'Pure Direct'     : 'MSPURE DIRECT\r', 
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }

    def deno_27_975_leastInputs_S700W(self):

        self.InputCommand = {
            'Tuner'        : 'TUNER\r', 
            'DVD'          : 'DVD\r', 
            'Blu-Ray'      : 'BD\r', 
            'TV'           : 'TV\r', 
            'SAT/CBL'      : 'SAT/CBL\r', 
            'Media Player' : 'MPLAY\r', 
            'Game'         : 'GAME\r', 
            'NET'          : 'NET\r', 
            'Pandora'      : 'PANDORA\r', 
            'Sirius XM'    : 'SIRIUSXM\r', 
            'Spotify'      : 'SPOTIFY\r', 
            'Last FM'      : 'LASTFM\r', 
            'Flickr'       : 'FLICKR\r', 
            'iRadio'       : 'IRADIO\r', 
            'Server'       : 'SERVER\r', 
            'Favorites'    : 'FAVORITES\r', 
            'Aux 1'        : 'AUX1\r',
            'Bluetooth'    : 'BT\r', 
            'USB/iPod'     : 'USB/IPOD\r'
        }

        self.SurroundModeCommand = {
            'Virtual'         : 'MSVIRTUAL\r', 
            'Movie'           : 'MSMOVIE\r', 
            'Music'           : 'MSMUSIC\r', 
            'Game'            : 'MSGAME\r',
            'Direct'          : 'MSDIRECT\r', 
            'Stereo'          : 'MSSTEREO\r', 
            'Auto'            : 'MSAUTO\r', 
            'Dolby Digital'   : 'MSDOLBY DIGITAL\r', 
            'DTS Surround'    : 'MSDTS SURROUND\r', 
            'Mch Stereo'      : 'MSMCH STEREO\r', 
            'Rock Arena'      : 'MSROCK ARENA\r', 
            'Jazz Club'       : 'MSJAZZ CLUB\r', 
            'Mono Movie'      : 'MSMONO MOVIE\r', 
            'Matrix'          : 'MSMATRIX\r', 
            'Video Game'      : 'MSVIDEO GAME\r', 
            'Classic Concert' : 'MSCLASSIC CONCERT\r'
        }


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
