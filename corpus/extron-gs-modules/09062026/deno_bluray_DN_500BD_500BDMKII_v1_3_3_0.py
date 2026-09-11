from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AlbumName': {'Status': {}},
            'ArtistName': {'Status': {}},
            'ChapterorTrack': {'Status': {}},
            'ChapterorTrackTotal': {'Status': {}},
            'ColorFunction': {'Status': {}},
            'CurrentTitle': {'Status': {}},
            'CurrentTitleTotal': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'DiscTray': {'Status': {}},
            'DisplayInfo': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'Keypad': {'Status': {}},
            'Language': {'Parameters': ['Mode'], 'Status': {}},
            'MediaStatus': {'Status': {}},
            'Mute': {'Status': {}},
            'MediaType': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'PowerOff': {'Status': {}},
            'RandomMode': {'Status': {}},
            'RemainingTime': {'Status': {}},
            'Repeat': { 'Status': {}},
            'Search': {'Parameters': ['Direction', 'Speed'], 'Status': {}},
            'Subtitle': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.regex_DeviceStatus = re.compile(b'ack\+@0ST(PL|PP|DVSR|DVSF|DVFR|DVFF|DVSP|ED|DVSU|DVTR|DVHM)')

    def UpdateAlbumName(self, value, qualifier):

        AlbumNameCmdString = '@0?al\r'
        res = self.__UpdateHelper('AlbumName', AlbumNameCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[8:12] == 'NULL':
                    value = 'No Info'
                elif res[0:8] == 'ack+@0al':
                    value = res[8:]

                if value:
                    self.WriteStatus('AlbumName', value, qualifier)
                else:
                    self.Error(['Album Name: Invalid/unexpected response'])
            except IndexError:
                self.Error(['Album Name: Invalid/unexpected response'])

    def UpdateArtistName(self, value, qualifier):

        ArtistNameCmdString = '@0?at\r'
        res = self.__UpdateHelper('ArtistName', ArtistNameCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[8:12] == 'NULL':
                    value = 'No Info'
                elif res[0:8] == 'ack+@0at':
                    value = res[8:]

                if value:
                    self.WriteStatus('ArtistName', value, qualifier)
                else:
                    self.Error(['Artist Name: Invalid/unexpected response'])
            except IndexError:
                self.Error(['Artist Name: Invalid/unexpected response'])

    def SetChapterorTrack(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 2000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ChapterorTrackCmdString = '@0Tr{0:04}\r'.format(value)
            self.__SetHelper('ChapterorTrack', ChapterorTrackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChapterorTrack')

    def UpdateChapterorTrack(self, value, qualifier):

        ChapterorTrackCmdString = '@0?Tr\r'
        res = self.__UpdateHelper('ChapterorTrack', ChapterorTrackCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'UNKN' or res[4:9] == 'error':
                    value = 1
                elif res[0:8] == 'ack+@0Tr':
                    value = int(res[8:12])

                if value:
                    self.WriteStatus('ChapterorTrack', value, None)
                else:
                    self.Error(['Chapter or Track: Invalid/unexpected response'])
            except (IndexError, ValueError):
                self.Error(['Chapter or Track: Invalid/unexpected response'])

    def UpdateChapterorTrackTotal(self, value, qualifier):

        ChapterorTrackTotalCmdString = '@0?Tt\r'
        res = self.__UpdateHelper('ChapterorTrackTotal', ChapterorTrackTotalCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'UNKN' or res[4:9] == 'error':
                    value = 0
                elif res[0:8] == 'ack+@0Tt':
                    value = int(res[8:12])

                if isinstance(value, int):
                    self.WriteStatus('ChapterorTrackTotal', value, None)
                else:
                    self.Error(['Chapter or Track Total: Invalid/unexpected response'])
            except (IndexError, ValueError):
                self.Error(['Chapter or Track Total: Invalid/unexpected response'])

    def SetColorFunction(self, value, qualifier):

        ValueStateValues = {
            'Red': '1',
            'Green': '2',
            'Blue': '3',
            'Yellow': '4',
        }

        if value in ValueStateValues:
            ColorCmdString = '@0DVFCLR{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('ColorFunction', ColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorFunction')

    def SetCurrentTitle(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 2000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CurrentTitleCmdString = '@0PCGp{0:04}\r'.format(value)
            self.__SetHelper('CurrentTitle', CurrentTitleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCurrentTitle')

    def UpdateCurrentTitle(self, value, qualifier):

        CurrentTitleCmdString = '@0?PCGp\r'
        res = self.__UpdateHelper('CurrentTitle', CurrentTitleCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'UNKN' or res[4:9] == 'error':
                    value = 1
                elif res[0:10] == 'ack+@0PCGp':
                    value = int(res[10:14])

                if value:
                    self.WriteStatus('CurrentTitle', value, None)
                else:
                    self.Error(['Current Title: Invalid/unexpected response'])
            except (IndexError, ValueError):
                self.Error(['Current Title: Invalid/unexpected response'])

    def UpdateCurrentTitleTotal(self, value, qualifier):

        CurrentTitleTotalCmdString = '@0?PCTG\r'
        res = self.__UpdateHelper('CurrentTitleTotal', CurrentTitleTotalCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'UNKN' or res[4:9] == 'error':
                    value = 0
                elif res[0:10] == 'ack+@0PCTG':
                    value = int(res[10:14])

                if isinstance(value, int):
                    self.WriteStatus('CurrentTitleTotal', value, None)
                else:
                    self.Error(['Current Title Total: Invalid/unexpected response'])
            except (IndexError, ValueError):
                self.Error(['Current Title Total: Invalid/unexpected response'])

    def UpdateCurrentTrackTime(self, value, qualifier):

        CurrentTrackTimeCmdString = '@0?tl\r'
        res = self.__UpdateHelper('CurrentTrackTime', CurrentTrackTimeCmdString, value, qualifier)
        if res:
            try:
                if res[0:8] == 'ack+@0tl':
                    hoursMinutes = divmod(int(res[8:11]), 60)  # format: (hh, mm)
                    value = '{}:{}:{}'.format(str(hoursMinutes[0]).zfill(2), str(hoursMinutes[1]).zfill(2), res[11:13])  # format: hh:mm:ss
                    self.WriteStatus('CurrentTrackTime', value, None)
                else:
                    self.Error(['Current Track Time: Invalid/unexpected response'])
            except(IndexError, ValueError):
                self.Error(['Current Track Time: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'PL': 'Play',
            'PP': 'Pause',
            'DVSR': 'Slow Play Reverse',
            'DVSF': 'Slow Play Forward',
            'DVFR': 'Fast Play Reverse',
            'DVFF': 'Fast Play Forward',
            'DVSP': 'Step Play',
            'ED': 'Menu',
            'DVSU': 'Setup',
            'DVTR': 'Track Menu',
            'DVHM': 'Home'
        }

        DeviceStatusCmdString = '@0?ST\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ''
                match = re.search(self.regex_DeviceStatus, res.encode())
                if match:
                    value = ValueStateValues[match.group(1).decode()]
                elif res[0:4] == 'ack+':
                    value = 'Other'

                if value:
                    self.WriteStatus('DeviceStatus', value, None)
                else:
                    self.Error(['Device Status: Invalid/unexpected response'])
            except(KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetDiscTray(self, value, qualifier):

        ValueStateValues = {
            'Open': '@0PCDTRYOP\r',
            'Close': '@0PCDTRYCL\r'
        }

        if value in ValueStateValues:
            DiscTrayCmdString = ValueStateValues[value]
            self.__SetHelper('DiscTray', DiscTrayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDiscTray')

    def SetDisplayInfo(self, value, qualifier):

        DisplayInfoCmdString = '@0DVDSIF\r'
        self.__SetHelper('DisplayInfo', DisplayInfoCmdString, value, qualifier)

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = '@0?ET\r'
        res = self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'error':
                    value = '000:00:00'
                elif res[0:4] == 'ack+':
                    value = '{}:{}:{}'.format(res[4:7], res[7:9], res[9:11])  # format: hhh:mm:ss

                if value:
                    self.WriteStatus('ElapsedTime', value, qualifier)
                else:
                    self.Error(['Elapsed Time: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Elapsed Time: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '@023KL\r',
            'Off': '@023KU\r'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '@0PCTKEY0\r',
            '1': '@0PCTKEY1\r',
            '2': '@0PCTKEY2\r',
            '3': '@0PCTKEY3\r',
            '4': '@0PCTKEY4\r',
            '5': '@0PCTKEY5\r',
            '6': '@0PCTKEY6\r',
            '7': '@0PCTKEY7\r',
            '8': '@0PCTKEY8\r',
            '9': '@0PCTKEY9\r'
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetLanguage(self, value, qualifier):

        ModeStates = {
            'Audio': 'GAD',
            'Disc Menu': 'GDM',
            'OSD': 'GOS',
            'Subtitle': 'GST'
        }

        ValueStateValues = {
            'English': 'eng',
            'French': 'fra',
            'Spanish': 'spa',
            'German': 'deu',
            'Dutch': 'nld',
            'Chinese': 'zho',
            'Italian': 'ita',
            'Portuguese': 'por',
            'Danish': 'dan',
            'Swedish': 'swe',
            'Finnish': 'fin',
            'Norwegian': 'nor',
            'Russian': 'rus',
            'Korean': 'kor',
            'Japanese': 'jpn',
            'Off': 'OFF'
        }

        if qualifier['Mode'] in ModeStates and value in ValueStateValues:
            LanguageCmdString = '@0DVL{0}{1}\r'.format(ModeStates[qualifier['Mode']], ValueStateValues[value])
            self.__SetHelper('Language', LanguageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLanguage')

    def UpdateLanguage(self, value, qualifier):

        ModeStates = {
            'Audio': 'GAD',
            'Disc Menu': 'GDM',
            'OSD': 'GOS',
            'Subtitle': 'GST'
        }

        ModeValues = {
            'GAD': 'Audio',
            'GDM': 'Disc Menu',
            'GOS': 'OSD',
            'GST': 'Subtitle'
        }

        ValueStateValues = {
            'eng': 'English',
            'fra': 'French',
            'spa': 'Spanish',
            'deu': 'German',
            'nld': 'Dutch',
            'zho': 'Chinese',
            'ita': 'Italian',
            'por': 'Portuguese',
            'dan': 'Danish',
            'swe': 'Swedish',
            'fin': 'Finnish',
            'nor': 'Norwegian',
            'rus': 'Russian',
            'kor': 'Korean',
            'jpn': 'Japanese',
            'OFF': 'Off'
        }

        LanguageCmdString = '@0?DVL{0}\r'.format(ModeStates[qualifier['Mode']])
        res = self.__UpdateHelper('Language', LanguageCmdString, value, qualifier)
        if res:
            try:
                mode = ModeValues[res[9:12]]
                value = ValueStateValues[res[12:15]]
                self.WriteStatus('Language', value, {'Mode': mode})
            except(KeyError, IndexError):
                self.Error(['Language: Invalid/unexpected response'])

    def UpdateMediaStatus(self, value, qualifier):

        ValueStateValues = {
            'NC': 'No Disc',
            'CI': 'Disc In',
            'UF': 'Unformatted Disc',
            'TO': 'Tray Open',
            'TC': 'Tray Closed',
            'TE': 'Tray Error'
        }

        MediaStatusCmdString = '@0?CD\r'
        res = self.__UpdateHelper('MediaStatus', MediaStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:10]]
                self.WriteStatus('MediaStatus', value, None)
            except(KeyError, IndexError):
                self.Error(['Media Status: Invalid/unexpected response'])

    def UpdateMediaType(self, value, qualifier):

        ValueStateValues = {
            'DVV': 'DVD Video',
            'DVA': 'DVD Audio',
            'DVR': 'DVD VR',
            'CDR': 'CD-ROM',
            'SAC': 'SACD',
            'CDA': 'CDDA',
            'BDM': 'BDMV',
            'BDA': 'BDAV',
            'AVH': 'AVCHD',
            'DLN': 'DLNA',
            'EXT': 'External Memory',
            'UKN': 'Unknown'
        }

        MediaTypeCmdString = '@0?PCTYP\r'
        res = self.__UpdateHelper('MediaType', MediaTypeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[11:14]]
                self.WriteStatus('MediaType', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Media Type: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Setup Menu': '@0PCSU\r',
            'Disc Menu': '@0DVTP\r',
            'Option Menu': '@0DVOP\r',
            'Pop Up Menu': '@0DVPU\r',
            'Return': '@0PCRTN\r',
            'Up': '@0PCCUSR3\r',
            'Down': '@0PCCUSR4\r',
            'Left': '@0PCCUSR1\r',
            'Right': '@0PCCUSR2\r',
            'Enter': '@0PCENTR\r',
            'Home': '@0PCHM\r',
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '@0mt00\r',
            'Off': '@0mt01\r'
        }

        if value in ValueStateValues:
            MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        MuteCmdString = '@0?mt\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[9]]
                self.WriteStatus('Mute', value, None)
            except(KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '@0PW00\r',
            'Off': '@0PW01\r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '@0?PW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        try:
            if res[0:3] == 'ack' or res[0] == '\x00':
                self.WriteStatus('Power', 'On', qualifier)
            else:
                self.WriteStatus('Power', 'Off', qualifier)
        except IndexError:
            self.Error(['Power: Invalid/unexpected response'])

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '@0PW01\r'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetRandomMode(self, value, qualifier):

        self.__SetHelper('RandomMode', '@0PCPMR\r', value, qualifier)

    def UpdateRandomMode(self, value, qualifier):

        ValueStateValues = {
            'S': 'Shuffle',
            'R': 'Random',
            'O': 'Off'
        }

        RandomModeCmdString = '@0?PCPMR\r'
        res = self.__UpdateHelper('RandomMode', RandomModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[11:12]]
                self.WriteStatus('RandomMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Random Mode: Invalid/unexpected response'])

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = '@0?RM\r'
        res = self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)
        if res:
            try:
                value = ''
                if res[4:9] == 'error':
                    value = '000:00:00'
                elif res[0:4] == 'ack+':
                    value = '{}:{}:{}'.format(res[4:7], res[7:9], res[9:11])  # format: hhh:mm:ss

                if value:
                    self.WriteStatus('RemainingTime', value, qualifier)
                else:
                    self.Error(['Remaining Time: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Remaining Time: Invalid/unexpected response'])

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Set A for A-B':          '@0PCRPAF\r',
            'Set B and Start Repeat': '@0PCRPBF\r',
            'Exit A-B':               '@0PCEXRP\r'
            }

        if value in ValueStateValues:
            RepeatCmdString = ValueStateValues[value]
            self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRepeat')

    def SetSearch(self, value, qualifier):

        SpeedStates = {
            'Fast': 'f',
            'Slow': 's'
        }

        DirectionStates = {
            'Forward': 'F',
            'Reverse': 'R'
        }

        if qualifier['Speed'] in SpeedStates and qualifier['Direction'] in DirectionStates:
            if qualifier['Speed'] == 'Slow' and qualifier['Direction'] == 'Reverse':  # bug in fw, Slow Reverse currently doesnt work
                self.Discard('Invalid Command for SetSearch')
            else:
                SearchCmdString = '@0PCSLS{0}{1}\r'.format(DirectionStates[qualifier['Direction']], SpeedStates[qualifier['Speed']])
                self.__SetHelper('Search', SearchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSearch')

    def SetSubtitle(self, value, qualifier):

        SubtitleCmdString = '@0DVSBTL1\r'
        self.__SetHelper('Subtitle', SubtitleCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop': '@02354\r',
            'Play': '@02353\r',
            'Pause': '@02348\r',
            'Track/Chapter Next': '@02332\r',
            'Track/Chapter Prev': '@02333\r',
            'Group/Title Next': '@0PCGPNX\r',
            'Group/Title Prev': '@0PCGPPV\r'
        }

        if value in ValueStateValues:
            TransportCmdString = ValueStateValues[value]
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -90,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == 0:
                VolumeCmdString = '@0DVOV000\r'
            else:
                VolumeCmdString = '@0DVOV-{0:02}\r'.format(value * -1)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '@0?DVOV\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10:13])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if 'nack' in response and sourceCmdName != 'Power':
            self.Error(['{0}: Unknown or invalid command'.format(sourceCmdName)])
            response = ''
        elif '@0BDERBUSY' in response:
            self.Error(['Device is busy'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)


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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)