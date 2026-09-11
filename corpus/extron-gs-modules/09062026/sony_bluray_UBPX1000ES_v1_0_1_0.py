from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DiscTrayControl': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Transport': {'Status': {}},
        }

    def SetDiscTrayControl(self, value, qualifier):

        ValueStateValues = {
            'Open': b'\x01',
            'Close': b'\x00',
            'Eject': b'\x02'
        }

        DiscTrayControlCmdString = b'\x02\x03\x80\x50' + ValueStateValues[value] + b'\x00'
        self.__SetHelper('DiscTrayControl', DiscTrayControlCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x1B',
            'Up': b'\x15',
            'Down': b'\x19',
            'Right': b'\x18',
            'Left': b'\x16',
            'Enter': b'\x17',
            'Return': b'\x1C',
            'Top Menu': b'\x1A',
            'Home': b'\x30',
            'Audio': b'\x0D',
            'Favorite': b'\x3C',
            'Display': b'\x23',
            'Option': b'\x31',
            'Subtitle': b'\x0E',
            'Net Service': b'\x2B',
            'Bluetooth': b'\x2C',
            'NetFlix': b'\x3D',
            'USB': b'\x3E',
            'DISC': b'\x3F'
        }

        MenuNavigationCmdString = b'\x02\x02\x80' + ValueStateValues[value] + b'\x00'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b'\x02\x03\x80\x60' + ValueStateValues[value] + b'\x00'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': b'\x12',
            'Pause': b'\x13',
            'Stop': b'\x14',
            'Open/Close': b'\x39',
            'Rewind': b'\x20',
            'Fast Forward': b'\x21',
            'Next': b'\x11',
            'Previous': b'\x10'
        }

        TransportCmdString = b'\x02\x02\x80' + ValueStateValues[value] + b'\x00'
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class DeviceEthernetClass:
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
            'MenuNavigation': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Transport': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\"playback\.status\",\"value\":\"(Playing|Stopped|Paused|FF|FR|video playback|photo playback|TrayOpen|NoMedia)\"}'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(re.compile(b'\"main\.power\",\"value\":\"(on|off)\"}'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\"(ERR|NAK)\"'), self.__MatchError, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'popupmenu',
            'Up': 'up',
            'Down': 'down',
            'Right': 'right',
            'Left': 'left',
            'Enter': 'enter',
            'Return': 'return',
            'Top Menu': 'topmenu',
            'Home': 'home',
            'Audio': 'audio',
            'Favorite': 'favorite',
            'Display': 'display',
            'Option': 'optionmenu',
            'Subtitle': 'subtitle',
            'Net Service': 'netservice',
            'Bluetooth': 'bluetooth',
            'NetFlix': 'netflix',
            'USB': 'usb',
            'DISC': 'disc'
        }

        MenuNavigationCmdString = '{"type":"set","feature":"gui.' + ValueStateValues[value] + '","value":"pulse"}'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdatePlaybackStatus(self, value, qualifier):

        PlaybackStatusCmdString = '{"type":"get","feature":"playback.status"}'
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):

        ValueStateValues = {
            'Playing': 'Playing',
            'Stopped': 'Stopped',
            'Paused': 'Paused',
            'FF': 'Fast Forward',
            'FR': 'Rewind',
            'video playback': 'Video Playback',
            'photo playback': 'Photo Playback',
            'TrayOpen': 'Tray Open',
            'NoMedia': 'No Media'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PlaybackStatus', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PowerCmdString = '{"type":"set","feature":"main.power","value":"' + ValueStateValues[value] + '"}'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '{"type":"get","feature":"main.power"}'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'play',
            'Pause': 'pause',
            'Stop': 'stop',
            'Open/Close': 'ejectdisc',
            'Rewind': 'fr',
            'Fast Forward': 'ff',
            'Next': 'next',
            'Previous': 'previous'
        }

        TransportCmdString = '{"type":"set","feature":"gui.' + ValueStateValues[value] + '","value":"pulse"}'
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

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

        DeviceErrorCodes = {
            'ERR': 'Setting cannot be performed in current AVR configuration.',
            'NAK': 'Syntax error in received packet.'
        }
        if match.group(1).decode() in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode()]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(1).decode()])

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
