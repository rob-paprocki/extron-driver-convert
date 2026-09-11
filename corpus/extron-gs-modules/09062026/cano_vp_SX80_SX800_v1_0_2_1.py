from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not modify the variables below
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.DefaultResponseTimeout = 0.3
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Image': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mode': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'g:POWER=(ON|OFF|ON2OFF|OFF2ON)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'g:ERR=(NO_ERROR|ABNORMAL_TEMPERATURE|FAULTY_LAMP|FAULTY_LAMP_COVER|FAULTY_COOLING_FAN|FAULTY_POWER_SUPPLY|FAULTY_AK|FAULTY_ASC|FAULTY_AF|FAULTY_POWER_ZOOM|FAULTY_POWER_FOCUS)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'g:SIGNALSTATUS=(NO_SIGNAL|DISPLAYING|SETTING)\r'), self.__MatchSignalStatus, None)
            self.AddMatchString(re.compile(b'g:IMAGE=(PRESENTATION|STANDARD|SRGB|MOVIE|PHOTO|DCM_SIM)\r'), self.__MatchImage, None)
            self.AddMatchString(re.compile(b'g:ASPECT=(AUTO|4:3|16:9|TRUE|ZOOM)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'g:FREEZE=(ON|OFF)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'g:BLANK=(ON|OFF)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'g:MUTE=(ON|OFF)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'g:MODE=(REMOTE|LOCAL)\r'), self.__MatchMode, None)
            self.AddMatchString(re.compile(b'g:INPUT=(A-RGB1|A-RGB2|D-RGB|VIDEO|S-VIDEO|COMP|HDMI|USB)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'g:LMPT=([0-9]{1,5}).*\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'g:LAMP=(NORMAL|SILENT)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'g:AVOL=([0-9]{1,2})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'g:KEYLOCK=(MAIN|RC|OFF)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'e:[0-9A-F]{4}.*\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'i:.*\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):
        AspectStateValues = {
            'Auto': 'ASPECT=AUTO\r',
            '4:3': 'ASPECT=4:3\r',
            '16:9': 'ASPECT=16:9\r',
            'True': 'ASPECT=TRUE\r',
            'Zoom': 'ASPECT=ZOOM\r'
        }
        AspectCmdString = AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = 'GET ASPECT\r'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        AspectStateNames = {
            'AUTO': 'Auto',
            '4:3': '4:3',
            '16:9': '16:9',
            'TRUE': 'True',
            'ZOOM': 'Zoom'
        }
        value = AspectStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        AudioMuteStateValues = {
            'On': 'MUTE=ON\r',
            'Off': 'MUTE=OFF\r'
        }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'GET MUTE\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        AudioMuteStateNames = {
            'ON': 'On',
            'OFF': 'Off'
        }
        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'GET ERR\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):
        DeviceStateNames = {
            'NO_ERROR': 'No Error',
            'ABNORMAL_TEMPERATURE': 'Temperature Error',
            'FAULTY_LAMP': 'Lamp Error',
            'FAULTY_LAMP_COVER': 'Lamp Cover Error',
            'FAULTY_COOLING_FAN': 'Cooling Fan Error',
            'FAULTY_POWER_SUPPLY': 'Power Supply Error',
            'FAULTY_AK': 'AK Error',
            'FAULTY_ASC': 'ASC Error',
            'FAULTY_AF': 'AF Error',
            'FAULTY_POWER_ZOOM': 'Zoom Error',
            'FAULTY_POWER_FOCUS': 'Focus Error'
        }
        value = DeviceStateNames[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            'Main': 'KEYLOCK=MAIN\r',
            'Remote': 'KEYLOCK=RC\r',
            'Off': 'KEYLOCK=OFF\r'
        }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'GET KEYLOCK\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ExecutiveModeStateNames = {
            'MAIN': 'Main',
            'RC': 'Remote',
            'OFF': 'Off',
        }
        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):
        FreezeStateValues = {
            'On': 'FREEZE=ON\r',
            'Off': 'FREEZE=OFF\r'
        }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'GET FREEZE\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        FreezeStateNames = {
            'ON': 'On',
            'OFF': 'Off'
        }
        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetImage(self, value, qualifier):
        ImageStateValues = {
            'Standard': 'IMAGE=STANDARD\r',
            'Presentation': 'IMAGE=PRESENTATION\r',
            'sRGB': 'IMAGE=SRGB\r',
            'Movie': 'IMAGE=MOVIE\r',
            'Photo': 'IMAGE=PHOTO\r',
            'DICOM': 'IMAGE=DCM_SIM\r'
        }
        ImageCmdString = ImageStateValues[value]
        self.__SetHelper('Image', ImageCmdString, value, qualifier, 2)

    def UpdateImage(self, value, qualifier):

        ImageCmdString = 'GET IMAGE\r'
        self.__UpdateHelper('Image', ImageCmdString, value, qualifier)

    def __MatchImage(self, match, tag):
        ImageStateNames = {
            'STANDARD': 'Standard',
            'PRESENTATION': 'Presentation',
            'SRGB': 'sRGB',
            'MOVIE': 'Movie',
            'PHOTO': 'Photo',
            'DCM_SIM': 'DICOM'
        }
        value = ImageStateNames[match.group(1).decode()]
        self.WriteStatus('Image', value, None)

    def SetInput(self, value, qualifier):
        InputStateValues = {
            'RGB 1': 'INPUT=A-RGB1\r',
            'RGB 2': 'INPUT=A-RGB2\r',
            'DVI': 'INPUT=D-RGB\r',
            'Video': 'INPUT=VIDEO\r',
            'S-Video': 'INPUT=S-VIDEO\r',
            'Component': 'INPUT=COMP\r',
            'HDMI': 'INPUT=HDMI\r',
            'USB Port': 'INPUT=USB\r'
        }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 4)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GET INPUT\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        InputStateNames = {
            'A-RGB1': 'RGB 1',
            'A-RGB2': 'RGB 2',
            'D-RGB': 'DVI',
            'VIDEO': 'Video',
            'S-VIDEO': 'S-Video',
            'COMP': 'Component',
            'HDMI': 'HDMI',
            'USB': 'USB Port'
        }
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):
        LampModeStateValues = {
            'Normal': 'LAMP=NORMAL\r',
            'Silent': 'LAMP=SILENT\r'
        }
        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'GET LAMP\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        LampModeStateNames = {
            'NORMAL': 'Normal',
            'SILENT': 'Silent'
        }
        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'GET LMPT\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationStateValues = {
            'Menu': 'RC MENU\r',
            'Up': 'RC UP\r',
            'Down': 'RC DOWN\r',
            'Left': 'RC LEFT\r',
            'Right': 'RC RIGHT\r',
            'Enter': 'RC OK\r',
        }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 2)

    def SetMode(self, value, qualifier):
        ModeStateValues = {
            'Remote': 'REMOTE\r',
            'Local': 'LOCAL\r'
        }
        ModeCmdString = ModeStateValues[value]
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def UpdateMode(self, value, qualifier):

        ModeCmdString = 'GET MODE\r'
        self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)

    def __MatchMode(self, match, tag):
        ModeStateNames = {
            'LOCAL': 'Local',
            'REMOTE': 'Remote'
        }
        value = ModeStateNames[match.group(1).decode()]
        self.WriteStatus('Mode', value, None)

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On': 'POWER ON\r',
            'Off': 'POWER OFF\r',
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 2)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET POWER\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        PowerStateNames = {
            'ON': 'On',
            'OFF': 'Off',
            'OFF2ON': 'Warming',
            'ON2OFF': 'Cooling',
        }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def UpdateSignalStatus(self, value, qualifier):

        SignalStatusCmdString = 'GET SIGNALSTATUS\r'
        self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)

    def __MatchSignalStatus(self, match, tag):
        SignalStatusStateNames = {
            'NO_SIGNAL': 'No Signal',
            'DISPLAYING': 'Signal Displaying',
            'SETTING': 'Processing'
        }
        value = SignalStatusStateNames[match.group(1).decode()]
        self.WriteStatus('SignalStatus', value, None)

    def SetVideoMute(self, value, qualifier):
        VideoMuteStateValues = {
            'On': 'BLANK=ON\r',
            'Off': 'BLANK=OFF\r'
        }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 2)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'GET BLANK\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        VideoMuteStateNames = {
            'ON': 'On',
            'OFF': 'Off'
        }
        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 20
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'AVOL={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Set Command for Volume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET AVOL\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
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
        value = match.group(0).decode().split(':')
        print(value[1])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it matched with device expectancy.
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback
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
        if self.connectionFlag == False:
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
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
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
