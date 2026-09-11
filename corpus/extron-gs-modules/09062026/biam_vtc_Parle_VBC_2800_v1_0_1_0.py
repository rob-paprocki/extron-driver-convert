# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ALSMicrophoneInputLevel': { 'Status': {}},
            'ALSMicrophoneInputMute': { 'Status': {}},
            'ALSSource': { 'Status': {}},
            'AnalogInputGain': { 'Status': {}},
            'AnalogInputLevel': { 'Status': {}},
            'AnalogInputMute': { 'Status': {}},
            'AutoFraming': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputSource': { 'Status': {}},
            'PanTilt': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'USBHook': { 'Status': {}},
            'USBInputLevel': { 'Status': {}},
            'USBInputMute': { 'Status': {}},
            'USBOutputLevel': { 'Status': {}},
            'USBOutputMute': { 'Status': {}},
            'Zoom': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\! "publishToken":"ALSMicrophoneInputLevel" "value":(-?\d+\.\d+)(?: \+OK)?\r\n'), self.__MatchALSMicrophoneInputLevel, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"ALSMicrophoneInputMute" "value":(true|false)(?: \+OK)?\r\n'), self.__MatchALSMicrophoneInputMute, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"ALSSource" "value":([0-3])(?: \+OK)?\r\n'), self.__MatchALSSource, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"AnalogInputGain" "value":(\d+\.\d+)(?: \+OK)?\r\n'), self.__MatchAnalogInputGain, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"AnalogInputLevel" "value":(-?\d+\.\d+)(?: \+OK)?\r\n'), self.__MatchAnalogInputLevel, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"AnalogInputMute" "value":(true|false)(?: \+OK)?\r\n'), self.__MatchAnalogInputMute, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"InputSource" "value":([012])(?: \+OK)?\r\n'), self.__MatchInputSource, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"USBHook" "value":([01]|true|false)(?: \+OK)?\r\n'), self.__MatchUSBHook, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"USBInputLevel" "value":(\d+)(?: \+OK)?\r\n'), self.__MatchUSBInputLevel, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"USBInputMute" "value":([01]|true|false)(?: \+OK)?\r\n'), self.__MatchUSBInputMute, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"USBOutputLevel" "value":(\d+)(?: \+OK)?\r\n'), self.__MatchUSBOutputLevel, None)
            self.AddMatchString(re.compile(b'\! "publishToken":"USBOutputMute" "value":([01]|true|false)(?: \+OK)?\r\n'), self.__MatchUSBOutputMute, None)
            self.AddMatchString(re.compile(b'\+OK "value":"(\d+\.\d+\.\d+)"\r\n'), self.__MatchFirmwareVersion, None)

    def build_subscription(self, subject, attribute, subscription_name):

        return '{} subscribe {} {}\r\n'.format(subject, attribute, subscription_name)
    
    def SetALSMicrophoneInputLevel(self, value, qualifier):

        if -100 <= value <= 12:
            ALSMicrophoneInputLevelCmdString = 'MicrophoneALSInput set level {:.1f}\r\n'.format(value)
            self.__SetHelper('ALSMicrophoneInputLevel', ALSMicrophoneInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetALSMicrophoneInputLevel')

    def UpdateALSMicrophoneInputLevel(self, value, qualifier):

        ALSMicrophoneInputLevelCmdString = self.build_subscription('MicrophoneALSInput', 'level', 'ALSMicrophoneInputLevel')
        self.__UpdateHelper('ALSMicrophoneInputLevel', ALSMicrophoneInputLevelCmdString, value, qualifier)

    def __MatchALSMicrophoneInputLevel(self, match, tag):

        value = int(float(match.group(1).decode()))
        if -100 <= value <= 12:
            self.WriteStatus('ALSMicrophoneInputLevel', value, None)

    def SetALSMicrophoneInputMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'true',
            'Off':  'false'
        }

        if value in ValueStateValues:
            ALSMicrophoneInputMuteCmdString = 'MicrophoneALSInput set mute {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ALSMicrophoneInputMute', ALSMicrophoneInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetALSMicrophoneInputMute')

    def UpdateALSMicrophoneInputMute(self, value, qualifier):

        ALSMicrophoneInputMuteCmdString = self.build_subscription('MicrophoneALSInput', 'mute', 'ALSMicrophoneInputMute')
        self.__UpdateHelper('ALSMicrophoneInputMute', ALSMicrophoneInputMuteCmdString, value, qualifier)

    def __MatchALSMicrophoneInputMute(self, match, tag):

        ValueStateValues = {
            'true': 'On',
            'false': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ALSMicrophoneInputMute', value, None)

    def SetALSSource(self, value, qualifier):

        ValueStateValues = {
            'Off':                  '0',
            'Far End Only':         '1',
            'Near End Only':        '2',
            'Far/Near End Mixed':   '3'
        }

        if value in ValueStateValues:
            ALSSourceCmdString = 'ALSSource set input {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ALSSource', ALSSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetALSSource')

    def UpdateALSSource(self, value, qualifier):

        ALSSourceCmdString = self.build_subscription('ALSSource', 'input', 'ALSSource')
        self.__UpdateHelper('ALSSource', ALSSourceCmdString, value, qualifier)

    def __MatchALSSource(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Far End Only',
            '2': 'Near End Only',
            '3': 'Far/Near End Mixed'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ALSSource', value, None)

    def SetAnalogInputGain(self, value, qualifier):

        if 0 <= value <= 24:
            AnalogInputGainCmdString = 'AnalogInput set gain {:.1f}\r\n'.format(value)
            self.__SetHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputGain')

    def UpdateAnalogInputGain(self, value, qualifier):

        AnalogInputGainCmdString = self.build_subscription('AnalogInput', 'gain', 'AnalogInputGain')
        self.__UpdateHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)

    def __MatchAnalogInputGain(self, match, tag):

        value = int(float(match.group(1).decode()))
        if 0 <= value <= 24:
            self.WriteStatus('AnalogInputGain', value, None)

    def SetAnalogInputLevel(self, value, qualifier):

        if -100 <= value <= 12:
            AnalogInputLevelCmdString = 'AnalogInput set level {:.1f}\r\n'.format(value)
            self.__SetHelper('AnalogInputLevel', AnalogInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputLevel')

    def UpdateAnalogInputLevel(self, value, qualifier):

        AnalogInputLevelCmdString = self.build_subscription('AnalogInput', 'level', 'AnalogInputLevel')
        self.__UpdateHelper('AnalogInputLevel', AnalogInputLevelCmdString, value, qualifier)

    def __MatchAnalogInputLevel(self, match, tag):

        value = int(float(match.group(1).decode()))
        if -100 <= value <= 12:
            self.WriteStatus('AnalogInputLevel', value, None)

    def SetAnalogInputMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'true',
            'Off':  'false'
        }

        if value in ValueStateValues:
            AnalogInputMuteCmdString = 'AnalogInput set mute {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AnalogInputMute', AnalogInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputMute')

    def UpdateAnalogInputMute(self, value, qualifier):

        AnalogInputMuteCmdString = self.build_subscription('AnalogInput', 'mute', 'AnalogInputMute')
        self.__UpdateHelper('AnalogInputMute', AnalogInputMuteCmdString, value, qualifier)

    def __MatchAnalogInputMute(self, match, tag):

        ValueStateValues = {
            'true':     'On',
            'false':    'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AnalogInputMute', value, None)

    def SetAutoFraming(self, value, qualifier):

        ValueStateValues = {
            'On':       'Camera set autoframing true\r\n',
            'Off':      'Camera set autoframing false\r\n',
            'Toggle':   'Camera toggle autoframing\r\n'
        }

        if value in ValueStateValues:
            AutoFramingCmdString = ValueStateValues[value]
            self.__SetHelper('AutoFraming', AutoFramingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFraming')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'DEVICE get version\r\n'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):


        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInputSource(self, value, qualifier):

        ValueStateValues = {
            'USB Only':         '0',
            'Analog Only':      '1',
            'USB/Analog Mixed': '2'
        }

        if value in ValueStateValues:
            InputSourceCmdString = 'InputSource set input {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSource')

    def UpdateInputSource(self, value, qualifier):

        InputSourceCmdString = self.build_subscription('InputSource', 'input', 'InputSource')
        self.__UpdateHelper('InputSource', InputSourceCmdString, value, qualifier)

    def __MatchInputSource(self, match, tag):

        ValueStateValues = {
            '0': 'USB Only',
            '1': 'Analog Only',
            '2': 'USB/Analog Mixed'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSource', value, None)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up':       'Camera increment tilt 1\r\n',
            'Down':     'Camera decrement tilt 1\r\n',
            'Left':     'Camera decrement pan 1\r\n',
            'Right':    'Camera increment pan 1\r\n'
        }

        if value in ValueStateValues:
            PanTiltCmdString = ValueStateValues[value]
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 3:
            PresetRecallCmdString = 'Camera set presetRecall {}\r\n'.format(int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateUSBHook(self, value, qualifier):

        USBHookCmdString = self.build_subscription('USBOut', 'hook', 'USBHook')
        self.__UpdateHelper('USBHook', USBHookCmdString, value, qualifier)

    def __MatchUSBHook(self, match, tag):

        ValueStateValues = {
            '0':        'On',
            '1':        'Off',
            'false':    'On',
            'true':     'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBHook', value, None)

    def SetUSBInputLevel(self, value, qualifier):

        if 0 <= value <= 100:
            USBInputLevelCmdString = 'USBIn set level {}\r\n'.format(value)
            self.__SetHelper('USBInputLevel', USBInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBInputLevel')

    def UpdateUSBInputLevel(self, value, qualifier):

        USBInputLevelCmdString = self.build_subscription('USBIn', 'level', 'USBInputLevel')
        self.__UpdateHelper('USBInputLevel', USBInputLevelCmdString, value, qualifier)

    def __MatchUSBInputLevel(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('USBInputLevel', value, None)

    def SetUSBInputMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'true',
            'Off':  'false'
        }

        if value in ValueStateValues:
            USBInputMuteCmdString = 'USBIn set mute {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('USBInputMute', USBInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBInputMute')

    def UpdateUSBInputMute(self, value, qualifier):

        USBInputMuteCmdString = self.build_subscription('USBIn', 'mute', 'USBInputMute')
        self.__UpdateHelper('USBInputMute', USBInputMuteCmdString, value, qualifier)

    def __MatchUSBInputMute(self, match, tag):

        ValueStateValues = {
            '1':        'On',
            '0':        'Off',
            'true':     'On',
            'false':    'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBInputMute', value, None)

    def SetUSBOutputLevel(self, value, qualifier):

        if 0 <= value <= 100:
            USBOutputLevelCmdString = 'USBOut set level {}\r\n'.format(value)
            self.__SetHelper('USBOutputLevel', USBOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBOutputLevel')

    def UpdateUSBOutputLevel(self, value, qualifier):

        USBOutputLevelCmdString = self.build_subscription('USBOut', 'level', 'USBOutputLevel')
        self.__UpdateHelper('USBOutputLevel', USBOutputLevelCmdString, value, qualifier)

    def __MatchUSBOutputLevel(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('USBOutputLevel', value, None)

    def SetUSBOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'true',
            'Off':  'false'
        }

        if value in ValueStateValues:
            USBOutputMuteCmdString = 'USBOut set mute {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('USBOutputMute', USBOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBOutputMute')

    def UpdateUSBOutputMute(self, value, qualifier):

        USBOutputMuteCmdString = self.build_subscription('USBOut', 'mute', 'USBOutputMute')
        self.__UpdateHelper('USBOutputMute', USBOutputMuteCmdString, value, qualifier)

    def __MatchUSBOutputMute(self, match, tag):

        ValueStateValues = {
            '1':        'On',
            '0':        'Off',
            'true':     'On',
            'false':    'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBOutputMute', value, None)


    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'Camera increment zoom 0.5\r\n',
            'Wide': 'Camera decrement zoom 0.5\r\n'
        }

        if value in ValueStateValues:
            ZoomCmdString = ValueStateValues[value]
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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()