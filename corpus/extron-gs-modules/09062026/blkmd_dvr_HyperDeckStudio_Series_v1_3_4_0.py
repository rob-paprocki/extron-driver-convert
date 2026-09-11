from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import time
import re


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Jog': {'Status': {}},
            'Preview': {'Status': {}},
            'Review': {'Status': {}},
            'Shuttle': {'Status': {}},
            'Standby': {'Status': {}},
            'Transport': {'Status': {}},
            'DeviceStatus': {'Status': {}},
        }

    def SetFreeze(self, value, qualifier):

        FreezeNames = {
            'On': b'\x20\x6B\x8B',
            'Off': b'\x20\x6A\x8A',
        }

        CommandString = FreezeNames[value]
        self.__SetHelper('Freeze', CommandString, value, qualifier)

    def SetJog(self, value, qualifier):

        ValueStateValues = {
            'Fwd 1': b'\x21\x11\x32',
            'Fwd 2': b'\x22\x11\x33',
            'Rev 1': b'\x21\x21\x42',
            'Rev 2': b'\x22\x21\x43'
        }

        JogCmdString = ValueStateValues[value]
        self.__SetHelper('Jog', JogCmdString, value, qualifier)

    def SetPreview(self, value, qualifier):
        PreviewCmdString = b'\x20\x40\x60'
        self.__SetHelper('Preview', PreviewCmdString, value, qualifier)

    def SetReview(self, value, qualifier):

        ReviewCmdString = b'\x20\x41\x61'
        self.__SetHelper('Review', ReviewCmdString, value, qualifier)

    def SetShuttle(self, value, qualifier):

        ValueStateValues = {
            'Fwd 1': b'\x21\x13\x34',
            'Fwd 2': b'\x22\x13\x35',
            'Rev 1': b'\x21\x23\x44',
            'Rev 2': b'\x22\x23\x45'
        }

        ShuttleCmdString = ValueStateValues[value]
        self.__SetHelper('Shuttle', ShuttleCmdString, value, qualifier)

    def SetStandby(self, value, qualifier):

        StandbyNames = {
            'On': b'\x20\x05\x25',
            'Off': b'\x20\x04\x24',
        }

        CommandString = StandbyNames[value]

        self.__SetHelper('Standby', CommandString, value, qualifier)

    def SetTransport(self, value, qualifier):

        TransportNames = {
            'Play': b'\x20\x01\x21',
            'Stop': b'\x20\x00\x20',
            'Record': b'\x20\x02\x22',
            'Eject': b'\x20\x0F\x2F',
            'Fast Fwd': b'\x20\x10\x30',
            'Rew': b'\x20\x20\x40',
        }

        CommandString = TransportNames[value]

        self.__SetHelper('Transport', CommandString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusNames = {
            b'\x01': 'Play',
            b'\x20': 'Stop',
            b'\x04': 'Fast Fwd',
            b'\x08': 'Rew',
            b'\x80': 'Standby',
            b'\x02': 'Record'
        }

        CommandString = b'\x70\x20\x90'
        res = self.__UpdateHelper('DeviceStatus', CommandString, value, qualifier)
        if res:
            try:
                value = DeviceStatusNames[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except  (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)

            return self.__CheckResponseForErrors(command + ':', res)

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
        self.Models = {
            'HyperDeck Studio': self.blkmd_37_382_std,
            'HyperDeck Studio Pro': self.blkmd_37_382_pro,
            'HyperDeck Studio 12G': self.blkmd_37_382_12G,
            'HyperDeck Studio Mini': self.blkmd_37_382_std,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Status': {}},
            'ClipCount': {'Status': {}},
            'ClipName': {'Parameters': ['Clip ID'], 'Status': {}},
            'ClipTimecodeDuration': {'Parameters': ['Clip ID'], 'Status': {}},
            'ClipTimecodeStart': {'Parameters': ['Clip ID'], 'Status': {}},
            'ErrorStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Override': {'Status': {}},
            'PlayLoop': {'Status': {}},
            'PlaySingleClip': {'Status': {}},
            'PlaySpeed': {'Status': {}},
            'PreviewMode': {'Status': {}},
            'SlotID': {'Status': {}},
            'TimecodeDisplayStatus': {'Status': {}},
            'TimecodeGoTo': {'Parameters': ['Action'], 'Status': {}},
            'TimecodeGoToClip': {'Parameters': ['Action', 'Clip ID'], 'Status': {}},
            'TimecodeMemory': {'Parameters': ['Action'], 'Status': {}},
            'TimecodeMemoryStatus': {'Parameters': ['Number'], 'Status': {}},
            'TimecodeStatus': {'Status': {}},
            'Transport': {'Status': {}},
            'TransportInformation': {'Status': {}},
            'VideoFormat': {'Status': {}},
            'VideoInput': {'Status': {}},
        }

        self.ClipCount = 0
        self.Timecode = ''
        self.DisplayTimecode = ''
        self.TimecodeMemory = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'audio input: (embedded|XLR|RCA)\r\n'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'(\d+) clips info:\r\nclip count: (\d+)\r\n'), self.__MatchClipCount, None)
            self.AddMatchString(re.compile(b'(\d+): (.+) (\d\d:\d\d:\d\d:\d\d) (\d\d:\d\d:\d\d:\d\d)\r\n'), self.__MatchClipInfo, None)
            self.AddMatchString(re.compile(b'enabled: (true|false)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'override: (true|false)\r\n'), self.__MatchOverride, None)
            self.AddMatchString(re.compile(b'status: (?P<transport>preview|stopped|play|forward|rewind|jog|shuttle|record)\r\nspeed: (?P<speed>[+-]?\d+)\r\nslot id: (?P<slotID>[12]|none)\r\nclip id: (?P<clipID>\d+|none)\r\n(single clip: (?P<singleClip>false|true)\r\n)?display timecode: (?P<display>\d\d:\d\d:\d\d[:;]\d\d)\r\ntimecode: (?P<timecode>\d\d:\d\d:\d\d[:;]\d\d)\r\nvideo format: (?P<videoFormat>.+)\r\nloop: (?P<loop>false|true)\r\n'), self.__MatchTransportInformation, None)
            self.AddMatchString(re.compile(b'video input: (SDI|HDMI|component)\r\n'), self.__MatchVideoInput, None)
            self.AddMatchString(re.compile(b'([0-9]{3}) (syntax error|unsupported parameter|invalid value|unsupported|disk full|no disk|disk error|timeline empty|out of range|no input|remote control disabled|connection rejected|invalid state).*?\r\n', re.DOTALL), self.__MatchError, None)

        self.SetRemoteEnable(None, None)

    def SetRemoteEnable(self, value, qualifier):
        self.Send('remote: enable: true\r\n')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Embedded': 'configuration: audio input: embedded\r\n',
            'XLR': 'configuration: audio input: XLR\r\n',
            'RCA': 'configuration: audio input: RCA\r\n'
        }

        AudioInputCmdString = ValueStateValues[value]
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdString = 'configuration\r\n'
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            'embedded': 'Embedded',
            'XLR': 'XLR',
            'RCA': 'RCA'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInput', value, None)

    def UpdateClipCount(self, value, qualifier):

        ClipCmdString = 'clips get\r\n'
        self.__UpdateHelper('ClipCount', ClipCmdString, value, qualifier)

    def __MatchClipCount(self, match, tag):

        self.ClipCount = int(match.group(2).decode())
        self.WriteStatus('ClipCount', self.ClipCount, None)

    def UpdateClipName(self, value, qualifier):
        if int(qualifier['Clip ID']) < self.ClipCount:
            ClipNameCmdString = 'clips get\r\n'
            self.__UpdateHelper('ClipName', ClipNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateClipName')

    def __MatchClipInfo(self, match, tag):

        qualifier = {'Clip ID': match.group(1).decode()}
        nameValue = match.group(2).decode()
        startValue = match.group(3).decode()
        durationValue = match.group(4).decode()
        self.WriteStatus('ClipName', nameValue, qualifier)
        self.WriteStatus('ClipTimecodeStart', startValue, qualifier)
        self.WriteStatus('ClipTimecodeDuration', durationValue, qualifier)

    def UpdateClipTimecodeDuration(self, value, qualifier):

        self.UpdateClipName(value, qualifier)

    def UpdateClipTimecodeStart(self, value, qualifier):

        self.UpdateClipName(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'remote: enable: false\r\n',
            'Off': 'remote: enable: true\r\n'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'remote\r\n'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            'false': 'On',
            'true': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetOverride(self, value, qualifier):

        ValueStateValues = {
            'On': 'remote: override: true\r\n',
            'Off': 'remote: override: false\r\n'
        }

        OverrideCmdString = ValueStateValues[value]
        self.__SetHelper('Override', OverrideCmdString, value, qualifier)

    def UpdateOverride(self, value, qualifier):

        OverrideCmdString = 'remote\r\n'
        self.__UpdateHelper('Override', OverrideCmdString, value, qualifier)

    def __MatchOverride(self, match, tag):

        ValueStateValues = {
            'true': 'On',
            'false': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Override', value, None)

    def SetPlayLoop(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        PlayLoopCmdString = 'play: loop: {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PlayLoop', PlayLoopCmdString, value, qualifier)

    def UpdatePlayLoop(self, value, qualifier):
        self.UpdateTransportInformation(value, qualifier)

    def SetPlaySingleClip(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        PlaySingleClipCmdString = 'play: single clip: {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PlaySingleClip', PlaySingleClipCmdString, value, qualifier)

    def SetPlaySpeed(self, value, qualifier):

        ValueConstraints = {
            'Min': -1600,
            'Max': 1600
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PlaySpeedCmdString = 'play: speed: {0}\r\n'.format(value)
            self.__SetHelper('PlaySpeed', PlaySpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaySpeed')

    def UpdatePlaySpeed(self, value, qualifier):
        self.UpdateTransportInformation(value, qualifier)

    def SetPreviewMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'preview: enable: true\r\n',
            'Off': 'preview: enable: false\r\n'
        }

        PreviewModeCmdString = ValueStateValues[value]
        self.__SetHelper('PreviewMode', PreviewModeCmdString, value, qualifier)

    def SetSlotID(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
        }

        SlotIDCmdString = 'slot select: slot id: {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('SlotID', SlotIDCmdString, value, qualifier)

    def UpdateSlotID(self, value, qualifier):
        self.UpdateTransportInformation(value, qualifier)

    def SetTimecodeGoTo(self, value, qualifier):

        action = {
            'Go to Specified Timecode': '',
            'Move Forward': '+',
            'Move Backward': '-'
        }[qualifier['Action']]

        state = {
            'Timecode': self.Timecode,
            'Display Timecode': self.DisplayTimecode,
        }[value]

        if state:
            TimecodeGoToCmdString = 'goto: timecode: {0}{1}\r\n'.format(action, state)
            self.__SetHelper('TimecodeGoTo', TimecodeGoToCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimecodeGoTo')

    def SetTimecodeGoToClip(self, value, qualifier):

        action = {
            'Go to Specified Timecode': '',
            'Move Forward': '+',
            'Move Backward': '-'
        }[qualifier['Action']]

        state = {
            'Timecode Start': self.ReadStatus('ClipTimecodeStart', {'Clip ID': qualifier['Clip ID']}),
            'Timecode Duration': self.ReadStatus('ClipTimecodeDuration', {'Clip ID': qualifier['Clip ID']})
        }[value]

        if state:
            TimecodeGoToClipCmdString = 'goto: timecode: {0}{1}\r\n'.format(action, state)
            self.__SetHelper('TimecodeGoToClip', TimecodeGoToClipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimecodeGoToClip')

    def SetTimecodeMemory(self, value, qualifier):

        if 1 <= int(value) <= 10:
            if qualifier['Action'] == 'Save' and self.Timecode:
                self.TimecodeMemory[value] = self.Timecode
                self.WriteStatus('TimecodeMemoryStatus', self.TimecodeMemory[value], {'Number': value})
            elif qualifier['Action'] == 'Recall':
                if value in self.TimecodeMemory:
                    TimecodeMemoryCmdString = 'goto: timecode: {0}\r\n'.format(self.TimecodeMemory[value])
                    self.__SetHelper('TimecodeMemory', TimecodeMemoryCmdString, value, qualifier)
                else:
                    self.Error(['Timecode Memory has no timecode in slot number: {0}'.format(value)])
            else:
                self.Discard('Inappropriate Command for SetTimecodeMemory')
        else:
            self.Discard('Inappropriate Command for SetTimecodeMemory')

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'play\r\n',
            'Stop': 'stop\r\n',
            'Record': 'record\r\n',
            'Next': 'goto: clip id: +1\r\n',
            'Previous': 'goto: clip id: -1\r\n',
            'Forward': 'goto: timecode: +00:00:00:01\r\n',
            'Reverse': 'goto: timecode: -00:00:00:01\r\n',
            'Fast Forward': 'goto: timecode: +00:00:00:05\r\n',
            'Fast Reverse': 'goto: timecode: -00:00:00:05\r\n',
            'Start': 'goto: clip: start\r\n',
            'End': 'goto: clip: end\r\n'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransportInformation(self, value, qualifier):

        TransportInformationCmdString = 'transport info\r\n'
        self.__UpdateHelper('TransportInformation', TransportInformationCmdString, value, qualifier)

    def __MatchTransportInformation(self, match, tag):

        transportStateValues = {
            'play': 'Playing',
            'stopped': 'Stopped',
            'forward': 'Forward',
            'jog': 'Jog',
            'shuttle': 'Shuttle',
            'record': 'Record',
            'rewind': 'Rewind',
            'preview': 'Preview'
        }
        SlotIDStateValues = {
            '1': '1',
            '2': '2',
            'none': 'None'
        }
        PlayStateValues = {
            'true': 'On',
            'false': 'Off'
        }

        try:
            transportValue = transportStateValues[match.group('transport').decode()]
            self.WriteStatus('TransportInformation', transportValue, None)
        except KeyError:
            self.Error(['Transport State: Invalid/unexpected response'])

        try:
            slotIDValue = SlotIDStateValues[match.group('slotID').decode()]
            self.WriteStatus('SlotID', slotIDValue, None)
        except KeyError:
            self.Error(['Slot ID: Invalid/unexpected response'])

        try:
            speedValue = int(match.group('speed').decode())
            self.WriteStatus('PlaySpeed', speedValue, None)
        except ValueError:
            self.Error(['Play Speed: Invalid/unexpected response'])

        try:
            videoFormatValue = self.VideoFormatStateValues[match.group('videoFormat').decode()]
            self.WriteStatus('VideoFormat', videoFormatValue, None)
        except KeyError:
            self.Error(['Video Format: Invalid/unexpected response'])

        try:
            loopValue = PlayStateValues[match.group('loop').decode()]
            self.WriteStatus('PlayLoop', loopValue, None)
        except KeyError:
            self.Error(['Play Loop: Invalid/unexpected response'])

        if self.DisplayTimecode != match.group('display').decode():
            self.DisplayTimecode = match.group('display').decode()
            self.WriteStatus('TimecodeDisplayStatus', self.DisplayTimecode, None)
        if self.Timecode != match.group('timecode').decode():
            self.Timecode = match.group('timecode').decode()
            self.WriteStatus('TimecodeStatus', self.Timecode, None)

    def SetVideoFormat(self, value, qualifier):

        VideoFormatCmdString = 'slot select: video format: {0}\r\n'.format(self.VideoFormatStateValues[value])
        self.__SetHelper('VideoFormat', VideoFormatCmdString, value, qualifier)

    def UpdateVideoFormat(self, value, qualifier):
        self.UpdateTransportInformation(value, qualifier)

    def SetVideoInput(self, value, qualifier):

        VideoInputCmdString = self.VideoInputStateValues[value]
        self.__SetHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def UpdateVideoInput(self, value, qualifier):

        VideoInputCmdString = 'configuration\r\n'
        self.__UpdateHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def __MatchVideoInput(self, match, tag):

        value = self.VideoInputStateNames[match.group(1).decode()]
        self.WriteStatus('VideoInput', value, None)

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

        ERROR_CODES = {
            '100': 'Syntax error.',
            '101': 'Unsupported parameter.',
            '102': 'Invalid value.',
            '103': 'Unsupported.',
            '104': 'Disk full.',
            '105': 'No disk.',
            '106': 'Disk error.',
            '107': 'Timeline empty.',
            '109': 'Out of range.',
            '110': 'No input.',
            '111': 'Remote control disabled.',
            '120': 'Connection rejected.',
            '150': 'Invalid state.'
        }

        self.Error([ERROR_CODES[match.group(1).decode()]])
        self.WriteStatus('ErrorStatus', ERROR_CODES[match.group(1).decode()][:-1].title(), None)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetRemoteEnable(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.ClipCount = 0
        self.Timecode = ''
        self.DisplayTimecode = ''
        self.TimecodeMemory = {}

    def blkmd_37_382_pro(self):
        self.VideoFormatStateValues = {
            'NTSC': 'NTSC',
            'PAL': 'PAL',
            'NTSCp': 'NTSCp',
            'PALp': 'PALp',
            '720p50': '720p50',
            '720p5994': '720p5994',
            '720p60': '720p60',
            '1080p23976': '1080p23976',
            '1080p24': '1080p24',
            '1080p25': '1080p25',
            '1080p2997': '1080p2997',
            '1080p30': '1080p30',
            '1080i50': '1080i50',
            '1080i5994': '1080i5994',
            '1080i60': '1080i60',
            '4Kp23976': '4Kp23976',
            '4Kp24': '4Kp24',
            '4Kp25': '4Kp25',
            '4Kp2997': '4Kp2997',
            '4Kp30': '4Kp30'
        }

        self.VideoInputStateValues = {
            'SDI': 'configuration: video input: SDI\r\n',
            'HDMI': 'configuration: video input: HDMI\r\n',
            'Component': 'configuration: video input: component\r\n'
        }
        self.VideoInputStateNames = {
            'SDI': 'SDI',
            'HDMI': 'HDMI',
            'component': 'Component'
        }

    def blkmd_37_382_std(self):
        self.VideoFormatStateValues = {
            'NTSC': 'NTSC',
            'PAL': 'PAL',
            'NTSCp': 'NTSCp',
            'PALp': 'PALp',
            '720p50': '720p50',
            '720p5994': '720p5994',
            '720p60': '720p60',
            '1080p23976': '1080p23976',
            '1080p24': '1080p24',
            '1080p25': '1080p25',
            '1080p2997': '1080p2997',
            '1080p30': '1080p30',
            '1080i50': '1080i50',
            '1080i5994': '1080i5994',
            '1080i60': '1080i60',
            '1080p50': '1080p50'
        }
        self.VideoInputStateValues = {
            'SDI': 'configuration: video input: SDI\r\n',
            'HDMI': 'configuration: video input: HDMI\r\n'
        }
        self.VideoInputStateNames = {
            'SDI': 'SDI',
            'HDMI': 'HDMI'
        }

    def blkmd_37_382_12G(self):
        self.VideoFormatStateValues = {
            'NTSC': 'NTSC',
            'PAL': 'PAL',
            'NTSCp': 'NTSCp',
            'PALp': 'PALp',
            '720p50': '720p50',
            '720p5994': '720p5994',
            '720p60': '720p60',
            '1080p23976': '1080p23976',
            '1080p24': '1080p24',
            '1080p25': '1080p25',
            '1080p2997': '1080p2997',
            '1080p30': '1080p30',
            '1080i50': '1080i50',
            '1080i5994': '1080i5994',
            '1080i60': '1080i60',
            '4Kp23976': '4Kp23976',
            '4Kp24': '4Kp24',
            '4Kp25': '4Kp25',
            '4Kp2997': '4Kp2997',
            '4Kp30': '4Kp30',
            '4Kp50': '4Kp50',
            '4Kp5994': '4Kp5994',
            '4Kp60': '4Kp60'
        }
        self.VideoInputStateValues = {
            'SDI': 'configuration: video input: SDI\r\n',
            'HDMI': 'configuration: video input: HDMI\r\n'
        }
        self.VideoInputStateNames = {
            'SDI': 'SDI',
            'HDMI': 'HDMI'
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
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
