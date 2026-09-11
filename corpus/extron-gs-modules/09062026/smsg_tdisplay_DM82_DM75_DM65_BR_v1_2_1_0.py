from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = b'\x01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenMode': {'Status': {}},
            'ScreenSize': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x15(\x00|\x01|\x10|\x04|\x05|\x06|\x09|[\x0B-\x0F]|\x18|\x20|\x21|\x31|\x32)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13(\x00|\x01)[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14([\x14|\x18|\x0C|\x08|\x20|\x1F|\x30|\x40|\x21|\x22|\x23|\x24|\x25|\x64])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18(\x01|\x04|\x31|\x0B)[\x00-\xFF]'), self.__MatchScreenMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x19([\x00-\xFF])[\x00-\xFF]'), self.__MatchScreenSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x00-\xFF])[\x00-\xFF][\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = b'\xFE'
        elif 0 <= int(value) <= 224:
            self._DeviceID = pack('>B', int(tempDeviceID))
        else:
            self.Discard('Invalid DeviceID. DeviceID range: 0 - 99 or Broadcast')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto Wide': b'\x00',
            '16:9': b'\x01',
            'Zoom': b'\x04',
            'Zoom 1': b'\x05',
            'Zoom 2': b'\x06',
            'Just Scan': b'\x09',
            '4:3': b'\x0B',
            'Wide Fit': b'\x0C',
            'Custom': b'\x0D',
            'Smart View 1': b'\x0E',
            'Smart View 2': b'\x0F',
            'Wide Zoom': b'\x31',
            '21:9': b'\x32',
            '16:9 (PC)': b'\x10',
            '4:3 (PC)': b'\x18',
            'Original Ratio (PC)': b'\x20',
            '21:9 (PC)': b'\x21',
        }

        checksum = pack('>B', (0x15 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AspectRatioCmdString = b''.join([b'\xAA\x15', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = pack('>B', (0x15 + self._DeviceID[0]) & 0xFF)
        AspectRatioCmdString = b''.join([b'\xAA\x15', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00': 'Auto Wide',
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x05': 'Zoom 1',
            '\x06': 'Zoom 2',
            '\x09': 'Just Scan',
            '\x0B': '4:3',
            '\x0C': 'Wide Fit',
            '\x0D': 'Custom',
            '\x0E': 'Smart View 1',
            '\x0F': 'Smart View 2',
            '\x31': 'Wide Zoom',
            '\x32': '21:9',
            '\x10': '16:9 (PC)',
            '\x18': '4:3 (PC)',
            '\x20': 'Original Ratio (PC)',
            '\x21': '21:9 (PC)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        checksum = pack('>B', (0x13 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        AudioMuteCmdString = b''.join([b'\xAA\x13', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        checksum = pack('>B', (0x13 + self._DeviceID[0]) & 0xFF)
        AudioMuteCmdString = b''.join([b'\xAA\x13', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = pack('>B', (0x3D + self._DeviceID[0] + 0x01) & 0xFF)
        AutoImageCmdString = b''.join([b'\xAA\x3D', self._DeviceID, b'\x01\x00', checksum])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x5D + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ExecutiveModeCmdString = b''.join([b'\xAA\x5D', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        checksum = pack('>B', (0x5D + self._DeviceID[0]) & 0xFF)
        ExecutiveModeCmdString = b''.join([b'\xAA\x5D', self._DeviceID, b'\x00', checksum])
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
            'MagicInfo': b'\x20',
            'AV': b'\x0C',
            'DTV': b'\x40',
            'DisplayPort': b'\x25',
            'HDMI 1': b'\x21',
            'HDMI 2': b'\x23',
            'Component': b'\x08',
            'IWB': b'\x64'
        }
        checksum = pack('>B', (0x14 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        InputCmdString = b''.join([b'\xAA\x14', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = pack('>B', (0x14 + self._DeviceID[0]) & 0xFF)
        InputCmdString = b''.join([b'\xAA\x14', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x0C': 'AV',
            '\x40': 'DTV',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI - VIDEO',
            '\x22': 'HDMI 1 PC',
            '\x24': 'HDMI 2 PC',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x08': 'Component',
            '\x64': 'IWB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x3C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PIPModeCmdString = b''.join([b'\xAA\x3C', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        checksum = pack('>B', (0x3C + self._DeviceID[0]) & 0xFF)
        PIPModeCmdString = b''.join([b'\xAA\x3C', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x11 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        PowerCmdString = b''.join([b'\xAA\x11', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = pack('>B', (0x11 + self._DeviceID[0]) & 0xFF)
        PowerCmdString = b''.join([b'\xAA\x11', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetScreenMode(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x01',
            'Zoom': b'\x04',
            '4:3': b'\x0B',
            'Wide Zoom': b'\x31'
        }

        checksum = pack('>B', (0x18 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        ScreenModeCmdString = b''.join([b'\xAA\x18', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('ScreenMode', ScreenModeCmdString, value, qualifier)

    def UpdateScreenMode(self, value, qualifier):

        checksum = pack('>B', (0x18 + self._DeviceID[0]) & 0xFF)
        ScreenModeCmdString = b''.join([b'\xAA\x18', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('ScreenMode', ScreenModeCmdString, value, qualifier)

    def __MatchScreenMode(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x0B': '4:3',
            '\x31': 'Wide Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenMode', value, None)

    def UpdateScreenSize(self, value, qualifier):

        checksum = pack('>B', (0x19 + self._DeviceID[0]) & 0xFF)
        ScreenSizeCmdString = b''.join([b'\xAA\x19', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)

    def __MatchScreenSize(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('ScreenSize', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        checksum = pack('>B', (0x84 + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallCmdString = b''.join([b'\xAA\x84', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        checksum = pack('>B', (0x84 + self._DeviceID[0]) & 0xFF)
        VideoWallCmdString = b''.join([b'\xAA\x84', self._DeviceID, b'\x00', checksum])
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
        checksum = pack('>B', (0x5C + self._DeviceID[0] + 0x01 + ValueStateValues[value][0]) & 0xFF)
        VideoWallModeCmdString = b''.join([b'\xAA\x5C', self._DeviceID, b'\x01', ValueStateValues[value], checksum])
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        checksum = pack('>B', (0x5C + self._DeviceID[0]) & 0xFF)
        VideoWallModeCmdString = b''.join([b'\xAA\x5C', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = pack('>B', (0x12 + self._DeviceID[0] + 0x01 + value) & 0xFF)
            VolumeCmdString = b''.join([b'\xAA\x12', self._DeviceID, b'\x01', pack('>B', value), checksum])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = pack('>B', (0x12 + self._DeviceID[0]) & 0xFF)
        VolumeCmdString = b''.join([b'\xAA\x12', self._DeviceID, b'\x00', checksum])
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\xFE':
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

        Error = {
            b'\x5D' : 'Executive Mode',
            b'\x14' : 'Input',
            b'\x3C' : 'PIP Mode',
            b'\x11' : 'Power',
            b'\x84' : 'Video Wall',
            b'\x5C' : 'Video Wall Mode',
            b'\x12' : 'Volume',
            b'\x3D' : 'AutoImage',
            b'\x13' : 'Audio Mute',
            b'\x15' : 'Aspect Ratio',
            b'\x18' : 'Screen Mode',
            b'\x19' : 'Screen Size'
            }
        self.Error(['Error with Command: {0}.'.format(Error[match.group(2)])])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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