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
            'BacklightIntensity': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Input': {'Parameters':['Video Controller ID'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PanelPower': {'Parameters': ['Panel Number'], 'Status': {}},
            'Power': { 'Status': {}},
            'PowerModuleStatus': {'Parameters':['Module'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RemoteLock': { 'Status': {}},
            'TestPattern': { 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'BACKLIGHT\.INTENSITY:(\d{1,3})\r'), self.__MatchBacklightIntensity, None)
            self.AddMatchString(re.compile(b'BACKLIGHT\.MODE:(MANUAL|AUTO)\r'), self.__MatchBacklightMode, None)
            self.AddMatchString(re.compile(rb'PANEL\.POWER\(PN(\d{1,3})\):([01])\r'), self.__MatchPanelPower, None)
            self.AddMatchString(re.compile(b'SYSTEM\.POWER:(ON|OFF)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'PS\.STATUS\(([1-4])\):0x([0-9A-Fa-f]{2,4}|[fF]{8})\r'), self.__MatchPowerModuleStatus, None)
            self.AddMatchString(re.compile(b'PRESET\.ACTIVE:(\d{1,3})\r\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'IR\.LOCK:(ENABLE|DISABLE)\r'), self.__MatchRemoteLock, None)
            self.AddMatchString(re.compile(b'PATTERN:(NONE|BLACK|WHITE|RED|GREEN|BLUE|CYAN|MAGENTA|YELLOW|GRAY|CUSTOM_COLOR|RED_SCALE|GREEN_SCALE|BLUE_SCALE|GRAY_SCALE|LOGO|GRID|CONTRAST|COLOR_BARS)\r'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'ERR (\d+)\r|\^(NAK)'), self.__MatchError, None)

    def SetBacklightIntensity(self, value, qualifier):

        if 0 <= value <= 100:
            BacklightIntensityCmdString = 'BACKLIGHT.INTENSITY={0}\r\n'.format(value)
            self.__SetHelper('BacklightIntensity', BacklightIntensityCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetBacklightIntensity')

    def UpdateBacklightIntensity(self, value, qualifier):

        BacklightIntensityCmdString = 'BACKLIGHT.INTENSITY?\r\n'
        self.__UpdateHelper('BacklightIntensity', BacklightIntensityCmdString, value, qualifier)

    def __MatchBacklightIntensity(self, match, tag):

        value = int(match.group(1))
        if 0 <= value <= 100:
            self.WriteStatus('BacklightIntensity', value, None)

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : 'AUTO',
            'Manual' : 'MANUAL'
        }

        if value in ValueStateValues:
            BacklightModeCmdString = 'BACKLIGHT.MODE={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightMode')

    def UpdateBacklightMode(self, value, qualifier):

        BacklightModeCmdString = 'BACKLIGHT.MODE?\r\n'
        self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def __MatchBacklightMode(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('BacklightMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'        : 'IN1',
            'HDMI 2'        : 'IN2',
            'HDMI 3'        : 'IN3',
            'HDMI 4'        : 'IN4',
            'DisplayPort'   : 'DP'
        }

        if 1 <= int(qualifier['Video Controller ID']) <= 999 and value in ValueStateValues:
            InputCmdString = 'QCONFIG=VC{0}.{1}\r\n'.format(qualifier['Video Controller ID'], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'            : 'UP',
            'Down'          : 'DOWN',
            'Left'          : 'LEFT',
            'Right'         : 'RIGHT',
            'Menu'          : 'MENU',
            'Exit'          : 'EXIT',
            'Enter'         : 'ENTER',
            'Previous Menu' : 'PREV'
        }

        MenuNavigationCmdString = 'KEY={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        
    def SetPanelPower(self, value, qualifier):
    
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Panel Number']) <= 200:
            PanelPowerCmdString = 'PANEL.POWER(PN{0})={1}\r'.format(qualifier['Panel Number'], ValueStateValues[value])
            self.__SetHelper('PanelPower', PanelPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanelPower')

    def UpdatePanelPower(self, value, qualifier):

        if 1 <= int(qualifier['Panel Number']) <= 200:
            PanelPowerCmdString = 'PANEL.POWER(PN{0})?\r'.format(qualifier['Panel Number'])
            self.__UpdateHelper('PanelPower', PanelPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePanelPower')

    def __MatchPanelPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 0 <= int(match.group(1)) <= 200:
            qualifier = {'Panel Number': match.group(1).decode()}
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('PanelPower', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'ON', 
            'Off'   : 'OFF',
        }

        if value in ValueStateValues:
            PowerCmdString = 'SYSTEM.POWER={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'SYSTEM.POWER?\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):


        value = match.group(1).decode().title()
        self.WriteStatus('Power', value, None)

    def UpdatePowerModuleStatus(self, value, qualifier):

        if 1 <= int(qualifier['Module']) <= 4:
            PowerModuleStatusCmdString = 'PS.STATUS({})?\r\n'.format(qualifier['Module'])
            self.__UpdateHelper('PowerModuleStatus', PowerModuleStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePowerModuleStatus')

    def __MatchPowerModuleStatus(self, match, tag):

        ValueStateValues = {
            0   : 'Unspecified fault 1',
            1   : 'Communication Memory Fault',
            2   : 'Module temperature may have exceeded the maximum',
            3   : 'VAC is below minimum',
            4   : 'IDC is above maximum',
            5   : 'VDC is above maximum',
            6   : 'Module DC is off',
            7   : 'Module is performing previously requested actions',
            8   : 'Unspecified fault 2',
            9   : 'Unspecified fault 3',
            10  : 'Fan failure',
            11  : 'Power status',
            12  : 'Unspecified fault 4',
            13  : 'VAC fault warning',
            14  : 'IDC fault or warning',
            15  : 'VDC fault or warning'
        }

        value = ''
        response = "{0:b}".format(int(match.group(2).decode(), 16))[::-1].ljust(16, '0')

        if match.group(2).decode().upper() == 'FFFFFFFF':
            value = 'Module not present, invalid or off'
        elif response.count('1') == 0:
            value = 'Normal'
        elif response.count('1') >= 2:
            value = 'Multiple Errors'
        else:
            for i in range(0, len(response)):
                if response[i] == '1':
                    value = ValueStateValues[i]

        if value:
            self.WriteStatus('PowerModuleStatus', value , {'Module': match.group(1).decode()} )

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 999:
            PresetRecallCmdString = 'PRESET.RECALL({})\r\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier) # Query delay not needed, tested in v1_1_0
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'PRESET.ACTIVE?\r\n'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = int(match.group(1))
        if 0 <= value <= 999:
            self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 999:
            PresetSaveCmdString = 'PRESET.SAVE({})\r\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier) # Query delay not needed, tested in v1_1_0
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'ENABLE',
            'Disable' : 'DISABLE'
        }
        if value in ValueStateValues:
            RemoteLockCmdString = 'IR.LOCK={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRemoteLock')

    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = 'IR.LOCK?\r\n'
        self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def __MatchRemoteLock(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('RemoteLock', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'None'          : 'NONE',
            'Black'         : 'BLACK',
            'White'         : 'WHITE',
            'Red'           : 'RED',
            'Green'         : 'GREEN',
            'Blue'          : 'BLUE',
            'Cyan'          : 'CYAN',
            'Magenta'       : 'MAGENTA',
            'Yellow'        : 'YELLOW',
            'Gray'          : 'GRAY',
            'Custom Color'  : 'CUSTOM_COLOR',
            'Red Scale'     : 'RED_SCALE',
            'Green Scale'   : 'GREEN_SCALE',
            'Blue Scale'    : 'BLUE_SCALE',
            'Gray Scale'    : 'GRAY_SCALE',
            'Logo'          : 'LOGO',
            'Grid'          : 'GRID',
            'Contrast'      : 'CONTRAST',
            'Color Bars'    : 'COLOR_BARS'
        }

        if value in ValueStateValues:
            TestPatternCmdString = 'PATTERN={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'PATTERN?\r\n'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            'NONE'          : 'None',
            'BLACK'         : 'Black',
            'WHITE'         : 'White',
            'RED'           : 'Red',
            'GREEN'         : 'Green',
            'BLUE'          : 'Blue',
            'CYAN'          : 'Cyan',
            'MAGENTA'       : 'Magenta',
            'YELLOW'        : 'Yellow',
            'GRAY'          : 'Gray',
            'CUSTOM_COLOR'  : 'Custom Color',
            'RED_SCALE'     : 'Red Scale',
            'GREEN_SCALE'   : 'Green Scale',
            'BLUE_SCALE'    : 'Blue Scale',
            'GRAY_SCALE'    : 'Gray Scale',
            'LOGO'          : 'Logo',
            'GRID'          : 'Grid',
            'CONTRAST'      : 'Contrast',
            'COLOR_BARS'    : 'Color Bars'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

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

    def __MatchError(self, match, qualifier):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '1' : 'Invalid syntax',
            '2' : 'Reserved for future use',
            '3' : 'Command not recognized',
            '4' : 'Invalid modifier',
            '5' : 'Invalid operands',
            '6' : 'Invalid operator'
        }

        if match.group(1):
            value = match.group(1).decode()
        else:
            value = match.group(2).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error: ' + DEVICE_ERROR_CODES[value]])
        elif 'NAK' in value:
            self.Error(['Error: Command was received but cannot be processed at this time.'])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

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

