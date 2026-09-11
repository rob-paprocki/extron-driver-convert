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
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'AudioVolume': {'Parameters': ['Channel'], 'Status': {}},
            'CameraStandby': {'Parameters': ['Camera'], 'Status': {}},
            'Focus': {'Parameters': ['Camera', 'Focus Speed'], 'Status': {}},
            'FocusMode': {'Parameters': ['Camera'], 'Status': {}},
            'Home': {'Parameters': ['Camera'], 'Status': {}},
            'Input': { 'Status': {}},
            'Pan': {'Parameters': ['Camera', 'Pan Speed'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Camera'], 'Status': {}},
            'PresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'Tilt': {'Parameters': ['Camera', 'Tilt Speed'], 'Status': {}},
            'VideoType': {'Parameters': ['Input'], 'Status': {}},
            'Zoom': {'Parameters': ['Camera', 'Zoom Speed'], 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'audio (master|easy_mic_1|easy_mic_2|usb_playback|line_out_1|usb_record) mute get\r\nmute:\s+?(on|off)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'audio (master|easy_mic_1|easy_mic_2|usb_playback|line_out_1|usb_record) volume get\r\nvolume:\s+?([-\d\.]+) dB\r\n'), self.__MatchAudioVolume, None)
            self.AddMatchString(re.compile(b'camera ([1-4]) standby get\r\nstandby:\s+?(on|off)\r\n'), self.__MatchCameraStandby, None)
            self.AddMatchString(re.compile(b'camera ([1-4]) focus mode get\r\nauto_focus:\s+?(on|off)\r\n'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'video source set input([1-4])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'video source get\r\nsource:\s+?input([1-4])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'video input([1-4]) type get\r\ninput type:\s+?(camera|video)\r\n'), self.__MatchVideoType, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchSendPassword, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x01\xFF\xFB\x03'), self.__MatchHandshake, None)

    def SetHandshake(self, value, qualifier):

        self.__SetHelper('Handshake', b'\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x01\xFF\xFE\x03', None, None)

    def __MatchHandshake(self, match, tag):

        self.SetHandshake( None, None)

    def SetSendUsername(self, value, qualifier):

        self.Send(self.deviceUsername + '\r\n')

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')
        
    def __MatchSendUsername(self, match, tag):

        self.SetSendUsername( None, None)

    def __MatchSendPassword(self, match, tag):

        self.SetSendPassword( None, None)
    
    def SetAudioMute(self, value, qualifier):
        
        ChannelStates = {
            'Master'      : 'master', 
            'Easy Mic 1'  : 'easy_mic_1', 
            'Easy Mic 2'  : 'easy_mic_2', 
            'USB Playback': 'usb_playback', 
            'Line Out'    : 'line_out_1', 
            'USB Record'  : 'usb_record'
        }

        ValueStateValues = {
            'On' : 'on', 
            'Off': 'off'
        }
        
        if value in ValueStateValues and qualifier['Channel'] in ChannelStates:
            AudioMuteCmdString = 'audio {} mute {}\r\n'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master'      : 'master', 
            'Easy Mic 1'  : 'easy_mic_1', 
            'Easy Mic 2'  : 'easy_mic_2', 
            'USB Playback': 'usb_playback', 
            'Line Out'    : 'line_out_1', 
            'USB Record'  : 'usb_record'
        }
        
        if qualifier['Channel'] in ChannelStates:
            AudioMuteCmdString = 'audio {} mute get\r\n'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ChannelStates = {
            'master'      : 'Master', 
            'easy_mic_1'  : 'Easy Mic 1', 
            'easy_mic_2'  : 'Easy Mic 2', 
            'usb_playback': 'USB Playback', 
            'line_out_1'  : 'Line Out', 
            'usb_record'  : 'USB Record'
        }

        ValueStateValues = {
            'on' : 'On', 
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAudioVolume(self, value, qualifier):
        
        ChannelStates = {
            'Master'      : 'master', 
            'Easy Mic 1'  : 'easy_mic_1', 
            'Easy Mic 2'  : 'easy_mic_2', 
            'USB Playback': 'usb_playback', 
            'Line Out'    : 'line_out_1', 
            'USB Record'  : 'usb_record'
        }

        if -42 <= value <= 6 and qualifier['Channel'] in ChannelStates:
            AudioVolumeCmdString = 'audio {} volume set {}\r\n'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        ChannelStates = {
            'Master'      : 'master', 
            'Easy Mic 1'  : 'easy_mic_1', 
            'Easy Mic 2'  : 'easy_mic_2', 
            'USB Playback': 'usb_playback', 
            'Line Out'    : 'line_out_1', 
            'USB Record'  : 'usb_record'
        }
        
        if qualifier['Channel'] in ChannelStates:
            AudioVolumeCmdString = 'audio {} volume get\r\n'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioVolume')

    def __MatchAudioVolume(self, match, tag):
        
        ChannelStates = {
            'master'      : 'Master', 
            'easy_mic_1'  : 'Easy Mic 1', 
            'easy_mic_2'  : 'Easy Mic 2', 
            'usb_playback': 'USB Playback', 
            'line_out_1'  : 'Line Out', 
            'usb_record'  : 'USB Record'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        
        value = int(float(match.group(2).decode()))
        self.WriteStatus('AudioVolume', value, qualifier)

    def SetCameraStandby(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off': 'off'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4:
            CameraStandbyCmdString = 'camera {} standby {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraStandby')

    def UpdateCameraStandby(self, value, qualifier):
        
        if 1 <= int(qualifier['Camera']) <= 4:
            CameraStandbyCmdString = 'camera {} standby get\r\n'.format(qualifier['Camera'])
            self.__UpdateHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCameraStandby')

    def __MatchCameraStandby(self, match, tag):

        ValueStateValues = {
            'on' : 'On', 
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Camera'] = match.group(1).decode()
        
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CameraStandby', value, qualifier)

    def SetFocus(self, value, qualifier):
        
        focus_speed = int(qualifier['Focus Speed'])
        
        ValueStateValues = {
            'Near': 'near {}'.format(focus_speed), 
            'Far' : 'far {}'.format(focus_speed), 
            'Stop': 'stop'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4 and 1 <= focus_speed <= 8:
            FocusCmdString = 'camera {} focus {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'  : 'auto', 
            'Manual': 'manual'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4:
            FocusModeCmdString = 'camera {} focus mode {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):
        
        if 1 <= int(qualifier['Camera']) <= 4:
            FocusModeCmdString = 'camera {} focus mode get\r\n'.format(qualifier['Camera'])
            self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFocusMode')

    def __MatchFocusMode(self, match, tag):

        ValueStateValues = {
            'on' : 'Auto', 
            'off': 'Manual'
        }

        qualifier = {}
        qualifier['Camera'] = match.group(1).decode()
        
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FocusMode', value, qualifier)

    def SetHome(self, value, qualifier):
        
        if 1 <= int(qualifier['Camera']) <= 4:
            HomeCmdString = 'camera {} home\r\n'.format(qualifier['Camera'])
            self.__SetHelper('Home', HomeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHome')

    def SetInput(self, value, qualifier):
        
        if 1 <= int(value) <= 4:
            InputCmdString = 'video source set input{}\r\n'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
            
        InputCmdString = 'video source get\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        
        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetPan(self, value, qualifier):
        
        pan_speed = int(qualifier['Pan Speed'])
        
        ValueStateValues = {
            'Left' : 'left {}'.format(pan_speed), 
            'Right': 'right {}'.format(pan_speed), 
            'Stop' : 'stop'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4 and 1 <= pan_speed <= 24:
            PanCmdString = 'camera {} pan {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPresetRecall(self, value, qualifier):
        
        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Camera']) <= 4:
            PresetRecallCmdString = 'camera {} preset recall {}\r\n'.format(qualifier['Camera'], value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):
        
        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Camera']) <= 4:
            PresetSaveCmdString = 'camera {} preset store {}\r\n'.format(qualifier['Camera'], value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetTilt(self, value, qualifier):
        
        tilt_speed = int(qualifier['Tilt Speed'])
        
        ValueStateValues = {
            'Up'  : 'up {}'.format(tilt_speed), 
            'Down': 'down {}'.format(tilt_speed), 
            'Stop': 'stop'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4 and 1 <= tilt_speed <= 20:
            TiltCmdString = 'camera {} tilt {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetVideoType(self, value, qualifier):

        ValueStateValues = {
            'Camera': 'camera', 
            'Video' : 'video'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Input']) <= 4:
            VideoTypeCmdString = 'video input{} type set {}\r\n'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('VideoType', VideoTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoType')

    def UpdateVideoType(self, value, qualifier):
        
        if 1 <= int(qualifier['Input']) <= 4:
            VideoTypeCmdString = 'video input{} type get\r\n'.format(qualifier['Input'])
            self.__UpdateHelper('VideoType', VideoTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoType')

    def __MatchVideoType(self, match, tag):

        ValueStateValues = {
            'camera': 'Camera', 
            'video' : 'Video'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoType', value, qualifier)

    def SetZoom(self, value, qualifier):
        
        zoom_speed = int(qualifier['Zoom Speed'])

        ValueStateValues = {
            'In'  : 'in {}'.format(zoom_speed), 
            'Out' : 'out {}'.format(zoom_speed), 
            'Stop': 'stop'
        }
        
        if value in ValueStateValues and 1 <= int(qualifier['Camera']) <= 4 and 1 <= zoom_speed <= 20:
            ZoomCmdString = 'camera {} zoom {}\r\n'.format(qualifier['Camera'], ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        self.Error(["There was an error in the command response."])

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