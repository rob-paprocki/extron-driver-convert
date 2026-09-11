from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Blank': { 'Status': {}},
            'ColorTemperature': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'IRRemoteControlLock': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'VideoSource': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb':01r;00([0-2])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(rb':01r900([01])\r'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(rb':01r@00([0-2])\r'), self.__MatchColorTemperature, None)
            self.AddMatchString(compile(rb':01rB00([01])\r'), self.__MatchIRRemoteControlLock, None)
            self.AddMatchString(compile(rb':01r=00([0-3])\r'), self.__MatchPictureMode, None)
            self.AddMatchString(compile(rb':01r000([0-2])\r'), self.__MatchPower, None)
            self.AddMatchString(compile(rb':01r700([1-4])\r'), self.__MatchSoundMode, None)
            self.AddMatchString(compile(rb':01r:(0(?:0[0-27]|21)|10[13])\r'), self.__MatchVideoSource, None)
            self.AddMatchString(compile(rb':01r8(0\d\d|100)\r'), self.__MatchVolume, None)
            self.AddMatchString(compile(rb'401-\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': '0',
            '4:3':  '1',
            'PTP':  '2',
        }

        AspectRatioCmdString = ':01S;00{}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = ':01G;000\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': '16:9',
            '1': '4:3',
            '2': 'PTP',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        AudioMuteCmdString = ':01S900{}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = ':01G9000\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On':  '1',
        }

        BacklightCmdString = ':01S000{}\r'.format(ValueStateValues[value])
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):
        self.UpdatePower( value, qualifier)        

    def SetBlank(self, value, qualifier):

        BlankCmdString = ':01SA031\r'
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)

    def SetColorTemperature(self, value, qualifier):

        ValueStateValues = {
            'Cool':     '0',
            'Standard': '1',
            'Warm':     '2',
        }

        ColorTemperatureCmdString = ':01S@00{}\r'.format(ValueStateValues[value])
        self.__SetHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)

    def UpdateColorTemperature(self, value, qualifier):

        ColorTemperatureCmdString = ':01G@000\r'
        self.__UpdateHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)

    def __MatchColorTemperature(self, match, tag):

        ValueStateValues = {
            '0': 'Cool',
            '1': 'Standard',
            '2': 'Warm',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorTemperature', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = ':01SA032\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'Lock':   '1',
            'Unlock': '0',
        }

        IRRemoteControlLockCmdString = ':01SB00{}\r'.format(ValueStateValues[value])
        self.__SetHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)

    def UpdateIRRemoteControlLock(self, value, qualifier):

        IRRemoteControlLockCmdString = ':01GB000\r'
        self.__UpdateHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)

    def __MatchIRRemoteControlLock(self, match, tag):

        ValueStateValues = {
            '1': 'Lock',
            '0': 'Unlock',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IRRemoteControlLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':    '10',
            'Down':  '11',
            'Left':  '12',
            'Right': '13',
            'Ok':    '14',
            'Menu':  '20',
            'Exit':  '22',
        }

        MenuNavigationCmdString = ':01SA0{}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Bright':   '1',
            'Soft':     '2',
            'Customer': '3',
        }

        PictureModeCmdString = ':01S=00{}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = ':01G=000\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Bright',
            '2': 'Soft',
            '3': 'Customer',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '3',
            'Off': '2',
        }

        PowerCmdString = ':01S000{}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = ':01G0000\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }


        value = match.group(1).decode()
        if value in ['0', '1']:
            power_value = 'On'
            backlight_value = ValueStateValues[value]
        else:
            power_value = 'Off'
            backlight_value = 'Off'

        self.WriteStatus('Power', power_value, None)
        self.WriteStatus('Backlight', backlight_value, None)

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard':  '1',
            'Custom':    '2',
            'Classroom': '3',
            'Meeting':   '4',
        }

        SoundModeCmdString = ':01S700{}\r'.format(ValueStateValues[value])
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = ':01G7000\r'
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            '1': 'Standard',
            '2': 'Custom',
            '3': 'Classroom',
            '4': 'Meeting',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetVideoSource(self, value, qualifier):

        ValueStateValues = {
            'VGA':         '000',
            'HDMI 1':      '001',
            'HDMI 2':      '002',
            'HDMI 3':      '021',
            'DisplayPort': '007',
            'iiWare':      '101',
            'Slot in PC':  '103',
        }

        VideoSourceCmdString = ':01S:{}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoSource', VideoSourceCmdString, value, qualifier)

    def UpdateVideoSource(self, value, qualifier):

        VideoSourceCmdString = ':01G:000\r'
        self.__UpdateHelper('VideoSource', VideoSourceCmdString, value, qualifier)

    def __MatchVideoSource(self, match, tag):

        ValueStateValues = {
            '000': 'VGA',
            '001': 'HDMI 1',
            '002': 'HDMI 2',
            '021': 'HDMI 3',
            '007': 'DisplayPort',
            '101': 'iiWare',
            '103': 'Slot in PC',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoSource', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = ':01S8{:03}\r'.format(int(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = ':01G8000\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



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

        self.Error(['Set command failed.'])

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
                result = search(regexString, self.__receiveBuffer)
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

