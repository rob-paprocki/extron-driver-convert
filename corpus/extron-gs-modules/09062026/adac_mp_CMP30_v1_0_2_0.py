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
            'DIR': { 'Status': {}},
            'Function': { 'Status': {}},
            'Power': { 'Status': {}},
            'Random': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'TrackNumber': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Volume': { 'Status': {}},
        }
        
        if self.Unidirectional == 'False':           #Power      Function     Volume        EQ      Transport      Repeat      Random      Intro     RF Band      RF1         RF2       RF3        RF4        RF5        RF6        RF7       Track No           
            self.AddMatchString(re.compile(b'\x55\xD1(\x01|\x02)([\x10-\x12])([\x00-\x21])[\x40-\x43]([\x60-\x62])([\x90-\x92])(\xA0|\xA1)[\xB0-\xB2][\xC3|\xC4][\x00-\xFF][\x00-\xFF][\x00-\xFF][\x00-\xFF][\x00-\xFF][\x00-\xFF]([\x00-\xFF])([\x00-\xFF])\xAA'), self.__MatchPower, None)

    def SetDIR(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x55\x80\xAA', 
            'Down': b'\x55\x81\xAA'
        }

        DIRCmdString = ValueStateValues[value]
        self.__SetHelper('DIR', DIRCmdString, value, qualifier)
    def SetFunction(self, value, qualifier):


        FunctionStateValues = {
            'USB'   : b'\x55\x10\xAA',
            'CD'    : b'\x55\x11\xAA',
            'Radio' : b'\x55\x12\xAA',
            }
        
        FunctionCmdString = FunctionStateValues[value]
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)
        
    def UpdateFunction(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):


        PowerStateValues = {
            'On'  : b'\x55\x01\xAA',
            'Off' : b'\x55\x02\xAA',
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier): 


        PowerCmdString = b'\x55\xD0\xAA'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, qualifier):


        PowerStateNames = {
            b'\x01' : 'On',
            b'\x02' : 'Off',
            }
                               
        FunctionStateNames = {
            b'\x10' : 'USB',
            b'\x11' : 'CD',
            b'\x12' : 'Radio',
            }

        TransportStateNames = {
            b'\x60' : 'Play',
            b'\x61' : 'Pause',
            b'\x62' : 'Stop',
            }

        RepeatStateNames = {
            b'\x90' : 'Off',
            b'\x91' : 'One',
            b'\x92' : 'All',
            }

        RandomStateNames = {
            b'\xA0' : 'Off',
            b'\xA1' : 'On',
            }

        PowerValue = PowerStateNames[match.group(1)]
        self.WriteStatus('Power', PowerValue, None)
        FunctionValue = FunctionStateNames[match.group(2)]
        self.WriteStatus('Function', FunctionValue, None)
        VolumeValue = match.group(3)[0]
        self.WriteStatus('Volume', VolumeValue, None)
        TransportValue = TransportStateNames[match.group(4)]
        self.WriteStatus('Transport', TransportValue, None)
        RepeatValue = RepeatStateNames[match.group(5)]
        self.WriteStatus('Repeat', RepeatValue, None)
        RandomValue = RandomStateNames[match.group(6)]
        self.WriteStatus('Random', RandomValue, None)
        Tens = match.group(7)[0]
        Singles = match.group(8)[0]
        TrackNumberValue = Tens * 10 + Singles
        self.WriteStatus('TrackNumber', TrackNumberValue, None)

    def SetRandom(self, value, qualifier):


        RandomStateValues = {
            'On'  : b'\x55\xA1\xAA',
            'Off' : b'\x55\xA0\xAA',
            }

        RandomCmdString = RandomStateValues[value]
        self.__SetHelper('Random', RandomCmdString, value, qualifier)
        
    def UpdateRandom(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetRepeat(self, value, qualifier):


        RepeatStateValues = {
            'Off'    : b'\x55\x90\xAA',
            'One'    : b'\x55\x91\xAA',
            'All'    : b'\x55\x92\xAA',
            }

        RepeatCmdString = RepeatStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
    
    def UpdateRepeat(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetTransport(self, value, qualifier):

        
        TransportStateValues = {
            'Play'  : b'\x55\x60\xAA',
            'Pause' : b'\x55\x61\xAA',
            'Stop'  : b'\x55\x62\xAA',
            'Next'  : b'\x55\x70\xAA',
            'Back'  : b'\x55\x71\xAA',
            }
        
        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        
    def UpdateTransport(self, value, qualifier):
        self.UpdatePower(value, qualifier)
            

    def SetVolume(self, value, qualifier):


        VolumeConstraints = {
            'Min' : 0,
            'Max' : 33
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = pack('>BBBB', 0x55, 0x30, value, 0xAA)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
            
    def UpdateVolume(self, value, qualifier):
        self.UpdatePower(value, qualifier)

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

