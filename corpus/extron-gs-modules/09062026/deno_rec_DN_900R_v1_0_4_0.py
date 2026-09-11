from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AlbumName': {'Status': {}},
            'ArtistName': {'Status': {}},
            'CurrentFolderName': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'DualRecording': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FolderName': {'Parameters': ['Number'], 'Status': {}},
            'FolderNumber': {'Status': {}},
            'Media': {'Status': {}},
            'MediaStatus': {'Status': {}},
            'PlaybackMode': {'Status': {}},
            'Power': {'Status': {}},
            'Random': {'Status': {}},
            'Record': {'Status': {}},
            'RemainingRecordTime': {'Status': {}},
            'RemainingTime': {'Status': {}},
            'Repeat': {'Status': {}},
            'Search': {'Status': {}},
            'TotalFolderNumbers': {'Status': {}},
            'TracklistSize': {'Status': {}},
            'TrackName': {'Status': {}},
            'TrackNameLong': {'Status': {}},
            'TrackNameofSpecifiedFile': {'Parameters': ['Number'], 'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
        }

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        self.regex = re.compile(rb'\x06@0[\S ]+\r|\x15|@0BDERBUSY')

    def UpdateAlbumName(self, value, qualifier):

        AlbumNameCmdString = '@0?al\r'
        res = self.__UpdateHelper('AlbumName', AlbumNameCmdString, value, qualifier)
        if res:
            try:
                value = res[5:-1] if res[5:-1] else 'None'
                self.WriteStatus('AlbumName', value, qualifier)
            except IndexError:
                self.Error(['Album Name: Invalid/unexpected response'])

    def UpdateArtistName(self, value, qualifier):

        ArtistNameCmdString = '@0?at\r'
        res = self.__UpdateHelper('ArtistName', ArtistNameCmdString, value, qualifier)
        if res:
            try:
                value = res[5:-1] if res[5:-1] else 'None'
                self.WriteStatus('ArtistName', value, qualifier)
            except IndexError:
                self.Error(['Artist Name: Invalid/unexpected response'])

    def UpdateCurrentFolderName(self, value, qualifier):

        CurrentFolderNameCmdString = '@0?SF\r'
        res = self.__UpdateHelper('CurrentFolderName', CurrentFolderNameCmdString, value, qualifier)
        if res:
            try:
                value = res[6:-1] if res[6:-1] else 'None'
                self.WriteStatus('CurrentFolderName', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Folder Name: Invalid/unexpected response'])

    def UpdateCurrentTrackTime(self, value, qualifier):

        CurrentTrackTimeCmdString = '@0?tl\r'
        res = self.__UpdateHelper('CurrentTrackTime', CurrentTrackTimeCmdString, value, qualifier)
        if res:
            try:
                hoursMinutes = divmod(int(res[5:8]), 60)  # format: (hh, mm)
                value = '{}:{}:{}'.format(str(hoursMinutes[0]).zfill(2), str(hoursMinutes[1]).zfill(2), res[8:10])  # format: hh:mm:ss
                self.WriteStatus('CurrentTrackTime', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Track Time: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'RE': 'Recording',
            'RP': 'Recording Paused',
            'RU': 'DIR Unlocked',
            'PL': 'Playing',
            'AB': 'A-B Repeat',
            'PP': 'Paused',
            'PR': 'Repeat Paused',
            'RW': 'Rewinding',
            'FF': 'Fast Forwarding',
            'ST': 'Stopped',
            'CU': 'Cued',
            'CE': 'Cued',  # obtained from testing w/ device
            'AC': 'Autocued',
            'SH': 'Timer Standby',
            'LD': 'Loading',
            'BY': 'Busy',
            'FL': 'File List Opening',
            'ED': 'Main Menu Opening',
            'ER': 'Error'
        }

        DeviceStatusCmdString = '@0?ST\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetDualRecording(self, value, qualifier):

        ValueStateValues = {
            'Off': 'OF',
            'SD 1': 'S1',
            'SD 2': 'S2',
            'USB': 'US'
        }

        if value in ValueStateValues:
            DualRecordingCmdString = '@0dR{}\r'.format(ValueStateValues[value])
            self.__SetHelper('DualRecording', DualRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDualRecording')

    def UpdateDualRecording(self, value, qualifier):

        ValueStateValues = {
            'OF': 'Off',
            'S1': 'SD 1',
            'S2': 'SD 2',
            'US': 'USB'
        }

        DualRecordingCmdString = '@0?dR\r'
        res = self.__UpdateHelper('DualRecording', DualRecordingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('DualRecording', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Dual Recording: Invalid/unexpected response'])

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = '@0?ET\r'
        res = self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{}:{}:{}'.format(res[5:8], res[8:10], res[10:12])  # format: hhh:mm:ss
                self.WriteStatus('ElapsedTime', value, qualifier)
            except IndexError:
                self.Error(['Elapsed Time: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'All Keys Locked': 'L',
            'All Keys Unlocked': 'U',
            'Keys Restricted': 'S',
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '@023K{}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'LK': 'All Keys Locked',
            'UL': 'All Keys Unlocked',
            'SL': 'Keys Restricted',
        }

        ExecutiveModeCmdString = '@0?LS\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def UpdateFolderName(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= number_val <= 2000:
            FolderNameCmdString = '@0?Fn{0:04d}\r'.format(number_val)
            res = self.__UpdateHelper('FolderName', FolderNameCmdString, value, qualifier)
            if res:
                try:
                    value = res[5:-1] if res[5:-1] else 'None'
                    self.WriteStatus('FolderName', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Folder Name: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFolderName')

    def SetFolderNumber(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 2000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FolderNumberCmdString = '@0Sf{0:04d}\r'.format(value)
            self.__SetHelper('FolderNumber', FolderNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFolderNumber')

    def SetMedia(self, value, qualifier):

        ValueStateValues = {
            'SD 1': 'S1',
            'SD 2': 'S2',
            'USB': 'US',
            'Network': 'NE'
        }

        if value in ValueStateValues:
            MediaCmdString = '@0MM{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Media', MediaCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMedia')

    def UpdateMedia(self, value, qualifier):

        ValueStateValues = {
            'S1': 'SD 1',
            'S2': 'SD 2',
            'US': 'USB',
            'NE': 'Network'
        }

        MediaCmdString = '@0?MM\r'
        res = self.__UpdateHelper('Media', MediaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('Media', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Media: Invalid/unexpected response'])

    def UpdateMediaStatus(self, value, qualifier):

        ValueStateValues = {
            'CI': 'SD Card In',
            'NC': 'SD Card Out',
            'CE': 'SD Card Error',
            'UF': 'Unformatted SD Card',
            'WP': 'Write Protected SD',
            'DO': 'SD Card Door Opened'
        }

        MediaStatusCmdString = '@0?CD\r'
        res = self.__UpdateHelper('MediaStatus', MediaStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('MediaStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Media Status: Invalid/unexpected response'])

    def SetPlaybackMode(self, value, qualifier):

        ValueStateValues = {
            'Single Play': 'SP',
            'Continuous': 'CN'
        }

        if value in ValueStateValues:
            PlaybackModeCmdString = '@0PM{}\r'.format(ValueStateValues[value])
            self.__SetHelper('PlaybackMode', PlaybackModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaybackMode')

    def UpdatePlaybackMode(self, value, qualifier):

        ValueStateValues = {
            'SP': 'Single Play',
            'CN': 'Continuous'
        }

        PlaybackModeCmdString = '@0?PM\r'
        res = self.__UpdateHelper('PlaybackMode', PlaybackModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('PlaybackMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Playback Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '@023PW\r',
            'Standby': '@02312\r',
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier, PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Standby',
            '2': 'Network Standby'
        }

        PowerCmdString = '@0?PW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'On': '1',  # based on testing, command strings are opposite of whats shown in protocol
            'Off': '0'
        }

        if value in ValueStateValues:
            RandomCmdString = '@0RN0{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Random', RandomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRandom')

    def UpdateRandom(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        RandomCmdString = '@0?RN\r'
        res = self.__UpdateHelper('Random', RandomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6]]
                self.WriteStatus('Random', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Random: Invalid/unexpected response'])

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start': '@02355\r',
            'Pause': '@023Rp\r',
            'Split': '@023MT\r'
        }

        if value in ValueStateValues:
            RecordCmdString = ValueStateValues[value]
            self.__SetHelper('Record', RecordCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecord')

    def UpdateRemainingRecordTime(self, value, qualifier):

        RemainingRecordTimeCmdString = '@0?RT\r'
        res = self.__UpdateHelper('RemainingRecordTime', RemainingRecordTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{}:{}:{}'.format(res[5:8], res[8:10], res[10:12])  # format: hhh:mm:ss
                self.WriteStatus('RemainingRecordTime', value, qualifier)
            except IndexError:
                self.Error(['Remaining Record Time: Invalid/unexpected response'])

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = '@0?RM\r'
        res = self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{}:{}:{}'.format(res[5:8], res[8:10], res[10:12])  # format: hhh:mm:ss
                self.WriteStatus('RemainingTime', value, qualifier)
            except IndexError:
                self.Error(['Remaining Time: Invalid/unexpected response'])

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        if value in ValueStateValues:
            RepeatCmdString = '@0RE0{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRepeat')

    def UpdateRepeat(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        RepeatCmdString = '@0?RE\r'
        res = self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6]]
                self.WriteStatus('Repeat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Repeat: Invalid/unexpected response'])

    def SetSearch(self, value, qualifier):

        ValueStateValues = {
            'Rewind': '@02350\r',
            'Skip Back': '@023SB\r',
            'Fast Forward': '@02352\r'
        }

        if value in ValueStateValues:
            SearchCmdString = ValueStateValues[value]
            self.__SetHelper('Search', SearchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSearch')

    def UpdateTotalFolderNumbers(self, value, qualifier):

        TotalFolderNumbersCmdString = '@0?Tf\r'
        res = self.__UpdateHelper('TotalFolderNumbers', TotalFolderNumbersCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:9])
                self.WriteStatus('TotalFolderNumbers', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Total Folder Numbers: Invalid/unexpected response'])

    def UpdateTracklistSize(self, value, qualifier):

        TracklistSizeCmdString = '@0?Tt\r'
        res = self.__UpdateHelper('TracklistSize', TracklistSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:9])
                self.WriteStatus('TracklistSize', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Tracklist Size: Invalid/unexpected response'])

    def UpdateTrackName(self, value, qualifier):

        TrackNameCmdString = '@0?ti\r'
        res = self.__UpdateHelper('TrackName', TrackNameCmdString, value, qualifier)
        if res:
            try:
                value = res[5:-1] if res[5:-1] else 'None'
                self.WriteStatus('TrackName', value, qualifier)
            except IndexError:
                self.Error(['Track Name: Invalid/unexpected response'])

    def UpdateTrackNameLong(self, value, qualifier):

        TrackNameLongCmdString = '@0?T1\r'
        res = self.__UpdateHelper('TrackNameLong', TrackNameLongCmdString, value, qualifier)
        if res:
            try:
                value = res[5:-1] if res[5:-1] else 'None'
                self.WriteStatus('TrackNameLong', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Track Name Long: Invalid/unexpected response'])

    def UpdateTrackNameofSpecifiedFile(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= number_val <= 2000:
            TrackNameofSpecifiedFileCmdString = '@0?tn{0:04d}\r'.format(number_val)
            res = self.__UpdateHelper('TrackNameofSpecifiedFile', TrackNameofSpecifiedFileCmdString, value, qualifier)
            if res:
                try:
                    value = res[5:-1] if res[5:-1] else 'None'
                    self.WriteStatus('TrackNameofSpecifiedFile', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Track Name of Specified File: Invalid/unexpected response'])

    def SetTrackNumber(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 2000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrackNumberCmdString = '@0Tr{0:04}\r'.format(value)
            self.__SetHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackNumber')

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?Tr\r'
        res = self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:9]) if int(res[5:9]) != 0 else 1
                self.WriteStatus('TrackNumber', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Track Number: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@02353\r',
            'Pause': '@02348\r',
            'Stop': '@02354\r',
            'Next': '@02332\r',
            'Previous': '@02333\r'
        }

        if value in ValueStateValues:
            TransportCmdString = ValueStateValues[value]
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if 'Unauthorized' in response and 'Serial' not in self.ConnectionType:  # if device returns not authenticated response for Ethernet
            res = self.SendAndWait('@0?LIAD:{}\r'.format(self.devicePassword), self.DefaultResponseTimeout, deliRex=self.regex).decode()  # send login command
            if res:
                if 'LIOK' in res:  # if authentication successful
                    self.Authenticated = 'Authenticated'
                elif 'LING' in res:  # if authentication failed
                    self.Authenticated = 'Invalid'  # stop sending queries
                else:
                    self.PasswdPromptCount += 1
                    if self.PasswdPromptCount > 1:  # ensures login command only sends twice
                        self.Authenticated = 'Invalid'
            else:
                self.PasswdPromptCount += 1
                if self.PasswdPromptCount > 1:
                    self.Authenticated = 'Invalid'
        elif '\x15' in response:
            self.Error(['{}: Unknown/invalid command'.format(sourceCmdName)])
            response = ''
        elif '@0BDERBUSY' in response:
            self.Error(['Device is busy'])
            response = ''
        else:
            if self.Authenticated != 'Authenticated' and 'Serial' not in self.ConnectionType:  # prevents flag from being set multiple times for Ethernet
                self.Authenticated = 'Authenticated'  # set flag to authenticated for Ethernet if no password is set
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated == 'Authenticated' or 'Serial' in self.ConnectionType:  # if authenticated or serial
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated != 'Invalid':
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            if command == 'Power' and 'Serial' not in self.ConnectionType:  # only send error message for heartbeat command for Ethernet
                self.Error(['Login failed. Please supply correct password'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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