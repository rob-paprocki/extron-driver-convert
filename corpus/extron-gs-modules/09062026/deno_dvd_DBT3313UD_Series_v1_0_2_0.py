from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re


class DeviceClass():
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Angle': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'CurrentChapterTrackNum': {'Status': {}},
            'CurrentTitleAlbumNum': {'Status': {}},
            'DiscTypeStatus': {'Status': {}},
            'Function': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuCall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'RepeatMode': {'Status': {}},
            'SearchTitle': {'Status': {}},
            'SearchTrack': {'Status': {}},
            'SubtitleLanguage': {'Status': {}},
            'Subtitles': {'Status': {}},
            'Transport': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'TMS ([0-9]{3})/([0-9]{4})[0-9A-Z/]{14}\r'), self.__MatchCurrentChapterTrackNum, None)
            self.AddMatchString(re.compile(b'PS (CDDA|CDRM|DVDV|DVDA|DVVR|SACD|DLNA|AVCR|AVCH|WEBS|EXTM|BDMV|BDAV|NODC)/(PLAY|PAUS|STOP|FFFW|FFRV|SLFW|SLRV|STUP|OPEN|CLOS|HOME|LOAD|MENU|RESM)[0-9A-Za-z/]{14}\r'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(re.compile(b'PW (ON|OFF)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'AUDSP [0-9A-Z+/]{12}(JP|EN|FR|DE|IT|ES|NI|ZH|RU|KO|OH)\r'), self.__MatchSubtitleLanguage, None)
        

    def SetAngle(self, value, qualifier):
        AngleCmdString = 'KYANGL UP\r'
        self.__SetHelper('Angle', AngleCmdString, value, qualifier)


    def SetAspectRatio(self, value, qualifier):
        AspectRatioStateValues = {
            '16:9': 'SUVIASP 16:9\r',
            '16:9 Wide': 'SUVIASP WIDE\r'
        }
        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)


    def UpdateCurrentChapterTrackNum(self, value, qualifier):

        CurrentChapterTrackNumCmdString = 'TMS?\r'
        self.__UpdateHelper('CurrentChapterTrackNum', CurrentChapterTrackNumCmdString, value, qualifier)

    def __MatchCurrentChapterTrackNum(self, match, tag):

        TitleGroupValue = int(match.group(1).decode())
        ChapterTrackValue = int(match.group(2).decode())

        self.WriteStatus('CurrentTitleAlbumNum', TitleGroupValue, None)
        self.WriteStatus('CurrentChapterTrackNum', ChapterTrackValue, None)

    def UpdateCurrentTitleAlbumNum(self, value, qualifier):

        CurrentChapterTrackNumCmdString = 'TMS?\r'
        self.__UpdateHelper('CurrentTitleAlbumNum', CurrentChapterTrackNumCmdString, value, qualifier)

    def __MatchCurrentTitleAlbumNum(self, match, tag):
        pass

    def UpdateDiscTypeStatus(self, value, qualifier):
        DiscTypeStatus = 'PS?\r'
        self.__UpdateHelper('DiscTypeStatus', DiscTypeStatus, value, qualifier)

    def __MatchDiscTypeStatus(self, match, tag):
        pass

    def SetFunction(self, value, qualifier):
        FunctionStateValues = {
            'Clear': 'KYCLEAR\r',
            'Program': 'KYPRGNML\r',
            'Setup': 'KYSETUP\r',
            'Display': 'KYDISP\r',
            'Random': 'KYRAND CH\r'
        }
        FunctionCmdString = FunctionStateValues[value]
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)


    def SetKeypad(self, value, qualifier):
        KeypadStateValues = {
            '0': 'KYNUM 0\r',
            '1': 'KYNUM 1\r',
            '2': 'KYNUM 2\r',
            '3': 'KYNUM 3\r',
            '4': 'KYNUM 4\r',
            '5': 'KYNUM 5\r',
            '6': 'KYNUM 6\r',
            '7': 'KYNUM 7\r',
            '8': 'KYNUM 8\r',
            '9': 'KYNUM 9\r',
            '+10': 'KYNUM P\r'
        }
        KeypadCmdString = KeypadStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier, 3)


    def SetMenuCall(self, value, qualifier):
        MenuCallStateValues = {
            'Top Menu': 'KYTMENU\r',
            'Home': 'KYHOME\r'
        }
        MenuCallCmdString = MenuCallStateValues[value]
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier, 3)


    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationStateValues = {
            'Up': 'KYCR UP\r',
            'Down': 'KYCR DW\r',
            'Left': 'KYCR LT\r',
            'Right': 'KYCR RT\r',
            'Menu': 'KYPMENU\r',
            'Return': 'KYRETURN\r',
            'Enter': 'KYENTER\r'
        }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)


    def UpdatePlaybackStatus(self, value, qualifier):
        PlaybackStatusCmdString = 'PS?\r'
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):
        PlayBackStateNames = {
            'PLAY': 'Playing',
            'PAUS': 'Paused',
            'STOP': 'Stopped',
            'FFFW': 'Fast Forward',
            'FFRV': 'Fast Reverse',
            'SLFW': 'Slow Forward',
            'SLRV': 'Slow Reverse',
            'STUP': 'Setup',
            'OPEN': 'Tray Opening',
            'CLOS': 'Tray Closing',
            'HOME': 'Home',
            'MENU': 'DVD Menus',
            'LOAD': 'Disk Loading',
            'RESM': 'Resume Stop',
        }

        DiscTypeStateNames = {
            'CDDA': 'CD-DA',
            'CDRM': 'CD-ROM',
            'DVDV': 'DVD Video',
            'DVDA': 'DVD Audio',
            'DVVR': 'DVD VR',
            'SACD': 'Super Audio CD',
            'DLNA': 'DLNA',
            'AVCR': 'AVCREC',
            'AVCH': 'AVCHD',
            'WEBS': 'Web Stream',
            'EXTM': 'External Memory',
            'BDMV': 'BDMV',
            'BDAV': 'BDAV',
            'NODC': 'No Disc',
        }
        DiscTypeState = DiscTypeStateNames[match.group(1).decode()]
        PlaybackState = PlayBackStateNames[match.group(2).decode()]

        self.WriteStatus('DiscTypeStatus', DiscTypeState, None)
        self.WriteStatus('PlaybackStatus', PlaybackState, None)

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On': 'KYPW ON\r',
            'Off': 'KYPW OF\r'
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        PowerStateNames = {
            'ON': 'On',
            'OFF': 'Off'
        }
        PowerState = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', PowerState, None)

    def SetRepeatMode(self, value, qualifier):
        RepeatModeStateValues = {
            'Repeat': 'KYRPT CH\r',
            'AB': 'KYRPT AB\r'
        }

        RepeatModeCmdString = RepeatModeStateValues[value]
        self.__SetHelper('RepeatMode', RepeatModeCmdString, value, qualifier)


    def SetSearchTitle(self, value, qualifier):
        SearchTitleConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if SearchTitleConstraints['Min'] <= value <= SearchTitleConstraints['Max']:
            SearchTitleCmdString = 'KYDT {0:04d}\r'.format(value)
            self.__SetHelper('SearchTitle', SearchTitleCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetSearchTitle')


    def SetSearchTrack(self, value, qualifier):
        SearchTrackConstraints = {
            'Min': 1,
            'Max': 9999
        }

        if SearchTrackConstraints['Min'] <= value <= SearchTrackConstraints['Max']:
            SearchTrackCmdString = 'KYDC {0:04d}\r'.format(value)
            self.__SetHelper('SearchTrack', SearchTrackCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetSearchTrack')


    def SetSubtitles(self, value, qualifier):
        SubtitlesStateValues = {
            'Primary': 'KYPSUB UP\r',
            'Secondary': 'KYSSUB UP\r',
            'Toggle': 'KYSTYL UP\r'
        }
        SubtitlesCmdString = SubtitlesStateValues[value]
        self.__SetHelper('Subtitles', SubtitlesCmdString, value, qualifier)


    def UpdateSubtitleLanguage(self, value, qualifier):

        SubtitleLanguageCmdString = 'AUDSP?\r'
        self.__UpdateHelper('SubtitleLanguage', SubtitleLanguageCmdString, value, qualifier)

    def __MatchSubtitleLanguage(self, match, tag):
        SubLangStateNames = {
            'JP': 'Japanese',
            'EN': 'English',
            'FR': 'Francais',
            'DE': 'Deutsch',
            'IT': 'Italiano',
            'ES': 'Espanol',
            'NI': 'Netherlands',
            'ZH': 'Chinese',
            'RU': 'Russian',
            'KO': 'Korean',
            'OH': 'Other'
        }
        value = SubLangStateNames[match.group(1).decode()]
        self.WriteStatus('SubtitleLanguage', value, None)

    def SetTransport(self, value, qualifier):
        TransportStateValues = {
            'Play': 'KYPLAY\r',
            'Stop': 'KYSTOP\r',
            'Pause': 'KYPAUS\r',
            'Next': 'KYSK FW\r',
            'Previous': 'KYSK RV\r',
            'FFwd': 'KYSE FW\r',
            'Rew': 'KYSE RV\r',
            'Eject': 'KYTY EJ\r'
        }
        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier, 3)
            

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)
                
            

    def __MatchError(self, match, tag):
        pass

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

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

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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

