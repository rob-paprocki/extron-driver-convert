import base64
import urllib.error
import urllib.request
import json
from extronlib import Version
from extronlib.system import GetUnverifiedContext

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self._SSLVerifyMode = 'Off'
        
        if self._SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),  
                                                    urllib.request.HTTPSHandler(context=self._context)) 

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
            'CameraControl': {'Parameters':['Status'], 'Status': {}},
            'CodecMode': { 'Status': {}},
            'FrameSize': { 'Status': {}},
            'MicStatus': {'Parameters':['Mic'], 'Status': {}},
            'PIPWindowPosition': { 'Status': {}},
            'SystemStatus': { 'Status': {}},
            'TrackingMode': { 'Status': {}},
            'TrackingSpeed': { 'Status': {}},
            'WakeUp': { 'Status': {}},
        }

        
        self.sessionID = ''

        self._updateMicStatus = 0
        self._updateTrackingInfo = 0

 
    @property
    def SSLVerifyMode(self):
        return self._SSLVerifyMode

    @SSLVerifyMode.setter
    def SSLVerifyMode(self, value):
        self._SSLVerifyMode= value

    def SetLogin(self, value, qualifier):
        
        url = 'https:{}/api/login'.format(self.RootURL.split(':')[1])
        print(url)
        my_request = urllib.request.Request(url, method='GET')
        
        try:
            res = urllib.request.urlopen(my_request, context=self._context) 
            if res:
                headers = res.getheaders()
                for h in headers:
                    if 'Cookie' in h[0]:
                        self.sessionID = h[1].split(';')[0]
        except:
            self.Error(['Error obtaining sessionID'])

    def SetCameraControl(self, value, qualifier):
        
        if qualifier['Status'] in ['Start', 'Stop'] and value in ['Up', 'Down', 'Left', 'Right', 'In', 'Out']:
            self.__SetHelper('CameraControl', value, qualifier, url='rest/cameraControl', data=json.dumps({"action": value.lower(), "status": qualifier['Status'].lower()}).encode())
        else:
            self.Discard('Invalid Command for SetCameraControl')

    def SetCodecMode(self, value, qualifier):

        ValueStateValues = {
            'Group Series'           : {"codecMode": "Group Series"},
            'Connect Your Own Device': {"codecMode": "Connect Your Own Device"},
            'Automatic'              : {"codecMode": "Automatic"}
        }

        if value in ValueStateValues:
            self.__SetHelper('CodecMode', value, qualifier, url='rest/codecMode', data=json.dumps(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetCodecMode')

    def UpdateCodecMode(self, value, qualifier):

        res = self.__UpdateHelper('CodecMode', value, qualifier, url='rest/codecMode')
        if res:
            try:
                value = json.loads(res)["codecMode"]
                self.WriteStatus('CodecMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Codec Mode: Invalid/unexpected response'])

    def SetFrameSize(self, value, qualifier):

        ValueStateValues = {
            'Wide'  : {"frameSize": "Wide"},
            'Medium': {"frameSize": "Medium"},
            'Tight' : {"frameSize": "Tight"}
        }

        if value in ValueStateValues:
            self.__SetHelper('FrameSize', value, qualifier, url='api/tracking', data=json.dumps(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetFrameSize')

    def UpdateFrameSize(self, value, qualifier):
      
        self.UpdateTrackingMode(None, None)

    def UpdateMicStatus(self, value, qualifier):
       
        res = self.__UpdateHelper('MicStatus', value, qualifier, url='api/audioDiagnostics')
        if res:
            try:
                values = json.loads(res)
                for mic in range(10):
                    value = values["mic_{}".format(mic)]
                    self.WriteStatus('MicStatus', value, {'Mic': str(mic+1)})
                self.WriteStatus('MicStatus', values["mic_left"], {'Mic': 'Left'})
                self.WriteStatus('MicStatus', values["mic_right"], {'Mic': 'Right'})
            except (ValueError, IndexError):
                self.Error(['Mic Status: Invalid/unexpected response'])

    def SetPIPWindowPosition(self, value, qualifier):

        ValueStateValues = {
            'Off'         : {"PIPLayOut": "OFF"},
            'Left Top'    : {"PIPLayOut": "Left Top"},
            'Right Top'   : {"PIPLayOut": "Right Top"},
            'Left Bottom' : {"PIPLayOut": "Left Bottom"},
            'Right Bottom': {"PIPLayOut": "Right Bottom"},
            'Split Window': {"PIPLayOut": "Split Window"}
        }

        if value in ValueStateValues:
            self.__SetHelper('PIPWindowPosition', value, qualifier, url='api/tracking', data=json.dumps(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetPIPWindowPosition')

    def UpdatePIPWindowPosition(self, value, qualifier):

        self.UpdateTrackingMode(None, None)

    def UpdateSystemStatus(self, value, qualifier):
        
        ValueStateValues = {
            'BootingUp' : 'Booting Up', 
            'Running'   : 'Running', 
            'Sleep'     : 'Sleep', 
            'FakeSleep' : 'Fake Sleep', 
            'SwUpdating': 'Software Updating', 
            'InConf'    : 'In Conference', 
            'ErrOccur'  : 'Error Occur'
        }

        res = self.__UpdateHelper('SystemStatus', value, qualifier, url='api/getSystemStatus')
        if res:
            try:
                value = ValueStateValues[json.loads(res)["systemStatus"]]
                self.WriteStatus('SystemStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Status: Invalid/unexpected response'])

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Off'          : {"trackingMode": "OFF"}, 
            'Frame Speaker': {"trackingMode": "Frame Speaker"}, 
            'Frame Group'  : {"trackingMode": "Frame Group"}
        }

        if value in ValueStateValues:
            self.__SetHelper('TrackingMode', value, qualifier, url='api/tracking', data=json.dumps(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def UpdateTrackingMode(self, value, qualifier):
       
        res = self.__UpdateHelper('TrackingMode', value, qualifier, url='api/tracking')
        if res:
            value = json.loads(res)
            try:
                self.WriteStatus('TrackingMode', value["trackingMode"].title(), qualifier)
            except (KeyError, IndexError):
                self.Error(['Tracking Mode: Invalid/unexpected response'])
                    
            try:
                self.WriteStatus('TrackingSpeed', value["trackingSpeed"], qualifier)
            except (KeyError, IndexError):
                self.Error(['Tracking Speed: Invalid/unexpected response'])
                    
            try:
                self.WriteStatus('FrameSize', value["framingSize"], qualifier)
            except (KeyError, IndexError):
                self.Error(['Frame Size: Invalid/unexpected response'])
                    
            try:
                self.WriteStatus('PIPWindowPosition', value["pipLayout"].title(), qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Window Position: Invalid/unexpected response'])

    def SetTrackingSpeed(self, value, qualifier):

        ValueStateValues = {
            'Slow'  : {"trackingSpeed": "Slow"},
            'Normal': {"trackingSpeed": "Normal"},
            'Fast'  : {"trackingSpeed": "Fast"}
        }

        if value in ValueStateValues:
            self.__SetHelper('TrackingSpeed', value, qualifier, url='api/tracking', data=json.dumps(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetTrackingSpeed')

    def UpdateTrackingSpeed(self, value, qualifier):
      
        self.UpdateTrackingMode(None, None)

    def SetWakeUp(self, value, qualifier):

        if value in ['Set', 'Keep']:
            self.__SetHelper('WakeUp', value, qualifier, url='api/{}WakeUp'.format(value.lower()))
        else:
            self.Discard('Invalid Command for SetWakeUp')
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = 'https:{}/{}'.format(self.RootURL.split(':')[1], url)
        print('URL', url)
        headers = {'Content-Type': 'application/json'}
        if command not in ['CameraControl', 'CodecMode']:
            if self.sessionID:
                headers['Cookie'] = self.sessionID
            else:
                self.SetLogin( None, None)
                self.Error(['Error with sessionID'])
        
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()        
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        res = ''
        try:
            res = urllib.request.urlopen(my_request, context=self._context)  # open() returns a http.client.HTTPResponse object if successful
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

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = 'https:{}/{}'.format(self.RootURL.split(':')[1], url)

        headers = {'Content-Type': 'application/json'}
        if command not in ['CameraControl', 'CodecMode']:
            if self.sessionID:
                headers['Cookie'] = self.sessionID
            else:
                self.SetLogin( None, None)
                #self.__UpdateHelper(command, value, qualifier, url, data)
                self.Error(['Error with sessionID'])
              
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        res = ''
        try:
            res = urllib.request.urlopen(my_request, context=self._context)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            if command == 'SystemStatus':
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

        
        self.SetLogin( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        
        self.sessionID = ''

        
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