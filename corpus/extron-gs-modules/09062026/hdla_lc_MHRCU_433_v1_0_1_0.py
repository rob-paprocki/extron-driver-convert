from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PanelControlButton': {'Status': {}},
            'PanelControlState': {'Status': {}},
            'Scene': {'Parameters': ['Area'], 'Status': {}},
            'Sequence': {'Parameters': ['Area'], 'Status': {}},
            'SingleChannel': {'Parameters': ['Channel Number', 'Running Time'], 'Status': {}},
            'SingleChannelStatus': {'Parameters': ['Channel Number'], 'Status': {}},
            'UniversalSwitch': {'Parameters': ['Number'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\xE3\xDB[\x00-\xFF]{2}\x12([\x01-\x10])[\x00-\xFF]{2}'), self.__MatchPanelControlButton, None)
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\xE3\xDB[\x00-\xFF]{2}\x11([\x00-\x01])[\x00-\xFF]{2}'), self.__MatchPanelControlState, None)
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\xE0\x19[\x00-\xFF]{2}([\x01-\xFE])([\x00\x01])[\x00-\xFF]{2}'), self.__MatchUniversalSwitch, None)
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\x00\x0D[\x00-\xFF]{2}([\x01-\xFE])([\x00-\xFF])[\x00-\xFF]{2}'), self.__MatchScene, None)
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\xE0\x15[\x00-\xFF]{2}([\x01-\xFE])([\x00-\xFF])[\x00-\xFF]{2}'), self.__MatchSequence, None)
            self.AddMatchString(re.compile(b'\xAA\xAA[\x00-\xFF]{5}\x00\x34[\x00-\xFF]{2}([\x01-\xFF])([\x01-\x64]){1,255}[\x00-\xFF]{2}'), self.__MatchSingleChannel, None)

        self.CRC_TAB = (
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
            0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
            0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
            0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
            0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
            0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
            0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
            0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
            0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
            0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
            0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
            0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
            0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
            0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
            0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
            0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
            0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
            0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
            0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
            0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
            0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
            0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
            0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
            0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
            0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0)
        
        self.parameter_error_flag = False

    def PackCRC(self, Cmd):
        Crc = 0
        for a in Cmd:
            Dat = Crc >> 8
            Crc = (Crc << 8) & 0xFFFF
            Crc ^= self.CRC_TAB[Dat ^ a]
        return b''.join([Cmd, Crc.to_bytes(2, 'big')])
    
    def InitializeParameters(self, OrigDeviceID, OrigSubnetID, OrigDeviceType, TargetDeviceID, TargetSubnetID, TargetIP=None):
        OrigDeviceID = int(OrigDeviceID)
        OrigSubnetID = int(OrigSubnetID)
        TargetDeviceID = 255 if TargetDeviceID == 'Broadcast' else int(TargetDeviceID)
        TargetSubnetID = 255 if TargetSubnetID == 'Broadcast' else int(TargetSubnetID)
        
        self.OriginalIDs = pack('>2BH', OrigSubnetID, OrigDeviceID, OrigDeviceType)
        self.TargetIDs = pack('>2B', TargetSubnetID, TargetDeviceID)
        
        if 'Serial' not in self.ConnectionType:
            if TargetIP is None:
                print('TargetIP parameter is missing.')
            else:
                TargetIP = TargetIP.split('.')
                TargetIP = [int(a) for a in TargetIP]
                TargetIP = [a for a in TargetIP if a < 256]
                self.Header = b''.join([bytes(TargetIP), b'HDLMIRACLE\xAA\xAA'])
        else:
            self.Header = b'\xAA\xAA'

    def SetPanelControlButton(self, value, qualifier):

        Button = int(value)
        if 1 <= Button <= 16:
            CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\xE3\xE8', self.TargetIDs, b'\x12', Button.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__SetHelper('PanelControlButton', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanelControlButton')

    def UpdatePanelControlButton(self, value, qualifier):

        CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\xE3\xDA', self.TargetIDs, b'\x12'])
        CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
        self.__UpdateHelper('PanelControlButton', CmdString, value, qualifier)

    def __MatchPanelControlButton(self, match, tag):

        value = str(match.group(1)[0])
        self.WriteStatus('PanelControlButton', value, None)

    def SetPanelControlState(self, value, qualifier):

        States = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\xE3\xE8', self.TargetIDs, b'\x11', States[value]])
        CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
        self.__SetHelper('PanelControlState', CmdString, value, qualifier)

    def UpdatePanelControlState(self, value, qualifier):
        CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\xE3\xDA', self.TargetIDs, b'\x11'])
        CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
        self.__UpdateHelper('PanelControlState', CmdString, value, qualifier)

    def __MatchPanelControlState(self, match, tag):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = States[match.group(1)]
        self.WriteStatus('PanelControlState', value, None)

    def SetScene(self, value, qualifier):

        Area = int(qualifier['Area'])
        Scene = int(value)

        if 1 <= Area <= 255 and 0 <= Scene <= 255:
            CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\x00\x02', self.TargetIDs, Area.to_bytes(1, 'big'), Scene.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__SetHelper('Scene', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetScene')

    def UpdateScene(self, value, qualifier):

        Area = int(qualifier['Area'])
        if 1 <= Area <= 255:
            CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\x00\x0C', self.TargetIDs, Area.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__UpdateHelper('Scene', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateScene')

    def __MatchScene(self, match, tag):

        Area = str(match.group(1)[0])
        value = str(match.group(2)[0])
        self.WriteStatus('Scene', value, {'Area': Area})

    def SetSequence(self, value, qualifier):

        Area = int(qualifier['Area'])
        Sequence = int(value)

        if 1 <= Area <= 255 and 0 <= Sequence <= 255:
            CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\x00\x1A', self.TargetIDs, Area.to_bytes(1, 'big'), Sequence.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__SetHelper('Sequence', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetSequence')

    def UpdateSequence(self, value, qualifier):

        Area = int(qualifier['Area'])
        if True:
            CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\xE0\x14', self.TargetIDs, Area.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__UpdateHelper('Sequence', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateSequence')

    def __MatchSequence(self, match, tag):

        Area = str(match.group(1)[0])
        value = str(match.group(2)[0])
        self.WriteStatus('Sequence', value, {'Area': Area})

    def SetSingleChannel(self, value, qualifier):

        Channel = int(qualifier['Channel Number'])
        RTimeH = int(qualifier['Running Time'] / 256)
        RTimeL = int(qualifier['Running Time'] % 256)
        Level = int(value)

        if 1 <= Channel <= 255 and 0 <= qualifier['Running Time'] <= 3600 and 0 <= Level <= 100:
            CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\x00\x1A', self.TargetIDs, Channel.to_bytes(1, 'big'), Level.to_bytes(1, 'big'), RTimeH.to_bytes(1, 'big'), RTimeL.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__SetHelper('Sequence', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetSingleChannel')

    def UpdateSingleChannelStatus(self, value, qualifier):
        CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\x00\x33', self.TargetIDs])
        CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
        self.__UpdateHelper('SingleChannelStatus', CmdString, value, qualifier)

    def __MatchSingleChannel(self, match, tag):

        NumChannels = match.group(1)[0]
        ChannelString = match.group(2)

        for i in range(1, NumChannels + 1):
            self.WriteStatus('SingleChannelStatus', ChannelString[i - 1], {'Channel Number': str(i)})

    def SetUniversalSwitch(self, value, qualifier):

        States = {
            'On': b'\xFF',
            'Off': b'\x00'
        }

        Number = int(qualifier['Number'])
        if 1 <= Number <= 254:
            CmdString = b''.join([b'\x0D', self.OriginalIDs, b'\xE0\x1C', self.TargetIDs, Number.to_bytes(1, 'big'), States[value]])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__SetHelper('UniversalSwitch', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetUniversalSwitch')

    def UpdateUniversalSwitch(self, value, qualifier):

        Number = int(qualifier['Number'])
        if 1 <= Number <= 254:
            CmdString = b''.join([b'\x0C', self.OriginalIDs, b'\xE0\x18', self.TargetIDs, Number.to_bytes(1, 'big')])
            CmdString = b''.join([self.Header, self.PackCRC(CmdString)])
            self.__UpdateHelper('UniversalSwitch', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateUniversalSwitch')

    def __MatchUniversalSwitch(self, match, tag):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        Number = str(match.group(1)[0])
        value = States[match.group(2)]
        self.WriteStatus('UniversalSwitch', value, {'Number': Number})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        elif 255 not in self.TargetIDs:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            self.Send(commandstring)

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
            if self.check_for_header():
                getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
            
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            if self.check_for_header():
                getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')
            
    def check_for_header(self):
        if hasattr(self, 'Header'):
            return True
        elif not self.parameter_error_flag:
            error_log = """ {0} module has not had the necessary parameters initialized
 with InitializeParameters or it was not initialized correctly. Please refer to the
 communication sheet for more information.""".format(__name__)
            ProgramLog(error_log, 'warning')
            self.parameter_error_flag = True
            return False

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


class EthernetClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=6000, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
