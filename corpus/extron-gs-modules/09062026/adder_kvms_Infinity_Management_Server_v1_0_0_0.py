import urllib.error
import urllib.request
import base64
from extronlib.standard.exml.etree import ElementTree as ET

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
 
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
 
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 
        
        self.connectionCounter = 15

        self.IPAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Heartbeat': {'Status': {}},
            'ConnectChanneltoReceiver': {'Parameters': ['Channel ID', 'Mode'], 'Status': {}},
            'DisconnectReceiver': {'Status': {}},
            'SetPreset': {'Status': {}}
        }


        self.token = ''


    def SetLogin(self, value, qualifier):
        url_login = 'api/?v=5&method=login&username={0}&password={1}'.format(self.deviceUsername, self.devicePassword)
        res = self.__UpdateHelper('Login', None, None, url_login)
        if res:
            root = ET.fromstring(res)
            try:
                if root.findall(".//success")[0].text.split('.')[0] == '1':
                    self.token = root.findall(".//token")[0].text.split('.')[0]
                else:
                    print('Login Failed')
            except:
                print('Login Failed')
        else:
            self.token = ''
            print('Login Failed')

    def UpdateHeartbeat(self, value, qualifier):

        url = 'api/?v=1&method=get_presets&token={}'.format(self.token)
        self.__UpdateHelper('Heartbeat', None, None, url)

    def SetConnectChanneltoReceiver(self, value, qualifier):

        CH = qualifier['Channel ID']
        Modes = {
            'Video Only': 'v',
            'Shared': 's',
            'Exclusive': 'e',
            'Private': 'p'
        }
        Mode = Modes[qualifier['Mode']]
        if self.token and 0 <= CH <= 99999999 and 0 <= value <= 999 :
            url = 'api/?v=5&method=connect_channel&c_id={0}&rx_id={1}&mode={2}&token={3}'.format(CH, value, Mode, self.token)
            self.__SetHelper('ConnectChanneltoReceiver', value, qualifier, url)
        else:
            print('Invalid Command for SetConnectChanneltoReceiver')

    def SetDisconnectReceiver(self, value, qualifier):

        if self.token and 0 <= value <= 999:
            url = 'api/?v=5&method=disconnect_channel&rx_id={0}&token={1}'.format(value, self.token)
            self.__SetHelper('Channel', value, qualifier, url)
        else:
            print('Invalid Command for SetDisconnectReceiver')

    def SetSetPreset(self, value, qualifier):
        if self.token and 0 <= value <= 999:
            url = 'api/?v=5&method=connect_preset&id={0}&token={1}'.format(value, self.token)
            self.__SetHelper('Set Preset', value, qualifier, url)
        else:
            print('Invalid Command for SetSetPreset')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/html'}

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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
            
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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

        self.token = ''

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
