from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self.DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAdjust': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PiPMode': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenSize': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Columns', 'Rows'], 'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x14(\x14|\x18|\x20|\x1F|\x21|\x22|\x25)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPiPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x19([\x00-\xFF])[\x00-\xFF]'), self.__MatchScreenSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x04A\x89([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03A\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFD]\x03N(\x18|\x5D|\x14|\x3C|\x11|\x19|\x84|\x5C|\x89|\x12)([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = pack('B', 0xFE)
        elif 1 <= int(value) <= 224:
            self._DeviceID = pack('B', int(value))

    def checksum(self, command):
        cks = 0
        for i in command[1:]:
            cks += i
        return pack('B', cks & 255)

    def SetAutoAdjust(self, value, qualifier):

        AutoAdjustCmdString = b'\xAA\x3D' + self._DeviceID + b'\x01\x00'
        AutoAdjustCmdString = AutoAdjustCmdString + self.checksum(AutoAdjustCmdString)
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        ExecutiveModeCmdString = b'\xAA\x5D' + self._DeviceID + b'\x01' + ValueStateValues[value]
        ExecutiveModeCmdString = ExecutiveModeCmdString + self.checksum(ExecutiveModeCmdString)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\xAA\x5D' + self._DeviceID + b'\x00'
        ExecutiveModeCmdString = ExecutiveModeCmdString + self.checksum(ExecutiveModeCmdString)
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
            'PC': b'\x14',
            'DVI': b'\x18',
            'MagicInfo': b'\x0C',
            'HDMI': b'\x21',
            'DisplayPort': b'\x25'
        }

        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x01' + ValueStateValues[value]
        InputCmdString = InputCmdString + self.checksum(InputCmdString)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xAA\x14' + self._DeviceID + b'\x00'
        InputCmdString = InputCmdString + self.checksum(InputCmdString)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x1F': 'DVI (Video)',
            '\x21': 'HDMI',
            '\x22': 'HDMI (PC)',
            '\x25': 'DisplayPort'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPiPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PiPModeCmdString = b'\xAA\x3C' + self._DeviceID + b'\x01' + ValueStateValues[value]
        PiPModeCmdString = PiPModeCmdString + self.checksum(PiPModeCmdString)
        self.__SetHelper('PiPMode', PiPModeCmdString, value, qualifier)

    def UpdatePiPMode(self, value, qualifier):

        PiPModeCmdString = b'\xAA\x3C' + self._DeviceID + b'\x00'
        PiPModeCmdString = PiPModeCmdString + self.checksum(PiPModeCmdString)
        self.__UpdateHelper('PiPMode', PiPModeCmdString, value, qualifier)

    def __MatchPiPMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PiPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b'\xAA\x11' + self._DeviceID + b'\x01' + ValueStateValues[value]
        PowerCmdString = PowerCmdString + self.checksum(PowerCmdString)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xAA\x11' + self._DeviceID + b'\x00'
        PowerCmdString = PowerCmdString + self.checksum(PowerCmdString)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetScreenSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ScreenSizeCmdString = b'\xAA\x19' + self._DeviceID + b'\x01' + pack('B', value)
            ScreenSizeCmdString = ScreenSizeCmdString + self.checksum(ScreenSizeCmdString)
            self.__SetHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScreenSize')

    def UpdateScreenSize(self, value, qualifier):

        ScreenSizeCmdString = b'\xAA\x19' + self._DeviceID + b'\x00'
        ScreenSizeCmdString = ScreenSizeCmdString + self.checksum(ScreenSizeCmdString)
        self.__UpdateHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)

    def __MatchScreenSize(self, match, tag):

        value = unpack('B', match.group(1))[0]
        if 0 <= value <= 255:
            self.WriteStatus('ScreenSize', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoWallCmdString = b'\xAA\x84' + self._DeviceID + b'\x01' + ValueStateValues[value]
        VideoWallCmdString = VideoWallCmdString + self.checksum(VideoWallCmdString)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        VideoWallCmdString = b'\xAA\x84' + self._DeviceID + b'\x00'
        VideoWallCmdString = VideoWallCmdString + self.checksum(VideoWallCmdString)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x01',
            'Natural': b'\x00'
        }

        VideoWallModeCmdString = b'\xAA\x5C' + self._DeviceID + b'\x01' + ValueStateValues[value]
        VideoWallModeCmdString = VideoWallModeCmdString + self.checksum(VideoWallModeCmdString)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        VideoWallModeCmdString = b'\xAA\x5C' + self._DeviceID + b'\x00'
        VideoWallModeCmdString = VideoWallModeCmdString + self.checksum(VideoWallModeCmdString)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        row = int(qualifier['Rows'])
        col = int(qualifier['Columns'])
        value = int(value)

        if 1 <= row <= 15 and 1 <= col <= 15 and 1 <= value <= 100:
            if (row * col) <= 100 and value <= (row * col):
                VideoWallSizeCmdString = b'\xAA\x89' + self._DeviceID + b'\x02' + pack('B', row * 16 + col) + pack('B', value)
                VideoWallSizeCmdString = VideoWallSizeCmdString + self.checksum(VideoWallSizeCmdString)

                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        VideoWallSizeCmdString = b'\xAA\x89' + self._DeviceID + b'\x00'
        VideoWallSizeCmdString = VideoWallSizeCmdString + self.checksum(VideoWallSizeCmdString)
        self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        rowXcol = unpack('B', match.group(1))[0]
        qualifier = {}
        qualifier['Columns'] = str(rowXcol % 16)
        qualifier['Rows'] = str(rowXcol // 16)
        value = str(unpack('B', match.group(2))[0])

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\xAA\x12' + self._DeviceID + b'\x01' + pack('B', value)
            VolumeCmdString = VolumeCmdString + self.checksum(VolumeCmdString)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xAA\x12' + self._DeviceID + b'\x00'
        VolumeCmdString = VolumeCmdString + self.checksum(VolumeCmdString)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('B', match.group(1))[0]
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
        print('Error message: ' + str(unpack('B', match.group(2))[0]) + ', from device with ID: ' + str(unpack('B', match.group(1))[0]))

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
