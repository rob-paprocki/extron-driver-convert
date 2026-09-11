from extronlib.system import GetUnverifiedContext
import re
import base64
import urllib.error
import urllib.request

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Debug = False
        self.IPAddress = ipAddress
        self.port = port
        self.Models = {}
        self.Subscription = {}
        self._NumberofListEntriesShown = 5
        self.Username = deviceUsername

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

        self.Commands = {
            'AvailableTwilioPhoneNumberSelected': {'Parameters':['Data Type'], 'Status': {}},
            'AvailableTwilioPhoneNumbersEntrySelect': {'Parameters':['Position'], 'Status': {}},
            'AvailableTwilioPhoneNumbersEntryStatus': {'Parameters':['Position'], 'Status': {}},
            'AvailableTwilioPhoneNumbersNavigation': { 'Status': {}},
            'AvailableTwilioPhoneNumbersRefresh': { 'Status': {}},
            'MakePhoneCallApp': {'Status': {}},
            'MakePhoneCallURL': {'Status': {}},
            'OutgoingCallerIDEntrySelect': {'Parameters':['Position'], 'Status': {}},
            'OutgoingCallerIDEntryStatus': {'Parameters':['Position'], 'Status': {}},
            'OutgoingCallerIDNavigation': { 'Status': {}},
            'OutgoingCallerIDRefresh': { 'Status': {}},
            'OutgoingCallerIDSelected': { 'Status': {}},
            'OutgoingPhoneNumberSelected': {'Status': {}},
            'SendSMSMessage': { 'Status': {}},
            'SMSMessageString': { 'Status': {}},
        }
        
        self.twilioNumbers = Directory(self._NumberofListEntriesShown, filler='')
        self.twilioNumbers.write_status_function = self.WriteAvailableTwilioPhoneNumbersEntryStatus
        self.outCallerIDs = Directory(self._NumberofListEntriesShown, filler='')
        self.outCallerIDs.write_status_function = self.WriteOutgoingCallerIDEntryStatus

        self.nameSearch = re.compile('<FriendlyName>(.*)</FriendlyName>')
        self.numberSearch = re.compile('<PhoneNumber>(\+\d+)</PhoneNumber>')

    @property
    def NumberofListEntriesShown(self):
        return self._NumberofListEntriesShown

    @NumberofListEntriesShown.setter
    def NumberofListEntriesShown(self, value):
        self._NumberofListEntriesShown= value

    def SetAvailableTwilioPhoneNumbersEntrySelect(self, value, qualifier):
        self.Debug = True

        if 1 <= int(qualifier['Position']) <= self._NumberofListEntriesShown:
            entry = self.ReadStatus('AvailableTwilioPhoneNumbersEntryStatus', qualifier)
            if entry:
                name = entry.split(':')[0].strip()
                self.WriteStatus('AvailableTwilioPhoneNumberSelected', name, {'Data Type':'Name'})
                phoneNum = entry.split(':')[1].strip()
                self.WriteStatus('AvailableTwilioPhoneNumberSelected', name, {'Data Type':'Number'})
        else:
            self.Discard('Invalid Command for SetAvailableTwilioPhoneNumbersEntrySelect')

    def SetAvailableTwilioPhoneNumbersNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.twilioNumbers.scroll_up(1)
        elif value == 'Down':
            self.twilioNumbers.scroll_down(1)
        elif value == 'Page Up':
            self.twilioNumbers.scroll_up(self._NumberofListEntriesShown)
        elif value == 'Page Down':
            self.twilioNumbers.scroll_down(self._NumberofListEntriesShown)
        else:
            self.Discard('Invalid Command for SetAvailableTwilioPhoneNumbersNavigation')

    def WriteAvailableTwilioPhoneNumbersEntryStatus(self,value,qualifier):
        self.WriteStatus('AvailableTwilioPhoneNumbersEntryStatus', value, qualifier)

    def SetAvailableTwilioPhoneNumbersRefresh(self, value, qualifier):
        self.Debug = True

        res = self.__UpdateHelper('AvailableTwilioPhoneNumbersRefresh', value, qualifier, 'IncomingPhoneNumbers')
        if res:
            nameList = self.nameSearch.findall(res)
            numberList = self.numberSearch.findall(res)
            new_directory_data = ['{0} : {1}'.format(entry[0], entry[1]) for entry in zip(nameList, numberList)]
            new_directory_data.append('*** End of List ***')
            self.twilioNumbers.reset(new_directory_data)
        else:
            self.twilioNumbers.reset(['*** Not Available ***'])

    def SetMakePhoneCallApp(self, value, qualifier):

        app_sid = qualifier['Application Sid']
        to_number = qualifier['To Number']
        from_number = qualifier['From Number']
        data = 'To={0}&From={1}&Sid={2}'.format(to_number, from_number, app_sid)
        self.__SetHelper('MakePhoneCallApp', value, qualifier, 'Calls', data)

    def SetMakePhoneCallURL(self, value, qualifier):

        url_string = qualifier['URL']
        to_number = qualifier['To Number']
        from_number = qualifier['From Number']
        data = 'To={0}&From={1}&Url={2}'.format(to_number, from_number, url_string)
        self.__SetHelper('MakePhoneCallURL', value, qualifier, 'Calls', data)

    def SetOutgoingCallerIDEntrySelect(self, value, qualifier):
        self.Debug = True
        
        if 1 <= int(qualifier['Position']) <= self._NumberofListEntriesShown:
            entry = self.ReadStatus('OutgoingCallerIDEntryStatus', qualifier)
            if entry:
                name = entry.split(':')[0].strip()
                self.WriteStatus('OutgoingCallerIDSelected', name, None)
                phoneNum = entry.split(':')[1].strip()
                self.WriteStatus('OutgoingPhoneNumberSelected', name, None)
        else:
            self.Discard('Invalid Command for SetOutgoingCallerIDEntrySelect')

    def SetOutgoingCallerIDNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.outCallerIDs.scroll_up(1)
        elif value == 'Down':
            self.outCallerIDs.scroll_down(1)
        elif value == 'Page Up':
            self.outCallerIDs.scroll_up(self._NumberofListEntriesShown)
        elif value == 'Page Down':
            self.outCallerIDs.scroll_down(self._NumberofListEntriesShown)
        else:
            self.Discard('Invalid Command for SetOutgoingCallerIDNavigation')

    def WriteOutgoingCallerIDEntryStatus(self, value, qualifier):
        self.WriteStatus('OutgoingCallerIDEntryStatus', value, qualifier)

    def SetOutgoingCallerIDRefresh(self, value, qualifier):
        self.Debug = True

        res = self.__UpdateHelper('OutgoingCallerIDRefresh', value, qualifier, 'OutgoingCallerIds')
        if res:
            nameList = self.nameSearch.findall(res)
            numberList = self.numberSearch.findall(res)
            
            new_directory_data = ['{0} : {1}'.format(entry[0], entry[1]) for entry in zip(nameList, numberList)]
            new_directory_data.append('*** End of List ***')
            self.outCallerIDs.reset(new_directory_data)
        else:
            self.outCallerIDs.reset(['*** Not Available ***'])

    def SetSendSMSMessage(self, value, qualifier):

        sms_message = qualifier['Message']
        to_number = qualifier['To Number']
        from_number = qualifier['From Number']

        data = 'To={0}&From={1}&Body={2}'.format(to_number, from_number, sms_message)
        self.__SetHelper('SendSMSMessage', value, qualifier, 'Calls', data)

    def __CheckResponseForErrors(self, sourceCmdName, response):
    
        return response.read().decode()    

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}2010-04-01/Accounts/{1}/{2}'.format(self.RootURL, self.Username, url)
        data = data.encode(encoding='iso-8859-1')
        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request) # open() returns a http.client.HTTPResponse object if successful            
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
        """Update Helper
        This function is used to determine how to send.

        """

        url = '{0}2010-04-01/Accounts/{1}/{2}'.format(self.RootURL, self.Username, url)
        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        
        # Create Request object
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        try:
            res = self.Opener.open(my_request) # open() returns a http.client.HTTPResponse object if successful            
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
                    except BaseException:
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
                    except BaseException:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
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
        except BaseException:
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
        except BaseException:
            return None

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
    def __init__(self, ipAddress, port=443, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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

    def __init__(self, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
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
            self.write_status_function(self.entry_function(entry[0]), {self.qualifier_name : position_value})

    def write_status_function(self, value, qualifier):
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