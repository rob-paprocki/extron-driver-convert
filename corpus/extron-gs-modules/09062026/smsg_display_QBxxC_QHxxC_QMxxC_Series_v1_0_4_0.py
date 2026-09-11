from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

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
        self._DeviceID = 0
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False' and self._DeviceID != 254:
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x15([\x10\x18\x20\x21\x22])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x13([\x01\x00])[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x5D([\x01\x00])[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x14([\x20\x21\x22\x23\x24\x25\x31\x32])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x11([\x01\x00])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\xF9([\x01\x00])[\x00-\xFF]'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        elif 0 <= int(value) <= 224:
            self._DeviceID = int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x10,
            '4:3': 0x18,
            'Original Ratio': 0x20,
            '21:9': 0x21,
            'Custom': 0x22
            }

        if value in ValueStateValues:
            cks = int(hex(0x15 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x15, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        cks = int(hex(0x15 + self._DeviceID)[-2:], 16)
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x15, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x10' : '16:9',
            '\x18' : '4:3',
            '\x20' : 'Original Ratio',
            '\x21' : '21:9',
            '\x22' : 'Custom'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01,
            'Off' : 0x00
        }

        if value in ValueStateValues:
            cks = int(hex(0x13 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        cks = int(hex(0x13 + self._DeviceID)[-2:], 16)
        AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
        }

        if value in ValueStateValues:
            cks = int(hex(0x5D + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            ExecutiveModeCmdString = pack('>BBBBBB', 0xAA, 0x5D, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        cks = int(hex(0x5D + self._DeviceID)[-2:], 16)
        ExecutiveModeCmdString = pack('>BBBBB', 0xAA, 0x5D, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'MagicInfo':    0x20,
            'HDMI 1':       0x21,
            'HDMI 2':       0x23,
            'DisplayPort':  0x25,
            'HDMI 3':       0x31
            }

        if value in ValueStateValues:
            cks = int(hex(0x14 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        cks = int(hex(0x14 + self._DeviceID)[-2:], 16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x20': 'MagicInfo',
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort',
            '\x31': 'HDMI 3',
            '\x32': 'HDMI 3 PC'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'      : 0x1A,
            'Exit'      : 0x2D,
            'Return'    : 0x58,
            'Up'        : 0x60,
            'Down'      : 0x61,
            'Right'     : 0x62,
            'Left'      : 0x65,
            'Enter'     : 0x68
            }

        if value in ValueStateValues:
            cks = int(hex(0xB0 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            MenuNavigationCmdString = pack('>BBBBBB', 0xAA, 0xB0, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
        }

        if value in ValueStateValues:
            cks = int(hex(0x11 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        cks = int(hex(0x11 + self._DeviceID)[-2:], 16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
            }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01,
            'Off' : 0x00
        }

        if value in ValueStateValues:
            cks = int(hex(0xF9 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
            VideoMuteCmdString = pack('>BBBBBB', 0xAA, 0xF9, self._DeviceID, 0x01, ValueStateValues[value], cks)
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        cks = int(hex(0xF9 + self._DeviceID)[-2:], 16)
        VideoMuteCmdString = pack('>BBBBB', 0xAA, 0xF9, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            cks = int(hex(0x12 + self._DeviceID + 0x01 + value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self._DeviceID, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        cks = int(hex(0x12 + self._DeviceID)[-2:], 16)
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int.from_bytes(match.group(1), byteorder='big')
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 254:
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

        DEVICE_ERROR_CODES = {
            b'\x15': 'Aspect Ratio',
            b'\x13': 'Audio Mute',
            b'\x14': 'Input',
            b'\x11': 'Power',
            b'\x5D': 'Executive Mode',
            b'\xF9': 'Video Mute',
            b'\x12': 'Volume'
        }

        if match.group(1) in DEVICE_ERROR_CODES:
            errorstring = 'Command: {0}, Error Code: {1}'.format(DEVICE_ERROR_CODES[match.group(1)], ord(match.group(2)))
        else:
            errorstring = 'Command: {0}, Error Code: {1}'.format('Unknown', ord(match.group(2)))
        self.Error([errorstring])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()