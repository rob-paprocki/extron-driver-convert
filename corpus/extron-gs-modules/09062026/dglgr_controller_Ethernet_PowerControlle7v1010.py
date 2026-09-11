from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import GetUnverifiedContext, ProgramLog
import urllib.error
import urllib.request
import binascii
import base64


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
            
        if port == 443:
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        else:
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                  urllib.request.HTTPSHandler(context=self._context))
        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MasterControl'   : {'Status': {}},
            'OutletControl'   : {'Parameters':['Outlet'], 'Status': {}},
            'OutletCritical'  : {'Parameters':['Outlet'], 'Status': {}},
            'OutletCycle'     : {'Parameters':['Outlet'], 'Status': {}},
            'OutletCycleDelay': {'Parameters':['Outlet'], 'Status': {}},
            'OutletLockState' : {'Parameters':['Outlet'], 'Status': {}},
            'OutletStatus'    : {'Status': {}}
        }

    def SetMasterControl(self, value, qualifier):
        ValueStateValues = {
            'All Outlets On' : 'true',
            'All Outlets Off': 'false'
        }
        self.__SetHelper('MasterControl', value, qualifier, url='all;/state', data=ValueStateValues[value].encode())

    def SetOutletControl(self, value, qualifier):
        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }
        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7:
            self.__SetHelper('OutletControl', value, qualifier, url='{}/state'.format(outlet), data=ValueStateValues[value].encode())
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def UpdateOutletCritical(self, value, qualifier):

        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7:
            res = self.__UpdateHelper('OutletCritical', value, qualifier, url='{}/critical'.format(outlet))
            if res:
                try:
                    value = str(res).title()
                    self.WriteStatus('OutletCritical', value, qualifier)
                except (ValueError):
                    self.Error(['Outlet Critical: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletCritical')

    def SetOutletCycle(self, value, qualifier):

        outlet = 'all;' if qualifier['Outlet'] == 'All' else int(qualifier['Outlet']) - 1
        if outlet == 'all;' or 0 <= outlet <= 7:
            self.__SetHelper('OutletCycle', value, qualifier, url='{}/cycle'.format(outlet))
        else:
            self.Discard('Invalid Command for SetOutletCycle')

    def SetOutletCycleDelay(self, value, qualifier):

        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7:
            value = 'null' if value == 0 else str(value)
            self.__SetHelper('OutletCycleDelay', value, qualifier, url='{}/cycle_delay'.format(outlet), data=value.encode())
        else:
            self.Discard('Invalid Command for SetOutletCycleDelay')

    def UpdateOutletCycleDelay(self, value, qualifier):

        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7:
            res = self.__UpdateHelper('OutletCycleDelay', value, qualifier, url='{}/cycle_delay'.format(outlet))
            if res:
                try:
                    value = 0 if res == 'null' else int(res)
                    self.WriteStatus('OutletCycleDelay', value, qualifier)
                except (ValueError):
                    self.Error(['Outlet Critical: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletCycleDelay')

    def SetOutletLockState(self, value, qualifier):

        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7 and value in ['True', 'False']:
            self.__SetHelper('OutletLockState', value, qualifier, url='{}/locked'.format(outlet), data=value.lower().encode())
        else:
            self.Discard('Invalid Command for SetOutletLockState')

    def UpdateOutletLockState(self, value, qualifier):

        outlet = int(qualifier['Outlet']) - 1
        if 0 <= outlet <= 7:
            res = self.__UpdateHelper('OutletLockState', value, qualifier, url='{}/locked'.format(outlet))
            if res:
                try:
                    value = str(res).title()
                    self.WriteStatus('OutletLockState', value, qualifier)
                except (ValueError):
                    self.Error(['Outlet Lock State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletLockState')

    def UpdateOutletStatus(self, value, qualifier):

        res = self.__UpdateHelper('OutletStatus', value, qualifier, url='all;/state')
        if res:
            try:
                outlet = 1
                values = res[1:-1].split(',')
                for val in values:
                    value = 'On' if val == 'true' else 'Off'
                    self.WriteStatus('OutletControl', value, {'Outlet': str(outlet)})
                    outlet += 1
            except (ValueError, IndexError):
                self.Error(['Outlet Status: Invalid/unexpected response'])
    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        url = '{}restapi/relay/outlets/{}/'.format(self.RootURL, url)
        if command == 'OutletCycle':
            headers = {
                'X-CSRF': 'x'
            }
            method = 'POST'
        else:
            headers = {
                'X-CSRF': 'x',
                'Content-Type': 'application/json'
            }
            method = 'PUT'
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        url = '{}restapi/relay/outlets/{}/'.format(self.RootURL, url)
        headers = {}
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