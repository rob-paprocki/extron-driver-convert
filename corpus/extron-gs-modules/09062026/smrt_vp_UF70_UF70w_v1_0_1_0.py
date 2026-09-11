from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import math
import re
import binascii


class DeviceSerialClass:
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'aspectratio=(fill|match|16:9)\r', re.IGNORECASE), self.__MatchAspectRatio,
                                None)
            self.AddMatchString(re.compile(b'(video)?mute=(on|off)\r', re.IGNORECASE), self.__MatchAudioVideoMute, None)
            self.AddMatchString(re.compile(b'cc=(cc1|cc2|off)\r', re.IGNORECASE), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(
                b'failurelog=(normal|overtemp|fanlock|fanDMD|fanblower|fansystem|lamperror|colorwheelbreak|lampignite|lampoverheat|lampdriver|lampoverhours)\r',
                re.IGNORECASE), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'videofreeze=(on|off)\r', re.IGNORECASE), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'input=(VGA1|Composite|HDMI1)\r', re.IGNORECASE), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'lamphrs=(\d+)\r', re.IGNORECASE), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'syshrs=(\d+)\r', re.IGNORECASE), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'powerstate=(Powering|On|Cooling|Idle)\r', re.IGNORECASE),
                                self.__MatchPower, None)
            self.AddMatchString(re.compile(b'volumecontrol=(-?[\d]+)\r', re.IGNORECASE), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': '16:9',
            'Fill': 'fill',
            'Match': 'match'
        }

        AspectRatioCmdString = 'set aspectratio={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'get aspectratio\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '16:9': '16:9',
            'fill': 'Fill',
            'match': 'Match'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AudioMuteCmdString = 'set mute={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'get mute\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioVideoMute(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        response = match.group().decode()
        value = ValueStateValues[response[:-1].split('=')[1]]
        if response.find('video') >= 0:
            self.WriteStatus('VideoMute', value, None)
        else:
            self.WriteStatus('AudioMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1': 'cc1',
            'CC2': 'cc2',
            'Off': 'off'
        }

        ClosedCaptionCmdString = 'set cc={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'get cc\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            'cc1': 'CC1',
            'cc2': 'CC2',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'get failurelog\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'normal': 'Normal',
            'overtemp': 'Over Temperature',
            'fanlock': 'Fan Lock',
            'fandmd': 'Fan DMD',
            'fanblower': 'Fan Blower Error',
            'fansystem': 'Fan System Error',
            'lamperror': 'Lamp Error',
            'colorwheelbreak': 'Color Wheel Break',
            'lampignite': 'Lamp Ignition Error',
            'lampoverheat': 'Lamp Overheat',
            'lampdriver': 'Lamp Driver Error',
            'lampoverhours': 'Lamp Over Hours'
        }

        dev_status = match.group(1).decode()
        value = ValueStateValues[dev_status.lower()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        FreezeCmdString = 'set videofreeze-{0}'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'get videofreeze\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': 'VGA1',
            'HDMI1': 'HDMI1',
            'Composite': 'COMPOSITE'
        }

        InputCmdString = 'set input={0}'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'get input\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'vga1': 'VGA 1',
            'hdmi1': 'HDMI1',
            'composite': 'Composite'
        }

        inputVal = match.group(1).decode()
        value = ValueStateValues[inputVal.lower()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'get lamphrs\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'get syshrs\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on\r',
            'Off': 'off now\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'get powerstate\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'idle': 'Off',
            'powering': 'Warming Up',
            'cooling': 'Cooling Down',
        }

        power_state = match.group(1).decode()
        value = ValueStateValues[power_state.lower()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = 'set videomute={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'get videomute\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 40
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'set volume={0}\r'.format(value - 20)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) + 20
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        value = match.group(0).decode().split(':')
        print(value[1])

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


class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.privateCommunityString = 'private'

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaptionEnable': {'Status': {}},
            'ClosedCaptionLanguage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.CommandOIDDict = {
            'AspectRatio': '1.3.6.1.4.1.29485.3.2.11.2.7.0',
            'AudioMute': '1.3.6.1.4.1.29485.3.2.11.3.2.0',
            'ClosedCaptionEnable': '1.3.6.1.4.1.29485.3.2.11.3.4.0',
            'ClosedCaptionLanguage': '1.3.6.1.4.1.29485.3.2.11.3.5.0',
            'DeviceStatus': '1.3.6.1.4.1.29485.3.2.11.7.1.0',
            'Freeze': '1.3.6.1.4.1.29485.3.2.11.2.13.0',
            'Input': '1.3.6.1.4.1.29485.3.2.11.2.1.0',
            'LampUsage': '1.3.6.1.4.1.29485.3.2.11.6.3.0',
            'OperationHours': '1.3.6.1.4.1.29485.3.2.11.6.15.0',
            'Power': '1.3.6.1.4.1.29485.3.2.11.1.0',
            'VideoMute': '1.3.6.1.4.1.29485.3.2.11.2.12.0',
            'Volume': '1.3.6.1.4.1.29485.3.2.11.3.1.0'
        }

        self.SNMP = SNMPDevice(self.privateCommunityString, self.CommandOIDDict)

    @property
    def Writecommunity(self):
        return self.privateCommunityString

    @Writecommunity.setter
    def Writecommunity(self, value):
        self.privateCommunityString = value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 3,
            'Fill': 1,
            'Match': 2
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            3: '16:9',
            2: 'Fill',
            1: 'Match'
        }

        res = self.__UpdateHelper('AspectRatio', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('AudioMute', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetClosedCaptionEnable(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1
        }

        ClosedCaptionEnableCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionEnable', ClosedCaptionEnableCmdString, qualifier)

    def UpdateClosedCaptionEnable(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('ClosedCaptionEnable', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ClosedCaptionEnable', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateClosedCaptionEnable')

    def SetClosedCaptionLanguage(self, value, qualifier):

        ValueStateValues = {
            'CC1': 1,
            'CC2': 2
        }

        ClosedCaptionLanguageCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaptionLanguage', ClosedCaptionLanguageCmdString, qualifier)

    def UpdateClosedCaptionLanguage(self, value, qualifier):

        ValueStateValues = {
            1: 'CC1',
            2: 'CC2'
        }

        res = self.__UpdateHelper('ClosedCaptionLanguage', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ClosedCaptionLanguage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateClosedCaptionLanguage')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Normal',
            2: 'Over Temperature',
            3: 'Fan Lock',
            4: 'Lamp Error',
            5: 'Color Wheel Break',
            6: 'Lamp Overheat',
            7: 'Lamp Driver Error',
            8: 'Fan DMD',
            9: 'Fan Blower Error',
            10: 'Fan System Error',
            11: 'Lamp Over Hours'
        }

        res = self.__UpdateHelper('DeviceStatus', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('Freeze', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': 1,
            'HDMI1': 5,
            'Composite': 3
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            1: 'VGA 1',
            5: 'HDMI1',
            3: 'Composite'
        }

        res = self.__UpdateHelper('Input', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError):
                print('Invalid/Unexpected Response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 2
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off',
            3: 'Warming Up',
            4: 'Cooling Down'
        }

        res = self.__UpdateHelper('Power', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('VideoMute', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 40
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = value
            self.__SetHelper('Volume', VolumeCmdString, qualifier)

        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: "Response message too large to transport",
            2: "The name of the requested object was not found",
            3: "A data type in the request did not match the data type in the SNMP agent",
            4: "The SNMP manager attempted to set a read-only parameter",
            5: "General Error",
            6: "The specified SNMP variable is not accessible.",
            7: "The value specifies a type that is inconsistent with the type required for the variable.",
            8: "The value specifies a length that is inconsistent with the length required for the variable.",
            9: "The value contains an Abstract Syntax Notation One (ASN.1) encoding that is inconsistent with the ASN.1 tag of the field.",
            10: "The value cannot be assigned to the variable.",
            11: "The variable does not exist, and the agent cannot create it.",
            12: "The value is inconsistent with values of other managed objects.",
            13: "Assigning the value to the variable requires allocation of resources that are currently unavailable.",
            14: "No validation errors occurred, but no variables were updated.",
            15: "No validation errors occurred. Some variables were updated because it was not possible to undo their assignment.",
            16: "An authorization error occurred.",
            17: "The variable exists but the agent cannot modify it.",
            18: "The variable does not exist; the agent cannot create it because the named object instance is inconsistent with the values of other managed objects."
        }

        if response[0] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]]))
            response = ''
        else:
            response = response[1]

        return response

    def __SetHelper(self, command, value, qualifier):

        commandstring = self.SNMP.encodeMsg('Set', command, value)
        self.Send(commandstring)

    def __UpdateHelper(self, command, value, qualifier):

        commandstring = self.SNMP.encodeMsg('Get', command)
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                resDecode = self.SNMP.decodeMsg(res, command)
                return self.__CheckResponseForErrors(command, resDecode)

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


class SNMPDeviceException(Exception):
    pass


class SNMPDevice:
    def __init__(self, community, CommandOIDDict):

        self.community = community
        self.CommandOIDDict = CommandOIDDict
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(self.CommandOIDDict[command])
        self.community = community
        self.communityString = b'\x04' + pack('>B', len(self.community)) + self.community.encode()
        self.GetNext = False

    def addOID(self, command, oid):

        if command in self.oidList:
            raise SNMPDeviceException('Command/UID already associated with a different OID')
        self.oidList[command] = self.__BuildOID(oid)

    def getOID(self, command):

        if command not in self.oidList:
            raise SNMPDeviceException('Command/UID not in OID List of the device')
        return self.__RebuildOIDString(self.oidList[command])

    def decodeOID(self, msg, command=None, OID=None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if OID is None and command is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')
        try:
            if OID is not None:
                oidIndex = msg.index(self.__BuildOID(OID))
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex - 1]
            OID = msg[oidIndex: oidIndex + oidLength]
            value = self.__RebuildOIDString(OID)
            return value
        except ValueError:
            raise SNMPDeviceException('OID for that command/UID not found in the message')

    def encodeMsg(self, queryType, command=None, value=None, OID=None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
        }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04' + pack('>B', valueLen) + valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:]) / 2) * 2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02' + pack('>B', valueLen) + valueBytes
            else:
                raise TypeError('Value is not of type int or string')
        else:
            valueMsg = b'\x05\x00'

        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
            else:
                oid = self.oidList[command]
        else:
            oid = self.nextOID
            self.GetNext = False
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(
            requestID + error + errorIndex + varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(
            snmpVersion + self.communityString + snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def encodeMsgMultiOID(self, queryType, command=None, value=None, OID=None, NextOID=None):

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
        }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04' + pack('>B', valueLen) + valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:]) / 2) * 2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02' + pack('>B', valueLen) + valueBytes
            else:

                pass
        else:
            valueMsg = b'\x05\x00'

        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
                # else:
                # oid = self.oidList[command]
        else:
            oid = self.nextOID
            self.GetNext = False

        varbindListMsg = b''
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:
            if NextOID:
                oid = self.oidList[command2do] + pack('>B', NextOID)
                # oid = self.oidList[command2do]+ b'.' + NextOID
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
            varbindListMsg += varbindMsg
            # 6/10/15            varbindListMsg += (b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg)
        if len(varbindListMsg) < 128:
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg
        elif len(varbindListMsg) < 4096:
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg)) + varbindListMsg

        pduLen = len(requestID + error + errorIndex + varbindListMsg)
        if pduLen < 128:
            pduLenMsg = pack('>B', pduLen)
        elif pduLen < 4096:
            pduLenMsg = b'\x81' + pack('>B', pduLen)

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg

        snmpLen = len(snmpVersion + self.communityString + snmpPduMsg)
        if snmpLen < 128:
            snmpLenMsg = pack('>B', snmpLen)
        elif snmpLen < 4096:
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def decodeMsg(self, msg, command=None, OID=None):

        ValueTypeDict = {
            2: 'Integer',
            4: 'Octet String',
            5: 'Null',
            6: 'OID',
            64: 'IPAdddress',
            65: 'Counter32',
            66: 'Gauge',
            67: 'Timeticks',
            68: 'Opaque',
            69: 'NsapAddress',
            70: 'Counter64',
        }

        oidIndex = -1
        valueType = '???'

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. You must specify at least one')

        try:
            if OID is not None:
                cutomOIDHex = self.__BuildOID(OID)
                oidIndex = msg.index(cutomOIDHex)
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex - 1]
            self.nextOID = msg[oidIndex: oidIndex + oidLength]
            valueIndex = oidIndex + oidLength
            valueType = ValueTypeDict[msg[valueIndex]]
            valueLen = msg[valueIndex + 1]
            if valueType == 'Octet String':
                value = msg[valueIndex + 2:valueIndex + 2 + valueLen].decode()
            elif valueType == 'Null':
                value = None
            elif valueType in ['Integer', 'Timeticks', 'Counter32', 'Gauge']:
                valueBytes = msg[valueIndex + 2:valueIndex + 2 + valueLen]
                value = int(binascii.hexlify(valueBytes), 16)
            elif valueType == 'OID':
                value = self.__RebuildOIDString(msg[valueIndex + 2:valueIndex + 2 + valueLen])
            elif valueType == 'IPAdddress':
                valueBytes = msg[valueIndex + 2:valueIndex + 2 + valueLen]
                ipAddress = [byte for byte in valueBytes]
                value = '.'.join([str(i) for i in ipAddress])
            error = self.__DecodeError(msg)
            if OID is not None:
                oidCheck = self.nextOID != cutomOIDHex
            else:
                oidCheck = self.nextOID != self.oidList[command]
            if oidCheck and error == 0:
                self.GetNext = True
                return (error, value, self.encodeMsg('Get-Next', command=command))
            return (error, value)
        except ValueError:
            pass
        except KeyError:
            pass

    def __DecodeError(self, msg):
        try:
            pduIndex = msg.index(self.community.encode()) + len(self.community.encode())
            requestIdIndex = pduIndex + 2
            ErrorIndex = requestIdIndex + 2 + msg[requestIdIndex + 1]
            error = msg[ErrorIndex + 2]
            return error
        except ValueError:

            pass

    def __BuildOID(self, oidValue):
        try:
            oidValueNumberList = [int(i) for i in oidValue.split('.')]
        except ValueError:
            raise SNMPDeviceException('OIDs supplied is of invalid type/format')

        oid = pack('>B', 40 * oidValueNumberList[0] + oidValueNumberList[1])
        for number in oidValueNumberList[2:]:
            if number < 128:
                oid += pack('>B', number)
            else:
                oid += self.__ConvertToMultipleBytes(number)
        return oid

    def __ConvertToMultipleBytes(self, number):
        binaryNumberSplit = re.findall('[0-1]{7}', bin(number)[2:].zfill(math.ceil(len(bin(number)[2:]) / 7) * 7))
        return pack('>' + 'B' * len(binaryNumberSplit),
                    *[int(i, 2) if e == len(binaryNumberSplit) - 1 else int(i, 2) + 0x80 for e, i in
                      enumerate(binaryNumberSplit)])

    def __RebuildOIDString(self, oidBytes):
        if oidBytes[0] == 43:
            oid = [1, 3]
        else:
            oid = [0, 0]
        highBitCheck = False
        oidbin = ''
        for byte in oidBytes[1:]:
            if byte < 127:
                if highBitCheck:
                    oidbin += bin(byte)[2:].zfill(7)
                    oid.append(int(oidbin, 2))
                    oidbin = ''
                    highBitCheck = False
                else:
                    oid.append(byte)
            else:
                oidbin += bin(byte - 0x80)[2:].zfill(7)
                highBitCheck = True
        return '.'.join([str(i) for i in oid])


class SerialClass(SerialInterface, DeviceSerialClass):
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):
    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
