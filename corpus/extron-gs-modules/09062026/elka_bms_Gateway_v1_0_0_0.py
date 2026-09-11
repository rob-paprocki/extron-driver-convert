from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from struct import pack, unpack
from binascii import hexlify, unhexlify
import copy


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
        self._DevicesTemperatureScale = 'CEL'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmbientTemperature': {'Parameters': ['GroupAddress', 'Scale'], 'Status': {}},
            'Button': {'Parameters': ['GroupAddress'], 'Status': {}},
            'Dimmer': {'Parameters': ['GroupAddress'], 'Status': {}},
            'Scaling': {'Parameters': ['GroupAddress'], 'Status': {}},
            'Switch': {'Parameters': ['GroupAddress'], 'Status': {}},
            'ThermostatSetpoint': {'Parameters': ['GroupAddress', 'Scale'], 'Status': {}},
            'UpdateScalingStatus': {'Status': {}},
        }

        self.Addresses = {}
        self.ScaleUpdate = []

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\x02FE.*\r'), self.__MatchError, None)

    @property
    def DevicesTemperatureScale(self):
        return self._DevicesTemperatureScale

    @DevicesTemperatureScale.setter
    def DevicesTemperatureScale(self, value):
        self._DevicesTemperatureScale = 'FAH' if value == 'Fahrenheit' else 'CEL'

    def UpdateAmbientTemperature(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'], Function='KnxGrpRequest')
        if km:
            self.__UpdateHelper('AmbientTemperature', km, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmbientTemperature')

    def __MatchAmbientTemperature(self, match, tag):

        km = KNXMsg(Message=match.group(0))
        knx_value = km.getData(Format='INTEGER')
        if self.DevicesTemperatureScale == 'CEL':
            CelValue = ConvertFromKnxFloat(knx_value)
            FahValue = CelsiusToFahrenheit(CelValue)
        else:
            FahValue = ConvertFromKnxFloat(knx_value)
            CelValue = FahrenheitToCelsius(FahValue)
        qualifier1 = {'GroupAddress': self.Addresses[tag][0], 'Scale': 'Celsius'}
        qualifier2 = {'GroupAddress': self.Addresses[tag][0], 'Scale': 'Fahrenheit'}

        self.WriteStatus('AmbientTemperature', CelValue, qualifier1)
        self.WriteStatus('AmbientTemperature', FahValue, qualifier2)

    def UpdateButton(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'], Function='KnxGrpRequest')
        if km:
            self.__UpdateHelper('Button', km, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateButton')

    def __MatchButton(self, match, tag):

        ValueStateValues = {
            '01': 'Pressed',
            '00': 'Released'
        }
        km = KNXMsg(Message=match.group(0))
        qualifier = {'GroupAddress': self.Addresses[tag][0]}
        value = ValueStateValues[km.getData()]
        self.WriteStatus('Button', value, qualifier)

    def SetDimmer(self, value, qualifier):

        StateStateValues = {
            'Up': '09',
            'Down': '01',
            'Stop': '00'
        }
        km = KNXMsg(qualifier['GroupAddress'])
        if km:
            km.setData(StateStateValues[value])
            self.__SetHelper('Dimmer', km, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmer')

    def SetScaling(self, value, qualifier):

        LevelConstraints = {
            'Min': 0,
            'Max': 255
        }
        km = KNXMsg(qualifier['GroupAddress'])
        if LevelConstraints['Min'] <= value <= LevelConstraints['Max'] and km:
            km.setData(value)
            self.__SetHelper('Scaling', km, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScaling')

    def UpdateScaling(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'], Function='KnxGrpRequest')
        if km:
            self.__UpdateHelper('Scaling', km, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScaling')

    def __MatchScaling(self, match, tag):
        km = KNXMsg(Message=match.group(0))
        qualifier = {'GroupAddress': self.Addresses[tag][0]}
        value = km.getData(Format='INTEGER')
        self.WriteStatus('Scaling', value, qualifier)

    def SetSwitch(self, value, qualifier):

        StateStateValues = {
            'On': '01',
            'Off': '00'
        }
        km = KNXMsg(qualifier['GroupAddress'])
        if km:
            km.setData(StateStateValues[value])
            self.__SetHelper('Switch', km, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitch')

    def UpdateSwitch(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'], Function='KnxGrpRequest')
        if km:
            self.__UpdateHelper('Switch', km, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSwitch')

    def __MatchSwitch(self, match, tag):

        StateStateValues = {
            '01': 'On',
            '00': 'Off'
        }
        km = KNXMsg(Message=match.group(0))
        qualifier = {'GroupAddress': self.Addresses[tag][0]}
        value = StateStateValues[km.getData()]
        self.WriteStatus('Switch', value, qualifier)

    def SetThermostatSetpoint(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'])
        if km:
            if qualifier['Scale'] == 'Fahrenheit':
                FahValue = value
                CelValue = FahrenheitToCelsius(FahValue)
            else:
                CelValue = value
                FahValue = CelsiusToFahrenheit(CelValue)
            if self.DevicesTemperatureScale == 'CEL':
                km.setData('{:04X}'.format(ConvertToKnxFloat(CelValue)))
            else:
                km.setData('{:04X}'.format(ConvertToKnxFloat(FahValue)))

            self.__SetHelper('ThermostatSetpoint', km, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThermostatSetpoint')

    def UpdateThermostatSetpoint(self, value, qualifier):

        km = KNXMsg(qualifier['GroupAddress'], Function='KnxGrpRequest')
        if km:
            self.__UpdateHelper('ThermostatSetpoint', km, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateThermostatSetpoint')

    def __MatchThermostatSetpoint(self, match, tag):
        km = KNXMsg(Message=match.group(0))
        knx_value = km.getData(Format='INTEGER')
        if self.DevicesTemperatureScale == 'CEL':
            CelValue = ConvertFromKnxFloat(knx_value)
            FahValue = CelsiusToFahrenheit(CelValue)
        else:
            FahValue = ConvertFromKnxFloat(knx_value)
            CelValue = FahrenheitToCelsius(FahValue)
        qualifier1 = {'GroupAddress': self.Addresses[tag][0], 'Scale': 'Celsius'}
        qualifier2 = {'GroupAddress': self.Addresses[tag][0], 'Scale': 'Fahrenheit'}
        self.WriteStatus('ThermostatSetpoint', CelValue, qualifier1)
        self.WriteStatus('ThermostatSetpoint', FahValue, qualifier2)

    def SetUpdateScalingStatus(self, value, qualifier):

        if self.ScaleUpdate:
            for ScaleString in self.ScaleUpdate:
                self.Send(ScaleString)
        else:
            self.Discard('Invalid Command for SetUpdateScalingStatus')

    def __SetHelper(self, command, km, value, qualifier):
        self.Debug = True
        self.Send(km.encodeMessage())

    def __UpdateHelper(self, command, km, value, qualifier):

        Matches = {
            'AmbientTemperature': self.__MatchAmbientTemperature,
            'Button': self.__MatchButton,
            'Scaling': self.__MatchScaling,
            'Switch': self.__MatchSwitch,
            'ThermostatSetpoint': self.__MatchThermostatSetpoint
        }
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if command in Matches:
                Address = km.getGroupAddress('HEX')
                self.Addresses[Address] = [km.getGroupAddress('PRINT'), Matches[command]]
                if command in ('AmbientTemperature', 'ThermostatSetpoint'):
                    self.AddMatchString(compile(b'\x02' + km.ReturnFunction + Address + b'[0-9A-F]{6}\r'), self.__MatchAll, Address)
                else:
                    self.AddMatchString(compile(b'\x02' + km.ReturnFunction + Address + b'[0-9A-F]{4}\r'), self.__MatchAll, Address)

                if command == 'Scaling':
                    if km.encodeMessage() not in self.ScaleUpdate:
                        self.ScaleUpdate.append(km.encodeMessage())

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            self.Send(km.encodeMessage())

    def __MatchError(self, match, tag):
        self.Error([match.group(0).decode()])

    def __MatchAll(self, match, tag):
        self.Send(b'\x06')
        self.Addresses[tag][1](match, tag)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.ScaleUpdate = []

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.ScaleUpdate = []

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
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        tempList = copy.copy(self._compile_list)
        for regexString in tempList:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    tempList[regexString]['callback'](result, tempList[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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


class EthernetClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


def swap(dictionary):
    return dict(zip(dictionary.values(), dictionary.keys()))


def ConvertToKnxFloat(value):
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


def ConvertFromKnxFloat(knx_value):
    value = knx_value & 0x07FF
    if (knx_value & 0x08000) != 0:
        value |= (~0x07FF)
        value = -value
    value <<= ((knx_value & 0x07800) >> 11)
    if (knx_value & 0x08000) != 0:
        value = -value
    return round(value / 100, 2)


def CelsiusToFahrenheit(degCel):
    return round(9.0 / 5.0 * degCel + 32, 2)


def FahrenheitToCelsius(degFah):
    return round((degFah - 32) * 5.0 / 9.0, 2)


class KNXMsg(object):
    reGroupAddress = compile(r'^\d{1,2}/\d{1,4}$|^\d{1,2}/\d/\d{1,3}$')

    Functions = {
        'VersionQuery': b'01',
        'VersionResponse': b'81',
        'DataReadQuery': b'03',
        'DataReadResponse': b'83',
        'KnxPolling': b'04',
        'KnxGrpAddrResponse': b'FC',
        'DownloadStart': b'05',
        'DownloadData': b'06',
        'DownloadEnd': b'07',
        'DownloadEndResponse': b'87',
        'GatewayRestart': b'08',
        'ConfigQuery': b'09',
        'ConfigResponse': b'89',
        'KnxGrpTransmit': b'0B',
        'KnxGrpRequest': b'0C',
        'DataReadExtendedQuery': b'0D',
        'DataReadExtendedResponse': b'8D',
        'FlashPageSizeQuery': b'30',
        'FlashPageSizeResponse': b'B0',
        'FlashErasedValueQuery': b'31',
        'FlashErasedValueResponse': b'B1',
        'FlashPageErase': b'32',
        'FlashPageWrite': b'34',
        'DownloadFwStart': b'35',
        'DownloadFwData': b'36',
        'DownloadFwEnd': b'37',
        'ErrorMsg': b'FE',
    }

    Priorities = {
        'Low': b'0C',
        'High': b'04'
    }

    def __init__(self, GroupAddress=None, Function='KnxGrpTransmit', Priority='Low', GroupAddressType=None, Message=None):

        self.__gadType = GroupAddressType

        if GroupAddress:
            self.setGroupAddress(GroupAddress)
        else:
            self.__gad = None

        if Function in self.Functions:
            self.__function = Function
        else:
            raise ValueError('Invalid Function ' + Function)

        if Priority in self.Priorities:
            self.__priority = Priority
        else:
            raise ValueError('Invalid Priority ' + Priority)

        self.setData(None)

        if Message:
            self.decodeMessage(Message)

    def __str__(self):
        return self.getData('PRINT')

    @property
    def ReturnFunction(self):
        return self.Functions[{
            'VersionQuery': 'VersionResponse',
            'DataReadQuery': 'DataReadResponse',
            'KnxPolling': 'KnxGrpAddrResponse',
            'ConfigQuery': 'ConfigResponse',
            'KnxGrpTransmit': 'KnxGrpAddrResponse',
            'KnxGrpRequest': 'KnxGrpAddrResponse',
            'DataReadExtendedQuery': 'DataReadExtendedResponse',
            'FlashPageSizeQuery': 'FlashPageSizeResponse',
            'FlashErasedValueQuery': 'FlashErasedValueResponse',
        }[self.__function]]

    def setGroupAddress(self, GroupAddress):
        if self.reGroupAddress.match(GroupAddress):
            gad = GroupAddress.split('/')
            self.__gadType = '2-level' if len(gad) == 2 else '3-level'
            gad = tuple([int(node) for node in gad])
            if self.__gadType == '2-level':
                if 0 <= gad[0] <= 15 and 0 <= gad[1] <= 2047:
                    self.__gad = gad
                else:
                    raise ValueError('UserInput ' + GroupAddress)
            elif self.__gadType == '3-level':
                if 0 <= gad[0] <= 15 and 0 <= gad[1] <= 7 and 0 <= gad[2] <= 255:
                    self.__gad = gad
                else:
                    raise ValueError('UserInput ' + GroupAddress)
        else:
            raise ValueError('UserInput ' + GroupAddress)

    def getGroupAddress(self, Format='PRINT'):
        if isinstance(self.__gad, tuple):
            if Format == 'BINARY':
                if self.__gadType == '2-level':
                    return ((self.__gad[0] << 11) + self.__gad[1]).to_bytes(2, byteorder='big')
                elif self.__gadType == '3-level':
                    return ((self.__gad[0] << 11) + (self.__gad[1] << 8) + self.__gad[2]).to_bytes(2, byteorder='big')
                else:
                    return self.__gad
            elif Format == 'HEX':
                gad = self.getGroupAddress('BINARY')
                return hexlify(gad).upper()
            elif Format == 'PRINT':
                return '/'.join(str(node) for node in self.__gad)
            else:
                return None
        else:
            return self.__gad

    def setData(self, value):
        try:
            self.__data = hexlify(value.to_bytes(1, byteorder='big')).upper()
        except:
            if isinstance(value, str):
                self.__data = value.encode()
            elif isinstance(value, bytes):
                self.__data = value

    def getData(self, Format='PRINT'):
        if Format == 'INTEGER':
            return int('0x' + self.getData(), 16)
        elif Format == 'BINARY':
            return unhexlify(self.__data)
        elif Format == 'HEX':
            return self.__data
        elif Format == 'PRINT':
            try:
                return self.__data.decode()
            except:
                return self.__data

    def encodeMessage(self):
        m = b''
        if self.__function in ['KnxGrpTransmit']:
            data = self.getData('PRINT')
            if len(data) == 2:
                m = pack('>2s4s2s2s',
                         self.Functions[self.__function],
                         self.getGroupAddress('HEX'),
                         self.Priorities[self.__priority],
                         self.getData('HEX')
                         )
            elif len(data) == 4:
                m = pack('>2s4s2s4s',
                         self.Functions[self.__function],
                         self.getGroupAddress('HEX'),
                         self.Priorities[self.__priority],
                         self.getData('HEX')
                         )
        elif self.__function in ['KnxGrpRequest']:
            m = pack('>2s4s',
                     self.Functions[self.__function],
                     self.getGroupAddress('HEX')
                     )
        elif self.__function in ['VersionQuery', 'KnxPolling']:
            m = pack('>2s',
                     self.Functions[self.__function],
                     )
        checksum = 0
        for byte in unhexlify(m):
            checksum = (checksum + byte) & 0xFF
        checksum = checksum ^ 0xFF
        m += hexlify(checksum.to_bytes(1, byteorder='big'))
        return (b'\x02' + m + b'\x0D').upper()

    def decodeMessage(self, m):
        M = m[1:-3]
        self.__function = swap(self.Functions)[M[0:2]]

        if self.__function in ['KnxGrpTransmit']:
            _, GroupAddress, Priority, Data = unpack('>2s4s2s2s', M)
            self.__priority = swap(self.Priorities)[Priority]
        elif self.__function in ['KnxGrpAddrResponse']:
            if len(M) == 8:
                _, GroupAddress, Data = unpack('>2s4s2s', M)
            elif len(M) == 10:
                _, GroupAddress, Data = unpack('>2s4s4s', M)

        gad = unpack('>H', unhexlify(GroupAddress))[0]
        if self.__gadType == '2-level':
            main = gad >> 11
            sub = gad - (main << 11)
            self.__gad = (main, sub)
        elif self.__gadType == '3-level':
            main = gad >> 11
            middle = (gad - (main << 11)) >> 8
            sub = gad - (main << 11) - (middle << 8)
            self.__gad = (main, middle, sub)
        else:
            self.__gad = GroupAddress.decode()

        self.__data = Data.decode()
