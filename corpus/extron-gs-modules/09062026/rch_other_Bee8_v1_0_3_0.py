from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog
from struct import pack

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
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CaptureMode': {'Status': {}},
            'Line': {'Status': {}},
            'MediaStatus': {'Status': {}},
            'Microphone': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Recording': {'Status': {}},
            'Resolution': {'Status': {}},
            'SingleChannelFullScreenSwitch': {'Status': {}},
            'VideoBitRate': {'Status': {}}
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'mode:(0|1)'), self.__MatchCaptureMode, None)
            self.AddMatchString(re.compile(b'line:(0|1)'), self.__MatchLine, None)
            self.AddMatchString(re.compile(b'media center status:(0|1)'), self.__MatchMediaStatus, None)
            self.AddMatchString(re.compile(b'mic:(0|1)'), self.__MatchMicrophone, None)
            self.AddMatchString(re.compile(b'(vga resolution|resolution):(720x480|704x576|1024x768|1024x720|1280x720|1280x800|1280x1024|1366x768|1400x1050|1440x900|1920x1080)'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'layoutid:(10|21|22|23|24|25|26|31|32)'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'record state:(stopped|recording|paused)'), self.__MatchRecording, None)
            self.AddMatchString(re.compile(b'bitrate:(768|1024|2048|4096)kbps'), self.__MatchVideoBitRate, None)
            self.AddMatchString(re.compile(b'operate failed'), self.__MatchError, None)

    def SetCaptureMode(self, value, qualifier):

        States = {
            'Self': 0x02,
            'Force On': 0x01
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x25, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('CaptureMode', CmdString, value, qualifier)

    def UpdateCaptureMode(self, value, qualifier):
        self.__UpdateHelper('CaptureMode', b'\x3c\x3c\xc2\x41\x00\x3e\x3e', value, qualifier)

    def __MatchCaptureMode(self, match, tag):

        States = {
            '0': 'Self',
            '1': 'Force On'
        }

        self.WriteStatus('CaptureMode', States[match.group(1).decode()], None)

    def SetLine(self, value, qualifier):

        States = {
            'On': 0x01,
            'Off': 0x00
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x21, 0x01, States[value], 0x3e, 0x3e)
        self.__SetHelper('Line', CmdString, value, qualifier)

    def UpdateLine(self, value, qualifier):
        self.__UpdateHelper('Line', b'\x3c\x3c\xc2\x31\x00\x00\x3e\x3e', value, qualifier)

    def __MatchLine(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Line', States[match.group(1).decode()], None)

    def UpdateMediaStatus(self, value, qualifier):

        self.__UpdateHelper('MediaStatus', b'\x3c\x3c\xc2\x40\x00\x3e\x3e', value, qualifier)

    def __MatchMediaStatus(self, match, tag):

        States = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        self.WriteStatus('MediaStatus', States[match.group(1).decode()], None)

    def SetMicrophone(self, value, qualifier):

        States = {
            'On': 0x01,
            'Off': 0x00
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x21, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('Microphone', CmdString, value, qualifier)

    def UpdateMicrophone(self, value, qualifier):
        self.__UpdateHelper('Microphone', b'\x3c\x3c\xc2\x31\x00\x00\x3e\x3e', value, qualifier)

    def __MatchMicrophone(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Microphone', States[match.group(1).decode()], None)

    def SetOutputResolution(self, value, qualifier):

        States = {
            '1024x768': 0x07,
            '1280x720': 0x06,
            '1280x800': 0x05,
            '1280x1024': 0x04,
            '1366x768': 0x03,
            '1400x1050': 0x02,
            '1440x900': 0x01,
            '1920x1080': 0x08,
        }

        CmdString = pack('>7B', 0x3c, 0x3c, 0xc2, 0x36, States[value], 0x3e, 0x3e)
        self.__SetHelper('OutputResolution', CmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):
        self.__UpdateHelper('OutputResolution', b'\x3c\x3c\xc2\x37\x00\x3e\x3e', value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        OutputResStateValues = {
            '1024x768': '1024x768',
            '1280x720': '1280x720',
            '1280x800': '1280x800',
            '1280x1024': '1280x1024',
            '1366x768': '1366x768',
            '1400x1050': '1400x1050',
            '1440x900': '1440x900',
            '1920x1080': '1920x1080'
        }

        ResStateValues = {
            '720x480': '720x480',
            '704x576': '704x576',
            '1024x720': '1024x720',
            '1920x1080': '1920x1080'
        }

        type_ = match.group(1).decode()
        if type_.find('vga') == 0:
            self.WriteStatus('OutputResolution', OutputResStateValues[match.group(2).decode()], None)
        elif type_.find('vga') == -1:
            self.WriteStatus('Resolution', ResStateValues[match.group(2).decode()], None)

    def SetPIP(self, value, qualifier):

        States = {
            '2 Picture': 0x15,
            '2 Picture Side By Side': 0x16,
            'Upper Left': 0x17,
            'Upper Right': 0x18,
            'Bottom Left': 0x19,
            'Bottom Right': 0x1A,
            '3 Picture': 0x1F,
            '3 Picture Side By Side': 0x20,
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x10, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('PIP', CmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):
        self.__UpdateHelper('PIP', b'\x3c\x3c\xc2\x38\x00\x00\x3e\x3e', value, qualifier)

    def __MatchPIP(self, match, tag):

        States = {
            '21': '2 Picture',
            '22': '2 Picture Side By Side',
            '23': 'Upper Left',
            '24': 'Upper Right',
            '25': 'Bottom Left',
            '26': 'Bottom Right',
            '31': '3 Picture',
            '32': '3 Picture Side By Side',
            '10': 'Off'
        }

        self.WriteStatus('PIP', States[match.group(1).decode()], None)

    def SetPIPSwap(self, value, qualifier):
        self.__SetHelper('PIPSwap', b'\x3c\x3c\xc2\x11\x00\x01\x3e\x3e', value, qualifier)

    def SetRecording(self, value, qualifier):

        States = {
            'Start': 0x01,
            'Pause': 0x02,
            'Stop': 0x03,
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x80, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('Recording', CmdString, value, qualifier)

    def UpdateRecording(self, value, qualifier):
        self.__UpdateHelper('Recording', b'\x3c\x3c\xc2\x39\x00\x3e\x3e', value, qualifier)

    def __MatchRecording(self, match, tag):

        States = {
            'recording': 'Start',
            'stopped': 'Stop',
            'paused': 'Pause'
        }

        self.WriteStatus('Recording', States[match.group(1).decode()], None)

    def SetResolution(self, value, qualifier):

        States = {
            '720x480': 0x01,
            '704x576': 0x02,
            '1024x720': 0x03,
            '1920x1080': 0x04,
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x85, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('Resolution', CmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):
        self.__UpdateHelper('Resolution', b'\x3c\x3c\xc2\x30\x00\x00\x3e\x3e', value, qualifier)
        
    def SetSingleChannelFullScreenSwitch(self, value, qualifier):
        States = {
            'All'               : 0x00, 
            'First Channel'     : 0x01, 
            'Second Channel'    : 0x02, 
            'Third Channel'     : 0x03
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x12, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('SingleChannelFullScreenSwitch', CmdString, value, qualifier)

    def SetVideoBitRate(self, value, qualifier):

        States = {
            '768': 0x01,
            '1024': 0x02,
            '2048': 0x03,
            '4096': 0x04,
        }

        CmdString = pack('>8B', 0x3c, 0x3c, 0xc2, 0x15, 0x00, States[value], 0x3e, 0x3e)
        self.__SetHelper('VideoBitRate', CmdString, value, qualifier)

    def UpdateVideoBitRate(self, value, qualifier):
        self.__UpdateHelper('VideoBitRate', b'\x3c\x3c\xc2\x16\x00\x00\x3e\x3e', value, qualifier)

    def __MatchVideoBitRate(self, match, tag):

        States = {
            '768': '768',
            '1024': '1024',
            '2048': '2048',
            '4096': '4096'
        }

        self.WriteStatus('VideoBitRate', States[match.group(1).decode()], None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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
        print('Command operation has failed')

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
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        
        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CaptureMode': {'Status': {}},
            'Line': {'Status': {}},
            'MediaStatus': {'Status': {}},
            'Microphone': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Recording': {'Status': {}},
            'RecordVideo': {'Parameters': ['Bit Rate'], 'Status': {}},
            'SingleChannelFullScreenSwitch': {'Status': {}},
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'mode:(0|1)'), self.__MatchCaptureMode, None)
            self.AddMatchString(re.compile(b'line:(0|1)'), self.__MatchLine, None)
            self.AddMatchString(re.compile(b'status:(0|1)'), self.__MatchMediaStatus, None)
            self.AddMatchString(re.compile(b'record state:(recording|pause|stop)'), self.__MatchRecording, None)
            self.AddMatchString(re.compile(b'mic:(0|1)'), self.__MatchMicrophone, None)
            self.AddMatchString(re.compile(b'(video bitrate:(768|1024|2048|4096)kbps\rvideo\\sresolution:(720x480|704x576|1280x720|1920x1080)|resolution:(1024x768|1280x720|1280x800|1280x1024|1366x768|1400x1050|1440x900|1920x1080))'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(b'layoutid:(10|21|22|23|24|25|26|31|32)'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'Username|username'), self.__MatchLoginAdmin, None)
            self.AddMatchString(re.compile(b'Password|password'), self.__MatchLoginPass, None)
            self.AddMatchString(re.compile(b'choice'), self.__MatchVGARes, None)
            self.AddMatchString(re.compile(b'operate failed'), self.__MatchError, None)

    def __MatchLoginAdmin(self, match, tag):
        self.SetUsername(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchLoginPass(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchVGARes(self, match, tag):
        self.SetVGARes(None, None)

    def SetVGARes(self, value, qualifier):
        self.Send('tnrc setvgaresolution yes\r')

    def __MatchResolution(self, match, tag):

        result = match.group(1).decode()
        if result.find('video') == 0:
            self.__MatchRecordVideo(result, None)
        elif result.find('video') == -1:
            self.__MatchOutputResolution(result, None)

    def SetCaptureMode(self, value, qualifier):

        States = {
            'Self': 'tnrc setvideomode mode:0',
            'Force On': 'tnrc setvideomode mode:1'
        }

        self.__SetHelper('CaptureMode', States[value], value, qualifier)

    def UpdateCaptureMode(self, value, qualifier):
        self.__UpdateHelper('CaptureMode', 'tnrc getvideomode', value, qualifier)

    def __MatchCaptureMode(self, match, tag):

        States = {
            '0': 'Self',
            '1': 'Force On'
        }

        self.WriteStatus('CaptureMode', States[match.group(1).decode()], None)

    def SetLine(self, value, qualifier):

        States = {
            'On': 'tnrc setaudioinput line:1 mic:0',
            'Off': 'tnrc setaudioinput line:0 mic:0',
        }

        self.__SetHelper('Line', States[value], value, qualifier)

    def UpdateLine(self, value, qualifier):
        self.__UpdateHelper('Line', 'tnrc getaudiosource', value, qualifier)

    def __MatchLine(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Line', States[match.group(1).decode()], None)

    def UpdateMediaStatus(self, value, qualifier):

        self.__UpdateHelper('MediaStatus', 'tnrc getmediastatus', value, qualifier)

    def __MatchMediaStatus(self, match, tag):

        States = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        self.WriteStatus('MediaStatus', States[match.group(1).decode()], None)

    def SetMicrophone(self, value, qualifier):

        States = {
            'On': 'tnrc setaudioinput line:0 mic:1',
            'Off': 'tnrc setaudioinput line:0 mic:0',
        }

        self.__SetHelper('Microphone', States[value], value, qualifier)

    def UpdateMicrophone(self, value, qualifier):
        self.__UpdateHelper('Microphone', 'tnrc getaudiosource', value, qualifier)

    def __MatchMicrophone(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Microphone', States[match.group(1).decode()], None)

    def SetOutputResolution(self, value, qualifier):

        States = {
            '1024x768': 'tnrc setvgaresolution index:7',
            '1280x720': 'tnrc setvgaresolution index:6',
            '1280x800': 'tnrc setvgaresolution index:5',
            '1280x1024': 'tnrc setvgaresolution index:4',
            '1366x768': 'tnrc setvgaresolution index:3',
            '1400x1050': 'tnrc setvgaresolution index:2',
            '1440x900': 'tnrc setvgaresolution index:1',
            '1920x1080': 'tnrc setvgaresolution index:8'
        }

        self.__SetHelper('OutputResolution', States[value], value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):
        self.__UpdateHelper('OutputResolution', 'tnrc getvgaresolution', value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        States = {
            '1024x768': '1024x768',
            '1280x720': '1280x720',
            '1280x800': '1280x800',
            '1280x1024': '1280x1024',
            '1366x768': '1366x768',
            '1400x1050': '1400x1050',
            '1440x900': '1440x900',
            '1920x1080': '1920x1080'
        }

        resolution = re.search('resolution:(1024x768|1280x720|1280x800|1280x1024|1366x768|1400x1050|1440x900|1920x1080)', match)
        value = States[resolution.group(1)]
        self.WriteStatus('OutputResolution', value, None)

    def SetPIP(self, value, qualifier):

        States = {
            '2 Picture': 'tnrc setlayout id:21',
            '2 Picture Side By Side': 'tnrc setlayout id:22',
            'Upper Left': 'tnrc setlayout id:23',
            'Upper Right': 'tnrc setlayout id:24',
            'Bottom Left': 'tnrc setlayout id:25',
            'Bottom Right': 'tnrc setlayout id:26',
            '3 Picture': 'tnrc setlayout id:31',
            '3 Picture Side By Side': 'tnrc setlayout id:32',
        }

        self.__SetHelper('PIP', States[value], value, qualifier)

    def UpdatePIP(self, value, qualifier):
        self.__UpdateHelper('PIP', 'tnrc getlayout', value, qualifier)

    def __MatchPIP(self, match, tag):

        States = {
            '21': '2 Picture',
            '22': '2 Picture Side By Side',
            '23': 'Upper Left',
            '24': 'Upper Right',
            '25': 'Bottom Left',
            '26': 'Bottom Right',
            '31': '3 Picture',
            '32': '3 Picture Side By Side',
            '10': 'Off'
        }

        self.WriteStatus('PIP', States[match.group(1).decode()], None)

    def SetPIPSwap(self, value, qualifier):
        self.__SetHelper('PIPSwap', 'tnrc switch', value, qualifier)

    def SetRecording(self, value, qualifier):

        States = {
            'Start': 'tnrc record bRecord:1',
            'Stop': 'tnrc record bRecord:0',
            'Pause': 'tnrc record bRecord:2'
        }

        self.__SetHelper('Recording', States[value], value, qualifier)

    def UpdateRecording(self, value, qualifier):
        self.__UpdateHelper('Recording', 'tnrc getrecordstate', value, qualifier)

    def __MatchRecording(self, match, tag):

        States = {
            'recording': 'Start',
            'stop': 'Stop',
            'pause': 'Pause'
        }

        self.WriteStatus('Recording', States[match.group(1).decode()], None)

    def SetRecordVideo(self, value, qualifier):

        BitRates = {
            '768': '1',
            '1024': '2',
            '2048': '3',
            '4096': '4'
        }

        Resolutions = {
            '720x480': '1',
            '704x576': '2',
            '1280x720': '3',
            '1920x1080': '4'
        }

        CmdString = 'tnrc setrecordparameter vbitrate:{0} resolution:{1}'.format(BitRates[qualifier['Bit Rate']], Resolutions[value])
        self.__SetHelper('RecordVideo', CmdString, value, qualifier)

    def UpdateRecordVideo(self, value, qualifier):
        self.__UpdateHelper('RecordVideo', 'tnrc getrecordparameter', value, qualifier)

    def __MatchRecordVideo(self, match, tag):

        BitRates = {
            '768': '768',
            '1024': '1024',
            '2048': '2048',
            '4096': '4096'
        }

        Resolutions = {
            '720x480': '720x480',
            '704x576': '704x576',
            '1280x720': '1280x720',
            '1920x1080': '1920x1080'
        }

        result = re.search('video bitrate:(768|1024|2048|4096)kbps\rvideo\sresolution:(720x480|704x576|1280x720|1920x1080)', match)
        self.WriteStatus('RecordVideo', Resolutions[result.group(2)], {'Bit Rate': BitRates[result.group(1)]})
        
    def SetSingleChannelFullScreenSwitch(self, value, qualifier):
        States = {
            'All'               : 'tnrc fullscreen channel:0', 
            'First Channel'     : 'tnrc fullscreen channel:1', 
            'Second Channel'    : 'tnrc fullscreen channel:2', 
            'Third Channel'     : 'tnrc fullscreen channel:3'
        }

        self.__SetHelper('SingleChannelFullScreenSwitch', States[value], value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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
        print('Command operation has failed')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
