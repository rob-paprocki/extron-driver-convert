from extronlib.interface import DanteInterface
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
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ATOutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            }

        self.VerboseDisabled = True

        self.LevelTypes = {
            'InputGain'                 : {'Min' : -18,  'Max' : 60},
            'ATOutputAttenuation'         : {'Min' : -100, 'Max' : 0},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DsG(40000|40001|40002|40003)\*([0-9 -]{1,5})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'DsM(40000|40001|40002|40003)\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'DsG(60000|60001|60002|60003)\*([0-9 -]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(re.compile(b'DsM(6000[0-3])\*([01])\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'(60-1947-01)'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'E([0-9]{2})\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetATOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize and self.__CheckValidLevelValue('ATOutputAttenuation', value):
            commandString = 'WG{0}*{1}AU\r'.format(channel + 59999, value)
            self.__SetHelper('ATOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATOutputAttenuation')

    def UpdateATOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            commandString = 'WG{0}AU\r'.format(channel + 59999)
            self.__UpdateHelper('ATOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):
        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output' : channel}
        value = int(match.group(2))
        self.WriteStatus('ATOutputAttenuation', value, qualifier)

    def SetInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize and self.__CheckValidLevelValue('InputGain', value):
            commandString = 'WG{0}*{1}AU\r'.format(channel + 39999, value)
            self.__SetHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize:
            commandString = 'WG{0}AU\r'.format(channel + 39999)
            self.__UpdateHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input' : channel}
        value = int(match.group(2))
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize:
            commandString = 'wM{0}*{1}AU\r'.format(channel + 39999, MuteStateValues[value])
            self.__SetHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize:
            commandString = 'wM{0}AU\r'.format(channel + 39999)
            self.__UpdateHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input' : channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            commandString = 'wM{0}*{1}AU\r'.format(channel + 59999, MuteStateValues[value])
            self.__SetHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            commandString = 'wM{0}AU\r'.format(channel + 59999)
            self.__UpdateHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output' : channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)
        
    def UpdatePartNumber(self, value, qualifier):

        PartNumberCmdString = 'n'
        self.__UpdateHelper('PartNumber', PartNumberCmdString, value, qualifier)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 8:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def __CheckValidLevelValue(self, command, value):
        return self.LevelTypes[command]['Min'] <= value <= self.LevelTypes[command]['Max']

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseDisabled:
                self.Send('w3cv\r')
                self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid Input Number',
            '06' : 'Invalid Channel Change',
            '10' : 'Invalid Command',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System/command timed out',
            '22' : 'Busy',
            '25' : 'Device not present',
            '30' : 'Hardware Failure',
            }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.SendNotify = True

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

class DanteClass(DanteInterface, DeviceClass):
    def __init__(self, Hostname, Protocol='Extron', DanteDomainManager=None, Domain=None, Model=None):
        DanteInterface.__init__(self, Hostname, Protocol, DanteDomainManager, Domain)
        DeviceClass.__init__(self)
        self.ConnectionType = 'Dante'
        self.HostName = Hostname
        self.IsSerial = False
        self.VerboseDisabled = False
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.HostName)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        DanteInterface.Disconnect(self)
        self.OnDisconnected()
