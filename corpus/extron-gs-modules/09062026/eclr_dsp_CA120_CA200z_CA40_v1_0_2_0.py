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
            'CA40': self.eclr_25_563_40,
            'CA200z': self.eclr_25_563_200,
            'CA120': self.eclr_25_563_120,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Bass': {'Parameters': ['Zone', 'Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemote': {'Status': {}},
            'Line1Bass': {'Status': {}},
            'Line1Treble': {'Status': {}},
            'Line1Volume': {'Status': {}},
            'Line2Bass': {'Status': {}},
            'Line2Treble': {'Status': {}},
            'Line2Volume': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MicrophoneBass': {'Status': {}},
            'MicrophoneTreble': {'Status': {}},
            'MicrophoneVolume': {'Status': {}},
            'Mute': {'Status': {}},
            'OutputMode': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Treble': {'Parameters': ['Zone', 'Input'], 'Status': {}},
            'Volume': {'Parameters': ['Zone', 'Input'], 'Status': {}},
            'ZoneInput': {'Parameters': ['Input', 'Zone'], 'Status': {}},
            'ZoneMasterVolume': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneMute': {'Parameters': ['Zone'], 'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DATA BASS (LINE1|LINE2|LINE3|LINE4|MICRO1|MICRO2) (0|2|4|6|8|10|-2|-4|-6|-8|-10) (ZA|ZB)'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'DATA PANEL_LOCKED (OFF|ON)\r?\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'DATA INPUT (LINE1|LINE2|MICL3|MICRO|LINE1_AND_MICL3|LINE1_AND_MICL3)\r?\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'DATA IR_REMOTE (ON|OFF)\r?\n'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'DATA LINE1_BASS (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchLine1Bass, None)
            self.AddMatchString(re.compile(b'DATA LINE1_TREBLE (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchLine1Treble, None)
            self.AddMatchString(re.compile(b'DATA LINE1_VOL ([0-9]|[1-5][0-9]|6[0-4])\r?\n'), self.__MatchLine1Volume, None)
            self.AddMatchString(re.compile(b'DATA LINE2_BASS (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchLine2Bass, None)
            self.AddMatchString(re.compile(b'DATA LINE2_TREBLE (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchLine2Treble, None)
            self.AddMatchString(re.compile(b'DATA LINE2_VOL ([0-9]|[1-5][0-9]|6[0-4])\r?\n'), self.__MatchLine2Volume, None)
            self.AddMatchString(re.compile(b'DATA MASTER_VOL ([0-9]|[1-5][0-9]|6[0-4])\r?\n'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'DATA (MICL3|MICRO)_BASS (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchMicrophoneBass, None)
            self.AddMatchString(re.compile(b'DATA (MICL3|MICRO)_TREBLE (0|2|4|6|8|10|-2|-4|-6|-8|-10)'), self.__MatchMicrophoneTreble, None)
            self.AddMatchString(re.compile(b'DATA (MICL3|MICRO)_VOL ([0-9]|[1-5][0-9]|6[0-4])\r?\n'), self.__MatchMicrophoneVolume, None)
            self.AddMatchString(re.compile(b'DATA MUTE (ON|OFF)\r?\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'DATA OUTPUT_MODE (STEREO|MONO|BRIDGE|ZONES)\r?\n'), self.__MatchOutputMode, None)
            self.AddMatchString(re.compile(b'DATA POWER (ON|STANDBY)\r?\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'DATA PRESET_NUMBER (1|2|3|4|5)\r?\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'DATA TREBLE (LINE1|LINE2|LINE3|LINE4|MICRO1|MICRO2) (0|2|4|6|8|10|-2|-4|-6|-8|-10) (ZA|ZB)'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'DATA VOL (LINE1|LINE2|LINE3|LINE4|MICRO1|MICRO2) ([0-9]|[1-5][0-9]|6[0-4]) (ZA|ZB)'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'DATA INPUT (LINE1|LINE2|LINE3|LINE4|MICRO1|MICRO2) (ON|OFF) (ZA|ZB)'), self.__MatchZoneInput, None)
            self.AddMatchString(re.compile(b'DATA MASTER_VOL ([0-9]|[1-5][0-9]|6[0-4]) (ZA|ZB)'), self.__MatchZoneMasterVolume, None)
            self.AddMatchString(re.compile(b'DATA MUTE (ON|OFF) (ZA|ZB)'), self.__MatchZoneMute, None)
            self.AddMatchString(re.compile(b'ERROR (\d+?).*?\r?\n'), self.__MatchError, None)

    def SetBass(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }
        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BassCmdString = 'SET BASS {0} {1} {2}\n'.format(Input, value, Zone)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
 

    def UpdateBass(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        BassCmdString = 'GET BASS {0} {1}\n'.format(Input, Zone)
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        ZoneStates = {
            'ZA': 'A',
            'ZB': 'B'
        }

        InputStates = {
            'LINE1': 'Line 1',
            'LINE2': 'Line 2',
            'LINE3': 'Line 3',
            'LINE4': 'Line 4',
            'MICRO1': 'Mic 1',
            'MICRO2': 'Mic 2'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        qualifier['Input'] = InputStates[match.group(2).decode()]
        value = int(match.group(3).decode())
        self.WriteStatus('Bass', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'PANEL_LOCKED ON',
            'Off': 'PANEL_LOCKED OFF'
        }

        ExecutiveModeCmdString = 'SET {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'GET PANEL_LOCKED\n'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = 'SET {0}\n'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GET INPUT\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetIRRemote(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        IRRemoteCmdString = 'SET IR_REMOTE {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('IRRemote', IRRemoteCmdString, value, qualifier)

    def UpdateIRRemote(self, value, qualifier):

        IRRemoteCmdString = 'GET IR_REMOTE\n'
        self.__UpdateHelper('IRRemote', IRRemoteCmdString, value, qualifier)

    def __MatchIRRemote(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('IRRemote', value, None)

    def SetLine1Bass(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line1BassCmdString = 'SET LINE1_BASS {0}\n'.format(value)
            self.__SetHelper('Line1Bass', Line1BassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine1Bass')

    def UpdateLine1Bass(self, value, qualifier):

        Line1BassCmdString = 'GET LINE1_BASS\n'
        self.__UpdateHelper('Line1Bass', Line1BassCmdString, value, qualifier)

    def __MatchLine1Bass(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line1Bass', value, None)

    def SetLine1Treble(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line1TrebleCmdString = 'SET LINE1_TREBLE {0}\n'.format(value)
            self.__SetHelper('Line1Treble', Line1TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine1Treble')

    def UpdateLine1Treble(self, value, qualifier):

        Line1TrebleCmdString = 'GET LINE1_TREBLE\n'
        self.__UpdateHelper('Line1Treble', Line1TrebleCmdString, value, qualifier)

    def __MatchLine1Treble(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line1Treble', value, None)

    def SetLine1Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 64
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line1VolumeCmdString = 'SET LINE1_VOL {0}\n'.format(value)
            self.__SetHelper('Line1Volume', Line1VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine1Volume')

    def UpdateLine1Volume(self, value, qualifier):

        Line1VolumeCmdString = 'GET LINE1_VOL\n'
        self.__UpdateHelper('Line1Volume', Line1VolumeCmdString, value, qualifier)

    def __MatchLine1Volume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line1Volume', value, None)

    def SetLine2Bass(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line2BassCmdString = 'SET LINE2_BASS {0}\n'.format(value)
            self.__SetHelper('Line2Bass', Line2BassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine2Bass')

    def UpdateLine2Bass(self, value, qualifier):

        Line2BassCmdString = 'GET LINE2_BASS\n'
        self.__UpdateHelper('Line2Bass', Line2BassCmdString, value, qualifier)

    def __MatchLine2Bass(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line2Bass', value, None)

    def SetLine2Treble(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line2TrebleCmdString = 'SET LINE2_TREBLE {0}\n'.format(value)
            self.__SetHelper('Line2Treble', Line2TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine2Treble')

    def UpdateLine2Treble(self, value, qualifier):

        Line2TrebleCmdString = 'GET LINE2_TREBLE\n'
        self.__UpdateHelper('Line2Treble', Line2TrebleCmdString, value, qualifier)

    def __MatchLine2Treble(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line2Treble', value, None)

    def SetLine2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 64
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line2VolumeCmdString = 'SET LINE2_VOL {0}\n'.format(value)
            self.__SetHelper('Line2Volume', Line2VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLine2Volume')

    def UpdateLine2Volume(self, value, qualifier):

        Line2VolumeCmdString = 'GET LINE2_VOL\n'
        self.__UpdateHelper('Line2Volume', Line2VolumeCmdString, value, qualifier)

    def __MatchLine2Volume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Line2Volume', value, None)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 64
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = 'SET MASTER_VOL {0}\n'.format(value)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'GET MASTER_VOL\n'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('MasterVolume', value, None)

    def SetMicrophoneBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneBassCmdString = 'SET {0}_BASS {1}\n'.format(self.mic, value)
            self.__SetHelper('MicrophoneBass', MicrophoneBassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicrophoneBass')

    def UpdateMicrophoneBass(self, value, qualifier):

        MicrophoneBassCmdString = 'GET {0}_BASS\n'.format(self.mic)
        self.__UpdateHelper('MicrophoneBass', MicrophoneBassCmdString, value, qualifier)

    def __MatchMicrophoneBass(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('MicrophoneBass', value, None)

    def SetMicrophoneTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneTrebleCmdString = 'SET {0}_TREBLE {1}\n'.format(self.mic, value)
            self.__SetHelper('MicrophoneTreble', MicrophoneTrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicrophoneTreble')

    def UpdateMicrophoneTreble(self, value, qualifier):

        MicrophoneTrebleCmdString = 'GET {0}_TREBLE\n'.format(self.mic)
        self.__UpdateHelper('MicrophoneTreble', MicrophoneTrebleCmdString, value, qualifier)

    def __MatchMicrophoneTreble(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('MicrophoneTreble', value, None)

    def SetMicrophoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 64
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneVolumeCmdString = 'SET {0}_VOL {1}\n'.format(self.mic, value)

            self.__SetHelper('MicrophoneVolume', MicrophoneVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicrophoneVolume')

    def UpdateMicrophoneVolume(self, value, qualifier):

        MicrophoneVolumeCmdString = 'GET {0}_VOL\n'.format(self.mic)
        self.__UpdateHelper('MicrophoneVolume', MicrophoneVolumeCmdString, value, qualifier)

    def __MatchMicrophoneVolume(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('MicrophoneVolume', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE ON',
            'Off': 'MUTE OFF'
        }

        MuteCmdString = 'SET {0}\n'.format(ValueStateValues[value])

        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'GET MUTE\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Stereo': 'STEREO',
            'Mono': 'MONO',
            'Bridge': 'BRIDGE',
            'Zones': 'ZONES'
        }

        OutputModeCmdString = 'SET OUTPUT_MODE {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('OutputMode', OutputModeCmdString, value, qualifier)

    def UpdateOutputMode(self, value, qualifier):

        OutputModeCmdString = 'GET OUTPUT_MODE\n'
        self.__UpdateHelper('OutputMode', OutputModeCmdString, value, qualifier)

    def __MatchOutputMode(self, match, tag):

        ValueStateValues = {
            'STEREO': 'Stereo',
            'MONO': 'Mono',
            'BRIDGE': 'Bridge',
            'ZONES': 'Zones'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Standby': 'STANDBY'
        }

        PowerCmdString = 'SET POWER {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET POWER\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'STANDBY': 'Standby'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        PresetRecallCmdString = 'SET LOAD_PRESET {0}\n' .format(ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'GET PRESET_NUMBER\n'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        PresetSaveCmdString = 'SET SAVE_PRESET {0}\n' .format(ValueStateValues[value])
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetTreble(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        ValueConstraints = {
            'Min': -10,
            'Max': 10
            }

        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrebleCmdString = 'SET TREBLE {0} {1} {2}\n'.format(Input, value, Zone)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }
        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        TrebleCmdString = 'GET TREBLE {0} {1}\n'.format(Input, Zone)
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        ZoneStates = {
            'ZA': 'A',
            'ZB': 'B'
        }

        InputStates = {
            'LINE1': 'Line 1',
            'LINE2': 'Line 2',
            'LINE3': 'Line 3',
            'LINE4': 'Line 4',
            'MICRO1': 'Mic 1',
            'MICRO2': 'Mic 2'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(3).decode()]
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('Treble', value, qualifier)

    def SetVolume(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 64
            }
        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'SET VOL {0} {1} {2}\n'.format(Input, value, Zone)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }
        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        VolumeCmdString = 'GET VOL {0} {1}\n'.format(Input, Zone)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        ZoneStates = {
            'ZA': 'A',
            'ZB': 'B'
        }

        InputStates = {
            'LINE1': 'Line 1',
            'LINE2': 'Line 2',
            'LINE3': 'Line 3',
            'LINE4': 'Line 4',
            'MICRO1': 'Mic 1',
            'MICRO2': 'Mic 2'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(3).decode()]
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, qualifier)

    def SetZoneInput(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        ZoneInputCmdString = 'SET INPUT {0} {1} {2}\n'.format(Input, ValueStateValues[value], Zone)
        self.__SetHelper('ZoneInput', ZoneInputCmdString, value, qualifier)

    def UpdateZoneInput(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        InputStates = {
            'Line 1': 'LINE1',
            'Line 2': 'LINE2',
            'Line 3': 'LINE3',
            'Line 4': 'LINE4',
            'Mic 1': 'MICRO1',
            'Mic 2': 'MICRO2'
        }

        Zone = ZoneStates[qualifier['Zone']]
        Input = InputStates[qualifier['Input']]
        ZoneInputCmdString = 'GET INPUT {0} {1}\n'.format(Input, Zone)
        self.__UpdateHelper('ZoneInput', ZoneInputCmdString, value, qualifier)

    def __MatchZoneInput(self, match, tag):

        ZoneStates = {
                    'ZA': 'A',
                    'ZB': 'B'
                    }
        InputStates = {
            'LINE1': 'Line 1',
            'LINE2': 'Line 2',
            'LINE3': 'Line 3',
            'LINE4': 'Line 4',
            'MICRO1': 'Mic 1',
            'MICRO2': 'Mic 2'
            }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        qualifier['Zone'] = ZoneStates[match.group(3).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ZoneInput', value, qualifier)

    def SetZoneMasterVolume(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 64
        }

        Zone = ZoneStates[qualifier['Zone']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoneMasterVolumeCmdString = 'SET MASTER_VOL {0} {1}\n'.format(value, Zone)
            self.__SetHelper('ZoneMasterVolume', ZoneMasterVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneMasterVolume')

    def UpdateZoneMasterVolume(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        Zone = ZoneStates[qualifier['Zone']]
        ZoneMasterVolumeCmdString = 'GET MASTER_VOL {0}\n'.format(Zone)
        self.__UpdateHelper('ZoneMasterVolume', ZoneMasterVolumeCmdString, value, qualifier)

    def __MatchZoneMasterVolume(self, match, tag):

        ZoneStates = {
            'ZA': 'A',
            'ZB': 'B'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(2).decode()]
        value = int(match.group(1).decode())
        self.WriteStatus('ZoneMasterVolume', value, qualifier)

    def SetZoneMute(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        ValueStateValues = {
            'On': 'MUTE ON',
            'Off': 'MUTE OFF'
        }
        Zone = ZoneStates[qualifier['Zone']]
        ZoneMuteCmdString = 'SET {0} {1}\n'.format(ValueStateValues[value], Zone)
        self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)

    def UpdateZoneMute(self, value, qualifier):

        ZoneStates = {
            'A': 'ZA',
            'B': 'ZB'
        }

        Zone = ZoneStates[qualifier['Zone']]
        ZoneMuteCmdString = 'GET MUTE {0}\n'.format(Zone)
        self.__UpdateHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)

    def __MatchZoneMute(self, match, tag):

        ZoneStates = {
            'ZA': 'A',
            'ZB': 'B'
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(2).decode()]
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ZoneMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        value = match.group(0).decode()
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def eclr_25_563_40(self):
        
        self.mic = 'MICRO'
        self.InputStateValues = {
            'Line 1'         : 'INPUT LINE1', 
            'Line 2'         : 'INPUT LINE2', 
            'Microphone'     : 'INPUT MICRO', 
            'Line 1 and Mic' : 'INPUT LINE1_AND_MICRO', 
            'Line 2 and Mic' : 'INPUT LINE2_AND_MICRO'
        }
        self.InputStateNames = {
            'LINE1' : 'Line 1', 
            'LINE2' : 'Line 2', 
            'MICRO' : 'Microphone', 
            'LINE1_AND_MICRO' : 'Line 1 and Mic', 
            'LINE2_AND_MICRO' : 'Line 2 and Mic', 
        }

    def eclr_25_563_120(self):

        self.mic = 'MICL3'
        self.InputStateValues = {
            'Line 1'         : 'INPUT LINE1', 
            'Line 2'         : 'INPUT LINE2', 
            'Microphone'     : 'INPUT MICL3', 
            'Line 1 and Mic' : 'INPUT LINE1_AND_MICL3', 
            'Line 2 and Mic' : 'INPUT LINE2_AND_MICL3'
        }
        
        self.InputStateNames = {
            'LINE1' : 'Line 1', 
            'LINE2' : 'Line 2', 
            'MICL3' : 'Microphone', 
            'LINE1_AND_MICRO' : 'Line 1 and Mic', 
            'LINE2_AND_MICRO' : 'Line 2 and Mic', 
        }
        
    def eclr_25_563_200(self):

        self.InputStateValues = {
            'Line 1'         : 'INPUT LINE1', 
            'Line 2'         : 'INPUT LINE2', 
            'Microphone'     : 'INPUT MICL3', 
            'Line 1 and Mic' : 'INPUT LINE1_AND_MICL3', 
            'Line 2 and Mic' : 'INPUT LINE2_AND_MICL3'
        }
        
        self.InputStateNames = {
            'LINE1' : 'Line 1', 
            'LINE2' : 'Line 2', 
            'MICL3' : 'Microphone', 
            'LINE1_AND_MICRO' : 'Line 1 and Mic', 
            'LINE2_AND_MICRO' : 'Line 2 and Mic', 
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
