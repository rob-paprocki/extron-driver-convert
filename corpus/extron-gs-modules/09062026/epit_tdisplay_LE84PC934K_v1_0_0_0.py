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
        self.__DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenSize': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False' and self.__DeviceID != 0:
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9A', b'\x17(\x00|\x01)\x8A'])), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9A', b'\x15([\x01\x03\x14\x24\x34\x05\x06\x07\x09\x0B])\x8A'])), self.__MatchInput, None)
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9A', b'\x14(\x00|\x01)\x8A'])), self.__MatchMute, None)
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9A', b'\x11(\x00|\x01)\x8A'])), self.__MatchPower, None)
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9A', b'\x13([\x00-\x64])\x8A'])), self.__MatchVolume, None)
            self.AddMatchString(re.compile(self.__DeviceID.to_bytes(1, 'big').join([b'\xA9N', b'([\x17\x15\x14\x11\x13\x16])([\x00-\xFF])\x8A'])), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self.__DeviceID = 0
        elif (0 <= int(value) <= 255) and int(value) not in {138, 168}:
            self.__DeviceID = int(value)
        else:
            print('Device ID parameter should be set to Broadcast or in range 1 - 255, excluding numbers 138 and 168')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }
        ExecutiveModeCmdString = pack('>5B', 0xA9, 0x17, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = pack('>5B', 0xA9, 0x17, self.__DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = pack('>5B', 0xA9, 0x16, self.__DeviceID, 0xB8, 0x8A)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': 1,
            'Component': 3,
            'VGA 1': 0x14,
            'VGA 2': 0x24,
            'VGA 3': 0x34,
            'HDMI 1': 5,
            'HDMI 2': 6,
            'HDMI 3': 7,
            'Inside PC': 9,
            'USB': 0x0B
        }
        InputCmdString = pack('>5B', 0xA9, 0x15, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('>5B', 0xA9, 0x15, self.__DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x01': 'AV',
            b'\x03': 'Component',
            b'\x14': 'VGA 1',
            b'\x24': 'VGA 2',
            b'\x34': 'VGA 3',
            b'\x05': 'HDMI 1',
            b'\x06': 'HDMI 2',
            b'\x07': 'HDMI 3',
            b'\x09': 'Inside PC',
            b'\x0B': 'USB'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 0xD9,
            '1': 0x95,
            '2': 0x99,
            '3': 0x9D,
            '4': 0xD6,
            '5': 0xDA,
            '6': 0xDE,
            '7': 0x96,
            '8': 0x9A,
            '9': 0x9E,
        }
        KeypadCmdString = pack('>5B', 0xA9, 0x16, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x84,
            'Up': 0x92,
            'Down': 0xD8,
            'Right': 0x9F,
            'Left': 0x97,
            'Enter': 0x9B,
            'Exit': 0xD4,
            'Home': 0xBC,
            'Red': 0xB2,
            'Green': 0xB3,
            'Yellow': 0xB4,
            'Blue': 0xB5,
            'Info': 0xB7
        }
        MenuNavigationCmdString = pack('>5B', 0xA9, 0x16, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }
        MuteCmdString = pack('>5B', 0xA9, 0x14, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = pack('>5B', 0xA9, 0x14, self.__DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }
        PowerCmdString = pack('>5B', 0xA9, 0x11, self.__DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('>5B', 0xA9, 0x11, self.__DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetScreenSize(self, value, qualifier):

        ScreenSizeCmdString = pack('>5B', 0xA9, 0x16, self.__DeviceID, 0x81, 0x8A)
        self.__SetHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('>5B', 0xA9, 0x13, self.__DeviceID, value, 0x8A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('>5B', 0xA9, 0x13, self.__DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1)[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.__DeviceID == 0:
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

        Commands = {
            b'\x17' : 'Executive Mode',
            b'\x15' : 'Input',
            b'\x14' : 'Mute',
            b'\x11' : 'Power',
            b'\x13' : 'Volume',
            b'\x16' : 'Remote Emulation'
        }
        Errors = {
            b'\x01' : 'Invalid Command',
            b'\x02' : 'Invalid Data'
        }
        print('{}: {}'.format(Commands[match.group(1)],Errors.get(match.group(2),'Unknown Error')))

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
