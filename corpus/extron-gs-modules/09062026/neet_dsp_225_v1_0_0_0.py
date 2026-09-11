from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.UnitID = '1'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioOutput': {'Status': {}},
            'Input1Mixer': {'Status': {}},
            'Input1Mute': {'Status': {}},
            'Input1Volume': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'IOControl': {'Parameters': ['Port', 'Delay', 'Time'], 'Status': {}},
            'IOControlStatus': {'Parameters': ['Port'], 'Status': {}},
            'IOFunction': {'Parameters': ['Port'], 'Status': {}},
            'OutputMute': {'Status': {}},
            'OutputVolume': {'Status': {}},
            'Power': {'Status': {}},
            }

    def __updateMatchStrings(self):
        if self.Unidirectional == 'False':
            self._compile_list.clear()

            self.AddMatchString(re.compile('NEUNIT={},INPUT=([1-5])\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile('NEUNIT={},SETTINGS=OUTPUT,INPUT=([1-5])\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchAudioOutput, None)
            self.AddMatchString(re.compile('NEUNIT={},SETTINGS=INPUT,INPUT=1,MIX=(TRUE|FALSE)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchInput1Mixer, None)
            self.AddMatchString(re.compile('NEUNIT={},MIXMUTE=(ON|OFF)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchInput1Mute, None)
            self.AddMatchString(re.compile('NEUNIT={},MIXVOL=([-+]?[1-7]?[0-9])\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchInput1Volume, None)
            self.AddMatchString(re.compile('NEUNIT={},SETTINGS=INPUT,INPUT=([1-4]),GAIN=([-+]?[01]?[0-9])\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchInputGain, None)
            self.AddMatchString(re.compile('NEUNIT={},IO=([1-4]),STATUS=(HIGH|LOW)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchIOControlStatus, None)
            self.AddMatchString(re.compile('NEUNIT={},SETTINGS=IO,IO=([1-4]),FUNCTION=(INPUT|OUTPUT)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchIOFunction, None)
            self.AddMatchString(re.compile('NEUNIT={},MUTE=(ON|OFF)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile('NEUNIT={},VOL=([-+]?[1-7]?[0-9])\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile('NEUNIT={},POWER=(ON|OFF)\r'.format(self._UnitID).encode(encoding='iso-8859-1')), self.__MatchPower, None)

    @property
    def UnitID(self):
        return self._UnitID

    @UnitID.setter
    def UnitID(self, value):
        if len(value) > 9:
            print('Unit ID parameter should not exceed 9 characters')
        else:
            self._UnitID = value
            self.__updateMatchStrings()

    def SetAudioInput(self, value, qualifier):

        if value in {'1', '2', '3', '4', '5'}:
            AudioInputCmdString = 'NEUNIT={},INPUT={}\r'.format(self._UnitID, value).encode(encoding='iso-8859-1')
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdString = 'NEUNIT={},INPUT?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('AudioInput', value, None)

    def SetAudioOutput(self, value, qualifier):

        if value in {'1', '2', '3', '4', '5'}:
            AudioOutputCmdString = 'NEUNIT={},SETTINGS=OUTPUT,INPUT={}\r'.format(self._UnitID, value).encode(encoding='iso-8859-1')
            self.__SetHelper('AudioOutput', AudioOutputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):

        AudioOutputCmdString = 'NEUNIT={},SETTINGS=OUTPUT,INPUT=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('AudioOutput', AudioOutputCmdString, value, qualifier)

    def __MatchAudioOutput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('AudioOutput', value, None)

    def SetInput1Mixer(self, value, qualifier):

        ValueStateValues = {
            'On': 'TRUE',
            'Off': 'FALSE'
        }
        Input1MixerCmdString = 'NEUNIT={},SETTINGS=INPUT,INPUT=1,MIX={}\r'.format(self._UnitID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Input1Mixer', Input1MixerCmdString, value, qualifier)

    def UpdateInput1Mixer(self, value, qualifier):

        Input1MixerCmdString = 'NEUNIT={},SETTINGS=INPUT,INPUT=1,MIX=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Input1Mixer', Input1MixerCmdString, value, qualifier)

    def __MatchInput1Mixer(self, match, tag):

        ValueStateValues = {
            b'TRUE': 'On',
            b'FALSE': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input1Mixer', value, None)

    def SetInput1Mute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }
        Input1MuteCmdString = 'NEUNIT={},MIXMUTE={}\r'.format(self._UnitID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Input1Mute', Input1MuteCmdString, value, qualifier)

    def UpdateInput1Mute(self, value, qualifier):

        Input1MuteCmdString = 'NEUNIT={},MIXMUTE=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Input1Mute', Input1MuteCmdString, value, qualifier)

    def __MatchInput1Mute(self, match, tag):

        ValueStateValues = {
            b'ON': 'On',
            b'OFF': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input1Mute', value, None)

    def SetInput1Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 12
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Input1VolumeCmdString = 'NEUNIT={},MIXVOL={}\r'.format(self._UnitID, value).encode(encoding='iso-8859-1')
            self.__SetHelper('Input1Volume', Input1VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput1Volume')

    def UpdateInput1Volume(self, value, qualifier):

        Input1VolumeCmdString = 'NEUNIT={},MIXVOL=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Input1Volume', Input1VolumeCmdString, value, qualifier)

    def __MatchInput1Volume(self, match, tag):

        ValueConstraints = {
            'Min': -70,
            'Max': 12
        }
        value = int(match.group(1))
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.WriteStatus('Input1Volume', value, None)
        else:
            print('Input 1 Volume: An invalid value was received')

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }
        Input = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in {'1', '2', '3', '4'}:
            InputGainCmdString = 'NEUNIT={},SETTINGS=INPUT,INPUT={},GAIN={}\r'.format(self._UnitID, Input, value).encode(encoding='iso-8859-1')
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if Input in {'1', '2', '3', '4'}:
            InputGainCmdString = 'NEUNIT={},SETTINGS=INPUT,INPUT={},GAIN=?\r'.format(self._UnitID, Input).encode(encoding='iso-8859-1')
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }
        value = int(match.group(2))
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            qualifier = {'Input': match.group(1).decode()}
            self.WriteStatus('InputGain', value, qualifier)
        else:
            print('Input Gain: An invalid value was received')

    def SetIOControl(self, value, qualifier):

        DelayTimeConstraints = {
            'Min': 0,
            'Max': 6500
        }
        ValueStateValues = {
            'Set': 'SET',
            'Release': 'RELEASE'
        }
        Delay = qualifier['Delay']
        Time = qualifier['Time']
        Port = qualifier['Port']
        if (DelayTimeConstraints['Min'] <= Delay <= DelayTimeConstraints['Max'] and
            DelayTimeConstraints['Min'] <= Time <= DelayTimeConstraints['Max'] and Port in {'1', '2', '3', '4'}):
            IOControlCmdString = 'NEUNIT={},IO={},TIME={:.1f},DELAY={:.1f},ACTION={}\r'.format(self._UnitID, Port, Time, Delay, ValueStateValues[value]).encode(encoding='iso-8859-1')
            self.__SetHelper('IOControl', IOControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIOControl')

    def UpdateIOControlStatus(self, value, qualifier):

        Port = qualifier['Port']
        if Port in {'1', '2', '3', '4'}:
            IOControlStatusCmdString = 'NEUNIT={},IO={},STATUS=?\r'.format(self._UnitID, Port).encode(encoding='iso-8859-1')
            self.__UpdateHelper('IOControlStatus', IOControlStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateIOControlStatus')

    def __MatchIOControlStatus(self, match, tag):

        ValueStateValues = {
            b'HIGH': 'High',
            b'LOW': 'Low'
        }
        qualifier = {'Port': match.group(1).decode()}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('IOControlStatus', value, qualifier)

    def SetIOFunction(self, value, qualifier):

        ValueStateValues = {
            'Input': 'INPUT',
            'Output': 'OUTPUT'
        }
        Port = qualifier['Port']
        if Port in {'1', '2', '3', '4'}:
            IOFunctionCmdString = 'NEUNIT={},SETTINGS=IO,IO={},FUNCTION={}\r'.format(self._UnitID, Port, ValueStateValues[value]).encode(encoding='iso-8859-1')
            self.__SetHelper('IOFunction', IOFunctionCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIOFunction')

    def UpdateIOFunction(self, value, qualifier):

        Port = qualifier['Port']
        if Port in {'1', '2', '3', '4'}:
            IOFunctionCmdString = 'NEUNIT={},SETTINGS=IO,IO={},FUNCTION=?\r'.format(self._UnitID, Port).encode(encoding='iso-8859-1')
            self.__UpdateHelper('IOFunction', IOFunctionCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateIOFunction')

    def __MatchIOFunction(self, match, tag):

        ValueStateValues = {
            b'INPUT': 'Input',
            b'OUTPUT': 'Output'
        }
        qualifier = {'Port': match.group(1).decode()}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('IOFunction', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }
        OutputMuteCmdString = 'NEUNIT={},MUTE={}\r'.format(self._UnitID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'NEUNIT={},MUTE=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            b'ON': 'On',
            b'OFF': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OutputMute', value, None)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 12
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = 'NEUNIT={},VOL={}\r'.format(self._UnitID, value).encode(encoding='iso-8859-1')
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = 'NEUNIT={},VOL=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        ValueConstraints = {
            'Min': -70,
            'Max': 12
        }
        value = int(match.group(1))
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.WriteStatus('OutputVolume', value, None)
        else:
            print('Output Volume: An invalid value was received')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }
        PowerCmdString = 'NEUNIT={},POWER={}\r'.format(self._UnitID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'NEUNIT={},POWER=?\r'.format(self._UnitID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'ON': 'On',
            b'OFF': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
            print(command, 'does not exist in the module')

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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        compileDict = self._compile_list.copy()
        for regexString in compileDict:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    compileDict[regexString]['callback'](result, compileDict[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
