from extronlib.system import Wait, ProgramLog
import json
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
            'ChannelDiscreteCommand': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'v1/mute'
            data = {
                'mute': ValueStateValues[value]
            }

            self.__SetHelper('AudioMute', value, qualifier, url=AudioMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }

        AudioMuteCmdString = 'v1/mute'
        res = self.__UpdateHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannelDiscreteCommand(self, value, qualifier):

        channel = value

        if channel:
            ChannelDiscreteCommandCmdString = 'v1/channel'
            data = {
                'channel': channel
            }

            self.__SetHelper('ChannelDiscreteCommand', value, qualifier, url=ChannelDiscreteCommandCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetChannelDiscreteCommand')

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up':   'ChannelUp',
            'Down': 'ChannelDown'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = 'v1/key'
            data = {
                'key': ValueStateValues[value]
            }

            self.__SetHelper('ChannelStep', value, qualifier, url=ChannelStepCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = 'v1/key'
            data = {
                'key': 'digit' + str(int(value))
            }

            self.__SetHelper('Keypad', value, qualifier, url=KeypadCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = [
            'Up',
            'Down',
            'Left',
            'Right',
            'Menu',
            'OK',
            'Exit',
            'Back'
        ]

        if value in ValueStateValues:
            MenuNavigationCmdString = 'v1/key'
            data = {
                'key': value.lower()
            }

            self.__SetHelper('MenuNavigation', value, qualifier, url=MenuNavigationCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   False,
            'Off':  True
        }

        if value in ValueStateValues:
            PowerCmdString = 'v1/sleep'
            data = {
                'sleep': ValueStateValues[value]
            }

            self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            False:  'On',
            True:   'Off'
        }

        PowerCmdString = 'v1/sleep'
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'v1/volume'
            data = {
                'volume': value
            }

            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'v1/volume'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                value = int(res['result'])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except:
            self.Error(['{}: Invalid/unexpected response.'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        data = json.dumps(data).encode()

        headers = {
            'Content-Type': 'application/json'
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=1)
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

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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