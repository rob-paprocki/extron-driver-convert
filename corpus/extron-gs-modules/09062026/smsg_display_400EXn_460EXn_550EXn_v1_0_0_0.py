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
            'AllKeysLock': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ErrorStatus': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'Volume': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Columns', 'Rows'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x77([\x00-\x01])[\x00-\xFF]'), self.__MatchAllKeysLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x15([\x00-\x31])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13([\x00-\x01])[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x08\x41\x0D([\x00-\x01]{6})[\x00-\xFF]'), self.__MatchErrorStatus, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x08|\x0C|\x14|\x20|\x21|\x22)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x70([\x00-\x01])[\x00-\xFF]'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5F([\x00-\x01])[\x00-\xFF]'), self.__MatchPanelLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11([\x00-\x01])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D([\x00-\x01])[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xff[\x00-\xFF]\x03A\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03A\\\(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x04A\x89([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        elif int(value) == 0:
            self._DeviceID = 255
        elif int(value) >= 0 and int(value) < 100:
            self._DeviceID = int(value)
        else:
            print('Module level parameter DeviceID set to an invalid value: {}'.format(value))

    def SetAllKeysLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        CKS = (0x78 + self._DeviceID + ValueStateValues[value]) & 0xff
        AllKeysLockCmdString = pack('>BBBBBB', 0xAA, 0x77, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('AllKeysLock', AllKeysLockCmdString, value, qualifier)

    def UpdateAllKeysLock(self, value, qualifier):

        CKS = (0x77 + self._DeviceID) & 0xff
        AllKeysLockCmdString = pack('>BBBBB', 0xAA, 0x77, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('AllKeysLock', AllKeysLockCmdString, value, qualifier)

    def __MatchAllKeysLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AllKeysLock', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9 (PC)': 0x10,
            '4:3 (PC)': 0x18,
            '16:9': 0x01,
            '4:3': 0x0B,
            'Auto Wide': 0x00,
            'Zoom': 0x04,
            'Zoom 1': 0x05,
            'Zoom 2': 0x06,
            'Just Scan': 0x09,
            'Wide Zoom': 0x31,
            'Wide Fit': 0x0C
        }
        CKS = (0x16 + self._DeviceID + ValueStateValues[value]) & 0xff
        AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x15, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CKS = (0x15 + self._DeviceID) & 0xff
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x15, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x10': '16:9 (PC)',
            '\x18': '4:3 (PC)',
            '\x01': '16:9',
            '\x0B': '4:3',
            '\x00': 'Auto Wide',
            '\x04': 'Zoom',
            '\x05': 'Zoom 1',
            '\x06': 'Zoom 2',
            '\x09': 'Just Scan',
            '\x31': 'Wide Zoom',
            '\x0C': 'Wide Fit'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off': 0x00,
            'On': 0x01
        }
        CKS = (0x14 + self._DeviceID + ValueStateValues[value]) & 0xff
        AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        CKS = (0x13 + self._DeviceID) & 0xff
        AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
           '\x00': 'Off',
           '\x01': 'On'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        CKS = (0x3E + self._DeviceID) & 0xff
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, CKS)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateErrorStatus(self, value, qualifier):

        CKS = (0x0d + self._DeviceID) & 0xff
        ErrorStatusCmdString = pack('>BBBBB', 0xAA, 0x0d, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)

    def __MatchErrorStatus(self, match, tag):

        ValueStateValues = {
            0: 'Lamp Error',
            1: 'Temperature Error',
            2: 'Bright Sensor Error',
            3: 'No Sync',
            4: 'Fan Error',
        }
        val = match.group(1).decode()
        errorString = val[0:4] + val[5:6]
        if errorString.count('\x01') == 0:
            value = 'No Errors'
        elif errorString.count('\x01') == 1:
            value = ValueStateValues[errorString.index('\x01')]
        else:
            value = 'Multiple Errors'
        self.WriteStatus('ErrorStatus', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'PC': 0x14,
            'HDMI': 0x21,
            'AV': 0x0C,
            'Component': 0x08,
            'MagicNet': 0x20,
        }

        CKS = (0x15 + self._DeviceID + ValueStateValues[value]) & 0xff
        InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CKS = (0x14 + self._DeviceID) & 0xff
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x14': 'PC',
            '\x21': 'HDMI',
            '\x22': 'HDMI',
            '\x0C': 'AV',
            '\x08': 'Component',
            '\x20': 'MagicNet',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        CKS = (0x71 + self._DeviceID + ValueStateValues[value]) & 0xff
        OnScreenDisplayCmdString = pack('>BBBBBB', 0xAA, 0x70, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        CKS = (0x70 + self._DeviceID) & 0xff
        OnScreenDisplayCmdString = pack('>BBBBB', 0xAA, 0x70, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPanelLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        CKS = (0x60 + self._DeviceID + ValueStateValues[value]) & 0xff
        PanelLockCmdString = pack('>BBBBBB', 0xAA, 0x5f, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('PanelLock', PanelLockCmdString, value, qualifier)

    def UpdatePanelLock(self, value, qualifier):

        CKS = (0x5f + self._DeviceID) & 0xff
        PanelLockCmdString = pack('>BBBBB', 0xAA, 0x5f, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('PanelLock', PanelLockCmdString, value, qualifier)

    def __MatchPanelLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PanelLock', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': 0x00,
            'On': 0x01
        }
        CKS = (0x12 + self._DeviceID + ValueStateValues[value]) & 0xff
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CKS = (0x11 + self._DeviceID) & 0xff
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        CKS = (0x5e + self._DeviceID + ValueStateValues[value]) & 0xff
        SafetyLockCmdString = pack('>BBBBBB', 0xAA, 0x5d, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        CKS = (0x5d + self._DeviceID) & 0xff
        SafetyLockCmdString = pack('>BBBBB', 0xAA, 0x5d, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        CKS = (0x85 + self._DeviceID + ValueStateValues[value]) & 0xff
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        CKS = (0x84 + self._DeviceID) & 0xff
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self._DeviceID, 0x00, CKS)
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
            'Full': 0x01,
            'Natural': 0x00
        }

        CKS = (0x5D + self._DeviceID + ValueStateValues[value]) & 0xff
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self._DeviceID, 0x01, ValueStateValues[value], CKS)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        CKS = (0x5C + self._DeviceID) & 0xff
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        rows = int(qualifier['Rows'])
        columns = int(qualifier['Columns'])
        value = int(value)

        if 1 <= rows <= 5 and 1 <= columns <= 5 and 1 <= value <= 25:
            if (rows * columns) <= 25 and value <= (rows * columns):
                CKS = (0x91 + self._DeviceID + rows + columns + value) & 0xff
                VideoWallSizeCmdString = b'\xaa\x89' + pack('>B', self._DeviceID) + b'\x02' + pack('B', rows * 16 + columns) + pack('B', value)
                VideoWallSizeCmdString = VideoWallSizeCmdString + pack('>B', CKS)

                self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                print('Invalid Command for SetVideoWallSize')
        else:
            print('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        CKS = (0x89 + self._DeviceID) & 0xff
        VideoWallSizeCmdString = b'\xaa\x89' + pack('>B', self._DeviceID) + b'\x00'
        VideoWallSizeCmdString = VideoWallSizeCmdString + pack('>B', CKS)
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
            CKS = (0x13 + self._DeviceID + value) & 0xff
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self._DeviceID, 0x01, value, CKS)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CKS = (0x12 + self._DeviceID) & 0xff
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self._DeviceID, 0x00, CKS)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1)[0])
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 254:
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
        print('Recieved error code from device')

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
