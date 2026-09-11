from json import loads, dumps
import urllib.error
import urllib.request
import base64
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

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CameraControl': {'Parameters':['Position'], 'Status': {}},
            'FullscreenMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Layout': { 'Status': {}},
            'Page': { 'Status': {}},
            'Power': { 'Status': {}},
            }
                    
        self.reIPaddress = re.compile(r'\d+\.\d+\.\d+\.\d+')

    def SetCameraControl(self, value, qualifier):

        try:
            ip_address = qualifier['IP Address']
            username_val = qualifier['Username']
            password_val = qualifier['Password']
            uri_string = qualifier['Uri']
            port_string = qualifier['Port']
            protocol_type = qualifier['Protocol']
            position_val = qualifier['Position']
        except KeyError:
            self.Error(['SetCameraControl command missing qualifier'])

        if (self.reIPaddress.match(ip_address) and port_string and protocol_type and 1 <= position_val <= 16 and
            username_val and password_val and uri_string):        
            CameraControlCmdString = 'api/v1/cameras/{}'.format(position_val)
            jsonData = dumps({'ipAddress' : ip_address, 'userName' : username_val, 
                              'userPassword' : password_val, 'port' : port_string, 
                              'protocol' : protocol_type, 'uri' : uri_string})
            self.__SetHelper('CameraControl', value, qualifier, CameraControlCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetCameraControl')
    def SetFullscreenMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '{"fullScreen": true}', 
            'Off' : '{"fullScreen": false}'
        }

        FullscreenModeCmdString = 'api/v1/live-view/settings'
        jsonData = ValueStateValues[value]
        self.__SetHelper('FullscreenMode', value, qualifier, FullscreenModeCmdString, jsonData.encode())

    def UpdateFullscreenMode(self, value, qualifier):

        ValueStateValues = {
            True  : 'On', 
            False : 'Off'
        }
        
        LayoutValues = {
            1   : '1', 
            3   : '3', 
            4   : '4', 
            8   : '8', 
            9   : '9', 
            16  : '16', 
            255 : 'Custom'
        }

        FullscreenModeCmdString = 'api/v1/live-view/settings'
        res = self.__UpdateHelper('FullscreenMode', value, qualifier, FullscreenModeCmdString)
        if res:
            try:
                value = ValueStateValues[res['fullScreen']]
                self.WriteStatus('FullscreenMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Fullscreen Mode: Invalid/unexpected response'])
                    
            try:
                value = LayoutValues[res['layout']]
                self.WriteStatus('Layout', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Layout: Invalid/unexpected response'])
                    
            try:
                value = res['page']
                if 1 <= int(value) <= 16:
                    self.WriteStatus('Page', str(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Page: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdateFullscreenMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI Port'      : 'hdmiPort', 
            'Live View'      : 'liveView', 
            'Setting Screen' : 'settingView'
        }

        InputCmdString = 'api/v1/system/state'
        jsonData = dumps({'state':ValueStateValues[value]})
        self.__SetHelper('Input', value, qualifier, InputCmdString, jsonData.encode())

    def SetLayout(self, value, qualifier):

        ValueStateValues = {
            '1'      : 1, 
            '3'      : 3, 
            '4'      : 4, 
            '8'      : 8, 
            '9'      : 9, 
            '16'     : 16, 
            'Custom' : 255
        }
        
        LayoutCmdString = 'api/v1/live-view/settings'
        jsonData = dumps({'layout':ValueStateValues[value]})
        self.__SetHelper('Layout', value, qualifier, LayoutCmdString, jsonData.encode())

    def UpdateLayout(self, value, qualifier):

        self.UpdateFullscreenMode(value, qualifier)

    def SetPage(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PageCmdString = 'api/v1/live-view/settings'
            jsonData = dumps({'page':int(value)})
            self.__SetHelper('Page', value, qualifier, PageCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetPage')

    def UpdatePage(self, value, qualifier):

        self.UpdateFullscreenMode(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'liveView', 
            'Off' : 'quickPowerOff'
        }

        PowerCmdString = 'api/v1/system/state'
        jsonData = dumps({'state':ValueStateValues[value]})
        self.__SetHelper('Power', value, qualifier, PowerCmdString, jsonData.encode())

    def UpdatePower(self, value, qualifier):

        InputValues = {
            'liveView'      : 'Live View', 
            'settingView'   : 'Setting Screen', 
            'hdmiPort'      : 'HDMI Port'
        }

        PowerCmdString = 'api/v1/system/state'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                if res['state'] == 'quickPowerOff':
                    value = 'Off'
                else:
                    value = 'On'
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])
                
            try:
                value = InputValues[res['state']]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, resource, data = None):        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')
        
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

        url = '{0}{1}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers) #method defaults to GET when data is None

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