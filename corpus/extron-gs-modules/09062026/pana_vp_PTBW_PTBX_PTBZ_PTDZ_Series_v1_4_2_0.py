from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify
from extronlib.system import Wait, ProgramLog

class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PT-VW530U': self.pana_1_764_GroupB,
            'PT-VX60': self.pana_1_764_GroupB,
            'PT-VX600': self.pana_1_764_GroupB,
            'PT-VZ570': self.pana_1_764_GroupB,
            'PT-VZ575N': self.pana_1_764_GroupA,
            'PT-VW535N': self.pana_1_764_GroupA,
            'PT-VX605N': self.pana_1_764_GroupA,
            'PT-BZ575NC': self.pana_1_764_GroupA,
            'PT-BW535NC': self.pana_1_764_GroupA,
            'PT-BX655NC': self.pana_1_764_GroupA,
            'PT-BZ570C': self.pana_1_764_GroupB,
            'PT-BW530C': self.pana_1_764_GroupB,
            'PT-BX650C': self.pana_1_764_GroupB,
            'PT-BX621C': self.pana_1_764_GroupB,
            'PT-BX620C': self.pana_1_764_GroupB,
            'PT-VW530': self.pana_1_764_GroupB,
            'PT-DZ870ULK': self.pana_1_764_GroupB,
            'PT-VW530AJ': self.pana_1_764_GroupB,
            'PT-VZ575NU': self.pana_1_764_GroupA,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ExhaustAirTemperature': {'Status': {}},
            'FilterCounterTimer': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'IntakeAirTemperature':  {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Model':{'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SerialNumber':{'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto': '\x02VSE:00\x03',
            'Normal': '\x02VSE:01\x03',
            'Wide': '\x02VSE:02\x03',
            'Native': '\x02VSE:05\x03',
            'Full': '\x02VSE:06\x03',
            'H-Fit': '\x02VSE:09\x03',
            'V-Fit': '\x02VSE:10\x03'
        }

        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Normal',
            '2': 'Wide',
            '5': 'Native',
            '6': 'Full',
            '9': 'H-Fit',
            '10': 'V-Fit'
        }

        AspectRatioCmdString = '\x02QS1\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateAspectRatio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03'
        }

        AudioMuteCmdString = AudioMuteValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteValues = {
            '1': 'On',
            '0': 'Off'
        }        

        AudioMuteCmdString = '\x02QMT\x03'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteValues[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateAudioMute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'Off': '\x02OCC:0\x03',
            'CC1': '\x02OCC:1\x03',
            'CC2': '\x02OCC:2\x03',
            'CC3': '\x02OCC:3\x03',
            'CC4': '\x02OCC:4\x03'
        }

        ClosedCaptionCmdString = ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            '0': 'Off',
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4'
        }       

        ClosedCaptionCmdString = '\x02QCC\x03'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateValues[res[1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateClosedCaption: Invalid/unexpected response'])

    def UpdateExhaustAirTemperature(self, value, qualifier):
       
        ExhaustAirTemperatureCmdString = '\x02QTM:1\x03'
        res = self.__UpdateHelper('ExhaustAirTemperature', ExhaustAirTemperatureCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:5])
                self.WriteStatus('ExhaustAirTemperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Exhaust Air Temperature: Invalid/unexpected response'])

    def SetFilterCounterTimer(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FilterCounterTimerCmdString = '\x02VXX:FCTI1=+{0:05d}\x03'.format(value)
            self.__SetHelper('FilterCounterTimer', FilterCounterTimerCmdString, value, qualifier)
        else:
            self.Error(['SetFilterCounterTimer: Invalid/unexpected response'])

    def UpdateFilterCounterTimer(self, value, qualifier):

        FilterCounterTimerCmdString = '\x02QVX:FCTI1\x03'
        res = self.__UpdateHelper('FilterCounterTimer', FilterCounterTimerCmdString, value, qualifier)
        if res:
            try:
                value = int(res[8:-1])
                self.WriteStatus('FilterCounterTimer', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['UpdateFilterCounterTimer: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '\x02QFI:0\x03'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['UpdateFilterUsage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '\x02OFZ:1\x03',
            'Off': '\x02OFZ:0\x03'
        }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '\x02QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateFreeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[1:4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateInput: Invalid/unexpected response'])
    
    def UpdateIntakeAirTemperature(self, value, qualifier):

        IntakeAirTemperatureCmdString = '\x02QTM:0\x03'
        res = self.__UpdateHelper('IntakeAirTemperature', IntakeAirTemperatureCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:5])
                self.WriteStatus('IntakeAirTemperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['IntakeAirTemperature: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal': '\x02OLP:1\x03',
            'Eco': '\x02OLP:0\x03'
        }

        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStateValues = {
            '1': 'Normal',
            '0': 'Eco'
        }

        LampModeCmdString = '\x02QLP\x03'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateValues[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateLampMode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '\x02Q$L\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:5])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['UpdateLampUsage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuStateValues = {
            'Menu': '\x02OMN\x03',
            'Enter': '\x02OEN\x03',
            'Up': '\x02OCU\x03',
            'Down': '\x02OCD\x03',
            'Left': '\x02OCL\x03',
            'Right': '\x02OCR\x03',
            'Return': '\x02OBK\x03'
        }

        MenuNavigationCmdString = MenuStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateModel(self, value, qualifier):

        ModelCmdString = '\x02QID\x03'
        res = self.__UpdateHelper('Model', ModelCmdString, value, qualifier)
        if res:
            try:
                value = res[1:-1]
                self.WriteStatus('Model', value, qualifier)
            except (IndexError):
                self.Error(['Model: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x02QVX:RTMI0\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[8:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['UpdateOperationHours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': '\x02VPM:DYN\x03',
            'Natural': '\x02VPM:NAT\x03',
            'Standard': '\x02VPM:STD\x03',
            'Blackboard': '\x02VPM:BBD\x03',
            'Cinema': '\x02VPM:CIN\x03',
            'Whiteboard': '\x02VPM:WBD\x03'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'BBD': 'Blackboard',
            'CIN': 'Cinema',
            'WBD': 'Whiteboard'
        }

        PictureModeCmdString = '\x02QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:4]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdatePictureMode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03',
        }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down'
        }

        PowerCmdString = '\x02Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdatePower: Invalid/unexpected response'])

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '\x02QSN\x03'
        res = self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)
        if res:
            try:
                value = res[1:-1]
                self.WriteStatus('SerialNumber', value, qualifier)
            except (IndexError):
                self.Error(['Serial Number: Invalid/unexpected response'])


    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': '\x02OSH:1\x03',
            'Off': '\x02OSH:0\x03'
        }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '\x02QSH\x03'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['UpdateVideoMute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 63
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '\x02AVL:{0:03d}\x03'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Error(['SetVolume: Invalid/unexpected response'])

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x02QAV\x03'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['UpdateVolume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {'\x02ER401\x03': "Invalid Command Reply.",
                              '\x02ER402\x03': "Invalid Parameter."}
        if response in DEVICE_ERROR_CODES:
            print('{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
        if not res:
            return ''
        else:
            return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_1_764_GroupA(self):
        self.InputStateValues = {
            'Computer 1': '\x02IIS:RG1\x03',
            'Computer 2': '\x02IIS:RG2\x03',
            'Video': '\x02IIS:VID\x03',
            'HDMI 1': '\x02IIS:HD1\x03',
            'HDMI 2': '\x02IIS:HD2\x03',
            'Network/USB': '\x02IIS:NWP\x03',
            'Panasonic Application': '\x02IIS:PA1\x03',
            'Miracast': '\x02IIS:MC1\x03',
            'Memory Viewer': '\x02IIS:MV1\x03',
            'Digital Link': '\x02IIS:DL1\x03'

        }
        self.InputStateNames = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'NWP': 'Network/USB',
            'PA1': 'Panasonic Application',
            'MC1': 'Miracast',
            'MV1': 'Memory Viewer',
            'DL1': 'Digital Link'

        }

    def pana_1_764_GroupB(self):

        self.InputStateValues = {
            'Computer 1': '\x02IIS:RG1\x03',
            'Computer 2': '\x02IIS:RG2\x03',
            'Video': '\x02IIS:VID\x03',
            'HDMI 1': '\x02IIS:HD1\x03',
            'HDMI 2': '\x02IIS:HD2\x03'
        }
        self.InputStateNames = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2'
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


class DeviceEthernetClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-BW530C': self.pana_1_764_GroupD,
            'PT-BW535NC': self.pana_1_764_GroupC,
            'PT-BX620C': self.pana_1_764_GroupD,
            'PT-BX621C': self.pana_1_764_GroupD,
            'PT-BX650C': self.pana_1_764_GroupD,
            'PT-BX655NC': self.pana_1_764_GroupC,
            'PT-BZ570C': self.pana_1_764_GroupD,
            'PT-BZ575NC': self.pana_1_764_GroupC,
            'PT-VW530': self.pana_1_764_GroupD,
            'PT-VW530U': self.pana_1_764_GroupD,
            'PT-VW535N': self.pana_1_764_GroupC,
            'PT-VX60': self.pana_1_764_GroupD,
            'PT-VX600': self.pana_1_764_GroupD,
            'PT-VX605N': self.pana_1_764_GroupC,
            'PT-VZ570': self.pana_1_764_GroupD,
            'PT-VZ575N': self.pana_1_764_GroupC,
            'PT-DZ870ULK': self.pana_1_764_GroupD,
            'PT-VW530AJ': self.pana_1_764_GroupD,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.md5hash = ''
        self.Security = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'NTCONTROL 0\r'), self.__MatchNoAuthentication, None)
            self.AddMatchString(re.compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def __MatchAuthentication(self, match, tag):

        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto': '0',
            'Normal': '1',
            'Wide': '2',
            'Native': '5',
            'Full': '6',
            'H-Fit': '9',
            'V-Fit': '10'
        }

        AspectRatioCmdString = '00VSE:{0}\r'.format(AspectRatioStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '00OAS\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '00OSH:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'Off': '0',
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4'
        }

        ClosedCaptionCmdString = '00OCC:{0}\r'.format(ClosedCaptionStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '00OFZ:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = '00IIS:{0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'OMN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
            'Enter': 'OEN',
            'Return': 'OBK'
        }

        MenuNavigationCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Blackboard': 'BBD',
            'Cinema': 'CIN',
            'Whiteboard': 'WBD'
        }

        PictureModeCmdString = '00VPM:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'AUU',
            'Down': 'AUD'
        }

        VolumeCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security is True:
            self.Send(self.md5hash + commandstring.encode())
        else:
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorValue = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            '5': 'Wrong data length',
            'A': 'Password mismatch',

        }
        self.Security = 'Not Authorized'
        value = match.group(1).decode()
        print(ErrorValue[value])

    def OnDisconnected(self):

        self.Security = False

    def pana_1_764_GroupC(self):

        self.InputStateValues = {
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'Network/USB': 'NWP',
            'Panasonic Application': 'PA1',
            'Miracast': 'MC1',
            'Memory Viewer': 'MV1',
            'Digital Link': 'DL1'

        }

    def pana_1_764_GroupD(self):

        self.InputStateValues = {
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2'
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
