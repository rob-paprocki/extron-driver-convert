from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
            'AntennaInput': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Teletext': {'Status': {}},
            'TeletextMode': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x58\x00\x01\x04([\x00-\xFF])[\x00-\xFF]{4}'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x58\x00\x00\x01([\x02|\x03])[\x00-\xFF]'), self.__MatchError, None)

    def InitilizeControl(self):

        self.Send(b'\x58\x80\x00\x00\xD8')
        self.Send(b'\x58\x80\x15\x02\x00\x00\xEF')

    def SetAntennaInput(self, value, qualifier):

        ValueStateValues = {
            'Air': b'\x58\x80\x32\x01\x00\x0B',
            'Cable': b'\x58\x80\x32\x01\x80\x8B'
        }

        AntennaInputCmdString = ValueStateValues[value]
        self.__SetHelper('AntennaInput', AntennaInputCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto Wide': b'\x58\x80\x08\x01\x00\xE1',
            '16:9': b'\x58\x80\x08\x01\x01\xE2',
            'Just Scan': b'\x58\x80\x08\x01\x02\xE3',
            '4:3': b'\x58\x80\x08\x01\x03\xE4'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x58\x80\x05\x02\x07\x12\xF8',
            'Down': b'\x58\x80\x05\x02\x07\x10\xF6'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': b'\x58\x80\x06\x01\x03\xE2',
            'HDMI 1': b'\x58\x80\x06\x01\x0B\xEA',
            'HDMI 2': b'\x58\x80\x06\x01\x0C\xEB',
            'Component': b'\x58\x80\x06\x01\x07\xE6'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x58\x80\x05\x02\x07\x11\xF7',
            '1': b'\x58\x80\x05\x02\x07\x04\xEA',
            '2': b'\x58\x80\x05\x02\x07\x05\xEB',
            '3': b'\x58\x80\x05\x02\x07\x06\xEC',
            '4': b'\x58\x80\x05\x02\x07\x08\xEE',
            '5': b'\x58\x80\x05\x02\x07\x09\xEF',
            '6': b'\x58\x80\x05\x02\x07\x0A\xF0',
            '7': b'\x58\x80\x05\x02\x07\x0C\xF2',
            '8': b'\x58\x80\x05\x02\x07\x0D\xF3',
            '9': b'\x58\x80\x05\x02\x07\x0E\xF4'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x58\x80\x05\x02\x07\x60\x46',
            'Down': b'\x58\x80\x05\x02\x07\x61\x47',
            'Right': b'\x58\x80\x05\x02\x07\x62\x48',
            'Left': b'\x58\x80\x05\x02\x07\x65\x4B',
            'Enter': b'\x58\x80\x05\x02\x07\x68\x4E',
            'Exit': b'\x58\x80\x05\x02\x07\x2D\x13',
            'Guide': b'\x58\x80\x05\x02\x07\x4F\x35',
            'TV': b'\x58\x80\x05\x02\x07\x1B\x01',
            'WiseLink': b'\x58\x80\x05\x02\x07\x8C\x72',
            'Return': b'\x58\x80\x05\x02\x07\x58\x3E'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x58\x80\x05\x02\x07\x0F\xF5'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x58\x80\x16\x01\x00\xEF',
            'Disable': b'\x58\x80\x16\x01\x80\x6F'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': b'\x58\x80\x1D\x01\x00\xF6',
            'Standard': b'\x58\x80\x1D\x01\x01\xF7',
            'Movie': b'\x58\x80\x1D\x01\x02\xF8'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x58\x80\x01\x01\x80\x5A',
            'Off': b'\x58\x80\x01\x01\x00\xDA'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x58\x80\x00\x00\xD8'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        StateValues = {
            '1': 'On',
            '0': 'Off'
        }

        temp = '{0:08b}'.format(ord(match.group(1)))
        self.WriteStatus('Power', StateValues[temp[3]], None)
        self.WriteStatus('TeletextMode', StateValues[temp[4]], None)

    def SetTeletext(self, value, qualifier):

        ValueStateValues = {
            'Key': b'\x58\x80\x05\x02\x07\x2C\x12',
            'Red': b'\x58\x80\x05\x02\x07\x6C\x52',
            'Green': b'\x58\x80\x05\x02\x07\x14\xFA',
            'Yellow': b'\x58\x80\x05\x02\x07\x15\xFB',
            'Cyan': b'\x58\x80\x05\x02\x07\x16\xFC'
        }

        TeletextCmdString = ValueStateValues[value]
        self.__SetHelper('Teletext', TeletextCmdString, value, qualifier)

    def SetTeletextMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x58\x80\x07\x01\x80\x60',
            'Off': b'\x58\x80\x07\x01\x00\xE0'
        }

        TeletextModeCmdString = ValueStateValues[value]
        self.__SetHelper('TeletextMode', TeletextModeCmdString, value, qualifier)

    def UpdateTeletextMode(self, value, qualifier):
        self.UpdatePower(None, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CheckSum = (0xE6 + value) & 0xFF
            VolumeCmdString = pack('>BBBBBB', 0x58, 0x80, 0x0D, 0x01, value, CheckSum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

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

        ErrorCodes = {
            '\x02' : 'Command not Acknowledged.',
            '\x03' : 'Command Unsupported.'
            }
        print(ErrorCodes[match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.InitilizeControl()

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
