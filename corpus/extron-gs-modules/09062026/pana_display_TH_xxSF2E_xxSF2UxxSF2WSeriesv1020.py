from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import hashlib
import binascii


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
        self.Models = {
            'TH-65SF2U': self.pana_10_3142_Other,
            'TH-65SF2E': self.pana_10_3142_65SF2E,
            'TH-55SF2U': self.pana_10_3142_Other,
            'TH-49SF2U': self.pana_10_3142_Other,
            'TH-43SF2U': self.pana_10_3142_Other,
            'TH-43SF2E': self.pana_10_3142_Other,
            'TH-49SF2E': self.pana_10_3142_Other,
            'TH-55SF2E': self.pana_10_3142_Other,
            'TH-43SF2W': self.pana_10_3142_65SF2E,
            'TH-49SF2W': self.pana_10_3142_65SF2E,
            'TH-55SF2W': self.pana_10_3142_65SF2E,
            'TH-65SF2W': self.pana_10_3142_65SF2E,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMode': {'Status': {}},
            'SoundOutput': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.md5hash = ''
        self.devicePassword = 'panasonic'

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'PDPCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PDPCONTROL 0\r'), self.__MatchNoAuthentication, None)
            self.AddMatchString(re.compile(b'(?:PDPCONTROL )?ERRA\r'), self.__MatchFailedPassword, None)
            self.Delim = '\r'
            self.Security = 'Not Authenticated'
            self.PasswdPromptCount = 0
        else:
            self.Delim = ''
        self.Security = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(FULL|NORM|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:([01])\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|DV1|PC1|VD1|UD1|DL1|MV1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD([01])\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(VIV|NAT|STD|SUV|GRH|DCM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:([01])\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QAC:MEN(STD|DYN|CLR)\x03'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'\x02QAC:OUT(SPO|LNO)\x03'), self.__MatchSoundOutput, None)
            self.AddMatchString(re.compile(b'\x02QVM:([01])\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9][0-9][0-9])\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ERR[1-5]|ER401)'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = binascii.hexlify(code_hash.digest()).decode()
        self.Security = 'Admin'

    def __MatchNoAuthentication(self, match, tag):
        self.Security = 'Not Needed'

    def __MatchFailedPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper User name and Password'])
        self.Security = 'Not Authenticated'

    def CommandStringBuild(self, command, commandstring):
        if self.Security == 'Admin':
            commandstring = self.md5hash + commandstring + self.Delim
        else:
            commandstring = commandstring + self.Delim
        return commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': '\x02DAM:FULL\x03',
            'Normal': '\x02DAM:NORM\x03',
            'Zoom 1': '\x02DAM:ZOOM\x03',
            'Zoom 2': '\x02DAM:ZOM2\x03'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02QAS\x03'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x02QAM\x03'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02DGE:ASU1\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02QMI\x03'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02OSP:OSD0\x03',
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '\x02QSP:OSD\x03'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid Signage': '\x02VPC:MENVIV\x03',
            'Natural Signage': '\x02VPC:MENNAT\x03',
            'Standard': '\x02VPC:MENSTD\x03',
            'Surveillance': '\x02VPC:MENSUV\x03',
            'Graphic': '\x02VPC:MENGRH\x03',
            'Dicom': '\x02VPC:MENDCM\x03'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\x02QPC:MEN\x03'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'VIV': 'Vivid Signage',
            'NAT': 'Natural Signage',
            'STD': 'Standard',
            'SUV': 'Surveillance',
            'GRH': 'Graphic',
            'DCM': 'Dicom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x02QPW\x03'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '\x02AAC:MENSTD\x03',
            'Dynamic': '\x02AAC:MENDYN\x03',
            'Clear': '\x02AAC:MENCLR\x03'
        }

        SoundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = '\x02QAC:MEN\x03'
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CLR': 'Clear'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetSoundOutput(self, value, qualifier):

        ValueStateValues = {
            'Line Out': '\x02AAC:OUTLNO\x03',
            'Speaker Out': '\x02AAC:OUTSPO\x03'
        }

        SoundOutputCmdString = ValueStateValues[value]
        self.__SetHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def UpdateSoundOutput(self, value, qualifier):

        SoundOutputCmdString = '\x02QAC:OUT\x03'
        self.__UpdateHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def __MatchSoundOutput(self, match, tag):

        ValueStateValues = {
            'LNO': 'Line Out',
            'SPO': 'Speaker Out'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundOutput', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02VMT:1\x03',
            'Off': '\x02VMT:0\x03'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\x02QVM\x03'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x02AVL:{0}\x03'.format(str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x02QAV\x03'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        commandstring = self.CommandStringBuild(command, commandstring)
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Security in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                commandstring = self.CommandStringBuild(command, commandstring)
                self.Send(commandstring)
        else:
            self.Discard('Not Authenticated')

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            'ERR1': 'Undefined Control Command.',
            'ERR2': 'Out of Parameter Range.',
            'ERR3': 'Busy State or No-acceptable Period.',
            'ERR4': 'Timeout or No-acceptable Period.',
            'ERR5': 'Wrong Data Length.',
            'ER401': 'Invalid Command Reply.'
        }

        if match.group(1).decode() in DEVICE_ERROR_CODES.keys():
            self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.md5hash = ''
            self.PasswdPromptCount = 0
            self.Security = 'Not Authenticated'

    def pana_10_3142_65SF2E(self):
        self.InputStateValues = {
            'HDMI 1': '\x02IMS:HM1\x03',
            'HDMI 2': '\x02IMS:HM2\x03',
            'DVI-D': '\x02IMS:DV1\x03',
            'PC': '\x02IMS:PC1\x03',
            'Video': '\x02IMS:VD1\x03',
            'USB Display': '\x02IMS:UD1\x03',
            'Digital Link': '\x02IMS:DL1\x03',
            'Memory Viewer': '\x02IMS:MV1\x03'
        }
        self.InputStateNames = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB Display',
            'DL1': 'Digital Link',
            'MV1': 'Memory Viewer'
        }

    def pana_10_3142_Other(self):
        self.InputStateValues = {
            'HDMI 1': '\x02IMS:HM1\x03',
            'HDMI 2': '\x02IMS:HM2\x03',
            'DVI-D': '\x02IMS:DV1\x03',
            'PC': '\x02IMS:PC1\x03',
            'Video': '\x02IMS:VD1\x03',
            'USB Display': '\x02IMS:UD1\x03',
            'Memory Viewer': '\x02IMS:MV1\x03'
        }
        self.InputStateNames = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB Display',
            'MV1': 'Memory Viewer'
        }

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
