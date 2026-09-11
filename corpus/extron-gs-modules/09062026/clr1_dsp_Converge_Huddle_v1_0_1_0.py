from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.deviceUsername = 'clearone'
        self.devicePassword = 'converge'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'OutputGain': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'SpeakerGain': {'Parameters': ['Speaker Number'], 'Status': {}},
            'SpeakerMute': {'Parameters': ['Speaker Number'], 'Status': {}},
        }

        self.PasswdPromptCount = 0
        self.QueryFlag = True

        self.AddMatchString(re.compile(b'Username:\s'), self.__MatchUsername, None)
        self.AddMatchString(re.compile(b'Password:\s'), self.__MatchPassword, None)

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'VERSION ([\S ]+\r)'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'EP OUTPUT ([12]) LEVEL GAIN (-?\d{1,2}(?:\.\d{1,2})?)\r'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'EP OUTPUT ([12]) LEVEL MUTE ([01])\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'EP SPEAKER ([12]) LEVEL GAIN (-?\d{1,2}(?:\.\d{1,2})?)\r'), self.__MatchSpeakerGain, None)
            self.AddMatchString(re.compile(b'EP SPEAKER ([12]) LEVEL MUTE ([01])\r'), self.__MatchSpeakerMute, None)
            self.AddMatchString(re.compile(b'STACK NOTIFICATION HW_RESYNC.*'), self.__MatchQueryFlag, None)

    def __MatchUsername(self, match, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):

        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password.'])
        else:
            if self.devicePassword is not None:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')
            self.PasswdPromptCount += 1

    def __MatchQueryFlag(self, match, qualifier):
        self.QueryFlag = True

    def UpdateFirmwareVersion(self, value, qualifier):
        FirmwareVersionCmdString = 'VERSION * FW 1\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        if match.group(0).decode() == 'VERSION * FW 1\x00\r':
            self.QueryFlag = False
            self.WriteStatus('FirmwareVersion', 'Initializing', None)
        else:
            value = match.group(1).decode()
            value = value.split(' ')[3]

            self.WriteStatus('FirmwareVersion', value, None)

    def SetOutputGain(self, value, qualifier):

        channel = qualifier['Channel']
        if -65 <= value <= 20 and channel in ['1', '2']:
            OutputGainCmdString = 'EP OUTPUT {} LEVEL GAIN {}\r'.format(channel, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['1', '2']:
            OutputGainCmdString = 'EP OUTPUT {} LEVEL GAIN\r'.format(channel)
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Channel': match.group(1).decode()}
        value = float(match.group(2).decode())
        self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['Channel']
        if channel in ['1', '2']:
            OutputMuteCmdString = 'EP OUTPUT {} LEVEL MUTE {}\r'.format(channel, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['1', '2']:
            OutputMuteCmdString = 'EP OUTPUT {} LEVEL MUTE\r'.format(channel)
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetSpeakerGain(self, value, qualifier):

        spkrnum = qualifier['Speaker Number']
        if -65 <= value <= 20 and spkrnum in ['1', '2']:
            SpeakerGainCmdString = 'EP SPEAKER {} LEVEL GAIN {}\r'.format(spkrnum, value)
            self.__SetHelper('SpeakerGain', SpeakerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerGain')

    def UpdateSpeakerGain(self, value, qualifier):

        spkrnum = qualifier['Speaker Number']
        if spkrnum in ['1', '2']:
            SpeakerGainCmdString = 'EP SPEAKER {} LEVEL GAIN\r'.format(spkrnum)
            self.__UpdateHelper('SpeakerGain', SpeakerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeakerGain')

    def __MatchSpeakerGain(self, match, tag):

        qualifier = {'Speaker Number': match.group(1).decode()}
        value = float(match.group(2).decode())
        self.WriteStatus('SpeakerGain', value, qualifier)

    def SetSpeakerMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        spkrnum = qualifier['Speaker Number']
        if spkrnum in ['1', '2']:
            SpeakerMuteCmdString = 'EP SPEAKER {} LEVEL MUTE {}\r'.format(spkrnum, ValueStateValues[value])
            self.__SetHelper('SpeakerMute', SpeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerMute')

    def UpdateSpeakerMute(self, value, qualifier):

        spkrnum = qualifier['Speaker Number']
        if spkrnum in ['1', '2']:
            SpeakerMuteCmdString = 'EP SPEAKER {} LEVEL MUTE\r'.format(spkrnum)
            self.__UpdateHelper('SpeakerMute', SpeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeakerMute')

    def __MatchSpeakerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Speaker Number': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SpeakerMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if not self.QueryFlag:
            self.Send('VERSION * FW 1\r')
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0
        value = match.group(1).decode()
        self.Error(['Error Occured with {0}'.format(value)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.PasswdPromptCount = 0
        self.QueryFlag = True

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
        if command in self.Subscription:
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
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
