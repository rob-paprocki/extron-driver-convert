from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import json

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
        self._MaxSourceSearchResults = 4
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Mute': { 'Status': {}},
            'NowPlaying': { 'Status': {}},
            'PlayerID': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'Shuffle': { 'Status': {}},
            'SourceNavigation': { 'Status': {}},
            'SourceSearchResults': {'Parameters':['Button'], 'Status': {}},
            'SourceSearchSet': { 'Status': {}},
            'SourceUpdate': { 'Status': {}},
            'Volume': { 'Status': {}},
        }        
        self.responsejson = re.compile(b'\{.*(\}\r\n)+')
        self.lastRepeatUpdate = 0
        self.PlayerID = "0"
        self.SourceDict = {}
        self.SourceList = []
        self.SourceMinLabel = 0
        self.SourceMaxLabel = 4
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'player/get_mute.+?pid=\d+&state=(on|off)'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'{.+?heos.+?player/get_now_playing_media.+?}\r\n'), self.__MatchNowPlaying, None) 
            self.AddMatchString(re.compile(b'player/get_players.+?pid[\": ]+(\d+)'), self.__MatchPlayerID, None)
            self.AddMatchString(re.compile(b'player/get_play_mode.+?repeat=(on_all|on_one|off)&shuffle=(on|off)'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'player/get_play_state.+?state=(play|pause|stop)'), self.__MatchTransport, None)
            self.AddMatchString(re.compile(b'player/get_volume.+?level=(\d{1,3})'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'result\W+fail.+?eid=(\d{1,2})'), self.__MatchError, None)

    @property
    def MaxSourceSearchResults(self):
        return self._MaxSourceSearchResults

    @MaxSourceSearchResults.setter
    def MaxSourceSearchResults(self, value):
        self._MaxSourceSearchResults= value

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'     : 'heos://player/set_mute?pid=' + self.PlayerID + '&state=on\r\n',
            'Off'    : 'heos://player/set_mute?pid=' + self.PlayerID + '&state=off\r\n', 
            'Toggle' : 'heos://player/toggle_mute?pid=' + self.PlayerID + '\r\n'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteCmdString = 'heos://player/get_mute?pid=' + self.PlayerID + '\r\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'on' : 'On',
            'off' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def UpdateNowPlaying(self, value, qualifier):

        NowPlayingCmdString = 'heos://player/get_now_playing_media?pid=' + self.PlayerID + '\r\n'
        self.__UpdateHelper('NowPlaying', NowPlayingCmdString, value, qualifier)

    def __MatchNowPlaying(self, match, tag):

        res = match.group(0).decode()
        if res:
            try:
                j = json.loads(res)
                value = str(j['payload']['artist']) + ' - ' + str(j['payload']['song'])
                self.WriteStatus('NowPlaying', value, None)
            except:
                self.Error(['Now Playing: Invalid/Unexpected Response'])

    def UpdatePlayerID(self, value, qualifier):

        PlayerIDCmdString = 'heos://player/get_players\r\n'
        self.__UpdateHelper('PlayerID', PlayerIDCmdString, value, qualifier)

    def __MatchPlayerID(self, match, tag):

        value = match.group(1).decode()
        self.PlayerID = value
        self.WriteStatus('PlayerID', value, None)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'All' : 'on_all', 
            'One' : 'on_one', 
            'Off' : 'off'
        }

        ShuffleStates = {
            'On'  : 'on',
            'Off' : 'off'
        }

        Shuffle = self.ReadStatus('Shuffle', None)
        if not Shuffle: Shuffle = 'Off'
        RepeatCmdString = 'heos://player/set_play_mode?pid=' + self.PlayerID
        RepeatCmdString += '&repeat=' + ValueStateValues[value] + '&shuffle=' + ShuffleStates[Shuffle] + '\r\n'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):
        
        RepeatCmdString = 'heos://player/get_play_mode?pid=' + self.PlayerID + '\r\n'
        self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            'on_all' : 'All',
            'on_one' : 'One',
            'off'    : 'Off'
        }

        ShuffleValues = {
            'on'  : 'On',
            'off' : 'Off'
        }

        repeat = ValueStateValues[match.group(1).decode()]
        shuffle = ShuffleValues[match.group(2).decode()]
        self.WriteStatus('Repeat', repeat, None)
        self.WriteStatus('Shuffle', shuffle, None)

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on',
            'Off' : 'off'
        }
        RepeatStates = {
            'All' : 'on_all', 
            'One' : 'on_one', 
            'Off' : 'off'
        }

        Repeat = self.ReadStatus('Repeat', None)
        if not Repeat: Repeat = 'Off'
        ShuffleCmdString = 'heos://player/set_play_mode?pid=' + self.PlayerID + '&repeat=' + RepeatStates[Repeat] + '&shuffle=' + ValueStateValues[value] + '\r\n'
        self.__SetHelper('Shuffle', ShuffleCmdString, value, qualifier)

    def UpdateShuffle(self, value, qualifier):
                self.UpdateRepeat(value, qualifier)

    def SetSourceNavigation(self, value, qualifier):

        if len(self.SourceDict) > 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down']:
                if 'Page' in value:
                    numToAdvance = self.MaxSourceSearchResults
                else:
                    numToAdvance = 1
                if 'Down' in value and self.SourceMinLabel < len(self.SourceDict):
                    self.SourceMinLabel += numToAdvance
                    self.SourceMaxLabel += numToAdvance
                elif 'Up' in value:
                    self.SourceMinLabel -= numToAdvance
                    self.SourceMaxLabel -= numToAdvance
                if self.SourceMinLabel < 0:
                    self.SourceMinLabel = 0
                if self.SourceMaxLabel < self.MaxSourceSearchResults:
                    self.SourceMaxLabel = self.MaxSourceSearchResults

                if self.SourceMinLabel > len(self.SourceDict):
                    self.SourceMinLabel = len(self.SourceDict)
                    self.SourceMaxLabel = self.SourceMinLabel + self.MaxSourceSearchResults

                button = 1
                for i in range(self.SourceMinLabel, self.SourceMaxLabel):
                    try:
                        if self.SourceList[i]:
                            self.WriteStatus('SourceSearchResults', self.SourceList[i], {'Button': str(button)})
                            button += 1
                    except IndexError:
                        break
                if button <= self.MaxSourceSearchResults:
                    self.WriteStatus('SourceSearchResults', '***End of list***', {'Button': str(button)})
                    button += 1
                    for i in range(button, int(self.MaxSourceSearchResults) + 1):
                        self.WriteStatus('SourceSearchResults', '', {'Button': str(i)})
        else:
            self.Discard('Invalid Command for SetSourceNavigation')

    def SetSourceSearchSet(self, value, qualifier):

        if len(self.SourceDict) > 0: #Used to prevent error
            if 1 <= int(value) <= 8:
                sourceName = self.ReadStatus('SourceSearchResults', {'Button': value})
                if sourceName in self.SourceDict:
                    SourceSearchSetCmdString = self.SourceDict[sourceName]
                    self.__SetHelper('SourceSearchSet', SourceSearchSetCmdString, value, qualifier)

    def SetSourceUpdate(self, value, qualifier):

        self.SourceDict.clear()
        self.SourceList.clear()
        self.SourceMinLabel = 0 #Reset min label value
        self.SourceMaxLabel = self.MaxSourceSearchResults #Reset max label value
        print(self.SourceMaxLabel)
        for i in range(self.SourceMinLabel, self.SourceMaxLabel):
            try:
                loadingStr = '***Loading***' if i == 0 else ''
                self.WriteStatus('SourceSearchResults', loadingStr, {'Button': str(i + 1)})
            except IndexError:
                break
        res = self.SendAndWait('heos://browse/get_music_sources\r\n', 5, deliRex=self.responsejson)
        res = res.decode()
        if res:
            music_serviceSID = ''
            heos_serviceSID = ''
            noMusicService = False
            noHeosService = False

            #try:
            j = json.loads(res)
            for i in j['payload']: #Loop through the payload to find the SID's
                if 'heos_service' in i['name']:
                    heos_serviceSID = i['sid'] #Store heos_service (Aux Input)
                elif 'music_service' in i['name']:
                    music_serviceSID = i['sid'] #Store music_service (Stations)
            #except:
                #self.Error(['Source Update (Get Music Sources): Invalid/unexpected response.'])
            if music_serviceSID:
                res = self.SendAndWait('heos://browse/browse?sid={0}\r\n'.format(music_serviceSID), 5, deliRex=self.responsejson)
                res = res.decode()
                if res:
                    try:
                        j = json.loads(res)
                        for i in j['payload']: #Loop through payload to find available stations
                            if 'station' in i['type']: #Loop through to find the stations
                                self.SourceDict[i['name']] = 'heos://browse/play_stream?pid={0}&sid={1}&mid={2}&name={3}\r\n'.format(self.PlayerID, music_serviceSID, i['mid'], i['name']) 
                                self.SourceList.append(i['name'])
                    except:
                        self.Error(['Source Update (Browse Music Service): Invalid/unexpected response.'])
                else:
                    noMusicService = True
            if heos_serviceSID:
                res = self.SendAndWait('heos://browse/browse?sid={0}\r\n'.format(heos_serviceSID), 5, deliRex=self.responsejson)
                res = res.decode()
                if res:
                    try:
                        j = json.loads(res)
                        for i in j['payload']:
                            if 'AUX' in i['type'].upper() or 'AUX' in i['name'].upper(): #Check to see if the word aux is in the type or name (ambiguous Aux Input name based on protocol)
                                self.SourceDict[i['name']] = 'heos://browse/play_stream?pid={0}&sid={1}&mid={2}\r\n'.format(self.PlayerID, heos_serviceSID, i['mid'])
                                self.SourceList.append(i['name'])
                    except:
                        self.Error(['Source Update (Browse Heos Service): Invalid/unexpected response.'])
                else:
                    noHeosService = True
            if noMusicService == True or noHeosService == True:
                for i in range(self.SourceMinLabel, self.SourceMaxLabel):
                    try:
                        loadingStr = '***No Results***' if i == 0 else ''
                        self.WriteStatus('SourceSearchResults', loadingStr, {'Button': str(i + 1)})
                    except IndexError:
                        break
            elif self.SourceDict and self.SourceList:
                button = 1
                for i in range(self.SourceMinLabel, self.SourceMaxLabel):
                    try:
                        if self.SourceList[i]:
                            self.WriteStatus('SourceSearchResults', self.SourceList[i], {'Button': str(button)})
                            button += 1 #Increment button count by number of items being written
                    except IndexError:
                        break

                if button <= self.MaxSourceSearchResults: #If at the last result
                    self.WriteStatus('SourceSearchResults', '***End of list***', {'Button': str(button)})
                    button += 1
                    for i in range(button, int(self.MaxSourceSearchResults) + 1):
                        self.WriteStatus('SourceSearchResults', '', {'Button': str(i)})
            else:
                for i in range(self.SourceMinLabel, self.SourceMaxLabel):
                    try:
                        loadingStr = '***End of List***' if i == 0 else ''
                        self.WriteStatus('SourceSearchResults', loadingStr, {'Button': str(i + 1)})
                    except IndexError:
                        break
                self.Error(['Source Update (Writing to Labels): Invalid/unexpected response for SetSourceUpdate .'])

        else: #No response from the first query of sources
            for i in range(self.SourceMinLabel, self.SourceMaxLabel):
                try:
                    loadingStr = '***No Results***' if i == 0 else ''
                    self.WriteStatus('SourceSearchResults', loadingStr, {'Button': str(i + 1)})
                except IndexError:
                    break
            self.Error(['Source Update (Writing to Labels): Invalid/unexpected response.'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'      : 'heos://player/set_play_state?pid=' + self.PlayerID + '&state=play\r\n',
            'Pause'     : 'heos://player/set_play_state?pid=' + self.PlayerID + '&state=pause\r\n',
            'Stop'      : 'heos://player/set_play_state?pid=' + self.PlayerID + '&state=stop\r\n',
            'Next'      : 'heos://player/play_next?pid=' + self.PlayerID + '\r\n',
            'Previous'  : 'heos://player/play_previous?pid=' + self.PlayerID + '\r\n'
        }

        TransportCmdString = ValueStateValues[value]        
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        TransportCmdString = 'heos://player/get_play_state?pid=' + self.PlayerID + '\r\n'
        self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)

    def __MatchTransport(self, match, tag):

        ValueStateValues = {
            'play'  : 'Play',
            'pause' : 'Pause',
            'stop'  : 'Stop',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Transport', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'heos://player/set_volume?pid=' + self.PlayerID + '&level=' + str(value) + '\r\n'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'heos://player/get_volume?pid=' + self.PlayerID + '\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

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

        DEVICE_ERROR_CODES = {
            '1'  : 'Unrecognized Command.',
            '2'  : 'Invalid ID.',
            '3'  : 'Wrong Number of Command Arguments.',
            '4'  : 'Requested Data Not Available.',
            '5'  : 'Resource Currently Not Available.',
            '6'  : 'Invalid Credentials.',
            '7'  : 'Command Could Not Be Executed.',
            '8'  : 'User Not Logged In.',
            '9'  : 'Parameter Out of Range.',
            '10' : 'User Not Found.',
            '11' : 'Internal Error.',
            '12' : 'System Error.',
            '13' : 'Processing Previous Command.',
            '14' : 'Media Can Not Be Played.',
            '15' : 'Option Not Supported.',
            '16' : 'Too many commands in message queue to process.',
            '17' : 'Reached skip limit.'
        }

        self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0       

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastRepeatUpdate = 0
    
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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
        
    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.UpdatePlayerID( None, None)
        return result
    
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

