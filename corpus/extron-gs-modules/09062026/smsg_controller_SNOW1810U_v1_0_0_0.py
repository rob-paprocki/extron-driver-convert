from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack

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
        self._DeviceID = 1
        self.Models = {}
        self._DeviceID = 1
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Blank': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallFormat': {'Status': {}},
            'VideoWallPosition': {'Parameters': ['Horizontal', 'Vertical'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\x14(\x21|\x23|\x25|\x60|\x65)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\x71(\x00|\x01|\x02|\x04|\x16)[\x00-\xFF]'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallFormat, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE1]\x04\x41\x89([\x00-\xFF])([\x00-\xE1])[\x00-\xFF]'), self.__MatchVideoWallPosition, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0xFE
        elif 1 <= int(value) <= 225:
            self._DeviceID = int(value)

    def SetBlank(self, value, qualifier):

        checksum = int(hex(0xB0 + self._DeviceID + 0x01 + 0x24)[-2:], 16)
        BlankCmdString = pack('>BBBBBB', 0xAA, 0xB0, self._DeviceID, 0x01, 0x24, checksum)
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)  

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'DisplayPort': 0x25,
            'MagicInfo S': 0x60,
            'URL Launcher': 0x63,  # Must be enabled within device menu
            'Web Browser': 0x65
        }

        checksum = int(hex(0x14 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)  # Query delay not needed, tested with the device

    def UpdateInput(self, value, qualifier):

        checksum = int(hex(0x14 + self._DeviceID)[-2:], 16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x21': 'HDMI 1',  # \xAA\xFF\x01\x03\x41\x14\x21\x7A
            b'\x23': 'HDMI 2',  # \xAA\xFF\x01\x03\x41\x14\x23\x7C
            b'\x25': 'DisplayPort',  # \xAA\xFF\x01\x03\x41\x14\x25\x7E
            b'\x60': 'MagicInfo S',  # \xAA\xFF\x01\x03\x41\x14\x60\xB9
            b'\x65': 'Web Browser'  # \xAA\xFF\x01\x03\x41\x14\x65\x79
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': 0x04,
            '2': 0x05,
            '3': 0x06,
            '4': 0x08,
            '5': 0x09,
            '6': 0x0A,
            '7': 0x0C,
            '8': 0x0D,
            '9': 0x0E,
            '0': 0x11
        }

        checksum = int(hex(0xB0 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        KeypadCmdString = pack('>BBBBBB', 0xAA, 0xB0, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)  # Query delay not needed, tested with the device

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x1A,
            'Up': 0x60,
            'Down': 0x61,
            'Left': 0x65,
            'Right': 0x62,
            'Enter': 0x68,
            'Return': 0x58,
            'Exit': 0x2D,
            'Home': 0x79
        }

        checksum = int(hex(0xB0 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        MenuNavigationCmdString = pack('>BBBBBB', 0xAA, 0xB0, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)  # Query delay not needed, tested with the device

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 0x00,
            'Live': 0x01,
            'Movie': 0x02,
            'Natural': 0x04,
            'Calibration': 0x16
        }

        checksum = int(hex(0x71 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        PictureModeCmdString = pack('>BBBBBB', 0xAA, 0x71, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        checksum = int(hex(0x71 + self._DeviceID)[-2:], 16)
        PictureModeCmdString = pack('>BBBBB', 0xAA, 0x71, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Dynamic',  # \xAA\xFF\x01\x03\x41\x71\x00\xB6
            b'\x01': 'Live',  # \xAA\xFF\x01\x03\x41\x71\x01\xB7
            b'\x02': 'Movie',  # \xAA\xFF\x01\x03\x41\x71\x02\xB8
            b'\x04': 'Natural',  # \xAA\xFF\x01\x03\x41\x71\x04\xBA
            b'\x16': 'Calibration'  # \xAA\xFF\x01\x03\x41\x71\x16\xCC
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = int(hex(0x11 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = int(hex(0x11 + self._DeviceID)[-2:], 16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',  # \xAA\xFF\x01\x03\x41\x11\x01\x56
            b'\x00': 'Off'  # \xAA\xFF\x01\x03\x41\x11\x00\x55
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = int(hex(0x5D + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        SafetyLockCmdString = pack('>BBBBBB', 0xAA, 0x5D, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        checksum = int(hex(0x5D + self._DeviceID)[-2:], 16)
        SafetyLockCmdString = pack('>BBBBB', 0xAA, 0x5D, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',  # \xAA\xFF\x01\x03\x41\x5D\x01\xA2
            b'\x00': 'Off'  # \xAA\xFF\x01\x03\x41\x5D\x00\xA1
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        checksum = int(hex(0x84 + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)  # Query delay needed based on testing with the device

    def UpdateVideoWall(self, value, qualifier):

        checksum = int(hex(0x84 + self._DeviceID)[-2:], 16)
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',  # \xAA\xFF\x01\x03\x41\x84\x01\xC9
            b'\x00': 'Off'  # \xAA\xFF\x01\x03\x41\x84\x00\xC8
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallFormat(self, value, qualifier):

        ValueStateValues = {
            'Full': 0x01,  # \xAA\xFF\x01\x03\x41\x5C\x01\xA1
            'Natural': 0x00  # \xAA\xFF\x01\x03\x41\x5C\x00\xA0
        }

        checksum = int(hex(0x5C + self._DeviceID + 0x01 + ValueStateValues[value])[-2:], 16)
        VideoWallFormatCmdString = pack('>BBBBBB', 0xAA, 0x5C, self._DeviceID, 0x01, ValueStateValues[value], checksum)
        self.__SetHelper('VideoWallFormat', VideoWallFormatCmdString, value, qualifier)  # Query delay needed based on testing with the device

    def UpdateVideoWallFormat(self, value, qualifier):

        checksum = int(hex(0x5C + self._DeviceID)[-2:], 16)
        VideoWallFormatCmdString = pack('>BBBBB', 0xAA, 0x5C, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallFormat', VideoWallFormatCmdString, value, qualifier)

    def __MatchVideoWallFormat(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Full',
            b'\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoWallFormat', value, None)

    def SetVideoWallPosition(self, value, qualifier):

        horizontal = int(qualifier['Horizontal'])
        vertical = int(qualifier['Vertical'])
        valueInt = int(value)

        if 1 <= valueInt <= 225 and 1 <= horizontal <= 15 and 1 <= vertical <= 15:
            if valueInt <= horizontal * vertical:  # Value must be less than the total number of squares since value is the position of the tile from left to right
                position = horizontal * 16 + vertical
                checksum = int(hex(0x89 + self._DeviceID + 0x02 + position + valueInt)[-2:], 16)
                VideoWallPositionCmdString = pack('>BBBBBBB', 0xAA, 0x89, self._DeviceID, 0x02, position, valueInt, checksum)
                self.__SetHelper('VideoWallPosition', VideoWallPositionCmdString, value, qualifier)  # Query delay needed based on testing with the device
            else:
                self.Discard('Invalid Command for SetVideoWallPosition')
        else:
            self.Discard('Invalid Command for SetVideoWallPosition')

    def UpdateVideoWallPosition(self, value, qualifier):

        checksum = int(hex(0x89 + self._DeviceID)[-2:], 16)
        VideoWallPositionCmdString = pack('>BBBBB', 0xAA, 0x89, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallPosition', VideoWallPositionCmdString, value, qualifier)

    def __MatchVideoWallPosition(self, match, tag):

        position = unpack('B', match.group(1))[0]
        verticalPosition = str(position % 16)
        horizontalPosition = str(position // 16)
        qualifier = {'Horizontal': horizontalPosition, 'Vertical': verticalPosition}
        value = str(unpack('B', match.group(2))[0])
        self.WriteStatus('VideoWallPosition', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0xFE:
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
            b'\x14' : 'Input',
            b'\x11' : 'Power',
            b'\x5D' : 'Safety Lock',
            b'\x84' : 'Video Wall',
            b'\x5C' : 'Video Wall Format',
            b'\x89' : 'Video Wall Position',
            b'\xB0' : 'Keypad / Menu Navigation / Blank'
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

