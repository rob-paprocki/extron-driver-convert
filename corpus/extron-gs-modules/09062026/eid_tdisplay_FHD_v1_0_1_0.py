from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack

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
            'AudioMute': {'Status': {}},
            'BLU': {'Status': {}},
            'Channel': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Color': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x14(\x01|\x00)\x8A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x12(\x01|\x00)\x8A'), self.__MatchBLU, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x15(\x01|\x03|\x04|\x05|\x06|\x08|\x09|\x0B)\x8A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x11(\x01|\x00)\x8A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x13([\x00-\x64])\x8A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xA9\x4E[\x00-\x80]([\x11-\x16])([\x01-\xFF])\x8A'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceID = value
        if DeviceID == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(DeviceID) <= 128:
            self._DeviceID = int(DeviceID)
        else:
            print('Device ID Parameter is set to wrong value.')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('<5B', 0xA9, 0x14, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = pack('<5B', 0xA9, 0x14, self._DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self._DeviceID == unpack('B',match.group(1))[0]:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, None)

    def SetBLU(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        BLUCmdString = pack('<5B', 0xA9, 0x12, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('BLU', BLUCmdString, value, qualifier)

    def UpdateBLU(self, value, qualifier):

        BLUCmdString = pack('<5B', 0xA9, 0x12, self._DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('BLU', BLUCmdString, value, qualifier)

    def __MatchBLU(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self._DeviceID == unpack('B',match.group(1))[0]:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('BLU', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x80,
            'Down': 0x8E
        }

        ChannelCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, 0x82, 0x8A)
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Red': 0xB2,
            'Green': 0xB3,
            'Blue': 0xB5,
            'Yellow': 0xB4
        }

        ColorCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Color', ColorCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, 0xB8, 0x8A)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': 0x01,
            'Component': 0x03,
            'VGA': 0x04,
            'HDMI 1': 0x05,
            'HDMI 2': 0x06,
            'DisplayPort': 0x08,
            'Inside PC': 0x09,
            'USB': 0x0B
        }

        InputCmdString = pack('<5B', 0xA9, 0x15, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('<5B', 0xA9, 0x15, self._DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x01': 'AV',
            '\x03': 'Component',
            '\x04': 'VGA',
            '\x05': 'HDMI 1',
            '\x06': 'HDMI 2',
            '\x08': 'DisplayPort',
            '\x09': 'Inside PC',
            '\x0B': 'USB'
        }

        if self._DeviceID == unpack('B',match.group(1))[0]:
            value = ValueStateValues[match.group(2).decode()]
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
            '9': 0x9E
        }

        KeypadCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x8A,
            'Exit': 0xD4,
            'Up': 0x92,
            'Down': 0xD8,
            'Left': 0x97,
            'Right': 0x9F,
            'Enter': 0x9B
        }

        MenuNavigationCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeCmdString = pack('<5B', 0xA9, 0x16, self._DeviceID, 0xC3, 0x8A)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('<5B', 0xA9, 0x11, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('<5B', 0xA9, 0x11, self._DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self._DeviceID == unpack('B',match.group(1))[0]:

            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('<5B', 0xA9, 0x13, self._DeviceID, value, 0x8A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('<5B', 0xA9, 0x13, self._DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        if self._DeviceID == unpack('B',match.group(1))[0]:
            value = ord(match.group(2).decode())
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
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

        COMMAND_CODES = {
            '\x11': "Power",
            '\x12': "BLU",
            '\x13': "Volume",
            '\x14': "Audio Mute",
            '\x15': "Input",
            '\x16': "Remote Control Command"
            }

        ERROR_CODES = {
            1 : "Invalid Command",
            2 : "Invalid Data"
            }
        if unpack('B',match.group(2))[0] in ERROR_CODES:
            value = "Error occured with command: {}, Error: {}.".format(COMMAND_CODES[match.group(1).decode()], ERROR_CODES[unpack('B',match.group(2))[0]])
        else:
            value = "Error occured with command: {}, Error: Unknown.".format(COMMAND_CODES[match.group(1).decode()])
        
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
