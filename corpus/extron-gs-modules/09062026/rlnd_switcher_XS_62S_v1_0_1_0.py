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
            'AutoMixing': { 'Status': {}},
            'DSK': { 'Status': {}},
            'DSKMultiview': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'InputAspectRatio': {'Parameters':['Input'], 'Status': {}},
            'InputMasterVolume': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'InputPresetVolume': {'Parameters':['Input'], 'Status': {}},
            'OutputAspectRatio': { 'Status': {}},
            'OutputChannel': {'Parameters':['Output'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'OutputSignalType': {'Parameters':['Output'], 'Status': {}},
            'OutputVolume': {'Parameters':['Output'], 'Status': {}},
            'PinP': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Split': { 'Status': {}},
            'Take': { 'Status': {}},
            'TranisitionCut': { 'Status': {}},
            'TransitionEffect': { 'Status': {}},
            'TransitionTime': { 'Status': {}},
        }

                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QVC:([0-2]),([0-7]);'), self.__MatchOutputChannel, None)
            self.AddMatchString(re.compile(b'\x02QVR:([0-9]|10);'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'\x02QAL:1([1-3]),([\-\d]+);'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'\x02ERR:([045]);'), self.__MatchError, None)

    def SetAutoMixing(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        AutoMixingCmdString = '\x02ATM:{};'.format(ValueStateValues[value])
        self.__SetHelper('AutoMixing', AutoMixingCmdString, value, qualifier)

    def SetDSK(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        DSKCmdString = '\x02DSK:{};'.format(ValueStateValues[value])
        self.__SetHelper('DSK', DSKCmdString, value, qualifier)

    def SetDSKMultiview(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        DSKMultiviewCmdString = '\x02DVW:{};'.format(ValueStateValues[value])
        self.__SetHelper('DSKMultiview', DSKMultiviewCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        FreezeCmdString = '\x02FRZ:{};'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInputAspectRatio(self, value, qualifier):

        InputStates = {
            'HDMI IN 5' : '0', 
            'HDMI IN 6' : '1', 
            'RGB IN 6'  : '2'
        }

        ValueStateValues = {
            'Full'       : '0',
            'Letterbox'  : '1',
            'Crop'       : '2',
            'Dot by Dot' : '3', 
            'Manual'     : '4'
        }

        InputAspectRatioCmdString = '\x02VIA:{},{};'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('InputAspectRatio', InputAspectRatioCmdString, value, qualifier)

    def SetInputMasterVolume(self, value, qualifier):

        InputStates = {
            'AUDIO IN 1'  : '0',
            'AUDIO IN 2'  : '1',
            'AUDIO IN 3'  : '2',
            'AUDIO IN 4'  : '3',
            'AUDIO IN 5/6': '4',
            'SDI IN 1'    : '5',
            'SDI IN 2'    : '6',
            'SDI IN 3'    : '7',
            'SDI IN 4'    : '8',
            'HDMI IN 5'   : '9',
            'HDMI IN 6'   : '10'
        }

        if -80 <= value <= 10:
            InputMasterVolumeCmdString = '\x02IL1:{},{};'.format(InputStates[qualifier['Input']], value*10)
            self.__SetHelper('InputMasterVolume', InputMasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMasterVolume')

    def SetInputMute(self, value, qualifier):

        InputStates = {
            'AUDIO IN 1'  : '0',
            'AUDIO IN 2'  : '1',
            'AUDIO IN 3'  : '2',
            'AUDIO IN 4'  : '3',
            'AUDIO IN 5/6': '4',
            'SDI IN 1'    : '5',
            'SDI IN 2'    : '6',
            'SDI IN 3'    : '7',
            'SDI IN 4'    : '8',
            'HDMI IN 5'   : '9',
            'HDMI IN 6'   : '10'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        InputMuteCmdString = '\x02IAM:{},{};'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)

    def SetInputPresetVolume(self, value, qualifier):

        InputStates = {
            'AUDIO IN 1'  : '0',
            'AUDIO IN 2'  : '1',
            'AUDIO IN 3'  : '2',
            'AUDIO IN 4'  : '3',
            'AUDIO IN 5/6': '4',
            'SDI IN 1'    : '5',
            'SDI IN 2'    : '6',
            'SDI IN 3'    : '7',
            'SDI IN 4'    : '8',
            'HDMI IN 5'   : '9',
            'HDMI IN 6'   : '10'
        }

        if -80 <= value <= 10:
            InputPresetVolumeCmdString = '\x02IL2:{},{};'.format(InputStates[qualifier['Input']], value*10)
            self.__SetHelper('InputPresetVolume', InputPresetVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetVolume')

    def SetOutputAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full'       : '0',
            'Letterbox'  : '1',
            'Crop'       : '2',
            'Dot by Dot' : '3', 
            'Manual'     : '4'
        }

        OutputAspectRatioCmdString = '\x02VOA:{};'.format(ValueStateValues[value])
        self.__SetHelper('OutputAspectRatio', OutputAspectRatioCmdString, value, qualifier)

    def SetOutputChannel(self, value, qualifier):

        OutputStates = {
            'Master' : 'PGM', 
            'Preset' : 'PST', 
            'AUX'    : 'AUX'
        }

        ValueStateValues = {
            'SDI IN 1'      : '0',
            'SDI IN 2'      : '1',
            'SDI IN 3'      : '2',
            'SDI IN 4'      : '3',
            'HDMI IN 5'     : '4',
            'HDMI/ANLG IN 6': '5',
            'STL/BKG IN 7'  : '6',
            'STL/BKG IN 8'  : '7'
        }

        OutputChannelCmdString = '\x02{}:{};'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('OutputChannel', OutputChannelCmdString, value, qualifier)

    def UpdateOutputChannel(self, value, qualifier):

        OutputStates = {
            'Master' : '0',
            'Preset' : '1',
            'AUX'    : '2'
        }

        OutputChannelCmdString = '\x02QVC:{};'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputChannel', OutputChannelCmdString, value, qualifier)

    def __MatchOutputChannel(self, match, tag):


        OutputStates = {
            '0' : 'Master',
            '1' : 'Preset',
            '2' : 'AUX'
        }

        ValueStateValues = {
            '0' : 'SDI IN 1', 
            '1' : 'SDI IN 2', 
            '2' : 'SDI IN 3', 
            '3' : 'SDI IN 4', 
            '4' : 'HDMI IN 5', 
            '5' : 'HDMI/ANLG IN 6', 
            '6' : 'STL/BKG IN 7', 
            '7' : 'STL/BKG IN 8'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputChannel', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '480p, 576p': '0',
            '720p'      : '1',
            '1080p'     : '2',
            'SVGA'      : '3',
            'XGA'       : '4',
            'WXGA'      : '5',
            'SXGA'      : '6',
            'FWXGA'     : '7',
            'SXGA+'     : '8',
            'UXGA'      : '9',
            'WUXGA'     : '10'
        }

        OutputResolutionCmdString = '\x02VOR:{};'.format(ValueStateValues[value])
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = '\x02QVR;'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '0' : '480p, 576p', 
            '1' : '720p', 
            '2' : '1080p', 
            '3' : 'SVGA', 
            '4' : 'XGA', 
            '5' : 'WXGA', 
            '6' : 'SXGA', 
            '7' : 'FWXGA', 
            '8' : 'SXGA+', 
            '9' : 'UXGA', 
            '10': 'WUXGA'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetOutputSignalType(self, value, qualifier):

        OutputStates = {
            'HDMI OUT 1' : '0', 
            'HDMI OUT 2' : '1', 
            'HDMI OUT 3' : '2'
        }

        ValueStateValues = {
            'DVI-D' : '0', 
            'HDMI'  : '1'
        }

        OutputSignalTypeCmdString = '\x02VOD:{},{};'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('OutputSignalType', OutputSignalTypeCmdString, value, qualifier)

    def SetOutputVolume(self, value, qualifier):

        OutputStates = {
            'Master' : '1',
            'Preset' : '2',
            'AUX'    : '3'
        }

        if -80 <= value <= 10:
            OutputVolumeCmdString = '\x02OL{}:{};'.format(OutputStates[qualifier['Output']], value*10)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputStates = {
            'Master' : '1',
            'Preset' : '2',
            'AUX'    : '3'
        }

        OutputVolumeCmdString = '\x02QAL:1{};'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        OutputStates = {
            '1' : 'Master',
            '2' : 'Preset',
            '3' : 'AUX'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = int(int(match.group(2).decode())/10)
        self.WriteStatus('OutputVolume', value, qualifier)

    def SetPinP(self, value, qualifier):

        ValueStateValues = {
            'Off'   : '0',
            'Master': '1',
            'Preset': '2'
        }

        PinPCmdString = '\x02PPS:{};'.format(ValueStateValues[value])
        self.__SetHelper('PinP', PinPCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 8:
            PresetRecallCmdString = '\x02MEM:{};'.format(int(value)-1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetSplit(self, value, qualifier):

        ValueStateValues = {
            'Off'   : '0',
            'Master': '1',
            'Preset': '2'
        }

        SplitCmdString = '\x02SPS:{};'.format(ValueStateValues[value])
        self.__SetHelper('Split', SplitCmdString, value, qualifier)

    def SetTake(self, value, qualifier):

        TakeCmdString = '\x02TAK;'
        self.__SetHelper('Take', TakeCmdString, value, qualifier)

    def SetTranisitionCut(self, value, qualifier):

        TranisitionCutCmdString = '\x02CUT;'
        self.__SetHelper('TranisitionCut', TranisitionCutCmdString, value, qualifier)

    def SetTransitionEffect(self, value, qualifier):

        ValueStateValues = {
            'Mix 1': '0',
            'Mix 2': '1',
            'Wipe' : '2'
        }

        TransitionEffectCmdString = '\x02TRS:{};'.format(ValueStateValues[value])
        self.__SetHelper('TransitionEffect', TransitionEffectCmdString, value, qualifier)

    def SetTransitionTime(self, value, qualifier):

        if 0 <= value <= 40:
            TransitionTimeCmdString = '\x02TIM:{};'.format(value)
            self.__SetHelper('TransitionTime', TransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionTime')

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

        ERROR_CODES = {
            '0': 'Syntax Error',
            '4': 'Invalid',
            '5': 'Out of Range Error'
        }

        value = match.group(1).decode()
        self.Error([ERROR_CODES[value]])

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