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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampUsage': {'Parameters': ['Number'], 'Status': {}},
            'LensFocus': {'Status': {}},
            'LensShiftHorizontal': {'Status': {}},
            'LensShiftVertical': {'Status': {}},
            'LensZoom': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        self._DeviceIDValues = {
            'Broadcast': 'ZZ',
            'Group A': '0A',
            'Group B': '0B',
            'Group C': '0C',
            'Group D': '0D',
            'Group E': '0E',
            'Group F': '0F',
            'Group G': '0G',
            'Group H': '0H',
            'Group I': '0I',
            'Group J': '0J',
            'Group K': '0K',
            'Group L': '0L',
            'Group M': '0M',
            'Group N': '0N',
            'Group O': '0O',
            'Group P': '0P',
            'Group Q': '0Q',
            'Group R': '0R',
            'Group S': '0S',
            'Group T': '0T',
            'Group U': '0U',
            'Group V': '0V',
            'Group W': '0W',
            'Group X': '0X',
            'Group Y': '0Y',
            'Group Z': '0Z',
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value in self._DeviceIDValues:
            self._DeviceID = self._DeviceIDValues[value]
        elif 1 <= int(value) <= 64:
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['Device ID should be a value between 1 to 64, Group A to Z, or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Default/Auto': '\x02AD{0};VSE:0\x03',
            '4:3': '\x02AD{0};VSE:1\x03',
            '16:9': '\x02AD{0};VSE:2\x03',
            'Through': '\x02AD{0};VSE:5\x03',
            'HV Fit': '\x02AD{0};VSE:6\x03',
            'H Fit': '\x02AD{0};VSE:9\x03',
            'V Fit': '\x02AD{0};VSE:10\x03'
        }

        AspectRatioCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Default/Auto',
            '1': '4:3',
            '2': '16:9',
            '5': 'Through',
            '6': 'HV Fit',
            '9': 'H Fit',
            '10': 'V Fit'
        }

        AspectRatioCmdString = '\x02AD{0};QSE\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02AD{};OAS\x03'.format(self._DeviceID).encode()
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '\x02AD{};OCC:0\x03',
            '1': '\x02AD{};OCC:1\x03',
            '2': '\x02AD{};OCC:2\x03',
            '3': '\x02AD{};OCC:3\x03',
            '4': '\x02AD{};OCC:4\x03'
        }

        ClosedCaptionCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ClosedCaptionCmdString = '\x02AD{};QCC\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except KeyError:
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{};OFZ:1\x03',
            'Off': '\x02AD{};OFZ:0\x03'
        }

        FreezeCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '\x02AD{};QFZ\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except KeyError:
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': '\x02AD{0};IIS:RG1\x03',
            'RGB 2': '\x02AD{0};IIS:RG2\x03',
            'DVI-D': '\x02AD{0};IIS:DVI\x03',
            'HDMI': '\x02AD{0};IIS:HD1\x03',
            'Digital Link': '\x02AD{0};IIS:DL1\x03',
            'SDI': '\x02AD{0};IIS:SD1\x03'
        }

        InputCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'DVI': 'DVI-D',
            'HD1': 'HDMI',
            'DL1': 'Digital Link',
            'SD1': 'SDI'
        }

        InputCmdString = '\x02AD{};QIN\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '\x02AD{};ONK:0\x03',
            '1': '\x02AD{};ONK:1\x03',
            '2': '\x02AD{};ONK:2\x03',
            '3': '\x02AD{};ONK:3\x03',
            '4': '\x02AD{};ONK:4\x03',
            '5': '\x02AD{};ONK:5\x03',
            '6': '\x02AD{};ONK:6\x03',
            '7': '\x02AD{};ONK:7\x03',
            '8': '\x02AD{};ONK:8\x03',
            '9': '\x02AD{};ONK:9\x03'
        }

        KeypadCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        lamp_val = qualifier['Number']
        if lamp_val in ['1', '2']:
            LampUsageCmdString = '\x02AD{};Q$L:{}\x03'.format(self._DeviceID, lamp_val).encode()
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetLensFocus(self, value, qualifier):

        ValueStateValues = {
            'Fine 1 +': '\x02AD{};VXX:LNSI4=+00000\x03',
            'Fine 1 -': '\x02AD{};VXX:LNSI4=+00001\x03',
            'Fine 2 +': '\x02AD{};VXX:LNSI4=+00100\x03',
            'Fine 2 -': '\x02AD{};VXX:LNSI4=+00101\x03',
            'Coarse +': '\x02AD{};VXX:LNSI4=+00200\x03',
            'Coarse -': '\x02AD{};VXX:LNSI4=+00201\x03'
        }

        LensFocusCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('LensFocus', LensFocusCmdString, value, qualifier)

    def SetLensShiftHorizontal(self, value, qualifier):

        ValueStateValues = {
            'Fine 1 +': '\x02AD{};VXX:LNSI2=+00000\x03',
            'Fine 1 -': '\x02AD{};VXX:LNSI2=+00001\x03',
            'Fine 2 +': '\x02AD{};VXX:LNSI2=+00100\x03',
            'Fine 2 -': '\x02AD{};VXX:LNSI2=+00101\x03',
            'Coarse +': '\x02AD{};VXX:LNSI2=+00200\x03',
            'Coarse -': '\x02AD{};VXX:LNSI2=+00201\x03'
        }

        LensShiftHorizontalCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)

    def SetLensShiftVertical(self, value, qualifier):

        ValueStateValues = {
            'Fine 1 +': '\x02AD{};VXX:LNSI3=+00000\x03',
            'Fine 1 -': '\x02AD{};VXX:LNSI3=+00001\x03',
            'Fine 2 +': '\x02AD{};VXX:LNSI3=+00100\x03',
            'Fine 2 -': '\x02AD{};VXX:LNSI3=+00101\x03',
            'Coarse +': '\x02AD{};VXX:LNSI3=+00200\x03',
            'Coarse -': '\x02AD{};VXX:LNSI3=+00201\x03'
        }

        LensShiftVerticalCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)

    def SetLensZoom(self, value, qualifier):

        ValueStateValues = {
            'Fine 1 +': '\x02AD{};VXX:LNSI5=+00000\x03',
            'Fine 1 -': '\x02AD{};VXX:LNSI5=+00001\x03',
            'Fine 2 +': '\x02AD{};VXX:LNSI5=+00100\x03',
            'Fine 2 -': '\x02AD{};VXX:LNSI5=+00101\x03',
            'Coarse +': '\x02AD{};VXX:LNSI5=+00200\x03',
            'Coarse -': '\x02AD{};VXX:LNSI5=+00201\x03'
        }

        LensZoomCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('LensZoom', LensZoomCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '\x02AD{};OMN\x03',
            'Enter': '\x02AD{};OEN\x03',
            'Up': '\x02AD{};OCU\x03',
            'Down': '\x02AD{};OCD\x03',
            'Left': '\x02AD{};OCL\x03',
            'Right': '\x02AD{};OCR\x03',
            'Default': '\x02AD{};OST\x03',
            'Function': '\x02AD{};FC1\x03',
            'System Selector': '\x02AD{};OSL\x03'
        }

        MenuNavigationCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x02AD{};QVX:RTMS1\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'Off': '\x02AD{};OPP:0\x03',
            'User 1': '\x02AD{};OPP:1\x03',
            'User 2': '\x02AD{};OPP:2\x03',
            'User 3': '\x02AD{};OPP:3\x03'
        }

        PictureInPictureCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3'
        }

        PictureInPictureCmdString = '\x02AD{};QPP\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture In Picture: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': '\x02AD{};VPM:DYN\x03',
            'Natural': '\x02AD{};VPM:NAT\x03',
            'Standard': '\x02AD{};VPM:STD\x03',
            'Cinema': '\x02AD{};VPM:CIN\x03',
            'Graphic': '\x02AD{};VPM:GRA\x03',
            'Dicom Sim': '\x02AD{};VPM:DIC\x03',
            'User': '\x02AD{};VPM:USR\x03',
            'REC709': '\x02AD{};VPM:709\x03'
        }

        PictureModeCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'Dicom Sim',
            'USR': 'User',
            '709': 'REC709'
        }

        PictureModeCmdString = '\x02AD{};QPM\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{0};PON\x03',
            'Off': '\x02AD{0};POF\x03'
        }

        PowerCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Warming Up',
            '3': 'Cooling Down',
            '0': 'Off'
        }

        PowerCmdString = '\x02AD{};Q$S\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{};OSH:1\x03',
            'Off': '\x02AD{};OSH:0\x03'
        }

        ShutterCmdString = ValueStateValues[value].format(self._DeviceID).encode()
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ShutterCmdString = '\x02AD{};QSH\x03'.format(self._DeviceID).encode()
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Command Cannot be Executed.',
            '\x02ER402\x03': 'Invalid Parameter.'
        }
        if isinstance(response, bytes):
            response = response.decode()
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID in self._DeviceIDValues.values():
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID in self._DeviceIDValues.values():
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        self.devicePassword = 'panasonic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Parameters': ['Number'], 'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        self.md5hash = b''
        self.Security = 'Not Authenticated'

        self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)

        self.UpdateDeviceStatusMatch = re.compile('%1ERST=([0-2]{6})\r')
        self.UpdateInputMatch = re.compile('%1INPT=(11|12|31|32|33|34)\r')
        self.UpdateLampUsageMatch = re.compile('%1LAMP=([0-9]{1,5}) [01] ([0-9]{1,5}) [01]\r')
        self.UpdatePowerMatch = re.compile('%1POWR=([0-3])\r')
        self.UpdateShutterMatch = re.compile('%1AVMT=3([01])\r')
        self.ErrorMatch = re.compile('ERR([1234A])\r')

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = 'Authenticated'

    def __MatchNoAuthentication(self, match, tag):
        self.Security = 'Not Needed'

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Fan',
            1: 'Light Source',
            2: 'Temperature',
            4: 'Filter',
            5: 'Other'
        }

        DeviceStatusCmdString = self.md5hash + b'%1ERST ?\r'
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
                        value = '{} Warning'.format(ValueStateValues[index])
                    elif ErrorStrings.count('2') == 1:
                        index = ErrorStrings.index('2')
                        value = '{} Error'.format(ValueStateValues[index])
                    self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': b'%1INPT 11\r',
            'RGB 2': b'%1INPT 12\r',
            'DVI-D': b'%1INPT 31\r',
            'HDMI': b'%1INPT 32\r',
            'Digital Link': b'%1INPT 33\r',
            'SDI': b'%1INPT 34\r'
        }

        InputCmdString = self.md5hash + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'RGB 1',
            '12': 'RGB 2',
            '31': 'DVI-D',
            '32': 'HDMI',
            '33': 'Digital Link',
            '34': 'SDI'
        }

        InputCmdString = self.md5hash + b'%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateInputMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        if qualifier['Number'] in ['1', '2']:
            LampUsageCmdString = self.md5hash + b'%1LAMP ?\r'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    matchObject = re.search(self.UpdateLampUsageMatch, res)
                    if matchObject:
                        lamp1 = int(matchObject.group(1))
                        lamp2 = int(matchObject.group(2))
                        self.WriteStatus('LampUsage', lamp1, {'Number': '1'})
                        self.WriteStatus('LampUsage', lamp2, {'Number': '2'})
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'%1POWR 1\r',
            'Off': b'%1POWR 0\r',
        }

        PowerCmdString = self.md5hash + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warming Up',
            '2': 'Cooling Down'
        }

        PowerCmdString = self.md5hash + b'%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdatePowerMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': b'%1AVMT 31\r',
            'Off': b'%1AVMT 30\r'
        }

        ShutterCmdString = self.md5hash + ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ShutterCmdString = self.md5hash + b'%1AVMT ?\r'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateShutterMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            'A': 'Password mismatch'
        }

        if isinstance(response, bytes):
            response = response.decode()
        if 'ERR' in response:
            MatchObject = re.search(self.ErrorMatch, response)
            if MatchObject:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[MatchObject.group(1)])])
                if 'ERRA' in response:
                    self.Security = 'Not Authenticated'
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Security in ['Authenticated', 'Not Needed']:
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
