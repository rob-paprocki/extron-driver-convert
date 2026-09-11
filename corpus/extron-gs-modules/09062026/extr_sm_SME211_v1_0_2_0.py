from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from math import floor


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'Alarm': {'Parameters': ['Alarm Number'], 'Status': {}},
            'AlarmSeverity': {'Parameters': ['Alarm Number'], 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioBitRate': {'Parameters': ['Encoder'], 'Status': {}},
            'AudioInputGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioLevel': {'Parameters': ['L/R'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'BitRateControlType': {'Parameters': ['Encoder'], 'Status': {}},
            'ClearActiveAlarms': { 'Status': {}},
            'CPUUsage': { 'Status': {}},
            'EDID': { 'Status': {}},
            'EncodeProfile': {'Parameters': ['Encoder'], 'Status': {}}, 
            'ExecutiveMode': { 'Status': {}},
            'GOPLength': {'Parameters': ['Encoder'], 'Status': {}},
            'HDCPStatus': { 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'Metadata': { 'Status': {}},
            'MetadataStatus': {'Parameters': ['Type'], 'Status': {}},
            'OutputAudioMute': {'Parameters': ['L/R'], 'Status': {}},
            'RecallEncoderPreset': {'Parameters': ['Encoder'], 'Status': {}},
            'RecallInputPreset': { 'Status': {}},
            'RecallStreamingPreset': {'Parameters': ['Encoder', 'Type'], 'Status': {}},
            'MetadataProfiles': { 'Status': {}},
            'VideoFrameRate': {'Parameters': ['Encoder'], 'Status': {}},
            'VideoEncodingResolution': {'Parameters': ['Encoder'], 'Status': {}},
            'RTMPPrimaryDestination': { 'Status': {}},
            'RTMPPrimaryDestinationURLStatus': { 'Status': {}},
            'RTMPStream': { 'Status': {}},
            'SaveEncoderPreset': {'Parameters': ['Encoder'], 'Status': {}},
            'SaveInputPreset': { 'Status': {}},
            'StreamingControls': { 'Status': {}},
            'StreamingPresetSave': {'Parameters': ['Encoder', 'Type'], 'Status': {}},
            'StreamingPresetName': {'Parameters': ['Preset', 'Type'], 'Status': {}},
            'VideoBitRate': {'Parameters': ['Encoder'], 'Status': {}},
            'VideoMute': { 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Inf39(?:\*\<name\:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server)\,level\:(warning|critical|info|emergency)\>)+\r\n'), self.__MatchAlarm, None)
            self.AddMatchString(re.compile(b'Inf39\*(None active)\r\n'), self.__MatchAlarm, "No Alarm")
            self.AddMatchString(re.compile(b'Aspr([1-3])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'BitrA([12])\*(080|096|128|192|256|320)\r\n'), self.__MatchAudioBitRate, None)
            self.AddMatchString(re.compile(b'DsG(40000|40001|40002|40003)\*(\-?\d{1,3})\r\n'), self.__MatchAudioInputGain, None)
            self.AddMatchString(re.compile(b'Inf34\*(-?\d{1,4})\*(-?\d{1,4})\r\n'), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b'DsM4000([0-3])\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'DsM6000([01])\*([01])\r\n'), self.__MatchOutputAudioMute, None)
            self.AddMatchString(re.compile(b'Brct([12])\*([0-2])\r\n'), self.__MatchBitRateControlType, None)
            self.AddMatchString(re.compile(b'Inf11\*(\d{1,3})\r\n'), self.__MatchCPUUsage, None)
            self.AddMatchString(re.compile(b'EdidA(\d{2})\r\n'), self.__MatchEDID, None)
            self.AddMatchString(re.compile(b'Epro([12])\*(\d+)\r\n'), self.__MatchEncodeProfile, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Gopl([12])\*(\d{1,2})\r\n'), self.__MatchGOPLength, None)
            self.AddMatchString(re.compile(b'HdcpI([0-2])\r\n'), self.__MatchHDCPStatus, None)
            self.AddMatchString(re.compile(b'PrstL5\*(0[0-9]|1[0-6])'), self.__MatchMetadataProfiles, None)
            self.AddMatchString(re.compile(b'StrmM([0-9]|1[0-9])\*([\s\S]{0,})\r\n'), self.__MatchMetadataStatus, None)
            self.AddMatchString(re.compile(b'Vfrm([12])\*([1-8])\r\n'), self.__MatchVideoFrameRate, None)
            self.AddMatchString(re.compile(b'Vres([12])\*([0-5])\r\n'), self.__MatchVideoEncodingResolution, None)
            self.AddMatchString(re.compile(b'BitrV([12])\*(\d{4,5})\r\n'), self.__MatchVideoBitRate, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'RtmpU1\*([\s\S]{0,})\r\n'), self.__MatchRTMPPrimaryDestinationURLStatus, None)
            self.AddMatchString(re.compile(b'(Strm|STRMY)([0-3])\r\n'), self.__MatchStreamingControls, None)
            self.AddMatchString(re.compile(b'RtmpE1\*([01])\r\n'), self.__MatchRTMPStream, None)
            self.findCondition = re.compile(b'\*\<name\:(video_loss|hdcp_video|audio_loss|disk_space|disk_error|record_halt|temperature\.internal|cpu_usage|ntp\.sync|usb\.front\.overcurrent|usb\.rear\.overcurrent|usb\.keyboard\.overcurrent|usb\.mouse\.overcurrent|auth_failures|sched_server)\,level\:(warning|critical|info|emergency)\>')
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)     
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)  

        self.MetadataStatusRegex = re.compile('StrmM(.*)\r\n')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __QueuePassword(self):
        self.SetPassword( None, None)

    def __MatchPassword(self, match, tag):        
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

    def __MatchLoginAdmin(self, match, tag):
        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0
        
    def __MatchLoginUser(self, match, tag):
        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])
           
    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
    def UpdateAlarm(self, value, qualifier):
        AlarmCmdString = '39i'
        self.__UpdateHelper('Alarm', AlarmCmdString, value, qualifier)

    def __MatchAlarm(self, match, tag):

        LevelStates = {
            'warning'   : 'Warning', 
            'critical'  : 'Critical', 
            'info'      : 'Info', 
            'emergency' : 'Emergency'
        }

        ValueStateValues = {
            'video_loss'                : 'Video Loss', 
            'audio_loss'                : 'Audio Loss', 
            'disk_space'                : 'Disk Space', 
            'record_halt'               : 'Halt Recording', 
            'ntp.sync'                  : 'NTP Sync',
            'auth_failures'             : 'Authentication Failures', 
            'disk_error'                : 'Disk Error', 
            'temperature.internal'      : 'Internal Temperature', 
            'hdcp_video'                : 'HDCP',
            'cpu_usage'                 : 'CPU Usage', 
            'usb.front.overcurrent'     : 'USB Front Overcurrent', 
            'usb.rear.overcurrent'      : 'USB Rear Overcurrent', 
            'usb.keyboard.overcurrent'  : 'USB Keyboard Overcurrent', 
            'usb.mouse.overcurrent'     : 'USB Mouse Overcurrent', 
            'sched_server'              : 'Schedule Server'
        }

        if tag == 'No Alarm':
            for x in range(0,12):
                qualifier = {'Alarm Number' : str(x+1)}
                self.WriteStatus('Alarm', 'None Active', qualifier)
                self.WriteStatus('AlarmSeverity', 'Cleared', qualifier)        
        else:
            alarmList = re.findall(self.findCondition, match.group(0))
            
            for enum, x in enumerate(alarmList):
                qualifier = {'Alarm Number' : str(enum+1)}
                self.WriteStatus('Alarm', ValueStateValues[x[0].decode()], qualifier)
                self.WriteStatus('AlarmSeverity', LevelStates[x[1].decode()], qualifier)
        
            for x in range(len(alarmList), 12):
                qualifier = {'Alarm Number' : str(x+1)}
                self.WriteStatus('Alarm', 'None Active', qualifier)
                self.WriteStatus('AlarmSeverity', 'Cleared', qualifier)

    def UpdateAlarmSeverity(self, value, qualifier):

        self.UpdateAlarm( value, qualifier)
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill'   : '1', 
            'Follow' : '2', 
            'Fit'    : '3'
        }

        AspectRatioCmdString = 'w{0}ASPR\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'wASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1' : 'Fill', 
            '2' : 'Follow', 
            '3' : 'Fit'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioBitRate(self, value, qualifier):

        ValueStateValues = {
            '80' : '80', 
            '96' : '96', 
            '128' : '128', 
            '192' : '192', 
            '256' : '256', 
            '320' : '320'
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            AudioBitRateCmdString = 'wA{0}*{1}BITR\r'.format(encoder, ValueStateValues[value])
            self.__SetHelper('AudioBitRate', AudioBitRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioBitRate')

    def UpdateAudioBitRate(self, value, qualifier):

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            AudioBitRateCmdString = 'wA{0}BITR\r'.format(encoder)
            self.__UpdateHelper('AudioBitRate', AudioBitRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioBitRate')

    def __MatchAudioBitRate(self, match, tag):

        ValueStateValues = {
            '080' : '80', 
            '096' : '96', 
            '128' : '128', 
            '192' : '192', 
            '256' : '256', 
            '320' : '320'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioBitRate', value, {'Encoder': '1'})
        self.WriteStatus('AudioBitRate', value, {'Encoder': '2'})

    def SetAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Analog audio left'   : '40000', 
            'Analog audio right'  : '40001', 
            'HDMI audio left'     : '40002', 
            'HDMI audio right'    : '40003', 
        }

        ValueConstraints = {
            'Min' : -18,
            'Max' : 24
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioInputGainCmdString = 'wG{0}*{1}AU\r'.format(TypeStates[qualifier['Channel']],value*10)
            self.__SetHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputGain')

    def UpdateAudioInputGain(self, value, qualifier):

        TypeStates = {
            'Analog audio left'   : '40000', 
            'Analog audio right'  : '40001', 
            'HDMI audio left'     : '40002', 
            'HDMI audio right'    : '40003',  
        }

        AudioInputGainCmdString = 'wG{0}AU\r'.format(TypeStates[qualifier['Channel']])
        self.__UpdateHelper('AudioInputGain', AudioInputGainCmdString, value, qualifier)

    def __MatchAudioInputGain(self, match, tag):

        TypeStates = {
            '40000' :'Analog audio left', 
            '40001' :'Analog audio right', 
            '40002' :'HDMI audio left', 
            '40003' :'HDMI audio right', 
        }

        value = int(int(match.group(2).decode())/10)
        self.WriteStatus('AudioInputGain', value, {'Channel':TypeStates[match.group(1).decode()]})

    def UpdateAudioLevel(self, value, qualifier):

        AudioLevelCmdString = '34i'
        self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)

    def __MatchAudioLevel(self, match, tag):

        Left = int(match.group(1).decode())/10
        Right = int(match.group(2).decode())/10
        self.WriteStatus('AudioLevel', Left, {'L/R':'Left'})
        self.WriteStatus('AudioLevel', Right, {'L/R':'Right'})

    def SetAudioMute(self, value, qualifier):

        Chan = {
            'Analog audio left' : '0', 
            'Analog audio right': '1',
            'HDMI audio left'   : '2',
            'HDMI audio right'  : '3',
        }
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        AudioMuteCmdString = 'wM4000{0}*{1}AU\r'.format(Chan[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        
        Chan = {
            'Analog audio left' : '0', 
            'Analog audio right': '1',
            'HDMI audio left'   : '2',
            'HDMI audio right'  : '3',
        }

        AudioMuteCmdString = 'wM4000{0}AU\r'.format(Chan[qualifier['Channel']])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Chan = {
            '0': 'Analog audio left', 
            '1': 'Analog audio right',
            '2': 'HDMI audio left',
            '3': 'HDMI audio right',
        }

        State = {
            '1':'On', 
            '0':'Off'
        }
        qualifier = {'Channel' : Chan[match.group(1).decode()]}

        value = State[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetOutputAudioMute(self, value, qualifier):

        LRStates = {
            'Left'  : '0', 
            'Right' : '1'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        OutputAudioMuteCmdString = 'wM6000{0}*{1}AU\r'.format(LRStates[qualifier['L/R']],ValueStateValues[value])
        self.__SetHelper('OutputAudioMute', OutputAudioMuteCmdString, value, qualifier)

    def UpdateOutputAudioMute(self, value, qualifier):

        LRStates = {
            'Left' : '0', 
            'Right' : '1'
        }
        OutputAudioMuteCmdString = 'wM6000{0}AU\r'.format(LRStates[qualifier['L/R']])
        self.__UpdateHelper('OutputAudioMute', OutputAudioMuteCmdString, value, qualifier)

    def __MatchOutputAudioMute(self, match, tag):

        LRStates = {
            '0':'Left', 
            '1':'Right'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {'L/R' : LRStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputAudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier): 

        ValueStateValues = {
            'Execute' : 'A',
            'Execute and fill' : '1*A',
            'Execute and follow' : '2*A',
        }

        CmdString = '{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetBitRateControlType(self, value, qualifier):

        ValueStateValues = {
            'VBR'  : '0', 
            'CVBR' : '1', 
            'CBR'  : '2'
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            BitRateControlTypeCmdString ='w{0}*{1}BRCT\r'.format(encoder, ValueStateValues[value])
            self.__SetHelper('BitRateControlType', BitRateControlTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBitRateControlType')

    def UpdateBitRateControlType(self, value, qualifier):

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            BitRateControlTypeCmdString = 'w{0}BRCT\r'.format(encoder)
            self.__UpdateHelper('BitRateControlType', BitRateControlTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBitRateControlType')

    def __MatchBitRateControlType(self, match, tag):

        ValueStateValues = {
            '0' : 'VBR', 
            '1' : 'CVBR', 
            '2' : 'CBR'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BitRateControlType', value, {'Encoder': match.group(1).decode()})

    def SetClearActiveAlarms(self, value, qualifier):

        ClearActiveAlarmsCmdString = '\x1BCALRM\r'
        self.__SetHelper('ClearActiveAlarms', ClearActiveAlarmsCmdString, value, qualifier)
    def UpdateCPUUsage(self, value, qualifier):

        CPUUsageCmdString = '11i'
        self.__UpdateHelper('CPUUsage', CPUUsageCmdString, value, qualifier)

    def __MatchCPUUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CPUUsage', value, None)

    def SetEDID(self, value, qualifier):

        ValueStateValues = {
            '800x600 60HZ PC DVI' : '1', 
            '1024x768 60HZ PC DVI' : '2', 
            '1280x720 60HZ PC DVI' : '3', 
            '1280x768 60HZ PC DVI' : '4', 
            '1280x800 60HZ PC DVI' : '5', 
            '1280x1024 60HZ PC DVI' : '6', 
            '1360x768 60HZ PC DVI' : '7', 
            '1366x768 60HZ PC DVI' : '8', 
            '1400x1050 60HZ PC DVI' : '9', 
            '1440x900 60HZ PC DVI' : '10', 
            '1600x900 60HZ PC DVI' : '11', 
            '1600x1200 60HZ PC DVI' : '12', 
            '1680x1050 60HZ PC DVI' : '13', 
            '1920x1080 60HZ PC DVI' : '14', 
            '1920x1200 60HZ PC DVI' : '15', 
            '800x600 60HZ PC HDMI' : '16', 
            '1024x768 60HZ PC HDMI' : '17', 
            '1280x768 60HZ PC HDMI' : '18', 
            '1280x800 60HZ PC HDMI' : '19', 
            '1280x1024 60HZ PC HDMI' : '20', 
            '1360x768 60HZ PC HDMI' : '21', 
            '1366x768 60HZ PC HDMI' : '22', 
            '1400x1050 60HZ PC HDMI' : '23', 
            '1440x900 60HZ PC HDMI' : '24', 
            '1600x900 60HZ PC HDMI' : '25', 
            '1600x1200 60HZ PC HDMI' : '26', 
            '1680x1050 60HZ PC HDMI' : '27', 
            '1920x1200 60HZ PC HDMI' : '28', 
            '480p 60HZ HDTV HDMI' : '29', 
            '576p 50HZ HDTV HDMI' : '30', 
            '720p 50HZ HDTV HDMI' : '31', 
            '720p 60HZ HDTV HDMI' : '32', 
            '1080i 50HZ HDTV HDMI' : '33', 
            '1080i 60HZ HDTV HDMI' : '34', 
            '1080p 50/25HZ HDTV HDMI' : '35', 
            '1080p 50HZ HDTV HDMI' : '36', 
            '1080p 60/24HZ HDTV HDMI' : '37', 
            '1080p 60HZ HDTV HDMI' : '38', 
            'User Loaded Slot 1': '39',
            'User Loaded Slot 2': '40',
            'User Loaded Slot 3': '41',
        }

        EDIDCmdString = 'wA{0}EDID\r'.format(ValueStateValues[value])
        self.__SetHelper('EDID', EDIDCmdString, value, qualifier)

    def UpdateEDID(self, value, qualifier):

        EDIDCmdString = 'wAEDID\r'
        self.__UpdateHelper('EDID', EDIDCmdString, value, qualifier)

    def __MatchEDID(self, match, tag):

        ValueStateValues = {
            '01' : '800x600 60HZ PC DVI', 
            '02' : '1024x768 60HZ PC DVI', 
            '03' : '1280x720 60HZ PC DVI', 
            '04' : '1280x768 60HZ PC DVI', 
            '05' : '1280x800 60HZ PC DVI', 
            '06' : '1280x1024 60HZ PC DVI', 
            '07' : '1360x768 60HZ PC DVI', 
            '08' : '1366x768 60HZ PC DVI', 
            '09' : '1400x1050 60HZ PC DVI', 
            '10' : '1440x900 60HZ PC DVI', 
            '11' : '1600x900 60HZ PC DVI', 
            '12' : '1600x1200 60HZ PC DVI', 
            '13' : '1680x1050 60HZ PC DVI', 
            '14' : '1920x1080 60HZ PC DVI', 
            '15' : '1920x1200 60HZ PC DVI',
            '16' : '800x600 60HZ PC HDMI', 
            '17' : '1024x768 60HZ PC HDMI', 
            '18' : '1280x768 60HZ PC HDMI', 
            '19' : '1280x800 60HZ PC HDMI', 
            '20' : '1280x1024 60HZ PC HDMI', 
            '21' : '1360x768 60HZ PC HDMI', 
            '22' : '1366x768 60HZ PC HDMI', 
            '23' : '1400x1050 60HZ PC HDMI', 
            '24' : '1440x900 60HZ PC HDMI', 
            '25' : '1600x900 60HZ PC HDMI', 
            '26' : '1600x1200 60HZ PC HDMI', 
            '27' : '1680x1050 60HZ PC HDMI', 
            '28' : '1920x1200 60HZ PC HDMI',
            '29' : '480p 60HZ HDTV HDMI', 
            '30' : '576p 50HZ HDTV HDMI', 
            '31' : '720p 50HZ HDTV HDMI', 
            '32' : '720p 60HZ HDTV HDMI', 
            '33' : '1080i 50HZ HDTV HDMI', 
            '34' : '1080i 60HZ HDTV HDMI', 
            '35' : '1080p 50/25HZ HDTV HDMI', 
            '36' : '1080p 50HZ HDTV HDMI', 
            '37' : '1080p 60/24HZ HDTV HDMI', 
            '38' : '1080p 60HZ HDTV HDMI', 
            '39': 'User Loaded Slot 1',
            '40': 'User Loaded Slot 2',
            '41': 'User Loaded Slot 3',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EDID', value, None)

    def SetEncodeProfile(self, value, qualifier):

        EncoderProfileName = {
               'Base' : 1,
               'Main' : 2,
               'High' : 3
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            EncoderProfileString = 'w{0}*{1}EPRO\r'.format(encoder, EncoderProfileName[value])
            self.__SetHelper('EncodeProfile', EncoderProfileString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEncodeProfile') 

    def UpdateEncodeProfile(self, value, qualifier):

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            EncoderProfileString = 'w{0}EPRO\r'.format(encoder)
            self.__UpdateHelper('EncodeProfile', EncoderProfileString, value, qualifier) 
        else:
            self.Discard('Invalid Command for UpdateEncodeProfile')

    def __MatchEncodeProfile(self, match, tag):

        EncoderProfileNames = {
               1 : 'Base',
               2 : 'Main',
               3 : 'High'
        }
        Chan = match.group(1).decode()
        qualifier = {'Encoder': Chan} 
        value = int(match.group(2))
        self.WriteStatus('EncodeProfile', EncoderProfileNames[value], qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0', 
            'On'  : '1' 
        }

        ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        CmdString = 'X'   
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier) 

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGOPLength(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 30
        }

        encoder = qualifier['Encoder']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(encoder) <= 2:
            GOPLengthCmdString = 'w{0}*{1}GOPL\r'.format(encoder, value)
            self.__SetHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGOPLength')

    def UpdateGOPLength(self, value, qualifier):

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            GOPLengthCmdString = 'w{0}GOPL\r'.format(encoder)
            self.__UpdateHelper('GOPLength', GOPLengthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGOPLength')

    def __MatchGOPLength(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('GOPLength', value, {'Encoder': match.group(1).decode()})

    def UpdateHDCPStatus(self, value, qualifier):

        HDCPStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPStatus', HDCPStatusCmdString, value, qualifier)

    def __MatchHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Detected', 
            '1' : 'HDCP Detected', 
            '2' : 'No HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPStatus', value,None)

    def SetMetadata(self, value, qualifier):

        TypeStateValues = {
            'Contributor' : '0', 
            'Coverage'    : '1', 
            'Creator'     : '2', 
            'Date'        : '3', 
            'Description' : '4', 
            'Format'      : '5', 
            'Identifier'  : '6', 
            'Language'    : '7', 
            'Publisher'   : '8', 
            'Course ID'    : '9', 
            'Rights'      : '10', 
            'Source'      : '11', 
            'Subject'     : '12', 
            'Title'       : '13', 
            'Type'        : '14', 
            'System Name' : '15', 
            'Course Name' : '16',
            'License' : '17',
            'Relation' : '18',
            'Location' : '19',
        }

        MetaString= qualifier['Metadata']
        if MetaString:
            MetadataCmdString = 'wM{0}*{1}STRM\r'.format(TypeStateValues[value],MetaString)
            self.__SetHelper('Metadata', MetadataCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMetadata')

    def UpdateMetadataStatus(self, value, qualifier):

        TypeStateValues = {
            'Contributor' : '0', 
            'Coverage'    : '1', 
            'Creator'     : '2', 
            'Date'        : '3', 
            'Description' : '4', 
            'Format'      : '5', 
            'Identifier'  : '6', 
            'Language'    : '7', 
            'Publisher'   : '8', 
            'Course ID'    : '9', 
            'Rights'      : '10', 
            'Source'      : '11', 
            'Subject'     : '12', 
            'Title'       : '13', 
            'Type'        : '14', 
            'System Name' : '15', 
            'Course Name' : '16',
            'License' : '17',
            'Relation' : '18',
            'Location' : '19',
        }

        MetadataStatusCmdString = 'wM{0}STRM\r'.format(TypeStateValues[qualifier['Type']])
        res = self.__UpdateSyncHelper('MetadataStatus', MetadataStatusCmdString, value, qualifier)
        if res:
            values = re.search(self.MetadataStatusRegex, res)
            try:
                if values.group(1):
                    self.WriteStatus('MetadataStatus', values.group(1), qualifier)
                else:
                    self.WriteStatus('MetadataStatus', 'No Information', qualifier)
            except AttributeError:
                self.Error(['Metadata Status: Invalid/unexpected response'])

    def __MatchMetadataStatus(self, match, tag):
        
        typeStates = {
            '0' : 'Contributor',
            '1' : 'Coverage',
            '2' : 'Creator',
            '3' : 'Date', 
            '4' : 'Description',
            '5' : 'Format', 
            '6' : 'Identifier', 
            '7' : 'Language', 
            '8' : 'Publisher', 
            '9' : 'Course ID', 
            '10': 'Rights', 
            '11': 'Source', 
            '12': 'Subject', 
            '13': 'Title', 
            '14': 'Type', 
            '15': 'System Name', 
            '16': 'Course Name',
            '17': 'License',
            '18': 'Relation',
            '19': 'Location'
        }

        typeVal = typeStates[match.group(1).decode()]
        value = match.group(2).decode()
        self.WriteStatus('MetadataStatus', value, {'Type': typeVal})
                
    def SetRecallInputPreset(self, value, qualifier): 

        if 1 <= int(value) <= 128:
            CmdString = '2*{0}.'.format(value)
            self.__SetHelper('RecallInputPreset', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetRecallInputPreset')

    def SetRecallEncoderPreset(self, value, qualifier): 

        encoder = qualifier['Encoder']
        if 1 <= int(value) <= 64 and 1 <= int(encoder) <= 2:
            CmdString = '4*{0}*{1}.'.format(encoder, value)
            self.__SetHelper('RecallEncoderPreset', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetRecallEncoderPreset')

    def SetMetadataProfiles(self, value, qualifier):

        ValueStateValues = {
            '1' : '01', 
            '2' : '02', 
            '3' : '03', 
            '4' : '04', 
            '5' : '05', 
            '6' : '06', 
            '7' : '07', 
            '8' : '08', 
            '9' : '09', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16'
        }

        MetadataProfilesCmdString = '\x1BR5*{0}PRST\r'.format(ValueStateValues[value])
        self.__SetHelper('MetadataProfiles', MetadataProfilesCmdString, value, qualifier)

    def UpdateMetadataProfiles(self, value, qualifier):

        MetadataProfilesCmdString = '\x1BL5PRST\r'
        self.__UpdateHelper('MetadataProfiles', MetadataProfilesCmdString, value, qualifier)

    def __MatchMetadataProfiles(self, match, tag):

        ValueStateValues = {
            '00' : 'No Profile',
            '01' : '1', 
            '02' : '2', 
            '03' : '3', 
            '04' : '4', 
            '05' : '5', 
            '06' : '6', 
            '07' : '7', 
            '08' : '8', 
            '09' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MetadataProfiles', value, None)

    def SetVideoFrameRate(self, value, qualifier):

        State = {
            '30 fps'    : '1',  
            '25 fps'    : '2',
            '24 fps'    : '3', 
            '15 fps'    : '4',  
            '12.5 fps'  : '5',
            '12 fps'    : '6',
            '10 fps'    : '7',
            '5 fps'     : '8' 
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:    
            CmdString = 'w{0}*{1}VFRM\r'.format(encoder, State[value])
            self.__SetHelper('VideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoFrameRate')

    def UpdateVideoFrameRate(self, value, qualifier):
   
        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            CmdString = 'w{0}VFRM\r'.format(encoder) 
            self.__UpdateHelper('VideoFrameRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoFrameRate')
      
    def __MatchVideoFrameRate(self, match, tag):

        State = {
            '1':'30 fps',  
            '2':'25 fps',
            '3':'24 fps', 
            '4':'15 fps',  
            '5':'12.5 fps',
            '6':'12 fps',
            '7':'10 fps',
            '8':'5 fps'
        } 

        value = State[match.group(2).decode()]
        self.WriteStatus('VideoFrameRate', value, {'Encoder': match.group(1).decode()})

    def SetVideoEncodingResolution(self, value, qualifier):

        ValueStateValues = {
            '512x288' : '0', 
            '480p' : '1', 
            '720p' : '2',
            '1080p' : '3',
            '1024x768' : '4',
            '1280x1024' : '5' 
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            VideoEncodingResolutionCmdString = 'w{0}*{1}VRES\r'.format(encoder, ValueStateValues[value])
            self.__SetHelper('VideoEncodingResolution', VideoEncodingResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoEncodingResolution')

    def UpdateVideoEncodingResolution(self, value, qualifier):


        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            VideoEncodingResolutionCmdString = 'w{0}VRES\r'.format(encoder)
            self.__UpdateHelper('VideoEncodingResolution', VideoEncodingResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoEncodingResolution')

    def __MatchVideoEncodingResolution(self, match, tag):

        ValueStateValues = {
            '0': '512x288', 
            '1': '480p', 
            '2': '720p',
            '3': '1080p',
            '4': '1024x768',
            '5': '1280x1024' 
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoEncodingResolution', value, {'Encoder': match.group(1).decode()})

    def SetRTMPPrimaryDestination(self, value, qualifier):

        RTMPString = qualifier['Primary Destination URL']
        if RTMPString:
            RTMPCmdString = 'wU1*{0}RTMP\r'.format(RTMPString)
            self.__SetHelper('RTMPPrimaryDestination', RTMPCmdString, value, qualifier)

    def UpdateRTMPPrimaryDestinationURLStatus(self, value, qualifier):

        RTMPPrimaryDestinationURLStatusCmdString = 'wU1RTMP\r'
        self.__UpdateHelper('RTMPPrimaryDestinationURLStatus', RTMPPrimaryDestinationURLStatusCmdString, value, qualifier)

    def __MatchRTMPPrimaryDestinationURLStatus(self, match, tag):

        value = match.group(1).decode()
        if value:
            self.WriteStatus('RTMPPrimaryDestinationURLStatus', value, None)
        else:
            self.WriteStatus('RTMPPrimaryDestinationURLStatus', 'RTMP Destination Not Configured', None)

    def SetRTMPStream(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1', 
            'Disable' : '0'
        }

        RTMPStreamCmdString = 'wE1*{0}RTMP\r'.format(ValueStateValues[value])
        self.__SetHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)

    def UpdateRTMPStream(self, value, qualifier):

        RTMPStreamCmdString = 'wE1RTMP\r'
        self.__UpdateHelper('RTMPStream', RTMPStreamCmdString, value, qualifier)

    def __MatchRTMPStream(self, match, tag):

        ValueStateValues = {
            '1' : 'Enable', 
            '0' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RTMPStream', value, None)

    def SetStreamingControls(self, value, qualifier):

        States = {
            'Start' : 'wY1STRM\r', 
            'Stop'  : 'wY0STRM\r', 
            'Pause' : 'wY2STRM\r'
        }

        self.__SetHelper('StreamingControls', States[value] , value, qualifier)

    def UpdateStreamingControls(self, value, qualifier):
        self.__UpdateHelper('StreamingControls', 'wYSTRM\r', value, qualifier)

    def __MatchStreamingControls(self, match, tag):

        States = {
            '0' : 'Stop',
            '1' : 'Start', 
            '2' : 'Pause',
            '3' : 'Start',
        }

        self.WriteStatus('StreamingControls',  States[match.group(2).decode()] , None)

    def UpdateStreamingPresetName(self, value, qualifier):

        PresetState = {
            'RSTP': '6',
            'UDP-RTP': '7',
            'RTMP': '8',
            }

        preset = qualifier['Preset']
        if 1 <= int(preset) <= 16:
            StreamingPresetNameCmdString = '\x1B{0}*{1}PNAM\r'.format(PresetState[qualifier['Type']], preset)
            res = self.__UpdateSyncHelper('StreamingPresetName', StreamingPresetNameCmdString, value, qualifier)
            if res:
                try:
                    values = res[8:-2]
                    self.WriteStatus('StreamingPresetName', values, qualifier)
                except IndexError:
                    self.Error(['Streaming Preset Name: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStreamingPresetName')

    def SetRecallStreamingPreset(self, value, qualifier):

        PresetState = {
            'RSTP': '6',
            'UDP-RTP': '7',
            'RTMP': '8',
            }

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16'
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            StreamingPresetRecallCmdString = '\x1bR{1}*{0}*{2}PRST\r\n'.format(encoder, PresetState[qualifier['Type']], ValueStateValues[value])
            self.__SetHelper('StreamingPresetRecall', StreamingPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallStreamingPreset')

    def SetSaveInputPreset(self, value, qualifier):

        if 1 <= int(value) <= 128:
            CmdString = '2*{0},'.format(value)
            self.__SetHelper('SaveInputPreset', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetSaveInputPreset')

    def SetSaveEncoderPreset(self, value, qualifier): 

        encoder = qualifier['Encoder']
        if 1 <= int(value) <= 64 and 1 <= int(encoder) <= 2:
            CmdString = '4*{0}*{1},'.format(encoder, value)
            self.__SetHelper('SaveEncoderPreset', CmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetSaveEncoderPreset')

    def SetStreamingPresetSave(self, value, qualifier):

        PresetState = {
            'RSTP': '6',
            'UDP-RTP': '7',
            'RTMP': '8',
            }

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16'
        }

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            StreamingPresetSaveCmdString = '\x1bS{1}*{0}*{2}PRST\r\n'.format(encoder, PresetState[qualifier['Type']], ValueStateValues[value])
            self.__SetHelper('StreamingPresetSave', StreamingPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingPresetSave')

    def SetVideoBitRate(self, value, qualifier):

        ValueConstraints = {
            'Min' : 2000,
            'Max' : 25000
        }

        encoder = qualifier['Encoder']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(encoder) <= 2:
            VideoBitRateCmdString = 'wV{0}*{1}BITR\r'.format(encoder, value)
            self.__SetHelper('VideoBitRate', VideoBitRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoBitRate')

    def UpdateVideoBitRate(self, value, qualifier):

        encoder = qualifier['Encoder']
        if 1 <= int(encoder) <= 2:
            VideoBitRateCmdString = 'wV{0}BITR\r'.format(encoder)
            self.__UpdateHelper('VideoBitRate', VideoBitRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoBitRate')

    def __MatchVideoBitRate(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('VideoBitRate', value, {'Encoder' : match.group(1).decode()})

    def SetVideoMute(self, value, qualifier): 

        State = {
            'On'   : '1',  
            'Off'  : '0',
        }

        CmdString = '{0}B'.format(State[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)  

    def UpdateVideoMute(self, value, qualifier):  

        CmdString = 'B'
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)   
      
    def __MatchVideoMute(self, match, tag):

        State = {
            '0':'Off',  
            '1':'On',
        }

        self.WriteStatus('VideoMute', State[match.group(1).decode()], None)

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

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __UpdateSyncHelper(self, command, commandstring, value, qualifier):
        
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
            return ''            
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                res = res.decode()
                if res[0] == 'E':
                    self.__MatchErrors(res, 'Sync')
                    return ''
                else:
                    return res

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Command not available for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid event number',
            '28' : 'Bad filename or file not found',
            '30' : 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31' : 'Attempt to break port pass-through when it has not been set',
            '32' : 'Incorrect V-chip password'
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
        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
        self.VerboseDisabled = True
        
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
            print(command, 'does not exist in the module')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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

