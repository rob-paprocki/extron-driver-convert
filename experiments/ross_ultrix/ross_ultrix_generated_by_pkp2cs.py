# Copyright 2026, Extron. All rights reserved.

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'RefreshMatrix': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'RequiredCommand': {'Status': {}},
            }

        pass

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x10\x02[\x03\x04]([\x00-\x0f])\x00([\x00-?]{2,4})[\x05-\x07][\x00-\xff]{1,2}\x10\x03'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'\x10\x02[\x83\x84]\x00([\x00-\x0f]|\x10\x10)([\x00-?]{4,7})[\x07-\x08][\x00-\xff]{1,2}\x10\x03'), self.__MatchOutputTieStatus, 'Extended')

    def SetMatrixTieCommand(self, value, qualifier):
        TieTypeStates = {'Video': 0, 'Audio 1': 1, 'Audio 2': 2, 'Audio 3': 3, 'Audio 4': 4, 'Audio 5': 5, 'Audio 6': 6, 'Audio 7': 7, 'Audio 8': 8, 'Audio 9': 9, 'Audio 10': 10, 'Audio 11': 11, 'Audio 12': 12, 'Audio 13': 13, 'Audio 14': 14, 'Audio 15': 15, 'Audio 16': 16}
        input_val = int(qualifier['Input'])
        output_val = int(qualifier['Output'])
        tie_val = qualifier['Tie Type']
        if 1 <= input_val <= 64 and 1 <= output_val <= 64 and (tie_val in TieTypeStates):
            buffer = [130, 0, TieTypeStates[tie_val], 0, output_val - 1, 0, input_val - 1, 7]
            buffer.append(self.CalcChecksum(buffer))
            MatrixTieCommandCmdString = b''.join([b'\x10\x02', bytes(self.escaped(buffer)), b'\x10\x03'])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __MatchOutputTieStatus(self, match, tag):
        self.Send(b'\x10\x06')
        TieTypeStates = {0: 'Video', 1: 'Audio 1', 2: 'Audio 2', 3: 'Audio 3', 4: 'Audio 4', 5: 'Audio 5', 6: 'Audio 6', 7: 'Audio 7', 8: 'Audio 8', 9: 'Audio 9', 10: 'Audio 10', 11: 'Audio 11', 12: 'Audio 12', 13: 'Audio 13', 14: 'Audio 14', 15: 'Audio 15', 16: 'Audio 16'}
        io_val = match.group(2).replace(b'\x10\x10', b'\x10')
        if tag != 'Extended':
            qualifier = {'Output': str(io_val[0] + 1), 'Tie Type': TieTypeStates[match.group(1)[0]]}
            value = str(io_val[1] + 1)
        else:
            qualifier = {'Output': str(io_val[1] + 1), 'Tie Type': TieTypeStates[match.group(1)[0]]}
            value = str(io_val[3] + 1)
        self.WriteStatus('OutputTieStatus', value, qualifier)
        if qualifier == {'Output': '1', 'Tie Type': 'Video'}:
            pass

    def SetRefreshMatrix(self, value, qualifier):
        output = int(qualifier['Output'])
        TieTypeStates = {'Video': 0, 'Audio 1': 1, 'Audio 2': 2, 'Audio 3': 3, 'Audio 4': 4, 'Audio 5': 5, 'Audio 6': 6, 'Audio 7': 7, 'Audio 8': 8, 'Audio 9': 9, 'Audio 10': 10, 'Audio 11': 11, 'Audio 12': 12, 'Audio 13': 13, 'Audio 14': 14, 'Audio 15': 15, 'Audio 16': 16}
        tie_type = qualifier['Tie Type']
        if 1 <= output <= 64 and tie_type in TieTypeStates:
            buffer = [129, 0, TieTypeStates[tie_type], 0, output - 1, 5]
            buffer.append(self.CalcChecksum(buffer))
            MatrixCmdString = b''.join([b'\x10\x02', bytes(self.escaped(buffer)), b'\x10\x03'])
            self.__SetHelper('RefreshMatrix', MatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def UpdateRequiredCommand(self, value, qualifier):
        buffer = [129, 0, 0, 0, 0, 5]
        buffer.append(self.CalcChecksum(buffer))
        RequiredCommandCmdString = b''.join([b'\x10\x02', bytes(self.escaped(buffer)), b'\x10\x03'])
        self.__UpdateHelper('RequiredCommand', RequiredCommandCmdString, value, qualifier)

    def escaped(self, Data):
        d = 0
        List = []
        Escaped = {16: [16, 16]}
        for d in Data:
            if d in Escaped:
                List.append(Escaped[d][0])
                List.append(Escaped[d][1])
            else:
                List.append(d)
        return List

    def CalcChecksum(self, buffer):
        sum = 0
        for val in buffer:
            sum += 255 - val + 1
        return sum & 255

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

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

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
