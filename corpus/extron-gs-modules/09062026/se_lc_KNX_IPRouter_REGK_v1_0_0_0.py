from extronlib.interface import EthernetClientInterface
from re import compile, DOTALL, escape, search
from struct import pack, unpack
from binascii import hexlify, unhexlify

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmbientTemperature': {'Status': {},
                                    'Parameters': ['GroupAddress', 'Scale']},
            'Dimmer': {'Status': {},
                                    'Parameters': ['GroupAddress']},
            'Scaling': {'Status': {},
                                    'Parameters': ['GroupAddress']},
            'Switch': {'Status': {},
                                    'Parameters': ['GroupAddress']},
            'ThermostatSetpoint': {'Status': {},
                                    'Parameters': ['GroupAddress', 'Scale']},
        }

        self.addresses = dict()

        self._DevicesTemperatureScale = 'Celsius (centigrade)'
        self.UnicastIPPort = 3671
        self.ControllerIPAddress = '192.168.254.250'

    @property
    def DevicesTemperatureScale(self):
        return 'Fahrenheit' if self._DevicesTemperatureScale == 'FAH' else 'Celsius (centigrade)'

    @DevicesTemperatureScale.setter
    def DevicesTemperatureScale(self, value):
        if value == 'Fahrenheit':
            self._DevicesTemperatureScale = 'FAH'
        elif value == 'Celsius (centigrade)':
            self._DevicesTemperatureScale = 'CEL'
        else:
            print('Invalid DevicesTemperatureScale. Must be either Fahrenheit or Celsius (centigrade).')

    @property
    def ControllerIPAddress(self):
        return self.Controller_IP_address

    @ControllerIPAddress.setter
    def ControllerIPAddress(self, controller_ip_address):
        ip_match_regex = compile('^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.){3}(?:25[0-5]'
                                     '|2[0-4]\d|1\d\d|[1-9]\d?|\d)$')
        self.Controller_IP_address = ip_match_regex.match(controller_ip_address)
        if self.Controller_IP_address:
            self.Controller_IP_address = self.Controller_IP_address.group(0).split('.')
            self.Controller_IP_address = list(map(lambda val: int(val), self.Controller_IP_address))
        else:
            print('Missing or wrongly formulated Controller IP Address.')

    @property
    def UnicastIPPort(self):
        return self.Unicast_IP_port

    @UnicastIPPort.setter
    def UnicastIPPort(self, unicast_ip_port):
        if 0 <= unicast_ip_port <= 65535:
            self.Unicast_IP_port = unicast_ip_port
        else:
            print('Unicast IP Port must be greater than 0 and less than or equal to 65535.')

    def UpdateAmbientTemperature(self, value, qualifier):

        se_msg = SeKnxMsg(qualifier['GroupAddress'], apci_telegram_type='GroupValueRead')

        se_msg.set_data(0, '1 Bit')
        if se_msg:
            self.__UpdateHelper('AmbientTemperature', se_msg, value, qualifier)
        else:
            print('Invalid Command for UpdateAmbientTemperature')

    def __MatchAmbientTemperature(self, match, tag):

        temp_value = int.from_bytes(match.group(1), byteorder='big')
        if self._DevicesTemperatureScale == 'CEL':
            celsius_value = convert_from_knx_float(temp_value)
            fahrenheit_value = celsius_to_fahrenheit(celsius_value)
        else:
            fahrenheit_value = convert_from_knx_float(temp_value)
            celsius_value = fahrenheit_to_celsius(fahrenheit_value)
        qualifier1 = dict()
        qualifier1['GroupAddress'] = self.addresses[tag][0]
        qualifier2 = dict()
        qualifier2['GroupAddress'] = self.addresses[tag][0]
        qualifier1['Scale'] = 'Celsius'
        self.WriteStatus('AmbientTemperature', celsius_value, qualifier1)
        qualifier2['Scale'] = 'Fahrenheit'
        self.WriteStatus('AmbientTemperature', fahrenheit_value, qualifier2)

    def SetDimmer(self, value, qualifier):

        StateStateValues = {
            'Up': '09',
            'Down': '01',
            'Stop': '00'
        }
        se_msg = SeKnxMsg(qualifier['GroupAddress'])
        if se_msg:
            se_msg.set_data(StateStateValues[value], '4 Bits')
            self.__SetHelper('Dimmer', se_msg, value, qualifier)
        else:
            print('Invalid Command for SetDimmer')


    def SetScaling(self, value, qualifier):

        level_constraints={
            'Min': 0,
            'Max': 255
        }
        se_msg = SeKnxMsg(qualifier['GroupAddress'])
        if level_constraints['Min'] <= value <= level_constraints['Max'] and se_msg:
            se_msg.set_data(value, '1 Byte')
            self.__SetHelper('Scaling', se_msg, value, qualifier)
        else:
            print('Invalid Command for SetScaling')

    def UpdateScaling(self, value, qualifier):

        se_msg = SeKnxMsg(qualifier['GroupAddress'], apci_telegram_type='GroupValueRead')

        se_msg.set_data(0, '1 Bit')
        if se_msg:
            self.__UpdateHelper('Scaling', se_msg, value, qualifier)
        else:
            print('Invalid Command for UpdateScaling')

    def __MatchScaling(self, match, tag):

        temp_value = int.from_bytes(match.group(1), byteorder='big')
        qualifier = dict()
        qualifier['GroupAddress'] = self.addresses[tag][0]
        self.WriteStatus('Scaling', temp_value, qualifier)

    def SetSwitch(self, value, qualifier):

        state_values = {
            'On':  '01',
            'Off': '00'
        }
        se_msg = SeKnxMsg(qualifier['GroupAddress'])
        if se_msg:
            se_msg.set_data(state_values[value], '1 Bit')
            self.__SetHelper('Switch', se_msg, value, qualifier)
        else:
            print('Invalid Command for SetSwitch')

    def UpdateSwitch(self, value, qualifier):

        se_msg = SeKnxMsg(qualifier['GroupAddress'], apci_telegram_type='GroupValueRead')
        se_msg.set_data(0, '1 Bit')
        if se_msg:
            self.__UpdateHelper('Switch', se_msg, value, qualifier)
        else:
            print('Invalid Command for UpdateSwitch')

    def __MatchSwitch(self, match, tag):

        state_values = {
            '01': 'On',
            '00': 'Off'
        }
        temp_value = '{:02x}'.format(int.from_bytes(match.group(1), byteorder='big') & 0b00000001)
        qualifier = dict()
        qualifier['GroupAddress'] = self.addresses[tag][0]
        value = state_values[temp_value]
        self.WriteStatus('Switch', value, qualifier)

    def SetThermostatSetpoint(self, value, qualifier):

        se_msg = SeKnxMsg(qualifier['GroupAddress'])
        if se_msg:
            if qualifier['Scale'] == 'Fahrenheit':
                fahrenheit_value = value
                celsius_value = fahrenheit_to_celsius(fahrenheit_value)
            else:
                celsius_value = value
                fahrenheit_value = celsius_to_fahrenheit(celsius_value)
            if self._DevicesTemperatureScale == 'CEL':
                se_msg.set_data('{:04X}'.format(convert_to_knx_float(celsius_value)), '2 Bytes')
            else:
                se_msg.set_data('{:04X}'.format(convert_to_knx_float(fahrenheit_value)), '2 Bytes')
            qualifier1 = dict()
            qualifier1['GroupAddress'] = qualifier['GroupAddress']
            qualifier2 = dict()
            qualifier2['GroupAddress'] = qualifier['GroupAddress']
            qualifier1['Scale'] = 'Celsius'
            qualifier2['Scale'] = 'Fahrenheit'
            self.__SetHelper('ThermostatSetpoint', se_msg, value, qualifier)
        else:
            print('Invalid Command for SetThermostatSetpoint')

    def UpdateThermostatSetpoint(self, value, qualifier):

        se_msg = SeKnxMsg(qualifier['GroupAddress'], apci_telegram_type='GroupValueRead')

        se_msg.set_data(0, '1 Bit')
        if se_msg:
            self.__UpdateHelper('ThermostatSetpoint', se_msg, value, qualifier)
        else:
            print('Invalid Command for UpdateThermostatSetpoint')

    def __MatchThermostatSetpoint(self, match, tag):

        knx_value = int.from_bytes(match.group(1), byteorder='big')
        if self._DevicesTemperatureScale == 'CEL':
            celsius_value = convert_from_knx_float(knx_value)
            fahrenheit_value = celsius_to_fahrenheit(celsius_value)
        else:
            fahrenheit_value = convert_from_knx_float(knx_value)
            celsius_value = fahrenheit_to_celsius(fahrenheit_value)
        qualifier1 = dict()
        qualifier1['GroupAddress'] = self.addresses[tag][0]
        qualifier2 = dict()
        qualifier2['GroupAddress'] = self.addresses[tag][0]
        qualifier1['Scale'] = 'Celsius'
        self.WriteStatus('ThermostatSetpoint', celsius_value, qualifier1)
        qualifier2['Scale'] = 'Fahrenheit'
        self.WriteStatus('ThermostatSetpoint', fahrenheit_value, qualifier2)

    def __SetHelper(self, command, se_msg, value, qualifier):
        self.Debug = True



        self.Send(se_msg.encode_message())

    def __UpdateHelper(self, command, se_msg, value, qualifier):

        matches = {
            'AmbientTemperature': self.__MatchAmbientTemperature,
            'Scaling': self.__MatchScaling,
            'Switch': self.__MatchSwitch,
            'ThermostatSetpoint': self.__MatchThermostatSetpoint
        }
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if command in matches:
                address = se_msg.get_group_address('HEX')
                self.addresses[address] = [se_msg.get_group_address('PRINT'), matches[command]]
                if command == 'Switch':
                    se_msg.set_regex_type('1 Bit')
                    self.AddMatchString(compile(se_msg.create_status_regex(), DOTALL), self.__MatchAll, address)
                elif command == 'Scaling':
                    se_msg.set_regex_type('1 Byte')
                    self.AddMatchString(compile(se_msg.create_status_regex(), DOTALL), self.__MatchAll, address)
                elif command in ('AmbientTemperature', 'ThermostatSetpoint'):
                    se_msg.set_regex_type('2 Bytes')
                    self.AddMatchString(compile(se_msg.create_status_regex(), DOTALL), self.__MatchAll, address)

            self.Send(se_msg.encode_message())

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchAll(self, match, tag):
        self.addresses[tag][1](match, tag)

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
            print(command, 'does not exist in the module')

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
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it was matched with device expectancy. 
    def CheckMatchedString(self):
        compile_dict = self._compile_list.copy()
        for regexString in compile_dict:
            while True:
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    compile_dict[regexString]['callback'](result, compile_dict[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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

def convert_from_knx_float(knx_value):

    value = knx_value & 0x07FF
    if (knx_value & 0x08000) != 0:
        value |= (~0x07FF)
        value = -value
    value <<= ((knx_value & 0x07800) >> 11)
    if (knx_value & 0x08000) != 0:
        value = -value
    return round(value / 100, 2)


def celsius_to_fahrenheit(degrees_celsius):
    return round(9.0 / 5.0 * degrees_celsius + 32, 2)

def fahrenheit_to_celsius(degrees_fahrenheit):
    return round((degrees_fahrenheit - 32) * 5.0 / 9.0, 2)

class SeKnxMsg(object):
    HEADER_SIZE_10 = 0x06
    KNX_NET_IP_VERSION = 0x10

    KNX_NET_IP_SERVICE_TYPES = {
        'SEARCH_REQUEST':       0x0201,
        'SEARCH_RESPONSE':      0x0202,
        'DESCRIPTION_REQUEST':  0x0203,
        'DESCRIPTION_RESPONSE': 0x0204,
        'ROUTING_INDICATION':   0x0530,
    }

    CEMI_MESSAGE_CODES = {
        'L_Data.ind': 0x29,
        'L_Data.con': 0x2E,
    }

    CEMI_PRIORITIES = {
        'SYSTEM':   0b00,
        'NORMAL':   0b01,
        'URGENT':   0b10,
        'LOW':      0b11,
    }

    CEMI_REPEATED_TELEGRAM = {
        'Yes':  0b0,
        'No':   0b1,
    }

    T_PDU_COMMUNICATION_TYPES = {
        'UDP': 0b00,
        'NDP': 0b01,
        'UCD': 0b10,
        'NCD': 0b11,
    }

    APCI_TELEGRAM_TYPES = {
        'GroupValueRead':           0b0000,
        'GroupValueResponse':       0b0001,
        'GroupValueWrite':          0b0010,
        'IndividualAddrWrite':      0b0011,
        'IndividualAddrRequest':    0b0100,
        'IndividualAddrResponse':   0b0101,
        'AdcRead':                  0b0110,
        'AdcResponse':              0b0111,
        'MemoryRead':               0b1000,
        'MemoryResponse':           0b1001,
        'MemoryWrite':              0b1010,
        'UserMessage':              0b1011,
        'MaskVersionRead':          0b1100,
        'MaskVersionResponse':      0b1101,
        'Restart':                  0b1110,
        'Escape':                   0b1111,
    }

    RECEIVER_ADDRESS_TYPES = {
        'Individual Telegram':  0b0,
        'Group Telegram':       0b1,
    }

    ROUTING_COUNTER = 0b101

    __data = None
    __data_size = None
    __encoded_message = None
    __created_status_regex = None
    __regex_size = None

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
            'GroupValueRead':           'GroupValueResponse',
            'IndividualAddrRequest':    'IndividualAddrResponse',
            'AdcRead':                  'AdcResponse',
            'MemoryRead':               'MemoryResponse',
            'MaskVersionRead':          'MaskVersionResponse',
        }[self.__apci_telegram_type]]

    @property
    def return_unsolicited_apci_telegram_type(self):
        return self.APCI_TELEGRAM_TYPES[{
            'GroupValueRead':           'GroupValueWrite',
            'IndividualAddrRequest':    'IndividualAddrWrite',
            'MemoryRead':               'MemoryWrite',
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

    def set_regex_type(self, value_size):
        self.__regex_size = value_size

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

    def __create_group_value_read_or_write_message(self):
        data_size = {
            '1 Bit':    (0x01, 0x0011),
            '4 Bits':   (0x01, 0x0011),
            '1 Byte':   (0x02, 0x0012),
            '2 Bytes':  (0x03, 0x0013),
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

    def __create_endpoint_search_or_description_request(self):
        created_message = b''.join([pack('>2B2H6BH',
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
        return created_message

    def __create_group_value_read_regex(self):
        regex_size = {
            '1 Bit':   (0x01, 0x0011),
            '4 Bits':  (0x01, 0x0011),
            '1 Byte':  (0x02, 0x0012),
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
        regex_header.add_meta_character_data(pack('>2s', b'..'))
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
            regex_end.add_meta_character_data(b')(.)')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        elif self.__regex_size == '2 Bytes':
            regex_end = BinaryHexRegex()
            regex_end.add_meta_character_data(b'(?:')
            regex_end.add_data_section(pack('>B', (self.return_unsolicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b'|')
            regex_end.add_data_section(pack('>B', (self.return_solicited_apci_telegram_type << 6) | 0b0 & 0xFF))
            regex_end.add_meta_character_data(b')(..)')
            created_regex = b''.join([regex_header.get_generated_regex(), regex_end.get_generated_regex()])

        return created_regex

    def encode_message(self):
        new_message = b''
        if self.__knx_net_ip_service_type in ['ROUTING_INDICATION']:
            if self.__apci_telegram_type in ['GroupValueWrite', 'GroupValueRead']:
                new_message = self.__create_group_value_read_or_write_message()
        elif self.__knx_net_ip_service_type in ['SEARCH_REQUEST', 'DESCRIPTION_REQUEST']:
            new_message = self.__create_endpoint_search_or_description_request()
        self.__encoded_message = new_message
        return self.__encoded_message

    def get_message(self, output_format='BINARY'):
        if output_format == 'BINARY':
            return self.__encoded_message
        elif output_format == 'PRINT':
            msg_len = len(self.__encoded_message)
            return ''.join(["%02X " % _ for _ in unpack('>{}B'.format(msg_len), self.__encoded_message)]).strip()

    def create_status_regex(self):
        new_regex = b''
        if self.__knx_net_ip_service_type in ['ROUTING_INDICATION']:
            if self.__apci_telegram_type in ['GroupValueRead']:
                new_regex = self.__create_group_value_read_regex()
        self.__created_status_regex = new_regex
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
    
    
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=3671, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
