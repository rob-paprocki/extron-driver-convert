from extronlib.system import Wait, ProgramLog
from extronlib.interface import SerialInterface, EthernetClientInterface
from collections import OrderedDict
import re


class DeviceClass:
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
        self.Models = {
            'MLS 100 A': self.extr_2_195_MLS100,
            'MLS 103 V': self.extr_2_195_Other,
            'MLS 102 VGA': self.extr_2_195_Other,
            'MLS 103 SV': self.extr_2_195_Other,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(Chn|Aud|Vid)(\d)\r\n'), self.__MatchInputSingle, None)
            self.AddMatchString(re.compile(b'Vid([0-3]) Aud([0-4])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'E(\d{2})\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Vol(\d{3})\r\n'), self.__MatchVolume, None)

    def SetInput(self, value, qualifier):
        if self.model == '100A':
            if 0 <= int(value) <= 4:
                InputCmdString = '{0}$'.format(int(value))
                self.__SetHelper('AudioInput', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')
        else:
            SwitchType = qualifier['Type']

            SwitchTypeNames = {
                'Audio': '$',
                'Video': '&',
                'Audio/Video': '!'
            }
            if SwitchType in SwitchTypeNames:
                InputCmdString = '{0}{1}'.format(int(value), SwitchTypeNames[SwitchType])
                self.__SetHelper('AudioVideoInput', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'I', value, qualifier)

    def __MatchInput(self, match, tag):

        if self.model == '100A':
            states = {
                b'0': '0',
                b'1': '1',
                b'2': '2',
                b'3': '3',
                b'4': '4'
            }
            audioInputValue = match.group(2)
            self.WriteStatus('Input', states[audioInputValue], None)
        else:
            videoInputValue = match.group(1).decode()
            audioInputValue = match.group(2).decode()

            if videoInputValue == audioInputValue:
                Channel = videoInputValue
            else:
                Channel = 0

            self.WriteStatus('Input', str(audioInputValue), {'Type': 'Audio'})
            self.WriteStatus('Input', str(videoInputValue), {'Type': 'Video'})
            self.WriteStatus('Input', str(Channel), {'Type': 'Audio/Video'})

    def __MatchInputSingle(self, match, tag):

        Type = match.group(1).decode()
        InputValue = match.group(2).decode()

        if self.model == '100A':
            if Type in ['Chn', 'Aud']:
                self.WriteStatus('Input', str(InputValue), None)
        else:
            CurrentAud = self.ReadStatus('Input', {'Type': 'Audio'})
            CurrentVid = self.ReadStatus('Input', {'Type': 'Video'})
            if Type == 'Chn':
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
            elif Type == 'Aud':
                if InputValue == CurrentVid:
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
                else:
                    self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
            elif Type == 'Vid':
                if InputValue == CurrentAud:
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
                else:
                    self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
                    self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})

    def SetAudioMute(self, value, qualifier):

        cmd = {
            'On': b'1Z',
            'Off': b'0Z'
        }

        self.__SetHelper('AudioMute', cmd[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'Z', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        states = {
            b'1': 'On',
            b'0': 'Off'
        }

        r = match.group(1)
        self.WriteStatus('AudioMute', states[r], None)

    def SetExecutiveMode(self, value, qualifier):

        cmd = {
            'On': b'1X',
            'Off': b'0X'
        }

        self.__SetHelper('ExecutiveMode', cmd[value], value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        states = {
            b'1': 'On',
            b'0': 'Off'
        }

        r = match.group(1)
        self.WriteStatus('ExecutiveMode', states[r], None)

    def SetVolume(self, value, qualifier):

        limits = {
            'min': 0,
            'max': 100
        }

        if limits['min'] <= value <= limits['max']:
            cmd = '{0}V'.format(value)
            self.__SetHelper('Volume', cmd, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __MatchVolume(self, match, tag):
        r = int(match.group(1))
        self.WriteStatus('Volume', r, None)

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

        errorList = {
            b'01': 'Invalid input channel number',
            b'10': 'Invalid command',
            b'13': 'Invalid value',
            b'14': 'Invalid for this configuration'
        }

        err = match.group(1)
        if err in errorList:
            self.Error([errorList[err]])
        else:
            self.Error(['Unrecognized error code: E{0}'.format(err)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def extr_2_195_MLS100(self):
        self.model = '100A'

    def extr_2_195_Other(self):
        self.model = 'Other'

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
            print(command, 'does not exist in the module')

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
