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
            'AudioInput': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiWindowMode': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'PresetMode': {'Status': {}},
            'Volume': {'Status': {}},
            'WindowInput': {'Parameters': ['Window'], 'Status': {}},
            'WindowMode': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ALL:\s?AUT=00([0-8])'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'ALL:\s?SRC=00([0-8])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ALL:\s?WMT=00([0-9])'), self.__MatchMultiWindowMode, None)
            self.AddMatchString(re.compile(b'ALL:\s?MUT=00([01])'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'ALL:\s?PMT=00([0-2])'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'ALL:\s?PWR=00([0-2])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ALL:\s?PRS=0([0-1][0-9]|20|1)'), self.__MatchPresetMode, None)
            self.AddMatchString(re.compile(b'ALL:\s?VOL=(0[0-9][0-9]|100)'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ALL:\s?W([1-4])S=00([0-8])'), self.__MatchWindowInput, None)
            self.AddMatchString(re.compile(b'ALL:\s?(AUT|SRC|WMT|RUP|RDN|RRT|RLT|REN|RMN|MUT|PMT|PWR|PRS|VOL|W1S|W2S|W3S|W4S|WN1|WN2|WN3|WN4)=N'), self.__MatchError, None)


# COMMAND BUILDER FUNCTION
    def __CommandBuilder(self, command, end, value=''):

        return 'K:ALL{CMD}{VAL}{END}'.format(CMD=command, VAL=value, END=end)


    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1': '0',
            'DisplayPort 2': '1',
            'HDMI 1': '2',
            'HDMI 2': '3',
            'HDMI 3': '4',
            'HDMI 4': '5',
            'DVI': '6',
            'OPS/HDMI': '7',
            'OPS/DP': '8'
        }

        if value in ValueStateValues:
            self.__SetHelper('AudioInput', self.__CommandBuilder(command='AI', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        self.__UpdateHelper('AudioInput', self.__CommandBuilder(command='AUT', end='?'), value, qualifier)

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            '0': 'DisplayPort 1',
            '1': 'DisplayPort 2',
            '2': 'HDMI 1',
            '3': 'HDMI 2',
            '4': 'HDMI 3',
            '5': 'HDMI 4',
            '6': 'DVI',
            '7': 'OPS/HDMI',
            '8': 'OPS/DP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInput', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1': '0',
            'DisplayPort 2': '1',
            'HDMI 1': '2',
            'HDMI 2': '3',
            'HDMI 3': '4',
            'HDMI 4': '5',
            'DVI': '6',
            'OPS/HDMI': '7',
            'OPS/DP': '8'
        }

        if value in ValueStateValues:
            self.__SetHelper('Input', self.__CommandBuilder(command='SH', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', self.__CommandBuilder(command='SRC', end='?'), value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'DisplayPort 1',
            '1': 'DisplayPort 2',
            '2': 'HDMI 1',
            '3': 'HDMI 2',
            '4': 'HDMI 3',
            '5': 'HDMI 4',
            '6': 'DVI',
            '7': 'OPS/HDMI',
            '8': 'OPS/DP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MN',
            'Up': 'UP',
            'Down': 'DN',
            'Left': 'LT',
            'Right': 'RT',
            'Enter': 'EN'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuNavigation', self.__CommandBuilder(command='R', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMultiWindowMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'F',
            'Single': '0',
            'Dual 1': '1',
            'Dual 2': '2',
            'Dual 3': '3',
            'Dual 4': '4',
            'Triple 1': '5',
            'Triple 2': '6',
            'Triple 3': '7',
            'Triple 4': '8',
            'Quad': '9'
        }

        if value in ValueStateValues:
            if value != 'Off':
                self.__SetHelper('MultiWindowMode', self.__CommandBuilder(command='WM', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiWindowMode')

    def UpdateMultiWindowMode(self, value, qualifier):

        self.__UpdateHelper('MultiWindowMode', self.__CommandBuilder(command='WMT', end='?'), value, qualifier)

    def __MatchMultiWindowMode(self, match, tag):

        ValueStateValues = {
            '0': 'Single',
            '1': 'Dual 1',
            '2': 'Dual 2',
            '3': 'Dual 3',
            '4': 'Dual 4',
            '5': 'Triple 1',
            '6': 'Triple 2',
            '7': 'Triple 3',
            '8': 'Triple 4',
            '9': 'Quad'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MultiWindowMode', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'N',
            'Off': 'F'
        }

        if value in ValueStateValues:
            self.__SetHelper('Mute', self.__CommandBuilder(command='MO', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        self.__UpdateHelper('Mute', self.__CommandBuilder(command='MUT', end='?'), value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Dynamic': '1',
            'User': '2'
        }

        if value in ValueStateValues:
            self.__SetHelper('PictureMode', self.__CommandBuilder(command='PM', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        self.__UpdateHelper('PictureMode', self.__CommandBuilder(command='PMT', end='?'), value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Dynamic',
            '2': 'User'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'N',
            'Off': 'F'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', self.__CommandBuilder(command='PO', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', self.__CommandBuilder(command='PWR', end='?'), value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off',
            '2': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetMode(self, value, qualifier):

        preset = 0 if value == 'Off' else int(value)

        if 0 <= preset <= 20:
            self.__SetHelper('PresetMode', self.__CommandBuilder(command='PRS', end='.', value=str(preset).zfill(3)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetMode')

    def UpdatePresetMode(self, value, qualifier):

        self.__UpdateHelper('PresetMode', self.__CommandBuilder(command='PRS', end='?'), value, qualifier)

    def __MatchPresetMode(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8',
            '09': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            '1': '20'  # added to account for likely bug in firmware
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresetMode', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', self.__CommandBuilder(command='VOL', end='.', value=str(value).zfill(3)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', self.__CommandBuilder(command='VOL', end='?'), value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetWindowInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1': '0',
            'DisplayPort 2': '1',
            'HDMI 1': '2',
            'HDMI 2': '3',
            'HDMI 3': '4',
            'HDMI 4': '5',
            'DVI': '6',
            'OPS/HDMI': '7',
            'OPS/DP': '8'
        }

        if value in ValueStateValues and qualifier['Window'] in '1234':
            self.__SetHelper('WindowInput', self.__CommandBuilder(command='W{}'.format(qualifier['Window']), end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowInput')

    def UpdateWindowInput(self, value, qualifier):

        if qualifier['Window'] in '1234':
            self.__UpdateHelper('WindowInput', self.__CommandBuilder(command='W{}S'.format(qualifier['Window']), end='?'), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowInput')

    def __MatchWindowInput(self, match, tag):

        WindowStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '0': 'DisplayPort 1',
            '1': 'DisplayPort 2',
            '2': 'HDMI 1',
            '3': 'HDMI 2',
            '4': 'HDMI 3',
            '5': 'HDMI 4',
            '6': 'DVI',
            '7': 'OPS/HDMI',
            '8': 'OPS/DP'
        }

        qualifier = {}
        qualifier['Window'] = WindowStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('WindowInput', value, qualifier)

    def SetWindowMode(self, value, qualifier):

        ValueStateValues = {
            'Window 1': '1',
            'Window 2': '2',
            'Window 3': '3',
            'Window 4': '4'
        }

        if value in ValueStateValues:
            self.__SetHelper('WindowMode', self.__CommandBuilder(command='WN', end='.', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowMode')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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
        else:
            self.Send(commandstring)


    def __MatchError(self, match, tag):
        self.counter = 0
        
        COMMANDS = {
            'AUT': 'Audio Input',
            'SRC': 'Input',
            'WMT': 'Multi Window Mode',
            'RUP': 'Menu Navigation',
            'RDN': 'Menu Navigation',
            'RRT': 'Menu Navigation',
            'RLT': 'Menu Navigation',
            'REN': 'Menu Navigation',
            'RMN': 'Menu Navigation',
            'MUT': 'Mute',
            'PMT': 'Picture Mode',
            'PWR': 'Power',
            'PRS': 'Preset Mode',
            'VOL': 'Volume',
            'W1S': 'Window 1 Input',
            'W2S': 'Window 2 Input',
            'W3S': 'Window 3 Input',
            'W4S': 'Window 4 Input',
            'WN1': 'Window Mode',
            'WN2': 'Window Mode',
            'WN3': 'Window Mode',
            'WN4': 'Window Mode'
        }
        
        value = COMMANDS[match.group(1).decode()]
        self.Error(['Error: {}'.format(value)])

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

