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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Freeze': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2}) OK(06|0B)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2}) OK0([01])x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2}) OK0([01])x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'x ([0-9A-F]{2}) OK0([01])x'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2}) OK(60|90|91|95|C0)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l ([0-9A-F]{2}) OK0([01])x'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2}) OK0([01])x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2}) OK(01|00)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2}) OK([0-9A-F]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([abcdeflmx]) ([0-9A-F]{2}) NG(.*)x'), self.__MatchError, None)

    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 99:
            return '{0:02X}'.format(int(ID))
        else:
            self.Error(['Invalid Device ID provided'])
            return None

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Original': '06',
            'Full Wide': '0B',
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kc {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kc {0} FF\r'.format(ID)
            self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        States = {
            '06': 'Original',
            '0B': 'Full Wide',
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode().upper()]
            self.WriteStatus('AspectRatio', value, {'Device ID': str(ID)})

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'ke {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('AudioMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'ke {0} FF\r'.format(ID)
            self.__UpdateHelper('AudioMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        States = {
            '0': 'On',
            '1': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, {'Device ID': str(ID)})

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'ju {0} 01\r'.format(ID)
            self.__SetHelper('AutoImage', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'km {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'km {0} FF\r'.format(ID)
            self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, {'Device ID': str(ID)})

    def SetFreeze(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kx {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('Freeze', CmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kx {0} FF\r'.format(ID)
            self.__UpdateHelper('Freeze', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('Freeze', value, {'Device ID': str(ID)})

    def SetInput(self, value, qualifier):

        States = {
            'RGB': '60',
            'HDMI 1': '90',
            'HDMI 2': '91',
            'OPS/DVI-D': '95',
            'DisplayPort': 'C0'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'xb {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            self.__UpdateHelper('Input', 'xb {0} FF\r'.format(ID), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        States = {
            '60': 'RGB',
            '90': 'HDMI 1',
            '91': 'HDMI 2',
            '95': 'OPS/DVI-D',
            'C0': 'DisplayPort'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('Input', value, {'Device ID': str(ID)})

    def SetKeypad(self, value, qualifier):

        States = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'mc {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('Keypad', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'mc {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('MenuNavigation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kl {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kl {0} FF\r'.format(ID)
            self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOnScreenDisplay')

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('OnScreenDisplay', value, {'Device ID': str(ID)})

    def SetPower(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'ka {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'ka {0} FF\r'.format(ID)
            self.__UpdateHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        value = States[match.group(2).decode()]
        if 1 <= ID <= 99:
            self.WriteStatus('Power', value, {'Device ID': str(ID)})

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00',
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kd {0} {1}\r'.format(ID, States[value])
            self.__SetHelper('VideoMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kd {0} FF\r'.format(ID)
            self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off',
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 99:
            value = States[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, {'Device ID': str(ID)})

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(ID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            CmdString = 'kf {0} FF\r'.format(ID)
            self.__UpdateHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):
        ID = int(match.group(1).decode(), 16)
        value = int(match.group(2).decode(), 16)
        if 1 <= ID <= 99:
            self.WriteStatus('Volume', value, {'Device ID': str(ID)})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Reject = False
        if 'Device ID' in qualifier and qualifier['Device ID'] == 'Broadcast':
            Reject = True

        if self.Unidirectional == 'True' or Reject:
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

        CommandStates = {
            'c': 'Aspect Ratio',
            'e': 'Audio Mute/ Keypad/ Menu Navigation',
            'u': 'Auto Image',
            'm': 'Executive Mode',
            'b': 'Input',
            'l': 'On Screen Display',
            'a': 'Power',
            'd': 'Video Mute',
            'f': 'Volume',
            'x': 'Freeze'
        }

        command = CommandStates[match.group(1).decode()]
        device_id = int(match.group(2).decode().upper(), 16)
        data = match.group(3).decode()
        value = '{0} Error occurred, Device ID:{1}, State:{2}'.format(command, device_id, data)
        self.Error([value])

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
