from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

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
            'AudioGainAttenuation': {'Status': {}},
            'AudioInputFormat': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'BlackSignal': {'Status': {}},
            'BlackSignalResolution': {'Status': {}},
            'HDCPInputAuthorization': {'Status': {}},
            'HDCPStatus': {'Status': {}},
            'HorizontalShift': {'Status': {}},
            'ImageReset': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'PixelPhase': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'VerticalShift': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aud([-+][0-9]{2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'AfmtI([0-2])\r\n'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'AfmtB(0|1)\r\n'), self.__MatchBlackSignal, None)
            self.AddMatchString(re.compile(b'AfmtA(2|4|6)\r\n'), self.__MatchBlackSignalResolution, None)
            self.AddMatchString(re.compile(b'HdcpE(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI0([0-2])\r\n'), self.__MatchHDCPStatus, None)
            self.AddMatchString(re.compile(b'Hctr([0-9]{5})\r\n'), self.__MatchHorizontalShift, None)
            self.AddMatchString(re.compile(b'In(1|2)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Frq(0|1)(0|1)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Phas([0-9]{3})\r\n'), self.__MatchPixelPhase, None)
            self.AddMatchString(re.compile(b'Vctr([0-9]{5})\r\n'), self.__MatchVerticalShift, None)
            self.AddMatchString(re.compile(b'^E(01|06|10|11|12|13|14|17)\r\n'), self.__MatchError, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 24
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:

            if value < 0:
                AudioGainAttenuationCmdString = str(abs(value)) + 'g'

            else:
                AudioGainAttenuationCmdString = str(abs(value)) + 'G'
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        AudioGainAttenuationCmdString = 'G'
        self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AudioGainAttenuation', value, None)

    def SetAudioInputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Digital Embedded': '1',
            'Analog': '2'
        }

        AudioInputFormatCmdString = 'wI' + ValueStateValues[value] + 'AFMT\r'
        self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        AudioInputFormatCmdString = 'wIAFMT\r'
        self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Digital Embedded',
            '2': 'Analog'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInputFormat', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Highest Active Input': '1',
            'Lowest Active Input': '2'
        }

        AutoSwitchModeCmdString = 'w' + ValueStateValues[value] + 'AUSW\r'
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetBlackSignal(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        BlackSignalCmdString = 'wB' + ValueStateValues[value] + 'AFMT\r'
        self.__SetHelper('BlackSignal', BlackSignalCmdString, value, qualifier)

    def UpdateBlackSignal(self, value, qualifier):

        BlackSignalCmdString = 'wBAFMT\r'
        self.__UpdateHelper('BlackSignal', BlackSignalCmdString, value, qualifier)

    def __MatchBlackSignal(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BlackSignal', value, None)

    def SetBlackSignalResolution(self, value, qualifier):

        ValueStateValues = {
            '720p @ 50 Hz': '2',
            '720p @ 60 Hz': '4',
            '1080p @ 60 Hz': '6'
        }

        BlackSignalResolutionCmdString = 'wA' + ValueStateValues[value] + 'AFMT\r'
        self.__SetHelper('BlackSignalResolution', BlackSignalResolutionCmdString, value, qualifier)

    def UpdateBlackSignalResolution(self, value, qualifier):

        BlackSignalResolutionCmdString = 'wAAFMT\r'
        self.__UpdateHelper('BlackSignalResolution', BlackSignalResolutionCmdString, value, qualifier)

    def __MatchBlackSignalResolution(self, match, tag):

        ValueStateValues = {
            '2': '720p @ 50 Hz',
            '4': '720p @ 60 Hz',
            '6': '1080p @ 60 Hz'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BlackSignalResolution', value, None)

    def WriteBlackSignalResolution(self, value, qualifier, context):

        self.WriteStatus('StatusHelper', 'BlackSignalResolution', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        HDCPInputAuthorizationCmdString = 'wE' + ValueStateValues[value] + 'HDCP\r'
        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def UpdateHDCPStatus(self, value, qualifier):

        HDCPStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPStatus', HDCPStatusCmdString, value, qualifier)

    def __MatchHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source',
            '1': 'HDCP Compliant Source',
            '2': 'Non-HDCP Compliant Source'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPStatus', value, None)

    def SetHorizontalShift(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            HorizontalShiftCmdString = 'w' + str(value + 32640) + 'HCTR\r'
            self.__SetHelper('HorizontalShift', HorizontalShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalShift')

    def UpdateHorizontalShift(self, value, qualifier):

        HorizontalShiftCmdString = 'wHCTR\r'
        self.__UpdateHelper('HorizontalShift', HorizontalShiftCmdString, value, qualifier)

    def __MatchHorizontalShift(self, match, tag):

        value = int(match.group(1).decode()) - 32640
        self.WriteStatus('HorizontalShift', value, None)

    def SetImageReset(self, value, qualifier):

        ImageResetCmdString = '1A'
        self.__SetHelper('ImageReset', ImageResetCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2'
        }

        InputCmdString = ValueStateValues[value] + '!'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', '!', value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(1).decode()], {'Input': '1'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(2).decode()], {'Input': '2'})

    def SetPixelPhase(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PixelPhaseCmdString = 'w' + str(value) + 'PHAS\r'
            self.__SetHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPixelPhase')

    def UpdatePixelPhase(self, value, qualifier):

        PixelPhaseCmdString = 'wPHAS\r'
        self.__UpdateHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)

    def __MatchPixelPhase(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('PixelPhase', value, None)

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = value + '.'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = value + ','
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetVerticalShift(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VerticalShiftCmdString = 'w' + str(value + 32640) + 'VCTR\r'
            self.__SetHelper('VerticalShift', VerticalShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalShift')

    def UpdateVerticalShift(self, value, qualifier):

        VerticalShiftCmdString = 'wVCTR\r'
        self.__UpdateHelper('VerticalShift', VerticalShiftCmdString, value, qualifier)

    def __MatchVerticalShift(self, match, tag):

        value = int(match.group(1).decode()) - 32640
        self.WriteStatus('VerticalShift', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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

        ErrorResponses = {
            '01': 'Invalid input number',
            '06': 'Invalid switch attempt in this mode',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type'
        }

        self.Error([ErrorResponses[match.group(1).decode()]])

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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
