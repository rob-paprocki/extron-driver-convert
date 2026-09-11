from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict
import json
from datetime import datetime

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
        self._NumberofChannelListSearch = 5
        self._NumberofFavoritesFolderSearch = 5
        self._NumberofFavoritesItemSearch = 5
        self._NumberofFileSearch = 5
        self._NumberofFolderSearch = 5
        self._NumberofHistoryListSearch = 5
        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.Models = {
            'SMD 101': self.extr_42_1339_SMD_101,
            'SMD 202': self.extr_42_1339_SMD_202,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChangeDirectory': {'Parameters':['Directory Path'], 'Status': {}},
            'ChannelListNavigation': { 'Status': {}},
            'ChannelListSearchResults': {'Parameters':['Position'], 'Status': {}},
            'ChannelListUpdate': {'Parameters':['Type'], 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'CurrentClipLength': { 'Status': {}},
            'CurrentDirectory': { 'Status': {}},
            'CurrentPlaylistTrack': { 'Status': {}},
            'CurrentSourceItem': { 'Status': {}},
            'CurrentSourceStreamMode': {'Status': {}},
            'CurrentTimecode': { 'Status': {}},
            'FavoritesFolderNavigation': { 'Status': {}},
            'FavoritesFolderSearchResults': {'Parameters':['Position'], 'Status': {}},
            'FavoritesFolderUpOneDirectory': { 'Status': {}},
            'FavoritesItemandFolderUpdate': { 'Status': {}},
            'FavoritesItemNavigation': { 'Status': {}},
            'FavoritesItemSearchResults': {'Parameters':['Position'], 'Status': {}},
            'FileandFolderUpdate': {'Parameters':['Sort', 'Directory'], 'Status': {}},
            'FileNavigation': { 'Status': {}},
            'FileSearchResults': {'Parameters':['Position'], 'Status': {}},
            'FilterChannelListByExtension': {'Parameters':['File Extension'], 'Status': {}},
            'FilterFavoritesItemsByExtension': {'Parameters':['File Extension'], 'Status': {}},
            'FilterItemsByExtension': {'Parameters':['File Extension'], 'Status': {}},
            'FilterHistoryListByExtension': {'Parameters':['File Extension'], 'Status': {}},
            'FolderAction': {'Parameters':['Action'], 'Status': {}},
            'FolderNavigation': { 'Status': {}},
            'FolderSearchResults': {'Parameters':['Position'], 'Status': {}},
            'FolderUpOneDirectory': { 'Status': {}},
            'HDCPInputStatus101': { 'Status': {}},
            'HDCPInputStatus202': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'HistoryListNavigation': { 'Status': {}},
            'HistoryListSearchResults': {'Parameters':['Position'], 'Status': {}},
            'HistoryListUpdate': { 'Status': {}},
            'Input': { 'Status': {}},
            'LoadFileCommand': { 'Status': {}},
            'LoadPlaylistCommand': { 'Status': {}},
            'LoadSelectedChannel': { 'Status': {}},
            'LoadSelectedFavoritesItem': { 'Status': {}},
            'LoadSelectedItem': { 'Status': {}},
            'LoadSelectedHistoryItem': { 'Status': {}},
            'LoadSourceCommand': { 'Status': {}},
            'LoopPlay': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'Playback': { 'Status': {}},
            'PowerMode': { 'Status': {}},
            'ChannelPresetRecall': { 'Status': {}},
            'ChannelPresetRecallStep': { 'Status': {}},
            'ScreenSaver': { 'Status': {}},
            'Seek': {'Parameters':['Step'], 'Status': {}},
            'StandbyTimer': { 'Status': {}},
            'StepIntoFavoritesFolder': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPatterns': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aspr0?1\*([0-2])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'Amt(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'SubtE1\*(1|0)\r\n'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'PlyrZ1\*(|\d+:\d{2}:\d{2}\.\d{9})\r\n'), self.__MatchCurrentClipLength, None)
            self.AddMatchString(re.compile(b'Dir (.*?)/\r\n'), self.__MatchCurrentDirectory, None)
            self.AddMatchString(re.compile(b'PlyrL1\*(.*?)\r\n'), self.__MatchCurrentPlaylistTrack, None)
            self.AddMatchString(re.compile(b'PlyrU1\*(.*?)\r\n'), self.__MatchCurrentSourceItem, None)
            self.AddMatchString(re.compile(b'Smod([0-3])\r\n'), self.__MatchCurrentSourceStreamMode, None)
            self.AddMatchString(re.compile(b'PlyrT1\*(\d+)\r\n'), self.__MatchCurrentTrackNumber, None)
            self.AddMatchString(re.compile(b'PlstG (.*?)\r\n'), self.__MatchCurrentPlaylistTrackList, None)
            self.AddMatchString(re.compile(b'PlyrK1\*(|\d+:\d{2}:\d{2}\.\d{9})\r\n'), self.__MatchCurrentTimecode, None)
            self.AddMatchString(re.compile(b'HdcpI(1|2)\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Rate(\d{2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'In0?(1|2) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'PlyrR1\*(1|0)\r\n'), self.__MatchLoopPlay, None)
            self.AddMatchString(re.compile(b'Plyr([YSO])1(?:\*([0-2]))?\r\n'), self.__MatchPlayback, None)
            self.AddMatchString(re.compile(b'Psav(0|1)\r\n'), self.__MatchPowerMode, None)
            self.AddMatchString(re.compile(b'TvprT1\*(\d{2,3})\r\n'), self.__MatchChannelPresetRecall, None)
            self.AddMatchString(re.compile(b'SsavM([0-2])\r\n'), self.__MatchScreenSaver, None)
            self.AddMatchString(re.compile(b'Stat ([\d.]+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Test0?([023456789])\r\n'), self.__MatchTestPatterns, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([-+])(\d{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(\d{2})\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH

            self.InvalidCharRegex = re.compile('[' + re.escape(':*?"<>|') + ']') # used for SetChangeDirectory
            self.PresetRegex = re.compile('\"preset\":(?P<preset>\d{1,3}),')
            self.NameRegex = re.compile('\"name\":\"(?P<name>.*?)\"')
            self.URIRegex = re.compile('\"uri\":\"(?P<uri>.*?)\"')
            self.FileRegex = re.compile('(?P<filepath>.*?\.?(?:264|flv|m2t|m2ts|mov|mp4|m4v|sdp|ts|aac|m4a|wav|bmp|gif|jpg|jpeg|tif|tiff|png|m3u8|m3u|pls|jspf|xspf|mpg|mpeg|mp1|mp2|mp3|m1v|m1a|m2a|mpa|mpv|xfer_complete)) (?P<date>(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2}) GMT \d+\r\n', re.I)
            self.FavoritesRegex = re.compile('FavsG ({.*?)\r\n')

        self.FileExtensionStates = ['bmp', 'm3u', 'aac', 'm2ts', 'm2t', 'sdp', 'm4a', 'pls', 'mp4',
                                    'm3u8', 'ts', 'gif', 'mov', 'png', 'tiff', 'xspf', 'jspf', 'jpg',
                                    'tif', 'm4v', 'flv', 'wav', 'jpeg', '264', 'mpg', 'mpeg', 'mp1',
                                    'mp2', 'mp3', 'm1v', 'm1a', 'm2a', 'mpa', 'mpv', 'None']

        self.ChannelList = [] # holds list of all items (determined by ChannelListUpdate Type qualifier)
        self.ChannelLoadLookup = {} # dictionary used to map a channel number to a channel name or uri
        self.ChannelListUnfiltered = [] # used when changing between file extension filters
        self.ChannelMinLabel = 0
        self.ChannelMaxLabel = self.NumberofChannelListSearch
        self.ChannelFileExtensionFilter = 'None'
        self.CurrentPlayingPlaylist = ''
        self.CurrentTrackNumber = ''
        self.FavoritesDirectory = OrderedDict() # stores main directory
        self.FavoritesTraverseList = [] # used to keep track of location in directory
        self.FavoritesFolderList = [] # used to display the folders for FavoritesFolderSearchResults
        self.FavoritesItemList = [] # used to display the items for FavoritesItemSearchResults
        self.FavoritesItemListUnfiltered = [] # used when changing between file extension filters
        self.FavoritesFolderMinLabel = 0
        self.FavoritesFolderMaxLabel = self.NumberofFavoritesFolderSearch
        self.FavoritesItemMinLabel = 0
        self.FavoritesItemMaxLabel = self.NumberofFavoritesItemSearch
        self.FavoritesItemExtensionFilter = 'None'
        self.FavoritesItemExtensionFilterCopy = 'None' # used to ensure new results are filtered properly when navigating
        self.FileandFolderUpdateParams = None # used for SetFolderUpOneDirectory
        self.AllPathsList = [] # used to create main directory
        self.Directory = OrderedDict() # stores main directory
        self.CurrentDirectoryList = [] # used to keep track of current directory
        self.FolderList = [] # used to display the folders for FolderSearchResults
        self.FileList = [] # used to display the files for FileSearchResults
        self.FileListUnfiltered = [] # used when changing between file extension filters
        self.FolderMinLabel = 0
        self.FolderMaxLabel = self.NumberofFolderSearch
        self.FileMinLabel = 0
        self.FileMaxLabel = self.NumberofFileSearch
        self.FileExtensionFilter = 'None'
        self.FileExtensionFilterCopy = 'None' # used to ensure new results are filtered properly when navigating
        self.HistoryList = [] # holds list of all uri's
        self.HistoryListUnfiltered = [] # used when changing between file extension filters
        self.HistoryMinLabel = 0
        self.HistoryMaxLabel = self.NumberofHistoryListSearch
        self.HistoryFileExtensionFilter = 'None'

    @property
    def NumberofChannelListSearch(self):
        return self._NumberofChannelListSearch

    @NumberofChannelListSearch.setter
    def NumberofChannelListSearch(self, value):
        self._NumberofChannelListSearch = int(value)
        self.ChannelMaxLabel = self._NumberofChannelListSearch

    @property
    def NumberofFavoritesFolderSearch(self):
        return self._NumberofFavoritesFolderSearch

    @NumberofFavoritesFolderSearch.setter
    def NumberofFavoritesFolderSearch(self, value):
        self._NumberofFavoritesFolderSearch = int(value)
        self.FavoritesFolderMaxLabel = self._NumberofFavoritesFolderSearch

    @property
    def NumberofFavoritesItemSearch(self):
        return self._NumberofFavoritesItemSearch

    @NumberofFavoritesItemSearch.setter
    def NumberofFavoritesItemSearch(self, value):
        self._NumberofFavoritesItemSearch = int(value)
        self.FavoritesItemMaxLabel = self._NumberofFavoritesItemSearch

    @property
    def NumberofFileSearch(self):
        return self._NumberofFileSearch

    @NumberofFileSearch.setter
    def NumberofFileSearch(self, value):
        self._NumberofFileSearch = int(value)
        self.FileMaxLabel = self._NumberofFileSearch

    @property
    def NumberofFolderSearch(self):
        return self._NumberofFolderSearch

    @NumberofFolderSearch.setter
    def NumberofFolderSearch(self, value):
        self._NumberofFolderSearch = int(value)
        self.FolderMaxLabel = self._NumberofFolderSearch

    @property
    def NumberofHistoryListSearch(self):
        return self._NumberofHistoryListSearch

    @NumberofHistoryListSearch.setter
    def NumberofHistoryListSearch(self, value):
        self._NumberofHistoryListSearch = int(value)
        self.HistoryMaxLabel = self._NumberofHistoryListSearch

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAspectRatio(self, value, qualifier):
    
        ValueStateValues = {
            'Zoom'   : '0',
            'Fill'   : '1',
            'Follow' : '2'
        }

        AspectRatioCmdString = 'w1*{0}ASPR\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'w1ASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0' : 'Zoom',
            '1' : 'Fill',
            '2' : 'Follow'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        AudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateCurrentPlaylistTrack(self, value, qualifier):

        CurrentPlaylistTrackCmdString = 'wL1PLYR\r'
        self.__UpdateHelper('CurrentPlaylistTrack', CurrentPlaylistTrackCmdString, value, qualifier)

    def __MatchCurrentPlaylistTrack(self, match, tag):

        value = match.group(1).decode() if match.group(1).decode().split('.')[-1] in ['m3u', 'm3u8', 'pls', 'jspf', 'xspf'] else '' # if extension is a playlist, write result, else write empty string (known FW issue)
        self.WriteStatus('CurrentPlaylistTrack', value, None)

    def UpdateCurrentSourceItem(self, value, qualifier):

        CurrentSourceItemCmdString = 'wU1PLYR\r' # get current playing item
        self.__UpdateHelper('CurrentSourceItem', CurrentSourceItemCmdString, value, qualifier)

    def __MatchCurrentSourceItem(self, match, tag):

        if match.group(1).decode().split('.')[-1] not in ['m3u', 'm3u8', 'pls', 'jspf', 'xspf']: # if item is not a playlist
            value = match.group(1).decode()
            self.WriteStatus('CurrentSourceItem', value, None) # write current playing track
        else:
            self.CurrentPlayingPlaylist = match.group(1).decode() # save in global variable to use in MatchCurrentTrackNumber
            self.Send('wT1PLYR\r') # get current track number

    def __MatchCurrentTrackNumber(self, match, tag):
    
        self.CurrentTrackNumber = match.group(1).decode()  # save in global variable to use in MatchCurrentPlaylistTrackList
        if self.CurrentPlayingPlaylist:
            self.Send('wG{}PLST\r'.format(self.CurrentPlayingPlaylist))  # get current playlist track list

    def __MatchCurrentPlaylistTrackList(self, match, tag):
    
        jsonData = json.loads(match.group(1).decode())
        try:
            value = jsonData[int(self.CurrentTrackNumber) - 1]['location'][0]  # use self.CurrentTrackNumber as index to get current playing track
        except (ValueError, KeyError, IndexError):  # if jsonData is empty -> []
            value = ''
        self.WriteStatus('CurrentSourceItem', value, None)  # write current playing track
        
    def UpdateCurrentSourceStreamMode(self, value, qualifier):
    
        CurrentSourceStreamModeCmdString = 'wSMOD\r'
        self.__UpdateHelper('CurrentSourceStreamMode', CurrentSourceStreamModeCmdString, value, qualifier)

    def __MatchCurrentSourceStreamMode(self, match, tag):

        try:
            value = self.StreamModeStates[match.group(1).decode()]
            self.WriteStatus('CurrentSourceStreamMode', value, None)
        except KeyError:
            pass
            
    def SetChangeDirectory(self, value, qualifier):

        path = qualifier['Directory Path']
        if re.search(self.InvalidCharRegex, path):
            self.Discard('Invalid Command for SetChangeDirectory')
        else:
            if path.startswith('root'):
                path = path[4:] # remove 'root' from target folder name

            ChangeDirectoryCmdString = 'w{0}/CJ\r'.format(path)
            self.__SetHelper('ChangeDirectory', ChangeDirectoryCmdString, value, qualifier)

    def SetChannelListUpdate(self, value, qualifier):
    
        if qualifier['Type'] in ['Channel', 'Name', 'URI']:
            for position in range(1, self.NumberofChannelListSearch + 1):
                string = '*** Loading... Please wait ***' if position == 1 else ''  # write loading for position 1 and empty strings after
                self.WriteStatus('ChannelListSearchResults', string, {'Position': str(position)})

            CmdString = 'wGTVPR\r'
            res = self.__SetHelperSync('ChannelListUpdate', CmdString, value, qualifier)
            if res:
                States = {  # used to determine which regex and group name to use
                    'Channel': [self.PresetRegex, 'preset'],
                    'Name': [self.NameRegex, 'name'],
                    'URI': [self.URIRegex, 'uri']
                }
                resIterPreset = re.finditer(self.PresetRegex, res)  # used to get all preset numbers
                resIterItem = re.finditer(States[qualifier['Type']][0], res)  # used to get all items
                self.ChannelFileExtensionFilter = 'None'  # reset file extension filter
                self.ChannelMinLabel = 0  # reset min label value
                self.ChannelMaxLabel = self.NumberofChannelListSearch  # reset max label value
                self.ChannelList.clear()
                self.ChannelListUnfiltered.clear()
                self.ChannelLoadLookup.clear()

                presetList = []  # define preset list used to create ChannelLoadLookup
                for preset in resIterPreset:  # get all preset numbers
                    presetList.append(preset.group('preset'))  # add preset number to list

                for item in resIterItem:  # get all items
                    self.ChannelList.append(item.group(States[qualifier['Type']][1]))  # add item to list
                if qualifier['Type'] == 'URI':  # only use file extension filter if items are uri's
                    self.ChannelListUnfiltered = self.ChannelList  # create copy of channels list (used when file extension filter is set)

                for item in self.ChannelList:  # create ChannelLoadLookup
                    self.ChannelLoadLookup[item] = presetList[self.ChannelList.index(item)]  # add item as key and preset number as value to dictionary

                self.ChannelListPositionHandler()  # update search result positions
            else:
                self.WriteStatus('ChannelListSearchResults', '*** Timeout ***', {'Position': '1'})  # write no response for position 1 if no response
        else:
            self.Discard('Invalid Command for SetChannelListUpdate')
            
    def ChannelListPositionHandler(self):

        position = 1
        for index in range(self.ChannelMinLabel, self.ChannelMaxLabel):
            try:
                self.WriteStatus('ChannelListSearchResults', self.ChannelList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last item in channels list)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofChannelListSearch: # if last result
            string = '*** End of List ***' if self.ChannelList else '*** No Items to Show ***'
            self.WriteStatus('ChannelListSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no items to show
            position += 1
            for index in range(position, self.NumberofChannelListSearch+1):
                self.WriteStatus('ChannelListSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def SetChannelListNavigation(self, value, qualifier):

        if self.ChannelList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if channels list is populated and value selected
            NumberOfAdvance = self.NumberofChannelListSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.ChannelMaxLabel <= len(self.ChannelList): # prevent from scrolling when end of list is reached
                self.ChannelMinLabel += NumberOfAdvance
                self.ChannelMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.ChannelMinLabel -= NumberOfAdvance
                self.ChannelMaxLabel -= NumberOfAdvance

            if self.ChannelMinLabel < 0: # prevents from scrolling up above first result
                self.ChannelMinLabel = 0

            if self.ChannelMaxLabel < self.NumberofChannelListSearch: # prevents from scrolling past more results that are configured
                self.ChannelMaxLabel = self.NumberofChannelListSearch

            if self.ChannelMinLabel > len(self.ChannelList): # prevents from scrolling past more items that exist
                self.ChannelMinLabel = len(self.ChannelList)
                self.ChannelMaxLabel = self.ChannelMinLabel + self.NumberofChannelListSearch

            self.ChannelListPositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetChannelListNavigation')

    def SetFilterChannelListByExtension(self, value, qualifier):

        if self.ChannelListUnfiltered and qualifier['File Extension'] in self.FileExtensionStates: # if unfiltered channels list is populated and valid qualifier
            self.ChannelFileExtensionFilter = qualifier['File Extension']
            self.ChannelMinLabel = 0 # reset min label value
            self.ChannelMaxLabel = self.NumberofChannelListSearch # reset max label value
            if self.ChannelFileExtensionFilter != 'None': # if file extension filter is set
                ChannelListFiltered = [] # define filtered channels list
                for uri in self.ChannelListUnfiltered:
                    if uri.lower().endswith(self.ChannelFileExtensionFilter): # if file extension filter set is in uri
                        ChannelListFiltered.append(uri) # add uri to filtered list
                self.ChannelList = ChannelListFiltered # overwrite channels list as filtered channels list
            else: # if file extension filter is None
                self.ChannelList = self.ChannelListUnfiltered # overwrite channels list as unfiltered channels list
            self.ChannelListPositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetFilterChannelListByExtension')

    def SetLoadSelectedChannel(self, value, qualifier):

        if self.ChannelList and 1 <= int(value) <= 100: # if channel list is populated and value is within range
            item = self.ReadStatus('ChannelListSearchResults', {'Position': value}) # get item from selected position
            if item and item not in ['*** End of List ***', '*** Timeout ***', '*** No Items to Show ***']: # check if item exists and not invalid
                CmdString = '{0}T'.format(self.ChannelLoadLookup[item]) # load channel
                self.__SetHelper('LoadSelectedChannel', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoadSelectedChannel')
        else:
            self.Discard('Invalid Command for SetLoadSelectedChannel')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        ClosedCaptionCmdString = 'wE1*{0}SUBT\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'wE1SUBT\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateCurrentClipLength(self, value, qualifier):

        CurrentClipLengthCmdString = 'wZ1PLYR\r'
        self.__UpdateHelper('CurrentClipLength', CurrentClipLengthCmdString, value, qualifier)

    def __MatchCurrentClipLength(self, match, tag):

        value = match.group(1).decode().split('.')[0]
        self.WriteStatus('CurrentClipLength', value, None)

    def UpdateCurrentDirectory(self, value, qualifier):

        CurrentDirectoryCmdString = 'wCJ\r'
        self.__UpdateHelper('CurrentDirectory', CurrentDirectoryCmdString, value, qualifier)

    def __MatchCurrentDirectory(self, match, tag):

        value = '/ (root)' if match.group(1).decode() == '' else '/{}'.format(match.group(1).decode())
        self.WriteStatus('CurrentDirectory', value, None)
        self.CurrentDirectoryList.clear() # clear list to update with new results
        if value != '/ (root)': # dont add anything if in root directory
            for item in value.lstrip('/').split('/'): # remove leading '/' and split items into list
                self.CurrentDirectoryList.append(item) # add items

    def UpdateCurrentTimecode(self, value, qualifier):

        CurrentTimecodeCmdString = 'wK1PLYR\r'
        self.__UpdateHelper('CurrentTimecode', CurrentTimecodeCmdString, value, qualifier)

    def __MatchCurrentTimecode(self, match, tag):

        value = match.group(1).decode().split('.')[0]
        self.WriteStatus('CurrentTimecode', value, None)

    def SetFavoritesItemandFolderUpdate(self, value, qualifier):

        for position in range(1, self.NumberofFavoritesFolderSearch+1):
            string = '*** Loading... Please wait ***' if position == 1 else '' # write loading for position 1 and empty strings after
            self.WriteStatus('FavoritesFolderSearchResults', string, {'Position': str(position)})

        for position in range(1, self.NumberofFavoritesItemSearch+1):
            string = '*** Loading... Please wait ***' if position == 1 else '' # write loading for position 1 and empty strings after
            self.WriteStatus('FavoritesItemSearchResults', string, {'Position': str(position)})

        CmdString = 'wGFAVS\r'
        res = self.__SetHelperSync('FavoritesItemandFolderUpdate', CmdString, value, qualifier)
        if res:
            results = re.search(self.FavoritesRegex, res)
            jsonData = json.loads(results.group(1))
            self.FavoritesFolderMinLabel = 0 # reset min label value
            self.FavoritesFolderMaxLabel = self.NumberofFavoritesFolderSearch # reset max label value
            self.FavoritesItemMinLabel = 0 # reset min label value
            self.FavoritesItemMaxLabel = self.NumberofFavoritesItemSearch # reset max label value
            self.FavoritesItemExtensionFilter = 'None' # reset item extension filter
            self.FavoritesItemExtensionFilterCopy = 'None' # reset item extension filter copy
            self.FavoritesDirectory.clear() # clear directory before updating new results (self.FavoritesFolderList and self.FavoritesItemList is cleared in FavoritesGetResultsHandler)

            self.BuildFavoritesDirectory(jsonData) # creates favorites directory
            self.FavoritesDirectory = self.FavoritesDirectory['root']

            self.FavoritesGetResultsHandler('Update') # get/write results
        else:
            self.WriteStatus('FavoritesFolderSearchResults', '*** Timeout ***', {'Position': '1'}) # write no response for position 1 if no response
            self.WriteStatus('FavoritesItemSearchResults', '*** Timeout ***', {'Position': '1'}) # write no response for position 1 if no response

    def BuildFavoritesDirectory(self, jsonData, b=None, c=None):

        if jsonData['name'] == 'root':
            branch = self.FavoritesDirectory.setdefault('root', OrderedDict())
            parent_branch = branch
        else:
            branch = b
            parent_branch = c
        child = jsonData.get('children')
        if child:
            for i in child:
                if i['type'] == 'folder':
                    if i.get('children'):
                        branch = branch.setdefault(i['name'], OrderedDict())
                        self.BuildFavoritesDirectory(i, branch, parent_branch)
                        branch = parent_branch
                    else:
                        branch[i['name']] = OrderedDict()
                elif i['type'] == 'uri':
                    branch[i['name']] = i['uri']

    def FavoritesGetResultsHandler(self, Type=''):

        tempDirectory = self.FavoritesDirectory # create copy of main directory (used for loop)
        for result in self.FavoritesTraverseList:
            tempDirectory = tempDirectory[result] # obtain location in self.FavoritesDirectory based on items in self.FavoritesTraverseList

        if Type == 'Check':
            return tempDirectory # return current location in directory

        self.FavoritesFolderList.clear() # clear folder list to add new folders
        self.FavoritesItemList.clear() # clear item list to add new items
        for result in tempDirectory.keys():
            if isinstance(tempDirectory[result], str): # if item is a string (uri)
                self.FavoritesItemList.append(result) # add item to item list
            else: # if folder
                self.FavoritesFolderList.append(result) # add folder to folder list
        self.FavoritesItemListUnfiltered = self.FavoritesItemList # create copy of unfiltered item list (used when changing between item extension filters)

        if self.FavoritesItemExtensionFilterCopy != 'None': # if navigating and item extension filter is set
            self.SetFilterFavoritesItemsByExtension('FavoritesGetResultsHandler', {'File Extension': self.FavoritesItemExtensionFilterCopy}) # filter new results

        self.FavoritesFolderPositionHandler() # update folder search result positions
        self.FavoritesItemPositionHandler() # update item search result positions

    def FavoritesFolderPositionHandler(self):

        position = 1
        for index in range(self.FavoritesFolderMinLabel, self.FavoritesFolderMaxLabel):
            try:
                self.WriteStatus('FavoritesFolderSearchResults', self.FavoritesFolderList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last folder)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofFavoritesFolderSearch: # if last result
            string = '*** End of List ***' if self.FavoritesFolderList else '*** No Folders to Show ***'
            self.WriteStatus('FavoritesFolderSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no folders to show
            position += 1
            for index in range(position, self.NumberofFavoritesFolderSearch+1):
                self.WriteStatus('FavoritesFolderSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def FavoritesItemPositionHandler(self):

        position = 1
        for index in range(self.FavoritesItemMinLabel, self.FavoritesItemMaxLabel):
            try:
                self.WriteStatus('FavoritesItemSearchResults', self.FavoritesItemList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last item)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofFavoritesItemSearch: # if last result
            string = '*** End of List ***' if self.FavoritesItemList else '*** No Items to Show ***'
            self.WriteStatus('FavoritesItemSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no items to show
            position += 1
            for index in range(position, self.NumberofFavoritesItemSearch+1):
                self.WriteStatus('FavoritesItemSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def SetFavoritesFolderNavigation(self, value, qualifier):

        if self.FavoritesFolderList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if folder list is populated and value selected
            NumberOfAdvance = self.NumberofFavoritesFolderSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.FavoritesFolderMaxLabel <= len(self.FavoritesFolderList): # prevent from scrolling when end of list is reached
                self.FavoritesFolderMinLabel += NumberOfAdvance
                self.FavoritesFolderMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.FavoritesFolderMinLabel -= NumberOfAdvance
                self.FavoritesFolderMaxLabel -= NumberOfAdvance

            if self.FavoritesFolderMinLabel < 0: # prevents from scrolling up above first result
                self.FavoritesFolderMinLabel = 0

            if self.FavoritesFolderMaxLabel < self.NumberofFavoritesFolderSearch: # prevents from scrolling past more results that are configured
                self.FavoritesFolderMaxLabel = self.NumberofFavoritesFolderSearch

            if self.FavoritesFolderMinLabel > len(self.FavoritesFolderList): # prevents from scrolling past more folders that exist
                self.FavoritesFolderMinLabel = len(self.FavoritesFolderList)
                self.FavoritesFolderMaxLabel = self.FavoritesFolderMinLabel + self.NumberofFavoritesFolderSearch

            self.FavoritesFolderPositionHandler() # update folder search result positions
        else:
            self.Discard('Invalid Command for SetFavoritesFolderNavigation')

    def SetFavoritesItemNavigation(self, value, qualifier):

        if self.FavoritesItemList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if item list is populated and value selected
            NumberOfAdvance = self.NumberofFavoritesItemSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.FavoritesItemMaxLabel <= len(self.FavoritesItemList): # prevent from scrolling when end of list is reached
                self.FavoritesItemMinLabel += NumberOfAdvance
                self.FavoritesItemMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.FavoritesItemMinLabel -= NumberOfAdvance
                self.FavoritesItemMaxLabel -= NumberOfAdvance

            if self.FavoritesItemMinLabel < 0: # prevents from scrolling up above first result
                self.FavoritesItemMinLabel = 0

            if self.FavoritesItemMaxLabel < self.NumberofFavoritesItemSearch: # prevents from scrolling past more results that are configured
                self.FavoritesItemMaxLabel = self.NumberofFavoritesItemSearch

            if self.FavoritesItemMinLabel > len(self.FavoritesItemList): # prevents from scrolling past more items that exist
                self.FavoritesItemMinLabel = len(self.FavoritesItemList)
                self.FavoritesItemMaxLabel = self.FavoritesItemMinLabel + self.NumberofFavoritesItemSearch

            self.FavoritesItemPositionHandler() # update item search result positions
        else:
            self.Discard('Invalid Command for SetFavoritesItemNavigation')

    def SetStepIntoFavoritesFolder(self, value, qualifier):

        if self.FavoritesFolderList and 1 <= int(value) <= 100: # if folder list is populated and value within range
            folder = self.ReadStatus('FavoritesFolderSearchResults', {'Position': value}) # get folder name from selected position
            if folder and folder not in ['*** End of List ***', '*** Timeout ***', '*** No Folders to Show ***']: # if folder exits and is not invalid
                self.FavoritesFolderMinLabel = 0 # reset min label value
                self.FavoritesFolderMaxLabel = self.NumberofFolderSearch # reset max label value
                if self.FavoritesItemExtensionFilter != 'None': # if item extension filter is set
                    self.FavoritesItemExtensionFilterCopy = self.FavoritesItemExtensionFilter # create a copy of it to filter new results
                self.FavoritesTraverseList.append(folder) # append folder selected to self.FavoritesTraverseList
                self.FavoritesGetResultsHandler('Update') # get/write new results
            else:
                self.Discard('Invalid Command for SetStepIntoFavoritesFolder')
        else:
            self.Discard('Invalid Command for SetStepIntoFavoritesFolder')

    def SetLoadSelectedFavoritesItem(self, value, qualifier):

        if self.FavoritesItemList and 1 <= int(value) <= 100: # if item list is populated and value within range
            item = self.ReadStatus('FavoritesItemSearchResults', {'Position': value}) # get item name from selected position
            if item and item not in ['*** End of List ***', '*** Timeout ***', '*** No Items to Show ***']: # if item exits and is not invalid
                currentLocation = self.FavoritesGetResultsHandler('Check') # grab item uri from directory
                CmdString = 'wU1*{}PLYR\r'.format(currentLocation[item]) # load item
                self.__SetHelper('LoadSelectedFavoritesItem', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoadSelectedFavoritesItem')
        else:
            self.Discard('Invalid Command for SetLoadSelectedFavoritesItem')

    def SetFilterFavoritesItemsByExtension(self, value, qualifier):

        if self.FavoritesItemListUnfiltered and qualifier['File Extension'] in self.FileExtensionStates: # if unfiltered item list is populated and valid qualifier
            self.FavoritesItemExtensionFilter = qualifier['File Extension']
            self.FavoritesItemExtensionFilterCopy = 'None' # reset item extension filter copy
            self.FavoritesItemMinLabel = 0 # reset min label value
            self.FavoritesItemMaxLabel = self.NumberofFavoritesItemSearch # reset max label value
            if self.FavoritesItemExtensionFilter != 'None': # if item extension filter is set
                itemListFiltered = [] # define filtered item list
                for item in self.FavoritesItemListUnfiltered:
                    if item.lower().endswith(self.FavoritesItemExtensionFilter): # if item extension filter set is in uri
                        itemListFiltered.append(item) # add item to filtered list
                self.FavoritesItemList = itemListFiltered # overwrite item list as filtered item list
            else: # if no item extension filter is set
                self.FavoritesItemList = self.FavoritesItemListUnfiltered # overwrite item list as unfiltered item list

            if value != 'FavoritesGetResultsHandler': # self.FavoritesItemPositionHandler() is already called in FavoritesGetResultsHandler
                self.FavoritesItemPositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetFilterFavoritesItemsByExtension')

    def SetFavoritesFolderUpOneDirectory(self, value, qualifier):

        if self.FavoritesTraverseList: # check if traverse list is populated
            self.FavoritesTraverseList.pop() # remove last folder from traverse list
            if self.FavoritesItemExtensionFilter != 'None': # if item extension filter is set
                self.FavoritesItemExtensionFilterCopy = self.FavoritesItemExtensionFilter # create a copy of it to filter new results
            self.FavoritesGetResultsHandler('Update') # get/write new results
        else:
            self.Discard('Invalid Command for SetFavoritesFolderUpOneDirectory')

    def SetFileandFolderUpdate(self, value, qualifier):
    
        DirectoryStates = {
            'Current Directory Only': 'wdf\r',
            'Current Directory and Below': 'wlf\r'
        }

        if qualifier['Sort'] in ['Alphanumeric', 'Date Modified'] and qualifier['Directory'] in DirectoryStates:
            for position in range(1, self.NumberofFolderSearch + 1):
                string = '*** Loading... Please wait ***' if position == 1 else ''  # write loading for position 1 and empty strings after
                self.WriteStatus('FolderSearchResults', string, {'Position': str(position)})

            for position in range(1, self.NumberofFileSearch + 1):
                string = '*** Loading... Please wait ***' if position == 1 else ''  # write loading for position 1 and empty strings after
                self.WriteStatus('FileSearchResults', string, {'Position': str(position)})

            if value != 'FolderUpOneDirectory':  # necessary for when SetFolderUpOneDirectory calls SetFileandFolderUpdate
                self.FileandFolderUpdateParams = qualifier
            CmdString = DirectoryStates[self.FileandFolderUpdateParams['Directory']]
            res = self.__SetHelperSync('FileandFolderUpdate', CmdString, value, qualifier)
            if res:
                resIter = re.finditer(self.FileRegex, res)
                self.FolderMinLabel = 0  # reset min label value
                self.FolderMaxLabel = self.NumberofFolderSearch  # reset max label value
                self.FileMinLabel = 0  # reset min label value
                self.FileMaxLabel = self.NumberofFileSearch  # reset max label value
                if value != 'FolderUpOneDirectory':  # necessary for when SetFolderUpOneDirectory calls SetFileandFolderUpdate
                    self.FileExtensionFilter = 'None'  # reset file extension filter
                    self.FileExtensionFilterCopy = 'None'  # reset file extension filter copy
                self.AllPathsList.clear()
                self.Directory.clear()
                for file in resIter:
                    tempList = file.group('filepath').split('/') + [file.group('date')]  # create temp list to split filepath into list and append date
                    self.AllPathsList.append(tempList)  # append temp list to self.AllPathsList

                if self.FileandFolderUpdateParams['Sort'] == 'Date Modified':  # if sort by date modified (alphanumeric sorting handled in GetResultsHandler)
                    self.AllPathsList.sort(key=lambda date: datetime.strptime(date[-1], '%a, %d %b %Y %H:%M:%S'), reverse=True)  # sort self.AllPathsList by date modified
                for path in self.AllPathsList:
                    branch = self.Directory
                    for p in path[0:-2]:  # -2 index to not include date modified in self.Directory
                        branch = branch.setdefault(p, OrderedDict())
                    branch[path[-2]] = 'File'  # mark all files w/ 'File' tag string for dictionary value (used when file extension filter is set and LoadSelectedItem)

                self.GetResultsHandler('Initial')  # get/write initial results
            else:
                self.WriteStatus('FolderSearchResults', '*** Timeout ***', {'Position': '1'})  # write no response for position 1 if no response
                self.WriteStatus('FileSearchResults', '*** Timeout ***', {'Position': '1'})  # write no response for position 1 if no response
        else:
            self.Discard('Invalid Command for SetFileandFolderUpdate')

    def GetResultsHandler(self, Type=''):

        if Type == 'Initial': # added to prevent MatchCurrentDirectory from updating self.CurrentDirectoryList when not needed
            self.Send('wCJ\r') # get current directory to update self.CurrentDirectoryList (via MatchCurrentDirectory method)
        if Type != 'Initial': # added to not change directory for initial results
            path = '/{}'.format('/'.join(self.CurrentDirectoryList)) # join items in self.CurrentDirectoryList to create filepath string
            self.SetChangeDirectory(None, {'Directory Path': path}) # change directory on device to match current directory

        tempDirectory = self.Directory # create copy of main directory (used for loop)
        if Type != 'Initial': # since self.CurrentDirectoryList doesn't have any items upon initial update
            for result in self.CurrentDirectoryList:
                try:
                    tempDirectory = tempDirectory[result] # obtain location in self.Directory based on items in self.CurrentDirectoryList
                except KeyError:
                    continue

        self.FolderList.clear() # clear folder list to add new folders
        self.FileList.clear() # clear file list to add new files
        for result in tempDirectory.keys():
            if tempDirectory[result] == 'File': # if item is a file
                self.FileList.append(result) # add file to file list
            else: # if item is a folder
                self.FolderList.append(result) # add folder to folder list
        if self.FileandFolderUpdateParams['Sort'] == 'Alphanumeric': # if sort by alphanumeric (case insensitive)
            self.FolderList = sorted(self.FolderList, key=lambda s: s.lower()) # sort folder list alphanumeric
            self.FileList = sorted(self.FileList, key=lambda s: s.lower()) # sort file list alphanumeric
        self.FileListUnfiltered = self.FileList # create copy of unfiltered file list (used when changing between file extension filters)

        if self.FileExtensionFilterCopy != 'None': # if navigating and file extension filter is set
            self.SetFilterItemsByExtension('GetResultsHandler', {'File Extension': self.FileExtensionFilterCopy}) # filter new results

        self.FolderPositionHandler() # update folder search result positions
        self.FilePositionHandler() # update file search result positions

    def FolderPositionHandler(self):

        position = 1
        for index in range(self.FolderMinLabel, self.FolderMaxLabel):
            try:
                self.WriteStatus('FolderSearchResults', self.FolderList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last folder)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofFolderSearch: # if last result
            string = '*** End of List ***' if self.FolderList else '*** No Folders to Show ***'
            self.WriteStatus('FolderSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no folders to show
            position += 1
            for index in range(position, self.NumberofFolderSearch+1):
                self.WriteStatus('FolderSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def FilePositionHandler(self):

        position = 1
        for index in range(self.FileMinLabel, self.FileMaxLabel):
            try:
                self.WriteStatus('FileSearchResults', self.FileList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last file)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofFileSearch: # if last result
            string = '*** End of List ***' if self.FileList else '*** No Items to Show ***'
            self.WriteStatus('FileSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no items to show
            position += 1
            for index in range(position, self.NumberofFileSearch+1):
                self.WriteStatus('FileSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def SetFolderNavigation(self, value, qualifier):

        if self.FolderList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if folder list is populated and value selected
            NumberOfAdvance = self.NumberofFolderSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.FolderMaxLabel <= len(self.FolderList): # prevent from scrolling when end of list is reached
                self.FolderMinLabel += NumberOfAdvance
                self.FolderMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.FolderMinLabel -= NumberOfAdvance
                self.FolderMaxLabel -= NumberOfAdvance

            if self.FolderMinLabel < 0: # prevents from scrolling up above first result
                self.FolderMinLabel = 0

            if self.FolderMaxLabel < self.NumberofFolderSearch: # prevents from scrolling past more results that are configured
                self.FolderMaxLabel = self.NumberofFolderSearch

            if self.FolderMinLabel > len(self.FolderList): # prevents from scrolling past more folders that exist
                self.FolderMinLabel = len(self.FolderList)
                self.FolderMaxLabel = self.FolderMinLabel + self.NumberofFolderSearch

            self.FolderPositionHandler() # update folder search result positions
        else:
            self.Discard('Invalid Command for SetFolderNavigation')

    def SetFileNavigation(self, value, qualifier):

        if self.FileList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if file list is populated and value selected
            NumberOfAdvance = self.NumberofFileSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.FileMaxLabel <= len(self.FileList): # prevent from scrolling when end of list is reached
                self.FileMinLabel += NumberOfAdvance
                self.FileMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.FileMinLabel -= NumberOfAdvance
                self.FileMaxLabel -= NumberOfAdvance

            if self.FileMinLabel < 0: # prevents from scrolling up above first result
                self.FileMinLabel = 0

            if self.FileMaxLabel < self.NumberofFileSearch: # prevents from scrolling past more results that are configured
                self.FileMaxLabel = self.NumberofFileSearch

            if self.FileMinLabel > len(self.FileList): # prevents from scrolling past more folders that exist
                self.FileMinLabel = len(self.FileList)
                self.FileMaxLabel = self.FileMinLabel + self.NumberofFileSearch

            self.FilePositionHandler() # update file search result positions
        else:
            self.Discard('Invalid Command for SetFileNavigation')

    def SetFolderAction(self, value, qualifier):

        if self.FolderList and qualifier['Action'] in ['Step into Folder', 'Load Folder'] and 1 <= int(value) <= 100: # if folder list is populated, valid qualifier, and value within range
            folder = self.ReadStatus('FolderSearchResults', {'Position': value}) # get folder name from selected position
            if folder and folder not in ['*** End of List ***', '*** Timeout ***', '*** No Folders to Show ***']: # if folder exits and is not invalid
                if qualifier['Action'] == 'Load Folder':
                    header = '/' if len(self.CurrentDirectoryList) >= 1 else '' # if more than 1 folder in self.CurrentDirectoryList, add leading '/' to form CmdString properly
                    fullFolderPath = '{0}{1}{2}'.format('/'.join(self.CurrentDirectoryList), header, folder) # join current directory path with selected folder
                    CmdString = 'wU1*file:///{0}PLYR\r'.format(fullFolderPath) # load folder
                    self.__SetHelper('FolderAction', CmdString, value, qualifier)
                else: # Step into Folder
                    self.FolderMinLabel = 0 # reset min label value
                    self.FolderMaxLabel = self.NumberofFolderSearch # reset max label value
                    if self.FileExtensionFilter != 'None': # if file extension filter is set
                        self.FileExtensionFilterCopy = self.FileExtensionFilter # create a copy of it to filter new results
                    self.CurrentDirectoryList.append(folder) # append folder selected to self.CurrentDirectoryList
                    self.GetResultsHandler('Update') # get/write new results and change current directory on device
            else:
                self.Discard('Invalid Command for SetFolderAction')
        else:
            self.Discard('Invalid Command for SetFolderAction')
            
    def SetLoadSelectedItem(self, value, qualifier):
    
        if self.FileList and 1 <= int(value) <= 100:  # if file list is populated and value within range
            file = self.ReadStatus('FileSearchResults', {'Position': value})  # get file name from selected position
            if file and file not in ['*** End of List ***', '*** Timeout ***', '*** No Items to Show ***', 'xfer_complete']:  # if file exits and is not invalid
                fullFilePath = '{0}/{1}'.format('/'.join(self.CurrentDirectoryList), file)  # join current directory list with filename
                CmdString = 'wU1*file:///{0}PLYR\r'.format(fullFilePath)  # load file
                self.__SetHelper('LoadSelectedItem', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoadSelectedItem')
        else:
            self.Discard('Invalid Command for SetLoadSelectedItem')
            
    def SetFilterItemsByExtension(self, value, qualifier):

        if self.FileListUnfiltered and qualifier['File Extension'] in self.FileExtensionStates: # if unfiltered file list is populated and valid qualifier
            self.FileExtensionFilter = qualifier['File Extension']
            self.FileExtensionFilterCopy = 'None' # reset file extension filter copy
            self.FileMinLabel = 0 # reset min label value
            self.FileMaxLabel = self.NumberofFileSearch # reset max label value
            if self.FileExtensionFilter != 'None': # if file extension filter is set
                fileListFiltered = [] # define filtered file list
                for file in self.FileListUnfiltered:
                    if file.lower().endswith(self.FileExtensionFilter): # if file extension filter set is in filename
                        fileListFiltered.append(file) # add file to filtered list
                self.FileList = fileListFiltered # overwrite file list as filtered file list
            else: # if no file extension filter is set
                self.FileList = self.FileListUnfiltered # overwrite file list as unfiltered file list

            if value != 'GetResultsHandler': # self.FilePositionHandler() is already called in GetResultsHandler
                self.FilePositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetFilterItemsByExtension')

    def SetFolderUpOneDirectory(self, value, qualifier):

        if self.FileandFolderUpdateParams and self.CurrentDirectoryList: # check if SetFileandFolderUpdate was pressed and not in root directory
            self.Send('w..CJ\r') # send up one directory command to device
            if self.FileExtensionFilter != 'None': # if file extension filter is set
                self.FileExtensionFilterCopy = self.FileExtensionFilter # create a copy of it to filter new results
            self.SetFileandFolderUpdate('FolderUpOneDirectory', self.FileandFolderUpdateParams) # update new results
        else:
            self.Discard('Invalid Command for SetFolderUpOneDirectory')

    def UpdateHDCPInputStatus101(self, value, qualifier):

        HDCPInputStatus101CmdString = 'wI1HDCP\r' # protocol has typo, input number is required based on testing
        self.__UpdateHelper('HDCPInputStatus101', HDCPInputStatus101CmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        InputStates = {
            '1' : 'Decoder',
            '2' : 'HDMI'
        }

        ValueStateValues = {
            '0' : 'No Source Device Detected', 
            '1' : 'Source Detected with HDCP', 
            '2' : 'Source Detected without HDCP'
        }

        if self.Model == '101':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputStatus101', value, None)
        else:
            qualifier = {'Input': InputStates[match.group(1).decode()]}
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputStatus202', value, qualifier)

    def UpdateHDCPInputStatus202(self, value, qualifier):

        InputStates = {
            'Decoder' : '1',
            'HDMI'    : '2'
        }

        if qualifier['Input'] in InputStates:
            HDCPInputStatus202CmdString = 'wI{}HDCP\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('HDCPInputStatus202', HDCPInputStatus202CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus202')

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Sink Device Detected', 
            '1' : 'Sink Detected with HDCP', 
            '2' : 'Sink Detected without HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto'             : '00',
            '576p (50Hz)'      : '26',
            '640x480 (50Hz)'   : '10',
            '640x480 (60Hz)'   : '11',
            '800x600 (50Hz)'   : '12',
            '800x600 (60Hz)'   : '13',
            '1024x768 (50Hz)'  : '14',
            '1024x768 (60Hz)'  : '15',
            '1280x1024 (50Hz)' : '16',
            '1280x1024 (60Hz)' : '17',
            '1366x768 (50Hz)'  : '18',
            '1366x768 (60Hz)'  : '19',
            '1600x1200 (50Hz)' : '20',
            '1600x1200 (60Hz)' : '21',
            '1920x1200 (50Hz)' : '22',
            '1920x1200 (60Hz)' : '23',
            '480p (59.94Hz)'   : '24',
            '480p (60Hz)'      : '25',
            '720p (50Hz)'      : '32',
            '720p (60Hz)'      : '34',
            '1080i (50Hz)'     : '35',
            '1080i (59.94Hz)'  : '36',
            '1080i (60Hz)'     : '37',
            '1080p (23.98Hz)'  : '38',
            '1080p (24Hz)'     : '39',
            '1080p (25Hz)'     : '40',
            '1080p (29.97Hz)'  : '41',
            '1080p (30Hz)'     : '42',
            '1080p (50Hz)'     : '43',
            '1080p (59.94Hz)'  : '44',
            '1080p (60Hz)'     : '45',
            '720p (59.94Hz)'   : '33',
            '1280x800 (50Hz)'  : '27',
            '1280x800 (60Hz)'  : '28'
        }

        OutputResolutionCmdString = 'w{0}RATE\r'.format(ValueStateValues[value])
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'wRATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '00' : 'Auto',
            '26' : '576p (50Hz)',
            '10' : '640x480 (50Hz)',
            '11' : '640x480 (60Hz)',
            '12' : '800x600 (50Hz)',
            '13' : '800x600 (60Hz)',
            '14' : '1024x768 (50Hz)',
            '15' : '1024x768 (60Hz)',
            '16' : '1280x1024 (50Hz)',
            '17' : '1280x1024 (60Hz)',
            '18' : '1366x768 (50Hz)',
            '19' : '1366x768 (60Hz)',
            '20' : '1600x1200 (50Hz)',
            '21' : '1600x1200 (60Hz)',
            '22' : '1920x1200 (50Hz)',
            '23' : '1920x1200 (60Hz)',
            '24' : '480p (59.94Hz)',
            '25' : '480p (60Hz)',
            '32' : '720p (50Hz)',
            '34' : '720p (60Hz)',
            '35' : '1080i (50Hz)',
            '36' : '1080i (59.94Hz)',
            '37' : '1080i (60Hz)',
            '38' : '1080p (23.98Hz)',
            '39' : '1080p (24Hz)',
            '40' : '1080p (25Hz)',
            '41' : '1080p (29.97Hz)',
            '42' : '1080p (30Hz)',
            '43' : '1080p (50Hz)',
            '44' : '1080p (59.94Hz)',
            '45' : '1080p (60Hz)',
            '33' : '720p (59.94Hz)',
            '27' : '1280x800 (50Hz)',
            '28' : '1280x800 (60Hz)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetHistoryListUpdate(self, value, qualifier):

        for position in range(1, self.NumberofHistoryListSearch+1):
            string = '*** Loading... Please wait ***' if position == 1 else '' # write loading for position 1 and empty strings after
            self.WriteStatus('HistoryListSearchResults', string, {'Position': str(position)})

        CmdString = 'wGHIST\r'
        res = self.__SetHelperSync('HistoryListUpdate', CmdString, value, qualifier)
        if res:
            resIter = re.finditer(self.URIRegex, res)
            self.HistoryFileExtensionFilter = 'None' # reset file extension filter
            self.HistoryMinLabel = 0 # reset min label value
            self.HistoryMaxLabel = self.NumberofHistoryListSearch # reset max label value
            self.HistoryList.clear()

            for uri in resIter:
                self.HistoryList.append(uri.group('uri')) # append all uri's to list
            self.HistoryListUnfiltered = self.HistoryList # create copy of history list (used when file extension filter is set)

            self.HistoryListPositionHandler() # update search result positions
        else:
            self.WriteStatus('HistoryListSearchResults', '*** Timeout ***', {'Position': '1'}) # write no response for position 1 if no response

    def HistoryListPositionHandler(self):

        position = 1
        for index in range(self.HistoryMinLabel, self.HistoryMaxLabel):
            try:
                self.WriteStatus('HistoryListSearchResults', self.HistoryList[index], {'Position': str(position)}) # write as many results as possible until IndexError (last uri in history list)
                position += 1
            except IndexError:
                break

        if position <= self.NumberofHistoryListSearch: # if last result
            string = '*** End of List ***' if self.HistoryList else '*** No Items to Show ***'
            self.WriteStatus('HistoryListSearchResults', string, {'Position': str(position)}) # write end of list if list exists, else no items to show
            position += 1
            for index in range(position, self.NumberofHistoryListSearch+1):
                self.WriteStatus('HistoryListSearchResults', '', {'Position': str(position)}) # write empty strings after last result
                position += 1

    def SetHistoryListNavigation(self, value, qualifier):

        if self.HistoryList and value in ['Up', 'Down', 'Page Up', 'Page Down']: # if history list is populated and value selected
            NumberOfAdvance = self.NumberofHistoryListSearch if 'Page' in value else 1 # defines number to advance
            if 'Down' in value and self.HistoryMaxLabel <= len(self.HistoryList): # prevent from scrolling when end of list is reached
                self.HistoryMinLabel += NumberOfAdvance
                self.HistoryMaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.HistoryMinLabel -= NumberOfAdvance
                self.HistoryMaxLabel -= NumberOfAdvance

            if self.HistoryMinLabel < 0: # prevents from scrolling up above first result
                self.HistoryMinLabel = 0

            if self.HistoryMaxLabel < self.NumberofHistoryListSearch: # prevents from scrolling past more results that are configured
                self.HistoryMaxLabel = self.NumberofHistoryListSearch

            if self.HistoryMinLabel > len(self.HistoryList): # prevents from scrolling past more uri's that exist
                self.HistoryMinLabel = len(self.HistoryList)
                self.HistoryMaxLabel = self.HistoryMinLabel + self.NumberofHistoryListSearch

            self.HistoryListPositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetHistoryListNavigation')

    def SetFilterHistoryListByExtension(self, value, qualifier):

        if self.HistoryListUnfiltered and qualifier['File Extension'] in self.FileExtensionStates: # if unfiltered history list is populated and valid qualifier
            self.HistoryFileExtensionFilter = qualifier['File Extension']
            self.HistoryMinLabel = 0 # reset min label value
            self.HistoryMaxLabel = self.NumberofHistoryListSearch # reset max label value
            if self.HistoryFileExtensionFilter != 'None': # if file extension filter is set
                historyListFiltered = [] # define filtered history list
                for uri in self.HistoryListUnfiltered:
                    if uri.lower().endswith(self.HistoryFileExtensionFilter): # if file extension filter set is in uri
                        historyListFiltered.append(uri) # add uri to filtered list
                self.HistoryList = historyListFiltered # overwrite history list as filtered history list
            else: # if file extension filter is None
                self.HistoryList = self.HistoryListUnfiltered # overwrite history list as unfiltered history list
            self.HistoryListPositionHandler() # update search result positions
        else:
            self.Discard('Invalid Command for SetFilterHistoryListByExtension')

    def SetLoadSelectedHistoryItem(self, value, qualifier):

        if self.HistoryList and 1 <= int(value) <= 100: # if history list is populated and value is within range
            uri = self.ReadStatus('HistoryListSearchResults', {'Position': value}) # get uri from selected position
            if uri and uri in self.HistoryList: # check if uri exists and in history list
                CmdString = 'wU1*{0}PLYR\r'.format(uri) # load uri
                self.__SetHelper('LoadSelectedHistoryItem', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoadSelectedHistoryItem')
        else:
            self.Discard('Invalid Command for SetLoadSelectedHistoryItem')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Decoder' : '1',
            'HDMI'    : '2'
        }

        InputCmdString = '{0}!'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1' : 'Decoder',
            '2' : 'HDMI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLoadFileCommand(self, value, qualifier):

        path = value
        if path:
            LoadFileCommandCmdString = 'wU1*file:///{0}PLYR\r'.format(path)
            self.__SetHelper('LoadFileCommand', LoadFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadFileCommand')

    def SetLoadPlaylistCommand(self, value, qualifier):

        path = value
        if path:
            LoadPlaylistCommandCmdString = 'wL1*file:///{0}PLYR\r'.format(path)
            self.__SetHelper('LoadPlaylistCommand', LoadPlaylistCommandCmdString, value, qualifier)

    def SetLoadSourceCommand(self, value, qualifier):

        path = value
        if path:
            LoadSourceCommandCmdString = 'wU1*{0}PLYR\r'.format(path)
            self.__SetHelper('LoadSourceCommand', LoadSourceCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadSourceCommand')

    def SetLoopPlay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        LoopPlayCmdString = 'wR1*{0}PLYR\r'.format(ValueStateValues[value])
        self.__SetHelper('LoopPlay', LoopPlayCmdString, value, qualifier)

    def UpdateLoopPlay(self, value, qualifier):

        LoopPlayCmdString = 'wR1PLYR\r'
        self.__UpdateHelper('LoopPlay', LoopPlayCmdString, value, qualifier)

    def __MatchLoopPlay(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LoopPlay', value, None)

    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Play'     : 'wS1*1',
            'Pause'    : 'wE1',
            'Stop'     : 'wO1',
            'Next'     : 'wN1',
            'Previous' : 'wP1'
        }

        PlaybackCmdString = '{0}PLYR\r'.format(ValueStateValues[value])
        self.__SetHelper('Playback', PlaybackCmdString, value, qualifier)

    def UpdatePlayback(self, value, qualifier):

        PlaybackCmdString = 'wY1PLYR\r'
        self.__UpdateHelper('Playback', PlaybackCmdString, value, qualifier)

    def __MatchPlayback(self, match, tag):

        ValueStateValuesY = {
            '1' : 'Play',
            '2' : 'Pause',
            '0' : 'Stop'
        }

        ValueStateValuesS = {
            '1' : 'Play',
            '0' : 'Pause'
        }

        if match.group(1).decode() == 'Y':
            value = ValueStateValuesY[match.group(2).decode()]
            self.WriteStatus('Playback', value, None)
        elif match.group(1).decode() == 'O':
            value = 'Stop'
            self.WriteStatus('Playback', value, None)
        else:
            value = ValueStateValuesS[match.group(2).decode()]
            self.WriteStatus('Playback', value, None)

    def SetPowerMode(self, value, qualifier):

        ValueStateValues = {
            'Full Power'                : '0',
            'Low Power - Standby State' : '1'
        }

        PowerModeCmdString = 'w{0}PSAV\r'.format(ValueStateValues[value])
        self.__SetHelper('PowerMode', PowerModeCmdString, value, qualifier)

    def UpdatePowerMode(self, value, qualifier):

        PowerModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerMode', PowerModeCmdString, value, qualifier)

    def __MatchPowerMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Full Power',
            '1' : 'Low Power - Standby State'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerMode', value, None)

    def SetChannelPresetRecall(self, value, qualifier):

        if 1 <= value <= 999:
            ChannelPresetRecallCmdString = '{0}T'.format(value)
            self.__SetHelper('ChannelPresetRecall', ChannelPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelPresetRecall')

    def UpdateChannelPresetRecall(self, value, qualifier):

        ChannelPresetRecallCmdString = 'T'
        self.__UpdateHelper('ChannelPresetRecall', ChannelPresetRecallCmdString, value, qualifier)

    def __MatchChannelPresetRecall(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('ChannelPresetRecall', value, None)

    def SetChannelPresetRecallStep(self, value, qualifier):

        ValueStateValues = {
            'Next'    : '+',
            'Previous': '-'
        }

        ChannelPresetRecallStepCmdString = '{0}T'.format(ValueStateValues[value])
        self.__SetHelper('ChannelPresetRecallStep', ChannelPresetRecallStepCmdString, value, qualifier)

    def SetScreenSaver(self, value, qualifier):

        ValueStateValues = {
            'Custom color set via webpage' : '0',
            'Black Screen'                 : '1',
            'Blue Screen with OSD Text'    : '2'
        }

        ScreenSaverCmdString = 'wM{0}SSAV\r'.format(ValueStateValues[value])
        self.__SetHelper('ScreenSaver', ScreenSaverCmdString, value, qualifier)

    def UpdateScreenSaver(self, value, qualifier):

        ScreenSaverCmdString = 'wMSSAV\r'
        self.__UpdateHelper('ScreenSaver', ScreenSaverCmdString, value, qualifier)

    def __MatchScreenSaver(self, match, tag):

        ValueStateValues = {
            '0' : 'Custom color set via webpage',
            '1' : 'Black Screen',
            '2' : 'Blue Screen with OSD Text'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaver', value, None)

    def SetSeek(self, value, qualifier):
    
        if 1 <= qualifier['Step'] <= 65535 and value in ['Forward', 'Backward']:
            if value == 'Forward':
                step = qualifier['Step']
            elif value == 'Backward':
                step = -qualifier['Step']

            currentTimeCode = self.ReadStatus('CurrentTimecode', None)
            currentClipLength = self.ReadStatus('CurrentClipLength', None)

            if currentTimeCode and currentClipLength:
                currentTimeCode = currentTimeCode.split(':')
                currentTimeSeconds = int(currentTimeCode[0]) * 3600 + int(currentTimeCode[1]) * 60 + int(currentTimeCode[2])

                currentClipLength = currentClipLength.split(':')
                currentLengthSeconds = int(currentClipLength[0]) * 3600 + int(currentClipLength[1]) * 60 + int(currentClipLength[2])
                newTimeSeconds = currentTimeSeconds + step
                if newTimeSeconds > currentLengthSeconds:
                    newTimeSeconds = currentLengthSeconds
                elif newTimeSeconds < 0:
                    newTimeSeconds = 0
                hours = newTimeSeconds // 3600
                minutes = (newTimeSeconds % 3600) // 60
                seconds = (newTimeSeconds % 3600) % 60

                SeekCmdString = 'wK1*{0}:{1}:{2}PLYR\r'.format(hours, minutes, seconds)
                self.__SetHelper('Seek', SeekCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSeek')

    def SetStandbyTimer(self, value, qualifier):

        if 0 <= value <= 500:
            StandbyTimerCmdString = 'wT{0}SSAV\r'.format(value)
            self.__SetHelper('StandbyTimer', StandbyTimerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandbyTimer')
            
    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPatterns(self, value, qualifier):

        ValueStateValues = {
            'Off'                : '0',
            'Alternating Pixels' : '2',
            'Alternating Lines'  : '3',
            'Crosshatch'         : '4',
            'Color Bars'         : '6',
            '4x4 Crosshatch'     : '5',
            'Grayscale'          : '7',
            'Ramp'               : '8',
            'White Field'        : '9'
        }

        TestPatternsCmdString = 'w{0}TEST\r'.format(ValueStateValues[value])
        self.__SetHelper('TestPatterns', TestPatternsCmdString, value, qualifier)

    def UpdateTestPatterns(self, value, qualifier):

        TestPatternsCmdString = 'wTEST\r'
        self.__UpdateHelper('TestPatterns', TestPatternsCmdString, value, qualifier)

    def __MatchTestPatterns(self, match, tag):

        ValueStateValues = {
            '0' : 'Off',
            '2' : 'Alternating Pixels',
            '3' : 'Alternating Lines',
            '4' : 'Crosshatch',
            '6' : 'Color Bars',
            '5' : '4x4 Crosshatch',
            '7' : 'Grayscale',
            '8' : 'Ramp',
            '9' : 'White Field'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPatterns', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video Mute'          : '1B',
            'Sync and Video Mute' : '2B',
            'Unmute'              : '0B'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'Video Mute',
            '2' : 'Sync and Video Mute',
            '0' : 'Unmute'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if -100 <= value <= 0:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        sign = match.group(1).decode()
        value = int(match.group(2).decode()) if sign == '+' else -int(match.group(2).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled:
            self.Send('w0echo\r\n')
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                @Wait(1)
                def SendCommand():
                    self.Send(commandstring)
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                @Wait(1)
                def SendCommand():
                    self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __SetHelperSync(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled:
            self.Send('w0echo\r\n')
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                @Wait(1)
                def SendCommand():
                    res = self.SendAndWait(commandstring, 30, deliTag=b'Bytes Left\r\n' if command == 'FileandFolderUpdate' else b'\r\n')
                    if res:
                        return res.decode()
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                @Wait(1)
                def SendCommand():
                    res = self.SendAndWait(commandstring, 30, deliTag=b'Bytes Left\r\n' if command == 'FileandFolderUpdate' else b'\r\n')
                    if res:
                        return res.decode()
        else:
            res = self.SendAndWait(commandstring, 30, deliTag=b'Bytes Left\r\n' if command == 'FileandFolderUpdate' else b'\r\n')
            if res:
                return res.decode()

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.EchoDisabled:
                self.Send('w0echo\r\n')
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    @Wait(1)
                    def SendCommand():
                        self.Send(commandstring)
            elif self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    @Wait(1)
                    def SendCommand():
                        self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '10' : 'Unrecognized Command',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Command not available for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found',
            '30' : 'Hardware failure',
            '31' : 'Attempt to break port pass-through when it has not been set',
        }

        value = match.group(1).decode()
        errorCode = DEVICE_ERROR_CODES.get(value)
        if errorCode:
            self.Error([errorCode])
        else:
            self.Error(['Unrecognized error code: E'+ value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.FileExtensionFilter = 'None'
        
    def extr_42_1339_SMD_101(self):

        self.Model = '101'
    
        self.StreamModeStates = {
            '0' : 'Still Image',
            '1' : 'Audio Only',
            '2' : 'Video Only',
            '3' : 'Audio and Video'
        }

    def extr_42_1339_SMD_202(self):

        self.Model = '202'

        self.StreamModeStates = {
            '0' : 'Audio and Video',
            '1' : 'Video Only'
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None, None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
