from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import hashlib
from binascii import hexlify

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA9\x00\x20\x02\x00([\x00-\x0A])'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x31\x02\x00([\x00\x01])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x3E\x02\x00([\x00-\x08])'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x01\x02\x00([\x00|\x01|\x02|\x04|\x08|\x10|\x20|\x40|\x80])'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x01\x02\x00([\x00-\x07])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x40\x02\x00([\x00-\x03])'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x13\x02([\x00-\xFF]{2})'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x02\x02\x00([\x00-\x05])'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x02\x02\x00([\x00-\x08])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x30\x02\x00([\x00\x01])'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x16\x02\x00([\x00-\x64])'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xA9([\x01|\xF0][\x01-\x50])\x03'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectStateValues = {
            'Full': b'\xA9\x00\x20\x00\x00\x00\x20\x9A',
            'Zoom': b'\xA9\x00\x20\x00\x00\x03\x23\x9A',
            '4:3': b'\xA9\x00\x20\x00\x00\x09\x29\x9A',
            '16:9': b'\xA9\x00\x20\x00\x00\x0A\x2A\x9A',
            'Full1': b'\xA9\x00\x20\x00\x00\x07\x27\x9A',
            'Full2': b'\xA9\x00\x20\x00\x00\x08\x28\x9A',
            'Normal': b'\xA9\x00\x20\x00\x00\x01\x21\x9A'
            }
        AspectCmdString = AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = b'\xA9\x00\x20\x01\x00\x00\x21\x9A'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectStateNames = {
            '\x00': 'Full',
            '\x03': 'Zoom',
            '\x09': '4:3',
            '\x0A': '16:9',
            '\x07': 'Full1',
            '\x08': 'Full2',
            '\x01': 'Normal'
            }
        value = AspectStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': b'\xA9\x00\x31\x00\x00\x01\x31\x9A',
            'Off': b'\xA9\x00\x31\x00\x00\x00\x31\x9A'
            }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xA9\x00\x31\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '\x01': 'On',
            '\x00': 'Off'
            }
        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'Off': b'\xA9\x00\x3E\x00\x00\x00\x3E\x9A',
            'CC1': b'\xA9\x00\x3E\x00\x00\x01\x3F\x9A',
            'CC2': b'\xA9\x00\x3E\x00\x00\x02\x3E\x9A',
            'CC3': b'\xA9\x00\x3E\x00\x00\x03\x3F\x9A',
            'CC4': b'\xA9\x00\x3E\x00\x00\x04\x3E\x9A',
            'TEXT1': b'\xA9\x00\x3E\x00\x00\x05\x3F\x9A',
            'TEXT2': b'\xA9\x00\x3E\x00\x00\x06\x3E\x9A',
            'TEXT3': b'\xA9\x00\x3E\x00\x00\x07\x3F\x9A',
            'TEXT4': b'\xA9\x00\x3E\x00\x00\x08\x3E\x9A'
            }
        ClosedCaptionCmdString = ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x01\x00\x00\x3F\x9A'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionStateNames = {
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
        value = ClosedCaptionStateNames[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\xA9\x01\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temp Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Warning Temp',
            b'\x80': 'NVM Data Error'
            }
        value = DeviceStatusStateNames[match.group(1)]
        self.WriteStatus('DeviceStatus', value, None)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Video': b'\xA9\x00\x01\x00\x00\x00\x01\x9A',
            'S-Video': b'\xA9\x00\x01\x00\x00\x01\x01\x9A',
            'Input A': b'\xA9\x00\x01\x00\x00\x02\x03\x9A',
            'Input B': b'\xA9\x00\x01\x00\x00\x03\x03\x9A',
            'Input C': b'\xA9\x00\x01\x00\x00\x04\x05\x9A',
            'Input D': b'\xA9\x00\x01\x00\x00\x05\x05\x9A'
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xA9\x00\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
            '\x00': 'Video',
            '\x01': 'S-Video',
            '\x02': 'Input A',
            '\x03': 'Input B',
            '\x04': 'Input C',
            '\x05': 'Input D'
            }
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'High': b'\xA9\x00\x40\x00\x00\x00\x40\x9A',
            'Standard': b'\xA9\x00\x40\x00\x00\x01\x41\x9A',
            'Auto': b'\xA9\x00\x40\x00\x00\x03\x43\x9A'
            }
        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\xA9\x00\x40\x01\x00\x00\x41\x9A'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeStateNames = {
            '\x00': 'High',
            '\x01': 'Standard',
            '\x03': 'Auto'
            }
        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xA9\x01\x13\x01\x00\x00\x13\x9A'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>h', match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuStateValues = {
            'Menu': b'\xA9\x17\x29\x00\x00\x00\x3F\x9A',
            'Up': b'\xA9\x17\x35\x00\x00\x00\x37\x9A',
            'Down': b'\xA9\x17\x36\x00\x00\x00\x37\x9A',
            'Left': b'\xA9\x17\x34\x00\x00\x00\x37\x9A',
            'Right': b'\xA9\x17\x33\x00\x00\x00\x37\x9A',
            'Enter': b'\xA9\x17\x5A\x00\x00\x00\x5F\x9A'
            }
        MenuCmdString = MenuStateValues[value]
        self.__SetHelper('MenuNavigation', MenuCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Dynamic': b'\xA9\x00\x02\x00\x00\x00\x02\x9A',
            'Standard': b'\xA9\x00\x02\x00\x00\x01\x03\x9A',
            'Presentation': b'\xA9\x00\x02\x00\x00\x02\x02\x9A'
            }
        PictureModeCmdString = PictureModeStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\xA9\x00\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        PictureModeStateNames = {
            '\x00': 'Dynamic',
            '\x01': 'Standard',
            '\x02': 'Presentation'
            }
        value = PictureModeStateNames[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': b'\xA9\x17\x2F\x00\x00\x00\x3F\x9A',
            'On': b'\xA9\x17\x2E\x00\x00\x00\x3F\x9A'
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA9\x01\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '\x00': 'Off',
            '\x08': 'Off',
            '\x03': 'On',
            '\x01': 'Warming Up',
            '\x02': 'Warming Up',
            '\x04': 'Cooling Down',
            '\x05': 'Cooling Down',
            '\x06': 'Cooling Down',
            '\x07': 'Cooling Down'
            }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': b'\xA9\x00\x30\x00\x00\x01\x31\x9A',
            'Off': b'\xA9\x00\x30\x00\x00\x00\x30\x9A'
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xA9\x00\x30\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '\x01': 'On',
            '\x00': 'Off'
            }
        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            ChkSum = value | 0x16
            VolumeCmdString = pack('<BBBBBBBB', 0xA9, 0x00, 0x16, 0x00, 0x00, value, ChkSum, 0x9A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xA9\x00\x16\x01\x00\x00\x17\x9A'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
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

        ErrorStateNames = { 
            b'\x01\x01' : 'Undefined Command',
            b'\x01\x04' : 'Size Error',
            b'\x01\x05' : 'Select Error',
            b'\x01\x06' : 'Range Over',
            b'\x01\x06' : 'Not Applicable',
            b'\xF0\x10' : 'Check Sum Error',
            b'\xF0\x20' : 'Framing Error',
            b'\xF0\x30' : 'Parity Error',
            b'\xF0\x40' : 'Over Run Error',
            b'\xF0\x50' : 'Other Comm Error'
            }
        print(ErrorStateNames[match.group(1)])

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

###################################### Ethernet Class###################################
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters': ['Type'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(value))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        inStr = match.group(1).decode()
        outStr = inStr + self.devicePassword
        m = hashlib.md5(outStr.encode())
        password = hexlify(m.digest()) + b'\x251POWR ?\r'
        self.Authenticated = 'Admin'
        self.SetPassword(password, None)

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        AVMuteQualifierValues = {
            'Audio': '2',
            'Video': '1',
            'Audio Video': '3'
        }
        AVMuteCmdString = '%1AVMT {0}{1}\r'.format(AVMuteQualifierValues[qualifier['Type']], AVMuteStateValues[value])
        if 'Video' in qualifier['Type']:
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            '11': {'Audio': 'Off', 'Video': 'On', 'Audio Video': 'Off'},
            '21': {'Audio': 'On', 'Video': 'Off', 'Audio Video': 'Off'},
            '31': {'Audio': 'On', 'Video': 'On', 'Audio Video': 'On'},
            '30': {'Audio': 'Off', 'Video': 'Off', 'Audio Video': 'Off'}
        }
        matchString = re.compile('%1AVMT=([1-3][0-1])\r')
        AVMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res != '':
            matchObject = re.search(matchString, res)
            if matchObject is not None:
                AVMuteValues = AVMuteStateNames[matchObject.group(1)]
                for Type in ['Audio', 'Video', 'Audio Video']:
                    qualifier = {'Type': Type}
                    value = AVMuteValues[Type]
                    self.WriteStatus('AVMute', value, qualifier)
            else:
                print('Invalid/Unexpected Response for UpdateAVMute')

    def UpdateDeviceStatus(self, value, qualifier):

        ErrorWarningNames = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            4: 'Cover',
            5: 'Filter',
            6: 'Other'
        }
        matchString = re.compile('%1ERST=([0-3]{6})\r')
        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res != '':
            matchObject = re.search(matchString, res)
            if matchObject is not None:
                ErrorStrings = matchObject.group(1)
                if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                    value = 'Normal'
                if ErrorStrings.count('1') + ErrorStrings.count('2') > 2:
                    value = 'Multiple Errors/Warnings'
                elif ErrorStrings.count('1') == 1:
                    index = ErrorStrings.index('1')
                    if ErrorWarningNames[index + 1] != 'Temp':
                        value = '{0} Warning'.format(ErrorWarningNames[index + 1])
                    else:
                        value = 'Warning Temp'
                elif ErrorStrings.count('2') == 1:
                    index = ErrorStrings.index('2')
                    value = '{0} Error'.format(ErrorWarningNames[index + 1])
                self.WriteStatus('DeviceStatus', value, None)
            else:
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Video': '21',
            'S-Video': '22',
            'Input A': '31',
            'Input B': '32',
            'Input C': '33',
            'Input D': '34'
        }

        InputCmdString = '%1INPT {0}\r'.format(InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            '21': 'Video',
            '22': 'S-Video',
            '31': 'Input A',
            '32': 'Input B',
            '33': 'Input C',
            '34': 'Input D'
        }

        matchString = re.compile('%1INPT=([2-3][1-4])\r')
        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject is not None:
                    value = InputStateNames[matchObject.group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        matchString = re.compile('%1LAMP=([0-9]{1,5}) [0-1]')
        LampUsageCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res != '':
            matchObject = re.search(matchString, res)
            if matchObject is not None:
                lamp = matchObject.group(1)
                value = int(lamp)
                self.WriteStatus('LampUsage', value, None)
            else:
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '1',
            'Off': '0'
        }
        PowerCmdString = '%1POWR {0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1': 'On',
            '2': 'Cooling Down',
            '3': 'Warming Up',
            '0': 'Off'
        }
        matchString = re.compile('%1POWR=([0-3])\r')
        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res != '':
            matchObject = re.search(matchString, res)
            if matchObject is not None:
                value = PowerStateNames[matchObject.group(1)]
                self.WriteStatus('Power', value, None)
            else:
                print('Invalid/Unexpected Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            ErrorMatchString = re.compile('ERR(1|2|3|4|A)')
            MatchObject = re.search(ErrorMatchString, response)
            if MatchObject is not None:
                MatchNames = {
                    '1': 'Undefined Command',
                    '2': 'Out of Parameter',
                    '3': 'Unavailable Time',
                    '4': 'Projector Failure',
                    'A': 'Invalid Password'
                }

                print('Error = {0}; Command = {1}', MatchNames[MatchObject.group(1)], sourceCmdName)
                if 'ERRA' in response:
                    self.Authenticated = 'None'
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    print('No Response')
                    print('Invalid/Unexpected Response')
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            print('Device requires Authentication. Password')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())
        else:
            print('Inappropriate Command ', command)
            return ''


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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


