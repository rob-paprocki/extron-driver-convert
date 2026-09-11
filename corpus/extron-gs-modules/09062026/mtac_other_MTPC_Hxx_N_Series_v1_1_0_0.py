from extronlib.system import ProgramLog, Wait
import base64
import urllib.error
import urllib.request
import json
import base64

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
        self._NumberofAppListResults = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AppListNavigation': { 'Status': {}},
            'AppListRefresh': { 'Status': {}},
            'AppListResults': {'Parameters':['Position'], 'Status': {}},
            'AppListSelect': { 'Status': {}},
            'CurrentRunningApp': { 'Status': {}},
            'LaunchAppCommand': { 'Status': {}},
        }

        self.app_list_scroller = Scroller([], int(self._NumberofAppListResults), end=('*** End of List ***', 0))
        self.app_dictionary = {}

    @property
    def NumberofAppListResults(self):
        return self._NumberofAppListResults

    @NumberofAppListResults.setter
    def NumberofAppListResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofAppListResults = value
            self.app_list_scroller = Scroller([], int(self._NumberofAppListResults), end=('*** End of List ***', 0))
        else:
            self.Error(['Number of App List Results Parameter is out of range.'])

    def listRefresh(self):
        for entry,data in enumerate(self.app_list_scroller, 1):
            self.WriteStatus('AppListResults', data[0], {'Position': str(entry)})
    
    def __GetBasicAuthHeader(self):
        authHandler = '{0}:{1}'.format(self.deviceUsername, self.devicePassword).encode()
        authHeader = base64.b64encode(authHandler).decode("ascii")
        return authHeader
    
    def SetAppListNavigation(self, value, qualifier):

        if value == 'Up':
            self.app_list_scroller.previous()
        elif value == 'Down':
            self.app_list_scroller.next()
        elif value == 'Page Up':
            self.app_list_scroller.previous_page()
        elif value == 'Page Down':
            self.app_list_scroller.next_page()
        else:
            self.Discard('Invalid Command for SetAppListNavigation')
        self.listRefresh()
        
    def SetAppListRefresh(self, value, qualifier):

        path = 'api/run-configs'
        res = self.__SetHelper('AppListRefresh', value, qualifier, url=path)
        if res:
            self.app_list_scroller.clear()
            for app in res:
                self.app_list_scroller.append((app["name"], app["id"]))
                if app["running"] == True:
                    value = app["name"]
            self.listRefresh()

    def SetAppListSelect(self, value, qualifier):

        if 1 <= int(value) <= self._NumberofAppListResults and self.app_list_scroller.offset + int(value) <= self.app_list_scroller.all_size:
            name = self.ReadStatus('AppListResults', {'Position': value})
            if name and name not in ['*** End of List ***']:
                app_id = self.app_list_scroller[int(value) - 1][1]
                path = 'api/run-configs/{}/run'.format(app_id)
                self.__SetHelper('AppListSelect', value, qualifier, url=path)
            else:
                self.Discard('Invalid Command for SetAppListSelect')
        else:
            self.Discard('Invalid Command for SetAppListSelect')

    def UpdateCurrentRunningApp(self, value, qualifier):

        path = 'api/run-configs'
        res = self.__UpdateHelper('CurrentRunningApp', value, qualifier, url=path)
        if res:
            try:
                self.app_dictionary.clear()
                for app in res:
                    self.app_dictionary[app["name"]] = app["id"]
                    if app["running"] == True:
                        value = app["name"]
                self.WriteStatus('CurrentRunningApp', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Current Running App: Invalid/unexpected response'])

    def SetLaunchAppCommand(self, value, qualifier):

        app = value
        if app and app in self.app_dictionary:
            path = 'api/run-configs/{}/run'.format(self.app_dictionary[app])
            self.__SetHelper('LaunchAppCommand', value, qualifier, url=path)
        else:
            self.Discard('Invalid Command for SetLaunchAppCommand')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader())}

        if command == 'AppListRefresh':
            method = 'GET'
        else:
            method = 'POST'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

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
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader())}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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