from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {}
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SideBySideMainInput': {'Status': {}},
            'SideBySideMode': {'Status': {}},
            'SideBySideSubInput': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'All':
            self._DeviceID = 'ZZ'
        elif 0 <= int(value) <= 65:
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['Device ID should be a value between 0 to 65 or All.'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Standard': '0',
            '4:3': '1',
            '16:9': '2',
            'Through': '5',
            'HV Fit': '6',
            'H Fit': '9',
            'V Fit': '10',
            'S1 Auto': '20',
            'Vid Auto': '30'
        }
        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';VSE:' + AspectRatioStateValues[value].encode() + b'\x03'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            b'0\x03': 'Standard',
            b'1\x03': '4:3',
            b'2\x03': '16:9',
            b'5\x03': 'Through',
            b'6\x03': 'HV Fit',
            b'9\x03': 'H Fit',
            b'10': 'V Fit',
            b'20': 'S1 Auto',
            b'30': 'Vid Auto',
        }

        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[1:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        AudioMuteCmdString = b'\x02AD' + self._DeviceID.encode() + b';AMT:' + AudioMuteStateValues[value].encode() + b'\x03'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02AD' + self._DeviceID.encode() + b';OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        AVMuteCmdString = b'\x02AD' + self._DeviceID.encode() + b';OSH:' + AVMuteStateValues[value].encode() + b'\x03'
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }
        AVMuteCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSH\x03'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = AVMuteStateNames[res[1:2]]
                self.WriteStatus('AVMute', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateValues = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
        }
        ClosedCaptionModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OCC:' + ClosedCaptionModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateNames = {
            b'0': 'Off',
            b'1': 'CC1',
            b'2': 'CC2',
            b'3': 'CC3',
            b'4': 'CC4'
        }
        ClosedCaptionModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QCC\x03'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionModeStateNames[res[1:2]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1',
            'Off': '0'
        }
        FreezeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OFZ:' + FreezeStateValues[value].encode() + b'\x03'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }

        FreezeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Network': 'NWP'
        }
        InputCmdString = b'\x02AD' + self._DeviceID.encode() + b';IIS:' + InputStateValues[value].encode() + b'\x03'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            b'RG1': 'RGB 1',
            b'RG2': 'RGB 2',
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'DVI': 'DVI',
            b'HD1': 'HDMI',
            b'NWP': 'Network'
        }
        InputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[1:4]]
                self.WriteStatus('Input', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Eco': '1',
            'Normal': '0'
        }
        LampModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OLP:' + LampModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStateNames = {
            b'0': 'Normal',
            b'1': 'Eco'
        }

        LampModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QLP\x03'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[1:2]]
                self.WriteStatus('LampMode', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x02AD' + self._DeviceID.encode() + b';Q$L\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:5])
                self.WriteStatus('LampUsage', value, qualifier)
            except  (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': b'OMN',
            'Up': b'OCU',
            'Down': b'OCD',
            'Left': b'OCL',
            'Right': b'OCR',
            'Enter': b'OEN',
            'Return': b'OBK'
        }

        MenuNavigationCmdString = b'\x02AD' + self._DeviceID.encode() + b';' + MenuNavigationStateValues[value] + b'\x03'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On': '1',
            'Off': '0'
        }
        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceID.encode() + b';OOS:' + OnScreenDisplayStateValues[value].encode() + b'\x03'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }

        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceID.encode() + b';QOS\x03'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateNames[res[1:2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02AD' + self._DeviceID.encode() + b';QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:6])
                self.WriteStatus('OperationHours', value, qualifier)
            except  (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural': 'NAT',
            'Standard': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM SIM': 'DIC',
            'REC709': '709'
        }
        PictureModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';VPM:' + PictureModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeStateNames = {
            b'NA': 'Natural',
            b'ST': 'Standard',
            b'DY': 'Dynamic',
            b'CI': 'Cinema',
            b'GR': 'Graphic',
            b'DI': 'DICOM SIM',
            b'70': 'REC709'
        }

        PictureModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:3]]
                self.WriteStatus('PictureMode', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = b'\x02AD' + self._DeviceID.encode() + b';' + PowerStateValues[value].encode() + b'\x03'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'2': 'On',
            b'1': 'Warming Up',
            b'3': 'Cooling Down',
            b'0': 'Off'
        }

        PowerCmdString = b'\x02AD' + self._DeviceID.encode() + b';Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSideBySideMainInput(self, value, qualifier):

        SideBySideMainInputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Network': 'NWP',
        }
        SideBySideMainInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';MSI:' + SideBySideMainInputStateValues[value].encode() + b'\x03'
        self.__SetHelper('SideBySideMainInput', SideBySideMainInputCmdString, value, qualifier)

    def UpdateSideBySideMainInput(self, value, qualifier):

        SideBySideMainInputStateNames = {
            b'RG1': 'RGB 1',
            b'RG2': 'RGB 2',
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'DVI': 'DVI',
            b'HD1': 'HDMI',
            b'NWP': 'Network'
        }

        SideBySideMainInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIM\x03'
        res = self.__UpdateHelper('SideBySideMainInput', SideBySideMainInputCmdString, value, qualifier)
        if res:
            try:
                value = SideBySideMainInputStateNames[res[1:4]]
                self.WriteStatus('SideBySideMainInput', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Side By Side Main Input: Invalid/unexpected response'])

    def SetSideBySideMode(self, value, qualifier):

        SideBySideModeStateValues = {
            'On': '1',
            'Off': '0'
        }
        SideBySideModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OPP:' + SideBySideModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('SideBySideMode', SideBySideModeCmdString, value, qualifier)

    def UpdateSideBySideMode(self, value, qualifier):

        SideBySideModeStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        SideBySideModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QPP\x03'
        res = self.__UpdateHelper('SideBySideMode', SideBySideModeCmdString, value, qualifier)
        if res:
            try:
                value = SideBySideModeStateNames[res[1:2]]
                self.WriteStatus('SideBySideMode', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Side By Side Mode: Invalid/unexpected response'])

    def SetSideBySideSubInput(self, value, qualifier):

        SideBySideSubInputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Network': 'NWP',
        }
        SideBySideSubInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';SIS:' + SideBySideSubInputStateValues[value].encode() + b'\x03'
        self.__SetHelper('SideBySideSubInput', SideBySideSubInputCmdString, value, qualifier)

    def UpdateSideBySideSubInput(self, value, qualifier):

        SideBySideSubInputStateNames = {
            b'RG1': 'RGB 1',
            b'RG2': 'RGB 2',
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'DVI': 'DVI',
            b'HD1': 'HDMI',
            b'NWP': 'Network'
        }

        SideBySideSubInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIS\x03'
        res = self.__UpdateHelper('SideBySideSubInput', SideBySideSubInputCmdString, value, qualifier)
        if res:
            try:
                value = SideBySideSubInputStateNames[res[1:4]]
                self.WriteStatus('SideBySideSubInput', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Side By Side Sub Input: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            VolumeCmdString = b'\x02AD' + self._DeviceID.encode() + b';AVL:' + str(value).zfill(3).encode() + b'\x03'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QAV\x03'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:4])
                self.WriteStatus('Volume', value, qualifier)
            except  (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02ER401\x03': "Invalid Command.",
            b'\x02ER402\x03': "Invalid Parameter"
        }
        if response in DEVICE_ERROR_CODES:
            self.Error([sourceCmdName + ' ' + DEVICE_ERROR_CODES[response]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
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
                return self.__CheckResponseForErrors(command, res)

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
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.devicePassword = 'panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
        }

        self.md5hash = ''
        self.Security = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = 'Admin'

    def __MatchNoAuthentication(self, match, tag):
        self.Security = 'Not Needed'

    def cmdBuild(self, commandstring):
        if self.Security == 'Admin':
            commandstring = self.md5hash + commandstring.encode()
        return commandstring

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = self.cmdBuild('%1AVMT 3{0}\r'.format(ValueStateValues[value]))
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '30': 'Off',
            '31': 'On'
        }

        AVMuteCmdString = self.cmdBuild('%1AVMT ?\r')
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AVMute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            5: 'Filter',
            6: 'Other'
        }

        DeviceStatusCmdString = self.cmdBuild('%1ERST ?\r')
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                ErrorStrings = res[7:-1]
                if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                    value = 'Normal'
                if ErrorStrings.count('1') + ErrorStrings.count('2') >= 2:
                    value = 'Multiple Errors/Warnings'
                elif ErrorStrings.count('1') == 1:
                    index = ErrorStrings.index('1')
                    value = '{0} Warning'.format(ValueStateValues[index + 1])
                elif ErrorStrings.count('2') == 1:
                    index = ErrorStrings.index('2')
                    value = '{0} Error'.format(ValueStateValues[index + 1])
                self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': '11',
            'RGB 2': '12',
            'Video': '21',
            'S-Video': '22',
            'DVI': '31',
            'HDMI': '32',
            'Network': '51'
        }

        InputCmdString = self.cmdBuild('%1INPT {0}\r'.format(ValueStateValues[value]))
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'RGB 1',
            '12': 'RGB 2',
            '21': 'Video',
            '22': 'S-Video',
            '31': 'DVI',
            '32': 'HDMI',
            '51': 'Network'
        }

        InputCmdString = self.cmdBuild('%1INPT ?\r')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = self.cmdBuild('%1LAMP ?\r')
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-3])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = self.cmdBuild('%1POWR {0}\r'.format(ValueStateValues[value]))
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warming Up',
            '2': 'Cooling Down'
        }

        PowerCmdString = self.cmdBuild('%1POWR ?\r')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERR1': "Undefined command.",
            'ERR2': "Out of parameter.",
            'ERR3': "Unavailable time.",
            'ERR4': "Projector failure.",
            'ERRA': "Invalid password."
        }

        if isinstance(response, bytes):
            response = response.decode()
        if 'ERR' in response:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[7:-1]])])
            if 'ERRA' in response:
                self.Security = 'None'
            response = ''
        elif 'PJLINK 1' in response:
            inStr = response[9:-1]  # Responses from projector
            outStr = inStr + self.devicePassword  # Encrypted password
            encrypted = hashlib.md5(outStr.encode())
            self.md5hash = hexlify(encrypted.digest())
            self.Security = 'Admin'
        elif 'PJLINK 0' in response:
            self.Security = 'Not Needed'
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')
            return ''

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Security in ['Admin', 'Not Needed']:

            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
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
                    self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)
            return ''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.md5hash = ''
        self.Security = None
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
        index = 0  # Start of possible good data

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
