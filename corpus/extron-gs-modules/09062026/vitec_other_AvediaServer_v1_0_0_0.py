from extronlib.system import ProgramLog, Wait
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
        self._NumberofAllChannelsListResults = 5
        self._NumberofEndpointListResults = 5
        self._NumberofGroupListResults = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AllChannelsListNavigation': { 'Status': {}},
            'AllChannelsListResults': {'Parameters':['Position'], 'Status': {}},
            'AllChannelsListResultSet': {'Parameters':['Target'], 'Status': {}},
            'AllChannelsListSearch': {'Parameters':['Type'], 'Status': {}},
            'AllChannelsListUpdate': {'Parameters':['Type'], 'Status': {}},
            'ChannelSet': {'Parameters':['Target','Type'], 'Status': {}},
            'EndpointListNavigation': { 'Status': {}},
            'EndpointListResults': {'Parameters':['Position'], 'Status': {}},
            'EndpointListResultSet': { 'Status': {}},
            'EndpointListSearch': { 'Status': {}},
            'EndpointListUpdate': { 'Status': {}},
            'EndpointSet': { 'Status': {}},
            'GroupListNavigation': { 'Status': {}},
            'GroupListResults': {'Parameters':['Position'], 'Status': {}},
            'GroupListResultSet': { 'Status': {}},
            'GroupListSearch': { 'Status': {}},
            'GroupListUpdate': { 'Status': {}},
            'GroupSet': { 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'Mute': {'Parameters':['Target'], 'Status': {}},
            'Power': {'Parameters':['Target'], 'Status': {}},
            'Volume': {'Parameters':['Target'], 'Status': {}}
        }

        self.AllChannelsListUpdateParam = None # used to lookup Type qualifier used for AllChannelsListUpdate
        self.ChannelDuplicateCount = {} # used to keep track of duplicate channel names
        self.AllChannelsListDataByName = {} # holds all channel data by name for lookup
        self.AllChannelsListDataByNumber = {} # holds all channel data by number for lookup
        self.EndpointListData = {} # holds all endpoint data for lookup
        self.GroupListData = {} # holds all group data for lookup
        self.CurrentEndpointSelected = None # determines which endpoint is selected
        self.CurrentGroupSelected = None # determines which group is selected

        self.all_channel_list_directory = Directory('AllChannelsListResults', self._NumberofAllChannelsListResults, filler='')
        self.all_channel_list_directory.write_status_function = self.WriteStatus

        self.endpoint_list_directory = Directory('EndpointListResults', self._NumberofEndpointListResults, filler='')
        self.endpoint_list_directory.write_status_function = self.WriteStatus

        self.group_list_directory = Directory('GroupListResults', self._NumberofGroupListResults, filler='')
        self.group_list_directory.write_status_function = self.WriteStatus

    @property
    def NumberofAllChannelsListResults(self):
        return self._NumberofAllChannelsListResults

    @NumberofAllChannelsListResults.setter
    def NumberofAllChannelsListResults(self, value):
        if 1 <= int(value) <= 20:
            self._NumberofAllChannelsListResults = value
            self.all_channel_list_directory = Directory('AllChannelsListResults', self._NumberofAllChannelsListResults, filler='')
        else:
            self.Error(['Number of All Channels List Results is out of range.'])

    @property
    def NumberofEndpointListResults(self):
        return self._NumberofEndpointListResults

    @NumberofEndpointListResults.setter
    def NumberofEndpointListResults(self, value):
        if 1 <= int(value) <= 20:
            self._NumberofEndpointListResults = value
            self.endpoint_list_directory = Directory('EndpointListResults', self._NumberofEndpointListResults, filler='')
        else:
            self.Error([('Number of Endpoint List Results is out of range.')])

    @property
    def NumberofGroupListResults(self):
        return self._NumberofGroupListResults

    @NumberofGroupListResults.setter
    def NumberofGroupListResults(self, value):
        if 1 <= int(value) <= 20:
            self._NumberofGroupListResults = value
            self.group_list_directory = Directory('GroupListResults', self._NumberofGroupListResults, filler='')
        else:
            self.Error(['Number of Group List Results is out of range.'])

    def ChannelDataLookupHandler(self, type_):

        Types = {
            'Name'  : self.AllChannelsListDataByName,
            'Number': self.AllChannelsListDataByNumber
        }

        try:
            return Types[type_]
        except KeyError:
            return None

    def TargetIDHandler(self, qualifier):

        if qualifier['Target'] == 'Endpoint': # if qualifier selected is endpoint
            lookup = [self.EndpointListData, self.CurrentEndpointSelected] # set variables to use for lookup to endpoint
        elif qualifier['Target'] == 'Group': # elif qualifier selected is group
            lookup = [self.GroupListData, self.CurrentGroupSelected] # set variables to use for lookup to group

        try:
            return lookup[0][lookup[1]] # looks up target ID based on qualifier selection
        except (NameError, KeyError):
            return ''

    def CommandURLHandler(self, qualifier, value):

        TargetStates = {
            'Endpoint' : 'devices',
            'Group' : 'groups'
        }

        targetID = self.TargetIDHandler(qualifier)

        url = ''
        if targetID:
            url = 'api/public/control/{}/{}/commands/{}'.format(TargetStates[qualifier['Target']], targetID, value)
        return url

    def CommandBodyHandler(self, command, dataLookup, value):

        data = None
        if command in ['AllChannelsListResultSet', 'ChannelSet']:
            try:
                data = {
                    "channelid": dataLookup[value]['Channel ID'],
                    "uri": "",
                    "isFullScreen": 0,
                    "params": {}
                }
            except KeyError:
                return None
        elif command == 'Volume':
            data = {"params": str(value)}
        return data
    
    def SetAllChannelsListNavigation(self, value, qualifier):

        if value == 'Up':
            self.all_channel_list_directory.scroll_up(1)
        elif value == 'Down':
            self.all_channel_list_directory.scroll_down(1)
        elif value == 'Page Up':
            self.all_channel_list_directory.scroll_up(self._NumberofAllChannelsListResults)
        elif value == 'Page Down':
            self.all_channel_list_directory.scroll_down(self._NumberofAllChannelsListResults)
        else:
            self.Discard('Invalid Command for SetAllChannelsListNavigation')

    def SetAllChannelsListResultSet(self, value, qualifier):

        item = None
        if 1 <= int(value) <= 20:
            item = self.ReadStatus('AllChannelsListResults', {'Position': value})

        dataLookup = self.ChannelDataLookupHandler(self.AllChannelsListUpdateParam) # get appropriate AllChannelsListData lookup dictionary based on Type qualifier
        if item and item not in ['*** End of List ***', '*** Loading... Please wait ***'] and dataLookup:
            cmdString = self.CommandURLHandler(qualifier, 'channel')
            data = self.CommandBodyHandler('AllChannelsListResultSet', dataLookup, item)
            if cmdString and data:
                self.__SetHelper('AllChannelsListResultSet', value, qualifier, url=cmdString, data=data)
            else:
                self.Discard('Invalid Command for SetAllChannelsListResultSet')
        else:
            self.Discard('Invalid Command for SetAllChannelsListResultSet')

    def SetAllChannelsListSearch(self, value, qualifier):

        dataLookup = self.ChannelDataLookupHandler(qualifier['Type']) # get appropriate AllChannelsListData lookup dictionary based on Type qualifier
        if dataLookup and qualifier['Type'] == self.AllChannelsListUpdateParam:
            allChannelListItems = []
            for item in dataLookup:
                if value.lower() in str(item).lower():
                    allChannelListItems.append(item)
            new_directory_data = sorted(allChannelListItems) # sort results
            new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item
            self.all_channel_list_directory.reset(new_directory_data)
        else:
            self.Discard('Invalid Command for SetAllChannelsListSearch')

    def SetAllChannelsListUpdate(self, value, qualifier):

        if qualifier['Type'] in ['Name', 'Number']:
            self.all_channel_list_directory.reset(['*** Loading... Please wait ***'])
            self.AllChannelsListUpdateParam = qualifier['Type'] # store Type qualifier to use in AllChannelsListResultSet and ChannelSet
            cmdString = 'api/public/control/channels'
            res = self.__UpdateHelper('AllChannelsListUpdate', value, qualifier, url=cmdString)
            if res:
                results = json.loads(res.read().decode())
                self.ChannelDuplicateCount.clear()
                for i in range(0, len(results)): # max value determined by number of channels in response
                    name = results[i]['name']
                    if self.ChannelDuplicateCount.__contains__(name): # if duplicate
                        self.ChannelDuplicateCount[name] = self.ChannelDuplicateCount[name]+1 # store channel name as key and count as value, ex: {'CNN': 3, 'FS2': 1}
                    else:
                        self.ChannelDuplicateCount[name] = 1 # if not a duplicate or not added to ChannelDuplicateCount yet

                allChannelListItems = []
                self.AllChannelsListDataByName.clear()
                self.AllChannelsListDataByNumber.clear()

                for i in range(0, len(results)):
                    name = results[i]['name']
                    channelData = {
                        'Channel ID': results[i]['channelid'],
                        'Number': results[i]['number'],
                        'Name': name
                    }
                    if self.ChannelDuplicateCount[name] > 1: # if duplicate
                        name = '{}: {}'.format(name, results[i]['number']) # format channel name to include channel number, ex: 'CNN: 1'
                    if qualifier['Type'] == 'Name':
                        allChannelListItems.append(name) # ex: ['CNN', 'FS2'] or ['CNN: 1', 'FS2']
                    else: # if Type is Number
                        allChannelListItems.append(results[i]['number']) # ex: ['1', '2']
                    self.AllChannelsListDataByName[name] = channelData
                    self.AllChannelsListDataByNumber[results[i]['number']] = channelData

                new_directory_data = sorted(allChannelListItems) # sort results
                new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item
                self.all_channel_list_directory.reset(new_directory_data)
        else:
            self.Discard('Invalid Command for SetAllChannelsListUpdate')

    def SetChannelSet(self, value, qualifier):

        item = value # channel name or number
        if item and qualifier['Target'] in ['Endpoint', 'Group'] and qualifier['Type'] in ['Name', 'Number']:
            if not self.AllChannelsListUpdateParam: # if AllChannelsListData dictionaries not updated yet
                self.SetAllChannelsListUpdate(None, {'Type': qualifier['Type']}) # call all channels update method once to update AllChannelsListData dictionaries

            dataLookup = self.ChannelDataLookupHandler(qualifier['Type']) # get appropriate AllChannelsListData lookup dictionary based on Type qualifier
            if dataLookup:
                if qualifier['Type'] != 'Name': # if string entered for ChannelSetString should be a number (Number type)
                    try:
                        item = int(item) # try to convert to int
                    except ValueError: # if unable to
                        self.Discard('Invalid Command for SetChannelSet') # discard command
                        return # exit the method

                cmdString = self.CommandURLHandler(qualifier, 'channel')
                data = self.CommandBodyHandler('ChannelSet', dataLookup, item)
                if cmdString and data:
                    self.__SetHelper('ChannelSet', value, qualifier, url=cmdString, data=data)
                else:
                    self.Discard('Invalid Command for SetChannelSet')
            else:
                self.Discard('Invalid Command for SetChannelSet')
        else:
            self.Discard('Invalid Command for SetChannelSet')

    def SetEndpointListNavigation(self, value, qualifier):

        if value == 'Up':
            self.endpoint_list_directory.scroll_up(1)
        elif value == 'Down':
            self.endpoint_list_directory.scroll_down(1)
        elif value == 'Page Up':
            self.endpoint_list_directory.scroll_up(self._NumberofEndpointListResults)
        elif value == 'Page Down':
            self.endpoint_list_directory.scroll_down(self._NumberofEndpointListResults)
        else:
            self.Discard('Invalid Command for SetEndpointListNavigation')

    def SetEndpointListResultSet(self, value, qualifier):

        item = None
        if 1 <= int(value) <= 20:
            item = self.ReadStatus('EndpointListResults', {'Position': value}) # endpoint name

        if item and item not in ['N/A', '*** End of List ***', '*** Loading... Please wait ***']:
            self.CurrentEndpointSelected = item  # set endpoint item selected to CurrentEndpointSelected (validated in TargetIDHandler method)
        else:
            self.Discard('Invalid Command for SetEndpointListResultSet')

    def SetEndpointListSearch(self, value, qualifier):

        if self.EndpointListData:
            endpointListItems = []
            for item in self.EndpointListData:
                if value.lower() in str(item).lower():
                    endpointListItems.append(item)
            new_directory_data = sorted(endpointListItems) # sort results
            new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item
            self.endpoint_list_directory.reset(new_directory_data)
        else:
            self.Discard('Invalid Command for SetEndpointListSearch')

    def SetEndpointListUpdate(self, value, qualifier):

        self.endpoint_list_directory.reset(['*** Loading... Please wait ***'])
        cmdString = 'api/public/control/devices'
        res = self.__UpdateHelper('EndpointListUpdate', value, qualifier, url=cmdString)
        if res:
            results = json.loads(res.read().decode())
            endpointListItems = []
            self.EndpointListData.clear()
            for i in range(0, len(results)): # max value determined by number of endpoints in response
                if results[i]['name']: # if endpoint item exists
                    endpointListItems.append(results[i]['name']) # create list of endpoint items to show defined by Type qualifier, ex: ['047B49', 'm9405 Demo']
                    self.EndpointListData[results[i]['name']] = results[i]['id'] # stores endpoint name as key and endpoint id as value, ex: {'047B49': '6786205014884513'}
                else:
                    endpointListItems.append('N/A') # if endpoint item does not exist, show N/A
            new_directory_data = sorted(endpointListItems) # sort results
            new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item

            self.endpoint_list_directory.reset(new_directory_data)
                
    def SetEndpointSet(self, value, qualifier):

        item =  value # endpoint name
        if item:
            self.CurrentEndpointSelected = item # set endpoint item entered to CurrentEndpointSelected (validated in TargetIDHandler method)
            self.SetEndpointListUpdate(None, None) # call endpoint update method to update EndpointListData
        else:
            self.Discard('Invalid Command for SetEndpointSet')

    def SetGroupListNavigation(self, value, qualifier):

        if value == 'Up':
            self.group_list_directory.scroll_up(1)
        elif value == 'Down':
            self.group_list_directory.scroll_down(1)
        elif value == 'Page Up':
            self.group_list_directory.scroll_up(self._NumberofGroupListResults)
        elif value == 'Page Down':
            self.group_list_directory.scroll_down(self._NumberofGroupListResults)
        else:
            self.Discard('Invalid Command for SetGroupListNavigation')

    def SetGroupListResultSet(self, value, qualifier):

        name = None
        if 1 <= int(value) <= 20:
            name = self.ReadStatus('GroupListResults', {'Position': value}) # group name

        if name and name not in ['*** End of List ***', '*** Loading... Please wait ***']:
            self.CurrentGroupSelected = name # set group name selected to CurrentGroupSelected (validated in TargetIDHandler method)
        else:
            self.Discard('Invalid Command for SetGroupListResultSet')

    def SetGroupListSearch(self, value, qualifier):

        if self.GroupListData:
            groupListItems = []
            for item in self.GroupListData:
                if value.lower() in str(item).lower():
                    groupListItems.append(item)
            new_directory_data = sorted(groupListItems) # sort results
            new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item
            self.group_list_directory.reset(new_directory_data)
        else:
            self.Discard('Invalid Command for SetGroupListSearch')

    def SetGroupListUpdate(self, value, qualifier):

        self.group_list_directory.reset(['*** Loading... Please wait ***'])
        cmdString = 'api/public/control/groups'
        res = self.__UpdateHelper('GroupListUpdate', value, qualifier, url=cmdString)
        if res:
            results = json.loads(res.read().decode())
            groupListItems = []
            self.GroupListData.clear()
            for i in range(0, len(results)): # max value determined by number of groups in response
                groupListItems.append(results[i]['name']) # create list of group names to show, ex: ['Tower A', 'Tower B']
                self.GroupListData[results[i]['name']] = str(results[i]['id']) # stores group name as key and group id as value, ex: {'Tower A': '1'}
            new_directory_data = sorted(groupListItems) # sort results
            new_directory_data.append('*** End of List ***') # add '*** End of List ***' as last item
            self.group_list_directory.reset(new_directory_data)
            
    def SetGroupSet(self, value, qualifier):

        name =  value # group name
        if name:
            self.CurrentGroupSelected = name # set group name entered to CurrentGroupSelected (validated in TargetIDHandler method)
            self.SetGroupListUpdate(None, None) # call group update method to update GroupListData
        else:
            self.Discard('Invalid Command for SetGroupSet')

    def UpdateHeartbeat(self, value, qualifier):

        cmdString = 'api/webserver/status'
        self.__UpdateHelper('Heartbeat', value, qualifier, url=cmdString)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'mute',
            'Off' : 'unmute'
        }

        if value in ValueStateValues:
            cmdString = self.CommandURLHandler(qualifier, ValueStateValues[value])
            if cmdString:
                self.__SetHelper('Mute', value, qualifier, url=cmdString)
            else:
                self.Discard('Invalid Command for SetMute')
        else:
            self.Discard('Invalid Command for SetMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'poweron',
            'Off' : 'poweroff',
            'Reboot' : 'reboot'
        }

        if value in ValueStateValues:
            cmdString = self.CommandURLHandler(qualifier, ValueStateValues[value])
            if cmdString:
                self.__SetHelper('Power', value, qualifier, url=cmdString)
            else:
                self.Discard('Invalid Command for SetPower')
        else:
            self.Discard('Invalid Command for SetPower')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            cmdString = self.CommandURLHandler(qualifier, value)
            data = self.CommandBodyHandler('Volume', None, value)
            if cmdString and data:
                self.__SetHelper('Volume', value, qualifier, url=cmdString, data=data)
            else:
                self.Discard('Invalid Command for SetVolume')
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        if data: # if command body exists
            data = json.dumps(data).encode() # encode it

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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
            self.write_to_module()
        return res
    return wrapper

class Directory:

    def __init__(self, write_function_name, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
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
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value})

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