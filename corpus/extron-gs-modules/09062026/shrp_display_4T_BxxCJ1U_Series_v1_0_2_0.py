from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Authenticated = 'Not Needed'
        self.AuthenticatedError = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ATVChannelDirectCommand': {'Status': {}},
            'AVMode': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DTVChannelAirCommand': {'Status': {}},
            'DTVChannelCable1Command': {'Status': {}},
            'DTVChannelCable2Command': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Unknown'
            self.AddMatchString(re.compile(b'Username:'), self.__MatchUsernamePrompt, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPasswordPrompt, None)
            self.AddMatchString(re.compile(b'ERR\r'), self.__MatchWrongUsernamePasswordPrompt, None)

    def __MatchUsernamePrompt(self, match, tag):
        self.Authenticated = 'Needed'
        self.AuthenticatedError = False
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r')
            @Wait(3)
            def CheckUsername():
                if self.AuthenticatedError:
                    self.Error(['Login Failed. Please supply proper Username/Password'])
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPasswordPrompt(self, match, tag):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r')
            @Wait(3)
            def CheckPassword():
                if not self.AuthenticatedError and self.Authenticated == 'Needed':
                    self.Authenticated = 'Authenticated'
                else:
                    self.Error(['Login Failed. Please supply proper Username/Password'])
        else:
            self.MissingCredentialsLog('Password')

    def __MatchWrongUsernamePasswordPrompt(self, match, tag):
        self.AuthenticatedError = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '1',
            'Zoom 14:9': '2',
            'Panorama': '3',
            'Full': '4',
            'Cinema 16:9': '5',
            'Cinema 14:9': '6',
            'Dot by Dot': '10',
            'Overscan': '14'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'WIDE{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            1: 'Normal',
            2: 'Zoom 14:9',
            3: 'Panorama',
            4: 'Full',
            5: 'Cinema 16:9',
            6: 'Cinema 14:9',
            10: 'Dot by Dot',
            14: 'Overscan'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetATVChannelDirectCommand(self, value, qualifier):

        temp = value
        if temp and 1 <= int(temp) <= 135:
            ATVChannelDirectCommandCmdString = 'DCCH{:<4}\r'.format(temp)
            self.__SetHelper('ATVChannelDirectCommand', ATVChannelDirectCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATVChannelDirectCommand')

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '1',
            'Movie': '2',
            'User': '4',
            'Dynamic': '5',
            'Dynamic (Fixed)': '6'
        }

        if value in ValueStateValues:
            AVModeCmdString = 'AVMD{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMode')

    def UpdateAVMode(self, value, qualifier):

        ValueStateValues = {
            1: 'Standard',
            2: 'Movie',
            4: 'User',
            5: 'Dynamic',
            6: 'Dynamic (Fixed)'
        }

        AVModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['AV Mode: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DW'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = 'CH{}    \r'.format(ValueStateValues[value])
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDTVChannelAirCommand(self, value, qualifier):

        temp = value
        if temp and 100 <= int(temp) <= 9999:
            DTVChannelAirCommandCmdString = 'DA2P{}\r'.format(temp.zfill(4))
            self.__SetHelper('DTVChannelAirCommand', DTVChannelAirCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelAirCommand')

    def SetDTVChannelCable1Command(self, value, qualifier):

        temp = value
        if temp:
            if temp.__contains__('.'):
                major, minor = temp.split('.')
            else:  # if major is the only value
                major = temp
                minor = '0'

            if 1 <= int(major) <= 999 and 0 <= int(minor) <= 999:
                DTVChannelCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(major))
                DTVChannelCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(minor))
                self.__SetHelper('DTVChannelCable1Command', DTVChannelCableMajorCommandCmdString, value, qualifier)
                self.__SetHelper('DTVChannelCable1Command', DTVChannelCableMinorCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTVChannelCable1Command')
        else:
            self.Discard('Invalid Command for SetDTVChannelCable1Command')

    def SetDTVChannelCable2Command(self, value, qualifier):

        temp = value
        if temp and (0 <= int(temp) <= 6383 or 10000 <= int(temp) <= 19999):
            DTVChannelCable2CommandCmdString = 'DC1{0:05d}\r'.format(int(temp))
            self.__SetHelper('DTVChannelCable2Command', DTVChannelCable2CommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelCable2Command')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'Video': '3',
            'USB': '4',
            'Home Network': '5'
        }

        if value in ValueStateValues:
            InputCmdString = 'IAVD{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0: 'TV',
            1: 'HDMI 1',
            2: 'HDMI 2',
            3: 'Video',
            4: 'USB',
            5: 'Home Network'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'Dot': '10'
        }

        if value in ValueStateValues:
            KeypadCmdString = 'RCKY{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '38',
            'Up': '41',
            'Down': '42',
            'Left': '43',
            'Right': '44',
            'Enter': '40',
            'Return': '45',
            'Exit': '46'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'RCKY{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2'
        }

        if value in ValueStateValues:
            MuteCmdString = 'MUTE{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerCmdString = 'POWR{:<4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'VOLM{:<4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            self.Error(['{}: Error occurred.'.format(sourceCmdName)])
            response = ''
        elif 'WAIT' in response:
            self.Error([sourceCmdName + ' : Waiting for a response.'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Authenticated in ['Not Needed', 'Authenticated']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Not Authenticated')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Not Needed', 'Authenticated']:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Unknown'
            self.AuthenticatedError = False

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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