from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = '\x02AD01;'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ExhaustAirTemperature': {'Parameters':['Type'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'LightTemperature': {'Parameters':['Light','Type'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'OperationMode': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '\x02ADZZ;'
        elif 1 <= int(value) <= 64:
            self._DeviceID = '\x02AD{0};'.format(value.zfill(2))
        else:
            self.Error(['Missing DeviceID Parameter. Range is from 1 to 64 or Broadcast'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'             : '0',
            'Normal (4:3)'     : '1',
            'Wide (16:9)'      : '2',
            'Native (Through)' : '5',
            'Full (HV Fit)'    : '6',
            'H-Fit'            : '9',
            'V-Fit'            : '10'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = '{0}VSE:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0'  : 'Auto',
            '1'  : 'Normal (4:3)',
            '2'  : 'Wide (16:9)',
            '5'  : 'Native (Through)',
            '6'  : 'Full (HV Fit)',
            '9'  : 'H-Fit',
            '10' : 'V-Fit'
        }

        AspectRatioCmdString = '{0}QSE\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '{0}AMT:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        AudioMuteCmdString = '{0}QMT\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '{0}OAS\x03'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1' : '1',
            'CC2' : '2',
            'CC3' : '3',
            'CC4' : '4',
            'Off' : '0'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = '{0}OCC:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '1' : 'CC1',
            '2' : 'CC2',
            '3' : 'CC3',
            '4' : 'CC4',
            '0' : 'Off'
        }

        ClosedCaptionCmdString = '{0}QCC\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateExhaustAirTemperature(self, value, qualifier):

        ExhaustAirTemperatureCmdString = '{0}QTM:1\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('ExhaustAirTemperature', ExhaustAirTemperatureCmdString, value, qualifier)
        if res:
            try:
                celsius = int(res[1:-1].split('/')[0])
                fahrenheit = int(res[1:-1].split('/')[1])
                self.WriteStatus('ExhaustAirTemperature', celsius, {'Type': 'Celsius'})
                self.WriteStatus('ExhaustAirTemperature', fahrenheit, {'Type': 'Fahrenheit'})
            except (ValueError, IndexError):
                self.Error(['Exhaust Air Temperature: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            FreezeCmdString = '{0}OFZ:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        FreezeCmdString = '{0}QFZ\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1'              : 'RG1',
            'Computer 2'              : 'RG2',
            'Video'                   : 'VID',
            'DVI'                     : 'DVI',
            'HDMI 1'                  : 'HD1',
            'HDMI 2'                  : 'HD2',
            'Digital Link'            : 'DL1',
            'Digital Link Computer 1' : 'DL1:PC1',
            'Digital Link Computer 2' : 'DL1:PC2',
            'Digital Link Video'      : 'DL1:VID',
            'Digital Link HDMI 1'     : 'DL1:HD1',
            'Digital Link HDMI 2'     : 'DL1:HD2'
        }

        if value in ValueStateValues:
            InputCmdString = '{0}IIS:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'RG1'     : 'Computer 1',
            'RG2'     : 'Computer 2',
            'VID'     : 'Video',
            'DVI'     : 'DVI',
            'HD1'     : 'HDMI 1',
            'HD2'     : 'HDMI 2',
            'DL1'     : 'Digital Link',
            'DL1:PC1' : 'Digital Link Computer 1',
            'DL1:PC2' : 'Digital Link Computer 2',
            'DL1:VID' : 'Digital Link Video',
            'DL1:HD1' : 'Digital Link HDMI 1',
            'DL1:HD2' : 'Digital Link HDMI 2'
        }

        InputCmdString = '{0}QIN\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '{0}Q$L:1\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def UpdateLightTemperature(self, value, qualifier):

        light = qualifier['Light']

        TypeStates = [
            'Celsius',
            'Fahrenheit'
        ]
        type_ = qualifier['Type']

        if light in ['1', '2'] and type_ in TypeStates:

            LightTemperatureCmdString = '{0}QTM:1{1}\x03'.format(self._DeviceID, light)
            res = self.__UpdateHelper('LightTemperature', LightTemperatureCmdString, value, qualifier)
            if res:
                try:
                    celsius = int(res[1:-1].split('/')[0])
                    fahrenheit = int(res[1:-1].split('/')[1])
                    self.WriteStatus('LightTemperature', celsius, {'Light': light, 'Type': 'Celsius'})
                    self.WriteStatus('LightTemperature', fahrenheit, {'Light': light, 'Type': 'Fahrenheit'})
                except (ValueError, IndexError):
                    self.Error(['Light Temperature: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLightTemperature')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'   : 'OMN',
            'Up'     : 'OCU',
            'Down'   : 'OCD',
            'Left'   : 'OCL',
            'Right'  : 'OCR',
            'Enter'  : 'OEN',
            'Return' : 'OBK'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '{0}{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = '{0}OOS:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        OnScreenDisplayCmdString = '{0}QOS\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '{0}QVX:RTMS1\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetOperationMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : '000',
            'Eco'    : '001',
            'Silent' : '002',
            'User'   : '101'
        }

        if value in ValueStateValues:
            OperationModeCmdString = '{0}VXX:OPEI1=+00{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOperationMode')

    def UpdateOperationMode(self, value, qualifier):

        ValueStateValues = {
            '000' : 'Normal',
            '001' : 'Eco',
            '002' : 'Silent',
            '101' : 'User'
        }

        OperationModeCmdString = '{0}QVX:OPEI1\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OperationMode', OperationModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:-1]]
                self.WriteStatus('OperationMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Operation Mode: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic'   : 'DYN',
            'Natural'   : 'NAT',
            'Standard'  : 'STD',
            'Cinema'    : 'CIN',
            'Graphic'   : 'GRA',
            'DICOM SIM' : 'DIC',
            'REC709'    : '709'
        }

        if value in ValueStateValues:
            PictureModeCmdString = '{0}VPM:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN' : 'Dynamic',
            'NAT' : 'Natural',
            'STD' : 'Standard',
            'CIN' : 'Cinema',
            'GRA' : 'Graphic',
            'DIC' : 'DICOM SIM',
            '709' : 'REC709'
        }

        PictureModeCmdString = '{0}QPM\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'    : '0',
            'User 1' : '1',
            'User 2' : '2',
            'User 3' : '3'
        }

        if value in ValueStateValues:
            PIPModeCmdString = '{0}OPP:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off',
            '1' : 'User 1',
            '2' : 'User 2',
            '3' : 'User 3'
        }

        PIPModeCmdString = '{0}QPP\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PON',
            'Off' : 'POF'
        }

        if value in ValueStateValues:
            PowerCmdString = '{0}{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        PowerCmdString = '{0}QPW\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open'  : '0',
            'Close' : '1'
        }

        if value in ValueStateValues:
            ShutterCmdString = '{0}OSH:{1}\x03'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Open',
            '1' : 'Close'
        }

        ShutterCmdString = '{0}QSH\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}AVL:{1}\x03'.format(self._DeviceID, str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '{0}QAV\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = { '\x02ER401\x03': 'Invalid Command',
                               '\x02ER402\x03': 'Invalid Parameter' }

        if isinstance(response, bytes):
            response = response.decode()
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '\x02ADZZ;':
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
                return self.__CheckResponseForErrors(command , res)

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
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
        self._DeviceID = 1
        self.deviceUsername = None
        self.devicePassword = 'panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters':['Type'], 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
        }

        self.md5hash = b''
        self.Authentication = 'Undetermined'
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)
            self.UpdateAVMuteMatch = re.compile('%1AVMT=([1-3][0-1])\r')
            self.UpdateDeviceStatusMatch = re.compile('%1ERST=([0-2]{6})\r')
            self.UpdateInputMatch = re.compile('%1INPT=([1-3][1236])\r')
            self.UpdateLampUsageMatch = re.compile('%1LAMP=([0-9]{1,5})')
            self.UpdatePowerMatch = re.compile('%1POWR=([0-3])\r')
            self.ErrorMatch = re.compile('ERR(1|2|3|4|A)\r')

    def __MatchAuthentication(self, match, tag):

        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Authentication = 'Authenticated'

    def __MatchNoAuthentication(self, match, tag):
        self.Authentication = 'Not Needed'

    def SetAVMute(self, value, qualifier):

        TypeStates = {
            'Audio' : '2',
            'Video' : '1',
            'Audio/Video' : '3'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off'  : '0'
        }

        if qualifier['Type'] in TypeStates and value in ValueStateValues:
            AVMuteCmdString = self.md5hash + '%1AVMT {0}{1}\r'.format(TypeStates[qualifier['Type']], ValueStateValues[value]).encode()
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            '10': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '11': {'Audio': 'Off', 'Video': 'On',  'Audio/Video': 'Off'},
            '20': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '21': {'Audio': 'On',  'Video': 'Off', 'Audio/Video': 'Off'},
            '30': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '31': {'Audio': 'On',  'Video': 'On',  'Audio/Video': 'On'}
        }

        AVMuteCmdString = self.md5hash + '%1AVMT ?\r'.encode()
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateAVMuteMatch, res)
                if matchObject:
                    AVMuteValues = AVMuteStateNames[matchObject.group(1)]
                    for Type in ['Audio', 'Video', 'Audio/Video']:
                        qualifier = {'Type': Type}
                        value = AVMuteValues[Type]
                        self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            1 : 'Fan',
            2 : 'Light Source',
            3 : 'Temp',
            6 : 'Other'
        }

        DeviceStatusCmdString = self.md5hash + '%1ERST ?\r'.encode()
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateDeviceStatusMatch, res)
                if matchObject:
                    ErrorStrings = matchObject.group(1)
                    if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                        value = 'Normal'
                    if ErrorStrings.count('1') + ErrorStrings.count('2') >= 2:
                        value = 'Multiple Errors/Warnings'
                    elif ErrorStrings.count('1') == 1:
                        index = ErrorStrings.index('1')
                        value = '{0} Warning'.format(ValueStateValues[index+1])
                    elif ErrorStrings.count('2') == 1:
                        index = ErrorStrings.index('2')
                        value = '{0} Error'.format(ValueStateValues[index+1])
                    self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1'   : '11',
            'Computer 2'   : '12',
            'Video'        : '21',
            'DVI'          : '31',
            'HDMI 1'       : '32',
            'HDMI 2'       : '36',
            'Digital Link' : '33'
        }

        if value in ValueStateValues:
            InputCmdString = self.md5hash + '%1INPT {0}\r'.format(ValueStateValues[value]).encode()
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11' : 'Computer 1',
            '12' : 'Computer 2',
            '21' : 'Video',
            '31' : 'DVI',
            '32' : 'HDMI 1',
            '36' : 'HDMI 2',
            '33' : 'Digital Link'
        }

        InputCmdString = self.md5hash + '%1INPT ?\r'.encode()
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateInputMatch, res)
                if matchObject:
                    value = '{0}'.format(ValueStateValues[matchObject.group(1)])
                    self.WriteStatus('Input', value, None)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = self.md5hash + '%1LAMP ?\r'.encode()
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateLampUsageMatch, res)
                if matchObject:
                    value = int(matchObject.group(1))
                    self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            PowerCmdString = self.md5hash + '%1POWR {0}\r'.format(ValueStateValues[value]).encode()
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off',
            '3' : 'Warming Up',
            '2' : 'Cooling Down'
        }

        PowerCmdString = self.md5hash + '%1POWR ?\r'.encode()
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdatePowerMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if 'ERR' in response:
            matchObject = re.search(self.ErrorMatch, response)
            if matchObject:
                DEVICE_ERROR_CODES = {
                    '1' : 'Undefined control command',
                    '2' : 'Out of parameter range',
                    '3' : 'Busy state or no-acceptable period',
                    '4' : 'Timeout or no-acceptable period',
                    'A' : 'Password mismatch'
                }

                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[matchObject.group(1)])])
                if 'ERRA' in response:
                    self.Authentication = 'Invalid'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authentication in ['Authenticated', 'Not Needed']:
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
                    return ''
                else:
                    return self.__CheckResponseForErrors(command , res)
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.md5hash = b''
        self.Authentication = 'Undetermined'

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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