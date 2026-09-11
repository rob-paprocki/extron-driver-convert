from extronlib.standard.exml.etree import ElementTree as ET
import urllib.error
import urllib.request
import base64
import re

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberofQueueResult = 5
        self._NumberofRadioStationsResult = 5
        self._NumberofPlaylistsResult = 5
        self._NumberofAvailableZonesResult = 5
        self.IPAddress = ipAddress
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddToQueue': {'Parameters':['URI'], 'Status': {}},
            'ClearQueue': { 'Status': {}},
            'AvailableZonesNavigation': { 'Status': {}},
            'AvailableZonesResult': {'Parameters':['Button','Details Type'], 'Status': {}},
            'AvailableZonesSearch': { 'Status': {}},
            'CurrentTrackStatus': {'Parameters':['Details Type'], 'Status': {}},
            'Join': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PartyMode': { 'Status': {}},
            'AddPlaylistToQueue': { 'Status': {}},
            'PlaylistNavigation': { 'Status': {}},
            'PlaylistResult': {'Parameters':['Button','Details Type'], 'Status': {}},
            'PlaylistSearch': { 'Status': {}},
            'PlayMode': { 'Status': {}},
            'PointtoQueue': { 'Status': {}},
            'PointtoQueueIndex': { 'Status': {}},
            'QueueNavigation': { 'Status': {}},
            'QueueResult': {'Parameters':['Button','Details Type'], 'Status': {}},
            'QueueSearch': { 'Status': {}},
            'RemoveFromQueue': { 'Status': {}},
            'AddRadioStationToQueue': { 'Status': {}},
            'RadioStationsNavigation': { 'Status': {}},
            'RadioStationsResult': {'Parameters':['Button','Details Type'], 'Status': {}},
            'RadioStationsSearch': { 'Status': {}},
            'SetURI': {'Parameters':['URI'], 'Status': {}},
            'SpeakerInformation': {'Parameters':['Details'], 'Status': {}},
            'SwitchtoLineIn': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Unjoin': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.NumberofAvailableZones = 0
        self.NumberofPlaylist = 0
        self.PlaylistNameDir = Directory(self.NumberofPlaylistsResult, 'PlaylistResult', 'Name', filler='')
        self.PlaylistURIDir = Directory(self.NumberofPlaylistsResult, 'PlaylistResult', 'URI', filler='')
        self.PlaylistNameDir.write_status_function = self.WriteStatus
        self.PlaylistURIDir.write_status_function = self.WriteStatus
        self.QueueIndexDir = Directory(self._NumberofQueueResult, 'QueueResult', 'Index', filler='')
        self.QueueTitleDir = Directory(self._NumberofQueueResult, 'QueueResult', 'Title', filler='')
        self.QueueIndexDir.write_status_function = self.WriteStatus
        self.QueueTitleDir.write_status_function = self.WriteStatus
        self.RadioStationNameDir = Directory(self._NumberofRadioStationsResult, 'RadioStationsResult', 'Name', filler='')
        self.RadioStationURIDir = Directory(self._NumberofRadioStationsResult, 'RadioStationsResult', 'URI', filler='')
        self.RadioStationNameDir.write_status_function = self.WriteStatus
        self.RadioStationURIDir.write_status_function = self.WriteStatus
        self.IPAddressList = []
        self.ZoneNameDir = Directory(self._NumberofAvailableZonesResult, 'AvailableZonesResult', 'Zone Name', filler='')
        self.ZoneIPAddressDir = Directory(self._NumberofAvailableZonesResult, 'AvailableZonesResult', 'Zone IP Address', filler='')
        self.ZoneNameDir.write_status_function = self.WriteStatus
        self.ZoneIPAddressDir.write_status_function = self.WriteStatus

    @property
    def NumberofQueueResult(self):
        return self._NumberofQueueResult

    @NumberofQueueResult.setter
    def NumberofQueueResult(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofQueueResult = int(value)

    @property
    def NumberofRadioStationsResult(self):
        return self._NumberofRadioStationsResult

    @NumberofRadioStationsResult.setter
    def NumberofRadioStationsResult(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofRadioStationsResult = int(value)

    @property
    def NumberofPlaylistsResult(self):
        return self._NumberofPlaylistsResult

    @NumberofPlaylistsResult.setter
    def NumberofPlaylistsResult(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofPlaylistsResult = int(value)

    @property
    def NumberofAvailableZonesResult(self):
        return self._NumberofAvailableZonesResult

    @NumberofAvailableZonesResult.setter
    def NumberofAvailableZonesResult(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofAvailableZonesResult = int(value)

    def SetAddToQueue(self, value, qualifier):

        uri = qualifier['URI']
        if uri:
            AddToQueueCmdString = '/MediaRenderer/AVTransport/Control'
            action = 'urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
                    <s:Body><u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><EnqueuedURI>{}</EnqueuedURI><EnqueuedURIMetaData>\
                    </EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>0</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>1</EnqueueAsNext></u:AddURIToQueue></s:Body></s:Envelope>'.format(uri)
            self.__SetHelper('AddToQueue', value, qualifier, AddToQueueCmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetAddToQueue')

    def SetClearQueue(self, value, qualifier):

        ClearQueueCmdString = '/MediaRenderer/AVTransport/Control'
        action = 'urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue></s:Body></s:Envelope>'
        self.__SetHelper('ClearQueue', value, qualifier, ClearQueueCmdString, action, data.encode())

    def SetAvailableZonesNavigation(self, value, qualifier):
        self.Debug = True
        if value == 'Up':
            self.ZoneNameDir.scroll_up(1)
            self.ZoneIPAddressDir.scroll_up(1)
        elif value == 'Down':
            self.ZoneNameDir.scroll_down(1)
            self.ZoneIPAddressDir.scroll_down(1)
        elif value == 'Page Up':
            self.ZoneNameDir.scroll_up(self._NumberofAvailableZonesResult)
            self.ZoneIPAddressDir.scroll_up(self._NumberofAvailableZonesResult)
        elif value == 'Page Down':
            self.ZoneNameDir.scroll_down(self._NumberofAvailableZonesResult)
            self.ZoneIPAddressDir.scroll_down(self._NumberofAvailableZonesResult)
            
    def SetAvailableZonesSearch(self, value, qualifier):

        AvailableZonesSearchCmdString = '/support/review'
        headers = {'Content-Type': 'text/xml'}
        res =  self.__UpdateHelper('AvailableZonesSearch', value, qualifier, AvailableZonesSearchCmdString, headers)
        if res:
            try:
                AvailableZoneNameList = []
                AvailableZoneIPAddressList = []
                Temp = ET.fromstring(res)
                self.NumberofAvailableZones = len(Temp.findall('.//ZPInfo'))                
                for i in Temp.findall('.//ZPInfo'):
                        AvailableZoneNameList.append(i.findtext('.//ZoneName'))
                        AvailableZoneIPAddressList.append(i.findtext('.//IPAddress'))
                self.IPAddressList = AvailableZoneIPAddressList
                new_queue_data1 = ['{0}'.format(entry[0]) for entry in zip(AvailableZoneNameList)]
                new_queue_data1.append('**End of List**')
                new_queue_data2 = ['{0}'.format(entry[0]) for entry in zip(AvailableZoneIPAddressList)]
                new_queue_data2.append('**End of List**')
                self.ZoneNameDir.reset(new_queue_data1)
                self.ZoneIPAddressDir.reset(new_queue_data2)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Available Zones Search: Invalid/unexpected response'])
                            
    def UpdateCurrentTrackStatus(self, value, qualifier):

        CurrentTrackStatusCmdString = '/MediaRenderer/AVTransport/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:AVTransport:1#GetPositionInfo'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:GetPositionInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetPositionInfo></s:Body></s:Envelope>'
        res = self.__UpdateHelper('CurrentTrackStatus', value, qualifier, CurrentTrackStatusCmdString, headers, data.encode())
        if res:
            try: 
                Temp = ET.fromstring(res)
                PlaylistPos = Temp.findtext('.//Track')
                self.WriteStatus('CurrentTrackStatus', PlaylistPos, {'Details Type':'Queue Index'})
                Duration = Temp.findtext('.//TrackDuration')
                self.WriteStatus('CurrentTrackStatus', Duration, {'Details Type':'Duration'})
                URI = Temp.findtext('.//TrackURI')
                self.WriteStatus('CurrentTrackStatus', URI, {'Details Type':'URI'})
                Elaspedtime = Temp.findtext('.//RelTime')
                self.WriteStatus('CurrentTrackStatus', Elaspedtime, {'Details Type':'Current Elapsed Time'})

                Title = ''
                Artist =''
                d = Temp.findtext('.//TrackMetaData')
                if d != '' and Duration == '0:00:00':
                    metadata = ET.fromstring(d)
                    trackinfo = metadata.findtext('.//{urn:schemas-rinconnetworks-com:metadata-1-0/}streamContent')
                    index = trackinfo.find(' - ')
                    if index > -1:
                        Artist = trackinfo[:index]
                        Title = trackinfo[index+3:]
                    else:
                        Title = trackinfo
                elif d != '' and d != 'NOT_IMPLEMENTED':
                    metadata  = ET.fromstring(d)
                    md_title  = metadata.findtext('.//{http://purl.org/dc/elements/1.1/}title')
                    md_artist = metadata.findtext('.//{http://purl.org/dc/elements/1.1/}creator')                 
                    if (md_title):
                        Title = md_title       
                    if (md_artist):
                        Artist = md_artist

                if Title:
                    self.WriteStatus('CurrentTrackStatus', Title, {'Details Type':'Title'})
                if Artist:
                    self.WriteStatus('CurrentTrackStatus', Artist, {'Details Type':'Artist'})
            except (ValueError, IndexError):
                self.Error(['Current Track Status: Invalid/unexpected response'])

    def SetJoin(self, value, qualifier):

        masterUID = self.ReadStatus('SpeakerInformation', {'Details':'UID'})
        ZoneIPAdress = qualifier['IP Address']
        if masterUID and ZoneIPAdress:
            JoinCmdString = 'http://{}:1400/MediaRenderer/AVTransport/Control'.format(ZoneIPAdress)
            action = 'urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
            <s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:{}</CurrentURI>\
            <CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'.format(masterUID)
            self.__SetHelper('Join', value, qualifier, JoinCmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetJoin')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        MuteCmdString = '/MediaRenderer/RenderingControl/Control'
        action = 'urn:schemas-upnp-org:service:RenderingControl:1#SetMute'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel>\
        <DesiredMute>{}</DesiredMute></u:SetMute></s:Body></s:Envelope>'.format(ValueStateValues[value])
        self.__SetHelper('Mute', value, qualifier, MuteCmdString, action, data.encode())         

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        MuteCmdString = '/MediaRenderer/RenderingControl/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:RenderingControl:1#GetMute'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:GetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetMute></s:Body></s:Envelope>'
        res = self.__UpdateHelper('Mute', value, qualifier, MuteCmdString, headers, data.encode())
        if res:
            try:
                Temp = ET.fromstring(res)
                value = ValueStateValues[Temp.findtext('.//CurrentMute')]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPartyMode(self, value, qualifier):

        masterUID = self.ReadStatus('SpeakerInformation', {'Details':'UID'})
        if masterUID and self.IPAddressList:
            for i in range(1, len(self.IPAddressList)):
                self.SetJoinHandler(value, qualifier, self.IPAddressList[i], masterUID)
        else:
            self.Discard('Invalid Command for SetPartyMode')
                
    def SetJoinHandler(self, value, qualifier, IPAddress, masterUID):
        url = 'http://{}:1400/MediaRenderer/AVTransport/Control'.format(IPAddress)
        action = 'urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:{}</CurrentURI>\
        <CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'.format(masterUID)
        self.__SetHelper('Join', value, qualifier, url, action, data.encode())

    def SetPlaylistNavigation(self, value, qualifier):

        if value == 'Up':
            self.PlaylistNameDir.scroll_up(1)
            self.PlaylistURIDir.scroll_up(1)
        elif value == 'Down':
            self.PlaylistNameDir.scroll_down(1)
            self.PlaylistURIDir.scroll_down(1)
        elif value == 'Page Up':
            self.PlaylistNameDir.scroll_up(self.NumberofPlaylistsResult)
            self.PlaylistURIDir.scroll_up(self.NumberofPlaylistsResult)
        elif value == 'Page Down':
            self.PlaylistNameDir.scroll_down(self.NumberofPlaylistsResult)
            self.PlaylistURIDir.scroll_down(self.NumberofPlaylistsResult)

    def SetPlaylistSearch(self, value, qualifier):

        PlaylistSearchCmdString = '/MediaServer/ContentDirectory/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:ContentDirectory:1#Browse'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>\
        <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>SQ:</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag>\
        <Filter>*</Filter><StartingIndex>0</StartingIndex><RequestedCount>100</RequestedCount><SortCriteria></SortCriteria></u:Browse></s:Body></s:Envelope>'
        res = self.__UpdateHelper('PlaylistSearch', value, qualifier, PlaylistSearchCmdString, headers, data.encode())
        if res:
            try:
                PlaylistNameList = []
                PlaylistURIList = []
                Temp = ET.fromstring(res)
                self.NumberofPlaylist = int(Temp.findtext('.//NumberReturned'))                
                d = Temp.findtext('.//Result')
                if d != '':
                    metadata = ET.fromstring(d)
                    for item in metadata.findall('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}container'):
                        PlaylistNameList.append(item.findtext('.//{http://purl.org/dc/elements/1.1/}title'))
                        PlaylistURIList.append(item.findtext('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}res'))
                new_queue_data1 = ['{0}'.format(entry[0]) for entry in zip(PlaylistNameList)]
                new_queue_data1.append('**End of List**')
                new_queue_data2 = ['{0}'.format(entry[0]) for entry in zip(PlaylistURIList)]
                new_queue_data2.append('**End of List**')
                self.PlaylistNameDir.reset(new_queue_data1)
                self.PlaylistURIDir.reset(new_queue_data2)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Playlist Search: Invalid/unexpected response'])

    def SetAddPlaylistToQueue(self, value, qualifier):

        PlaylistURI = qualifier['Playlist URI']
        if PlaylistURI:
            self.SetAddToQueue(value, {'URI' : PlaylistURI})

    def SetPlayMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'             : 'NORMAL', 
            'Shuffle Non Repeat' : 'SHUFFLE_NOREPEAT', 
            'Shuffle'            : 'SHUFFLE', 
            'Repeat All'         : 'REPEAT_ALL'
        }

        PlayModeCmdString = '/MediaRenderer/AVTransport/Control'
        action = 'urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID>\
        <NewPlayMode>{}</NewPlayMode></u:SetPlayMode></s:Body></s:Envelope>'.format(ValueStateValues[value])
        self.__SetHelper('PlayMode', value, qualifier, PlayModeCmdString, action, data.encode())

    def SetPointtoQueue(self, value, qualifier):

        UID = self.ReadStatus('SpeakerInformation', {'Details':'UID'})
        uri = 'x-rincon-queue:{}#0'.format(UID)
        self.SetSetURI(value, {'URI':uri})

    def SetPointtoQueueIndex(self, value, qualifier):

        Index = qualifier['Index']
        if Index:
            PointtoQueueIndexCmdString = '/MediaRenderer/AVTransport/Control'
            action = 'urn:schemas-upnp-org:service:AVTransport:1#Seek'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
            <s:Body><u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>{}</Target>\
            </u:Seek></s:Body></s:Envelope>'.format(Index)
            self.__SetHelper('PointtoQueueIndex', value, qualifier, PointtoQueueIndexCmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetPointtoQueueIndex')

    def SetQueueNavigation(self, value, qualifier):

        if value == 'Up':
            self.QueueIndexDir.scroll_up(1)
            self.QueueTitleDir.scroll_up(1)
        elif value == 'Down':
            self.QueueIndexDir.scroll_down(1)
            self.QueueTitleDir.scroll_down(1)
        elif value == 'Page Up':
            self.QueueIndexDir.scroll_up(self._NumberofQueueResult)
            self.QueueTitleDir.scroll_up(self._NumberofQueueResult)
        elif value == 'Page Down':
            self.QueueIndexDir.scroll_down(self._NumberofQueueResult)
            self.QueueTitleDir.scroll_down(self._NumberofQueueResult)

    def SetQueueSearch(self, value, qualifier):

        QueueSearchCmdString = '/MediaServer/ContentDirectory/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:ContentDirectory:1#Browse'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Browse \
        xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>Q:0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>dc:title,res,dc:creator,\
        upnp:artist,upnp:album,upnp:albumArtURI</Filter><StartingIndex>0</StartingIndex><RequestedCount>500</RequestedCount><SortCriteria></SortCriteria></u:Browse></s:Body></s:Envelope>'
        res = self.__UpdateHelper('QueueSearch', value, qualifier, QueueSearchCmdString, headers, data.encode())
        if res:
            try:
                ItemTitleList = []
                ItemIndexList = []
                Temp = ET.fromstring(res)             
                d = Temp.findtext('.//Result')    
                if d != '':
                    metadata = ET.fromstring(d)
                    index = 0
                    for item in metadata.findall('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item'):
                        index = index+1
                        ItemTitleList.append(item.findtext('.//{http://purl.org/dc/elements/1.1/}title'))
                        ItemIndexList.append(str(index))
                new_queue_data1 = ['{0}'.format(entry[0]) for entry in zip(ItemIndexList)]
                new_queue_data1.append('**End of List**')
                new_queue_data2 = ['{0}'.format(entry[0]) for entry in zip(ItemTitleList)]
                new_queue_data2.append('**End of List**')
                self.QueueIndexDir.reset(new_queue_data1)
                self.QueueTitleDir.reset(new_queue_data2)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Queue Search: Invalid/unexpected response'])

    def SetRemoveFromQueue(self, value, qualifier):

        index = qualifier['Index']
        if index:
            RemoveFromQueueCmdString = '/MediaRenderer/AVTransport/Control'
            action = 'urn:schemas-upnp-org:service:AVTransport:1#RemoveTrackFromQueue'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
            <s:Body><u:RemoveTrackFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><ObjectID>Q:0/{}</ObjectID>\
            <UpdateID>0</UpdateID></u:RemoveTrackFromQueue></s:Body></s:Envelope>'.format(index)
            self.__SetHelper('RemoveFromQueue', value, qualifier, RemoveFromQueueCmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetRemoveFromQueue')

    def SetAddRadioStationToQueue(self, value, qualifier):

        RadioStationURI = qualifier['Radio Station URI']
        if RadioStationURI:
            RadioStationURI = RadioStationURI.replace('&',';')
            self.SetAddToQueue(value, {'URI':RadioStationURI})
        else:
            self.Discard('Invalid Command for SetAddRadioStationToQueue')

    def SetRadioStationsNavigation(self, value, qualifier):

        if value == 'Up':
            self.RadioStationNameDir.scroll_up(1)
            self.RadioStationURIDir.scroll_up(1)
        elif value == 'Down':
            self.RadioStationNameDir.scroll_down(1)
            self.RadioStationURIDir.scroll_down(1)
        elif value == 'Page Up':
            self.RadioStationNameDir.scroll_up(self._NumberofRadioStationsResult)
            self.RadioStationURIDir.scroll_up(self._NumberofRadioStationsResult)
        elif value == 'Page Down':
            self.RadioStationNameDir.scroll_down(self._NumberofRadioStationsResult)
            self.RadioStationURIDir.scroll_down(self._NumberofRadioStationsResult)

    def SetRadioStationsSearch(self, value, qualifier):

        RadioStationsSearchCmdString = '/MediaServer/ContentDirectory/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:ContentDirectory:1#Browse'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>\
        <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>R:0/0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter>\
        <StartingIndex>0</StartingIndex><RequestedCount>100</RequestedCount><SortCriteria></SortCriteria></u:Browse></s:Body></s:Envelope>'
        res = self.__UpdateHelper('RadioStationsSearch', value, qualifier, RadioStationsSearchCmdString, headers, data.encode())
        if res:
            try:
                RadioStationsNameList = []
                RadioStationsURIList = []
                Temp = ET.fromstring(res)             
                d = Temp.findtext('.//Result')    
                if d != '':
                    metadata = ET.fromstring(d)
                    for item in metadata.findall('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item'):
                        RadioStationsNameList.append(item.findtext('.//{http://purl.org/dc/elements/1.1/}title'))
                        RadioStationsURIList.append(item.findtext('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}res'))
                new_queue_data1 = ['{0}'.format(entry[0]) for entry in zip(RadioStationsNameList)]
                new_queue_data1.append('**End of List**')
                new_queue_data2 = ['{0}'.format(entry[0]) for entry in zip(RadioStationsURIList)]
                new_queue_data2.append('**End of List**')
                self.RadioStationNameDir.reset(new_queue_data1)
                self.RadioStationURIDir.reset(new_queue_data2)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Radio Stations Search: Invalid/unexpected response'])

    def SetSetURI(self, value, qualifier):

        uri = qualifier['URI']
        if uri:
            SetURICmdString = '/MediaRenderer/AVTransport/Control'
            action = 'urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
            <s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>{}</CurrentURI>\
            <CurrentURIMetaData>Radio</CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'.format(uri)
            self.__SetHelper('SetURI', value, qualifier, SetURICmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetSetURI')

    def UpdateSpeakerInformation(self, value, qualifier):

        SpeakerInformationCmdString = '/status/zp'
        headers = {'Content-Type': 'text/xml'}
        res = self.__UpdateHelper('SpeakerInformation', value, qualifier, SpeakerInformationCmdString, headers)
        if res:
            try:
                Temp = ET.fromstring(res)
                ZoneName = Temp.findtext('.//ZoneName')
                self.WriteStatus('SpeakerInformation', ZoneName, {'Details':'Zone Name'})
                UID = Temp.findtext('.//LocalUID')
                self.WriteStatus('SpeakerInformation', UID, {'Details':'UID'})
            except (ValueError, IndexError):
                self.Error(['Speaker Information: Invalid/unexpected response'])

    def SetSwitchtoLineIn(self, value, qualifier):

        UID = self.ReadStatus('SpeakerInformation', {'Details':'UID'})
        SwitchtoLineInCmdString = '/MediaRenderer/AVTransport/Control'
        action = 'urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>\
        <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon-stream:{}</CurrentURI>\
        <CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'.format(UID)
        self.__SetHelper('SwitchtoLineIn', value, qualifier, SwitchtoLineInCmdString, action, data.encode())

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'     : 'Play', 
            'Pause'    : 'Pause', 
            'Stop'     : 'Stop', 
            'Next'     : 'Next', 
            'Previous' : 'Previous'
        }

        TransportCmdString = '/MediaRenderer/AVTransport/Control'
        action = 'urn:schemas-upnp-org:service:AVTransport:1#{}'.format(ValueStateValues[value])
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:{} xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID>\
        <Speed>1</Speed></u:{}></s:Body></s:Envelope>'.format(ValueStateValues[value],ValueStateValues[value])
        self.__SetHelper('Transport', value, qualifier, TransportCmdString, action, data.encode())

    def UpdateTransport(self, value, qualifier):

        ValueStateValues = {
            'PLAYING'         : 'Play', 
            'PAUSED_PLAYBACK' : 'Pause', 
            'STOPPED'         : 'Stop'
        }

        TransportCmdString = '/MediaRenderer/AVTransport/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:AVTransport:1#GetTransportInfo'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:GetTransportInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>'
        res = self.__UpdateHelper('Transport', value, qualifier, TransportCmdString, headers, data.encode())
        if res:
            try:
                Temp = ET.fromstring(res)
                value = ValueStateValues[Temp.findtext('.//CurrentTransportState')]
                self.WriteStatus('Transport', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Transport: Invalid/unexpected response'])

    def SetUnjoin(self, value, qualifier):

        UnjoinCmdString = '/MediaRenderer/AVTransport/Control'
        action = 'urn:schemas-upnp-org:service:AVTransport:1#BecomeCoordinatorOfStandaloneGroup'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>\
        <u:BecomeCoordinatorOfStandaloneGroup xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:BecomeCoordinatorOfStandaloneGroup></s:Body></s:Envelope>' 
        self.__SetHelper('Unjoin', value, qualifier, UnjoinCmdString, action, data.encode())

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '/MediaRenderer/RenderingControl/Control'
            action = 'urn:schemas-upnp-org:service:RenderingControl:1#SetVolume'
            data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
            <s:Body><u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel>\
            <DesiredVolume>{}</DesiredVolume></u:SetVolume></s:Body></s:Envelope>'.format(str(value))
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString, action, data.encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '/MediaRenderer/RenderingControl/Control'
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': 'urn:schemas-upnp-org:service:RenderingControl:1#GetVolume'
        }
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
        <s:Body><u:GetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetVolume></s:Body></s:Envelope>'
        res = self.__UpdateHelper('Volume', value, qualifier, VolumeCmdString, headers, data.encode())
        if res:
            try:
                Temp = ET.fromstring(res)
                value = int(Temp.findtext('.//CurrentVolume'))
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response = response.read().decode()
        return response
  
    def __SetHelper(self, command, value, qualifier, url, action, data=None):

        self.Debug = True       
        if command != 'Join':
            url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': action
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=10)           
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
        return res

    def __UpdateHelper(self, command, value, qualifier, url, headers, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        if command == 'SpeakerInformation' or command =='AvailableZonesSearch':
            my_request = urllib.request.Request(url, data=data, headers=headers)
        else:
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful  
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)        
        return res         

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_module()
        return res

    return wrapper

class Directory:
    
    def __init__(self, display_count, write_function_name, detailstype, filler=None):
        self._display_count = int(display_count)
        self.detailstype = detailstype
        self.qualifier_list = ['Button','Details Type']
        self._qualifier_type = 'Enum'
        self._write_function_name = write_function_name
        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.entry_function = lambda entry: entry
        
    @property
    def display_count(self):
        return self._display_count
    
    @property
    def qualifier_type(self):
        return self._qualifier_type
    
    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value
    
    def write_to_module(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_list[0]:position_value, self.qualifier_list[1]:self.detailstype})

    def write_status_function(self, value, qualifier, context):
        pass    

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)
            
    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):
        
        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler
        
    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler
        
    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1
                
            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count
        
    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0
    
    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1 # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0
    
    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0
    
    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1