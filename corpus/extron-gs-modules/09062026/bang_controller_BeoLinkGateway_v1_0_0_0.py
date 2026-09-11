from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import struct


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

        self.DestinationValues = {
            'Video Source': 0x00,
            'Audio Source': 0x01,
            'V.TAPE/V.MEM': 0x05,
            'All Products': 0x0F
        }

        self.CommandValues = {
            'SOURCE: STANDBY': 0x0C,
            'SOURCE: SLEEP': 0x47,
            'SOURCE: TV': 0x80,
            'SOURCE: RADIO': 0x81,
            'SOURCE: AUX_V / DTV2': 0x82,
            'SOURCE: AUX_A': 0x83,
            'SOURCE: VTR / V.MEM / DVD2': 0x85,
            'SOURCE: CDV / DVD': 0x86,
            'SOURCE: CAMCORDER / CAMERA': 0x87,
            'SOURCE: TEXT': 0x88,
            'SOURCE: V_SAT / DTV': 0x8A,
            'SOURCE: PC': 0x8B,
            'SOURCE: DOORCAM / V.AUX2': 0x8D,
            'SOURCE: TP1 / A.MEM': 0x91,
            'SOURCE: CD': 0x92,
            'SOURCE: PH / N.RADIO': 0x93,
            'SOURCE: TP2 / N.MUSIC': 0x94,
            'SOURCE: CD2 / JOIN': 0x97,
            'SOURCE: VTR2': 0xA8,
            'SOURCE: MEDIA': 0x84,
            'SOURCE: WEB': 0x8C,
            'SOURCE: PHOTO': 0x8E,
            'SOURCE: USB2': 0x90,
            'SOURCE: SERVER': 0x95,
            'SOURCE: NET': 0x96,
            'SOURCE: PICTURE_IN_PICTURE / P-AND-P': 0xFA,
            'DIGIT: 0': 0x00,
            'DIGIT: 1': 0x01,
            'DIGIT: 2': 0x02,
            'DIGIT: 3': 0x03,
            'DIGIT: 4': 0x04,
            'DIGIT: 5': 0x05,
            'DIGIT: 6': 0x06,
            'DIGIT: 7': 0x07,
            'DIGIT: 8': 0x08,
            'DIGIT: 9': 0x09,
            'CONTROL: STEP_UP': 0x1E,
            'CONTROL: STEP_DW': 0x1F,
            'CONTROL: REWIND': 0x32,
            'CONTROL: REC_RETURN / RETURN': 0x33,
            'CONTROL: WIND': 0x34,
            'CONTROL: GO / PLAY': 0x35,
            'CONTROL: STOP': 0x36,
            'CONTROL: CNTL_WIND / Yellow': 0xD4,
            'CONTROL: CNTL_REWIND / Green': 0xD5,
            'CONTROL: CNTL_STEP_UP / Blue': 0xD8,
            'CONTROL: CNTL_STEP_DW / Red': 0xD9,
            'SOUND: MUTE': 0x0D,
            'SOUND: SOUND / SPEAKER': 0x44,
            'SOUND: ANALOG_UP_1 / Volume UP': 0x60,
            'SOUND: ANALOG_DW_1 / Volume DOWN': 0x64,
            'PICTURE: MENU': 0x5C,
            'PICTURE: PICTURE_TOGGLE / P.MUTE': 0x1C,
            'PICTURE: PICTURE_FORMAT / FORMAT': 0x2A,
            'PICTURE: CINEMA_ON': 0xDA,
            'PICTURE: CINEMA_OFF': 0xDB,
            'OTHER: OPEN_STAND / STAND': 0xF7,
            'OTHER: CLEAR': 0x0A,
            'OTHER: STORE': 0x0B,
            'OTHER: RESET / INDEX': 0x0E,
            'OTHER: BACK': 0x14,
            'OTHER: CMD_A / MOTS': 0x15,
            'OTHER: GOTO / TRACK / LAMP': 0x20,
            'OTHER: SHOW_CLOCK / CLOCK': 0x28,
            'OTHER: EJECT': 0x2D,
            'OTHER: RECORD': 0x37,
            'OTHER: MEDIUM_SELECT / SELECT': 0x3F,
            'OTHER: TURN / SOUND': 0x46,
            'OTHER: EXIT': 0x7F,
            'OTHER: CNTL_0 / SHIFT-0 / EDIT': 0xC0,
            'OTHER: CNTL_1 / SHIFT-1 / RANDOM': 0xC1,
            'OTHER: CNTL_2 / SHIFT-2': 0xC2,
            'OTHER: CNTL_3 / SHIFT-3 / REPEAT': 0xC3,
            'OTHER: CNTL_4 / SHIFT-4 / SELECT': 0xC4,
            'OTHER: CNTL_5 / SHIFT-5': 0xC5,
            'OTHER: CNTL_6 / SHIFT-6': 0xC6,
            'OTHER: CNTL_7 / SHIFT-7': 0xC7,
            'OTHER: CNTL_8 / SHIFT-8': 0xC8,
            'OTHER: CNTL_9 / SHIFT-9': 0xC9,
            'CONTINUE: C_REWIND / Continue REWIND': 0x70,
            'CONTINUE: C_WIND / Continue WIND': 0x71,
            'CONTINUE: C_STEP_UP / Continue step UP': 0x72,
            'CONTINUE: C_STEP_DW / Continue step DOWN': 0x73,
            'CONTINUE: CONTINUE / Continue (other keys)': 0x75,
            'CONTINUE: CNTL_C_REWIND / Continue Green': 0x76,
            'CONTINUE: CNTL_C_WIND / Continue Yellow': 0x77,
            'CONTINUE: CNTL_C_STEP_UP / Continue Blue': 0x78,
            'CONTINUE: CNTL_C_STEP_DW / Continue Red': 0x79,
            'CONTINUE: KEY_RELEASE': 0x7E,
            'FUNCTION_1': 0x0F,
            'FUNCTION_2': 0x10,
            'FUNCTION_3': 0x11,
            'FUNCTION_4': 0x12,
            'FUNCTION_5': 0x19,
            'FUNCTION_6': 0x1A,
            'FUNCTION_7': 0x21,
            'FUNCTION_8': 0x22,
            'FUNCTION_9': 0x23,
            'FUNCTION_10': 0x24,
            'FUNCTION_11': 0x25,
            'FUNCTION_12': 0x26,
            'FUNCTION_13': 0x27,
            'FUNCTION_14': 0x39,
            'FUNCTION_15': 0x3A,
            'FUNCTION_16': 0x3B,
            'FUNCTION_17': 0x3C,
            'FUNCTION_18': 0x3D,
            'FUNCTION_19': 0x3E,
            'FUNCTION_20': 0x4B,
            'FUNCTION_21': 0x4C,
            'FUNCTION_22': 0x50,
            'FUNCTION_23': 0x51,
            'FUNCTION_24': 0x7D,
            'FUNCTION_25': 0xA5,
            'FUNCTION_26': 0xA6,
            'FUNCTION_27': 0xA9,
            'FUNCTION_28': 0xAA,
            'FUNCTION_29': 0xDD,
            'FUNCTION_30': 0xDE,
            'FUNCTION_31': 0xE0,
            'FUNCTION_32': 0xE1,
            'FUNCTION_33': 0xE2,
            'FUNCTION_34': 0xE6,
            'FUNCTION_35': 0xE7,
            'FUNCTION_36': 0xF2,
            'FUNCTION_37': 0xF3,
            'FUNCTION_38': 0xF4,
            'FUNCTION_39': 0xF5,
            'FUNCTION_40': 0xF6,
            'CURSOR: SELECT': 0x13,
            'CURSOR: UP': 0xCA,
            'CURSOR: DW': 0xCB,
            'CURSOR: LEFT': 0xCC,
            'CURSOR: RIGHT': 0xCD
        }

        self.Link = {
            'Local / Default source': 0x00,
            'Remote source / OPTION 4 product': 0x01
        }

        self.SourceNames = {
            b'\x0b': 'TV',
            b'\x15': 'V_MEM / V_TAPE',
            b'\x16': 'DVD_2 / V_TAPE2',
            b'\x1f': 'SAT / DTV',
            b'\x29': 'DVD',
            b'\x33': 'DTV_2 / V_AUX',
            b'\x3e': 'V_AUX2 / DOORCAM',
            b'\x47': 'PC',
            b'\x6f': 'RADIO',
            b'\x79': 'A_MEM',
            b'\x7a': 'A_MEM2',
            b'\x8d': 'CD',
            b'\x97': 'A_AUX',
            b'\xa1': 'N_RADIO'
        }

        self.SourceActivityNames = {
            b'\x00': 'Unknown',
            b'\x01': 'Stop',
            b'\x02': 'Playing',
            b'\x03': 'Wind',
            b'\x04': 'Rewind',
            b'\x05': 'Record lock',
            b'\x06': 'Standby',
            b'\x07': 'No medium',
            b'\x08': 'Still picture',
            b'\x14': 'Scan-play forward',
            b'\x15': 'Scan-play reverse',
            b'\xff': 'Blank status'
        }

        self.PictureFormatNames = {
            b'\x00': 'Unknown',
            b'\x01': 'Known by decoder',
            b'\x02': '4:3',
            b'\x03': '16:9',
            b'\x04': '4:3 Letterbox middle',
            b'\x05': '4:3 Letterbox top',
            b'\x06': '4:3 Letterbox bottom',
            b'\xff': 'Blank picture'
        }

        self.SoundStatusNames = {
            b'\x00': 'Sound not muted',
            b'\x01': 'Sound muted',
        }

        self.SpeakerMode = {
            b'\x01': 'Speaker mode 1 (center channel)',
            b'\x02': 'Speaker mode 2 (2ch stereo)',
            b'\x03': 'Speaker mode 3 (front surround)',
            b'\x04': 'Speaker mode 4 (4ch stereo)',
            b'\x05': 'Speaker mode 5 (full surround)'
        }

        self.ScreenMute = {
            b'\x00': 'Screen not muted',
            b'\x01': 'Screen signal muted'
        }

        self.ScreenActive = {
            b'\x00': 'Not active screen',
            b'\x01': 'Active screen'
        }

        self.CinemaMode = {
            b'\x00': 'Cinema mode off',
            b'\x01': 'Cinema mode on'
        }

        self.StereoIndicator = {
            b'\x00': 'Mono',
            b'\x01': 'Stereo'
        }

        self.MLNConstraints = {
            'Min': 1,
            'Max': 30
        }

        self.NetworkValues = {
            'Local Source': 0x00,
            'Remote Source': 0x01
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Beo4Command': {'Status': {}, 'Parameters': ['Destination', 'Command']},
            'BeoRemoteOneControlCommand': {'Status': {}, 'Parameters': ['Command', 'Network']},
            'BeoRemoteOneSourceSelection': {'Status': {}, 'Parameters': ['Command', 'Network']},
            'MLN': {'Status': {}},
            'Source': {'Status': {}},
            'SourceMediumPosition': {'Status': {}},
            'SourcePosition': {'Status': {}},
            'SourceActivity': {'Status': {}},
            'PictureFormat': {'Status': {}},
            'SoundStatus': {'Status': {}},
            'SpeakerMode': {'Status': {}},
            'VolumeLevel': {'Status': {}},
            'Screen1Mute': {'Status': {}},
            'Screen1Active': {'Status': {}},
            'Screen2Mute': {'Status': {}},
            'Screen2Active': {'Status': {}},
            'CinemaMode': {'Status': {}},
            'StereoIndicator': {'Status': {}},
            'LightAndControl': {'Status': {}, 'Parameters': ['Command', 'Type']},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x01\x02\x08\x00([\x01-\x1F])([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])([\x00-\x08]|\x14|\x15|\xFF)([\x00-\x06]|\xFF)'), self.MatchUnsollicited, 'SourceStatus')
            self.AddMatchString(re.compile(b'\x01\x03\x0A\x00([\x01-\x1F])(\x00|\x01)([\x01-\x05])([\x00-\x5A])(\x00|\x01)(\x00|\x01)(\x00|\x01)(\x00|\x01)(\x00|\x01)(\x00|\x01)'), self.MatchUnsollicited, 'PictureAndSoundStatus')
            self.AddMatchString(re.compile(b'\x01\x04\x03\x00([\x01-\x1F])(\x01|\x02)([\x00-\xFF])'), self.__MatchLightAndControl, None)
            self.AddMatchString(re.compile(b'\x01\x37\x00\x00'), self.__MatchPingPong, None)

    def MatchUnsollicited(self, match, tag):

        self.WriteStatus('MLN', str(ord(match.group(1))), None)
        if tag == 'SourceStatus':

            self.WriteStatus('Source', self.SourceNames.get(match.group(2), 'Not Available'), None)
            self.WriteStatus('SourceMediumPosition', ord(match.group(3)) * 256 + ord(match.group(4)), None)
            self.WriteStatus('SourcePosition', ord(match.group(5)) * 256 + ord(match.group(6)), None)
            self.WriteStatus('SourceActivity', self.SourceActivityNames.get(match.group(7), 'Not Available'), None)
            self.WriteStatus('PictureFormat', self.PictureFormatNames.get(match.group(8), 'Not Available'), None)
        elif tag == 'PictureAndSoundStatus':

            self.WriteStatus('SoundStatus', self.SoundStatusNames.get(match.group(2), 'Not Available'), None)
            self.WriteStatus('SpeakerMode', self.SpeakerMode.get(match.group(3), 'Not Available'), None)
            self.WriteStatus('VolumeLevel', ord(match.group(4)), None)
            self.WriteStatus('Screen1Mute', self.ScreenMute.get(match.group(5), 'Not Available'), None)
            self.WriteStatus('Screen1Active', self.ScreenActive.get(match.group(6), 'Not Available'), None)
            self.WriteStatus('Screen2Mute', self.ScreenMute.get(match.group(7), 'Not Available'), None)
            self.WriteStatus('Screen2Active', self.ScreenActive.get(match.group(8), 'Not Available'), None)
            self.WriteStatus('CinemaMode', self.CinemaMode.get(match.group(9), 'Not Available'), None)
            self.WriteStatus('StereoIndicator', self.StereoIndicator.get(match.group(10), 'Not Available'), None)

    def UpdatePingPong(self, value, qualifier):
        PingPongCmdString = b'\x01\x36\x00\x00'
        self.__UpdateHelper('PingPong', PingPongCmdString, value, qualifier)

    def __MatchPingPong(self, match, tag):
        self.OnConnected()

    def SetBeo4Command(self, value, qualifier):

        MLN = int(value)
        Command = qualifier['Command']
        Destination = qualifier['Destination']
        if (self.MLNConstraints['Min'] <= MLN <= self.MLNConstraints['Max'] and Command in self.CommandValues and Destination in self.DestinationValues):
            Destination = self.DestinationValues[Destination]
            Command = self.CommandValues[Command]
            CmdString = struct.pack('>BBBBBBB', 1, 1, 3, 0, MLN, Destination, Command)
            self.__SetHelper('Beo4Command', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetBeo4Command')

    def SetBeoRemoteOneControlCommand(self, value, qualifier):

        MLN = int(value)
        Command = qualifier['Command']
        Network = qualifier['Network']
        if (self.MLNConstraints['Min'] <= MLN <= self.MLNConstraints['Max'] and Command in self.CommandValues and Network in self.NetworkValues):
            Command = self.CommandValues[Command]
            Network = self.NetworkValues[Network]
            CmdString = struct.pack('>BBBBBBBB', 1, 6, 4, 0, MLN, Command, 0, Network)
            self.__SetHelper('BeoRemoteOneControlCommand', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetBeoRemoteOneControlCommand')

    def SetBeoRemoteOneSourceSelection(self, value, qualifier):

        CommandStates = {
            'TV': (0x80, 0),
            'RADIO': (0x81, 0),
            'TUNEIN': (0x81, 1),
            'DVB RADIO': (0x81, 2),
            'AV IN': (0x82, 0),
            'LINE IN': (0x83, 0),
            'A.AUX': (0x83, 1),
            'BLUETOOTH': (0x83, 2),
            'HOMEMEDIA': (0x84, 0),
            'DLNA-DMR': (0x84, 1),
            'RECORDINGS': (0x85, 0),
            'CAMERA': (0x87, 0),
            'USB': (0x90, 0),
            'USB 2': (0x90, 1),
            'A.MEM': (0x91, 0),
            'CD': (0x92, 0),
            'NET RADIO': (0x93, 0),
            'MUSIC': (0x94, 0),
            'DLNA-DMR': (0x94, 1),
            'AirPlay': (0x94, 2),
            'SPOTIFY': (0x96, 0),
            'DEEZER': (0x96, 1),
            'QPLAY': (0x96, 2),
            'JOIN (toggle)': (0x97, 0),
            'WEBMEDIA': (0x8C, 0),
            'YOUTUBE': (0x8C, 1),
            'HOME APP': (0x8C, 2),
            'HDMI 1': (0xCE, 0),
            'HDMI 2': (0xCE, 1),
            'HDMI 3': (0xCE, 2),
            'HDMI 4': (0xCE, 3),
            'HDMI 5': (0xCE, 4),
            'HDMI 6': (0xCE, 5),
            'HDMI 7': (0xCE, 6),
            'HDMI 8': (0xCE, 7),
            'MATRIX 1': (0xCF, 0),
            'MATRIX 2': (0xCF, 1),
            'MATRIX 3': (0xCF, 2),
            'MATRIX 4': (0xCF, 3),
            'MATRIX 5': (0xCF, 4),
            'MATRIX 6': (0xCF, 5),
            'MATRIX 7': (0xCF, 6),
            'MATRIX 8': (0xCF, 7),
            'MATRIX 9': (0xD0, 0),
            'MATRIX 10': (0xD0, 1),
            'MATRIX 11': (0xD0, 2),
            'MATRIX 12': (0xD0, 3),
            'MATRIX 13': (0xD0, 4),
            'MATRIX 14': (0xD0, 5),
            'MATRIX 15': (0xD0, 6),
            'MATRIX 16': (0xD0, 7),
            'PERSONAL 1': (0xD1, 0),
            'PERSONAL 2': (0xD1, 1),
            'PERSONAL 3': (0xD1, 2),
            'PERSONAL 4': (0xD1, 3),
            'PERSONAL 5': (0xD1, 4),
            'PERSONAL 6': (0xD1, 5),
            'PERSONAL 7': (0xD1, 6),
            'PERSONAL 8': (0xD1, 7),
            'TV ON': (0xD2, 0),
            'MUSIC ON': (0xD3, 0),
            'PATTERNPLAY': (0xD3, 1)
        }

        MLN = int(value)
        Command = qualifier['Command']
        Network = qualifier['Network']
        if (self.MLNConstraints['Min'] <= MLN <= self.MLNConstraints['Max'] and Command in CommandStates and Network in self.NetworkValues):
            Command = CommandStates[Command]
            Network = self.NetworkValues[Network]
            CmdString = struct.pack('>BBBBBBBBB', 1, 7, 5, 0, MLN, Command[0], Command[1], 0, Network)
            self.__SetHelper('BeoRemoteOneSourceSelection', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetBeoRemoteOneSourceSelection')

    def __MatchLightAndControl(self, match, tag):

        TypeStates = {
            b'\x01': 'Light',
            b'\x02': 'Control'
        }

        CommandStates = {
            b'\x9B': 'LIGHT',
            b'\x9C': 'CONTROL',
            b'\x00': 'DIGIT: 0',
            b'\x01': 'DIGIT: 1',
            b'\x02': 'DIGIT: 2',
            b'\x03': 'DIGIT: 3',
            b'\x04': 'DIGIT: 4',
            b'\x05': 'DIGIT: 5',
            b'\x06': 'DIGIT: 6',
            b'\x07': 'DIGIT: 7',
            b'\x08': 'DIGIT: 8',
            b'\x09': 'DIGIT: 9',
            b'\x1E': 'STEP_UP',
            b'\x1F': 'STEP_DW',
            b'\x32': 'REWIND',
            b'\x33': 'REC_RETURN / RETURN',
            b'\x34': 'WIND',
            b'\x35': 'GO / PLAY',
            b'\x36': 'STOP',
            b'\x0C': 'STANDBY',
            b'\xD4': 'CNTL_WIND / Yellow',
            b'\xD5': 'CNTL_REWIND / Green',
            b'\xD8': 'CNTL_STEP_UP / Blue',
            b'\xD9': 'CNTL_STEP_DW / Red',
            b'\x5C': 'MENU',
            b'\x14': 'BACK',
            b'\x37': 'RECORD',
            b'\xAB': 'ALL STANDBY',
            b'\x70': 'C_REWIND / Continue REWIND',
            b'\x71': 'C_WIND / Continue WIND',
            b'\x72': 'C_STEP_UP / Continue step UP',
            b'\x73': 'C_STEP_DW / Continue step DOWN',
            b'\x75': 'CONTINUE / Continue (other keys)',
            b'\x76': 'CNTL_C_REWIND / Continue Green',
            b'\x77': 'CNTL_C_WIND / Continue Yellow',
            b'\x78': 'CNTL_C_STEP_UP / Continue Blue',
            b'\x79': 'CNTL_C_STEP_DW / Continue Red',
            b'\x7E': 'KEY RELEASE',
            b'\xD6': 'CNTL_PLAY',
            b'\xD7': 'CNTL_STOP',
            b'\x13': 'SELECT / Cursor SELECT',
            b'\xCA': 'CURSOR_UP',
            b'\xCB': 'CURSOR_DW',
            b'\xCC': 'CURSOR_LEFT',
            b'\xCD': 'CURSOR_RIGHT',
            b'\x0F': 'FUNCTION_1',
            b'\x10': 'FUNCTION_2',
            b'\x11': 'FUNCTION_3',
            b'\x12': 'FUNCTION_4',
            b'\x19': 'FUNCTION_5',
            b'\x1A': 'FUNCTION_6',
            b'\x21': 'FUNCTION_7',
            b'\x22': 'FUNCTION_8',
            b'\x23': 'FUNCTION_9',
            b'\x24': 'FUNCTION_10',
            b'\x25': 'FUNCTION_11',
            b'\x26': 'FUNCTION_12',
            b'\x27': 'FUNCTION_13',
            b'\x39': 'FUNCTION_14',
            b'\x3A': 'FUNCTION_15',
            b'\x3B': 'FUNCTION_16',
            b'\x3C': 'FUNCTION_17',
            b'\x3D': 'FUNCTION_18',
            b'\x3E': 'FUNCTION_19',
            b'\x4B': 'FUNCTION_20',
            b'\x4C': 'FUNCTION_21',
            b'\x50': 'FUNCTION_22',
            b'\x51': 'FUNCTION_23',
            b'\x7D': 'FUNCTION_24',
            b'\xA5': 'FUNCTION_25',
            b'\xA6': 'FUNCTION_26',
            b'\xA9': 'FUNCTION_27',
            b'\xAA': 'FUNCTION_28',
            b'\xDD': 'FUNCTION_29',
            b'\xDE': 'FUNCTION_30',
            b'\xE0': 'FUNCTION_31',
            b'\xE1': 'FUNCTION_32',
            b'\xE2': 'FUNCTION_33',
            b'\xE6': 'FUNCTION_34',
            b'\xE7': 'FUNCTION_35',
            b'\xF2': 'FUNCTION_36',
            b'\xF3': 'FUNCTION_37',
            b'\xF4': 'FUNCTION_38',
            b'\xF5': 'FUNCTION_39',
            b'\xF6': 'FUNCTION_40'
        }

        self.WriteStatus('LightAndControl', str(ord(match.group(1))), {'Type': TypeStates[match.group(2)], 'Command': CommandStates[match.group(3)]})

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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