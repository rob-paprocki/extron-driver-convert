from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog


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
            'Chapter': {'Parameters': ['Title'], 'Status': {}},
            'DiscType': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Lock Type'], 'Status': {}},
            'Function': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NTSCandPAL': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PlayerStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Track': {'Status': {}},
            'Transport': {'Status': {}},
            'Zoom': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\[(PR|PS),(SOC|GetC),0,([0-9]{1,2}),([0-9]{1,3})\]'), self.__MatchChapter, None)
            self.AddMatchString(compile(b'\[PS,GetDiscType,0,([0-7])\]'), self.__MatchDiscType, None)
            self.AddMatchString(compile(b'\[PS,GetT,0,([0-9]{1,2})\]'), self.__MatchTrack, None)
            self.AddMatchString(compile(b'\[(PR|PS),(StatusChange|GetStatus),0,([0-5])\]'), self.__MatchPlayerStatus, None)
            self.AddMatchString(compile(b'\[(PR|PS|PC),([a-zA-Z]{1,12}),(1|2|5|10)(?:,[0-9]{1,3}){0,2}\]'), self.__MatchError, None)

    def SetChapter(self, value, qualifier):

        Title = qualifier['Title']

        if 1 <= value <= 99 and 1 <= Title <= 99:
            CmdString = '[PC,PlayC,{0},{1}]\r'.format(Title, value)
            self.__SetHelper('Chapter', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetChapter')

    def UpdateChapter(self, value, qualifier):
        self.__UpdateHelper('Chapter', '[PS,GetC]\r', value, qualifier)

    def __MatchChapter(self, match, tag):
        self.WriteStatus('Chapter', int(match.group(4).decode()), {'Title': int(match.group(3).decode())})

    def UpdateDiscType(self, value, qualifier):
        self.__UpdateHelper('DiscType', '[PS,GetDiscType]\r', value, qualifier)

    def __MatchDiscType(self, match, tag):

        States = {
            '0': 'No Disc',
            '1': 'DVD',
            '2': 'VCD/SVCD',
            '3': 'CD-DA',
            '4': 'MP3 (CD-R/RW)',
            '5': 'WMA',
            '6': 'DivX',
            '7': 'JPEG',
        }

        self.WriteStatus('DiscType', States[match.group(1).decode()], None)

    def SetExecutiveMode(self, value, qualifier):

        LockTypeStates = {
            'Front Panel': 'LKC',
            'IR Remote': 'RCC'
        }

        States = {
            'On': 'ON',
            'Off': 'OFF'
        }

        LockType = LockTypeStates[qualifier['Lock Type']]

        CmdString = '[PC,{0},{1}]\r'.format(LockType, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)
       
    def SetFunction(self, value, qualifier):

        States = {
            'Clear': '[PC,RC,181]\r',
            'Subtitle': '[PC,RC,75]\r',
            'Call': '[PC,RC,182]\r',
            'Audio': '[PC,RC,78]\r',
            'Setup': '[PC,RC,130]\r',
            'Angle': '[PC,RC,133]\r',
            'Slide Show': '[PC,RC,184]\r',
            'Display': '[PC,RC,200]\r',
        }

        self.__SetHelper('Function', States[value], value, qualifier)

    def SetKeypad(self, value, qualifier):

        States = {
            '1': '[PC,RC,1]\r',
            '2': '[PC,RC,2]\r',
            '3': '[PC,RC,3]\r',
            '4': '[PC,RC,4]\r',
            '5': '[PC,RC,5]\r',
            '6': '[PC,RC,6]\r',
            '7': '[PC,RC,7]\r',
            '8': '[PC,RC,8]\r',
            '9': '[PC,RC,9]\r',
            '+10': '[PC,RC,180]\r',
            '0': '[PC,RC,0]\r'
        }

        self.__SetHelper('Keypad', States[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': '[PC,RC,113]\r',
            'Top Menu/PBC': '[PC,RC,84]\r',
            'Up': '[PC,RC,88]\r',
            'Down': '[PC,RC,89]\r',
            'Left': '[PC,RC,90]\r',
            'Right': '[PC,RC,91]\r',
            'Enter': '[PC,RC,92]\r',
            'Return': '[PC,RC,131]\r'
        }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def SetNTSCandPAL(self, value, qualifier):

        self.__SetHelper('NTSCandPAL', '[PC,RC,183]\r', value, qualifier)

    def SetPower(self, value, qualifier):

        self.__SetHelper('Power', '[PC,RC,12]\r', value, qualifier)

    def SetTransport(self, value, qualifier):

        States = {
            'Play': '[PC,RC,44]\r',
            'Pause': '[PC,RC,48]\r',
            'Stop': '[PC,RC,49]\r',
            'A-B Repeat': '[PC,RC,59]\r',
            'Random': '[PC,RC,28]\r',
            'Repeat': '[PC,RC,29]\r',
            'Open/Close': '[PC,RC,66]\r',
            'Slow/Search+': '[PC,RC,40]\r',
            'Slow/Search-': '[PC,RC,41]\r'
        }

        self.__SetHelper('Transport', States[value], value, qualifier)

    def SetZoom(self, value, qualifier):

        self.__SetHelper('Zoom', '[PC,RC,247]\r', value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': '[PC,OSD,ON]\r',
            'Off': '[PC,OSD,OFF]\r'
        }

        self.__SetHelper('OnScreenDisplay', States[value], value, qualifier)

    def UpdatePlayerStatus(self, value, qualifier):

        self.__UpdateHelper('PlayerStatus', '[PS,GetStatus]\r', value, qualifier)

    def __MatchPlayerStatus(self, match, tag):

        States = {
            '0': 'Disc Error',
            '1': 'Opened',
            '2': 'No Disc',
            '3': 'Stopped',
            '4': 'Playing',
            '5': 'Paused'
        }

        self.WriteStatus('PlayerStatus', States[match.group(3).decode()], None)

    def SetTrack(self, value, qualifier):

        if 0 <= value <= 99:
            CmdString = '[PC,PlayT,{0}]\r'.format(value)
            self.__SetHelper('Track', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTrack')

    def UpdateTrack(self, value, qualifier):
        self.__UpdateHelper('Track', '[PS,GetT]\r', value, qualifier)

    def __MatchTrack(self, match, tag):
        self.WriteStatus('Track', int(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)           

    def __MatchError(self, match, tag):

        DeviceErrorStateValues = {
            1: 'Cause of error not known',
            2: 'Invalid parameter',
            5: 'Command not valid',
            10: 'Command not valid for Current disc'
        }

        CmdName = match.group(2).decode()
        Error = int(match.group(3).decode())
        print(CmdName + ':' + DeviceErrorStateValues[Error])

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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
