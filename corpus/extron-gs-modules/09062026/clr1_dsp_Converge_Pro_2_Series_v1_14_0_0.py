from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog, Timer

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
        self._NumberofSkypeSearch = 5
        self.deviceUsername = 'clearone'
        self.devicePassword = 'converge'

        self.Models = {
            'Converge Pro 2 128TD': self.clr1_25_2525_normal_12,
            'Converge Pro 2 128V': self.clr1_25_2525_voip_12,
            'Converge Pro 2 128VD': self.clr1_25_2525_voip_12,
            'Converge Pro 2 120': self.clr1_25_2525_normal_12,
            'Converge Pro 2 48T': self.clr1_25_2525_normal_4,
            'Beamforming Microphone Array 2': self.clr1_25_2525_beamform,
            'Converge Pro 2 128D': self.clr1_25_2525_normal_12,
            'Converge Pro 2 128SR': self.clr1_25_2525_normal_12,
            'Converge Pro 2 128SRD': self.clr1_25_2525_normal_12,
            'Converge Pro 2 48V': self.clr1_25_2525_voip_4,
            'Converge Pro 2 48VT': self.clr1_25_2525_voip_4,
            'Converge Pro 2 128VT': self.clr1_25_2525_voip_12,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BeamformingMicrophoneArrayGain': {'Parameters': ['Channel Name'], 'Status': {}},
            'BeamformingMicrophoneArrayMode': {'Parameters': ['Channel Name'], 'Status': {}},
            'BeamformingMicrophoneArrayMute': {'Parameters': ['Channel Name'], 'Status': {}},
            'BeamformingMicrophoneArrayMuteLED': {'Parameters': ['Channel Name'], 'Status': {}},
            'BeamformingMicrophoneArrayZone': {'Parameters': ['Channel Name', 'Zone'], 'Status': {}},
            'BeamReport': {'Parameters': ['Device Name', 'BMA360 ID', 'Beam'], 'Status': {}},
            'CallDirection': {'Status': {}},
            'CallerID': {'Parameters': ['Channel Name'], 'Status': {}},
            'CallForwarding': {'Parameters': ['Channel Name'], 'Status': {}},
            'CallState': {'Parameters': ['Channel Name', 'Party Line'], 'Status': {}},
            'ClearMatrixTies': {'Status': {}},
            'GainCoarse': {'Parameters': ['Channel Name'], 'Status': {}},
            'DoNotDisturb': {'Parameters': ['Channel Name'], 'Status': {}},
            'DTMFTelco': {'Parameters': ['Box Number'], 'Status': {}},
            'DTMFVoIP': {'Parameters': ['Channel Name'], 'Status': {}},
            'Firmware': {'Status': {}},
            'Gain': {'Parameters': ['Channel Name'], 'Status': {}},
            'GainFine': {'Parameters': ['Channel Name'], 'Status': {}},
            'GateReport': {'Parameters': ['Device Name', 'Channel'], 'Status': {}},
            'GraphicEQEnable': {'Parameters': ['Channel Name'], 'Status': {}},
            'GraphicEQGain': {'Parameters': ['Channel Name', 'Gain Number'], 'Status': {}},
            'HoldTransfer': {'Parameters': ['Channel Name'], 'Status': {}},
            'HookTelco': {'Parameters': ['Channel Name'], 'Status': {}},
            'HookVoIP': {'Parameters': ['Channel Name', 'Party Line'], 'Status': {}},
            'IncomingCallStatus': {'Parameters': ['Channel Name'], 'Status': {}},
            'InitiateorAddtoConferenceCall': {'Parameters': ['Channel Name'], 'Status': {}},
            'JoinConference': {'Parameters': ['Channel Name'], 'Status': {}},
            'Macro': {'Status': {}},
            'MatrixTie': {'Parameters': ['Input', 'Output', 'Crosspoint Type'], 'Status': {}},
            'MicPhantomPower': {'Parameters': ['Channel Name'], 'Status': {}},
            'Mute': {'Parameters': ['Channel Name'], 'Status': {}},
            'OutputMicLine': {'Parameters': ['Channel Name'], 'Status': {}},
            'OutputPolarity': {'Parameters': ['Channel Name'], 'Status': {}},
            'PostGain': {'Parameters': ['Channel Name'], 'Status': {}},
            'Reject': {'Parameters': ['Channel Name'], 'Status': {}},
            'RoomSelect': {'Parameters': ['Room Number', 'Sub Room', 'Config File'], 'Status': {}},
            'SelectPartyLine': {'Parameters': ['Channel Name'], 'Status': {}},
            'SignalGeneratorEnable': {'Parameters': ['Channel Name'], 'Status': {}},
            'SkypeCallStatus': {'Parameters': ['Channel Name', 'Session ID'], 'Status': {}},
            'SkypeNavigation': {'Status': {}},
            'SkypeSearch': {'Status': {}},
            'SkypeSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'SkypeSearchSet': {'Status': {}},
            'SkypeUpdate': {'Parameters': ['Channel Name'], 'Status': {}},
        }

        self.PasswdPromptCount = 0
        self.QueryFlag = True

        self.Advance = True
        self.MinLabel = 1
        self.MaxLabel = 5
        self.SkypeContacts = []
        self.lastSkypeChannel = ''

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'Username:\s'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:\s'), self.__MatchPassword, None)

        self.QueryDelay = 0
        self.QueryDelayTimer = Timer(0.5, self.QueryDelayTimerHandler)
        self.QueryDelayTimer.Stop()

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'VERSION ([\S ]+\r)'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'STACK NOTIFICATION HW_RESYNC'), self.__MatchQueryFlag, None)

    def CreateMatchString(self):
        if self.Model == 'beamform':
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL GAIN (?P<value>-?\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchBeamformingMicrophoneArrayGain, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) BF BF_MODE (?P<value>[1-4]) ?(?:\.\d*)?\r'), self.__MatchBeamformingMicrophoneArrayMode, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL MUTE (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchBeamformingMicrophoneArrayMute, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) BF BF_LED (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchBeamformingMicrophoneArrayMuteLED, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) BF ZONE_(?P<Zone>\d{1,2}) (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchBeamformingMicrophoneArrayZone, None)
        else:
            self.AddMatchString(re.compile(b'BEAMREPORT ([ \S]+?) \d+ 1 (.*)\r\n'), self.__MatchBeamReport, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) INQUIRE DIRECTION (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchCallDirection, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) (NOTIFICATION|INQUIRE) CALLER_ID (?P<value>.+) ?\r'), self.__MatchCallerID, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) KEY KEY_FORWARD (?P<value>[0-3]) ?(?:\.\d*)?\r\n'), self.__MatchCallForwarding, None)

            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL GAIN_COARSE (?P<value>\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchGainCoarse, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) KEY KEY_DO_NOT_DISTURB (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL GAIN (?P<value>-?\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL GAIN_FINE (?P<value>-?\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchGainFine, None)
            self.AddMatchString(re.compile(b'GATEREPORT (?P<DeviceName>[ \S]+) 0 1 \d ([01]{4,12})  \r'), self.__MatchGateReport, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) GRAPHICEQ ENABLE (?P<value>[01])(?:\.\d*)? ?\r'), self.__MatchGraphicEQEnable, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) GRAPHICEQ GAIN_(?P<GainNumber>[1-9]|10) (?P<value>-?\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchGraphicEQGain, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) (INQUIRE|NOTIFICATION) HOOK (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchHookTelco, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) NOTIFICATION INCOMING_CALL (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchIncomingCallStatus, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL MUTE (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL MICLINE (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchOutputMicLine, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) LEVEL POLARITY (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchOutputPolarity, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) COMPRESSOR POST_GAIN (?P<value>\d{1,2}(?:\.\d{1,2})?) ?\r'), self.__MatchPostGain, None)
            self.AddMatchString(re.compile(b'EP (?P<Channel>[ \S]+) SIG_GEN ENABLE (?P<value>[01]) ?(?:\.\d*)?\r'), self.__MatchSignalGeneratorEnable, None)

            self.AddMatchString(re.compile(b'([=> ]?EP (?P<Channel>[\w]+) NOTIFICATION SESSION_CALL_STATE_CHANGE (\d)\|[\s\S]+\|(IDLE|CONNECTING|RINGING|BUSY|ACTIVE|HOLD|INCOMING|CONFERENCE_JOIN|INVITE_JOIN_AUDIO)[\s\S])|(\d)\s{0,}=> EP (?P<Channel2>[\w]+) NOTIFICATION ERROR INQUIRE SESSION (CALL STATE FAILED):|EP (?P<Channel3>[\w]+) INQUIRE_RESULT SESSION_CALL_STATE (\d)[ \S]+\|(IDLE)'), self.__MatchSkypeCallStatus, None)

            self.deliRegex = re.compile(b'EP ([ \S]+) INQUIRE_RESULT ACTIVE_PARTIES ([\s\S]+) \r')
            self.DTMFRegex = re.compile(b'EP ([ \S]+) (\d)01 KEY KEY_DIGIT_PRESSED ([0-9]|\*|#) \r\n=>')

            self.callpattern = re.compile('IDLE[:|;]|DIAL_TONE[:|;]|BLIND_TRANSFERRING_DIAL_TONE[:|;]|TRANSFERRING_DIAL_TONE[:|;]|INPROCESS[:|;]|RINGING[:|;]|BUSY[:|;]|ACTIVE[:|;]|HOLD[:|;]|INCOMING[:|;]|CONFERENCE_ACTIVE[:|;]|CONFERENCE_HOLD[:|;]|TRANSFER_ACTIVE[:|;]|TRANSFER_HOLD[:|;]|TRANSFERRING_INPROCESS[:|;]|TRANSFERRING_RINGING[:|;]|TRANSFERRING_BUSY[:|;]|TRANSFERRING_ACTIVE[:|;]|TRANSFERRING_HOLD[:|;]|BLIND_TRANSFER_HOLD[:|;]|BLIND_TRANSFERRING_INPROCESS[:|;]|BLIND_TRANSFERRING_RINGING[:|;]|BLIND_TRANSFERRING_BUSY[:|;]|BLIND_TRANSFERRING_DIALING[:|;]|TRANSFERRING_DIALING[:|;]|DIALING[:|;]')
            self.callStateIDPattern = re.compile('(?:ACTIVE|HOLD|INCOMING):\"([ \S]+?)\" <sip:(\d+)@(\d+\.\d+\.\d+\.\d+)>')
            self.beamReportPattern = re.compile('48 (\d{3}) ([01]{12})')


    def QueryDelayTimerHandler(self, timer, count):
        if count / 2 >= self.QueryDelay:
            if self.QueryDelayTimer.State == 'Running':
                self.QueryDelayTimer.Pause()

    @property
    def NumberofSkypeSearch(self):
        return self._NumberofSkypeSearch

    @NumberofSkypeSearch.setter
    def NumberofSkypeSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofSkypeSearch = int(value)
        else:
            self.Error(['Number of Skype Search should be a value between 1 to 10.'])

    def __MatchUsername(self, match, qualifier):

        if self.deviceUsername is not None:
            self.QueryDelay = 2
            self.QueryDelayTimer.Restart()
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password.'])
        else:
            if self.devicePassword is not None:
                self.QueryDelay = 2
                self.QueryDelayTimer.Restart()
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Username')

    def __MatchQueryFlag(self, match, qualifier):

        self.QueryFlag = True
        self.QueryDelay = 0
        if self.QueryDelayTimer.State == 'Running':
            self.QueryDelayTimer.Pause()

    def UpdateFirmware(self, value, qualifier):

        CmdString = 'VERSION * FW 1\r'
        self.__UpdateHelper('Firmware', CmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        if match.group(0).decode() == 'VERSION * FW 1\x00\r':
            self.QueryFlag = False
            self.WriteStatus('Firmware', 'Initializing', None)
        else:
            self.QueryFlag = True
            value = match.group(1).decode()
            value = value.split(' ')[3]

            self.QueryDelay = 0
            if self.QueryDelayTimer.State == 'Running':
                self.QueryDelayTimer.Pause()

            self.WriteStatus('Firmware', value, None)

    def UpdateSkypeCallStatus(self, value, qualifier):

        Channel = qualifier['Channel Name']
        Session = qualifier['Session ID']
        if 1 <= len(Channel) <= 64 and 0 <= int(Session) <= 5:
            SkypeCallStatusCmdString = 'EP {0} INQUIRE SESSION_CALL_STATE {1}\r'.format(Channel, Session)
            self.__UpdateHelper('SkypeCallStatus', SkypeCallStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSkypeCallStatus')

    def __MatchSkypeCallStatus(self, match, tag):
        ValueStateValues = {
            'IDLE': 'Idle',
            'RINGING': 'Ringing',
            'BUSY': 'Busy',
            'ACTIVE': 'Active',
            'HOLD': 'Hold',
            'INCOMING': 'Incoming',
            'CONFERENCE_JOIN': 'Join Conference',
            'INVITE_JOIN_AUDIO': 'Add Audio',
            'CONNECTING': 'Connecting',
            'CALL STATE FAILED': 'Idle'
        }

        if match.group(5):
            value = match.group(7).decode()
            session = match.group(5).decode()
            qualifier = {'Channel Name': match.group('Channel2').decode(), 'Session ID': session}
            self.WriteStatus('SkypeCallStatus', ValueStateValues[value], qualifier)
        elif match.group(9):
            value = match.group(10).decode()
            session = match.group(9).decode()
            qualifier = {'Channel Name': match.group('Channel3').decode(), 'Session ID': session}
            self.WriteStatus('SkypeCallStatus', ValueStateValues[value], qualifier)
        else:
            qualifier = {'Channel Name': match.group('Channel').decode(), 'Session ID': match.group(3).decode()}
            value = match.group(4).decode()
            self.WriteStatus('SkypeCallStatus', ValueStateValues[value], qualifier)

    def SetSkypeNavigation(self, value, qualifier):

        if self.MaxLabel != 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.SkypeContacts:
                if 'Page' in value:
                    NumberOfAdvance = self._NumberofSkypeSearch
                else:
                    NumberOfAdvance = 1

                if 'Down' in value and self.MinLabel <= len(self.SkypeContacts) and self.Advance:  # Stop scroll up to as many configured
                    self.MinLabel += NumberOfAdvance
                    self.MaxLabel += NumberOfAdvance

                elif 'Up' in value:
                    self.MinLabel -= NumberOfAdvance
                    self.MaxLabel -= NumberOfAdvance
                if self.MaxLabel < self._NumberofSkypeSearch:
                    self.MaxLabel = self._NumberofSkypeSearch

                if self.MinLabel < 1:
                    self.MinLabel = 1

                button = 1
                for i in range(self.MinLabel, self.MaxLabel + 1):  # populate up to max labels configured
                        if i > len(self.SkypeContacts):
                            for j in range(button, int(self._NumberofSkypeSearch) + 1):
                                    self.WriteStatus('SkypeSearchResult', '', {'Button': j})
                                    button += 1
                        else:
                            for name in self.SkypeContacts[i - 1]:
                                if name == '***End of list***':
                                    self.Advance = False
                                    self.WriteStatus('SkypeSearchResult', '{0}'.format(name), {'Button': button})
                                else:
                                    self.Advance = True
                                    self.WriteStatus('SkypeSearchResult', '{0} : {1}'.format(name, self.SkypeContacts[i - 1][name]), {'Button': button})
                                button += 1
        else:
            self.Discard('Invalid Command for SetSkypeNavigation')

    def SetSkypeSearchSet(self, value, qualifier):

        if 1 <= value <= self._NumberofSkypeSearch:
            number = self.ReadStatus('SkypeSearchResult', {'Button': value})
            if number:
                if number != '***End of list***':
                    number = number[number.find(' : ') + 7:]  # 5:
                    self.SetHookVoIP('Dial', {'Dial String': number})
        else:
            self.Discard('Invalid Command for SetSkypeSearchSet')

    def SetSkypeUpdate(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            self.lastSkypeChannel = Channel
            temp = qualifier['Search Name']
            string = str(temp)
            res = self.SendAndWait(b'EP ' + Channel.encode() + b' INQUIRE CONTACT_SEARCH \"' + string.encode() + b'\"\r', 15)

            if res:
                if b'SFB Process Failure' in res:
                    self.QueryDelay = 0
                    if self.QueryDelayTimer.State == 'Running':
                        self.QueryDelayTimer.Pause()

                self.SkypeContacts = []
                try:
                    tempList = res.split(b'\x0D\x0A')
                    del tempList[0:2]
                    SkypeName = []
                    SkypeAddress = []
                    for x in tempList:
                        perEntryList = x.split(b'|')
                        if b'INQUIRE_RESULT CONTACT_SEARCH' in perEntryList[0]:
                            SkypeName.append(perEntryList[3].decode())
                            SkypeAddress.append(perEntryList[2].decode())

                    SkypeName.append('***End of list***')
                    SkypeAddress.append('***End of list***')

                    for i in range(0, len(SkypeName)):
                        temp = {SkypeName[i]: SkypeAddress[i]}
                        self.SkypeContacts.append(temp)

                    self.MinLabel = 1
                    self.MaxLabel = self._NumberofSkypeSearch

                    button = 1
                    for i in range(self.MinLabel, self.MaxLabel + 1):  # populate up to max labels configured
                            if i > len(self.SkypeContacts):
                                for j in range(button, int(self._NumberofSkypeSearch) + 1):
                                        self.WriteStatus('SkypeSearchResult', '', {'Button': j})
                                        button += 1
                            else:
                                for name in self.SkypeContacts[i - 1]:
                                    if name == '***End of list***':
                                        self.Advance = False
                                        self.WriteStatus('SkypeSearchResult', '{0}'.format(name), {'Button': button})
                                    else:
                                        self.Advance = True
                                        self.WriteStatus('SkypeSearchResult', '{0} : {1}'.format(name, self.SkypeContacts[i - 1][name]), {'Button': button})
                                    button += 1

                except (ValueError, IndexError):
                    self.Error(['Skype Update: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetSkypeUpdate')

    def SetBeamformingMicrophoneArrayGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if -65 <= value <= 20 and 1 <= len(Channel) <= 64:
            CmdString = 'EP {0} LEVEL GAIN {1}\r'.format(Channel, value)
            self.__SetHelper('BeamformingMicrophoneArrayGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeamformingMicrophoneArrayGain')

    def UpdateBeamformingMicrophoneArrayGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayGainCmdString = 'EP {0} LEVEL GAIN\r'.format(Channel)
            self.__UpdateHelper('BeamformingMicrophoneArrayGain', BeamformingMicrophoneArrayGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamformingMicrophoneArrayGain')

    def __MatchBeamformingMicrophoneArrayGain(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('BeamformingMicrophoneArrayGain', float(value), qualifier)

    def SetBeamformingMicrophoneArrayMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Ceiling': '2',
            'Wall': '3',
            'Tabletop': '4'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayModeCmdString = 'EP {0} BF BF_MODE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('BeamformingMicrophoneArrayMode', BeamformingMicrophoneArrayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeamformingMicrophoneArrayMode')

    def UpdateBeamformingMicrophoneArrayMode(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayModeCmdString = 'EP {0} BF BF_MODE\r'.format(Channel)
            self.__UpdateHelper('BeamformingMicrophoneArrayMode', BeamformingMicrophoneArrayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamformingMicrophoneArrayMode')

    def __MatchBeamformingMicrophoneArrayMode(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '2': 'Ceiling',
            '3': 'Wall',
            '4': 'Tabletop'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('BeamformingMicrophoneArrayMode', ValueStateValues[value], qualifier)

    def SetBeamformingMicrophoneArrayMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayMuteCmdString = 'EP {0} LEVEL MUTE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('BeamformingMicrophoneArrayMute', BeamformingMicrophoneArrayMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeamformingMicrophoneArrayMute')

    def UpdateBeamformingMicrophoneArrayMute(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayMuteCmdString = 'EP {0} LEVEL MUTE\r'.format(Channel)
            self.__UpdateHelper('BeamformingMicrophoneArrayMute', BeamformingMicrophoneArrayMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamformingMicrophoneArrayMute')

    def __MatchBeamformingMicrophoneArrayMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('BeamformingMicrophoneArrayMute', ValueStateValues[value], qualifier)

    def SetBeamformingMicrophoneArrayMuteLED(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayMuteLEDCmdString = 'EP {0} BF BF_LED {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('BeamformingMicrophoneArrayMuteLED', BeamformingMicrophoneArrayMuteLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeamformingMicrophoneArrayMuteLED')

    def UpdateBeamformingMicrophoneArrayMuteLED(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            BeamformingMicrophoneArrayMuteLEDCmdString = 'EP {0} BF BF_LED\r'.format(Channel)
            self.__UpdateHelper('BeamformingMicrophoneArrayMuteLED', BeamformingMicrophoneArrayMuteLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamformingMicrophoneArrayMuteLED')

    def __MatchBeamformingMicrophoneArrayMuteLED(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('BeamformingMicrophoneArrayMuteLED', ValueStateValues[value], qualifier)

    def SetBeamformingMicrophoneArrayZone(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        Zone = qualifier['Zone']

        if value in ValueStateValues and 1 <= len(Channel) <= 64 and 1 <= int(Zone) <= 12:
            BeamformingMicrophoneArrayZoneCmdString = 'EP {0} BF ZONE_{1} {2}\r'.format(Channel, Zone, ValueStateValues[value])
            self.__SetHelper('BeamformingMicrophoneArrayZone', BeamformingMicrophoneArrayZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeamformingMicrophoneArrayZone')

    def UpdateBeamformingMicrophoneArrayZone(self, value, qualifier):

        Channel = qualifier['Channel Name']
        Zone = qualifier['Zone']
        if 1 <= len(Channel) <= 64 and 1 <= int(Zone) <= 12:
            BeamformingMicrophoneArrayZoneCmdString = 'EP BFM {0} BF ZONE_{1}\r'.format(Channel, Zone)
            self.__UpdateHelper('BeamformingMicrophoneArrayZone', BeamformingMicrophoneArrayZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamformingMicrophoneArrayZone')

    def __MatchBeamformingMicrophoneArrayZone(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        zone = match.group('Zone').decode()

        if 1 <= int(zone) <= 12:
            qualifier = {
                'Channel Name': match.group('Channel').decode(),
                'Zone': zone
            }

            value = match.group('value').decode()
            self.WriteStatus('BeamformingMicrophoneArrayZone', ValueStateValues[value], qualifier)

    def UpdateBeamReport(self, value, qualifier):

        if qualifier['Device Name'] and qualifier['BMA360 ID'] and 1 <= int(qualifier['Beam']) <= 12:
            BeamReportCmdString = 'BEAM * 5 1\r'
            self.__UpdateHelper('BeamReport', BeamReportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamReport')

    def __MatchBeamReport(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active',
        }

        deviceName = match.group(1).decode()

        response = match.group(2).decode()
        responseList = re.findall(self.beamReportPattern, response)
        for index in responseList:
            beamStatus = index[1][::-1]
            for beam in range(0, len(beamStatus)):
                qualifier = {
                    'Device Name': deviceName,
                    'BMA360 ID': index[0],
                    'Beam': str(beam + 1)
                }
                value = ValueStateValues[beamStatus[beam]]
                self.WriteStatus('BeamReport', value, qualifier)

    def UpdateCallDirection(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            CallDirectionCmdString = 'EP {0} INQUIRE DIRECTION\r'.format(Channel)
            self.__UpdateHelper('CallDirection', CallDirectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCallDirection')

    def __MatchCallDirection(self, match, tag):

        ValueStateValues = {
            '1': 'Incoming',
            '0': 'Outgoing'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('CallDirection', ValueStateValues[value], qualifier)

    def UpdateCallerID(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            CallerIDCmdString = 'EP {0} INQUIRE CALLER_ID\r'.format(Channel)
            self.__UpdateHelper('CallerID', CallerIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCallerID')

    def __MatchCallerID(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()

        if 'NO_ACTIVE_CALL' in value:
            self.WriteStatus('CallerID', 'No Active Call', qualifier)
        else:
            self.WriteStatus('CallerID', value, qualifier)

    def SetCallForwarding(self, value, qualifier):

        ValueStateValues = {
            'Disable': '0',
            'Unconditional': '1',
            'Busy': '2',
            'No Answer': '3'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            CallForwardingCmdString = 'EP {0} KEY KEY_FORWARD {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('CallForwarding', CallForwardingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallForwarding')

    def UpdateCallForwarding(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            CallForwardingCmdString = 'EP {0} KEY KEY_FORWARD\r'.format(Channel)
            self.__UpdateHelper('CallForwarding', CallForwardingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCallForwarding')

    def __MatchCallForwarding(self, match, tag):

        ValueStateValues = {
            '0': 'Disable',
            '1': 'Unconditional',
            '2': 'Busy',
            '3': 'No Answer'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()

        self.WriteStatus('CallForwarding', ValueStateValues[value], qualifier)

    def UpdateCallState(self, value, qualifier):

        States = {
            'IDLE': 'Idle',
            'DIAL_TONE': 'Dial Tone',
            'DIALING': 'Dialing',
            'INPROCESS': 'In Process',
            'RINGING': 'Ringing',
            'BUSY': 'Busy',
            'ACTIVE': 'Active',
            'HOLD': 'Hold',
            'INCOMING': 'Incoming',
            'CONFERENCE_ACTIVE': 'In Conference Call, Active',
            'CONFERENCE_HOLD': 'On Hold In Conference Call',
            'TRANSFER_HOLD': 'Transferring, Call On Hold',
            'TRANSFER_ACTIVE': 'Transferring, Active Call',
            'TRANSFERRING_DIAL_TONE': 'Transferring, Dial Tone',
            'TRANSFERRING_DIALING': 'Transferring, Dialing',
            'TRANSFERRING_INPROCESS': 'Transferring, In Process',
            'TRANSFERRING_RINGING': 'Transferring, Ringing',
            'TRANSFERRING_BUSY': 'Transferring, Busy',
            'TRANSFERRING_ACTIVE': 'Transferring, Active',
            'TRANSFERRING_HOLD': 'Transferring, On Hold',
            'BLIND_TRANSFER_HOLD': 'Blind Transfer, On Hold',
            'BLIND_TRANSFERRING_DIAL_TONE': 'Blind Transfer, Dial Tone',
            'BLIND_TRANSFERRING_DIALING': 'Blind Transfer, Dialing',
            'BLIND_TRANSFERRING_INPROCESS': 'Blind Transfer, In Process',
            'BLIND_TRANSFERRING_RINGING': 'Blind Transfer, Ringing',
            'BLIND_TRANSFERRING_BUSY': 'Blind Transfer, Busy'
        }

        Hook_States = {
            'IDLE': 'On Hook',
            'DIALING': 'Off Hook',
            'INPROCESS': 'Off Hook',
            'ACTIVE': 'Off Hook'
        }

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            CallStateCmdString = 'EP {0} INQUIRE ACTIVE_PARTIES\r'.format(Channel)
            response = self.__UpdateHelper('CallState', CallStateCmdString, value, qualifier)
            if response:
                try:
                    tempmatch = re.search('EP (?P<Channel>[ \S]+) INQUIRE_RESULT ACTIVE_PARTIES (?P<value>[ \S]+) ?\r', response)
                    hooklist = re.findall(self.callpattern, tempmatch.group(0))
                    callStateIDList = re.findall(self.callStateIDPattern, tempmatch.group(0))
                    self.WriteCallStateID(callStateIDList)

                    for x, y in enumerate(hooklist):
                        try:
                            z = y[0:-1]
                            if z in Hook_States:
                                self.WriteStatus('HookVoIP', Hook_States[z], {'Channel Name': tempmatch.group('Channel'), 'Party Line': str(x + 1)})
                        except(KeyError, IndexError):
                            self.Error(['Hook Status provided an unexpected response'])

                        try:
                            s = y[0:-1]
                            if s in States:
                                self.WriteStatus('CallState', States[s], {'Channel Name': tempmatch.group('Channel'), 'Party Line': str(x + 1)})
                        except(KeyError, IndexError):
                            self.Error(['Call State Status provided an unexpected response'])
                except(KeyError, IndexError, AttributeError):
                    self.Error(['Call State Response: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCallState')

    def WriteCallStateID(self, matchList):
        for i in range(0, 6):
            if i < len(matchList):
                # List[0]: Name, List[1]: Number, List[2]: IP Address
                tempString = matchList[i][0] + ' - ' + matchList[i][1]
                self.WriteStatus('CallStateIDString', tempString, {'Party Line': str(i)})
            else:
                self.WriteStatus('CallStateIDString', ' ', {'Party Line': str(i)})

    def SetClearMatrixTies(self, value, qualifier):

        self.__SetHelper('ClearMatrixTies', 'CLRMATRIX\r', value, qualifier)

    def SetGainCoarse(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 0 <= value <= 56 and 1 <= len(Channel) <= 64:
            GainCoarseCmdString = 'EP {0} LEVEL GAIN_COARSE {1}\r'.format(Channel, value)
            self.__SetHelper('GainCoarse', GainCoarseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGainCoarse')

    def UpdateGainCoarse(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            GainCoarseCmdString = 'EP {0} LEVEL GAIN_COARSE\r'.format(Channel)
            self.__UpdateHelper('GainCoarse', GainCoarseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGainCoarse')

    def __MatchGainCoarse(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('GainCoarse', int(value), qualifier)

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            DoNotDisturbCmdString = 'EP {0} KEY KEY_DO_NOT_DISTURB {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            DoNotDisturbCmdString = 'EP {0} KEY KEY_DO_NOT_DISTURB\r'.format(Channel)
            self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDoNotDisturb')

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('DoNotDisturb', ValueStateValues[value], qualifier)

    def SetDTMFTelco(self, value, qualifier):

        BoxNumber = int(qualifier['Box Number'])
        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#'] and 1 <= BoxNumber <= 9:
            CmdStringPress = 'EP TELCO_RX {}01 KEY KEY_DIGIT_PRESSED {}\r'.format(BoxNumber, value)
            CmdStringRelease = 'EP TELCO_RX {}01 KEY KEY_DIGIT_RELEASED {}\r'.format(BoxNumber, value)

            res = self.SendAndWait(CmdStringPress.encode(), 1, deliRex=self.DTMFRegex)
            if res:
                self.SendAndWait(CmdStringRelease.encode(), 0.2)
        else:
            self.Discard('Invalid Command for SetDTMFTelco')

    def SetDTMFVoIP(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#'] and 1 <= len(Channel) <= 64:
            CmdStringPress = 'EP {0} KEY KEY_DIGIT_PRESSED {1}\r'.format(Channel, value)
            CmdStringRelease = 'EP {0} KEY KEY_DIGIT_RELEASED {1}\r'.format(Channel, value)
            self.__SetHelper('DTMFVoIP', CmdStringPress, value, qualifier)
            self.__SetHelper('DTMFVoIP', CmdStringRelease, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMFVoIP')

    def SetGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if -65 <= value <= 20 and 1 <= len(Channel) <= 64:
            GainCmdString = 'EP {0} LEVEL GAIN {1}\r'.format(Channel, value)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            GainCmdString = 'EP {0} LEVEL GAIN\r'.format(Channel)
            self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGain')

    def __MatchGain(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('Gain', float(value), qualifier)

    def SetGainFine(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if -65 <= value <= 20 and 1 <= len(Channel) <= 64:
            GainFineCmdString = 'EP {0} LEVEL GAIN_FINE {1}\r'.format(Channel, value)
            self.__SetHelper('GainFine', GainFineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGainFine')

    def UpdateGainFine(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            GainFineCmdString = 'EP {0} LEVEL GAIN_FINE\r'.format(Channel)
            self.__UpdateHelper('GainFine', GainFineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGainFine')

    def __MatchGainFine(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('GainFine', float(value), qualifier)

    def UpdateGateReport(self, value, qualifier):

        if qualifier['Device Name'] and 1 <= int(qualifier['Channel']) <= self.ChannelSize:
            GateReportCmdString = 'GATE {} 1 1\r'.format(qualifier['Device Name'])
            self.__UpdateHelper('GateReport', GateReportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGateReport')

    def __MatchGateReport(self, match, tag):

        deviceName = match.group(1).decode()
        response = match.group(2).decode()[::-1]

        for channel in range(0, self.ChannelSize):
            if response[channel] == '1':
                self.WriteStatus('GateReport', 'Gated', {'Device Name': deviceName, 'Channel': str(channel + 1)})
            else:
                self.WriteStatus('GateReport', 'Not Gated', {'Device Name': deviceName, 'Channel': str(channel + 1)})

    def SetGraphicEQEnable(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            GraphicEQEnableCmdString = 'EP {0} GRAPHICEQ ENABLE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('GraphicEQEnable', GraphicEQEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGraphicEQEnable')

    def UpdateGraphicEQEnable(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            GraphicEQEnableCmdString = 'EP {0} GRAPHICEQ ENABLE\r'.format(Channel)
            self.__UpdateHelper('GraphicEQEnable', GraphicEQEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGraphicEQEnable')

    def __MatchGraphicEQEnable(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('GraphicEQEnable', ValueStateValues[value], qualifier)

    def SetGraphicEQGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        Gain = qualifier['Gain Number']
        if -12 <= value <= 12 and 1 <= len(Channel) <= 64 and 1 <= int(Gain) <= 10:
            GraphicEQGainCmdString = 'EP {0} GRAPHICEQ GAIN_{1} {2}\r'.format(Channel, qualifier['Gain Number'], value)
            self.__SetHelper('GraphicEQGain', GraphicEQGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGraphicEQGain')

    def UpdateGraphicEQGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        Gain = qualifier['Gain Number']
        if 1 <= len(Channel) <= 64 and 1 <= int(Gain) <= 10:
            GraphicEQGainCmdString = 'EP {0} GRAPHICEQ GAIN_{1}\r'.format(Channel, qualifier['Gain Number'])
            self.__UpdateHelper('GraphicEQGain', GraphicEQGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGraphicEQGain')

    def __MatchGraphicEQGain(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        qualifier['Gain Number'] = match.group('GainNumber').decode()
        self.WriteStatus('GraphicEQGain', float(value), qualifier)

    def SetHoldTransfer(self, value, qualifier):

        ValueStateValues = {
            'Hold': 'KEY_HOLD',
            'Resume': 'KEY_RESUME',
            'Transfer': 'KEY_TRANSFER',
            'Blind Transfer': 'KEY_BLIND_TRANSFER'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            HoldTransferCmdString = 'EP {0} KEY {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('HoldTransfer', HoldTransferCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHoldTransfer')

    def SetHookTelco(self, value, qualifier):

        ValueStateValues = {
            'On Hook': 'KEY_HOOK 0\r',
            'Off Hook': 'KEY_HOOK 1\r',
            'Dial': 'KEY_CALL',
            'Redial': 'KEY_REDIAL\r',
            'Flash': 'KEY_HOOK_FLASH\r'
        }

        DialString = qualifier['Dial String']
        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            if value == 'Dial' and DialString:
                HookTelcoCmdString = 'EP {0} KEY {1} {2}\r'.format(Channel, ValueStateValues[value], DialString)
            else:
                HookTelcoCmdString = 'EP {0} KEY {1}'.format(Channel, ValueStateValues[value])
            if value != 'Dial' or value != 'Redial' or value != 'Flash':
                self.__SetHelper('HookTelco', HookTelcoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHookTelco')

    def UpdateHookTelco(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            CmdString = 'EP {} INQUIRE HOOK\r'.format(Channel)
            self.__UpdateHelper('HookTelco', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHookTelco')

    def __MatchHookTelco(self, match, tag):

        ValueStateValues = {
            '0': 'On Hook',
            '1': 'Off Hook',
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()

        self.WriteStatus('HookTelco', ValueStateValues[value], qualifier)
        if ValueStateValues[value] == 'On Hook':
            self.WriteStatus('IncomingCallStatus', 'No Call', qualifier)

    def SetHookVoIP(self, value, qualifier):

        DialString = qualifier['Dial String']
        Channel = qualifier['Channel Name']

        ValueStateValues = {
            'On Hook': 'KEY_HOOK 0\r',
            'Off Hook': 'KEY_HOOK 1\r',
            'Dial': 'KEY_CALL {}\r'.format(DialString),
            'Redial': 'KEY_REDIAL\r'
        }

        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            HookVoIPCmdString = 'EP {0} KEY {1}'.format(Channel, ValueStateValues[value])
            self.__SetHelper('HookVoIP', HookVoIPCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHookVoIP')

    def UpdateHookVoIP(self, value, qualifier):

        self.UpdateCallState(value, qualifier)

    def __MatchIncomingCallStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Call Incoming',
            '0': 'No Call'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('IncomingCallStatus', ValueStateValues[value], qualifier)

    def SetInitiateorAddtoConferenceCall(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 0 <= int(value) <= 5 and 1 <= len(Channel) <= 64:
            CmdString = 'EP {0} KEY KEY_CONFERENCE {1}\r'.format(Channel, value)
            self.__SetHelper('InitiateorAddtoConferenceCall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInitiateorAddtoConferenceCall')

    def SetJoinConference(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            JoinConferenceCmdString = 'EP {0} KEY KEY_CONFERENCE\r'.format(Channel)
            self.__SetHelper('JoinConference', JoinConferenceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetJoinConference')

    def SetMacro(self, value, qualifier):

        macroName = qualifier['Name']
        if macroName:
            self.__SetHelper('Macro', 'MCCF {0}\r'.format(macroName), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def SetMatrixTie(self, value, qualifier):

        CrosspointTypeStates = {
            'Normal': '1',
            'Gated': '3',
            'Non-Gated': '4',
            'Pre-AEC': '5',
        }

        ValueStateValues = {
            'Tie': '1',
            'Untie': '0',
        }

        Input = qualifier['Input']
        Output = qualifier['Output']
        if value in ValueStateValues and 1 <= len(Input) <= 64 and 1 <= len(Output) <= 64 and qualifier['Crosspoint Type'] in CrosspointTypeStates:
            MatrixTieCmdString = 'MT {0} {1} {2} 0 {3}\r'.format(Input, Output, ValueStateValues[value], CrosspointTypeStates[qualifier['Crosspoint Type']])
            self.__SetHelper('MatrixTie', MatrixTieCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTie')

    def SetMicPhantomPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            MicPhantomPowerCmdString = 'EP {0} LEVEL PHAN_PWR {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('MicPhantomPower', MicPhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicPhantomPower')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            MuteCmdString = 'EP {0} LEVEL MUTE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            MuteCmdString = 'EP {0} LEVEL MUTE\r'.format(Channel)
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('Mute', ValueStateValues[value], qualifier)

    def SetOutputMicLine(self, value, qualifier):

        ValueStateValues = {
            'Line Level': '0',
            'Mic Level': '1'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            OutputMicLineCmdString = 'EP {0} LEVEL MICLINE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('OutputMicLine', OutputMicLineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMicLine')

    def UpdateOutputMicLine(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            OutputMicLineCmdString = 'EP {0} LEVEL MICLINE\r'.format(Channel)
            self.__UpdateHelper('OutputMicLine', OutputMicLineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMicLine')

    def __MatchOutputMicLine(self, match, tag):

        ValueStateValues = {
            '0': 'Line Level',
            '1': 'Mic Level'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('OutputMicLine', ValueStateValues[value], qualifier)

    def SetOutputPolarity(self, value, qualifier):

        ValueStateValues = {
            'Default': '0',
            'Reverse': '1'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            OutputPolarityCmdString = 'EP {0} LEVEL POLARITY {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('OutputPolarity', OutputPolarityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputPolarity')

    def UpdateOutputPolarity(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            OutputPolarityCmdString = 'EP {0} LEVEL POLARITY\r'.format(Channel)
            self.__UpdateHelper('OutputPolarity', OutputPolarityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputPolarity')

    def __MatchOutputPolarity(self, match, tag):

        ValueStateValues = {
            '0': 'Default',
            '1': 'Reverse'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('OutputPolarity', ValueStateValues[value], qualifier)

    def SetPostGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 0 <= value <= 20 and 1 <= len(Channel) <= 64:
            PostGainCmdString = 'EP {0} COMPRESSOR POST_GAIN {1}\r'.format(Channel, value)
            self.__SetHelper('PostGain', PostGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPostGain')

    def UpdatePostGain(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            PostGainCmdString = 'EP {0} COMPRESSOR POST_GAIN\r'.format(Channel)
            self.__UpdateHelper('PostGain', PostGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePostGain')

    def __MatchPostGain(self, match, tag):

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('PostGain', float(value), qualifier)

    def SetReject(self, value, qualifier):

        ValueStateValues = {
            'Line 1': '1',
            'Line 2': '2',
            'Line 3': '3',
            'Line 4': '4',
            'Line 5': '5'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            RejectCmdString = 'EP {0} KEY KEY_REJECT {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('Reject', RejectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReject')

    def SetRoomSelect(self, value, qualifier):

        if 0 < qualifier['Room Number'] and qualifier['Sub Room'] and qualifier['Config File']:
            RoomSelectCmdString = 'ROOM {0} 7 {1} {2}\r'.format(qualifier['Room Number'], qualifier['Sub Room'], qualifier['Config File'])
            self.__SetHelper('RoomSelect', RoomSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomSelect')

    def SetSelectPartyLine(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= int(value) <= 5 and 1 <= len(Channel) <= 64:
            SelectPartyLineCmdString = 'EP {0} KEY KEY_PARTY {1}\r'.format(Channel, value)
            self.__SetHelper('SelectPartyLine', SelectPartyLineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelectPartyLine')

    def SetSignalGeneratorEnable(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Channel = qualifier['Channel Name']
        if value in ValueStateValues and 1 <= len(Channel) <= 64:
            SignalGeneratorEnableCmdString = 'EP {0} SIG_GEN ENABLE {1}\r'.format(Channel, ValueStateValues[value])
            self.__SetHelper('SignalGeneratorEnable', SignalGeneratorEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalGeneratorEnable')

    def UpdateSignalGeneratorEnable(self, value, qualifier):

        Channel = qualifier['Channel Name']
        if 1 <= len(Channel) <= 64:
            SignalGeneratorEnableCmdString = 'EP {0} SIG_GEN ENABLE\r'.format(Channel)
            self.__UpdateHelper('SignalGeneratorEnable', SignalGeneratorEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalGeneratorEnable')

    def __MatchSignalGeneratorEnable(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel Name': match.group('Channel').decode()}
        value = match.group('value').decode()
        self.WriteStatus('SignalGeneratorEnable', ValueStateValues[value], qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if isinstance(response, bytes):
            response = response.decode('iso-8859-1')
        if 'ERROR' in response:
            self.Error(['Error Occured with {0}'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.QueryDelayTimer.State != 'Running':
            if not self.QueryFlag:
                self.Send('VERSION * FW 1\r')
                self.QueryDelay = 165
                self.QueryDelayTimer.Restart()
            else:
                if self.initializationChk:
                    self.Send('VERSION * FW 1\r')
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.QueryDelay = 0.5
                self.QueryDelayTimer.Restart()
                if command == 'CallState':
                    res = self.SendAndWait(commandstring + '\r', self.DefaultResponseTimeout, deliRex=self.deliRegex)
                    if not res:
                        return ''
                    else:
                        return self.__CheckResponseForErrors(command, res)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Device Is Busy.')

    def __MatchError(self, match, tag):
        self.counter = 0
        value = match.group(1).decode()
        self.Error(['Error Occured with {0}'.format(value)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.QueryFlag = True

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.QueryFlag = False
        self.PasswdPromptCount = 0

    def clr1_25_2525_beamform(self):
        self.Model = 'beamform'

    def clr1_25_2525_normal_12(self):
        self.ChannelSize = 12
        self.Model = 'normal'

    def clr1_25_2525_voip_12(self):
        self.ChannelSize = 12
        self.Model = 'voip'

    def clr1_25_2525_normal_4(self):
        self.ChannelSize = 4
        self.Model = 'normal'

    def clr1_25_2525_voip_4(self):
        self.ChannelSize = 4
        self.Model = 'voip'

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
        
        # check incoming data if it matched any expected data from device module
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
        self.CreateMatchString()

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
        self.CreateMatchString()

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
        self.CreateMatchString()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()