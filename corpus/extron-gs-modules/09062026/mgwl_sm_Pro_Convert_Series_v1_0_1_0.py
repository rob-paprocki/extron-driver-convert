from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
import hashlib
import json
from extronlib import Version

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
        self._NumberofSourcePresetsListResults = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentSelectedSourceStatus': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'SourcePresetCommand': {'Parameters':['NDI Source'], 'Status': {}},
            'SourcePresetsListNavigation': { 'Status': {}},
            'SourcePresetsListRefresh': {'Parameters':['Type'], 'Status': {}},
            'SourcePresetsListResults': {'Parameters':['Position'], 'Status': {}},
            'SourcePresetsListSelect': {'Parameters':['NDI Source'], 'Status': {}},
            'SourcePresetString': { 'Status': {}}, 
        }

        self.source_presets_list_directory = Directory('SourcePresetsListResults', self._NumberofSourcePresetsListResults, filler='')
        self.source_presets_list_directory.write_status_function = self.WriteStatus

    @property
    def NumberofSourcePresetsListResults(self):
        return self._NumberofSourcePresetsListResults

    @NumberofSourcePresetsListResults.setter
    def NumberofSourcePresetsListResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofSourcePresetsListResults = int(value)
            self.source_presets_list_directory = Directory('SourcePresetsListResults', self._NumberofSourcePresetsListResults, filler='')
            self.source_presets_list_directory.write_status_function = self.WriteStatus
        else:
            print('Invalid Number of Source Preset Lists Results Parameter.')

    def SetLogin(self, value, qualifier):
        opener = self.Opener
        opener.add_handler(urllib.request.HTTPCookieProcessor())
        url = 'mwapi?method=login&id={0}&pass={1}'.format(self.deviceUsername, hashlib.md5(self.devicePassword.encode()).hexdigest())
        my_request = urllib.request.Request(''.join([self.RootURL, url]), headers={'Content-Type': 'application/json'}, method='GET')
        response = opener.open(my_request, timeout=10)
        if response:
            res = json.loads(response.read().decode())
            if res['status'] != 0:
                self.Error(['Login: Invalid/unexpected response'])

    def UpdateCurrentSelectedSourceStatus(self, value, qualifier):

        cmdString = 'mwapi?method=get-channel'
        res = self.__UpdateHelper('CurrentSelectedSourceStatus', value, qualifier, url=cmdString)
        if res:
            try:
                value = res['name']
                self.WriteStatus('CurrentSelectedSourceStatus', value, qualifier)
            except KeyError:
                self.Error(['Current Selected Source Status: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        cmdString = 'mwapi?method=reboot'
        self.__SetHelper('Reboot', value, qualifier, url=cmdString)

    def SetSourcePresetCommand(self, value, qualifier):

        NDISourceStates = {
            'True' : True,
            'False' : False
        }

        name = value
        if qualifier['NDI Source'] in NDISourceStates and name:
            cmdString = 'mwapi?method=set-channel&ndi-name={}&name={}'.format(NDISourceStates[qualifier['NDI Source']], name)
            self.__SetHelper('SourcePresetCommand', value, qualifier, url=cmdString)
        else:
            self.Discard('Invalid Command for SetSourcePresetCommand')

    def SetSourcePresetsListNavigation(self, value, qualifier):

        if value == 'Up':
            self.source_presets_list_directory.scroll_up(1)
        elif value == 'Down':
            self.source_presets_list_directory.scroll_down(1)
        elif value == 'Page Up':
            self.source_presets_list_directory.scroll_up(self._NumberofSourcePresetsListResults)
        elif value == 'Page Down':
            self.source_presets_list_directory.scroll_down(self._NumberofSourcePresetsListResults)
        else:
            self.Discard('Invalid Command for SetSourcePresetsListNavigation')

    def SetSourcePresetsListRefresh(self, value, qualifier):

        if qualifier['Type'] in ['Name', 'URL']:
            self.source_presets_list_directory.reset(['*** Loading... Please wait ***'])
            cmdString = 'mwapi?method=list-channels'
            res = self.__SetHelper('SourcePresetsListRefresh', value, qualifier, url=cmdString)
            if res:
                SourcePresetsList = []
                for item in res['channels']:
                    SourcePresetsList.append(item[qualifier['Type'].lower()])
                SourcePresetsList.append('*** End of List ***')
                self.source_presets_list_directory.reset(SourcePresetsList)
        else:
            self.Discard('Invalid Command for SetSourcePresetsListRefresh')

    def SetSourcePresetsListSelect(self, value, qualifier):

        NDISourceStates = {
            'True' : True,
            'False' : False
        }

        if qualifier['NDI Source'] in NDISourceStates and 1 <= int(value) <= 10:
            name = self.ReadStatus('SourcePresetsListResults', {'Position': value})
            if name and name not in ['*** End of List ***', '*** Loading... Please wait ***']:
                cmdString = 'mwapi?method=set-channel&ndi-name={}&name={}'.format(NDISourceStates[qualifier['NDI Source']], name)
                self.__SetHelper('SourcePresetsListSelect', value, qualifier, url=cmdString)
            else:
                self.Discard('Invalid Command for SetSourcePresetsListSelect')
        else:
            self.Discard('Invalid Command for SetSourcePresetsListSelect')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = json.loads(response.read().decode())
        if res:
            if res['status'] != 0:
                if res['status'] == 37: # MW_STATUS_NOT_LOGGED_IN
                    self.SetLogin( None, None)
                else:
                    self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
                res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers={'Content-Type': 'application/json'}, method='GET') # create Request object

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
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

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers={'Content-Type': 'application/json'}) # create Request object

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
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
            self.write_to_driver()
        return res
    return wrapper

class Directory:

    def __init__(self, write_function_name, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
        self.write_function_name = write_function_name
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

    def write_to_driver(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self.write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value})

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