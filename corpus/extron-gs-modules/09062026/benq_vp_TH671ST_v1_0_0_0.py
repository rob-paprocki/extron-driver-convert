from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DMode': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'VolumeStatus': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*3D=(OFF|AUTO|TB|FS|FP|SBS|DA|IV)#\r\n', re.I), self.__Match3DMode, None)
            self.AddMatchString(re.compile(b'\*ASP=(AUTO|4:3|16:9|WIDE|LBOX)#\r\n', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#\r\n', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#\r\n', re.I), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|HDMI|HDMI2)#\r\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|SECO)#\r\n', re.I), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTIM=(\d+)#\r\n', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*APPMOD=(BRIGHT|VIVID|CINE|GAME|USER1|USER2)#\r\n', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#\r\n', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#\r\n', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*VOL=(\d+)#\r\n', re.I), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'(Illegal format|Unsupported item|Block item)\r', re.I), self.__MatchError, None)

    def Set3DMode(self, value, qualifier):
        ValueStateValues = {
            'Off':                  'off',
            'Auto':                 'auto',
            'Top Bottom':           'tb',
            'Frame Sequential':     'fs',
            'Frame Packing':        'fp',
            'Side by Side':         'sbs',
            'Inverter Disable':     'da',
            'Inverter Enable':      'iv'
        }
        _3DModeCmdString = '\r*3d={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('3DMode', _3DModeCmdString, value, qualifier)

    def Update3DMode(self, value, qualifier):
        _3DModeCmdString = '\r*3d=?#\r'
        self.__UpdateHelper('3DMode', _3DModeCmdString, value, qualifier)

    def __Match3DMode(self, match, tag):
        ValueStateValues = {
            'OFF':  'Off',
            'AUTO': 'Auto',
            'TB':   'Top Bottom',
            'FS':   'Frame Sequential',
            'FP':   'Frame Packing',
            'SBS':  'Side by Side',
            'DA':   'Inverter Disable',
            'IV':   'Inverter Enable'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('3DMode', value, None)

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Auto':         'AUTO',
            '4:3':          '4:3',
            '16:9':         '16:9',
            'Wide':         'WIDE',
            'Letterbox':    'LBOX'
        }
        AspectRatioCmdString = '\r*asp={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            'AUTO': 'Auto',
            '4:3':  '4:3',
            '16:9': '16:9',
            'WIDE': 'Wide',
            'LBOX': 'Letterbox'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }
        AudioMuteCmdString = '\r*mute={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        AudioMuteCmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        ValueStateValues = {
            'ON':   'On',
            'OFF':  'Off'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }
        FreezeCmdString = '\r*freeze={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        FreezeCmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        ValueStateValues = {
            'ON':   'On',
            'OFF':  'Off'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Computer': 'RGB',
            'HDMI 1':   'hdmi',
            'HDMI 2':   'hdmi2'
        }
        InputCmdString = '\r*sour={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ValueStateValues = {
            'RGB':      'Computer',
            'HDMI':     'HDMI 1',
            'HDMI2':    'HDMI 2'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):
        ValueStateValues = {
            'Normal':       'lnor',
            'Eco':          'eco',
            'Smart Eco':    'seco'
        }
        LampModeCmdString = '\r*lampm={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        ValueStateValues = {
            'LNOR': 'Normal',
            'ECO':  'Eco',
            'SECO': 'Smart Eco'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuCall(self, value, qualifier):
        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }
        MenuCallCmdString = '\r*menu={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up':       'up',
            'Down':     'down',
            'Left':     'left',
            'Right':    'right',
            'Enter':    'enter'
        }
        MenuNavigationCmdString = '\r*{}#\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):
        ValueStateValues = {
            'Bright':   'bright',
            'Vivid':    'vivid',
            'Cinema':   'cine',
            'Game':     'game',
            'User 1':   'user1',
            'User 2':   'user2'
        }
        PictureModeCmdString = '\r*appmod={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        PictureModeCmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):
        ValueStateValues = {
            'BRIGHT': 'Bright',
            'VIVID': 'Vivid',
            'CINE': 'Cinema',
            'GAME': 'Game',
            'USER1': 'User 1',
            'USER2': 'User 2'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }
        PowerCmdString = '\r*pow={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            'ON':   'On',
            'OFF':  'Off'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }
        VideoMuteCmdString = '\r*blank={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ValueStateValues = {
            'ON':   'On',
            'OFF':  'Off'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('VideoMute', value, None)

    def UpdateVolumeStatus(self, value, qualifier):
        VolumeStatusCmdString = '\r*vol=?#\r'
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('VolumeStatus', value, None)

    def SetVolumeStep(self, value, qualifier):
        ValueStateValues = {
            'Up':   '+',
            'Down': '-'
        }
        VolumeStepCmdString = '\r*vol={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

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
        value = match.group(1).decode()
        self.Error(['An error occurred: {}.'.format(value)])

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