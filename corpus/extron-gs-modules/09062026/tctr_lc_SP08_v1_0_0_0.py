from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile
class DeviceClass:

    def __init__(self):

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
        self._DeviceID = 1
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Dimmer': {'Parameters': ['Device Type', 'Device Number', 'Ramping Time Minutes', 'Ramping Time Seconds', 'Value Type'], 'Status': {}},
            'DimmerStatus': {'Parameters': ['Device Type', 'Device Number', 'Value Type'], 'Status': {}},
            'TemperatureSetting': {'Status': {}},
        }


        update_regex_str = {
            'DimmerStatus': b'AB00(?:[01]\d\d|2[0-4]\d|25[0-5])E',
            'TemperatureSetting': b'AB00(?:[0-2])E'
        }
        self.UpdateRegex = {k: compile(v) for k, v in update_regex_str.items()}

    
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = 99 if value == 'Broadcast' else int(value)
        if self._DeviceID not in range(0, 256):
            print('DeviceID Parameter should be in range 0 - 255, or Broadcast (99).')

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetDimmer(self, value, qualifier):

        device_type = qualifier['Device Type']
        value_type = qualifier['Value Type']

        DeviceTypeStates = {
            'DMX512': ('1', 1, 64),
            'DALI': ('2', 0, 63),
            'DSI': ('3', 0, 0),
            'Analog Output': ('4', 1, 8)
        }

        DeviceNumberConstraints = {
            'Min': DeviceTypeStates[device_type][1] if device_type in DeviceTypeStates else 0,
            'Max': DeviceTypeStates[device_type][2] if device_type in DeviceTypeStates else 0,
            'Value': int(qualifier['Device Number']) if qualifier['Device Number'].isdigit() else -1
        }

        RampingTimeMinutesConstraints = {
            'Min': 0,
            'Max': 59,
            'Value': int(qualifier['Ramping Time Minutes']) if qualifier['Ramping Time Minutes'].isdigit() else -1
        }

        RampingTimeSecondsConstraints = {
            'Min': 0,
            'Max': 59,
            'Value': int(qualifier['Ramping Time Seconds']) if qualifier['Ramping Time Seconds'].isdigit() else -1
        }

        ValueTypeStates = {
            'Decimal': 'd',
            'Percentage': '%'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100 if (value_type in ValueTypeStates and value_type == 'Percentage') else 255,
            'Value': value
        }

        if (self.__constraint_checker(DeviceNumberConstraints, RampingTimeMinutesConstraints,
                                      RampingTimeSecondsConstraints, ValueConstraints)
                and device_type in DeviceTypeStates and value_type in ValueTypeStates):
            DimmerCmdString = 'SB{:03}D{}{:03}{:03}{}{:02}{:02}E'.format(self._DeviceID,
                                                                         DeviceTypeStates[device_type][0],
                                                                         DeviceNumberConstraints['Value'],
                                                                         ValueConstraints['Value'],
                                                                         ValueTypeStates[value_type],
                                                                         RampingTimeMinutesConstraints['Value'],
                                                                         RampingTimeSecondsConstraints['Value'])
            self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmer')

    def UpdateDimmerStatus(self, value, qualifier):

        device_type = qualifier['Device Type']
        value_type = qualifier['Value Type']

        DeviceTypeStates = {
            'DMX512': ('1', 1, 64),
            'DALI': ('2', 0, 63),
            'DSI': ('3', 0, 0),
            'Analog Output': ('4', 1, 8)
        }

        DeviceNumberConstraints = {
            'Min': DeviceTypeStates[device_type][1] if device_type in DeviceTypeStates else 0,
            'Max': DeviceTypeStates[device_type][2] if device_type in DeviceTypeStates else 0,
            'Value': int(qualifier['Device Number']) if qualifier['Device Number'].isdigit() else -1
        }

        ValueTypeStates = {
            'Decimal': 'd',
            'Percentage': '%'
        }

        if (self.__constraint_checker(DeviceNumberConstraints)
                and device_type in DeviceTypeStates
                and value_type in ValueTypeStates):
            DimmerStatusCmdString = 'SB{:03}QD{}{:03}{}E'.format(self._DeviceID,
                                                                 DeviceTypeStates[device_type][0],
                                                                 DeviceNumberConstraints['Value'],
                                                                 ValueTypeStates[value_type])
            res = self.__UpdateHelper('DimmerStatus', DimmerStatusCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[4:7])
                    if value_type == 'Percentage' and value > 100:
                        raise ValueError
                    self.WriteStatus('DimmerStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Dimmer Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDimmerStatus')

    def UpdateTemperatureSetting(self, value, qualifier):

        ValueStateValues = {
            0: 'Celsius',
            1: 'Fahrenheit',
            2: 'Kelvin'
        }

        TemperatureSettingCmdString = 'SB{:03}QKE'.format(self._DeviceID)
        res = self.__UpdateHelper('TemperatureSetting', TemperatureSettingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[4:5])]
                self.WriteStatus('TemperatureSetting', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Temperature Setting: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex[command])
            if not res:
                return ''
            else:
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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
