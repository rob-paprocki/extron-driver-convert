from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AspectRatioStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSetup': {'Status': {}},
            'AutoSetupStatus': {'Status': {}},
            'AVMute': {'Status': {}},
            'AVMuteStatus': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'FreezeStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'VS1'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatioStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Normal',
            '2': 'Wide'
        }

        AspectRatioStatusCmdString = 'QS1'
        res = self.__UpdateHelper('AspectRatioStatus', AspectRatioStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatioStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio Status: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = 'AMT:{}'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = 'QMT'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoSetup(self, value, qualifier):

        AutoSetupCmdString = 'OAS'
        self.__SetHelper('AutoSetup', AutoSetupCmdString, value, qualifier)

    def UpdateAutoSetupStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        AutoSetupStatusCmdString = 'QAS'
        res = self.__UpdateHelper('AutoSetupStatus', AutoSetupStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AutoSetupStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Setup Status: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        AVMuteCmdString = 'OSH'
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMuteStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AVMuteStatusCmdString = 'QSH'
        res = self.__UpdateHelper('AVMuteStatus', AVMuteStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AVMuteStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute Status: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
        }

        ClosedCaptionCmdString = 'OCC:{}'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            '0': 'Off'
        }

        ClosedCaptionCmdString = 'QCC'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'OFZ'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreezeStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeStatusCmdString = 'QFZ'
        res = self.__UpdateHelper('FreezeStatus', FreezeStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('FreezeStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': 'VID',
            'S-Video': 'SVD',
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'HDMI': 'HD1',
            'Component': 'CP1',
            'Memory Viewer': 'MV1',
            'USB Display': 'UD1',
            'Network': 'NWP'
        }

        InputCmdString = 'IIS:{}'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'VID': 'Video',
            'SVD': 'S-Video',
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'HD1': 'HDMI',
            'CP1': 'Component',
            'MV1': 'Memory Viewer',
            'UD1': 'USB Display',
            'NWP': 'Network'
        }

        InputCmdString = 'QIN'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'Q$L'
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
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
            'Enter': 'OEN'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'QVX:RTMI0'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = 'QPW'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'AUU',
            'Down': 'AUD'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'\x02ER401\x03': 'Invalid Command',
                              '\x02ER402\x03': 'Invalid Parameter'}
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            commandstring = '\x02{}\x03'.format(commandstring)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            commandstring = '\x02{}\x03'.format(commandstring)
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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


class DeviceEthernetClass:

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
        self.devicePassword = 'panasonic'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters': ['Type'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
        }

        self.md5hash = ''
        self.Security = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)
            self.UpdateAVMuteMatch = re.compile('%1AVMT=(10|11|20|21|30|31)\r')
            self.UpdateDeviceStatusMatch = re.compile('%1ERST=([0-2]{6})\r')
            self.UpdateInputMatch = re.compile('%1INPT=(11|12|21|22|23|31|41|51|52)\r')
            self.UpdateLampUsageMatch = re.compile('%1LAMP=([0-9]{1,5})')
            self.UpdatePowerMatch = re.compile('%1POWR=([0-3])\r')
            self.ErrorMatch = re.compile('ERR([1234A])\r')

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def SetAVMute(self, value, qualifier):

        TypeStates = {
            'Audio': '2',
            'Video': '1',
            'Audio/Video': '3'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '%1AVMT {0}{1}\r'.format(TypeStates[qualifier['Type']], ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            '10': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '11': {'Audio': 'Off', 'Video': 'On', 'Audio/Video': 'Off'},
            '20': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '21': {'Audio': 'On', 'Video': 'Off', 'Audio/Video': 'Off'},
            '30': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'},
            '31': {'Audio': 'On', 'Video': 'On', 'Audio/Video': 'On'}
        }

        AVMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateAVMuteMatch, res)
                if matchObject is not None:
                    AVMuteValues = AVMuteStateNames[matchObject.group(1)]
                    for Type in ['Audio', 'Video', 'Audio/Video']:
                        qualifier = {'Type': Type}
                        value = AVMuteValues[Type]
                        self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            2: 'Lamp',
            3: 'Temp'
        }

        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateDeviceStatusMatch, res)
                if matchObject is not None:
                    ErrorStrings = matchObject.group(1)
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
            'Video': '21',
            'S-Video': '22',
            'Computer 1': '11',
            'Computer 2': '12',
            'HDMI': '31',
            'Component': '23',
            'Memory Viewer': '41',
            'USB Display': '51',
            'Network': '52'
        }

        InputCmdString = '%1INPT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '21': 'Video',
            '22': 'S-Video',
            '11': 'Computer 1',
            '12': 'Computer 2',
            '31': 'HDMI',
            '23': 'Component',
            '41': 'Memory Viewer',
            '51': 'USB Display',
            '52': 'Network'
        }

        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateInputMatch, res)
                if matchObject is not None:
                    value = '{0}'.format(ValueStateValues[matchObject.group(1)])
                    self.WriteStatus('Input', value, None)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateLampUsageMatch, res)
                if matchObject is not None:
                    value = int(matchObject.group(1))
                    self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '%1POWR {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warming Up',
            '2': 'Cooling Down'
        }

        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdatePowerMatch, res)
                if matchObject is not None:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if 'ERR' in response:
            MatchObject = re.search(self.ErrorMatch, response)
            if MatchObject is not None:
                DEVICE_ERROR_CODES = {
                    '1': 'Undefined control command',
                    '2': 'Out of parameter range',
                    '3': 'Busy state or no-acceptable period',
                    '4': 'Timeout or no-acceptable period',
                    'A': 'Password mismatch'
                }
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[MatchObject.group(1)])])
                if 'ERRA' in response:
                    self.Security = False
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security:
            commandstring = self.md5hash + commandstring.encode()

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            if self.Security:
                commandstring = self.md5hash + commandstring.encode()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

        self.md5hash = ''
        self.Security = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
