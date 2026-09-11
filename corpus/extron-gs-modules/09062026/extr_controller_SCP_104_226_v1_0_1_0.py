from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
            'SCP 104': self.extr_20_235_104,
            'SCP 226': self.extr_20_235_226,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DisplayPower': {'Parameters': ['Button'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'FrontPanelLED': {'Parameters': ['LED'], 'Status': {}},
            'Input': {'Parameters': ['Button'], 'Status': {}},
            'RoomSelect': {'Parameters': ['Button'], 'Status': {}},
            'Volume': {'Status': {}},
            'VolumeLED': {'Parameters': ['LED'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Lmp(1|2|3|4|5|6|7|8|9|10|11)\*([0-9])\r'), self.__MatchFrontPanelLED, None)
            self.AddMatchString(re.compile(b'(\d+\.\d+)\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'(SwPrs|SwRls)\*(\d{1,2})\r'), self.__MatchRoomSelect, None)
            self.AddMatchString(re.compile(b'Vol(Dn|Up)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Vlmp([0-5])\*([0-4])\r'), self.__MatchVolumeLED, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)

    def UpdateFirmwareVersion(self, value, qualifier):
        self.__UpdateHelper('FirmwareVersion', 'q', value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetFrontPanelLED(self, value, qualifier):

        FrontPanelLEDValues = {
            'Off': '0',
            'Green': '1',
            'Red': '2',
            'Amber': '3',
            'Slowly Blinking Green': '4',
            'Slowly Blinking Red': '5',
            'Slowly Blinking Amber': '6',
            'Fast Blinking Green': '7',
            'Fast Blinking Red': '8',
            'Fast Blinking Amber': '9',
        }

        LED = qualifier['LED']
        LedStatusCmdString = '{0}*{1}*51#'.format(FrontPanelLEDValues[value], self.LEDnames[LED])
        self.__SetHelper('FrontPanelLED', LedStatusCmdString, value, qualifier)

    def UpdateFrontPanelLED(self, value, qualifier):

        LED = qualifier['LED']
        LedStatusCmdString = '{0}*51#'.format(self.LEDnames[LED])
        self.__UpdateHelper('FrontPanelLED', LedStatusCmdString, value, qualifier)

    def __MatchFrontPanelLED(self, match, tag):

        LedStatusNames = {
            '0': 'Off',
            '1': 'Green',
            '2': 'Red',
            '3': 'Amber',
            '4': 'Slowly Blinking Green',
            '5': 'Slowly Blinking Red',
            '6': 'Slowly Blinking Amber',
            '7': 'Fast Blinking Green',
            '8': 'Fast Blinking Red',
            '9': 'Fast Blinking Amber',
        }

        self.WriteStatus('FrontPanelLED', LedStatusNames[str(int(match.group(2).decode()))], {'LED': self.LEDNumbers[str(int(match.group(1).decode()))]})

    def __MatchRoomSelect(self, match, tag):

        SwitchStates = {
            'SwPrs': 'Press',
            'SwRls': 'Release'
        }

        Routing = int(match.group(2).decode())

        if 1 <= Routing <= 14:
            qualifier = {'Button': self.SwitchValues[match.group(2).decode()]}
            if 5 <= Routing <= 7:
                self.WriteStatus('RoomSelect', SwitchStates[match.group(1).decode()], qualifier)
            elif 1 <= Routing <= 2:
                self.WriteStatus('DisplayPower', SwitchStates[match.group(1).decode()], qualifier)
            elif 9 <= Routing <= 14:
                self.WriteStatus('Input', SwitchStates[match.group(1).decode()], qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1).decode()
        if value == 'Up':
            self.WriteStatus('Volume', 'Volume Up', None)
        elif value == 'Dn':
            self.WriteStatus('Volume', 'Volume Down', None)

    def SetVolumeLED(self, value, qualifier):

        LedStates = {
            'Off': 0,
            'Bottom': 1,
            'Blink On': 2,
            'Chase Up': 3,
            'Chase Down': 4,

        }

        LED = {
            'No LED': 0,
            'Bottom LED': 1,
            'LED 2': 2,
            'LED 3': 3,
            'LED 4': 4,
            'LED 5': 5,
        }

        LEDNum = qualifier['LED']

        LedStatusCmdString = '{0}*{1}*52#'.format(LedStates[value], LED[LEDNum])
        self.__SetHelper('VolumeLED', LedStatusCmdString, value, qualifier)

    def UpdateVolumeLED(self, value, qualifier):

        LEDnames = {
            'No LED': 0,
            'Bottom LED': 1,
            'LED 2': 2,
            'LED 3': 3,
            'LED 4': 4,
            'LED 5': 5,
        }
        LED = qualifier['LED']
        LedStatusCmdString = '{0}*52#'.format(LEDnames[LED])
        self.__UpdateHelper('VolumeLED', LedStatusCmdString, value, qualifier)

    def __MatchVolumeLED(self, match, tag):

        LedStates = {
            '0': 'Off',
            '1': 'Bottom',
            '2': 'Blink On',
            '3': 'Chase Up',
            '4': 'Chase Down',
        }

        LED = {
            '0': 'No LED',
            '1': 'Bottom LED',
            '2': 'LED 2',
            '3': 'LED 3',
            '4': 'LED 4',
            '5': 'LED 5',
        }

        self.WriteStatus('VolumeLED', LedStates[match.group(2).decode()], {'LED': LED[match.group(1).decode()]})

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

    def __MatchErrors(self, match, qualifier):
        self.counter = 0
        DEVICE_ERROR_CODES = {
            '10': 'Invalid command',
            '13': 'Invalid parameter',
            '23': 'Bad Checksum',
            '28': 'Bad filename or file not found',
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def extr_20_235_226(self):

        self.SwitchValues = {
            '1': 'Display Power On',
            '2': 'Display Power Off',
            '5': 'Room/Function Button 1',
            '6': 'Room/Function Button 2',
            '7': 'Room/Function Button 3',
            '9': 'Input 1',
            '10': 'Input 2',
            '11': 'Input 3',
            '12': 'Input 4',
            '13': 'Input 5',
            '14': 'Input 6',
        }

        self.LEDnames = {
            'Display Power On': '1',
            'Display Power Off': '2',
            'Room/Function Button 1': '3',
            'Room/Function Button 2': '4',
            'Room/Function Button 3': '5',
            'Input 1': '6',
            'Input 2': '7',
            'Input 3': '8',
            'Input 4': '9',
            'Input 5': '10',
            'Input 6': '11',
        }

        self.LEDNumbers = {
            '1': 'Display Power On',
            '2': 'Display Power Off',
            '3': 'Room/Function Button 1',
            '4': 'Room/Function Button 2',
            '5': 'Room/Function Button 3',
            '6': 'Input 1',
            '7': 'Input 2',
            '8': 'Input 3',
            '9': 'Input 4',
            '10': 'Input 5',
            '11': 'Input 6',
        }

    def extr_20_235_104(self):

        self.SwitchValues = {
            '1': 'Display Power On',
            '2': 'Display Power Off',
            '9': 'Input 1',
            '10': 'Input 2',
            '11': 'Input 3',
            '12': 'Input 4',
        }

        self.LEDnames = {
            'Display Power On': '1',
            'Display Power Off': '2',
            'Input 1': '6',
            'Input 2': '7',
            'Input 3': '8',
            'Input 4': '9',
        }

        self.LEDNumbers = {
            '1': 'Display Power On',
            '2': 'Display Power Off',
            '6': 'Input 1',
            '7': 'Input 2',
            '8': 'Input 3',
            '9': 'Input 4',
        }

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
