import base64
import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Subscription = {}

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self._NumberofNDISourceListResults = 5
        self.Models = {}


        self.Commands = {
            'NDIDecoderSourceSelect': {'Parameters':['IP Address','Port Number','Source Name','Source PC Name'], 'Status': {}},
            'NDISourceListNavigation': { 'Status': {}},
            'NDISourceListRefresh': { 'Status': {}},
            'NDISourceListResults': {'Parameters':['Position'], 'Status': {}},
            }
        
        self.ndi_source_list_directory = Directory('NDISourceListResults', self._NumberofNDISourceListResults, filler='')
        self.ndi_source_list_directory.write_status_function = self.WriteStatus

    @property
    def NumberofNDISourceListResults(self):
        return self._NumberofNDISourceListResults

    @NumberofNDISourceListResults.setter
    def NumberofNDISourceListResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofNDISourceListResults = int(value)
            self.ndi_source_list_directory = Directory('NDISourceListResults', self._NumberofNDISourceListResults, filler='')
            self.ndi_source_list_directory.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of NDI Source List Results Parameter is out of range.'])

    def SetNDIDecoderSourceSelect(self, value, qualifier):

        if qualifier['Source Name'] and qualifier['Source PC Name']:
            if qualifier['IP Address'] and qualifier['Port Number']:
                try:
                    data = {"connectToIp": qualifier['IP Address'], "port": int(qualifier['Port Number']), "sourceName": qualifier['Source Name'], "sourcePcName": qualifier['Source PC Name']}
                except ValueError:
                    self.Discard('Invalid Command for SetNDIDecoderSourceSelect')
                    return
            elif not qualifier['IP Address'] and not qualifier['Port Number']:
                data = {"sourceName": qualifier['Source Name'], "sourcePcName": qualifier['Source PC Name']}
            else:
                self.Discard('Invalid Command for SetNDIDecoderSourceSelect')
                return

            cmdString = 'connectTo'
            self.__SetHelper('NDIDecoderSourceSelect', value, qualifier, url=cmdString, data=data)
        else:
            self.Discard('Invalid Command for SetNDIDecoderSourceSelect')

    def SetNDISourceListNavigation(self, value, qualifier):

        if value == 'Up':
            self.ndi_source_list_directory.scroll_up(1)
        elif value == 'Down':
            self.ndi_source_list_directory.scroll_down(1)
        elif value == 'Page Up':
            self.ndi_source_list_directory.scroll_up(self._NumberofNDISourceListResults)
        elif value == 'Page Down':
            self.ndi_source_list_directory.scroll_down(self._NumberofNDISourceListResults)
        else:
            self.Discard('Invalid Command for SetNDISourceListNavigation')

    def SetNDISourceListRefresh(self, value, qualifier):

        self.ndi_source_list_directory.reset(['*** Loading... Please wait ***'])
        cmdString = 'List'
        res = self.__SetHelper('NDISourceListRefresh', value, qualifier, url=cmdString)
        if res:
            results = json.loads(res.read().decode())
            NDISourceList = []
            for sourceName in results:
                NDISourceList.append(sourceName)
            NDISourceList.append('*** End of List ***')
            self.ndi_source_list_directory.reset(NDISourceList)

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        if data: # if command body exists
            data = json.dumps(data).encode() # encode it
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        method = 'GET' if command == 'NDISourceListRefresh' else 'POST'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

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
        return res

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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