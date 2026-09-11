from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self.Models = {
            'QB65H': self.smsg_10_3416_QB,
            'QB75H': self.smsg_10_3416_QB,
            'QH55H': self.smsg_10_3416_QH,
            'QH65H': self.smsg_10_3416_QH,
            'LH65QBHPLGC/GO': self.smsg_10_3416_QB,
            'LH75QBHPLGC/GO': self.smsg_10_3416_QB,
            'LH55QHHPLGC/GO': self.smsg_10_3416_QH,
            'LH65QHHPLGC/GO': self.smsg_10_3416_QH,
            'LH65QBHPLGC/EN': self.smsg_10_3416_QB,
            'LH65QHHPLGC/EN': self.smsg_10_3416_QH,
            'LH75QBHPLGC/EN': self.smsg_10_3416_QB,
            'LH55QHHPLGC/EN': self.smsg_10_3416_QH,
            'DB43J': self.smsg_10_3416_DB,
            'DB49J': self.smsg_10_3416_DB,
            'LH43DBJPLGA/GO': self.smsg_10_3416_DB,
            'LH49DBJPLGA/GO': self.smsg_10_3416_DB,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'SafetyLock': { 'Status': {}},
            'VideoWall': { 'Status': {}},
            'VideoWallMode': { 'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': { 'Status': {}},
        }



        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x13([\x01\x00])[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x14([\x18\x0C\x20\x1F\x21\x22\x23\x24\x25])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x11([\x01\x00])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x5D([\x01\x00])[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\x84([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x03\x41\\x5C([\x01\x00])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xE0]\x04\x41\x89([\x00-\xFF])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
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

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On':   0x01,
            'Off':  0x00
        }

        cks = int(hex(0x13 + self.DeviceID + 0x01 + AudioMuteStateValues[value])[-2:], 16)
        AudioMuteCmdString = pack('BBBBBB', 0xAA, 0x13, self.DeviceID, 0x01, AudioMuteStateValues[value], cks)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        cks = int(hex(0x13 + self.DeviceID)[-2:], 16)
        AudioMuteCmdString = pack('BBBBB', 0xAA, 0x13, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        cks = int(hex(0x14 + self.DeviceID + 0x01 + self.SetInputState[value])[-2:], 16)
        InputCmdString = pack('>BBBBBB', 0xAA, 0x14, self.DeviceID, 0x01, self.SetInputState[value], cks)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        cks = int(hex(0x14 + self.DeviceID)[-2:], 16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.GetInputState[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On':   0x01,
            'Off':  0x00
        }

        cks = int(hex(0x11 + self.DeviceID + 0x01 + PowerState[value])[-2:], 16)
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self.DeviceID, 0x01, PowerState[value], cks)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        cks = int(hex(0x11 + self.DeviceID)[-2:], 16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }


        value = PowerState[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetSafetyLock(self, value, qualifier):

        SafetyLockState = {
            'On':   0x01,
            'Off':  0x00
        }

        cks = int(hex(0x5D + self.DeviceID + 0x01 + SafetyLockState[value])[-2:], 16)
        SafetyLockCmdString = pack('>BBBBBB', 0xAA, 0x5D, self.DeviceID, 0x01, SafetyLockState[value], cks)
        self.__SetHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        cks = int(hex(0x5D + self.DeviceID)[-2:], 16)
        SafetyLockCmdString = pack('>BBBBB', 0xAA, 0x5D, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('SafetyLock', SafetyLockCmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        SafetyLockState = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = SafetyLockState[match.group(1)]
        self.WriteStatus('SafetyLock', value, None)

    def SetVideoWall(self, value, qualifier):

        VideoWallState = {
            'On':   0x01,
            'Off':  0x00
        }

        cks = int(hex(0x84 + self.DeviceID + 0x01 + VideoWallState[value])[-2:], 16)
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self.DeviceID, 0x01, VideoWallState[value], cks)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        cks = int(hex(0x84 + self.DeviceID)[-2:], 16)
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        VideoWallState = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = VideoWallState[match.group(1)]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        VideoWallModeState = {
            'Full':     0x01,
            'Natural':  0x00
        }

        cks = int(hex(0x5C + self.DeviceID + 0x01 + VideoWallModeState[value])[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self.DeviceID, 0x01, VideoWallModeState[value], cks)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        cks = int(hex(0x5C + self.DeviceID)[-2:], 16)
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        VideoWallModeState = {
            b'\x01': 'Full',
            b'\x00': 'Natural'
        }

        value = VideoWallModeState[match.group(1)]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        rowState = {
            '1':  0x10,
            '2':  0x20,
            '3':  0x30,
            '4':  0x40,
            '5':  0x50,
            '6':  0x60,
            '7':  0x70,
            '8':  0x80,
            '9':  0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
        }

        rowValue = int(qualifier['Row'])
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15 and 0 < rowValue <= 15:
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
                    Valid = False                                       #All qualifiers configured wrong
                if Valid:
                    checksum = int(hex(0x89 + self.DeviceID + 0x02 + size + displayNum)[-2:], 16)
                    VideoWallSizeCmdString = pack('>BBBBBBB', 0xAA, 0x89, self.DeviceID, 0x02, size, displayNum, checksum)
                    self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetVideoWallSize')
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier): 
      
        checksum = int(hex(0x89 + self.DeviceID)[-2:], 16)
        VideoWallSizeCmdString = pack('>BBBBB', 0xAA, 0x89, self.DeviceID, 0x00, checksum)
        self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group(2).decode())) #value
        value2 = ord(match.group(1)) #size
        if value2 < 0x20: # row 1
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30: # row 2
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40: # row 3
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50: # row 4
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60: # row 5
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70: # row 6
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80: # row 7
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90: # row 8
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0: # row 9
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0: # row 10
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0: # row 11
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0: # row 12
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0: # row 13
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0: # row 14
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7: # row 15
            row = '15'
            value3 = value2 - 0xF0
        qualifier = {'Column': str(value3), 'Row': row}

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = int(hex(0x12 + self.DeviceID + 0x01 + value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBB', 0xAA, 0x12, self.DeviceID, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        cks = int(hex(0x12 + self.DeviceID)[-2:], 16)
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 254:
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
            b'\x13': 'Audio Mute',
            b'\x14': 'Input',
            b'\x11': 'Power',
            b'\x5D': 'Safety Lock',
            b'\x84': 'Video Wall',
            b'\x5C': 'Video Wall Mode',
            b'\x89': 'Video Wall Size',
            b'\x12': 'Volume'
        }

        self.Error(['An error occurred: Command: {0}, Error Code: {1}'.format(DEVICE_ERROR_CODES.get(match.group(1), 'Unknown'), ord(match.group(2)))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_3416_DB(self):
        self.SetInputState = {
            'DVI':          0x18,
            'Input Source': 0x0C,
            'MagicInfo':    0x20,
            'HDMI 1':       0x21,
            'HDMI 2':       0x23
        }

        self.GetInputState = {
            b'\x18': 'DVI',
            b'\x0C': 'Input Source',
            b'\x20': 'MagicInfo',
            b'\x1F': 'DVI Video',
            b'\x21': 'HDMI 1',
            b'\x22': 'HDMI 1 PC',
            b'\x23': 'HDMI 2',
            b'\x24': 'HDMI 2 PC'
        }



    def smsg_10_3416_QB(self):
        self.SetInputState = {
            'DVI':          0x18,
            'Input Source': 0x0C,
            'MagicInfo':    0x20,
            'HDMI 1':       0x21,
            'HDMI 2':       0x23,
            'DisplayPort':  0x25
        }

        self.GetInputState = {
            b'\x18': 'DVI',
            b'\x0C': 'Input Source',
            b'\x20': 'MagicInfo',
            b'\x1F': 'DVI Video',
            b'\x21': 'HDMI 1',
            b'\x22': 'HDMI 1 PC',
            b'\x23': 'HDMI 2',
            b'\x24': 'HDMI 2 PC',
            b'\x25': 'DisplayPort'
        }



    def smsg_10_3416_QH(self):
        self.SetInputState = {
            'Input Source': 0x0C,
            'MagicInfo':    0x20,
            'HDMI 1':       0x21,
            'HDMI 2':       0x23,
            'DisplayPort':  0x25
        }

        self.GetInputState = {
            b'\x0C': 'Input Source',
            b'\x20': 'MagicInfo',
            b'\x21': 'HDMI 1',
            b'\x22': 'HDMI 1 PC',
            b'\x23': 'HDMI 2',
            b'\x24': 'HDMI 2 PC',
            b'\x25': 'DisplayPort'
        }


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

