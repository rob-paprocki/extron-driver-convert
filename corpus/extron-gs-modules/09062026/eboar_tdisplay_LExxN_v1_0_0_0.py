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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControl': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x80(\x00|\x01)\x00(\x80|\x81)\xDD\xEE\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x00([\x00-\x64])[\x00-\xFF]\xDD\xEE\xFF'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x01(\x00|\x01)(\x83|\x84)\xDD\xEE\xFF'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x81([\x03-\x11])\x00[\x84-\x92]\xDD\xEE\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x83([\x00-\x03])\x00[\x83-\x86]\xDD\xEE\xFF'), self.__MatchPCPower, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '16:9': b'\x08\x00\x00\x08',
            '4:3': b'\x08\x01\x00\x09',
            'Point to Point': b'\x08\x07\x00\x0F'
            }

        self.__SetHelper('AspectRatio', States[value], value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'\x03\x01\x00\x04',
            'Off': b'\x03\x01\x01\x05'
            }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', b'\x03\x03\x00\x06', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            0x00: 'On',
            0x01: 'Off'
        }

        self.WriteStatus('AudioMute', States[ord(match.group(1))], None)

    def SetInput(self, value, qualifier):

        States = {
            'VGA': b'\x02\x03\x00\x05',
            'HDMI 1': b'\x02\x06\x00\x08',
            'HDMI 2': b'\x02\x07\x00\x09',
            'HDMI 3': b'\x02\x05\x00\x07',
            'PC': b'\x02\x08\x00\x0A',
            'Android': b'\x02\x0A\x00\x0C',
            'Android +': b'\x02\x0E\x00\x10',
            'DisplayPort': b'\x02\x11\x00\x13'
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', b'\x02\x00\x00\x02', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            0x03: 'VGA',
            0x06: 'HDMI 1',
            0x07: 'HDMI 2',
            0x05: 'HDMI 3',
            0x08: 'PC',
            0x0A: 'Android',
            0x0E: 'Android +',
            0x11: 'DisplayPort'
        }

        self.WriteStatus('Input', States[ord(match.group(1))], None)

    def SetPCPower(self, value, qualifier):

        States = {
            'On': b'\x09\x01\x00\x0A',
            'Off': b'\x09\x00\x00\x09',
        }

        self.__SetHelper('PCPower', States[value], value, qualifier)

    def UpdatePCPower(self, value, qualifier):
        self.__UpdateHelper('PCPower', b'\x09\x02\x00\x0B', value, qualifier)

    def __MatchPCPower(self, match, tag):

        States = {
            0x00: 'On',
            0x01: 'Off',
            0x02: 'Sleep',
            0x03: 'Hibernate'
        }

        self.WriteStatus('PCPower', States[ord(match.group(1))], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x01\x00\x00\x01',
            'Off': b'\x01\x01\x00\x02'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', b'\x01\x02\x00\x03', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            0x00: 'On',
            0x01: 'Off'
        }

        self.WriteStatus('Power', States[ord(match.group(1))], None)

    def SetChannel(self, value, qualifier):

        States = {
            'Up': 0x02,
            'Down': 0x09
        }

        self.__SetHelper('Channel', bytes([7, States[value], 0, States[value] + 7]), value, qualifier)

    def SetKeypad(self, value, qualifier):

        States = {
            '0': 0x1B,
            '1': 0x00,
            '2': 0x10,
            '3': 0x11,
            '4': 0x13,
            '5': 0x14,
            '6': 0x15,
            '7': 0x17,
            '8': 0x18,
            '9': 0x19
        }

        self.__SetHelper('Keypad', bytes([7, States[value], 0, States[value] + 7]), value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Home': 0x48,
            'Menu': 0x0D,
            'Delete': 0x40,
            'Up': 0x47,
            'Down': 0x4D,
            'Left': 0x49,
            'Right': 0x4B,
            'Enter': 0x4A,
            'Back': 0x0A,
        }

        self.__SetHelper('MenuNavigation', bytes([7, States[value], 0, States[value] + 7]), value, qualifier)

    def SetRemoteControl(self, value, qualifier):

        States = {
            'Windows': 0x0B,
            'Space': 0x46,
            'Alt + Tab': 0x1D,
            'Alt + F4': 0x1F,
            'Display': 0x1C,
            'Refresh': 0x4C,
            'Input': 0x07,
            'Page Up': 0x42,
            'Page Down': 0x0F,
            'F1': 0x45,
            'F2': 0x12,
            'F3': 0x51,
            'F4': 0x5B,
            'F5': 0x44,
            'F6': 0x50,
            'F7': 0x43,
            'F8': 0x1A,
            'F9': 0x04,
            'F10': 0x59,
            'F11': 0x57,
            'F12': 0x08,
            'Red': 0x0C,
            'Green': 0x64,
            'Yellow': 0x5E,
            'Blue': 0x5F,
            'Energy': 0x4E,
            'Point': 0x06,
        }

        self.__SetHelper('RemoteControl', bytes([7, States[value], 0, States[value] + 7]), value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', bytes([3, 0, value, value + 3]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', b'\x03\x02\x00\x05', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', ord(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(b'\xAA\xBB\xCC' + commandstring + b'\xDD\xEE\xFF')

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

            self.Send(b'\xAA\xBB\xCC' + commandstring + b'\xDD\xEE\xFF')

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
