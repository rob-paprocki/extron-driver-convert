from extronlib.system import Wait, ProgramLog
import re
import base64
import json
import urllib.error
import urllib.request
import base64
import hmac
import hashlib
import time


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActionSet': {'Status': {}},
            'Lighting': {'Parameters': ['Light ID'], 'Status': {}},
            'LightingLevel': {'Parameters': ['Light ID'], 'Status': {}},
            'LightingRemoveEmergency': {'Parameters': ['Light ID'], 'Status': {}},
            'LightingSetEmergency': {'Parameters': ['Light ID', 'Timeout', 'Light Level'], 'Status': {}},
            'LightSensor': {'Parameters': ['Sensor ID'], 'Status': {}},
            'MotionSensor': {'Parameters': ['Sensor ID'], 'Status': {}},
            'Relay': {'Parameters': ['Relay ID'], 'Status': {}},
            'SpaceLighting': {'Parameters': ['Space ID'], 'Status': {}},
            'SpaceLightingLevel': {'Parameters': ['Space ID'], 'Status': {}},
            'SpaceMode': {'Parameters': ['Space ID'], 'Status': {}},
            'SpaceSync': {'Status': {}},
            'TemperatureSensor': {'Parameters': ['Sensor ID', 'Degrees'], 'Status': {}},
        }

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.jti = 0
        self.jti_index = 0
        self.jti_count = 0
        self._ApplicationKey = ''


    @property
    def ApplicationKey(self):
        return self._ApplicationKey

    @ApplicationKey.setter
    def ApplicationKey(self, value):
        self._ApplicationKey = value

    def reset_jti(self):
        self.jti = 0
        self.jti_index = 0

    def get_jti(self):
        jti = (self.jti_index * 1000000) + self.jti
        self.jti += 1
        return jti

    def auth_join(self, a, b):
        return b'.'.join([a, b])

    def b64_encode(self, value):
        return base64.urlsafe_b64encode(value).replace(b'=', b'')

    def hmac_sha256(self, key, message):
        return self.b64_encode(hmac.new(key.encode(), message, hashlib.sha256).digest())

    def generate_jwt(self, jti, app_key):
        header = b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'  # base64URLEncode({"typ":"JWT","alg":"HS256"})
        time_value = int(time.monotonic())  # this is used to define issued time, which is required in the authentication token
        payload = self.b64_encode(json.dumps({"iat": time_value, "jti": jti}).encode())
        header_payload = self.auth_join(header, payload)
        hash256 = self.hmac_sha256(app_key, header_payload)
        jwt_auth = self.auth_join(header_payload, hash256)
        return jwt_auth.decode()

    def SetActionSet(self, value, qualifier):

        if 1 <= value <= 65535:
            CmdString = 'actionsets/{}/execute'.format(value)
            self.__SetHelper('ActionSet', value, qualifier, url=CmdString)
        else:
            self.Discard('Invalid Command for SetActionSet')

    def SetLighting(self, value, qualifier):

        ValueStateValues = {
            'On': 'turnon',
            'Off': 'turnoff'
        }

        light = qualifier['Light ID']
        if 1 <= light <= 65535:
            CmdString = 'lights/{}/{}'.format(light, ValueStateValues[value])
            self.__SetHelper('Lighting', value, qualifier, url=CmdString)
        else:
            self.Discard('Invalid Command for SetLighting')

    def UpdateLighting(self, value, qualifier):

        light = qualifier['Light ID']
        if 1 <= light <= 65535:
            res = self.__UpdateHelper('Lighting', value, qualifier, url='lights/{}'.format(light))
            if res:
                try:
                    value = json.loads(res)
                except(ValueError, TypeError):
                    self.Error(['Lighting: Invalid/unexpected response'])
                else:
                    try:
                        self.WriteStatus('Lighting', value['state'], qualifier)
                    except KeyError:
                        self.Error(['Lighting: Invalid/unexpected response'])

                    try:
                        self.WriteStatus('LightingLevel', int(value['level'] / 100), qualifier)
                    except (KeyError, ValueError):
                        self.Error(['LightingLevel: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLighting')

    def SetLightingLevel(self, value, qualifier):

        light = qualifier['Light ID']
        if 0 <= value <= 100 and 1 <= light <= 65535:
            CmdString = 'lights/{}/lighting'.format(light)
            data_string = json.dumps({"level": value * 100}).encode()
            self.__SetHelper('LightingLevel', value, qualifier, url=CmdString, data=data_string)
        else:
            self.Discard('Invalid Command for SetLightingLevel')

    def UpdateLightingLevel(self, value, qualifier):

        self.UpdateLighting(value, qualifier)

    def SetLightingRemoveEmergency(self, value, qualifier):

        light = qualifier['Light ID']
        if 1 <= light <= 65535:
            self.__SetHelper('LightingRemoveEmergency', value, qualifier, url='lights/{}/emergency-settings'.format(light))
        else:
            self.Discard('Invalid Command for SetLightingRemoveEmergency')

    def SetLightingSetEmergency(self, value, qualifier):

        light = qualifier['Light ID']
        timeout = int(qualifier['Timeout'])
        level = qualifier['Light Level']
        if 1 <= light <= 65535 and 1 <= level <= 100 and timeout in [0, 5000, 10000, 15000, 20000, 25000, 30000]:
            CmdString = 'lights/{}/emergency-settings'.format(light)
            data_string = json.dumps({"timeout": timeout, "lightLevel": level * 100}).encode()
            self.__SetHelper('LightingSetEmergency', value, qualifier, url=CmdString, data=data_string)
        else:
            self.Discard('Invalid Command for SetLightingSetEmergency')

    def UpdateLightSensor(self, value, qualifier):

        sensor = qualifier['Sensor ID']
        if 1 <= sensor <= 65535:
            CmdString = 'lightsensors/{}'.format(sensor)
            res = self.__UpdateHelper('LightSensor', value, qualifier, url=CmdString)
            if res:
                try:
                    value = json.loads(res)['sensorLevel']
                    self.WriteStatus('LightSensor', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Light Sensor: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLightSensor')

    def UpdateMotionSensor(self, value, qualifier):

        sensor = qualifier['Sensor ID']
        if 1 <= sensor <= 65535:
            CmdString = 'motionsensors/{}'.format(sensor)
            res = self.__UpdateHelper('MotionSensor', value, qualifier, url=CmdString)
            if res:
                try:
                    value = json.loads(res)['state'].lower()
                    if 'vac' in value:
                        self.WriteStatus('MotionSensor', 'Vacant', qualifier)
                    elif 'occ' in value:
                        self.WriteStatus('MotionSensor', 'Occupied', qualifier)
                except (ValueError, IndexError):
                    self.Error(['Motion Sensor: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMotionSensor')

    def SetRelay(self, value, qualifier):

        relay = qualifier['Relay ID']
        if 1 <= relay <= 65535 and value in ['Open', 'Close']:
            CmdString = 'relays/{}/{}'.format(relay, value.lower())
            self.__SetHelper('Relay', value, qualifier, url=CmdString)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        relay = qualifier['Relay ID']
        if 1 <= relay <= 65535:
            CmdString = 'relays/{}'.format(relay)
            res = self.__UpdateHelper('Relay', value, qualifier, url=CmdString)
            if res:
                try:
                    value = {'o': 'Open', 'c': 'Close'}[json.loads(res)['state'][0].lower()]
                    self.WriteStatus('Relay', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Relay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRelay')

    def SetSpaceLighting(self, value, qualifier):

        ValueStateValues = {
            'On': 'turnon',
            'Off': 'turnoff'
        }

        space = qualifier['Space ID']
        if 1 <= space <= 65535:
            CmdString = 'spaces/{}/{}'.format(space, ValueStateValues[value])
            self.__SetHelper('SpaceLighting', value, qualifier, url=CmdString)
        else:
            self.Discard('Invalid Command for SetSpaceLighting')

    def UpdateSpaceLighting(self, value, qualifier):
        self.UpdateSpaceMode(value, qualifier)

    def SetSpaceLightingLevel(self, value, qualifier):

        space = qualifier['Space ID']
        if 1 <= value <= 100 and 1 <= space <= 65535:
            CmdString = 'spaces/{}/lighting'.format(space)
            data_string = json.dumps({"level": value * 100}).encode()
            self.__SetHelper('SpaceLightingLevel', value, qualifier, url=CmdString, data=data_string)
        else:
            self.Discard('Invalid Command for SetSpaceLightingLevel')

    def UpdateSpaceLightingLevel(self, value, qualifier):
        self.UpdateSpaceMode(value, qualifier)

    def UpdateSpaceMode(self, value, qualifier):

        if self.jti_count == 1500:
            self.reset_jti()
        self.jti_count += 1

        CmdString = 'spaces'
        res = self.__UpdateHelper('SpaceMode', value, qualifier, url=CmdString)
        if res:
            try:
                spaces = json.loads(res)['list']
            except(ValueError, TypeError):
                self.Error(['SpaceMode: Invalid/unexpected response'])
            else:
                for space in spaces:
                    try:
                        self.WriteStatus('SpaceMode', space['mode'], {'Space ID': space['id']})
                    except KeyError:
                        self.Error(['SpaceMode: Invalid/unexpected response'])

                    try:
                        self.WriteStatus('SpaceLighting', space['state'], {'Space ID': space['id']})
                    except KeyError:
                        self.Error(['SpaceLighting: Invalid/unexpected response'])

                    try:
                        self.WriteStatus('SpaceLightingLevel', int(space['level'] / 100), {'Space ID': space['id']})
                    except (KeyError, ValueError):
                        self.Error(['SpaceLightingLevel: Invalid/unexpected response'])

    def SetSpaceSync(self, value, qualifier):

        self.__SetHelper('SpaceSync', value, qualifier, url='spaces/synchronize')

    def UpdateTemperatureSensor(self, value, qualifier):

        sensor = qualifier['Sensor ID']
        degree = qualifier['Degrees']
        if 1 <= sensor <= 65535 and degree in ['Fahrenheit', 'Celsius']:
            CmdString = 'temperaturesensors/{}'.format(sensor)
            res = self.__UpdateHelper('TemperatureSensor', value, qualifier, url=CmdString)
            if res:
                try:
                    value = json.loads(res)['temperature']
                    if degree == 'Celsisu':
                        self.WriteStatus('TemperatureSensor', round(value, 1), qualifier)
                    else:
                        self.WriteStatus('TemperatureSensor', round((value*(9/5))+32, 1), qualifier)
                except (ValueError, IndexError):
                    self.Error(['Temperature Sensor: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemperatureSensor')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}api/{}'.format(self.RootURL, url)

        if data:
            headers = {
                'Authorization': 'Bearer {}'.format(self.generate_jwt(self.get_jti(), self.ApplicationKey)),
                'Content-Type': 'application/json'
            }
        else:
            headers = {
                'Authorization': 'Bearer {}'.format(self.generate_jwt(self.get_jti(), self.ApplicationKey)),
                'Content-Length': 0,
                'Content-Type': 'application/json'
            }

        method = 'POST' if command != 'LightingRemoveEmergency' else 'DELETE'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            if command == 'ActionSet':
                res = urllib.request.urlopen(my_request, timeout=5)
            else:
                res = urllib.request.urlopen(my_request)

        except urllib.error.HTTPError as err:
            if err.code in (400, 401):
                self.jti_index += 1
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        url = '{}api/{}'.format(self.RootURL, url)
        headers = {
            'Authorization': 'Bearer {}'.format(self.generate_jwt(self.get_jti(), self.ApplicationKey)),
            'Content-Type': 'application/json'
        }

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            res = urllib.request.urlopen(my_request)
        except urllib.error.HTTPError as err:
            if err.code in (400, 401):
                self.jti_index += 1
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.jti_count = 0

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
