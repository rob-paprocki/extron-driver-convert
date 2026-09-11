from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Blank': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FocusContinuous'			: {'Status': {}},
            'FocusStep'					: {'Status': {}},
            'Freeze': {'Status': {}},
            'ImageMode': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensPosition'				: {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'Volume': {'Status': {}},
            'ZoomContinuous'			: {'Status': {}},
            'ZoomStep'					: {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'g:ASPECT=(AUTO|4:3|16:9|16:10|ZOOM|TRUE)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'g:MUTE=(ON|OFF)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'g:BLANK=(ON|OFF)\r'), self.__MatchBlank, None)
            self.AddMatchString(re.compile(b'g:ERR=(NO_ERROR|ABNORMAL_TEMPERATURE|FAULTY_LAMP|FAULTY_LAMP_COVER|FAULTY_COOLING_FAN|FAULTY_POWER_SUPPLY|FAULTY_AIR_FILTER)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'g:FREEZE=(ON|OFF)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'g:IMAGE=(STANDARD|PRESENTATION|VIVID_PHOTO|PHOTO_SRGB|DYNAMIC|VIDEO|CINEMA|USER_1|USER_2|USER_3|USER_4|USER_5)\r'), self.__MatchImageMode, None)
            self.AddMatchString(re.compile(b'g:INPUT=(HDMI|D-RGB|A-RGB1|A-RGB2|LAN|USB|HDBT|COMP)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'g:LMPT=([0-9]{1,4}).*?\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'g:LAMP=(FULL|ECO)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'g:POWER=(ON|OFF|ON2OFF|OFF2ON)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'g:SIGNALSTATUS=(NO_SIGNAL|DISPLAYING|SETTING)\r'), self.__MatchSignalStatus, None)
            self.AddMatchString(re.compile(b'g:AVOL=(20|[0-1]?[0-9])\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'e:[0-9A-F]{4}.*\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'Zoom': 'ZOOM',
            'True Size': 'TRUE'
        }

        AspectRatioCmdString = 'ASPECT={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'GET=ASPECT\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'AUTO': 'Auto',
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'ZOOM': 'Zoom',
            'TRUE': 'True Size'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AudioMuteCmdString = 'MUTE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'GET=MUTE\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'RC=AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBlank(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        BlankCmdString = 'BLANK={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)

    def UpdateBlank(self, value, qualifier):

        BlankCmdString = 'GET=BLANK\r'
        self.__UpdateHelper('Blank', BlankCmdString, value, qualifier)

    def __MatchBlank(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Blank', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'GET=ERR\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'NO_ERROR': 'No Error',
            'ABNORMAL_TEMPERATURE': 'Temperature Error',
            'FAULTY_LAMP': 'Lamp Error',
            'FAULTY_LAMP_COVER': 'Lamp Cover Error',
            'FAULTY_COOLING_FAN': 'Cooling Fan Error',
            'FAULTY_POWER_SUPPLY': 'Power Supply Error',
            'FAULTY_AIR_FILTER': 'Air Filter Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFocusContinuous(self, value, qualifier):

        ValueStateValues = {
            'Stop': 'STOP',
            'Far': 'FAR',
            'Near': 'NEAR'
        }

        FocusContinuousCmdString = 'FCONTDRV={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('FocusContinuous', FocusContinuousCmdString, value, qualifier)

    def SetFocusStep(self, value, qualifier):

        ValueStateValues = {
            'Far': 'FAR',
            'Near': 'NEAR'
        }

        FocusStepCmdString = 'FSTEPDRV={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('FocusStep', FocusStepCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = 'FREEZE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'GET=FREEZE\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': 'STANDARD',
            'Presentation': 'PRESENTATION',
            'VividPhoto': 'VIVID_PHOTO',
            'Photo/sRGB': 'PHOTO_SRGB',
            'Dynamic': 'DYNAMIC',
            'Video': 'VIDEO',
            'Cinema': 'CINEMA',
            'User 1': 'USER_1',
            'User 2': 'USER_2',
            'User 3': 'USER_3',
            'User 4': 'USER_4',
            'User 5': 'USER_5'
        }

        ImageModeCmdString = 'IMAGE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def UpdateImageMode(self, value, qualifier):

        ImageModeCmdString = 'GET=IMAGE\r'
        self.__UpdateHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def __MatchImageMode(self, match, tag):

        ValueStateValues = {
            'STANDARD': 'Standard',
            'PRESENTATION': 'Presentation',
            'VIVID_PHOTO': 'VividPhoto',
            'PHOTO_SRGB': 'Photo/sRGB',
            'DYNAMIC': 'Dynamic',
            'VIDEO': 'Video',
            'CINEMA': 'Cinema',
            'USER_1': 'User 1',
            'USER_2': 'User 2',
            'USER_3': 'User 3',
            'USER_4': 'User 4',
            'USER_5': 'User 5'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ImageMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 'HDMI',
            'Digital PC': 'D-RGB',
            'Analog PC 1': 'A-RGB1',
            'Analog PC 2': 'A-RGB2',
            'Component': 'COMP',
            'LAN': 'LAN',
            'USB': 'USB',
            'HDBaseT': 'HDBT'
        }

        InputCmdString = 'INPUT={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GET=INPUT\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HDMI': 'HDMI',
            'D-RGB': 'Digital PC',
            'A-RGB1': 'Analog PC 1',
            'A-RGB2': 'Analog PC 2',
            'COMP': 'Component',
            'LAN': 'LAN',
            'USB': 'USB',
            'HDBT': 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'FULL',
            'Eco': 'ECO'
        }

        LampModeCmdString = 'LAMP={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'GET=LAMP\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            'FULL': 'Normal',
            'ECO': 'Eco'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'GET=LMPT\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetLensPosition(self, value, qualifier):

        ValueStateValues = {
            'Load 1': '1',
            'Load 2': '2',
            'Load 3': '3'
        }

        LensPositionCmdString = 'LPOSLD={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LensPosition', LensPositionCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On': 'RC=MENU\r',
            'Menu Off': 'RC=EXIT\r',
            'Up': 'RC=UP\r',
            'Down': 'RC=DOWN\r',
            'Right': 'RC=RIGHT\r',
            'Left': 'RC=LEFT\r',
            'OK': 'RC=OK\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        PowerCmdString = 'POWER={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET=POWER\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
            'OFF2ON': 'Warming Up',
            'ON2OFF': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AVOL={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET=AVOL\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def UpdateSignalStatus(self, value, qualifier):

        SignalStatusCmdString = 'GET=SIGNALSTATUS\r'
        self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)

    def __MatchSignalStatus(self, match, tag):

        ValueStateValues = {
            'NO_SIGNAL': 'No Signal',
            'DISPLAYING': 'Displaying',
            'SETTING': 'Setting'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SignalStatus', value, None)

    def SetZoomContinuous(self, value, qualifier):

        ValueStateValues = {
            'Stop': 'STOP',
            'Wide': 'WIDE',
            'Tele': 'TELE'
        }

        ZoomContinuousCmdString = 'ZCONTDRV={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ZoomContinuous', ZoomContinuousCmdString, value, qualifier)

    def SetZoomStep(self, value, qualifier):

        ValueStateValues = {
            'Wide': 'WIDE',
            'Tele': 'TELE'
        }

        ZoomStepCmdString = 'ZSTEPDRV={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ZoomStep', ZoomStepCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=2, FlowControl='Off', CharDelay=0, Model=None):
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
