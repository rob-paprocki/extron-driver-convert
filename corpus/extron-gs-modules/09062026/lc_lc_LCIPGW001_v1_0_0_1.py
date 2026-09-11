from extronlib.interface import EthernetClientInterface
from re import compile, escape, search
from struct import pack, unpack
from binascii import hexlify, unhexlify
from collections import OrderedDict


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = OrderedDict()
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self._DevicesTemperatureScale = 'CEL'
        self._UnicastIPPort = self.ServicePort
        self._ControllerIPAddress = ''

        self.connect_flag = True
        self.at_max_connection = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmbientTemperature': {'Status': {}, 'Parameters': ['Group Address', 'Scale']},
            'Dimmer': {'Status': {}, 'Parameters': ['Group Address']},
            'InitializationStatus': {'Status': {}},
            'Scaling': {'Status': {}, 'Parameters': ['Group Address']},
            'Switch': {'Status': {}, 'Parameters': ['Group Address']},
            'ThermostatSetpoint': {'Status': {}, 'Parameters': ['Group Address', 'Scale']},
        }

        self.addresses = dict()
        self.communication_channel_id = None
        self.initialize_successful = False
        self.driver_message = ''
        self.driver_sequence_counter = SequenceCounter()
        self.last_send_message = None

        if self.Unidirectional == 'False':

            self.AddMatchString(compile(b'\x06\x10\x02\x06\x00\x14([\x00-\xFF])(\x00|[\x22-\x24])\x08\x01[\x00-'
                                        b'\xFF]{4}\x0E\x57\x04\x04[\x00-\xFF]{2}'), self.__MatchConnectResponse, 'Good')

            self.AddMatchString(
                compile(b'\x06\x10\x02\x06\x00\x08\x00([\x00-\xFF])'),
                self.__MatchConnectResponse, 'MaxConnection')

            self.AddMatchString(compile(b'\x06\x10\x02\x08\x00\x08([\x00-\xFF])(\x00|\x21|\x26|\x27)'),
                                self.__MatchInitializationStatus, None)

            self.AddMatchString(compile(b'\x06\x10\x04\x21\x00\x0A\x04([\x00-\xFF])([\x00-\xFF])\x04'),
                                self.__Match_E_SEQUENCE_NUMBER_Response, None)

            self.AddMatchString(compile(b'\x06\x10\x04\x20\x00[\x15-\x17]\x04([\x00-\xFF])([\x00-\xFF])\x00\\x2E'
                                        b'\x00[\xBC\x9C]\xE0[\x00-\xFF]{4}(?:(?:\x01\x00{2})|(?:\x01\x00[\x80-\x8F])|'
                                        b'(?:\x02\x00\x80[\x00-\xFF])|(?:\x03\x00\x80[\x00-\xFF]{2}))'),
                                self.__Match_L_Data_con_Response, None)

            self.get_all_l_data_ind_messages = compile(b'\x06\x10\x04\x20\x00[\x15-\xFF]\x04([\x00-\xFF])([\x00-\xFF])'
                                                       b'\x00\\x29\x00[\xBC\x9C]\xE0[\x00-\xFF]{4}[\x01-\xEC]\x00'
                                                       b'[\x00-\xFF]{1,236}?')
            self.AddMatchString(self.get_all_l_data_ind_messages, self.__Match_L_Data_ind_Msg, None)

    @property
    def DevicesTemperatureScale(self):
        return self._DevicesTemperatureScale

    @DevicesTemperatureScale.setter
    def DevicesTemperatureScale(self, value):
        self._DevicesTemperatureScale = 'FAH' if value == 'Fahrenheit' else 'CEL'

    @property
    def ControllerIPAddress(self):
        return self._ControllerIPAddress

    @ControllerIPAddress.setter
    def ControllerIPAddress(self, value):
        ip_match_regex = compile('^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d?|\d)$')
        self._ControllerIPAddress = ip_match_regex.match(value)
        if self._ControllerIPAddress:
            IPAddr = self._ControllerIPAddress.group(0).split('.')
            self._ControllerIPAddress = list(map(lambda val: int(val), IPAddr))

    def __Match_E_SEQUENCE_NUMBER_Response(self, match, tag):
        if self.communication_channel_id == match.group(1)[0]:
            new_sequence_counter = match.group(2)[0]

            if new_sequence_counter == 255:
                new_sequence_counter = (new_sequence_counter + 1) & 255

            self.driver_sequence_counter.sequence_counter = new_sequence_counter
            resend_message = b''.join([self.last_send_message[:8],
                                       new_sequence_counter.to_bytes(1, byteorder='big'),
                                       self.last_send_message[9:]])
            self.Send(resend_message, None)

    def __Match_L_Data_con_Response(self, match, tag):
        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    def __Match_L_Data_ind_Msg(self, match, tag):
        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    @staticmethod
    def convert_to_knx_float(value):
        exponent = 0
        knx_value = 0
        quotient = 0x07FF
        value *= 100
        value = int(value)
        if value < 0:
            knx_value = 0x8000
            value = -value
            quotient = 0x800
        while value > quotient:
            value >>= 1
            exponent += 1
        if knx_value != 0:
            value |= (~0x07FF)
            value = -value
        knx_value |= value & 0x07FF
        knx_value |= (exponent << 11) & 0x07800
        return knx_value

    @staticmethod
    def convert_from_knx_float(knx_value):

        value = knx_value & 0x07FF
        if (knx_value & 0x08000) != 0:
            value |= (~0x07FF)
            value = -value
        value <<= ((knx_value & 0x07800) >> 11)
        if (knx_value & 0x08000) != 0:
            value = -value
        return round(value / 100, 2)

    @staticmethod
    def celsius_to_fahrenheit(degrees_celsius):
        return round(9.0 / 5.0 * degrees_celsius + 32, 2)

    @staticmethod
    def fahrenheit_to_celsius(degrees_fahrenheit):
        return round((degrees_fahrenheit - 32) * 5.0 / 9.0, 2)

    def SetConnectRequest(self):

        lc_msg = LcKnxMsg(knx_net_ip_service_type='CONNECT_REQUEST',
                          control_endpoint_ip=self._ControllerIPAddress,
                          control_endpoint_port=self._UnicastIPPort)
        if lc_msg:
            self.connect_flag = True
            self.Send(lc_msg.encode_message())
        else:
            self.Error(['Problem creating the CONNECT_REQUEST message for ConnectRequest'])

    def __MatchConnectResponse(self, match, tag):
        connect_response_status_codes = {
            0x22: 'The KNXnet/IP Server device does not support the requested connection type.',
            0x23: 'The KNXnet/IP Server device does not support one or more requested connection options.',
            0x24: 'The KNXnet/IP Server device cannot accept the new data connection because its maximum amount'
                  ' of concurrent connections is already used.',
        }
        if tag == 'MaxConnection':
            status_code = match.group(1)[0]
        else:
            status_code = match.group(2)[0]

        if status_code == 0x00:
            self.communication_channel_id = match.group(1)[0]
            self.SetConnectionStateRequest()
            self.OnConnected()
            self.connect_flag = True
            self.driver_message = ''
            self.at_max_connection = False
        elif status_code in connect_response_status_codes:
            self.driver_message = connect_response_status_codes[status_code]
            self.initialize_successful = False
            if status_code == 0x24:
                self.at_max_connection = True
        else:
            self.driver_message = 'An unknown error occurred.'
            self.initialize_successful = False

        if self.driver_message:
            self.connect_flag = False
            self._ReceiveBuffer = b''
            self.OnDisconnected()
            self.Discard(self.driver_message)

    def SetDisconnectRequest(self, comm_id=None):
        lc_msg = LcKnxMsg(knx_net_ip_service_type='DISCONNECT_REQUEST',
                            control_endpoint_ip=self._ControllerIPAddress,
                            control_endpoint_port=self._UnicastIPport)

        if lc_msg and self.communication_channel_id and comm_id is None:
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            self.Send(lc_msg.encode_message())
        elif lc_msg and comm_id:
            lc_msg.set_communication_channel_id(comm_id)
            self.Send(lc_msg.encode_message())
        else:
            self.driver_message = 'Problem creating the DISCONNECT_REQUEST message.'

    def SetConnectionStateRequest(self):

        lc_msg = LcKnxMsg(knx_net_ip_service_type='CONNECTIONSTATE_REQUEST',
                          control_endpoint_ip=self._ControllerIPAddress,
                          control_endpoint_port=self._UnicastIPPort)

        if lc_msg:
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            self.Send(lc_msg.encode_message())
        else:
            self.driver_message = 'Problem creating the CONNECTIONSTATE_REQUEST message.'

    def SetTunnellingAcknowledge(self, value, qualifier):

        communication_channel_id = value[0]
        sequence_counter = value[1]

        lc_msg = LcKnxMsg(knx_net_ip_service_type='TUNNELLING_ACK')

        if lc_msg:
            lc_msg.set_communication_channel_id(communication_channel_id)
            lc_msg.sequence_counter = sequence_counter
            self.Send(lc_msg.encode_message())
        else:
            self.SetDisconnectRequest(communication_channel_id)
            self.Discard('Invalid Command for SetTunnellingAcknowledge')

    def UpdateAmbientTemperature(self, value, qualifier):

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST',
                          apci_telegram_type='GroupValueRead')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(0, '1 Bit')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__UpdateHelper('AmbientTemperature', lc_msg, value, qualifier)
        else:
            if self.driver_message:
                self.Discard(self.driver_message)
            else:
                self.Discard('Invalid Command')

    def __MatchAmbientTemperature(self, match, tag):

        temp_value = int.from_bytes(match.group(3), byteorder='big')
        if self._DevicesTemperatureScale == 'CEL':
            celsius_value = self.convert_from_knx_float(temp_value)
            fahrenheit_value = self.celsius_to_fahrenheit(celsius_value)
        else:
            fahrenheit_value = self.convert_from_knx_float(temp_value)
            celsius_value = self.fahrenheit_to_celsius(fahrenheit_value)
        qualifier1 = dict()
        qualifier1['Group Address'] = self.addresses[tag][0]
        qualifier2 = dict()
        qualifier2['Group Address'] = self.addresses[tag][0]
        qualifier1['Scale'] = 'Celsius'
        self.WriteStatus('AmbientTemperature', celsius_value, qualifier1)
        qualifier2['Scale'] = 'Fahrenheit'
        self.WriteStatus('AmbientTemperature', fahrenheit_value, qualifier2)

        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    def SetDimmer(self, value, qualifier):

        StateStateValues = {
            'Up': '09',
            'Down': '01',
            'Stop': '00'
        }

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(StateStateValues[value], '4 Bits')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__SetHelper('Dimmer', lc_msg, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmer')

    def UpdateInitializationStatus(self, value, qualifier):

        lc_msg = LcKnxMsg(knx_net_ip_service_type='CONNECTIONSTATE_REQUEST',
                          control_endpoint_ip=self._ControllerIPAddress,
                          control_endpoint_port=self._UnicastIPPort)

        if lc_msg and self.communication_channel_id:
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            self.__UpdateHelper('InitializationStatus', lc_msg, value, qualifier)
        else:
            if self.driver_message:
                self.Discard(self.driver_message)
            else:
                self.Discard('Invalid Command')

    def __MatchInitializationStatus(self, match, tag):

        connectionstate_response_status_codes = {
            0x21: 'The KNXnet/IP Server device cannot find an active data connection with the specified ID.',
            0x26: 'The KNXnet/IP Server device detects an error concerning the data connection with the specified ID.',
            0x27: 'The KNXnet/IP Server device detects an error concerning the KNX connection with the specified ID.',
        }

        status_code = match.group(2)[0]
        if status_code == 0x00 and self.communication_channel_id == match.group(1)[0]:
            self.initialize_successful = True
            self.connect_flag = True
        elif status_code in connectionstate_response_status_codes:
            self.driver_message = connectionstate_response_status_codes[status_code]
            self.initialize_successful = False
        else:
            self.driver_message = 'An unknown error occurred.'
            self.initialize_successful = False

        if self.initialize_successful:
            self.WriteStatus('InitializationStatus', 'Successful', None)
        else:
            self.WriteStatus('InitializationStatus', 'Not Successful', None)
            self.connect_flag = False
            self._ReceiveBuffer = b''
            self.OnDisconnected()

    def SetScaling(self, value, qualifier):

        level_constraints = {
            'Min': 0,
            'Max': 255
        }
        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST')
        if (level_constraints['Min'] <= value <= level_constraints['Max'] and
                lc_msg and self.communication_channel_id and lc_msg.get_group_address()):
            lc_msg.set_data(value, '1 Byte')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__SetHelper('Scaling', lc_msg, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScaling')

    def UpdateScaling(self, value, qualifier):

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          apci_telegram_type='GroupValueRead',
                          knx_net_ip_service_type='TUNNELLING_REQUEST')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(0, '1 Bit')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__UpdateHelper('Scaling', lc_msg, value, qualifier)
        else:
            if self.driver_message:
                self.Discard(self.driver_message)
            else:
                self.Discard('Invalid Command')

    def __MatchScaling(self, match, tag):

        temp_value = int.from_bytes(match.group(3), byteorder='big')
        qualifier = dict()
        qualifier['Group Address'] = self.addresses[tag][0]
        self.WriteStatus('Scaling', temp_value, qualifier)

        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    def SetSwitch(self, value, qualifier):

        state_values = {
            'On': '01',
            'Off': '00'
        }

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(state_values[value], '1 Bit')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__SetHelper('Switch', lc_msg, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitch')

    def UpdateSwitch(self, value, qualifier):

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST',
                          apci_telegram_type='GroupValueRead')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(0, '1 Bit')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__UpdateHelper('Switch', lc_msg, value, qualifier)
        else:
            if self.driver_message:
                self.Discard(self.driver_message)
            else:
                self.Discard('Invalid Command')

    def __MatchSwitch(self, match, tag):

        state_values = {
            '01': 'On',
            '00': 'Off'
        }
        temp_value = '{:02x}'.format(int.from_bytes(match.group(3), byteorder='big') & 0b00000001)
        qualifier = dict()
        qualifier['Group Address'] = self.addresses[tag][0]
        value = state_values[temp_value]
        self.WriteStatus('Switch', value, qualifier)

        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    def SetThermostatSetpoint(self, value, qualifier):

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            if qualifier['Scale'] == 'Fahrenheit':
                fahrenheit_value = value
                celsius_value = self.fahrenheit_to_celsius(fahrenheit_value)
            else:
                celsius_value = value
                fahrenheit_value = self.celsius_to_fahrenheit(celsius_value)
            if self._DevicesTemperatureScale == 'CEL':
                lc_msg.set_data('{:04X}'.format(self.convert_to_knx_float(celsius_value)), '2 Bytes')
            else:
                lc_msg.set_data('{:04X}'.format(self.convert_to_knx_float(fahrenheit_value)), '2 Bytes')
            qualifier1 = dict()
            qualifier1['Group Address'] = qualifier['Group Address']
            qualifier2 = dict()
            qualifier2['Group Address'] = qualifier['Group Address']
            qualifier1['Scale'] = 'Celsius'
            qualifier2['Scale'] = 'Fahrenheit'
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__SetHelper('ThermostatSetpoint', lc_msg, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThermostatSetpoint')

    def UpdateThermostatSetpoint(self, value, qualifier):

        lc_msg = LcKnxMsg(qualifier['Group Address'],
                          knx_net_ip_service_type='TUNNELLING_REQUEST',
                          apci_telegram_type='GroupValueRead')

        if lc_msg and self.communication_channel_id and lc_msg.get_group_address():
            lc_msg.set_data(0, '1 Bit')
            lc_msg.set_communication_channel_id(self.communication_channel_id)
            lc_msg.sequence_counter = self.driver_sequence_counter.sequence_counter
            self.__UpdateHelper('ThermostatSetpoint', lc_msg, value, qualifier)
        else:
            if self.driver_message:
                self.Discard(self.driver_message)
            else:
                self.Discard('Invalid Command')

    def __MatchThermostatSetpoint(self, match, tag):

        knx_value = int.from_bytes(match.group(3), byteorder='big')
        if self._DevicesTemperatureScale == 'CEL':
            celsius_value = self.convert_from_knx_float(knx_value)
            fahrenheit_value = self.celsius_to_fahrenheit(celsius_value)
        else:
            fahrenheit_value = self.convert_from_knx_float(knx_value)
            celsius_value = self.fahrenheit_to_celsius(fahrenheit_value)
        qualifier1 = dict()
        qualifier1['Group Address'] = self.addresses[tag][0]
        qualifier2 = dict()
        qualifier2['Group Address'] = self.addresses[tag][0]
        qualifier1['Scale'] = 'Celsius'
        self.WriteStatus('ThermostatSetpoint', celsius_value, qualifier1)
        qualifier2['Scale'] = 'Fahrenheit'
        self.WriteStatus('ThermostatSetpoint', fahrenheit_value, qualifier2)

        communication_channel_id = match.group(1)[0]
        sequence_counter = match.group(2)[0]
        self.SetTunnellingAcknowledge((communication_channel_id, sequence_counter), None)

    def __SetHelper(self, command, lc_msg, value, qualifier):
        self.Debug = True

        if self.initialize_successful:
            self.last_send_message = lc_msg.encode_message()
            self.Send(self.last_send_message)
        else:
            self.Error(['{} Please check the device and perform a restart of the controller.'.format(self.driver_message)])
            self.driver_sequence_counter.decrement()

    def __UpdateHelper(self, command, lc_msg, value, qualifier):

        matches = {
            'AmbientTemperature': self.__MatchAmbientTemperature,
            'Scaling': self.__MatchScaling,
            'Switch': self.__MatchSwitch,
            'ThermostatSetpoint': self.__MatchThermostatSetpoint
        }
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.initialize_successful:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ', command)
                self.driver_sequence_counter.sequence_counter -= 1
            else:
                if command in matches:
                    address = lc_msg.get_group_address('HEX')
                    self.addresses[address] = [lc_msg.get_group_address('PRINT'), matches[command]]
                    feedback_regex = None
                    if command == 'Switch':
                        lc_msg.set_regex_type('1 Bit')
                        feedback_regex = compile(lc_msg.create_status_regex())
                    elif command == 'Scaling':
                        lc_msg.set_regex_type('1 Byte')
                        feedback_regex = compile(lc_msg.create_status_regex())
                    elif command in ('AmbientTemperature', 'ThermostatSetpoint'):
                        lc_msg.set_regex_type('2 Bytes')
                        feedback_regex = compile(lc_msg.create_status_regex())

                    if feedback_regex:
                        self.RemoveMatchString(self.get_all_l_data_ind_messages)
                        self.AddMatchString(feedback_regex, self.__MatchAll, address)
                        self.AddMatchString(self.get_all_l_data_ind_messages, self.__Match_L_Data_ind_Msg, None)

                self.last_send_message = lc_msg.encode_message()
                self.Send(self.last_send_message)
        else:
            self.Error(['{} Please check the device and perform a restart of the controller.'.format(self.driver_message)])
            self.driver_sequence_counter.decrement()

    def __MatchAll(self, match, tag):
        self.addresses[tag][1](match, tag)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.initialize_successful = False
        self.driver_sequence_counter = None
        self.driver_sequence_counter = SequenceCounter()

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        if self.connect_flag:
            self._ReceiveBuffer += data
            # check incoming data if it matched any expected data from device module
            if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
                self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    def RemoveMatchString(self, regex):
        self._compile_list.pop(regex, None)

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        compile_dict = self._compile_list.copy()
        for regexString in compile_dict.keys():
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort=3671, Protocol='UDP', ServicePort=3672, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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


class LcKnxMsg(object):

    HEADER_SIZE_10 = 0x06
    KNX_NET_IP_VERSION = 0x10

    KNX_NET_IP_SERVICE_TYPES = {
        'SEARCH_REQUEST': 0x0201,
        'SEARCH_RESPONSE': 0x0202,
        'DESCRIPTION_REQUEST': 0x0203,
        'DESCRIPTION_RESPONSE': 0x0204,
        'CONNECT_REQUEST': 0x0205,
        'CONNECT_RESPONSE': 0x0206,
        'CONNECTIONSTATE_REQUEST': 0x0207,
        'CONNECTIONSTATE_RESPONSE': 0x0208,
        'DISCONNECT_REQUEST': 0x0209,
        'DISCONNECT_RESPONSE': 0x020A,
        'TUNNELLING_REQUEST': 0x0420,
        'TUNNELLING_ACK': 0x0421,
        'ROUTING_INDICATION': 0x0530,
    }

    CEMI_MESSAGE_CODES = {
        'L_Data.req': 0x11,
        'L_Data.ind': 0x29,
        'L_Data.con': 0x2E,
    }

    CEMI_PRIORITIES = {
        'SYSTEM': 0b00,
        'NORMAL': 0b01,
        'URGENT': 0b10,
        'LOW': 0b11,
    }

    CEMI_REPEATED_TELEGRAM = {
        'Yes': 0b0,
        'No': 0b1,
    }

    T_PDU_COMMUNICATION_TYPES = {
        'UDP': 0b00,
        'NDP': 0b01,
        'UCD': 0b10,
        'NCD': 0b11,
    }

    APCI_TELEGRAM_TYPES = {
        'GroupValueRead': 0b0000,
        'GroupValueResponse': 0b0001,
        'GroupValueWrite': 0b0010,
        'IndividualAddrWrite': 0b0011,
        'IndividualAddrRequest': 0b0100,
        'IndividualAddrResponse': 0b0101,
        'AdcRead': 0b0110,
        'AdcResponse': 0b0111,
        'MemoryRead': 0b1000,
        'MemoryResponse': 0b1001,
        'MemoryWrite': 0b1010,
        'UserMessage': 0b1011,
        'MaskVersionRead': 0b1100,
        'MaskVersionResponse': 0b1101,
        'Restart': 0b1110,
        'Escape': 0b1111,
    }

    RECEIVER_ADDRESS_TYPES = {
        'Individual Telegram': 0b0,
        'Group Telegram': 0b1,
    }

    ROUTING_COUNTER = 0b110

    __data = None
    __data_size = None
    __encoded_message = None
    __created_status_regex = None
    __regex_size = None
    __communication_channel_id = None
    __sequence_counter = None

    reGroupAddress = compile(r'^\d{1,2}/\d{1,4}$|^\d{1,2}/\d/\d{1,3}$')

    def __init__(self, group_address=None, knx_net_ip_service_type='ROUTING_INDICATION', cemi_priority='LOW',
                 group_address_type=None, apci_telegram_type='GroupValueWrite', control_endpoint_ip=None,
                 control_endpoint_port=None):

        self.groupAddressType = group_address_type

        if group_address:
            self.set_group_address(group_address)
        else:
            self.__group_address = None

        if knx_net_ip_service_type in self.KNX_NET_IP_SERVICE_TYPES:
            self.__knx_net_ip_service_type = knx_net_ip_service_type
        else:
            raise ValueError('Invalid KNX Net IP service type {}'.format(knx_net_ip_service_type))

        if cemi_priority in self.CEMI_PRIORITIES:
            self.__cemi_priority = cemi_priority
        else:
            raise ValueError('Invalid Priority {}'.format(cemi_priority))

        if apci_telegram_type in self.APCI_TELEGRAM_TYPES:
            self.__apci_telegram_type = apci_telegram_type
        else:
            raise ValueError('Invalid APCI telegram type {}'.format(apci_telegram_type))

        self.set_data(None, None)

        if control_endpoint_ip and control_endpoint_port:
            self.__control_endpoint_details = (control_endpoint_ip, control_endpoint_port)
        else:
            self.__control_endpoint_details = None

    def __str__(self):
        return self.get_data('PRINT')

    @property
    def return_solicited_apci_telegram_type(self):
        return self.APCI_TELEGRAM_TYPES[{
            'GroupValueRead': 'GroupValueResponse',
            'IndividualAddrRequest': 'IndividualAddrResponse',
            'AdcRead': 'AdcResponse',
            'MemoryRead': 'MemoryResponse',
            'MaskVersionRead': 'MaskVersionResponse',
        }[self.__apci_telegram_type]]

    @property
    def return_unsolicited_apci_telegram_type(self):
        return self.APCI_TELEGRAM_TYPES[{
            'GroupValueRead': 'GroupValueWrite',
            'IndividualAddrRequest': 'IndividualAddrWrite',
            'MemoryRead': 'MemoryWrite',
        }[self.__apci_telegram_type]]

    def set_group_address(self, input_group_address):

        if self.reGroupAddress.match(input_group_address):
            group_address = input_group_address.split('/')
            self.groupAddressType = '2-level' if len(group_address) == 2 else '3-level'
            group_address = tuple([int(node) for node in group_address])
            if self.groupAddressType == '2-level':
                if 0 <= group_address[0] <= 15 and 0 <= group_address[1] <= 2047:
                    self.__group_address = group_address
                else:
                    raise ValueError('UserInput ' + input_group_address)
            elif self.groupAddressType == '3-level':
                if 0 <= group_address[0] <= 15 and 0 <= group_address[1] <= 7 and 0 <= group_address[2] <= 255:
                    self.__group_address = group_address
                else:
                    raise ValueError('UserInput ' + input_group_address)
        else:
            raise ValueError('UserInput ' + input_group_address)

    def get_group_address(self, output_format='PRINT'):

        if isinstance(self.__group_address, tuple):
            if output_format == 'BINARY':
                if self.groupAddressType == '2-level':
                    return ((self.__group_address[0] << 11) + self.__group_address[1]).to_bytes(2, byteorder='big')
                elif self.groupAddressType == '3-level':
                    return ((self.__group_address[0] << 11) + (self.__group_address[1] << 8) +
                            self.__group_address[2]).to_bytes(2, byteorder='big')
                else:
                    return self.__group_address
            elif output_format == 'HEX':
                group_address = self.get_group_address('BINARY')
                return hexlify(group_address).upper()
            elif output_format == 'PRINT':
                return '/'.join(str(node) for node in self.__group_address)
            else:
                return None
        else:
            return self.__group_address

    def set_data(self, value, value_size):

        try:
            self.__data = hexlify(value.to_bytes(1, byteorder='big')).upper()
        except (ValueError, AttributeError, OverflowError):
            if isinstance(value, str):
                self.__data = value.encode()
            elif isinstance(value, bytes):
                self.__data = value
        finally:
            self.__data_size = value_size

    def get_data(self, output_format='PRINT'):

        if output_format == 'INTEGER':
            return int('0x' + self.get_data(), 16)
        elif output_format == 'BINARY':
            return unhexlify(self.__data)
        elif output_format == 'HEX':
            return self.__data
        elif output_format == 'PRINT':
            try:
                return self.__data.decode()
            except (ValueError, AttributeError):
                return self.__data

    def set_regex_type(self, value_size):

        self.__regex_size = value_size

    def set_communication_channel_id(self, input_communication_channel_id):

        self.__communication_channel_id = int(input_communication_channel_id)

    @property
    def sequence_counter(self):
        if not self.__sequence_counter:
            self.__sequence_counter = 0
        return self.__sequence_counter

    @sequence_counter.setter
    def sequence_counter(self, new_value):
        self.__sequence_counter = new_value

    def __create_group_value_read_or_write_message(self):

        data_size = {
            '1 Bit': (0x01, 0x0011),
            '4 Bits': (0x01, 0x0011),
            '1 Byte': (0x02, 0x0012),
            '2 Bytes': (0x03, 0x0013),
        }

        control_field1 = ((((((0b10 << 1) | self.CEMI_REPEATED_TELEGRAM['No']) << 1) | 0b1) << 2) |
                          self.CEMI_PRIORITIES[self.__cemi_priority]) << 2
        control_field2 = ((self.RECEIVER_ADDRESS_TYPES['Group Telegram'] << 3) | self.ROUTING_COUNTER) << 4
        source_address = 0x0000

        t_pdu = [0x00, 0x00]
        if self.__data_size == '1 Bit' or self.__data_size == '4 Bits':
            t_pdu[0] = (((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                        self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2)
            t_pdu[1] = (((self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] << 6) |
                         self.get_data('INTEGER')) & 0xFF)
        else:
            t_pdu[0] = (((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                        self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2)
            t_pdu[1] = ((self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] << 6) & 0xFF)

        created_message = b''.join([pack('>2B2H4BH',

                                         self.HEADER_SIZE_10,
                                         self.KNX_NET_IP_VERSION,
                                         self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                                         data_size[self.__data_size][1],

                                         self.CEMI_MESSAGE_CODES['L_Data.ind'],
                                         0x00,
                                         control_field1,
                                         control_field2,
                                         source_address
                                         ),
                                    self.get_group_address('BINARY'),
                                    pack('>3B', data_size[self.__data_size][0], t_pdu[0], t_pdu[1])])

        if self.__data_size == '1 Byte':
            created_message = b''.join([created_message, pack('>s', self.get_data('BINARY'))])
        elif self.__data_size == '2 Bytes':
            created_message = b''.join([created_message, pack('>2s', self.get_data('BINARY'))])

        return created_message

    def __create_tunnelling_value_read_or_write_message(self):

        data_size = {
            '1 Bit': (0x01, 0x0015),
            '4 Bits': (0x01, 0x0015),
            '1 Byte': (0x02, 0x0016),
            '2 Bytes': (0x03, 0x0017),
        }

        control_field1 = ((((((0b10 << 1) | self.CEMI_REPEATED_TELEGRAM['No']) << 1) | 0b1) << 2) |
                          self.CEMI_PRIORITIES[self.__cemi_priority]) << 2
        control_field2 = ((self.RECEIVER_ADDRESS_TYPES['Group Telegram'] << 3) | self.ROUTING_COUNTER) << 4
        source_address = 0x0000

        t_pdu = [0x00, 0x00]
        if self.__data_size == '1 Bit' or self.__data_size == '4 Bits':
            t_pdu[0] = (((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                        self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2)
            t_pdu[1] = (((self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] << 6) |
                         self.get_data('INTEGER')) & 0xFF)
        else:
            t_pdu[0] = (((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                        self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2)
            t_pdu[1] = ((self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] << 6) & 0xFF)

        created_message = b''.join([pack('>2B2H4B4BH',

                                         self.HEADER_SIZE_10,
                                         self.KNX_NET_IP_VERSION,
                                         self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                                         data_size[self.__data_size][1],


                                         0x04,
                                         self.__communication_channel_id,
                                         self.__sequence_counter,
                                         0x00,

                                         self.CEMI_MESSAGE_CODES['L_Data.req'],
                                         0x00,
                                         control_field1,
                                         control_field2,
                                         source_address
                                         ),
                                    self.get_group_address('BINARY'),
                                    pack('>3B', data_size[self.__data_size][0], t_pdu[0], t_pdu[1])])

        if self.__data_size == '1 Byte':
            created_message = b''.join([created_message, pack('>s', self.get_data('BINARY'))])
        elif self.__data_size == '2 Bytes':
            created_message = b''.join([created_message, pack('>2s', self.get_data('BINARY'))])

        return created_message

    def __create_endpoint_search_or_description_request(self):

        return b''.join([pack('>2B2H6BH',
                              self.HEADER_SIZE_10,
                              self.KNX_NET_IP_VERSION,
                              self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                              0x000E,
                              0x08,
                              0x01,
                              self.__control_endpoint_details[0][0],
                              self.__control_endpoint_details[0][1],
                              self.__control_endpoint_details[0][2],
                              self.__control_endpoint_details[0][3],
                              self.__control_endpoint_details[1])])

    def __create_endpoint_connect_request(self):

        return b''.join([pack('>2B2H6BH6BH4B',
                              self.HEADER_SIZE_10,
                              self.KNX_NET_IP_VERSION,
                              self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                              0x001A,
                              0x08,
                              0x01,
                              self.__control_endpoint_details[0][0],
                              self.__control_endpoint_details[0][1],
                              self.__control_endpoint_details[0][2],
                              self.__control_endpoint_details[0][3],
                              self.__control_endpoint_details[1],
                              0x08,
                              0x01,
                              self.__control_endpoint_details[0][0],
                              self.__control_endpoint_details[0][1],
                              self.__control_endpoint_details[0][2],
                              self.__control_endpoint_details[0][3],
                              self.__control_endpoint_details[1],
                              0x04,
                              0x04,
                              0x02,
                              0x00)])

    def __create_endpoint_connectionstate_request(self):

        return b''.join([pack('>2B2H8BH',
                              self.HEADER_SIZE_10,
                              self.KNX_NET_IP_VERSION,
                              self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                              0x0010,
                              self.__communication_channel_id,
                              0x00,
                              0x08,
                              0x01,
                              self.__control_endpoint_details[0][0],
                              self.__control_endpoint_details[0][1],
                              self.__control_endpoint_details[0][2],
                              self.__control_endpoint_details[0][3],
                              self.__control_endpoint_details[1]
                              )])

    def __create_endpoint_disconnect_request(self):

        return b''.join([pack('>2B2H8BH',
                              self.HEADER_SIZE_10,
                              self.KNX_NET_IP_VERSION,
                              self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                              0x0010,
                              self.__communication_channel_id,
                              0x00,
                              0x08,
                              0x01,
                              self.__control_endpoint_details[0][0],
                              self.__control_endpoint_details[0][1],
                              self.__control_endpoint_details[0][2],
                              self.__control_endpoint_details[0][3],
                              self.__control_endpoint_details[1]
                              )])

    def __create_tunnelling_acknowledge_response(self):

        return b''.join([pack('>2B2H4B',
                              self.HEADER_SIZE_10,
                              self.KNX_NET_IP_VERSION,
                              self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                              0x000A,
                              0x04,
                              self.__communication_channel_id,
                              self.__sequence_counter,

                              0x00
                              )])

    def __create_routing_group_value_read_regex(self):

        regex_size = {
            '1 Bit': (0x01, 0x0011),
            '4 Bits': (0x01, 0x0011),
            '1 Byte': (0x02, 0x0012),
            '2 Bytes': (0x03, 0x0013)
        }

        control_field1 = ((((((0b10 << 1) | self.CEMI_REPEATED_TELEGRAM['No']) << 1) | 0b1) << 2) |
                          self.CEMI_PRIORITIES[self.__cemi_priority]) << 2
        control_field2 = ((self.RECEIVER_ADDRESS_TYPES['Group Telegram'] << 3) | self.ROUTING_COUNTER) << 4

        created_regex = b''
        regex_header = BinaryHexRegex(pack('>2B2H4B',
                                           self.HEADER_SIZE_10,
                                           self.KNX_NET_IP_VERSION,
                                           self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                                           regex_size[self.__regex_size][1],
                                           self.CEMI_MESSAGE_CODES['L_Data.ind'],
                                           0x00,
                                           control_field1,
                                           control_field2))
        regex_header.add_meta_character_data(b'[\x00-\xFF]{2}')
        regex_header.add_data_section(pack('>2s2B', self.get_group_address('BINARY'), regex_size[self.__regex_size][0],
                                           ((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                                           self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2))

        if self.__regex_size == '1 Bit':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b1 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b1 & 0xFF))
            regex_end.add_meta_character_data(b')')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        elif self.__regex_size == '4 Bits':

            created_regex = b''

        elif self.__regex_size == '1 Byte':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(?:')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b')([\x00-\xFF])')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        elif self.__regex_size == '2 Bytes':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(?:')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b')([\x00-\xFF]{2})')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        return created_regex

    def __create_tunnelling_group_value_read_regex(self):

        regex_size = {
            '1 Bit': (0x01, 0x0015),
            '4 Bits': (0x01, 0x0015),
            '1 Byte': (0x02, 0x0016),
            '2 Bytes': (0x03, 0x0017)
        }

        control_field1a = ((((((0b10 << 1) | self.CEMI_REPEATED_TELEGRAM['No']) << 1) | 0b1) << 2) |
                           self.CEMI_PRIORITIES[self.__cemi_priority]) << 2
        control_field1b = ((((((0b10 << 1) | self.CEMI_REPEATED_TELEGRAM['Yes']) << 1) | 0b1) << 2) |
                           self.CEMI_PRIORITIES[self.__cemi_priority]) << 2
        control_field2 = ((self.RECEIVER_ADDRESS_TYPES['Group Telegram'] << 3) | self.ROUTING_COUNTER) << 4

        created_regex = b''
        regex_header = BinaryHexRegex(pack('>2B2H',

                                           self.HEADER_SIZE_10,
                                           self.KNX_NET_IP_VERSION,
                                           self.KNX_NET_IP_SERVICE_TYPES[self.__knx_net_ip_service_type],
                                           regex_size[self.__regex_size][1]))

        regex_header.add_data_section(pack('B',


                                           0x04))
        regex_header.add_meta_character_data(b'([\x00-\xFF])([\x00-\xFF])')
        regex_header.add_data_section(pack('B', 0x00))

        regex_header.add_data_section(pack('2B',
                                           self.CEMI_MESSAGE_CODES['L_Data.ind'],
                                           0x00))
        regex_header.add_meta_character_data(b'[')
        regex_header.add_data_section(pack('2B', control_field1a, control_field1b))
        regex_header.add_meta_character_data(b']')
        regex_header.add_data_section(pack('B', control_field2))
        regex_header.add_meta_character_data(b'[\x00-\xFF]{2}')
        regex_header.add_data_section(pack('>2s2B', self.get_group_address('BINARY'), regex_size[self.__regex_size][0],
                                           ((self.T_PDU_COMMUNICATION_TYPES['UDP'] << 4) | 0b0000 << 4) |
                                           self.APCI_TELEGRAM_TYPES[self.__apci_telegram_type] >> 2))

        if self.__regex_size == '1 Bit':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b1 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b1 & 0xFF))
            regex_end.add_meta_character_data(b')')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        elif self.__regex_size == '4 Bits':

            created_regex = b''

        elif self.__regex_size == '1 Byte':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(?:')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b')([\x00-\xFF])')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        elif self.__regex_size == '2 Bytes':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(?:')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b')([\x00-\xFF]{2})')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        return created_regex

    def encode_message(self):

        new_message = b''
        if self.__knx_net_ip_service_type in ['ROUTING_INDICATION']:
            if self.__apci_telegram_type in ['GroupValueWrite', 'GroupValueRead']:
                new_message = self.__create_group_value_read_or_write_message()
        elif self.__knx_net_ip_service_type in ['SEARCH_REQUEST', 'DESCRIPTION_REQUEST']:
            new_message = self.__create_endpoint_search_or_description_request()
        elif self.__knx_net_ip_service_type in ['CONNECT_REQUEST']:
            new_message = self.__create_endpoint_connect_request()
        elif self.__knx_net_ip_service_type in ['CONNECTIONSTATE_REQUEST']:
            new_message = self.__create_endpoint_connectionstate_request()
        elif self.__knx_net_ip_service_type in ['TUNNELLING_REQUEST']:
            if self.__apci_telegram_type in ['GroupValueWrite', 'GroupValueRead']:
                new_message = self.__create_tunnelling_value_read_or_write_message()
        elif self.__knx_net_ip_service_type in ['TUNNELLING_ACK']:
            new_message = self.__create_tunnelling_acknowledge_response()
        elif self.__knx_net_ip_service_type in ['DISCONNECT_REQUEST']:
            new_message = self.__create_endpoint_disconnect_request()
        self.__encoded_message = new_message
        return self.__encoded_message

    def get_message(self, output_format='BINARY'):

        if output_format == 'BINARY':
            return self.__encoded_message
        elif output_format == 'PRINT':
            msg_len = len(self.__encoded_message)
            return ''.join(["%02X " % _ for _ in unpack('>{}B'.format(msg_len), self.__encoded_message)]).strip()

    def create_status_regex(self):

        self.__created_status_regex = b''
        if self.__knx_net_ip_service_type in ['ROUTING_INDICATION']:
            if self.__apci_telegram_type in ['GroupValueRead']:
                self.__created_status_regex = self.__create_routing_group_value_read_regex()
        elif self.__knx_net_ip_service_type in ['TUNNELLING_REQUEST']:
            if self.__apci_telegram_type in ['GroupValueRead']:
                self.__created_status_regex = self.__create_tunnelling_group_value_read_regex()
        return self.__created_status_regex


class BinaryHexRegex(object):

    def __init__(self, data_part=None):
        self.Generated_Regex = pack('>')
        if data_part:
            self.add_data_section(data_part)

    def add_data_section(self, data_part=None):
        if data_part:
            checked_data = escape(data_part)
            self.Generated_Regex = b''.join([self.Generated_Regex, pack('B' * len(checked_data), *checked_data)])

    def add_meta_character_data(self, data):
        self.Generated_Regex = b''.join([self.Generated_Regex, pack('B' * len(data), *data)])

    def get_generated_regex(self):
        return self.Generated_Regex


class SequenceCounter(object):

    _sequence_counter = None

    @property
    def sequence_counter(self):
        if ((not self._sequence_counter and not self._sequence_counter == 0) or
                self._sequence_counter < 0):
            self._sequence_counter = 0
        else:
            self._sequence_counter += 1
        return self._sequence_counter & 0xFF

    @sequence_counter.setter
    def sequence_counter(self, value):
        if value < 0:
            value = 0
        self._sequence_counter = value

    def decrement(self, value=1):
        self._sequence_counter -= value
