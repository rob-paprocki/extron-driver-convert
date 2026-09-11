from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampControlStatus': {'Status': {}},
            'LampStatus': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPFrameLock': {'Status': {}},
            'PIPInput': {'Parameters': ['PIP Type'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '\x02ADZZ;'
        elif 'A' <= value <= 'Z' or 1 <= int(value) <= 64:
            self._DeviceID = '\x02AD' + str(value).zfill(2) + ';'
        else:
            self.Error(['Device ID should be a value between 1 and 64, or A thru Z, or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)': '1',
            'Wide (16:9)': '2',
            'Native': '5',
            'Full (HV Fit)': '6',
            'H-Fit': '9',
            'V-Fit': '10',
            'Default': '0',
        }

        AspectRatioCmdString = ''.join([self._DeviceID, 'VSE:', ValueStateValues[value], '\x03'])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Normal (4:3)',
            '2': 'Wide (16:9)',
            '5': 'Native',
            '6': 'Full (HV Fit)',
            '9': 'H-Fit',
            '10': 'V-Fit',
            '0': 'Default',
        }

        AspectRatioCmdString = ''.join([self._DeviceID, 'QSE\x03'])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        FreezeCmdString = ''.join([self._DeviceID, 'OFZ:', ValueStateValues[value], '\x03'])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        FreezeCmdString = ''.join([self._DeviceID, 'QFZ\x03'])
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Digital Link': 'DL1',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2',
            'Digital Link S-Video': 'DL1:SVD',
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'Y/C': 'SVD',
            'DVI': 'DVI',
            'HDMI 1': 'HD1',
            'SDI 1': 'SD1',
            'SDI 2': 'SD2',
        }

        InputCmdString = ''.join([self._DeviceID, 'IIS:', ValueStateValues[value], '\x03'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'DL1': 'Digital Link',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2',
            'DL1:SVD': 'Digital Link S-Video',
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'SVD': 'Y/C',
            'DVI': 'DVI',
            'HD1': 'HDMI 1',
            'SD1': 'SDI 1',
            'SD2': 'SDI 2',
        }

        InputCmdString = ''.join([self._DeviceID, 'QIN\x03'])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
        }

        KeypadCmdString = ''.join([self._DeviceID, 'ONK:', ValueStateValues[value], '\x03'])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampControlStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Lamp Off',
            '1': 'In turning On',
            '2': 'Lamp On',
            '3': 'Lamp Cooling',
        }

        LampControlStatusCmdString = ''.join([self._DeviceID, 'Q$S\x03'])
        res = self.__UpdateHelper('LampControlStatus', LampControlStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampControlStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Control Status: Invalid/unexpected response'])

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'All Off',
            '1': 'Lamp 1 On',
            '2': 'Lamp 2 On',
            '3': 'All On',
        }

        LampStatusCmdString = ''.join([self._DeviceID, 'QLS\x03'])
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Status: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if 1 <= int(lamp) <= 2:
            LampUsageCmdString = ''.join([self._DeviceID, 'Q$L:{0}\x03'.format(lamp)])
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'OMN',
            'Enter': 'OEN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
        }

        MenuNavigationCmdString = ''.join([self._DeviceID, ValueStateValues[value], '\x03'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM SIM': 'DIC',
            'User': 'USR',
        }

        PictureModeCmdString = ''.join([self._DeviceID, 'VPM:', ValueStateValues[value], '\x03'])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM SIM',
            'USR': 'User',
        }

        PictureModeCmdString = ''.join([self._DeviceID, 'QPM\x03'])
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            'Main Window': '0',
            'Sub Window': '1',
        }

        PIPFrameLockCmdString = ''.join([self._DeviceID, 'PFL:', ValueStateValues[value], '\x03'])
        self.__SetHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)

    def UpdatePIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            '0': 'Main Window',
            '1': 'Sub Window',
        }

        PIPFrameLockCmdString = ''.join([self._DeviceID, 'QPF\x03'])
        res = self.__UpdateHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPFrameLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Frame Lock: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main': 'MSI:',
            'Sub': 'SIS:',
        }

        ValueStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'SDI 1': 'SD1',
            'SDI 2': 'SD2',
        }

        pip_type = qualifier['PIP Type']
        if pip_type in PIPTypeStates and value in ValueStateValues:
            PIPInputCmdString = ''.join([self._DeviceID, PIPTypeStates[pip_type], ValueStateValues[value], '\x03'])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main': 'QIM',
            'Sub': 'QIS',
        }

        ValueStateValues = {
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'DVI': 'DVI',
            'HD1': 'HDMI',
            'SD1': 'SDI 1',
            'SD2': 'SDI 2',
        }

        pip_type = qualifier['PIP Type']
        if pip_type in PIPTypeStates:
            PIPInputCmdString = ''.join([self._DeviceID, PIPTypeStates[pip_type], '\x03'])
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[1:-1]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
        }

        PIPModeCmdString = ''.join([self._DeviceID, 'OPP:', ValueStateValues[value], '\x03'])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3',
        }

        PIPModeCmdString = ''.join([self._DeviceID, 'QPP\x03'])
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF',
        }

        PowerCmdString = ''.join([self._DeviceID, ValueStateValues[value], '\x03'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        PowerCmdString = ''.join([self._DeviceID, 'QPW\x03'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        ShutterCmdString = ''.join([self._DeviceID, 'OSH:', ValueStateValues[value], '\x03'])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        ShutterCmdString = ''.join([self._DeviceID, 'QSH\x03'])
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Invalid Command.',
            '\x02ER402\x03': 'Invalid Parameter',
        }

        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
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
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPFrameLock': { 'Status': {}},
            'PIPInput': {'Parameters': ['PIP Type'], 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Shutter': { 'Status': {}},
        }

        self.md5hash = ''
        self.Security = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)':  '1', 
            'Wide (16:9)':   '2', 
            'Native':        '5', 
            'Full (HV Fit)': '6', 
            'H-Fit':         '9', 
            'V-Fit':         '10', 
            'Default':       '0',
        }

        AspectRatioCmdString = '00VSE:{}\r'.format(ValueStateValues[value])
        if self.Security:
            AspectRatioCmdString = b''.join([self.md5hash, AspectRatioCmdString.encode()])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  '1', 
            'Off': '0',
        }

        FreezeCmdString = '00OFZ:{}\r'.format(ValueStateValues[value])
        if self.Security:
            FreezeCmdString = b''.join([self.md5hash, FreezeCmdString.encode()])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Digital Link':              'DL1', 
            'Digital Link Computer 1':   'DL1:PC1', 
            'Digital Link Computer 2':   'DL1:PC2', 
            'Digital Link Video':        'DL1:VID', 
            'Digital Link HDMI 1':       'DL1:HD1', 
            'Digital Link HDMI 2':       'DL1:HD2', 
            'Digital Link S-Video':      'DL1:SVD', 
            'Computer 1':                'RG1', 
            'Computer 2':                'RG2', 
            'Video':                     'VID', 
            'Y/C':                       'SVD', 
            'DVI':                       'DVI', 
            'HDMI 1':                    'HD1', 
            'SDI 1':                     'SD1', 
            'SDI 2':                     'SD2',
        }

        InputCmdString = '00IIS:{}\r'.format(ValueStateValues[value])
        if self.Security:
            InputCmdString = b''.join([self.md5hash, InputCmdString.encode()])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '0', 
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4', 
            '5': '5', 
            '6': '6', 
            '7': '7', 
            '8': '8', 
            '9': '9',
        }

        KeypadCmdString = '00ONK:{}\r'.format(ValueStateValues[value])
        if self.Security:
            KeypadCmdString = b''.join([self.md5hash, KeypadCmdString.encode()])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':  'OMN', 
            'Enter': 'OEN', 
            'Up':    'OCU', 
            'Down':  'OCD', 
            'Left':  'OCL', 
            'Right': 'OCR',
        }

        MenuNavigationCmdString = '00{}\r'.format(ValueStateValues[value])
        if self.Security:
            MenuNavigationCmdString = b''.join([self.md5hash, MenuNavigationCmdString.encode()])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic':   'DYN', 
            'Natural':   'NAT', 
            'Standard':  'STD', 
            'Cinema':    'CIN', 
            'Graphic':   'GRA', 
            'DICOM SIM': 'DIC', 
            'User':      'USR',
        }

        PictureModeCmdString = '00VPM:{}\r'.format(ValueStateValues[value])
        if self.Security:
            PictureModeCmdString = b''.join([self.md5hash, PictureModeCmdString.encode()])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            'Main Window': '0', 
            'Sub Window':  '1',
        }

        PIPFrameLockCmdString = '00PFL:{}\r'.format(ValueStateValues[value])
        if self.Security:
            PIPFrameLockCmdString = b''.join([self.md5hash, PIPFrameLockCmdString.encode()])
        self.__SetHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main': 'MSI:', 
            'Sub':  'SIS:',
        }
        
        ValueStateValues = {
            'RGB 1': 'RG1', 
            'RGB 2': 'RG2', 
            'DVI':   'DVI', 
            'HDMI':  'HD1', 
            'SDI 1': 'SD1', 
            'SDI 2': 'SD2',
        }
        
        pip_type = qualifier['PIP Type']
        if pip_type in PIPTypeStates and value in ValueStateValues:
            PIPInputCmdString = '00{}{}\r'.format(PIPTypeStates[pip_type], ValueStateValues[value])
            if self.Security:
                PIPInputCmdString = b''.join([self.md5hash, PIPInputCmdString.encode()])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off':    '0',
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
        }

        PIPModeCmdString = '00OPP:{}\r'.format(ValueStateValues[value])
        if self.Security:
            PIPModeCmdString = b''.join([self.md5hash, PIPModeCmdString.encode()])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '00POF\r'
        if self.Security:
            PowerOffCmdString = b''.join([self.md5hash, PowerOffCmdString.encode()])
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        ShutterCmdString = '00OSH:{}\r'.format(ValueStateValues[value])
        if self.Security:
            ShutterCmdString = b''.join([self.md5hash, ShutterCmdString.encode()])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorValue = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            '5': 'Wrong data length',
            'A': 'Password mismatch',
        }

        value = match.group(1).decode()
        self.Error([ErrorValue[value]])

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
