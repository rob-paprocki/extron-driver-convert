import base64
import json
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
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AlertStatus': {'Parameters': ['Alert'], 'Status': {}},
            'CoolTemperature': { 'Status': {}},
            'FanSetting': { 'Status': {}},
            'FanState': { 'Status': {}},
            'HeatTemperature': { 'Status': {}},
            'SensorTemperature': {'Parameters': ['Sensor'], 'Status': {}},
            'SpaceTemperature': { 'Status': {}},
            'StatusQuery': { 'Status': {}},
            'TemperatureUnits': { 'Status': {}},
            'ThermostatMode': { 'Status': {}},
            'ThermostatState': { 'Status': {}},
        }

    def UpdateAlertStatus(self, value, qualifier):

        ValueStateValues = {
            True : 'Active',
            False: 'Not Active'
        }

        res = self.__UpdateHelper('AlertStatus', value, qualifier, url='query/alerts')
        if res:
            try:
                alerts = json.loads(res)['alerts']
                for alert in alerts:
                    self.WriteStatus('AlertStatus', ValueStateValues[alert['active']], {'Alert': alert['name']})
            except (KeyError, IndexError):
                self.Error(['Alert Status: Invalid/unexpected response'])

    def SetCoolTemperature(self, value, qualifier):
 
        heat = self.ReadStatus('HeatTemperature', None)

        if 0 <= value <= 100 and heat:
            self.__SetHelper('CoolTemperature', value, qualifier, url='control', data='heattemp={}&cooltemp={}'.format(heat, value).encode())
        else:
            self.Discard('Invalid Command for SetCoolTemperature')

    def SetFanSetting(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'On'  : '1'
        }

        if value in ValueStateValues:
            self.__SetHelper('FanSetting', value, qualifier, url='control', data='fan={}'.format(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetFanSetting')

    def SetHeatTemperature(self, value, qualifier):

        cool = self.ReadStatus('CoolTemperature', None)
        
        if 0 <= value <= 100 and cool:
            self.__SetHelper('HeatTemperature', value, qualifier, url='control', data='heattemp={}&cooltemp={}'.format(value, cool).encode())
        else:
            self.Discard('Invalid Command for SetHeatTemperature')

    def UpdateSensorTemperature(self, value, qualifier):
    
        res = self.__UpdateHelper('SensorTemperature', value, qualifier, url='query/sensors')
        if res:
            try:
                sensors = json.loads(res)['sensors']
                for sensor in sensors:
                    self.WriteStatus('SensorTemperature', int(sensor['temp']), {'Sensor': sensor['name']})
            except (KeyError, IndexError):
                self.Error(['Sensor Temperature: Invalid/unexpected response'])

    def UpdateStatusQuery(self, value, qualifier):

        fan_settings = {
            0: 'Auto',
            1: 'Off'
        }

        fan_states = {
            0: 'Off',
            1: 'On'
        }

        temp_units = {
            0: 'Fahrenheit',
            1: 'Celsius'
        }

        thermostat_modes = {
            0: 'Off',
            1: 'Heat',
            2: 'Cool',
            3: 'Auto'
        }

        thermostat_states = {
            0: 'Idle',
            1: 'Heating',
            2: 'Cooling',
            3: 'Lockout',
            4: 'Error'
        }

        res = self.__UpdateHelper('StatusQuery', value, qualifier, url='query/info')
        if res:
            value = json.loads(res)
            try:
                self.WriteStatus('CoolTemperature', int(value['cooltemp']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Cool Temperature: Invalid/unexpected response'])

            try:
                self.WriteStatus('FanSetting', fan_settings[value['fan']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Fan Setting: Invalid/unexpected response'])

            try:
                self.WriteStatus('FanState', fan_states[value['fanstate']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Fan State: Invalid/unexpected response'])

            try:
                self.WriteStatus('HeatTemperature', int(value['heattemp']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Heat Temperature: Invalid/unexpected response'])

            try:
                self.WriteStatus('SpaceTemperature', int(value['spacetemp']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Space Temperature: Invalid/unexpected response'])

            try:
                self.WriteStatus('TemperatureUnits', temp_units[value['tempunits']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Temperature Units: Invalid/unexpected response'])

            try:
                self.WriteStatus('ThermostatMode', thermostat_modes[value['mode']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Thermostat Mode: Invalid/unexpected response'])

            try:
                self.WriteStatus('ThermostatState', thermostat_states[value['state']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Thermostat State: Invalid/unexpected response'])
                
    def SetTemperatureUnits(self, value, qualifier):


        ValueStateValues = {
            'Fahrenheit': '0',
            'Celsius'   : '1'
        }

        if value in ValueStateValues:
            self.__SetHelper('TemperatureUnits', value, qualifier, url='settings', data='tempunits={}'.format(ValueStateValues[value]).encode())
        else:
            self.Discard('Invalid Command for SetTemperatureUnits')

    def SetThermostatMode(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0', 
            'Heat': '1',
            'Cool': '2',
            'Auto': '3'
        }

        heat = self.ReadStatus('HeatTemperature', None)
        cool = self.ReadStatus('CoolTemperature', None)
                                                            
        if value in ValueStateValues and heat and cool:
            if value == 'Auto' and abs(heat-cool) < 2: # based on customer feedback
                    self.Discard('Invalid Command for SetThermostatMode')
            else:
                self.__SetHelper('ThermostatMode', value, qualifier, url='control', data='mode={}&heattemp={}&cooltemp={}'.format(ValueStateValues[value], heat, cool).encode())
        else:
            self.Discard('Invalid Command for SetThermostatMode')

    def __CheckResponseForErrors(self, sourceCmdName, response):


        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True



        url = '{}{}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = urllib.request.urlopen(my_request)  # open() returns a http.client.HTTPResponse object if successful
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            res = urllib.request.urlopen(my_request)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            if command == 'StatusQuery':
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