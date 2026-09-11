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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AspectRatioSub': {'Parameters': ['Mode'], 'Status': {}},
            'Input': {'Parameters': ['Mode'], 'Status': {}},
            'MainSubScreenChange': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'f 0[0-a] OK0([0-4])x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'([ghi]) 0[0-a] OK0([01])x', re.I), self.__MatchAspectRatioSub, None)
            self.AddMatchString(re.compile(b'([bcde]) 0[0-a] OK(9[0-3]|C0|E0)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'm 0[0-a] OK0([01])x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'x 0[0-a] OK(0[012456789ABCDEF]|1[0-4])x', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'n 0[0-a] OK0([0-9])x', re.I), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'p 0[0-a] OK0([012])x', re.I), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'a 0[0-a] OK0([01])x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd 0[0-a] OK0([01])x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'([abcdefghimnpx]) 0[0-a] NG(.*)x', re.I), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 10:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            self.Error(['Device Id should be a value between 1 to 10 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Wide': '0',
            'Original': '1',
            '1:1': '2',
            'Cinema 1': '3',
            'Cinema 2': '4'
        }

        AspectRatioCmdString = 'xf {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'xf {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Full Wide',
            '1': 'Original',
            '2': '1:1',
            '3': 'Cinema 1',
            '4': 'Cinema 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAspectRatioSub(self, value, qualifier):

        ModeStates = {
            'Sub': 'g',
            'Sub 2': 'h',
            'Sub 3': 'i'
        }

        ValueStateValues = {
            'Full Wide': '0',
            'Original': '1'
        }

        AspectRatioSubCmdString = 'x{} {} 0{}\r'.format(ModeStates[qualifier['Mode']], self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatioSub', AspectRatioSubCmdString, value, qualifier)

    def UpdateAspectRatioSub(self, value, qualifier):

        ModeStates = {
            'Sub': 'g',
            'Sub 2': 'h',
            'Sub 3': 'i'
        }

        AspectRatioSubCmdString = 'x{} {} FF\r'.format(ModeStates[qualifier['Mode']], self._DeviceID)
        self.__UpdateHelper('AspectRatioSub', AspectRatioSubCmdString, value, qualifier)

    def __MatchAspectRatioSub(self, match, tag):

        ModeStates = {
            'g': 'Sub',
            'h': 'Sub 2',
            'i': 'Sub 3'
        }

        ValueStateValues = {
            '0': 'Full Wide',
            '1': 'Original'
        }

        qualifier = {'Mode': ModeStates[match.group(1).decode().lower()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatioSub', value, qualifier)

    def SetInput(self, value, qualifier):

        ModeStates = {
            'Main': 'b',
            'Sub': 'c',
            'Sub 2': 'd',
            'Sub 3': 'e'
        }

        ValueStateValues = {
            'HDMI 1': '90',
            'HDMI 2': '91',
            'HDMI 3': '92',
            'HDMI 4': '93',
            'DisplayPort': 'C0',
            'USB-C': 'E0'
        }

        InputCmdString = 'x{} {} {}\r'.format(ModeStates[qualifier['Mode']], self._DeviceID, ValueStateValues[value], 3)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ModeStates = {
            'Main': 'b',
            'Sub': 'c',
            'Sub 2': 'd',
            'Sub 3': 'e'
        }

        InputCmdString = 'x{} {} FF\r'.format(ModeStates[qualifier['Mode']], self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ModeStates = {
            'b': 'Main',
            'c': 'Sub',
            'd': 'Sub 2',
            'e': 'Sub 3'
        }

        ValueStateValues = {
            '90': 'HDMI 1',
            '91': 'HDMI 2',
            '92': 'HDMI 3',
            '93': 'HDMI 4',
            'C0': 'DisplayPort',
            'E0': 'USB-C'
        }

        qualifier = {'Mode': ModeStates[match.group(1).decode().lower()]}
        value = ValueStateValues[match.group(2).decode().upper()]
        self.WriteStatus('Input', value, qualifier)

    def SetMainSubScreenChange(self, value, qualifier):

        MainSubScreenChangeCmdString = 'ma {} 01\r'.format(self._DeviceID)
        self.__SetHelper('MainSubScreenChange', MainSubScreenChangeCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = 'km {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = 'km {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Custom': '00',
            'Mono': '01',
            'Reader': '02',
            'Photo': '04',
            'Cinema': '05',
            'sRGB': '06',
            'Color Weakness': '07',
            'Game': '08',
            'FPS Game 1': '09',
            'FPS Game 2': '0A',
            'RTS Game': '0B',
            'Custom Game': '0C',
            'EBU': '0D',
            'REC 709': '0E',
            'SMPTE C': '0F',
            'DICOM': '10',
            'Calibration 1': '11',
            'Calibration 2': '12',
            'Dark Room 1': '13',
            'Dark Room 2': '14'
        }

        PictureModeCmdString = 'dx {} {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'dx {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Custom',
            '01': 'Mono',
            '02': 'Reader',
            '04': 'Photo',
            '05': 'Cinema',
            '06': 'sRGB',
            '07': 'Color Weakness',
            '08': 'Game',
            '09': 'FPS Game 1',
            '0A': 'FPS Game 2',
            '0B': 'RTS Game',
            '0C': 'Custom Game',
            '0D': 'EBU',
            '0E': 'REC 709',
            '0F': 'SMPTE C',
            '10': 'DICOM',
            '11': 'Calibration 1',
            '12': 'Calibration 2',
            '13': 'Dark Room 1',
            '14': 'Dark Room 2'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'PBP': '1',
            'PBP 2': '2',
            'PIP Top Left': '3',
            'PIP Top Right': '4',
            'PIP Bottom Left': '5',
            'PIP Bottom Right': '6',
            'PBP 3': '7',
            'PBP Left 1 Right 2': '8',
            'PBP 4': '9'
        }

        PIPModeCmdString = 'kn {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = 'kn {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PBP',
            '2': 'PBP 2',
            '3': 'PIP Top Left',
            '4': 'PIP Top Right',
            '5': 'PIP Bottom Left',
            '6': 'PIP Bottom Right',
            '7': 'PBP 3',
            '8': 'PBP Left 1 Right 2',
            '9': 'PBP 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '0',
            'Medium': '1',
            'Large': '2'
        }

        PIPSizeCmdString = 'kp {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'kp {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = 'ka {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = 'kd {} 0{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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

        State = {
            'f': 'Aspect Ratio',
            'g': 'Aspect Ratio Sub',
            'h': 'Aspect Ratio Sub 2',
            'i': 'Aspect Ratio Sub 3',
            'b': 'Input Main',
            'c': 'Input Sub',
            'd': 'Input Sub 2 / Video Mute',
            'e': 'Input Sub 3',
            'm': 'On Screen Display',
            'x': 'Picture Mode',
            'n': 'PIP Mode',
            'p': 'PIP Size',
            'a': 'Power'
        }

        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1, temp2)
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
