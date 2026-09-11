from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import hashlib
from binascii import hexlify

class DeviceSerialClass:
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
        self.devicePassword = 'admin'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Input': { 'Status': {}},
            'KeyLock': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
            

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*ASP=(4:3|16:9|16:10|AUTO)#',re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#',re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|HDMI|HDMI2|HDBASET)#',re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*KEYLOCK=(ON|OFF)#',re.I), self.__MatchKeyLock, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|PORTRAIT360)#',re.I), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTIM=(\d+)#',re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#',re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#',re.I), self.__MatchVideoMute, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3'   : '\r*asp=4:3#\r', 
            '16:9'  : '\r*asp=16:9#\r', 
            '16:10' : '\r*asp=16:10#\r', 
            'Auto'  : '\r*asp=AUTO#\r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '4:3' : '4:3', 
            '16:9' : '16:9', 
            '16:10' : '16:10', 
            'AUTO' : 'Auto'
            }

        value = AspectRatioState[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On'    : '\r*mute=on#\r', 
            'Off'   : '\r*mute=off#\r'
            }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = AudioMuteState[match.group(1).decode().upper()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        InputState = {
            'Computer / YPbPr' : '\r*sour=RGB#\r', 
            'HDMI 1'    : '\r*sour=hdmi#\r', 
            'HDMI 2'    : '\r*sour=hdmi2#\r', 
            'HDBaseT'   : '\r*sour=hdbaset#\r'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            'RGB' : 'Computer / YPbPr', 
            'HDMI' : 'HDMI 1', 
            'HDMI2' : 'HDMI 2', 
            'HDBASET' : 'HDBaseT'
            }

        value = InputState[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

    def SetKeyLock(self, value, qualifier):

        KeyLockState = {
            'On'    : '\r*keylock=on#\r', 
            'Off'   : '\r*keylock=off#\r'
            }

        KeyLockCmdString = KeyLockState[value]
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def UpdateKeyLock(self, value, qualifier):

        KeyLockCmdString = '\r*keylock=?#\r'
        self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def __MatchKeyLock(self, match, tag):

        KeyLockState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = KeyLockState[match.group(1).decode().upper()]
        self.WriteStatus('KeyLock', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal'    : '\r*lampm=lnor#\r', 
            'Eco'       : '\r*lampm=eco#\r', 
            '360 and Portrait' : '\r*lampm=portrait360#\r'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeState = {
            'LNOR' : 'Normal', 
            'ECO' : 'Eco', 
            'PORTRAIT360' : '360 and Portrait'
            }

        value = LampModeState[match.group(1).decode().upper()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode().upper())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuCall(self, value, qualifier):

        MenuCallState = {
            'On'    : '\r*menu=on#\r', 
            'Off'   : '\r*menu=off#\r'
            }

        MenuCallCmdString = MenuCallState[value]
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up'    : '\r*up#\r', 
            'Down'  : '\r*down#\r', 
            'Left'  : '\r*left#\r', 
            'Right' : '\r*right#\r', 
            'Enter' : '\r*enter#\r', 
            'Back'  : '\r*back#\r'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : '\r*pow=on#\r', 
            'Off'   : '\r*pow=off#\r'
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }


        value = PowerState[match.group(1).decode().upper()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On'    : '\r*blank=on#\r', 
            'Off'   : '\r*blank=off#\r'
            }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = VideoMuteState[match.group(1).decode().upper()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeState = {
            'Up'    : '\r*vol=+#\r', 
            'Down'  : '\r*vol=-#\r'
            }

        VolumeCmdString = VolumeState[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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


class DeviceEthernetClass:
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
        self.devicePassword = 'admin'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }

        
        self.Authenticated = 'Not Needed'
        
        self.lastAVMuteUpdate = 0

                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%1AVMT=(30|31|21|11)\r'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'%1ERST=([0-2]{6})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'%1INPT=(11|31|32|51)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'%1LAMP=([0-9]{1,5}) [01]\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'%1POWR=(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'%1(AVMT|ERST|INPT|LAMP|POWR)=ERR([1-4A])\r'), self.__MatchError, None)
            
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None) 
    def __MatchPassword(self, match, tag):

        self.SetPassword( match.group(1), None)
        
    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
            self.Authenticated = 'Admin'
        else:
            self.MissingCredentialsLog('Password')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '%1AVMT 21\r', 
            'Off' : '%1AVMT 20\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateAVMute(value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '%1AVMT 31\r', 
            'Off' : '%1AVMT 30\r'
        }

        AVMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = '%1AVMT ?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)


    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            '11' : ('Off', 'Off', 'On'),
            '21' : ('Off', 'On',  'Off'),
            '30' : ('Off', 'Off', 'Off'),
            '31' : ('On',  'On',  'On'),# AV, A, V
        }

        value = match.group(1).decode()
        self.WriteStatus('AVMute', ValueStateValues[value][0], None)
        self.WriteStatus('AudioMute', ValueStateValues[value][1], None)
        self.WriteStatus('VideoMute', ValueStateValues[value][2], None)
        
    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '%1ERST ?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '000000' : 'Normal', 
            '100000' : 'Fan Warning', 
            '200000' : 'Fan Error', 
            '010000' : 'Lamp Warning', 
            '020000' : 'Lamp Error', 
            '001000' : 'Temperature Warning', 
            '002000' : 'Temperature Error', 
            '000100' : 'Cover Warning', 
            '000200' : 'Cover Error', 
            '000010' : 'Filter Warning', 
            '000020' : 'Filter Error', 
            '000001' : 'Other Warning', 
            '000002' : 'Other Error'
        }

        value = match.group(1).decode()
        if value in ValueStateValues:
            self.WriteStatus('DeviceStatus', ValueStateValues[value], None)
        else:
            self.WriteStatus('DeviceStatus', 'Multiple Warnings / Errors', None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer / YPbPr'  : '%1INPT 11\r', 
            'HDMI 1'            : '%1INPT 31\r', 
            'HDMI 2'            : '%1INPT 32\r', 
            'HDBaseT'           : '%1INPT 51\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '%1INPT ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '11' : 'Computer / YPbPr', 
            '31' : 'HDMI 1', 
            '32' : 'HDMI 2', 
            '51' : 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '%1LAMP ?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '%1POWR 1\r', 
            'Off' : '%1POWR 0\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '%1POWR ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '%1AVMT 11\r', 
            'Off' : '%1AVMT 10\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.UpdateAVMute(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin']:
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

        CommandValues = {
            'AVMT' : 'Mute', 
            'ERST' : 'Device Status', 
            'INPT' : 'Input', 
            'LAMP' : 'Lamp Usage', 
            'POWR' : 'Power'
        }
        
        ErrorValues = {
            '1' : 'Undefined command.',
            '2' : 'Out of parameter.',
            '3' : 'Unavailable time.',
            '4' : 'Projector failure.',
            'A' : 'Invalid password.'
        }
        if match.group(2).decode() == 'A':
            self.Authenticated = 'None'
        value = '{0}: {1}'.format(CommandValues[match.group(1).decode()], ErrorValues[match.group(2).decode()])
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastAVMuteUpdate = 0
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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