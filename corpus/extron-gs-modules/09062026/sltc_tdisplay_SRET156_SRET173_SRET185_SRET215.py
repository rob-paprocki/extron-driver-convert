from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
from struct import pack


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Input': {'Parameters': ['DeviceID'], 'Status': {}},
            'LocalButtons': {'Parameters': ['DeviceID'], 'Status': {}},
            'Monitor': {'Parameters': ['DeviceID'], 'Status': {}},
            'Power': {'Parameters': ['DeviceID'], 'Status': {}},
            'Tilt': {'Parameters': ['DeviceID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\x02\x01([\x00-\x1F])[\x00|\x01]([\x00-\xFF])\x03'), self.__MatchPower, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': 0,
            'DVI': 1
        }

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 4 + ValueStateValues[value] + 3)
            InputCmdString = pack('7B', 2, 1, DeviceID, 4, ValueStateValues[value], 3, checksum)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            self.UpdatePower(value, {'DeviceID': str(DeviceID)})
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetLocalButtons(self, value, qualifier):

        ValueStateValues = {
            'Enable': 0,
            'Disable': 1
        }

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 2 + ValueStateValues[value] + 3)
            LocalButtonsCmdString = pack('7B', 2, 1, DeviceID, 2, ValueStateValues[value], 3, checksum)
            self.__SetHelper('LocalButtons', LocalButtonsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLocalButtons')

    def UpdateLocalButtons(self, value, qualifier):

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            self.UpdatePower(value, {'DeviceID': str(DeviceID)})
        else:
            self.Discard('Invalid Command for UpdateLocalButtons')

    def SetMonitor(self, value, qualifier):

        ValueStateValues = {
            'Up': 0,
            'Down': 1
        }

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 0 + ValueStateValues[value] + 3)
            MonitorCmdString = pack('7B', 2, 1, DeviceID, 0, ValueStateValues[value], 3, checksum)
            self.__SetHelper('Monitor', MonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMonitor')

    def UpdateMonitor(self, value, qualifier):

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            self.UpdatePower(value, {'DeviceID': str(DeviceID)})
        else:
            self.Discard('Invalid Command for UpdateMonitor')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0,
            'Off': 1
        }

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 3 + ValueStateValues[value] + 3)
            PowerCmdString = pack('7B', 2, 1, DeviceID, 3, ValueStateValues[value], 3, checksum)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 5 + 0 + 3)
            PowerCmdString = pack('7B', 2, 1, DeviceID, 5, 0, 3, checksum)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        InputStateValues = {
            '0': 'VGA',
            '1': 'DVI'
        }

        LocalButtonsStateValues = {
            '0': 'Enable',
            '1': 'Disable'
        }

        MonitorStateValues = {
            '0': 'Up',
            '1': 'Down'
        }

        PowerStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        TiltStateValues = {
            '00': '20 Degree',
            '01': '0 Degree',
            '10': 'Unknown Position'
        }

        DeviceID = ord(match.group(1))
        ret_value = '{0:08b}'.format(ord(match.group(2)))

        self.WriteStatus('Input', InputStateValues[ret_value[1]], {'DeviceID': str(DeviceID)})
        self.WriteStatus('LocalButtons', LocalButtonsStateValues[ret_value[3]], {'DeviceID': str(DeviceID)})
        self.WriteStatus('Monitor', MonitorStateValues[ret_value[7]], {'DeviceID': str(DeviceID)})
        self.WriteStatus('Power', PowerStateValues[ret_value[2]], {'DeviceID': str(DeviceID)})
        self.WriteStatus('Tilt', TiltStateValues[ret_value[4:6]], {'DeviceID': str(DeviceID)})

    def SetTilt(self, value, qualifier):

        ValueStateValues = {
            '0 Degree': 1,
            '20 Degree': 0
        }

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            checksum = 256 - (2 + 1 + DeviceID + 1 + ValueStateValues[value] + 3)
            TiltCmdString = pack('7B', 2, 1, DeviceID, 1, ValueStateValues[value], 3, checksum)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def UpdateTilt(self, value, qualifier):

        DeviceID = int(qualifier['DeviceID'])
        if 0 <= DeviceID <= 31:
            self.UpdatePower(value, {'DeviceID': str(DeviceID)})
        else:
            self.Discard('Invalid Command for UpdateTilt')

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
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='Serial_RS232', Model=None):
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
