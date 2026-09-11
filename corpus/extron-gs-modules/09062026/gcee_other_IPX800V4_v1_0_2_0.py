import base64
import json
import time
import urllib.error
import urllib.request
from re import compile, search

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):

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
        self.devicePassword = devicePassword
        self.Commands = {
            'ConnectionStatus': {'Parameters': ['Number'],'Status': {}},
            'AnalogInput': {'Parameters': ['Number'],'Status': {}},
            'AnalogInputVoltage': {'Parameters': ['Number'],'Status': {}},
            'Counter': {'Parameters': ['Number'],'Status': {}},
            'DigitalInput': {'Parameters': ['Number'],'Status': {}},
            'ModelName': {'Status': {}},
            'Relay': {'Parameters': ['Number'],'Status': {}},
            'Reset': {'Status': {}},
            'VirtualAnalogInput': {'Parameters': ['Number'],'Status': {}},
            'VirtualInput': {'Parameters': ['Number'],'Status': {}},
            'VirtualOutput': {'Parameters': ['Number'],'Status': {}},
            'XDimmer': {'Parameters': ['Number'],'Status': {}}, #'Transition Time qualifier is only for control
        }

        self.lastVirtualAnalogInputUpdate = 0
        self.lastCounterUpdate = 0
        self.lastAnalogInputUpdate = 0
        self.lastXDimmerUpdate = 0
        self.XDimmer_regex = compile(r"{'.*?': '(?:ON|OFF)', '.*?': (\d|[1-9]\d|100)}|"
                                     r"{'.*?': (\d|[1-9]\d|100), '.*?': '(?:ON|OFF)'}")


    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def UpdateAnalogInputVoltage(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 4,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints):
            ctime = time.monotonic()
            if ctime - self.lastAnalogInputUpdate > 1:
                self.lastAnalogInputUpdate = ctime
                AnalogInputCmdString = 'api/xdevices.json?key={}&Get=A'.format(self.devicePassword)
                res = self.__UpdateHelper('AnalogInputVoltage', value, qualifier, AnalogInputCmdString)
                if res:
                    try:
                        for input_num in range(1, 5):
                            qualifier = dict()
                            qualifier['Number'] = '{}'.format(input_num)
                            bit_value = int(res['A{}'.format(input_num)])
                            voltage_value = float((3.3 / 2**16) * bit_value)
                            self.WriteStatus('AnalogInput', bit_value, qualifier)
                            self.WriteStatus('AnalogInputVoltage', voltage_value, qualifier)
                    except (KeyError, IndexError, ValueError):
                        self.Error(['Analog Input Voltage: Invalid/unexpected response'])
            else:
                self.Discard('Wait  at least 1 sec before sending another UpdateAnalogInputVoltage, the response comees back with the status of all quialifiers')
        else:
            self.Discard('Device Is Busy for UpdateAnalogInputVoltage')

    def SetCounter(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 16,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 255,
            'Value': value
        }

        if self.__constraint_checker(NumberConstraints, ValueConstraints):
            CounterCmdString = 'api/xdevices.json?key={}&SetC{:02}={}'.format(self.devicePassword,
                                                                              NumberConstraints['Value'],
                                                                              ValueConstraints['Value'])
            self.__SetHelper('Counter', value, qualifier, url=CounterCmdString)
        else:
            self.Discard('Set Counter: Invalid Command for SetCounter')

    def UpdateCounter(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 16,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints):
            ctime = time.monotonic()
            if ctime - self.lastCounterUpdate > 1:
                self.lastCounterUpdate = ctime
                CounterCmdString = 'api/xdevices.json?key={}&Get=C'.format(self.devicePassword)
                res = self.__UpdateHelper('Counter', value, qualifier, CounterCmdString)
                if res:
                    try:
                        for counter_num in range(1, 17):
                            qualifier = dict()
                            qualifier['Number'] = '{}'.format(counter_num)
                            value = res['C{}'.format(counter_num)]
                            self.WriteStatus('Counter', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Counter: Invalid/unexpected response'])
            else:
                self.Discard('Wait  at least 1 sec before sending another UpdateCounter, the response comees back with the status of all quialifiers')
        else:
            self.Discard('Device Is Busy for UpdateCounter')

    def UpdateModelName(self, value, qualifier):

        RelayStateValues = {
            0: 'Open',
            1: 'Close'
        }

        DigitalInputStateValues = {
            0: 'Inactive',
            1: 'Active'
        }

        DigitalStateValues = {
            0: 'Low',
            1: 'High'
        }

        RelayCmdString = 'api/xdevices.json?key={}&Get=all'.format(self.devicePassword)
        res = self.__UpdateHelper('ModelName', value, qualifier, url=RelayCmdString)
        if res:
            try:
                value = res['product']
                self.WriteStatus('ModelName', value, None)
            except (KeyError, IndexError):
                self.Error(['Model Name: Invalid/unexpected response'])
            try:
                for relay_num in range(1, 57):
                    qualifier = dict()
                    qualifier['Number'] = '{}'.format(relay_num)
                    value = RelayStateValues[res['R{}'.format(relay_num)]]
                    self.WriteStatus('Relay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Relay: Invalid/unexpected response'])
            try:
                for digital_input_num in range(1, 57):
                    qualifier = dict()
                    qualifier['Number'] = '{}'.format(digital_input_num)
                    value = DigitalInputStateValues[res['D{}'.format(digital_input_num)]]
                    self.WriteStatus('DigitalInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Digital Input: Invalid/unexpected response'])
            try:
                for virtual_input_num in range(1, 129):
                    qualifier = dict()
                    qualifier['Number'] = '{}'.format(virtual_input_num)
                    value = DigitalStateValues[res['VI{}'.format(virtual_input_num)]]
                    self.WriteStatus('VirtualInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Virtual Input: Invalid/unexpected response'])
            try:
                for virtual_output_num in range(1, 129):
                    qualifier = dict()
                    qualifier['Number'] = '{}'.format(virtual_output_num)
                    value = DigitalStateValues[res['VO{}'.format(virtual_output_num)]]
                    self.WriteStatus('VirtualOutput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Virtual Output: Invalid/unexpected response'])

    def SetRelay(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 56,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueStateValues = {
            'Open': 'api/xdevices.json?key={}&ClearR={{:02}}'.format(self.devicePassword),
            'Close': 'api/xdevices.json?key={}&SetR={{:02}}'.format(self.devicePassword)
        }

        if self.__constraint_checker(NumberConstraints):
            RelayCmdString = ValueStateValues[value].format(NumberConstraints['Value'])
            self.__SetHelper('Relay', value, qualifier, url=RelayCmdString)
        else:
            self.Discard('Invalid Command for SetRelay')

    def SetReset(self, value, qualifier):

        ResetCmdString = 'api/xdevices.json?key={}&Reset'.format(self.devicePassword)
        self.__SetHelper('Reset', value, qualifier, url=ResetCmdString)

    def SetVirtualAnalogInput(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 32,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 65535,
            'Value': value
        }

        if self.__constraint_checker(NumberConstraints, ValueConstraints):
            VirtualAnalogInputCmdString = 'api/xdevices.json?key={}&SetVA{:02}={}'.format(self.devicePassword,
                                                                                          NumberConstraints['Value'],
                                                                                          ValueConstraints['Value'])
            self.__SetHelper('VirtualAnalogInput', value, qualifier, url=VirtualAnalogInputCmdString)
        else:
            self.Discard('Invalid Command for SetVirtualAnalogInput')

    def UpdateVirtualAnalogInput(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 32,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints):
            ctime = time.monotonic()
            if ctime - self.lastVirtualAnalogInputUpdate > 1:
                self.lastVirtualAnalogInputUpdate = ctime
                VirtualAnalogInputCmdString = 'api/xdevices.json?key={}&Get=VA'.format(self.devicePassword)
                res = self.__UpdateHelper('VirtualAnalogInput', value, qualifier, url=VirtualAnalogInputCmdString)
                if res:
                    try:
                        for input_num in range(1, 33):
                            qualifier = dict()
                            qualifier['Number'] = '{}'.format(input_num)
                            value = res['VA{}'.format(input_num)]
                            self.WriteStatus('VirtualAnalogInput', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Virtual Analog Input: Invalid/unexpected response'])
            else:
                self.Discard('Wait  at least 1 sec before sending another UpdateVirtualAnalogInput, the response comees back with the status of all quialifiers')
        else:
            self.Discard('Device Is Busy for UpdateVirtualAnalogInput')

    def SetVirtualInput(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 128,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueStateValues = {
            'High': 'api/xdevices.json?key={}&SetVI={{:03}}'.format(self.devicePassword),
            'Low': 'api/xdevices.json?key={}&ClearVI={{:03}}'.format(self.devicePassword)
        }

        if self.__constraint_checker(NumberConstraints):
            VirtualInputCmdString = ValueStateValues[value].format(NumberConstraints['Value'])
            self.__SetHelper('VirtualInput', value, qualifier, url=VirtualInputCmdString)
        else:
            self.Discard('Invalid Command for SetVirtualInput')

    def SetVirtualOutput(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 128,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueStateValues = {
            'High': 'api/xdevices.json?key={}&SetVO={{:03}}'.format(self.devicePassword),
            'Low': 'api/xdevices.json?key={}&ClearVO={{:03}}'.format(self.devicePassword)
        }

        if self.__constraint_checker(NumberConstraints):
            VirtualOutputCmdString = ValueStateValues[value].format(NumberConstraints['Value'])
            self.__SetHelper('VirtualOutput', value, qualifier, url=VirtualOutputCmdString)
        else:
            self.Discard('Invalid Command for SetVirtualOutput')

    def SetXDimmer(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 24,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            'Value': value,
        }

        transition_time = qualifier['Transition Time']
        if self.__constraint_checker(NumberConstraints, ValueConstraints):
            XDimmerCmdString = 'api/xdevices.json?key={}&SetG{:02}={}'.format(self.devicePassword,
                                                                              NumberConstraints['Value'],
                                                                              ValueConstraints['Value'])
            if transition_time and transition_time > 0:
                XDimmerCmdString = ''.join([XDimmerCmdString, '&Time={}'.format(transition_time)])
            self.__SetHelper('XDimmer', value, qualifier, url=XDimmerCmdString)
        else:
            self.Discard('Invalid Command for SetXDimmer')

    def UpdateXDimmer(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 24,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints):
            ctime = time.monotonic()
            if ctime - self.lastXDimmerUpdate > 1:
                self.lastXDimmerUpdate = ctime
                XDimmerCmdString = 'api/xdevices.json?key={}&Get=G'.format(self.devicePassword)
                res = self.__UpdateHelper('XDimmer', value, qualifier, url=XDimmerCmdString)
                if res:
                    try:
                        for dimmer_num in range(1, 25):
                            qualifier = dict()
                            qualifier['Number'] = '{}'.format(dimmer_num)
                            result = self.XDimmer_regex.match(str(res['G{}'.format(dimmer_num)]))
                            value = int(result.group(1) if result.group(1) else result.group(2))
                            self.WriteStatus('XDimmer', value, qualifier)
                    except (ValueError, IndexError):
                        self.Error(['XDimmer: Invalid/unexpected response'])
            else:
                self.Discard('Wait  at least 1 sec before sending another UpdateXDimmer, the response comees back with the status of all quialifiers')
                                
        else:
            self.Discard('Device Is Busy for UpdateXDimmer')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        json_output = json.loads(res.replace(': ,', ': 0,'))
        try:
            res = json_output if json_output['status'] == 'Success' else dict()
        except (KeyError, IndexError):
            res = dict()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
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
        
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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
