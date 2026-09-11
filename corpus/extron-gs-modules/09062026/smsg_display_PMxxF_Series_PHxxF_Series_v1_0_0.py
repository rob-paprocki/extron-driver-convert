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
        self._DeviceID = 0

        self.Models = {
            'PM49F': self.smsg_10_2533_PM,
            'PM32F': self.smsg_10_2533_PM,
            'PM43F': self.smsg_10_2533_PM,
            'PM55F': self.smsg_10_2533_PM,
            'PH43F': self.smsg_10_2533_PH,
            'PH49F': self.smsg_10_2533_PH,
            'PH55F': self.smsg_10_2533_PH,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoWall': {'Status': {}},
            'VideoWallMode': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18(\x01|\x04|\x31|\x0B)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x18|\x0C|\x08|\x1F|\x20|\x21|\x22|\x23|\\x24|\x25|\x30|\x40)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0xFE
        else:
            self._DeviceID = int(value)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x01,
            'Zoom': 0x04,
            'Wide Zoom': 0x31,
            '4:3': 0x0B
        }

        cks = (0x18 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        AspectRatioCmdString = pack('>6B', 0xAA, 0x18, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        cks = (0x18 + self._DeviceID) & 0xFF
        AspectRatioCmdString = pack('>5B', 0xAA, 0x18, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x31': 'Wide Zoom',
            '\x0B': '4:3'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        cks = (0x3D + self._DeviceID + 0x01) & 0xFF
        AutoImageCmdString = pack('>6B', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, cks)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        cks = (0x5D + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        ExecutiveModeCmdString = pack('>6B', 0xAA, 0x5D, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        cks = (0x5D + self._DeviceID) & 0xFF
        ExecutiveModeCmdString = pack('>5B', 0xAA, 0x5D, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        cks = (0x14 + self._DeviceID + 0x01 + self.InputStateValues[value]) & 0xFF
        InputCmdString = pack('>6B', 0xAA, 0x14, self._DeviceID, 0x01, self.InputStateValues[value], cks)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        cks = (0x14 + self._DeviceID) & 0xFF
        InputCmdString = pack('>5B', 0xAA, 0x14, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        cks = (0x3C + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PIPModeCmdString = pack('>6B', 0xAA, 0x3C, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        cks = (0x3C + self._DeviceID) & 0xFF
        PIPModeCmdString = pack('>5B', 0xAA, 0x3C, self._DeviceID, 0x00, cks)
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
            'On': 0x01,
            'Off': 0x00
        }

        cks = (0x11 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PowerCmdString = pack('>6B', 0xAA, 0x11, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        cks = (0x11 + self._DeviceID) & 0xFF
        PowerCmdString = pack('>5B', 0xAA, 0x11, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        cks = (0x84 + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallCmdString = pack('>6B', 0xAA, 0x84, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        cks = (0x84 + self._DeviceID) & 0xFF
        VideoWallCmdString = pack('>5B', 0xAA, 0x84, self._DeviceID, 0x00, cks)
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

        cks = (0x5C + self._DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallModeCmdString = pack('>6B', 0xAA, 0x5C, self._DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        cks = (0x5C + self._DeviceID) & 0xFF
        VideoWallModeCmdString = pack('>5B', 0xAA, 0x5C, self._DeviceID, 0x00, cks)
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
            cks = (0x12 + self._DeviceID + 0x01 + value) & 0xFF
            VolumeCmdString = pack('>6B', 0xAA, 0x12, self._DeviceID, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        cks = (0x12 + self._DeviceID) & 0xFF
        VolumeCmdString = pack('>5B', 0xAA, 0x12, self._DeviceID, 0x00, cks)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.DeviceID == 0xFE:
            print('Inappropriate Command')
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            b'\x18': 'Aspect Ratio',
            b'\x5D': 'Executive Mode',
            b'\x14': 'Input',
            b'\x3C': 'PIP Mode',
            b'\x11': 'Power',
            b'\x84': 'Video Wall',
            b'\x5C': 'Video Wall Mode',
            b'\x12': 'Volume'
        }

        if match.group(1) in DEVICE_ERROR_CODES:
            print('Error with Command: {0} and Error code is {1}.'.format(DEVICE_ERROR_CODES[match.group(1)], match.group(2)))
        else:
            self.Error(['Error with Unknown Command and Error code is {0}.'.format(match.group(2))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_10_2533_PM(self):

        self.InputStateValues = {
            'PC': 0x14,
            'DVI': 0x18,
            'Input Source': 0x0C,
            'Component': 0x08,
            'MagicInfo': 0x20,
            'RF(TV)': 0x30,
            'DTV': 0x40,
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'DisplayPort': 0x25
        }
        self.InputStateNames = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI_Video',
            '\x22': 'HDMI1_PC',
            '\x24': 'HDMI2_PC'
        }

    def smsg_10_2533_PH(self):

        self.InputStateValues = {
            'PC': 0x14,
            'DVI': 0x18,
            'Input Source': 0x0C,
            'Component': 0x08,
            'MagicInfo': 0x20,
            'HDMI 1': 0x21,
            'HDMI 2': 0x23,
            'DisplayPort': 0x25
        }
        self.InputStateNames = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x0C': 'Input Source',
            '\x08': 'Component',
            '\x20': 'MagicInfo',
            '\x21': 'HDMI 1',
            '\x23': 'HDMI 2',
            '\x25': 'DisplayPort',
            '\x1F': 'DVI_Video',
            '\x22': 'HDMI1_PC',
            '\x24': 'HDMI2_PC'
        }

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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
