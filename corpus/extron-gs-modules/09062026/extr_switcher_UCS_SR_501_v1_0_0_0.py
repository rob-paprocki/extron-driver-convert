# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SPInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
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
            'AutoSwitchMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': {'Parameters':['Tie Type'], 'Status': {}},
            'InputHDCPAuthorization': {'Parameters':['Input'], 'Status': {}},
            'InputHDCPStatus': {'Parameters':['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'OutputHDCPStatus': { 'Status': {}},
            'OutputSignalStatus': { 'Status': {}},
            'ScreenSaverMode': { 'Status': {}},
            'ScreenSaverTimeout': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'USBDevicePort': {'Parameters':['Port'], 'Status': {}},
            'USBDeviceSignalStatus': {'Parameters':['Port'], 'Status': {}},
            'USBHostSignalStatus': {'Parameters':['Port'], 'Status': {}},
            'VideoMute': { 'Status': {}}
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Ausw(?P<value>[0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe(?P<value>[0-1])\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'In(?P<Input>[0-2]) (?P<value>All|Vid|Usb)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'HdcpE[0-1]? ?(?P<Input2>[0-1])\r\n'), self.__MatchInputHDCPAuthorization, 'All')
            self.AddMatchString(re.compile(b'HdcpE2\*(?P<Value>[0-1])\r\n'), self.__MatchInputHDCPAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI(?P<Input1>[0-2]) (?P<Input2>[0-2])\r\n'), self.__MatchInputHDCPStatus, None)
            self.AddMatchString(re.compile(b'Sig ?(?P<Input1>[0-1]) (?P<Input2>[0-1])\*(?P<Output>[0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(?P<value>[0-2])\r\n'), self.__MatchOutputHDCPStatus, None)
            self.AddMatchString(re.compile(b'SsavM(?P<value>[12])\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(re.compile(b'SsavT(?P<value>\d+)\r\n'), self.__MatchScreenSaverTimeout, None)
            self.AddMatchString(re.compile(b'SsavS(?P<value>[0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'UsbcX(?P<Port1>[0-1]) (?P<Port2>[0-1]) (?P<Port3>[0-1])\r\n'), self.__MatchUSBDevicePort, 'All')
            self.AddMatchString(re.compile(b'UsbcO(?P<Port1>[0-1]) (?P<Port2>[0-1]) (?P<Port3>[0-1])\r\n'), self.__MatchUSBDeviceSignalStatus, None)
            self.AddMatchString(re.compile(b'UsbcI(?P<Port1>[0-1]) (?P<Port2>[0-1])\r\n'), self.__MatchUSBHostSignalStatus, None)
            self.AddMatchString(re.compile(b'UsbcX(?P<Port>[1-3])\*(?P<Value>[0-1])\r\n'), self.__MatchUSBDevicePort, None)
            self.AddMatchString(re.compile(b'Vmt(?P<value>[0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()        
        self.VerboseDisabled = False

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'User Defined Priority': '1',
            'Input Memory Priority': '2'
            }

        if value in ValueStateValues:
            AutoSwitchModeCmdString = 'w{}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'User Defined Priority',
            '2': 'Input Memory Priority'
            }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        TypeStates = {
            'Audio/Video': '%',
            'USB': '^',
            'All': '!'
            }

        if qualifier['Tie Type'] in TypeStates and 0 <= int(value) <= 2:
            InputCmdString = '{}{}'.format(value, TypeStates[qualifier['Tie Type']])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        TypeStates = {
            'Audio/Video': '%',
            'USB': '^',
            'All': '!'
            }

        if qualifier['Tie Type'] in TypeStates:
            InputCmdString = '%^'
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        typestates = {
            'All': 'All', 
            'Vid': 'Audio/Video',
            'Usb': 'USB'
        }

        value = match.group('value').decode()
        input_ = match.group('Input').decode()
        if value == 'All':
            self.WriteStatus('Input', input_, {'Tie Type': typestates[value]})
            self.WriteStatus('Input', input_, {'Tie Type': 'Audio/Video'})
            self.WriteStatus('Input', input_, {'Tie Type': 'USB'})
        else:
            opposite = 'USB' if typestates[value] == 'Audio/Video' else 'Audio/Video'
            other_input = self.ReadStatus('Input', {'Tie Type': opposite})
            if other_input == input_:
                self.WriteStatus('Input', input_, {'Tie Type': typestates[value]})
                self.WriteStatus('Input', input_, {'Tie Type': 'All'})
            else:
                self.WriteStatus('Input', input_, {'Tie Type': typestates[value]})
                self.WriteStatus('Input', '0', {'Tie Type': 'All'})
        

    def SetInputHDCPAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            InputHDCPAuthorizationCmdString = 'wE2*{}HDCP\r'.format(ValueStateValues[value])
            self.__SetHelper('InputHDCPAuthorization', InputHDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDCPAuthorization')

    def UpdateInputHDCPAuthorization(self, value, qualifier):

        InputHDCPAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('InputHDCPAuthorization', InputHDCPAuthorizationCmdString, value, qualifier)

    def __MatchInputHDCPAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }
        
        if tag == 'All':
            Input2 = ValueStateValues[match.group('Input2').decode()]
            self.WriteStatus('InputHDCPAuthorization', Input2, None)
        else:
            Value = ValueStateValues[match.group('Value').decode()]
            self.WriteStatus('InputHDCPAuthorization', Value, None)

    def UpdateInputHDCPStatus(self, value, qualifier):

        InputHDCPStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('InputHDCPStatus', InputHDCPStatusCmdString, value, qualifier)

    def __MatchInputHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Detected',
            '1': 'Source Detected With HDCP',
            '2': 'Source Detected Without HDCP'
            }

        Input1 = ValueStateValues[match.group('Input1').decode()]
        Input2 = ValueStateValues[match.group('Input2').decode()]
        self.WriteStatus('InputHDCPStatus', Input1, {'Input': '1'})
        self.WriteStatus('InputHDCPStatus', Input2, {'Input': '2'})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r\n'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }

        Input1 = ValueStateValues[match.group('Input1').decode()]
        Input2 = ValueStateValues[match.group('Input2').decode()]
        self.WriteStatus('InputSignalStatus', Input1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', Input2, {'Input': '2'})

        output = ValueStateValues[match.group('Output').decode()]
        self.WriteStatus('OutputSignalStatus', output, None)

    def UpdateOutputHDCPStatus(self, value, qualifier):

        OutputHDCPStatusCmdString = 'wOHDCP\r\n'
        self.__UpdateHelper('OutputHDCPStatus', OutputHDCPStatusCmdString, value, qualifier)

    def __MatchOutputHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Detected',
            '1': 'Source Detected With HDCP',
            '2': 'Source Detected Without HDCP'
            }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('OutputHDCPStatus', value, None)

    def UpdateOutputSignalStatus(self, value, qualifier):

        self.UpdateInputSignalStatus(value, {'Input': '1'})

    def SetScreenSaverMode(self, value, qualifier):

        ValueStateValues = {
            'Black Output': '1',
            'Blue Output': '2'
        }
        if value in ValueStateValues:
            ScreenSaverModeCmdString = 'wM{}SSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverMode')

    def UpdateScreenSaverMode(self, value, qualifier):

        ScreenSaverModeCmdString = 'wMSSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, tag):

        ValueStateValues = {
            '1': 'Black Output',
            '2': 'Blue Output' 
        }
        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('ScreenSaverMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wSSSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Active input detected, timer not running',
            '1': 'No active input, timer running, output sync enabled',
            '2': 'No active input, timer expired, output sync disabled'
        }
        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def SetScreenSaverTimeout(self, value, qualifier):

        if 0 <= value <= 501:
            ScreenSaverTimeoutCmdString = 'wT{}SSAV\r'.format(value)
            self.__SetHelper('ScreenSaverTimeout', ScreenSaverTimeoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverTimeout')

    def UpdateScreenSaverTimeout(self, value, qualifier):

        ScreenSaverTimeoutCmdString = 'wTSSAV\r'
        self.__UpdateHelper('ScreenSaverTimeout', ScreenSaverTimeoutCmdString, value, qualifier)

    def __MatchScreenSaverTimeout(self, match, tag):

        value = int(match.group('value').decode())
        self.WriteStatus('ScreenSaverTimeout', value, None)

    def SetUSBDevicePort(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
            }

        if value in ValueStateValues and 1 <= int(qualifier['Port']) <= 3:
            USBDevicePortCmdString = 'wX{}*{}USBC\r'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('USBDevicePort', USBDevicePortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBDevicePort')

    def UpdateUSBDevicePort(self, value, qualifier):

        USBDevicePortCmdString = 'wXUSBC\r'
        self.__UpdateHelper('USBDevicePort', USBDevicePortCmdString, value, qualifier)

    def __MatchUSBDevicePort(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
            }
        if tag == 'All':
            port1 = ValueStateValues[match.group('Port1').decode()]
            port2 = ValueStateValues[match.group('Port2').decode()]
            port3 = ValueStateValues[match.group('Port3').decode()]
            self.WriteStatus('USBDevicePort', port1, {'Port': '1'})
            self.WriteStatus('USBDevicePort', port2, {'Port': '2'})
            self.WriteStatus('USBDevicePort', port3, {'Port': '3'})
        else:
            port = match.group('Port').decode()
            value = ValueStateValues[match.group('Value').decode()]
            self.WriteStatus('USBDevicePort', value, {'Port': port})

    def UpdateUSBDeviceSignalStatus(self, value, qualifier):

        USBDeviceSignalStatusCmdString = 'wOUSBC\r'
        self.__UpdateHelper('USBDeviceSignalStatus', USBDeviceSignalStatusCmdString, value, qualifier)

    def __MatchUSBDeviceSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }
        
        port1 = ValueStateValues[match.group('Port1').decode()]
        port2 = ValueStateValues[match.group('Port2').decode()]
        port3 = ValueStateValues[match.group('Port3').decode()]
        self.WriteStatus('USBDeviceSignalStatus', port1, {'Port': '1'})
        self.WriteStatus('USBDeviceSignalStatus', port2, {'Port': '2'})
        self.WriteStatus('USBDeviceSignalStatus', port3, {'Port': '3'})

    def UpdateUSBHostSignalStatus(self, value, qualifier):

        USBHostSignalStatusCmdString = 'wIUSBC\r'
        self.__UpdateHelper('USBHostSignalStatus', USBHostSignalStatusCmdString, value, qualifier)

    def __MatchUSBHostSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }
        
        port1 = ValueStateValues[match.group('Port1').decode()]
        port2 = ValueStateValues[match.group('Port2').decode()]
        self.WriteStatus('USBHostSignalStatus', port1, {'Port': '1'})
        self.WriteStatus('USBHostSignalStatus', port2, {'Port': '2'})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'Video and Sync': '2'
            }

        if value in ValueStateValues:
            VideoMuteCmdString = '{}B'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Video and Sync'
            }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid Input Number',
            '06': 'Invalid Channel Change',
            '10': 'Invalid command',
            '13': 'Invalid Parameter',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type'
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
        self.VerboseDisabled = True
        
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class SPIClass(SPInterface, DeviceClass):

    def __init__(self, spd, Model=None):
        SPInterface.__init__(self, spd)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        self.OnDisconnected()