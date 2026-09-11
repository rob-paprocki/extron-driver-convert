from extronlib.system import ProgramLog, Wait
import urllib.error
import urllib.request
from re import search
import base64

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.base64Auth = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.base64Auth = None

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
            'AutoReboot': { 'Status': {}},
            'CurrentValue': { 'Status': {}},
            'OutletControl': {'Parameters':['Outlet'], 'Status': {}},
            'OutletName': {'Parameters':['Outlet'], 'Status': {}},
            'OutletStatus': {'Parameters':['Outlet'], 'Status': {}},
            'PowerValue': { 'Status': {}},
            'VoltageValue': { 'Status': {}},
        }

    def UpdateAutoReboot(self, value, qualifier):

        ARStates = {
            '1' : 'Enabled', 
            '0' : 'Disabled'
        }

        OutletStates = {
            '1' : 'On', 
            '0' : 'Off'
        } 

        AutoRebootCmdString = 'wattbox_info.xml'
        res = self.__UpdateHelper('AutoReboot', value, qualifier, AutoRebootCmdString)
        if res:         
            try:
                auto_reboot = search('<auto_reboot>(0|1)</auto_reboot>', res)
                self.WriteStatus('AutoReboot', ARStates[auto_reboot.group(1)], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Reboot: Invalid/unexpected response'])

            try:
                outlet_name = search('<outlet_name>([\s\S]+)</outlet_name>', res)
                nameList = outlet_name.group(1).split(',')
                for i in range(0, len(nameList)):
                    self.WriteStatus('OutletName', nameList[i], {'Outlet': str(i+1)})
            except (KeyError, IndexError):
                self.Error(['Outlet Name: Invalid/unexpected response'])

            try:
                outlet_status = search('<outlet_status>([01,]+)</outlet_status>', res)
                statusList = outlet_status.group(1).split(',')
                for i in range(0, len(statusList)):
                    self.WriteStatus('OutletStatus', OutletStates[statusList[i]], {'Outlet': str(i+1)})
            except (KeyError, IndexError):
                self.Error(['Outlet Status: Invalid/unexpected response'])

            try:
                voltage_value = search('<voltage_value>(\d+)</voltage_value>', res)
                self.WriteStatus('VoltageValue', int(voltage_value.group(1))/10, qualifier)
            except (ValueError, IndexError):
                self.Error(['Voltage Value: Invalid/unexpected response'])

            try:
                current_value = search('<current_value>(\d+)</current_value>', res)
                self.WriteStatus('CurrentValue', int(current_value.group(1))/10, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Value: Invalid/unexpected response'])

            try:
                power_value = search('<power_value>(\d+)</power_value>', res)
                self.WriteStatus('PowerValue', int(power_value.group(1)), qualifier)
            except (ValueError, IndexError):
                self.Error(['Power Value: Invalid/unexpected response'])

    def SetOutletControl(self, value, qualifier):

        ValueStateValues = {
            'Power On'        : '1', 
            'Power Off'       : '0', 
            'Power Reset'     : '3', 
            'Auto Reboot On'  : '4', 
            'Auto Reboot Off' : '5'
        }

        outlet = qualifier['Outlet']
        if 1 <= int(outlet) <= 3 and value in ValueStateValues:
            OutletControlCmdString = 'outlet={0}&command={1}'.format(outlet, ValueStateValues[value])
            self.__SetHelper('OutletControl', value, qualifier, OutletControlCmdString, None)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def __CheckResponseForErrors(self, sourceCmdName, response):
 
        res = response.read(2)
        while res[-10:] != b'</request>': # while not end of response
            res += response.read(1) # read each byte individually and append to res
        return res.decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}control.cgi?{}'.format(self.RootURL, url)
        headers = {'Authorization': self.base64Auth}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = urllib.request.urlopen(my_request, timeout=10)          
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Authorization': self.base64Auth}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = urllib.request.urlopen(my_request, timeout=10)          
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