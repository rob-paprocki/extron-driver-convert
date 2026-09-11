from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceSerialClass:
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
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LED': {'Status': {}},
            'Power': {'Status': {}},
            'Rotation': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@MNG;OIA;(NORMAL|FULL)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'@STG;FRZ;([01])'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'@STG;LSW;([01])'), self.__MatchLED, None)
            self.AddMatchString(re.compile(b'@STG;ROT;(0|90|180|270)'), self.__MatchRotation, None)
            self.AddMatchString(re.compile(b'ERR([1-5])'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (16:9)': 'NORMAL',
            'Full (4:3)': 'FULL'
        }

        AspectRatioCmdString = '\x02@MNS;OIA;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02@MNG;OIA\x03'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'NORMAL': 'Normal (16:9)',
            'FULL': 'Full (4:3)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '\x02@BTN;AFS\x03'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'FAR',
            'Near': 'NEAR',
            'Stop': 'STOP'
        }

        speed = qualifier['Speed']
        if speed == 'Auto' or 0 <= int(speed) <= 14:
            if value == 'Stop':
                FocusCmdString = '\x02@BTN;MFS;{}\x03'.format(ValueStateValues[value])
            else:
                FocusCmdString = '\x02@BTN;MFS;{0};{1}\x03'.format(ValueStateValues[value], speed.upper())
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = '\x02@BTN;FRZ;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '\x02@STG;FRZ\x03'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Camera': 'CAM',
            'HDMI 1': 'HDMI1',
            'HDMI 2': 'HDMI2',
            'RGB': 'RGB'
        }

        InputCmdString = '\x02@BTN;SIN;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLED(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        LEDCmdString = '\x02@BTN;LSW;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('LED', LEDCmdString, value, qualifier)

    def UpdateLED(self, value, qualifier):

        LEDCmdString = '\x02@STG;LSW\x03'
        self.__UpdateHelper('LED', LEDCmdString, value, qualifier)

    def __MatchLED(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LED', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        PowerCmdString = '\x02@BTN;PWR;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRotation(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '90': '90',
            '180': '180',
            '270': '270'
        }

        RotationCmdString = '\x02@BTN;ROT;{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Rotation', RotationCmdString, value, qualifier)

    def UpdateRotation(self, value, qualifier):

        RotationCmdString = '\x02@STG;ROT\x03'
        self.__UpdateHelper('Rotation', RotationCmdString, value, qualifier)

    def __MatchRotation(self, match, tag):

        ValueStateValues = {
            '0': '0',
            '90': '90',
            '180': '180',
            '270': '270'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Rotation', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Wide': 'WIDE',
            'Tele': 'TELE',
            'Stop': 'STOP'
        }

        speed = qualifier['Speed']
        if speed == 'Auto' or 0 <= int(speed) <= 7:
            if value == 'Stop':
                ZoomCmdString = '\x02@BTN;ZOM;{}\x03'.format(ValueStateValues[value])
            else:
                ZoomCmdString = '\x02@BTN;ZOM;{0};{1}\x03'.format(ValueStateValues[value], speed.upper())
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        DEVICE_ERROR_CODES = {
            '1': 'Command acceptance not possible',
            '2': 'Parameter error',
            '3': 'Device abnormality',
            '4': 'Undefined command',
            '5': 'Capacity shortage'
        }

        self.Error(['Error: ' + DEVICE_ERROR_CODES[match.group(1).decode()]])

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


class DeviceEthernetClass:
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
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LED': {'Status': {}},
            'Rotation': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{ "aspect ratio" : "(normal|full)" }'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'{ "freeze" : ([01]) }'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'{ "light switch" : ([01]) }'), self.__MatchLED, None)
            self.AddMatchString(re.compile(b'{ "rotation" : (0|90|180|270) }'), self.__MatchRotation, None)
            self.AddMatchString(re.compile(b'"error" ?: ?-([1-5])'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (16:9)': 'normal',
            'Full (4:3)': 'full'
        }

        AspectRatioCmdString = '{{ "aspect ratio" : "{}" }}'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '{ "aspect ratio" : "get" }'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'normal': 'Normal (16:9)',
            'full': 'Full (4:3)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '{ "focus" : "action" }'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'far',
            'Near': 'near',
            'Stop': 'stop'
        }

        speed = qualifier['Speed']
        if speed == 'Auto' or 0 <= int(speed) <= 14:
            if value == 'Stop':
                FocusCmdString = '{{ "focus" : "{}" }}'.format(ValueStateValues[value])
            else:
                if speed == 'Auto':
                    speed = '"{}"'.format(speed.lower())
                FocusCmdString = '{{ "focus" : {{ "{0}" : {1} }} }}'.format(ValueStateValues[value], speed)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        FreezeCmdString = '{{ "freeze" : "{}" }}'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '{ "freeze" : "status" }'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Camera': 'camera',
            'HDMI 1': 'hdmi1',
            'HDMI 2': 'hdmi2',
            'RGB': 'rgb'
        }

        InputCmdString = '{{ "switch input" : "{}" }}'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLED(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        LEDCmdString = '{{ "light switch" : "{}" }}'.format(ValueStateValues[value])
        self.__SetHelper('LED', LEDCmdString, value, qualifier)

    def UpdateLED(self, value, qualifier):

        LEDCmdString = '{ "light switch" : "status" }'
        self.__UpdateHelper('LED', LEDCmdString, value, qualifier)

    def __MatchLED(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LED', value, None)

    def SetRotation(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '90': '90',
            '180': '180',
            '270': '270'
        }

        RotationCmdString = '{{ "rotation" : {} }}'.format(ValueStateValues[value])
        self.__SetHelper('Rotation', RotationCmdString, value, qualifier)

    def UpdateRotation(self, value, qualifier):

        RotationCmdString = '{ "rotation" : "status" }'
        self.__UpdateHelper('Rotation', RotationCmdString, value, qualifier)

    def __MatchRotation(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Rotation', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Wide': 'wide',
            'Tele': 'tele',
            'Stop': 'stop'
        }

        speed = qualifier['Speed']
        if speed == 'Auto' or 0 <= int(speed) <= 7:
            if value == 'Stop':
                ZoomCmdString = '{{ "zoom" : "{}" }}'.format(ValueStateValues[value])
            else:
                if speed == 'Auto':
                    speed = '"{}"'.format(speed.lower())
                ZoomCmdString = '{{ "zoom" : {{ "{0}" : {1} }} }}'.format(ValueStateValues[value], speed)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        DEVICE_ERROR_CODES = {
            '1': 'Busy: Not ready to accept commands.',
            '2': 'Invalid Parameter: Parameter(s) are invalid.',
            '3': 'Mechanical Abnormality: Product is not working correctly.',
            '4': 'Not Found: Undefined command.',
            '5': 'Media Full: No enough space in the media.'
        }

        self.Error(['Error, ' + DEVICE_ERROR_CODES[match.group(1).decode()]])

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
