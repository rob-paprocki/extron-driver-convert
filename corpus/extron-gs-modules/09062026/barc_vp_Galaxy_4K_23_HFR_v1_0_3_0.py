from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack,unpack

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Freeze': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Macro': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }

        if 'Serial' not in self.ConnectionType:
            self.Projectoraddress = 0x00
        else:
            self.Projectoraddress = 0x01

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE[\x00-\x01]\x76\x90([\x00-\xFF]{5,10})\xFF'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\x01]\xE8\x05([\x01-\x54])[\x01-\xFF]\xFF'), self.__MatchMacro, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\x01]\x76\x9A([\x00-\x01])[\x10-\x12]\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xFE[\x00-\x01]\x21\x42([\x00-\x01])[\x63-\x65]\xFF'), self.__MatchVideoMute, None)
    
    def escaped(self, Data):
        d = 0
        List = []
        Escaped = {
            0x80 : [0x80,0x00],
            0xFE : [0x80,0x7E],
            0xFF : [0x80,0x7F]
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
        for i in range(0,len(Data)):
            Crc = (Crc + Data[i]) % 256
        return Crc           
        
    def conversion(self, List):
        cmdStr = b''
        for i in range(len(List)):
            cmdStr += pack('>B', List[i])
        return cmdStr
    
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : [self.Projectoraddress,0x27,0x23],  
            'Off' : [self.Projectoraddress,0x26,0x23]
        }

        FreezeCmdString = pack('>B3s2B',0xFE,pack('B' * len(ValueStateValues[value]),*ValueStateValues[value]),self.CalCRC(ValueStateValues[value]),0xFF)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        buffer = [self.Projectoraddress,0x00,0x03,0x02,0x76,0x90]
        LampUsageCmdString = pack('>B6s2B',0xFE,pack('B' * len(buffer),*buffer),self.CalCRC(buffer),0xFF)
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        temp = match.group(1)
        data = []
        pos = 0
        for i in range(0,4):
            if temp[i+pos] == 128:
                ind = temp[i+pos] + temp[i+pos+1]
                data.append(ind)
                pos += 1
            else:
                data.append(temp[i+pos])
        value = ((data[0] * pow(256,3)) + (data[1] * pow(256,2)) + (data[2] * pow(256,1)) + (data[3] * pow(256,0)))//3600
        self.WriteStatus('LampUsage', value, None)

    def SetMacro(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 84
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            buffer = [self.Projectoraddress,0xE8,0x85,value]
            buffer.append(self.CalCRC(buffer))
            list = self.escaped(buffer)
            MacroCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Macro', MacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def UpdateMacro(self, value, qualifier):

        buffer = [self.Projectoraddress,0xE8,0x05]
        MacroCmdString = pack('>B3s2B',0xFE,pack('B' * len(buffer),*buffer),self.CalCRC(buffer),0xFF)
        self.__UpdateHelper('Macro', MacroCmdString, value, qualifier)

    def __MatchMacro(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Macro', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : [self.Projectoraddress,0x76,0x1A,0x01], 
            'Off' : [self.Projectoraddress,0x76,0x1A,0x00]
        }

        PowerCmdString = pack('>B4s2B',0xFE,pack('B' * len(ValueStateValues[value]),*ValueStateValues[value]),self.CalCRC(ValueStateValues[value]),0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        buffer=[self.Projectoraddress,0x76,0x9A]
        PowerCmdString = pack('>B3s2B',0xFE,pack('B' * len(buffer),*buffer),self.CalCRC(buffer),0xFF)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        
        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }
        
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : [self.Projectoraddress,0x23,0x42,0x00], 
            'Off' : [self.Projectoraddress,0x22,0x42,0x00]
        }
        
        VideoMuteCmdString = pack('>B4s2B',0xFE,pack('B' * len(ValueStateValues[value]),*ValueStateValues[value]),self.CalCRC(ValueStateValues[value]),0xFF)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        buffer=[self.Projectoraddress,0x21,0x42]
        VideoMuteCmdString = pack('>B3s2B',0xFE,pack('B' * len(buffer),*buffer),self.CalCRC(buffer),0xFF)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In' : [self.Projectoraddress,0xF4,0x82,0x00], 
            'Out' : [self.Projectoraddress,0xF4,0x82,0x01]
        }

        ZoomCmdString = pack('>B4s2B',0xFE,pack('B' * len(ValueStateValues[value]),*ValueStateValues[value]),self.CalCRC(ValueStateValues[value]),0xFF)
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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
        
        #check incoming data if it matched any expected data from device module
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

