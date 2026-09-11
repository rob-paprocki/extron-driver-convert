from extronlib.interface import EthernetClientInterface, EthernetServerInterface
import urllib.error
import urllib.request
import re
from json import loads

class DeviceHttpClass:
    
    def __init__(self, ipAddress, port):

        self.ipAddress = ipAddress
        self.port = port
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        
        self.Models = {
        'Expert Power Control NET 8012'  : self.gude_20_1211_other,
        'Expert Power Control NET 8211'  : self.gude_20_1211_other,
        'Expert Power Control NET 8220'  : self.gude_20_1211_8220,
        
        }
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress,port)
        self.auth_handler = urllib.request.HTTPBasicAuthHandler()
        self.opener = urllib.request.build_opener(self.auth_handler)
        urllib.request.install_opener(self.opener)
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Power': {'Parameters':['Port'],'Status': {}},
            }

    def SetPower(self, value, qualifier):
    
        ValueStateValues = {
            'On' :  1, 
            'Off' : 0
        }

        port = int(qualifier['Port'])
        if self.PortConstraints['Min'] <= port <= self.PortConstraints['Max']:
            PowerCmdString = '/?cmd=1&p={0}&s={1}'.format(port, ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, PowerCmdString)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
    
        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        PowerCmdString = '/statusjsn.js?components=1'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                for a in range(self.PortConstraints['Max']):
                    port = str(int(res['outputs'][a]['name'][-2:]))
                    value = ValueStateValues[res['outputs'][a]['state']]
                    self.WriteStatus('Power', value, {'Port': port})
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')

    def __CheckResponseForErrors(self, sourceCmdName, res):
        return loads(res.read().decode())

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'application/json'}
        
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        
        try:
            res = self.opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
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
        headers = {'Content-Type': 'application/json'}

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
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

    def gude_20_1211_8220(self):

        self.PortConstraints = {
            'Min': 1,
            'Max': 12
        }

    def gude_20_1211_other(self):

        self.PortConstraints = {
            'Min': 1,
            'Max': 8
        }

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)
        except AttributeError:
            print(command, 'does not support Update.')

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}


    # Check incoming unsolicited data to see if it matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback
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
        if self.connectionFlag == False:
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
            
class EthernetClass(DeviceHttpClass):

    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHttpClass.__init__(self, ipAddress, port)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
