from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import hashlib
from binascii import hexlify


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OSDExit': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMode': {'Status': {}},
            'SoundOutput': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.Delim = ''

        if self.ConnectionType == 'Ethernet':
            self.Delim = '\x0D'
            self.ResponseDelim = b'\x0D'
            self.deviceUsername = 'admin1'
            self.devicePassword = 'panasonic'
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'ERRA\r'), self.__MatchFaliedPassword, None)
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
        else:
            self.Delim = ''
            self.ResponseDelim = b'\x03'
            self.Authenticated = 'Not Needed'


    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        cmdString = self.md5hash + '\x02QPW\x03\x0D'.encode()
        self.Send(cmdString)
        self.Authenticated = 'Admin'

    def __MatchFaliedPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            print('Log in failed. Please supply proper User name and Password')
        self.Authenticated = 'None'

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': '\x02DAM:FULL\x03',
            'Normal': '\x02DAM:NORM\x03',
            'Zoom 1': '\x02DAM:ZOOM\x03',
            'Zoom 2': '\x02DAM:ZOM2\x03'
        }

        AspectRatioCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        AspectRatioCmdString = '\x02QAS\x03' + self.Delim
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[5:-2]]
                else:
                    value = ValueStateValues[res[5:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03'
        }

        AudioMuteCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '\x02QAM\x03' + self.Delim
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[5:-2]]
                else:
                    value = ValueStateValues[res[5:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '\x02IMS:HM1\x03',
            'HDMI 2': '\x02IMS:HM2\x03',
            'DVI': '\x02IMS:DV1\x03',
            'PC': '\x02IMS:PC1\x03',
            'Video': '\x02IMS:VD1\x03',
            'USB Display': '\x02IMS:UD1\x03'
        }

        InputCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB Display'
        }

        InputCmdString = '\x02QMI\x03' + self.Delim
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[5:-2]]
                else:
                    value = ValueStateValues[res[5:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02OSP:OSD0\x03',
        }

        OnScreenDisplayCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = '\x02QSP:OSD\x03' + self.Delim
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[8:-2]]
                else:
                    value = ValueStateValues[res[8:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetOSDExit(self, value, qualifier):

        CmdString = '\x02VDO\x03' + self.Delim
        self.__SetHelper('OSDExit', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '\x02VPC:MENSTD\x03',
            'Dynamic': '\x02VPC:MENDYN\x03',
            'Cinema': '\x02VPC:MENCNM\x03'
        }

        PictureModeCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CNM': 'Cinema'
        }

        PictureModeCmdString = '\x02QPC:MEN\x03' + self.Delim
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[8:-2]]
                else:
                    value = ValueStateValues[res[8:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03'
        }

        PowerCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '\x02QPW\x03' + self.Delim
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[5:-2]]
                else:
                    value = ValueStateValues[res[5:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '\x02AAC:MENSTD\x03',
            'Dynamic': '\x02AAC:MENDYN\x03',
            'Clear': '\x02AAC:MENCLR\x03'
        }

        SoundModeCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        ValueStateValues = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CLR': 'Clear'
        }

        SoundModeCmdString = '\x02QAC:MEN\x03' + self.Delim
        res = self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[8:-2]]
                else:
                    value = ValueStateValues[res[8:-1]]
                self.WriteStatus('SoundMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSoundMode')

    def SetSoundOutput(self, value, qualifier):

        ValueStateValues = {
            'Line Out': '\x02AAC:OUTLNO\x03',
            'Speaker Out': '\x02AAC:OUTSPO\x03'
        }

        SoundOutputCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def UpdateSoundOutput(self, value, qualifier):

        ValueStateValues = {
            'LNO': 'Line Out',
            'SPO': 'Speaker Out'
        }

        SoundOutputCmdString = '\x02QAC:OUT\x03' + self.Delim
        res = self.__UpdateHelper('SoundOutput', SoundOutputCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[8:-2]]
                else:
                    value = ValueStateValues[res[8:-1]]
                self.WriteStatus('SoundOutput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSoundOutput')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02VMT:1\x03',
            'Off': '\x02VMT:0\x03'
        }

        VideoMuteCmdString = ValueStateValues[value] + self.Delim
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '\x02QVM\x03' + self.Delim
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = ValueStateValues[res[5:-2]]
                else:
                    value = ValueStateValues[res[5:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x02AVL:{0}\x03'.format(str(value).zfill(3)) + self.Delim
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x02QAV\x03' + self.Delim
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                if self.ResponseDelim == b'\x0D':
                    value = int(res[5:-2])
                else:
                    value = int(res[5:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == '\x02ER401\x03':
            print('Error Occured in command: {0}'.format(sourceCmdName))
            reponse = ''
        elif response[0:9] == 'NTCONTROL':
            rand_num = response[12:-1]
            full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
            code_hash = hashlib.md5(full_str.encode())
            self.md5hash = hexlify(code_hash.digest())
            cmdString = self.md5hash + '\x02QPW\x03\x0D'.encode()
            self.Send(cmdString)
            self.Authenticated = 'Admin'
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('Invalid/unexpected response')
            else:
                self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.ResponseDelim)
                if not res:
                    print('Invalid/unexpected response')
                    return ''
                else:
                    return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)
        else:
            self.Error(['Authentication Failed'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.PasswdPromptCount = 0

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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
