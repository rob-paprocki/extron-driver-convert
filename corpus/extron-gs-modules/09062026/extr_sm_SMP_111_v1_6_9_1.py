from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from math import floor

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
            'Alarm': {'Parameters': ['Alarm'], 'Status': {}},
            'AlarmSeverity': {'Parameters': ['Alarm'], 'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioBitrate': {'Status': {}},
            'AudioInputGain': {'Parameters': ['Type'], 'Status': {}},
            'AudioLevel': {'Parameters': ['L/R'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'BitrateControl': {'Parameters': ['Stream'], 'Status': {}},
            'ChapterMarker': {'Status': {}},
            'ClearActiveAlarms': {'Status': {}},
            'CPUUsage': {'Status': {}},
            'CurrentRecordingDuration': {'Status': {}},
            'EDID': {'Status': {}},
            'EjectUSBStorage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FileDestination': {'Parameters': ['Drive'], 'Status': {}},
            'GOPLength': {'Parameters': ['Stream'], 'Status': {}},
            'HDCPStatus': {'Status': {}},
            'HDMIOutputMute': {'Parameters': ['Type'], 'Status': {}},
            'InputAudioMute': {'Parameters': ['Type', 'L/R'], 'Status': {}},
            'Metadata': {'Parameters': ['Type'], 'Status': {}},
            'MetadataStatus': {'Parameters': ['Type'], 'Status': {}},
            'OutputAudioMute': {'Parameters': ['L/R'], 'Status': {}},
            'RCPConnectionStatus': {'Status': {}},
            'RecallEncoderPreset': {'Parameters': ['Stream'], 'Status': {}},
            'Record': {'Status': {}},
            'RecordControl': {'Status': {}},
            'RecordDestination': {'Status': {}},
            'RecordingMode': {'Status': {}},
            'RecordingProfiles': {'Status': {}},
            'RecordingStartCountdown': {'Status': {}},
            'RemainingFreeDiskSpace': {'Parameters': ['Drive'], 'Status': {}},
            'RemainingRecordingTime': {'Parameters': ['Drive'], 'Status': {}},
            'RTMPPrimaryDestination': {'Status': {}},
            'RTMPPrimaryDestinationURLStatus': {'Status': {}},
            'RTMPStream': {'Status': {}},
            'RTSPStreamURL': {'Status': {}},
            'StreamControl': {'Status': {}},
            'StreamingPresetName': {'Parameters': ['Preset'], 'Status': {}},
            'StreamingPresetRecall': {'Status': {}},
            'StreamingPresetSave': {'Status': {}},
            'USBStatus': {'Parameters': ['USB Port'], 'Status': {}},
            'VideoBitrate': {'Parameters': ['Stream'], 'Status': {}},
            'VideoFrameRate': {'Parameters': ['Stream'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'VideoResolution': {'Parameters': ['Stream'], 'Status': {}}
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.ConfiguredMetadataList = []  # keeps track of configured Metadata Status

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Inf39(?:\*<name:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server|firmware_failure|file_upload),level:(warning|critical|info|emergency)>,?)+\r\n'), self.__MatchAlarm, None)
            self.AddMatchString(re.compile(b'Inf39\*(None active)\r\n'), self.__MatchAlarm, "No Alarm")
            self.AddMatchString(re.compile(b'Aspr([1-3])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'BitrA1\*(080|096|128|192|256|320)\r\n'), self.__MatchAudioBitrate, None)
            self.AddMatchString(re.compile(b'DsG(40000|40001|40002|40003)\*(-?\d{1,3})\r\n'), self.__MatchAudioInputGain, None)
            self.AddMatchString(re.compile(b'Inf34\*(-?\d{1,4})\*(-?\d{1,4})\r\n'), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b'DsM4000([0-7])\*([01])\r\n'), self.__MatchInputAudioMute, None)
            self.AddMatchString(re.compile(b'DsM6000([01])\*([01])\r\n'), self.__MatchOutputAudioMute, None)
            self.AddMatchString(re.compile(b'Brct([12])\*([0-2])\r\n'), self.__MatchBitrateControl, None)
            self.AddMatchString(re.compile(b'Inf11\*(\d{1,3})\r\n'), self.__MatchCPUUsage, None)
            self.AddMatchString(re.compile(b'Inf35\*(\d{1,2}):(\d{1,2}):(\d{1,2})\r\n'), self.__MatchCurrentRecordingDuration, None)
            self.AddMatchString(re.compile(b'EdidA(\d{2})\r\n'), self.__MatchEDID, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Inf\*<.*?>\*<.*?>\*<(internal|usbfront|usbrear|usbrcp|auto|N/A|).*?(?:\*?(internal|usbfront|usbrear|usbrcp|N/A|\*))?.*?>\*(?:<([0-9]*)(\*[0-9]*)?(\*N/A)?>\*<.*?>\*<.*?>|<\d*:\d*:\d*>\*<\d*:\d*:\d*>)?\r\n'), self.__MatchFileDestination, None)  # Also handles Remaining Free Disk Space status
            self.AddMatchString(re.compile(b'Gopl([12])\*(\d{1,2})\r\n'), self.__MatchGOPLength, None)
            self.AddMatchString(re.compile(b'HdcpI([0-2])\r\n'), self.__MatchHDCPStatus, None)
            self.AddMatchString(re.compile(b'([AV])mt99\*([01])\r\n'), self.__MatchHDMIOutputMute, None)
            self.AddMatchString(re.compile(b'RcdrM((?P<type>1?[0-9])\*?(?P<value>.*))?\r\n'), self.__MatchMetadataStatus, None)  # this will only catch responses with metadata
            self.AddMatchString(re.compile(b'Inf50(.*)|E25'), self.__MatchRCPConnectionStatus, None)
            self.AddMatchString(re.compile(b'RcdrY([0-2])\r\n'), self.__MatchRecord, None)
            self.AddMatchString(re.compile(b'RcdrX(?P<value>[01])\r\n'), self.__MatchRecordControl, None)
            self.AddMatchString(re.compile(b'RcdrD(00|01|02|03|04|11|12|13|14)\r\n'), self.__MatchRecordDestination, None)
            self.AddMatchString(re.compile(b'Rmod([1-3])\r\n'), self.__MatchRecordingMode, None)
            self.AddMatchString(re.compile(b'RecStart([0-9]{2})\r\n'), self.__MatchRecordingStartCountdown, None)
            self.AddMatchString(re.compile(b'PrstL5\*(00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16)'), self.__MatchRecordingProfiles, None)
            self.AddMatchString(re.compile(b'Vfrm([12])\*([1-8])\r\n'), self.__MatchVideoFrameRate, None)
            self.AddMatchString(re.compile(b'Vres([12])\*([0-5])\r\n'), self.__MatchVideoResolution, None)
            self.AddMatchString(re.compile(b'Inf36\*(?:internal|usbfront|usbrear)?.*? (\d+):(\d{1,2}):(\d{1,2})(?:\*(?:internal|usbfront|usbrear|).*? (\d+):(\d{1,2}):(\d{1,2}))?\r\n'), self.__MatchRemainingRecordingTime, None)
            self.AddMatchString(re.compile(b'Strc0(?P<value>[0-3])\r\n'), self.__MatchStreamControl, None)
            self.AddMatchString(re.compile(b'BitrV([12])\*(\d{4,5})\r\n'), self.__MatchVideoBitrate, None)
            self.AddMatchString(re.compile(b'RtmpU1\*(|[ \S]+?)\r\n'), self.__MatchRTMPPrimaryDestinationURLStatus, None)
            self.AddMatchString(re.compile(b'RtmpE1\*([01])\r\n'), self.__MatchRTMPStream, None)
            self.AddMatchString(re.compile(b'Ipi ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\r\nStrcN1\*(|[ \S]+?)\r\n'), self.__MatchRTSPStreamURL, None)
            self.AddMatchString(re.compile(b'Pnam3\*0(00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16),(.*)'), self.__MatchStreamingPresetName, None)
            self.AddMatchString(re.compile(b'Inf(5[678])\*(N/A|usbfront|usbrear|usbrcp)'), self.__MatchUSBStatus, 'Query')
            self.AddMatchString(re.compile(b'RcdrN([01])\*(usbfront|usbrear|usbrcp)\r\n'), self.__MatchUSBStatus, 'Verbose')
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.findAlarmCondition = re.compile(b'<name:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server|firmware_failure|file_upload),level:(warning|critical|info|emergency)>')
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
    
    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False
    
    def UpdateAlarm(self, value, qualifier):
        AlarmCmdString = '39i'
        self.__UpdateHelper('Alarm', AlarmCmdString, value, qualifier)

    def __MatchAlarm(self, match, tag):

        AlarmStates = {
            'video_loss': 'Video Loss',
            'audio_loss': 'Audio Loss',
            'disk_space': 'Disk Space',
            'record_halt': 'Record Halt',
            'ntp.sync': 'NTP Sync',
            'auth_failures': 'Authentication Failures',
            'disk_error': 'Disk Error',
            'temperature.internal': 'Temperature Internal',
            'hdcp_video': 'HDCP Video',
            'cpu_usage': 'CPU Usage',
            'usb.front.overcurrent': 'USB Front Overcurrent',
            'usb.rear.overcurrent': 'USB Rear Overcurrent',
            'usb.keyboard.overcurrent': 'USB Keyboard Overcurrent',
            'usb.mouse.overcurrent': 'USB Mouse Overcurrent',
            'sched_server': 'Schedule Server',
            'firmware_failure': 'Firmware Failure',
            'file_upload': 'File Upload'
        }

        if tag == 'No Alarm':
            for alarms in AlarmStates:
                qualifier = {'Alarm': AlarmStates[alarms]}
                self.WriteStatus('Alarm', 'Not Active', qualifier)
                self.WriteStatus('AlarmSeverity', 'Cleared', qualifier)
        else:
            LevelStates = {
                'warning': 'Warning',
                'critical': 'Critical',
                'info': 'Info',
                'emergency': 'Emergency'
            }

            alarmList = re.findall(self.findAlarmCondition, match.group(0))

            alarmResults = {}
            for result in alarmList:
                alarmResults[result[0].decode()] = result[1].decode()

            for alarmValues in AlarmStates:
                qualifier = {'Alarm': AlarmStates[alarmValues]}
                if alarmValues in alarmResults:
                    self.WriteStatus('Alarm', 'Active', qualifier)
                    self.WriteStatus('AlarmSeverity', LevelStates[alarmResults[alarmValues]], qualifier)
                else:
                    self.WriteStatus('Alarm', 'Not Active', qualifier)
                    self.WriteStatus('AlarmSeverity', 'Cleared', qualifier)

    def UpdateAlarmSeverity(self, value, qualifier):

        self.UpdateAlarm(value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': '1',
            'Follow': '2',
            'Fit': '3'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'w{0}ASPR\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'wASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Fill',
            '2': 'Follow',
            '3': 'Fit'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioBitrate(self, value, qualifier):

        ValueStateValues = {
            '80': '80',
            '96': '96',
            '128': '128',
            '192': '192',
            '256': '256',
            '320': '320'
        }

        if value in ValueStateValues:
            AudioBitrateCmdString = 'wA1*{0}BITR\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioBitrate', AudioBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioBitrate')

    def UpdateAudioBitrate(self, value, qualifier):

        AudioBitrateCmdString = 'wA1BITR\r'
        self.__UpdateHelper('AudioBitrate', AudioBitrateCmdString, value, qualifier)

    def __MatchAudioBitrate(self, match, tag):

        ValueStateValues = {
            '080': '80',
            '096': '96',
            '128': '128',
            '192': '192',
            '256': '256',
            '320': '320'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioBitrate', value, None)

    def SetAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Audio Channel A (L)': '40000',
            'Audio Channel A (R)': '40001',
            'Digital Channel A (L)': '40002',
            'Digital Channel A (R)': '40003',
        }

        if -18 <= value <= 24 and qualifier['Type'] in TypeStates:
            AudioInputGainCmdString = 'wG{0}*{1}AU\r'.format(TypeStates[qualifier['Type']], value * 10)
            self.__SetHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputGain')

    def UpdateAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Audio Channel A (L)': '40000',
            'Audio Channel A (R)': '40001',
            'Digital Channel A (L)': '40002',
            'Digital Channel A (R)': '40003',
        }

        if qualifier['Type'] in TypeStates:
            AudioInputGainCmdString = 'wG{0}AU\r'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioInputGain')

    def __MatchAudioInputGain(self, match, tag):

        TypeStates = {
            '40000': 'Audio Channel A (L)',
            '40001': 'Audio Channel A (R)',
            '40002': 'Digital Channel A (L)',
            '40003': 'Digital Channel A (R)',
        }

        value = int(int(match.group(2).decode()) / 10)
        self.WriteStatus('AudioInputGain', value, {'Type': TypeStates[match.group(1).decode()]})

    def UpdateAudioLevel(self, value, qualifier):
        AudioLevelCmdString = '34I'
        self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)

    def __MatchAudioLevel(self, match, tag):

        Left = int(match.group(1).decode()) / 10
        Right = int(match.group(2).decode()) / 10
        self.WriteStatus('AudioLevel', Left, {'L/R': 'Left'})
        self.WriteStatus('AudioLevel', Right, {'L/R': 'Right'})

    def SetInputAudioMute(self, value, qualifier):

        TypeStates = {
            'Audio': 0,
            'Digital': 2
        }

        LRStates = {
            'Left': 0,
            'Right': 1
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Type'] in TypeStates and qualifier['L/R'] in LRStates and value in ValueStateValues:
            Shift = TypeStates[qualifier['Type']] + LRStates[qualifier['L/R']]
            InputAudioMuteCmdString = 'wM4000{0}*{1}AU\r'.format(Shift, ValueStateValues[value])
            self.__SetHelper('InputAudioMute', InputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioMute')

    def UpdateInputAudioMute(self, value, qualifier):

        TypeStates = {
            'Audio': 0,
            'Digital': 2
        }

        LRStates = {
            'Left': 0,
            'Right': 1
        }

        if qualifier['Type'] in TypeStates and qualifier['L/R'] in LRStates:
            Shift = TypeStates[qualifier['Type']] + LRStates[qualifier['L/R']]
            InputAudioMuteCmdString = 'wM4000{0}AU\r'.format(Shift)
            self.__UpdateHelper('InputAudioMute', InputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioMute')

    def __MatchInputAudioMute(self, match, tag):

        Left = [0, 2, 4, 6]
        Digital = [2, 3, 6, 7]

        State = {
            '1': 'On',
            '0': 'Off'
        }

        if int(match.group(1).decode()) in Digital:
            Type = 'Digital'
        else:
            Type = 'Audio'

        if int(match.group(1).decode()) in Left:
            LR = 'Left'
        else:
            LR = 'Right'

        qualifier = {'Type': Type, 'L/R': LR}

        value = State[match.group(2).decode()]
        self.WriteStatus('InputAudioMute', value, qualifier)

    def SetOutputAudioMute(self, value, qualifier):

        LRStates = {
            'Left': '0',
            'Right': '1'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['L/R'] in LRStates and value in ValueStateValues:
            OutputAudioMuteCmdString = 'wM6000{0}*{1}AU\r'.format(LRStates[qualifier['L/R']], ValueStateValues[value])
            self.__SetHelper('OutputAudioMute', OutputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAudioMute')

    def UpdateOutputAudioMute(self, value, qualifier):

        LRStates = {
            'Left': '0',
            'Right': '1'
        }

        if qualifier['L/R'] in LRStates:
            OutputAudioMuteCmdString = 'wM6000{0}AU\r'.format(LRStates[qualifier['L/R']])
            self.__UpdateHelper('OutputAudioMute', OutputAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAudioMute')

    def __MatchOutputAudioMute(self, match, tag):

        LRStates = {
            '0': 'Left',
            '1': 'Right'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'L/R': LRStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputAudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute': 'A',
            'Execute and Fill': '1*A',
            'Execute and Follow': '2*A'
        }

        if value in ValueStateValues:
            CmdString = '{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoImage', CmdString, value, qualifier)  # Query delay not needed, tested with device
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBitrateControl(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        ValueStateValues = {
            'VBR': '0',
            'CVBR': '1',
            'CBR': '2'
        }

        if qualifier['Stream'] in InputState and value in ValueStateValues:
            BitrateControlCmdString = 'w{0}*{1}BRCT\r'.format(InputState[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('BitrateControl', BitrateControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBitrateControl')

    def UpdateBitrateControl(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState:
            BitrateControlCmdString = 'w{0}BRCT\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('BitrateControl', BitrateControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBitrateControl')

    def __MatchBitrateControl(self, match, tag):

        InputState = {
            '1': 'Record',
            '2': 'Stream',
        }

        ValueStateValues = {
            '0': 'VBR',
            '1': 'CVBR',
            '2': 'CBR'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BitrateControl', value, {'Stream': InputState[match.group(1).decode()]})

    def SetChapterMarker(self, value, qualifier):

        CmdString = 'wBRCDR\r'
        self.__SetHelper('ChapterMarker', CmdString, value, qualifier)

    def SetClearActiveAlarms(self, value, qualifier):

        ClearActiveAlarmsCmdString = '\x1BCALRM\r'
        self.__SetHelper('ClearActiveAlarms', ClearActiveAlarmsCmdString, value, qualifier)

    def UpdateCPUUsage(self, value, qualifier):

        CPUUsageCmdString = '11I'
        self.__UpdateHelper('CPUUsage', CPUUsageCmdString, value, qualifier)

    def __MatchCPUUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CPUUsage', value, None)

    def UpdateCurrentRecordingDuration(self, value, qualifier):

        CmdString = '35I'
        self.__UpdateHelper('CurrentRecordingDuration', CmdString, value, qualifier)

    def __MatchCurrentRecordingDuration(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        self.WriteStatus('CurrentRecordingDuration', value, None)

    def SetEDID(self, value, qualifier):

        ValueStateValues = {
            '800x600 60HZ PC DVI': '1',
            '1024x768 60HZ PC DVI': '2',
            '1280x720 60HZ PC DVI': '3',
            '1280x768 60HZ PC DVI': '4',
            '1280x800 60HZ PC DVI': '5',
            '1280x1024 60HZ PC DVI': '6',
            '1360x768 60HZ PC DVI': '7',
            '1366x768 60HZ PC DVI': '8',
            '1400x1050 60HZ PC DVI': '9',
            '1440x900 60HZ PC DVI': '10',
            '1600x900 60HZ PC DVI': '11',
            '1600x1200 60HZ PC DVI': '12',
            '1680x1050 60HZ PC DVI': '13',
            '1920x1080 60HZ PC DVI': '14',
            '1920x1200 60HZ PC DVI': '15',
            '800x600 60HZ PC HDMI': '16',
            '1024x768 60HZ PC HDMI': '17',
            '1280x768 60HZ PC HDMI': '18',
            '1280x800 60HZ PC HDMI': '19',
            '1280x1024 60HZ PC HDMI': '20',
            '1360x768 60HZ PC HDMI': '21',
            '1366x768 60HZ PC HDMI': '22',
            '1400x1050 60HZ PC HDMI': '23',
            '1440x900 60HZ PC HDMI': '24',
            '1600x900 60HZ PC HDMI': '25',
            '1600x1200 60HZ PC HDMI': '26',
            '1680x1050 60HZ PC HDMI': '27',
            '1920x1200 60HZ PC HDMI': '28',
            '480p 60HZ HDTV HDMI': '29',
            '576p 50HZ HDTV HDMI': '30',
            '720p 50HZ HDTV HDMI': '31',
            '720p 60HZ HDTV HDMI': '32',
            '1080i 50HZ HDTV HDMI': '33',
            '1080i 60HZ HDTV HDMI': '34',
            '1080p 50/25HZ HDTV HDMI': '35',
            '1080p 50HZ HDTV HDMI': '36',
            '1080p 60/24HZ HDTV HDMI': '37',
            '1080p 60HZ HDTV HDMI': '38',
            'User Loaded Slot 1': '39',
            'User Loaded Slot 2': '40',
            'User Loaded Slot 3': '41',
        }

        if value in ValueStateValues:
            EDIDCmdString = 'wA{0}EDID\r'.format(ValueStateValues[value])
            self.__SetHelper('EDID', EDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEDID')

    def UpdateEDID(self, value, qualifier):

        EDIDCmdString = 'wAEDID\r'
        self.__UpdateHelper('EDID', EDIDCmdString, value, qualifier)

    def __MatchEDID(self, match, tag):

        ValueStateValues = {
            '01': '800x600 60HZ PC DVI',
            '02': '1024x768 60HZ PC DVI',
            '03': '1280x720 60HZ PC DVI',
            '04': '1280x768 60HZ PC DVI',
            '05': '1280x800 60HZ PC DVI',
            '06': '1280x1024 60HZ PC DVI',
            '07': '1360x768 60HZ PC DVI',
            '08': '1366x768 60HZ PC DVI',
            '09': '1400x1050 60HZ PC DVI',
            '10': '1440x900 60HZ PC DVI',
            '11': '1600x900 60HZ PC DVI',
            '12': '1600x1200 60HZ PC DVI',
            '13': '1680x1050 60HZ PC DVI',
            '14': '1920x1080 60HZ PC DVI',
            '15': '1920x1200 60HZ PC DVI',
            '16': '800x600 60HZ PC HDMI',
            '17': '1024x768 60HZ PC HDMI',
            '18': '1280x768 60HZ PC HDMI',
            '19': '1280x800 60HZ PC HDMI',
            '20': '1280x1024 60HZ PC HDMI',
            '21': '1360x768 60HZ PC HDMI',
            '22': '1366x768 60HZ PC HDMI',
            '23': '1400x1050 60HZ PC HDMI',
            '24': '1440x900 60HZ PC HDMI',
            '25': '1600x900 60HZ PC HDMI',
            '26': '1600x1200 60HZ PC HDMI',
            '27': '1680x1050 60HZ PC HDMI',
            '28': '1920x1200 60HZ PC HDMI',
            '29': '480p 60HZ HDTV HDMI',
            '30': '576p 50HZ HDTV HDMI',
            '31': '720p 50HZ HDTV HDMI',
            '32': '720p 60HZ HDTV HDMI',
            '33': '1080i 50HZ HDTV HDMI',
            '34': '1080i 60HZ HDTV HDMI',
            '35': '1080p 50/25HZ HDTV HDMI',
            '36': '1080p 50HZ HDTV HDMI',
            '37': '1080p 60/24HZ HDTV HDMI',
            '38': '1080p 60HZ HDTV HDMI',
            '39': 'User Loaded Slot 1',
            '40': 'User Loaded Slot 2',
            '41': 'User Loaded Slot 3',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EDID', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1',
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        CmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFileDestination(self, value, qualifier):
        FileDestinationCmdString = 'I'
        self.__UpdateHelper('FileDestination', FileDestinationCmdString, value, qualifier)

    def __MatchFileDestination(self, match, tag):

        ValueStateValues = {
            'N/A': 'NA',
            'internal': 'Internal',
            'usbfront': 'Front USB',
            'usbrear': 'Rear USB',
            'auto': 'Auto',
            '*': 'Drive not inserted while USB is set as Destination',
            '': 'Drive not inserted while USB is set as Destination',
            'usbrcp': 'AAP USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FileDestination', value, {'Drive': 'Primary'})

        if value == 'Auto':
            self.WriteStatus('RemainingFreeDiskSpace', 0, {'Drive': 'Primary'})
            self.WriteStatus('FileDestination', 'NA', {'Drive': 'Secondary'})
            self.WriteStatus('RemainingFreeDiskSpace', 0, {'Drive': 'Secondary'})
        else:
            if value != 'NA' and value != 'Drive not inserted while USB is set as Destination':
                self.WriteStatus('RemainingFreeDiskSpace', floor(int(match.group(3).decode()) / 1000), {'Drive': 'Primary'})
            else:
                self.WriteStatus('RemainingFreeDiskSpace', 0, {'Drive': 'Primary'})
            if match.group(2) is not None:
                value2 = ValueStateValues[match.group(2).decode()]
                self.WriteStatus('FileDestination', value2, {'Drive': 'Secondary'})
                if match.group(4) is not None:
                    self.WriteStatus('RemainingFreeDiskSpace', floor(int(match.group(4).decode().replace('*', '')) / 1000), {'Drive': 'Secondary'})
                elif match.group(5) is not None:
                    self.WriteStatus('RemainingFreeDiskSpace', 0, {'Drive': 'Secondary'})
            else:
                self.WriteStatus('RemainingFreeDiskSpace', 0, {'Drive': 'Secondary'})
                self.WriteStatus('FileDestination', 'NA', {'Drive': 'Secondary'})

    def SetGOPLength(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if 1 <= value <= 30 and qualifier['Stream'] in InputState:
            GOPLengthCmdString = 'w{0}*{1}GOPL\r'.format(InputState[qualifier['Stream']], value)
            self.__SetHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGOPLength')

    def UpdateGOPLength(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState:
            GOPLengthCmdString = 'w{0}GOPL\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGOPLength')

    def __MatchGOPLength(self, match, tag):

        InputState = {
            '1': 'Record',
            '2': 'Stream',
        }

        value = int(match.group(2).decode())
        self.WriteStatus('GOPLength', value, {'Stream': InputState[match.group(1).decode()]})

    def UpdateHDCPStatus(self, value, qualifier):

        HDCPStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPStatus', HDCPStatusCmdString, value, qualifier)

    def __MatchHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Detected',
            '1': 'HDCP Detected',
            '2': 'No HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPStatus', value, None)

    def SetHDMIOutputMute(self, value, qualifier):

        TypeStates = {
            'Video': 'B',
            'Audio': 'Z'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Type'] in TypeStates and value in ValueStateValues:
            HDMIOutputMuteCmdString = '99*{0}{1}'.format(ValueStateValues[value], TypeStates[qualifier['Type']])
            self.__SetHelper('HDMIOutputMute', HDMIOutputMuteCmdString, value, qualifier)  # Query delay not needed, tested with the device.
        else:
            self.Discard('Invalid Command for SetHDMIOutputMute')

    def UpdateHDMIOutputMute(self, value, qualifier):

        TypeStates = {
            'Video': 'B',
            'Audio': 'Z'
        }

        if qualifier['Type'] in TypeStates:
            HDMIOutputMuteCmdString = '99{}'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('HDMIOutputMute', HDMIOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIOutputMute')

    def __MatchHDMIOutputMute(self, match, tag):

        TypeStates = {
            'V': 'Video',
            'A': 'Audio'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Type': TypeStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDMIOutputMute', value, qualifier)

    def SetMetadata(self, value, qualifier):

        TypeStateValues = {
            'Contributor': '0',
            'Coverage': '1',
            'Presenter': '2',
            'Description': '4',
            'Format': '5',
            'Language': '7',
            'Publisher': '8',
            'Relation': '9',
            'Rights': '10',
            'Source': '11',
            'Subject': '12',
            'Title': '13',
            'Type': '14',
            'System Name': '15',
            'Course': '16',
        }

        MetaString = value
        if qualifier['Type'] in TypeStateValues and MetaString:
            MetadataCmdString = 'wM{0}*{1}RCDR\r'.format(TypeStateValues[qualifier['Type']], MetaString)
            self.__SetHelper('Metadata', MetadataCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMetadata')

    def UpdateMetadataStatus(self, value, qualifier):

        TypeStateValues = {
            'Contributor': '0',
            'Coverage': '1',
            'Presenter': '2',
            'Date': '3',  # read only per API
            'Description': '4',
            'Format': '5',
            'Identifier': '6',  # read only per API
            'Language': '7',
            'Publisher': '8',
            'Relation': '9',
            'Rights': '10',
            'Source': '11',
            'Subject': '12',
            'Title': '13',
            'Type': '14',
            'System Name': '15',
            'Course': '16'
        }

        if qualifier['Type'] in TypeStateValues:
            if qualifier['Type'] not in self.ConfiguredMetadataList:
                self.ConfiguredMetadataList.append(qualifier['Type'])

            if qualifier['Type'] == self.ConfiguredMetadataList[0]:
                for type_ in self.ConfiguredMetadataList:
                    if self.ReadStatus('MetadataStatus', {'Type': type_}) is None:
                        self.WriteStatus('MetadataStatus', 'No Information', {'Type': type_})

            MetadataStatusCmdString = 'wM{0}RCDR\r'.format(TypeStateValues[qualifier['Type']])
            self.__UpdateHelper('MetadataStatus', MetadataStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMetadataStatus')

    def __MatchMetadataStatus(self, match, tag):

        TypeStates = {
            '0': 'Contributor',
            '1': 'Coverage',
            '2': 'Presenter',
            '3': 'Date',
            '4': 'Description',
            '5': 'Format',
            '6': 'Identifier',
            '7': 'Language',
            '8': 'Publisher',
            '9': 'Relation',
            '10': 'Rights',
            '11': 'Source',
            '12': 'Subject',
            '13': 'Title',
            '14': 'Type',
            '15': 'System Name',
            '16': 'Course'
        }

        typeValue = match.group('type')
        if match.group('value'):
            value = match.group('value').decode()
        else:
            value = 'No Information'
        if typeValue and value:
            self.WriteStatus('MetadataStatus', value, {'Type': TypeStates[typeValue.decode()]})

    def SetRecallEncoderPreset(self, value, qualifier):

        TypeStates = {
            'Record': '1',
            'Stream': '2',
        }

        if 1 <= int(value) <= 16 and qualifier['Stream'] in TypeStates:
            CmdString = '4*{0}*{1}.'.format(TypeStates[qualifier['Stream']], value)
            self.__SetHelper('RecallEncoderPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallEncoderPreset')

    def SetRecord(self, value, qualifier):

        State = {
            'Start': '1',
            'Stop': '0',
            'Pause': '2'
        }

        CmdString = 'wY{0}RCDR\r'.format(State[value])
        self.__SetHelper('Record', CmdString, value, qualifier)

    def UpdateRecord(self, value, qualifier):

        CmdString = 'wYRCDR\r'
        self.__UpdateHelper('Record', CmdString, value, qualifier)

    def __MatchRecord(self, match, tag):

        State = {
            '1': 'Start',
            '0': 'Stop',
            '2': 'Pause'
        }

        value = State[match.group(1).decode()]
        self.WriteStatus('Record', value, None)

    def UpdateRCPConnectionStatus(self, value, qualifier):

        RCPConnectionStatusCmdString = '50I'
        self.__UpdateHelper('RCPConnectionStatus', RCPConnectionStatusCmdString, value, qualifier)

    def __MatchRCPConnectionStatus(self, match, tag):

        if match.group(1):
            value = match.group(1).decode()
        else:
            value = 'Device Not Present'
        self.WriteStatus('RCPConnectionStatus', value, None)

    def SetRecordControl(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if value in ValueStateValues:
            RecordControlCmdString = 'wX{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordControl', RecordControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateRecordControl(self, value, qualifier):

        RecordControlCmdString = 'wXRCDR\r'
        self.__UpdateHelper('RecordControl', RecordControlCmdString, value, qualifier)

    def __MatchRecordControl(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('RecordControl', value, None)

    def SetRecordDestination(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Internal': '1',
            'Front USB': '2',
            'Rear USB': '3',
            'RCP USB': '4',
            'Internal + Auto': '11',
            'Internal + Front USB': '12',
            'Internal + Rear USB': '13',
            'Internal + RCP USB': '14',
        }

        if value in ValueStateValues:
            RecordDestinationCmdString = 'wD{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordDestination', RecordDestinationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordDestination')

    def UpdateRecordDestination(self, value, qualifier):

        RecordDestinationCmdString = 'wDRCDR\r'
        self.__UpdateHelper('RecordDestination', RecordDestinationCmdString, value, qualifier)

    def __MatchRecordDestination(self, match, tag):

        ValueStateValues = {
            '00': 'Auto',
            '01': 'Internal',
            '02': 'Front USB',
            '03': 'Rear USB',
            '04': 'RCP USB',
            '11': 'Internal + Auto',
            '12': 'Internal + Front USB',
            '13': 'Internal + Rear USB',
            '14': 'Internal + RCP USB',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordDestination', value, None)

    def SetRecordingMode(self, value, qualifier):

        ValueStateValues = {
            'Video Only': '1',
            'Audio Only': '2',
            'Video + Audio Only': '3',
        }

        if value in ValueStateValues:
            RecordingModeCmdString = 'w{0}RMOD\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordingMode', RecordingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordingMode')

    def UpdateRecordingMode(self, value, qualifier):

        RecordingModeCmdString = 'wRMOD\r'
        self.__UpdateHelper('RecordingMode', RecordingModeCmdString, value, qualifier)

    def __MatchRecordingMode(self, match, tag):

        ValueStateValues = {
            '1': 'Video Only',
            '2': 'Audio Only',
            '3': 'Video + Audio Only',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordingMode', value, None)

    def SetRecordingProfiles(self, value, qualifier):

        if 1 <= int(value) <= 16:
            RecordingProfilesCmdString = '\x1BR5*{0}PRST\r'.format(value)
            self.__SetHelper('RecordingProfiles', RecordingProfilesCmdString, value, qualifier)
        else:
            self.Disacrd('Invalid Command')

    def UpdateRecordingProfiles(self, value, qualifier):

        RecordingProfilesCmdString = '\x1BL5PRST\r'
        self.__UpdateHelper('RecordingProfiles', RecordingProfilesCmdString, value, qualifier)

    def __MatchRecordingProfiles(self, match, tag):

        ValueStateValues = {
            '00': 'No Profile',
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8',
            '09': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordingProfiles', value, None)

    def __MatchRecordingStartCountdown(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('RecordingStartCountdown', value, None)

    def UpdateRemainingFreeDiskSpace(self, value, qualifier):

        self.UpdateFileDestination(value, qualifier)

    def UpdateRemainingRecordingTime(self, value, qualifier):

        CmdString = '36I'
        self.__UpdateHelper('RemainingRecordingTime', CmdString, value, qualifier)

    def __MatchRemainingRecordingTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        self.WriteStatus('RemainingRecordingTime', value, {'Drive': 'Primary'})
        if match.group(4) is not None:
            value2 = match.group(4).decode() + ':' + match.group(5).decode() + ':' + match.group(6).decode()
            self.WriteStatus('RemainingRecordingTime', value2, {'Drive': 'Secondary'})
        else:
            self.WriteStatus('RemainingRecordingTime', '00:00:00', {'Drive': 'Secondary'})

    def SetRTMPPrimaryDestination(self, value, qualifier):

        RTMPString = value
        if RTMPString:
            RTMPCmdString = 'wU1*{0}RTMP\r'.format(RTMPString)
            self.__SetHelper('RTMPPrimaryDestination', RTMPCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRTMPPrimaryDestination')

    def UpdateRTMPPrimaryDestinationURLStatus(self, value, qualifier):

        RTMPPrimaryDestinationURLStatusCmdString = 'wU1RTMP\r'
        self.__UpdateHelper('RTMPPrimaryDestinationURLStatus', RTMPPrimaryDestinationURLStatusCmdString, value, qualifier)

    def __MatchRTMPPrimaryDestinationURLStatus(self, match, tag):

        value = match.group(1).decode()
        if value == '':
            value = 'None'
        self.WriteStatus('RTMPPrimaryDestinationURLStatus', value, None)

    def SetRTMPStream(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if value in ValueStateValues:
            RTMPStreamCmdString = 'wE1*{0}RTMP\r'.format(ValueStateValues[value])
            self.__SetHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRTMPStream')

    def UpdateRTMPStream(self, value, qualifier):

        RTMPStreamCmdString = 'wE1RTMP\r'
        self.__UpdateHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)

    def __MatchRTMPStream(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RTMPStream', value, None)

    def UpdateRTSPStreamURL(self, value, qualifier):

        RTSPStreamURLCmdString = 'wCi\rwN1STRC\r'
        res = self.__UpdateHelper('RTSPStreamURL', RTSPStreamURLCmdString, value, qualifier)

    def __MatchRTSPStreamURL(self, match, tag):

        ipAddress = match.group(1).decode()
        name = match.group(2).decode()
        if name == '':
            value = 'None'
        else:
            value = 'rtsp://' + ipAddress + '/' + name
        self.WriteStatus('RTSPStreamURL', value, None)

    def SetEjectUSBStorage(self, value, qualifier):

        ValueStateValues = {
            'All': '0',
            'USB Front': '2',
            'USB Rear': '3',
            'USB RCP': '4'
        }

        EjectUSBStorageCmdString = 'w{}USBE\r'.format(ValueStateValues[value])
        self.__SetHelper('EjectUSBStorage', EjectUSBStorageCmdString, value, qualifier)

    def SetStreamControl(self, value, qualifier):

        ValueStateValues = {
            'RTMP': '1',
            'Disable': '0',
            'RTSP': '2',
            'Push RTP': '3'
        }

        if value in ValueStateValues:
            StreamControlCmdString = 'w1*{0}STRC\r'.format(ValueStateValues[value])
            self.__SetHelper('StreamControl', StreamControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamControl')

    def UpdateStreamControl(self, value, qualifier):

        StreamControlCmdString = 'w1STRC\r'
        self.__UpdateHelper('StreamControl', StreamControlCmdString, value, qualifier)

    def __MatchStreamControl(self, match, tag):

        ValueStateValues = {
            '1': 'RTMP',
            '0': 'Disable',
            '2': 'RTSP',
            '3': 'Push RTP',
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('StreamControl', value, None)

    def UpdateStreamingPresetName(self, value, qualifier):

        if 1 <= int(qualifier['Preset']) <= 16:
            StreamingPresetNameCmdString = '\x1B3*{0}PNAM\r'.format(qualifier['Preset'])
            self.__UpdateHelper('StreamingPresetName', StreamingPresetNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStreamingPresetName')

    def __MatchStreamingPresetName(self, match, tag):

        PresetStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8',
            '09': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        qualifier = {'Preset': PresetStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('StreamingPresetName', value, qualifier)

    def SetStreamingPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            StreamingPresetRecallCmdString = '3*1*{0}.'.format(value)
            self.__SetHelper('StreamingPresetRecall', StreamingPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingPresetRecall')

    def SetStreamingPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            StreamingPresetsCmdString = '3*1*{0},'.format(value)
            self.__SetHelper('StreamingPresetSave', StreamingPresetsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingPresetSave')

    def UpdateUSBStatus(self, value, qualifier):

        USBPortStates = {
            'Front USB': '56I',
            'Rear USB': '57I',
            'Rear RCP': '58I'
        }

        if qualifier['USB Port'] in USBPortStates:
            USBStatusCmdString = USBPortStates[qualifier['USB Port']]
            self.__UpdateHelper('USBStatus', USBStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUSBStatus')

    def __MatchUSBStatus(self, match, tag):

        if tag == 'Query':
            USBPortStates = {
                '56': 'Front USB',
                '57': 'Rear USB',
                '58': 'Rear RCP'
            }

            if match.group(2).decode() == 'N/A':
                value = 'Removed'
            else:
                value = 'Inserted'
            port = USBPortStates[match.group(1).decode()]
        else:
            ValueStateValues = {
                '1': 'Inserted',
                '0': 'Removed'
            }

            USBPortStates = {
                'usbfront': 'Front USB',
                'usbrear': 'Rear USB',
                'usbrcp': 'Rear RCP'
            }

            value = ValueStateValues[match.group(1).decode()]
            port = USBPortStates[match.group(2).decode()]

        qualifier = {'USB Port': port}
        self.WriteStatus('USBStatus', value, qualifier)

    def SetVideoBitrate(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if 2000 <= value <= 10000 and qualifier['Stream'] in InputState:
            VideoBitrateCmdString = 'wV{0}*{1}BITR\r'.format(InputState[qualifier['Stream']], value)
            self.__SetHelper('VideoBitrate', VideoBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoBitrate')

    def UpdateVideoBitrate(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState:
            VideoBitrateCmdString = 'wV{0}BITR\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('VideoBitrate', VideoBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoBitrate')

    def __MatchVideoBitrate(self, match, tag):

        InputState = {
            '1': 'Record',
            '2': 'Stream',
        }

        value = int(match.group(2).decode())
        self.WriteStatus('VideoBitrate', value, {'Stream': InputState[match.group(1).decode()]})

    def SetVideoFrameRate(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        State = {
            '30 fps': '1',
            '25 fps': '2',
            '24 fps': '3',
            '15 fps': '4',
            '12.5 fps': '5',
            '12 fps': '6',
            '10 fps': '7',
            '5 fps': '8',
        }

        if qualifier['Stream'] in InputState and value in State:
            CmdString = 'w{0}*{1}VFRM\r'.format(InputState[qualifier['Stream']], State[value])
            self.__SetHelper('VideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoFrameRate')

    def UpdateVideoFrameRate(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState:
            CmdString = 'w{0}VFRM\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('VideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoFrameRate')

    def __MatchVideoFrameRate(self, match, tag):

        State = {
            '1': '30 fps',
            '2': '25 fps',
            '3': '24 fps',
            '4': '15 fps',
            '5': '12.5 fps',
            '6': '12 fps',
            '7': '10 fps',
            '8': '5 fps',
        }

        InputState = {
            '1': 'Record',
            '2': 'Stream',
        }

        value = State[match.group(2).decode()]
        self.WriteStatus('VideoFrameRate', value, {'Stream': InputState[match.group(1).decode()]})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'Off': '0B',
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVideoResolution(self, value, qualifier):

        ValueStateValues = {
            '512x288': '0',
            '848x480': '1',
            '1024x768': '4',
            '1280x720': '2',
            '1280x1024': '5',
            '1920x1080': '3'
        }

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState and value in ValueStateValues:
            VideoResolutionCmdString = 'w{0}*{1}VRES\r'.format(InputState[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('VideoResolution', VideoResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoResolution')

    def UpdateVideoResolution(self, value, qualifier):

        InputState = {
            'Record': '1',
            'Stream': '2',
        }

        if qualifier['Stream'] in InputState:
            VideoResolutionCmdString = 'w{0}VRES\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('VideoResolution', VideoResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoResolution')

    def __MatchVideoResolution(self, match, tag):

        ValueStateValues = {
            '0': '512x288',
            '1': '848x480',
            '4': '1024x768',
            '2': '1280x720',
            '5': '1280x1024',
            '3': '1920x1080'
        }

        InputState = {
            '1': 'Record',
            '2': 'Stream',
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoResolution', value, {'Stream': InputState[match.group(1).decode()]})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.EchoDisabled and 'Serial' not in self.ConnectionType:
                self.Send('w0echo\r\n')
                
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '10': 'Unrecognized command',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum connections exceeded',
            '28': 'Bad filename or file not found'
        }

        if qualifier:
            value = match[1:-2]
        else:
            value = match.group(1).decode()

        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.ConfiguredMetadataList = []  # keeps track of configured Metadata Status

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


class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None, None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
