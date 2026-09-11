from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import binascii

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
            'AspectRatio': { 'Status': {}},
            'DiscStatus': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PlayMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'Transport': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!7AST(0[0-3]|FF)\x1A'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'!7DST(00|01|04|07|10|12|FF)\x1A'), self.__MatchDiscStatus, None)
            self.AddMatchString(re.compile(b'!7SST(0[0-3]|FF)\x1A'), self.__MatchPower, None)
            
         

    def commandBuilder(self, commandString):
        if 'Serial' in self.ConnectionType:
            return commandString
        else:
            tempLength = str(len(commandString) + 4).zfill(2)
            return b'ISCP\x00\x00\x00\x10\x00\x00\x00' + binascii.unhexlify(tempLength) + b'\x01\x00\x00\x00' + commandString + b'\r'

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3 Letterbox'   : b'0',
            '4:3 Normal'      : b'1',
            '16:9 Widescreen' : b'2',
            '16:9 Squeeze'    : b'3'
        }

        AspectRatioCmdString = self.commandBuilder(b'!7ASC0' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.commandBuilder(b'!7?STAS') + b'\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '00' : '4:3 Letterbox',
            '01' : '4:3 Normal',
            '02' : '16:9 Widescreen',
            '03' : '16:9 Squeeze',
            'FF' : 'Unknown / Other'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def UpdateDiscStatus(self, value, qualifier):

        DiscStatusCmdString = self.commandBuilder(b'!7?STDS') + b'\r'
        self.__UpdateHelper('DiscStatus', DiscStatusCmdString, value, qualifier)

    def __MatchDiscStatus(self, match, tag):

        ValueStateValues = {
            '00' : 'No Disc',
            '01' : 'DVD',
            '04' : 'CD',
            '07' : 'CD Data',
            '10' : 'BD-ROM',
            '12' : 'USB',
            'FF' : 'Unknown'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DiscStatus', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : b'00',
            '1' : b'01',
            '2' : b'02',
            '3' : b'03',
            '4' : b'04',
            '5' : b'05',
            '6' : b'06',
            '7' : b'07',
            '8' : b'08',
            '9' : b'09'
        }

        KeypadCmdString = self.commandBuilder(b'!7NUM' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'     : b'OSDUP',
            'Down'   : b'OSDDN',
            'Left'   : b'OSDLF',
            'Right'  : b'OSDRH',
            'Home'   : b'HOM',
            'Menu'   : b'MNU',
            'Return' : b'RET',
            'Enter'  : b'ENT'
        }

        MenuNavigationCmdString = self.commandBuilder(b'!7' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'ON',
            'Off' : b'OF'
        }

        PIPModeCmdString = self.commandBuilder(b'!7PIP' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPlayMode(self, value, qualifier):

        PlayModeCmdString = self.commandBuilder(b'!7PLMTG') + b'\r'
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'1',
            'Off' : b'0'
        }

        PowerCmdString = self.commandBuilder(b'!7PWR0' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.commandBuilder(b'!7?STST') + b'\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '00' : ('Off', 'Unknown'),
            '01' : ('On' , 'Play'),
            '02' : ('On' , 'Pause'),
            '03' : ('On' , 'Stop'),
            'FF' : ('Unknown', 'Unknown')
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value[0], None)
        self.WriteStatus('Transport', value[1], None)

    def SetRepeat(self, value, qualifier):

        RepeatCmdString = self.commandBuilder(b'!7RPT') + b'\r'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'       : b'PLYUP',
            'Stop'       : b'STP',
            'Pause'      : b'PAS',
            'Skip Up'    : b'SKPUP',
            'Skip Down'  : b'SKPDN',
            'Scan Up'    : b'SCNUP',
            'Scan Down'  : b'SCNDN',
            'A-B Repeat' : b'ABR',
            'Open/Close' : b'OPC',
            'Subtitle'   : b'SUB',
            'Title'      : b'TMN'
        }

        TransportCmdString = self.commandBuilder(b'!7' + ValueStateValues[value]) + b'\r'
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
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
        self.Send(self.commandBuilder(b'!7PMS01\r'))
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