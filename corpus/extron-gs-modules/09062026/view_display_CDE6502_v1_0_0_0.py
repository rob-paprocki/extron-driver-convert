from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Type'], 'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}r([nopq])00(0|1)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rj0(04|14|06)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rg00(0|1)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rl00(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rf(\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 1 <= int(value) <= 98:
            self._DeviceID = '{0:02d}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': '0',
            'Normal': '1',
            'Custom': '2',
            'Dynamic': '3',
            'Real': '4'
        }

        AspectRatioCmdString = '8{0}s100{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Power': '4',
            'Button': '8',
            'Menu': '>',
            'Remote Control': 'B'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        RCValues = {
            'On': '0',
            'Off': '1'
        }
        if qualifier['Type'] != 'Remote Control':
            ExecutiveModeCmdString = '8{0}s{1}00{2}\r'.format(self._DeviceID, TypeStates[qualifier['Type']], ValueStateValues[value])
        else:
            ExecutiveModeCmdString = '8{0}s{1}00{2}\r'.format(self._DeviceID, TypeStates[qualifier['Type']], RCValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Power': 'o',
            'Button': 'p',
            'Menu': 'q',
            'Remote Control': 'n'
        }

        ExecutiveModeCmdString = '8{0}g{1}000\r'.format(self._DeviceID, TypeStates[qualifier['Type']])
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        TypeStates = {
            'o': 'Power',
            'p': 'Button',
            'q': 'Menu',
            'n': 'Remote Control'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        RCValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Type': TypeStates[match.group(1).decode()]}
        if TypeStates[match.group(1).decode()] != 'Remote Control':
            value = ValueStateValues[match.group(2).decode()]
        else:
            value = RCValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '04',
            'HDMI 2': '14',
            'VGA': '06'
        }

        InputCmdString = '8{0}s\x220{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '8{0}gj000\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '04': 'HDMI 1',
            '14': 'HDMI 2',
            '06': 'VGA'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '0',
            'Down': '1',
            'Left': '2',
            'Right': '3',
            'Enter': '4',
            'Menu': '6'
        }

        MenuNavigationCmdString = '8{0}sA00{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MuteCmdString = '8{0}s600{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '8{0}gg000\r'.format(self._DeviceID)
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

        PowerCmdString = '8{0}s!00{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '8{0}gl000\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '8{0}s5{1:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '8{0}gf000\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }
        value = int(match.group(1).decode())
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        print('Device responded with an error message.')

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it was matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True 
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
