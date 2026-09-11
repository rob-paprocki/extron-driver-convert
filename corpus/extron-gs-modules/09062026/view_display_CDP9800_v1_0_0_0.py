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
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Mode'], 'Status': {}},
            'Input': { 'Status': {}},
            'IRRemote': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}r(?P<mode>[opq])00(?P<value>[01])\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rj0(?P<value>0[0-9]|1[46]|24)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rn00(?P<value>[0-2])\r'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rg00(?P<value>[01])\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rl00(?P<value>[01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rf(?P<value>\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 1 <= int(value) <= 98:
            self._DeviceID = temp.zfill(2)

    def __CommandBuilder(self, cmd_type, cmd, value=None):

        value = '000' if not value else value.zfill(3)
        return '8' + self._DeviceID + cmd_type + cmd + value + '\r'

    def SetAspectRatio(self, value, qualifier):


        ValueStateValues = {
            'Full'   : '0',
            'Normal' : '1', 
            'Custom' : '2', 
            'Dynamic': '3',
            'Real'   : '4'
        }

        if value in ValueStateValues:
            self.__SetHelper('AspectRatio', self.__CommandBuilder(cmd_type='s', cmd='1', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')
    def SetExecutiveMode(self, value, qualifier):


        ModeStates = {
            'Power' : '4',
            'Button': '8',
            'Menu'  : '>'
        }

        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }

        if value in ValueStateValues and qualifier['Mode'] in ModeStates:
            self.__SetHelper('ExecutiveMode', self.__CommandBuilder(cmd_type='s', cmd=ModeStates[qualifier['Mode']], value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):


        ModeStates = {
            'Power' : 'o',
            'Button': 'p',
            'Menu'  : 'q'
        }

        if qualifier['Mode'] in ModeStates:
            self.__UpdateHelper('ExecutiveMode', self.__CommandBuilder(cmd_type='g', cmd=ModeStates[qualifier['Mode']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):


        ModeStates = {
            'o': 'Power',
            'p': 'Button',
            'q': 'Menu'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('ExecutiveMode', value, {'Mode': ModeStates[match.group('mode').decode()]})

    def SetInput(self, value, qualifier):


        ValueStateValues = {
            'TV'             : '0',
            'AV'             : '1',
            'S-Video'        : '2',
            'YPbPr'          : '3',
            'HDMI 1'         : '4',
            'HDMI 2'         : '14',
            'HDMI 3'         : '24',
            'DVI'            : '5',
            'VGA 1 (PC)'     : '6',
            'VGA 2'          : '16',
            'OPS'            : '7',
            'Internal Memory': '8',
            'DisplayPort'    : '9'
        }

        if value in ValueStateValues:
            self.__SetHelper('Input', self.__CommandBuilder(cmd_type='s', cmd='"', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):


        self.__UpdateHelper('Input', self.__CommandBuilder(cmd_type='g', cmd='j'), value, qualifier)

    def __MatchInput(self, match, tag):


        ValueStateValues = {
            '00': 'TV',
            '01': 'AV',
            '02': 'S-Video',
            '03': 'YPbPr',
            '04': 'HDMI 1',
            '14': 'HDMI 2',
            '24': 'HDMI 3',
            '05': 'DVI',
            '06': 'VGA 1 (PC)',
            '16': 'VGA 2',
            '07': 'OPS',
            '08': 'Internal Memory',
            '09': 'DisplayPort'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('Input', value, None)

    def SetIRRemote(self, value, qualifier):


        ValueStateValues = {
            'Enable'      : '1',
            'Disable'     : '0',
            'Pass through': '2'
        }

        if value in ValueStateValues:
            self.__SetHelper('IRRemote', self.__CommandBuilder(cmd_type='s', cmd='B', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemote')

    def UpdateIRRemote(self, value, qualifier):


        self.__UpdateHelper('IRRemote', self.__CommandBuilder(cmd_type='g', cmd='n'), value, qualifier)

    def __MatchIRRemote(self, match, tag):


        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable',
            '2': 'Pass through'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('IRRemote', value, None)

    def SetMenuNavigation(self, value, qualifier):


        ValueStateValues = {
            'Menu' : '6',
            'Up'   : '0',
            'Down' : '1',
            'Left' : '2',
            'Right': '3',
            'Enter': '4'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuNavigation', self.__CommandBuilder(cmd_type='s', cmd='A', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
    def SetMute(self, value, qualifier):


        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('Mute', self.__CommandBuilder(cmd_type='s', cmd='6', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):


        self.__UpdateHelper('Mute', self.__CommandBuilder(cmd_type='g', cmd='g'), value, qualifier)

    def __MatchMute(self, match, tag):


        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):


        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', self.__CommandBuilder(cmd_type='s', cmd='!', value=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):



        self.__UpdateHelper('Power', self.__CommandBuilder(cmd_type='g', cmd='l'), value, qualifier)

    def __MatchPower(self, match, tag):


        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }


        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):


        if 0 <= value <= 100:
            self.__SetHelper('Volume', self.__CommandBuilder(cmd_type='s', cmd='5', value=str(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):


        self.__UpdateHelper('Volume', self.__CommandBuilder(cmd_type='g', cmd='f'), value, qualifier)

    def __MatchVolume(self, match, tag):


        value = int(match.group('value').decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '99':
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
        self.Error(['An error occurred.'])

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

