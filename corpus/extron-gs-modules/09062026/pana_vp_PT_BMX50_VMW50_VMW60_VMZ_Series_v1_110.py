from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import binascii
import hashlib

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
        self.Models = {
            'PT-VMW50': self.pana_1_4192_A,
            'PT-VMW50U': self.pana_1_4192_A,
            'PT-VMZ50': self.pana_1_4192_A,
            'PT-VMZ50U': self.pana_1_4192_A,
            'PT-VMZ250T': self.pana_1_4192_A,
            'PT-VMZ60': self.pana_1_4192_A,
            'PT-VMW60': self.pana_1_4192_A,
            'PT-VMZ40': self.pana_1_4192_B,
            'PT-VMZ40U': self.pana_1_4192_B,
            'PT-BMX50': self.pana_1_4192_B,
            'PT-BMX50C': self.pana_1_4192_B,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LightUsage': {'Parameters':['Light Source'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
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
            self.Error(['Invalid Device ID Parameter.'])

    def construct_command(self, command, value=''):

        if value:
            return '\x02AD{id};{command}:{value}\x03'.format(id=self._DeviceID, command=command, value=value)

        return '\x02AD{id};{command}\x03'.format(id=self._DeviceID, command=command)
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto':     '0',
            'Normal':   '1',
            'Wide':     '2',
            'Native':   '5',
            'Full':     '6',
            'H-Fit':    '9',
            'V-Fit':    '10'
        }

        AspectRatioCmdString = self.construct_command('VSE', ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0':    'Auto',
            '1':    'Normal',
            '2':    'Wide',
            '5':    'Native',
            '6':    'Full',
            '9':    'H-Fit',
            '10':   'V-Fit'
        }

        AspectRatioCmdString = self.construct_command('QSE')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        AudioMuteCmdString = self.construct_command('AMT', ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = self.construct_command('QMT')
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.construct_command('OAS')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        AVMuteCmdString = self.construct_command('OSH', ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AVMuteCmdString = self.construct_command('QSH')
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4'
        }

        ClosedCaptionCmdString = self.construct_command('OCC', ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4'
        }

        ClosedCaptionCmdString = self.construct_command('QCC')
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = self.construct_command('QFI', '0')
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        FreezeCmdString = self.construct_command('OFZ', ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = self.construct_command('QFZ')
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self.construct_command('IIS', self.set_input_states[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.construct_command('QIN')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.get_input_states[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        if value in {'1', '2', '3', '4', '5', '6'}:
            KeypadCmdString = self.construct_command('ONK', value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateLightUsage(self, value, qualifier):

        lightSrc = int(qualifier['Light Source'])
        if lightSrc in [1,2]:
            LightUsageCmdString = self.construct_command('QVX', 'LRTS3=0{}'.format(lightSrc-1))
            res = self.__UpdateHelper('LightUsage', LightUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[10:-1])
                    self.WriteStatus('LightUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Light Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLightUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       'OCU',
            'Down':     'OCD',
            'Left':     'OCL',
            'Right':    'OCR',
            'Enter':    'OEN',
            'Menu':     'OMN',
            'Return':   'OBK'
        }

        MenuNavigationCmdString = self.construct_command(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        OnScreenDisplayCmdString = self.construct_command('OOS', ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = self.construct_command('QOS')
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = self.construct_command('QVX', 'RTMI0')
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[8:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic':      'DYN',
            'Natural':      'NAT',
            'Standard':     'STD',
            'Black Board':   'BBD',
            'White Board':   'WBD',
            'Cinema':       'CIN'
        }

        PictureModeCmdString = self.construct_command('VPM', ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'BBD': 'Black Board',
            'WBD': 'White Board',
            'CIN': 'Cinema'
        }

        PictureModeCmdString = self.construct_command('QPM')
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'PON',
            'Off':  'POF'
        }

        PowerCmdString = self.construct_command(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = self.construct_command('QPW')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.construct_command('AVL', '{:03d}'.format(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.construct_command('QAV')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            '\x02ER401\x03': 'Invalid command',
            '\x02ER402\x03': 'Invalid parameter'
        }

        if response in error_map:
            self.Error(['An error occurred: {command}: {error}.'.format(command=sourceCmdName, error=error_map[response])])
            response = ''

        return response

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
            
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_1_4192_A(self):
        self.set_input_states = {
            'Computer 1':       'RG1',
            'Computer 2':       'RG2',
            'Video':            'VID',
            'HDMI 1':           'HD1',
            'HDMI 2':           'HD2',
            'Network/USB':      'NWP',
            'Memory Viewer':    'MV1',
            'Digital Link':     'DL1'
        }

        self.get_input_states = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'NWP': 'Network/USB',
            'MV1': 'Memory Viewer',
            'DL1': 'Digital Link'
        }

    def pana_1_4192_B(self):
        self.set_input_states = {
            'Computer 1':       'RG1',
            'Computer 2':       'RG2',
            'Video':            'VID',
            'HDMI 1':           'HD1',
            'HDMI 2':           'HD2',
            'Network/USB':      'NWP',
            'Memory Viewer':    'MV1'
        }

        self.get_input_states = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'NWP': 'Network/USB',
            'MV1': 'Memory Viewer'
        }

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
        self.deviceUsername = 'Username'
        self.devicePassword = '@Panasonic'
        self.Models = {
            'PT-VMW50': self.pana_1_4192_A,
            'PT-VMW50U': self.pana_1_4192_A,
            'PT-VMZ50': self.pana_1_4192_A,
            'PT-VMZ50U': self.pana_1_4192_A,
            'PT-VMZ250T': self.pana_1_4192_A,
            'PT-VMZ60': self.pana_1_4192_A,
            'PT-VMW60': self.pana_1_4192_A,
            'PT-BMX50': self.pana_1_4192_B,
            'PT-BMX50C': self.pana_1_4192_B,
            'PT-VMZ40': self.pana_1_4192_B,
            'PT-VMZ40U': self.pana_1_4192_B,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LightUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
        }

        self.__is_authenticated = False
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchAuthentication, False)
            self.AddMatchString(re.compile(b'%1AVMT=(21|30|31)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'%1ERST=([012]{6})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'%2FILT=([0-9]{1,5})\r'), self.__MatchFilterUsage, None)
            self.AddMatchString(re.compile(b'%2FREZ=([01])\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'%1LAMP=([0-9]{1,5}) [01]\r'), self.__MatchLightUsage, None)
            self.AddMatchString(re.compile(b'%1POWR=([012])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ERR[1-4]\r|PJLINK ERRA\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        if tag:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.Send(binascii.hexlify(code_hash.digest()).decode() + '%1POWR ?\r')
        else:
            self.__is_authenticated = True

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '21',
            'Off':  '20'
        }

        AudioMuteCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '%1AVMT ?\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = match.group(1).decode()

        if value == '21':
            self.WriteStatus('AudioMute', 'On', None)
            self.WriteStatus('AVMute', 'Off', None)
        elif value == '30':
            self.WriteStatus('AudioMute', 'Off', None)
            self.WriteStatus('AVMute', 'Off', None)
        elif value == '31':
            self.WriteStatus('AudioMute', 'On', None)
            self.WriteStatus('AVMute', 'On', None)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '31',
            'Off':  '30'
        }

        AVMuteCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '%1ERST ?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '000000': 'Normal',
            '100000': 'Fan Warning',
            '200000': 'Fan Error',
            '010000': 'Lamp Warning',
            '020000': 'Lamp Error',
            '001000': 'Temperature Warning',
            '002000': 'Temperature Error',
            '000010': 'Filter Warning',
            '000020': 'Filter Error',
            '000001': 'Other Warning',
            '000002': 'Other Error'
        }

        value = ValueStateValues.get(match.group(1).decode(), 'Multiple Warnings/Errors')
        self.WriteStatus('DeviceStatus', value, None)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '%2FILT ?\r'
        self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)

    def __MatchFilterUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('FilterUsage', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        FreezeCmdString = '%2FREZ {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '%2FREZ ?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = '%1INPT {}\r'.format(self.set_input_states[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '%1INPT ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.get_input_states[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLightUsage(self, value, qualifier):

        LightUsageCmdString = '%1LAMP ?\r'
        self.__UpdateHelper('LightUsage', LightUsageCmdString, value, qualifier)

    def __MatchLightUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LightUsage', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0',
        }

        PowerCmdString = '%1POWR {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '%1POWR ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        if not self.__is_authenticated:
            self.__is_authenticated = True

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up':   '1',
            'Down': '0'
        }

        VolumeStepCmdString = '%2SVOL {}\r'.format(ValueStateValues[value])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.__is_authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.counter = 0

        err = match.group(0).decode().strip()

        if err == 'PJLINK ERRA':
            self.Error(['Log in failed. Please supply proper password.'])
            self.__is_authenticated = False
            return

        error_map = {
            'ERR1': 'Undefined command',
            'ERR2': 'Out of parameter',
            'ERR3': 'Unavailable time',
            'ERR4': 'Projector failure'
        }

        self.Error(['An error occurred: {}: {}'.format(err, error_map[err])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.__is_authenticated = False

    def pana_1_4192_A(self):
        self.set_input_states = {
            'Computer 1':       '11',
            'Computer 2':       '12',
            'Video':            '21',
            'HDMI 1':           '31',
            'HDMI 2':           '32',
            'Network':          '51',
            'Memory Viewer':    '41',
            'Digital Link':     '33'
        }

        self.get_input_states = {
            '11': 'Computer 1',
            '12': 'Computer 2',
            '21': 'Video',
            '31': 'HDMI 1',
            '32': 'HDMI 2',
            '51': 'Network',
            '41': 'Memory Viewer',
            '33': 'Digital Link'
        }

        self.AddMatchString(re.compile(b'%1INPT=(11|12|21|31|32|33|41|51)\r'), self.__MatchInput, None)

    def pana_1_4192_B(self):
        self.set_input_states = {
            'Computer 1':       '11',
            'Computer 2':       '12',
            'Video':            '21',
            'HDMI 1':           '31',
            'HDMI 2':           '32',
            'Network':          '51',
            'Memory Viewer':    '41'
        }

        self.get_input_states = {
            '11': 'Computer 1',
            '12': 'Computer 2',
            '21': 'Video',
            '31': 'HDMI 1',
            '32': 'HDMI 2',
            '51': 'Network',
            '41': 'Memory Viewer'
        }

        self.AddMatchString(re.compile(b'%1INPT=(11|12|21|31|32|41|51)\r'), self.__MatchInput, None)

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