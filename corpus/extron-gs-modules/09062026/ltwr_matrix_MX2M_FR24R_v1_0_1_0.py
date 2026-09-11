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
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OverallHealth': { 'Status': {}},
            'PresetRecallCommand': { 'Status': {}},
            'RefreshMatrix': {'Parameters': ['Tie Type'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'/MEDIA/PORTS/VIDEO/I([1-9]|1\d|2[0-4])/PARAMETERS\.SignalPresent=([10F])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'/MEDIA/XP/(VIDEO|AUDIO)\.DestinationConnectionStatus=([\dI;]+);\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'/HEALTH\.OverallHealthState=(OK|WARNING|ERROR)\r\n'), self.__MatchOverallHealth, None)

            self.AddMatchString(re.compile(b'[npm]E .+? %E(\d{3}:.*?)\r\n'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   'mute',
            'Off':  'unmute'
        }

        if 1 <= output <= 280 and value in ValueStateValues:
            AudioMuteCmdString = 'CALL /MEDIA/XP/AUDIO:{}Destination(O{})\r\n'.format(ValueStateValues[value], output)
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateInputSignalStatus(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 24:
            InputSignalStatusCmdString = 'GET /MEDIA/PORTS/VIDEO/I{}/PARAMETERS.SignalPresent\r\n'.format(input_)
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active',
            'F': 'Unknown'
        }

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = int(qualifier['Input'])
        output = qualifier['Output']

        TieTypeStates = {
            'Audio': 280,
            'Video': 24
        }
        tie_type = qualifier['Tie Type']

        if tie_type in TieTypeStates and 0 <= input_ <= TieTypeStates[tie_type] and (output == 'All' or 1 <= int(output) <= TieTypeStates[tie_type]):
            input_ = 'I{}'.format(input_) if input_ != 0 else '0'

            if output != 'All':
                MatrixTieCommandCmdString = 'CALL /MEDIA/XP/{}:switch({}:O{})\r\n'.format(tie_type.upper(), input_, output)
            else:
                MatrixTieCommandCmdString = 'CALL /MEDIA/XP/{}:switchAll({})\r\n'.format(tie_type.upper(), input_)

            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __MatchOutputTieStatus(self, match, tag):

        tie_type = match.group(1).decode().title()
        outputs = match.group(2).decode().split(';')

        try:
            for output, input_ in enumerate(outputs, 1):
                if output > 280:
                    break
                
                if input_[0] == 'I':
                    input_ = input_[1:]

                input_ = int(input_)
                if 0 <= input_ <= 280:
                    self.WriteStatus('OutputTieStatus', str(input_), {'Output': str(output), 'Tie Type': tie_type})
        except:
            self.Error(['Output Tie Status: Invalid/unexpected response'])
            return

    def UpdateOverallHealth(self, value, qualifier):

        OverallHealthCmdString = 'GET /HEALTH.OverallHealthState\r\n'
        self.__UpdateHelper('OverallHealth', OverallHealthCmdString, value, qualifier)

    def __MatchOverallHealth(self, match, tag):

        ValueStateValues = {
            'OK':       'OK',
            'WARNING':  'Warning',
            'ERROR':    'Error'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OverallHealth', value, None)

    def SetPresetRecallCommand(self, value, qualifier):

        preset = value

        if preset:
            PresetRecallCommandCmdString = 'CALL /MEDIA/PRESET/{}:load()\r\n'.format(preset)
            self.__SetHelper('PresetRecallCommand', PresetRecallCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallCommand')

    def SetRefreshMatrix(self, value, qualifier):

        TieTypeStates = [
            'Audio',
            'Video'
        ]
        tie_type = qualifier['Tie Type']

        if tie_type in TieTypeStates:
            RefreshMatrixCmdString = 'GET /MEDIA/XP/{}.DestinationConnectionStatus\r\n'.format(tie_type.upper())
            self.__SetHelper('RefreshMatrix', RefreshMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def SetVideoMute(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   'mute',
            'Off':  'unmute'
        }

        if 1 <= output <= 24 and value in ValueStateValues:
            VideoMuteCmdString = 'CALL /MEDIA/XP/VIDEO:{}Destination(O{})\r\n'.format(ValueStateValues[value], output)
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 280 and 0 <= value <= 100:
            VolumeCmdString = 'SET /MEDIA/PORTS/AUDIO/O{}/PARAMETERS.VolumePercent={}\r\n'.format(output, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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

        self.Error(['An error occurred: {}'.format(match.group(1).decode())])

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