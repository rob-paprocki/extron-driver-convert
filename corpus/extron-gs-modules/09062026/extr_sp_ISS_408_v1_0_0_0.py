from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
from collections import defaultdict

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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'DissolveSpeed': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Output', 'Type'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'PresetSave': {'Parameters': ['Output'], 'Status': {}},
            'SwitchEffect': {'Status': {}},
            'SwitchMode': {'Status': {}},
            'TestPattern': {'Parameters': ['Output'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            if self.devicePassword:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def SetAudioGainAttenuation(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 8 and -24 <= value <= 9:
            if value >= 0:
                AudioGainAttenuationCmdString = '{}*{}G'.format(input_, value)
            else:
                AudioGainAttenuationCmdString = '{}*{}g'.format(input_, value)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 8:
            AudioGainAttenuationCmdString = '{}g'.format(input_)
            res = self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
            if res:
                try:
                    value = int(res.strip().replace(' ', ''))
                    if -24 <= value <= 9:
                        self.WriteStatus('AudioGainAttenuation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Audio Gain Attenuation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if output in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if output in OutputStates:
            AudioMuteCmdString = '{}Z'.format(OutputStates[output])
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.strip()]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Program': '1',
            'Preview': '2',
            'Both': '3'
        }

        if value in ValueStateValues:
            AutoImageCmdString = '0{}*14#'.format(ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetDissolveSpeed(self, value, qualifier):

        if 0.1 <= value <= 5.0:
            DissolveSpeedCmdString = '{}*5#'.format(int(value * 10))
            self.__SetHelper('DissolveSpeed', DissolveSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDissolveSpeed')

    def UpdateDissolveSpeed(self, value, qualifier):

        DissolveSpeedCmdString = '5#'
        res = self.__UpdateHelper('DissolveSpeed', DissolveSpeedCmdString, value, qualifier)
        if res:
            try:
                value = int(res) / 10
                if 0.1 <= value <= 5.0:
                    self.WriteStatus('DissolveSpeed', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Dissolve Speed: Invalid/unexpected response'])

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

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecutiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip()]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if output in OutputStates and value in ValueStateValues:
            FreezeCmdString = '{}*{}F'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if output in OutputStates:
            FreezeCmdString = '{}F'.format(OutputStates[output])
            res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.strip()]
                    self.WriteStatus('Freeze', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Freeze: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def SetInput(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }

        type_ = qualifier['Type']

        if output in OutputStates and type_ in TypeStates and 1 <= int(value) <= 8:
            InputCmdString = '{}*{}{}'.format(OutputStates[output], value, TypeStates[type_])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }

        type_ = qualifier['Type']

        Freeze_ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if output in OutputStates and type_ in TypeStates:
            InputCmdString = '{}I'.format(OutputStates[output])
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    video = int(res[3])
                    audio = int(res[8])

                    if 1 <= video <= 8 and 1 <= audio <= 8:
                        if video != audio:
                            av = 0
                        else:
                            av = video

                        self.WriteStatus('Input', str(audio), {'Output': output, 'Type': 'Audio'})
                        self.WriteStatus('Input', str(video), {'Output': output, 'Type': 'Video'})
                        self.WriteStatus('Input', str(av), {'Output': output, 'Type': 'Audio/Video'})
                    else:
                        self.Error(['Input: Invalid/unexpected response'])
                except (KeyError, IndexError, ValueError):
                    self.Error(['Input: Invalid/unexpected response'])

                try:
                    freeze = Freeze_ValueStateValues[res[13]]
                    self.WriteStatus('Freeze', freeze, {'Output': output})
                except (KeyError, IndexError):
                    self.Error(['Freeze: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetPresetRecall(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 3:
            PresetRecallCmdString = '{}*{}.'.format(OutputStates[output], value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        if output in OutputStates and 1 <= int(value) <= 3:
            PresetSaveCmdString = '{}*{},'.format(OutputStates[output], value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSwitchEffect(self, value, qualifier):

        ValueStateValues = {
            'Cut': '0',
            'Dissolve': '1'
        }

        if value in ValueStateValues:
            SwitchEffectCmdString = '0{}*4#'.format(ValueStateValues[value])
            self.__SetHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchEffect')

    def UpdateSwitchEffect(self, value, qualifier):

        ValueStateValues = {
            '0': 'Cut',
            '1': 'Dissolve'
        }

        SwitchEffectCmdString = '4#'
        res = self.__UpdateHelper('SwitchEffect', SwitchEffectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[str(int(res))]
                self.WriteStatus('SwitchEffect', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Switch Effect: Invalid/unexpected response'])

    def SetSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Stay': '0',
            'Swap': '1'
        }

        if value in ValueStateValues:
            SwitchModeCmdString = '{}*20#'.format(ValueStateValues[value])
            self.__SetHelper('SwitchMode', SwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchMode')

    def UpdateSwitchMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Stay',
            '1': 'Swap'
        }

        SwitchModeCmdString = '20#'
        res = self.__UpdateHelper('SwitchMode', SwitchModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip()]
                self.WriteStatus('SwitchMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Switch Mode: Invalid/unexpected response'])

    def SetTestPattern(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2',
            'Both': '3'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'Color Bars': 1,
            'Crosshatch': 2,
            '4x4 Crosshatch': 3,
            'Gray Scale': 4,
            'Crop': 5,
            'Alternating Pixels': 6,
            'Film 1': 7,
            'Film 2': 8,
            'Film 3': 9,
            'Ramp': 10,
            'Off': None
        }

        if output in OutputStates and value in ValueStateValues:
            if value == 'Off':
                TestPatternCmdString = '0*001J'
            else:
                TestPatternCmdString = '{}*{:03d}J'.format(OutputStates[output], ValueStateValues[value])

            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        OutputStates = {
            '1': 'Program',
            '2': 'Preview',
            '3': 'Both',
            '0': 'Off'
        }

        output = qualifier['Output']

        ValueStateValues = {
            1:  'Color Bars',
            2:  'Crosshatch',
            3:  '4x4 Crosshatch',
            4:  'Gray Scale',
            5:  'Crop',
            6:  'Alternating Pixels',
            7:  'Film 1',
            8:  'Film 2',
            9:  'Film 3',
            10: 'Ramp'
        }

        if output in ['Program', 'Preview', 'Both']:

            TestPatternCmdString = 'J'
            res = self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)
            if res:
                try:
                    output = OutputStates[res[0]]
                    value = ValueStateValues[int(res[2:])]

                    if output == 'Off':
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Program'})
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Preview'})
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
                    elif output == 'Program':
                        self.WriteStatus('TestPattern', value, {'Output': 'Program'})
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Preview'})
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
                    elif output == 'Preview':
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Program'})
                        self.WriteStatus('TestPattern', value, {'Output': 'Preview'})
                        self.WriteStatus('TestPattern', 'Off', {'Output': 'Both'})
                    elif output == 'Both':
                        self.WriteStatus('TestPattern', value, {'Output': 'Program'})
                        self.WriteStatus('TestPattern', value, {'Output': 'Preview'})
                        self.WriteStatus('TestPattern', value, {'Output': 'Both'})
                except (KeyError, IndexError, ValueError):
                    self.Error(['Test Pattern: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTestPattern')

    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }

        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in OutputStates and value in ValueStateValues:
            VideoMuteCmdString = '{}*{}B'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        OutputStates = {
            'Program': '1',
            'Preview': '2'
        }
        output = qualifier['Output']

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if output in OutputStates:
            VideoMuteCmdString = '{}B'.format(OutputStates[output])
            res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.strip()]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            'E01': 'Invalid input channel number (too large)',
            'E10': 'Invalid command',
            'E11': 'Invalid preset number (too large)',
            'E12': 'Invalid output number (too large)',
            'E13': 'Invalid value (out of range)'
        }

        if response.strip() in error_map:
            self.Error(['An error occurred: {}: {}: {}.'.format(sourceCmdName, response.strip(), error_map[response.strip()])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
    
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

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
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

