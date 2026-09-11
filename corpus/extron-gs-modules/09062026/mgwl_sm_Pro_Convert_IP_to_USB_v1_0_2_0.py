# Copyright 2026, Extron. All rights reserved.

import urllib.error
import urllib.request
from hashlib import sha256
import json
import re

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

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
        self._NumberofSourceListResults = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentSelectedSourceStatus': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'SourceListNameResults': {'Parameters': ['Position'], 'Status': {}},
            'SourceListNavigation': { 'Status': {}},
            'SourceListRefresh': { 'Status': {}},
            'SourceListSelect': { 'Status': {}},
            'SourceListURLResults': {'Parameters': ['Position'], 'Status': {}},
            'SourceSelect': { 'Status': {}},
        }

        self.LoginsFailed = 0

        self.source_list_scroller = Scroller([], self._NumberofSourceListResults, end={'config': {'name': '*** End of List ***', 'data': {'url': '*** End of List ***'}}}, fill={'config': {'name': '', 'data': {'url': ''}}})
        self.cookie = ''

    @property
    def NumberofSourceListResults(self):
        return self._NumberofSourceListResults

    @NumberofSourceListResults.setter
    def NumberofSourceListResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofSourceListResults = int(value)
            self.source_list_scroller = Scroller([], self._NumberofSourceListResults, end={'config': {'name': '*** End of List ***', 'data': {'url': '*** End of List ***'}}}, fill={'config': {'name': '', 'data': {'url': ''}}})

    def refresh_source_list(self):
        for position, source in enumerate(self.source_list_scroller, 1):
            self.WriteStatus('SourceListNameResults', source['config']['name'], {'Position': str(position)})
            self.WriteStatus('SourceListURLResults', source['config']['data'].get('url', 'Unknown'), {'Position': str(position)})

    def SetLogin(self, value, qualifier):
        opener = self.Opener
        url = '{}{}'.format(self.RootURL, 'api/user/login')
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'username': self.deviceUsername,
            'password': sha256(self.devicePassword.encode()).hexdigest()
        }

        my_request = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode(), method='POST')
        response = opener.open(my_request, timeout=10)
        if response:
            try:
                res = json.loads(response.read().decode())
                if 'status' in res:
                    status = int(res['status'])
                else:
                    status = int(res['result'])

                if status == 0:
                    if 'Set-Cookie' in response.headers:
                        cookie = response.headers['Set-Cookie']
                        cookie_match = re.search(r'(sid-.+=.+)(;path=/)?', cookie)
                        self.cookie = cookie_match.group(1)
                        self.LoginsFailed = 0
                    else:
                        self.LoginsFailed += 1
                        if self.LoginsFailed >= 3:
                            url = '/api/user/logout'
                            my_request = urllib.request.Request(''.join([self.RootURL, url]), headers=headers, method='GET')
                            opener.open(my_request, timeout=1)
                            self.cookie = ''
                            self.LoginsFailed = 0
                elif status == 16:
                    self.Error(['Login: The user does not exist'])
                elif status == 36:
                    self.Error(['Login: Wrong password'])
                else:
                    self.Error(['Login: Invalid/unexpected response ({})'.format(status)])
            except:
                self.Error(['Login: Invalid/unexpected response'])

    def UpdateCurrentSelectedSourceStatus(self, value, qualifier):

        CurrentSelectedSourceStatusCmdString = 'api/stream/status/get'
        res = self.__UpdateHelper('CurrentSelectedSourceStatus', value, qualifier, url=CurrentSelectedSourceStatusCmdString)
        if res:
            try:
                value = res['data']['name']
                self.WriteStatus('CurrentSelectedSourceStatus', value, qualifier)
            except KeyError:
                self.Error(['Current Selected Source Status: Invalid/unexpected response'])

    def UpdateFirmware(self, value, qualifier):

        url = 'api/system/device-info'
        res = self.__UpdateHelper('Firmware', value, qualifier, url=url)
        if res:
            try:
                value = res['firmware-ver']
                self.WriteStatus('Firmware', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Firmware: Invalid/unexpected response'])

            try:
                value = res['serial-number']
                self.WriteStatus('SerialNumber', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Serial Number: Invalid/unexpected response'])

    def SetSourceListNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.source_list_scroller.previous,
            'Down':         self.source_list_scroller.next,
            'Page Up':      self.source_list_scroller.previous_page,
            'Page Down':    self.source_list_scroller.next_page
        }

        if value in ValueStateValues and self.source_list_scroller.current_size > 0:
            ValueStateValues[value]()
            self.refresh_source_list()
        else:
            self.Discard('Invalid Command for SetSourceListNavigation')

    def SetSourceListRefresh(self, value, qualifier):

        ValueStateValues = {
            'Source Presets':   'static',
            'NDI Discovery':    'dynamic'
        }

        if value in ValueStateValues:
            SourceListRefreshCmdString = 'api/source/list?type={}'.format(ValueStateValues[value])
            res = self.__SetHelper('SourceListRefresh', value, qualifier, url=SourceListRefreshCmdString)
            if res:
                try:
                    self.source_list_scroller.overwrite(res['data'])
                    self.refresh_source_list()
                except KeyError:
                    self.Error(['Source List Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetSourceListRefresh')

    def SetSourceListSelect(self, value, qualifier):

        if 1 <= int(value) <= self._NumberofSourceListResults and self.source_list_scroller.offset + int(value) <= self.source_list_scroller.current_size:
            SourceListSelectCmdString = 'api/source/select'
            data = {
                'id': self.source_list_scroller[int(value) - 1]['id']
            }

            self.__SetHelper('SourceListSelect', value, qualifier, url=SourceListSelectCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSourceListSelect')

    def SetSourceSelect(self, value, qualifier):

        if 0 <= int(value) <= 100:
            SourceSelectCmdString = 'api/source/select'
            data = {
                'id': int(value)
            }

            self.__SetHelper('SourceSelect', value, qualifier, url=SourceSelectCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSourceSelect')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = json.loads(response.read().decode())

        if res:
            if 'status' in res:
                status = res['status']
            else:
                status = res['result']

            if status != 0:
                if status == 37 or status == -17: # MW_STATUS_NOT_LOGGED_IN
                    self.cookie = ''
                    self.SetLogin( None, None)
                else:
                    self.Error(['{}: Invalid/unexpected response ({})'.format(sourceCmdName, status)])
                res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {}
        if self.cookie:
            headers['Cookie'] = self.cookie
        if data:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, headers=headers, data=data, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=1)
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


        url = '{}{}'.format(self.RootURL, url)
        headers = {}
        if self.cookie:
            headers['Cookie'] = self.cookie
        if data:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, headers=headers, data=data, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=1)
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

        self.SetLogin( None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.LoginsFailed = 0

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