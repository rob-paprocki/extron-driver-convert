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
        self._DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'SafetyLock': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18(\x01|\x04|\x31|\x0B)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x08|\x20|\x21|\x23|\x18|\x30|\x40|\x1F|\x22|\\x24)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x04\x41\x89([\x00-\xFF])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\xFF])\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        else:
            self._DeviceID = int(value)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
           '16:9': 0x01,
           'Zoom': 0x04,
           'Wide Zoom': 0x31,
           '4:3': 0x0B
           }

        checksum = int(hex(0x18 + self._DeviceID + 0x01 + AspectRatioState[value])[-2:], 16)
        AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x18, self._DeviceID, 0x01, AspectRatioState[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = int(hex(0x18 + self._DeviceID + 0x00)[-2:], 16)
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x18, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x31': 'Wide Zoom',
            '\x0B': '4:3'
            }

        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = int(hex(0x3D + self._DeviceID + 0x01 + 0x00)[-2:], 16)
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'PC': 0x14,
            'Component': 0x08,
            'MagicInfo': 0x20,
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'DVI': 0x18,
            'RF (TV)': 0x30,
            'DTV': 0x40
        }

        checksum = int(hex(0x14 + self._DeviceID + 0x01 + InputState[value])[-2:], 16)
        InputCmdString = pack('BBBBBB', 0xAA, 0x14, self._DeviceID, 0x01, InputState[value], checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = int(hex(0x14 + self._DeviceID + 0x00)[-2:], 16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputNames = {
            '\x14': 'PC',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x18': 'DVI',
            '\x30': 'RF (TV)',
            '\x40': 'DTV',
            '\x1F': 'DVI-Video',
            '\x22': 'HDMI 1 (PC)',
            '\x24': 'HDMI 2 (PC)'
        }

        value = InputNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
           'On': 0x01,
           'Off': 0x00
           }
        checksum = int(hex(0x3C + self._DeviceID + 0x01 + PIPModeState[value])[-2:], 16)
        PIPModeCmdString = pack('>BBBBBB', 0xAA, 0x3C, self._DeviceID, 0x01, PIPModeState[value], checksum)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        checksum = int(hex(0x3C + self._DeviceID + 0x00)[-2:], 16)
        PIPModeCmdString = pack('>BBBBB', 0xAA, 0x3C, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeNames = {
           '\x01': 'On',
           '\x00': 'Off'
           }

        value = PIPModeNames[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
           'On': 0x01,
           'Off': 0x00
           }
        checksum = int(hex(0x11 + self._DeviceID + 0x01 + PowerState[value])[-2:], 16)
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self._DeviceID, 0x01, PowerState[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = int(hex(0x11 + self._DeviceID + 0x00)[-2:], 16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerNames = {
            '\x01': 'On',
            '\x00': 'Off'
            }

        value = PowerNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        SafetyLockState = {
           'On': 0x01,
           'Off': 0x00
           }
        checksum = int(hex(0x5D + self._DeviceID + 0x01 + SafetyLockState[value])[-2:], 16)
        SafetyLockCmdString = pack('>BBBBBB', 0xAA, 0x5D, self._DeviceID, 0x01, SafetyLockState[value], checksum)
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        checksum = int(hex(0x5D + self._DeviceID + 0x00)[-2:], 16)
        SafetyLockCmdString = pack('>BBBBB', 0xAA, 0x5D, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        SafetyLockNames = {
            '\x01': 'On',
            '\x00': 'Off'
            }

        value = SafetyLockNames[match.group(1).decode()]
        self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        VideoWallState = {
           'On': 0x01,
           'Off': 0x00
           }
        checksum = int(hex(0x84 + self._DeviceID + 0x01 + VideoWallState[value])[-2:], 16)
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self._DeviceID, 0x01, VideoWallState[value], checksum)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        checksum = int(hex(0x84 + self._DeviceID + 0x00)[-2:], 16)
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        VideoWallNames = {
           '\x01': 'On',
           '\x00': 'Off'
           }

        value = VideoWallNames[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        VideoWallModeState = {
           'Full': 0x01,
           'Natural': 0x00
           }
        checksum = int(hex(0x5C + self._DeviceID + 0x01 + VideoWallModeState[value])[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self._DeviceID, 0x01, VideoWallModeState[value], checksum)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        checksum = int(hex(0x5C + self._DeviceID + 0x00)[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        VideoWallModeNames = {
           '\x01': 'Full',
           '\x00': 'Natural'
           }

        value = VideoWallModeNames[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        rowState = {
            '1': 0x10,
            '2': 0x20,
            '3': 0x30,
            '4': 0x40,
            '5': 0x50,
            '6': 0x60,
            '7': 0x70,
            '8': 0x80,
            '9': 0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
            }
        rowtemp = int(qualifier['Row'])
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < rowtemp <= 15:
            if 0 < displayNum <= 100:
                row = rowState[qualifier['Row']]
                size = row + column
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
                    checksum = int(hex(0x89 + self._DeviceID + 0x02 + size + displayNum)[-2:], 16)
                    VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, self._DeviceID, 0x02, size, displayNum, checksum)
                    self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
            else:
                print('Invalid Command for SetVideoWallSize')
        else:
            print('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        checksum = int(hex(0x89 + self._DeviceID)[-2:], 16)
        VideoWallSizeCmdString = pack('>BBBBB', 0xAA, 0x89, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group(2).decode()))
        value2 = ord(match.group(1).decode())
        if value2 < 0x20:
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30:
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40:
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50:
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60:
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70:
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80:
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90:
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0:
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0:
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0:
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0:
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0:
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0:
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7:
            row = '15'
            value3 = value2 - 0xF0
        qualifier = {'Column': str(value3), 'Row': row}

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            checksum = int(hex(0x12 + self._DeviceID + 0x01 + value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self._DeviceID, 0x01, value, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = int(hex(0x12 + self._DeviceID + 0x00)[-2:], 16)
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
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

        CommandList = {
            b'\x18' : 'AspectRatio',
            b'\x3D' : 'AutoImage',
            b'\x14' : 'Input',
            b'\x3C' : 'PIPMode',
            b'\x11' : 'Power',
            b'\x5D' : 'SafetyLock',
            b'\x84' : 'VideoWall',
            b'\x5C' : 'VideoWallMode',
            b'\x89' : 'VideoWallSize',
            b'\x12' : 'Volume',
        }
        
        if match.group(2) in CommandList:        
            errorstring = 'DeviceID: {0}, Command: {1}, Error Code: {2}'.format(ord(match.group(1)), CommandList[match.group(2)], ord(match.group(3)))
        else:
            errorstring = 'DeviceID: {0}, Command: {1}, Error Code: {2}'.format(ord(match.group(1)), 'Unknown' , ord(match.group(3)))
        print(errorstring)

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
