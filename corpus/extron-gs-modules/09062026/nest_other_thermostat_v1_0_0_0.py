import re
import base64
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.connectionCounter = 15
        self.deviceUsername = 'Username'

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CoolStatus': {'Status': {}},
            'FanStatus': {'Status': {}},
            'FanTimerDuration': {'Status': {}},
            'HeatStatus': {'Status': {}},
            'Humidity': {'Status': {}},
            'HVACMode': {'Status': {}},
            'HVACStatus': {'Status': {}},
            'LockStatus': {'Status': {}},
            'TemperatureCelcius': {'Status': {}},
            'TemperatureFahrenheit': {'Status': {}},
            'TemperatureScale': {'Status': {}},
        }

    def UpdateCoolStatus(self, value, qualifier):

        CoolStatusCmdString = 'can_cool'
        res = self.__UpdateHelper('CoolStatus', value, qualifier, CoolStatusCmdString)
        if res:
            try:
                cool = re.search('can_cool=(true|false)', res)
                self.WriteStatus('CoolStatus', cool.group(1).title(), qualifier)
            except IndexError:
                self.Error(['Cool Status: Invalid/Unexpected Response'])

    def UpdateFanStatus(self, value, qualifier):

        FanStatusCmdString = 'has_fan'
        res = self.__UpdateHelper('FanStatus', value, qualifier, FanStatusCmdString)
        if res:
            try:
                fanvalue = re.search('has_fan=(true|false)', res)
                self.WriteStatus('FanStatus', fanvalue.group(1).title(), qualifier)
            except IndexError:
                self.Error(['Fan Status: Invalid/Unexpected Response'])

    def SetFanTimerDuration(self, value, qualifier):

        FanTimerDurationState = {
            '15': '15',
            '30': '30',
            '45': '45',
            '60': '60',
            '120': '120',
            '240': '240',
            '480': '480',
            '960': '960'
        }

        FanTimerDurationCmdString = 'fan_timer_duration/{0}'.format(FanTimerDurationState[value])
        self.__SetHelper('FanTimerDuration', value, qualifier, FanTimerDurationCmdString, None)

    def UpdateFanTimerDuration(self, value, qualifier):

        FanTimerDurationCmdString = 'fan_timer_duration'
        res = self.__UpdateHelper('FanTimerDuration', value, qualifier, FanTimerDurationCmdString)
        if res:
            try:
                fantimerduration = re.search('fan_timer_duration=(15|30|45|60|120|240|480|960)', res)
                self.WriteStatus('FanTimerDuration', fantimerduration.group(1), qualifier)
            except IndexError:
                self.Error(['Fan Timer Duration: Invalid/Unexpected Response'])

    def UpdateHeatStatus(self, value, qualifier):

        HeatStatusCmdString = 'can_heat'
        res = self.__UpdateHelper('HeatStatus', value, qualifier, HeatStatusCmdString)
        if res:
            try:
                heatvalue = re.search('can_heat=(true|false)', res)
                self.WriteStatus('HeatStatus', heatvalue.group(1).title(), qualifier)
            except IndexError:
                self.Error(['Heat Status: Invalid/Unexpected Response'])

    def UpdateHumidity(self, value, qualifier):

        HumidityCmdString = 'humidity'
        res = self.__UpdateHelper('Humidity', value, qualifier, HumidityCmdString)
        if res:
            try:
                humidity = re.search('humidity=([0-9]{1,3})', res)
                self.WriteStatus('Humidity', int(humidity.group(1)), qualifier)
            except IndexError:
                self.Error(['Humidity: Invalid/Unexpected Response'])

    def SetHVACMode(self, value, qualifier):

        HVACModeState = {
            'Heat': 'heat',
            'Cool': 'cool',
            'Heat-Cool': 'heat-cool',
            'Eco': 'eco',
            'Off': 'off'
        }

        HVACModeCmdString = 'hvac_mode/{0}'.format(HVACModeState[value])
        self.__SetHelper('HVACMode', value, qualifier, HVACModeCmdString)

    def UpdateHVACMode(self, value, qualifier):

        HVACModeCmdString = 'hvac_mode'
        res = self.__UpdateHelper('HVACMode', value, qualifier, HVACModeCmdString)
        if res:
            try:
                hvacmode = re.search('hvac_mode=(heat|cool|heat-cool|eco|off)\r', res)
                self.WriteStatus('HVACMode', hvacmode.group(1).title(), qualifier)
            except IndexError:
                self.Error(['HVAC Mode: Invalid/Unexpected Response'])

    def UpdateHVACStatus(self, value, qualifier):

        HVACStatusCmdString = 'hvac_state'
        res = self.__UpdateHelper('HVACStatus', value, qualifier, HVACStatusCmdString)
        if res:
            try:
                hvacstatus = re.search('hvac_state=(heating|cooling|off)', res)
                self.WriteStatus('HVACStatus', hvacstatus.group(1).title(), qualifier)
            except IndexError:
                self.Error(['HVAC Status: Invalid/Unexpected Response'])

    def UpdateLockStatus(self, value, qualifier):

        LockStatusCmdString = 'is_locked'
        res = self.__UpdateHelper('LockStatus', value, qualifier, LockStatusCmdString)
        if res:
            try:
                lockvalue = re.search('is_locked=(true|false)', res)
                self.WriteStatus('LockStatus', lockvalue.group(1).title(), qualifier)
            except IndexError:
                self.Error(['Lock Status: Invalid/Unexpected Response'])

    def SetTemperatureCelcius(self, value, qualifier):

        ValueConstraints = {
            'Min': 9,
            'Max': 32
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TemperatureCelciusCmdString = 'target_temperature_c/{0}'.format(value)
            self.__SetHelper('TemperatureCelcius', value, qualifier, TemperatureCelciusCmdString, None)
        else:
            self.Discard('Invalid Command for SetTemperatureCelcius')

    def UpdateTemperatureCelcius(self, value, qualifier):

        TemperatureCelciusCmdString = 'target_temperature_c'
        res = self.__UpdateHelper('TemperatureCelcius', value, qualifier, TemperatureCelciusCmdString)
        if res:
            try:
                tempcelcius = re.search('target_temperature_c=([0-9]{1,2})', res)
                self.WriteStatus('TemperatureCelcius', int(tempcelcius.group(1)), qualifier)
            except IndexError:
                self.Error(['Temperature Celcius: Invalid/Unexpected Response'])

    def SetTemperatureFahrenheit(self, value, qualifier):

        ValueConstraints = {
            'Min': 50,
            'Max': 90
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TemperatureFahrenheitCmdString = 'target_temperature_f/{0}'.format(value)
            self.__SetHelper('TemperatureFahrenheit', value, qualifier, TemperatureFahrenheitCmdString, None)
        else:
            self.Discard('Invalid Command for SetTemperatureFahrenheit')

    def UpdateTemperatureFahrenheit(self, value, qualifier):

        TemperatureFahrenheitCmdString = 'target_temperature_f'
        res = self.__UpdateHelper('TemperatureFahrenheit', value, qualifier, TemperatureFahrenheitCmdString)
        if res:
            try:
                tempfahr = re.search('target_temperature_f=([0-9]{1,2})', res)
                self.WriteStatus('TemperatureFahrenheit', int(tempfahr.group(1)), qualifier)
            except IndexError:
                self.Error(['Temperature Fahrenheit: Invalid/Unexpected Response'])

    def SetTemperatureScale(self, value, qualifier):

        TemperatureScaleState = {
            'F': 'F',
            'C': 'C'
        }

        TemperatureScaleCmdString = 'temperature_scale/{0}'.format(TemperatureScaleState[value])
        self.__SetHelper('TemperatureScale', value, qualifier, TemperatureScaleCmdString)

    def UpdateTemperatureScale(self, value, qualifier):

        TemperatureScaleCmdString = 'temperature_scale'
        res = self.__UpdateHelper('TemperatureScale', value, qualifier, TemperatureScaleCmdString)
        if res:
            try:
                tempscale = re.search('temperature_scale=(F|C)', res)
                self.WriteStatus('TemperatureScale', tempscale.group(1), qualifier)
            except IndexError:
                self.Error(['Temperature Scale: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/developer-api.nest.com/devices/thermostats/peyiJNo0IldT2YlIVtYaGQ/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=None, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
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

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}/developer-api.nest.com/devices/thermostats/peyiJNo0IldT2YlIVtYaGQ/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
