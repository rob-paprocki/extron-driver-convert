import base64
import re
import urllib.error
import urllib.request

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'Shuffle': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
        
        self.VolRegex = re.compile('<actualvolume>(\d+)</actualvolume>')

    def SetMute(self, value, qualifier):

        MuteCmdString = 'key'
        Data = '<key state="press" sender="Gabbo">MUTE</key>'
        self.__SetHelper('Mute', value, qualifier, url=MuteCmdString, data=Data)

    def SetPower(self, value, qualifier):

        PowerCmdString = 'key'
        Data1 = '<key state="press" sender="Gabbo">POWER</key>'
        Data2 = '<key state="release" sender="Gabbo">POWER</key>'
        self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=Data1)
        self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=Data2)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1' : 'PRESET_1', 
            '2' : 'PRESET_2', 
            '3' : 'PRESET_3', 
            '4' : 'PRESET_4', 
            '5' : 'PRESET_5', 
            '6' : 'PRESET_6'
        }

        PresetCmdString = 'key'
        Data = '<key state="release" sender="Gabbo">{}</key>'.format(ValueStateValues[value])
        self.__SetHelper('Preset', value, qualifier, url=PresetCmdString, data=Data)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Off' : 'REPEAT_OFF', 
            'One' : 'REPEAT_ONE', 
            'All' : 'REPEAT_ALL'
        }

        RepeatCmdString = 'key'
        Data = '<key state="press" sender="Gabbo">{}</key>'.format(ValueStateValues[value])
        self.__SetHelper('Repeat', value, qualifier, url=RepeatCmdString, data=Data)

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'SHUFFLE_ON', 
            'Off' : 'SHUFFLE_OFF'
        }

        ShuffleCmdString = 'key'
        Data = '<key state="press" sender="Gabbo">{}</key>'.format(ValueStateValues[value])
        self.__SetHelper('Shuffle', value, qualifier, url=ShuffleCmdString, data=Data)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'           : 'PLAY', 
            'Pause'          : 'PAUSE', 
            'Stop'           : 'STOP', 
            'Previous Track' : 'PREV_TRACK', 
            'Next Track'     : 'NEXT_TRACK'
        }

        TransportCmdString = 'key'
        Data = '<key state="press" sender="Gabbo">{}</key>'.format(ValueStateValues[value])
        self.__SetHelper('Transport', value, qualifier, url=TransportCmdString, data=Data)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'volume'
            Data = '<volume>{}</volume>'.format(value)
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=Data)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                value = int(re.findall(self.VolRegex, res)[0])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data.encode(), headers=headers, method='POST')
        
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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