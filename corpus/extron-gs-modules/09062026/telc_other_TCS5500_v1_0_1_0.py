from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait
import re


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
            'MaximumActiveMicrophones': {'Status': {}},
            'MicrophoneControl': {'Parameters': ['Number'], 'Status': {}},
            'MicrophoneMode': {'Status': {}},
            'MicrophoneRequest': {'Parameters': ['Number'], 'Status': {}},
            'MicrophoneReset': {'Status': {}},
            'MicrophoneStatus': {'Parameters': ['Number'], 'Status': {}},
            'Mute': {'Status': {}},
            'MuteDCS': {'Status': {}},
            'PreviousMicOn': {'Status': {}},
            'RequiredConnect': {'Status': {}},
            'RequiredDisconnect': {'Status': {}},
            'RequiredPolling': {'Status': {}},
        }

        self.Counter = 0
        self.HeartbeatWait = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%1([LlD])([0-9]{4})[0-9A-Fa-f]{4}\r'), self.__MatchMicrophoneStatus, None)
            self.AddMatchString(re.compile(b'%1([rs])[0-9A-Fa-f]{4}\r'), self.__MatchMute, None)

    def CalCRC(self, Data):
        val = 0
        for i in Data:
            val = val + i
        return val

    def SetMaximumActiveMicrophones(self, value, qualifier):

        if 1 <= int(value) <= 9:
            MaximumActiveMicrophonesCmdString = '%1xe0{0}{1:04X}\r'.format(value, self.CalCRC(b'1xe0' + value.encode()))
            self.__SetHelper('MaximumActiveMicrophones', MaximumActiveMicrophonesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaximumActiveMicrophones')

    def SetMicrophoneControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        micNum = qualifier['Number']
        if 1 <= micNum <= 999:
            MicControl = '1g{0:04}{1}'.format(micNum, ValueStateValues[value])
            MicrophoneControlCmdString = '%{0}{1:04X}\r'.format(MicControl, self.CalCRC(MicControl.encode()))
            self.__SetHelper('MicrophoneControl', MicrophoneControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneControl')

    def SetMicrophoneMode(self, value, qualifier):

        ValueStateValues = {
            'No Request': '0',
            'With Request': '1',
            'With Request No Clear': '2',
            'Direct Access': '3',
            'FIFO': '4',
            'Group 1': '5',
            'Group 2': '6',
            'Group 3': '7',
            'Group 4': '8',
            'Override': '9'
        }

        MicrophoneModeCmdString = '%1U0{0}{1:04X}\r'.format(ValueStateValues[value], self.CalCRC(b'1U0' + ValueStateValues[value].encode()))
        self.__SetHelper('MicrophoneMode', MicrophoneModeCmdString, value, qualifier)

    def SetMicrophoneRequest(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        micNum = qualifier['Number']
        if 1 <= micNum <= 999:
            MicRequest = '1D{0:04}{1}'.format(micNum, ValueStateValues[value])
            MicrophoneRequestCmdString = '%{0}{1:04X}\r'.format(MicRequest, self.CalCRC(MicRequest.encode()))
            self.__SetHelper('MicrophoneRequest', MicrophoneRequestCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneRequest')

    def SetMicrophoneReset(self, value, qualifier):

        MicrophoneResetCmdString = '%1xJ00F3\r'
        self.__SetHelper('MicrophoneReset', MicrophoneResetCmdString, value, qualifier)

    def __MatchMicrophoneStatus(self, match, tag):

        ValueStateValues = {
            'L': 'Activated',
            'l': 'Deactivated',
            'D': 'In Request'
        }

        qualifier = {'Number': int(match.group(2).decode())}
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MicrophoneStatus', value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '%1r00A3\r',
            'Off': '%1s00A4\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'r': 'On',
            's': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetMuteDCS(self, value, qualifier):

        MuteDCSCmdString = '%1xf010F\r'
        self.__SetHelper('MuteDCS', MuteDCSCmdString, value, qualifier)

    def SetPreviousMicOn(self, value, qualifier):

        PreviousMicOnCmdString = '%1u00A6\r'
        self.__SetHelper('PreviousMicOn', PreviousMicOnCmdString, value, qualifier)

    def UpdateRequiredConnect(self):
        RequiredConnectCmdString = '%10C00A4\r'
        res = self.__UpdateHelper('RequiredConnect', RequiredConnectCmdString, None, None)
        if res:
            if res[2] == '0':
                if self.HeartbeatWait:
                    self.HeartbeatWait.Restart()
                else:
                    self.HeartbeatWait = Wait(5, self.UpdateRequiredPolling)
            elif res[2] == '9':
                if res[3] == 'a':
                    self.Error(['Connect Request: Client not allowed. Please register the client IP address.'])
                elif res[3] == 'b':
                    self.Error(['Connect Request: Maximum clients has exceeded.'])
                else:
                    self.Error(['Connect Request: Unknown Error.'])
        else:
            self.Error(['Connect Request: No Response'])

    def UpdateRequiredDisconnect(self):
        RequiredDisconnectCmdString = '%110062\r'
        res = self.__UpdateHelper('RequiredDisconnect', RequiredDisconnectCmdString, None, None)
        if res:
            self.UpdateRequiredConnect()
        else:
            self.Error(['Disconnect Request: No Response'])

    def UpdateRequiredPolling(self):
        RequiredPollingCmdString = '%120063\r'
        res = self.__UpdateHelper('RequiredPolling', RequiredPollingCmdString, None, None)
        self.HeartbeatWait.Restart()
        if res:
            self.Counter = 0
        else:
            self.Counter = self.Counter + 1
            if self.Counter > 3:
                self.UpdateRequiredDisconnect()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return res.decode()

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
        except BaseException:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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
                
    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.UpdateRequiredConnect()
        return result
        
    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
