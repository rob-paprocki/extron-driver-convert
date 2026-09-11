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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'Home': {'Parameters': ['Camera'], 'Status': {}},
            'Pan': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Tilt': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Camera', 'Speed'], 'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'standby:\s+(on|off)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'pattern\s+(color_bars|black_screen)\r\n'), self.__MatchVideoMute, None)

    def SetFocus(self, value, qualifier):

        Camera = int(qualifier['Camera'])
        Speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Near': 'near',
            'Far': 'far',
        }

        if 1 <= Camera <= 16 and 1 <= Speed <= 8:
            if value == 'Stop':
                FocusCmdString = 'camera {0} focus stop\r'.format(Camera)
            else:
                FocusCmdString = 'camera {0} focus {1} {2}\r'.format(Camera, ValueStateValues[value], Speed)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetHome(self, value, qualifier):

        Camera = int(qualifier['Camera'])
        if 1 <= Camera <= 16:
            HomeCmdString = 'camera {0} home\r'.format(Camera)
            self.__SetHelper('Home', HomeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHome')

    def SetPan(self, value, qualifier):

        Camera = int(qualifier['Camera'])
        Speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right',
        }

        if 1 <= Camera <= 16 and 1 <= Speed <= 24:
            if value == 'Stop':
                PanCmdString = 'camera {0} pan stop\r'.format(Camera)
            else:
                PanCmdString = 'camera {0} pan {1} {2}\r'.format(Camera, ValueStateValues[value], Speed)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'off',
            'Off': 'on'
        }

        PowerCmdString = 'system standby {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'system standby get\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'off': 'On',
            'on': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTilt(self, value, qualifier):

        Camera = int(qualifier['Camera'])
        Speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
        }

        if 1 <= Camera <= 16 and 1 <= Speed <= 20:
            if value == 'Stop':
                TiltCmdString = 'camera {0} tilt stop\r'.format(Camera)
            else:
                TiltCmdString = 'camera {0} tilt {1} {2}\r'.format(Camera, ValueStateValues[value], Speed)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilt')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'black_screen',
            'Off': 'color_bars'
        }

        VideoMuteCmdString = 'video mute pattern set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'video mute pattern get\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'black_screen': 'On',
            'color_bars': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        Camera = int(qualifier['Camera'])
        Speed = int(qualifier['Speed'])

        ValueStateValues = {
            'In': 'in',
            'Out': 'out',
        }

        if 1 <= Camera <= 16 and 1 <= Speed <= 7:
            if value == 'Stop':
                ZoomCmdString = 'camera {0} zoom stop\r'.format(Camera)
            else:
                ZoomCmdString = 'camera {0} zoom {1} {2}\r'.format(Camera, ValueStateValues[value], Speed)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
