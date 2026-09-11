from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
import time


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
            'DSP40': self.adac_25_2129_dsp40,
            'ISP40': self.adac_25_2129_isp40,
            'MSP40': self.adac_25_2129_msp40,
            'TSP40': self.adac_25_2129_tsp40,
            'XMP44': self.adac_25_2129_xmp44,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutomaticTuning': {'Parameters': ['Slot'], 'Status': {}},
            'Band': {'Parameters': ['Slot'], 'Status': {}},
            'BMP40Disconnect': {'Parameters': ['Slot'], 'Status': {}},
            'BMP40Info': {'Parameters': ['Slot'], 'Status': {}},
            'CurrentSongInfo': {'Parameters': ['Slot'], 'Status': {}},
            'DABChannel': {'Parameters': ['Slot'], 'Status': {}},
            'DeviceType': { 'Status': {}},
            'FavoriteStationNavigation': {'Parameters': ['Slot'], 'Status': {}},
            'FavoriteStationResult': {'Parameters': ['Slot', 'Button'], 'Status': {}},
            'FavoriteStationSelect': {'Parameters': ['Slot'], 'Status': {}},
            'FavoriteStationUpdate': {'Parameters': ['Slot'], 'Status': {}},
            'Mode': {'Parameters': ['Slot'], 'Status': {}},
            'Output': {'Parameters': ['Slot'], 'Status': {}},
            'OutputGain': {'Parameters': ['Slot'], 'Status': {}},
            'OutputStatus': {'Parameters': ['Slot'], 'Status': {}},
            'Pairing': {'Parameters': ['Slot'], 'Status': {}},
            'PlayedTime': {'Parameters': ['Slot'], 'Status': {}},
            'PlayStatus': {'Parameters': ['Slot'], 'Status': {}},
            'ProgramName': {'Parameters': ['Slot'], 'Status': {}},
            'ProgramText': {'Parameters': ['Slot'], 'Status': {}},
            'Random': {'Parameters': ['Slot'], 'Status': {}},
            'Recording': {'Parameters': ['Slot'], 'Status': {}},
            'Repeat': {'Parameters': ['Slot'], 'Status': {}},
            'SelectPreset': {'Parameters': ['Slot'], 'Status': {}},
            'SetPreset': {'Parameters': ['Slot'], 'Status': {}},
            'SignalStatus': {'Parameters': ['Slot'], 'Status': {}},
            'SongName': {'Parameters': ['Slot'], 'Status': {}},
            'StationName': {'Parameters': ['Slot'], 'Status': {}},
            'Transport': {'Parameters': ['Slot'], 'Status': {}},
            'TuningFrequency': {'Parameters': ['Slot'], 'Status': {}},
            'Unpair': {'Parameters': ['Slot'], 'Status': {}},
        }

        self.FavoriteStation = {'1': ListNavigation(), '2': ListNavigation(), '3': ListNavigation(), '4': ListNavigation()}
        self.FavoriteStationPointer = {'1': {}, '2': {}, '3': {}, '4': {}}
        self.FavoriteStation['1'].Max = 1
        self.FavoriteStation['2'].Max = 1
        self.FavoriteStation['3'].Max = 1
        self.FavoriteStation['4'].Max = 1

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|BND([1-4])\|([01])\|.*?\|\r\n'), self.__MatchBand, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|BMPI([1-4])\|([\s\S]+?)\|.*?\|\r\n'), self.__MatchBMP40Info, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PSI([1-4])\|([\s\S]+?)\|.*?\|\r\n'), self.__MatchCurrentSongInfo, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|CH([1-4])\|(-?\d+?)\|.*?\|\r\n'), self.__MatchDABChannel, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|TPS\|(.*?)\|.*?\|\r\n'), self.__MatchDeviceType, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|FAV([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchFavoriteStationResult, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|RRM([1-4])\|([01])\|.*?\|\r\n'), self.__MatchMode, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|OG([1-4])\|([0-9]{1,2}|100)\|.*?\|\r\n'), self.__MatchOutputGain, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|STST([1-4])\|(\d+?)\|.*?\|\r\n'), self.__MatchOutputStatus, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PAIRS([1-4])\|([0-4])\|.*?\|\r\n'), self.__MatchPairing, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PPTI([1-4])\|(\d+?)\|.*?\|\r\n'), self.__MatchPlayedTime, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PSTAT([1-4])\|([01]\^[01]\^[01])\|.*?\|\r\n'), self.__MatchPlayStatus, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PRGN([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchProgramName, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|PRGT([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchProgramText, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|SIGS([1-4])\|(\d+?)\|.*?\|\r\n'), self.__MatchSignalStatus, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|SON([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchSongName, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|STN([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchStationName, None)
            self.AddMatchString(compile(b'#\|(?:web|ALL)\|D001\|FREQ([1-4])\|([0-9]{1,5})\|.*?\|\r\n'), self.__MatchTuningFrequency, None)
    
    @property
    def MaxFavoriteStations(self):
        return self._MaxFavoriteStations

    @MaxFavoriteStations.setter
    def MaxFavoriteStations(self, value):
        if self.Model in ['ISP40', 'XMP44']:
            MaxFav = int(value)
            if 1 <= MaxFav <= 10:
                self.FavoriteStation['1'].Max = MaxFav
                self.FavoriteStation['2'].Max = MaxFav
                self.FavoriteStation['3'].Max = MaxFav
                self.FavoriteStation['4'].Max = MaxFav
            else:
                self.Error(['MaxFavoriteStations should be in range 1 - 10.'])

    def SetAutomaticTuning(self, value, qualifier):

        ValueStateValues = {
            'Up':   'UP',
            'Down': 'DN',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            AutomaticTuningCmdString = '#|D001|web|SFS{0}{1}|0|U|\r\n'.format(ValueStateValues[value], slot)
            self.__SetHelper('AutomaticTuning', AutomaticTuningCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomaticTuning')

    def SetBand(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BandCmdString = '#|D001|web|SSBND{0}|0|U|\r\n'.format(slot)
            self.__SetHelper('Band', BandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBand')

    def UpdateBand(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BandCmdString = '#|D001|web|GBND{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('Band', BandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBand')

    def __MatchBand(self, match, tag):

        ValueStateValues = {
            '1': 'FM',
            '0': 'DAB',
        }
        qualifier = {'Slot': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Band', value, qualifier)

    def SetBMP40Disconnect(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BMP40DisconnectCmdString = '#|D001|web|SDISC{0}|0|U|\r\n'.format(slot)
            self.__SetHelper('BMP40Disconnect', BMP40DisconnectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBMP40Disconnect')

    def UpdateBMP40Info(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BMP40InfoCmdString = '#|D001|web|GBMPI{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('BMP40Info', BMP40InfoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBMP40Info')

    def __MatchBMP40Info(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode().replace('^', ',')
        self.WriteStatus('BMP40Info', value, qualifier)

    def UpdateCurrentSongInfo(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            CurrentSongInfoCmdString = '#|D001|web|GPSI{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('CurrentSongInfo', CurrentSongInfoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCurrentSongInfo')

    def __MatchCurrentSongInfo(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value_list = match.group(2).decode().split('^')
        value = ''.join(['Song Name:', value_list[0], '\r\nArtist:', value_list[1],
                         '\r\nAlbum:', value_list[2], '\r\nLength:', value_list[3],
                         '\r\nSeconds Played:', value_list[4]])
        self.WriteStatus('CurrentSongInfo', value, qualifier)

    def UpdateDABChannel(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            DABChannelCmdString = '#|D001|web|GCH{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('DABChannel', DABChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDABChannel')

    def __MatchDABChannel(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = int(match.group(2))
        self.WriteStatus('DABChannel', value, qualifier)

    def UpdateDeviceType(self, value, qualifier):

        DeviceTypeCmdString = '#|D001|web|GTPS|0|U|\r\n'
        self.__UpdateHelper('DeviceType', DeviceTypeCmdString, value, qualifier)

    def __MatchDeviceType(self, match, tag):

        value = match.group(1).decode().replace('^', ',')
        self.WriteStatus('DeviceType', value, None)

    def SetFavoriteStationNavigation(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            self.FavoriteStation[slot].Navigate(value)
            FavoriteStationNavigationCmdString = '#|D001|web|GFAV{0}|{1}|U|\r\n'.format(slot, self.FavoriteStation[slot].StartingEntry)
            self.__UpdateHelper('FavoriteStationNavigation', FavoriteStationNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFavoriteStationNavigation')

    def __MatchFavoriteStationResult(self, match, tag):

        slot = match.group(1).decode()
        Stations = match.group(2).decode().split('^')
        if len(Stations) >= 3:
            del Stations[::3]
            if any(Stations):
                self.FavoriteStation[slot].Clear()
                for Name in Stations[::2]:
                    if Name:
                        self.FavoriteStation[slot].Append(Name)
                    else:
                        break
                self.FavoriteStationPointer[slot] = dict(zip(Stations[::2], Stations[1::2]))
                self.FavoriteStation[slot].End()
                self.FavoriteStation[slot].UpdateTLP(self.WriteStatus,'FavoriteStationResult', slot)
            else:
                self.FavoriteStation[slot].UndoNavigate()
        else:
            self.FavoriteStation[slot].UndoNavigate()

    def SetFavoriteStationSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 10
        }
        slot = qualifier['Slot']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(slot) <= 4:
            Line = self.ReadStatus('FavoriteStationResult', {'Slot': slot, 'Button': value})
            if Line not in self.FavoriteStation[slot].InvalidLines:
                Pointer = self.FavoriteStationPointer[slot][Line]
                FavoriteStationSelectCmdString = '#|D001|web|DWSEST{0}|{1}|U|\r\n'.format(slot, Pointer)
                self.__SetHelper('FavoriteStationSelect', FavoriteStationSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFavoriteStationSelect')

    def SetFavoriteStationUpdate(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            FavoriteStationUpdateCmdString = '#|D001|web|GFAV{0}|{1}|U|\r\n'.format(slot, self.FavoriteStation[slot].StartingEntry)
            self.__UpdateHelper('FavoriteStationUpdate', FavoriteStationUpdateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFavoriteStationUpdate')

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Player':   '0',
            'Recorder': '1',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            ModeCmdString = '#|D001|web|SRRM{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMode')

    def UpdateMode(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            ModeCmdString = '#|D001|web|GRRM{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMode')

    def __MatchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Player',
            '1': 'Recorder',
        }

        qualifier = {'Slot': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mode', value, qualifier)

    def SetOutput(self, value, qualifier):

        ValueStateValues = {
            'Stereo': '1',
            'Mono':   '0',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            OutputCmdString = '#|D001|web|SSTSE{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Output', OutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutput')

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -92,
            'Max': 8,
        }

        slot = qualifier['Slot']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(slot) <= 4:
            gain = -value + 8
            OutputGainCmdString = '#|D001|web|SOG{0}|{1}|U|\r\n'.format(slot, gain)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            OutputGainCmdString = '#|D001|web|GOG{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = int(match.group(2))
        value = -value + 8
        self.WriteStatus('OutputGain', value, qualifier)

    def UpdateOutputStatus(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            OutputStatusCmdString = '#|D001|web|GSTST{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('OutputStatus', OutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputStatus')

    def __MatchOutputStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Stereo',
            '0': 'Mono',
        }

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode()
        if value in ValueStateValues:
            value = ValueStateValues[value]
        else:
            value = 'Other'
        self.WriteStatus('OutputStatus', value, qualifier)

    def SetPairing(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PairingCmdString = '#|D001|web|SPAIR{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Pairing', PairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPairing')

    def UpdatePairing(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PairingCmdString = '#|D001|web|GPAIRS{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('Pairing', PairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePairing')

    def __MatchPairing(self, match, tag):

        ValueStateValues = {
            '0': 'Success',
            '1': 'Time-out',
            '2': 'Failed',
            '3': 'Enabled',
            '4': 'Disabled',
        }

        qualifier = {'Slot': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Pairing', value, qualifier)

    def UpdatePlayedTime(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PlayedTimeCmdString = '#|D001|web|PPTI{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('PlayedTime', PlayedTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlayedTime')

    def __MatchPlayedTime(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = time.strftime("%H:%M:%S", time.gmtime(int(match.group(2))))
        self.WriteStatus('PlayedTime', value, qualifier)

    def UpdatePlayStatus(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PlayStatusCmdString = '#|D001|web|GPSTAT{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('PlayStatus', PlayStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlayStatus')

    def __MatchPlayStatus(self, match, tag):

        ValueStateValues = {
            '0^1^0': 'Playing',
            '1^0^0': 'Paused',
            '0^0^0': 'Stopped',
            '0^0^1': 'Recording',
        }

        qualifier = {'Slot': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PlayStatus', value, qualifier)

    def UpdateProgramName(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            ProgramNameCmdString = '#|D001|web|GPRGN{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('ProgramName', ProgramNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateProgramName')

    def __MatchProgramName(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode()
        if value in ['', ' ']:
            value = 'None'
        self.WriteStatus('ProgramName', value, qualifier)

    def UpdateProgramText(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            ProgramTextCmdString = '#|D001|web|GPRGT{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('ProgramText', ProgramTextCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateProgramText')

    def __MatchProgramText(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode()
        if value in ['', ' ']:
            value = 'None'
        self.WriteStatus('ProgramText', value, qualifier)

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            RandomCmdString = '#|D001|web|SPRND{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Random', RandomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRandom')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Start':  'STA',
            'Stop':   'STO',
            'Pause':  'PAU',
            'Cancel': 'CAN',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            RecordingCmdString = '#|D001|web|SR{0}{1}|0|U|\r\n'.format(ValueStateValues[value], slot)
            self.__SetHelper('Recording', RecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecording')

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'One':     '0',
            'Folder':  '1',
            'X times': '2',
            'Off':     '3',
            'All':     '4',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            RepeatCmdString = '#|D001|web|SPRP{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRepeat')

    def SetSelectPreset(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(value) <= 10 and 1 <= int(slot) <= 4:
            SelectPresetCmdString = '#|D001|web|SELPR{0}|{1}|U|\r\n'.format(slot, value)
            self.__SetHelper('SelectPreset', SelectPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelectPreset')

    def SetSetPreset(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(value) <= 10 and 1 <= int(slot) <= 4:
            SetPresetCmdString = '#|D001|web|SPRES{0}|{1}|U|\r\n'.format(slot, value)
            self.__SetHelper('SetPreset', SetPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetPreset')

    def UpdateSignalStatus(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            SignalStatusCmdString = '#|D001|web|GSIGS{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalStatus')

    def __MatchSignalStatus(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = int(match.group(2))
        self.WriteStatus('SignalStatus', value, qualifier)

    def UpdateSongName(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            SongNameCmdString = '#|D001|web|GSON{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('SongName', SongNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSongName')

    def __MatchSongName(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('SongName', value, qualifier)

    def UpdateStationName(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            StationNameCmdString = '#|D001|web|GSTN{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('StationName', StationNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStationName')

    def __MatchStationName(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('StationName', value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play':         'PLAY',
            'Stop':         'STOP',
            'Pause':        'PAUS',
            'Begin':        'GTST',
            'Next':         'NEXT',
            'Previous':     'PREV',
            'Fast Forward': 'FFW',
            'Fast Rewind':  'FRW',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            TransportCmdString = '#|D001|web|SP{0}{1}|0|U|\r\n'.format(ValueStateValues[value], slot)
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetTuningFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min': 87.00,
            'Max': 108.00
        }
        slot = qualifier['Slot']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(slot) <= 4:
            TuningFrequencyCmdString = '#|D001|web|SFREQ{0}|{1}|U|\r\n'.format(slot, int(value * 100))
            self.__SetHelper('TuningFrequency', TuningFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTuningFrequency')

    def UpdateTuningFrequency(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            TuningFrequencyCmdString = '#|D001|web|GFREQ{0}|0|U|\r\n'.format(slot)
            self.__UpdateHelper('TuningFrequency', TuningFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTuningFrequency')

    def __MatchTuningFrequency(self, match, tag):

        qualifier = {'Slot': match.group(1).decode()}
        value = float(match.group(2).decode())/100
        self.WriteStatus('TuningFrequency', value, qualifier)

    def SetUnpair(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(value) <= 8 and 1 <= int(slot) <= 4:
            UnpairCmdString = '#|D001|web|SFORGET{0}|{1}|U|\r\n'.format(slot, value)
            self.__SetHelper('Unpair', UnpairCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUnpair')

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

    def adac_25_2129_xmp44(self):
        self.Model = 'XMP44'

    def adac_25_2129_isp40(self):
        self.Model = 'ISP40'

    def adac_25_2129_msp40(self):
        self.Model = 'MSP40'

    def adac_25_2129_dsp40(self):
        self.Model = 'DSP40'

    def adac_25_2129_tsp40(self):
        self.Model = 'TSP40'

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
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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


class ListNavigation:
    EndofList = '***End of list***'
    EmptyList = EndofList
    InvalidLines = (EndofList, EmptyList, None, '')
    PreviousStartingEntry = 0
    StartingEntry = 0
    Max = 1

    def __init__(self):
        self.Empty()

    def Empty(self):
        self.List = [self.EmptyList]

    def Clear(self):
        self.List.clear()

    def Append(self, Line):
        if Line not in self.InvalidLines:
            self.List.append(Line)

    def End(self):
        self.List.append(self.EndofList)

    def Navigate(self, Direction):
        self.PreviousStartingEntry = self.StartingEntry

        if Direction == 'Page Up':
            self.StartingEntry -= self.Max
        elif Direction == 'Page Down':
            self.StartingEntry += self.Max
        elif Direction == 'Up':
            self.StartingEntry -= 1
        elif Direction == 'Down':
            self.StartingEntry += 1

        if self.StartingEntry < 0:
            self.StartingEntry = 0

    def UndoNavigate(self):
        self.StartingEntry = self.PreviousStartingEntry

    def UpdateTLP(self, Function, command, Slot):
        Button = 0
        for Button, Line in enumerate(self.List[:self.Max], 1):
            Function(command, Line, {'Button': Button, 'Slot': Slot})
        for Button in range(Button + 1, self.Max + 1):
            Function(command, '', {'Button': Button, 'Slot': Slot})

