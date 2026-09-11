from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = 0

        self.Models = {
            'QM43R': self.smsg_10_4337_others,
            'QM49R': self.smsg_10_4337_others,
            'QM55R': self.smsg_10_4337_others,
            'QM65R': self.smsg_10_4337_others,
            'QM75R': self.smsg_10_4337_others,
            'QM32R': self.smsg_10_4337_32,
            'LH32QMREBGCXXL': self.smsg_10_4337_32,
            'LH43QMREBGCXXL': self.smsg_10_4337_others,
            'LH49QMREBGCXXL': self.smsg_10_4337_others,
            'LH55QMREBGCXXL': self.smsg_10_4337_others,
            'LH65QMREBGCXXL': self.smsg_10_4337_others,
            'LH75QMREBGCXXL': self.smsg_10_4337_others,
            'LH85QMREBGCXXL': self.smsg_10_4337_others,
            'QM85R': self.smsg_10_4337_others,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'MasterPower': {'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'SafetyLock': {'Parameters': ['Device ID'], 'Status': {}},
            'ScreenMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallSize': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False' and self._DeviceID != 254:
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x13([\x00\x01])[\x00-\xFF]'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x11([\x00\x01])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x5D([\x00\x01])[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x18([\x01\x04\x0B\x31])[\x00-\xFF]'), self.__MatchScreenMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x84([\x00\x01])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\\x5C([\x00\x01])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x04\x41\x89([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x41\x12([\x00-\xFF])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        elif 0 <= int(value) <= 224:
            self._DeviceID = int(value)

    def checksum(self, cmd):
        return cmd + pack('>B', sum(cmd[1:]) & 0xFF)

    def idCheck(self, DeviceID):
        try:
            if DeviceID == 'Broadcast':
                return 0xFE
            elif 0 <= int(DeviceID) <= 224:
                return int(DeviceID)
            else:
                return None
        except ValueError:
            return None

    def SetAudioMute(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            AudioMuteCmdString = self.checksum(pack('>BBBBB', 0xAA, 0xB0, DeviceID, 0x01, 0x0F))
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in self.SetInput_ValueStateValues:
            InputCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x14, DeviceID, 0x01, self.SetInput_ValueStateValues[value]))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            InputCmdString = self.checksum(pack('>BBBB', 0xAA, 0x14, DeviceID, 0x00))
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }

        value = self.MatchInput_ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def UpdateMasterPower(self, value, qualifier):

        cks = (0x11 + self._DeviceID) & 0xFF
        self.__UpdateHelper('MasterPower', bytes([0xAA, 0x11, self._DeviceID, 0x00, cks]), value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            MuteCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x13, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            MuteCmdString = self.checksum(pack('>BBBB', 0xAA, 0x13, DeviceID, 0x00))
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            PowerCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x11, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            PowerCmdString = self.checksum(pack('>BBBB', 0xAA, 0x11, DeviceID, 0x00))
            if DeviceID != self._DeviceID:
                self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        DeviceID = match.group(1)[0]
        qualifier = {
            'Device ID': str(DeviceID)
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def SetSafetyLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            SafetyLockCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x5D, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSafetyLock')

    def UpdateSafetyLock(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            SafetyLockCmdString = self.checksum(pack('>BBBB', 0xAA, 0x5D, DeviceID, 0x00))
            self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSafetyLock')

    def __MatchSafetyLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SafetyLock', value, qualifier)

    def SetScreenMode(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x01,
            'Zoom': 0x04,
            '4:3': 0x0B,
            'Wide Zoom': 0x31
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            ScreenModeCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x18, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenMode')

    def UpdateScreenMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            ScreenModeCmdString = self.checksum(pack('>BBBB', 0xAA, 0x18, DeviceID, 0x00))
            self.__UpdateHelper('ScreenMode', ScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScreenMode')

    def __MatchScreenMode(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x0B': '4:3',
            '\x31': 'Wide Zoom'
        }

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ScreenMode', value, qualifier)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            VideoWallCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x84, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWall')

    def UpdateVideoWall(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            VideoWallCmdString = self.checksum(pack('>BBBB', 0xAA, 0x84, DeviceID, 0x00))
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWall')

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoWall', value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': 0x01,
            'Natural': 0x00
        }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            VideoWallModeCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x5C, DeviceID, 0x01, ValueStateValues[value]))
            self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallMode')

    def UpdateVideoWallMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            VideoWallModeCmdString = self.checksum(pack('>BBBB', 0xAA, 0x5C, DeviceID, 0x00))
            self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallMode')

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoWallMode', value, qualifier)

    def SetVideoWallSize(self, value, qualifier):

        horizontal = int(qualifier['Row'])
        vertical = int(qualifier['Column'])
        val = int(value)
        DeviceID = self.idCheck(qualifier['Device ID'])

        if all([DeviceID is not None,
                1 <= horizontal <= 10,
                1 <= vertical <= 10,
                1 <= val <= 100,
                val <= horizontal * vertical]):
            position = horizontal * 16 + vertical
            VideoWallSizeCmdString = self.checksum(pack('>BBBBBB', 0xAA, 0x89, DeviceID, 0x02, position, val))
            self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            VideoWallSizeCmdString = self.checksum(pack('>BBBB', 0xAA, 0x89, DeviceID, 0x00))
            self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallSize')

    def __MatchVideoWallSize(self, match, tag):

        position = unpack('B', match.group(2))[0]
        verticalPosition = str(position % 16)
        horizontalPosition = str(position // 16)

        qualifier = {
            'Device ID': str(match.group(1)[0]),
            'Row': horizontalPosition,
            'Column': verticalPosition
        }
        value = str(match.group(3)[0])
        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and 0 <= value <= 100:
            VolumeCmdString = self.checksum(pack('>BBBBB', 0xAA, 0x12, DeviceID, 0x01, value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None:
            VolumeCmdString = self.checksum(pack('>BBBB', 0xAA, 0x12, DeviceID, 0x00))
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {
            'Device ID': str(match.group(1)[0])
        }

        value = match.group(2)[0]
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 254 or (qualifier and qualifier['Device ID'] == 'Broadcast'):
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

        error_map = {
            b'\xB0': 'Audio Mute',
            b'\x14': 'Input',
            b'\x13': 'Mute',
            b'\x11': 'Power',
            b'\x18': 'Screen Mode',
            b'\x5D': 'Safety Lock',
            b'\x84': 'Video Wall',
            b'\x5C': 'Video Wall Mode',
            b'\x89': 'Video Wall Size',
            b'\x12': 'Volume'
        }

        error = match.group(2)

        if error in error_map:
            self.Error(['Device ID: {}. An error occurred: {} with value {}.'.format(match.group(1)[0], error_map[error], match.group(3)[0])])
        else:
            self.Error(['Device ID: {}. An error occurred: Unknown: {}'.format(match.group(1)[0], match.group(3)[0])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False


    def smsg_10_4337_others(self):

        self.SetInput_ValueStateValues = {
            'DVI':              0x18,
            'MagicInfo':        0x20,
            'HDMI 1':           0x21,
            'HDMI 2':           0x23,
            'DisplayPort':      0x25,
            'MagicInfo S':      0x60
        }

        self.MatchInput_ValueStateValues = {
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x1F': 'DVI Video',
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort',
            '\x60': 'MagicInfo S'
        }

        self.AddMatchString(re.compile('\xAA\xFF([\x00-\xFF])\x03\x41\x14([{}])[\x00-\xFF]'.format(''.join(self.MatchInput_ValueStateValues.keys())).encode(encoding='iso-8859-1')), self.__MatchInput, None)



    def smsg_10_4337_32(self):
        self.SetInput_ValueStateValues = {
            'HDMI 1':           0x21,
            'HDMI 2':           0x23,
            'DisplayPort':      0x25,
            'MagicInfo S':      0x60
        }

        self.MatchInput_ValueStateValues = {
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort',
            '\x60': 'MagicInfo S'
        }

        self.AddMatchString(re.compile('\xAA\xFF([\x00-\xFF])\x03\x41\x14([{}])[\x00-\xFF]'.format(''.join(self.MatchInput_ValueStateValues.keys())).encode(encoding='iso-8859-1')), self.__MatchInput, None)


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