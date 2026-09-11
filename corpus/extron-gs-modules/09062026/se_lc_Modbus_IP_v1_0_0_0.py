from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
        self._UnitID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Register': {'Parameters': ['Address'], 'Status': {}},
        }       

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x05\xA6\x00\x00\x00\x06.\x06(..)(..)', re.S), self.__MatchRegister, None)
            self.AddMatchString(re.compile(b'\x05\xA6\x00\x00\x00\x03.\x86(\x01|\x02|\x03|\x04)', re.S), self.__MatchError, None)

        self.regex = re.compile(b'\x05\xA6\x00\x00\x00((\x05.\x03\x02..)|(\x03.\x83(\x01|\x02|\x03|\x04)))', re.S)

    @property
    def UnitID(self):
        return self._UnitID

    @UnitID.setter
    def UnitID(self, value):
        if 1 <= int(value) <= 255:
            self._UnitID = int(value)

    def SetRegister(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 65536
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65535
        }
        Address = int(qualifier['Address'])
        if AddressConstraints['Min'] <= Address <= AddressConstraints['Max'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            RegisterCmdString = b'\x05\xA6\x00\x00\x00\x06' + pack('>B', self._UnitID) + b'\x06' + pack('>H', Address - 1) + pack('>H', value)
            self.__SetHelper('Register', RegisterCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRegister')

    def UpdateRegister(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 65536
        }
        Address = qualifier['Address']
        if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
            RegisterCmdString = b'\x05\xA6\x00\x00\x00\x06' + pack('>B', self._UnitID) + b'\x03' + pack('>H', Address - 1) + b'\x00\x01'
            res = self.__UpdateHelper('Register', RegisterCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>H', res[-2:])[0]
                    self.WriteStatus('Register', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateRegister')
        else:
            print('Invalid Command for UpdateRegister')

    def __MatchRegister(self, match, tag):

        qualifier = {}
        qualifier['Address'] = unpack('>H', match.group(1))[0] + 1
        value = unpack('>H', match.group(2))[0]
        self.WriteStatus('Register', value, qualifier)            

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ERROR_CODES = {
            1: "Illegal Function",
            2: "Illegal Data Address",
            3: "Illegal Data Value",
            4: "Server Device Failure"
        }
        if response:
            try:
                if response[7] == 0x83:
                    value = ERROR_CODES.get(response[8], "Unknown Error Occured")
                    print(value)
                    response = ''
            except (KeyError, IndexError):
                print('Invalid/unexpected response for', command)
        return response

    def __MatchError(self, match, tag):

        ERROR_CODES = {
            b'\x01': "Illegal Function",
            b'\x02': "Illegal Data Address",
            b'\x03': "Illegal Data Value",
            b'\x04': "Server Device Failure"
        }
        value = ERROR_CODES[match.group(1)]
        print(value)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
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
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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
