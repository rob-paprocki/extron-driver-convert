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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BrowseFilter': {'Parameters': ['Type'], 'Status': {}},
            'BrowseList': {'Parameters': ['List Type', 'Position'], 'Status': {}},
            'BrowseListNavigation': {'Parameters': ['List Type', 'Step'], 'Status': {}},
            'BrowseListUpdate': {'Status': {}},
            'ClearNowPlayingQueue': {'Status': {}},
            'CurrentAlbum': {'Status': {}},
            'CurrentArtist': {'Status': {}},
            'CurrentInstanceStatus': {'Status': {}},
            'CurrentSongTitle': {'Status': {}},
            'CurrentTrack': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'MCSInstanceList': {'Parameters': ['Position'], 'Status': {}},
            'MCSInstanceListNavigation': {'Parameters': ['Step'], 'Status': {}},
            'MCSInstanceListUpdate': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PlayMedia': {'Parameters': ['Position', 'Queue'], 'Status': {}},
            'Repeat': {'Status': {}},
            'SetMCSInstance': {'Status': {}},
            'Shuffle': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeLevelStatus': {'Status': {}}
        }

        self.numQueries = 250
        self.AlbumQueryCounter = 0
        self.ArtistQueryCounter = 0
        self.SongQueryCounter = 0
        self.GenreQueryCounter = 0
        self.NowPlayingQueryCounter = 0
        self.PlaylistQueryCounter = 0
        self.RSourceQueryCounter = 0
        self.RStationQueryCounter = 0
        self.RGenreQueryCounter = 0

        self.AlbumsList = []
        self.AlbumsListReference = {}
        self.AlbumsListStartIndex = 0

        self.ArtistsList = []
        self.ArtistsListReference = {}
        self.ArtistsListStartIndex = 0

        self.GenresList = []
        self.GenresListReference = {}
        self.GenresListStartIndex = 0

        self.NowPlayingList = []
        self.NowPlayingListReference = {}
        self.NowPlayingListStartIndex = 0

        self.PlaylistsList = []
        self.PlaylistsListReference = {}
        self.PlaylistsListStartIndex = 0

        self.SongsList = []
        self.SongsListReference = {}
        self.SongsListStartIndex = 0

        self.RSourcesList = []
        self.RSourcesListReference = {}
        self.RSourcesListStartIndex = 0

        self.RStationsList = []
        self.RStationsListReference = {}
        self.RStationsListStartIndex = 0

        self.RGenresList = []
        self.RGenresListReference = {}
        self.RGenresListStartIndex = 0

        self.MCSInstanceList = []
        self.MCSInstanceListReference = {}
        self.MCSInstanceListStartIndex = 0
        self.lastMCSUpdate = 0

        self.FilterFlag = True        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'MusicFilter Ok\r\n'), self.__MatchMusicFilterUpdate, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (.*) (?:MediaControl|PlayState)=(Stop|Playing|Paused|Skip(?:Next|Prev)|(?:Next|Prev)Frame|SlowMotion[123]|Rewind[123]|FF[123])\r\n'), self.__MatchTransport, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) MetaData3=(.*)\r\n'), self.__MatchCurrentAlbum, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) MetaData2=(.*)\r\n'), self.__MatchCurrentArtist, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) InstanceName=(.*)\r\n'), self.__MatchCurrentInstanceStatus, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) MetaData4=(.*)\r\n'), self.__MatchCurrentSongTitle, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) MetaData1=(.*)\r\n'), self.__MatchCurrentTrack, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) TrackTime=(.*)\r\n'), self.__MatchCurrentTrackTime, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) Repeat=(.*)\r\n'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) Shuffle=(.*)\r\n'), self.__MatchShuffle, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) Volume=(.*)\r\n'), self.__MatchVolumeLevelStatus, None)
            self.AddMatchString(re.compile(b'(?:ReportState|StateChanged) (?:.*) Running=(True|False)\r\n'), self.__MatchInstanceFailure, None)
            self.AddMatchString(re.compile(b'GetStatus=Done\r\n'), self.__MatchTransport, 'StatusDone')
            self.AddMatchString(re.compile(b'(Error:.*).\r'), self.__MatchError, None)

        self.Browse_Regex = re.compile('(?:Album|Artist|Genre|Title|Playlist|RadioSource|RadioStation|RadioGenre) {.*} \"(.*?[^\\\\])\".*')
        self.validMCSInstance = re.compile('BeginInstances .*[\s\S]{1,2}([.\s\S]*)EndInstances NoMore')
        self.is_offline = re.compile('Error: You are currently offline.')

    def __MatchInstanceFailure(self, match, tag):
        if match.group(1).decode() == 'False':
            self.SetInstance()

    def SetInstance():
        self.Send('StartMCS\r\n')

    def SetBrowseFilter(self, value, qualifier):

        TypeStates = {
            'Artist': 'Artist',
            'Album': 'Album',
            'Genre': 'Genre',
            'Playlist': 'Playlist',
            'Song': 'Title',
            'Search': 'Search',
            'Disable Filter': 'Clear'
        }

        RadioTypes = {
            'Radio Source': 'Source',
            'Radio Genre': 'Genre',
            'Disable Radio Filter': 'RadioClear'
        }

        FilterString = value;

        if qualifier['Type'] in TypeStates:
            if qualifier['Type'] == 'Disable Filter' or FilterString == '':

                cmdString = 'SetMusicFilter Clear\r\n'
            else:
                cmdString = 'SetMusicFilter {0}=\"{1}\"\r\n'.format(TypeStates[qualifier['Type']], FilterString)
            self.__SetHelper('BrowseFilter', cmdString, value, qualifier)
        elif qualifier['Type'] in RadioTypes:
            if qualifier['Type'] == 'Disable Radio Filter' or FilterString == '':

                cmdString = 'SetRadioFilter Clear\r\n'
            else:
                cmdString = 'SetRadioFilter {0}=\"{1}\"\r\n'.format(RadioTypes[qualifier['Type']], FilterString)
            self.__SetHelper('BrowseFilter', cmdString, value, qualifier)
        else:
            print('Inappropriate Command for SetBrowseFilter')

    def __MatchMusicFilterUpdate(self, match, tag):

        self.AlbumsListStartIndex = 0
        self.ArtistsListStartIndex = 0
        self.GenresListStartIndex = 0
        self.NowPlayingListStartIndex = 0
        self.PlaylistsListStartIndex = 0
        self.SongsListStartIndex = 0
        self.RSourcesListStartIndex = 0
        self.RStationsListStartIndex = 0
        self.RGenresListStartIndex = 0
        self.mcsListStartIndex = 0

        self.AlbumQueryCounter = 0
        self.ArtistQueryCounter = 0
        self.SongQueryCounter = 0
        self.GenreQueryCounter = 0
        self.NowPlayingQueryCounter = 0
        self.PlaylistQueryCounter = 0
        self.RSourceQueryCounter = 0
        self.RStationQueryCounter = 0
        self.RGenreQueryCounter = 0

        self.FilterFlag = False

    def __ListPositionHandler(self, listType):
        StartIndexStates = {
            'Albums': self.AlbumsListStartIndex,
            'Artists': self.ArtistsListStartIndex,
            'Genres': self.GenresListStartIndex,
            'NowPlaying': self.NowPlayingListStartIndex,
            'Playlists': self.PlaylistsListStartIndex,
            'Songs': self.SongsListStartIndex,
            'RadioSources': self.RSourcesListStartIndex,
            'RadioStations': self.RStationsListStartIndex,
            'RadioGenres': self.RGenresListStartIndex
        }

        ListStates = {
            'Albums': self.AlbumsList,
            'Artists': self.ArtistsList,
            'Genres': self.GenresList,
            'NowPlaying': self.NowPlayingList,
            'Playlists': self.PlaylistsList,
            'Songs': self.SongsList,
            'RadioSources': self.RSourcesList,
            'RadioStations': self.RStationsList,
            'RadioGenres': self.RGenresList
        }

        listTypeStates = {
            'Albums': 'Albums',
            'Artists': 'Artists',
            'Genres': 'Genres',
            'NowPlaying': 'Now Playing',
            'Playlists': 'Playlists',
            'Songs': 'Songs',
            'RadioSources': 'Radio Sources',
            'RadioStations': 'Radio Stations',
            'RadioGenres': 'Radio Genres'
        }

        listType = listType.replace(' ', '')
        index = StartIndexStates[listType]

        index_end = index + 11
        position = 1
        while (index < len(ListStates[listType])):
            self.WriteStatus('BrowseList', ListStates[listType][index], {'List Type': listTypeStates[listType], 'Position': str(position)})
            position += 1
            index += 1
            if(position > index_end):
                break
        else:
            while (position <= 10):
                self.WriteStatus('BrowseList', '', {'List Type': listTypeStates[listType], 'Position': str(position)})
                position += 1

    def SetBrowseListNavigation(self, value, qualifier):

        StepStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        ListStates = {
            'Albums': self.AlbumsList,
            'Artists': self.ArtistsList,
            'Genres': self.GenresList,
            'NowPlaying': self.NowPlayingList,
            'Playlists': self.PlaylistsList,
            'Songs': self.SongsList,
            'RadioSources': self.RSourcesList,
            'RadioStations': self.RStationsList,
            'RadioGenres': self.RGenresList
        }

        StartIndexStates = {
            'Albums': self.AlbumsListStartIndex,
            'Artists': self.ArtistsListStartIndex,
            'Genres': self.GenresListStartIndex,
            'NowPlaying': self.NowPlayingListStartIndex,
            'Playlists': self.PlaylistsListStartIndex,
            'Songs': self.SongsListStartIndex,
            'RadioSources': self.RSourcesListStartIndex,
            'RadioStations': self.RStationsListStartIndex,
            'RadioGenres': self.RGenresListStartIndex
        }

        CounterStates = {
            'Albums': self.AlbumQueryCounter,
            'Artists': self.ArtistQueryCounter,
            'Songs': self.SongQueryCounter,
            'Genres': self.GenreQueryCounter,
            'NowPlaying': self.NowPlayingQueryCounter,
            'Playlists': self.PlaylistQueryCounter,
            'RadioSources': self.RSourceQueryCounter,
            'RadioStations': self.RStationQueryCounter,
            'RadioGenres': self.RGenreQueryCounter
        }

        ListTypeStates = {
            'Albums': 'Albums',
            'Artists': 'Artists',
            'Genres': 'Genres',
            'Now Playing': 'NowPlaying',
            'Playlists': 'Playlists',
            'Songs': 'Songs',
            'Radio Sources': 'RadioSources',
            'Radio Stations': 'RadioStations',
            'Radio Genres': 'RadioGenres'
        }

        if self.FilterFlag:
            step = int(StepStates[qualifier['Step']])
            L_Type = ListTypeStates[qualifier['List Type']]

            if ListStates[L_Type]:

                if value == 'Up':

                    if StartIndexStates[L_Type] - step >= 0:
                        if L_Type == 'Albums':
                            self.AlbumQueryCounter -= step
                            self.AlbumsListStartIndex -= step
                        elif L_Type == 'Artists':
                            self.ArtistQueryCounter -= step
                            self.ArtistsListStartIndex -= step
                        elif L_Type == 'Genres':
                            self.GenreQueryCounter -= step
                            self.GenresListStartIndex -= step
                        elif L_Type == 'NowPlaying':
                            self.NowPlayingQueryCounter -= step
                            self.NowPlayingListStartIndex -= step
                        elif L_Type == 'Playlists':
                            self.PlaylistQueryCounter -= step
                            self.PlaylistsListStartIndex -= step
                        elif L_Type == 'Songs':
                            self.SongQueryCounter -= step
                            self.SongsListStartIndex -= step
                        elif L_Type == 'RadioSources':
                            self.RSourceQueryCounter -= step
                            self.RSourcesListStartIndex -= step
                        elif L_Type == 'RadioStations':
                            self.RStationQueryCounter -= step
                            self.RStationsListStartIndex -= step
                        elif L_Type == 'RadioGenres':
                            self.RGenreQueryCounter -= step
                            self.RGenresListStartIndex -= step
                    else:
                        if CounterStates[L_Type] == 0:
                            pass
                        elif CounterStates[L_Type] > step:
                            if L_Type == 'Albums':
                                if self.AlbumQueryCounter > self.numQueries:
                                    self.AlbumQueryCounter = self.AlbumQueryCounter - self.numQueries
                                    self.AlbumsListStartIndex = self.numQueries
                                else:
                                    self.AlbumQueryCounter = 0
                                    self.AlbumsListStartIndex = self.numQueries
                            elif L_Type == 'Artists':
                                if self.ArtistQueryCounter > self.numQueries:
                                    self.ArtistQueryCounter = self.ArtistQueryCounter - self.numQueries
                                    self.ArtistsListStartIndex = self.numQueries
                                else:
                                    self.ArtistQueryCounter = 0
                                    self.ArtistsListStartIndex = self.numQueries
                            elif L_Type == 'Genres':
                                if self.GenreQueryCounter > self.numQueries:
                                    self.GenreQueryCounter = self.GenreQueryCounter - self.numQueries
                                    self.GenresListStartIndex = self.numQueries
                                else:
                                    self.GenreQueryCounter = 0
                                    self.GenresListStartIndex = self.numQueries
                            elif L_Type == 'NowPlaying':
                                if self.NowPlayingQueryCounter > self.numQueries:
                                    self.NowPlayingQueryCounter = self.NowPlayingQueryCounter - self.numQueries
                                    self.NowPlayingListStartIndex = self.numQueries
                                else:
                                    self.NowPlayingQueryCounter = 0
                                    self.NowPlayingListStartIndex = self.numQueries
                            elif L_Type == 'Playlists':
                                if self.PlaylistQueryCounter > self.numQueries:
                                    self.PlaylistQueryCounter = self.PlaylistQueryCounter - self.numQueries
                                    self.PlaylistsListStartIndex = self.numQueries
                                else:
                                    self.PlaylistQueryCounter = 0
                                    self.PlaylistsListStartIndex = self.numQueries
                            elif L_Type == 'Songs':
                                if self.SongQueryCounter > self.numQueries:
                                    self.SongQueryCounter = self.SongQueryCounter - self.numQueries
                                    self.SongsListStartIndex = self.numQueries
                                else:
                                    self.SongQueryCounter = 0
                                    self.SongsListStartIndex = self.numQueries
                            elif L_Type == 'RadioSources':
                                if self.RSourceQueryCounter > self.numQueries:
                                    self.RSourceQueryCounter = self.RSourceQueryCounter - self.numQueries
                                    self.RSourcesListStartIndex = self.numQueries
                                else:
                                    self.RSourceQueryCounter = 0
                                    self.RSourcesListStartIndex = self.numQueries
                            elif L_Type == 'RadioStations':
                                if self.RStationQueryCounter > self.numQueries:
                                    self.RStationQueryCounter = self.RStationQueryCounter - self.numQueries
                                    self.RStationsListStartIndex = self.numQueries
                                else:
                                    self.RStationQueryCounter = 0
                                    self.RStationsListStartIndex = self.numQueries
                            elif L_Type == 'RadioGenres':
                                if self.RGenreQueryCounter > self.numQueries:
                                    self.RGenreQueryCounter = self.RGenreQueryCounter - self.numQueries
                                    self.RGenresListStartIndex = self.numQueries
                                else:
                                    self.RGenreQueryCounter = 0
                                    self.RGenresListStartIndex = self.numQueries
                            self.SetBrowseListUpdate(qualifier['List Type'], 'NavigationUP')
                        else:
                            if L_Type == 'Albums':
                                self.AlbumQueryCounter = 0
                                self.AlbumsListStartIndex = 0
                            elif L_Type == 'Artists':
                                self.ArtistQueryCounter = 0
                                self.ArtistsListStartIndex = 0
                            elif L_Type == 'Genres':
                                self.GenreQueryCounter = 0
                                self.GenresListStartIndex = 0
                            elif L_Type == 'NowPlaying':
                                self.NowPlayingQueryCounter = 0
                                self.NowPlayingListStartIndex = 0
                            elif L_Type == 'Playlists':
                                self.PlaylistQueryCounter = 0
                                self.PlaylistsListStartIndex = 0
                            elif L_Type == 'Songs':
                                self.SongQueryCounter = 0
                                self.SongsListStartIndex = 0
                            elif L_Type == 'RadioSources':
                                self.RSourceQueryCounter = 0
                                self.RSourcesListStartIndex = 0
                            elif L_Type == 'RadioStations':
                                self.RStationQueryCounter = 0
                                self.RStationsListStartIndex = 0
                            elif L_Type == 'RadioGenres':
                                self.RGenreQueryCounter = 0
                                self.RGenresListStartIndex = 0

                if value == 'Down':

                    if StartIndexStates[L_Type] + step < len(ListStates[L_Type]) - 1:
                        if L_Type == 'Albums':
                            self.AlbumQueryCounter += step
                            self.AlbumsListStartIndex += step
                        elif L_Type == 'Artists':
                            self.ArtistQueryCounter += step
                            self.ArtistsListStartIndex += step
                        elif L_Type == 'Genres':
                            self.GenreQueryCounter += step
                            self.GenresListStartIndex += step
                        elif L_Type == 'NowPlaying':
                            self.NowPlayingQueryCounter += step
                            self.NowPlayingListStartIndex += step
                        elif L_Type == 'Playlists':
                            self.PlaylistQueryCounter += step
                            self.PlaylistsListStartIndex += step
                        elif L_Type == 'Songs':
                            self.SongQueryCounter += step
                            self.SongsListStartIndex += step
                        elif L_Type == 'RadioSources':
                            self.RSourceQueryCounter += step
                            self.RSourcesListStartIndex += step
                        elif L_Type == 'RadioStations':
                            self.RStationQueryCounter += step
                            self.RStationsListStartIndex += step
                        elif L_Type == 'RadioGenres':
                            self.RGenreQueryCounter += step
                            self.RGenresListStartIndex += step
                    else:
                        if L_Type == 'Albums':
                            temp = self.AlbumsListStartIndex
                            self.AlbumsListStartIndex = len(ListStates[L_Type]) - 1
                            self.AlbumQueryCounter += (self.AlbumsListStartIndex - temp)
                        elif L_Type == 'Artists':
                            temp = self.ArtistsListStartIndex
                            self.ArtistsListStartIndex = len(ListStates[L_Type]) - 1
                            self.ArtistQueryCounter += (self.ArtistsListStartIndex - temp)
                        elif L_Type == 'Genres':
                            temp = self.GenresListStartIndex
                            self.GenresListStartIndex = len(ListStates[L_Type]) - 1
                            self.GenreQueryCounter += (self.GenresListStartIndex - temp)
                        elif L_Type == 'NowPlaying':
                            temp = self.NowPlayingListStartIndex
                            self.NowPlayingListStartIndex = len(ListStates[L_Type]) - 1
                            self.NowPlayingQueryCounter += (self.NowPlayingListStartIndex - temp)
                        elif L_Type == 'Playlists':
                            temp = self.PlaylistsListStartIndex
                            self.PlaylistsListStartIndex = len(ListStates[L_Type]) - 1
                            self.PlaylistQueryCounter += (self.PlaylistsListStartIndex - temp)
                        elif L_Type == 'Songs':
                            temp = self.SongsListStartIndex
                            self.SongsListStartIndex = len(ListStates[L_Type]) - 1
                            self.SongQueryCounter += (self.SongsListStartIndex - temp)
                        elif L_Type == 'RadioSources':
                            temp = self.RSourcesListStartIndex
                            self.RSourcesListStartIndex = len(ListStates[L_Type]) - 1
                            self.RSourceQueryCounter += (self.RSourcesListStartIndex - temp)
                        elif L_Type == 'RadioStations':
                            temp = self.RStationsListStartIndex
                            self.RStationsListStartIndex = len(ListStates[L_Type]) - 1
                            self.RStationQueryCounter += (self.RStationsListStartIndex - temp)
                        elif L_Type == 'RadioGenres':
                            temp = self.RGenresListStartIndex
                            self.RGenresListStartIndex = len(ListStates[L_Type]) - 1
                            self.RGenreQueryCounter += (self.RGenresListStartIndex - temp)
                        self.SetBrowseListUpdate(qualifier['List Type'], 'Navigation')

                self.__ListPositionHandler(L_Type)
            else:
                print('Inappropriate Command for SetBrowseListNavigation')

    def SetBrowseListUpdate(self, value, qualifier):

        ListTypeNames = {
            'Albums': 'Albums',
            'Artists': 'Artists',
            'Genres': 'Genres',
            'NowPlaying': 'NowPlaying',
            'Playlists': 'Playlists',
            'Titles': 'Songs',
            'Songs': 'Songs',
            'RadioSources': 'RadioSources',
            'RadioStations': 'RadioStations',
            'RadioGenres': 'RadioGenres'
        }

        ListTypeStates = {
            'Albums': 'BrowseAlbums {0} 250\r\n',
            'Artists': 'BrowseArtists {0} 250\r\n',
            'Genres': 'BrowseGenres {0} 250\r\n',
            'Now Playing': 'BrowseNowPlaying {0} 250\r\n',
            'Playlists': 'BrowsePlaylists {0} 250\r\n',
            'Songs': 'BrowseTitles {0} 250\r\n',
            'Radio Sources': 'BrowseRadioSources {0} 250\r\n',
            'Radio Stations': 'BrowseRadioStations {0} 250\r\n',
            'Radio Genres': 'BrowseRadioGenres {0} 250\r\n'
        }

        ListStates = {
            'Albums': self.AlbumsList,
            'Artists': self.ArtistsList,
            'Genres': self.GenresList,
            'NowPlaying': self.NowPlayingList,
            'Playlists': self.PlaylistsList,
            'Songs': self.SongsList,
            'RadioSources': self.RSourcesList,
            'RadioStations': self.RStationsList,
            'RadioGenres': self.RGenresList
        }

        StartIndexStates = {
            'Albums': self.AlbumsListStartIndex,
            'Artists': self.ArtistsListStartIndex,
            'Genres': self.GenresListStartIndex,
            'Now Playing': self.NowPlayingListStartIndex,
            'Playlists': self.PlaylistsListStartIndex,
            'Songs': self.SongsListStartIndex,
            'Radio Sources': self.RSourcesListStartIndex,
            'Radio Stations': self.RStationsListStartIndex,
            'Radio Genres': self.RGenresListStartIndex
        }

        CounterStates = {
            'Albums': self.AlbumQueryCounter,
            'Artists': self.ArtistQueryCounter,
            'Songs': self.SongQueryCounter,
            'Genres': self.GenreQueryCounter,
            'NowPlaying': self.NowPlayingQueryCounter,
            'Playlists': self.PlaylistQueryCounter,
            'RadioSources': self.RSourceQueryCounter,
            'RadioStations': self.RStationQueryCounter,
            'RadioGenres': self.RGenreQueryCounter
        }

        
        res = ''
        if qualifier != 'Navigation' and qualifier != 'NavigationUP':
            BrowseListUpdateCmdString = ListTypeStates[value].format('1')
            if value.replace(' ', '') == 'Albums':
                self.AlbumQueryCounter = 0
                self.AlbumsListStartIndex = 0
            elif value.replace(' ', '') == 'Artists':
                self.ArtistQueryCounter = 0
                self.ArtistsListStartIndex = 0
            elif value.replace(' ', '') == 'Genres':
                self.GenreQueryCounter = 0
                self.GenresListStartIndex = 0
            elif value.replace(' ', '') == 'NowPlaying':
                self.NowPlayingQueryCounter = 0
                self.NowPlayingListStartIndex = 0
            elif value.replace(' ', '') == 'Playlists':
                self.PlaylistQueryCounter = 0
                self.PlaylistsListStartIndex = 0
            elif value.replace(' ', '') == 'Songs':
                self.SongQueryCounter = 0
                self.SongsListStartIndex = 0
            elif value.replace(' ', '') == 'RadioSources':
                self.RSourceQueryCounter = 0
                self.RSourcesListStartIndex = 0
            elif value.replace(' ', '') == 'RadioStations':
                self.RStationQueryCounter = 0
                self.RStationsListStartIndex = 0
            elif value.replace(' ', '') == 'RadioGenres':
                self.RGenreQueryCounter = 0
                self.RGenresListStartIndex = 0

            res = self.__SetHelper('BrowseListUpdate', BrowseListUpdateCmdString, value, None)

        elif CounterStates[value.replace(' ', '')] % self.numQueries == 0:
            if int(CounterStates[value.replace(' ', '')]) == 0:
                BrowseListUpdateCmdString = ListTypeStates[value].format(CounterStates[value.replace(' ', '')] + 1)
            else:
                BrowseListUpdateCmdString = ListTypeStates[value].format(CounterStates[value.replace(' ', '')])

            res = self.__SetHelper('BrowseListUpdate', BrowseListUpdateCmdString, value, None)
        if res:
            OfflineMatch = re.match(self.is_offline, res)
            if OfflineMatch:
                self.RSourcesListUpdated = True
                self.RSourcesList.clear()
                self.RSourcesList.append("***Currently Offline***")
                self.__ListPositionHandler('RadioSources')
            else:
                self.FilterFlag = True
                if qualifier == 'NavigationUP' and StartIndexStates[value.replace(' ', '')] != 0:
                    if value.replace(' ', '') == 'Albums':
                        self.AlbumQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'Artists':
                        self.ArtistQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'Genres':
                        self.GenreQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'NowPlaying':
                        self.NowPlayingQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'Playlists':
                        self.PlaylistQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'Songs':
                        self.SongQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'RadioSources':
                        self.RSourceQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'RadioStations':
                        self.RStationQueryCounter += self.numQueries
                    elif value.replace(' ', '') == 'RadioGenres':
                        self.RGenreQueryCounter += self.numQueries
                elif qualifier == 'Navigation':
                    if value.replace(' ', '') == 'Albums':
                        self.AlbumsListStartIndex = 0
                    elif value.replace(' ', '') == 'Artists':
                        self.ArtistsListStartIndex = 0
                    elif value.replace(' ', '') == 'Genres':
                        self.GenresListStartIndex = 0
                    elif value.replace(' ', '') == 'NowPlaying':
                        self.NowPlayingListStartIndex = 0
                    elif value.replace(' ', '') == 'Playlists':
                        self.PlaylistsListStartIndex = 0
                    elif value.replace(' ', '') == 'Songs':
                        self.SongsListStartIndex = 0
                    elif value.replace(' ', '') == 'RadioSources':
                        self.RSourcesListStartIndex = 0
                    elif value.replace(' ', '') == 'RadioStations':
                        self.RStationsListStartIndex = 0
                    elif value.replace(' ', '') == 'RadioGenres':
                        self.RGenresListStartIndex = 0
                qualifier = None
                if res[5:10] == 'Album':
                    L_Type = "Albums"
                elif res[5:10] == 'Artis':
                    L_Type = "Artists"
                elif res[5:10] == 'Genre':
                    L_Type = "Genres"
                elif res[5:10] == 'NowPl':
                    L_Type = "NowPlaying"
                elif res[5:10] == 'Playl':
                    L_Type = "Playlists"
                elif res[5:10] == 'Title':
                    L_Type = "Songs"
                elif res[5:10] == 'Radio':
                    if res[10:12] == 'So':
                        L_Type = "RadioSources"
                    elif res[10:12] == 'St':
                        L_Type = "RadioStations"
                    elif res[10:12] == 'Ge':
                        L_Type = "RadioGenres"
                else:
                    L_Type = ''

                if L_Type:
                    ListStates[L_Type].clear()

                    ListIter = re.finditer(self.Browse_Regex, res)
                    if ListIter:
                        for name in ListIter:
                            if name:
                                ListStates[L_Type].append(name.group(1).replace('\\', '').strip('"'))

                    ListStates[L_Type].append("***End of List***")
                    self.__ListPositionHandler(ListTypeNames[L_Type])
        else:
            if ListStates[value.replace(' ', '')] == []:
                ListStates[value.replace(' ', '')].append("***End of List***")

    def SetPlayMedia(self, value, qualifier):

        ListStates = {
            'Album': self.AlbumsList,
            'Artist': self.ArtistsList,
            'Genre': self.GenresList,
            'Playlist': self.PlaylistsList,
            'Song': self.SongsList,
            'Radio Station': self.RStationsList,
        }

        StartIndexStates = {
            'Album': self.AlbumsListStartIndex,
            'Artist': self.ArtistsListStartIndex,
            'Genre': self.GenresListStartIndex,
            'Playlist': self.PlaylistsListStartIndex,
            'Song': self.SongsListStartIndex,
            'Radio Station': self.RStationsListStartIndex,
        }

        PositionStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        QueueStates = {
            'True': 'true',
            'False': 'false'
        }

        ValueStateValues = {
            'Album': 'PlayAlbum \"{0}\" {1}\r\n',
            'Artist': 'PlayArtist \"{0}\" {1}\r\n',
            'Genre': 'PlayGenre \"{0}\" {1}\r\n',
            'Playlist': 'PlayPlaylist \"{0}\" {1}\r\n',
            'Song': 'PlayTitle \"{0}\" {1}\r\n',
            'Radio Station': 'PlayRadioStation \"{0}\" {1}\r\n'
        }

        if len(ListStates[value]) > 1:
            PlayMediaCmdString = ValueStateValues[value].format(ListStates[value][int(PositionStates[qualifier['Position']]) - 1 + int(StartIndexStates[value])], QueueStates[qualifier['Queue']])
            self.__SetHelper('PlayMedia', PlayMediaCmdString, value, qualifier)

        self.UpdateTransport(None, None)

    def __MCSInstanceListPositionHandler(self):

        index = self.MCSInstanceListStartIndex

        position = 1
        while (index < len(self.MCSInstanceList)):
            self.WriteStatus('MCSInstanceList', self.MCSInstanceList[index], {'Position': str(position)})
            position += 1
            index += 1
        else:

            while (position <= 10):
                self.WriteStatus('MCSInstanceList', '', {'Position': str(position)})
                position += 1

    def SetMCSInstanceListNavigation(self, value, qualifier):

        StepStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }
        step = int(StepStates[qualifier['Step']])
        if self.MCSInstanceList:

            if value == 'Up':

                if self.MCSInstanceListStartIndex - step >= 0:
                    self.MCSInstanceListStartIndex -= step
                else:
                    self.MCSInstanceListStartIndex = 0

            if value == 'Down':

                if self.MCSInstanceListStartIndex + step <= len(self.MCSInstanceList) - 1:
                    self.MCSInstanceListStartIndex += step
                else:
                    self.MCSInstanceListStartIndex = len(self.MCSInstanceList) - 1

            self.__MCSInstanceListPositionHandler()
        else:
            print('Inappropriate Command for SetMCSInstanceListNavigation')

    def SetMCSInstanceListUpdate(self, value, qualifier):       
        if self.MCSInstanceList == []:
            self.MCSInstanceList.append('***End of List***')
        MCSInstanceListUpdateCmdString = 'BrowseInstances\r\n'
        res = self.__SetHelper('MCSInstanceListUpdate', MCSInstanceListUpdateCmdString, value, qualifier)
        if res:
            self.MCSInstanceList.clear()
            self.MCSInstanceListStartIndex = 0

            mcsList = re.search(self.validMCSInstance, res)
            if mcsList:
                for name in mcsList.group(1).split('\r\n'):
                    if name:
                        self.MCSInstanceList.append(name)
            self.MCSInstanceList.append('***End of List***')
            self.__MCSInstanceListPositionHandler()
       

    def SetSetMCSInstance(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        if len(self.MCSInstanceList) > 1:
            SetMCSInstanceCmdString = 'SetInstance {0}\r\n'.format(self.MCSInstanceList[(int(ValueStateValues[value]) - 1) + self.MCSInstanceListStartIndex])
            self.__SetHelper('SetMCSInstance', SetMCSInstanceCmdString, value, qualifier)

        self.UpdateTransport(None, None)

    def SetClearNowPlayingQueue(self, value, qualifier):

        ClearNowPlayingQueueCmdString = 'ClearNowPlaying\r\n'
        self.__SetHelper('ClearNowPlayingQueue', ClearNowPlayingQueueCmdString, value, qualifier)

    def UpdateCurrentAlbum(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentAlbum(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentAlbum', value, None)

    def UpdateCurrentArtist(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentArtist(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentArtist', value, None)

    def UpdateCurrentInstanceStatus(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentInstanceStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentInstanceStatus', value, None)

    def UpdateCurrentSongTitle(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentSongTitle(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentSongTitle', value, None)

    def UpdateCurrentTrack(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentTrack(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentTrack', value, None)

    def UpdateCurrentTrackTime(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchCurrentTrackTime(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CurrentTrackTime', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': 'SendKeys Home\r\n',
            'Up': 'SendKeys Up\r\n',
            'Down': 'SendKeys Down\r\n',
            'Left': 'SendKeys Left\r\n',
            'Right': 'SendKeys Right\r\n',
            'Select': 'SendKeys Select\r\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        RepeatCmdString = 'Repeat {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            'True': 'On',
            'False': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        ShuffleCmdString = 'Shuffle {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Shuffle', ShuffleCmdString, value, qualifier)

    def UpdateShuffle(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchShuffle(self, match, tag):

        ValueStateValues = {
            'True': 'On',
            'False': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shuffle', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'Play\r\n',
            'Pause': 'Pause\r\n',
            'Stop': 'Stop\r\n',
            'Fast Forward': 'FastForward\r\n',
            'Rewind': 'Rewind\r\n',
            'Next': 'SkipNext\r\n',
            'Previous': 'SkipPrevious\r\n',
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        TransportCmdString = 'GetStatus\r\n'
        self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)        

    def __MatchTransport(self, match, tag):

        ValueStateValues = {
            'Playing': 'Play',
            'Paused': 'Pause',
            'Stop': 'Stop',
            'FF1': 'Fast Forward',
            'FF2': 'Fast Forward',
            'FF3': 'Fast Forward',
            'Rewind1': 'Rewind',
            'Rewind2': 'Rewind',
            'Rewind3': 'Rewind',
            'SkipNext': 'Next',
            'SkipPrev': 'Previous'
        }
        if tag == 'StatusDone':
            self.WriteStatus('Transport', 'Stop', None)
        else:
            instance_var = match.group(1).decode()

            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Transport', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'VolumeUp\r\n',
            'Down': 'VolumeDown\r\n'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeLevelStatus(self, value, qualifier):

        self.UpdateTransport(value, qualifier)

    def __MatchVolumeLevelStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VolumeLevelStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if command == 'BrowseListUpdate' or command == 'MCSInstanceListUpdate':
            res = self.SendAndWait(commandstring, 5, deliTag=b'More\r\n')
            if not res:
                if value == 'Radio Sources':
                    res = self.SendAndWait(commandstring, 5, deliTag=b'again.\r\n')
                else:
                    print('Invalid/unexpected response for', command)
            return res.decode()
        else:
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

    def __MatchError(self, match, tag):

        value = match.group(1).decode()
        print('value for', command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Send('SubscribeEvents True\r\n')

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
