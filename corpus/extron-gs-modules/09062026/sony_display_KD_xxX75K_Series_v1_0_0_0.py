from json import loads, dumps
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerSavingMode': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : True, 
            'Off' : False
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '/sony/audio'
            data = dumps({"method": "setAudioMute",
                        "id": 601,
                        "params": [{"status": ValueStateValues[value]}],
                        "version": "1.0"})
            self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateVolume(value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues ={
            'TV/DVB'    : 'tv:dvbt',
            'HDMI 1'    : 'extInput:hdmi?port=1', 
            'HDMI 2'    : 'extInput:hdmi?port=2', 
            'HDMI 3'    : 'extInput:hdmi?port=3', 
            'Composite' : 'extInput:composite?port=1'
        }
    
        if value in ValueStateValues:
            InputCmdString = '/sony/avContent'
            data = dumps({"method": "setPlayContent", 
                        "id": 101,
                        "params": [{"uri": ValueStateValues[value]}],
                        "version": "1.0"})
            self.__SetHelper('Input', value, qualifier, InputCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues ={
            'tv:dvbt'                   : 'TV/DVB', 
            'extInput:hdmi?port=1'      : 'HDMI 1', 
            'extInput:hdmi?port=2'      : 'HDMI 2', 
            'extInput:hdmi?port=3'      : 'HDMI 3', 
            'extInput:composite?port=1' : 'Composite'
        }
        
        InputCmdString = '/sony/avContent'
        data = dumps({"method": "getPlayingContentInfo", 
                    "id": 103,
                    "params": [],
                    "version": "1.0"})
        res = self.__UpdateHelper('Input', value, qualifier, InputCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['uri']]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : True, 
            'Sleep' : False
        }

        if value in ValueStateValues:
            PowerCmdString = '/sony/system'
            data = dumps({"method": "setPowerStatus",
                        "id": 55,
                        "params": [{"status": ValueStateValues[value]}],
                        "version": "1.0"})
            self.__SetHelper('Power', value, qualifier, PowerCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'active'  : 'On', 
            'standby' : 'Sleep'
        }

        PowerCmdString = '/sony/system'
        data = dumps({"method": "getPowerStatus",
                        "id": 50,
                        "params": [],
                        "version": "1.0"})
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['status']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            'Off'         : 'off', 
            'Low'         : 'low', 
            'High'        : 'high', 
            'Picture Off' : 'pictureOff'
        }

        if value in ValueStateValues:
            PowerSavingModeCmdString = '/sony/system'
            data = dumps({"method": "setPowerSavingMode", 
                            "id": 52,
                            "params": [{"mode": ValueStateValues[value]}],
                            "version": "1.0"})
            self.__SetHelper('PowerSavingMode', value, qualifier, PowerSavingModeCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetPowerSavingMode')

    def UpdatePowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            'off'        : 'Off', 
            'low'        : 'Low', 
            'high'       : 'High', 
            'pictureOff' : 'Picture Off'
        }

        PowerSavingModeCmdString = '/sony/system'
        data = dumps({"method": "getPowerSavingMode",
                        "id": 51,
                        "params": [],
                        "version": "1.0"})
        res = self.__UpdateHelper('PowerSavingMode', value, qualifier, PowerSavingModeCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['mode']]
                self.WriteStatus('PowerSavingMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Saving Mode: Invalid/unexpected response'])
     
    def SetReboot(self, value, qualifier):

        RebootCmdString = '/sony/system'
        data = dumps({"method": "requestReboot", 
                      "id": 10,
                      "params": [],
                      "version": "1.0"})
        self.__SetHelper('Reboot', value, qualifier, RebootCmdString, data.encode())

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '/sony/audio'
            data = dumps({  "method": "setAudioVolume", 
                        "id": 601,
                        "params": [{
                                    "volume": str(value),
                                    "target": "speaker"
                                }],
                        "version": "1.0"})
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        AudioMuteStates ={
            True  : 'On',
            False : 'Off'
        }

        VolumeCmdString = '/sony/audio'
        data = dumps({"method": "getVolumeInformation", 
                        "id": 33,
                        "params": [],
                        "version": "1.0"})
        res = self.__UpdateHelper('Volume', value, qualifier, VolumeCmdString, data.encode())
        if res:
            try:
                value = int(res['result'][0][0]['volume'])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])
            try:
                value = AudioMuteStates[res['result'][0][0]['mute']]
                self.WriteStatus('AudioMute', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = loads(response.read().decode())
        return res
        
    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
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

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port)
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
