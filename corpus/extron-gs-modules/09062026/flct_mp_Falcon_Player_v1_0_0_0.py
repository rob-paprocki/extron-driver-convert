# Copyright 2025, Extron. All rights reserved.

from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberofPlaylists = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PlayerStatus': { 'Status': {}},
            'PlaylistNavigation': { 'Status': {}},
            'PlaylistResult': {'Parameters':['Entry'], 'Status': {}},
            'PlaylistResultSet': {'Parameters':['Entry'], 'Status': {}},
            'PlaylistUpdate': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        self.playlist = Scroller([], self._NumberofPlaylists, end='*** End of list ***')
        self.playlist_set = None

    @property
    def NumberofPlaylists(self):
        return self._NumberofPlaylists

    @NumberofPlaylists.setter
    def NumberofPlaylists(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofPlaylists = value
            self.playlist = Scroller([], self._NumberofPlaylists, end='*** End of list ***')
        else:
            self.Error(['The value of Number of Playlists is outside of the range of allowable values.'])

    def __WritePlaylist(self):
        for entry, info in enumerate(self.playlist, 1):
            self.WriteStatus('PlaylistResult', info, {'Entry' : entry})

    def UpdatePlayerStatus(self, value, qualifier):

        PlayerStatusCmdString = 'api/system/status'
        res = self.__UpdateHelper('PlayerStatus', value, qualifier, url=PlayerStatusCmdString)
        if res:
            try:
                ValueStateValues = {
                    'idle' : 'Idle',
                    'playing' : 'Playing',
                    'stopping gracefully' : 'Stopping Gracefully',
                    'stopping gracefully after loop' : 'Stopping Gracefully After Loop',
                    'stopping now' : 'Stopping Now',
                    'paused' : 'Paused'
                }

                value = ValueStateValues[res['status_name']]
                self.WriteStatus('PlayerStatus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Player Status: Invalid/unexpected response'])

    def SetPlaylistNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : self.playlist.previous,
            'Down'      : self.playlist.next,
            'Page Up'   : self.playlist.previous_page,
            'Page Down' : self.playlist.next_page
        }

        if value in ValueStateValues and self.playlist.current_size > 0:
            ValueStateValues[value]()
            self.__WritePlaylist()
        else:
            self.Discard('Invalid Command for SetPlaylistNavigation')

    def SetPlaylistResultSet(self, value, qualifier):

        entry = int(qualifier['Entry'])

        if 1 <= entry <= self.playlist.window and self.playlist.offset + entry <= self.playlist.current_size:
            self.playlist_set = self.playlist[entry - 1]
        else:
            self.Discard('Invalid Command for SetPlaylistResultSet')

    def SetPlaylistUpdate(self, value, qualifier):

        self.playlist.clear()

        PlaylistUpdateCmdString = 'api/playlists'
        res = self.__UpdateHelper('PlaylistUpdate', value, qualifier, url=PlaylistUpdateCmdString)
        if res:
            try:
                for playlist in res:
                    self.playlist.append(playlist)
            except json.decoder.JSONDecodeError:
                self.Error(['Playlist Update: Invalid/unexpected response'])
        self.__WritePlaylist()

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Start'                     : 'start',
            'Stop'                      : 'playlists/stop',
            'Stop Gracefully'           : 'playlists/stopgracefully',
            'Stop Gracefully After Loop': 'playlists/stopgracefullyafterloop',
            'Pause'                     : 'playlists/pause',
            'Resume'                    : 'playlists/resume',
            'Next'                      : 'command/Next%20Playlist%20Item',
            'Previous'                  : 'command/Prev%20Playlist%20Item'
        }

        if value in ValueStateValues:
            if value == 'Start':
                playlist = self.playlist_set
                if playlist:
                    playlist = playlist.replace(' ', '%20')
                    TransportCmdString = 'api/playlist/{0}/{1}'.format(playlist, ValueStateValues[value])
                else:
                    TransportCmdString = ''
            else:
                TransportCmdString = 'api/{}'.format(ValueStateValues[value])
            if TransportCmdString:
                self.__SetHelper('Transport', value, qualifier, url=TransportCmdString)
            else:
                self.Discard('Invalid Command for SetTransport')
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            data = {
                'volume' : value
            }
            VolumeCmdString = 'api/system/volume'
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'api/system/volume'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                value = int(res['volume'])
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return json.loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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

        self.playlist_set = None

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port)
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

class Scroller:
    def __init__(self, items, window, mark_end=True, end='', fill=''):

        self.__all_items = list(items)
        self.__filtered_items = []
        self.__filter_key = None
        self.__current_items = self.__all_items
        self.__offset = 0
        self.__window = max(1, window)
        self.__mark_end = mark_end
        self.__end = end
        self.__fill = fill
    def __getitem__(self, index):

        return self.view()[index]

    def __iter__(self):

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            yield item

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                yield self.end

            for i in range(fill_count - int(self.mark_end)):
                yield self.fill

    def __str__(self):

        s = 'Offset {}/{}, viewing ({{}}) {}/{} items ({})'.format(self.offset, self.max_offset, self.window, self.current_size, self.view())

        if not self.filtered:
            return s.format('all')
        else:
            return s.format('filtered')
    @property
    def current_items(self):

        return self.__current_items.copy()

    @property
    def all_items(self):

        return self.__all_items.copy()

    @property
    def filtered_items(self):

        return self.__filtered_items.copy()

    @property
    def current_size(self):

        return len(self.__current_items)

    @property
    def all_size(self):

        return len(self.__all_items)

    @property
    def filtered_size(self):

        return len(self.__filtered_items)

    @property
    def offset(self):

        self.__offset = min(self.__offset, self.max_offset)
        return self.__offset

    @offset.setter
    def offset(self, offset):

        if 0 <= offset <= self.max_offset:
            self.__offset = offset
            return

        raise Exception('offset value \'{}\' is out of range [0, {}]'.format(offset, self.max_offset))

    @property
    def window(self):

        return self.__window

    @property
    def mark_end(self):

        return self.__mark_end

    @property
    def end(self):

        return self.__end

    @property
    def fill(self):

        return self.__fill

    @property
    def filtered(self):

        return self.__filter_key is not None

    @property
    def max_offset(self):

        return max(0, self.current_size - self.window + int(self.mark_end))

    def view(self):

        return list(self.__iter__())

    def format(self, key):

        items = []

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            items.append(key(item))

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                items.append(self.end)

            for i in range(fill_count - int(self.mark_end)):
                items.append(self.fill)

        return items
    def clear(self):

        self.__all_items.clear()

        self.__filtered_items.clear()
        self.__filter_key = None

        self.__current_items = self.__all_items

        self.offset = 0

    def overwrite(self, items):

        self.clear()
        self.extend(items)

    def append(self, item):

        self.__all_items.append(item)

        if self.__filter_key is not None and self.__filter_key(item):
            self.__filtered_items.append(item)

    def extend(self, items):

        self.__all_items.extend(items)

        if self.__filter_key is not None:
            for item in items:
                if self.__filter_key(item):
                    self.__filtered_items.append(item)

    def filter(self, key):

        self.__filter_key = key

        if self.__filter_key is not None:
            self.__filtered_items = [item for item in self.__all_items if self.__filter_key(item)]
            self.__current_items = self.__filtered_items
        else:
            self.__filtered_items.clear()
            self.__current_items = self.__all_items

        self.offset = 0
    def scroll(self, steps):

        self.offset = max(0, min(self.offset + steps, self.max_offset))
    def previous(self):

        self.scroll(-1)

    def next(self):

        self.scroll(1)

    def previous_page(self):

        self.scroll(-self.window)

    def next_page(self):

        self.scroll(self.window)

    def first(self):

        self.offset = 0

    def last(self):

        self.offset = self.max_offset