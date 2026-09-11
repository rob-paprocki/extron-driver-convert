from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
from re import compile, match, search
from binascii import hexlify, unhexlify

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
        self.Models = {
            'Galileo 616': self.myrs_25_134_616,
            'Galileo 408': self.myrs_25_134_408,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'Ping': {'Status': {}},
            'Recall': {'Parameters': ['CueListPlayer', 'Type'], 'Status': {}},
            'Transport': {'Parameters': ['CueListPlayer'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(\0\0\0[\x20\x24]/got\0\0\0\0,sbf\0\0\0\0\0\0\0\0\0\0\0[\x04\x06]\xff\x8e\xff\xa2[\x00-\xff]{4,8})'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'(\0\0\0[\x2c\x30]/got\0\0\0\0,sbf\0\0\0\0req-InputGain\0\0\0\0\0\0[\x04\x06]\xff\x8e\xff\xa2[\x00-\xff]{4,8})'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'(\0\0\0[\x1c\x20]/got\0\0\0\0,sb[TF]\0\0\0\0\0\0\0\0\0\0\0[\x04\x06]\xff\x8e\xff\xa4[\x00-\xff]{0,4})'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'(\0\0\0[\x28\x2c]/got\0\0\0\0,sb[TF]\0\0\0\0req-InputMute\0\0\0\0\0\0[\x04\x06]\xff\x8e\xff\xa4[\x00-\xff]{0,4})'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'(\0\0\0[\x20\x24]/got\0\0\0\0,sbf\0\0\0\0\0\0\0\0\0\0\0[\x04\x06]\xff\x8f\xff\xa2[\x00-\xff]{4,8})'), self.__MatchOutputGain, None)
            self.AddMatchString(compile(b'(\0\0\0[\x2c\x30]/got\0\0\0\0,sbf\0\0\0\0req-OutputGain\0\0\0\0\0[\x04\x06]\xff\x8f\xff\xa2[\x00-\xff]{4,8})'), self.__MatchOutputGain, None)
            self.AddMatchString(compile(b'(\0\0\0[\x1c\x20]/got\0\0\0\0,sb[TF]\0\0\0\0\0\0\0\0\0\0\0[\x04\x06]\xff\x8f\xff\xa4[\x00-\x0f]{0,4})'), self.__MatchOutputMute, None)
            self.AddMatchString(compile(b'(\0\0\0[\x28\x2c]/got\0\0\0\0,sb[TF]\0\0\0\0req-OutputMute\0\0\0\0\0[\x04\x06]\xff\x8f\xff\xa4[\x00-\x0f]{0,4})'), self.__MatchOutputMute, None)

    def SetInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if -60.0 <= value <= 10.0 and Input in self.Inputs:
            oscm = OSCMsg('set', ['input {0} gain'.format(Input), value])
            self.__SetHelper('InputGain', oscm, value, qualifier)
        else:
            self.Discard('Invalid command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.Inputs:
            oscm = OSCMsg('get', ['input {0} gain'.format(Input), 'req-InputGain'])
            self.__UpdateHelper('InputGain', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        InputValues = {
            b'\xff\x8e\xff\xa2': 'A',
            b'\xff\x8e\xff\xa2\x00\x01': 'B',
            b'\xff\x8e\xff\xa2\x00\x02': 'C',
            b'\xff\x8e\xff\xa2\x00\x03': 'D',
            b'\xff\x8e\xff\xa2\x00\x04': 'E',
            b'\xff\x8e\xff\xa2\x00\x05': 'F',
        }
        data = OSCMsg(Message=match.group(0)).getData()
        qualifier = {'Input': InputValues[data[1]]}
        value = data[2]
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        InputMuteStates = {'On': True, 'Off': False}
        Input = qualifier['Input']
        if Input in self.Inputs:
            oscm = OSCMsg('set', ['input {0} mute'.format(Input), InputMuteStates[value]])
            self.__SetHelper('InputMute', oscm, value, qualifier)
        else:
            self.Discard('Invalid command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.Inputs:
            oscm = OSCMsg('get', ['input {0} mute'.format(Input), 'req-InputMute'])
            self.__UpdateHelper('InputMute', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        InputValues = {
            b'\xff\x8e\xff\xa4': 'A',
            b'\xff\x8e\xff\xa4\x00\x01': 'B',
            b'\xff\x8e\xff\xa4\x00\x02': 'C',
            b'\xff\x8e\xff\xa4\x00\x03': 'D',
            b'\xff\x8e\xff\xa4\x00\x04': 'E',
            b'\xff\x8e\xff\xa4\x00\x05': 'F',
        }
        InputMuteStates = {True: 'On', False: 'Off'}
        data = OSCMsg(Message=match.group(0)).getData()
        qualifier = {'Input': InputValues[data[1]]}
        value = InputMuteStates[data[2]]
        self.WriteStatus('InputMute', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if -60.0 <= value <= 10.0 and self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            oscm = OSCMsg('set', ['output {0} gain'.format(Output), value])
            self.__SetHelper('OutputGain', oscm, value, qualifier)
        else:
            self.Discard('Invalid command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            oscm = OSCMsg('get', ['output {0} gain'.format(Output), 'req-OutputGain'])
            self.__UpdateHelper('OutputGain', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        OutputValues = {
            b'\xff\x8f\xff\xa2': '1',
            b'\xff\x8f\xff\xa2\x00\x01': '2',
            b'\xff\x8f\xff\xa2\x00\x02': '3',
            b'\xff\x8f\xff\xa2\x00\x03': '4',
            b'\xff\x8f\xff\xa2\x00\x04': '5',
            b'\xff\x8f\xff\xa2\x00\x05': '6',
            b'\xff\x8f\xff\xa2\x00\x06': '7',
            b'\xff\x8f\xff\xa2\x00\x07': '8',
            b'\xff\x8f\xff\xa2\x00\x08': '9',
            b'\xff\x8f\xff\xa2\x00\x09': '10',
            b'\xff\x8f\xff\xa2\x00\x0a': '11',
            b'\xff\x8f\xff\xa2\x00\x0b': '12',
            b'\xff\x8f\xff\xa2\x00\x0c': '13',
            b'\xff\x8f\xff\xa2\x00\x0d': '14',
            b'\xff\x8f\xff\xa2\x00\x0e': '15',
            b'\xff\x8f\xff\xa2\x00\x0f': '16',
        }
        data = OSCMsg(Message=match.group(0)).getData()
        qualifier = {'Output': OutputValues[data[1]]}
        value = data[2]
        self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        OutputMuteStates = {'On': True, 'Off': False}
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            oscm = OSCMsg('set', ['output {0} mute'.format(Output), OutputMuteStates[value]])
            self.__SetHelper('OutputMute', oscm, value, qualifier)
        else:
            self.Discard('Invalid command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            oscm = OSCMsg('get', ['output {0} mute'.format(Output), 'req-OutputMute'])
            self.__UpdateHelper('OutputMute', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        OutputValues = {
            b'\xff\x8f\xff\xa4': '1',
            b'\xff\x8f\xff\xa4\x00\x01': '2',
            b'\xff\x8f\xff\xa4\x00\x02': '3',
            b'\xff\x8f\xff\xa4\x00\x03': '4',
            b'\xff\x8f\xff\xa4\x00\x04': '5',
            b'\xff\x8f\xff\xa4\x00\x05': '6',
            b'\xff\x8f\xff\xa4\x00\x06': '7',
            b'\xff\x8f\xff\xa4\x00\x07': '8',
            b'\xff\x8f\xff\xa4\x00\x08': '9',
            b'\xff\x8f\xff\xa4\x00\x09': '10',
            b'\xff\x8f\xff\xa4\x00\x0a': '11',
            b'\xff\x8f\xff\xa4\x00\x0b': '12',
            b'\xff\x8f\xff\xa4\x00\x0c': '13',
            b'\xff\x8f\xff\xa4\x00\x0d': '14',
            b'\xff\x8f\xff\xa4\x00\x0e': '15',
            b'\xff\x8f\xff\xa4\x00\x0f': '16',
        }
        OutputMuteValues = {True: 'On', False: 'Off'}
        data = OSCMsg(Message=match.group(0)).getData()
        qualifier = {'Output': OutputValues[data[1]]}
        value = OutputMuteValues[data[2]]
        self.WriteStatus('OutputMute', value, qualifier)

    def UpdatePing(self, value, qualifier):

        self.__UpdateHelper('Ping', OSCMsg('ping'), value, qualifier)

    def SetRecall(self, value, qualifier):

        Type = {'Cue': 0, 'Subcue': 1}[qualifier['Type']]
        CueListPlayer = qualifier['CueListPlayer']
        if 0 <= CueListPlayer <= 127 and 0 <= value <= 16382:
            oscm = OSCMsg('recall', [Type, value, CueListPlayer])
            self.__SetHelper('Recall', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecall')

    def SetTransport(self, value, qualifier):

        TransportStates = {
            'Go': 'go',
            'Stop': 'stop',
            'Next': 'moveby',
            'Previous': 'moveby',
        }

        CueListPlayer = qualifier['CueListPlayer']
        if 0 <= CueListPlayer <= 127:
            data = [CueListPlayer]
            if value in ['Next', 'Previous']:
                data.append({'Next': 1, 'Previous': -1}[value])
            oscm = OSCMsg(TransportStates[value], data)
            self.__SetHelper('Transport', oscm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def __SetHelper(self, command, oscm, value, qualifier):
        self.Debug = True

        self.Send(oscm.encodeMessage())

    def __UpdateHelper(self, command, oscm, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            self.Send(oscm.encodeMessage())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def myrs_25_134_408(self):

        self.Inputs = 'ABCD'
        self.Outputs = (1, 8)

    def myrs_25_134_616(self):

        self.Inputs = 'ABCDEF'
        self.Outputs = (1, 16)

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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

class OSCMsg(object):

    Commands = ['go', 'stop', 'moveby', 'recall', 'set', 'setwf', 'setblock',
                'setblockwf', 'get', 'getblock', 'ping', 'subscribe', 'subscribeblock',
                'unsubscribe', 'unsubscribeblock', 'unsubscribeall', 'log']

    Responses = ['got', 'pong']

    DataTypes = {               # Data types supported by OSC
        int: 'i',
        float: 'f',
        str: 's',
        bytes: 'b',
        bool: {False: 'F', True: 'T'},
    }

    SeverityLevels = {          # Security levels for the 'log' command.
        'Critical Error': 1,
        'Error': 2,
        'Warning': 3,
        'Info': 4,
        'Debug': 5,
        'Trace': 6,
    }

    def __init__(self, Command=None, Data=[], Message=None):
        if Command:
            self.setCommand(Command)
        else:
            self.__command = None

        if Data:
            self.setData(Data)
        else:
            self.__data = []

        if Message:
            self.decodeMessage(Message)

    def __str__(self):
        return ' '.join(['/' + self.getCommand('STR'), self.getDataTypes('STR'), self.getData('STR')])

    def pad(self, segment):

        try:
            return segment + (4 - len(segment) % 4) * '\x00'
        except BaseException:
            if isinstance(segment, int):
                return segment + 4 - segment % 4
            elif isinstance(segment, bytes):
                return segment + (4 - len(segment) % 4) * b'\x00'
            else:
                return None

    def unpad(self, segment):

        return segment[:segment.index(b'\x00')]

    def setCommand(self, Command):

        if Command in self.Commands:
            self.__command = Command
        else:
            raise ValueError('UserInput ' + Command)

    def getCommand(self, Format='BYTES'):

        if self.__command:
            if Format == 'BYTES':
                return self.pad('/' + self.__command).encode()
            elif Format == 'STR':
                return self.__command
            else:
                return None
        else:
            if Format == 'BYTES':
                return b''
            elif Format == 'STR':
                return ''
            else:
                return None

    def getDataTypes(self, Format='BYTES'):

        if self.__data:
            ds = ','
            for datum in self.__data:
                dt = type(datum)
                if dt == bool:
                    ds += self.DataTypes[dt][datum]
                elif datum is None:
                    ds += 'N'
                elif datum == 'Impulse':
                    ds += 'I'
                else:
                    ds += self.DataTypes[dt]
            if Format == 'BYTES':
                return self.pad(ds).encode()
            elif Format == 'STR':
                return ds
            else:
                return None
        else:
            if Format == 'BYTES':
                return b''
            elif Format == 'STR':
                return ''
            else:
                return None

    def setData(self, Data):

        for datum in Data:
            if datum is not None and datum != 'Impulse' and type(datum) not in self.DataTypes:
                raise ValueError('UserInput ' + datum)
        self.__data = Data

    def getData(self, Format='LIST'):

        if self.__data:
            if Format == 'BYTES':
                data = b''
                for datum in self.__data:
                    dt = type(datum)
                    if dt == int:
                        data += pack('>i', datum)
                    elif dt == float:
                        data += pack('>f', datum)
                    elif dt == str:
                        if datum != 'Impulse':
                            data += self.pad(datum).encode()
                    elif dt == bytes:
                        size = len(datum)
                        if size == 4:
                            data += pack('>i', size) + datum
                        else:
                            data += pack('>i', size) + self.pad(datum)
                return data
            elif Format == 'STR':
                return ' '.join([str(datum) for datum in self.__data])
            elif Format == 'LIST':
                return self.__data
            else:
                return None
        else:
            if Format == 'BYTES':
                return b''
            elif Format == 'STR':
                return ''
            elif Format == 'LIST':
                return []
            else:
                return None

    def encodeMessage(self, Format='BYTES'):

        if Format == 'BYTES':
            m = self.getCommand() + self.getDataTypes() + self.getData('BYTES')
            return pack('>i', len(m)) + m
        elif Format == 'EXTRON':
            return (b'%' + b'%'.join([hexlify(b.to_bytes(1, 'big')) for b in self.encodeMessage()])).decode()

    def decodeMessage(self, m):

        length, message = unpack('>i', m[:4])[0], m[4:]                                         # Separate length and message
        if length == len(message):                                                              # Verify length
            self.__command = self.unpad(message)[1:].decode()                                   # Extract Command
            message = message[self.pad(len('/' + self.__command)):]
            if message:                                                                         # Test for attached data
                dataTypes = self.unpad(message)[1:].decode()                                    # Extract Data Types
                data = message[self.pad(len(',' + dataTypes)):]
                for dataType in dataTypes:
                    if dataType == 'i':                                                         # Extract Integer, 4 bytes
                        datum = unpack('>i', data[:4])[0]
                        data = data[4:]
                    elif dataType == 'f':                                                       # Extract Float, 4 bytes
                        datum = unpack('>f', data[:4])[0]
                        data = data[4:]
                    elif dataType == 's':                                                       # Extract String, null terminated
                        datum = self.unpad(data).decode()
                        data = data[self.pad(len(datum)):]
                    elif dataType in ['T', 'F', 'N', 'I']:                                      # True, False, None, Impulse: No actuall data
                        datum = {'T': True, 'F': False, 'N': None, 'I': 'Impulse'}[dataType]
                    elif dataType == 'b':                                                       # Extract Blob (ByteArray), Data is prefixed with a 4 byte Integer length.
                        size, data = unpack('>i', data[:4])[0], data[4:]                        # Separate size and datum
                        datum = data[:size]
                        if size == 4:
                            data = data[size:]
                        else:
                            data = data[self.pad(size):]
                    self.__data.append(datum)                                                   # Append to data
                if data:
                    raise ValueError('Leftovers: {}'.format(data))                              # This most likely means the beginning of the message is unknown/misplaced.
        else:
            raise ValueError('Incomplete message: expected {0} bytes, received {1} bytes.'.format(length, len(message)))
