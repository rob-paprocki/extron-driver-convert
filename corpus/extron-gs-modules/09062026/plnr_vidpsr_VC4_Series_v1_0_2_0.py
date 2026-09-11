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
        self.Models = {
            'VC4-HSL': self.plnr_29_5614_HSL,
            'VC4-L': self.plnr_29_5614_L
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BacklightIntensity': { 'Status': {}},
            'DeviceConnected': {'Parameters': ['Device'], 'Status': {}},
            'FanStatus': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Temperature': {'Parameters': ['Device', 'Unit'], 'Status': {}},
            'WallBrightness': { 'Status': {}},
            'ZoneInput': {'Parameters': ['Zone', 'Video Controller'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'BACKLIGHT\.INTENSITY:(\d+)\r'), self.__MatchBacklightIntensity, None)
            self.AddMatchString(re.compile(b'CONNECTED\((.+?)\):(YES|NO)\r'), self.__MatchDeviceConnected, None)
            self.AddMatchString(re.compile(b'FAN\.STATUS:(OK|FAULT)\r'), self.__MatchFanStatus, None)
            self.AddMatchString(re.compile(b'SYSTEM\.POWER:(ON|OFF)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'TEMPERATURE\((.+?)\):(\d+\.\d+)\r'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'WALL\.BRIGHTNESS:(\d+\.\d+)\r'), self.__MatchWallBrightness, None)
            self.AddMatchString(re.compile(b'ZONE\.INPUT\((\d+)\):VC(\d+)\.IN(\d+)\r'), self.__MatchZoneInput, None)

            self.AddMatchString(re.compile(b'\^NAK\r|!ERR ([1-6])\r'), self.__MatchError, None)

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

    def UpdateDeviceConnected(self, value, qualifier):

        device = qualifier['Device']

        if device:
            DeviceConnectedCmdString = 'CONNECTED({})?\r'.format(device)
            self.__UpdateHelper('DeviceConnected', DeviceConnectedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDeviceConnected')

    def __MatchDeviceConnected(self, match, tag):

        ValueStateValues = {
            'YES':  'Connected',
            'NO':   'Disconnected'
        }

        qualifier = {
            'Device': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DeviceConnected', value, qualifier)

    def UpdateFanStatus(self, value, qualifier):

        FanStatusCmdString = 'FAN.STATUS?\r'
        self.__UpdateHelper('FanStatus', FanStatusCmdString, value, qualifier)

    def __MatchFanStatus(self, match, tag):

        ValueStateValues = {
            'OK':       'Normal',
            'FAULT':    'Fault'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FanStatus', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':       'SYSTEM.POWER=ON\r',
            'Off':      'SYSTEM.POWER=OFF\r',
            'Reboot':   'SYSTEM.REBOOT\r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'SYSTEM.POWER?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 999:
            PresetRecallCmdString = 'PRESET.RECALL({})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateTemperature(self, value, qualifier):

        device = qualifier['Device']

        UnitStates = [
            'Celsius',
            'Fahrenheit'
        ]
        unit = qualifier['Unit']

        if device and unit in UnitStates:
            TemperatureCmdString = 'TEMPERATURE({})?\r'.format(device)
            self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __MatchTemperature(self, match, tag):

        device = match.group(1).decode()

        c = float(match.group(2).decode())
        f = c * 9/5 + 32

        self.WriteStatus('Temperature', c, {'Device': device, 'Unit': 'Celsius'})
        self.WriteStatus('Temperature', f, {'Device': device, 'Unit': 'Fahrenheit'})

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

        value = int(float(match.group(1).decode()))
        if 0 <= value <= 100:
            self.WriteStatus('WallBrightness', value, None)

    def SetZoneInput(self, value, qualifier):

        zone = qualifier['Zone']
        vc = qualifier['Video Controller']

        if 1 <= zone and 1 <= vc and 1 <= int(value) <= self.zone_input_max:
            ZoneInputCmdString = 'ZONE.INPUT({})=VC{}.IN{}\r'.format(zone, vc, int(value))
            self.__SetHelper('ZoneInput', ZoneInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneInput')

    def UpdateZoneInput(self, value, qualifier):

        zone = qualifier['Zone']
        vc = qualifier['Video Controller']

        if 1 <= zone and 1 <= vc:
            ZoneInputCmdString = 'ZONE.INPUT({})?\r'.format(zone, vc)
            self.__UpdateHelper('ZoneInput', ZoneInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneInput')

    def __MatchZoneInput(self, match, tag):

        qualifier = {
            'Zone':             int(match.group(1).decode()),
            'Video Controller': int(match.group(2).decode())
        }

        value = match.group(3).decode()
        if 1 <= qualifier['Zone'] and 1 <= qualifier['Video Controller']:
            self.WriteStatus('ZoneInput', value, qualifier)

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

        error_map = {
            '1': 'Invalid syntax',
            '2': 'Reserved for future use',
            '3': 'Command not recognized',
            '4': 'Invalid modifier',
            '5': 'Invalid operands',
            '6': 'Invalid operator'
        }

        if 'NAK' in match.group(0).decode():
            self.Error(['An error occurred: Command could not be processed at this time.'])
        else:
            self.Error(['An error occurred: {}.'.format(error_map[match.group(1).decode()])])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def plnr_29_5614_HSL(self):

        self.zone_input_max = 4
    
    def plnr_29_5614_L(self):

        self.zone_input_max = 5

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()