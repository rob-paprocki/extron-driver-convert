from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
        
        if self.ConnectionType == 'Serial':
            self.oppo_3_261_serial()
        else:
            self.oppo_3_261_tcp()

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            'Apps': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioSelector': {'Status': {}},
            'Blue': {'Status': {}},
            'CurrentChapterandTrack': {'Status': {}},
            'CurrentTitle': {'Status': {}},
            'Dimmer': {'Status': {}},
            'Green': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Option': {'Status': {}},
            'PIP': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'PureAudio': {'Status': {}},
            'Red': {'Status': {}},
            'Setup': {'Status': {}},
            'Subtitle': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
            'Yellow': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'@QCH OK ([0-9]{1,3})/([0-9]{1,3})\r'), self.__MatchCurrentChapterandTrack, None)
            self.AddMatchString(compile(b'@QTK OK ([0-9]{1,3})/([0-9]{1,3})\r'), self.__MatchCurrentTitle, None)
            self.AddMatchString(compile(b'@UTC ([0-9]{1,3}) ([0-9]{1,3}) .*\r'), self.__MatchChapterandTitle, None)
            self.AddMatchString(compile(b'@(UIS|QIS)( | OK )([0-7]) (BD-PLAYER|HDMI-FRONT|HDMI-BACK|ARC-HDMI-OUT1|ARC-HDMI-OUT2|OPTICAL|COAXIAL|USB-AUDIO)\r'), self.__MatchInput, None)
            self.AddMatchString(compile(b'@(UPL|QPL)( | OK )(DISC|LOAD|OPEN|CLOS|PLAY|PAUS|STOP|STPF|STPR|FFW([1-5]|D)|FRV[1-5]|SFW([1-4]|D)|SRV[0-5]|HOME|MCTR|NO DISC|LOADING|CLOSE|PAUSE|STEP|FREV|SREV|SETUP|HOME MENU|MEDIA CENTER)\r'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(compile(b'@(UPW|QPW)( | OK )([0-1]|ON|OFF)\r'), self.__MatchPower, None)
            self.AddMatchString(compile(b'@(UVL|QVL)( | OK )([0-9]{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'@(\w\w\w) ER.*\r'), self.__MatchError, None)
            
    def SetOnConnectedString(self, value, qualifier):
        if self.ConnectionType == 'Ethernet':
            self.Send('REMOTE SVM 3')
        else:
            self.Send('#SVM 3\r')

    def Set3D(self, value, qualifier):

        ThreeDCmdString = '#M3D\r'
        self.__SetHelper('3D', ThreeDCmdString, value, qualifier)

    def SetApps(self, value, qualifier):

        AppsCmdString = self.AppsStateValues[value]
        self.__SetHelper('Apps', AppsCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto': '#SZM AR\r',
            'Full Screen': '#SZM FS\r',
            'Underscan': '#SZM US\r',
            '1.2': '#SZM 1.2\r',
            '1.3': '#SZM 1.3\r',
            '1.5': '#SZM 1.5\r',
            '2': '#SZM 2\r',
            '1/2': '#SZM 1/2\r',
            '3': '#SZM 3\r',
            '4': '#SZM 4\r',
            '1/3': '#SZM 1/3\r',
            '1/4': '#SZM 1/4\r',
            'Zoom': '#ZOM\r',
            '1': '#SZM 1\r'
            }
        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = '#MUT\r'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAudioSelector(self, value, qualifier):

        AudioSelectorCmdString = '#AUD\r'
        self.__SetHelper('AudioSelector', AudioSelectorCmdString, value, qualifier)

    def SetBlue(self, value, qualifier):

        BlueCmdString = '#BLU\r'
        self.__SetHelper('Blue', BlueCmdString, value, qualifier)

    def UpdateCurrentChapterandTrack(self, value, qualifier):

        CurrentChapterandTrackCmdString = '#QCH\r'
        self.__UpdateHelper('CurrentChapterandTrack', CurrentChapterandTrackCmdString, value, qualifier)

    def __MatchCurrentChapterandTrack(self, match, tag):

        chap1 = str(int(match.group(1).decode()))
        chap2 = str(int(match.group(2).decode()))
        value = chap1 + '/' + chap2
        self.WriteStatus('CurrentChapterandTrack', value, None)

    def __MatchChapterandTitle(self, match, tag):
        prevTitl = self.ReadStatus('CurrentTitle', None).split('/')
        if prevTitl is not None:
            try:
                title1 = str(int(match.group(1).decode()))
                title2 = str(int(prevTitl[1]))
                value1 = title1 + '/' + title2
            except (AttributeError, IndexError):
                value1 = str(int(match.group(1).decode()))
            self.WriteStatus('CurrentTitle', value1, None)

        prevChap = self.ReadStatus('CurrentChapterandTrack', None).split('/')
        if prevChap is not None:
            try:
                chap1 = str(int(match.group(2).decode()))
                chap2 = str(int(prevChap[1]))
                value2 = chap1 + '/' + chap2
            except (AttributeError, IndexError):
                value2 = str(int(match.group(2).decode()))
            self.WriteStatus('CurrentChapterandTrack', value2, None)

    def UpdateCurrentTitle(self, value, qualifier):

        CurrentTitleCmdString = '#QTK\r'
        self.__UpdateHelper('CurrentTitle', CurrentTitleCmdString, value, qualifier)

    def __MatchCurrentTitle(self, match, tag):

        titl1 = str(int(match.group(1).decode()))
        titl2 = str(int(match.group(2).decode()))
        value = titl1 + '/' + titl2
        self.WriteStatus('CurrentTitle', value, None)

    def SetDimmer(self, value, qualifier):

        DimmerCmdString = '#DIM\r'
        self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)

    def SetGreen(self, value, qualifier):

        GreenCmdString = '#GRN\r'
        self.__SetHelper('Green', GreenCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Blu-Ray Player': '#SIS 0\r',
            'HDMI 1': '#SIS 1\r',
            'HDMI 2': '#SIS 2\r',
            'ARC 1': '#SIS 3\r',
            'ARC 2': '#SIS 4\r',
            'Optical': '#SIS 5\r',
            'Coaxial': '#SIS 6\r',
            'USB Audio': '#SIS 7\r'
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '#QIS\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
            '0': 'Blu-Ray Player',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'ARC 1',
            '4': 'ARC 2',
            '5': 'Optical',
            '6': 'Coaxial',
            '7': 'USB Audio'
            }
        value = InputStateNames[match.group(3).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        KeypadStateValues = {
            '1': '#NU1\r',
            '2': '#NU2\r',
            '3': '#NU3\r',
            '4': '#NU4\r',
            '5': '#NU5\r',
            '6': '#NU6\r',
            '7': '#NU7\r',
            '8': '#NU8\r',
            '9': '#NU9\r',
            '0': '#NU0\r',
            'Clear': '#CLR\r'
            }
        KeypadCmdString = KeypadStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Home': '#HOM\r',
            'Page Up': '#PUP\r',
            'Page Down': '#PDN\r',
            'Top Menu': '#TTL\r',
            'Pop-Up Menu': '#MNU\r',
            'Setup': '#SET\r',
            'Return': '#RET\r',
            'Up': '#NUP\r',
            'Down': '#NDN\r',
            'Left': '#NLT\r',
            'Right': '#NRT\r',
            'Enter': '#SEL\r'
            }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '#OSD\r'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetOption(self, value, qualifier):

        OptionCmdString = '#OPT\r'
        self.__SetHelper('Option', OptionCmdString, value, qualifier)

    def SetPIP(self, value, qualifier):

        PIPCmdString = '#PIP\r'
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePlaybackStatus(self, value, qualifier):

        PlaybackStatusCmdString = '#QPL\r'
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):

        PlaybackStatusStateNames = {
            'NO DISC': 'No Disc',
            'DISC': 'No Disc',
            'LOADING': 'Loading',
            'LOAD': 'Loading',
            'OPEN': 'Open',
            'CLOSE': 'Close',
            'CLOS': 'Close',
            'PLAY': 'Play',
            'PAUSE': 'Pause',
            'PAUS': 'Pause',
            'STOP': 'Stop',
            'STEP': 'Step',
            'STPF': 'Step Forward',
            'STPR': 'Step Reverse',
            'FREV': 'Fast Reverse',
            'FRV1': 'Fast Reverse',
            'FRV2': 'Fast Reverse',
            'FRV3': 'Fast Reverse',
            'FRV4': 'Fast Reverse',
            'FRV5': 'Fast Reverse',
            'FFWD': 'Fast Forward',
            'FFW1': 'Fast Forward',
            'FFW2': 'Fast Forward',
            'FFW3': 'Fast Forward',
            'FFW4': 'Fast Forward',
            'FFW5': 'Fast Forward',
            'SREV': 'Slow Reverse',
            'SRV1': 'Slow Reverse',
            'SRV2': 'Slow Reverse',
            'SRV3': 'Slow Reverse',
            'SRV4': 'Slow Reverse',
            'SFWD': 'Slow Forward',
            'SFW1': 'Slow Forward',
            'SFW2': 'Slow Forward',
            'SFW3': 'Slow Forward',
            'SFW4': 'Slow Forward',
            'SETUP': 'Setup',
            'HOME MENU': 'Home Menu',
            'HOME': 'Home Menu',
            'MEDIA CENTER': 'Media Center',
            'MCTR': 'Media Center'
            }
        value = PlaybackStatusStateNames[match.group(3).decode()]
        self.WriteStatus('PlaybackStatus', value, None)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '#PON\r',
            'Off': '#POF\r'
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '#QPW\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',
            'ON': 'On',
            'OFF': 'Off'
            }

        value = PowerStateNames[match.group(3).decode()]
        self.WriteStatus('Power', value, None)

    def SetPureAudio(self, value, qualifier):

        PureAudioCmdString = '#PUR\r'
        self.__SetHelper('PureAudio', PureAudioCmdString, value, qualifier)

    def SetRed(self, value, qualifier):

        RedCmdString = '#RED\r'
        self.__SetHelper('Red', RedCmdString, value, qualifier)

    def SetSetup(self, value, qualifier):

        SetupCmdString = '#SET\r'
        self.__SetHelper('Setup', SetupCmdString, value, qualifier)

    def SetSubtitle(self, value, qualifier):

        SubtitleCmdString = '#SUB\r'
        self.__SetHelper('Subtitle', SubtitleCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        TransportStateValues = {
            'Play': '#PLA\r',
            'Pause': '#PAU\r',
            'Stop': '#STP\r',
            'Previous': '#PRE\r',
            'Reverse': '#REV\r',
            'Forward': '#FWD\r',
            'Next': '#NXT\r',
            'Eject': '#EJT\r',
            'Repeat': '#RPT\r',
            }

        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '#SVL {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '#QVL\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(3).decode())
        self.WriteStatus('Volume', value, None)

    def SetYellow(self, value, qualifier):

        YellowCmdString = '#YLW\r'
        self.__SetHelper('Yellow', YellowCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.ConnectionType == 'Ethernet':
            commandstring = 'REMOTE ' + commandstring[1:-1]
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            if self.ConnectionType == 'Ethernet':
                commandstring = 'REMOTE ' + commandstring[1:-1]
                
            self.Send(commandstring)


    def __MatchError(self, match, tag):
        value = match.group(1).decode()
        print('Error Occurred When Executing Command: ', value)
    
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetOnConnectedString( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def oppo_3_261_serial(self):

        self.AppsStateValues = {
            'Netflix'                   : '#APP NFX\r',
            'YouTube'                   : '#APP YOU\r',
            'VUDU'                      : '#APP VUD\r',
            'Pandora'                   : '#APP PAN\r',
            'Berliner Philharmoniker'   : '#APP BER\r',
            'Picasa'                    : '#APP PIC\r',
            'Rhapsody'                  : '#APP RHA\r',
            'CinemaNow'                 : '#APP CIN\r'
            }

    def oppo_3_261_tcp(self):

        self.AppsStateValues = {
            'Netflix'                   : '#APP NFX\r',
            'YouTube'                   : '#APP YOU\r',
            'VUDU'                      : '#APP VUD\r',
            'Pandora'                   : '#APP PAN\r',
            'Picasa'                    : '#APP PIC\r',
            'Rhapsody'                  : '#APP RHA\r',
            'CinemaNow'                 : '#APP CIN\r'
            }
        
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
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
    
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
                
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
