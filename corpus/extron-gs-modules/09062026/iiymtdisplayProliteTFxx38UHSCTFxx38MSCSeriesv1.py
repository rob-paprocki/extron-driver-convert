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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ButtonControl': {'Status': {}},
            'Input': {'Status': {}},
            'IRControl': {'Status': {}},
            'IRControlandButtonControl': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'TouchMode': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x7700([01234])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6700([01])\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x7300([01])\r'), self.__MatchButtonControl, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6A00([01267])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6800([01])\r'), self.__MatchIRControl, None)
            self.AddMatchString(re.compile(b':[0-9]{2}r\x76([0-9]{5})\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\xB100([0123])\r'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6C00([01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x9E00([01])\r'), self.__MatchTouchMode, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x66([0-9]{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 1 <= int(value) <= 98:
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['Device ID should be a value between 1 to 98 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            '16:10': '1',
            '5:4': '2',
            '4:3': '3',
            'Real': '4'
        }

        AspectRatioCmdString = '8{}s\x3100{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '8{}g\x77000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': '16:10',
            '2': '5:4',
            '3': '4:3',
            '4': 'Real'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '8{}s\x3600{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '8{}g\x67000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '8{}s\x8F000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ButtonControlCmdString = '8{}s\x4500{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('ButtonControl', ButtonControlCmdString, value, qualifier)

    def UpdateButtonControl(self, value, qualifier):

        ButtonControlCmdString = '8{}g\x73000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('ButtonControl', ButtonControlCmdString, value, qualifier)

    def __MatchButtonControl(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonControl', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'DVI': '6',
            'DisplayPort': '7'
        }

        InputCmdString = '8{}s\x2200{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '8{}g\x6A000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '6': 'DVI',
            '7': 'DisplayPort'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetIRControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        IRControlCmdString = '8{}s\x4200{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)

    def UpdateIRControl(self, value, qualifier):

        IRControlCmdString = '8{}g\x68000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)

    def __MatchIRControl(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IRControl', value, None)

    def SetIRControlandButtonControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        IRControlandButtonControlCmdString = '8{}s\x4300{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('IRControlandButtonControl', IRControlandButtonControlCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '8{}g\x76000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Vivid': '1',
            'Cinema': '2',
            'Custom': '3'
        }

        PictureModeCmdString = '8{}s\x8100{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '8{}g\xB1000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Vivid',
            '2': 'Cinema',
            '3': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '8{}s\x2100{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '8{}g\x6C000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTouchMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        TouchModeCmdString = '8{}s\x9E00{}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('TouchMode', TouchModeCmdString, value, qualifier)

    def UpdateTouchMode(self, value, qualifier):

        TouchModeCmdString = '8{}g\x9E000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('TouchMode', TouchModeCmdString, value, qualifier)

    def __MatchTouchMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TouchMode', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '8{0}s\x35{1:03d}\r'.format(self._DeviceID, value).encode(encoding='iso-8859-1')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '8{}g\x66000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
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

        self.Error(['Error: Invalid command reply.'])

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
