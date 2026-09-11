from extronlib.system import Wait, ProgramLog
import urllib.error
import urllib.request
import json

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
            'InputVolume': {'Parameters':['Channel'], 'Status': {}},
            'OutputMute': {'Parameters':['Channel'], 'Status': {}},
            'OutputVolume': {'Parameters':['Channel'], 'Status': {}},
            'Power': { 'Status': {}},
        }

    def SetInputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 6 and -80.0 <= value <= 12.0:
            InputVolumeCmdString = 'dsp/INPUT/CHL00{0}/VOLUME01/GAIN/{1}'.format(qualifier['Channel'], round(value, 1))
            self.__SetHelper('InputVolume', value, qualifier, url=InputVolumeCmdString)
        else:
            self.Discard('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 6:
            InputVolumeCmdString = 'dsp/INPUT/CHL00{0}/VOLUME01/GAIN'.format(qualifier['Channel'])
            res = self.__UpdateHelper('InputVolume', value, qualifier, url=InputVolumeCmdString)
            if res:
                try:
                    value = float(res['Result'])
                    self.WriteStatus('InputVolume', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Input Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputVolume')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Channel']) <= 4 and value in ValueStateValues:
            OutputMuteCmdString = 'dsp/OUTPUT/CHL00{0}/MUTE01/ON_OFF/{1}'.format(qualifier['Channel'], ValueStateValues[value])
            self.__SetHelper('OutputMute', value, qualifier, url=OutputMuteCmdString)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4:
            OutputMuteCmdString = 'dsp/OUTPUT/CHL00{0}/MUTE01/ON_OFF'.format(qualifier['Channel'])
            res = self.__UpdateHelper('OutputMute', value, qualifier, url=OutputMuteCmdString)
            if res:
                try:
                    ValueStateValues = {
                        '1' : 'On',
                        '0' : 'Off'
                    }
                    
                    value = ValueStateValues[res['Result']]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Output Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetOutputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4 and -80.0 <= value <= 12.0:
            OutputVolumeCmdString = 'dsp/OUTPUT/CHL00{0}/VOLUME01/GAIN/{1}'.format(qualifier['Channel'], round(value, 1))
            self.__SetHelper('OutputVolume', value, qualifier, url=OutputVolumeCmdString)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4:
            OutputVolumeCmdString = 'dsp/OUTPUT/CHL00{0}/VOLUME01/GAIN'.format(qualifier['Channel'])
            res = self.__UpdateHelper('OutputVolume', value, qualifier, url=OutputVolumeCmdString)
            if res:
                try:
                    value = float(res['Result'])
                    self.WriteStatus('OutputVolume', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Output Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputVolume')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            PowerCmdString = 'micro/standby/{}'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url=PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'micro/standby'
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                ValueStateValues = {
                    'true'  : 'On',
                    'false' : 'Off'
                }

                value = ValueStateValues[res['Result']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            return None

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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