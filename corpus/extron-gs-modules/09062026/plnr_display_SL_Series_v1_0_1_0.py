from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
from struct import unpack
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
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio'           : {'Status': {}},
            'AutoImage'             : {'Status': {}},
            'Input'                 : {'Status': {}},
            'Keypad'                : {'Status': {}},
            'MenuNavigation'        : {'Status': {}},
            'Mute'                  : {'Status': {}},
            'OperationHours'        : {'Status': {}},
            'Power'                 : {'Status': {}},
            'Volume'                : {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x04\x01\x3B(\x00|\x02|\x03|\x04|\x05)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x05\x01\xAD\xFD(\x01|\x06|\x08|\x0A|\x0B|\x0F|\xFF)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x05\x01\x0F([\x00-\xFF]{2})[\x00-\xFF]'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x04\x01\x19(\x01|\x02)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x04\x01\x45([\x00-\x3C])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x21[\x00-\xFF]\x00\x00\x04\x01\x00(\x03|\x04)[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            print('Invalid Device ID value.')
            
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'         : 0x00, 
            'Native'      : 0x02, 
            'Full Screen' : 0x03, 
            'Letterbox'   : 0x04, 
            'Auto'        : 0x05
        }

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x3A ^ ValueStateValues[value]
        AspectRatioCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x3A, ValueStateValues[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x3B         
        AspectRatioCmdString = pack('>9B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x3B, checksum)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00' : '4:3', 
            '\x02' : 'Native', 
            '\x03' : 'Full Screen', 
            '\x04' : 'Letterbox', 
            '\x05' : 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x05 ^ 0x01 ^ 0x70 ^ 0x40 ^ 0x00 
        AutoImageCmdString = pack('>11B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x05, 0x01, 0x70, 0x40, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video'     : [0x01, 0x00], 
            'Component' : [0x03, 0x00], 
            'VGA'       : [0x05, 0x00], 
            'USB'       : [0x08, 0x01], 
            'HDMI'      : [0x09, 0x00], 
            'DVI-D'     : [0x09, 0x01]
        }

        val1 = ValueStateValues[value][0]
        val2 = ValueStateValues[value][1]

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0xAC ^ val1 ^ val2 ^ 0x01 ^ 0x00
        InputCmdString = pack('>13B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x07, 0x01, 0xAC, val1, val2, 0x01, 0x00, checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0xAD         
        InputCmdString = pack('>9B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0xAD, checksum)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'Video', 
            b'\x06' : 'Component', 
            b'\x08' : 'VGA', 
            b'\x0A' : 'HDMI', 
            b'\x0B' : 'DVI-D', 
            b'\x0F' : 'USB', 
            b'\xFF' : 'Unknown'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : 0x00, 
            '1' : 0x01, 
            '2' : 0x02, 
            '3' : 0x03, 
            '4' : 0x04, 
            '5' : 0x05, 
            '6' : 0x06, 
            '7' : 0x07, 
            '8' : 0x08, 
            '9' : 0x09
        }

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xDB ^ ValueStateValues[value]
        KeypadCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xDB, ValueStateValues[value], checksum)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'   : 0xA1, 
            'Up'     : 0xA6, 
            'Down'   : 0xA7, 
            'Left'   : 0xA8, 
            'Right'  : 0xA9, 
            'Ok'     : 0xB1, 
            'Return' : 0xB2
        }

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xDB ^ ValueStateValues[value]
        MenuNavigationCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xDB, ValueStateValues[value], checksum)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xDB ^ 0xA5        
        MuteCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xDB, 0xA5, checksum)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x0F ^ 0x02        
        OperationHoursCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x0F, 0x02, checksum)
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off' : 0x01, 
            'On'  : 0x02
        }

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x18 ^ ValueStateValues[value]
        PowerCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x18, ValueStateValues[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x19         
        PowerCmdString = pack('>9B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x19, checksum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01' : 'Off', 
            '\x02' : 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x44 ^ value
            VolumeCmdString = pack('>10B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x44, value, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = 0xA6 ^ self._DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x45         
        VolumeCmdString = pack('>9B', 0xA6, self._DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x45, checksum)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>B', match.group(1))[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ValueStateValues = {
            '\x03' : 'NACK Command Coce Error', 
            '\x04' : 'NAV Checksum Error'
        }

        value = match.group(0).decode().split(':')
        print(ValueStateValues[value])

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
