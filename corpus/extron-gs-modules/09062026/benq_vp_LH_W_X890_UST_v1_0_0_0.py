from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'VolumeStatus': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*ASP=(4:3|16:6|16:9|16:10|AUTO|REAL|LBOX|WIDE|ANAM|ANAM2.35:1|ANAM16:9)#\r', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#\r', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#\r', re.I), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|RGB2|RGB3|YPBR|YPBR2|DVIA|DVID|HDMI|HDMI2|VID|SVID|NETWORK|USBDISPLAY|USBREADER|HDBASET|DP|SDI)#\r', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|SECO|SECO2|SECO3|DIMMING|CUSTOM|DUALBR|DUALRE|SINGLE|SINGLEECO)#\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTI(M|M2)=(\d+)#\r', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*APPMOD=([\w]+?|[\w]+?\-[\w]+?)#\r', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#\r', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#\r', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#\r', re.I), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item|Unsupported item)\r', re.I), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3' : '4:3', 
            '16:6' : '16:6', 
            '16:9' : '16:9', 
            '16:10' : '16:10', 
            'Auto' : 'AUTO', 
            'Real' : 'REAL', 
            'Letterbox' : 'LBOX', 
            'Wide' : 'WIDE', 
            'Anamorphic' : 'ANAM', 
            'Anamorphic 2.35:1' : 'ANAM2.35:1', 
            'Anamorphic 16:9' : 'ANAM16:9'
            }

        AspectRatioCmdString = '\r*asp={0}#\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '4:3' : '4:3', 
            '16:6' : '16:6', 
            '16:9' : '16:9', 
            '16:10' : '16:10', 
            'AUTO' : 'Auto', 
            'REAL' : 'Real', 
            'LBOX' : 'Letterbox', 
            'WIDE' : 'Wide', 
            'ANAM' : 'Anamorphic', 
            'ANAM2.35:1' : 'Anamorphic 2.35:1', 
            'ANAM16:9' : 'Anamorphic 16:9'
            }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        AudioMuteCmdString = '\r*mute={0}#\r'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        FreezeCmdString = '\r*freeze={0}#\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'Computer/YPbPr' : 'RGB', 
            'Computer 2/YPbPr2' : 'RGB2', 
            'Computer 3/YPbPr3' : 'RGB3', 
            'Component 1' : 'YPBR', 
            'Component 2' : 'YPBR2', 
            'DVI-A' : 'DVIA', 
            'DVI-D' : 'DVID', 
            'HDMI 1' : 'HDMI', 
            'HDMI 2' : 'HDMI2', 
            'Composite' : 'VID', 
            'S-Video' : 'SVID', 
            'Network' : 'NETWORK', 
            'USB Display' : 'USBDISPLAY', 
            'USB Reader' : 'USBREADER', 
            'HDBaseT' : 'HDBASET', 
            'DisplayPort' : 'DP', 
            '3G-SDI' : 'SDI'
            }

        InputCmdString = '\r*sour={0}#\r'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            'RGB' : 'Computer/YPbPr', 
            'RGB2' : 'Computer 2/YPbPr2', 
            'RGB3' : 'Computer 3/YPbPr3', 
            'YPBR' : 'Component 1', 
            'YPBR2' : 'Component 2', 
            'DVIA' : 'DVI-A', 
            'DVID' : 'DVI-D', 
            'HDMI' : 'HDMI 1', 
            'HDMI2' : 'HDMI 2', 
            'VID' : 'Composite', 
            'SVID' : 'S-Video', 
            'NETWORK' : 'Network', 
            'USBDISPLAY' : 'USB Display', 
            'USBREADER' : 'USB Reader', 
            'HDBASET' : 'HDBaseT', 
            'DP' : 'DisplayPort', 
            'SDI' : '3G-SDI'
            }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal' : 'lnor', 
            'Eco' : 'eco', 
            'Smart Eco' : 'seco', 
            'Smart Eco 2' : 'seco2', 
            'Smart Eco 3' : 'seco3', 
            'Dimming' : 'dimming', 
            'Custom' : 'custom', 
            'Dual Brightest' : 'dualbr', 
            'Dual Reliable' : 'dualre', 
            'Single Alternative' : 'single', 
            'Single Alternative Eco' : 'singleeco'
            }

        LampModeCmdString = '\r*lampm={0}#\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeState = {
            'LNOR' : 'Normal', 
            'ECO' : 'Eco', 
            'SECO' : 'Smart Eco', 
            'SECO2' : 'Smart Eco 2', 
            'SECO3' : 'Smart Eco 3', 
            'DIMMING' : 'Dimming', 
            'CUSTOM' : 'Custom', 
            'DUALBR' : 'Dual Brightest', 
            'DUALRE' : 'Dual Reliable', 
            'SINGLE' : 'Single Alternative', 
            'SINGLEECO' : 'Single Alternative Eco'
            }

        value = LampModeState[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampStates = {
            '1' : 'ltim',
            '2' : 'ltim2'
            }

        LampValue = LampStates[qualifier['Lamp']]
        LampUsageCmdString = '\r*{0}=?#\r'.format(LampValue)
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, qualifier):

        value = int(match.group(2).decode())
        lamp = match.group(1).decode().lower()
        if lamp == 'm':
            qualifier = {'Lamp' : '1'}
        elif lamp == 'm2':
            qualifier = {'Lamp' : '2'}
        self.WriteStatus('LampUsage', value, qualifier)

    def SetMenuCall(self, value, qualifier):

        MenuCallState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        MenuCallCmdString = '\r*menu={0}#\r'.format(MenuCallState[value])
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up' : 'up', 
            'Down' : 'down', 
            'Left' : 'left', 
            'Right' : 'right', 
            'Enter' : 'enter'
            }

        MenuNavigationCmdString = '\r*{0}#\r'.format(MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        PictureModeState = {
            'Dynamic' : 'dynamic', 
            'Presentation' : 'preset',
            'sRGB' : 'srgb', 
            'Bright' : 'bright', 
            'Living Room' : 'livingroom', 
            'Game' : 'game', 
            'Cinema' : 'cine', 
            'Standard/Vivid' : 'std', 
            'Football' : 'football', 
            'Football Bright' : 'footballbt', 
            'DICOM' : 'dicom', 
            'THX' : 'thx', 
            'Silence Mode' : 'silence', 
            'DCI-P3 Mode' : 'dci-p3', 
            'User 1' : 'user1', 
            'User 2' : 'user2', 
            'User 3' : 'user3', 
            'ISF Day' : 'isfday', 
            'ISF Night' : 'isfnight', 
            '3D' : 'threed'
            }

        PictureModeCmdString = '\r*appmod={0}#\r'.format(PictureModeState[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        PictureModeState = {
            'DYNAMIC' : 'Dynamic', 
            'PRESET' : 'Presentation',
            'SRGB' : 'sRGB', 
            'BRIGHT' : 'Bright', 
            'LIVINGROOM' : 'Living Room', 
            'GAME' : 'Game', 
            'CINE' : 'Cinema', 
            'STD' : 'Standard/Vivid', 
            'FOOTBALL' : 'Football', 
            'FOOTBALLBT' : 'Football Bright', 
            'DICOM' : 'DICOM', 
            'THX' : 'THX', 
            'SILENCE' : 'Silence Mode', 
            'DCI-P3' : 'DCI-P3 Mode', 
            'USER1' : 'User 1', 
            'USER2' : 'User 2', 
            'USER3' : 'User 3', 
            'ISFDAY' : 'ISF Day', 
            'ISFNIGHT' : 'ISF Night', 
            'THREED' : '3D'
            }

        value = PictureModeState[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : 'on', 
            'Off'   : 'off'
            }

        PowerCmdString = '\r*pow={0}#\r'.format(PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }


        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        VideoMuteCmdString = '\r*blank={0}#\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        value = VideoMuteState[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeState = {
            'Up' : '+', 
            'Down' : '-'
            }

        VolumeCmdString = '\r*vol={0}#\r'.format(VolumeState[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = '\r*vol=?#\r'
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VolumeStatus', value, None)

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

        value = match.group(0).decode()
        self.Error([value])

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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

