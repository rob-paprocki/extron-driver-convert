from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack


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
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampLightMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA9\x00\x20\x02\x00(\x00|\x01|\x03|\x07|\x08|\x09|\x0A)[\x00-\xFF]\x9A'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x31\x02\x00(\x00|\x01)[\x00-\xFF]\x9A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x3E\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08)[\x00-\xFF]\x9A'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x01\x02\x00(\x00|\x01|\x02|\x04|\x08|\x10|\x20|\x40|\x80)[\x00-\xFF]\x9A'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x01\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06)[\x00-\xFF]\x9A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x40\x02\x00(\x00|\x01|\x03)[\x00-\xFF]\x9A'), self.__MatchLampLightMode, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x13\x02([\x00-\xFF]{2})[\x00-\xFF]\x9A'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x02\x02\x00(\x00|\x01|\x02)[\x00-\xFF]\x9A'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\xA9\x01\x02\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08)[\x00-\xFF]\x9A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xA9\x00\x30\x02\x00(\x00|\x01)[\x00-\xFF]\x9A'), self.__MatchVideoMute, None)

            self.AddMatchString(re.compile(b'\xA9\x01\x0A\x03\x00(\x00|\x01)[\x00-\xFF]\x9A'), self.__MatchAudioMute, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x00\x20',
            'Full 1': b'\x07\x27',
            'Full 2': b'\x08\x28',
            'Normal': b'\x01\x21',
            '4:3': b'\x09\x29',
            '16:9': b'\x0A\x2A',
            'Zoom': b'\x03\x23'
        }

        AspectRatioCmdString = b'\xA9\x00\x20\x00\x00' + ValueStateValues[value] + b'\x9A'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xA9\x00\x20\x01\x00\x00\x21\x9A'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00': 'Full',
            '\x07': 'Full 1',
            '\x08': 'Full 2',
            '\x01': 'Normal',
            '\x09': '4:3',
            '\x0A': '16:9',
            '\x03': 'Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b'\xA9\x00\x31\x00\x00' + ValueStateValues[value] + b'\x31\x9A'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xA9\x00\x31\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xA9\x17\x7B\x00\x00\x00\x7F\x9A'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00\x3E',
            'CC1': b'\x01\x3F',
            'CC2': b'\x02\x3E',
            'CC3': b'\x03\x3F',
            'CC4': b'\x04\x3E',
            'Text1': b'\x05\x3F',
            'Text2': b'\x06\x3E',
            'Text3': b'\x07\x3F',
            'Text4': b'\x08\x3E'
        }

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x00\x00' + ValueStateValues[value] + b'\x9A'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\xA9\x00\x3E\x01\x00\x00\x3F\x9A'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'CC1',
            '\x02': 'CC2',
            '\x03': 'CC3',
            '\x04': 'CC4',
            '\x05': 'Text1',
            '\x06': 'Text2',
            '\x07': 'Text3',
            '\x08': 'Text4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\xA9\x01\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temp Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Warning Error',
            b'\x80': 'NVM Data Error'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\xA9\x19\x67\x00\x00\x00\x7F\x9A'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': b'\xA9\x00\x01\x00\x00\x00\x01\x9A',
            'S-Video': b'\xA9\x00\x01\x00\x00\x01\x01\x9A',
            'Input A': b'\xA9\x00\x01\x00\x00\x02\x03\x9A',
            'Input B': b'\xA9\x00\x01\x00\x00\x03\x03\x9A',
            'Input C': b'\xA9\x00\x01\x00\x00\x04\x05\x9A',
            'Input D': b'\xA9\x00\x01\x00\x00\x05\x05\x9A',
            'Input E' : b'\xA9\x00\x01\x00\x00\x06\x07\x9A'
        }

        InputSourceCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputSourceCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xA9\x00\x01\x01\x00\x00\x01\x9A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Video',
            b'\x01': 'S-Video',
            b'\x02': 'Input A',
            b'\x03': 'Input B',
            b'\x04': 'Input C',
            b'\x05': 'Input D', 
            b'\x06' : 'Input E'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetLampLightMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x03\x43',
            'Standard': b'\x01\x41',
            'High': b'\x00\x40'
        }

        LampLightModeCmdString = b'\xA9\x00\x40\x00\x00' + ValueStateValues[value] + b'\x9A'
        self.__SetHelper('LampLightMode', LampLightModeCmdString, value, qualifier)

    def UpdateLampLightMode(self, value, qualifier):

        LampLightModeCmdString = b'\xA9\x00\x40\x01\x00\x00\x41\x9A'
        self.__UpdateHelper('LampLightMode', LampLightModeCmdString, value, qualifier)

    def __MatchLampLightMode(self, match, tag):

        ValueStateValues = {
            '\x03': 'Auto',
            '\x01': 'Standard',
            '\x00': 'High'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampLightMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xA9\x01\x13\x01\x00\x00\x13\x9A'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\xA9\x17\x34\x00\x00\x00\x37\x9A',
            'Right': b'\xA9\x17\x33\x00\x00\x00\x37\x9A',
            'Up': b'\xA9\x17\x35\x00\x00\x00\x37\x9A',
            'Down': b'\xA9\x17\x36\x00\x00\x00\x37\x9A',
            'Menu': b'\xA9\x17\x29\x00\x00\x00\x3F\x9A',
            'Enter': b'\xA9\x17\x5A\x00\x00\x00\x3F\x9A'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': b'\x00\x02',
            'Standard': b'\x01\x03',
            'Presentation': b'\x02\x02'
        }

        PictureModeCmdString = b'\xA9\x00\x02\x00\x00' + ValueStateValues[value] + b'\x9A'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\xA9\x00\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '\x00': 'Dynamic',
            '\x01': 'Standard',
            '\x02': 'Presentation'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA9\x17\x2E\x00\x00\x00\x3F\x9A',
            'Off': b'\xA9\x17\x2F\x00\x00\x00\x3F\x9A'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA9\x01\x02\x01\x00\x00\x03\x9A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x03': 'On',
            '\x00': 'Off',
            '\x08': 'Off',
            '\x01': 'Warming Up',
            '\x02': 'Warming Up',
            '\x04': 'Cooling Down',
            '\x05': 'Cooling Down',
            '\x06': 'Cooling Down',
            '\x07': 'Cooling Down'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31',
            'Off': b'\x00\x30'
        }

        VideoMuteCmdString = b'\xA9\x00\x30\x00\x00' + ValueStateValues[value] + b'\x9A'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xA9\x00\x30\x01\x00\x00\x31\x9A'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ', command)
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampLightMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x20\x02\x00(\x00|\x01|\x03|\x07|\x08|\x09|\x0A)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x31\x02\x00(\x00|\x01)'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x3E\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08)'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x01\x01\x02\x00(\x00|\x01|\x02|\x04|\x08|\x10|\x20|\x40|\x80)'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x01\x02\x00(\x00|\x01|\x02|\x03|\x04|\x05|\x06)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x40\x02\x00(\x01|\x00|\x03)'), self.__MatchLampLightMode, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x01\x13\x02([\x00-\xFF]{2})'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x02\x02\x00(\x00|\x01|\x02)'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x01\x02\x02\x00([\x00-\x08])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02\x0ASONY\x02\x00\x30\x02\x00(\x00|\x01)'), self.__MatchVideoMute, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x00',
            'Full 1': b'\x07',
            'Full 2': b'\x08',
            'Normal': b'\x01',
            '4:3': b'\x09',
            '16:9': b'\x0A',
            'Zoom': b'\x03'
        }

        AspectRatioCmdString = b'\x02\x0ASONY\x00\x00\x20\x02\x00' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x02\x0ASONY\x01\x00\x20\x02\x00\x00'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00': 'Full',
            '\x07': 'Full 1',
            '\x08': 'Full 2',
            '\x01': 'Normal',
            '\x09': '4:3',
            '\x0A': '16:9',
            '\x03': 'Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b'\x02\x0ASONY\x00\x00\x31\x02\x00' + ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x02\x0ASONY\x01\x00\x31\x02\x00\x00'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0ASONY\x00\x17\x7B\x02\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00',
            'CC1': b'\x01',
            'CC2': b'\x02',
            'CC3': b'\x03',
            'CC4': b'\x04',
            'Text1': b'\x05',
            'Text2': b'\x06',
            'Text3': b'\x07',
            'Text4': b'\x08'
        }

        ClosedCaptionCmdString = b'\x02\x0ASONY\x00\x00\x3E\x02\x00' + ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = b'\x02\x0ASONY\x01\x00\x3E\x02\x00\x00'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'CC1',
            '\x02': 'CC2',
            '\x03': 'CC3',
            '\x04': 'CC4',
            '\x05': 'Text1',
            '\x06': 'Text2',
            '\x07': 'Text3',
            '\x08': 'Text4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\x02\x0ASONY\x01\x01\x01\x02\x00\x00'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Lamp Error',
            b'\x02': 'Fan Error',
            b'\x04': 'Cover Error',
            b'\x08': 'Temp Error',
            b'\x10': 'D5V Error',
            b'\x20': 'Power Error',
            b'\x40': 'Warning Error',
            b'\x80': 'NVM Data Error'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x02\x0ASONY\x00\x19\x67\x02\x00\x00'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': b'\x00',
            'S-Video': b'\x01',
            'Input A': b'\x02',
            'Input B': b'\x03',
            'Input C': b'\x04',
            'Input D': b'\x05',
            'Input E' : b'\x06'
        }

        InputSourceCmdString = b'\x02\x0ASONY\x00\x00\x01\x02\x00' + ValueStateValues[value]
        self.__SetHelper('Input', InputSourceCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02\x0ASONY\x01\x00\x01\x02\x00\x00'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Video',
            b'\x01': 'S-Video',
            b'\x02': 'Input A',
            b'\x03': 'Input B',
            b'\x04': 'Input C',
            b'\x05': 'Input D',
            b'\x06' : 'Input E'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetLampLightMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x03',
            'Standard': b'\x01',
            'High': b'\x00'
        }

        LampLightModeCmdString = b'\x02\x0ASONY\x00\x00\x40\x02\x00' + ValueStateValues[value]
        self.__SetHelper('LampLightMode', LampLightModeCmdString, value, qualifier)

    def UpdateLampLightMode(self, value, qualifier):

        LampLightModeCmdString = b'\x02\x0ASONY\x01\x00\x40\x02\x00\x00'
        self.__UpdateHelper('LampLightMode', LampLightModeCmdString, value, qualifier)

    def __MatchLampLightMode(self, match, tag):

        ValueStateValues = {
            '\x03': 'Auto',
            '\x01': 'Standard',
            '\x00': 'High'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampLightMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x02\x0ASONY\x01\x01\x13\x02\x00\x00'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('>H', match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\x02\x0ASONY\x00\x17\x34\x02\x00\x00',
            'Right': b'\x02\x0ASONY\x00\x17\x33\x02\x00\x00',
            'Up': b'\x02\x0ASONY\x00\x17\x35\x02\x00\x00',
            'Down': b'\x02\x0ASONY\x00\x17\x36\x02\x00\x00',
            'Menu': b'\x02\x0ASONY\x00\x17\x29\x02\x00\x00',
            'Enter': b'\x02\x0ASONY\x00\x17\x5A\x02\x00\x00'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': b'\x00',
            'Standard': b'\x01',
            'Presentation': b'\x02'
        }

        PictureModeCmdString = b'\x02\x0ASONY\x00\x00\x02\x02\x00' + ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x02\x0ASONY\x01\x00\x02\x02\x00\x00'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '\x00': 'Dynamic',
            '\x01': 'Standard',
            '\x02': 'Presentation'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x0ASONY\x00\x17\x2E\x02\x00\x00',
            'Off': b'\x02\x0ASONY\x00\x17\x2F\x02\x00\x00',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x02\x0ASONY\x01\x01\x02\x02\x00\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x03': 'On',
            '\x00': 'Off',
            '\x08': 'Off',
            '\x01': 'Warming Up',
            '\x02': 'Warming Up',
            '\x04': 'Cooling Down',
            '\x05': 'Cooling Down',
            '\x06': 'Cooling Down',
            '\x07': 'Cooling Down'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoMuteCmdString = b'\x02\x0ASONY\x00\x00\x30\x02\x00' + ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x02\x0ASONY\x01\x00\x30\x02\x00\x00'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ', command)
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
