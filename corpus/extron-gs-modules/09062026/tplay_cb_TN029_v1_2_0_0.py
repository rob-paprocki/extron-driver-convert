import re
import base64
import urllib.error
import urllib.request
import json

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
        self._NumberOfRecordingSearch = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelSelectCommand': {'Parameters': ['Client ID', 'Channel'], 'Status': {}},
            'ChannelStep': {'Parameters': ['Client ID'], 'Status': {}},
            'IPTVServicesNavigation': { 'Status': {}},
            'IPTVServicesResults': {'Parameters': ['Position'], 'Status': {}},
            'IPTVServicesResultSet': {'Parameters': ['Position'], 'Status': {}},
            'IPTVServicesUpdate': { 'Status': {}},  
            'Keypad': {'Parameters': ['Client ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Client ID'], 'Status': {}},            
            'Mute': {'Parameters': ['Client ID'], 'Status': {}},
            'Power': {'Parameters': ['Client ID'], 'Status': {}},
            'Reboot': {'Parameters': ['Client ID'], 'Status': {}},
            'RecordingChannelName': {'Parameters':['Button'], 'Status': {}},
            'RecordingID': {'Parameters':['Button'], 'Status': {}},
            'RecordingIDSet': { 'Status': {}},
            'RecordingName': {'Parameters':['Button'], 'Status': {}},
            'RecordingNavigation': { 'Status': {}},
            'RecordingStart': {'Parameters':['Recording User', 'Recording Channel Name', 'Recording Name', 'Recording Family', 'Recording Category', 'Repeat Schedule','Repeat Days'], 'Status': {}},
            'RecordingStatus': {'Parameters':['Button'], 'Status': {}},
            'RecordingStop': {'Parameters':['Recording User'], 'Status': {}},
            'RecordingUpdate': {'Parameters':['Recording User', 'Type'], 'Status': {}},
            'Transport': {'Parameters': ['Client ID'], 'Status': {}},
            'TVInput': {'Parameters': ['Client ID'], 'Status': {}},
            'TVPower': {'Parameters': ['Client ID'], 'Status': {}},
            'TVVolume': {'Parameters': ['Client ID'], 'Status': {}},
            'Volume': {'Parameters': ['Client ID'], 'Status': {}}
        }

        self.lastIPTVServicesRes = ''
        
        self.RecordingList = []
        self.RecAdvance = True
        self.RecordingStartingEntry = 0
        self.RecordStopID = ''

        self.IPTVServices = Directory('IPTVServicesResults', 10, filler='')
        self.IPTVServices.write_status_function = self.WriteStatus

        self.Channel = ''

    @property
    def NumberOfRecordingSearch(self):
        return self._NumberOfRecordingSearch

    @NumberOfRecordingSearch.setter
    def NumberOfRecordingSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfRecordingSearch = int(value)
        else:
            print('Number of Recording Parameter must be within range 1 to 15')

    def SetChannelSelectCommand(self, value, qualifier):

        if qualifier['Client ID']:
            self.Channel = qualifier['Channel']
            if self.Channel:
                self.__SetHelper('ChannelSelectCommand', value, qualifier, url='call={"jsonrpc":"2.0","method":"SelectChannel","params":[' + qualifier['Client ID'] + ',' + self.Channel + ']}')
            else:
                self.Discard('Invalid Command for SetChannelSelectCommand')
        else:
            self.Discard('Invalid Command for SetChannelSelectCommand')

    def SetChannelStep(self, value, qualifier):

        if value in ['Up', 'Down'] and qualifier['Client ID']:
            self.__SetHelper('ChannelStep', value, qualifier, url='call={"jsonrpc":"2.0","method":"Channel' + value + '","params":[' + qualifier['Client ID'] + ']}')
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetIPTVServicesNavigation(self, value, qualifier):
        
        if value == 'Up':
            self.IPTVServices.scroll_up(1)
        elif value == 'Down':
            self.IPTVServices.scroll_down(1)
        elif value == 'Page Up':
            self.IPTVServices.scroll_up(10)
        elif value == 'Page Down':
            self.IPTVServices.scroll_down(10)
        else:
            self.Discard('Invalid Command for SetIPTVServicesNavigation')

    def SetIPTVServicesResultSet(self, value, qualifier):
        
        if 1 <= int(qualifier['Position']) <= 10:
            result = self.ReadStatus('IPTVServicesResults', qualifier)
            if result and result not in ['*** End of List ***', '*** No IPTV Services Available ***']:
                self.Channel = result.split('.')[0]
            else:
                self.Discard('Invalid Command for SetIPTVServicesResultSet')
        else:
            self.Discard('Invalid Command for SetIPTVServicesResultSet')

    def UpdateIPTVServicesUpdate(self, value, qualifier):

        res = self.__UpdateHelper('IPTVServicesUpdate', value, qualifier, url='call={"jsonrpc":"2.0","method":"GetAllServices","params":[-1]}')
        if res:
            self.counter = 0
            if res != self.lastIPTVServicesRes:
                temp_list = []
                self.lastIPTVServicesRes = res
                for result in res['result']:
                    try:
                        temp_list.append('{}. {}'.format(result['channelNumber'], result['name']))
                    except KeyError:
                        self.Error(['IPTV Services Update: Invalid/unexpected response'])
                if len(temp_list) > 0:
                    temp_list.append('*** End of List ***')
                    self.IPTVServices.reset(temp_list)
                else:
                    self.IPTVServices.reset(['*** No IPTV Services Available ***'])
        else:
            self.IPTVServices.reset(['*** No IPTV Services Available ***'])
            self.Error(['No IPTV Services Available'])

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9 and qualifier['Client ID']:
            self.__SetHelper('Keypad', value, qualifier, url='call={"jsonrpc":"2.0","method":"HandleKeyPress","params":[' + qualifier['Client ID'] + ',"Number' + value + '"]}')
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'Menu',
            'Up'    : 'Up',
            'Left'  : 'Left',
            'Ok'    : 'OK',
            'Right' : 'Right',
            'Down'  : 'Down',
            'Back'  : 'Back',
            'Guide' : 'Guide',
            'TV'    : 'TV',
            'Red'   : 'Red',
            'Green' : 'Green',
            'Yellow': 'Yellow',
            'Blue'  : 'Blue'
        }

        if value in ValueStateValues and qualifier['Client ID']:
            self.__SetHelper('MenuNavigation', value, qualifier, url='call={"jsonrpc":"2.0","method":"HandleKeyPress","params":[' + qualifier['Client ID'] + ',"' + ValueStateValues[value] + '"]}')
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }

        if value in ValueStateValues and qualifier['Client ID']:
            self.__SetHelper('Mute', value, qualifier, url='call={"jsonrpc":"2.0","method":"SetMute","params":[' + qualifier['Client ID'] + ',' + ValueStateValues[value] + ']}')
        else:
            self.Discard('Invalid Command for SetMute')

    def SetPower(self, value, qualifier):

        if qualifier['Client ID']:
            self.__SetHelper('Power', value, qualifier, url='call={"jsonrpc":"2.0","method":"HandleKeyPress","params":[' + qualifier['Client ID'] + ',"Power"]}')
        else:
            self.Discard('Invalid Command for SetPower')

    def SetReboot(self, value, qualifier):

        if qualifier['Client ID']:
            self.__SetHelper('Reboot', value, qualifier, url='call={"jsonrpc":"2.0","method":"Reboot","params":[' + qualifier['Client ID'] + ']}')
        else:
            self.Discard('Invalid Command for SetReboot')

    def SetRecordingIDSet(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 15
            }

        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and self.RecordingList and
                len(self.RecordingList) >= self.RecordingStartingEntry+value):
            self.RecordStopID = ''
            id_val = str(self.RecordingList[self.RecordingStartingEntry+value-1]["Id"])
            if id_val not in '***End of list***':
                self.RecordStopID = id_val.strip()
        else:
            self.Discard('Invalid Command for SetRecordingIDSet')

    def SetRecordingNavigation(self, value, qualifier):

        ValueStates = {
            'S': 'Scheduled',
            'I': 'In-Progress',
            'C': 'Completed',
            'F': 'Failed',
            'E': '***End of list***'
        }

        if 'Page Up' == value:
            self.RecordingStartingEntry -= self._NumberOfRecordingSearch
        elif 'Page Down' == value and self.RecAdvance:
            self.RecordingStartingEntry += self._NumberOfRecordingSearch

        if self.RecordingStartingEntry >= len(self.RecordingList):
            self.RecordingStartingEntry = len(self.RecordingList) - 1

        if self.RecordingStartingEntry < 0:
            self.RecordingStartingEntry = 0

        self.RecAdvance = True
        
        Button = 1
        for a in self.RecordingList[self.RecordingStartingEntry:]:
            self.WriteStatus('RecordingID', a["Id"], {'Button': Button})
            self.WriteStatus('RecordingName', a["RecordingName"], {'Button': Button})
            self.WriteStatus('RecordingChannelName', a["ChannelName"], {'Button': Button})
            self.WriteStatus('RecordingStatus', ValueStates[a["Status"]], {'Button': Button})  
            Button += 1
            if Button == self._NumberOfRecordingSearch + 1:
                break
        if self.RecordingList:
            for a in range(Button, self._NumberOfRecordingSearch + 1):
                self.RecAdvance = False
                self.WriteStatus('RecordingID', '', {'Button': a})
                self.WriteStatus('RecordingName', '', {'Button': a})
                self.WriteStatus('RecordingChannelName', '', {'Button': a})
                self.WriteStatus('RecordingStatus', '', {'Button': a})

    def SetRecordingStart(self, value, qualifier):

        RepeatScheduleStates = ('True', 'False')
        RepeatDaysConstraints = {
            'Min' : 0,
            'Max' : 99
            }

        user_string = qualifier['Recording User']
        channel_string = qualifier['Recording Channel Name']
        name_string = qualifier['Recording Name']
        family_string = qualifier['Recording Family']
        category_string = qualifier['Recording Category']
        repeat_sch = qualifier['Repeat Schedule']
        repeat_day = qualifier['Repeat Days']
        if (user_string and channel_string and name_string and 
                    0 <= repeat_day <= 99 and repeat_sch in RepeatScheduleStates):
            if family_string and category_string:
                RecordingStartCmdString = ''.join(['call={"jsonrpc":"2.0","method":"RecordChannel","params":["',
                                               user_string.replace(' ','%20'), '",{"ChannelName":"',
                                               channel_string.replace(' ','%20'), '","RecordingName":"',
                                               name_string.replace(' ','%20'), '","Family":"',
                                               family_string.replace(' ','%20'), '","Category":"',
                                               category_string.replace(' ','%20'), '","RepeatSchedule":',
                                               repeat_sch.lower(), ',"RepeatDays":', str(repeat_day), '}]}'])
            else:
                RecordingStartCmdString = ''.join(['call={"jsonrpc":"2.0","method":"RecordChannel","params":["',
                                               user_string.replace(' ','%20'), '",{"ChannelName":"',
                                               channel_string.replace(' ','%20'), '","RecordingName":"',
                                               name_string.replace(' ','%20'), '","RepeatSchedule":',
                                               repeat_sch.lower(), ',"RepeatDays":', str(repeat_day), '}]}'])
            self.__SetHelper('RecordingStart', value, qualifier, url=RecordingStartCmdString)
        else:
            self.Discard('Invalid Command for SetRecordingStart')

    def SetRecordingStop(self, value, qualifier):

        user_string = qualifier['Recording User']
        if user_string and self.RecordStopID:
            RecordingStopCmdString = ''.join(['call={"jsonrpc":"2.0","method":"StopRecording","params":["',
                                               user_string.replace(' ','%20'), '","',
                                               self.RecordStopID.replace(' ','%20'), '"]}'])
            self.__SetHelper('RecordingStop', value, qualifier, url=RecordingStopCmdString)
        else:
            self.Discard('Invalid Command for SetRecordingStop')

    def SetRecordingUpdate(self, value, qualifier):

        TypeStates = {
            'Scheduled':    'S',
            'In Progress':  'I',
            'Completed':    'C',
            'Failed':       'F',
            'All':          '',
            }
            
        user_string = qualifier['Recording User']
        type_val = qualifier['Type']
        if user_string and type_val in TypeStates:
            self.RecordingList = []
            newList = []
            RecordingUpdateCmdString = ''.join(['call={"jsonrpc":"2.0","method":"ViewRecordings","params":["',
                                            user_string, '","', TypeStates[type_val],'"]}'])
            res = self.__UpdateHelper('RecordingUpdate', value, qualifier, url=RecordingUpdateCmdString)
            if res:
                try:
                    parsed_json = res["result"]
                    if  parsed_json:
                        PerEntryList = []
                        for i in parsed_json:
                            PerEntryList = {"Id": parsed_json[i]["Id"],
                                            "Status": parsed_json[i]["Status"], 
                                            "RecordingName": parsed_json[i]["RecordingName"],
                                            "ChannelName": parsed_json[i]["ChannelName"]}
                            newList.append(PerEntryList)
                    if newList:
                        self.RecordingList = newList
                    self.RecordingList.append({"Id": "***End of list***", "Status": 'E', 
                                                "RecordingName": "***End of list***",
                                                "ChannelName": "***End of list***"})
                    self.RecAdvance = True
                    self.RecordingStartingEntry = 0
                    self.SetRecordingNavigation( None, None)
                except (ValueError, KeyError, IndexError):
                    self.Error(['Recording Update: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetRecordingUpdate')

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'   : 'Play',
            'Pause'  : 'Pause',
            'Stop'   : 'Stop',
            'Rewind' : 'Rewind',
            'Forward': 'Forward'
        }

        if value in ValueStateValues and qualifier['Client ID']:
            self.__SetHelper('Transport', value, qualifier, url='call={"jsonrpc":"2.0","method":"HandleKeyPress","params":[' + qualifier['Client ID'] + ',"' + ValueStateValues[value] + '"]}')
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetTVInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'         : '103',
            'HDMI'        : '101',
            'HDMI 1'      : '153',
            'HDMI 2'      : '154',
            'HDMI 3'      : '155',
            'HDMI 4'      : '156',  
            'DVI'         : '102',
            'DisplayPort' : '139',
            'PC'          : '160',
            'Media'       : '158'
        }

        if value in ValueStateValues and qualifier['Client ID']:
            self.__SetHelper('TVInput', value, qualifier, url='call={"jsonrpc":"2.0","method":"SelectTVInput","params":[' + qualifier['Client ID'] + ',' + ValueStateValues[value] + ']}')
        else:
            self.Discard('Invalid Command for SetTVInput')

    def SetTVPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'PowerOnTv',
            'Off': 'PowerOffTv'
        }

        if value in ValueStateValues and qualifier['Client ID']:
            self.__SetHelper('TVPower', value, qualifier, url='call={"jsonrpc":"2.0","method":"' + ValueStateValues[value] + '","params":[' + qualifier['Client ID'] + ']}')
        else:
            self.Discard('Invalid Command for SetTVPower')

    def SetTVVolume(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Client ID']:
            self.__SetHelper('TVVolume', value, qualifier, url='call={"jsonrpc":"2.0","method":"SetTVVolume","params":[' + qualifier['Client ID'] + ',' + str(value) + ']}')
        else:
            self.Discard('Invalid Command for SetTVVolume')


    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Client ID']:
            self.__SetHelper('Volume', value, qualifier, url='call={"jsonrpc":"2.0","method":"SetVolume","params":[' + qualifier['Client ID'] + ',' + str(value) + ']}')
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        if command in ('RecordingStart', 'RecordingStop'):
            url = '{}tripleshift/JsonRpcHandler.php?{}'.format(self.RootURL, url)
        else:
            url = '{}triplecare/JsonRpcHandler.php?{}'.format(self.RootURL, url)
        my_request = urllib.request.Request(url, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
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

        if command in ('RecordingUpdate'):
            url = '{}tripleshift/JsonRpcHandler.php?{}'.format(self.RootURL, url)
        else:
            url = '{}triplecare/JsonRpcHandler.php?{}'.format(self.RootURL, url)
        my_request = urllib.request.Request(url, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
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

        self.RecordingList = []
        self.RecAdvance = True
        self.RecordingStartingEntry = 0
        self.lastIPTVServicesRes = ''
        self.Channel = ''

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