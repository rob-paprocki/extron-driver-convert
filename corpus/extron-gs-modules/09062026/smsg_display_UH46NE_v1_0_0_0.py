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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoAdjust': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'ScreenSize': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallSize': {'Parameters': ['Device ID', 'Columns', 'Rows'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFD])\x03A\x18([\x01\x04\x31\x0B])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x13([\x00\x01])[\x00-\xff]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x5d([\x01\x00])[\x00-\xff]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x14([\x18\x14\x21\x23\x25\x20])[\x00-\xff]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x11([\x01\x00])[\x00-\xff]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x19([\x00-\xff])[\x00-\xff]'), self.__MatchScreenSize, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x84([\x01\x00])[\x00-\xff]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\\\([\x01\x00])[\x00-\xff]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x04A\x89([\x00-\xff])([\x00-\xff])[\x00-\xff]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03A\x12([\x00-\x64])[\x00-\xff]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xaa\xff([\x00-\xfd])\x03N([\x00-\xff])([\x00-\xff])[\x00-\xff]'), self.__MatchError, None)


    def idCheck(self, DeviceID):
        try:
            if DeviceID == 'Broadcast':
                return b'\xfe'
            elif 0 <= int(DeviceID) <= 253:
                return pack('B', int(DeviceID))
            else:
                self.Discard('Invalid Command')
        except ValueError:
            self.Discard('Invalid Command')

    def calcChecksum(self, command):
        cks = 0
        for i in command[1:]:
            cks += i
        return pack('B', cks & 255)

    def SetAspectRatio(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            '16:9': b'\x01',
            'Zoom': b'\x04',
            'Wide Zoom': b'\x31',
            '4:3': b'\x0B'
        }

        AspectRatioCmdString = b'\xaa\x18' + DeviceID + b'\x01' + ValueStateValues[value]
        AspectRatioCmdString = AspectRatioCmdString + self.calcChecksum(AspectRatioCmdString)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            AspectRatioCmdString = b'\xaa\x18' + DeviceID + b'\x00'
            AspectRatioCmdString = AspectRatioCmdString + self.calcChecksum(AspectRatioCmdString)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x31': 'Wide Zoom',
            '\x0B': '4:3'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b'\xaa\x13' + DeviceID + b'\x01' + ValueStateValues[value]
        AudioMuteCmdString = AudioMuteCmdString + self.calcChecksum(AudioMuteCmdString)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        if DeviceID:
            AudioMuteCmdString = b'\xaa\x13' + DeviceID + b'\x00'
            AudioMuteCmdString = AudioMuteCmdString + self.calcChecksum(AudioMuteCmdString)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoAdjust(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        AutoAdjustCmdString = b'\xaa\x3d' + DeviceID + b'\x01\x00'
        AutoAdjustCmdString = AutoAdjustCmdString + self.calcChecksum(AutoAdjustCmdString)
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        ExecutiveModeCmdString = b'\xaa\x5d' + DeviceID + b'\x01' + ValueStateValues[value]
        ExecutiveModeCmdString = ExecutiveModeCmdString + self.calcChecksum(ExecutiveModeCmdString)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            ExecutiveModeCmdString = b'\xaa\x5d' + DeviceID + b'\x00'
            ExecutiveModeCmdString = ExecutiveModeCmdString + self.calcChecksum(ExecutiveModeCmdString)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            'PC': b'\x14',
            'DVI': b'\x18',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'DisplayPort': b'\x25',
            'MagicInfo': b'\x20'
        }

        InputCmdString = b'\xaa\x14' + DeviceID + b'\x01' + ValueStateValues[value]
        InputCmdString = InputCmdString + self.calcChecksum(InputCmdString)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            InputCmdString = b'\xaa\x14' + DeviceID + b'\x00'
            InputCmdString = InputCmdString + self.calcChecksum(InputCmdString)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x25': 'DisplayPort',
            '\x20': 'MagicInfo'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)


    def SetPower(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b'\xaa\x11' + DeviceID + b'\x01' + ValueStateValues[value]
        PowerCmdString = PowerCmdString + self.calcChecksum(PowerCmdString)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            PowerCmdString = b'\xaa\x11' + DeviceID + b'\x00'
            PowerCmdString = PowerCmdString + self.calcChecksum(PowerCmdString)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def SetScreenSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueConstraints = {
            'Min': 0,
            'Max': 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and DeviceID:
            ScreenSizeCmdString = b'\xaa\x19' + DeviceID + b'\x01' + pack('B', value)
            ScreenSizeCmdString = ScreenSizeCmdString + self.calcChecksum(ScreenSizeCmdString)
            self.__SetHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSize')

    def UpdateScreenSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            ScreenSizeCmdString = b'\xaa\x19' + DeviceID + b'\x00'
            ScreenSizeCmdString = ScreenSizeCmdString + self.calcChecksum(ScreenSizeCmdString)
            self.__UpdateHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)

    def __MatchScreenSize(self, match, tag):

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = unpack('B', match.group(2))[0]
        if 0 <= value <= 255:
            self.WriteStatus('ScreenSize', value, qualifier)

    def SetVideoWall(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoWallCmdString = b'\xaa\x84' + DeviceID + b'\x01' + ValueStateValues[value]
        VideoWallCmdString = VideoWallCmdString + self.calcChecksum(VideoWallCmdString)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallCmdString = b'\xaa\x84' + DeviceID + b'\x00'
            VideoWallCmdString = VideoWallCmdString + self.calcChecksum(VideoWallCmdString)
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoWall', value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            'Full': b'\x01',
            'Natural': b'\x00'
        }

        VideoWallModeCmdString = b'\xaa\x5c' + DeviceID + b'\x01' + ValueStateValues[value]
        VideoWallModeCmdString = VideoWallModeCmdString + self.calcChecksum(VideoWallModeCmdString)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallModeCmdString = b'\xaa\x5c' + DeviceID + b'\x00'
            VideoWallModeCmdString = VideoWallModeCmdString + self.calcChecksum(VideoWallModeCmdString)
            self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoWallMode', value, qualifier)

    def SetVideoWallSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        rows = int(qualifier['Rows'])
        columns = int(qualifier['Columns'])
        value = int(value)

        if 1 <= rows <= 15 and 1 <= columns <= 15 and 1 <= value <= 100:
            if (rows * columns) <= 100 and value <= (rows * columns):
                VideoWallSizeCmdString = b'\xaa\x89' + DeviceID + b'\x02' + pack('B', rows * 16 + columns) + pack('B', value)
                VideoWallSizeCmdString = VideoWallSizeCmdString + self.calcChecksum(VideoWallSizeCmdString)
                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallSizeCmdString = b'\xaa\x89' + DeviceID + b'\x00'
            VideoWallSizeCmdString = VideoWallSizeCmdString + self.calcChecksum(VideoWallSizeCmdString)
            self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        rowXcol = unpack('B', match.group(2))[0]
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        qualifier['Columns'] = str(rowXcol % 16)
        qualifier['Rows'] = str(rowXcol // 16)
        value = str(unpack('B', match.group(3))[0])
        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if 0 <= value <= 100:
            VolumeCmdString = b'\xaa\x12' + DeviceID + b'\x01' + pack('B', value)
            VolumeCmdString = VolumeCmdString + self.calcChecksum(VolumeCmdString)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VolumeCmdString = b'\xaa\x12' + DeviceID + b'\x00'
            VolumeCmdString = VolumeCmdString + self.calcChecksum(VolumeCmdString)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B', match.group(1))[0])
        value = unpack('B', match.group(2))[0]
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
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

        self.Error(['Error message: ' + str(match.group(3)[0]) + ', from device with ID: ' + str(match.group(1)[0])])

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

