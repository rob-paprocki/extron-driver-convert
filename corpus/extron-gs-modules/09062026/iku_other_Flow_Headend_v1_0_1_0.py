import urllib.error
import urllib.request
import base64
from json import loads,dumps
import re

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

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Mute': {'Parameters':['Device ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'ServiceIDStatus': {'Parameters':['Device ID'], 'Status': {}},
            'ServiceListResult': {'Parameters':['Button','Details Type'], 'Status': {}},
            'ServiceListNavigation': { 'Status': {}},
            'ServiceListSearch': { 'Status': {}},
            'ServiceListSelect': {'Parameters':['Button','Device ID','Details Type'], 'Status': {}},            
            }

        self.NumberofServices = 0
        self.NumberOfButton = 0
        self.ServiceNameList = []
        self.ServiceIDList = []
        self.ServiceListNav = True
        self._NumberofServicesSearch = '5'
        
    @property
    def NumberofServicesSearch(self):
        return self._NumberofServicesSearch
        

    @NumberofServicesSearch.setter
    def NumberofServicesSearch(self, value):
        if 1 <= int(value) <= 10:
            self.NumberOfButton = int(value)

    def Aunthentication(self, value, qualifier):
        AunthenticationCmdString = '/flow/api/auth/users/{}/login'.format(self.deviceUsername)
        data = dumps({'name': self.deviceUsername,'password': self.devicePassword})
        self.__SetHelper('Aunthentication', value, qualifier, AunthenticationCmdString, data.encode())

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : True, 
            'Off' : False
        }

        deviceID = int(qualifier['Device ID'])
        if 1 <= deviceID <= 100:
            MuteCmdString = '/devicemanager/api/commands' 
            jsonData = dumps({
                                'type': 'COMMAND_TYPE_SET_MUTE',
                                'deviceGroupIds': [],
                                'deviceIds': [deviceID],
                                'mute': ValueStateValues[value]
                              })
            self.__SetHelper('Mute', value, qualifier, MuteCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : True, 
            'Off' : False
        }

        deviceID = int(qualifier['Device ID'])
        if 1 <= deviceID <= 100:
            PowerCmdString = '/devicemanager/api/commands' 
            jsonData = dumps({
                                'type': 'COMMAND_TYPE_SET_POWER',
                                'deviceGroupIds': [],
                                'deviceIds': [deviceID],
                                'state': ValueStateValues[value]
                              })
            self.__SetHelper('Power', value, qualifier, PowerCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            True : 'On', 
            False : 'Off'
        }

        deviceID = int(qualifier['Device ID'])
        if 1 <= deviceID <= 100:
            PowerCmdString = '/devicemanager/api/devices/{}'.format(deviceID)
            res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
            if res:
                try:
                    powerstate = ValueStateValues[res['stb']['powerState']]
                    self.WriteStatus('Power', powerstate, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power : Invalid/unexpected response'])
                try:
                    mutestate = ValueStateValues[res['stb']['muted']]
                    self.WriteStatus('Mute', mutestate, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute : Invalid/unexpected response'])
                try:
                    serviceID = res['stb']['serviceId']
                    self.WriteStatus('ServiceIDStatus', serviceID, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Service ID Status : Invalid/unexpected response'])                                                
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetServiceListNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value and self.ServiceListNav:
                self.MinLabel += NumberOfAdvance
                self.MaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.MinLabel -= NumberOfAdvance
                self.MaxLabel -= NumberOfAdvance
            if self.MinLabel < 1:
                self.MinLabel = 1
            if self.MaxLabel < self.NumberOfButton:
                self.MaxLabel = self.NumberOfButton

            self.SetServiceListWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetServiceListNavigation')
    def SetServiceListSearch(self, value, qualifier):

        ServiceListSearchCmdString = '/devicemanager/api/services'
        res = self.__UpdateHelper('ServiceListSearch', value, qualifier, ServiceListSearchCmdString)
        if res:  
            self.NumberofServices = len(res)
            for i in range(0,self.NumberofServices):
                self.ServiceNameList.append(res[i]['name'])
                self.ServiceIDList.append(res[i]['ipAddress'])
            self.MinLabel = 1
            self.MaxLabel = self.NumberOfButton         
            self.SetServiceListWriteHandler(value, qualifier)

    def SetServiceListWriteHandler(self, value, qualifier):
        self.ServiceListNav = True
        button = 1
        for i in range(self.MinLabel,self.MaxLabel + 1): # populate up to max labels configured
            if i < self.NumberofServices+1:
                self.WriteStatus('ServiceListResult', self.ServiceNameList[i-1], {'Button':str(button), 'Details Type' : 'Service Name'})
                self.WriteStatus('ServiceListResult', self.ServiceIDList[i-1], {'Button':str(button), 'Details Type' : 'Service ID'})
                button += 1

        if button <= self.NumberOfButton:             # Show End of List
            self.WriteStatus('ServiceListResult', '*End of list*', {'Button':str(button), 'Details Type' : 'Service Name'})
            self.WriteStatus('ServiceListResult', '*End of list*', {'Button':str(button), 'Details Type' : 'Service ID'})
            button += 1
            for i in range(button, int(self.NumberOfButton) + 1):
                self.WriteStatus('ServiceListResult', '', {'Button':str(i), 'Details Type' : 'Service Name'})
                self.WriteStatus('ServiceListResult', '', {'Button':str(i), 'Details Type' : 'Service ID'}) 
            self.ServiceListNav = False       

    def SetServiceListSelect(self, value, qualifier):
        ButtonStates = {str(a): str(a) for a in range(1, 11)}
        deviceID = int(qualifier['Device ID'])
        if 1 <= deviceID <= 100:
            ServiceID = self.ReadStatus('ServiceListResult', {'Button':ButtonStates[qualifier['Button']], 'Details Type' : 'Service ID'})
            SetServiceIDCmdString = '/devicemanager/api/commands'
            jsonData = dumps({
                                'type': 'COMMAND_TYPE_SET_SERVICE',
                                'deviceGroupIds': [],
                                'deviceIds': [deviceID],
                                'serviceId': ServiceID
                              })
            self.__SetHelper('SetServiceID', value, qualifier, SetServiceIDCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetServiceListSelect')   
                       
    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True
        ipadd = re.search('http://(\S+):[0-9]+/',self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=10)           
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

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        ipadd = re.search('http://(\S+):[0-9]+/',self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers) #method defaults to GET when data is None

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful  
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        
        return res            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Aunthentication(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        except:
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