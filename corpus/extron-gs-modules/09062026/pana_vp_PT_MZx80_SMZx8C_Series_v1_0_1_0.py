from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from re import compile, search
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
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampControlStatus': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ZZ'
        elif 1 <= int(value) <= 64:
            self._DeviceID = '{:02d}'.format(int(value))
        else:
            print('Invalid Device ID Parameter.')

    def construct_cmd(self, command, value=None):

        if value:
            cmd = '\x02AD{id};{command}:{value}\x03'.format(id=self._DeviceID, command=command, value=value)
        else:
            cmd = '\x02AD{id};{command}\x03'.format(id=self._DeviceID, command=command)
        return cmd

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            '4:3': '1',
            'Wide': '2',
            'Native': '5',
            'Full': '6',
            'H Fit': '9',
            'V Fit': '10',
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.construct_cmd('VSE', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.construct_cmd('QSE')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '0': 'Normal',
                    '1': '4:3',
                    '2': 'Wide',
                    '5': 'Native',
                    '6': 'Full',
                    '9': 'H Fit',
                    '10': 'V Fit',
                }
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            AudioMuteCmdString = self.construct_cmd('AMT', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.construct_cmd('QMT')
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off',
                }

                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.construct_cmd('OAS')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = self.construct_cmd('QFI', '0')
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            FreezeCmdString = self.construct_cmd('OFZ', ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = self.construct_cmd('QFZ')
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off',
                }
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer': 'RG1',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'HDMI 3': 'HD3',
            'Digital Link': 'DL1',
        }

        if value in ValueStateValues:
            InputCmdString = self.construct_cmd('IIS', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.construct_cmd('QIN')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'RG1': 'Computer',
                    'HD1': 'HDMI 1',
                    'HD2': 'HDMI 2',
                    'HD3': 'HDMI 3',
                    'DL1': 'Digital Link',
                }
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = tuple(str(i) for i in range(0, 10))

        if value in ValueStateValues:
            KeypadCmdString = self.construct_cmd('ONK', value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateLampControlStatus(self, value, qualifier):

        LampControlStatusCmdString = self.construct_cmd('Q$S')
        res = self.__UpdateHelper('LampControlStatus', LampControlStatusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '0': 'Lamp Off',
                    '1': 'In turning On',
                    '2': 'Lamp On',
                    '3': 'Lamp Cooling',
                }

                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampControlStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Control Status: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = self.construct_cmd('Q$L', '1')
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'OMN',
            'Return': 'OBK',
            'Enter': 'OEN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.construct_cmd(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = self.construct_cmd('QVX', 'RTMI0')
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Whiteboard': 'WBD',
            'Cinema': 'CIN',
            'DICOM SIM': 'DIC',
        }

        if value in ValueStateValues:
            PictureModeCmdString = self.construct_cmd('VPM', ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = self.construct_cmd('QPM')
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'DYN': 'Dynamic',
                    'NAT': 'Natural',
                    'STD': 'Standard',
                    'WBD': 'Whiteboard',
                    'CIN': 'Cinema',
                    'DIC': 'DICOM SIM',
                }
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF',
        }

        if value in ValueStateValues:
            PowerCmdString = self.construct_cmd(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.construct_cmd('QPW')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off',
                }

                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            ShutterCmdString = self.construct_cmd('OSH', ValueStateValues[value])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = self.construct_cmd('QSH')
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off',
                }
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.construct_cmd('AVL', '{:03d}'.format(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.construct_cmd('QAV')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                if 0 <= value <= 63:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Invalid Command.',
            '\x02ER402\x03': 'Invalid Parameter',
        }

        if response in DEVICE_ERROR_CODES:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

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

        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.deviceUsername = 'dispadmin'
        self.devicePassword = ''
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.md5hash = ''
        self.Security = False

        self.AddMatchString(compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = ''.join([self.deviceUsername, ':', self.devicePassword, ':', rand_num])
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            '4:3':    '1',
            'Wide':   '2',
            'Native': '5',
            'Full':   '6',
            'H Fit':  '9',
            'V Fit':  '10',
        }

        if value in ValueStateValues:
            AspectRatioCmdString = '00VSE:{}\r'.format(ValueStateValues[value])
            if self.Security:
                AspectRatioCmdString = b''.join([self.md5hash, AspectRatioCmdString.encode()])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '00AMT:{}\r'.format(ValueStateValues[value])
            if self.Security:
                AudioMuteCmdString = b''.join([self.md5hash, AudioMuteCmdString.encode()])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '00OAS\r'
        if self.Security:
            AutoImageCmdString = b''.join([self.md5hash, AutoImageCmdString.encode()])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            FreezeCmdString = '00OFZ:{}\r'.format(ValueStateValues[value])
            if self.Security:
                FreezeCmdString = b''.join([self.md5hash, FreezeCmdString.encode()])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer':     'RG1',
            'HDMI 1':       'HD1',
            'HDMI 2':       'HD2',
            'HDMI 3':       'HD3',
            'Digital Link': 'DL1',
        }

        if value in ValueStateValues:
            InputCmdString = '00IIS:{}\r'.format(ValueStateValues[value])
            if self.Security:
                InputCmdString = b''.join([self.md5hash, InputCmdString.encode()])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = tuple(str(i) for i in range(0, 10))

        if value in ValueStateValues:
            KeypadCmdString = '00ONK:{}\r'.format(value)
            if self.Security:
                KeypadCmdString = b''.join([self.md5hash, KeypadCmdString.encode()])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':   'OMN',
            'Return': 'OBK',
            'Enter':  'OEN',
            'Up':     'OCU',
            'Down':   'OCD',
            'Left':   'OCL',
            'Right':  'OCR',
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '00{}\r'.format(ValueStateValues[value])
            if self.Security:
                MenuNavigationCmdString = b''.join([self.md5hash, MenuNavigationCmdString.encode()])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic':    'DYN',
            'Natural':    'NAT',
            'Standard':   'STD',
            'Whiteboard': 'WBD',
            'Cinema':     'CIN',
            'DICOM SIM':  'DIC',
        }

        if value in ValueStateValues:
            PictureModeCmdString = '00VPM:{}\r'.format(ValueStateValues[value])
            if self.Security:
                PictureModeCmdString = b''.join([self.md5hash, PictureModeCmdString.encode()])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')
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

        if value in ValueStateValues:
            ShutterCmdString = '00OSH:{}\r'.format(ValueStateValues[value])
            if self.Security:
                ShutterCmdString = b''.join([self.md5hash, ShutterCmdString.encode()])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '00AVL:{:03d}\r'.format(value)
            if self.Security:
                VolumeCmdString = b''.join([self.md5hash, VolumeCmdString.encode()])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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
                result = search(regexString, self.__receiveBuffer)
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
