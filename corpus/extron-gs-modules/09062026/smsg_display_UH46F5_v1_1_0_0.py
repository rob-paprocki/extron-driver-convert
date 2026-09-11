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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'ScreenSize': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallSize': {'Parameters': ['Device ID','Row','Column'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x18([\x01\x04\x31\x0B])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x14([\x14\x18\x0C\x20\x1F\x21\x22\x23\x24\x25])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x11([\x01\x00])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x5D([\x01\x00])[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x19([\x00-\xFF])[\x00-\xFF]'), self.__MatchScreenSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x84([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\\x5C([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x04\x41\x89([\x11-\xF6])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xE0])[\x03\x04]\x4E([\x11\x12\x14\x18\x19\x3D\\x5C\\x5D\x84\x89])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    def idCheck(self, DeviceID):
        if DeviceID == 'Broadcast':
            return b'\xfe'
        elif 0 <= int(DeviceID) <= 224:
            return pack('B', int(DeviceID))
        else:
            self.Discard('Invalid Command')
    
    def calcChecksum(self, command):
        cks = 0
        for i in command[1:]:
            cks += i
        return pack('B',cks & 255)

    def SetAspectRatio(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])       
        ValueStateValues = {
            '16:9' : b'\x01', 
            'Zoom' : b'\x04', 
            'Wide Zoom' : b'\x31', 
            '4:3' : b'\x0B'
        }

        if DeviceID:
            AspectRatioCmdString = b'\xAA\x18' + DeviceID + b'\x01' + ValueStateValues[value]
            AspectRatioCmdString = AspectRatioCmdString + self.calcChecksum(AspectRatioCmdString)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
       
        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            AspectRatioCmdString = b'\xAA\x18' + DeviceID + b'\x00'
            AspectRatioCmdString = AspectRatioCmdString + self.calcChecksum(AspectRatioCmdString)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        
        value = {
            0x01 : '16:9', 
            0x04 : 'Zoom', 
            0x31 : 'Wide Zoom', 
            0x0B : '4:3'
        }[ord(match.group(2))]
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAutoImage(self, value, qualifier):
       
        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            AutoImageCmdString = b'\xAA\x3D' + DeviceID + b'\x01\x00'
            AutoImageCmdString = AutoImageCmdString + self.calcChecksum(AutoImageCmdString)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        if DeviceID:
            ExecutiveModeCmdString = b'\xAA\x5D' + DeviceID + b'\x01' + ValueStateValues[value]
            ExecutiveModeCmdString = ExecutiveModeCmdString + self.calcChecksum(ExecutiveModeCmdString)
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            ExecutiveModeCmdString = b'\xAA\x5D' + DeviceID + b'\x00'
            ExecutiveModeCmdString = ExecutiveModeCmdString + self.calcChecksum(ExecutiveModeCmdString)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        
        ValueStateValues = {
            'PC'           : b'\x14', 
            'DVI'          : b'\x18', 
            'Input Source' : b'\x0C', 
            'MagicInfo'    : b'\x20', 
            'HDMI 1'       : b'\x21', 
            'HDMI 2'       : b'\x23', 
            'DisplayPort'  : b'\x25'
        }

        if DeviceID:
            InputCmdString = b'\xAA\x14' + DeviceID + b'\x01' + ValueStateValues[value]
            InputCmdString = InputCmdString + self.calcChecksum(InputCmdString)
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            InputCmdString = b'\xAA\x14' + DeviceID + b'\x00'
            InputCmdString = InputCmdString + self.calcChecksum(InputCmdString)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = {
            0x14 : 'PC', 
            0x18 : 'DVI', 
            0x0C : 'Input Source', 
            0x20 : 'MagicInfo', 
            0x1F : 'DVI_Video', 
            0x21 : 'HDMI 1', 
            0x22 : 'HDMI 1_PC', 
            0x23 : 'HDMI 2', 
            0x24 : 'HDMI 2_PC', 
            0x25 : 'DisplayPort'
        }[ord(match.group(2))]
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        self.WriteStatus('Input', value, qualifier)

    def SetPower(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }


        if DeviceID:
            PowerCmdString = b'\xAA\x11' + DeviceID + b'\x01' + ValueStateValues[value]
            PowerCmdString = PowerCmdString + self.calcChecksum(PowerCmdString)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            PowerCmdString = b'\xAA\x11' + DeviceID + b'\x00'
            PowerCmdString = PowerCmdString + self.calcChecksum(PowerCmdString)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def UpdateScreenSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            ScreenSizeCmdString = b'\xAA\x19' + DeviceID + b'\x00'
            ScreenSizeCmdString = ScreenSizeCmdString + self.calcChecksum(ScreenSizeCmdString)
            self.__UpdateHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)

    def __MatchScreenSize(self, match, tag):
        
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        value = ord(match.group(2))
        self.WriteStatus('ScreenSize', value, qualifier)

    def SetVideoWall(self, value, qualifier):
        
        DeviceID = self.idCheck(qualifier['Device ID'])
        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        if DeviceID:
            VideoWallCmdString = b'\xAA\x84' + DeviceID + b'\x01' + ValueStateValues[value]
            VideoWallCmdString = VideoWallCmdString + self.calcChecksum(VideoWallCmdString)
            self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallCmdString = b'\xAA\x84' + DeviceID + b'\x00'
            VideoWallCmdString = VideoWallCmdString + self.calcChecksum(VideoWallCmdString)
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        value = {
            0x01 : 'On', 
            0x00 : 'Off'
        }[ord(match.group(2))]
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        self.WriteStatus('VideoWall', value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        ValueStateValues = {
            'Full' : b'\x01', 
            'Natural' : b'\x00'
        }

        if DeviceID:
            VideoWallModeCmdString = b'\xAA\x5C' + DeviceID + b'\x01' + ValueStateValues[value]
            VideoWallModeCmdString = VideoWallModeCmdString + self.calcChecksum(VideoWallModeCmdString)
            self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallModeCmdString = b'\xAA\x5C' + DeviceID + b'\x00'
            VideoWallModeCmdString = VideoWallModeCmdString + self.calcChecksum(VideoWallModeCmdString)
            self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        
        ValueStateValues = {
            '\x01' : 'Full', 
            '\x00' : 'Natural'
        }

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoWallMode', value, qualifier)

    def SetVideoWallSize(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])

        row = {
            '1':  0x10,'2':  0x20,'3':  0x30,'4':  0x40,'5':  0x50,
            '6':  0x60,'7':  0x70,'8':  0x80,'9':  0x90,'10': 0xA0,
            '11': 0xB0,'12': 0xC0,'13': 0xD0,'14': 0xE0,'15': 0xF0
        }[qualifier['Row']]        
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < displayNum <= 100 and DeviceID:
            if row <= 0x60 and column <= 15 and displayNum <= 90:
                Valid = True
            elif row <= 0x70 and column < 15 and displayNum <= 98:
                Valid = True
            elif row <= 0x80 and column < 13 and displayNum <= 96:
                Valid = True
            elif row <= 0x90 and column < 12 and displayNum <= 99:
                Valid = True
            elif row <= 0xA0 and column < 11:
                Valid = True
            elif row <= 0xB0 and column < 10 and displayNum <= 99:
                Valid = True
            elif row <= 0xC0 and column < 9 and displayNum <= 96:
                Valid = True
            elif row <= 0xD0 and column < 8 and displayNum <= 91:
                Valid = True
            elif row <= 0xE0 and column < 8 and displayNum <= 98:
                Valid = True
            elif row <= 0xF0 and column < 7 and displayNum <= 90:
                Valid = True
            else:
                Valid = False
            if Valid:
                VideoWallSizeCmdString = b'\xAA\x89' + DeviceID + b'\x02' + pack('B', row + column) + pack('B',displayNum)
                VideoWallSizeCmdString = VideoWallSizeCmdString + self.calcChecksum(VideoWallSizeCmdString)
                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):
        
        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID:
            VideoWallSizeCmdString = b'\xAA\x89' + DeviceID + b'\x00'
            VideoWallSizeCmdString = VideoWallSizeCmdString + self.calcChecksum(VideoWallSizeCmdString)
            self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        rowXcol = unpack('B',match.group(2))[0]
        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        qualifier['Column'] = str(rowXcol % 16)
        qualifier['Row'] = str(rowXcol // 16)
        value = str(unpack('B', match.group(3))[0])
        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if 0 <= value <= 100 and DeviceID:
            VolumeCmdString = b'\xAA\x12' + DeviceID + b'\x01' + pack('B',value)
            VolumeCmdString = VolumeCmdString + self.calcChecksum(VolumeCmdString)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID: 
            VolumeCmdString = b'\xAA\x12' + DeviceID + b'\x00'
            VolumeCmdString = VolumeCmdString + self.calcChecksum(VolumeCmdString)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        qualifier = {}
        qualifier['Device ID'] = str(unpack('B',match.group(1))[0])
        value = unpack('B',match.group(2))[0]
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or (qualifier and qualifier['Device ID'] == 'Broadcast') or self.DeviceID == 254:
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
        error = {
            b'\x11' : 'Power',
            b'\x12' : 'Volume',
            b'\x14' : 'Input',
            b'\x18' : 'AspectRatio',
            b'\x19' : 'ScreenSize',
            b'\x3D' : 'AutoImage',
            b'\x5C' : 'VideoWallMode',
            b'\x5D' : 'ExecutiveMode',
            b'\x84' : 'VideoWall',            
            b'\x89' : 'VideoWallSize', 
        }[match.group(2)]

        self.Error(['Device ID: {0}, Command: {1}, Error Code: {2}'.format(ord(match.group(1)), error, match.group(3).decode(encoding='iso-8859-1'))])

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