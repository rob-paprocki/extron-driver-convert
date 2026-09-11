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
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'IRControl': {'Status': {}},
            'KeyboardControl': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'5b0035500(0|1)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'5b0030100(0|1|3|6|8|9)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'5b0039200(0|1)\r'), self.__MatchIRControl, None)
            self.AddMatchString(re.compile(b'5b0030300(0|1)\r'), self.__MatchKeyboardControl, None)
            self.AddMatchString(re.compile(b'5b0036100(0|1|2|3|4)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'5b0036000(0|1|2)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'5b0030000(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'5b00350([0-9]{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'560036\r|5600-\r'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '5b00155001\r',
            'Off': '5b00155000\r'
            }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '5800255\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            '1': 'On',
            '0': 'Off'
            }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'HDMI 1': '5b00101000\r',
            'HDMI 2': '5b00101001\r',
            'VGA': '5b00101003\r',
            'YPbPr': '5b00101006\r',
            'AV': '5b00101008\r',
            'DP 1': '5b00101009\r'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '5800201\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '3': 'VGA',
            '6': 'YPbPr',
            '8': 'AV',
            '9': 'DP 1'
            }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetIRControl(self, value, qualifier):

        IRControlState = {
            'On': '5b00192001\r',
            'Off': '5b00192000\r'
            }

        IRControlCmdString = IRControlState[value]
        self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)

    def UpdateIRControl(self, value, qualifier):

        IRControlCmdString = '5800292\r'
        self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)

    def __MatchIRControl(self, match, tag):

        IRControlState = {
            '1': 'On',
            '0': 'Off'
            }

        value = IRControlState[match.group(1).decode()]
        self.WriteStatus('IRControl', value, None)

    def SetKeyboardControl(self, value, qualifier):

        KeyboardControlState = {
            'Enable': '5b00103001\r',
            'Disable': '5b00103000\r'
            }

        KeyboardControlCmdString = KeyboardControlState[value]
        self.__SetHelper('KeyboardControl', KeyboardControlCmdString, value, qualifier)

    def UpdateKeyboardControl(self, value, qualifier):

        KeyboardControlCmdString = '5800203\r'
        self.__UpdateHelper('KeyboardControl', KeyboardControlCmdString, value, qualifier)

    def __MatchKeyboardControl(self, match, tag):

        KeyboardControlState = {
            '1': 'Enable',
            '0': 'Disable'
            }

        value = KeyboardControlState[match.group(1).decode()]
        self.WriteStatus('KeyboardControl', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'Off': '5b00161000\r',
            'PIP': '5b00161001\r',
            'POP': '5b00161002\r',
            'PBP-1': '5b00161003\r',
            'PBP-2': '5b00161004\r'
            }

        PIPModeCmdString = PIPModeState[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '5800261\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeState = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'POP',
            '3': 'PBP-1',
            '4': 'PBP-2'
            }

        value = PIPModeState[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Top Left': '5b00164000\r',
            'Top Right': '5b00164100\r',
            'Bottom Left': '5b00165000\r',
            'Bottom Right': '5b00165100\r'
            }

        PIPPositionCmdString = PIPPositionState[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
            'Small': '5b00160000\r',
            'Middle': '5b00160001\r',
            'Large': '5b00160002\r'
            }

        PIPSizeCmdString = PIPSizeState[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '5800260\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
            '0': 'Small',
            '1': 'Middle',
            '2': 'Large'
            }

        value = PIPSizeState[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '5b00100001\r',
            'Off': '5b00100000\r'
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '5800200\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '1': 'On',
            '0': 'Off'
            }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '5b00150' + str(value).zfill(3) + '\r'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '5800250\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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

        value = 'Error:' + match.group(0).decode() + ' = Invalid Command.'
        print(value)

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