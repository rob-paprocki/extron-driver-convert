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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }    

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]{1,2}\x32([\x01-\x04])[\x00-\xFF]{1,2}\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]{1,2}\x64([\x00-\xFF]{4,8})[\x00-\xFF]{1,2}\xFF'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]{1,2}\x62([\x00-\xFF]{4,8})[\x00-\xFF]{1,2}\xFF'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]{1,2}\x67([\x00-\xFF])[\x00-\xFF]{1,2}\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\xFF]{1,2}\x00\x15[\x00-\xFF]{1,2}\xFF'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 255:
            self._DeviceID = int(value)

    def escaped(self, Data):
        d = 0
        List = []
        Escaped = {
            0x80: [0x80, 0x00],
            0xFE: [0x80, 0x7E],
            0xFF: [0x80, 0x7F]
        }
        for d in Data:
            if d in Escaped:
                List.append(Escaped[d][0])
                List.append(Escaped[d][1])
            else:
                List.append(d)
        return List

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            Crc = (Crc + Data[i]) % 256
        return Crc

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': [self._DeviceID, 0x27, 0x23],
            'Off': [self._DeviceID, 0x26, 0x23]
        }
        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        FreezeCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': [self._DeviceID, 0x31, 0x01],
            '2': [self._DeviceID, 0x31, 0x02],
            '3': [self._DeviceID, 0x31, 0x03],
            '4': [self._DeviceID, 0x31, 0x04]
        }
        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        InputCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        buffer = self.escaped([self._DeviceID, 0x32])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        InputCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x01': '1',
            '\x02': '2',
            '\x03': '3',
            '\x04': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': [self._DeviceID, 0x30, 0x19],
            '1': [self._DeviceID, 0x30, 0x10],
            '2': [self._DeviceID, 0x30, 0x11],
            '3': [self._DeviceID, 0x30, 0x12],
            '4': [self._DeviceID, 0x30, 0x13],
            '5': [self._DeviceID, 0x30, 0x14],
            '6': [self._DeviceID, 0x30, 0x15],
            '7': [self._DeviceID, 0x30, 0x16],
            '8': [self._DeviceID, 0x30, 0x17],
            '9': [self._DeviceID, 0x30, 0x18]
        }

        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        KeypadCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        buffer = self.escaped([self._DeviceID, 0x64])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        LampUsageCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        temp = match.group(1)
        if b'\x80\x00' in temp:
            temp = temp.replace(b'\x80\x00', b'\x80')
        if b'\x80\x7E' in temp:
            temp = temp.replace(b'\x80\x7E', b'\xFE')
        if b'\x80\x7F' in temp:
            temp = temp.replace(b'\x80\x7F', b'\xFF')
        value = temp[0] * 256**3 + temp[1] * 256**2 + temp[2] * 256 + temp[3]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': [self._DeviceID, 0x30, 0x04],
            'Down': [self._DeviceID, 0x30, 0x05],
            'Left': [self._DeviceID, 0x30, 0x07],
            'Right': [self._DeviceID, 0x30, 0x06],
            'Menu': [self._DeviceID, 0x30, 0x09],
            'Enter': [self._DeviceID, 0x30, 0x0A],
            'Exit': [self._DeviceID, 0x30, 0x08]
        }

        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        MenuNavigationCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        buffer = self.escaped([self._DeviceID, 0x62])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        OperationHoursCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        temp = match.group(1)
        if b'\x80\x00' in temp:
            temp = temp.replace(b'\x80\x00', b'\x80')
        if b'\x80\x7E' in temp:
            temp = temp.replace(b'\x80\x7E', b'\xFE')
        if b'\x80\x7F' in temp:
            temp = temp.replace(b'\x80\x7F', b'\xFF')
        value = int((temp[0] * 256**3 + temp[1] * 256**2 + temp[2] * 256 + temp[3]) / 3600)
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [self._DeviceID, 0x65],
            'Off': [self._DeviceID, 0x66]
        }
        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        PowerCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        buffer = self.escaped([self._DeviceID, 0x67])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        PowerCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateValues = {
            1: 'On',
            0: 'Off'
        }
        VideoMuteStateValues = {
            4: 'On',
            0: 'Off'
        }
        FreezeStateValues = {
            8: 'On',
            0: 'Off'
        }
        temp = ord(match.group(1).decode())
        PowerValue = PowerStateValues[temp & 1]
        VideoMuteValue = VideoMuteStateValues[temp & 4]
        FreezeValue = FreezeStateValues[temp & 8]

        self.WriteStatus('Power', PowerValue, None)
        self.WriteStatus('VideoMute', VideoMuteValue, None)
        self.WriteStatus('Freeze', FreezeValue, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': [self._DeviceID, 0x27, 0x3E],
            'Off': [self._DeviceID, 0x26, 0x3E]
        }
        buffer = self.escaped(ValueStateValues[value])
        params = pack('B' * len(buffer), *buffer)
        temp = self.escaped([self.CalCRC(buffer)])
        VideoMuteCmdString = b''.join([b'\xFE', params, pack('B' * len(temp), *temp), b'\xFF'])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)            

    def __MatchError(self, match, tag):

        value = 'NACK was received'
        print(value)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
