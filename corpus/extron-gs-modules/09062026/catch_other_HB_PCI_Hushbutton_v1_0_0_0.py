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
            'PortLED': {'Parameters': ['Input'], 'Status': {}},
            'PortLEDAll': {'Status': {}},
            'SwitchPressStatus': {'Parameters': ['Input'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{=([1-8])(100|011|000)1}'), self.__MatchPortLED, None)
            self.AddMatchString(re.compile(b'{=a([0-9a-fA-F]{2})([0-9a-fA-F]{2})[0-9a-fA-F]{2}ff}'), self.__MatchPortStatus, None)
            self.AddMatchString(re.compile(b'{=s([0-9a-fA-F]{2})}'), self.__MatchSwitchPressStatus, None)

    def SetManagedMode(self):
        self.Send('{=axxxxxxff}')

    def SetPortLED(self, value, qualifier):

        ValueStateValues = {
            'Red': '100',
            'Green': '011',
            'Off': '000'
        }

        inputPort = qualifier['Input']
        if 1 <= int(inputPort) <= 8:
            PortLEDCmdString = '{' + '={0}{1}'.format(inputPort, ValueStateValues[value]) + '1}'
            self.__SetHelper('PortLED', PortLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPortLED')

    def __MatchPortLED(self, match, tag):

        ValueStateValues = {
            '100': 'Red',
            '011': 'Green',
            '000': 'Off'
        }

        qualifier = {'Input': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PortLED', value, qualifier)

    def SetPortLEDAll(self, value, qualifier):

        ValueStateValues = {
            'Red': '{=aff0000ff}{=aff0000ff}',
            'Green': '{=a00ffffff}{=a00ffffff}',
            'Off': '{=a000000ff}'
        }

        PortLEDAllCmdString = ValueStateValues[value]
        self.__SetHelper('PortLEDAll', PortLEDAllCmdString, value, qualifier)

    def UpdatePortLED(self, value, qualifier):
        PortStatusCmdString = '{?a}'
        self.__UpdateHelper('PortLED', PortStatusCmdString, value, qualifier)

    def __MatchPortStatus(self, match, tag):

        redLEDBinary = bin(int(match.group(1), 16))[2:].zfill(8)[::-1]
        greenLEDBinary = bin(int(match.group(2), 16))[2:].zfill(8)[::-1]

        for i in range(8):
            qualifier = {'Input': str(i + 1)}
            if redLEDBinary[i] == '1' and greenLEDBinary[i] == '0':
                value = 'Red'
            elif redLEDBinary[i] == '0' and greenLEDBinary[i] == '1':
                value = 'Green'
            else:
                value = 'Off'
            self.WriteStatus('PortLED', value, qualifier)

    def UpdateSwitchPressStatus(self, value, qualifier):
        SwitchPressStatusCmdString = '{?s}'
        self.__UpdateHelper('SwitchPressStatus', SwitchPressStatusCmdString, value, qualifier)

    def __MatchSwitchPressStatus(self, match, tag):

        hexResponse = match.group(1).decode()
        binaryValue = bin(int(hexResponse, 16))[2:].zfill(8)[::-1]
        for i in range(8):
            if binaryValue[i] == '1':
                value = 'Released'
            else:
                value = 'Pressed'
            qualifier = {'Input': str(i + 1)}
            self.WriteStatus('SwitchPressStatus', value, qualifier)

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
        self.SetManagedMode()

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
