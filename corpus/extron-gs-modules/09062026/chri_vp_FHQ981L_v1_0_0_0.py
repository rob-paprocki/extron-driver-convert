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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'InputResolution': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiWindowMode': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'WindowInput': {'Parameters': ['Window'], 'Status': {}},
            'WindowMode': {'Status': {}}
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ALL:SRC=(00[01234567])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ALL:IRT=(00[012345])'), self.__MatchInputResolution, None)
            self.AddMatchString(re.compile(b'ALL:MUT=(00[01])'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'ALL:WMT=(00[012])'), self.__MatchMultiWindowMode, None)
            self.AddMatchString(re.compile(b'ALL:PMT=(00[012])'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'ALL:VOL=([0-9]{3})'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ALL:W([1-4])S=00([0-6])'), self.__MatchWindowInput, None)
            self.AddMatchString(re.compile(b'ALL:WIN=00([1-4])'), self.__MatchWindowMode, None)
            self.AddMatchString(re.compile(b'ALL:(SRC|IRT|MUT|WMT|PMT|VOL)=N'), self.__MatchError, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'K:ALLRAT.'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': 'SPC',
            'DP': 'SH1',
            'HDMI 1': 'SH2',
            'HDMI 2': 'SH3',
            'HDMI 3': 'SH4',
            'HDMI 4': 'SH5',
            'OPS-HDMI': 'SH6',
            'OPS-DP': 'SH7'
        }

        InputCmdString = 'K:ALL{0}.'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'K:ALLSRC?'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '000': 'VGA',
            '001': 'DP',
            '002': 'HDMI 1',
            '003': 'HDMI 2',
            '004': 'HDMI 3',
            '005': 'HDMI 4',
            '006': 'OPS-HDMI',
            '007': 'OPS-DP'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetInputResolution(self, value, qualifier):

        InputResolutionState = {
            '1024x768': 'IR0',
            '1280x768': 'IR1',
            '1360x768': 'IR2',
            '1366x768': 'IR3',
            '1400x1050': 'IR4',
            '1680x1050': 'IR5'
        }

        InputResolutionCmdString = 'K:ALL{0}.'.format(InputResolutionState[value])
        self.__SetHelper('InputResolution', InputResolutionCmdString, value, qualifier)

    def UpdateInputResolution(self, value, qualifier):

        InputResolutionCmdString = 'K:ALLIRT?'
        self.__UpdateHelper('InputResolution', InputResolutionCmdString, value, qualifier)

    def __MatchInputResolution(self, match, tag):

        InputResolutionState = {
            '000': '1024x768',
            '001': '1280x768',
            '002': '1360x768',
            '003': '1366x768',
            '004': '1400x1050',
            '005': '1680x1050'
        }

        value = InputResolutionState[match.group(1).decode()]
        self.WriteStatus('InputResolution', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'RUP',
            'Down': 'RDN',
            'Left': 'RLT',
            'Right': 'RRT',
            'Select': 'REN',
            'Menu': 'RMN'
        }

        MenuNavigationCmdString = 'K:ALL{0}.'.format(MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMultiWindowMode(self, value, qualifier):

        MultiWindowModeState = {
            'Off': 'WM0',
            'PBP': 'WM1',
            'Quadrant': 'WM2'
        }

        MultiWindowModeCmdString = 'K:ALL{0}.'.format(MultiWindowModeState[value])
        self.__SetHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)

    def UpdateMultiWindowMode(self, value, qualifier):

        MultiWindowModeCmdString = 'K:ALLWMT?'
        self.__UpdateHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)

    def __MatchMultiWindowMode(self, match, tag):

        MultiWindowModeState = {
            '000': 'Off',
            '001': 'PBP',
            '002': 'Quadrant'
        }

        value = MultiWindowModeState[match.group(1).decode()]
        self.WriteStatus('MultiWindowMode', value, None)

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': 'MON',
            'Off': 'MOF'
        }

        MuteCmdString = 'K:ALL{0}.'.format(MuteState[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'K:ALLMUT?'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        MuteState = {
            '001': 'On',
            '000': 'Off'
        }

        value = MuteState[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPictureMode(self, value, qualifier):

        PictureModeState = {
            'Standard': 'PMO',
            'Dynamic': 'PM1',
            'User': 'PM2'
        }

        PictureModeCmdString = 'K:ALL{0}.'.format(PictureModeState[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'K:ALLPMT?'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        PictureModeState = {
            '000': 'Standard',
            '001': 'Dynamic',
            '002': 'User'
        }

        value = PictureModeState[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = 'K:ALL{0}.'.format(PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            VolumeCmdString = 'K:ALLVOL{0:03d}.'.format(int(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'K:ALLVOL?'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetWindowInput(self, value, qualifier):

        window = qualifier['Window']

        ValueStateValues = {
            'DP': '0',
            'HDMI 1' 	: '1',
            'HDMI 2': '2',
            'HDMI 3': '3',
            'HDMI 4': '4',
            'OPS-HDMI': '5',
            'OPS-DP': '6'
        }

        if 1 <= int(window) <= 4:
            WindowInputCmdString = 'K:ALLW{0}{1}.'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowInput', WindowInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWindowInput')

    def UpdateWindowInput(self, value, qualifier):

        window = qualifier['Window']

        if 1 <= int(window) <= 4:
            WindowInputCmdString = 'K:ALLW{0}S?'.format(window)
            self.__UpdateHelper('WindowInput', WindowInputCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateWindowInput')

    def __MatchWindowInput(self, match, tag):

        WindowStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '0': 'DP',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4',
            '5': 'OPS-HDMI',
            '6': 'OPS-DP'
        }

        qualifier = {}
        qualifier['Window'] = WindowStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('WindowInput', value, qualifier)

    def SetWindowMode(self, value, qualifier):

        ValueStateValues = {
            'Window 1': 'WN1',
            'Window 2': 'WN2',
            'Window 3': 'WN3',
            'Window 4': 'WN4'
        }

        WindowModeCmdString = 'K:ALL{0}.'.format(ValueStateValues[value])
        self.__SetHelper('WindowMode', WindowModeCmdString, value, qualifier)

    def UpdateWindowMode(self, value, qualifier):

        WindowModeCmdString = 'K:ALLWIN?'
        self.__UpdateHelper('WindowMode', WindowModeCmdString, value, qualifier)

    def __MatchWindowMode(self, match, tag):

        ValueStateValues = {
            '1': 'Window 1',
            '2': 'Window 2',
            '3': 'Window 3',
            '4': 'Window 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WindowMode', value, None)

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

        ErrorState = {
            'SRC': 'Input',
            'IRT': 'Input Resolution',
            'MUT': 'Mute',
            'WMT': 'Multi Window Mode',
            'PMT': 'Picture Mode',
            'VOL': 'Volume',
            'W1S': 'Window 1 Input',
            'W2S': 'Window 2 Input',
            'W3S': 'Window 3 Input',
            'W4S': 'Window 4 Input',
            'WIN': 'Window Mode'
        }

        value = 'Error: {0}'.format(ErrorState[match.group(1).decode()])
        print(value)

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
                result = re.search(regexString, self._ReceiveBuffer)
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
