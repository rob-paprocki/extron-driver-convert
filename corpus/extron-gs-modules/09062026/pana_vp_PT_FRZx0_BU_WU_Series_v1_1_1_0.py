from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampControlStatus': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LightOutput': {'Status': {}},
            'LightRuntime': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'ShiftHorizontal': {'Status': {}},
            'ShiftVertical': {'Status': {}},
            'Shutter': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Parameters': ['Axis'], 'Status': {}},
            'ZoomInterlocked': {'Status': {}},
            'ZoomMode': {'Status': {}},
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

    def construct_cmd(self, command, value=None, extended=False):

        if extended and value:
            cmd = '\x02AD{id};VXX:{command}={value}\x03'.format(id=self._DeviceID, command=command, value=value)
        elif value:
            cmd = '\x02AD{id};{command}:{value}\x03'.format(id=self._DeviceID, command=command, value=value)
        else:
            cmd = '\x02AD{id};{command}\x03'.format(id=self._DeviceID, command=command)

        return cmd

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            '4:3': '1',
            '16:9': '2',
            'Through': '5',
            'HV Fit': '6',
            'H Fit': '9',
            'V Fit': '10',
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.construct_cmd('VSE', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '5': 'Through',
            '6': 'HV Fit',
            '9': 'H Fit',
            '10': 'V Fit',
        }

        AspectRatioCmdString = self.construct_cmd('QSE')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.construct_cmd('OAS')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            FreezeCmdString = self.construct_cmd('OFZ', ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = self.construct_cmd('QFZ')
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'Digital Link': 'DL1',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2',
        }

        if value in ValueStateValues:
            InputCmdString = self.construct_cmd('IIS', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'DL1': 'Digital Link',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2',
        }

        InputCmdString = self.construct_cmd('QIN')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
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

        ValueStateValues = {
            '0': 'Lamp Off',
            '1': 'In turning On',
            '2': 'Lamp On',
            '3': 'Lamp Cooling',
        }

        LampControlStatusCmdString = self.construct_cmd('Q$S')
        res = self.__UpdateHelper('LampControlStatus', LampControlStatusCmdString, value, qualifier)
        if res:
            try:
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

    def SetLightOutput(self, value, qualifier):

        ValueConstraints = {
            'Min': 50,
            'Max': 1000,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            LightOutputCmdString = self.construct_cmd('LOPI2', '+{:05}'.format(ValueConstraints['Value']), True)
            self.__SetHelper('LightOutput', LightOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLightOutput')

    def UpdateLightOutput(self, value, qualifier):

        LightOutputCmdString = self.construct_cmd('QVX:LOPI2')
        res = self.__UpdateHelper('LightOutput', LightOutputCmdString, value, qualifier)
        if res:
            try:

                value = int(res[8:-1])
                self.WriteStatus('LightOutput', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Light Output: Invalid/unexpected response'])

    def UpdateLightRuntime(self, value, qualifier):

        LightRuntimeCmdString = self.construct_cmd('QVX:LRTS3=00')
        res = self.__UpdateHelper('LightRuntime', LightRuntimeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10:-1])
                self.WriteStatus('LightRuntime', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Light Runtime: Invalid/unexpected response'])

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

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM SIM': 'DIC',
            'REC709': '709',
        }

        if value in ValueStateValues:
            PictureModeCmdString = self.construct_cmd('VPM', ValueStateValues[value])
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
            '709': 'REC709',
        }

        PictureModeCmdString = self.construct_cmd('QPM')
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
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

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        PowerCmdString = self.construct_cmd('QPW')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShiftHorizontal(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4095,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            ShiftHorizontalCmdString = self.construct_cmd('VTH', '{:04}'.format(ValueConstraints['Value']))
            self.__SetHelper('ShiftHorizontal', ShiftHorizontalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShiftHorizontal')

    def UpdateShiftHorizontal(self, value, qualifier):

        ShiftHorizontalCmdString = self.construct_cmd('QTH')
        res = self.__UpdateHelper('ShiftHorizontal', ShiftHorizontalCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('ShiftHorizontal', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Shift Horizontal: Invalid/unexpected response'])

    def SetShiftVertical(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4094,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            ShiftVerticalCmdString = self.construct_cmd('VTV', '{:04}'.format(ValueConstraints['Value']))
            self.__SetHelper('ShiftVertical', ShiftVerticalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShiftVertical')

    def UpdateShiftVertical(self, value, qualifier):

        ShiftVerticalCmdString = self.construct_cmd('QTV')
        res = self.__UpdateHelper('ShiftVertical', ShiftVerticalCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('ShiftVertical', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Shift Vertical: Invalid/unexpected response'])

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

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        ShutterCmdString = self.construct_cmd('QSH')
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            VolumeCmdString = self.construct_cmd('AVL', '{:03}'.format(ValueConstraints['Value']))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.construct_cmd('QAV')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        AxisStates = {
            'Horizontal': 'H',
            'Vertical': 'V',
            'Both': 'O',
        }

        ValueConstraints = {
            'Min': 50,
            'Max': 999,
            'Value': value,
        }

        axis = qualifier['Axis']
        if axis in AxisStates and self.__constraint_checker(ValueConstraints):
            ZoomCmdString = self.construct_cmd('OZ{}'.format(AxisStates[axis]),
                                               '{:03}'.format(ValueConstraints['Value']))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        AxisStates = {
            'Horizontal': 'H',
            'Vertical': 'V',
            'Both': 'O',
        }

        axis = qualifier['Axis']
        if axis in AxisStates:
            ZoomCmdString = self.construct_cmd('QZ{}'.format(AxisStates[axis]))
            res = self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('Zoom', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Zoom {}: Invalid/unexpected response'.format(axis)])
        else:
            self.Discard('Invalid Command for UpdateZoom')

    def SetZoomInterlocked(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            ZoomInterlockedCmdString = self.construct_cmd('OZS', ValueStateValues[value])
            self.__SetHelper('ZoomInterlocked', ZoomInterlockedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomInterlocked')

    def UpdateZoomInterlocked(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        ZoomInterlockedCmdString = self.construct_cmd('QZS')
        res = self.__UpdateHelper('ZoomInterlocked', ZoomInterlockedCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ZoomInterlocked', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Zoom Interlocked: Invalid/unexpected response'])

    def SetZoomMode(self, value, qualifier):

        ValueStateValues = {
            'Full': '1',
            'Internal': '0',
        }

        if value in ValueStateValues:
            ZoomModeCmdString = self.construct_cmd('OZT', ValueStateValues[value])
            self.__SetHelper('ZoomMode', ZoomModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomMode')

    def UpdateZoomMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Full',
            '0': 'Internal',
        }

        ZoomModeCmdString = self.construct_cmd('QZT')
        res = self.__UpdateHelper('ZoomMode', ZoomModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ZoomMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Zoom Mode: Invalid/unexpected response'])

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
        self.Models = {}

        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampStatus': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.is_authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%1POWR=([01])\r'), self.__MatchPower, None)
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

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '21',
            'Off' : '20'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '21' : ('On', 'Off'),
            '30' : ('Off', 'Off'),
            '31' : ('On', 'On')
        }

        AudioMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]

                self.WriteStatus('AudioMute', value[0], None)
                self.WriteStatus('AVMute', value[1], None)
            except (KeyError, IndexError):
                self.Error(['Audio Mute/AV Mute: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '31',
            'Off' : '30'
        }

        if value in ValueStateValues:
            AVMuteCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '000000' : 'Normal',
            '100000' : 'Fan Warning',
            '200000' : 'Fan Error',
            '010000' : 'Lamp Warning',
            '020000' : 'Lamp Error',
            '001000' : 'Temperature Warning',
            '002000' : 'Temperature Error',
            '000100' : 'Cover Warning',
            '000200' : 'Cover Error',
            '000001' : 'Other Warning',
            '000002' : 'Other Error'
        }

        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res.strip().split('=')[-1], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '%2FILT ?\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res.strip().split('=')[-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            FreezeCmdString = '%2FREZ {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
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
            'Computer 1'    : '11',
            'Computer 2'    : '12',
            'Video'         : '21',
            'HDMI 1'        : '32',
            'HDMI 2'        : '36',
            'Digital Link'  : '33'
        }

        if value in ValueStateValues:
            InputCmdString = '%2INPT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11' : 'Computer 1',
            '12' : 'Computer 2',
            '21' : 'Video',
            '32' : 'HDMI 1',
            '36' : 'HDMI 2',
            '33' : 'Digital Link'
        }

        InputCmdString = '%2INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        LampStatusCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('=')[-1].split()[1]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Status: Invalid/unexpected response'])
            try:
                value = int(res.strip().split('=')[-1].split()[0])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        self.UpdateLampStatus(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            PowerCmdString = '%1POWR {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
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
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : '1',
            'Down' : '0'
        }

        if value in ValueStateValues:
            VolumeCmdString = '%2SVOL {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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