from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MaxNumberofActiveMicrophones': { 'Status': {}},
            'Microphone': {'Parameters':['ID'], 'Status': {}},
            'MicrophoneRequest': {'Parameters':['ID'], 'Status': {}},
            'OperationMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SpeakingList': {'Parameters':['Position'], 'Status': {}},
            'TurnOffAllMicrophones': { 'Status': {}}
        }

        self.controlFlag = False
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xe8\xe6\x00\x05\x04\x05\x01([\x00-\x04])\xed'), self.__MatchOperationMode, None)
            self.AddMatchString(re.compile(b'\xe8\xe6\x00\x04\x0B\x06(\x00|\x01|\x02)\xed'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xe8\xe6\x00\\x24\x05\x08([\x00-\x08])([\x00-\xFF]{32})\xed'), self.__MatchSpeakingList, None)

    def SetMaxNumberofActiveMicrophones(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x01', 
            '2': b'\x02', 
            '3': b'\x03', 
            '4': b'\x04', 
            '5': b'\x05', 
            '6': b'\x06', 
            '7': b'\x07', 
            '8': b'\x08'
        }

        if value in ValueStateValues:
            MaxNumberofActiveMicrophonesCmdString = b''.join([b'\xe8\xe6\x00\x05\x04\x06\x02', ValueStateValues[value], b'\xed'])
            self.__SetHelper('MaxNumberofActiveMicrophones', MaxNumberofActiveMicrophonesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaxNumberofActiveMicrophones')

    def UpdateMaxNumberofActiveMicrophones(self, value, qualifier):

        self.UpdateSpeakingList(None, {'Position' : '1'})

    def SetMicrophone(self, value, qualifier):

        IDConstraints = {
            'Min' : 1,
            'Max' : 4095
            }

        ValueStateValues = {
            'On':  b'\x01', 
            'Off': b'\x02'
        }

        mic_id = qualifier['ID']
        if value in ValueStateValues and IDConstraints['Min'] <= mic_id <= IDConstraints['Max']:
            MicrophoneCmdString = b''.join([b'\xe8\xe6\x00\x05\x05', ValueStateValues[value], pack('>H', mic_id), b'\xed'])
            self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetMicrophone')

    def SetMicrophoneRequest(self, value, qualifier):

        IDConstraints = {
            'Min' : 1,
            'Max' : 4095
            }

        ValueStateValues = {
            'On':                           (b'\x06\x05\x03', b'\x00'), 
            'Two Hands (Stronger Request)': (b'\x06\x05\x03', b'\x01'), 
            'Off':                          (b'\x05\x05\x05', b''),
        }

        mic_id = qualifier['ID']
        if value in ValueStateValues and IDConstraints['Min'] <= mic_id <= IDConstraints['Max']:
            MicrophoneRequestCmdString = b''.join([b'\xe8\xe6\x00', ValueStateValues[value][0], 
                                            pack('>H', mic_id), ValueStateValues[value][1], b'\xed'])
            self.__SetHelper('MicrophoneRequest', MicrophoneRequestCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetMicrophoneRequest')

    def SetOperationMode(self, value, qualifier):

        ValueStateValues = {
            'Open':     b'\x00', 
            'Override': b'\x01', 
            'Voice':    b'\x02', 
            'Request':  b'\x03', 
            'PTT':      b'\x04',
        }

        if value in ValueStateValues:
            OperationModeCmdString = b''.join([b'\xe8\xe6\x00\x05\x04\x06\x01', ValueStateValues[value], b'\xed'])
            self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetOperationMode')

    def UpdateOperationMode(self, value, qualifier):

        OperationModeCmdString = b'\xe8\xe6\x00\x04\x04\x04\x01\xed'
        self.__UpdateHelper('OperationMode', OperationModeCmdString, value, qualifier)

    def __MatchOperationMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Open', 
            b'\x01': 'Override', 
            b'\x02': 'Voice', 
            b'\x03': 'Request', 
            b'\x04': 'PTT',
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OperationMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':            b'\x02', 
            'Off':           b'\x01', 
            'Standby':       b'\x03',
            'Exit Standby':  b'\x04',
        }

        if value in ValueStateValues:
            PowerCmdString = b''.join([b'\xe8\xe6\x00\x03\x0B', ValueStateValues[value], b'\xed'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
            
        PowerCmdString = b'\xe8\xe6\x00\x03\x0B\x05\xed'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x00' : 'Off', 
            b'\x01' : 'Standby'
        }
        
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def UpdateSpeakingList(self, value, qualifier):

        if qualifier['Position'] in '12345678':
            SpeakingListCmdString = b'\xe8\xe6\x00\x03\x05\x07\xed'
            self.__UpdateHelper('SpeakingList', SpeakingListCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeakingList')

    def __MatchSpeakingList(self, match, tag):

        num = ord(match.group(1).decode())
        value = match.group(2)
        
        if 0 <= num <= 8:
            self.WriteStatus('MaxNumberofActiveMicrophones', str(num), None)

        i = 0
        if num==0:
            for j in range(1,9):
                self.WriteStatus('SpeakingList', 0, {'Position' : str(j)})
        else:
            for j in range(1,9):
                mic_id = unpack('>H', value[i:i+2])[0]
                self.WriteStatus('SpeakingList', mic_id, {'Position' : str(j)})
                i = i + 4
        
    def SetTurnOffAllMicrophones(self, value, qualifier):

        TurnOffAllMicrophonesCmdString = b'\xe8\xe6\x00\x05\x05\x02\x00\x00\xed'
        self.__SetHelper('TurnOffAllMicrophones', TurnOffAllMicrophonesCmdString, value, qualifier)

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

            if self.controlFlag == False:
                res = self.SendAndWait(b'\xe8\xe6\x00\x03\x03\x01\xed', self.DefaultResponseTimeout)
                if res:
                    self.controlFlag = True

            elif self.controlFlag == True:
                self.Send(commandstring)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.controlFlag = False
        
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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