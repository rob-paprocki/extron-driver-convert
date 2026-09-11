from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


class DeviceSerialClass:

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
        self.Models = {
            'VPL-EW225': self.sony_1_1181_E_Models,
            'VPL-EW226': self.sony_1_1181_E_Models,
            'VPL-EW235': self.sony_1_1181_E_Models,
            'VPL-EW245': self.sony_1_1181_E_Models,
            'VPL-EW246': self.sony_1_1181_E_Models,
            'VPL-EW253': self.sony_1_1181_E_Models,
            'VPL-EW255': self.sony_1_1181_E_Models,
            'VPL-EW275': self.sony_1_1181_E_Models,
            'VPL-EW276': self.sony_1_1181_E_Models,
            'VPL-EW295': self.sony_1_1181_E_Models,
            'VPL-EX221': self.sony_1_1181_E_Models,
            'VPL-EX222': self.sony_1_1181_E_Models,
            'VPL-EX225': self.sony_1_1181_E_Models,
            'VPL-EX226': self.sony_1_1181_E_Models,
            'VPL-EX230': self.sony_1_1181_E_Models,
            'VPL-EX233': self.sony_1_1181_E_Models,
            'VPL-EX235': self.sony_1_1181_E_Models,
            'VPL-EX241': self.sony_1_1181_E_Models,
            'VPL-EX242': self.sony_1_1181_E_Models,
            'VPL-EX245': self.sony_1_1181_E_Models,
            'VPL-EX246': self.sony_1_1181_E_Models,
            'VPL-EX250': self.sony_1_1181_E_Models,
            'VPL-EX253': self.sony_1_1181_E_Models,
            'VPL-EX255': self.sony_1_1181_E_Models,
            'VPL-EX271': self.sony_1_1181_E_Models,
            'VPL-EX272': self.sony_1_1181_E_Models,
            'VPL-EX273': self.sony_1_1181_E_Models,
            'VPL-EX274': self.sony_1_1181_E_Models,
            'VPL-EX275': self.sony_1_1181_E_Models,
            'VPL-EX276': self.sony_1_1181_E_Models,
            'VPL-EX283': self.sony_1_1181_E_Models,
            'VPL-EX290': self.sony_1_1181_E_Models,
            'VPL-EX293': self.sony_1_1181_E_Models,
            'VPL-EX295': self.sony_1_1181_E_Models,
            'VPL-SW526': self.sony_1_1181_S_Models,
            'VPL-SW526C': self.sony_1_1181_S_Models,
            'VPL-SW536': self.sony_1_1181_S_Models,
            'VPL-SW536C': self.sony_1_1181_S_Models,
            'VPL-SX536': self.sony_1_1181_S_Models,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x20][\x02][\x00](?P<value>[\x00-\x10])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x31][\x02][\x00](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x3E][\x02][\x00](?P<value>[\x00-\x08])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'[\xA9][\x01][\x01][\x02][\x00](?P<value>[\x00-\x80])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x01][\x02][\x00](?P<value>[\x00-\x07])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x40][\x02][\x00](?P<value>[\x00-\x03])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'[\xA9][\x01][\x13][\x02](?P<value>[\x00-\xFF]{2})(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'[\xA9][\x01][\x12][\x02](?P<value>[\x00-\xFF]{2})(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x02][\x02][\x00](?P<value>[\x00-\x10])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'[\xA9][\x01][\x02][\x02][\x00](?P<value>[\x00-\x10])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x30][\x02][\x00](?P<value>[\x00-\x01])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'[\xA9][\x00][\x16][\x02][\x00](?P<value>[\x00-\x64])(?P<checksum>[\x00-\xFF])[\x9A]'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ModeStateValues = {
            'Full': b'\xA9\x00\x20\x00\x00\x00\x20\x9A',
            'Normal': b'\xA9\x00\x20\x00\x00\x01\x21\x9A',
            'Zoom': b'\xA9\x00\x20\x00\x00\x03\x23\x9A',
            'Full 1': b'\xA9\x00\x20\x00\x00\x07\x27\x9A',
            'Full 2': b'\xA9\x00\x20\x00\x00\x08\x28\x9A',
            '4:3': b'\xA9\x00\x20\x00\x00\x09\x29\x9A',
            '16:9': b'\xA9\x00\x20\x00\x00\x0A\x2A\x9A',
            'Full 3': b'\xA9\x00\x20\x00\x00\x10\x30\x9A'
        }

        AspectRatioCmdString = ModeStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xA9\x00\x20\x01\x00\x00\x21\x9A'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ModeStateValues = {
            '\x00': 'Full',
            '\x01': 'Normal',
            '\x03': 'Zoom',
            '\x07': 'Full 1',
            '\x08': 'Full 2',
            '\x09': '4:3',
            '\x0A': '16:9',
            '\x10': 'Full 3'
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ModeStateValues = {
            'On': b'\xA9\x00\x31\x00\x00\x01\x31\x9A',
            'Off': b'\xA9\x00\x31\x00\x00\x00\x31\x9A',
        }

        AudioMuteCmdString = ModeStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xA9\x00\x31\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ModeStateValues = {
            '\x01': 'On',
            '\x00': 'Off',
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        CmdString = b'\xA9\x19\x60\x00\x00\x00\x79\x9A'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ModeStateValues = {
            'Off': b'\xA9\x00\x3E\x00\x00\x00\x3E\x9A',
            'CC1': b'\xA9\x00\x3E\x00\x00\x01\x3F\x9A',
            'CC2': b'\xA9\x00\x3E\x00\x00\x02\x3E\x9A',
            'CC3': b'\xA9\x00\x3E\x00\x00\x03\x3F\x9A',
            'CC4': b'\xA9\x00\x3E\x00\x00\x04\x3E\x9A',
            'TEXT1': b'\xA9\x00\x3E\x00\x00\x05\x3F\x9A',
            'TEXT2': b'\xA9\x00\x3E\x00\x00\x06\x3E\x9A',
            'TEXT3': b'\xA9\x00\x3E\x00\x00\x07\x3F\x9A',
            'TEXT4': b'\xA9\x00\x3E\x00\x00\x08\x3E\x9A',
        }

        ClosedCaptionCmdString = ModeStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x01\x00\x00\x3F\x9A'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ModeStateValues = {
            '\x00': 'Off',
            '\x01': 'CC1',
            '\x02': 'CC2',
            '\x03': 'CC3',
            '\x04': 'CC4',
            '\x05': 'TEXT1',
            '\x06': 'TEXT2',
            '\x07': 'TEXT3',
            '\x08': 'TEXT4'
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\xA9\x01\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        MessageStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temperature Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Temperature Warning',
            b'\x80': 'NVM Data Error'
        }

        value = MessageStateValues[match.group('value')]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        CmdString = b'\xA9\x19\x67\x00\x00\x00\x7F\x9A'
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.SetInputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xA9\x00\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group('value').decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ModeStateValues = {
            'High': b'\xA9\x00\x40\x00\x00\x00\x40\x9A',
            'Standard': b'\xA9\x00\x40\x00\x00\x01\x41\x9A',
            'Low': b'\xA9\x00\x40\x00\x00\x02\x42\x9A',
            'Auto': b'\xA9\x00\x40\x00\x00\x03\x43\x9A',
        }

        LampModeCmdString = ModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\xA9\x00\x40\x01\x00\x00\x41\x9A'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ModeStateValues = {
            '\x00': 'High',
            '\x01': 'Standard',
            '\x02': 'Low',
            '\x03': 'Auto',
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xA9\x01\x13\x01\x00\x00\x13\x9A'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>h', match.group('value'))[0]
        self.WriteStatus('LampUsage', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\xA9\x01\x12\x01\x00\x00\x13\x9A'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = unpack('>h', match.group('value'))[0]
        self.WriteStatus('OperationHours', value, None)

    def SetPictureMode(self, value, qualifier):

        ModeStateValues = {
            'Dynamic': b'\xA9\x00\x02\x00\x00\x00\x02\x9A',
            'Standard': b'\xA9\x00\x02\x00\x00\x01\x03\x9A',
            'Presentation': b'\xA9\x00\x02\x00\x00\x02\x02\x9A',
            'Black Board': b'\xA9\x00\x02\x00\x00\x03\x03\x9A',
            'Game': b'\xA9\x00\x02\x00\x00\x04\x06\x9A',
            'Cinema': b'\xA9\x00\x02\x00\x00\x05\x07\x9A'
        }

        PictureModeCmdString = ModeStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\xA9\x00\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ModeStateValues = {
            '\x00': 'Dynamic',
            '\x01': 'Standard',
            '\x02': 'Presentation',
            '\x03': 'Black Board',
            '\x04': 'Game',
            '\x05': 'Cinema',
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ModeStateValues = {
            'On': b'\xA9\x17\x2E\x00\x00\x00\x3F\x9A',
            'Off': b'\xA9\x17\x2F\x00\x00\x00\x3F\x9A',
        }

        PowerCmdString = ModeStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA9\x01\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ModeStateValues = {
            '\x03': 'On',
            '\x00': 'Off',
            '\x08': 'Off',
            '\x01': 'Warming Up',
            '\x02': 'Warming Up',
            '\x04': 'Cooling Down',
            '\x05': 'Cooling Down',
            '\x06': 'Cooling Down',
            '\x07': 'Cooling Down',
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ModeStateValues = {
            'On': b'\xA9\x00\x30\x00\x00\x01\x31\x9A',
            'Off': b'\xA9\x00\x30\x00\x00\x00\x30\x9A'
        }

        VideoMuteCmdString = ModeStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xA9\x00\x30\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ModeStateValues = {
            '\x01': 'On',
            '\x00': 'Off',
        }

        value = ModeStateValues[match.group('value').decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= int(value) <= 100:
            CKS = int(hex(0x16 | value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBBBB', 0xA9, 0x00, 0x16, 0x00, 0x00, value, CKS, 0x9A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xA9\x00\x16\x01\x00\x00\x17\x9A'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>B', match.group('value'))[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
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

    def sony_1_1181_E_Models(self):

        self.SetInputs = {
            'Video'   : b'\xA9\x00\x01\x00\x00\x00\x01\x9A', 
            'S-Video' : b'\xA9\x00\x01\x00\x00\x01\x01\x9A', 
            'Input A' : b'\xA9\x00\x01\x00\x00\x02\x03\x9A', 
            'Input B' : b'\xA9\x00\x01\x00\x00\x03\x03\x9A', 
            'Input C' : b'\xA9\x00\x01\x00\x00\x04\x05\x9A', 
            'USB B'   : b'\xA9\x00\x01\x00\x00\x05\x05\x9A', 
            'Network' : b'\xA9\x00\x01\x00\x00\x06\x07\x9A', 
            'USB A'   : b'\xA9\x00\x01\x00\x00\x07\x07\x9A'
        }

        self.InputValues = {
            '\x00' : 'Video', 
            '\x01' : 'S-Video', 
            '\x02' : 'Input A', 
            '\x03' : 'Input B', 
            '\x04' : 'Input C', 
            '\x05' : 'USB B', 
            '\x06' : 'Network', 
            '\x07' : 'USB A'
        }

    def sony_1_1181_S_Models(self):

        self.SetInputs = {
            'Video'   : b'\xA9\x00\x01\x00\x00\x00\x01\x9A', 
            'S-Video' : b'\xA9\x00\x01\x00\x00\x01\x01\x9A', 
            'Input A' : b'\xA9\x00\x01\x00\x00\x02\x03\x9A', 
            'Input B' : b'\xA9\x00\x01\x00\x00\x03\x03\x9A',
            'Input C' : b'\xA9\x00\x01\x00\x00\x04\x05\x9A'
        }

        self.InputValues = {
            '\x00' : 'Video', 
            '\x01' : 'S-Video', 
            '\x02' : 'Input A', 
            '\x03' : 'Input B',
            '\x04' : 'Input C' 
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


class DeviceEthernetClass:

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
        
        self.Models = {
            'VLP-DW125': self.sony_1_1181_D_Models,
            'VLP-DW126': self.sony_1_1181_D_Models,
            'VLP-DX125': self.sony_1_1181_D_Models,
            'VLP-DX126': self.sony_1_1181_D_Models,
            'VLP-DX145': self.sony_1_1181_D_Models,
            'VLP-DX146': self.sony_1_1181_D_Models,            
            'VPL-EW225': self.sony_1_1181_E_Models,
            'VPL-EW226': self.sony_1_1181_E_Models,
            'VPL-EW235': self.sony_1_1181_E_Models,
            'VPL-EW245': self.sony_1_1181_E_Models,
            'VPL-EW246': self.sony_1_1181_E_Models,
            'VPL-EW253': self.sony_1_1181_E_Models,
            'VPL-EW255': self.sony_1_1181_E_Models,
            'VPL-EW275': self.sony_1_1181_E_Models,
            'VPL-EW276': self.sony_1_1181_E_Models,
            'VPL-EW295': self.sony_1_1181_E_Models,
            'VPL-EX221': self.sony_1_1181_E_Models,
            'VPL-EX222': self.sony_1_1181_E_Models,
            'VPL-EX225': self.sony_1_1181_E_Models,
            'VPL-EX226': self.sony_1_1181_E_Models,
            'VPL-EX230': self.sony_1_1181_E_Models,
            'VPL-EX233': self.sony_1_1181_E_Models,
            'VPL-EX235': self.sony_1_1181_E_Models,
            'VPL-EX241': self.sony_1_1181_E_Models,
            'VPL-EX242': self.sony_1_1181_E_Models,
            'VPL-EX245': self.sony_1_1181_E_Models,
            'VPL-EX246': self.sony_1_1181_E_Models,
            'VPL-EX250': self.sony_1_1181_E_Models,
            'VPL-EX253': self.sony_1_1181_E_Models,
            'VPL-EX255': self.sony_1_1181_E_Models,
            'VPL-EX271': self.sony_1_1181_E_Models,
            'VPL-EX272': self.sony_1_1181_E_Models,
            'VPL-EX273': self.sony_1_1181_E_Models,
            'VPL-EX274': self.sony_1_1181_E_Models,
            'VPL-EX275': self.sony_1_1181_E_Models,
            'VPL-EX276': self.sony_1_1181_E_Models,
            'VPL-EX283': self.sony_1_1181_E_Models,
            'VPL-EX290': self.sony_1_1181_E_Models,
            'VPL-EX293': self.sony_1_1181_E_Models,
            'VPL-EX295': self.sony_1_1181_E_Models,            
            'VPL-SW526': self.sony_1_1181_S_Models,
            'VPL-SW526C': self.sony_1_1181_S_Models,
            'VPL-SW536': self.sony_1_1181_S_Models,
            'VPL-SW536C': self.sony_1_1181_S_Models,
            'VPL-SX536': self.sony_1_1181_S_Models,
            }
    
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'UserDefinedCommand': {'Status': {}},
            'UserDefinedString': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }
    
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x20\x02\x00([\x00|\x01|\x03|\x07|\x08|\x09|\x0A|\x10])'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x31\x02\x00([\x00|\x01])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x3E\x02\x00([\x00-\x08])'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x01\x02\x00([\x00|\x01|\x02|\x04|\x08|\x10|\x20|\x40|\x80])'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x01\x02\x00([\x00-\x07])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x40\x02\x00([\x00|\x01|\x02|\x03])'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x13\x02([\x00-\xFF]{2})'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x12\x02([\x00-\xFF]{2})'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x02\x02\x00([\x00|\x01|\x02|\x03|\x04|\x05])'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x01\x02\x02\x00([\x00-\x08])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x30\x02\x00([\x00|\x01])'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x01\x00\x16\x02\x00([\x00-\x64])'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x00[\x00-\x01][\x00-\x41]\x02([\x01\x02\x10\x20\xF0\xF1][\x01-\xF0])'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ModeStateValues = {
            'Full'   : 0, 
            'Normal' : 1, 
            'Zoom'   : 3, 
            'Full 1' : 7, 
            'Full 2' : 8, 
            '4:3'    : 9, 
            '16:9'   : 10, 
            'Full 3' : 16
        }

        AspectRatioCmdString = b'\x02\x0ASONY\x00\x00\x20\x02' + pack('>H',ModeStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02\x0ASONY\x01\x00\x20\x02\x00\x00'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ModeStateValues = {
            0  : 'Full', 
            1  : 'Normal', 
            3  : 'Zoom', 
            7  : 'Full 1', 
            8  : 'Full 2', 
            9  : '4:3', 
            10 : '16:9', 
            16 : 'Full 3'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ModeStateValues = {
            'On'  : 1, 
            'Off' : 0
        }
        AudioMuteCmdString = b'\x02\x0ASONY\x00\x00\x31\x02' + pack('>H',ModeStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x02\x0ASONY\x01\x00\x31\x02\x00\x00'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ModeStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('AudioMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ModeStateValues = {
            'Off'   : 0, 
            'CC1'   : 1, 
            'CC2'   : 2, 
            'CC3'   : 3, 
            'CC4'   : 4, 
            'TEXT1' : 5, 
            'TEXT2' : 6, 
            'TEXT3' : 7, 
            'TEXT4' : 8
        }

        ClosedCaptionCmdString = b'\x02\x0ASONY\x00\x00\x3E\x02' + pack('>H',ModeStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\x02\x0ASONY\x01\x00\x3E\x02\x00\x00'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ModeStateValues = {
            0 : 'Off', 
            1 : 'CC1', 
            2 : 'CC2', 
            3 : 'CC3', 
            4 : 'CC4', 
            5 : 'TEXT1', 
            6 : 'TEXT2', 
            7 : 'TEXT3', 
            8 : 'TEXT4'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '\x02\x0ASONY\x01\x01\x01\x02\x00\x00'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        MessageStateValues = {
            0   : 'Normal', 
            1   : 'Lamp Error', 
            2   : 'Fan Error', 
            4   : 'Cover Error', 
            8   : 'Temperature Error', 
            16  : 'D5V Error', 
            32  : 'Power Error', 
            64  : 'Temperature Warning', 
            128 : 'NVM Data Error'
        }

        value = MessageStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('DeviceStatus', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = b'\x02\x0ASONY\x00\x00\x01\x02' + pack('>B',self.SetInputs[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
        
    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02\x0ASONY\x01\x00\x01\x02\x00\x00'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ModeStateValues = {
            'High'     : 0, 
            'Standard' : 1, 
            'Low'      : 2, 
            'Auto'     : 3
        }

        LampModeCmdString = b'\x02\x0ASONY\x00\x00\x40\x02' + pack('>B',ModeStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\x02\x0ASONY\x01\x00\x40\x02\x00\x00'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ModeStateValues = {
            0 : 'High', 
            1 : 'Standard', 
            2 : 'Low', 
            3 : 'Auto'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x02\x0ASONY\x01\x01\x13\x02\x00\x00'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>H',match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02\x0ASONY\x02\x01\x12\x02\x00\x00'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = unpack('>H',match.group(1))[0]
        self.WriteStatus('OperationHours', value, None)

    def SetPictureMode(self, value, qualifier):

        ModeStateValues = {
            'Dynamic'      : 0, 
            'Standard'     : 1, 
            'Presentation' : 2, 
            'Black Board'  : 3, 
            'Game'         : 4, 
            'Cinema'       : 5
        }

        PictureModeCmdString = b'\x02\x0ASONY\x00\x00\x02\x02' + pack('>H',ModeStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x02\x0ASONY\x01\x00\x02\x02\x00\x00'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ModeStateValues = {
            0 : 'Dynamic', 
            1 : 'Standard', 
            2 : 'Presentation', 
            3 : 'Black Board', 
            4 : 'Game', 
            5 : 'Cinema'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ModeStateValues = {
            'On'  : b'\x02\x0ASONY\x00\x17\x2E\x02\x00\x00', 
            'Off' : b'\x02\x0ASONY\x00\x17\x2F\x02\x00\x00', 
        }

        PowerCmdString = ModeStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x02\x0ASONY\x01\x01\x02\x02\x00\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ModeStateValues = {
            '\x03' : 'On', 
            '\x00' : 'Off',
            '\x08' : 'Off',
            '\x01' : 'Warming Up',
            '\x02' : 'Warming Up',
            '\x04' : 'Cooling Down',
            '\x05' : 'Cooling Down',
            '\x06' : 'Cooling Down',
            '\x07' : 'Cooling Down'
        }

        value = ModeStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ModeStateValues = {
            'On' : b'\x02\x0ASONY\x00\x00\x30\x02\x00\x01', 
            'Off' : b'\x02\x0ASONY\x00\x00\x30\x02\x00\x00'
        }

        VideoMuteCmdString = ModeStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x02\x0ASONY\x01\x00\x30\x02\x00\x00'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ModeStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        value = ModeStateValues[unpack('>B',match.group(1))[0]]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = b'\x02\x0ASONY\x00\x00\x16\x02' + pack('>H',value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x02\x0ASONY\x01\x00\x16\x02\x00\x00'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>B',match.group(1))[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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

        ErrorCodes = {
            '\x01\x01': 'Invalid Item',
            '\x01\x02': 'Invalid Item Request',
            '\x01\x03': 'Invalid Item Length',
            '\x01\x04': 'Invalid Item Data',
            '\x01\x11': 'Short Data',
            '\x01\x80': 'Item Not Applicable',
            '\x02\x01': 'Different Community',
            '\x10\x01': 'Invalid Version',
            '\x10\x02': 'Invalid Equipment Category Code',
            '\x10\x03': 'Invalid Request',
            '\x10\x11': 'Short Header',
            '\x10\x12': 'Short Community',
            '\x10\x13': 'Short Command',
            '\x20\x01': 'Timeout',
            '\xF0\x01': 'Timeout',
            '\xF0\x10': 'Checksum Error',
            '\xF0\x20': 'Framing Error',
            '\xF0\x30': 'Parity Error',
            '\xF0\x40': 'Over Run Error',
            '\xF0\x50': 'Other Comm Error',
            '\xF0\xF0': 'Unknown Response',
            '\xF1\x10': 'Read Error',
            '\xF1\x20': 'Write Error'
        }

        value = ErrorCodes[match.group(1).decode(encoding='iso-8859-1')]
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def sony_1_1181_D_Models(self):
    
        self.SetInputs = {
            'Video'   : 0, 
            'Input A' : 2, 
            'Input B' : 3, 
            'USB B'   : 4, 
            'Network' : 5, 
            'USB A'   : 6
        }

        self.InputValues = {
            0 : 'Video', 
            2 : 'Input A', 
            3 : 'Input B', 
            4 : 'USB B', 
            5 : 'Network', 
            6 : 'USB A'
        }
    
    def sony_1_1181_E_Models(self):
    
        self.SetInputs = {
            'Video'   : 0, 
            'S-Video' : 1, 
            'Input A' : 2, 
            'Input B' : 3, 
            'Input C' : 4, 
            'USB B'   : 5, 
            'Network' : 6, 
            'USB A'   : 7
        }

        self.InputValues = {
            0 : 'Video', 
            1 : 'S-Video', 
            2 : 'Input A', 
            3 : 'Input B', 
            4 : 'Input C', 
            5 : 'USB B', 
            6 : 'Network', 
            7 : 'USB A'
        }
    
    def sony_1_1181_S_Models(self):
    
        self.SetInputs = {
            'Video'   : 0, 
            'S-Video' : 1, 
            'Input A' : 2, 
            'Input B' : 3,
            'Input C' : 4
        }

        self.InputValues = {
            0 : 'Video', 
            1 : 'S-Video', 
            2 : 'Input A', 
            3 : 'Input B',
            4 : 'Input C' 
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
