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
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'Username'
        self.devicePassword = '@Panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'ControllerUserLevel': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.md5hash = ''

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
            self.AddMatchString(re.compile(b'\x02QAS:(FULL|NORM|NATV|HFIT|VFIT|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:([01])\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QSP:BTL(OFF|MEN|ALL)\x03'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'\x02QSP:RCM([0-3])\x03'), self.__MatchControllerUserLevel, None)
            self.AddMatchString(re.compile(b'\x02QSU:ECO([01])\x03'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|DV1|PC1|VD1|UD1|MV1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD([01])\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(VIV|NAT|STD|SUV|GRH|DCM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:([01])\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QAC:MEN(STD|DYN|CLR)\x03'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'\x02QVM:([01])\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:(\d{3})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ER401|ERR[1-5]'), self.__MatchError, None)

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
        if command not in ['UserDefinedCommand']:
            if self.Security == 'Admin':
                commandstring = ''.join([self.md5hash, commandstring, self.Delim])
            else:
                commandstring = ''.join([commandstring, self.Delim])
        else:
            if self.Security == 'Admin':
                commandstring = b''.join([self.md5hash.encode(encoding='iso-8859-1'), commandstring, self.Delim.encode()])  # MD5 Hash String needs to be encoded
            else:
                commandstring = b''.join([commandstring, self.Delim.encode()])
        return commandstring
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': 'FULL',
            'Normal': 'NORM',
            'Native': 'NATV',
            'H Fit': 'HFIT',
            'V Fit': 'VFIT',
            'Zoom 1': 'ZOOM',
            'Zoom 2': 'ZOM2'
        }

        AspectRatioCmdString = '\x02DAM:{}\x03'.format(ValueStateValues[value])
        AspectRatioCmdString = self.CommandStringBuild('AspectRatio', AspectRatioCmdString)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02QAS\x03'
        AspectRatioCmdString = self.CommandStringBuild('AspectRatio', AspectRatioCmdString)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'NATV': 'Native',
            'HFIT': 'H Fit',
            'VFIT': 'V Fit',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '\x02AMT:{}\x03'.format(ValueStateValues[value])
        AudioMuteCmdString = self.CommandStringBuild('AudioMute', AudioMuteCmdString)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x02QAM\x03'
        AudioMuteCmdString = self.CommandStringBuild('AudioMute', AudioMuteCmdString)
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
        AutoImageCmdString = self.CommandStringBuild('AutoImage', AutoImageCmdString)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'ALL',
            'Menu and Enter': 'MEN',
            'Off': 'OFF'
        }

        ButtonLockCmdString = '\x02OSP:BTL{}\x03'.format(ValueStateValues[value])
        ButtonLockCmdString = self.CommandStringBuild('ButtonLock', ButtonLockCmdString)
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ButtonLockCmdString = '\x02QSP:BTL\x03'
        ButtonLockCmdString = self.CommandStringBuild('ButtonLock', ButtonLockCmdString)
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ValueStateValues = {
            'ALL': 'On',
            'MEN': 'Menu and Enter',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetControllerUserLevel(self, value, qualifier):

        ValueStateValues = {
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
            'Off': '0'
        }

        ControllerUserLevelCmdString = '\x02OSP:RCM{}\x03'.format(ValueStateValues[value])
        ControllerUserLevelCmdString = self.CommandStringBuild('ControllerUserLevel', ControllerUserLevelCmdString)
        self.__SetHelper('ControllerUserLevel', ControllerUserLevelCmdString, value, qualifier)

    def UpdateControllerUserLevel(self, value, qualifier):

        ControllerUserLevelCmdString = '\x02QSP:RCM\x03'
        ControllerUserLevelCmdString = self.CommandStringBuild('ControllerUserLevel', ControllerUserLevelCmdString)
        self.__UpdateHelper('ControllerUserLevel', ControllerUserLevelCmdString, value, qualifier)

    def __MatchControllerUserLevel(self, match, tag):

        ValueStateValues = {
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ControllerUserLevel', value, None)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        EcoModeCmdString = '\x02SSU:ECO{}\x03'.format(ValueStateValues[value])
        EcoModeCmdString = self.CommandStringBuild('EcoMode', EcoModeCmdString)
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        EcoModeCmdString = '\x02QSU:ECO\x03'
        EcoModeCmdString = self.CommandStringBuild('EcoMode', EcoModeCmdString)
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EcoMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'HM1',
            'HDMI 2': 'HM2',
            'DVI-D': 'DV1',
            'PC': 'PC1',
            'Video': 'VD1',
            'USB': 'UD1',
            'Memory Viewer': 'MV1'
        }

        InputCmdString = '\x02IMS:{}\x03'.format(ValueStateValues[value])
        InputCmdString = self.CommandStringBuild('Input', InputCmdString)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02QMI\x03'
        InputCmdString = self.CommandStringBuild('Input', InputCmdString)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB',
            'MV1': 'Memory Viewer'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = '\x02OSP:OSD{}\x03'.format(ValueStateValues[value])
        OnScreenDisplayCmdString = self.CommandStringBuild('OnScreenDisplay', OnScreenDisplayCmdString)
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '\x02QSP:OSD\x03'
        OnScreenDisplayCmdString = self.CommandStringBuild('OnScreenDisplay', OnScreenDisplayCmdString)
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
            'Vivid Signage': 'VIV',
            'Natural Signage': 'NAT',
            'Standard': 'STD',
            'Surveillance': 'SUV',
            'Graphic': 'GRH',
            'DICOM': 'DCM'
        }

        PictureModeCmdString = '\x02VPC:MEN{}\x03'.format(ValueStateValues[value])
        PictureModeCmdString = self.CommandStringBuild('PictureMode', PictureModeCmdString)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\x02QPC:MEN\x03'
        PictureModeCmdString = self.CommandStringBuild('PictureMode', PictureModeCmdString)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'VIV': 'Vivid Signage',
            'NAT': 'Natural Signage',
            'STD': 'Standard',
            'SUV': 'Surveillance',
            'GRH': 'Graphic',
            'DCM': 'DICOM'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'N',
            'Off': 'F'
        }

        PowerCmdString = '\x02PO{}\x03'.format(ValueStateValues[value])
        PowerCmdString = self.CommandStringBuild('Power', PowerCmdString)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x02QPW\x03'
        PowerCmdString = self.CommandStringBuild('Power', PowerCmdString)
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
            'Normal': 'STD',
            'Dynamic': 'DYN',
            'Clear': 'CLR'
        }

        SoundModeCmdString = '\x02AAC:MEN{}\x03'.format(ValueStateValues[value])
        SoundModeCmdString = self.CommandStringBuild('SoundMode', SoundModeCmdString)
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = '\x02QAC:MEN\x03'
        SoundModeCmdString = self.CommandStringBuild('SoundMode', SoundModeCmdString)
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Normal',
            'DYN': 'Dynamic',
            'CLR': 'Clear'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '\x02VMT:{}\x03'.format(ValueStateValues[value])
        VideoMuteCmdString = self.CommandStringBuild('VideoMute', VideoMuteCmdString)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\x02QVM\x03'
        VideoMuteCmdString = self.CommandStringBuild('VideoMute', VideoMuteCmdString)
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
            VolumeCmdString = '\x02AVL:{:03}\x03'.format(value)
            VolumeCmdString = self.CommandStringBuild('Volume', VolumeCmdString)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x02QAV\x03'
        VolumeCmdString = self.CommandStringBuild('Volume', VolumeCmdString)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Security in ['Admin', 'Not Needed']:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command + 'not authenticated')

    def __MatchError(self, match, tag):
        self.counter = 0

        error_map = {
            'ER401': 'Incorrect command',
            'ERR1': 'Undefined control command',
            'ERR2': 'Out of parameter range',
            'ERR3': 'Busy status or reception invalid period',
            'ERR4': 'Timeout or reception invalid period',
            'ERR5': 'Wrong data length'
        }

        err = match.group(0).decode()
        self.Error(['An error occurred: {}: {}.'.format(err, error_map[err])])

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
