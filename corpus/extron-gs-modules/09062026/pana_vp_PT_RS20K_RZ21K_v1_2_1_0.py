from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LaserHours': {'Parameters': ['Laser'], 'Status': {}},
            'LaserStatus': {'Parameters': ['Laser'], 'Status': {}},
            'LensShiftHorizontal': {'Parameters':['Speed'], 'Status': {}},
            'LensShiftVertical': {'Parameters':['Speed'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPFrameLock': { 'Status': {}},
            'PIPInput': {'Parameters': ['PIP Type'], 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ZZ'
        elif 'A' <= value <= 'Z':
            self._DeviceID = '0{}'.format(value)
        elif 1 <= int(value) <= 64:
            self._DeviceID = '{:02d}'.format(int(value))
        else:
            print('Invalid Device ID Parameter.')

    def construct_command(self, command, value=''):

        if value:
            return '\x02AD{id};{command}:{value}\x03'.format(id=self._DeviceID, command=command, value=value)

        return '\x02AD{id};{command}\x03'.format(id=self._DeviceID, command=command)
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)':     '1',
            'Wide (16:9)':      '2',
            'Native':           '5',
            'Full (HV Fit)':    '6',
            'H-Fit':            '9',
            'V-Fit':            '10',
            'Default':          '0'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.construct_command('VSE', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1':    'Normal (4:3)',
            '2':    'Wide (16:9)',
            '5':    'Native',
            '6':    'Full (HV Fit)',
            '9':    'H-Fit',
            '10':   'V-Fit',
            '0':    'Default'
        }

        AspectRatioCmdString = self.construct_command('QSE')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            'Slow': '0',
            'Normal': '1',
            'Fast': '2'
        }

        ValueStateValues = {
            'Far': '0',
            'Near': '1'
        }

        if qualifier['Speed'] in SpeedStates and value in ValueStateValues:
            FocusCmdString = self.construct_command('VXX', 'LNSI4=+00{}0{}'.format(SpeedStates[qualifier['Speed']], ValueStateValues[value]))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            FreezeCmdString = self.construct_command('OFZ', ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

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

        ValueStateValues = {
            'Computer 1':               'RG1',
            'Computer 2':               'RG2',
            'DVI':                      'DVI',
            'HDMI':                     'HD1',
            'SDI 1':                    'SD1',
            'SDI 2':                    'SD2',
            'Digital Link':             'DL1',
            'Digital Link Computer 1':  'DL1:PC1',
            'Digital Link Computer 2':  'DL1:PC2',
            'Digital Link Video':       'DL1:VID',
            'Digital Link HDMI 1':      'DL1:HD1',
            'Digital Link HDMI 2':      'DL1:HD2',
            'Digital Link S-Video':     'DL1:SVD'
        }

        if value in ValueStateValues:
            InputCmdString = self.construct_command('IIS', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'RG1':      'Computer 1',
            'RG2':      'Computer 2',
            'DVI':      'DVI',
            'HD1':      'HDMI',
            'SD1':      'SDI 1',
            'SD2':      'SDI 2',
            'DL1':      'Digital Link',
            'DL1:PC1':  'Digital Link Computer 1',
            'DL1:PC2':  'Digital Link Computer 2',
            'DL1:VID':  'Digital Link Video',
            'DL1:HD1':  'Digital Link HDMI 1',
            'DL1:HD2':  'Digital Link HDMI 2',
            'DL1:SVD':  'Digital Link S-Video'
        }

        InputCmdString = self.construct_command('QIN')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = self.construct_command('ONK', value.strip())
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateLaserHours(self, value, qualifier):

        laser = qualifier['Laser']

        if laser in {'1', '2'}:
            LaserHoursCmdString = self.construct_command('QVX', 'LRTS3=0{}'.format(int(laser) - 1))
            res = self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[10:-1])
                    self.WriteStatus('LaserHours', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Laser Hours: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLaserHours')

    def UpdateLaserStatus(self, value, qualifier):

        laser = qualifier['Laser']

        ValueStateValues = {
            '0': ('Off',    'Off'),
            '1': ('On',     'Off'),
            '2': ('Off',    'On'),
            '3': ('On',     'On')
        }

        if laser in {'1', '2'}:
            LaserStatusCmdString = self.construct_command('QLS')
            res = self.__UpdateHelper('LaserStatus', LaserStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]

                    self.WriteStatus('LaserStatus', value[0], {'Laser': '1'})
                    self.WriteStatus('LaserStatus', value[1], {'Laser': '2'})
                except (KeyError, IndexError):
                    self.Error(['Laser Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLaserStatus')

    def SetLensShiftHorizontal(self, value, qualifier):

        SpeedStates = {
            'Slow': '0',
            'Normal': '1',
            'Fast': '2'
        }

        ValueStateValues = {
            'Left': '0',
            'Right': '1'
        }

        if qualifier['Speed'] in SpeedStates and value in ValueStateValues:
            LensShiftHorizontalCmdString = self.construct_command('VXX', 'LNSI2=+00{}0{}'.format(
                SpeedStates[qualifier['Speed']], ValueStateValues[value]))
            self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensShiftHorizontal')

    def SetLensShiftVertical(self, value, qualifier):

        SpeedStates = {
            'Slow': '0',
            'Normal': '1',
            'Fast': '2'
        }

        ValueStateValues = {
            'Up': '0',
            'Down': '1'
        }

        if qualifier['Speed'] in SpeedStates and value in ValueStateValues:
            LensShiftVerticalCmdString = self.construct_command('VXX', 'LNSI3=+00{}0{}'.format(
                SpeedStates[qualifier['Speed']], ValueStateValues[value]))
            self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensShiftVertical')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       'OCU',
            'Down':     'OCD',
            'Left':     'OCL',
            'Right':    'OCR',
            'Menu':     'OMN',
            'Enter':    'OEN'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.construct_command(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
            
    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = self.construct_command('OOS', ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

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

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic':      'DYN',
            'Natural':      'NAT',
            'Standard':     'STD',
            'Cinema':       'CIN',
            'Graphic':      'GRA',
            'DICOM SIM':    'DIC',
            'User':         'USR'
        }

        if value in ValueStateValues:
            PictureModeCmdString = self.construct_command('VPM', ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM SIM',
            'USR': 'User'
        }

        PictureModeCmdString = self.construct_command('QPM')
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            'Main Window':  '0',
            'Sub Window':   '1'
        }

        if value in ValueStateValues:
            PIPFrameLockCmdString = self.construct_command('PFL', ValueStateValues[value])
            self.__SetHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPFrameLock')

    def UpdatePIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            '0': 'Main Window',
            '1': 'Sub Window'
        }

        PIPFrameLockCmdString = self.construct_command('QPF')
        res = self.__UpdateHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PIPFrameLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Frame Lock: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main': 'MSI',
            'Sub':  'SIS'
        }
        pip_type = qualifier['PIP Type']

        ValueStateValues = {
            'Computer 1':   'RG1',
            'Computer 2':   'RG2',
            'DVI':          'DVI',
            'HDMI':         'HD1',
            'SDI 1':        'SD1',
            'SDI 2':        'SD2'
        }

        if pip_type in PIPTypeStates and value in ValueStateValues:
            PIPInputCmdString = self.construct_command(PIPTypeStates[pip_type], ValueStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main': 'QIM',
            'Sub':  'QIS'
        }
        pip_type = qualifier['PIP Type']

        ValueStateValues = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'DVI': 'DVI',
            'HD1': 'HDMI',
            'SD1': 'SDI 1',
            'SD2': 'SDI 2'
        }

        if pip_type in PIPTypeStates:
            PIPInputCmdString = self.construct_command(PIPTypeStates[pip_type])
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
            'Off':      '0',
            'User 1':   '1',
            'User 2':   '2',
            'User 3':   '3'
        }

        if value in ValueStateValues:
            PIPModeCmdString = self.construct_command('OPP', ValueStateValues[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3'
        }

        PIPModeCmdString = self.construct_command('QPP')
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'PON',
            'Off':  'POF',
        }

        if value in ValueStateValues:
            PowerCmdString = self.construct_command(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

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

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9'
        }

        if value in ValueStateValues:
            PresetRecallCmdString = self.construct_command('VXX', 'LNMI1=+0000{}'.format(ValueStateValues[value]))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9'
        }

        if value in ValueStateValues:
            PresetSaveCmdString = self.construct_command('VXX', 'LNMI2=+0000{}'.format(ValueStateValues[value]))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = self.construct_command('OSH', ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = self.construct_command('QSH')
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            'Slow': '0',
            'Normal': '1',
            'Fast': '2'
        }

        ValueStateValues = {
            'Tele': '0',
            'Wide': '1'
        }

        if qualifier['Speed'] in SpeedStates and value in ValueStateValues:
            ZoomCmdString = self.construct_command('VXX', 'LNSI5=+00{}0{}'.format(SpeedStates[qualifier['Speed']], ValueStateValues[value]))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ' or '0A' <= self._DeviceID <= '0Z':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ' or '0A' <= self._DeviceID <= '0Z':
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
        self.deviceUsername = 'dispadmin'
        self.devicePassword = '@Panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LaserHours': {'Parameters': ['Laser'], 'Status': {}},
            'LaserStatus': {'Parameters': ['Laser'], 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
        }

        self.is_authenticated = False
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%1POWR=([012])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchAuthentication, False)

            self.AddMatchString(re.compile(b'ERR[1-4]\r|PJLINK ERRA\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):

        if tag:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.Send(binascii.hexlify(code_hash.digest()).decode() + '%1POWR ?\r')
        else:
            self.is_authenticated = True
    
    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '000000': 'Normal',
            '100000': 'Fan Warning',
            '200000': 'Fan Error',
            '010000': 'Light Warning',
            '020000': 'Light Error',
            '001000': 'Temperature Warning',
            '002000': 'Temperature Error',
            '000001': 'Other Warning',
            '000002': 'Other Error'
        }

        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res.strip().split('=')[-1], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            FreezeCmdString = '%2FREZ {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '%2FREZ ?\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1':   '11',
            'Computer 2':   '12',
            'DVI':          '31',
            'HDMI':         '32',
            'Digital Link': '33',
            'SDI 1':        '34',
            'SDI 2':        '35'
        }

        if value in ValueStateValues:
            InputCmdString = '%2INPT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'Computer 1',
            '12': 'Computer 2',
            '31': 'DVI',
            '32': 'HDMI',
            '33': 'Digital Link',
            '34': 'SDI 1',
            '35': 'SDI 2'
        }

        InputCmdString = '%2INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLaserHours(self, value, qualifier):

        laser = qualifier['Laser']

        if laser in ['1', '2']:

            LaserHoursCmdString = '%1LAMP ?\r'
            res = self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)
            if res:
                res = res.strip().split('=')[-1].split()

                try:
                    self.WriteStatus('LaserHours', int(res[0]), {'Laser': '1'})
                    self.WriteStatus('LaserHours', int(res[2]), {'Laser': '2'})
                except (ValueError, IndexError):
                    self.Error(['Laser Hours: Invalid/unexpected response'])

                try:
                    LaserStatus_ValueStateValues = {
                        '1': 'On',
                        '0': 'Off'
                    }

                    self.WriteStatus('LaserStatus', LaserStatus_ValueStateValues[res[1]], {'Laser': '1'})
                    self.WriteStatus('LaserStatus', LaserStatus_ValueStateValues[res[3]], {'Laser': '2'})
                except (KeyError, IndexError):
                    self.Error(['Laser Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLaserHours')

    def UpdateLaserStatus(self, value, qualifier):

        self.UpdateLaserHours(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0',
        }

        if value in ValueStateValues:
            PowerCmdString = '%1POWR {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Cooling Down'
        }

        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __MatchPower(self, match, tag):

        if not self.is_authenticated:
            self.is_authenticated = True

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '31',
            'Off':  '30'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '31': 'On',
            '30': 'Off'
        }

        VideoMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            'ERR1': 'Undefined command',
            'ERR2': 'Out of parameter',
            'ERR3': 'Unavailable time',
            'ERR4': 'Projector failure'
        }

        err = response.strip().split('=')[-1]

        if err == 'PJLINK ERRA':
            self.Error(['Log in failed. Please supply proper password.'])
            self.is_authenticated = False
            return ''
        elif err in error_map:
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map[err])])
            return ''

        return response

    def __MatchError(self, match, tag):
        self.counter = 0

        err = match.group(0).decode().strip()

        if err == 'PJLINK ERRA':
            self.Error(['Log in failed. Please supply proper password.'])
            self.is_authenticated = False
            return

        error_map = {
            'ERR1': 'Undefined command',
            'ERR2': 'Out of parameter',
            'ERR3': 'Unavailable time',
            'ERR4': 'Projector failure'
        }

        self.Error(['An error occurred: {}: {}.'.format(err, error_map[err])])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif self.is_authenticated:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.is_authenticated:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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
        
        self.is_authenticated = False

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