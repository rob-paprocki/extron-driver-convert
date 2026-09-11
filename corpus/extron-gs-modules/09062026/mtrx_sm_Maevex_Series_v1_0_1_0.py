from extronlib.system import GetUnverifiedContext
import urllib.error
import urllib.request
import base64
from json import loads,dumps
import re

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
            
        if port == '443':
            self.RootURL = 'https://{0}:{1}'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                  urllib.request.HTTPSHandler(context=self._context))
        else:
            self.RootURL = 'http://{0}:{1}'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Inputs = None
        self.Outputs = None

        self.Models = {
            'Maevex 6150 Encoder': self.mtrx_42_3836_6150,
            'Maevex 6120 Encoder': self.mtrx_42_3836_6120,
            'Maevex 6100 Encoder': self.mtrx_42_3836_6100,
            'Maevex 5150 Encoder': self.mtrx_42_3836_5150_En,
            'Maevex 5150 Decoder': self.mtrx_42_3836_5150_De,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'EjectUSB': {'Parameters':['USB ID'], 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'IPAddress': { 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'OutputVolume': {'Parameters':['Output'], 'Status': {}},
            'Reboot': { 'Status': {}},
            }                    
       
    def SetEjectUSB(self, value, qualifier):

        USBID = qualifier['USB ID']
        if USBID:
            EjectUSBCmdString = '/api/usb/msd1/eject'
            jsonData = dumps({'Id': USBID})
            self.__SetHelper('EjectUSB', value, qualifier, EjectUSBCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetEjectUSB')

    def SetInputGain(self, value, qualifier):

        InVal = qualifier['Input']
        if InVal in self.Inputs:
            InputGainCmdString = '/api/context/dynamicSettings/input/{}/gain'.format(InVal)
            jsonData = dumps({'Gain': int(value)})
            self.__SetHelper('InputGain', value, qualifier, InputGainCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetInputGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': True,
            'Off': False
        }

        InVal = qualifier['Input']
        if InVal in self.Inputs:
            InputMuteCmdString = '/api/context/dynamicSettings/input/{}/mute'.format(InVal)
            jsonData = dumps({'Mute': ValueStateValues[value]})
            self.__SetHelper('InputMute', value, qualifier, InputMuteCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = '/api/context/allsettings/default'
        res = self.__UpdateHelper('IPAddress', value, qualifier, IPAddressCmdString)
        if res:
            try:
                value = res['Settings']['EthernetInterface1']['Ipv4Address']
                self.WriteStatus('IPAddress', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['IP Address: Invalid/unexpected response'])

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': True,
            'Off': False
        }

        OutVal = qualifier['Output']
        if OutVal in self.Outputs:
            OutputMuteCmdString = '/api/context/dynamicSettings/output/{}/mute'.format(OutVal)
            jsonData = dumps({'Mute': ValueStateValues[value]})
            self.__SetHelper('OutputMute', value, qualifier, OutputMuteCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def SetOutputVolume(self, value, qualifier):

        OutVal = qualifier['Output']
        if OutVal in self.Outputs:
            OutputVolumeCmdString = '/api/context/dynamicSettings/output/{}/volume'.format(OutVal)
            jsonData = dumps({'Volume': int(value)})
            self.__SetHelper('OutputVolume', value, qualifier, OutputVolumeCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def SetReboot(self, value, qualifier):

        RebootCmdString = '/api/command/reboot'
        self.__SetHelper('Reboot', value, qualifier, RebootCmdString)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True
        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        if command == 'Reboot' or command == 'EjectUSB':
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        else:
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
        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
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
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
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

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def mtrx_42_3836_5150_De(self):
       
        self.Outputs = ['1']

    def mtrx_42_3836_5150_En(self):

        self.Inputs = ['1']
        self.Outputs = ['1','2']

    def mtrx_42_3836_6100(self):

        self.Inputs = ['1','2','3','4']

    def mtrx_42_3836_6120(self):

        self.Inputs = ['1', '2']
        self.Outputs = ['1', '2', '3']

    def mtrx_42_3836_6150(self):

        self.Inputs = ['1', '2', '3', '4']
        self.Outputs = ['1', '2', '3', '4', '5']

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