from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
            'AspectRatio': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
        }

        if 'Serial' not in self.ConnectionType:
            self._DeviceID = 0
        else:
            self._DeviceID = 1

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x21\x0B\xC0([\x00-\xFF]{1,6})[\x00-\xFF]\xFF'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x21\x23(\x00|\x01)[\x00-\xFF]\xFF'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x32([\x01-\x04])[\x00-\xFF]\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x76\x90([\x00-\xFF]{4})[\x00-\xFF]\xFF'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x62([\x00-\xFF]{4})[\x00-\xFF]\xFF'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]+\xFF\xFE[\x00-\xFF]\x67([\x00-\xFF])[\x00-\xFF]\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]\x00\x15[\x00-\xFF]\xFF'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if self.ConnectionType == 'Serial':
            if 1 <= int(value) <= 255:
                self._DeviceID = int(value)
            else:
                self.Error(['Device ID should be a value between 1 to 255.'])
        else:
            self.Error(['Device ID is not changeable for Ethernet control.'])

    def SetAspectRatio(self, value, qualifier):

        temp_list = []
        temp_str = b''
        temp_chksum = 0
        for x in value:
            temp_list.append(x)
        for x in temp_list:
            temp_str += pack('>B', ord(x))
            temp_chksum += ord(x)
        chksum = (self._DeviceID + 0x20 + 0x0B + 0xC0 + temp_chksum) % 256

        AspectRatioCmdString = b'\xFE' + pack('>B', self._DeviceID) + b'\x20\x0B\xC0' + temp_str + pack('>2B', chksum, 0xFF)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        chksum = (self._DeviceID + 0x21 + 0x0B + 0xC0) % 256

        AspectRatioCmdString = b'\xFE' + pack('>B', self._DeviceID) + b'\x21\x0B\xC0' + pack('>2B', chksum, 0xFF)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '4:3': '4:3',
            '16:9': '16:9',
            '5:4': '5:4',
            '2.35': '2.35',
            '1.88': '1.88',
            '1.85': '1.85',
            '1.78': '1.78',
            '16:10': '16:10',
            '1.67': '1.67',
            'Custom': 'Custom'
        }

        value = match.group(1).decode()
        self.WriteStatus('AspectRatio', ValueStateValues[value], None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 0x27,
            'Off': 0x26
        }
        chksum = (self._DeviceID + ValueStateValues[value] + 0x23) % 256

        FreezeCmdString = pack('>6B', 0xFE, self._DeviceID, ValueStateValues[value], 0x23, chksum, 0xFF)

        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        chksum = (self._DeviceID + 0x21 + 0x23) % 256

        FreezeCmdString = pack('>6B', 0xFE, self._DeviceID, 0x21, 0x23, chksum, 0xFF)
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
        }
        chksum = (self._DeviceID + 0x31 + ValueStateValues[value]) % 256

        InputCmdString = pack('>6B', 0xFE, self._DeviceID, 0x31, ValueStateValues[value], chksum, 0xFF)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        chksum = (self._DeviceID + 0x32) % 256

        InputCmdString = pack('>5B', 0xFE, self._DeviceID, 0x32, chksum, 0xFF)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x01': '1',
            '\x02': '2',
            '\x03': '3',
            '\x04': '4',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }
        chksum = (self._DeviceID + 0x76 + 0x1A + ValueStateValues[value]) % 256

        LampPowerCmdString = pack('>7B', 0xFE, self._DeviceID, 0x76, 0x1A, ValueStateValues[value], chksum, 0xFF)
        self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)

    def UpdateLampPower(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        chksum = (self._DeviceID + 0x76 + 0x90) % 256

        LampUsageCmdString = pack('>6B', 0xFE, self._DeviceID, 0x76, 0x90, chksum, 0xFF)
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        lamp_value = match.group(1)
        value = ((lamp_value[0] * (256 ** 3)) + (lamp_value[1] * (256 ** 2)) + (lamp_value[2] * 256) + lamp_value[3]) / 3600
        self.WriteStatus('LampUsage', round(value), None)

    def UpdateOperationHours(self, value, qualifier):
        chksum = (self._DeviceID + 0x62) % 256

        OperationHoursCmdString = pack('>5B', 0xFE, self._DeviceID, 0x62, chksum, 0xFF)
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        oper_value = match.group(1)
        value = ((oper_value[0] * (256 ** 3)) + (oper_value[1] * (256 ** 2)) + (oper_value[2] * 256) + oper_value[3]) / 3600
        self.WriteStatus('OperationHours', round(value), None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x65,
            'Off': 0x66,
        }
        chksum = (self._DeviceID + ValueStateValues[value]) % 256

        PowerCmdString = pack('>5B', 0xFE, self._DeviceID, ValueStateValues[value], chksum, 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        chksum = (self._DeviceID + 0x67) % 256

        PowerCmdString = pack('>5B', 0xFE, self._DeviceID, 0x67, chksum, 0xFF)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        pow_value = bin(ord(match.group(1).decode()))[2:].zfill(8)

        self.WriteStatus('Power', ValueStateValues[pow_value[-1]], None)
        self.WriteStatus('LampPower', ValueStateValues[pow_value[1]], None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.Error(['Error Reply Received'])

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
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
