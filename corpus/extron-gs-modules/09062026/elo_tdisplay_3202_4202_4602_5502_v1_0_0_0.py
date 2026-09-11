from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._SerialNumber = b'0000000000'   # Not a real serial number just a place holder
        self._SerialNumberSum = 480          # Sum of byte 0000000000
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'TouchControl': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02\x6E[\x80-\xFF][0-9A-Z]{10}\x01\x60\x00(\x80|\x20|\x10)[\x00-\xFF]\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02\x6E[\x80-\xFF][0-9A-Z]{10}\x01\xD6\x00(\x01|\x04)[\x00-\xFF]\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02\x6E[\x80-\xFF][0-9A-Z]{10}\x01\xC7\x00(\x00|\x01)[\x00-\xFF]\x03'), self.__MatchTouchControl, None)
            self.AddMatchString(re.compile(b'\x02\x6E[\x80-\xFF][0-9A-Z]{10}\x01\x62\x00\x64(\x00[\x00-\x64])[\x00-\xFF]\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x02\x6E[\x80-\xFF][0-9A-Z]{10}(\x01|\x04)(\x00|\x01|\x02|\x03|\x05)(\x1E|\x60|\x62|\xC7|\xD6)[\x00-\xFF]\x03'), self.__MatchError, None)

    @property
    def SerialNumber(self):
        return self._SerialNumber

    @SerialNumber.setter
    def SerialNumber(self, value):
        if len(value) != 10:
            print('SerialNumber must be 10 ASCII character long')
        else:
            self._SerialNumber = (value).encode()
            self._SerialNumberSum = sum(unpack('>10B', self._SerialNumber))


    def SetAutoImage(self, value, qualifier):

        val = sum(unpack('>2B', b'\x00\x01'))
        length = 0x80 + len(self._SerialNumber + b'\x04\x1E' + b'\x00\x01')
        checksum = (0x6E + length + self._SerialNumberSum + 0x04 + 0x1E + val) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        AutoImageCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x04\x1E' + b'\x00\x01' + checksum_byte + b'\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x00\x80',
            'HDMI': b'\x00\x20',
            'ECM-HDMI': b'\x00\x10'
        }

        val = sum(unpack('>2B', ValueStateValues[value]))
        length = 0x80 + len(self._SerialNumber + b'\x04\x60' + ValueStateValues[value])
        checksum = (0x6E + length + self._SerialNumberSum + 0x04 + 0x60 + val) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        InputCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x04\x60' + ValueStateValues[value] + checksum_byte + b'\x03'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        length = 0x80 + len(self._SerialNumber + b'\x01\x60')
        checksum = (0x6E + length + self._SerialNumberSum + 0x01 + 0x60) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        InputCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x01\x60' + checksum_byte + b'\x03'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x80': 'VGA',
            b'\x20': 'HDMI',
            b'\x10': 'ECM-HDMI'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00\x01',
            'Off': b'\x00\x04'
        }

        val = sum(unpack('>2B', ValueStateValues[value]))
        length = 0x80 + len(self._SerialNumber + b'\x04\xD6' + ValueStateValues[value])
        checksum = (0x6E + length + self._SerialNumberSum + 0x04 + 0xD6 + val) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        PowerCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x04\xD6' + ValueStateValues[value] + checksum_byte + b'\x03'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        length = 0x80 + len(self._SerialNumber + b'\x01\xD6')
        checksum = (0x6E + length + self._SerialNumberSum + 0x01 + 0xD6) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        PowerCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x01\xD6' + checksum_byte + b'\x03'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x04': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTouchControl(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00\x01',
            'Off': b'\x00\x00'
        }

        val = sum(unpack('>2B', ValueStateValues[value]))
        length = 0x80 + len(self._SerialNumber + b'\x04\xC7' + ValueStateValues[value])
        checksum = (0x6E + length + self._SerialNumberSum + 0x04 + 0xC7 + val) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        TouchControlCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x04\xC7' + ValueStateValues[value] + checksum_byte + b'\x03'
        self.__SetHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def UpdateTouchControl(self, value, qualifier):

        length = 0x80 + len(self._SerialNumber + b'\x01\xC7')
        checksum = (0x6E + length + self._SerialNumberSum + 0x01 + 0xC7) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        TouchControlCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x01\xC7' + checksum_byte + b'\x03'
        self.__UpdateHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def __MatchTouchControl(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TouchControl', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        length = 0x80 + len(self._SerialNumber + b'\x04\x62') + 2
        checksum = (0x6E + length + self._SerialNumberSum + 0x04 + 0x62 + value) & 0xFF

        val = pack('>H', value)
        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x04\x62' + val + checksum_byte + b'\x03'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        length = 0x80 + len(self._SerialNumber + b'\x01\x62')
        checksum = (0x6E + length + self._SerialNumberSum + 0x01 + 0x62) & 0xFF

        length_byte = pack('>B', length)
        checksum_byte = pack('>B', checksum)

        VolumeCmdString = b'\x02\x6E' + length_byte + self._SerialNumber + b'\x01\x62' + checksum_byte + b'\x03'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('Volume', value, None)

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
        self.counter = 0

        ReadWriteStateValues = {
            b'\x01' : 'Read',
            b'\x04' : 'Write'
        }

        ErrorStateValues = {
            b'\x00' : 'Error',
            b'\x01' : 'COMMAND TYPE not supported by slave',
            b'\x02' : 'Error',
            b'\x03' : 'Error',
            b'\x05' : 'Error'
        }

        CommandStateValues = {
            b'\x1E' : 'Auto Adjust',
            b'\x60' : 'Input',
            b'\xD6' : 'Power',
            b'\xC7' : 'Touch Control',
            b'\x62' : 'Volume'
        }

        val1 = ReadWriteStateValues[match.group(1)]
        val2 = ErrorStateValues[match.group(2)]
        val3 = CommandStateValues[match.group(3)]
        self.Error(['{0} {1}: {2}'.format(val3, val1, val2)])

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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

