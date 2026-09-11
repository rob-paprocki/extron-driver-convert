from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'CombinedLoad': { 'Status': {}},
            'CombinedWattage': { 'Status': {}},
            'Switched12VDC1': { 'Status': {}},
            'Switched12VDC2': { 'Status': {}},
            'Switched12VDC3': { 'Status': {}},
            'Switched12VDC4': { 'Status': {}},
            'Switched12VDC5': { 'Status': {}},
            'Switched12VDC6': { 'Status': {}},
            'Switched12VDC7': { 'Status': {}},
            'Switched12VDC8': { 'Status': {}},
            'Temperature': {'Parameters': ['Temperature Units'], 'Status': {}},
            'TemperatureState': { 'Status': {}}
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'33Stat +([0-2])\r\n'), self.__MatchCombinedLoad, None)
            self.AddMatchString(re.compile(b'34Stat ?(\d{1,2}\.\d{1,6})'), self.__MatchCombinedWattage, None)
            self.AddMatchString(re.compile(b'DcppP1\*([01])\r\n'), self.__MatchSwitched12VDC1, None)
            self.AddMatchString(re.compile(b'DcppP2\*([01])\r\n'), self.__MatchSwitched12VDC2, None)
            self.AddMatchString(re.compile(b'DcppP3\*([01])\r\n'), self.__MatchSwitched12VDC3, None)
            self.AddMatchString(re.compile(b'DcppP4\*([01])\r\n'), self.__MatchSwitched12VDC4, None)
            self.AddMatchString(re.compile(b'DcppP5\*([01])\r\n'), self.__MatchSwitched12VDC5, None)
            self.AddMatchString(re.compile(b'DcppP6\*([01])\r\n'), self.__MatchSwitched12VDC6, None)
            self.AddMatchString(re.compile(b'DcppP7\*([01])\r\n'), self.__MatchSwitched12VDC7, None)
            self.AddMatchString(re.compile(b'DcppP8\*([01])\r\n'), self.__MatchSwitched12VDC8, None)
            self.AddMatchString(re.compile(b'TempT1\*([-\d.]+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'TempS1\*([0-3])\r\n'), self.__MatchTemperatureState, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()

        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def UpdateCombinedLoad(self, value, qualifier):

        CombinedLoadCmdString = 'w33STAT\r'
        self.__UpdateHelper('CombinedLoad', CombinedLoadCmdString, value, qualifier)

    def __MatchCombinedLoad(self, match, tag):

        ValueStateValues = {
            '0' : 'Normal',
            '1' : 'Limit',
            '2' : 'Over'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CombinedLoad', value, None)

    def UpdateCombinedWattage(self, value, qualifier):

        CombinedWattageCmdString = 'w34STAT\r'
        self.__UpdateHelper('CombinedWattage', CombinedWattageCmdString, value, qualifier)

    def __MatchCombinedWattage(self, match, tag):

        value = round(float(match.group(1).decode()), 1)
        if 0.0 <= value <= 42.0:
            self.WriteStatus('CombinedWattage', value, None)

    def SetSwitched12VDC1(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC1CmdString = 'wP1*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC1', Switched12VDC1CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC1')

    def UpdateSwitched12VDC1(self, value, qualifier):

        Switched12VDC1CmdString = 'wP1DCPP\r'
        self.__UpdateHelper('Switched12VDC1', Switched12VDC1CmdString, value, qualifier)

    def __MatchSwitched12VDC1(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC1', value, None)

    def SetSwitched12VDC2(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC2CmdString = 'wP2*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC2', Switched12VDC2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC2')

    def UpdateSwitched12VDC2(self, value, qualifier):

        Switched12VDC2CmdString = 'wP2DCPP\r'
        self.__UpdateHelper('Switched12VDC2', Switched12VDC2CmdString, value, qualifier)

    def __MatchSwitched12VDC2(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC2', value, None)

    def SetSwitched12VDC3(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC3CmdString = 'wP3*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC3', Switched12VDC3CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC3')

    def UpdateSwitched12VDC3(self, value, qualifier):

        Switched12VDC3CmdString = 'wP3DCPP\r'
        self.__UpdateHelper('Switched12VDC3', Switched12VDC3CmdString, value, qualifier)

    def __MatchSwitched12VDC3(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC3', value, None)

    def SetSwitched12VDC4(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC4CmdString = 'wP4*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC4', Switched12VDC4CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC4')

    def UpdateSwitched12VDC4(self, value, qualifier):

        Switched12VDC4CmdString = 'wP4DCPP\r'
        self.__UpdateHelper('Switched12VDC4', Switched12VDC4CmdString, value, qualifier)

    def __MatchSwitched12VDC4(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC4', value, None)

    def SetSwitched12VDC5(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC5CmdString = 'wP5*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC5', Switched12VDC5CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC5')

    def UpdateSwitched12VDC5(self, value, qualifier):

        Switched12VDC5CmdString = 'wP5DCPP\r'
        self.__UpdateHelper('Switched12VDC5', Switched12VDC5CmdString, value, qualifier)

    def __MatchSwitched12VDC5(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC5', value, None)

    def SetSwitched12VDC6(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC6CmdString = 'wP6*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC6', Switched12VDC6CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC6')

    def UpdateSwitched12VDC6(self, value, qualifier):

        Switched12VDC6CmdString = 'wP6DCPP\r'
        self.__UpdateHelper('Switched12VDC6', Switched12VDC6CmdString, value, qualifier)

    def __MatchSwitched12VDC6(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC6', value, None)

    def SetSwitched12VDC7(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC7CmdString = 'wP7*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC7', Switched12VDC7CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC7')

    def UpdateSwitched12VDC7(self, value, qualifier):

        Switched12VDC7CmdString = 'wP7DCPP\r'
        self.__UpdateHelper('Switched12VDC7', Switched12VDC7CmdString, value, qualifier)

    def __MatchSwitched12VDC7(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC7', value, None)

    def SetSwitched12VDC8(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            Switched12VDC8CmdString = 'wP8*{0}DCPP\r'.format(ValueStateValues[value])
            self.__SetHelper('Switched12VDC8', Switched12VDC8CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitched12VDC8')

    def UpdateSwitched12VDC8(self, value, qualifier):

        Switched12VDC8CmdString = 'wP8DCPP\r'
        self.__UpdateHelper('Switched12VDC8', Switched12VDC8CmdString, value, qualifier)

    def __MatchSwitched12VDC8(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Switched12VDC8', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureUnitsStates = [
            'Celsius',
            'Fahrenheit'
        ]

        if qualifier['Temperature Units'] in TemperatureUnitsStates:

            TemperatureCmdString = 'wT1TEMP\r'
            self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __MatchTemperature(self, match, tag):

        celsius = float(match.group(1).decode())
        if -50.0 <= celsius <= 105.0:
            self.WriteStatus('Temperature', celsius, {'Temperature Units': 'Celsius'})

        fahrenheit = round((celsius * 9/5) + 32, 1)
        if -58.0 <= fahrenheit <= 221.0:
            self.WriteStatus('Temperature', fahrenheit, {'Temperature Units': 'Fahrenheit'})

    def UpdateTemperatureState(self, value, qualifier):

        TemperatureStateCmdString = 'wS1TEMP\r'
        self.__UpdateHelper('TemperatureState', TemperatureStateCmdString, value, qualifier)

    def __MatchTemperatureState(self, match, tag):

        ValueStateValues = {
            '0': 'Probe Error',
            '1': 'Normal',
            '2': 'Limit',
            '3': 'Over'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TemperatureState', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.EchoDisabled:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            '10' : 'Invalid command.',
            '12' : 'Command is for a port that is not available on the product.',
            '13' : 'Invalid value (the number is out of range or too large) or parameter.',
            '14' : 'Invalid for this configuration.',
            '18' : 'System or command timed out.',
            '22' : 'Busy.',
            '24' : 'Privilege violation.',
            '26' : 'Maximum number of connections has been exceeded.',
            '28' : 'Bad filename or file not found.',
            '37' : 'Invalid command while in SPD mode.'
        }

        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error(['An error occured: {}'.format(value)])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
