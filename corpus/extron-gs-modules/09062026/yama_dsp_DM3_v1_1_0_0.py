from extronlib.interface import EthernetClientInterface
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
            'InputFaderLevel': {'Parameters':['Input'], 'Status': {}},
            'InputFaderMute': {'Parameters':['Input'], 'Status': {}},
            'InputMatrixMute': {'Parameters':['Input','Matrix'], 'Status': {}},
            'InputMixMute': {'Parameters':['Input','Mix'], 'Status': {}},
            'InputPrePostMute': {'Parameters':['Input','Mix'], 'Status': {}},
            'MatrixFaderLevel': {'Parameters':['Matrix'], 'Status': {}},
            'MatrixFaderMute': {'Parameters':['Matrix'], 'Status': {}},
            'MatrixOutputBalance': {'Parameters':['Matrix'], 'Status': {}},
            'MixFaderLevel': {'Parameters':['Mix'], 'Status': {}},
            'MixFaderMute': {'Parameters':['Mix'], 'Status': {}},
            'MixOutputBalance': {'Parameters':['Mix'], 'Status': {}},
            'SceneRecallA': { 'Status': {}},
            'SceneRecallB': { 'Status': {}},
            'SceneSaveA': { 'Status': {}},
            'SceneSaveB': { 'Status': {}},
            'StereoFaderLevel': {'Parameters':['Stereo'], 'Status': {}},
            'StereoFaderMute': {'Parameters':['Stereo'], 'Status': {}},
            'StereoInputFaderLevel': {'Parameters':['Stereo Input'], 'Status': {}},
            'StereoInputFaderMute': {'Parameters':['Stereo Input'], 'Status': {}},
            'StereoInputMixLevel': {'Parameters':['Stereo Input','Mix'], 'Status': {}},
            'StereoOutputBalance': {'Parameters':['Stereo'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OK sscurrent_ex scene_a (\d+)( modified| unmodified)?'), self.__MatchSceneRecallA, None)
            self.AddMatchString(re.compile(b'OK sscurrent_ex scene_b (\d+)( modified| unmodified)?'), self.__MatchSceneRecallB, None)

    def SetInputFaderLevel(self, value, qualifier):

        input = int(qualifier['Input'])
        if 1 <= input <= 16 and -138 <= value <= 10:
            InputFaderLevelCmdString = 'set MIXER:Current/InCh/Fader/Level {0} 0 {1}'.format(input-1, value * 100)
            self.__SetHelper('InputFaderLevel', InputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputFaderLevel')

    def SetInputFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        input = int(qualifier['Input'])
        if 1 <= input <= 16 and value in ValueStateValues:
            InputFaderMuteCmdString = 'set MIXER:Current/InCh/Fader/On {0} 0 {1}'.format(input-1, ValueStateValues[value])
            self.__SetHelper('InputFaderMute', InputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputFaderMute')

    def SetInputMatrixMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        input = int(qualifier['Input'])
        matrix = int(qualifier['Matrix'])
        if 1 <= input <= 16 and 1 <= matrix <= 2 and value in ValueStateValues:
            InputMatrixMuteCmdString = 'set MIXER:Current/InCh/ToMtrx/On {0} {1} {2}'.format(input-1, matrix-1, ValueStateValues[value])
            self.__SetHelper('InputMatrixMute', InputMatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMatrixMute')

    def SetInputMixMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        input = int(qualifier['Input'])
        mix = int(qualifier['Mix'])
        if 1 <= input <= 16 and 1 <= mix <= 6 and value in ValueStateValues:
            InputMixMuteCmdString = 'set MIXER:Current/InCh/ToMix/On {0} {1} {2}'.format(input-1, mix-1, ValueStateValues[value])
            self.__SetHelper('InputMixMute', InputMixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMixMute')

    def SetInputPrePostMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        input = int(qualifier['Input'])
        mix = int(qualifier['Mix'])
        if 1 <= input <= 16 and 1 <= mix <= 6 and value in ValueStateValues:
            InputPrePostMuteCmdString = 'set MIXER:Current/InCh/ToMix/PrePost {0} {1} {2}'.format(input-1, mix-1, ValueStateValues[value])
            self.__SetHelper('InputPrePostMute', InputPrePostMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPrePostMute')

    def SetMatrixFaderLevel(self, value, qualifier):

        matrix = int(qualifier['Matrix'])
        if 1 <= matrix <= 2 and -138 <= value <= 10:
            MatrixFaderLevelCmdString = 'set MIXER:Current/Mtrx/Fader/Level {0} 0 {1}'.format(matrix-1, value * 100)
            self.__SetHelper('MatrixFaderLevel', MatrixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderLevel')

    def SetMatrixFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        matrix = int(qualifier['Matrix'])
        if 1 <= matrix <= 2 and value in ValueStateValues:
            MatrixFaderMuteCmdString = 'set MIXER:Current/Mtrx/Fader/On {0} 0 {1}'.format(matrix-1, ValueStateValues[value])
            self.__SetHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderMute')

    def SetMatrixOutputBalance(self, value, qualifier):

        matrix = int(qualifier['Matrix'])
        if 1 <= matrix <= 2 and -63 <= value <= 63:
            MatrixOutputBalanceCmdString = 'set MIXER:Current/Mtrx/Out/Balance {0} 0 {1}'.format(matrix-1, value)
            self.__SetHelper('MatrixOutputBalance', MatrixOutputBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixOutputBalance')

    def SetMixFaderLevel(self, value, qualifier):

        mix = int(qualifier['Mix'])
        if 1 <= mix <= 6 and -138 <= value <= 10:
            MixFaderLevelCmdString = 'set MIXER:Current/Mix/Fader/Level {0} 0 {1}'.format(mix-1, value * 100)
            self.__SetHelper('MixFaderLevel', MixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixFaderLevel')

    def SetMixFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        mix = int(qualifier['Mix'])
        if 1 <= mix <= 6 and value in ValueStateValues:
            MixFaderMuteCmdString = 'set MIXER:Current/Mix/Fader/On {0} 0 {1}'.format(mix-1, ValueStateValues[value])
            self.__SetHelper('MixFaderMute', MixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixFaderMute')

    def SetMixOutputBalance(self, value, qualifier):

        mix = int(qualifier['Mix'])
        if 1 <= mix <= 6 and -63 <= value <= 63:
            MixOutputBalanceCmdString = 'set MIXER:Current/Mix/Out/Balance {0} 0 {1}'.format(mix-1, value)
            self.__SetHelper('MixOutputBalance', MixOutputBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixOutputBalance')

    def SetSceneRecallA(self, value, qualifier):

        if 0 <= int(value) <= 99:
            SceneRecallACmdString = 'ssrecall_ex scene_a {0}'.format(value)
            self.__SetHelper('SceneRecallA', SceneRecallACmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecallA')

    def UpdateSceneRecallA(self, value, qualifier):

        SceneRecallACmdString = 'sscurrent_ex scene_a'
        self.__UpdateHelper('SceneRecallA', SceneRecallACmdString, value, qualifier)

    def __MatchSceneRecallA(self, match, tag):

        value = match.group(1).decode()
        if 0 <= int(value) <= 99:
            self.WriteStatus('SceneRecallA', value, None)

    def SetSceneRecallB(self, value, qualifier):

        if 0 <= int(value) <= 99:
            SceneRecallBCmdString = 'ssrecall_ex scene_b {0}'.format(value)
            self.__SetHelper('SceneRecallB', SceneRecallBCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecallB')

    def UpdateSceneRecallB(self, value, qualifier):

        SceneRecallBCmdString = 'sscurrent_ex scene_b'
        self.__UpdateHelper('SceneRecallB', SceneRecallBCmdString, value, qualifier)

    def __MatchSceneRecallB(self, match, tag):

        value = match.group(1).decode()
        if 0 <= int(value) <= 99:
            self.WriteStatus('SceneRecallB', value, None)

    def SetSceneSaveA(self, value, qualifier):

        if 0 <= int(value) <= 99:
            SceneSaveACmdString = 'ssupdate_ex scene_a {0}'.format(value)
            self.__SetHelper('SceneSaveA', SceneSaveACmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSaveA')

    def SetSceneSaveB(self, value, qualifier):

        if 0 <= int(value) <= 99:
            SceneSaveBCmdString = 'ssupdate_ex scene_b {0}'.format(value)
            self.__SetHelper('SceneSaveB', SceneSaveBCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSaveB')
            
    def SetStereoFaderLevel(self, value, qualifier):

        stereo = int(qualifier['Stereo'])
        if 1 <= stereo <= 2 and -138 <= value <= 10:
            StereoFaderLevelCmdString = 'set MIXER:Current/St/Fader/Level {0} 0 {1}'.format(stereo-1, value * 100)
            self.__SetHelper('StereoFaderLevel', StereoFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoFaderLevel')

    def SetStereoFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        stereo = int(qualifier['Stereo'])
        if 1 <= stereo <= 2 and value in ValueStateValues:
            StereoFaderMuteCmdString = 'set MIXER:Current/St/Fader/On {0} 0 {1}'.format(stereo-1, ValueStateValues[value])
            self.__SetHelper('StereoFaderMute', StereoFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoFaderMute')

    def SetStereoInputFaderLevel(self, value, qualifier):

        stereoInput = int(qualifier['Stereo Input'])
        if 1 <= stereoInput <= 2 and -138 <= value <= 10:
            StereoInputFaderLevelCmdString = 'set MIXER:Current/StInCh/Fader/Level {0} 0 {1}'.format(stereoInput-1, value * 100)
            self.__SetHelper('StereoInputFaderLevel', StereoInputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoInputFaderLevel')

    def SetStereoInputFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        stereoInput = int(qualifier['Stereo Input'])
        if 1 <= stereoInput <= 2 and value in ValueStateValues:
            StereoInputFaderMuteCmdString = 'set MIXER:Current/StInCh/Fader/On {0} 0 {1}'.format(stereoInput-1, ValueStateValues[value])
            self.__SetHelper('StereoInputFaderMute', StereoInputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoInputFaderMute')

    def SetStereoInputMixLevel(self, value, qualifier):

        mix = int(qualifier['Mix'])
        stereoInput = int(qualifier['Stereo Input'])
        if 1 <= stereoInput <= 2 and 1 <= mix <= 6 and -138 <= value <= 10:
            StereoInputMixLevelCmdString = 'set MIXER:Current/StInCh/ToMix/Level {0} {1} {2}'.format(stereoInput-1, mix-1, value * 100)
            self.__SetHelper('StereoInputMixLevel', StereoInputMixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoInputMixLevel')

    def SetStereoOutputBalance(self, value, qualifier):

        stereo = int(qualifier['Stereo'])
        if 1 <= stereo <= 2 and -63 <= value <= 63:
            StereoOutputBalanceCmdString = 'set MIXER:Current/St/Out/Balance {0} 0 {1}'.format(stereo-1, value)
            self.__SetHelper('StereoOutputBalance', StereoOutputBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStereoOutputBalance')

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