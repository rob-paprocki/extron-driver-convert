from extronlib.interface import SerialInterface, EthernetClientInterface
import base64
import urllib.error
import urllib.request
import json


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeterministicPlay': {'Status': {}},
            'DeterministicPlayStatus': {'Status': {}},
            'Eject': {'Status': {}},
            'Standby': {'Status': {}},
            'Transport': {'Status': {}},
        }

    def SetDeterministicPlay(self, value, qualifier):

        ValueStateValues = {
            'Arm': b'\x20\x08\x28',
            'Disarm': b'\x20\x09\x29'
        }

        if value in ValueStateValues:
            DeterministicPlayCmdString = ValueStateValues[value]
            self.__SetHelper('DeterministicPlay', DeterministicPlayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeterministicPlay')

    def UpdateDeterministicPlayStatus(self, value, qualifier):

        ValueStateValues = {
            '0b10': 'Ready',
            '0b1': 'Armed'
        }

        DeterministicPlayStatusCmdString = b'\x61\x20\xA1\x22'
        res = self.__UpdateHelper('DeterministicPlayStatus', DeterministicPlayStatusCmdString, value, qualifier)
        if res:
            try:
                response = bin(res[2])  # Convert response byte to binary
                value = ValueStateValues[response]
                self.WriteStatus('DeterministicPlayStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Deterministic Play Status: Invalid/unexpected response'])

    def SetEject(self, value, qualifier):

        EjectCmdString = b'\x20\x0F\x2F'
        self.__SetHelper('Eject', EjectCmdString, value, qualifier)

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x05\x25',
            'Off': b'\x20\x04\x24'
        }

        if value in ValueStateValues:
            StandbyCmdString = ValueStateValues[value]
            self.__SetHelper('Standby', StandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': b'\x20\x01\x21',
            'Stop': b'\x20\x00\x20',
            'Record': b'\x20\x02\x22',
            'Fast Forward': b'\x20\x10\x30',
            'Rewind': b'\x20\x20\x40'
        }

        if value in ValueStateValues:
            TransportCmdString = ValueStateValues[value]
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def UpdateTransport(self, value, qualifier):

        ValueStateValues = {
            '000001': 'Play',
            '100000': 'Stop',
            '000010': 'Record',
            '000100': 'Fast Forward',
            '001000': 'Rewind'
        }

        TransportCmdString = b'\x61\x20\x11\x92'
        res = self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)
        if res:
            try:
                response = bin(res[2])[2:].zfill(8)
                value = ValueStateValues[response[2:]]
                self.WriteStatus('Transport', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Transport: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': "Command not supported or command not recognized due to communication error.",
            b'\x02': "Software overrun due to sending another command before previous command completed.",
            b'\x04': "Command had incorrect checksum.",
            b'\x10': "Parity error on serial line.",
            b'\x20': "Overrun error on serial line.",
            b'\x40': "Framing error on serial line.",
            b'\x80': "Command timed out (not sent within 10 ms)."
        }

        if response:
            if response[0:1] == b'\x11':
                self.Error(['Error, {0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[2:3]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)        

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)    

class DeviceHTTPClass:
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
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Transport': {'Status': {}},
            'TransportState': {'Status': {}},
        }

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '1',
            'Record': '3',
            'Stop': '4',
            'Fast Forward': '5'
        }

        if value in ValueStateValues:
            TransportCmdString = 'config?action=set&paramid=eParamID_TransportCommand&value={}'.format(ValueStateValues[value])
            self.__SetHelper('Transport', value, qualifier, TransportCmdString)
        else:
            self.Discard('Invalid Command for SetTransport')

    def UpdateTransportState(self, value, qualifier):

        ValueStateValues = {
            '0': 'Uninitialized',
            '1': 'Idle',
            '2': 'Recording',
            '3': 'Playing Forward',
            '4': 'Forward 2X',
            '5': 'Forward 4X',
            '6': 'Forward 8X',
            '7': 'Forward 16X',
            '8': 'Forward Step',
            '9': 'Playing Reverse',
            '10': 'Reverse 2X',
            '11': 'Reverse 4X',
            '12': 'Reverse 8X',
            '13': 'Reverse 16X',
            '14': 'Reverse Step',
            '15': 'Paused',
            '16': 'Error in Idle',
            '17': 'Error in record',
            '18': 'Error in Play',
            '19': 'Error in Pause',
            '20': 'Shutdown'
        }

        TransportStateCmdString = 'config?action=get&paramid=eParamID_TransportState'
        res = self.__UpdateHelper('TransportState', value, qualifier, TransportStateCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('TransportState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Transport State: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = json.loads(response.read().decode())
        except ValueError:
            self.Error(['Invalid Response'])
            response = ''
        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
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
            
        url = '{0}{1}'.format(self.RootURL, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)
    
class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port)
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
