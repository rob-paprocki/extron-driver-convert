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
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ColorTemperature': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Scheme': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'\(0;ASP=([1289])\)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(rb'\(0;AUS=([01])\)\r'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(rb'\(0;CTS=([0-5])\)\r'), self.__MatchColorTemperature, None)
            self.AddMatchString(re.compile(rb'\(0;KLO=([01])\)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(rb'\(0;INS=([0-7])\)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(rb'\(0;MUT=([01])\)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(rb'\(0;PWR=([01])\)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(rb'\(0;MMP=([1-37-9])\)\r'), self.__MatchScheme, None)
            self.AddMatchString(re.compile(rb'\(0;VOL=([0-9]{1,2}|100)\)\r'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(rb'\(([1-9]|10|11);(ASP|AUS|ACB|CTS|KLO|KEY|INS|MUT|PWR|MMP|VOL)'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen': '1',
            '4:3': '2',
            'Letterbox': '8',
            'Native': '9'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = '(ASP={})\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(ASP?)\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Full Screen',
            '2': '4:3',
            '8': 'Letterbox',
            '9': 'Native'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Default': '0',
            'Audio In': '1'
        }

        if value in ValueStateValues:
            AudioInputCmdString = '(AUS={})\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdString = '(AUS?)\r'
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            '0': 'Default',
            '1': 'Audio In'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInput', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ACB=1)\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetColorTemperature(self, value, qualifier):

        ValueStateValues = {
            '9300K': '0',
            '6500K': '1',
            '5000K': '2',
            'User': '3',
            '7500K': '4',
            '3200K': '5'
        }

        if value in ValueStateValues:
            ColorTemperatureCmdString = '(CTS={})\r'.format(ValueStateValues[value])
            self.__SetHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorTemperature')

    def UpdateColorTemperature(self, value, qualifier):

        ColorTemperatureCmdString = '(CTS?)\r'
        self.__UpdateHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)

    def __MatchColorTemperature(self, match, tag):

        ValueStateValues = {
            '0': '9300K',
            '1': '6500K',
            '2': '5000K',
            '3': 'User',
            '4': '7500K',
            '5': '3200K'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorTemperature', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '(KLO={})\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '(KLO?)\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '(KEY=28)\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'DisplayPort': '3',
            'Android': '4',
            'Web Browser': '5',
            'Media Player': '6',
            'Android App': '7'
        }

        if value in ValueStateValues:
            InputCmdString = '(INS={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(INS?)\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'DisplayPort',
            '4': 'Android',
            '5': 'Web Browser',
            '6': 'Media Player',
            '7': 'Android App'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '11',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8',
            '8': '9',
            '9': '10'
        }

        if value in ValueStateValues:
            KeypadCmdString = '(KEY={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '18',
            'Down': '19',
            'Left': '20',
            'Right': '21',
            'Enter': '22',
            'Exit': '23',
            'Menu': '24'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '(KEY={})\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            MuteCmdString = '(MUT={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '(MUT?)\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerCmdString = '(PWR={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetScheme(self, value, qualifier):

        ValueStateValues = {
            'Standard': '1',
            'Soft': '2',
            'User': '3',
            'Vivid': '7',
            'Natural': '8',
            'Sports': '9'
        }

        if value in ValueStateValues:
            SchemeCmdString = '(MMP={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Scheme', SchemeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScheme')

    def UpdateScheme(self, value, qualifier):

        SchemeCmdString = '(MMP?)\r'
        self.__UpdateHelper('Scheme', SchemeCmdString, value, qualifier)

    def __MatchScheme(self, match, tag):

        ValueStateValues = {
            '1': 'Standard',
            '2': 'Soft',
            '3': 'User',
            '7': 'Vivid',
            '8': 'Natural',
            '9': 'Sports'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Scheme', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '(VOL={})\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '(VOL?)\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

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

        command_map = {
            'ASP': 'Aspect Ratio',
            'AUS': 'Audio Input',
            'ACB': 'Auto Image',
            'CTS': 'Color Temperature',
            'KLO': 'Executive Mode',
            'KEY': 'Freeze/Keypad/Menu Navigation',
            'INS': 'Input',
            'MUT': 'Mute',
            'PWR': 'Power',
            'MMP': 'Scheme',
            'VOL': 'Volume'
        }

        error_map = {
            '1':    'Unknown command code',
            '2':    'Invalid operator',
            '3':    'Destination parameter not supported',
            '4':    'Setting not available',
            '5':    'Setting value not available',
            '6':    'Setting value not supported',
            '7':    'String too long',
            '8':    'Command not supported in standby mode',
            '9':    'Invalid parameter',
            '10':   'Error processing command',
            '11':   'Password not entered'
        }

        self.Error(['An error occurred: {}: {}.'.format(command_map[match.group(2).decode()], error_map[match.group(1).decode()])])

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

