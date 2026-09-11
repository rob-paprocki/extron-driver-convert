from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'Buzzer': { 'Status': {}},
            'HotKey': { 'Status': {}},
            'JumptoConsoleChannel': { 'Status': {}},
            'SYNCJumptoConsoleChannel': { 'Status': {}},
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Buzzer: (ON|OFF)\r\n'), self.__MatchBuzzer, None)
            self.AddMatchString(re.compile(b'Hot KEY: (CTRL|Scroll|SHIFT|Caps)\r\n'), self.__MatchHotKey, None)
            self.AddMatchString(re.compile(b'ERROR\r\n'), self.__MatchError, None)

    def SetBuzzer(self, value, qualifier):

        BuzzerState = {
            'On' : 'bzon\r', 
            'Off' : 'bzoff\r'
            }

        BuzzerCmdString = BuzzerState[value]
        self.__SetHelper('Buzzer', BuzzerCmdString, value, qualifier)

    def UpdateBuzzer(self, value, qualifier):

        BuzzerCmdString = 'k1p0\r'
        self.__UpdateHelper('Buzzer', BuzzerCmdString, value, qualifier)

    def __MatchBuzzer(self, match, tag):

        BuzzerState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = BuzzerState[match.group(1).decode()]
        self.WriteStatus('Buzzer', value, None)

    def SetHotKey(self, value, qualifier):

        HotKeyState = {
            'Ctrl' : 'CTRL\r', 
            'Shift' : 'SHIFT\r', 
            'Scroll' : 'SCROLL\r', 
            'Caps' : 'CAPS\r'
            }

        HotKeyCmdString = HotKeyState[value]
        self.__SetHelper('HotKey', HotKeyCmdString, value, qualifier)

    def UpdateHotKey(self, value, qualifier):

        self.UpdateBuzzer(value, qualifier)

    def __MatchHotKey(self, match, tag):

        HotKeyState = {
            'CTRL' : 'Ctrl', 
            'SHIFT' : 'Shift', 
            'Scroll' : 'Scroll', 
            'Caps' : 'Caps'
            }

        value = HotKeyState[match.group(1).decode()]
        self.WriteStatus('HotKey', value, None)

    def SetJumptoConsoleChannel(self, value, qualifier):

        JumpConsoleState = {
            '1' : 'k1p1\r', 
            '2' : 'k1p2\r', 
            '3' : 'k1p3\r', 
            '4' : 'k1p4\r', 
            '5' : 'k1p5\r', 
            '6' : 'k1p6\r', 
            'A' : 'k1p7\r', 
            'B' : 'k1p8\r', 
            'C' : 'k1p9\r', 
            'D' : 'k1pA\r', 
            'E' : 'k1pB\r', 
            'F' : 'k1pC\r'
            }

        JumptoConsoleChannelCmdString = JumpConsoleState[value]
        self.__SetHelper('JumptoConsoleChannel', JumptoConsoleChannelCmdString, value, qualifier)

    def SetSYNCJumptoConsoleChannel(self, value, qualifier):

        SYNCJumpState = {
            '1' : 'CH1\r', 
            '2' : 'CH2\r', 
            '3' : 'CH3\r', 
            '4' : 'CH4\r', 
            '5' : 'CH5\r', 
            '6' : 'CH6\r', 
            'A' : 'CH7\r', 
            'B' : 'CH8\r', 
            'C' : 'CH9\r', 
            'D' : 'CHA\r', 
            'E' : 'CHB\r', 
            'F' : 'CHC\r'
            }

        SYNCJumptoConsoleChannelCmdString = SYNCJumpState[value]
        self.__SetHelper('SYNCJumptoConsoleChannel', SYNCJumptoConsoleChannelCmdString, value, qualifier)

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

        value = match.group(0).decode()
        self.Error([value[1]])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

