from extronlib.system import GetUnverifiedContext
import re
import json
import base64
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port == 443:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self._ClientID =''
        self._ClientSecret = ''
        self.IPAddress = ipAddress
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.Models = {
        'Healthy Home Coach': self._homecoach,
        'Weather Station': self._station
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CO2': {'Parameters': ['Device ID'], 'Status': {}},
            'GetStatus': {'Status': {}},
            'Login': {'Status': {}},
            'HealthIndex': {'Parameters': ['Device ID'], 'Status': {}},
            'Humidity': {'Parameters': ['Device ID'], 'Status': {}},
            'Noise': {'Parameters': ['Device ID'], 'Status': {}},
            'Pressure': {'Parameters': ['Device ID'], 'Status': {}},
            'PressureAbsolute': {'Parameters': ['Device ID'], 'Status': {}},
            'PressureTrend': {'Parameters': ['Device ID'], 'Status': {}},
            'Temperature': {'Parameters': ['Device ID'], 'Status': {}},
            'TemperatureTrend': {'Parameters': ['Device ID'], 'Status': {}},
            'WifiStatus': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self._access_token = ''
        self._refresh_token = ''

        self._last_update = 0

        self._id_regex = re.compile('\"_id\":\s?\"([0-9A-Za-z\:]+)\",')
        self._wifi_regex = re.compile('\"wifi_status\":\s?(\d+),')
        self._dashboard_regex = re.compile('\"dashboard_data\":\s?\{(.*)\}')
        self._health_index_regex = re.compile('\"health_idx\":\s?([0-4]),')
        self._temperature_regex = re.compile('\"Temperature\":\s?([\d\.]+),')
        self._temp_trend_regex = re.compile('\"temp_trend\":\s?\"(up|down|stable)\",')
        self._humidity_regex = re.compile('\"Humidity\":\s?(\d+),')
        self._pressure_regex = re.compile('\"Pressure\":\s?([\d\.]+),')
        self._pressure_abs_regex = re.compile('\"AbsolutePressure\":\s?([\d\.]+),')
        self._pressure_trend_regex = re.compile('\"pressure_trend\":\s?\"(up|down|stable)\"')
        self._noise_regex = re.compile('\"Noise\":\s?(\d+),')
        self._co2_regex = re.compile('\"CO2\":\s?(\d+),')

    @property
    def ClientID(self):
        return self._ClientID

    @ClientID.setter
    def ClientID(self, value):
        self._ClientID = value

    @property
    def ClientSecret(self):
        return self._ClientSecret

    @ClientSecret.setter
    def ClientSecret(self, value):
        self._ClientSecret = value

    def SetLogin(self, value, qualifier):

        data = "grant_type=password&client_id={}&client_secret={}&username={}&password={}&scope={}".format(
            self._ClientID, self._ClientSecret, self.deviceUsername, self.devicePassword, self._scope)

        res = self.__SetHelper('Login', value, qualifier, url='oauth2/token', data=data.encode())
        if res:
            try:
                self._access_token = json.loads(res)['access_token']
                self._refresh_token = json.loads(res)['refresh_token']
            except:
                self.Error(['Login: Invalid/unexpected response'])
        else:
            self.Error(['Login Failed'])

    def SetRefreshToken(self, value, qualifier):

        self._last_update = 0
        data = "grant_type=refresh_token&client_id={}&client_secret={}&refresh_token={}".format(
            self._ClientID, self._ClientSecret, self._refresh_token)

        if self._refresh_token:
            self.__SetHelper('RefreshToken', value, qualifier, url='oauth2/token', data=data.encode())
        else:
            self.Error(['Refresh Token unavailable'])

    def UpdateGetStatus(self, value, qualifier):

        health_states = {
            '0': 'Healthy',
            '1': 'Fine',
            '2': 'Fair',
            '3': 'Poor',
            '4': 'Unhealthy'
        }

        if self._access_token:

            if self._last_update == 2:#1000
                self.SetRefreshToken(None, None)
            self._last_update += 1

            res = self.__UpdateHelper('GetStatus', value, qualifier, url=self._get_status)
            if res:
                try:
                    new_list = []
                    for regex in [self._id_regex, self._wifi_regex, self._dashboard_regex]:
                        if re.findall(regex, res):
                            new_list.append(re.findall(regex, res))
                        else:
                            new_list.append([None])

                    deviceList = {i: '{}${}'.format(*j).split('$') for i in new_list[0] for j in [list(k) for k in zip(*new_list[1:])]}
                    for device in deviceList:
                        if device:
                            try:
                                wifi_status = 'Good' if int(deviceList[device][0]) <= 56 else 'Average' if int(deviceList[device][0]) <= 71 else 'Bad'
                                self.WriteStatus('WifiStatus', wifi_status, {'Device ID': device})
                            except:
                                self.Error(['Wifi Status: Invalid/unexpected response'])
                            dashboard, dashboard_data = deviceList[device][1], []
                            for regex in [self._co2_regex, self._humidity_regex, self._noise_regex, self._temperature_regex, self._temp_trend_regex]:
                                if re.search(regex, dashboard):
                                    dashboard_data.append(re.search(regex, dashboard).group(1))
                                else:
                                    dashboard_data.append(None)

                            try:
                                if dashboard_data[0]:
                                    self.WriteStatus('CO2', int(dashboard_data[0]), {'Device ID': device})
                                else:
                                    self.Error(['CO2: No Data Found'])
                            except:
                                self.Error(['CO2: Invalid/unexpected response'])

                            try:
                                if dashboard_data[1]:
                                    self.WriteStatus('Humidity', int(dashboard_data[1]), {'Device ID': device})
                                else:
                                    self.Error(['Humidity: No Data Found'])
                            except:
                                self.Error(['Humidity: Invalid/unexpected response'])

                            try:
                                if dashboard_data[2]:
                                    self.WriteStatus('Noise', int(dashboard_data[2]), {'Device ID': device})
                                else:
                                    self.Error(['Noise: No Data Found'])
                            except:
                                self.Error(['Noise: Invalid/unexpected response'])

                            try:
                                if dashboard_data[3]:
                                    self.WriteStatus('Temperature', float(dashboard_data[3]), {'Device ID': device})
                                else:
                                    self.Error(['Temperature: No Data Found'])
                            except:
                                self.Error(['Temperature: Invalid/unexpected response'])

                            try:
                                if dashboard_data[4]:
                                    self.WriteStatus('TemperatureTrend', dashboard_data[4].title(), {'Device ID': device})
                                else:
                                    self.Error(['Temperature Trend: No Data Found'])
                            except:
                                self.Error(['Temperature Trend: Invalid/unexpected response'])

                            if self._scope == "read_homecoach":
                                try:
                                    if re.search(self._health_index_regex, dashboard):
                                        health_index = re.search(self._health_index_regex, dashboard).group(1)
                                    else:
                                        health_index = None

                                    if health_index:
                                        self.WriteStatus('HealthIndex', health_states[str(health_index)], {'Device ID': device})
                                    else:
                                        self.Error(['Health Index: No Data Found'])
                                except:
                                    self.Error(['Health Index: Invalid/unexpected response'])
                            else:
                                pressure_data = []
                                for regex in [self._pressure_regex, self._pressure_abs_regex, self._pressure_trend_regex]:
                                    if re.search(regex, dashboard):
                                        pressure_data.append(re.search(regex, dashboard).group(1))
                                    else:
                                        pressure_data.append(None)

                                try:
                                    if pressure_data[0]:
                                        self.WriteStatus('Pressure', float(pressure_data[0]), {'Device ID': device})
                                    else:
                                        self.Error(['Pressure: No Data Found'])
                                except:
                                    self.Error(['Pressure: Invalid/unexpected response'])

                                try:
                                    if pressure_data[1]:
                                        self.WriteStatus('PressureAbsolute', float(pressure_data[1]), {'Device ID': device})
                                    else:
                                        self.Error(['Pressure Absolute: No Data Found'])
                                except:
                                    self.Error(['Pressure Absolute: Invalid/unexpected response'])

                                try:
                                    if pressure_data[2]:
                                        self.WriteStatus('PressureTrend', pressure_data[2].title(), {'Device ID': device})
                                    else:
                                        self.Error(['Pressure Trend: No Data Found'])
                                except:
                                    self.Error(['Pressure Trend: Invalid/unexpected response'])

                except (ValueError, IndexError):
                    self.Error(['Get Status: Invalid/unexpected response'])
        else:
            self.SetLogin(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        if 'error' in res:
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        # needed in SetHelper to make sure the counterFlag gets trigger
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False


        root = self.RootURL[7:-1].replace('.', '').replace(':', '')
        hostname = self.RootURL[:-1] if root.isdigit() else 'https:{}'.format(self.RootURL.split(':')[1])

        url = '{}/{}'.format(hostname, url)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
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

        root = self.RootURL[7:-1].replace('.', '').replace(':', '')
        hostname = self.RootURL[:-1] if root.isdigit() else 'https:{}'.format(self.RootURL.split(':')[1])

        url = '{}/api/{}?access_token={}'.format(hostname, url, self._access_token)        
        my_request = urllib.request.Request(url, data=data)

        try:
            res = self.Opener.open(my_request)
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self._access_token = ''
        self._refresh_token = ''

    def _homecoach(self):

        self._scope = "read_homecoach"
        self._get_status = "gethomecoachsdata"

    def _station(self):

        self._scope = "read_station"
        self._get_status = "getstationsdata"

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
