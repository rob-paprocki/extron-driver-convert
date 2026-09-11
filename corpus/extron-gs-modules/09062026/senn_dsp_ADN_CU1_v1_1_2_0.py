from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import time

class DeviceClass:
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ConferenceMode': {'Status': {}},
            'FloorEqualizer': {'Parameters': ['Type'], 'Status': {}},
            'MaxOpenMics': {'Status': {}},
            'MaxRequestMics': {'Status': {}},
            'MicLoudspeakerMute': {'Status': {}},
            'MuteAll': {'Status': {}},
            'Reboot': {'Status': {}},
            'Record': {'Status': {}},
            'Refresh': {'Status': {}},
            'Volume': {'Status': {}},
            'WiredMicLapsedTalkTime': {'Parameters': ['Mic Number'], 'Status': {}},
            'WiredMicrophone': {'Parameters': ['Mic Number'], 'Status': {}},
            'WirelessMicLapsedTalkTime': {'Parameters': ['Serial Number'], 'Status': {}},
            'WirelessMicrophone': {'Parameters': ['Serial Number'], 'Status': {}},
            'XLREnable': {'Parameters': ['Type'], 'Status': {}},
            'XLRInEq': {'Parameters': ['Type'], 'Status': {}},
            'XLROutEq': {'Parameters': ['Type'], 'Status': {}},
            'XLROutVolume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ConferenceMode ([1-4]);'), self.__MatchConferenceMode, None)
            self.AddMatchString(re.compile(b'(FloorEqualizerHigh|FloorEqualizerMid|FloorEqualizerLow) ([0-9]{1,2});'), self.__MatchFloorEqualizer, None)
            self.AddMatchString(re.compile(b'MaxOpenMic ([1-9]|10);'), self.__MatchMaxOpenMics, None)
            self.AddMatchString(re.compile(b'MaxSpeakReqListLength ([1-9]|10);'), self.__MatchMaxRequestMics, None)
            self.AddMatchString(re.compile(b'SwitchableMicVolumeIsActive (0|1);'), self.__MatchMicLoudspeakerMute, None)
            self.AddMatchString(re.compile(b'HdRecordIsActive (0|1);'), self.__MatchRecord, None)
            self.AddMatchString(re.compile(b'FloorVolume ([0-9]{1,2});'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'LapsedTalkTime ([0-9]|[1-9][0-9]|100) (\d+);'), self.__MatchWiredMicLapsedTalkTime, None)
            self.AddMatchString(re.compile(b'MicStatus ([0-9]|[1-9][0-9]|100) ([0-9]|10|11);'), self.__MatchWiredMicrophone, None)
            self.AddMatchString(re.compile(b'LapsedTalkTimeSN ([\S]+) (\d+);'), self.__MatchWirelessMicLapsedTalkTime, None)
            self.AddMatchString(re.compile(b'MicStatusSN ([\S]+) ([0-9]|10|11);'), self.__MatchWirelessMicrophone, None)
            self.AddMatchString(re.compile(b'(XLRinStatus|XLRoutStatus) (0|1);'), self.__MatchXLREnable, None)
            self.AddMatchString(re.compile(b'(XLRinEqHigh|XLRinEqMid|XLRinEqLow) ([0-9]{1,2});'), self.__MatchXLRInEq, None)
            self.AddMatchString(re.compile(b'(XLRoutEqHigh|XLRoutEqMid|XLRoutEqLow) ([0-9]{1,2});'), self.__MatchXLROutEq, None)
            self.AddMatchString(re.compile(b'XLRoutVolume ([0-9]{1,2});'), self.__MatchXLROutVolume, None)
            self.AddMatchString(re.compile(b'error (1000|1010|1020|1030|1040|1050|1060|1070):'), self.__MatchError, None)

    def SetConferenceMode(self, value, qualifier):

        ValueStateValues = {
            'Automatic': 'ConferenceMode 1;',
            'Override': 'ConferenceMode 2;',
            'Request': 'ConferenceMode 3;',
            'Push To Talk': 'ConferenceMode 4;'
        }

        if value in ValueStateValues:
            ConferenceModeCmdString = ValueStateValues[value]
            self.__SetHelper('ConferenceMode', ConferenceModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceMode')

    def UpdateConferenceMode(self, value, qualifier):

        ConferenceModeCmdString = 'ConferenceMode;'
        self.__UpdateHelper('ConferenceMode', ConferenceModeCmdString, value, qualifier)

    def __MatchConferenceMode(self, match, tag):

        ValueStateValues = {
            '1': 'Automatic',
            '2': 'Override',
            '3': 'Request',
            '4': 'Push To Talk'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ConferenceMode', value, None)

    def SetFloorEqualizer(self, value, qualifier):

        TypeStates = {
            'Low': 'FloorEqualizerLow',
            'Mid': 'FloorEqualizerMid',
            'High': 'FloorEqualizerHigh'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        type_val = qualifier['Type']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val in TypeStates:
            level = 13 - value
            FloorEqualizerCmdString = ''.join([TypeStates[type_val], ' ', str(level), ';'])
            self.__SetHelper('FloorEqualizer', FloorEqualizerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFloorEqualizer')

    def UpdateFloorEqualizer(self, value, qualifier):

        TypeStates = {
            'Low': b'FloorEqualizerLow;',
            'Mid': b'FloorEqualizerMid;',
            'High': b'FloorEqualizerHigh;'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            FloorEqualizerCmdString = TypeStates[type_val]
            self.__UpdateHelper('FloorEqualizer', FloorEqualizerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFloorEqualizer')

    def __MatchFloorEqualizer(self, match, tag):

        TypeStates = {
            'FloorEqualizerLow': 'Low',
            'FloorEqualizerMid': 'Mid',
            'FloorEqualizerHigh': 'High',
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        level = int(match.group(2).decode())
        if 1 <= level <= 25:
            value = 13 - level
            self.WriteStatus('FloorEqualizer', value, qualifier)

    def SetMaxOpenMics(self, value, qualifier):

        if 1 <= int(value) <= 10:
            MaxOpenMicsCmdString = 'MaxOpenMic {0};'.format(value)
            self.__SetHelper('MaxOpenMics', MaxOpenMicsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaxOpenMics')

    def UpdateMaxOpenMics(self, value, qualifier):

        MaxOpenMicsCmdString = 'MaxOpenMic;'
        self.__UpdateHelper('MaxOpenMics', MaxOpenMicsCmdString, value, qualifier)

    def __MatchMaxOpenMics(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MaxOpenMics', value, None)

    def SetMaxRequestMics(self, value, qualifier):

        if 1 <= int(value) <= 10:
            MaxRequestMicsCmdString = 'MaxSpeakReqListLength {0};'.format(value)
            self.__SetHelper('MaxRequestMics', MaxRequestMicsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaxRequestMics')

    def UpdateMaxRequestMics(self, value, qualifier):

        MaxRequestMicsCmdString = 'MaxSpeakReqListLength;'
        self.__UpdateHelper('MaxRequestMics', MaxRequestMicsCmdString, value, qualifier)

    def __MatchMaxRequestMics(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MaxRequestMics', value, None)

    def SetMicLoudspeakerMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'SwitchableMicVolumeIsActive 1;',
            'Off': 'SwitchableMicVolumeIsActive 0;',
        }

        if value in ValueStateValues:
            MicLoudspeakerMuteCmdString = ValueStateValues[value]
            self.__SetHelper('MicLoudspeakerMute', MicLoudspeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLoudspeakerMute')

    def UpdateMicLoudspeakerMute(self, value, qualifier):

        MicLoudspeakerMuteCmdString = 'SwitchableMicVolumeIsActive;'
        self.__UpdateHelper('MicLoudspeakerMute', MicLoudspeakerMuteCmdString, value, qualifier)

    def __MatchMicLoudspeakerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MicLoudspeakerMute', value, None)

    def SetMuteAll(self, value, qualifier):

        MuteAllCmdString = 'AllMicsOff 1;'
        self.__SetHelper('MuteAll', MuteAllCmdString, value, qualifier)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'ReinitSystem 1;'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'On': 'HdRecordIsActive 1;',
            'Off': 'HdRecordIsActive 0;'
        }

        if value in ValueStateValues:
            RecordCmdString = ValueStateValues[value]
            self.__SetHelper('Record', RecordCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecord')

    def UpdateRecord(self, value, qualifier):

        RecordCmdString = 'HdRecordIsActive;'
        self.__UpdateHelper('Record', RecordCmdString, value, qualifier)

    def __MatchRecord(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Record', value, None)

    def SetRefresh(self, value, qualifier):

        for mic_num in range(50):
            RefreshCmdString = 'MicStatus {0};'.format(str(mic_num + 1))
            self.__SetHelper('Refresh', RefreshCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 32
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'FloorVolume {0};'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'FloorVolume;'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 32:
            self.WriteStatus('Volume', value, None)

    def __MatchWiredMicLapsedTalkTime(self, match, tag):

        qualifier = {}
        qualifier['Mic Number'] = match.group(1).decode()
        value = time.strftime("%H:%M:%S", time.gmtime(int(match.group(2).decode())))
        self.WriteStatus('WiredMicLapsedTalkTime', value, qualifier)

    def SetWiredMicrophone(self, value, qualifier):

        mic_number = qualifier['Mic Number']
        if 1 <= int(mic_number) <= 100:
            WiredMicrophoneCmdString = 'MicButton {0};'.format(mic_number)
            self.__SetHelper('WiredMicrophone', WiredMicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWiredMicrophone')

    def UpdateWiredMicrophone(self, value, qualifier):

        mic_number = qualifier['Mic Number']
        if 1 <= int(mic_number) <= 100:
            WiredMicrophoneCmdString = 'MicStatus {0};'.format(mic_number)
            self.__UpdateHelper('WiredMicrophone', WiredMicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWiredMicrophone')

    def __MatchWiredMicrophone(self, match, tag):

        ValueStateValues = {
            '0': 'Unknown',
            '1': 'Mic On',
            '2': 'Mic On Muted',
            '3': 'Mic On Premonition',
            '4': 'Mic On Premonition Muted',
            '5': 'Mic On Overrun',
            '6': 'Mic On Overrun Muted',
            '7': 'Mic Off',
            '8': 'Mic Off Request',
            '9': 'Mapping Mode',
            '10': 'Service Calibrate Mic',
            '11': 'Mapping Mode Request'
        }

        qualifier = {}
        qualifier['Mic Number'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('WiredMicrophone', value, qualifier)

    def __MatchWirelessMicLapsedTalkTime(self, match, tag):

        qualifier = {}
        qualifier['Serial Number'] = match.group(1).decode()
        value = time.strftime("%H:%M:%S", time.gmtime(int(match.group(2).decode())))
        self.WriteStatus('WirelessMicLapsedTalkTime', value, qualifier)

    def SetWirelessMicrophone(self, value, qualifier):

        serial_number = qualifier['Serial Number']
        if serial_number:
            WirelessMicrophoneCmdString = 'MicButtonSN {0};'.format(serial_number)
            self.__SetHelper('WirelessMicrophone', WirelessMicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWirelessMicrophone')

    def UpdateWirelessMicrophone(self, value, qualifier):

        serial_number = qualifier['Serial Number']
        if serial_number:
            WirelessMicrophoneCmdString = 'MicStatusSN {0};'.format(serial_number)
            self.__UpdateHelper('WirelessMicrophone', WirelessMicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWirelessMicrophone')

    def __MatchWirelessMicrophone(self, match, tag):

        ValueStateValues = {
            '0': 'Unknown',
            '1': 'Mic On',
            '2': 'Mic On Muted',
            '3': 'Mic On Premonition',
            '4': 'Mic On Premonition Muted',
            '5': 'Mic On Overrun',
            '6': 'Mic On Overrun Muted',
            '7': 'Mic Off',
            '8': 'Mic Off Request',
            '9': 'Mapping Mode',
            '10': 'Service Calibrate Mic',
            '11': 'Mapping Mode Request'
        }

        qualifier = {}
        qualifier['Serial Number'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('WirelessMicrophone', value, qualifier)

    def SetXLREnable(self, value, qualifier):

        TypeStates = {
            'In': 'XLRinStatus',
            'Out': 'XLRoutStatus'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            XLREnableCmdString = ''.join([TypeStates[type_val], ' ', ValueStateValues[value], ';'])
            self.__SetHelper('XLREnable', XLREnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXLREnable')

    def UpdateXLREnable(self, value, qualifier):

        TypeStates = {
            'In': 'XLRinStatus;',
            'Out': 'XLRoutStatus;'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            XLREnableCmdString = TypeStates[type_val]
            self.__UpdateHelper('XLREnable', XLREnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateXLREnable')

    def __MatchXLREnable(self, match, tag):

        TypeStates = {
            'XLRinStatus': 'In',
            'XLRoutStatus': 'Out'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('XLREnable', value, qualifier)

    def SetXLRInEq(self, value, qualifier):

        TypeStates = {
            'Low': 'XLRinEqLow',
            'Mid': 'XLRinEqMid',
            'High': 'XLRinEqHigh'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        type_val = qualifier['Type']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val in TypeStates:
            level = 13 - value
            XLRInEqCmdString = ''.join([TypeStates[type_val], ' ', str(level), ';'])
            self.__SetHelper('XLRInEq', XLRInEqCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXLRInEq')

    def UpdateXLRInEq(self, value, qualifier):

        TypeStates = {
            'Low': 'XLRinEqLow;',
            'Mid': 'XLRinEqMid;',
            'High': 'XLRinEqHigh;'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            XLRInEqCmdString = TypeStates[type_val]
            self.__UpdateHelper('XLRInEq', XLRInEqCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateXLRInEq')

    def __MatchXLRInEq(self, match, tag):

        TypeStates = {
            'XLRinEqLow': 'Low',
            'XLRinEqMid': 'Mid',
            'XLRinEqHigh': 'High'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        if 1 <= value <= 25:
            self.WriteStatus('XLRInEq', 13 - value, qualifier)

    def SetXLROutEq(self, value, qualifier):

        TypeStates = {
            'Low': 'XLRoutEqLow',
            'Mid': 'XLRoutEqMid',
            'High': 'XLRoutEqHigh'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        type_val = qualifier['Type']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val in TypeStates:
            level = 13 - value
            XLROutEqCmdString = ''.join([TypeStates[type_val], ' ', str(level), ';'])
            self.__SetHelper('XLROutEq', XLROutEqCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXLROutEq')

    def UpdateXLROutEq(self, value, qualifier):

        TypeStates = {
            'Low': 'XLRoutEqLow;',
            'Mid': 'XLRoutEqMid;',
            'High': 'XLRoutEqHigh;'
        }
        type_val = qualifier['Type']
        if type_val in TypeStates:
            XLROutEqCmdString = TypeStates[type_val]
            self.__UpdateHelper('XLROutEq', XLROutEqCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateXLROutEq')

    def __MatchXLROutEq(self, match, tag):

        TypeStates = {
            'XLRoutEqLow': 'Low',
            'XLRoutEqMid': 'Mid',
            'XLRoutEqHigh': 'High'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        if 1 <= value <= 25:
            self.WriteStatus('XLROutEq', 13 - value, qualifier)

    def SetXLROutVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -20,
            'Max': 11
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            level = 21 + value
            XLROutVolumeCmdString = 'XLRoutVolume {0};'.format(level)
            self.__SetHelper('XLROutVolume', XLROutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXLROutVolume')

    def UpdateXLROutVolume(self, value, qualifier):

        XLROutVolumeCmdString = 'XLRoutVolume;'
        self.__UpdateHelper('XLROutVolume', XLROutVolumeCmdString, value, qualifier)

    def __MatchXLROutVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('XLROutVolume', value - 21, None)

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
        self.counter = 0

        Error_Codes = {
            '1000': 'Invalid Command',
            '1010': 'Invalid parameter',
            '1020': 'Value out of range',
            '1030': 'Relative parameter is not supported',
            '1040': 'Invalid number of parameters',
            '1050': 'Get request not allowed',
            '1060': 'Set request not allowed',
            '1070': 'Processing of request currently not possible',
        }

        self.Error([Error_Codes[match.group(1).decode()]])

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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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
