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
        self.Models = {
            'DM7': self.yama_25_17350_DM7,
            'DM7 Compact': self.yama_25_17350_DM7C
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DCAFaderLevel': {'Parameters':['DCA'], 'Status': {}},
            'DCAFaderPower': {'Parameters':['DCA'], 'Status': {}},
            'DeviceFirmware': { 'Status': {}},
            'InputMatrixLevel': {'Parameters':['Input','Matrix'], 'Status': {}},
            'InputMatrixPrePost': {'Parameters':['Input','Matrix'], 'Status': {}},
            'InputMixLevel': {'Parameters':['Input','Mix'], 'Status': {}},
            'MixMatrixLevel': {'Parameters':['Mix','Matrix'], 'Status': {}},
            'MixMatrixPower': {'Parameters':['Mix','Matrix'], 'Status': {}},
            'MuteGroup': {'Parameters':['Group'], 'Status': {}},
            'SceneRecall': {'Parameters':['Scene'], 'Status': {}},
            'SceneSave': {'Parameters':['Scene'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OK get MIXER:Current/DCA/Fader/Level ([12][0-9]|[0-9]) 0 (-?\d+)\n?'), self.__MatchDCAFaderLevel, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/DCA/Fader/On ([12][0-9]|[0-9]) 0 ([01])\n?'), self.__MatchDCAFaderPower, None)
            self.AddMatchString(re.compile(b'OK devinfo version "(.+)"\n?'), self.__MatchDeviceFirmware, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/InCh/ToMtrx/Level (\d+) (1[01]|[0-9]) (-?\d+)\n?'), self.__MatchInputMatrixLevel, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/InCh/ToMtrx/PrePost (\d+) (1[01]|[0-9]) ([01])\n?'), self.__MatchInputMatrixPrePost, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/InCh/ToMix/Level (\d+) ([1-4][0-9]|[0-9]) (-?\d+)\n?'), self.__MatchInputMixLevel, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/Mix/ToMtrx/Level ([1-4][0-9]|[0-9]) (1[01]|[0-9]) (-?\d+)\n?'), self.__MatchMixMatrixLevel, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/Mix/ToMtrx/On ([1-4][0-9]|[0-9]) (1[01]|[0-9]) ([01])\n?'), self.__MatchMixMatrixPower, None)
            self.AddMatchString(re.compile(b'OK get MIXER:Current/MuteGrpCtrl/On (1[01]|[0-9]) 0 ([01])\n?'), self.__MatchMuteGroup, None)
            self.AddMatchString(re.compile(b'OK sscurrent_ex scene_([ab]) (\d+)( modified| unmodified)?\n?'), self.__MatchSceneRecall, None)

    def SetDCAFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 24 and -138 <= value <= 10:
            DCAFaderLevelCmdString = 'set MIXER:Current/DCA/Fader/Level {} 0 {}\n\r'.format(int(qualifier['DCA'])-1, value*100)
            self.__SetHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderLevel')

    def UpdateDCAFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 24:
            DCAFaderLevelCmdString = 'get MIXER:Current/DCA/Fader/Level {} 0\n\r'.format(int(qualifier['DCA'])-1)
            self.__UpdateHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderLevel')

    def __MatchDCAFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['DCA'] = str(int(match.group(1).decode())+1)
        value = int(int(match.group(2).decode())/100)
        if -138 <= value <= 10:
            self.WriteStatus('DCAFaderLevel', value, qualifier)

    def SetDCAFaderPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['DCA']) <= 24 and value in ValueStateValues:
            DCAFaderPowerCmdString = 'set MIXER:Current/DCA/Fader/On {} 0 {}\n\r'.format(int(qualifier['DCA'])-1, ValueStateValues[value])
            self.__SetHelper('DCAFaderPower', DCAFaderPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderPower')

    def UpdateDCAFaderPower(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 24:
            DCAFaderPowerCmdString = 'get MIXER:Current/DCA/Fader/On {} 0\n\r'.format(int(qualifier['DCA'])-1)
            self.__UpdateHelper('DCAFaderPower', DCAFaderPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderPower')

    def __MatchDCAFaderPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['DCA'] = str(int(match.group(1).decode())+1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DCAFaderPower', value, qualifier)

    def UpdateDeviceFirmware(self, value, qualifier):

        DeviceFirmwareCmdString = 'devinfo version\n\r'
        self.__UpdateHelper('DeviceFirmware', DeviceFirmwareCmdString, value, qualifier)

    def __MatchDeviceFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceFirmware', value, None)

    def SetInputMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Matrix']) <= 12 and -138 <= value <= 10:
            InputMatrixLevelCmdString = 'set MIXER:Current/InCh/ToMtrx/Level {} {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Matrix'])-1, value*100)
            self.__SetHelper('InputMatrixLevel', InputMatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMatrixLevel')

    def UpdateInputMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Matrix']) <= 12:
            InputMatrixLevelCmdString = 'get MIXER:Current/InCh/ToMtrx/Level {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Matrix'])-1)
            self.__UpdateHelper('InputMatrixLevel', InputMatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMatrixLevel')

    def __MatchInputMatrixLevel(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode())+1)
        qualifier['Matrix'] = str(int(match.group(2).decode())+1)
        value = int(int(match.group(3).decode())/100)
        if -138 <= value <= 10:
            self.WriteStatus('InputMatrixLevel', value, qualifier)

    def SetInputMatrixPrePost(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Matrix']) <= 12 and value in ValueStateValues:
            InputMatrixPrePostCmdString = 'set MIXER:Current/InCh/ToMtrx/PrePost {} {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Matrix'])-1, ValueStateValues[value])
            self.__SetHelper('InputMatrixPrePost', InputMatrixPrePostCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMatrixPrePost')

    def UpdateInputMatrixPrePost(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Matrix']) <= 12:
            InputMatrixPrePostCmdString = 'get MIXER:Current/InCh/ToMtrx/PrePost {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Matrix'])-1)
            self.__UpdateHelper('InputMatrixPrePost', InputMatrixPrePostCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMatrixPrePost')

    def __MatchInputMatrixPrePost(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode())+1)
        qualifier['Matrix'] = str(int(match.group(2).decode())+1)
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('InputMatrixPrePost', value, qualifier)

    def SetInputMixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Mix']) <= 48 and -138 <= value <= 10:
            InputMixLevelCmdString = 'set MIXER:Current/InCh/ToMix/Level {} {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Mix'])-1, value*100)
            self.__SetHelper('InputMixLevel', InputMixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMixLevel')

    def UpdateInputMixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.maxInputs and 1 <= int(qualifier['Mix']) <= 48:
            InputMixLevelCmdString = 'get MIXER:Current/InCh/ToMix/Level {} {}\n\r'.format(int(qualifier['Input'])-1, int(qualifier['Mix'])-1)
            self.__UpdateHelper('InputMixLevel', InputMixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMixLevel')

    def __MatchInputMixLevel(self, match, tag):

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode())+1)
        qualifier['Mix'] = str(int(match.group(2).decode())+1)
        value = int(int(match.group(3).decode())/100)
        if -138 <= value <= 10:
            self.WriteStatus('InputMixLevel', value, qualifier)

    def SetMixMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Mix']) <= 48 and 1 <= int(qualifier['Matrix']) <= 12 and -138 <= value <= 10:
            MixMatrixLevelCmdString = 'set MIXER:Current/Mix/ToMtrx/Level {} {} {}\n\r'.format(int(qualifier['Mix'])-1, int(qualifier['Matrix'])-1, value*100)
            self.__SetHelper('MixMatrixLevel', MixMatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixMatrixLevel')

    def UpdateMixMatrixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Mix']) <= 48 and 1 <= int(qualifier['Matrix']) <= 12:
            MixMatrixLevelCmdString = 'get MIXER:Current/Mix/ToMtrx/Level {} {}\n\r'.format(int(qualifier['Mix'])-1, int(qualifier['Matrix'])-1)
            self.__UpdateHelper('MixMatrixLevel', MixMatrixLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixMatrixLevel')

    def __MatchMixMatrixLevel(self, match, tag):

        qualifier = {}
        qualifier['Mix'] = str(int(match.group(1).decode())+1)
        qualifier['Matrix'] = str(int(match.group(2).decode())+1)
        value = int(int(match.group(3).decode())/100)
        if -138 <= value <= 10:
            self.WriteStatus('MixMatrixLevel', value, qualifier)

    def SetMixMatrixPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Mix']) <= 48 and 1 <= int(qualifier['Matrix']) <= 12 and value in ValueStateValues:
            MixMatrixPowerCmdString = 'set MIXER:Current/Mix/ToMtrx/On {} {} {}\n\r'.format(int(qualifier['Mix'])-1, int(qualifier['Matrix'])-1, ValueStateValues[value])
            self.__SetHelper('MixMatrixPower', MixMatrixPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixMatrixPower')

    def UpdateMixMatrixPower(self, value, qualifier):

        if 1 <= int(qualifier['Mix']) <= 48 and 1 <= int(qualifier['Matrix']) <= 12:
            MixMatrixPowerCmdString = 'get MIXER:Current/Mix/ToMtrx/On {} {}\n\r'.format(int(qualifier['Mix'])-1, int(qualifier['Matrix'])-1)
            self.__UpdateHelper('MixMatrixPower', MixMatrixPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixMatrixPower')

    def __MatchMixMatrixPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Mix'] = str(int(match.group(1).decode())+1)
        qualifier['Matrix'] = str(int(match.group(2).decode())+1)
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MixMatrixPower', value, qualifier)

    def SetMuteGroup(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Group']) <= 12 and value in ValueStateValues:
            MuteGroupCmdString = 'set MIXER:Current/MuteGrpCtrl/On {} 0 {}\n\r'.format(int(qualifier['Group'])-1, ValueStateValues[value])
            self.__SetHelper('MuteGroup', MuteGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteGroup')

    def UpdateMuteGroup(self, value, qualifier):

        if 1 <= int(qualifier['Group']) <= 12:
            MuteGroupCmdString = 'get MIXER:Current/MuteGrpCtrl/On {} 0\n\r'.format(int(qualifier['Group'])-1)
            self.__UpdateHelper('MuteGroup', MuteGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMuteGroup')

    def __MatchMuteGroup(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Group'] = str(int(match.group(1).decode())+1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MuteGroup', value, qualifier)

    def SetSceneRecall(self, value, qualifier):

        SceneStates = {
            'A': 'a',
            'B': 'b'
            }
        scene = qualifier['Scene']

        if scene in SceneStates and 0 <= int(value) <= 499:
            SceneRecallCmdString = 'ssrecall_ex scene_{} {}\n\r'.format(SceneStates[scene], value)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def UpdateSceneRecall(self, value, qualifier):

        SceneStates = {
            'A': 'a',
            'B': 'b'
            }
        scene = qualifier['Scene']

        if scene in SceneStates:
            SceneRecallCmdString = 'sscurrent_ex scene_{}\n\r'.format(SceneStates[scene])
            self.__UpdateHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSceneRecall')

    def __MatchSceneRecall(self, match, tag):

        qualifier = {}
        qualifier['Scene'] = match.group(1).decode().upper()
        value = match.group(2).decode()
        if 0 <= int(value) <= 499:
            self.WriteStatus('SceneRecall', value, qualifier)

    def SetSceneSave(self, value, qualifier):

        SceneStates = {
            'A': 'a',
            'B': 'b'
            }
        scene = qualifier['Scene']

        if scene in SceneStates and 0 <= int(value) <= 499:
            SceneSaveCmdString = 'ssupdate_ex scene_{} {}\n\r'.format(SceneStates[scene], value)
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSave')

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

    def yama_25_17350_DM7(self):

        self.maxInputs = 120

    def yama_25_17350_DM7C(self):

        self.maxInputs = 72

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