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
            'BacklightIntensity': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Mode'], 'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SystemReboot': {'Status': {}},
            'WallBrightness': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'BACKLIGHT\.INTENSITY:(\d+)\r'), self.__MatchBacklightIntensity, None)
            self.AddMatchString(re.compile(b'(KEY|IR)\.LOCK:([01]|DISABLE|OFF|NO|FALSE|ENABLE|ON|YES|TRUE)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'SYSTEM\.STATE:([0-5]|STANDBY|POWERING\.ON|ON|POWERING\.DOWN|BACKLIGHT\.OFF|FAULT)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'WALL\.BRIGHTNESS:(\d+)[.\d]*\r'), self.__MatchWallBrightness, None)
            self.AddMatchString(re.compile(b'ERR ([1-6])\r|NAK\r'), self.__MatchError, None)

    def SetBacklightIntensity(self, value, qualifier):

        if 0 <= value <= 100:
            BacklightIntensityCmdString = 'BACKLIGHT.INTENSITY={}\r'.format(value)
            self.__SetHelper('BacklightIntensity', BacklightIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightIntensity')

    def UpdateBacklightIntensity(self, value, qualifier):

        BacklightIntensityCmdString = 'BACKLIGHT.INTENSITY?\r'
        self.__UpdateHelper('BacklightIntensity', BacklightIntensityCmdString, value, qualifier)

    def __MatchBacklightIntensity(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BacklightIntensity', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ModeStates = {
            'Front Keypad': 'KEY',
            'Remote': 'IR'
        }

        ValueStateValues = {
            'On': 'ENABLE',
            'Off': 'DISABLE'
        }

        if value in ValueStateValues and qualifier['Mode'] in ModeStates:
            self.__SetHelper('ExecutiveMode', '{}.LOCK={}\r'.format(ModeStates[qualifier['Mode']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ModeStates = {
            'Front Keypad': 'KEY',
            'Remote': 'IR'
        }

        if qualifier['Mode'] in ModeStates:
            self.__UpdateHelper('ExecutiveMode', '{}.LOCK?\r'.format(ModeStates[qualifier['Mode']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ModeStates = {
            'KEY': 'Front Keypad',
            'IR': 'Remote'
        }

        ValueStateValues = {
            '1': 'On',
            'ENABLE': 'On',
            'ON': 'On',
            'YES': 'On',
            'TRUE': 'On',
            '0': 'Off',
            'DISABLE': 'Off',
            'OFF': 'Off',
            'NO': 'Off',
            'FALSE': 'Off'
        }

        qualifier = {}
        qualifier['Mode'] = ModeStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '272',
            'HDMI 2': '273',
            'HDMI 3': '274',
            'HDMI 4': '275',
            'DisplayPort': '276'
        }

        if value in ValueStateValues:
            self.__SetHelper('Input', 'KEY={}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '32',
            '1': '17',
            '2': '18',
            '3': '19',
            '4': '20',
            '5': '21',
            '6': '22',
            '7': '23',
            '8': '24',
            '9': '25'
        }

        if value in ValueStateValues:
            self.__SetHelper('Keypad', 'KEY={}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '2',
            'Up': '0',
            'Down': '1',
            'Right': '15',
            'Left': '12',
            'Enter': '13',
            'Exit': '9'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuNavigation', 'KEY={}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('Power', 'SYSTEM.POWER={}\r'.format(value.upper()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'SYSTEM.STATE?\r', value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': ['Off', 'Normal'],
            '1': ['Warming Up', 'Normal'],
            '2': ['On', 'Normal'],
            '3': ['Cooling Down', 'Normal'],
            '4': ['On', 'Displays Off'],
            '5': ['Off', 'System Failure'],
            'STANDBY': ['Off', 'Normal'],
            'POWERING.ON': ['Warming Up', 'Normal'],
            'ON': ['On', 'Normal'],
            'POWERING.DOWN': ['Cooling Down', 'Normal'],
            'BACKLIGHT.OFF': ['On', 'Displays Off'],
            'FAULT': ['Off', 'System Failure']
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value[0], None)
        self.WriteStatus('DeviceStatus', value[1], None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 999:
            self.__SetHelper('PresetRecall', 'PRESET.RECALL({})\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 999:
            self.__SetHelper('PresetSave', 'PRESET.SAVE({})\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSystemReboot(self, value, qualifier):

        SystemRebootCmdString = 'SYSTEM.REBOOT\r'
        self.__SetHelper('SystemReboot', SystemRebootCmdString, value, qualifier)

    def SetWallBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            WallBrightnessCmdString = 'WALL.BRIGHTNESS={}\r'.format(value)
            self.__SetHelper('WallBrightness', WallBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWallBrightness')

    def UpdateWallBrightness(self, value, qualifier):

        WallBrightnessCmdString = 'WALL.BRIGHTNESS?\r'
        self.__UpdateHelper('WallBrightness', WallBrightnessCmdString, value, qualifier)

    def __MatchWallBrightness(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('WallBrightness', value, None)

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

        ERRORS = {
            '1': 'Invalid syntax',
            '2': '[Reserved for future use]',
            '3': 'Command not recognized',
            '4': 'Invalid modifier',
            '5': 'Invalid operands',
            '6': 'Invalid operator'
        }

        value = match.group(0).decode()
        if 'ERR' in value:
            self.Error([ERRORS[match.group(1).decode()]])
        else:
            self.Error(['Command received, but cannot be processed at this time'])


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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

