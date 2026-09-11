from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConfigurationCommand': {'Parameters':['Module ID','New Module ID','Baud Rate','Checksum'], 'Status': {}},
            'DigitalOutput': {'Parameters':['Module ID','Channel'], 'Status': {}},
            }                
        
        self.AddMatchString(re.compile(b'#([0-9a-fA-F]{2})1([0-7])0(0|1)\r'), self.__MatchDigitalOutput, None)
        self.AddMatchString(re.compile(b'\?[\S\s]+\r'), self.__MatchError, None)

    def SetConfigurationCommand(self, value, qualifier):

        BaudRateStates = {
            '1200'   : '03', 
            '2400'   : '04', 
            '4800'   : '05', 
            '9600'   : '06', 
            '19200'  : '07', 
            '38400'  : '08', 
            '57600'  : '09', 
            '115200' : '0A'
        }

        ChecksumStates = {
            'Enable'  : '40', 
            'Disable' : '00'
        }

        ModID = int(qualifier['Module ID'])
        NewModID = int(qualifier['New Module ID'])
        BaudRate = qualifier['Baud Rate']
        Chksum = qualifier['Checksum']
        if 0 <= ModID <= 255 and 0 <= NewModID <= 255 and BaudRate in BaudRateStates and Chksum in ChecksumStates:
            ConfigurationCommandCmdString = '%{0:02X}{1:02X}40{2}{3}\r'.format(ModID, NewModID, BaudRateStates[BaudRate], ChecksumStates[Chksum])
            self.__SetHelper('ConfigurationCommand', ConfigurationCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigurationCommand')

    def SetDigitalOutput(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        ModID = int(qualifier['Module ID'])
        channel = int(qualifier['Channel'])
        if 0 <= channel <= 7 and 0 <= ModID <= 255:
            DigitalOutputCmdString = '#{0:02X}{1:02X}{2}\r'.format(ModID, channel+16, ValueStateValues[value])
            self.__SetHelper('DigitalOutput', DigitalOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalOutput')

    def __MatchDigitalOutput(self, match, tag):

        ValueStateValues = {
            '1'  : 'On', 
            '0' : 'Off'
        }
        ModID = int(match.group(1).decode(), 16)
        channel = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('DigitalOutput', value, {'Module ID':str(ModID),'Channel':channel})

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Failed to execute command.'])

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}                def SubscribeStatus(self, command, qualifier, callback):        Command = self.Commands.get(command, None)        if Command:            if command not in self.Subscription:                self.Subscription[command] = {'method':{}}                    Subscribe = self.Subscription[command]            Method = Subscribe['method']                    if qualifier:                for Parameter in Command['Parameters']:                    try:                        Method = Method[qualifier[Parameter]]                    except:                        if Parameter in qualifier:                            Method[qualifier[Parameter]] = {}                            Method = Method[qualifier[Parameter]]                        else:                            return                    Method['callback'] = callback            Method['qualifier'] = qualifier            else:            raise KeyError('Invalid command for SubscribeStatus ' + command)    # This method is to check the command with new status have a callback method then trigger the callback    def NewStatus(self, command, value, qualifier):        if command in self.Subscription :            Subscribe = self.Subscription[command]            Method = Subscribe['method']            Command = self.Commands[command]            if qualifier:                for Parameter in Command['Parameters']:                    try:                        Method = Method[qualifier[Parameter]]                    except:                        break            if 'callback' in Method and Method['callback']:                Method['callback'](command, value, qualifier)      # Save new status to the command    def WriteStatus(self, command, value, qualifier=None):            Command = self.Commands[command]        Status = Command['Status']        if qualifier:            for Parameter in Command['Parameters']:                try:                    Status = Status[qualifier[Parameter]]                except KeyError:                    if Parameter in qualifier:                        Status[qualifier[Parameter]] = {}                        Status = Status[qualifier[Parameter]]                    else:                        return          try:            if Status['Live'] != value:                Status['Live'] = value                self.NewStatus(command, value, qualifier)        except:            Status['Live'] = value            self.NewStatus(command, value, qualifier)    # Read the value from a command.    def ReadStatus(self, command, qualifier=None):        Command = self.Commands.get(command, None)        if Command:            Status = Command['Status']            if qualifier:                for Parameter in Command['Parameters']:                    try:                        Status = Status[qualifier[Parameter]]                    except KeyError:                        return None            try:                return Status['Live']            except:                return None        else:            raise KeyError('Invalid command for ReadStatus: ' + command)               class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model =None):
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

