import re
import base64
import json
import urllib.error
import urllib.request

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15

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
        self._APIKey = ''
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ClimateHold': {'Status': {}},
            'CurrentHumidityLevel': {'Status': {}},
            'CurrentTemperature': {'Status': {}},
            'DeleteVacation': {'Status': {}},
            'FanMinOnTime': {'Status': {}},
            'FanMode': {'Status': {}},
            'HoldTemperature': {'Parameters': ['Heat Hold Temperature', 'Cool Hold Temperature'], 'Status': {}},
            'HumidityLevel': {'Status': {}},
            'HVACMode': {'Status': {}},
            'RefreshToken': {'Status': {}},
            'RequestPin': {'Status': {}},
            'ResumeProgram': {'Status': {}},
            'SendMessage': {'Status': {}},
        }

        self.runtime_dict = {}
        self.event_dict = {}
        self.settings_dict = {}
        self._APIKey = ''
        self.auth_code = ''
        self.pin = ''
        self.access_token = ''
        self.refresh_token = ''


    @property
    def APIKey(self):
        return self._APIKey

    @APIKey.setter
    def APIKey(self, value):
        self._APIKey = value

    def UpdateRequestPin(self, value, qualifier):

        url = 'authorize?response_type=ecobeePin&client_id={}&scope=smartWrite'.format(self._APIKey)
        res = self.__UpdateHelper('RequestPin', None, None, url)
        if res:
            try:
                self.auth_code = json.loads(res)['code']
                self.pin = json.loads(res)['ecobeePin']
                self.SetRequestTokens(None, None)
            except:
                self.Error(['Request PIN Failed'])
        else:
            self.Error(['Request PIN Failed'])

    def SetRequestTokens(self, value, qualifier):

        url = 'token?grant_type=ecobeePin&code={}&client_id={}'.format(self.auth_code, self._APIKey)
        res = self.__SetHelper('RequestTokens', None, None, url)
        if res:
            try:
                self.access_token = json.loads(res)['access_token']
                self.refresh_token = json.loads(res)['refresh_token']
                self.pin = ''
            except:
                self.Error(['Request Tokens Failed'])
        else:
            self.Error(['Request Tokens Failed'])

    def SetClimateHold(self, value, qualifier):

        ValueStateValues = {
            'Away': 'away',
            'Home': 'home',
            'Sleep': 'sleep'
        }

        url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"setHold","params":{{"holdType":"nextTransition","holdClimateRef":"{0}"}}}}]}}'.format(ValueStateValues[value])

        self.__SetHelper('ClimateHold', value, qualifier, url)

    def UpdateCurrentTemperature(self, value, qualifier):

        ClimateHoldValues = {
            'away': 'Away',
            'home': 'Home',
            'sleep': 'Sleep'
        }
        FanModeValues = {
            'auto': 'Auto',
            'minontime': 'Min On Time',
            'on': 'On'
        }
        HVACModeValues = {
            'auto': 'Auto',
            'auxHeatOnly': 'Aux Heat Only',
            'cool': 'Cool',
            'heat': 'Heat',
            'off': 'Off'
        }
        if self.access_token:
            url = '1/thermostat?format=json&body={"selection":{"selectionType":"registered","selectionMatch":"","includeRuntime":true,"includeEvents":true,"includeSettings":true}}'
            res = self.__UpdateHelper('CurrentTemperature', value, qualifier, url)
            if res:
                try:
                    self.runtime_dict = json.loads(res)['thermostatList'][0]['runtime']
                    self.event_dict = json.loads(res)['thermostatList'][0]['events'][0]
                    self.settings_dict = json.loads(res)['thermostatList'][0]['settings']
                except (KeyError, IndexError):
                    self.Error(['Current Temperature: Invalid/unexpected response of dictionaries initialization'])
                try:
                    curr_humidity_value = self.runtime_dict['actualHumidity']
                    self.WriteStatus('CurrentHumidityLevel', curr_humidity_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of curr_humidity_value'])
                try:
                    curr_temp_value = self.runtime_dict['actualTemperature'] / 10
                    self.WriteStatus('CurrentTemperature', curr_temp_value, qualifier)
                except (KeyError, ValueError):
                    self.Error(['Current Temperature: Invalid/unexpected response of curr_temp_value'])
                try:
                    climate_hold_value = ClimateHoldValues[self.event_dict['holdClimateRef']]
                    self.WriteStatus('ClimateHold', climate_hold_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of climate_hold_value'])
                try:
                    fanMinOnTime_value = self.event_dict['fanMinOnTime']
                    self.WriteStatus('FanMinOnTime', fanMinOnTime_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of fanMinOnTime_value'])
                try:
                    fanMode_value = FanModeValues[self.event_dict['fan']]
                    self.WriteStatus('FanMode', fanMode_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of fanMode_value'])
                try:
                    humidity_level_value = self.runtime_dict['desiredHumidity']
                    self.WriteStatus('HumidityLevel', humidity_level_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of humidity_level_value'])
                try:
                    hvacMode_value = HVACModeValues[self.settings_dict['hvacMode']]
                    self.WriteStatus('HVACMode', hvacMode_value, qualifier)
                except (KeyError):
                    self.Error(['Current Temperature: Invalid/unexpected response of hvacMode_value'])
        else:
            self.UpdateRequestPin(None, None)
            self.Error(['Current Temperature: Invalid Access Token.'])

    def SetDeleteVacation(self, value, qualifier):

        url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"deleteVacation","params":{{"name":"{0}"}}}}]}}'.format(value)

        self.__SetHelper('DeleteVacation', value, qualifier, url)

    def SetFanMinOnTime(self, value, qualifier):

        if 1 <= value <= 60:
            url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"settings":{{"fanMinOnTime":{0}}}}}'.format(value)
            self.__SetHelper('FanMinOnTime', value, qualifier, url)
        else:
            self.Discard('Invalid Command for SetFanMinOnTime')

    def SetFanMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            'Min On Time': 'minontime',
            'On': 'on'
        }
        if self.event_dict:
            url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"setHold","params":{{"holdType":"nextTransition","heatHoldTemp":{0},"coolHoldTemp":{1},"fan":"{2}"}}}}]}}'\
                .format(self.event_dict['heatHoldTemp'], self.event_dict['coolHoldTemp'], ValueStateValues[value])
            self.__SetHelper('FanMode', value, qualifier, url)

    def SetHoldTemperature(self, value, qualifier):

        heat_temp = qualifier['Heat Hold Temperature']
        cool_temp = qualifier['Cool Hold Temperature']
        if heat_temp in range(45, 74) and cool_temp in range(65, 93):
            url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"setHold","params":{{"holdType":"nextTransition","heatHoldTemp":{0},"coolHoldTemp":{1}}}]}}'.format(heat_temp * 10, cool_temp * 10)
            self.__SetHelper('HoldTemperature', value, qualifier, url)
        else:
            self.Discard('Invalid Command for SetHoldTemperature')

    def SetHumidityLevel(self, value, qualifier):

        if 1 <= value <= 100:
            url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"settings":{{"humidity":{0}}}}}'.format(value)
            self.__SetHelper('HumidityLevel', value, qualifier, url)
        else:
            self.Discard('Invalid Command for SetHumidityLevel')

    def SetHVACMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            'Aux Heat Only': 'auxHeatOnly',
            'Cool': 'cool',
            'Heat': 'heat',
            'Off': 'off'
        }

        url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"settings":{{"hvacMode":"{0}"}}}}'.format(ValueStateValues[value])
        self.__SetHelper('HVACMode', value, qualifier, url)

    def UpdateRefreshToken(self, value, qualifier):

        url = 'token?grant_type=refresh_token&refresh_token={}&client_id={}'.format(self.refresh_token, self._APIKey)
        res = self.__SetHelper('RefreshToken', None, None, url)
        if res:
            try:
                self.access_token = json.loads(res)['access_token']
                self.refresh_token = json.loads(res)['refresh_token']
            except:
                self.Error(['Refresh Tokens Failed'])
        else:
            self.Error(['Refresh Tokens Failed'])

    def SetResumeProgram(self, value, qualifier):

        ValueStateValues = {
            'All Events': 'true',
            'Next Event': 'false'
        }

        url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"resumeProgram","params":{{"resumeAll":{0}}}}}]}}'.format(ValueStateValues[value])
        self.__SetHelper('ResumeProgram', value, qualifier, url)

    def SetSendMessage(self, value, qualifier):

        url = '1/thermostat?format=json&body={{"selection":{{"selectionType":"registered","selectionMatch":""}},"functions":[{{"type":"sendMessage","params":{{"text":"{}"}}}}]}}'.format(value)
        self.__SetHelper('SendMessage', value, qualifier, url)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode('iso-8859-1')

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        #url = '{}{}'.format(self.RootURL.replace('http', 'https').replace(':443', ''), url)
        url = '{}{}'.format(self.RootURL, url) # use this url to test with emulator  
        if command == 'RefreshToken' or 'RequestTokens':
            headers = {}
        else:
            headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(self.access_token)}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        #url = '{}{}'.format(self.RootURL.replace('http', 'https').replace(':443', ''), url)
        url = '{}{}'.format(self.RootURL, url) # use this url to test with emulator  
        if command == 'RequestPin':
            headers = {}
        else:
            headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(self.access_token)}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.runtime_dict = {}
        self.event_dict = {}
        self.settings_dict = {}
        self._APIKey = ''
        self.auth_code = ''
        self.pin = ''
        self.access_token = ''
        self.refresh_token = ''
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
        self.ConnectionType = 'HTTPS'
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
