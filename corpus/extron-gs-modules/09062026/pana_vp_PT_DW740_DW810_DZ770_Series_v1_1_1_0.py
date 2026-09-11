from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

    @property
    def DeviceId(self):
        return self._DeviceID

    @DeviceId.setter
    def DeviceId(self, value):
        if value.upper() == 'ALL':
            self._DeviceID = 'ZZ'
        elif (0 < int(value) < 65) or ('A' < value < 'Z'):
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['DeviceID variable should be a number between 1 and 64, A to Z, or ALL.'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto/Default': '0',
            '4:3': '1',
            '16:9': '2',
            'Through': '5',
            'HV Fit': '6',
            'H Fit': '9',
            'V Fit': '10',
            'S1 Auto': '20',
            'Vid Auto (pri.)': '30'
        }
        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';VSE:' + AspectRatioStateValues[value].encode() + b'\x03'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            b'0\x03': 'Auto/Default',
            b'1\x03': '4:3',
            b'2\x03': '16:9',
            b'5\x03': 'Through',
            b'6\x03': 'HV Fit',
            b'9\x03': 'H Fit',
            b'10': 'V Fit',
            b'20': 'S1 Auto',
            b'30': 'Vid Auto (pri.)',
        }

        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[1:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02AD' + self._DeviceID.encode() + b';OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'In': b'\x00',
            'Out': b'\x01'
        }

        if self._DeviceID == 'ZZ':
            tempDeviceId = b'\x00'
        elif 0 < int(self._DeviceID) < 65:
            tempDeviceId = pack('>B', int(self._DeviceID))
        elif 'A' < self._DeviceID.strip('0') < 'Z':
            tempDeviceId = pack('>B', self._DeviceID.encode()[0] + 63)

        FocusCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C\x02\x01' + FocusStateValues[value] + b'\x03'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

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
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'HDMI': 'HD1',
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
            b'HD1': 'HDMI'
        }

        InputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[1:4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
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
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        LampUsageCmdString = b'\x02AD' + self._DeviceID.encode() + b';Q$L:' + lamp.encode() + b'\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetLampSelect(self, value, qualifier):

        LampSelectStateValues = {
            'Dual': '0',
            'Single': '1',
            'Lamp 1': '2',
            'Lamp 2': '3'
        }
        LampSelectCmdString = b'\x02AD' + self._DeviceID.encode() + b';LPM:' + LampSelectStateValues[value].encode() + b'\x03'
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        LampSelectStateNames = {
            b'0': 'Dual',
            b'1': 'Single',
            b'2': 'Lamp 1',
            b'3': 'Lamp 2'
        }

        LampSelectCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSL\x03'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = LampSelectStateNames[res[1:2]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Select: Invalid/unexpected response'])

    def SetLensShift(self, value, qualifier):

        LensShiftStateValues = {
            'Right': b'\x00\x01\x00',
            'Left': b'\x00\x01\x01',
            'Up': b'\x01\x01\x00',
            'Down': b'\x01\x01\x01'
        }

        if self._DeviceID == 'ZZ':
            tempDeviceId = b'\x00'
        elif 0 < int(self._DeviceID) < 65:
            tempDeviceId = pack('>B', int(self._DeviceID))
        elif 'A' < self._DeviceID.strip('0') < 'Z':
            tempDeviceId = pack('>B', self._DeviceID.encode()[0] + 63)

        LensShiftCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C' + LensShiftStateValues[value] + b'\x03'
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': b'OMN',
            'Up': b'OCU',
            'Down': b'OCD',
            'Left': b'OCL',
            'Right': b'OCR',
            'Enter': b'OEN'
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
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02AD' + self._DeviceID.encode() + b';QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural': 'NAT',
            'Standard': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM Sim': 'DIC',
            'Rec709': '709'
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
            b'DI': 'DICOM Sim',
            b'70': 'Rec709'
        }

        PictureModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:3]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        PIPInputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'HDMI': 'HD1'
        }
        PIPInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';SIS:' + PIPInputStateValues[value].encode() + b'\x03'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputStateNames = {
            b'RG1': 'RGB 1',
            b'RG2': 'RGB 2',
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'DVI': 'DVI',
            b'HD1': 'HDMI'
        }

        PIPInputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIS\x03'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPInputStateNames[res[1:4]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'On': '1',
            'Off': '0'
        }
        PIPModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OPP:' + PIPModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        PIPModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QPP\x03'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeStateNames[res[1:2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

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
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ShutterStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShutterCmdString = b'\x02AD' + self._DeviceID.encode() + b';OSH:' + ShutterStateValues[value].encode() + b'\x03'
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }

        ShutterCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSH\x03'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ShutterStateNames[res[1:2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02ER401\x03': "Invalid Command.",
            b'\x02ER402\x03': "Invalid Parameter"
        }
        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error([sourceCmdName + ' ' + v])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{0}:Invalid/unexpected response'.format(command)])
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        self.md5hash = ''
        self.Security = 'Required'
        self.devicePassword = 'panasonic'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)
            self.UpdateDeviceStatusMatch = re.compile('%1ERST=([0-2]{6})\r')
            self.UpdateInputMatch = re.compile('%1INPT=([1-3][12])\r')
            self.UpdateLampUsageMatch = re.compile('([0-9]{1,5}) [0-1]')
            self.UpdatePowerMatch = re.compile('%1POWR=([0-3])\r')
            self.UpdateShutterMatch = re.compile('%1AVMT=3([01])\r')
            self.ErrorMatch = re.compile('ERR(1|2|3|4|A)\r')

    def __MatchAuthentication(self, match, tag):
        if self.devicePassword is not None:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.md5hash = hexlify(code_hash.digest())
            self.Security = 'Admin'
        else:
            self.MissingCredentialsLog('Password')

    def __MatchNoAuthentication(self, match, tag):
        self.Security = 'Not Needed'

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            4: 'Cover',
            5: 'Filter',
            6: 'Other'
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
            'RGB 1': '11',
            'RGB 2': '12',
            'Video': '21',
            'S-Video': '22',
            'DVI': '31',
            'HDMI': '32'

        }

        InputCmdString = '%1INPT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'RGB 1',
            '12': 'RGB 2',
            '21': 'Video',
            '22': 'S-Video',
            '31': 'DVI',
            '32': 'HDMI'
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
                matchList = re.findall(self.UpdateLampUsageMatch, res)
                if matchList != []:
                    i = 1
                    for lamp in matchList:
                        qualifier = {'Lamp': str(i)}
                        value = int(lamp)
                        self.WriteStatus('LampUsage', value, qualifier)
                        i = i + 1
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

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShutterCmdString = '%1AVMT 3{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        ShutterCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateShutterMatch, res)
                if matchObject is not None:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
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
                self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[MatchObject.group(1)])])
                if 'ERRA' in response:
                    self.Security = 'None'
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security in ['Admin', 'Not Needed']:
            if self.Security == 'Admin':
                commandstring = self.md5hash + commandstring.encode()

            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if isinstance(res, bytes):
                    res = res.decode()
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

                if self.Security == 'Admin':
                    commandstring = self.md5hash + commandstring.encode()
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    return ''
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
        self.Security = 'Required'

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
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
