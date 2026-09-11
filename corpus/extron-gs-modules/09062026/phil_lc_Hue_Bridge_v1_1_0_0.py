from extronlib.system import Wait, ProgramLog
import json
import base64
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}/'.format(ipAddress)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GetAllLights': { 'Status': {}},
            'GroupBrightness': {'Parameters':['Group ID'], 'Status': {}},
            'GroupEffect': {'Parameters':['Group ID'], 'Status': {}},
            'GroupHue': {'Parameters':['Group ID'], 'Status': {}},
            'GroupMiredColorTemperature': {'Parameters':['Group ID'], 'Status': {}},
            'GroupSaturation': {'Parameters':['Group ID'], 'Status': {}},
            'GroupState': {'Parameters':['Group ID'], 'Status': {}},
            'GroupTransitionTime': {'Parameters':['Group ID'], 'Status': {}},
            'LightBrightness': {'Parameters':['Light ID'], 'Status': {}},
            'LightEffect': {'Parameters':['Light ID'], 'Status': {}},
            'LightHue': {'Parameters':['Light ID'], 'Status': {}},
            'LightMiredColorTemperature': {'Parameters':['Light ID'], 'Status': {}},
            'LightSaturation': {'Parameters':['Light ID'], 'Status': {}},
            'LightState': {'Parameters':['Light ID'], 'Status': {}},
            'LightTransitionTime': {'Parameters':['Light ID'], 'Status': {}},
            'SceneRecall': {'Parameters':['Group ID','Identifier'], 'Status': {}},
            'SyncStatus': { 'Status': {}},
        }

        self.token = ''
        
    def getToken(self, value, qualifier):

        res = self.__UpdateHelper('GetAllLights', value, qualifier, url='', 
                                  data=json.dumps({"devicetype":"my_hue_app#extron"}).encode())
        if res:
            try:
                if "error" in res:
                    self.WriteStatus('SyncStatus', 'Not Synced', None)
                else:
                    self.token = json.loads(res)[0]['success']['username']
                    self.WriteStatus('SyncStatus', 'Synced', None)
            except KeyError:
                self.WriteStatus('SyncStatus', 'Not Synced', None)
                self.Error(['Invalid Token'])

    def UpdateGetAllLights(self, value, qualifier):

        states = {
            True        : 'On',
            False       : 'Off',
            'none'      : 'None',
            'colorloop' : 'Color Loop'
        }

        if not self.token:
            self.getToken(value, qualifier)
        else:
            res = self.__UpdateHelper('GetAllLights', value, qualifier, url='lights')
            if res:
                try:
                    lights = json.loads(res)
                except(ValueError, TypeError):
                    self.Error(['Get All Lights: Invalid/unexpected response'])
                else:
                    for light in lights:
                        try:
                            state = lights[light]['state']
                            lightID = {'Light ID': int(light)}
                        except(ValueError, KeyError):
                            self.Error(['Get All Lights: Invalid/unexpected response'])
                        else:
                            try:
                                self.WriteStatus('LightBrightness', state['bri'], lightID)
                            except KeyError:
                                self.Error(['Light Brightness: Invalid/unexpected response'])
                            try:
                                self.WriteStatus('LightHue', state['hue'], lightID)
                            except KeyError:
                                self.Error(['Light Brightness: Invalid/unexpected response'])
                            try:
                                self.WriteStatus('LightEffect', states[state['effect']], lightID)
                            except KeyError:
                                self.Error(['Light Effect: Invalid/unexpected response'])
                            try:
                                self.WriteStatus('LightSaturation', state['sat'], lightID)
                            except KeyError:
                                self.Error(['Light Saturation: Invalid/unexpected response'])
                            try:
                                self.WriteStatus('LightMiredColorTemperature', state['ct'], lightID)
                            except KeyError:
                                self.Error(['Light Mired Color Temperature: Invalid/unexpected response'])
                            try:
                                self.WriteStatus('LightState', states[state['on']], lightID)
                            except KeyError:
                                self.Error(['Light State: Invalid/unexpected response'])

    def SetGroupBrightness(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 0 <= value <= 254 and self.token:
            self.__SetHelper('GroupBrightness', value, qualifier,
                             url='groups/{}/action'.format(qualifier['Group ID']),
                             data=json.dumps({"bri":value}).encode())
        else:
            self.Discard('Invalid Command for SetGroupBrightness')

    def UpdateGroupBrightness(self, value, qualifier):

        states = {
            True        : 'On',
            False       : 'Off',
            'none'      : 'None',
            'colorloop' : 'Color Loop'
        }

        if not self.token:
            self.getToken(value, qualifier)

        res = self.__UpdateHelper('GroupBrightness', value, qualifier, url='groups')
        if res:
            try:
                groups = json.loads(res)
            except (TypeError, ValueError):
                self.Error(['Group: Invalid/unexpected response'])
            else:
                for group in groups:
                    try:
                        state = groups[group]['action']
                        groupID = {'Group ID': int(group)}
                    except(TypeError, ValueError, KeyError):
                        self.Error(['Group: Invalid/unexpected response'])
                    else:
                        try:
                            self.WriteStatus('GroupBrightness', state['bri'], groupID)
                        except KeyError:
                            self.Error(['Group Brightness: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('GroupHue', state['hue'], groupID)
                        except KeyError:
                            self.Error(['Group Hue: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('GroupEffect', states[state['effect']], groupID)
                        except KeyError:
                            self.Error(['Group Effect: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('GroupSaturation', state['sat'], groupID)
                        except KeyError:
                            self.Error(['Group Saturation: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('GroupMiredColorTemperature', state['ct'], groupID)
                        except KeyError:
                            self.Error(['Group Mired Color Temperature: Invalid/unexpected response'])
                        try:
                            self.WriteStatus('GroupState', states[state['on']], groupID)
                        except KeyError:
                            self.Error(['Group State: Invalid/unexpected response'])

    def SetGroupEffect(self, value, qualifier):

        states = {
            'None'       : 'none',
            'Color Loop' : 'colorloop'
        }

        if not self.token:
            self.getToken(value, qualifier)

        self.__SetHelper('GroupEffect', value, qualifier, url='groups/{}/action'.format(qualifier['Group ID']),
                         data=json.dumps({"effect":"{}".format(states[value])}).encode())

    def UpdateGroupEffect(self, value, qualifier):

        self.UpdateGroupBrightness(value, qualifier)

    def SetGroupHue(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)
        if 0 <= value <= 65535:
            self.__SetHelper('GroupHue', value, qualifier,
                             url='groups/{}/action'.format(qualifier['Group ID']),
                             data=json.dumps({"hue":value}).encode())
        else:
            self.Discard('Invalid Command for SetGroupHue')

    def UpdateGroupHue(self, value, qualifier):

        self.UpdateGroupBrightness(value, qualifier)

    def SetGroupMiredColorTemperature(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 153 <= value <= 500:
            self.__SetHelper('GroupMiredColorTemperature', value, qualifier, 
                              url='groups/{}/action'.format(qualifier['Group ID']),
                              data=json.dumps({"ct":value}).encode())
        else:
            self.Discard('Invalid Command for SetGroupMiredColorTemperature')

    def UpdateGroupMiredColorTemperature(self, value, qualifier):

        self.UpdateGroupBrightness(value, qualifier)

    def SetGroupSaturation(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 0 <= value <= 254:
            self.__SetHelper('GroupSaturation', value, qualifier,
                             url='groups/{}/action'.format(qualifier['Group ID']),
                             data=json.dumps({"sat":value}).encode())
        else:
            self.Discard('Invalid Command for SetGroupSaturation')

    def UpdateGroupSaturation(self, value, qualifier):

        self.UpdateGroupBrightness(value, qualifier)

    def SetGroupState(self, value, qualifier):

        states = {
            'On'  : True,
            'Off' : False
        }

        if not self.token:
            self.getToken(value, qualifier)

        self.__SetHelper('GroupState', value, qualifier, url='groups/{}/action'.format(qualifier['Group ID']),
                         data=json.dumps({"on":states[value]}).encode())

    def UpdateGroupState(self, value, qualifier):

        self.UpdateGroupBrightness(value, qualifier)

    def SetGroupTransitionTime(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if value >= 0:
            self.__SetHelper('GroupTransitionTime', value, qualifier,
                                 url='groups/{}/action'.format(qualifier['Group ID']),
                                 data=json.dumps({"transitiontime":value/100}).encode())
        else:
            self.Discard('Invalid Command for SetGroupTransitionTime')

    def SetLightBrightness(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 1 <= value <= 254:
            self.__SetHelper('LightBrightness', value, qualifier,
                             url='lights/{}/state'.format(qualifier['Light ID']),
                             data=json.dumps({"bri":value}).encode())
        else:
            self.Discard('Invalid Command for SetLightBrightness')

    def SetLightEffect(self, value, qualifier):

        states = {
            'None'       : 'none',
            'Color Loop' : 'colorloop'
        }

        if not self.token:
            self.getToken(value, qualifier)
        self.__SetHelper('LightEffect', value, qualifier, url='lights/{}/state'.format(qualifier['Light ID']),
                         data=json.dumps({"effect":"{}".format(states[value])}).encode())

    def SetLightHue(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 0 <= value <= 65535:
            self.__SetHelper('LightHue', value, qualifier,
                             url='lights/{}/state'.format(qualifier['Light ID']),
                             data=json.dumps({"hue":value}).encode())
        else:
            self.Discard('Invalid Command for SetLightHue')

    def SetLightMiredColorTemperature(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 153 <= value <= 500:
            self.__SetHelper('LightMiredColorTemperature', value, qualifier,
                             url='lights/{}/state'.format(qualifier['Light ID']),
                             data=json.dumps({"ct":value}).encode())
        else:
            self.Discard('Invalid Command for SetLightMiredColorTemperature')

    def SetLightSaturation(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if 0 <= value <= 254:
            self.__SetHelper('LightSaturation', value, qualifier,
                             url='lights/{}/state'.format(qualifier['Light ID']),
                             data=json.dumps({"sat":value}).encode())
        else:
            self.Discard('Invalid Command for SetLightSaturation')

    def SetLightState(self, value, qualifier):

        states = {
            'On'  : True,
            'Off' : False
        }

        if not self.token:
            self.getToken(value, qualifier)

        self.__SetHelper('LightState', value, qualifier, url='lights/{}/state'.format(qualifier['Light ID']),
                         data=json.dumps({"on":states[value]}).encode())

    def SetLightTransitionTime(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        if value >= 0:
            self.__SetHelper('LightTransitionTime', value, qualifier,
                                 url='lights/{}/state'.format(qualifier['Light ID']),
                                 data=json.dumps({"transitiontime":value/100}).encode())
        else:
            self.Discard('Invalid Command for SetLightTransitionTime')

    def SetSceneRecall(self, value, qualifier):

        if not self.token:
            self.getToken(value, qualifier)

        group_id = qualifier['Group ID']
        identifier_val = qualifier['Identifier']
        if group_id and identifier_val:
            self.__SetHelper('SceneRecall', value, qualifier,
                                url='groups/{}/action'.format(group_id),
                                data=json.dumps({"scene":identifier_val}).encode(encoding='iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}api/{}/{}'.format(self.RootURL, self.token, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=5)
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

        if not self.token:
            url = '{}api'.format(self.RootURL, url)
        else:
            url = '{}api/{}/{}'.format(self.RootURL, self.token, url)

        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
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

        self.token = ''
        
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