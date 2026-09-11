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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'SC-75': self.pion_27_1093_75,
            'SC-72': self.pion_27_1093_72,
            }
       
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Bass': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'ListeningMode': { 'Status': {}},
            'MainMute': { 'Status': {}},
            'MainPower': { 'Status': {}},
            'MainVolume': { 'Status': {}},
            'RemoteLock': { 'Status': {}},
            'Resolution': { 'Status': {}},
            'Treble': { 'Status': {}},
            'TunerBand': { 'Status': {}},
            'TunerFrequency': { 'Status': {}},
            'TunerFrequencyStatus': { 'Status': {}},
            'TunerPreset': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone3Input': { 'Status': {}},
            'ZoneHDInput': { 'Status': {}},
            'ZoneMute': {'Parameters': ['Zone'], 'Status': {}},
            'ZonePower': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneVolume': {'Parameters': ['Zone'], 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'BA(\d{2})\r\n'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'PKL([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'FN(\d{2})\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'SR(\d{4})\r\n'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'PWR([01])\r\n'), self.__MatchMainPower, None)
            self.AddMatchString(re.compile(b'VOL(\d{3})\r\n'), self.__MatchMainVolume, None)
            self.AddMatchString(re.compile(b'RML([01])\r\n'), self.__MatchRemoteLock, None)
            self.AddMatchString(re.compile(b'VTC(\d{2})\r\n'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(b'TR(\d{2})\r\n'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'FR([AF])(\d{5})\r\n'), self.__MatchTunerFrequencyStatus, None)
            self.AddMatchString(re.compile(b'Z2F(\d{2})\r\n'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z3F(\d{2})\r\n'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'ZEA(\d{2})\r\n'), self.__MatchZoneHDInput, None)
            self.AddMatchString(re.compile(b'Z([23])MUT([01])\r\n'), self.__MatchZoneMute, None)
            self.AddMatchString(re.compile(b'^MUT([01])\r\n'), self.__MatchMainMute, None)
            self.AddMatchString(re.compile(b'(APR|BPR|ZEP)([01])\r\n'), self.__MatchZonePower, None)
            self.AddMatchString(re.compile(b'(ZV|YV)(\d{2})\r\n'), self.__MatchZoneVolume, None)
            self.AddMatchString(re.compile(b'(E02|E03|E04|E06|B00)\r\n'), self.__MatchError, None)

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max':  6
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BassCmdString = '{0:02}BA\r'.format(6 - value)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '?BA\r'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = int(match.group(1).decode())
        value = 6 - value
        self.WriteStatus('Bass', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':      '0',
            'Mode 1':   '1',
            'Mode 2':   '2'
        }

        ExecutiveModeCmdString = '{}PKL\r'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '?PKL\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):


        InputCmdString = '{}FN\r'.format(self._set_input_states[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '?F\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self._update_input_states[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ListeningModeCmdString = '{}SR\r'.format(self._set_listening_mode_states[value])
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

        ListeningModeCmdString = '?S\r'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        value = self._update_listening_mode_states[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMainMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        MainMuteCmdString = 'M{}\r'.format(ValueStateValues[value])
        self.__SetHelper('MainMute', MainMuteCmdString, value, qualifier)

    def UpdateMainMute(self, value, qualifier):

        MainMuteCmdString = '?M\r'
        self.__UpdateHelper('MainMute', MainMuteCmdString, value, qualifier)

    def __MatchMainMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainMute', value, None)

    def SetMainPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        MainPowerCmdString = 'P{}\r'.format(ValueStateValues[value])
        self.__SetHelper('MainPower', MainPowerCmdString, value, qualifier)

    def UpdateMainPower(self, value, qualifier):


        MainPowerCmdString = '?P\r'
        self.__UpdateHelper('MainPower', MainPowerCmdString, value, qualifier)

    def __MatchMainPower(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainPower', value, None)

    def SetMainVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max':  12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MainVolumeCmdString = '{0:03}VL\r'.format(int((80.5 + value) * 2))
            self.__SetHelper('MainVolume', MainVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainVolume')

    def UpdateMainVolume(self, value, qualifier):

        MainVolumeCmdString = '?V\r'
        self.__UpdateHelper('MainVolume', MainVolumeCmdString, value, qualifier)

    def __MatchMainVolume(self, match, tag):

        value = int(match.group(1).decode())
        value = value / 2 - 80.5
        self.WriteStatus('MainVolume', value, None)

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        RemoteLockCmdString = '{}RML\r'.format(ValueStateValues[value])
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = '?RML\r'
        self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def __MatchRemoteLock(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RemoteLock', value, None)

    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto':     '00',
            'Pure':     '01',
            'Reserved': '02',
            '480/576p': '03',
            '720p':     '04',
            '1080i':    '05',
            '1080p':    '06',
            '1080/24p': '07',
            '4K':       '08',
            '4K/24p':   '09'
        }

        ResolutionCmdString = '{}VTC\r'.format(ValueStateValues[value])
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        ResolutionCmdString = '?VTC\r'
        self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        ValueStateValues = {
            '00': 'Auto',
            '01': 'Pure',
            '02': 'Reserved',
            '03': '480/576p',
            '04': '720p',
            '05': '1080i',
            '06': '1080p',
            '07': '1080/24p',
            '08': '4K',
            '09': '4K/24p'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max':  6
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrebleCmdString = '{0:02}TR\r'.format(6 - value)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '?TR\r'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = int(match.group(1).decode())
        value = 6 - value
        self.WriteStatus('Treble', value, None)

    def SetTunerBand(self, value, qualifier):

        ValueStateValues = {
            'AM': '01',
            'FM': '00'
        }

        TunerBandCmdString = '{}TN\r'.format(ValueStateValues[value])
        self.__SetHelper('TunerBand', TunerBandCmdString, value, qualifier)
    def SetTunerFrequency(self, value, qualifier):

        ValueStateValues = {
            'Increment': 'I',
            'Decrement': 'D'
        }

        TunerFrequencyCmdString = 'TF{}\r'.format(ValueStateValues[value])
        self.__SetHelper('TunerFrequency', TunerFrequencyCmdString, value, qualifier)
    def UpdateTunerFrequencyStatus(self, value, qualifier):

        TunerFrequencyStatusCmdString = '?FR\r'
        self.__UpdateHelper('TunerFrequencyStatus', TunerFrequencyStatusCmdString, value, qualifier)

    def __MatchTunerFrequencyStatus(self, match, tag):

        freq = match.group(1).decode()
        band = match.group(2).decode()

        if freq == 'A':
            value = "AM {0}kHz".format(int(band))
        else:
            value = "FM {0}MHz".format(int(band) / 100)

        self.WriteStatus('TunerFrequencyStatus', value, None)

    def SetTunerPreset(self, value, qualifier):

        if 1 <= int(value) <= 10:
            TunerPresetCmdString = '{}TP\r'.format(int(value) - 1)
            self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTunerPreset')
    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'Internet Radio':   '38',
            'Pandora':          '41',
            'Media Server':     '44',
            'Favorites':        '45',
            'iPod/USB':         '17',
            'TV':               '05',
            'CD':               '01',
            'Tuner':            '02',
            'Adapter Port':     '33',
            'DVD':              '04',
            'SAT/CBL':          '06',
            'DVR/BDR':          '15',
            'Video':            '10',
        }

        Zone2InputCmdString = '{}ZS\r'.format(ValueStateValues[value])
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '?ZS\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            '38': 'Internet Radio',
            '41': 'Pandora',
            '44': 'Media Server',
            '45': 'Favorites',
            '17': 'iPod/USB',
            '05': 'TV',
            '01': 'CD',
            '02': 'Tuner',
            '33': 'Adapter Port',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video',
            '99': 'Multi-ZONE Music'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone3Input(self, value, qualifier):

        ValueStateValues = {
            'TV':           '05',
            'CD':           '01',
            'Tuner':        '02',
            'Adapter Port': '33',
            'DVD':          '04',
            'SAT/CBL':      '06',
            'DVR/BDR':      '15',
            'Video':        '10'
        }

        Zone3InputCmdString = '{}ZT\r'.format(ValueStateValues[value])
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = '?ZT\r'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):

        ValueStateValues = {
            '05': 'TV',
            '01': 'CD',
            '02': 'Tuner',
            '33': 'Adapter Port',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video',
            '99': 'Multi-ZONE Music'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Input', value, None)

    def SetZoneHDInput(self, value, qualifier):

        ZoneHDInputCmdString = '{}ZEA\r'.format(self._set_zone_hd_input_states[value])
        self.__SetHelper('ZoneHDInput', ZoneHDInputCmdString, value, qualifier)

    def UpdateZoneHDInput(self, value, qualifier):

        ZoneHDInputCmdString = '?ZEA\r'
        self.__UpdateHelper('ZoneHDInput', ZoneHDInputCmdString, value, qualifier)

    def __MatchZoneHDInput(self, match, tag):

        value = self._update_zone_hd_input_states[match.group(1).decode()]
        self.WriteStatus('ZoneHDInput', value, None)

    def SetZoneMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if qualifier['Zone'] in {'2', '3'}:
            ZoneMuteCmdString = 'Z{}M{}\r'.format(qualifier['Zone'], ValueStateValues[value])
            self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneMute')

    def UpdateZoneMute(self, value, qualifier):

        if qualifier['Zone'] in {'2', '3'}:
            ZoneMuteCmdString = '?Z{}M\r'.format(qualifier['Zone'])
            self.__UpdateHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneMute')

    def __MatchZoneMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        zone = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]

        self.WriteStatus('ZoneMute', value, {'Zone': zone})

    def SetZonePower(self, value, qualifier):

        ZoneStates = {
            '2':    'AP',
            '3':    'BP',
            'HD':   'ZE'
        }

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if qualifier['Zone'] in ZoneStates:
            ZonePowerCmdString = '{}{}\r'.format(ZoneStates[qualifier['Zone']], ValueStateValues[value])
            self.__SetHelper('ZonePower', ZonePowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZonePower')

    def UpdateZonePower(self, value, qualifier):

        ZoneStates = {
            '2':    'AP',
            '3':    'BP',
            'HD':   'ZEP'
        }

        if qualifier['Zone'] in ZoneStates:
            ZonePowerCmdString = '?{}\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('ZonePower', ZonePowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZonePower')

    def __MatchZonePower(self, match, tag):

        ZoneStates = {
            'APR':  '2',
            'BPR':  '3',
            'ZEP':  'HD'
        }

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Zone': ZoneStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ZonePower', value, qualifier)

    def SetZoneVolume(self, value, qualifier):

        ZoneStates = {
            '2': 'ZV',
            '3': 'YV'
        }

        ValueConstraints = {
            'Min': -80,
            'Max':   0
        }

        if qualifier['Zone'] in ZoneStates and (ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            ZoneVolumeCmdString = '{:02}{}\r'.format(value + 81, ZoneStates[qualifier['Zone']])
            self.__SetHelper('ZoneVolume', ZoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneVolume')

    def UpdateZoneVolume(self, value, qualifier):

        ZoneStates = {
            '2': 'ZV',
            '3': 'YV'
        }

        if qualifier['Zone'] in ZoneStates:
            ZoneVolumeCmdString = '?{}\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('ZoneVolume', ZoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneVolume')

    def __MatchZoneVolume(self, match, tag):

        ZoneStates = {
            'ZV': '2',
            'YV': '3'
        }

        qualifier = {'Zone': ZoneStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        value -= 81
        self.WriteStatus('ZoneVolume', value, qualifier)

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

    def __MatchError(self, match, tag):
        self.counter = 0

        error_map = {
             'E02': 'NOT AVAILABLE NOW',
             'E03': 'INVALID COMMAND',
             'E04': 'COMMAND ERROR',
             'E06': 'PARAMETER ERROR',
             'B00': 'BUSY',
        }

        value = match.group(1).decode()
        self.Error(['An error occurred: {}'.format(error_map.get(value, 'UNKNOWN ERROR'))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pion_27_1093_72(self):
        self._set_input_states = {
            'Blu-ray':          '25',
            'HDMI 1':           '19',
            'HDMI 2':           '20',
            'HDMI 3':           '21',
            'HDMI 4':           '22',
            'HDMI 5':           '23',
            'HDMI 6':           '24',
            'HDMI 7':           '34',
            'Internet Radio':   '38',
            'Pandora':          '41',
            'Media Server':     '44',
            'Favorites':        '45',
            'iPod/USB':         '17',
            'TV':               '05',
            'CD':               '01',
            'Tuner':            '02',
            'Adapter Port':     '33',
            'MHL':              '48',
            'DVD':              '04',
            'SAT/CBL':          '06',
            'DVR/BDR':          '15',
            'Video':            '10'
        }

        self._update_input_states = {
            '25': 'Blu-ray',
            '19': 'HDMI 1',
            '20': 'HDMI 2',
            '21': 'HDMI 3',
            '22': 'HDMI 4',
            '23': 'HDMI 5',
            '24': 'HDMI 6',
            '34': 'HDMI 7',
            '38': 'Internet Radio',
            '41': 'Pandora',
            '44': 'Media Server',
            '45': 'Favorites',
            '17': 'iPod/USB',
            '05': 'TV',
            '01': 'CD',
            '02': 'Tuner',
            '33': 'Adapter Port',
            '48': 'MHL',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video'
        }

        self._set_listening_mode_states = {
            'STEREO (direct set)':                      '0009',
            'PRO LOGIC2 MOVIE':                         '0013',
            'PRO LOGIC2x MOVIE':                        '0018',
            'PRO LOGIC2 MUSIC':                         '0014',
            'PRO LOGIC2x MUSIC':                        '0019',
            'PRO LOGIC2 GAME':                          '0015',
            'PRO LOGIC2x GAME':                         '0020',
            'PRO LOGIC2z HEIGHT':                       '0031',
            'WIDE SURROUND MOVIE':                      '0032',
            'WIDE SURROUND MUSIC':                      '0033',
            'PRO LOGIC':                                '0012',
            'Neo:X CINEMA':                             '0037',
            'Neo:X MUSIC':                              '0038',
            'Neo:X GAME':                               '0039',
            '(Multi ch source)':                        '0021',
            '(Multi ch source)+DOLBY EX':               '0022',
            '(Multi ch source)+PRO LOGIC2x MOVIE':      '0023',
            '(Multi ch source)+PRO LOGIC2x MUSIC':      '0024',
            '(Multi-ch Source)+PRO LOGIC2z HEIGHT':     '0034',
            '(Multi-ch Source)+WIDE SURROUND MOVIE':    '0035',
            '(Multi-ch Source)+WIDE SURROUND MUSIC':    '0036',
            '(Multi ch source)DTS-ES matrix':           '0026',
            '(Multi ch source)DTS-ES discrete':         '0027',
            '(Multi ch source)DTS-ES 8ch discrete':     '0030',
            '(Multi ch source)+Neo:X CINEMA':           '0043',
            '(Multi ch source)+Neo:X MUSIC':            '0044',
            '(Multi ch source)+Neo:X GAME':             '0045',
            'ACTION':                                   '0101',
            'DRAMA':                                    '0103',
            'ADVANCED GAME':                            '0118',
            'SPORTS':                                   '0117',
            'CLASSICAL':                                '0107',
            'ROCK/POP':                                 '0110',
            'EXTENDED STEREO':                          '0112',
            'Front Stage Surround Advance':             '0003',
            'ECO MODE 1':                               '0212',
            'ECO MODE 2':                               '0213',
            'RETRIEVER AIR':                            '0153',
            'PHONES SURROUND':                          '0113',
            'AUTO SURROUND':                            '0005',
            'Auto Level Control (A.L.C.)':              '0151',
            'DIRECT':                                   '0007',
            'PURE DIRECT':                              '0008'
        }

        self._update_listening_mode_states = {
            '0009': 'STEREO (direct set)',
            '0013': 'PRO LOGIC2 MOVIE',
            '0018': 'PRO LOGIC2x MOVIE',
            '0014': 'PRO LOGIC2 MUSIC',
            '0019': 'PRO LOGIC2x MUSIC',
            '0015': 'PRO LOGIC2 GAME',
            '0020': 'PRO LOGIC2x GAME',
            '0031': 'PRO LOGIC2z HEIGHT',
            '0032': 'WIDE SURROUND MOVIE',
            '0033': 'WIDE SURROUND MUSIC',
            '0012': 'PRO LOGIC',
            '0037': 'Neo:X CINEMA',
            '0038': 'Neo:X MUSIC',
            '0039': 'Neo:X GAME',
            '0021': '(Multi ch source)',
            '0022': '(Multi ch source)+DOLBY EX',
            '0023': '(Multi ch source)+PRO LOGIC2x MOVIE',
            '0024': '(Multi ch source)+PRO LOGIC2x MUSIC',
            '0034': '(Multi-ch Source)+PRO LOGIC2z HEIGHT',
            '0035': '(Multi-ch Source)+WIDE SURROUND MOVIE',
            '0036': '(Multi-ch Source)+WIDE SURROUND MUSIC',
            '0026': '(Multi ch source)DTS-ES matrix',
            '0027': '(Multi ch source)DTS-ES discrete',
            '0030': '(Multi ch source)DTS-ES 8ch discrete',
            '0043': '(Multi ch source)+Neo:X CINEMA',
            '0044': '(Multi ch source)+Neo:X MUSIC',
            '0045': '(Multi ch source)+Neo:X GAME',
            '0101': 'ACTION',
            '0103': 'DRAMA',
            '0118': 'ADVANCED GAME',
            '0117': 'SPORTS',
            '0107': 'CLASSICAL',
            '0110': 'ROCK/POP',
            '0112': 'EXTENDED STEREO',
            '0003': 'Front Stage Surround Advance',
            '0212': 'ECO MODE 1',
            '0213': 'ECO MODE 2',
            '0153': 'RETRIEVER AIR',
            '0113': 'PHONES SURROUND',
            '0005': 'AUTO SURROUND',
            '0151': 'Auto Level Control (A.L.C.)',
            '0007': 'DIRECT',
            '0008': 'PURE DIRECT'
        }

        self._set_zone_hd_input_states = {
            'Blu-ray':  '25',
            'HDMI 1':   '19',
            'HDMI 2':   '20',
            'HDMI 3':   '21',
            'HDMI 4':   '22',
            'HDMI 5':   '23',
            'HDMI 6':   '24',
            'HDMI 7':   '34',
            'MHL':      '48',
            'DVD':      '04',
            'SAT/CBL':  '06',
            'DVR/BDR':  '15',
            'Video':    '10'
        }

        self._update_zone_hd_input_states = {
            '25': 'Blu-ray',
            '19': 'HDMI 1',
            '20': 'HDMI 2',
            '21': 'HDMI 3',
            '22': 'HDMI 4',
            '23': 'HDMI 5',
            '24': 'HDMI 6',
            '34': 'HDMI 7',
            '48': 'MHL',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video'
        }



    def pion_27_1093_75(self):
        self._set_input_states = {
            'Blu-ray':          '25',
            'HDMI 1':           '19',
            'HDMI 2':           '20',
            'HDMI 3':           '21',
            'HDMI 4':           '22',
            'HDMI 5':           '23',
            'HDMI 6':           '24',
            'HDMI 7':           '34',
            'HDMI 8':           '35',
            'Internet Radio':   '38',
            'Pandora':          '41',
            'Media Server':     '44',
            'Favorites':        '45',
            'iPod/USB':         '17',
            'TV':               '05',
            'CD':               '01',
            'Tuner':            '02',
            'Adapter Port':     '33',
            'MHL':              '48',
            'DVD':              '04',
            'SAT/CBL':          '06',
            'DVR/BDR':          '15',
            'Video':            '10'
        }

        self._update_input_states = {
            '25': 'Blu-ray',
            '19': 'HDMI 1',
            '20': 'HDMI 2',
            '21': 'HDMI 3',
            '22': 'HDMI 4',
            '23': 'HDMI 5',
            '24': 'HDMI 6',
            '34': 'HDMI 7',
            '35': 'HDMI 8',
            '38': 'Internet Radio',
            '41': 'Pandora',
            '44': 'Media Server',
            '45': 'Favorites',
            '17': 'iPod/USB',
            '05': 'TV',
            '01': 'CD',
            '02': 'Tuner',
            '33': 'Adapter Port',
            '48': 'MHL',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video'
        }

        self._set_listening_mode_states = {
            'STEREO (direct set)':                          '0009',
            'PRO LOGIC2 MOVIE':                             '0013',
            'PRO LOGIC2x MOVIE':                            '0018',
            'PRO LOGIC2 MUSIC':                             '0014',
            'PRO LOGIC2x MUSIC':                            '0019',
            'PRO LOGIC2 GAME':                              '0015',
            'PRO LOGIC2x GAME':                             '0020',
            'PRO LOGIC2z HEIGHT':                           '0031',
            'WIDE SURROUND MOVIE':                          '0032',
            'WIDE SURROUND MUSIC':                          '0033',
            'PRO LOGIC':                                    '0012',
            'Neo:X CINEMA':                                 '0037',
            'Neo:X MUSIC':                                  '0038',
            'Neo:X GAME':                                   '0039',
            '(Multi ch source)':                            '0021',
            '(Multi ch source)+DOLBY EX':                   '0022',
            '(Multi ch source)+PRO LOGIC2x MOVIE':          '0023',
            '(Multi ch source)+PRO LOGIC2x MUSIC':          '0024',
            '(Multi-ch Source)+PRO LOGIC2z HEIGHT':         '0034',
            '(Multi-ch Source)+WIDE SURROUND MOVIE':        '0035',
            '(Multi-ch Source)+WIDE SURROUND MUSIC':        '0036',
            '(Multi ch source)DTS-ES matrix':               '0026',
            '(Multi ch source)DTS-ES discrete':             '0027',
            '(Multi ch source)DTS-ES 8ch discrete':         '0030',
            '(Multi ch source)+Neo:X CINEMA':               '0043',
            '(Multi ch source)+Neo:X MUSIC':                '0044',
            '(Multi ch source)+Neo:X GAME':                 '0045',
            'ACTION':                                       '0101',
            'DRAMA':                                        '0103',
            'ADVANCED GAME':                                '0118',
            'SPORTS':                                       '0117',
            'CLASSICAL':                                    '0107',
            'ROCK/POP':                                     '0110',
            'EXTENDED STEREO':                              '0112',
            'Front Stage Surround Advance':                 '0003',
            'ECO MODE 1':                                   '0212',
            'ECO MODE 2':                                   '0213',
            'RETRIEVER AIR':                                '0153',
            'PHONES SURROUND':                              '0113',
            'PROLOGIC + THX CINEMA':                        '0051',
            'PL2 MOVIE + THX CINEMA':                       '0052',
            'PL2x MOVIE + THX CINEMA':                      '0054',
            'PL2z HEIGHT + THX CINEMA':                     '0092',
            'THX CINEMA (for 2ch)':                         '0068',
            'THX MUSIC (for 2ch)':                          '0069',
            'THX GAMES (for 2ch)':                          '0070',
            'PL2 MUSIC + THX MUSIC':                        '0071',
            'PL2x MUSIC + THX MUSIC':                       '0072',
            'PL2z HEIGHT + THX MUSIC':                      '0093',
            'PL2 GAME + THX GAMES':                         '0074',
            'PL2x GAME + THX GAMES':                        '0075',
            'PL2z HEIGHT + THX GAMES':                      '0094',
            'Neo:X CINEMA + THX CINEMA':                    '0201',
            'Neo:X MUSIC + THX MUSIC':                      '0202',
            'Neo:X GAME + THX GAMES':                       '0203',
            'THX CINEMA (for multi ch)':                    '0056',
            'THX SURROUND EX (for multi ch)':               '0057',
            'PL2x MOVIE + THX CINEMA (for multi ch)':       '0058',
            'PL2z HEIGHT + THX CINEMA (for multi ch)':      '0095',
            'ES MATRIX + THX CINEMA (for multi ch)':        '0060',
            'ES DISCRETE + THX CINEMA (for multi ch)':      '0061',
            'ES 8ch DISCRETE + THX CINEMA (for multi ch)':  '0067',
            'THX MUSIC (for multi ch)':                     '0080',
            'THX GAMES (for multi ch)':                     '0081',
            'PL2x MUSIC + THX MUSIC (for multi ch)':        '0082',
            'PL2z HEIGHT + THX MUSIC (for multi ch)':       '0096',
            'PL2z HEIGHT + THX GAMES (for multi ch)':       '0097',
            'ES MATRIX + THX MUSIC (for multi ch)':         '0086',
            'ES MATRIX + THX GAMES (for multi ch)':         '0087',
            'ES DISCRETE + THX MUSIC (for multi ch)':       '0088',
            'ES DISCRETE + THX GAMES (for multi ch)':       '0089',
            'ES 8CH DISCRETE + THX MUSIC (for multi ch)':   '0090',
            'ES 8CH DISCRETE + THX GAMES (for multi ch)':   '0091',
            'Neo:X CINEMA + THX CINEMA (for multi ch)':     '0204',
            'Neo:X MUSIC + THX MUSIC (for multi ch)':       '0205',
            'Neo:X GAME + THX GAMES (for multi ch)':        '0206',
            'AUTO SURROUND':                                '0005',
            'Auto Level Control (A.L.C.)':                  '0151',
            'DIRECT':                                       '0007',
            'PURE DIRECT':                                  '0008',
            'OPTIMUM SURROUND':                             '0152'
        }

        self._update_listening_mode_states = {
            '0009': 'STEREO (direct set)',
            '0013': 'PRO LOGIC2 MOVIE',
            '0018': 'PRO LOGIC2x MOVIE',
            '0014': 'PRO LOGIC2 MUSIC',
            '0019': 'PRO LOGIC2x MUSIC',
            '0015': 'PRO LOGIC2 GAME',
            '0020': 'PRO LOGIC2x GAME',
            '0031': 'PRO LOGIC2z HEIGHT',
            '0032': 'WIDE SURROUND MOVIE',
            '0033': 'WIDE SURROUND MUSIC',
            '0012': 'PRO LOGIC',
            '0037': 'Neo:X CINEMA',
            '0038': 'Neo:X MUSIC',
            '0039': 'Neo:X GAME',
            '0021': '(Multi ch source)',
            '0022': '(Multi ch source)+DOLBY EX',
            '0023': '(Multi ch source)+PRO LOGIC2x MOVIE',
            '0024': '(Multi ch source)+PRO LOGIC2x MUSIC',
            '0034': '(Multi-ch Source)+PRO LOGIC2z HEIGHT',
            '0035': '(Multi-ch Source)+WIDE SURROUND MOVIE',
            '0036': '(Multi-ch Source)+WIDE SURROUND MUSIC',
            '0026': '(Multi ch source)DTS-ES matrix',
            '0027': '(Multi ch source)DTS-ES discrete',
            '0030': '(Multi ch source)DTS-ES 8ch discrete',
            '0043': '(Multi ch source)+Neo:X CINEMA',
            '0044': '(Multi ch source)+Neo:X MUSIC',
            '0045': '(Multi ch source)+Neo:X GAME',
            '0101': 'ACTION',
            '0103': 'DRAMA',
            '0118': 'ADVANCED GAME',
            '0117': 'SPORTS',
            '0107': 'CLASSICAL',
            '0110': 'ROCK/POP',
            '0112': 'EXTENDED STEREO',
            '0003': 'Front Stage Surround Advance',
            '0212': 'ECO MODE 1',
            '0213': 'ECO MODE 2',
            '0153': 'RETRIEVER AIR',
            '0113': 'PHONES SURROUND',
            '0051': 'PROLOGIC + THX CINEMA',
            '0052': 'PL2 MOVIE + THX CINEMA',
            '0054': 'PL2x MOVIE + THX CINEMA',
            '0092': 'PL2z HEIGHT + THX CINEMA',
            '0068': 'THX CINEMA (for 2ch)',
            '0069': 'THX MUSIC (for 2ch)',
            '0070': 'THX GAMES (for 2ch)',
            '0071': 'PL2 MUSIC + THX MUSIC',
            '0072': 'PL2x MUSIC + THX MUSIC',
            '0093': 'PL2z HEIGHT + THX MUSIC',
            '0074': 'PL2 GAME + THX GAMES',
            '0075': 'PL2x GAME + THX GAMES',
            '0094': 'PL2z HEIGHT + THX GAMES',
            '0201': 'Neo:X CINEMA + THX CINEMA',
            '0202': 'Neo:X MUSIC + THX MUSIC',
            '0203': 'Neo:X GAME + THX GAMES',
            '0056': 'THX CINEMA (for multi ch)',
            '0057': 'THX SURROUND EX (for multi ch)',
            '0058': 'PL2x MOVIE + THX CINEMA (for multi ch)',
            '0095': 'PL2z HEIGHT + THX CINEMA (for multi ch)',
            '0060': 'ES MATRIX + THX CINEMA (for multi ch)',
            '0061': 'ES DISCRETE + THX CINEMA (for multi ch)',
            '0067': 'ES 8ch DISCRETE + THX CINEMA (for multi ch)',
            '0080': 'THX MUSIC (for multi ch)',
            '0081': 'THX GAMES (for multi ch)',
            '0082': 'PL2x MUSIC + THX MUSIC (for multi ch)',
            '0096': 'PL2z HEIGHT + THX MUSIC (for multi ch)',
            '0097': 'PL2z HEIGHT + THX GAMES (for multi ch)',
            '0086': 'ES MATRIX + THX MUSIC (for multi ch)',
            '0087': 'ES MATRIX + THX GAMES (for multi ch)',
            '0088': 'ES DISCRETE + THX MUSIC (for multi ch)',
            '0089': 'ES DISCRETE + THX GAMES (for multi ch)',
            '0090': 'ES 8CH DISCRETE + THX MUSIC (for multi ch)',
            '0091': 'ES 8CH DISCRETE + THX GAMES (for multi ch)',
            '0204': 'Neo:X CINEMA + THX CINEMA (for multi ch)',
            '0205': 'Neo:X MUSIC + THX MUSIC (for multi ch)',
            '0206': 'Neo:X GAME + THX GAMES (for multi ch)',
            '0005': 'AUTO SURROUND',
            '0151': 'Auto Level Control (A.L.C.)',
            '0007': 'DIRECT',
            '0008': 'PURE DIRECT',
            '0152': 'OPTIMUM SURROUND'
        }

        self._set_zone_hd_input_states = {
            'Blu-ray':  '25',
            'HDMI 1':   '19',
            'HDMI 2':   '20',
            'HDMI 3':   '21',
            'HDMI 4':   '22',
            'HDMI 5':   '23',
            'HDMI 6':   '24',
            'HDMI 7':   '34',
            'HDMI 8':   '35',
            'MHL':      '48',
            'DVD':      '04',
            'SAT/CBL':  '06',
            'DVR/BDR':  '15',
            'Video':    '10'
        }

        self._update_zone_hd_input_states = {
            '25': 'Blu-ray',
            '19': 'HDMI 1',
            '20': 'HDMI 2',
            '21': 'HDMI 3',
            '22': 'HDMI 4',
            '23': 'HDMI 5',
            '24': 'HDMI 6',
            '34': 'HDMI 7',
            '35': 'HDMI 8',
            '48': 'MHL',
            '04': 'DVD',
            '06': 'SAT/CBL',
            '15': 'DVR/BDR',
            '10': 'Video'
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

