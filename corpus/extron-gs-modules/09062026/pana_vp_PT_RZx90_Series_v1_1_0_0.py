from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import hashlib
import binascii

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
            'LampUsage': {'Parameters': ['Number'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ZZ'
        elif 'Group A' <= value <= 'Group Z':
            self._DeviceID = '0{}'.format(value[-1])
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
            'Off': '0',
        }

        if value in ValueStateValues:
            FreezeCmdString = self.construct_cmd('OFZ', ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
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
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'SDI': 'SD1',
            'Digital Link': 'DL1',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2',
            'Digital Link S-Video': 'DL1:SVD',
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
            'DVI': 'DVI',
            'HD1': 'HDMI',
            'SD2': 'SDI',
            'DL1': 'Digital Link',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2',
            'DL1:SVD': 'Digital Link S-Video',
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

        lamp = qualifier['Number']
        if lamp in ['1', '2']:
            LampUsageCmdString = self.construct_cmd('Q$L', '{}'.format(lamp))
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

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Invalid Command.',
            '\x02ER402\x03': 'Invalid Parameter',
        }

        if response in DEVICE_ERROR_CODES:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
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
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': {'Parameters': ['Number'], 'Status': {}},
            'LampControlStatus': {'Parameters': ['Number'], 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchAuthentication, False)

            self.AddMatchString(re.compile(b'%1ERST=([012]{3}00[012])\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'%2FREZ=([01])\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'%2INPT=(1[1-2]|3[1-4])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'%1LAMP=(\d+) ([01]) (\d+) ([01])\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'%1POWR=([012])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'%1AVMT=(3[01])\r'), self.__MatchShutter, None)

            self.AddMatchString(re.compile(b'ERR[1-4]\r|PJLINK ERRA\r'), self.__MatchError, None)

        self.is_authenticated = False

    def __MatchAuthentication(self, match, tag):
        if tag:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.Send(binascii.hexlify(code_hash.digest()).decode() + '%1POWR ?\r')
        else:
            self.is_authenticated = True

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '%1ERST ?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '000000': 'Normal',
            '100000': 'Fan Warning',
            '200000': 'Fan Error',
            '010000': 'Light Source Warning',
            '020000': 'Light Source Error',
            '001000': 'Temperature Warning',
            '002000': 'Temperature Error',
            '000001': 'Other Warning',
            '000002': 'Other Error'
        }

        value = ValueStateValues.get(match.group(1).decode(), 'Multiple Errors')
        self.WriteStatus('DeviceStatus', value, None)

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

        ValueStateValues = {
            'Computer 1':        '11',
            'Computer 2':        '12',
            'DVI':        '31',
            'HDMI':         '32',
            'Digital Link': '33',
            'SDI':          '34'
        }

        if value in ValueStateValues:
            InputCmdString = '%2INPT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '%2INPT ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '11': 'Computer 1',
            '12': 'Computer 2',
            '31': 'DVI',
            '32': 'HDMI',
            '33': 'Digital Link',
            '34': 'SDI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Number']
        if lamp in {'1', '2'}:
            LampUsageCmdString = '%1LAMP ?\r'
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        LampControlStatus_ValueStateValues = {
            '1': 'Lamp On',
            '0': 'Lamp Off'
        }

        self.WriteStatus('LampUsage', int(match.group(1).decode()), {'Number': '1'})
        self.WriteStatus('LampUsage', int(match.group(3).decode()), {'Number': '2'})

        self.WriteStatus('LampControlStatus', LampControlStatus_ValueStateValues[match.group(2).decode()], {'Number': '1'})
        self.WriteStatus('LampControlStatus', LampControlStatus_ValueStateValues[match.group(4).decode()], {'Number': '2'})

    def UpdateLampControlStatus(self, value, qualifier):

        self.UpdateLampUsage(value, qualifier)

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


        PowerCmdString = '%1POWR ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

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

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On':   '31',
            'Off':  '30'
        }

        if value in ValueStateValues:
            ShutterCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = '%1AVMT ?\r'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '31': 'On',
            '30': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.is_authenticated:
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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