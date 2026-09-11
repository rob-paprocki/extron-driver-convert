from extronlib.system import GetUnverifiedContext
import base64
import re
from random import SystemRandom
import string
import urllib.error
import urllib.request

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
            
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
            
        if port == 443:
            self.RootURL = 'https://{}:{}/'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:
            self.RootURL = 'http://{}:{}/'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AdHocRadioInformationGetStatus': {'Parameters':['Name'], 'Status': {}},
            'AdHocRadioInformationSetCommand': { 'Status': {}},
            'AdHocTableInformationGetStatus': {'Parameters':['Name'], 'Status': {}},
            'AdHocTableInformationSetCommand': { 'Status': {}},
            'AdHocTextInformationGetStatus': {'Parameters':['Text', 'Name'], 'Status': {}},
            'AdHocTextInformationSetCommand': { 'Status': {}},
            'AdHocTVInformationGetStatus': {'Parameters':['Name'], 'Status': {}},
            'AdHocTVInformationSetCommand': { 'Status': {}},
            'AdvanceCommand': { 'Status': {}},
            'CheckingCapabilities': { 'Status': {}},
            'PlayerLocalInformationGetStatus': {'Parameters':['Name'], 'Status': {}},
            'PlayerLocalInformationSetCommand': { 'Status': {}},
            'ScheduleOverrideCommand': { 'Status': {}},
            }

        self.RadioInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.AdhocTextInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.AdhocTableInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.AdhocTvInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.AdvanceInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.CheckCapaid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))
        self.PlayerLocalInfoid = ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(22))     
        
        self.UpdateAdhocRadio = re.compile('<choice selected="yes">(.*?)</choice>')
        self.UpdateAdhocText = re.compile('<data_text_[plainrch]{4,5} item_name=".*?">(.*?)</data_text_[plainrch]{4,5}>')
        self.UpdateAdhocTable = re.compile('<data_table item_name=".*?">([\s\S]+)</data_table>')
        self.SetAdhoc_list = re.compile('Row: ?(\d+?), ?Cell: ?([A-Za-z\d]+), ?Data: ?([\s\S]+)')
        self.UpdateAdhocTV = re.compile('<choice selected="yes">(.*?)</choice>')
        self.UpdateCheckCap = re.compile('<capability name="(.*?)"/>')
        self.UpdatePlayerInfo = re.compile('<value>(.*?)</value>')

    def UpdateAdHocRadioInformationGetStatus(self, value, qualifier):

        AdHocRadioInformationGetCommandCmdString = '/XML2'
        name_string = qualifier['Name']
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
            '<command_list><get_ad_hoc_item_info command_id="{0}" item_name="{1}"/></command_list>'.format(self.RadioInfoid, name_string)

        res = self.__UpdateHelper('AdHocRadioInformationGetStatus', value, qualifier, AdHocRadioInformationGetCommandCmdString, data.encode())
        if res:
            try:
                value = re.findall(self.UpdateAdhocRadio, res)[0]
                self.WriteStatus('AdHocRadioInformationGetStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Get Ad Hoc Radio Information: Invalid/unexpected response'])

    def SetAdHocRadioInformationSetCommand(self, value, qualifier):

        data_string = qualifier['Data']
        name_string = qualifier['Name']
        if data_string and name_string:
            AdHocRadioInformationSetCommandCmdString = '/XML2'
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'\
                '<command_list><set_ad_hoc_item_info command_id="{0}" item_name="{1}">'\
                '<data_radio>{2}</data_radio></set_ad_hoc_item_info></command_list>'.format(self.RadioInfoid, name_string, data_string)                                                 
            self.__SetHelper('AdHocRadioInformationSetCommand', value, qualifier, AdHocRadioInformationSetCommandCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetAdHocRadioInformationSetCommand')

    def UpdateAdHocTableInformationGetStatus(self, value, qualifier):

        AdHocTableInformationGetCommandCmdString = '/XML2'
        name_string = qualifier['Name']
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                '<command_list><get_ad_hoc_item_info command_id="{0}" item_name="{1}"/></command_list>'.format(self.AdhocTableInfoid, name_string)
        res = self.__UpdateHelper('AdHocTableInformationGetStatus', value, qualifier, AdHocTableInformationGetCommandCmdString, data.encode())
        if res:
            try:
                value = re.findall(self.UpdateAdhocTable, res)[0].split('\n')
                self.WriteStatus('AdHocTableInformationGetStatus', '\n'.join(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Get Ad Hoc Table Information: Invalid/unexpected response'])

    def SetAdHocTableInformationSetCommand(self, value, qualifier):

        table_string = qualifier['Table']
        name_string = qualifier['Name']
        if table_string and name_string:
            data_string = re.findall(self.SetAdhoc_list, table_string)
            data_value = ''.join(['<row row_id="',data_string[0][0],'"><cell col_id="',data_string[0][1],'">',data_string[0][2],'</cell></row>'])
                
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                    '<command_list><set_ad_hoc_item_info command_id="{0}" item_name="{1}"><data_table>{2}</data_table>' \
                    '</set_ad_hoc_item_info></command_list>'.format(self.AdhocTableInfoid, name_string, data_value) 
            
            AdHocTableInformationSetCommandCmdString = '/XML2'
            self.__SetHelper('AdHocTableInformationSetCommand', value, qualifier, AdHocTableInformationSetCommandCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetAdHocTableInformationSetCommand')

    def UpdateAdHocTextInformationGetStatus(self, value, qualifier):

        text = qualifier['Text']
        name_string = qualifier['Name']
        if text in ['Plain', 'Rich'] and name_string:
            AdHocTextInformationGetCommandCmdString = '/XML2'
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                '<command_list><get_ad_hoc_item_info command_id="{0}" item_name="{1}"/></command_list>'.format(self.AdhocTextInfoid, name_string)
            res = self.__UpdateHelper('AdHocTextInformationGetStatus', value, qualifier, AdHocTextInformationGetCommandCmdString, data.encode())
            if res:
                try:
                    value = re.findall(self.UpdateAdhocText,res)[0]
                    self.WriteStatus('AdHocTextInformationGetStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Get Ad Hoc Text Information: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetAdHocTextInformationGetCommand')

    def SetAdHocTextInformationSetCommand(self, value, qualifier):

        TextStates = {
            'Plain' : 'plain', 
            'Rich' : 'rich'
        }
        text = qualifier['Text']
        data_string = qualifier['Data']
        name_string = qualifier['Name']
        if text in TextStates and data_string and name_string:
            AdHocTextInformationSetCommandCmdString = '/XML2'
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                    '<command_list><set_ad_hoc_item_info command_id="{0}" item_name="{1}">' \
                    '<data_text_{3}>{2}</data_text_{3}></set_ad_hoc_item_info></command_list>'.format(self.AdhocTextInfoid, name_string, data_string, TextStates[text])    
            self.__SetHelper('AdHocTextInformationSetCommand', value, qualifier, AdHocTextInformationSetCommandCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetAdHocTextInformationSetCommand')

    def UpdateAdHocTVInformationGetStatus(self, value, qualifier):

        AdHocTVInformationGetCommandCmdString = '/XML2'
        name_string = qualifier['Name']
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'\
            '<command_list><get_ad_hoc_item_info command_id="{0}" item_name="{1}"/></command_list>'.format(self.AdhocTvInfoid, name_string)
        res = self.__UpdateHelper('AdHocTVInformationGetStatus', value, qualifier, AdHocTVInformationGetCommandCmdString, data.encode())
        if res:
            try:
                value = re.findall(self.UpdateAdhocTV,res)[0]
                self.WriteStatus('AdHocTVInformationGetStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Get Ad Hoc TV Information: Invalid/unexpected response'])

    def SetAdHocTVInformationSetCommand(self, value, qualifier):

        data_string = qualifier['Data']
        name_string = qualifier['Name']
        if data_string and name_string:
            AdHocTVInformationSetCommandCmdString = '/XML2'
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                        '<command_list><set_ad_hoc_item_info command_id="{0}" item_name="{1}">' \
                        '<data_tv><choice>{2}</choice></data_tv></set_ad_hoc_item_info></command_list>'.format(self.AdhocTvInfoid, name_string, data_string)                         
            self.__SetHelper('AdHocTVInformationSetCommand', value, qualifier, AdHocTVInformationSetCommandCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetAdHocTVInformationSetCommand')

    def SetAdvanceCommand(self, value, qualifier):

        AdvanceCommandCmdString = '/XML2'
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                    '<command_list><advance_to rendezvous_name="{0}" command_id="{1}"/></command_list>'.format(value, self.AdvanceInfoid)
        self.__SetHelper('AdvanceCommand', value, qualifier, AdvanceCommandCmdString, data.encode())

    def UpdateCheckingCapabilities(self, value, qualifier):

        CheckingCapabilitiesCmdString = '/XML2'
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                                        '<command_list><get_all_capabilities command_id="{0}"/></command_list>'.format(self.CheckCapaid)
        res = self.__UpdateHelper('CheckingCapabilities', value, qualifier, CheckingCapabilitiesCmdString, data.encode())
        
        if res:
            try:
                value = re.findall(self.UpdateCheckCap,res)
                self.WriteStatus('CheckingCapabilities', '\n\n'.join(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Checking Capabilities: Invalid/unexpected response'])

    def UpdatePlayerLocalInformationGetStatus(self, value, qualifier):

        PlayerLocalInformationGetCommandCmdString = '/XML2'
        name_string = qualifier['Name']
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                '<command_list><get_player_local_info command_id="{0}" name="{1}" /></command_list>'.format(self.PlayerLocalInfoid, name_string)
        res = self.__UpdateHelper('PlayerLocalInformationGetStatus', value, qualifier, PlayerLocalInformationGetCommandCmdString, data.encode())
        if res:
            try:
                value = re.findall(self.UpdatePlayerInfo,res)
                self.WriteStatus('PlayerLocalInformationGetStatus', '\n'.join(value), qualifier)
            except (KeyError, IndexError):
                self.Error(['Get Player Local Information: Invalid/unexpected response'])

    def SetPlayerLocalInformationSetCommand(self, value, qualifier):

        value_string = qualifier['Data']
        name_string = qualifier['Name']
        if value_string and name_string:
            value_string = value_string.split()
            data_string = ''
            for val_str in value_string:
                tempString = ''.join(['<value>',val_str,'</value>'])
                data_string = data_string + tempString
            PlayerLocalInformationSetCommandCmdString = '/XML2'
            data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                    '<command_list><set_player_local_info command_id="{0}" name="{1}">' \
                    '<data_player_local_info>{2}</data_player_local_info></set_player_local_info></command_list>'.format(self.PlayerLocalInfoid, name_string, data_string)                
            self.__SetHelper('PlayerLocalInformationSetCommand', value, qualifier, PlayerLocalInformationSetCommandCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetPlayerLocalInformationSetCommand')

    def SetScheduleOverrideCommand(self, value, qualifier):

        ScheduleOverrideCommandCmdString = 'XML'
        data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
            '<activate_schedule href="file:control/channel/active/schedule/override/{0}.xml"/>'.format(value)
        self.__SetHelper('ScheduleOverrideCommand', value, qualifier, ScheduleOverrideCommandCmdString, data.encode())

    def __CheckResponseForErrors(self, sourceCmdName, res):

        res = res.read().decode()
        return res      

    def __SetHelper(self, command, value, qualifier, resource, data = None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'text/xml'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            res = self.Opener.open(my_request)      
                        
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
        
    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'text/xml'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST') #method defaults to GET when data is None

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
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
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