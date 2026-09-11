from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
        self.Models = {
            'SMP 351': self.SMP351_Base,
            'SMP 351 3G-SDI': self.SMP351_3GSDI,
            'SMP 352': self.SMP351_Base,
            'SMP 352 3G-SDI': self.SMP351_3GSDI,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveLayoutPreset': { 'Status': {}},
            'ActiveLayoutPresetConfidenceDual': { 'Status': {}},
            'Alarm': {'Parameters':['Alarm'], 'Status': {}},
            'AlarmSeverity': {'Parameters':['Alarm'], 'Status': {}},
            'AspectRatio': {'Parameters':['Input'], 'Status': {}},
            'AudioBitrate': { 'Status': {}},
            'AudioInputGain': {'Parameters':['Type'], 'Status': {}},
            'AudioLevel': {'Parameters':['L/R'], 'Status': {}},
            'AudioMuteInput': {'Parameters':['Type','Channel','L/R'], 'Status': {}},
            'AudioMuteOutput': {'Parameters':['L/R'], 'Status': {}},
            'AudioOnlyRecording': { 'Status': {}},
            'AutoImage': {'Parameters':['Channel'], 'Status': {}},
            'BackgroundImageCommand': {'Parameters': ['Image Name'], 'Status': {}},
            'BackupRTMPStatus': {'Parameters':['Stream'], 'Status': {}},
            'BitrateControl': {'Parameters':['Stream'], 'Status': {}},
            'ChapterMarker': { 'Status': {}},
            'ClearActiveAlarms': { 'Status': {}},
            'CPUUsage': { 'Status': {}},
            'CurrentRecordingDuration': { 'Status': {}},
            'DelayedRecordingDuration': { 'Status': {}},
            'DualChannelHDMIOutput': { 'Status': {}},
            'EjectUSBStorage': { 'Status': {}},
            'Encoder': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FileDestination': {'Parameters':['Drive'], 'Status': {}},
            'FTPUploadDestination': { 'Status': {}},
            'GOPLength': {'Parameters':['Stream'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDMIAudioMute': { 'Status': {}},
            'HDMIVideoMute': { 'Status': {}},
            'HorizontalVideoMirroring': {'Parameters': ['Input'], 'Status': {}},
            'Input3Format': { 'Status': {}},
            'InputA': { 'Status': {}},
            'InputB': { 'Status': {}},
            'InputStatus': { 'Status': {}},
            'LayoutPresetStatus': { 'Status': {}},
            'Metadata': {'Parameters': ['Metadata String'], 'Status': {}},
            'MetadataStatus': {'Parameters': ['Type'], 'Status': {}},
            'PrimaryRTMPStatus': {'Parameters': ['Stream'], 'Status': {}},
            'RCP101ExecutiveMode': { 'Status': {}},
            'RecallEncoderPreset': {'Parameters': ['Stream'], 'Status': {}},
            'RecallLayoutConfidenceDual': { 'Status': {}},
            'RecallLayoutPreset': {'Parameters': ['Inputs'], 'Status': {}},
            'RecallRecordingProfile': { 'Status': {}},
            'RecallStreamingPreset': {'Parameters': ['Stream'], 'Status': {}},
            'RecallUserPreset': {'Parameters': ['Channel'], 'Status': {}},
            'Record': { 'Status': {}},
            'RecordControl': { 'Status': {}},
            'RecordDestination': { 'Status': {}},
            'RecordDualControl': { 'Status': {}},
            'RecordExtend': { 'Status': {}},
            'RecordingMode': { 'Status': {}},
            'RecordingStartCountdown': { 'Status': {}},
            'RecordingVideoFrameRate': {'Parameters': ['Stream'], 'Status': {}},
            'RecordResolution': {'Parameters': ['Stream'], 'Status': {}},
            'RemainingFreeDiskSpace': {'Parameters': ['Drive','Unit'], 'Status': {}},
            'RemainingFrontUSBStorage': {'Parameters': ['Unit'], 'Status': {}},
            'RemainingInternalStorage': {'Parameters': ['Unit'], 'Status': {}},
            'RemainingRearRCPUSBStorage': {'Parameters': ['Unit'], 'Status': {}},
            'RemainingRearUSBStorage': {'Parameters': ['Unit'], 'Status': {}},
            'RemainingRecordingTime': {'Parameters': ['Drive'], 'Status': {}},
            'RTMPBackupURLCommand': {'Parameters': ['Stream', 'RTMP Backup URL String', 'RTMP Backup URL Key String'], 'Status': {}},
            'RTMPBackupURLStatus': {'Parameters': ['Stream'], 'Status': {}},
            'RTMPPrimaryURLCommand': {'Parameters': ['Stream', 'RTMP Backup URL String', 'RTMP Backup URL Key String'], 'Status': {}},
            'RTMPPrimaryURLStatus': {'Parameters': ['Stream'], 'Status': {}},
            'RTMPStream': {'Parameters': ['Stream'], 'Status': {}},
            'RTSPStreamURL': {'Parameters': ['Stream'], 'Status': {}},
            'SMPRecordingFolderShare': { 'Status': {}},
            'StreamControl': {'Parameters': ['Stream'], 'Status': {}},
            'StreamingPresetsName': {'Parameters':['Preset'], 'Status': {}},
            'SwapWindows': { 'Status': {}},
            'ThumbnailSize': { 'Status': {}},
            'USBStatus': {'Parameters': ['USB Port'], 'Status': {}},
            'VideoBitrate': {'Parameters':['Stream'], 'Status': {}},
            'VideoMute': {'Parameters':['Channel'], 'Status': {}},
            'VirtualInputRecording': {'Parameters':['Input'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[78]Rpr(\d{1,2})\r\n'), self.__MatchActiveLayoutPreset, None)
            self.AddMatchString(re.compile(b'9Rpr3\*([01][0-9])\r\n'), self.__MatchActiveLayoutPresetConfidenceDual, None)
            self.AddMatchString(re.compile(b'Inf39\*(?:<name:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server|firmware_failure|publish_failure),level:(warning|critical|info|emergency)>[,\*]?)+\r\n'), self.__MatchAlarm, None)
            self.AddMatchString(re.compile(b'Inf39\*(None active)\r\n'), self.__MatchAlarm, "No Alarm")
            self.AddMatchString(re.compile(b'Aspr0([1-5])\*0([1-3])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'BitrA1\*(080|096|128|192|256|320)\r\n'), self.__MatchAudioBitrate, None)
            self.AddMatchString(re.compile(b'DsG(4000[0-7])\*(-?\d{1,3})\r\n'), self.__MatchAudioInputGain, None)
            self.AddMatchString(re.compile(b'Inf34\*(-?\d{1,4})\*(-?\d{1,4})\r\n'), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b'DsM4000([0-7])\*([01])\r\n'), self.__MatchAudioMuteInput, None)
            self.AddMatchString(re.compile(b'DsM6000([01])\*([01])\r\n'), self.__MatchAudioMuteOutput, None)
            self.AddMatchString(re.compile(b'RcdrA1\*([01])\r\n'), self.__MatchAudioOnlyRecording, None)
            self.AddMatchString(re.compile(b'RtmpS2\*([1-3])\*([01])\r\n'), self.__MatchBackupRTMPStatus, None)
            self.AddMatchString(re.compile(b'Brct([1-3])\*([0-2])\r\n'), self.__MatchBitrateControl, None)
            self.AddMatchString(re.compile(b'Inf11\*(\d{1,3})\r\n'), self.__MatchCPUUsage, None)
            self.AddMatchString(re.compile(b'Inf35\*(\d{1,2}):(\d{1,2}):(\d{1,2})\r\n'), self.__MatchCurrentRecordingDuration, None)
            self.AddMatchString(re.compile(b'RcdrP([0-9]+)\r\n'), self.__MatchDelayedRecordingDuration, None)
            self.AddMatchString(re.compile(b'Omod([0-2])\r\n'), self.__MatchDualChannelHDMIOutput, None)
            self.AddMatchString(re.compile(b'Encm1\*([01])\r\n'), self.__MatchEncoder, None)
            self.AddMatchString(re.compile(b'Exe([0-3])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Inf\*<.*?>\*<.*?>\*<(internal|usbfront|usbrear|auto|N/A|).*?(?:\*?(internal|usbfront|usbrear|usbrcp|N/A|\*))?.*?>\*(?:<([0-9]*)(\*[0-9]*)?(\*N/A)?>\*<.*?>\*<.*?>|<\d*:\d*:\d*>\*<\d*:\d*:\d*>)?\r\n'), self.__MatchFileDestination, None) # Also handles Remaining Free Disk Space status
            self.AddMatchString(re.compile(b'Inf38\*(None|.*ftp|.*?,cifs)\r\n'), self.__MatchFTPUploadDestination, None)
            self.AddMatchString(re.compile(b'Gopl([1-3])\*(\d{1,3})\r\n'), self.__MatchGOPLength, None)
            self.AddMatchString(re.compile(b'HdcpI(01|02|04)\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'RcdrM(?P<type>1?[0-9])\*?(?P<value>.*)?\r\n'), self.__MatchMetadataStatus, None)
            self.AddMatchString(re.compile(b'Amt99\*([01])\r\n'), self.__MatchHDMIAudioMute, None)
            self.AddMatchString(re.compile(b'Vmt99\*([01])\r\n'), self.__MatchHDMIVideoMute, None)
            self.AddMatchString(re.compile(b'RotaI0([1-5])\*([04])\r\n'), self.__MatchHorizontalVideoMirroring, None)
            self.AddMatchString(re.compile(b'Typ03\*(0[1-3])\r\n'), self.__MatchInput3Format, None)
            self.AddMatchString(re.compile(b'Inf32\*ChA([12])\*ChB([3-5])\r\n'), self.__MatchInputStatus, 'Update')
            self.AddMatchString(re.compile(b'In0([1-5])\*0([12])\r\n'), self.__MatchInputStatus, 'Set')
            self.AddMatchString(re.compile(b'Inf49[\S ]+,(\d+)\*[\S ]+\r\n'), self.__MatchLayoutPresetStatus, None)
            self.AddMatchString(re.compile(b'RtmpS1\*([1-3])\*([01])\r\n'), self.__MatchPrimaryRTMPStatus, None)
            self.AddMatchString(re.compile(b'Exe99\*([01])\r\n'), self.__MatchRCP101ExecutiveMode, None)
            self.AddMatchString(re.compile(b'PrstL5\*([0-9]{2})\r\n'), self.__MatchRecallRecordingProfile, None)
            self.AddMatchString(re.compile(b'RcdrY([0-2])\r\n'), self.__MatchRecord, None)
            self.AddMatchString(re.compile(b'RcdrX1\*(?P<value>[0-2])\r\n'), self.__MatchRecordControl, None)
            self.AddMatchString(re.compile(b'RcdrD(00|01|02|03|11|12|13|14)\r\n'), self.__MatchRecordDestination, None)
            self.AddMatchString(re.compile(b'RcdrX2\*([01])\r\n'), self.__MatchRecordDualControl, None)
            self.AddMatchString(re.compile(b'Smod1\*([12])\r\n'), self.__MatchRecordingMode, None)
            self.AddMatchString(re.compile(b'RecStart([0-9]{2})\r\n'), self.__MatchRecordingStartCountdown, None)
            self.AddMatchString(re.compile(b'Vfrm([1-3])\*([1-8])\r\n'), self.__MatchRecordingVideoFrameRate, None)
            self.AddMatchString(re.compile(b'Vres([1-3])\*([0-6]|99)\r\n'), self.__MatchRecordResolution, None)
            self.AddMatchString(re.compile(b'Inf56\*(N/A|usbfront/[ \S]+\*[ \S]+\*[ \S]+\*(\d+)MB.*)\r\n'), self.__MatchRemainingFrontUSBStorage, None)
            self.AddMatchString(re.compile(b'Inf55\*Internal\*[ \S]+\*[ \S]+\*(\d+)MB.*\r\n'), self.__MatchRemainingInternalStorage, None)
            self.AddMatchString(re.compile(b'Inf58\*(N/A|usbrcp/[ \S]+\*[ \S]+\*[ \S]+\*(\d+)MB.*)\r\n'), self.__MatchRemainingRearRCPUSBStorage, None)
            self.AddMatchString(re.compile(b'Inf57\*(N/A|usbrear/[ \S]+\*[ \S]+\*[ \S]+\*(\d+)MB.*)\r\n'), self.__MatchRemainingRearUSBStorage, None)
            self.AddMatchString(re.compile(b'Inf36\*(?:internal|usbfront|usbrear|auto|usbrcp)?.*? (\d+):(\d{1,2}):(\d{1,2})(?:\*(?:internal|usbfront|usbrear|auto|usbrcp|N/A|).*? (\d+):(\d{1,2}):(\d{1,2}))?\r\n'), self.__MatchRemainingRecordingTime, None) #API Does not specify that N\A is returned or '' is returned, but added based on testing with the device.
            self.AddMatchString(re.compile(b'RtmpU2\*(0[1-3])\*(|[ \S]+?)\r\n'), self.__MatchRTMPBackupURLStatus, None)
            self.AddMatchString(re.compile(b'RtmpU1\*(0[1-3])\*(|[ \S]+?)\r\n'), self.__MatchRTMPPrimaryURLStatus, None)
            self.AddMatchString(re.compile(b'RtmpE(?P<type>1|2|3|01|02|03)\*(?P<value>0|1|00|01)\r\n'), self.__MatchRTMPStream, None)
            self.AddMatchString(re.compile(b'Ipi ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\r\nStrcN([1-3])\*(|[ \S]+?)\r\n'), self.__MatchRTSPStreamURL, None)
            self.AddMatchString(re.compile(b'Strc(?P<type>[1-3])\*(?P<value>[01])\r\n'), self.__MatchStreamControl, None)
            self.AddMatchString(re.compile(b'Pnam3\*([0-3][0-9]),(.+)\r\n'), self.__MatchStreamingPresetsName, None)
            self.AddMatchString(re.compile(b'ShrfE1\*([01])\r\n'), self.__MatchSMPRecordingFolderShare, None)
            self.AddMatchString(re.compile(b'RcdrT0([01])\r\n'), self.__MatchThumbnailSize, None)
            self.AddMatchString(re.compile(b'RcdrN([01])\*(usbfront|usbrear|usbrcp)\r\n'), self.__MatchUSBStatus, None)
            self.AddMatchString(re.compile(b'BitrV([1-3])\*(\d{3,5})\r\n'), self.__MatchVideoBitrate, None)
            self.AddMatchString(re.compile(b'Vmt0([12])\*(0[01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'RcdrX([45])\*([01])\r\n'), self.__MatchVirtualInputRecording, None)

            self.findAlarmCondition = re.compile(b'<name:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server|firmware_failure|publish_failure),level:(warning|critical|info|emergency)>')

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchActiveLayoutPreset(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 32:
            self.WriteStatus('ActiveLayoutPreset', str(value), None)

    def __MatchActiveLayoutPresetConfidenceDual(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 10:
            self.WriteStatus('ActiveLayoutPresetConfidenceDual', str(value), None)

    def UpdateAlarm(self, value, qualifier):
            
        AlarmCmdString = '39i'
        self.__UpdateHelper('Alarm', AlarmCmdString, value, qualifier)

    def __MatchAlarm(self, match, tag):

        AlarmStates = {
            'audio_loss'                : 'Audio Loss',
            'auth_failures'             : 'Authentication Failures',
            'cpu_usage'                 : 'CPU Usage',
            'disk_error'                : 'Disk Error',
            'disk_space'                : 'Disk Space',
            'firmware_failure'          : 'Firmware Failure',
            'hdcp_video'                : 'HDCP Video',
            'ntp.sync'                  : 'NTP Sync',
            'publish_failure'           : 'Publish Failure',
            'record_halt'               : 'Record Halt',
            'sched_server'              : 'Schedule Server',
            'temperature.internal'      : 'Temperature Internal',
            'usb.front.overcurrent'     : 'USB Front Overcurrent',
            'usb.keyboard.overcurrent'  : 'USB Keyboard Overcurrent',
            'usb.mouse.overcurrent'     : 'USB Mouse Overcurrent',
            'usb.rear.overcurrent'      : 'USB Rear Overcurrent',
            'video_loss'                : 'Video Loss'
        }

        if tag == 'No Alarm':
            for alarms in AlarmStates:
                qualifier = {'Alarm' : AlarmStates[alarms]}
                self.WriteStatus('Alarm', 'Not Active', qualifier)
                self.WriteStatus('AlarmSeverity', 'Cleared', qualifier)
        else:
            LevelStates = {
                'warning'   : 'Warning',
                'critical'  : 'Critical',
                'info'      : 'Info',
                'emergency' : 'Emergency'
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

        self.UpdateAlarm( value, qualifier)
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill'   : '1',
            'Follow' : '2', 
            'Fit'    : '3'
        }

        if value in ValueStateValues and qualifier['Input'] in self.InputStateQualifier:
            AspectRatioCmdString = 'w{0}*{1}ASPR\r'.format(self.InputStateQualifier[qualifier['Input']],ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        aspectInput = qualifier['Input']
        if aspectInput in self.InputStateQualifier:
            AspectRatioCmdString = 'w{0}ASPR\r'.format(self.InputStateQualifier[qualifier['Input']])
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1' : 'Fill', 
            '2' : 'Follow', 
            '3' : 'Fit'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Input' : match.group(1).decode()})

    def SetAudioBitrate(self, value, qualifier):

        ValueStateValues = {
            '80' : '80', 
            '96' : '96', 
            '128' : '128', 
            '192' : '192', 
            '256' : '256', 
            '320' : '320'
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
            '080' : '80', 
            '096' : '96', 
            '128' : '128', 
            '192' : '192', 
            '256' : '256', 
            '320' : '320'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioBitrate', value, None)

    def SetAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Analog Channel A (L)'   : '40000', 
            'Analog Channel A (R)'   : '40001', 
            'Digital Channel A (L)'  : '40002',
            'Digital Channel A (R)'  : '40003',
            'Analog Channel B (L)'   : '40004', 
            'Analog Channel B (R)'   : '40005', 
            'Digital Channel B (L)'  : '40006',
            'Digital Channel B (R)'  : '40007'
        }

        if -18 <= value <= 24 and qualifier['Type'] in TypeStates:
            AudioInputGainCmdString = 'wG{0}*{1}AU\r'.format(TypeStates[qualifier['Type']], value*10)
            self.__SetHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputGain')

    def UpdateAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Analog Channel A (L)'   : '40000', 
            'Analog Channel A (R)'   : '40001', 
            'Digital Channel A (L)'  : '40002',
            'Digital Channel A (R)'  : '40003',
            'Analog Channel B (L)'   : '40004', 
            'Analog Channel B (R)'   : '40005', 
            'Digital Channel B (L)'  : '40006',
            'Digital Channel B (R)'  : '40007'
        }

        if qualifier['Type'] in TypeStates:
            AudioInputGainCmdString = 'wG{0}AU\r'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioInputGain')

    def __MatchAudioInputGain(self, match, tag):

        TypeStates = {
            '40000' :'Analog Channel A (L)', 
            '40001' :'Analog Channel A (R)', 
            '40002' :'Digital Channel A (L)', 
            '40003' :'Digital Channel A (R)', 
            '40004' :'Analog Channel B (L)', 
            '40005' :'Analog Channel B (R)', 
            '40006' :'Digital Channel B (L)', 
            '40007' :'Digital Channel B (R)', 
        }

        value = int(int(match.group(2))/10)
        self.WriteStatus('AudioInputGain', value, {'Type' : TypeStates[match.group(1).decode()]})

    def UpdateAudioLevel(self, value, qualifier):

        if qualifier['L/R'] in ['Left', 'Right']:
            AudioLevelCmdString = '34i'
            self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioLevel')

    def __MatchAudioLevel(self, match, tag):

        self.WriteStatus('AudioLevel', int(match.group(1))/10, {'L/R':'Left'})
        self.WriteStatus('AudioLevel', int(match.group(2))/10, {'L/R':'Right'})

    def SetAudioMuteInput(self, value, qualifier):

        TypeStates = {
            'Analog'  : 0, 
            'Digital' : 2
        }

        ChannelStates = {
            'A' : 0, 
            'B' : 4
        }

        LRStates = {
            'Left'  : 0, 
            'Right' : 1
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues and qualifier['Type'] in TypeStates and qualifier['Channel'] in ChannelStates and \
                qualifier['L/R'] in LRStates:
            Shift = ChannelStates[qualifier['Channel']] + TypeStates[qualifier['Type']] + LRStates[qualifier['L/R']]
            AudioMuteInputCmdString = 'wM4000{0}*{1}AU\r'.format(Shift,ValueStateValues[value])
            self.__SetHelper('AudioMuteInput', AudioMuteInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteInput')

    def UpdateAudioMuteInput(self, value, qualifier):

        TypeStates = {
            'Analog'  : 0, 
            'Digital' : 2
        }

        ChannelStates = {
            'A' : 0, 
            'B' : 4
        }

        LRStates = {
            'Left'  : 0, 
            'Right' : 1
        }

        if qualifier['Type'] in TypeStates and qualifier['Channel'] in ChannelStates and qualifier['L/R'] in LRStates:
            Shift = ChannelStates[qualifier['Channel']] + TypeStates[qualifier['Type']] + LRStates[qualifier['L/R']]
            AudioMuteInputCmdString = 'wM4000{0}AU\r'.format(Shift)
            self.__UpdateHelper('AudioMuteInput', AudioMuteInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMuteInput')

    def __MatchAudioMuteInput(self, match, tag):

        Left = [0,2,4,6]
        Digital = [2,3,6,7]

        State = {
            '1' : 'On',
            '0' : 'Off'
        }

        if 0 <= int(match.group(1).decode()) <=3:
            Channel = 'A'
        elif 4 <= int(match.group(1).decode()) <=7:
            Channel = 'B'

        if int(match.group(1).decode()) in Digital:
            Type = 'Digital'
        else:
            Type = 'Analog'

        if int(match.group(1).decode()) in Left:
            LR = 'Left'
        else:
            LR = 'Right'
        
        qualifier = {'Channel' : Channel, 'Type' : Type, 'L/R' : LR}

        value = State[match.group(2).decode()]
        self.WriteStatus('AudioMuteInput', value, qualifier)

    def SetAudioMuteOutput(self, value, qualifier):

        LRStates = {
            'Left'  : '0',
            'Right' : '1'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues and qualifier['L/R'] in LRStates:
            AudioMuteOutputCmdString = 'wM6000{0}*{1}AU\r'.format(LRStates[qualifier['L/R']],ValueStateValues[value])
            self.__SetHelper('AudioMuteOutput', AudioMuteOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteOutput')

    def UpdateAudioMuteOutput(self, value, qualifier):

        LRStates = {
            'Left'  : '0',
            'Right' : '1'
        }

        if qualifier['L/R'] in LRStates:
            AudioMuteOutputCmdString = 'wM6000{0}AU\r'.format(LRStates[qualifier['L/R']])
            self.__UpdateHelper('AudioMuteOutput', AudioMuteOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMuteOutput')

    def __MatchAudioMuteOutput(self, match, tag):

        LRStates = {
            '0' : 'Left',
            '1' : 'Right'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {'L/R' : LRStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMuteOutput', value, qualifier)

    def SetAudioOnlyRecording(self, value, qualifier):

        ValueStateValues = {
            'Enable' : '1',
            'Disable': '0'
        }

        if value in ValueStateValues:
            AudioOnlyRecordingCmdString = 'wA1*{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioOnlyRecording', AudioOnlyRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOnlyRecording')

    def UpdateAudioOnlyRecording(self, value, qualifier):

        AudioOnlyRecordingCmdString = 'wA1RCDR\r'
        self.__UpdateHelper('AudioOnlyRecording', AudioOnlyRecordingCmdString, value, qualifier)

    def __MatchAudioOnlyRecording(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioOnlyRecording', value, None)

    def SetAutoImage(self, value, qualifier): 
  
        State = {
            'A' : '1',
            'B' : '2',
        }

        if qualifier['Channel'] in State:
            CmdString = '{0}A\r'.format(State[qualifier['Channel']])
            self.__SetHelper('AutoImage', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBackgroundImageCommand(self, value, qualifier):

        filename = qualifier['Image Name']
        if value in ['Enable', 'Disable'] and filename:
            if value == 'Enable': #Enable based on 'Image Name' qualifier
                BackgroundImageCommandCmdString = 'w{}RF\r'.format(filename)
            else: #Mute Background Image
                BackgroundImageCommandCmdString = 'w0RF\r'

            self.__SetHelper('BackgroundImageCommand', BackgroundImageCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundImageCommand')

    def UpdateBackupRTMPStatus(self, value, qualifier):

        InputState = {
            'Archive A' : '1',
            'Archive B' : '2',
            'Confidence A' : '3'
        }

        if qualifier['Stream'] in InputState:
            BackupRTMPStatusCmdString = 'wS2*{0}RTMP\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('BackupRTMPStatus', BackupRTMPStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBackupRTMPStatus')

    def __MatchBackupRTMPStatus(self, match, qualifier):

        InputState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ValueStateValues = {
            '1' : 'Live', 
            '0' : 'Offline'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BackupRTMPStatus', value, {'Stream' : InputState[match.group(1).decode()]})

    def SetBitrateControl(self, value, qualifier):

        InputState = {
            'Archive A' : '1',
            'Archive B' : '2',
            'Confidence A' : '3'
        }

        ValueStateValues = {
            'VBR' : '0', 
            'CVBR' : '1', 
            'CBR' : '2'
        }

        if value in ValueStateValues and qualifier['Stream'] in InputState:
            BitrateControlCmdString ='w{0}*{1}BRCT\r'.format(InputState[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('BitrateControl', BitrateControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBitrateControl')

    def UpdateBitrateControl(self, value, qualifier):

        InputState = {
            'Archive A' : '1',
            'Archive B' : '2',
            'Confidence A' : '3'
        }

        if qualifier['Stream'] in InputState:
            BitrateControlCmdString = 'w{0}BRCT\r'.format(InputState[qualifier['Stream']])
            self.__UpdateHelper('BitrateControl', BitrateControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBitrateControl')

    def __MatchBitrateControl(self, match, tag):

        InputState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ValueStateValues = {
            '0' : 'VBR', 
            '1' : 'CVBR', 
            '2' : 'CBR'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BitrateControl', value, {'Stream': InputState[match.group(1).decode()]})

    def SetChapterMarker(self, value, qualifier): 

        CmdString = 'wBRCDR\r'
        self.__SetHelper('ChapterMarker', CmdString, value, qualifier)

    def SetClearActiveAlarms(self, value, qualifier):

        ClearActiveAlarmsCmdString = 'wCALRM\r'
        self.__SetHelper('ClearActiveAlarms', ClearActiveAlarmsCmdString, value, qualifier)

    def UpdateCPUUsage(self, value, qualifier):

        CPUUsageCmdString = '11i'
        self.__UpdateHelper('CPUUsage', CPUUsageCmdString, value, qualifier)

    def __MatchCPUUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CPUUsage', value, None)

    def UpdateCurrentRecordingDuration(self, value, qualifier):  
   
        CmdString = '35i'   
        self.__UpdateHelper('CurrentRecordingDuration', CmdString, value, qualifier)   
      
    def __MatchCurrentRecordingDuration(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' +match.group(3).decode()
        self.WriteStatus('CurrentRecordingDuration', value, None)

    def SetDelayedRecordingDuration(self, value, qualifier):

        if 1 <= int(value) <= 60:
            DelayedRecordingDurationCmdString = 'wP{0}RCDR\r'.format(value)
            self.__SetHelper('DelayedRecordingDuration', DelayedRecordingDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelayedRecordingDuration')

    def UpdateDelayedRecordingDuration(self, value, qualifier):

        DelayedRecordingDurationCmdString = 'wPRCDR\r'
        self.__UpdateHelper('DelayedRecordingDuration', DelayedRecordingDurationCmdString, value, qualifier)

    def __MatchDelayedRecordingDuration(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('DelayedRecordingDuration', value, None)

    def SetDualChannelHDMIOutput(self, value, qualifier):

        ValueStateValues = {
            'Channel A Fullscreen' : '0', 
            'Channel B Fullscreen' : '1', 
            'Confidence Layout'    : '2'
        }

        if value in ValueStateValues:
            DualChannelHDMIOutputCmdString = 'w{}OMOD\r'.format(ValueStateValues[value])
            self.__SetHelper('DualChannelHDMIOutput', DualChannelHDMIOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDualChannelHDMIOutput')

    def UpdateDualChannelHDMIOutput(self, value, qualifier):

        DualChannelHDMIOutputCmdString = 'wOMOD\r'
        self.__UpdateHelper('DualChannelHDMIOutput', DualChannelHDMIOutputCmdString, value, qualifier)

    def __MatchDualChannelHDMIOutput(self, match, tag):

        ValueStateValues = {
            '0' : 'Channel A Fullscreen', 
            '1' : 'Channel B Fullscreen', 
            '2' : 'Confidence Layout'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DualChannelHDMIOutput', value, None)

    def SetEjectUSBStorage(self, value, qualifier):

        EjectUSBStorageState = {
            'All'       : '0',
            'USB Front' : '2', 
            'USB Rear'  : '3',
            'USB RCP'   : '4'
        }

        if value in EjectUSBStorageState:
            EjectUSBStorageCmdString = 'w{0}USBE\r'.format(EjectUSBStorageState[value])
            self.__SetHelper('EjectUSBStorage', EjectUSBStorageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEjectUSBStorage')

    def SetEncoder(self, value, qualifier):

        ValueStateValues = {
            'Composite' : '0', 
            'Dual'      : '1'
        }

        if value in ValueStateValues:
            EncoderCmdString = 'w1*{0}ENCM\r'.format(ValueStateValues[value])
            self.__SetHelper('Encoder', EncoderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEncoder')

    def UpdateEncoder(self, value, qualifier):

        EncoderCmdString = 'w1ENCM\r'
        self.__UpdateHelper('Encoder', EncoderCmdString, value, qualifier)

    def __MatchEncoder(self, match, tag):

        ValueStateValues = {
            '0' : 'Composite', 
            '1' : 'Dual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Encoder', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off'                   : '0',
            'Complete Lock Out'     : '1',
            'Menu Lock Out'         : '2',
            'Recording Control Only' : '3'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'Complete Lock Out', 
            '2' : 'Menu Lock Out', 
            '3' : 'Recording Control Only'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFileDestination(self, value, qualifier):

        if qualifier['Drive'] in ['Primary', 'Secondary']:
            FileDestinationCmdString = 'I'
            self.__UpdateHelper('FileDestination', FileDestinationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFileDestination')

    def __MatchFileDestination(self, match, tag):

        ValueStateValues = {
            'N/A'      : 'NA', 
            'internal' : 'Internal', 
            'usbfront' : 'Front USB', 
            'usbrear'  : 'Rear USB',
            'usbrcp'   : 'RCP USB',
            'auto'     : 'Auto',
            '*'        : 'Drive not inserted while USB is set as Destination',
            ''         : 'Drive not inserted while USB is set as Destination'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FileDestination', value, {'Drive' : 'Primary'})
 
        if value == 'Auto':
            self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Primary', 'Unit': 'MB'})
            self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Primary', 'Unit': 'GB'})
            self.WriteStatus('FileDestination', 'NA', {'Drive' : 'Secondary'})
            self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'MB'})
            self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'GB'})
        else:
            if value != 'NA' and value != 'Drive not inserted while USB is set as Destination':
                self.WriteStatus('RemainingFreeDiskSpace', round(int(match.group(3).decode())/1024,2), {'Drive': 'Primary', 'Unit': 'MB'})
                self.WriteStatus('RemainingFreeDiskSpace', round(int(match.group(3).decode())/(1024*1024),2), {'Drive': 'Primary', 'Unit': 'GB'})
            else:
                self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive' : 'Primary', 'Unit': 'MB'})
            if  match.group(2) is not None:
                value2 = ValueStateValues[match.group(2).decode()]
                self.WriteStatus('FileDestination', value2, {'Drive' : 'Secondary'})
                if match.group(4) is not None:
                    self.WriteStatus('RemainingFreeDiskSpace', round(int(match.group(4).decode().replace('*',''))/1024,2), {'Drive': 'Secondary', 'Unit': 'MB'})
                    self.WriteStatus('RemainingFreeDiskSpace', round(int(match.group(4).decode().replace('*',''))/(1024*1024),2), {'Drive': 'Secondary', 'Unit': 'GB'})
                elif match.group(5) is not None:
                    self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'MB'})
                    self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'GB'})
            else:
                self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'MB'})
                self.WriteStatus('RemainingFreeDiskSpace', 0.00, {'Drive': 'Secondary', 'Unit': 'GB'})
                self.WriteStatus('FileDestination', 'NA', {'Drive' : 'Secondary'})

    def UpdateFTPUploadDestination(self, value, qualifier):

        FTPUploadDestinationCmdString = '38i'
        self.__UpdateHelper('FTPUploadDestination', FTPUploadDestinationCmdString, value, qualifier)

    def __MatchFTPUploadDestination(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FTPUploadDestination', value, None)

    def SetGOPLength(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        if 1 <= value <= 300 and qualifier['Stream'] in StreamStates:
            GOPLengthCmdString = 'w{0}*{1}GOPL\r'.format(StreamStates[qualifier['Stream']], value)
            self.__SetHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGOPLength')

    def UpdateGOPLength(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            GOPLengthCmdString = 'w{0}GOPL\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGOPLength')

    def __MatchGOPLength(self, match, tag):

        StreamStates = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        qualifier = {'Stream' : StreamStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        self.WriteStatus('GOPLength', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        if (self.ReadStatus('InputA', None) != qualifier['Input']) or (self.ReadStatus('InputB', None) != qualifier['Input']) and qualifier['Input'] in ['1', '2', '4']:
            HDCPStatusCmdString = 'wI{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputStatus', HDCPStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        InputStates = {
            '01' : '1', 
            '02' : '2', 
            '04' : '4'
        }

        ValueStateValues = {
            '0' : 'No Source Connected', 
            '1' : 'HDCP Content', 
            '2' : 'No HDCP Content'
        }

        qualifier = {'Input' : InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value,qualifier)

    def SetHDMIAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            HDMIAudioMuteCmdString = '99*{0}Z\r'.format(ValueStateValues[value])
            self.__SetHelper('HDMIAudioMute', HDMIAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIAudioMute')

    def UpdateHDMIAudioMute(self, value, qualifier):

        HDMIAudioMuteCmdString = '99Z'
        self.__UpdateHelper('HDMIAudioMute', HDMIAudioMuteCmdString, value, qualifier)

    def __MatchHDMIAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIAudioMute', value, None)

    def SetHDMIVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            HDMIVideoMuteCmdString = '99*{0}B\r'.format(ValueStateValues[value])
            self.__SetHelper('HDMIVideoMute', HDMIVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIVideoMute')

    def UpdateHDMIVideoMute(self, value, qualifier):

        HDMIVideoMuteCmdString = '99B'
        self.__UpdateHelper('HDMIVideoMute', HDMIVideoMuteCmdString, value, qualifier)

    def __MatchHDMIVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIVideoMute', value, None)

    def SetHorizontalVideoMirroring(self, value, qualifier):

        ValueStateValues = {
            'On'  : '4',
            'Off' : '0',
        }

        if value in ValueStateValues and qualifier['Input'] in self.InputStateQualifier:
            HorizontalVideoMirroringCmdString = 'wI{0}*{1}ROTA\r'.format(self.InputStateQualifier[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('HorizontalVideoMirroring', HorizontalVideoMirroringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalVideoMirroring')

    def UpdateHorizontalVideoMirroring(self, value, qualifier):

        if qualifier['Input'] in self.InputStateQualifier:
            HorizontalVideoMirroringCmdString = 'wI{0}ROTA\r'.format(self.InputStateQualifier[qualifier['Input']])
            self.__UpdateHelper('HorizontalVideoMirroring', HorizontalVideoMirroringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHorizontalVideoMirroring')

    def __MatchHorizontalVideoMirroring(self, match, tag):

        ValueStateValues = {
            '4' : 'On',
            '0' : 'Off',
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HorizontalVideoMirroring', value, {'Input': match.group(1).decode()})

    def SetInput3Format(self, value, qualifier):

        ValueStateValues = {
            'YUVp/HDTV' : '1', 
            'YUVi'      : '2', 
            'Composite' : '3'
        }

        if value in ValueStateValues:
            Input3FormatCmdString = '3*{0}\\'.format(ValueStateValues[value])
            self.__SetHelper('Input3Format', Input3FormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput3Format')

    def UpdateInput3Format(self, value, qualifier):

        Input3FormatCmdString = '3\\'
        self.__UpdateHelper('Input3Format', Input3FormatCmdString, value, qualifier)

    def __MatchInput3Format(self, match, tag):

        ValueStateValues = {
            '01' : 'YUVp/HDTV', 
            '02' : 'YUVi', 
            '03' : 'Composite'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input3Format', value, None)

    def SetInputA(self, value, qualifier): 

        if value in ['1', '2']:
            CmdString = '{0}*1!\r'.format(value)
            self.__SetHelper('InputA', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputA')

    def SetInputB(self, value, qualifier): 

        if value in self.InputBState:
            CmdString = '{0}*2!\r'.format(self.InputBState[value])
            self.__SetHelper('InputB', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputB')

    def UpdateInputStatus(self, value, qualifier):  

        CmdString = '32I'   
        self.__UpdateHelper('InputStatus', CmdString, value, qualifier) 
      
    def __MatchInputStatus(self, match, tag):

        InputAState = {
            '1'   : '1',  
            '2'   : '2',    
        }

        if tag == 'Set':    # Handle response from a Set command
            if match.group(2).decode() == '1':
                self.WriteStatus('InputA', InputAState[str(match.group(1).decode())], None)
            elif match.group(2).decode() == '2':
                self.WriteStatus('InputB', self.InputBState[str(match.group(1).decode())], None)
        elif tag == 'Update':   # Handle response from an Update command
            self.WriteStatus('InputA', InputAState[str(match.group(1).decode())], None)
            self.WriteStatus('InputB', self.InputBState[str(match.group(2).decode())], None)

    def UpdateLayoutPresetStatus(self, value, qualifier):

        LayoutPresetStatusCmdString = '49I'
        self.__UpdateHelper('LayoutPresetStatus', LayoutPresetStatusCmdString, value, qualifier)

    def __MatchLayoutPresetStatus(self, match, tag):

        value = match.group(1).decode()
        if 1 <= int(value) <= 16:
            self.WriteStatus('LayoutPresetStatus', value, None)

    def SetMetadata(self, value, qualifier):

        TypeStateValues = {
            'Contributor' : '0', 
            'Coverage'    : '1', 
            'Presenter'   : '2',
            'Description' : '4',
            'Format'      : '5',
            'Language'    : '7',
            'Publisher'   : '8',
            'Relation'    : '9',
            'Rights'      : '10',
            'Source'      : '11',
            'Subject'     : '12',
            'Title'       : '13',
            'Type'        : '14',
            'System Name' : '15',
            'Course'      : '16',
        }

        MetaString = qualifier['Metadata String']
        if MetaString and value in TypeStateValues:
            MetadataCmdString = 'wM{0}*{1}RCDR\r'.format(TypeStateValues[value], MetaString)
            self.__SetHelper('Metadata', MetadataCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMetadata')

    def UpdateMetadataStatus(self, value, qualifier):

        TypeStateValues = {
            'Contributor' : '0', 
            'Coverage'    : '1', 
            'Presenter'   : '2', 
            'Date'        : '3', # read only per API
            'Description' : '4',
            'Format'      : '5',
            'Identifier'  : '6', # read only per API
            'Language'    : '7',
            'Publisher'   : '8',
            'Relation'    : '9',
            'Rights'      : '10',
            'Source'      : '11',
            'Subject'     : '12',
            'Title'       : '13',
            'Type'        : '14',
            'System Name' : '15',
            'Course'      : '16'
        }

        if qualifier['Type'] in TypeStateValues:
            MetadataStatusCmdString = 'wM{}RCDR\r'.format(TypeStateValues[qualifier['Type']])
            self.__UpdateHelper('MetadataStatus', MetadataStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMetadataStatus')

    def __MatchMetadataStatus(self, match, tag):

        TypeStates = {
            '0' : 'Contributor',
            '1' : 'Coverage',
            '2' : 'Presenter',
            '3' : 'Date',
            '4' : 'Description',
            '5' : 'Format',
            '6' : 'Identifier',
            '7' : 'Language',
            '8' : 'Publisher',
            '9' : 'Relation',
            '10': 'Rights',
            '11': 'Source',
            '12': 'Subject',
            '13': 'Title',
            '14': 'Type',
            '15': 'System Name',
            '16': 'Course'
        }

        typeValue = TypeStates[match.group('type').decode()]
        if match.group('value'):
            value = match.group('value').decode()
        else:
            value = 'No Information'

        self.WriteStatus('MetadataStatus', value, {'Type': typeValue})
        
    def UpdatePrimaryRTMPStatus(self, value, qualifier):

        StreamState = {
            'Archive A' : '1',
            'Archive B' : '2',
            'Confidence A' : '3'
        }

        if qualifier['Stream'] in StreamState:
            PrimaryRTMPStatusCmdString = 'wS1*{0}RTMP\r'.format(StreamState[qualifier['Stream']])
            self.__UpdateHelper('PrimaryRTMPStatus', PrimaryRTMPStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePrimaryRTMPStatus')

    def __MatchPrimaryRTMPStatus(self, match, qualifier):

        StreamState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ValueStateValues = {
            '1' : 'Live', 
            '0' : 'Offline'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PrimaryRTMPStatus', value, {'Stream' : StreamState[match.group(1).decode()]})

    def SetRCP101ExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            RCP101ExecutiveModeCmdString = '99*{0}X\r'.format(ValueStateValues[value])
            self.__SetHelper('RCP101ExecutiveMode', RCP101ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRCP101ExecutiveMode')

    def UpdateRCP101ExecutiveMode(self, value, qualifier):

        RCP101ExecutiveModeCmdString = '99*X\r'
        self.__UpdateHelper('RCP101ExecutiveMode', RCP101ExecutiveModeCmdString, value, qualifier)

    def __MatchRCP101ExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RCP101ExecutiveMode', value, None)

    def SetRecallLayoutConfidenceDual(self, value, qualifier): 

        if 1 <= int(value) <= 10:
            CmdString = '9*3*{0}.'.format(value)
            self.__SetHelper('RecallLayoutConfidenceDual', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetRecallLayoutConfidenceDual')

    def SetRecallLayoutPreset(self, value, qualifier): 

        InputState = {
            'With Inputs'    : '7',
            'Without Inputs' : '8',
        }

        if 1 <= int(value) <= 16 and qualifier['Inputs'] in InputState:
            CmdString = '{0}*{1}.'.format(InputState[qualifier['Inputs']],value)
            self.__SetHelper('RecallLayoutPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallLayoutPreset')

    def SetRecallEncoderPreset(self, value, qualifier): 

        StreamStates = {
            'Archive A' : '1',
            'Archive B' : '2', 
            'Confidence A' : '3'
        }

        if 1 <= int(value) <= 32 and qualifier['Stream'] in StreamStates:
            CmdString = '4*{0}*{1}.'.format(StreamStates[qualifier['Stream']], value)
            self.__SetHelper('RecallEncoderPreset', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetRecallEncoderPreset')

    def SetRecallRecordingProfile(self, value, qualifier):

        if 0 < int(value) <= 32:
            CmdString = 'wR5*{0}PRST\r'.format(value)
            self.__SetHelper('RecallRecordingProfile', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallRecordingProfile')

    def UpdateRecallRecordingProfile(self, value, qualifier):

        CmdString = 'wL5PRST\r'
        self.__UpdateHelper('RecallRecordingProfile', CmdString, value, qualifier)

    def __MatchRecallRecordingProfile(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('RecallRecordingProfile', value, None)

    def SetRecallStreamingPreset(self, value, qualifier):

        StreamStates = {
            'Archive A'    : '1',
            'Archive B'    : '2',
            'Confidence A' : '3'
        }

        if 1 <= int(value) <= 32 and qualifier['Stream'] in StreamStates:
            RecallStreamingPresetCmdString = '3*{0}*{1}.'.format(StreamStates[qualifier['Stream']], value)
            self.__SetHelper('RecallStreamingPreset', RecallStreamingPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallStreamingPreset')

    def SetRecallUserPreset(self, value, qualifier): 

        ChannelState = {
            'A' : '1',
            'B' : '2',
        }

        if 1 <= int(value) <= 16 and qualifier['Channel'] in ChannelState:
            CmdString = '1*{0}*{1}.'.format(ChannelState[qualifier['Channel']],value)
            self.__SetHelper('RecallUserPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallUserPreset')

    def SetRecord(self, value, qualifier): 

        State = {
            'Start'   : '1',  
            'Stop'    : '0',
            'Pause'   : '2' 
        }

        if value in State:
            CmdString = 'wY{0}RCDR\r'.format(State[value])
            self.__SetHelper('Record', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecord')

    def UpdateRecord(self, value, qualifier):  
   
        CmdString = 'wYRCDR\r'   
        self.__UpdateHelper('Record', CmdString, value, qualifier)   
      
    def __MatchRecord(self, match, tag):

        State = {
            '1':'Start',  
            '0':'Stop',
            '2':'Pause' 
        }

        value = State[match.group(1).decode()]
        self.WriteStatus('Record', value, None)

    def SetRecordExtend(self, value, qualifier): 
 
        if 1 <= int(value) <= 60:
            CmdString = 'wE{0}RCDR\r'.format(value)
            self.__SetHelper('RecordExtend', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordExtend')

    def SetRecordControl(self, value, qualifier):

        ValueStateValues = {
            'Enable'      : '1', 
            'Disable'     : '0',
            'Enable Dual' : '2'
        }

        if value in ValueStateValues:
            RecordControlCmdString = 'wX1*{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordControl', RecordControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordControl')

    def UpdateRecordControl(self, value, qualifier):

        RecordControlCmdString = 'wX1RCDR\r'
        self.__UpdateHelper('RecordControl', RecordControlCmdString, value, qualifier)

    def __MatchRecordControl(self, match, tag):

        ValueStateValues = {
            '1' : 'Enable', 
            '0' : 'Disable',
            '2' : 'Enable Dual'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('RecordControl', value, None)

    def SetRecordDestination(self, value, qualifier):

        ValueStateValues = {
            'Auto' : '0', 
            'Internal' : '1',
            'USB (Front)' : '2',
            'USB (Rear)' : '3',
            'Internal + USB Front' : '12',
            'Internal + USB Rear' : '13',
            'Internal + USB RCP' : '14',
            'Internal + Auto' : '11'
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
            '00' : 'Auto', 
            '01' : 'Internal',
            '02' : 'USB (Front)',
            '03' : 'USB (Rear)',
            '12' : 'Internal + USB Front',
            '13' : 'Internal + USB Rear',
            '14' : 'Internal + USB RCP',
            '11' : 'Internal + Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordDestination', value, None)

    def SetRecordDualControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            RecordDualControlCmdString = 'wX2*{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordDualControl', RecordDualControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordDualControl')

    def UpdateRecordDualControl(self, value, qualifier):

        RecordDualControlCmdString = 'wX2RCDR\r'
        self.__UpdateHelper('RecordDualControl', RecordDualControlCmdString, value, qualifier)

    def __MatchRecordDualControl(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordDualControl', value, None)

    def SetRecordingMode(self, value, qualifier):

        ValueStateValues = {
            'Audio and Video' : '1', 
            'Video Only' : '2'
        }

        if value in ValueStateValues:
            RecordingModeCmdString = 'w1*{0}SMOD\r'.format(ValueStateValues[value])
            self.__SetHelper('RecordingMode', RecordingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordingMode')

    def UpdateRecordingMode(self, value, qualifier):

        RecordingModeCmdString = 'w1SMOD\r'
        self.__UpdateHelper('RecordingMode', RecordingModeCmdString, value, qualifier)

    def __MatchRecordingMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Audio and Video', 
            '2' : 'Video Only'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordingMode', value, None)

    def __MatchRecordingStartCountdown(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('RecordingStartCountdown', value, None)

    def SetRecordingVideoFrameRate(self, value, qualifier): 

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        State = {
            '30 fps'    : '1',  
            '25 fps'    : '2',
            '24 fps'    : '3', 
            '15 fps'    : '4',  
            '12.5 fps'  : '5',
            '12 fps'    : '6',
            '10 fps'    : '7',
            '5 fps'     : '8',  
        }

        if value in State and qualifier['Stream'] in StreamStates:
            CmdString = 'w{0}*{1}VFRM\r'.format(StreamStates[qualifier['Stream']], State[value])
            self.__SetHelper('RecordingVideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordingVideoFrameRate')

    def UpdateRecordingVideoFrameRate(self, value, qualifier):  

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            CmdString = 'w{}VFRM\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RecordingVideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRecordingVideoFrameRate')
      
    def __MatchRecordingVideoFrameRate(self, match, tag):

        StreamState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        State = {
            '1' : '30 fps',
            '2' : '25 fps',
            '3' : '24 fps',
            '4' : '15 fps',
            '5' : '12.5 fps',
            '6' : '12 fps',
            '7' : '10 fps',
            '8' : '5 fps',
        }

        qualifier = {'Stream' : StreamState[match.group(1).decode()]}
        value = State[match.group(2).decode()]
        self.WriteStatus('RecordingVideoFrameRate', value, qualifier)

    def SetRecordResolution(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        ValueStateValues = {
            '480p'      : '1',
            '720p'      : '2',
            '1080p'     : '3',
            '512x288'   : '4',
            '1024x768'  : '5',
            '1280x1024' : '6',
            'Custom'    : '99'
        }

        if value in ValueStateValues and qualifier['Stream'] in StreamStates:
            RecordResolutionCmdString = 'w{0}*{1}VRES\r'.format(StreamStates[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('RecordResolution', RecordResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordResolution')

    def UpdateRecordResolution(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RecordResolutionCmdString = 'w{}VRES\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RecordResolution', RecordResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRecordResolution')

    def __MatchRecordResolution(self, match, tag):

        StreamState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ValueStateValues = {
            '1' : '480p', 
            '2' : '720p', 
            '3' : '1080p',
            '4' : '512x288',
            '5' : '1024x768',
            '6' : '1280x1024',
            '99' : 'Custom' 
        }

        qualifier = {'Stream': StreamState[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('RecordResolution', value, qualifier)

    def UpdateRemainingFreeDiskSpace(self, value, qualifier):  
   
        self.UpdateFileDestination( value, qualifier)
      
    def UpdateRemainingFrontUSBStorage(self, value, qualifier):

        RemainingFrontUSBStorageCmdString = '56I'
        self.__UpdateHelper('RemainingFrontUSBStorage', RemainingFrontUSBStorageCmdString, value, qualifier)

    def __MatchRemainingFrontUSBStorage(self, match, tag):

        if match.group(1).decode() == 'N/A':
            self.WriteStatus('RemainingFrontUSBStorage', 0, {'Unit': 'MB'})
            self.WriteStatus('RemainingFrontUSBStorage', 0, {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Removed', {'USB Port' : 'Front USB'})
        else:
            self.WriteStatus('RemainingFrontUSBStorage', round(int(match.group(2).decode())), {'Unit': 'MB'})
            self.WriteStatus('RemainingFrontUSBStorage', round(int(match.group(2).decode())/1000,2), {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Inserted', {'USB Port': 'Front USB'})

    def UpdateRemainingInternalStorage(self, value, qualifier):

        RemainingInternalStorageCmdString = '55I'
        self.__UpdateHelper('RemainingInternalStorage', RemainingInternalStorageCmdString, value, qualifier)

    def __MatchRemainingInternalStorage(self, match, tag):

        self.WriteStatus('RemainingInternalStorage', round(int(match.group(1).decode())), {'Unit': 'MB'})
        self.WriteStatus('RemainingInternalStorage', round(int(match.group(1).decode())/1000, 2), {'Unit': 'GB'})

    def UpdateRemainingRearRCPUSBStorage(self, value, qualifier):
            
        RemainingRearRCPUSBStorageCmdString = '58I'
        self.__UpdateHelper('RemainingRearRCPUSBStorage', RemainingRearRCPUSBStorageCmdString, value, qualifier)

    def __MatchRemainingRearRCPUSBStorage(self, match, tag):

        if match.group(1).decode() == 'N/A':
            self.WriteStatus('RemainingRearRCPUSBStorage', 0, {'Unit': 'MB'})
            self.WriteStatus('RemainingRearRCPUSBStorage', 0, {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Removed', {'USB Port': 'Rear RCP'})
        else:
            self.WriteStatus('RemainingRearRCPUSBStorage', round(int(match.group(2).decode())), {'Unit': 'MB'})
            self.WriteStatus('RemainingRearRCPUSBStorage', round(int(match.group(2).decode()) / 1000, 2), {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Inserted', {'USB Port': 'Rear RCP'})

    def UpdateRemainingRearUSBStorage(self, value, qualifier):
            
        RemainingRearUSBStorageCmdString = '57I'
        self.__UpdateHelper('RemainingRearUSBStorage', RemainingRearUSBStorageCmdString, value, qualifier)

    def __MatchRemainingRearUSBStorage(self, match, tag):

        if match.group(1).decode() == 'N/A':
            self.WriteStatus('RemainingRearUSBStorage', 0, {'Unit': 'MB'})
            self.WriteStatus('RemainingRearUSBStorage', 0, {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Removed', {'USB Port': 'Rear USB'})
        else:
            self.WriteStatus('RemainingRearUSBStorage', round(int(match.group(2).decode())), {'Unit': 'MB'})
            self.WriteStatus('RemainingRearUSBStorage', round(int(match.group(2).decode()) / 1000, 2), {'Unit': 'GB'})
            self.WriteStatus('USBStatus', 'Inserted', {'USB Port': 'Rear USB'})

    def UpdateRemainingRecordingTime(self, value, qualifier):  
            
        CmdString = '36i'   
        self.__UpdateHelper('RemainingRecordingTime', CmdString, value, qualifier)
      
    def __MatchRemainingRecordingTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        self.WriteStatus('RemainingRecordingTime', value, {'Drive' : 'Primary'})
        if match.group(4) is not None:
            value2 = match.group(4).decode() + ':' + match.group(5).decode() + ':' + match.group(6).decode()
            self.WriteStatus('RemainingRecordingTime', value2, {'Drive' : 'Secondary'})
        else:
            self.WriteStatus('RemainingRecordingTime', '00:00:00', {'Drive' : 'Secondary'})

    def SetRTMPBackupURLCommand(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1', 
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        RTMPString = qualifier['RTMP Backup URL String']
        if RTMPString and qualifier['Stream'] in StreamStates:
            RTMPKey = qualifier['RTMP Backup URL Key String']
            if RTMPKey:
                sendString = RTMPString + RTMPKey
            else:
                sendString = RTMPString

            RTMPBackupURLCommandCmdString = 'wU2*{0}*{1}RTMP\r'.format(StreamStates[qualifier['Stream']], sendString)
            self.__SetHelper('RTMPBackupURLCommand', RTMPBackupURLCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRTMPBackupURLCommand')

    def UpdateRTMPBackupURLStatus(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1', 
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RTMPBackupURLStatusCmdString = 'wU2*{0}RTMP\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RTMPBackupURLStatus', RTMPBackupURLStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRTMPBackupURLStatus')

    def __MatchRTMPBackupURLStatus(self, match, tag):

        TypeStates = {
            '01' : 'Archive A',
            '02' : 'Archive B',
            '03' : 'Confidence A'
        }

        qualifier = {'Stream' : TypeStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('RTMPBackupURLStatus', value, qualifier)

    def SetRTMPPrimaryURLCommand(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1', 
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RTMPString = qualifier['RTMP Backup URL String']
            RTMPKey = qualifier['RTMP Backup URL Key String']

            if RTMPKey:
                sendString = RTMPString + RTMPKey
            else:
                sendString = RTMPString

            if sendString:
                RTMPPrimaryURLCommandCmdString = 'wU1*{0}*{1}RTMP\r'.format(StreamStates[qualifier['Stream']], sendString)
                self.__SetHelper('RTMPPrimaryURLCommand', RTMPPrimaryURLCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetRTMPPrimaryURLCommand')
        else:
            self.Discard('Invalid Command for SetRTMPPrimaryURLCommand')

    def UpdateRTMPPrimaryURLStatus(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1', 
            'Archive B'     : '2', 
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RTMPPrimaryURLStatusCmdString = 'wU1*{0}RTMP\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RTMPPrimaryURLStatus', RTMPPrimaryURLStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRTMPPrimaryURLStatus')

    def __MatchRTMPPrimaryURLStatus(self, match, tag):

        TypeStates = {
            '01' : 'Archive A',
            '02' : 'Archive B',
            '03' : 'Confidence A'
        }

        qualifier = {'Stream' : TypeStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('RTMPPrimaryURLStatus', value, qualifier)

    def SetRTMPStream(self, value, qualifier):

        StreamStates = {
            'Archive A'       : '1',
            'Archive B'       : '2',
            'Confidence A'    : '3'
        }

        ValueStateValues = {
            'Enable' : '1', 
            'Disable' : '0'
        }

        if value in ValueStateValues and qualifier['Stream'] in StreamStates:
            RTMPStreamCmdString = 'wE{0}*{1}RTMP\r'.format(StreamStates[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRTMPStream')

    def UpdateRTMPStream(self, value, qualifier):

        StreamStates = {
            'Archive A'         : '1',
            'Archive B'         : '2',
            'Confidence A'      : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RTMPStreamCmdString = 'wE{0}RTMP\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRTMPStream')

    def __MatchRTMPStream(self, match, tag):

        StreamStates = {
            '1'     : 'Archive A',
            '01'    : 'Archive A',
            '2'     : 'Archive B',
            '02'    : 'Archive B',
            '3'     : 'Confidence A',
            '03'    : 'Confidence A'
        }

        ValueStateValues = {
            '1'     : 'Enable',
            '01'    : 'Enable',
            '0'     : 'Disable',
            '00'    : 'Disable'
        }

        qualifier = {'Stream' : StreamStates[match.group('type').decode()]}
        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('RTMPStream', value, qualifier)

    def UpdateRTSPStreamURL(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        if qualifier['Stream'] in StreamStates:
            RTSPStreamURLCmdString = 'wCi\rwN{}STRC\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('RTSPStreamURL', RTSPStreamURLCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRTSPStreamURL')

    def __MatchRTSPStreamURL(self, match, tag):

        ValueStateValues = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ipAddress = match.group(1).decode()
        name = match.group(3).decode()
        qualifier = {'Stream' : ValueStateValues[match.group(2).decode()]}
        if name == '':
            value = 'None'
        else:
            value = 'rtsp://' + ipAddress + '/' + name
        self.WriteStatus('RTSPStreamURL', value, qualifier)

    def SetSMPRecordingFolderShare(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if value in ValueStateValues:
            SMPRecordingFolderShareCmdString = 'wE1*{}SHRF\r'.format(ValueStateValues[value])
            self.__SetHelper('SMPRecordingFolderShare', SMPRecordingFolderShareCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSMPRecordingFolderShare')

    def UpdateSMPRecordingFolderShare(self, value, qualifier):

        SMPRecordingFolderShareCmdString = 'wE1SHRF\r'
        self.__UpdateHelper('SMPRecordingFolderShare', SMPRecordingFolderShareCmdString, value, qualifier)

    def __MatchSMPRecordingFolderShare(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SMPRecordingFolderShare', value, None)

    def SetStreamControl(self, value, qualifier):

        StreamStates = {
            'Archive A'       : '1',
            'Archive B'       : '2',
            'Confidence A'    : '3'
        }

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if value in ValueStateValues and qualifier['Stream'] in StreamStates:
            StreamControlCmdString = 'w{0}*{1}STRC\r'.format(StreamStates[qualifier['Stream']], ValueStateValues[value])
            self.__SetHelper('StreamControl', StreamControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamControl')

    def UpdateStreamControl(self, value, qualifier):

        StreamStates = {
            'Archive A'         : '1',
            'Archive B'         : '2',
            'Confidence A'      : '3'
        }

        if qualifier['Stream'] in StreamStates:
            StreamControlCmdString = 'w{0}STRC\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('StreamControl', StreamControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStreamControl')

    def __MatchStreamControl(self, match, tag):

        TypeStates = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        ValueStateValues = {
            '1' : 'Enable', 
            '0' : 'Disable'
        }

        qualifier = {'Stream' : TypeStates[match.group('type').decode()]}
        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('StreamControl', value, qualifier)

    def UpdateStreamingPresetsName(self, value, qualifier):

        if 1 <= int(qualifier['Preset']) <= 32:
            StreamingPresetsNameCmdString = 'w3*{}PNAM\r'.format(qualifier['Preset'])
            self.__UpdateHelper('StreamingPresetsName', StreamingPresetsNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStreamingPresetsName')

    def __MatchStreamingPresetsName(self, match, tag):

        preset = int(match.group(1).decode())
        if 1 <= preset <= 32:
            qualifier = {'Preset' : str(preset)}
            value = 'Unassigned' if match.group(2).decode() == 'null' else match.group(2).decode()
            self.WriteStatus('StreamingPresetsName', value, qualifier)

    def SetSwapWindows(self, value, qualifier): 

        CmdString = '%'
        self.__SetHelper('SwapWindows', CmdString, value, qualifier)

    def SetThumbnailSize(self, value, qualifier):

        ValueStateValues = {
            'Default' : '0', 
            'Archived Resolution' : '1'
        }

        if value in ValueStateValues:
            ThumbnailSizeCmdString = 'wT{0}RCDR\r'.format(ValueStateValues[value])
            self.__SetHelper('ThumbnailSize', ThumbnailSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThumbnailSize')

    def UpdateThumbnailSize(self, value, qualifier):

        ThumbnailSizeCmdString = 'wTRCDR\r'
        self.__UpdateHelper('ThumbnailSize', ThumbnailSizeCmdString, value, qualifier)

    def __MatchThumbnailSize(self, match, tag):

        ValueStateValues = {
            '0' : 'Default', 
            '1' : 'Archived Resolution'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ThumbnailSize', value, None)

    def UpdateUSBStatus(self, value, qualifier):

        usb = qualifier['USB Port']
        if usb == 'Front USB':
            self.UpdateRemainingFrontUSBStorage( value, qualifier)
        elif usb == 'Rear USB':
            self.UpdateRemainingRearUSBStorage( value, qualifier)
        elif usb == 'Rear RCP':
            self.UpdateRemainingRearRCPUSBStorage( value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUSBStatus')

    def __MatchUSBStatus(self, match, tag):

        USBPortStates = {
            'usbfront'  : 'Front USB',
            'usbrear'   : 'Rear USB',
            'usbrcp'    : 'Rear RCP'
        }

        ValueStateValues = {
            '1' : 'Inserted',
            '0' : 'Removed'
        }

        qualifier = {'USB Port' : USBPortStates[match.group(2).decode()]}
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBStatus', value, qualifier)

    def SetVideoBitrate(self, value, qualifier):

        StreamStates = {
            'Archive A'     : '1',
            'Archive B'     : '2',
            'Confidence A'  : '3'
        }

        if 200 <= value <= 10000 and qualifier['Stream'] in StreamStates:
            VideoBitrateCmdString = 'wV{0}*{1}BITR\r'.format(StreamStates[qualifier['Stream']], value)
            self.__SetHelper('VideoBitrate', VideoBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoBitrate')

    def UpdateVideoBitrate(self, value, qualifier):

        StreamStates = {
            'Archive A' : '1',
            'Archive B' : '2',
            'Confidence A' : '3'
        }

        if qualifier['Stream'] in StreamStates:
            VideoBitrateCmdString = 'wV{0}BITR\r'.format(StreamStates[qualifier['Stream']])
            self.__UpdateHelper('VideoBitrate', VideoBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoBitrate')

    def __MatchVideoBitrate(self, match, tag):

        InputState = {
            '1' : 'Archive A',
            '2' : 'Archive B',
            '3' : 'Confidence A'
        }

        value = int(match.group(2).decode())
        self.WriteStatus('VideoBitrate', value, {'Stream' : InputState[match.group(1).decode()]})

    def SetVideoMute(self, value, qualifier): 

        ChannelStates = {
            'A' : '1',
            'B' : '2',
        }

        State = {
            'On'   : '1',  
            'Off'  : '0',
        }

        if value in State and qualifier['Channel'] in ChannelStates:
            CmdString = '{0}*{1}B'.format(ChannelStates[qualifier['Channel']],State[value])
            self.__SetHelper('VideoMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):  

        ChannelStates = {
            'A'   : '1',  
            'B'   : '2',
        }

        if qualifier['Channel'] in ChannelStates:
            CmdString = '{0}B'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')
      
    def __MatchVideoMute(self, match, tag):

        State = {
            '00' : 'Off',
            '01' : 'On',
        }

        Channel = {
            '1'   : 'A',  
            '2'   : 'B',
        }
         
        self.WriteStatus('VideoMute', State[match.group(2).decode()], {'Channel' : Channel[match.group(1).decode()]})

    def SetVirtualInputRecording(self, value, qualifier):

        InputStates = {
            '1' : '4',
            '2' : '5'
        }

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if qualifier['Input'] in InputStates and value in ValueStateValues:
            VirtualInputRecordingCmdString = 'wX{}*{}RCDR\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('VirtualInputRecording', VirtualInputRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualInputRecording')

    def UpdateVirtualInputRecording(self, value, qualifier):

        InputStates = {
            '1' : '4',
            '2' : '5'
        }

        if qualifier['Input'] in InputStates:
            VirtualInputRecordingCmdString = 'wX{}RCDR\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('VirtualInputRecording', VirtualInputRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualInputRecording')

    def __MatchVirtualInputRecording(self, match, tag):

        InputStates = {
            '4' : '1',
            '5' : '2'
        }

        ValueStateValues = {
            '1' : 'Enable',
            '0' : 'Disable'
        }

        qualifier = {'Input' : InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VirtualInputRecording', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
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
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '10' : 'Unrecognized command',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter (number is out of range)',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '26' : 'Maximum connections exceeded',
            '28' : 'Bad filename or file not found'
        }

        if qualifier:
            value = match[1:-2]
        else:
            value = match.group(1).decode()

        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ value])
  
    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True

    def SMP351_Base(self):
        self.InputBState = {
            '3'   : '3',  
            '4'   : '4',
        }

        self.InputStateQualifier = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

    def SMP351_3GSDI(self):
        self.InputBState = {
            '3'   : '3',  
            '4'   : '4',
            '5'   : '5'
        }

        self.InputStateQualifier = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5'
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
        
        #check incoming data if it matched any expected data from device module
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()