from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog

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
            'CallStatus': {'Parameters': ['Number'], 'Status': {}},
            'CallStatus2': {'Parameters': ['Number'], 'Status': {}},
            'Connect': {'Parameters': ['Number'], 'Status': {}},
            'MessageListStatus': {'Status': {}},
            'Volume': {'Parameters': ['Input', 'Major Channel', 'Minor Channel'], 'Status': {}}
        }

        self.Authenticated = 'None'
        self.ErrorList = ['DEFECT', 'Mikrophon def', 'CONTROL', 'CONTACT', 'Power Supply', 'Battery voltage', 'System overheat', 'System temperature', 'FLASH CHECKSUM', 'BACKUP', 'AUDIO OK', 'IMP SHORT']
        
        self._deviceUsername = None
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Logon:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Incorrect password\r\n'), self.__MatchPasswordFailure, None)
            self.AddMatchString(re.compile(b'vol\s(pa|pr|sg)\s(\d{1,3})\.(\d{1,3})\s(-?\d{1,2})\r\n'), self.__MatchVolume, None)
            
    @property
    def deviceUsername(self):
        return self._deviceUsername
    
    @deviceUsername.setter
    def deviceUsername(self, value):
        self._deviceUsername = value
        self.AddMatchString(re.compile(value.encode() + b'\[0\]@'), self.__MatchPasswordSuccessful, None)

    def SetUsername(self, value, qualifier):
        if self._deviceUsername is not None:
            self.Send(self._deviceUsername + '\n')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, tag):
        self.SetUsername(match, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\n')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def __MatchPasswordFailure(self, match, tag):

        self.Authenticated = 'None'
        print('Password is wrong. Please enter correct Password')

    def __MatchPasswordSuccessful(self, match, tag):

        self.Authenticated = 'User'

    def UpdateCallStatus(self, value, qualifier):

        ValueStateValues = {
            'FULLCON': 'Occupied',
            'PARTCON': 'Occupied',
            'WAITING': 'Waiting',
            'BREAK': 'Waiting'
        }

        ValueStateValues2 = {
            'FULLCON': 'Fullcon',
            'PARTCON': 'Partcon',
            'WAITING': 'Waiting',
            'BREAK': 'Break'
        }

        NumberConstraints = {
            'Min': 1,
            'Max': 999
        }


        number = qualifier['Number']
        if NumberConstraints['Min'] <= number <= NumberConstraints['Max']:
            CallStatusCmdString = 'constat\r\n'
            res = self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
            if res:
                try:
                    temp = re.findall(r'CS\s(\d{3}).*?(PARTCON|FULLCON|WAITING|BREAK)', res)
                    if temp:
                        numberArray = []
                        for i in range(0, len(temp)):
                            numberArray.append(str(int(temp[i][0])))
                            self.WriteStatus('CallStatus2', ValueStateValues2[temp[i][1]], {'Number': int(temp[i][0])})
                            self.WriteStatus('CallStatus', ValueStateValues[temp[i][1]], {'Number': int(temp[i][0])})
                        for i in range(1, 1000):
                            if str(i) not in numberArray:
                                self.WriteStatus('CallStatus2', 'None', {'Number': i})
                                self.WriteStatus('CallStatus', 'Free', {'Number': i})
                    else:
                        for i in range(1, 1000):
                            self.WriteStatus('CallStatus2', 'None', {'Number': i})
                            self.WriteStatus('CallStatus', 'Free', {'Number': i})
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateCallStatus')
        else:
            print('Invalid Command for UpdateCallStatus')

    def UpdateCallStatus2(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def SetConnect(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 999
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        number = qualifier['Number']
        if NumberConstraints['Min'] <= number <= NumberConstraints['Max']:
            ConnectCmdString = 'csctrl {0} {1}\r\n'.format(number, ValueStateValues[value])
            self.__SetHelper('Connect', ConnectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetConnect')

    def SetMessageListRefresh(self, value, qualifier):

        self.UpdateMessageListStatus(value, qualifier)

    def UpdateMessageListStatus(self, value, qualifier):

        MessageCmdString = 'mlst\r\n'
        res = self.__UpdateHelper('MessageListStatus', MessageCmdString, value, qualifier)
        if res:
            try:
                finalArray = []
                message = re.findall('(\d{4}/\d{2}/\d{2} \- \d{2}:\d{2}:\d{2} SYS\-LO .*)', res)
                for i in range(0, len(message)):
                    for j in range(0, len(self.ErrorList)):
                        if self.ErrorList[j] in message[i] and message[i] not in finalArray:
                            finalArray.append(message[i])
                self.WriteStatus('MessageListStatus', finalArray[::-1][:16][::-1], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMessageListStatus')

    def SetVolume(self, value, qualifier):

        InputStates = {
            'Power Amplifier': 'pa',
            'Pre-Amplifier': 'pr',
            'Signal Generator': 'sg'
        }

        ValueConstraints = {
            'Min': -80,
            'Max': 6
        }

        input_ = qualifier['Input']
        majorchannel = qualifier['Major Channel']
        minorchannel = qualifier['Minor Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'vol {0} {1}.{2} {3}\r\n'.format(InputStates[input_], majorchannel, minorchannel, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __MatchVolume(self, match, tag):

        InputStates = {
            'pa': 'Power Amplifier',
            'pr': 'Pre-Amplifier',
            'sg': 'Signal Generator'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        qualifier['Major Channel'] = str(int(match.group(2).decode()))
        qualifier['Minor Channel'] = str(int(match.group(3).decode()))
        value = int(match.group(4).decode())
        self.WriteStatus('Volume', value, qualifier)

    def UpdateVolume(self, value, qualifier):

        InputStates = {
            'PA': 'Power Amplifier',
            'PR': 'Pre-Amplifier',
            'SG': 'Signal Generator'
        }

        VolumeCmdString = 'vol\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(PR|PA|SG)\s(\d{3})\.(\d{2})\s+?(-?\d{2})', res)
                for i in range(0, len(temp)):
                    self.WriteStatus('Volume', int(temp[i][3]), {'Input': InputStates[temp[i][0]], 'Major Channel': str(int(temp[i][1])), 'Minor Channel': str(int(temp[i][2]))})
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Authenticated in ['User']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command')
                return ''
            else:
                if command == 'MessageListStatus':
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'] >').decode()
                else:
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'>').decode()

                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            print('Inappropriate Command')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'None'

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
