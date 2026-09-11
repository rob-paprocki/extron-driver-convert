# Copyright 2026, Extron. All rights reserved.

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
        self._LoginLevel = b'\x02'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AudioVolume': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'ColorMode': { 'Status': {}},
            'DetailMode': { 'Status': {}},
            'DigitalZoom': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Light': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Resolution': { 'Status': {}},
            'Source': { 'Status': {}},
            'StreamingMode': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'\x08\x44\x3D\x01([\x00\x01])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(rb'\x08\x44\x3F\x01([\x00-\x64])'), self.__MatchAudioVolume, None)
            self.AddMatchString(re.compile(rb'\x08\x42\x0C\x01([\x00\x01])'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(rb'\x08\x42\x06\x01([\x00-\x05])'), self.__MatchColorMode, None)
            self.AddMatchString(re.compile(rb'\x08\x42\x09\x01([\x00-\x03])'), self.__MatchDetailMode, None)
            self.AddMatchString(re.compile(rb'\x08\x42\x0A\x01([\x00\x01])'), self.__MatchDigitalZoom, None)
            self.AddMatchString(re.compile(rb'\x08\x41\x05\x01([\x00\x01])'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(rb'\x08\x41\x04\x01([\x00\x01])'), self.__MatchLight, None)
            self.AddMatchString(re.compile(rb'\x08\x41\x00\x01([\x00\x01])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(rb'\x08\x44\x00\x01([\x00-\x05])'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(rb'\x08\x41\x06\x01([\x00-\x04])'), self.__MatchSource, None)
            self.AddMatchString(re.compile(rb'\x08\x44\x08\x01([\x00\x01])'), self.__MatchStreamingMode, None)
            self.AddMatchString(re.compile(rb'\x08\x42\x03\x01([\x00\x01])'), self.__MatchWhiteBalance, None)

            self.AddMatchString(re.compile(rb'[\x80\x81\x88\x89]([\x00-\xFF]{1,2})([\x01-\x0B])'), self.__MatchError, None)

    @property
    def LoginLevel(self):
        return self._LoginLevel

    @LoginLevel.setter
    def LoginLevel(self, value):
        if value == 'Admin':
            self._LoginLevel = b'\x02'
        else:
            self._LoginLevel = b'\x01'

    def SetCommandHelper(self, command, parameters):
        header = 0x01
        if len(command) == 2:
            header += 0b00001000

        parameterLength = len(parameters)
        if parameterLength > 255:
            header += 0b00000100
            return header.to_bytes(1,'little') + command + parameterLength.to_bytes(2,'big') + parameters
        else:
            return header.to_bytes(1,'little') + command + parameterLength.to_bytes(1,'big') + parameters

    def GetCommandHelper(self, command):
        if len(command) == 2:
            header = 0b00001000
        else:
            header = 0x00
        return header.to_bytes(1, 'little') + command + b'\x00'

    def SetOnConnectedString(self, value, qualifier):

        self.Authenticated = True
        connectString = self.SetCommandHelper(b'\x40\x0B', self._LoginLevel + self.devicePassword.encode())
        self.Send(connectString)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            AudioMuteCmdString = self.SetCommandHelper(b'\x44\x3D', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.GetCommandHelper(b'\x44\x3D')
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAudioVolume(self, value, qualifier):

        if 0 <= value <= 100:
            AudioVolumeCmdString = self.SetCommandHelper(b'\x44\x3F', value.to_bytes(1, 'little'))
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        AudioVolumeCmdString = self.GetCommandHelper(b'\x44\x3F')
        self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)

    def __MatchAudioVolume(self, match, tag):

        value = int.from_bytes(match.group(1), 'little')
        if 0 <= value <= 100:
            self.WriteStatus('AudioVolume', value, None)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            AutoFocusCmdString = self.SetCommandHelper(b'\x42\x0C', ValueStateValues[value])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self.GetCommandHelper(b'\x42\x0C')
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AutoFocus', value, None)

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB':             b'\x00',
            'Presentation':     b'\x01',
            'DLP':              b'\x02',
            'Web Conference':   b'\x03',
            'Black/White':      b'\x04',
            'Manual':           b'\x05'
            }

        if value in ValueStateValues:
            ColorModeCmdString = self.SetCommandHelper(b'\x42\x06', ValueStateValues[value])
            self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorMode')

    def UpdateColorMode(self, value, qualifier):

        ColorModeCmdString = self.GetCommandHelper(b'\x42\x06')
        self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def __MatchColorMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'sRGB',
            b'\x01': 'Presentation',
            b'\x02': 'DLP',
            b'\x03': 'Web Conference',
            b'\x04': 'Black/White',
            b'\x05': 'Manual'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ColorMode', value, None)

    def SetDetailMode(self, value, qualifier):

        ValueStateValues = {
            'Off':      b'\x03',
            'Low':      b'\x02',
            'Medium':   b'\x01',
            'High':     b'\x00'
            }

        if value in ValueStateValues:
            DetailModeCmdString = self.SetCommandHelper(b'\x42\x09', ValueStateValues[value])
            self.__SetHelper('DetailMode', DetailModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDetailMode')

    def UpdateDetailMode(self, value, qualifier):

        DetailModeCmdString = self.GetCommandHelper(b'\x42\x09')
        self.__UpdateHelper('DetailMode', DetailModeCmdString, value, qualifier)

    def __MatchDetailMode(self, match, tag):

        ValueStateValues = {
            b'\x03': 'Off',
            b'\x02': 'Low',
            b'\x01': 'Medium',
            b'\x00': 'High'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DetailMode', value, None)

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            DigitalZoomCmdString = self.SetCommandHelper(b'\x42\x0A', ValueStateValues[value])
            self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalZoom')

    def UpdateDigitalZoom(self, value, qualifier):

        DigitalZoomCmdString = self.GetCommandHelper(b'\x42\x0A')
        self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def __MatchDigitalZoom(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DigitalZoom', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  b'\x01',
            'Near': b'\x02',
            'Stop': b'\x00'
            }

        if 1 <= int(qualifier['Speed']) <= 15 and value in ValueStateValues:
            FocusCmdString = self.SetCommandHelper(b'\x42\x10', ValueStateValues[value] + int(qualifier['Speed']).to_bytes(2, 'big'))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            FreezeCmdString = self.SetCommandHelper(b'\x41\x05', ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = self.GetCommandHelper(b'\x41\x05')
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Freeze', value, None)

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            LightCmdString = self.SetCommandHelper(b'\x41\x04', ValueStateValues[value])
            self.__SetHelper('Light', LightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLight')

    def UpdateLight(self, value, qualifier):

        LightCmdString = self.GetCommandHelper(b'\x41\x04')
        self.__UpdateHelper('Light', LightCmdString, value, qualifier)

    def __MatchLight(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Light', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            PowerCmdString = self.SetCommandHelper(b'\x41\x00', ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = self.GetCommandHelper(b'\x41\x00')
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x00',
            '2': b'\x01',
            '3': b'\x02'
            }

        if 1 <= int(value) <= 3:
            PresetRecallCmdString = self.SetCommandHelper(b'\x41\x11', ValueStateValues[value])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x00',
            '2': b'\x01',
            '3': b'\x02'
            }

        if 1 <= int(value) <= 3:
            PresetSaveCmdString = self.SetCommandHelper(b'\x41\x12', ValueStateValues[value])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')
    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto':                 b'\x00',
            '4k@60Hz (4:4:4)':      b'\x01',
            '4k@60Hz (4:2:0)':      b'\x02',
            '4k@30Hz (4:4:4)':      b'\x03',
            '1080p@60Hz (4:4:4)':   b'\x04',
            '720p@60Hz (4:4:4)':    b'\x05'
            }

        if value in ValueStateValues:
            ResolutionCmdString = self.SetCommandHelper(b'\x44\x00', ValueStateValues[value])
            self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolution')

    def UpdateResolution(self, value, qualifier):

        ResolutionCmdString = self.GetCommandHelper(b'\x44\x00')
        self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x01': '4k@60Hz (4:4:4)',
            b'\x02': '4k@60Hz (4:2:0)',
            b'\x03': '4k@30Hz (4:4:4)',
            b'\x04': '1080p@60Hz (4:4:4)',
            b'\x05': '720p@60Hz (4:4:4)'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Resolution', value, None)

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'Live View':        b'\x00',
            'Internal Memory':  b'\x01',
            'USB':              b'\x02',
            'HDMI 1':           b'\x03',
            'HDMI 2':           b'\x04'
            }

        if value in ValueStateValues:
            SourceCmdString = self.SetCommandHelper(b'\x41\x06', ValueStateValues[value])
            self.__SetHelper('Source', SourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSource')

    def UpdateSource(self, value, qualifier):

        SourceCmdString = self.GetCommandHelper(b'\x41\x06')
        self.__UpdateHelper('Source', SourceCmdString, value, qualifier)

    def __MatchSource(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Live View',
            b'\x01': 'Internal Memory',
            b'\x02': 'USB',
            b'\x03': 'HDMI 1',
            b'\x04': 'HDMI 2'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Source', value, None)

    def SetStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            StreamingModeCmdString = self.SetCommandHelper(b'\x44\x08', ValueStateValues[value])
            self.__SetHelper('StreamingMode', StreamingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingMode')

    def UpdateStreamingMode(self, value, qualifier):

        StreamingModeCmdString = self.GetCommandHelper(b'\x44\x08')
        self.__UpdateHelper('StreamingMode', StreamingModeCmdString, value, qualifier)

    def __MatchStreamingMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('StreamingMode', value, None)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x00',
            'Manual': b'\x01'
            }

        if value in ValueStateValues:
            WhiteBalanceCmdString = self.SetCommandHelper(b'\x42\x03', ValueStateValues[value])
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        WhiteBalanceCmdString = self.GetCommandHelper(b'\x42\x03')
        self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def __MatchWhiteBalance(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x01': 'Manual'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('WhiteBalance', value, None)

    def SetZoom(self, value, qualifier):

        SpeedValue = int(qualifier['Speed'])

        ValueStateValues = {
            'Wide':         (b'\x01', SpeedValue),
            'Tele':         (b'\x02', SpeedValue),
            'Wide Stop':    (b'\x01', 0),
            'Tele Stop':    (b'\x02', 0)
            }

        if 1 <= SpeedValue <= 15 and value in ValueStateValues:
            ZoomCmdString = self.SetCommandHelper(b'\x42\x0F', ValueStateValues[value][0] + ValueStateValues[value][1].to_bytes(2, 'big'))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        elif self.Authenticated == False:
            self.Discard('Not Authenticated ' + command)
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

        Commands = {
            b'\x40\x0B': 'Authentication',
            b'\x44\x3D': 'Audio Mute',
            b'\x44\x3F': 'Audio Volume',
            b'\x42\x0C': 'Auto Focus',
            b'\x42\x06': 'Color Mode',
            b'\x42\x09': 'Detail Mode',
            b'\x42\x0A': 'Digital Zoom',
            b'\x42\x10': 'Focus',
            b'\x41\x05': 'Freeze',
            b'\x41\x04': 'Light',
            b'\x41\x00': 'Power',
            b'\x41\x11': 'Preset Recall',
            b'\x41\x12': 'Preset Save',
            b'\x44\x00': 'Resolution',
            b'\x41\x06': 'Source',
            b'\x44\x08': 'Streaming Mode',
            b'\x42\x03': 'White Balance',
            b'\x42\x0F': 'Zoom'
        }

        ErrorMatchValues = {
            b'\x01': 'Timeout',
            b'\x02': 'Invalid Command',
            b'\x03': 'Invalid Parameter',
            b'\x04': 'Invalid Length',
            b'\x05': 'FIFO Full',
            b'\x06': 'Firmware Update Error',
            b'\x07': 'Access Denied',
            b'\x08': 'Authentication Required',
            b'\x09': 'Busy',
            b'\x0A': 'SIP Required',
            b'\x0B': 'Power Off'
        }

        command = Commands[match.group(1)]
        value = ErrorMatchValues[match.group(2)]
        if command == 'Authentication':
            self.Error(['Authentication Failed, Error: {}.'.format(value, command)])
            self.Authenticated = False
        else:
            self.Error(['Error: {}, for Command: {}.'.format(value, command)])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = False
        
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.SetOnConnectedString(None, None)
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()