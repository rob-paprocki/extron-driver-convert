from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.Models = {}

        self._DeviceID = 1
        self.FavoriteStation = {'1': ListNavigation(), '2': ListNavigation(),
                                '3': ListNavigation(), '4': ListNavigation()}
        self.FavoriteStation['1'].Max = 5
        self.FavoriteStation['2'].Max = 5
        self.FavoriteStation['3'].Max = 5
        self.FavoriteStation['4'].Max = 5
        

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BMP40Disconnect': {'Parameters':['Slot'], 'Status': {}},
            'BMP40Info': {'Parameters':['Slot'], 'Status': {}},
            'CurrentSongInfo': {'Parameters':['Slot'], 'Status': {}},
            'FavoriteStationNavigation': {'Parameters':['Slot'], 'Status': {}},
            'FavoriteStationResult': {'Parameters':['Slot','Button'], 'Status': {}},
            'FavoriteStationSelect': {'Parameters':['Slot'], 'Status': {}},
            'FavoriteStationUpdate': {'Parameters':['Slot'], 'Status': {}},
            'Input': {'Parameters':['Zone'], 'Status': {}},
            'Mute': {'Parameters':['Zone'], 'Status': {}},
            'Pairing': {'Parameters':['Slot'], 'Status': {}},
            'PlayedTime': {'Parameters':['Slot'], 'Status': {}},
            'PlayStatus': {'Parameters':['Slot'], 'Status': {}},
            'Power': {'Parameters':['Zone'], 'Status': {}},
            'SongName': {'Parameters':['Slot'], 'Status': {}},
            'StationName': {'Parameters':['Slot'], 'Status': {}},
            'Transport': {'Parameters':['Slot'], 'Status': {}},
            'Unpair': {'Parameters':['Slot'], 'Status': {}},
            'Volume': {'Parameters':['Zone'], 'Status': {}},
        }

        self.FavoriteStationPointer = {'1': {}, '2': {}, '3': {}, '4': {}}

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F001\|BMPI([1-4])\|([\s\S]+?)\|.*?\|\r\n'), self.__MatchBMP40Info, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F001\|PSI([1-4])\|([\s\S]+?)\|.*?\|\r\n'), self.__MatchCurrentSongInfo, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|FAV([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchFavoriteStationResult, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|R0(1|2)\|.\^([1-8])\|U\|\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|M0(1|2)\|(1|0)\|U\|\r\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F001\|PAIRS([1-4])\|([0-4])\|.*?\|\r\n'), self.__MatchPairing, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F001\|PPTI([1-4])\|(\d+?)\|.*?\|\r\n'), self.__MatchPlayedTime, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F001\|PSTAT([1-4])\|([01]\^[01]\^[01])\|.*?\|\r\n'), self.__MatchPlayStatus, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|SBY0(1|2)\|(1|0)\|U\|\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|SON([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchSongName, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|STN([1-4])\|(.*?)\|.*?\|\r\n'), self.__MatchStationName, None)
            self.AddMatchString(re.compile(b'#\|(?:web|ALL)\|F[0-9]{3}\|V0(1|2)\|([0-9]{1,2})\|U\|\r\n'), self.__MatchVolume, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 999:
            self._DeviceID = int(value)
        else:
            print('The value of DeviceID is outside of the range of allowable values.')

    @property
    def MaxFavoriteStations(self):
        return self.FavoriteStation

    @MaxFavoriteStations.setter
    def MaxFavoriteStations(self, value):
        if 1 <= int(value) <= 10:
            self.FavoriteStation['1'].Max = int(value)
            self.FavoriteStation['2'].Max = int(value)
            self.FavoriteStation['3'].Max = int(value)
            self.FavoriteStation['4'].Max = int(value)
        else:
            print('Max Favorite Stations Parameter should be in range 1 - 10.')

    def SetBMP40Disconnect(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BMP40DisconnectCmdString = '#|F001|web|SDISC{0}|0|U|\r\n'.format(slot)
            self.__SetHelper('BMP40Disconnect', BMP40DisconnectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBMP40Disconnect')

    def UpdateBMP40Info(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            BMP40InfoCmdString = '#|F001|web|GBMPI{0}|0|U|\r\n'.format(slot)
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
            CurrentSongInfoCmdString = '#|F001|web|GPSI{0}|0|U|\r\n'.format(slot)
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

    def SetFavoriteStationNavigation(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            self.FavoriteStation[slot].Navigate(value)
            FavoriteStationNavigationCmdString = '#|F{0:03d}|web|GFAV{1}|{2}|U|\r\n'.format(self.DeviceID,
                                                    slot, self.FavoriteStation[slot].StartingEntry)
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
                self.FavoriteStation[slot].UpdateTLP('FavoriteStationResult', self.WriteStatus, slot)
            else:
                self.FavoriteStation[slot].UndoNavigate()
        else:
            self.FavoriteStation[slot].UndoNavigate()

    def SetFavoriteStationSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 10,
        }

        slot = qualifier['Slot']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(slot) <= 4:
            Line = self.ReadStatus('FavoriteStationResult', {'Slot': slot, 'Button': value})
            if Line not in self.FavoriteStation[slot].InvalidLines:
                Pointer = self.FavoriteStationPointer[slot][Line]
                FavoriteStationSelectCmdString = '#|F{0:03d}|web|DWSEST{1}|{2}|U|\r\n'.format(self.DeviceID,
                                                        slot, Pointer)
                self.__SetHelper('FavoriteStationSelect', FavoriteStationSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFavoriteStationSelect')

    def SetFavoriteStationUpdate(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            FavoriteStationUpdateCmdString = '#|F{0:03d}|web|GFAV{1}|{2}|U|\r\n'.format(self.DeviceID,
                                                    slot, self.FavoriteStation[slot].StartingEntry)
            self.__UpdateHelper('FavoriteStationUpdate', FavoriteStationUpdateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFavoriteStationUpdate')

    def SetInput(self, value, qualifier):

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val) <= 2 and 1 <= int(value) <= 8:
            InputCmdString = '#|F{0:03d}|web|SR{1}|{2}|U|\r\n'.format(self.DeviceID,
                                                    zone_val.zfill(2), value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val):
            InputCmdString = '#|F{0:03d}|web|GR{1}|0|U|\r\n'.format(self.DeviceID, zone_val.zfill(2))
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        qualifier = {}
        qualifier['Zone'] = match.group(1).decode()
        value = match.group(2).decode()
        self.WriteStatus('Input', value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val) <= 2 and value in ValueStateValues:
            MuteCmdString = '#|F{0:03d}|web|SM{1}|{2}|U|\r\n'.format(self.DeviceID,
                                    zone_val.zfill(2), ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val):
            MuteCmdString = '#|F{0:03d}|web|GM{1}|0|U|\r\n'.format(self.DeviceID, zone_val.zfill(2))
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = {}
        qualifier['Zone'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetPairing(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PairingCmdString = '#|F001|web|SPAIR{0}|{1}|U|\r\n'.format(slot, ValueStateValues[value])
            self.__SetHelper('Pairing', PairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPairing')

    def UpdatePairing(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            PairingCmdString = '#|F001|web|GPAIRS{0}|0|U|\r\n'.format(slot)
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
            PlayedTimeCmdString = '#|F001|web|PPTI{0}|0|U|\r\n'.format(slot)
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
            PlayStatusCmdString = '#|F001|web|GPSTAT{0}|0|U|\r\n'.format(slot)
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

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '0',
            'Off': '1',
        }

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val) <= 2 and value in ValueStateValues:
            PowerCmdString = '#|F{0:03d}|web|SSBY{1}|{2}|U|\r\n'.format(self.DeviceID,
                                    zone_val.zfill(2), ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val):
            PowerCmdString = '#|F{0:03d}|web|GSSBY{1}|standby|U|\r\n'.format(self.DeviceID, zone_val.zfill(2))
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off',
            }

        qualifier = {}
        qualifier['Zone'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def UpdateSongName(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            SongNameCmdString = '#|F{0:03d}|web|GSON{1}|0|U|\r\n'.format(self.DeviceID, slot)
            self.__UpdateHelper('SongName', SongNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSongName')

    def __MatchSongName(self, match, tag):

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = match.group(2).decode()
        self.WriteStatus('SongName', value, qualifier)

    def UpdateStationName(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(slot) <= 4:
            StationNameCmdString = '#|F{0:03d}|web|GSTN{0}|0|U|\r\n'.format(self.DeviceID, slot)
            self.__UpdateHelper('StationName', StationNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStationName')

    def __MatchStationName(self, match, tag):

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
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
            TransportCmdString = '#|F001|web|SP{0}{1}|0|U|\r\n'.format(ValueStateValues[value], slot)
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetUnpair(self, value, qualifier):

        slot = qualifier['Slot']
        if 1 <= int(value) <= 8 and 1 <= int(slot) <= 4:
            UnpairCmdString = '#|F001|web|SFORGET{0}|{1}|U|\r\n'.format(slot, value)
            self.__SetHelper('Unpair', UnpairCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUnpair')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -90,
            'Max': 0,
            }

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val) <= 2 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '#|F{0:03d}|web|SV{1}|{2}|U|\r\n'.format(self.DeviceID,
                                    zone_val.zfill(2), abs(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        zone_val = qualifier['Zone']
        if 1 <= int(zone_val) <= 2:
            VolumeCmdString = '#|F{0:03d}|web|GV{1}|0|U|\r\n'.format(self.DeviceID, zone_val.zfill(2))
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {}
        qualifier['Zone'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if -90 <= -(value) <= 0:
            self.WriteStatus('Volume', -(value), qualifier)

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

    def UpdateTLP(self, command, WriteFunction, Slot):
        Button = 0
        for Button, Line in enumerate(self.List[:self.Max], 1):
            WriteFunction(command, Line, {'Button': Button, 'Slot': Slot})
        for Button in range(Button + 1, self.Max + 1):
            WriteFunction(command, '', {'Button': Button, 'Slot': Slot})