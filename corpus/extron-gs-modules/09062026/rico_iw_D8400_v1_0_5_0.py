from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import GetUnverifiedContext
from json import loads, dumps
from struct import pack
import urllib.request
import urllib.error
import base64, time


class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port == 443:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'LoginInformation': {'Status': {}},
            'MessageCommand': {'Parameters': ['Icon Type'], 'Status': {}},
            'PageNavigation': {'Status': {}},
            'PageSearchSet': {'Status': {}},
            'PageSearchStatusDisplay': {'Parameters': ['Button'], 'Status': {}},
            'PageSearchStatusPageID': {'Parameters': ['Button'], 'Status': {}},
            'PageSearchStatusPageNumber': {'Parameters': ['Button'], 'Status': {}},
            'PageUpdate': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteMeetingControl': {'Parameters': ['Name'], 'Status': {}},
            'RemoteMeetingNavigation': {'Status': {}},
            'RemoteMeetingSearchSet': {'Status': {}},
            'RemoteMeetingStatus': {'Status': {}},
            'RemoteMeetingStatusIPAddress': {'Parameters': ['Button'], 'Status': {}},
            'RemoteMeetingStatusIWBName': {'Parameters': ['Button'], 'Status': {}},
            'RemoteMeetingUpdate': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}},
            }

        self._NumberofRemoteMeetingSearch = 5
        self._NumberofPageSearch = 5

        self.page_list_Display = Directory(self.NumberofPageSearch, filler='')
        self.page_list_Display.write_status_function = self.WritePageSearchStatusDisplay

        self.page_list_PageID = Directory(self.NumberofPageSearch, filler='')
        self.page_list_PageID.write_status_function = self.WritePageSearchStatusPageID

        self.page_list_PageNumber = Directory(self.NumberofPageSearch, filler='')
        self.page_list_PageNumber.write_status_function = self.WritePageSearchStatusPageNumber

        self.remoteMeeting_list_IPAddress = Directory(self.NumberofRemoteMeetingSearch, filler='')
        self.remoteMeeting_list_IPAddress.write_status_function = self.WriteRemoteMeetingStatusIPAddress

        self.remoteMeeting_list_IWBName = Directory(self.NumberofRemoteMeetingSearch, filler='')
        self.remoteMeeting_list_IWBName.write_status_function = self.WriteRemoteMeetingStatusIWBName

    @property
    def NumberofRemoteMeetingSearch(self):
        return self._NumberofRemoteMeetingSearch

    @NumberofRemoteMeetingSearch.setter
    def NumberofRemoteMeetingSearch(self, value):
        if 1<= int(value) <= 15:
            self._NumberofRemoteMeetingSearch = int(value)
        else:
            print('Invalid NumberofRemoteMeetingSearch range is from 1 to 15')

    @property
    def NumberofPageSearch(self):
        return self._NumberofPageSearch

    @NumberofPageSearch.setter
    def NumberofPageSearch(self, value):
        if 1<= int(value) <= 15:
            self._NumberofPageSearch = int(value)
        else:
            print('Invalid NumberofPageSearch range is from 1 to 15')

    def WritePageSearchStatusDisplay(self,value,qualifier):
        self.WriteStatus('PageSearchStatusDisplay', value, qualifier)

    def WritePageSearchStatusPageID(self,value,qualifier):
        self.WriteStatus('PageSearchStatusPageID', value, qualifier)

    def WritePageSearchStatusPageNumber(self,value,qualifier):
        self.WriteStatus('PageSearchStatusPageNumber', value, qualifier)

    def WriteRemoteMeetingStatusIPAddress(self,value,qualifier):
        self.WriteStatus('RemoteMeetingStatusIPAddress', value, qualifier)

    def WriteRemoteMeetingStatusIWBName(self,value,qualifier):
        self.WriteStatus('RemoteMeetingStatusIWBName', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'mute_on',
            'Off': 'mute_off'
        }

        AudioMuteCmdString = 'api/v2/audios/1'
        jsonData = dumps(
                        {'control': ValueStateValues[value]}
                        )

        self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, jsonData.encode())

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }


        AudioMuteCmdString = '/api/v2/audios'
        res = self.__UpdateHelper('AudioMute', value, qualifier, AudioMuteCmdString)
        if res:
            res = loads(res)
            try:
                value = ValueStateValues[res['audios'][0]['mute']]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

            try:
                value = int(res['audios'][0]['volume'])
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])


    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Whiteboard': '0',  # IWB-WebAPI-V2.3_Reference_en.pdf Page 31
            'HDMI': '1',
            'DisplayPort': '2',
            'VGA': '3',
            'Remote PC': '4'
        }

        InputCmdString = 'api/v2/inputs/{}'.format(ValueStateValues[value])
        jsonData = dumps(
                        {'control': 'select'}
                        )
        self.__SetHelper('Input', value, qualifier, InputCmdString, jsonData.encode())

    def UpdateInput(self, value, qualifier):

        InputCmdString = '/api/v2/inputs'
        res = self.__UpdateHelper('Input', value, qualifier, InputCmdString)
        if res:
            res = loads(res)
            try:
                for i in range(1, 5):
                    if res['inputs'][i - 1]['display'] == 'on':
                        value = res['inputs'][i - 1]['name']
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateLoginInformation(self, value, qualifier):

        LoginInformationCmdString = '/api/v2/users'
        res = self.__UpdateHelper('LoginInformation', value, qualifier, LoginInformationCmdString)
        if res:
            res = loads(res)
            try:
                user_info = res["users"]
                if user_info:
                    name_val = user_info[0]['display_name']
                    user_val = user_info[0]['mail']
                    value = 'Name: {0}\r\nMail Address: {1}'.format(name_val, user_val)
                else:
                    value = 'No Login information'
                self.WriteStatus('LoginInformation', value, qualifier)
            except (TypeError, IndexError, KeyError):
                self.Error(['Login Information: Invalid/unexpected response'])

    def SetMessageCommand(self, value, qualifier):

        IconTypeStates = {
            'Info': 'ticker_info',
            'Warn': 'ticker_warn'
        }

        icon_type = qualifier['Icon Type']
        msg_val = value
        if msg_val and icon_type in IconTypeStates:
            MessageCommandCmdString = 'api/v2/message'
            jsonData = dumps(
                            {'type': IconTypeStates[icon_type], 'message': msg_val}
                            )
            self.__SetHelper('MessageCommand', value, qualifier, MessageCommandCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetMessageCommand')

    def SetPageNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.page_list_Display.scroll_up(1)
            self.page_list_PageID.scroll_up(1)
            self.page_list_PageNumber.scroll_up(1)
        elif value == 'Down':
            self.page_list_Display.scroll_down(1)
            self.page_list_PageID.scroll_down(1)
            self.page_list_PageNumber.scroll_down(1)
        elif value == 'Page Up':
            self.page_list_Display.scroll_up(self.NumberofPageSearch)
            self.page_list_PageID.scroll_up(self.NumberofPageSearch)
            self.page_list_PageNumber.scroll_up(self.NumberofPageSearch)
        elif value == 'Page Down':
            self.page_list_Display.scroll_down(self.NumberofPageSearch)
            self.page_list_PageID.scroll_down(self.NumberofPageSearch)
            self.page_list_PageNumber.scroll_down(self.NumberofPageSearch)
        else:
        	self.Discard('Invalid Command for SetPageNavigation')

    
    def SetPageSelectCommand(self, value, qualifier):
        page_id = value
        if page_id:
            PageSelectCommandCmdString = 'api/v2/pages/{}'.format(page_id)
            jsonData = dumps(
                        {'control' : 'select'}
                        )

            self.__SetHelper('PageSelectCommand', value, qualifier, PageSelectCommandCmdString, jsonData.encode())

    def SetPageSearchSet(self, value, qualifier):
        self.Debug = True

        ValueConstraints = {
            'Min': 1,
            'Max': self.NumberofPageSearch
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            page_id = self.ReadStatus('PageSearchStatusPageID', {'Button': value})
            if page_id not in ['***Not Available***', '*** End of List ***','']:
                PageSelectCommandCmdString = 'api/v2/pages/{}'.format(page_id)
                jsonData = dumps({'control' : 'select'})
                # Sends out the selected Page
                self.__SetHelper('PageSelectCommand', value, qualifier, PageSelectCommandCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetPageSearchSet')


    def SetPageUpdate(self, value, qualifier):
        self.Debug = True

        PageUpdateCmdString = '/api/v2/pages'
        res = self.__UpdateHelper('PageUpdate', value, qualifier, PageUpdateCmdString)
        if res:
            res = loads(res)
            try:
                new_page_data = {'page_number': [], 'display': [], 'id': []}
                for typeVal in ['page_number', 'display', 'id']:
                    new_page_data[typeVal] = self.PageLists(res['pages'], typeVal)
                    new_page_data[typeVal].append('*** End of List ***')
                self.page_list_PageNumber.reset(new_page_data['page_number'])
                self.page_list_Display.reset(new_page_data['display'])
                self.page_list_PageID.reset(new_page_data['id'])
            except (KeyError, IndexError, TypeError):
                self.Error(['Page Update: Invalid/unexpected response'])
        else:
            self.page_list_PageNumber.reset(['***Not Available***'])
            self.page_list_Display.reset(['***Not Available***'])
            self.page_list_PageID.reset(['***Not Available***'])

    def PageLists(self, res, type_):

        tempList = []
        for entry in res:
            try:
                tempList.append(entry[type_].title()) if type_ == 'display' else tempList.append(entry[type_])
            except(KeyError):
                tempList.append('{} Unknown'.format(type_.title()))
        return tempList

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'resume',
            'Off': 'standby'
        }

        PowerCmdString = 'api/v2/system'
        jsonData = dumps(
                        {'control': ValueStateValues[value]}
                        )
        self.__SetHelper('Power', value, qualifier, PowerCmdString, jsonData.encode())

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'up': 'On',
            'local': 'On',
            'hold': 'On',
            'join': 'On',
            'standby': 'Off'
        }

        PowerCmdString = '/api/v2/system'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                res = loads(res)
                value = ValueStateValues[res['status']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRemoteMeetingControl(self, value, qualifier):

        ValueStateValues = {
            'Leave': 'leave',
            'Close': 'close'
        }

        jsonData = ''
        if value == 'Hold':
            jsonData = dumps(
                        {'control': 'hold', 'opt_passcode': "off", "opt_limit_func": "off"}
                        )
        elif value == 'Join':
            host_ip = qualifier['Name']
            if host_ip:
                jsonData = dumps(
                            {'control': 'join', 'host': host_ip}
                            )
        else:
            jsonData = dumps(
                        {'control': ValueStateValues[value]}
                        )
        RemoteMeetingControlCmdString = 'api/v2/remote'
        if jsonData:
            self.__SetHelper('RemoteMeetingControl', value, qualifier, RemoteMeetingControlCmdString, jsonData.encode())

    def SetRemoteMeetingNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.remoteMeeting_list_IPAddress.scroll_up(1)
            self.remoteMeeting_list_IWBName.scroll_up(1)
        elif value == 'Down':
            self.remoteMeeting_list_IPAddress.scroll_down(1)
            self.remoteMeeting_list_IWBName.scroll_down(1)
        elif value == 'Page Up':
            self.remoteMeeting_list_IPAddress.scroll_up(self.NumberofRemoteMeetingSearch)
            self.remoteMeeting_list_IWBName.scroll_up(self.NumberofRemoteMeetingSearch)
        elif value == 'Page Down':
            self.remoteMeeting_list_IPAddress.scroll_down(self.NumberofRemoteMeetingSearch)
            self.remoteMeeting_list_IWBName.scroll_down(self.NumberofRemoteMeetingSearch)
        else:
        	self.Discard('Invalid Command for SetRemoteMeetingNavigation')

    def SetRemoteMeetingSearchSet(self, value, qualifier):
        self.Debug = True

        ValueConstraints = {
            'Min': 1,
            'Max': self.NumberofRemoteMeetingSearch
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            remoteMeeting_IPAddr = self.ReadStatus('RemoteMeetingStatusIPAddress', {'Button': value})
            if remoteMeeting_IPAddr not in ['***Not Available***', '*** End of List ***']:
                self.SetRemoteMeetingControl('Join',{'Name':remoteMeeting_IPAddr})
        else:
            self.Discard('Invalid Command for SetRemoteMeetingSearchSet')

    def SetRemoteMeetingUpdate(self, value, qualifier):
        self.Debug = True

        ValueStateValues = {
            'ready': 'Ready',
            'not_ready': 'Not Ready',
            'hold': 'Hold',
            'holding': 'Holding',
            'join': 'Join',
            'joining': 'Joining',
            'closing': 'Closing',
            'leaving': 'Leaving'
        }

        RemoteMeetingUpdateCmdString = '/api/v2/remote'
        res = self.__UpdateHelper('PageUpdate', value, qualifier, RemoteMeetingUpdateCmdString)
        if res:
            res = loads(res)
            try:

                new_remote_data = {'ip_address': [], 'name': []}
                for typeVal in ['ip_address', 'name']:
                    new_remote_data[typeVal] = self.RemoteLists(res['iwb_list'], typeVal)
                    new_remote_data[typeVal].append('*** End of List ***')
                self.remoteMeeting_list_IPAddress.reset(new_remote_data['ip_address'])
                self.remoteMeeting_list_IWBName.reset(new_remote_data['name'])
            except (KeyError, IndexError, TypeError):
                self.Error(['Remote Meeting Update: Invalid/unexpected response'])

            try:
                value = ValueStateValues[res['status']]
                self.WriteStatus('RemoteMeetingStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Remote Meeting Status: Invalid/unexpected response'])
        else:
            self.remoteMeeting_list_IPAddress.reset(['***Not Available***'])
            self.remoteMeeting_list_IWBName.reset(['***Not Available***'])

    def RemoteLists(self, res, type_):

        tempList = []
        for entry in res:
            try:
                tempList.append(entry[type_])
            except(KeyError):
                tempList.append('{} Unknown'.format(type_.title()))
        return tempList

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'volume_up',
            'Down': 'volume_down'
        }

        VolumeCmdString = 'api/v2/audios/1'
        jsonData = dumps(
                        {'control': ValueStateValues[value]}
                        )
        self.__SetHelper('Volume', value, qualifier, VolumeCmdString, jsonData.encode())

    def UpdateVolumeStatus(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=10)
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

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=data, headers=headers)  # method defaults to GET when data is None
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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


def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res
    return wrapper


class Directory:

    def __init__(self, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Button'
        self._qualifier_type = 'Number'

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
            self.write_status_function(self.entry_function(entry[0]), {self.qualifier_name: position_value})

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
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1


class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoSearch': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'PowerSave': {'Status': {}},
            'Speaker': {'Status': {}},
            'TouchControlMode': {'Status': {}},
            'TouchControlSetting': {'Status': {}},
            'TouchFeature': {'Status': {}},
            'Volume': {'Status': {}},
            }
        self._DeviceID = b'01'

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcasst':
            self._DeviceID = b'99'
        elif 1<= int(value) <= 98:
            self._DeviceID = value.zfill(2).encode()


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'000',
            '4:3': b'001',
            'Wide Zoom': b'002'
        }

        AspectRatioCmdString = b''.join([b'8', self._DeviceID, b's\x31', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Full',
            b'1': '4:3',
            b'2': 'Wide Zoom'
        }

        AspectRatioCmdString = b''.join([b'8', self._DeviceID, b'g\x77000\x0D'])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000'
        }

        AudioMuteCmdString = b''.join([b'8', self._DeviceID, b's\x36', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        AudioMuteCmdString = b''.join([b'8', self._DeviceID, b'g\x67000\x0D'])
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b''.join([b'8', self._DeviceID, b's\x8F000\x0D'])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSearch(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000'
        }

        AutoSearchCmdString = b''.join([b'8', self._DeviceID, b's\x96', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('AutoSearch', AutoSearchCmdString, value, qualifier)

    def UpdateAutoSearch(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        AutoSearchCmdString = b''.join([b'8', self._DeviceID, b'g\xC6000\x0D'])
        res = self.__UpdateHelper('AutoSearch', AutoSearchCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AutoSearch', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Search: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'000',
            'HDMI 1': b'001',
            'HDMI 2/OPS': b'002',
            'DVI 1': b'006',
            'DisplayPort': b'007',
            'DVI 2': b'012'
        }

        InputCmdString = b''.join([b'8', self._DeviceID, b's\x22', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'00': 'VGA',
            b'01': 'HDMI 1',
            b'02': 'HDMI 2/OPS',
            b'06': 'DVI 1',
            b'07': 'DisplayPort',
            b'12': 'DVI 2',

        }

        InputCmdString = b''.join([b'8', self._DeviceID, b'g\x6A000\x0D'])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000'
        }

        OnScreenDisplayCmdString = b''.join([b'8', self._DeviceID, b's\x5B', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        OnScreenDisplayCmdString = b''.join([b'8', self._DeviceID, b'g\x5D000\x0D'])
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'000',
            'Vivid': b'001',
            'Cinema': b'002',
            'Custom': b'003',
            'Low Blue Light': b'004'
        }

        PictureModeCmdString = b''.join([b'8', self._DeviceID, b's\x81', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Standard',
            b'1': 'Vivid',
            b'2': 'Cinema',
            b'3': 'Custom',
            b'4': 'Low Blue Light'
        }

        PictureModeCmdString = b''.join([b'8', self._DeviceID, b'g\xB1000\x0D'])
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'000',
            'HDMI 1': b'001',
            'HDMI 2/OPS': b'002',
            'DVI 1': b'006',
            'DisplayPort': b'007',
            'DVI 2': b'012'
        }

        PIPInputCmdString = b''.join([b'8', self._DeviceID, b's\x8B', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            b'00': 'VGA',
            b'01': 'HDMI 1',
            b'02': 'HDMI 2/OPS',
            b'06': 'DVI 1',
            b'07': 'DisplayPort',
            b'12': 'DVI 2'
        }

        PIPInputCmdString = b''.join([b'8', self._DeviceID, b'g\xBB000\x0D'])
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000',
            'PBP': b'002'
        }

        PIPModeCmdString = b''.join([b'8', self._DeviceID, b's\x8A', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'PBP'
        }

        PIPModeCmdString = b''.join([b'8', self._DeviceID, b'g\xBA000\x0D'])
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left': b'000',
            'Upper Right': b'001',
            'Lower Left': b'002',
            'Lower Right': b'003'
        }

        PIPPositionCmdString = b''.join([b'8', self._DeviceID, b's\x8E', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Upper Left',
            b'1': 'Upper Right',
            b'2': 'Lower Left',
            b'3': 'Lower Right'
        }

        PIPPositionCmdString = b''.join([b'8', self._DeviceID, b'g\xBF000\x0D'])
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': b'000',
            'Large': b'001'
        }

        PIPSizeCmdString = b''.join([b'8', self._DeviceID, b's\x8D', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Small',
            b'1': 'Large'
        }

        PIPSizeCmdString = b''.join([b'8', self._DeviceID, b'g\xBD000\x0D'])
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b''.join([b'8', self._DeviceID, b's\x8C000\x0D'])
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000'
        }

        PowerCmdString = b''.join([b'8', self._DeviceID, b's\x21', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'Standby'
        }

        PowerCmdString = b''.join([b'8', self._DeviceID, b'g\x6C000\x0D'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerSave(self, value, qualifier):

        ValueStateValues = {
            'Off': b'000',
            'Low': b'001',
            'High': b'002'
        }

        PowerSaveCmdString = b''.join([b'8', self._DeviceID, b's\xA9', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('PowerSave', PowerSaveCmdString, value, qualifier)

    def UpdatePowerSave(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Off',
            b'1': 'Low',
            b'2': 'High'
        }

        PowerSaveCmdString = b''.join([b'8', self._DeviceID, b'g\xD9000\x0D'])
        res = self.__UpdateHelper('PowerSave', PowerSaveCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('PowerSave', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Save: Invalid/unexpected response'])

    def SetSpeaker(self, value, qualifier):

        ValueStateValues = {
            'Internal': b'000',
            'External': b'001'
        }

        SpeakerCmdString = b''.join([b'8', self._DeviceID, b's\x89', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('Speaker', SpeakerCmdString, value, qualifier)

    def UpdateSpeaker(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Internal',
            b'1': 'External'
        }

        SpeakerCmdString = b''.join([b'8', self._DeviceID, b'g\xB9000\x0D'])
        res = self.__UpdateHelper('Speaker', SpeakerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('Speaker', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Speaker: Invalid/unexpected response'])

    def SetTouchControlMode(self, value, qualifier):

        ValueStateValues = {
            'Old': b'000',
            'New': b'001'
        }

        TouchControlModeCmdString = b''.join([b'8', self._DeviceID, b's\xEC', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('TouchControlMode', TouchControlModeCmdString, value, qualifier)

    def UpdateTouchControlMode(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Old',
            b'1': 'New'
        }

        TouchControlModeCmdString = b''.join([b'8', self._DeviceID, b'g\xEC000\x0D'])
        res = self.__UpdateHelper('TouchControlMode', TouchControlModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('TouchControlMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Control Mode: Invalid/unexpected response'])

    def SetTouchControlSetting(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'000',
            'Computer In': b'001',
            'USB': b'002'
        }

        TouchControlSettingCmdString = b''.join([b'8', self._DeviceID, b's\xEB', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('TouchControlSetting', TouchControlSettingCmdString, value, qualifier)

    def UpdateTouchControlSetting(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Auto',
            b'1': 'Computer In',
            b'2': 'USB'
        }

        TouchControlSettingCmdString = b''.join([b'8', self._DeviceID, b'g\xEB000\x0D'])
        res = self.__UpdateHelper('TouchControlSetting', TouchControlSettingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('TouchControlSetting', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Control Setting: Invalid/unexpected response'])

    def SetTouchFeature(self, value, qualifier):

        ValueStateValues = {
            'On': b'001',
            'Off': b'000'
        }

        TouchFeatureCmdString = b''.join([b'8', self._DeviceID, b's\x9E', ValueStateValues[value], b'\x0D'])
        self.__SetHelper('TouchFeature', TouchFeatureCmdString, value, qualifier)

    def UpdateTouchFeature(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        TouchFeatureCmdString = b''.join([b'8', self._DeviceID, b'g\x9E000\x0D'])
        res = self.__UpdateHelper('TouchFeature', TouchFeatureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('TouchFeature', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Feature: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join([b'8', self._DeviceID, b's\x35', str(value).zfill(3).encode(), b'\x0D'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b''.join([b'8', self._DeviceID, b'g\x66000\x0D'])
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[3:4] == b'-':
                self.Error(['{0}: Invalid Command Response.'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == b'99':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'99':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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
