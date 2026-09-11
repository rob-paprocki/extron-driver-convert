from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re
from extronlib.system import Wait, ProgramLog


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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberKey': {'Status': {}},
            'PCStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }
               
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x01[\x00-\x01]([\x83-\x84])\xDD\xEE\xFF'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x81[\x01-\x0D]\x00([\x82-\x8E])\xDD\xEE\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x83[\x00-\x03]\x00([\x83-\x86])\xDD\xEE\xFF'), self.__MatchPCStatus, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x80[\x00-\x01]\x00([\x80-\x81])\xDD\xEE\xFF'), self.__MatchPower, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': (0x01, 0x09),
            '16:9': (0x00, 0x08),
            'Point to Point': (0x07, 0x0F)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x08, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': (0x00, 0x04),
            'Off': (0x01, 0x05)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x03, 0x01, States[value][0], States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', b'\xAA\xBB\xCC\x03\x03\x00\x06\xDD\xEE\xFF', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            131: 'On',
            132: 'Off'
        }

        self.WriteStatus('AudioMute', States[ord(match.group(1))], None)

    def SetInput(self, value, qualifier):

        States = {
            'TV': (0x01, 0x03),
            'CVBS': (0x02, 0x04),
            'VGA3': (0x0B, 0x0D),
            'VGA1': (0x03, 0x05),
            'VGA2': (0x04, 0x06),
            'HDMI1': (0x06, 0x08),
            'HDMI2': (0x07, 0x09),
            'HDMI3': (0x05, 0x07),
            'PC': (0x08, 0x0A),
            'Android': (0x0A, 0x0C),
            'WHDI': (0x0C, 0x0E),
            'HDMI (4k*2K)': (0x0D, 0x0F),
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x02, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', b'\xAA\xBB\xCC\x02\x00\x00\x02\xDD\xEE\xFF', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            130: 'TV',
            131: 'CVBS',
            140: 'VGA3',
            132: 'VGA1',
            133: 'VGA2',
            135: 'HDMI1',
            136: 'HDMI2',
            134: 'HDMI3',
            137: 'PC',
            139: 'Android',
            142: 'HDMI (4k*2K)',
            141: 'WHDI'
        }

        self.WriteStatus('Input', States[ord(match.group(1))], None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Left': (0x49, 0x50),
            'Right': (0x4B, 0x52),
            'Up': (0x47, 0x4E),
            'Down': (0x4D, 0x54),
            'Menu': (0x0D, 0x14),
            'Enter': (0x4A, 0x51),
            'Return': (0x0A, 0x11),
            'Home': (0x48, 0x4F)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x07, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetNumberKey(self, value, qualifier):

        States = {
            '0': (0x1B, 0x22),
            '1': (0x00, 0x07),
            '2': (0x10, 0x17),
            '3': (0x11, 0x18),
            '4': (0x13, 0x1A),
            '5': (0x14, 0x1B),
            '6': (0x15, 0x1C),
            '7': (0x17, 0x1E),
            '8': (0x18, 0x1F),
            '9': (0x19, 0x20)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x07, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('NumberKey', CmdString, value, qualifier)

    def UpdatePCStatus(self, value, qualifier):
        self.__UpdateHelper('PCStatus', b'\xAA\xBB\xCC\x09\x02\x00\x0B\xDD\xEE\xFF', value, qualifier)

    def __MatchPCStatus(self, match, tag):

        States = {
            131: 'On',
            132: 'Off',
            133: 'Sleep',
            134: 'Hibernate'
        }

        self.WriteStatus('PCStatus', States[ord(match.group(1))], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': (0x00, 0x01),
            'Off': (0x01, 0x02)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x01, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', b'\xAA\xBB\xCC\x01\x02\x00\x03\xDD\xEE\xFF', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            128: 'On',
            129: 'Off'
        }

        self.WriteStatus('Power', States[ord(match.group(1))], None)

    def SetVolume(self, value, qualifier):

        States = {
            'Up': (0x03, 0x0A),
            'Down': (0x41, 0x48)
            }

        CmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x07, States[value][0], 0x00, States[value][1], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Volume', CmdString, value, qualifier)

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
