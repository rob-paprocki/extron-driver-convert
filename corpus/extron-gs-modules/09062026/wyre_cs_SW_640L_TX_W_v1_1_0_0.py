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
            'AudioMute': { 'Status': {}},
            'AudioSource': { 'Status': {}},
            'AutoSwitching': { 'Status': {}},
            'BYODPin': { 'Status': {}},
            'FullScreenSource': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'Multiview': { 'Status': {}},
            'MultiviewLayout': { 'Status': {}},
            'MultiviewSourceCommand': { 'Status': {}},
            'MultiviewSourceSelect': {'Parameters': ['Window'], 'Status': {}},
            'MultiviewSourceStatus': {'Parameters': ['Window'], 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AUDIO_MUTE (ON|OFF)[\r\n]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'AUDIOSW ((?:IN|BYOD)[1-4])(?: STOP)?[\r\n]'), self.__MatchAudioSource, None)
            self.AddMatchString(re.compile(b'AUTOSW_FN (ON|OFF)[\r\n]'), self.__MatchAutoSwitching, None)
            self.AddMatchString(re.compile(b'BYOD_ACCESS_CODE (NONE|\d+)(?: AUTO)?[\r\n]'), self.__MatchBYODPin, None)
            self.AddMatchString(re.compile(b'SW (IN[1-4]|BYOD[1-4]|GUIDE|MV|DISCONNECTED) OUT([12])[\r\n]'), self.__MatchFullScreenSource, None)
            self.AddMatchString(re.compile(b'VIDIN_SIG (IN[1-4]|BYOD[1-4]) (NO|VALID)[\r\n]'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'MV_ENABLE (ON|OFF)[\r\n]'), self.__MatchMultiview, None)
            self.AddMatchString(re.compile(b'MV_LAYOUT 0X10[0-3] (FULLSCREEN|DUALVIEW|3WAYSPLIT|QUADVIEW)[\r\n]'), self.__MatchMultiviewLayout, None)
            self.AddMatchString(re.compile(b'MV_WIN_SRC (FULLSCREEN|DUALVIEW|3WAYSPLIT|QUADVIEW) (.+?)[\r\n]'), self.__MatchMultiviewSourceStatus, None)
            self.AddMatchString(re.compile(b'MV_WIN_SRC (NONE)[\r\n]'), self.__MatchMultiviewSourceStatus, None)
            self.AddMatchString(re.compile(b'STANDBY (ON|OFF)[\r\n]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOLGAIN_DATA (-?\d+)[\r\n]'), self.__MatchVolume, None)

        self.multiviewSource = {
            '1' : None,
            '2' : None,
            '3' : None,
            '4' : None
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            AudioMuteCmdString = 'SET AUDIO_MUTE {}\r\n'.format(value.upper())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'GET AUDIO_MUTE\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AudioMute', value, None)

    def SetAudioSource(self, value, qualifier):

        ValueStateValues = {
            'USB-C 1':  'IN1',
            'USB-C 2':  'IN2',
            'HDMI 3':   'IN3',
            'HDMI 4':   'IN4',
            'BYOD 1':   'BYOD1',
            'BYOD 2':   'BYOD2',
            'BYOD 3':   'BYOD3',
            'BYOD 4':   'BYOD4'
        }

        if value in ValueStateValues:
            AudioSourceCmdString = 'SET AUDIOSW {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AudioSource', AudioSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioSource')

    def UpdateAudioSource(self, value, qualifier):

        AudioSourceCmdString = 'GET AUDIOSW\r\n'
        self.__UpdateHelper('AudioSource', AudioSourceCmdString, value, qualifier)

    def __MatchAudioSource(self, match, tag):

        ValueStateValues = {
            'IN1': 'USB-C 1',
            'IN2': 'USB-C 2',
            'IN3': 'HDMI 3',
            'IN4': 'HDMI 4',
            'BYOD1': 'BYOD 1',
            'BYOD2': 'BYOD 2',
            'BYOD3': 'BYOD 3',
            'BYOD4': 'BYOD 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioSource', value, None)

    def SetAutoSwitching(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            AutoSwitchingCmdString = 'SET AUTOSW_FN {}\r\n'.format(value.upper())
            self.__SetHelper('AutoSwitching', AutoSwitchingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitching')

    def UpdateAutoSwitching(self, value, qualifier):

        AutoSwitchingCmdString = 'GET AUTOSW_FN\r\n'
        self.__UpdateHelper('AutoSwitching', AutoSwitchingCmdString, value, qualifier)

    def __MatchAutoSwitching(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoSwitching', value, None)

    def UpdateBYODPin(self, value, qualifier):

        BYODPinCmdString = 'GET BYOD_ACCESS_CODE\r\n'
        self.__UpdateHelper('BYODPin', BYODPinCmdString, value, qualifier)

    def __MatchBYODPin(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('BYODPin', value, None)

    def SetFullScreenSource(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'USB-C 1':  'IN1',
            'USB-C 2':  'IN2',
            'HDMI 3':   'IN3',
            'HDMI 4':   'IN4',
            'BYOD 1':   'BYOD1',
            'BYOD 2':   'BYOD2',
            'BYOD 3':   'BYOD3',
            'BYOD 4':   'BYOD4'
        }

        if 1 <= output <= 2 and value in ValueStateValues:
            FullScreenSourceCmdString = 'SET SW {} OUT{}\r\n'.format(ValueStateValues[value], output)
            self.__SetHelper('FullScreenSource', FullScreenSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFullScreenSource')

    def UpdateFullScreenSource(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            FullScreenSourceCmdString = 'GET SW OUT{}\r\n'.format(output)
            self.__UpdateHelper('FullScreenSource', FullScreenSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFullScreenSource')

    def __MatchFullScreenSource(self, match, tag):

        ValueStateValues = {
            'IN1':          'USB-C 1',
            'IN2':          'USB-C 2',
            'IN3':          'HDMI 3',
            'IN4':          'HDMI 4',
            'BYOD1':        'BYOD 1',
            'BYOD2':        'BYOD 2',
            'BYOD3':        'BYOD 3',
            'BYOD4':        'BYOD 4',
            'GUIDE':        'Guide',
            'MV':           'Multiview',
            'DISCONNECTED': 'None'
        }

        qualifier = {
            'Output': match.group(2).decode()
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FullScreenSource', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputStates = {
            'USB-C 1':  'IN1',
            'USB-C 2':  'IN2',
            'HDMI 3':   'IN3',
            'HDMI 4':   'IN4',
            'BYOD 1':   'BYOD1',
            'BYOD 2':   'BYOD2',
            'BYOD 3':   'BYOD3',
            'BYOD 4':   'BYOD4'
        }
        input_ = qualifier['Input']

        if input_ in InputStates:
            InputSignalStatusCmdString = 'GET VIDIN_SIG {}\r\n'.format(InputStates[input_])
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        InputStates = {
            'IN1': 'USB-C 1',
            'IN2': 'USB-C 2',
            'IN3': 'HDMI 3',
            'IN4': 'HDMI 4',
            'BYOD1': 'BYOD 1',
            'BYOD2': 'BYOD 2',
            'BYOD3': 'BYOD 3',
            'BYOD4': 'BYOD 4'
        }

        ValueStateValues = {
            'VALID':    'Active',
            'NO':       'Not Active'
        }

        qualifier = {
            'Input': InputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetMultiview(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            MultiviewCmdString = 'SET MV_ENABLE {}\r\n'.format(value.upper())
            self.__SetHelper('Multiview', MultiviewCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiview')

    def UpdateMultiview(self, value, qualifier):

        MultiviewCmdString = 'GET MV_ENABLE\r\n'
        self.__UpdateHelper('Multiview', MultiviewCmdString, value, qualifier)

    def __MatchMultiview(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Multiview', value, None)

    def SetMultiviewLayout(self, value, qualifier):

        ValueStateValues = {
            'Full Screen':  'FULLSCREEN',
            'Dual View':    'DUALVIEW',
            '3-Way Split':  '3WAYSPLIT',
            'Quad View':    'QUADVIEW'
        }

        if value in ValueStateValues:
            MultiviewLayoutCmdString = 'SET MV_LAYOUT {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('MultiviewLayout', MultiviewLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiviewLayout')

    def UpdateMultiviewLayout(self, value, qualifier):

        MultiviewLayoutCmdString = 'GET MV_LAYOUT\r\n'
        self.__UpdateHelper('MultiviewLayout', MultiviewLayoutCmdString, value, qualifier)

    def __MatchMultiviewLayout(self, match, tag):

        ValueStateValues = {
            'FULLSCREEN':   'Full Screen',
            'DUALVIEW':     'Dual View',
            '3WAYSPLIT':    '3-Way Split',
            'QUADVIEW':     'Quad View'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MultiviewLayout', value, None)

    def SetMultiviewSourceCommand(self, value, qualifier):

        InputStates = {
            'USB-C 1':  'IN1',
            'USB-C 2':  'IN2',
            'HDMI 3':   'IN3',
            'HDMI 4':   'IN4',
            'BYOD 1':   'BYOD1',
            'BYOD 2':   'BYOD2',
            'BYOD 3':   'BYOD3',
            'BYOD 4':   'BYOD4',
            'None':     'NONE'
        }
        
        ValueStateValues = {
            'Full Screen':  1,
            'Dual View':    2,
            '3-Way Split':  3,
            'Quad View':    4
        }

        if value in ValueStateValues:
            MultiviewSourceCommandCmdString = 'SET MV_WIN_SRC CURRENT'

            for window in range(1, ValueStateValues[value] + 1):
                input_ = self.multiviewSource[str(window)]

                if input_ is not None:
                    MultiviewSourceCommandCmdString += ' WIN{} {}'.format(window, InputStates[input_])
                else:
                    self.Discard('Invalid Command for SetMultiviewSourceCommand')
                    return
            
            MultiviewSourceCommandCmdString += '\r\n'

            self.__SetHelper('MultiviewSourceCommand', MultiviewSourceCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiviewSourceCommand')

    def SetMultiviewSourceSelect(self, value, qualifier):

        window = int(qualifier['Window'])

        ValueStateValues = {
            'USB-C 1',
            'USB-C 2',
            'HDMI 3',
            'HDMI 4',
            'BYOD 1',
            'BYOD 2',
            'BYOD 3',
            'BYOD 4',
            'None'
        }
        
        if 1 <= window <= 4 and value in ValueStateValues:
            self.multiviewSource[qualifier['Window']] = value
        else:
            self.Discard('Invalid Command for SetMultiviewSourceSelect')

    def UpdateMultiviewSourceStatus(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= 4:
            MultiviewSourceStatusCmdString = 'GET MV_WIN_SRC\r\n'
            self.__UpdateHelper('MultiviewSourceStatus', MultiviewSourceStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMultiviewSourceStatus')

    def __MatchMultiviewSourceStatus(self, match, tag):

        ValueStateValues = {
            'IN1': 'USB-C 1',
            'IN2': 'USB-C 2',
            'IN3': 'HDMI 3',
            'IN4': 'HDMI 4',
            'BYOD1': 'BYOD 1',
            'BYOD2': 'BYOD 2',
            'BYOD3': 'BYOD 3',
            'BYOD4': 'BYOD 4',
            'NONE': 'None'
        }

        LayoutStates = {
            'NONE':         0,
            'FULLSCREEN':   1,
            'DUALVIEW':     2,
            '3WAYSPLIT':    3,
            'QUADVIEW':     4
        }
        layout = match.group(1).decode()

        if layout != 'NONE':
            window_sources = match.group(2).decode().strip().split()

            for window in range(LayoutStates[layout]):
                value = ValueStateValues[window_sources[window * 2 + 1]]
            
                self.WriteStatus('MultiviewSourceStatus', value, {'Window': str(window + 1)})
        for window in range(LayoutStates[layout] + 1, 5):
            self.WriteStatus('MultiviewSourceStatus', 'None', {'Window': str(window)})

    def SetPower(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            PowerCmdString = 'SET STANDBY {}\r\n'.format(value.upper())
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET STANDBY\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if -100 <= value <= 6:
            VolumeCmdString = 'SET VOLGAIN_DATA {}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET VOLGAIN_DATA\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if -100 <= value <= 6:
            self.WriteStatus('Volume', value, None)

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

        self.multiviewSource = {
            '1' : None,
            '2' : None,
            '3' : None,
            '4' : None
        }

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()