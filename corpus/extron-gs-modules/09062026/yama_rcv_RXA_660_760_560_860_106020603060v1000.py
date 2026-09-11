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
            'RX-A660': self.yama_27_2766_660,
            'RX-A760': self.yama_27_2766_760,
            'RX-A3060': self.yama_27_2766_23_060,
            'RX-A860': self.yama_27_2766_860,
            'RX-A1060': self.yama_27_2766_1060,
            'RX-A2060': self.yama_27_2766_23_060,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AM': {'Status': {}},
            'Bass': {'Status': {}},
            'Decoder': {'Status': {}},
            'FM': {'Status': {}},
            'Input': {'Status': {}},
            'MainZoneTransport': {'Status': {}},
            'MainZoneVolume': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Menu': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Power': {'Status': {}},
            'PureDirect': {'Status': {}},
            'Scene': {'Status': {}},
            'Straight': {'Status': {}},
            'Surround': {'Status': {}},
            'Treble': {'Status': {}},
            'TunerBand': {'Status': {}},
            'TunerPreset': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Transport': {'Status': {}},
            'Zone2Volume': {'Status': {}}
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@MAIN:TONEBASS=(-?\d\.\d)\r\n'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'@MAIN:DECODERSEL=(DTS|Auto|Unavailable)\r\n'), self.__MatchDecoder, None)
            self.AddMatchString(re.compile(b'@MAIN:INP=(NET RADIO|PHONO|TUNER|MULTI CH|HDMI1|HDMI2|HDMI3|HDMI4|HDMI5|HDMI6|HDMI7|AV1|AV2|AV3|AV4|AV5|AV6|AV7|V-AUX|AUDIO1|AUDIO2|AUDIO3|AUDIO4|NET|Napster|Spotify|SERVER|USB|iPod\(USB\)|AirPlay)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'@MAIN:VOL=(-?\d{1,2}\.\d)\r\n'), self.__MatchMainZoneVolume, None)
            self.AddMatchString(re.compile(b'@MAIN:MUTE=(On|Off)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'@MAIN:PWR=(On|Standby)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'@MAIN:PUREDIRMODE=(On|Off)\r\n'), self.__MatchPureDirect, None)
            self.AddMatchString(re.compile(b'@MAIN:STRAIGHT=(On|Off)\r\n'), self.__MatchStraight, None)
            self.AddMatchString(re.compile(b'@MAIN:SOUNDPRG=(Action Game|Hall in Munich|Hall in Vienna|Hall in Amsterdam|Church in Freiburg|Church in Royaumont|Village Vanguard|Warehouse Loft|Chamber|Cellar Club|The Roxy Theatre|The Bottom Line|Sports|Surround Decoder|Roleplaying Game|Music Video|Standard|Spectacle|Sci-Fi|Adventure|Drama|Mono Movie|2ch Stereo|7ch Stereo|9ch Stereo|Recital/Opera)\r\n'), self.__MatchSurround, None)
            self.AddMatchString(re.compile(b'@MAIN:TONETREBLE=(-?\d\.\d)\r\n'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'@TUN:BAND=(AM|FM)\r\n'), self.__MatchTunerBand, None)
            self.AddMatchString(re.compile(b'@TUN:PRESET=([0-4]?[0-9])\r\n'), self.__MatchTunerPreset, None)
            self.AddMatchString(re.compile(b'@ZONE2:MUTE=(On|Off)\r\n'), self.__MatchZone2AudioMute, None)
            self.AddMatchString(re.compile(b'@ZONE2:INP=(NET RADIO|PHONO|TUNER|AV1|AV2|AV3|AV4|AV5|AV6|AV7|V-AUX|AUDIO1|AUDIO2|AUDIO3|AUDIO4|Napster|Spotify|SERVER|USB|iPod\(USB\)|AirPlay)\r\n'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'@ZONE2:PWR=(On|Standby)\r\n'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'@ZONE2:VOL=(-?\d{1,2}\.\d)\r\n'), self.__MatchZone2Volume, None)

    def SetAM(self, value, qualifier):

        ValueStateValues = {
            'Up': '@TUN:AMFREQ=Auto Up\r\n',
            'Down': '@TUN:AMFREQ=Auto Down\r\n'
        }

        AMCmdString = ValueStateValues[value]
        self.__SetHelper('AM', AMCmdString, value, qualifier)

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -6.0,
            'Max': 6.0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BassCmdString = '@MAIN:TONEBASS={0:.2}\r\n'.format(value)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '@MAIN:TONEBASS=?\r\n'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('Bass', value, None)

    def SetDecoder(self, value, qualifier):

        ValueStateValues = {
            'DTS': '@MAIN:DECODERSEL=DTS\r\n',
            'Auto': '@MAIN:DECODERSEL=Auto\r\n'
        }

        DecoderCmdString = ValueStateValues[value]
        self.__SetHelper('Decoder', DecoderCmdString, value, qualifier)

    def UpdateDecoder(self, value, qualifier):

        DecoderCmdString = '@MAIN:DECODERSEL=?\r\n'
        self.__UpdateHelper('Decoder', DecoderCmdString, value, qualifier)

    def __MatchDecoder(self, match, tag):

        ValueStateValues = {
            'DTS': 'DTS',
            'Auto': 'Auto',
            'Unavailable': 'Status Unavailable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Decoder', value, None)

    def SetFM(self, value, qualifier):

        ValueStateValues = {
            'Up': '@TUN:FMFREQ=Auto Up\r\n',
            'Down': '@TUN:FMFREQ=Auto Down\r\n'
        }

        FMCmdString = ValueStateValues[value]
        self.__SetHelper('FM', FMCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '@MAIN:INP=?\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZoneTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@MAIN:PLAYBACK=Play\r\n',
            'Pause': '@MAIN:PLAYBACK=Pause\r\n',
            'Stop': '@MAIN:PLAYBACK=Stop\r\n',
            'Skip +': '@MAIN:PLAYBACK=Skip Fwd\r\n',
            'Skip -': '@MAIN:PLAYBACK=Skip Rev\r\n'
        }

        MainZoneTransportCmdString = ValueStateValues[value]
        self.__SetHelper('MainZoneTransport', MainZoneTransportCmdString, value, qualifier)

    def SetMainZoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80.5,
            'Max': 16.5
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MainZoneVolumeCmdString = '@MAIN:VOL={0:.3}\r\n'.format(value)
            self.__SetHelper('MainZoneVolume', MainZoneVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMainZoneVolume')

    def UpdateMainZoneVolume(self, value, qualifier):

        MainZoneVolumeCmdString = '@MAIN:VOL=?\r\n'
        self.__UpdateHelper('MainZoneVolume', MainZoneVolumeCmdString, value, qualifier)

    def __MatchMainZoneVolume(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('MainZoneVolume', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '@MAIN:MUTE=On\r\n',
            'Off': '@MAIN:MUTE=Off\r\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '@MAIN:MUTE=?\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('AudioMute', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Down': 'Down',
            'Up': 'Up',
            'Left': 'Left',
            'Right': 'Right',
            'Select': 'Sel',
            'Return': 'Return',
            'Return to Home': 'Return to Home'
        }

        MenuNavigationCmdString = '@MAIN:CURSOR={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMenu(self, value, qualifier):

        ValueStateValues = {
            'On Screen': 'On Screen',
            'Top Menu': 'Top Menu',
            'Menu': 'Menu',
            'Option': 'Option',
            'Display': 'Display'
        }

        MenuCmdString = '@MAIN:MENU={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Menu', MenuCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '@MAIN:PWR=On\r\n',
            'Off': '@MAIN:PWR=Standby\r\n',
            'Toggle': '@MAIN:PWR=On/Standby\r\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '@MAIN:PWR=?\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Standby': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPureDirect(self, value, qualifier):

        ValueStateValues = {
            'On': '@MAIN:PUREDIRMODE=On\r\n',
            'Off': '@MAIN:PUREDIRMODE=Off\r\n'
        }

        PureDirectCmdString = ValueStateValues[value]
        self.__SetHelper('PureDirect', PureDirectCmdString, value, qualifier)

    def UpdatePureDirect(self, value, qualifier):

        PureDirectCmdString = '@MAIN:PUREDIRMODE=?\r\n'
        self.__UpdateHelper('PureDirect', PureDirectCmdString, value, qualifier)

    def __MatchPureDirect(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PureDirect', value, None)

    def SetScene(self, value, qualifier):

        SceneCmdString = '@MAIN:SCENE=Scene {0}\r\n'.format(self.SceneValues[value])
        self.__SetHelper('Scene', SceneCmdString, value, qualifier)

    def SetStraight(self, value, qualifier):

        ValueStateValues = {
            'On': '@MAIN:STRAIGHT=On\r\n',
            'Off': '@MAIN:STRAIGHT=Off\r\n'
        }

        StraightCmdString = ValueStateValues[value]
        self.__SetHelper('Straight', StraightCmdString, value, qualifier)

    def UpdateStraight(self, value, qualifier):

        StraightCmdString = '@MAIN:STRAIGHT=?\r\n'
        self.__UpdateHelper('Straight', StraightCmdString, value, qualifier)

    def __MatchStraight(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Straight', value, None)

    def SetSurround(self, value, qualifier):

        SurroundCmdString = self.SurroundValues[value]
        self.__SetHelper('Surround', SurroundCmdString, value, qualifier)

    def UpdateSurround(self, value, qualifier):

        SurroundCmdString = '@MAIN:SOUNDPRG=?\r\n'
        self.__UpdateHelper('Surround', SurroundCmdString, value, qualifier)

    def __MatchSurround(self, match, tag):

        value = self.SurroundState[match.group(1).decode()]
        self.WriteStatus('Surround', value, None)

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -6.0,
            'Max': 6.0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrebleCmdString = '@MAIN:TONETREBLE={0:.2}\r\n'.format(value)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '@MAIN:TONETREBLE=?\r\n'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('Treble', value, None)

    def SetTunerBand(self, value, qualifier):

        ValueStateValues = {
            'AM': '@TUN:BAND=AM\r\n',
            'FM': '@TUN:BAND=FM\r\n'
        }

        TunerBandCmdString = ValueStateValues[value]
        self.__SetHelper('TunerBand', TunerBandCmdString, value, qualifier)

    def UpdateTunerBand(self, value, qualifier):

        TunerBandCmdString = '@TUN:BAND=?\r\n'
        self.__UpdateHelper('TunerBand', TunerBandCmdString, value, qualifier)

    def __MatchTunerBand(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerBand', value, None)

    def SetTunerPreset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            TunerPresetCmdString = '@TUN:PRESET=' + value + '\r\n'
            self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTunerPreset')

    def UpdateTunerPreset(self, value, qualifier):

        TunerPresetCmdString = '@TUN:PRESET=?\r\n'
        self.__UpdateHelper('TunerPreset', TunerPresetCmdString, value, qualifier)

    def __MatchTunerPreset(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerPreset', value, None)

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '@ZONE2:MUTE=On\r\n',
            'Off': '@ZONE2:MUTE=Off\r\n'
        }

        Zone2AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def UpdateZone2AudioMute(self, value, qualifier):

        Zone2AudioMuteCmdString = '@ZONE2:MUTE=?\r\n'
        self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def __MatchZone2AudioMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Zone2AudioMute', value, None)

    def SetZone2Input(self, value, qualifier):

        Zone2InputCmdString = self.ZoneValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '@ZONE2:INP=?\r\n'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = self.ZoneState[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': '@ZONE2:PWR=On\r\n',
            'Off': '@ZONE2:PWR=Standby\r\n'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = '@ZONE2:PWR=?\r\n'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Standby': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Transport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@ZONE2:PLAYBACK=Play\r\n',
            'Pause': '@ZONE2:PLAYBACK=Pause\r\n',
            'Stop': '@ZONE2:PLAYBACK=Stop\r\n',
            'Skip +': '@ZONE2:PLAYBACK=Skip Fwd\r\n',
            'Skip -': '@ZONE2:PLAYBACK=Skip Rev\r\n'
        }

        Zone2TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Transport', Zone2TransportCmdString, value, qualifier)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80.5,
            'Max': 16.5
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = '@ZONE2:VOL={0:.3}\r\n'.format(value)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = '@ZONE2:VOL=?\r\n'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('Zone2Volume', value, None)

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

    def yama_27_2766_1060(self):
    
        self.InputValues = {
            'PHONO'     : '@MAIN:INP=PHONO\r\n', 
            'TUNER'     : '@MAIN:INP=TUNER\r\n', 
            'MULTI CH'  : '@MAIN:INP=MULTI CH\r\n',
            'AV 1'      : '@MAIN:INP=AV1\r\n', 
            'AV 2'      : '@MAIN:INP=AV2\r\n', 
            'AV 3'      : '@MAIN:INP=AV3\r\n', 
            'AV 4'      : '@MAIN:INP=AV4\r\n', 
            'AV 5'      : '@MAIN:INP=AV5\r\n', 
            'AV 6'      : '@MAIN:INP=AV6\r\n', 
            'AV 7'      : '@MAIN:INP=AV7\r\n', 
            'V-AUX'     : '@MAIN:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@MAIN:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@MAIN:INP=AUDIO2\r\n', 
            'AUDIO 3'   : '@MAIN:INP=AUDIO3\r\n', 
            'AUDIO 4'   : '@MAIN:INP=AUDIO4\r\n', 
            'NET'       : '@MAIN:INP=NET\r\n',
            'Napster'   : '@MAIN:INP=Napster\r\n', 
            'Spotify'   : '@MAIN:INP=Spotify\r\n',
            'SERVER'    : '@MAIN:INP=SERVER\r\n',
            'NET RADIO' : '@MAIN:INP=NET RADIO\r\n', 
            'USB'       : '@MAIN:INP=USB\r\n', 
            'iPod(USB)' : '@MAIN:INP=iPod(USB)\r\n',
            'AirPlay'   : '@MAIN:INP=AirPlay\r\n'
        }      

        self.InputState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'MULTI CH'  : 'MULTI CH',
            'TUNER'     : 'TUNER', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'AV7'       : 'AV 7', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'AUDIO3'    : 'AUDIO 3', 
            'AUDIO4'    : 'AUDIO 4', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
        self.SceneValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12'
        }
        
        self.SurroundValues = {
            'Action Game'         : '@MAIN:SOUNDPRG=Action Game\r\n', 
            'Hall in Munich'      : '@MAIN:SOUNDPRG=Hall in Munich\r\n', 
            'Hall in Vienna'      : '@MAIN:SOUNDPRG=Hall in Vienna\r\n',
            'Chamber'             : '@MAIN:SOUNDPRG=Chamber\r\n', 
            'Cellar Club'         : '@MAIN:SOUNDPRG=Cellar Club\r\n', 
            'The Roxy Theatre'    : '@MAIN:SOUNDPRG=The Roxy Theater\r\n', 
            'The Bottom Line'     : '@MAIN:SOUNDPRG=The Bottom Line\r\n', 
            'Sports'              : '@MAIN:SOUNDPRG=Sports\r\n', 
            'Surround Decoder'    : '@MAIN:SOUNDPRG=Surround Decoder\r\n', 
            'Roleplaying Game'    : '@MAIN:SOUNDPRG=Roleplaying Game\r\n', 
            'Music Video'         : '@MAIN:SOUNDPRG=Music Video\r\n', 
            'Standard'            : '@MAIN:SOUNDPRG=Standard\r\n', 
            'Spectacle'           : '@MAIN:SOUNDPRG=Spectacle\r\n', 
            'Sci-Fi'              : '@MAIN:SOUNDPRG=Sci-Fi\r\n', 
            'Adventure'           : '@MAIN:SOUNDPRG=Adventure\r\n', 
            'Drama'               : '@MAIN:SOUNDPRG=Drama\r\n', 
            'Mono Movie'          : '@MAIN:SOUNDPRG=Mono Movie\r\n', 
            '2ch Stereo'          : '@MAIN:SOUNDPRG=2ch Stereo\r\n', 
            '7ch Stereo'          : '@MAIN:SOUNDPRG=7ch Stereo\r\n',
        }
        
        self.SurroundState = {
            'Action Game'         : 'Action Game', 
            'Hall in Munich'      : 'Hall in Munich', 
            'Hall in Vienna'      : 'Hall in Vienna',
            'Chamber'             : 'Chamber', 
            'Cellar Club'         : 'Cellar Club', 
            'The Roxy Theatre'    : 'The Roxy Theatre', 
            'The Bottom Line'     : 'The Bottom Line', 
            'Sports'              : 'Sports', 
            'Surround Decoder'    : 'Surround Decoder', 
            'Roleplaying Game'    : 'Roleplaying Game', 
            'Music Video'         : 'Music Video', 
            'Standard'            : 'Standard', 
            'Spectacle'           : 'Spectacle', 
            'Sci-Fi'              : 'Sci-Fi', 
            'Adventure'           : 'Adventure', 
            'Drama'               : 'Drama', 
            'Mono Movie'          : 'Mono Movie', 
            '2ch Stereo'          : '2ch Stereo', 
            '7ch Stereo'          : '7ch Stereo',
        }
        
        self.ZoneValues = {
            'PHONO'     : '@ZONE2:INP=PHONO\r\n', 
            'TUNER'     : '@ZONE2:INP=TUNER\r\n', 
            'AV 1'      : '@ZONE2:INP=AV1\r\n', 
            'AV 2'      : '@ZONE2:INP=AV2\r\n', 
            'AV 3'      : '@ZONE2:INP=AV3\r\n', 
            'AV 4'      : '@ZONE2:INP=AV4\r\n', 
            'AV 5'      : '@ZONE2:INP=AV5\r\n', 
            'AV 6'      : '@ZONE2:INP=AV6\r\n', 
            'AV 7'      : '@ZONE2:INP=AV7\r\n', 
            'V-AUX'     : '@ZONE2:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@ZONE2:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@ZONE2:INP=AUDIO2\r\n', 
            'AUDIO 3'   : '@ZONE2:INP=AUDIO3\r\n', 
            'AUDIO 4'   : '@ZONE2:INP=AUDIO4\r\n', 
            'NET'       : '@ZONE2:INP=NET\r\n',
            'Napster'   : '@ZONE2:INP=Napster\r\n', 
            'Spotify'   : '@ZONE2:INP=Spotify\r\n',
            'SERVER'    : '@ZONE2:INP=SERVER\r\n',
            'NET RADIO' : '@ZONE2:INP=NET RADIO\r\n', 
            'USB'       : '@ZONE2:INP=USB\r\n', 
            'iPod(USB)' : '@ZONE2:INP=iPod(USB)\r\n',
            'AirPlay'   : '@ZONE2:INP=AirPlay\r\n'
        }
        
        self.ZoneState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'TUNER'     : 'TUNER', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'AV7'       : 'AV 7', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'AUDIO3'    : 'AUDIO 3', 
            'AUDIO4'    : 'AUDIO 4', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
    def yama_27_2766_23_060(self):
            
        self.InputValues = {
            'PHONO'     : '@MAIN:INP=PHONO\r\n', 
            'TUNER'     : '@MAIN:INP=TUNER\r\n', 
            'MULTI CH'  : '@MAIN:INP=MULTI CH\r\n',
            'AV 1'      : '@MAIN:INP=AV1\r\n', 
            'AV 2'      : '@MAIN:INP=AV2\r\n', 
            'AV 3'      : '@MAIN:INP=AV3\r\n', 
            'AV 4'      : '@MAIN:INP=AV4\r\n', 
            'AV 5'      : '@MAIN:INP=AV5\r\n', 
            'AV 6'      : '@MAIN:INP=AV6\r\n', 
            'AV 7'      : '@MAIN:INP=AV7\r\n', 
            'V-AUX'     : '@MAIN:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@MAIN:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@MAIN:INP=AUDIO2\r\n', 
            'AUDIO 3'   : '@MAIN:INP=AUDIO3\r\n', 
            'AUDIO 4'   : '@MAIN:INP=AUDIO4\r\n', 
            'NET'       : '@MAIN:INP=NET\r\n',
            'Napster'   : '@MAIN:INP=Napster\r\n', 
            'Spotify'   : '@MAIN:INP=Spotify\r\n',
            'SERVER'    : '@MAIN:INP=SERVER\r\n',
            'NET RADIO' : '@MAIN:INP=NET RADIO\r\n', 
            'USB'       : '@MAIN:INP=USB\r\n', 
            'iPod(USB)' : '@MAIN:INP=iPod(USB)\r\n',
            'AirPlay'   : '@MAIN:INP=AirPlay\r\n'
        }      

        self.InputState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'MULTI CH'  : 'MULTI CH',
            'TUNER'     : 'TUNER', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'AV7'       : 'AV 7', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'AUDIO3'    : 'AUDIO 3', 
            'AUDIO4'    : 'AUDIO 4', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
        self.SceneValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12'
        }
        
        self.SurroundValues = {
            'Action Game'         : '@MAIN:SOUNDPRG=Action Game\r\n', 
            'Hall in Munich'      : '@MAIN:SOUNDPRG=Hall in Munich\r\n', 
            'Hall in Vienna'      : '@MAIN:SOUNDPRG=Hall in Vienna\r\n',
            'Hall in Amsterdam'   : '@MAIN:SOUNDPRG=Hall in Amsterdam\r\n', 
            'Church in Freiburg'  : '@MAIN:SOUNDPRG=Church in Freiburg\r\n', 
            'Church in Royaumont' : '@MAIN:SOUNDPRG=Church in Royaumont\r\n', 
            'Village Vanguard'    : '@MAIN:SOUNDPRG=Village Vanguard\r\n', 
            'Warehouse Loft'      : '@MAIN:SOUNDPRG=Warehouse Loft\r\n',             
            'Chamber'             : '@MAIN:SOUNDPRG=Chamber\r\n', 
            'Cellar Club'         : '@MAIN:SOUNDPRG=Cellar Club\r\n', 
            'The Roxy Theatre'    : '@MAIN:SOUNDPRG=The Roxy Theater\r\n', 
            'The Bottom Line'     : '@MAIN:SOUNDPRG=The Bottom Line\r\n', 
            'Sports'              : '@MAIN:SOUNDPRG=Sports\r\n', 
            'Surround Decoder'    : '@MAIN:SOUNDPRG=Surround Decoder\r\n', 
            'Roleplaying Game'    : '@MAIN:SOUNDPRG=Roleplaying Game\r\n', 
            'Music Video'         : '@MAIN:SOUNDPRG=Music Video\r\n', 
            'Standard'            : '@MAIN:SOUNDPRG=Standard\r\n', 
            'Spectacle'           : '@MAIN:SOUNDPRG=Spectacle\r\n', 
            'Sci-Fi'              : '@MAIN:SOUNDPRG=Sci-Fi\r\n', 
            'Adventure'           : '@MAIN:SOUNDPRG=Adventure\r\n', 
            'Drama'               : '@MAIN:SOUNDPRG=Drama\r\n', 
            'Mono Movie'          : '@MAIN:SOUNDPRG=Mono Movie\r\n', 
            '2ch Stereo'          : '@MAIN:SOUNDPRG=2ch Stereo\r\n', 
            '9ch Stereo'          : '@MAIN:SOUNDPRG=9ch Stereo\r\n',
            'Recital/Opera'       : '@MAIN:SOUNDPRG=Recital/Opera\r\n'
        }
        
        self.SurroundState = {
            'Action Game'         : 'Action Game', 
            'Hall in Munich'      : 'Hall in Munich', 
            'Hall in Vienna'      : 'Hall in Vienna',
            'Hall in Amsterdam'   : 'Hall in Amsterdam',
            'Church in Freiburg'  : 'Church in Freiburg',
            'Church in Royaumont' : 'Church in Royaumont',
            'Village Vanguard'    : 'Village Vanguard',
            'Warehouse Loft'      : 'Warehouse Loft',
            'Chamber'             : 'Chamber', 
            'Cellar Club'         : 'Cellar Club', 
            'The Roxy Theatre'    : 'The Roxy Theatre', 
            'The Bottom Line'     : 'The Bottom Line', 
            'Sports'              : 'Sports', 
            'Surround Decoder'    : 'Surround Decoder', 
            'Roleplaying Game'    : 'Roleplaying Game', 
            'Music Video'         : 'Music Video', 
            'Standard'            : 'Standard', 
            'Spectacle'           : 'Spectacle', 
            'Sci-Fi'              : 'Sci-Fi', 
            'Adventure'           : 'Adventure', 
            'Drama'               : 'Drama', 
            'Mono Movie'          : 'Mono Movie', 
            '2ch Stereo'          : '2ch Stereo', 
            '9ch Stereo'          : '9ch Stereo',
            'Recital/Opera'       : 'Recital/Opera'
        }
        
        self.ZoneValues = {
            'PHONO'     : '@ZONE2:INP=PHONO\r\n', 
            'TUNER'     : '@ZONE2:INP=TUNER\r\n', 
            'AV 1'      : '@ZONE2:INP=AV1\r\n', 
            'AV 2'      : '@ZONE2:INP=AV2\r\n', 
            'AV 3'      : '@ZONE2:INP=AV3\r\n', 
            'AV 4'      : '@ZONE2:INP=AV4\r\n', 
            'AV 5'      : '@ZONE2:INP=AV5\r\n', 
            'AV 6'      : '@ZONE2:INP=AV6\r\n', 
            'AV 7'      : '@ZONE2:INP=AV7\r\n', 
            'V-AUX'     : '@ZONE2:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@ZONE2:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@ZONE2:INP=AUDIO2\r\n', 
            'AUDIO 3'   : '@ZONE2:INP=AUDIO3\r\n', 
            'AUDIO 4'   : '@ZONE2:INP=AUDIO4\r\n', 
            'NET'       : '@ZONE2:INP=NET\r\n',
            'Napster'   : '@ZONE2:INP=Napster\r\n', 
            'Spotify'   : '@ZONE2:INP=Spotify\r\n',
            'SERVER'    : '@ZONE2:INP=SERVER\r\n',
            'NET RADIO' : '@ZONE2:INP=NET RADIO\r\n', 
            'USB'       : '@ZONE2:INP=USB\r\n', 
            'iPod(USB)' : '@ZONE2:INP=iPod(USB)\r\n',
            'AirPlay'   : '@ZONE2:INP=AirPlay\r\n'
        }
        
        self.ZoneState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'TUNER'     : 'TUNER', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'AV7'       : 'AV 7', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'AUDIO3'    : 'AUDIO 3', 
            'AUDIO4'    : 'AUDIO 4', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
    def yama_27_2766_760(self):
    
        
        
        self.InputValues = {
            'TUNER'     : '@MAIN:INP=TUNER\r\n', 
            'HDMI 1'    : '@MAIN:INP=HDMI1\r\n', 
            'HDMI 2'    : '@MAIN:INP=HDMI2\r\n', 
            'HDMI 3'    : '@MAIN:INP=HDMI3\r\n', 
            'HDMI 4'    : '@MAIN:INP=HDMI4\r\n', 
            'HDMI 5'    : '@MAIN:INP=HDMI5\r\n', 
            'AV 1'      : '@MAIN:INP=AV1\r\n', 
            'AV 2'      : '@MAIN:INP=AV2\r\n', 
            'AV 3'      : '@MAIN:INP=AV3\r\n', 
            'AV 4'      : '@MAIN:INP=AV4\r\n', 
            'AV 5'      : '@MAIN:INP=AV5\r\n', 
            'AV 6'      : '@MAIN:INP=AV6\r\n', 
            'V-AUX'     : '@MAIN:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@MAIN:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@MAIN:INP=AUDIO2\r\n', 
            'NET'       : '@MAIN:INP=NET\r\n',
            'Napster'   : '@MAIN:INP=Napster\r\n', 
            'Spotify'   : '@MAIN:INP=Spotify\r\n',
            'SERVER'    : '@MAIN:INP=SERVER\r\n',
            'NET RADIO' : '@MAIN:INP=NET RADIO\r\n', 
            'USB'       : '@MAIN:INP=USB\r\n', 
            'iPod(USB)' : '@MAIN:INP=iPod(USB)\r\n',
            'AirPlay'   : '@MAIN:INP=AirPlay\r\n'
        }      

        self.InputState = {
            'NET RADIO' : 'NET RADIO',
            'TUNER'     : 'TUNER',             
            'HDMI1'     : 'HDMI 1', 
            'HDMI2'     : 'HDMI 2', 
            'HDMI3'     : 'HDMI 3', 
            'HDMI4'     : 'HDMI 4', 
            'HDMI5'     : 'HDMI 5', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
        self.SceneValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
        }
        
        self.SurroundValues = {
            'Action Game'         : '@MAIN:SOUNDPRG=Action Game\r\n', 
            'Hall in Munich'      : '@MAIN:SOUNDPRG=Hall in Munich\r\n', 
            'Hall in Vienna'      : '@MAIN:SOUNDPRG=Hall in Vienna\r\n',
            'Chamber'             : '@MAIN:SOUNDPRG=Chamber\r\n', 
            'Cellar Club'         : '@MAIN:SOUNDPRG=Cellar Club\r\n', 
            'The Roxy Theatre'    : '@MAIN:SOUNDPRG=The Roxy Theater\r\n', 
            'The Bottom Line'     : '@MAIN:SOUNDPRG=The Bottom Line\r\n', 
            'Sports'              : '@MAIN:SOUNDPRG=Sports\r\n', 
            'Surround Decoder'    : '@MAIN:SOUNDPRG=Surround Decoder\r\n', 
            'Roleplaying Game'    : '@MAIN:SOUNDPRG=Roleplaying Game\r\n', 
            'Music Video'         : '@MAIN:SOUNDPRG=Music Video\r\n', 
            'Standard'            : '@MAIN:SOUNDPRG=Standard\r\n', 
            'Spectacle'           : '@MAIN:SOUNDPRG=Spectacle\r\n', 
            'Sci-Fi'              : '@MAIN:SOUNDPRG=Sci-Fi\r\n', 
            'Adventure'           : '@MAIN:SOUNDPRG=Adventure\r\n', 
            'Drama'               : '@MAIN:SOUNDPRG=Drama\r\n', 
            'Mono Movie'          : '@MAIN:SOUNDPRG=Mono Movie\r\n', 
            '2ch Stereo'          : '@MAIN:SOUNDPRG=2ch Stereo\r\n', 
            '7ch Stereo'          : '@MAIN:SOUNDPRG=7ch Stereo\r\n',
        }
        
        self.SurroundState = {
            'Action Game'         : 'Action Game', 
            'Hall in Munich'      : 'Hall in Munich', 
            'Hall in Vienna'      : 'Hall in Vienna',
            'Chamber'             : 'Chamber', 
            'Cellar Club'         : 'Cellar Club', 
            'The Roxy Theatre'    : 'The Roxy Theatre', 
            'The Bottom Line'     : 'The Bottom Line', 
            'Sports'              : 'Sports', 
            'Surround Decoder'    : 'Surround Decoder', 
            'Roleplaying Game'    : 'Roleplaying Game', 
            'Music Video'         : 'Music Video', 
            'Standard'            : 'Standard', 
            'Spectacle'           : 'Spectacle', 
            'Sci-Fi'              : 'Sci-Fi', 
            'Adventure'           : 'Adventure', 
            'Drama'               : 'Drama', 
            'Mono Movie'          : 'Mono Movie', 
            '2ch Stereo'          : '2ch Stereo', 
            '7ch Stereo'          : '7ch Stereo',
        }
        
        self.ZoneValues = {
            'TUNER'     : '@ZONE2:INP=TUNER\r\n', 
            'AV 5'      : '@ZONE2:INP=AV5\r\n', 
            'AV 6'      : '@ZONE2:INP=AV6\r\n', 
            'AUDIO 1'   : '@ZONE2:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@ZONE2:INP=AUDIO2\r\n', 
            'NET'       : '@ZONE2:INP=NET\r\n',
            'Napster'   : '@ZONE2:INP=Napster\r\n', 
            'Spotify'   : '@ZONE2:INP=Spotify\r\n',
            'SERVER'    : '@ZONE2:INP=SERVER\r\n',
            'NET RADIO' : '@ZONE2:INP=NET RADIO\r\n', 
            'USB'       : '@ZONE2:INP=USB\r\n', 
            'iPod(USB)' : '@ZONE2:INP=iPod(USB)\r\n',
            'AirPlay'   : '@ZONE2:INP=AirPlay\r\n'
        }
        
        self.ZoneState = {
            'NET RADIO' : 'NET RADIO', 
            'TUNER'     : 'TUNER', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
    def yama_27_2766_860(self):
    
        
        
        self.InputValues = {
            'PHONO'     : '@MAIN:INP=PHONO\r\n', 
            'TUNER'     : '@MAIN:INP=TUNER\r\n', 
            'HDMI 1'    : '@MAIN:INP=HDMI1\r\n', 
            'HDMI 2'    : '@MAIN:INP=HDMI2\r\n', 
            'HDMI 3'    : '@MAIN:INP=HDMI3\r\n', 
            'HDMI 4'    : '@MAIN:INP=HDMI4\r\n', 
            'HDMI 5'    : '@MAIN:INP=HDMI5\r\n', 
            'HDMI 6'    : '@MAIN:INP=HDMI6\r\n', 
            'HDMI 7'    : '@MAIN:INP=HDMI7\r\n', 
            'AV 1'      : '@MAIN:INP=AV1\r\n', 
            'AV 2'      : '@MAIN:INP=AV2\r\n', 
            'AV 3'      : '@MAIN:INP=AV3\r\n', 
            'AV 4'      : '@MAIN:INP=AV4\r\n', 
            'AV 5'      : '@MAIN:INP=AV5\r\n', 
            'AV 6'      : '@MAIN:INP=AV6\r\n', 
            'V-AUX'     : '@MAIN:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@MAIN:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@MAIN:INP=AUDIO2\r\n', 
            'NET'       : '@MAIN:INP=NET\r\n',
            'Napster'   : '@MAIN:INP=Napster\r\n', 
            'Spotify'   : '@MAIN:INP=Spotify\r\n',
            'SERVER'    : '@MAIN:INP=SERVER\r\n',
            'NET RADIO' : '@MAIN:INP=NET RADIO\r\n', 
            'USB'       : '@MAIN:INP=USB\r\n', 
            'iPod(USB)' : '@MAIN:INP=iPod(USB)\r\n',
            'AirPlay'   : '@MAIN:INP=AirPlay\r\n'
        }      

        self.InputState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'TUNER'     : 'TUNER', 
            'HDMI1'     : 'HDMI 1', 
            'HDMI2'     : 'HDMI 2', 
            'HDMI3'     : 'HDMI 3', 
            'HDMI4'     : 'HDMI 4', 
            'HDMI5'     : 'HDMI 5', 
            'HDMI6'     : 'HDMI 6', 
            'HDMI7'     : 'HDMI 7', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
        self.SceneValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
        }
        
        self.SurroundValues = {
            'Action Game'         : '@MAIN:SOUNDPRG=Action Game\r\n', 
            'Hall in Munich'      : '@MAIN:SOUNDPRG=Hall in Munich\r\n', 
            'Hall in Vienna'      : '@MAIN:SOUNDPRG=Hall in Vienna\r\n',
            'Chamber'             : '@MAIN:SOUNDPRG=Chamber\r\n', 
            'Cellar Club'         : '@MAIN:SOUNDPRG=Cellar Club\r\n', 
            'The Roxy Theatre'    : '@MAIN:SOUNDPRG=The Roxy Theater\r\n', 
            'The Bottom Line'     : '@MAIN:SOUNDPRG=The Bottom Line\r\n', 
            'Sports'              : '@MAIN:SOUNDPRG=Sports\r\n', 
            'Surround Decoder'    : '@MAIN:SOUNDPRG=Surround Decoder\r\n', 
            'Roleplaying Game'    : '@MAIN:SOUNDPRG=Roleplaying Game\r\n', 
            'Music Video'         : '@MAIN:SOUNDPRG=Music Video\r\n', 
            'Standard'            : '@MAIN:SOUNDPRG=Standard\r\n', 
            'Spectacle'           : '@MAIN:SOUNDPRG=Spectacle\r\n', 
            'Sci-Fi'              : '@MAIN:SOUNDPRG=Sci-Fi\r\n', 
            'Adventure'           : '@MAIN:SOUNDPRG=Adventure\r\n', 
            'Drama'               : '@MAIN:SOUNDPRG=Drama\r\n', 
            'Mono Movie'          : '@MAIN:SOUNDPRG=Mono Movie\r\n', 
            '2ch Stereo'          : '@MAIN:SOUNDPRG=2ch Stereo\r\n', 
            '7ch Stereo'          : '@MAIN:SOUNDPRG=7ch Stereo\r\n',
        }
        
        self.SurroundState = {
            'Action Game'         : 'Action Game', 
            'Hall in Munich'      : 'Hall in Munich', 
            'Hall in Vienna'      : 'Hall in Vienna',
            'Chamber'             : 'Chamber', 
            'Cellar Club'         : 'Cellar Club', 
            'The Roxy Theatre'    : 'The Roxy Theatre', 
            'The Bottom Line'     : 'The Bottom Line', 
            'Sports'              : 'Sports', 
            'Surround Decoder'    : 'Surround Decoder', 
            'Roleplaying Game'    : 'Roleplaying Game', 
            'Music Video'         : 'Music Video', 
            'Standard'            : 'Standard', 
            'Spectacle'           : 'Spectacle', 
            'Sci-Fi'              : 'Sci-Fi', 
            'Adventure'           : 'Adventure', 
            'Drama'               : 'Drama', 
            'Mono Movie'          : 'Mono Movie', 
            '2ch Stereo'          : '2ch Stereo', 
            '7ch Stereo'          : '7ch Stereo',
        }
        
        self.ZoneValues = {
            'PHONO'     : '@ZONE2:INP=PHONO\r\n', 
            'TUNER'     : '@ZONE2:INP=TUNER\r\n', 
            'AV 5'      : '@ZONE2:INP=AV5\r\n', 
            'AV 6'      : '@ZONE2:INP=AV6\r\n', 
            'V-AUX'     : '@ZONE2:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@ZONE2:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@ZONE2:INP=AUDIO2\r\n', 
            'NET'       : '@ZONE2:INP=NET\r\n',
            'Napster'   : '@ZONE2:INP=Napster\r\n', 
            'Spotify'   : '@ZONE2:INP=Spotify\r\n',
            'SERVER'    : '@ZONE2:INP=SERVER\r\n',
            'NET RADIO' : '@ZONE2:INP=NET RADIO\r\n', 
            'USB'       : '@ZONE2:INP=USB\r\n', 
            'iPod(USB)' : '@ZONE2:INP=iPod(USB)\r\n',
            'AirPlay'   : '@ZONE2:INP=AirPlay\r\n'
        }
        
        self.ZoneState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'TUNER'     : 'TUNER', 
            'AV5'       : 'AV 5', 
            'AV6'       : 'AV 6', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
    def yama_27_2766_660(self):
    
        
        
        self.InputValues = {
            'TUNER'     : '@MAIN:INP=TUNER\r\n', 
            'HDMI 1'    : '@MAIN:INP=HDMI1\r\n', 
            'HDMI 2'    : '@MAIN:INP=HDMI2\r\n', 
            'HDMI 3'    : '@MAIN:INP=HDMI3\r\n', 
            'HDMI 4'    : '@MAIN:INP=HDMI4\r\n', 
            'AV 1'      : '@MAIN:INP=AV1\r\n', 
            'AV 2'      : '@MAIN:INP=AV2\r\n', 
            'AV 3'      : '@MAIN:INP=AV3\r\n', 
            'AV 4'      : '@MAIN:INP=AV4\r\n', 
            'V-AUX'     : '@MAIN:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@MAIN:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@MAIN:INP=AUDIO2\r\n', 
            'NET'       : '@MAIN:INP=NET\r\n',
            'Napster'   : '@MAIN:INP=Napster\r\n', 
            'Spotify'   : '@MAIN:INP=Spotify\r\n',
            'SERVER'    : '@MAIN:INP=SERVER\r\n',
            'NET RADIO' : '@MAIN:INP=NET RADIO\r\n', 
            'USB'       : '@MAIN:INP=USB\r\n', 
            'iPod(USB)' : '@MAIN:INP=iPod(USB)\r\n',
            'AirPlay'   : '@MAIN:INP=AirPlay\r\n'
        }      

        self.InputState = {
            'NET RADIO' : 'NET RADIO', 
            'TUNER'     : 'TUNER', 
            'HDMI1'     : 'HDMI 1', 
            'HDMI2'     : 'HDMI 2', 
            'HDMI3'     : 'HDMI 3', 
            'HDMI4'     : 'HDMI 4', 
            'AV1'       : 'AV 1', 
            'AV2'       : 'AV 2', 
            'AV3'       : 'AV 3', 
            'AV4'       : 'AV 4', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
        }
        
        self.SceneValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
        }
        
        self.SurroundValues = {
            'Action Game'         : '@MAIN:SOUNDPRG=Action Game\r\n', 
            'Hall in Munich'      : '@MAIN:SOUNDPRG=Hall in Munich\r\n', 
            'Hall in Vienna'      : '@MAIN:SOUNDPRG=Hall in Vienna\r\n',
            'Chamber'             : '@MAIN:SOUNDPRG=Chamber\r\n', 
            'Cellar Club'         : '@MAIN:SOUNDPRG=Cellar Club\r\n', 
            'The Roxy Theatre'    : '@MAIN:SOUNDPRG=The Roxy Theater\r\n', 
            'The Bottom Line'     : '@MAIN:SOUNDPRG=The Bottom Line\r\n', 
            'Sports'              : '@MAIN:SOUNDPRG=Sports\r\n', 
            'Surround Decoder'    : '@MAIN:SOUNDPRG=Surround Decoder\r\n', 
            'Roleplaying Game'    : '@MAIN:SOUNDPRG=Roleplaying Game\r\n', 
            'Music Video'         : '@MAIN:SOUNDPRG=Music Video\r\n', 
            'Standard'            : '@MAIN:SOUNDPRG=Standard\r\n', 
            'Spectacle'           : '@MAIN:SOUNDPRG=Spectacle\r\n', 
            'Sci-Fi'              : '@MAIN:SOUNDPRG=Sci-Fi\r\n', 
            'Adventure'           : '@MAIN:SOUNDPRG=Adventure\r\n', 
            'Drama'               : '@MAIN:SOUNDPRG=Drama\r\n', 
            'Mono Movie'          : '@MAIN:SOUNDPRG=Mono Movie\r\n', 
            '2ch Stereo'          : '@MAIN:SOUNDPRG=2ch Stereo\r\n', 
            '7ch Stereo'          : '@MAIN:SOUNDPRG=7ch Stereo\r\n',
        }
        
        self.SurroundState = {
            'Action Game'         : 'Action Game', 
            'Hall in Munich'      : 'Hall in Munich', 
            'Hall in Vienna'      : 'Hall in Vienna',
            'Chamber'             : 'Chamber', 
            'Cellar Club'         : 'Cellar Club', 
            'The Roxy Theatre'    : 'The Roxy Theatre', 
            'The Bottom Line'     : 'The Bottom Line', 
            'Sports'              : 'Sports', 
            'Surround Decoder'    : 'Surround Decoder', 
            'Roleplaying Game'    : 'Roleplaying Game', 
            'Music Video'         : 'Music Video', 
            'Standard'            : 'Standard', 
            'Spectacle'           : 'Spectacle', 
            'Sci-Fi'              : 'Sci-Fi', 
            'Adventure'           : 'Adventure', 
            'Drama'               : 'Drama', 
            'Mono Movie'          : 'Mono Movie', 
            '2ch Stereo'          : '2ch Stereo', 
            '7ch Stereo'          : '7ch Stereo',
        }
        
        self.ZoneValues = {
            'PHONO'     : '@ZONE2:INP=PHONO\r\n', 
            'TUNER'     : '@ZONE2:INP=TUNER\r\n', 
            'V-AUX'     : '@ZONE2:INP=V-AUX\r\n', 
            'AUDIO 1'   : '@ZONE2:INP=AUDIO1\r\n', 
            'AUDIO 2'   : '@ZONE2:INP=AUDIO2\r\n', 
            'NET'       : '@ZONE2:INP=NET\r\n',
            'Napster'   : '@ZONE2:INP=Napster\r\n', 
            'Spotify'   : '@ZONE2:INP=Spotify\r\n',
            'SERVER'    : '@ZONE2:INP=SERVER\r\n',
            'NET RADIO' : '@ZONE2:INP=NET RADIO\r\n', 
            'USB'       : '@ZONE2:INP=USB\r\n', 
            'iPod(USB)' : '@ZONE2:INP=iPod(USB)\r\n',
            'AirPlay'   : '@ZONE2:INP=AirPlay\r\n'
        }
        
        self.ZoneState = {
            'NET RADIO' : 'NET RADIO', 
            'PHONO'     : 'PHONO', 
            'TUNER'     : 'TUNER', 
            'V-AUX'     : 'V-AUX', 
            'AUDIO1'    : 'AUDIO 1', 
            'AUDIO2'    : 'AUDIO 2', 
            'Napster'   : 'Napster', 
            'Spotify'   : 'Spotify', 
            'SERVER'    : 'SERVER', 
            'USB'       : 'USB', 
            'iPod(USB)' : 'iPod(USB)', 
            'AirPlay'   : 'AirPlay'
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
