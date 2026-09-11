from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self._DeviceID = '015'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Gain': {'Parameters': ['Type', 'Channel'], 'Status': {}},
            'MixerGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MixerMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Mute': {'Parameters': ['Type', 'Channel'], 'Status': {}},
            'Preset': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xD0DFR22(?:\d{3})(INP|OUT)(00[12])L00([\x00-\x7F])\xD1'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'\xD0DFR22(?:\d{3})MIX(00[12])(00[12]|OUT)L00([\x00-\x7F])\xD1'), self.__MatchMixerGain, None)
            self.AddMatchString(re.compile(b'\xD0DFR22(?:\d{3})MIX(00[12])(00[12]|OUT)M00([01])\xD1'), self.__MatchMixerMute, None)
            self.AddMatchString(re.compile(b'\xD0DFR22(?:\d{3})(INP|OUT)(00[12])M00([01])\xD1'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\xD0DFR22(?:\d{3})PRE(\d{3})\xD1'), self.__MatchPreset, None)
            
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 15:
            self._DeviceID = value.zfill(3)
        else:
            self.Error(['Invalid Device ID Parameter. Range is 0 to 15'])

    def SetGain(self, value, qualifier):

        typeVal = {
            'Input':    'INP',
            'Output':   'OUT'
        }[qualifier['Type']]

        channelVal = {
            '1': '001',
            '2': '002'
        }[qualifier['Channel']]

        if 0 <= value <= 127:
            GainCmdString = '\xD0DFR22{id}{type}{ch}L00{val:c}\xD1'.format(id=self._DeviceID,
                                                                           type=typeVal.upper()[:3],
                                                                           ch=channelVal,
                                                                           val=value).encode(encoding='iso-8859-1')
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def __MatchGain(self, match, tag):

        typeVal = {
            'INP': 'Input',
            'OUT': 'Output'
        }[match.group(1).decode()]

        channelVal = str(int(match.group(2).decode()))

        qualifier = {
            'Type':     typeVal,
            'Channel':  channelVal
        }

        value = ord(match.group(3).decode())
        self.WriteStatus('Gain', value, qualifier)

    def SetMixerGain(self, value, qualifier):

        
        inputVal = {
            '1':            '001',
            '2':            '002',
            'Output Fader': 'OUT'
        }[qualifier['Input']]

        outputVal = {
            '1': '001',
            '2': '002'
        }[qualifier['Output']]

        if 0 <= value <= 127:
            MixerGainCmdString = '\xD0DFR22{id}MIX{output}{input}L00{val:c}\xD1'.format(id=self._DeviceID,
                                                                                        output=outputVal,
                                                                                        input=inputVal,
                                                                                        val=value).encode(encoding='iso-8859-1')
            self.__SetHelper('MixerGain', MixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerGain')

    def __MatchMixerGain(self, match, tag):

        inputVal = {
            '001': '1',
            '002': '2',
            'OUT': 'Output Fader'
        }[match.group(2).decode()]

        outputVal = str(int(match.group(1).decode()))

        qualifier = {
            'Input':    inputVal,
            'Output':   outputVal
        }

        value = ord(match.group(3).decode())
        self.WriteStatus('MixerGain', value, qualifier)

    def SetMixerMute(self, value, qualifier):

        
        inputVal = {
            '1':            '001',
            '2':            '002',
            'Output Fader': 'OUT'
        }[qualifier['Input']]

        outputVal = {
            '1': '001',
            '2': '002'
        }[qualifier['Output']]

        state = {
            'On':   '1',
            'Off':  '0'
        }[value]

        MixerMuteCmdString = '\xD0DFR22{id}MIX{output}{input}M00{val}\xD1'.format(id=self._DeviceID,
                                                                                  output=outputVal,
                                                                                  input=inputVal,
                                                                                  val=state).encode(encoding='iso-8859-1')
        self.__SetHelper('MixerMute', MixerMuteCmdString, value, qualifier)

    def __MatchMixerMute(self, match, tag):

        inputVal = {
            '001': '1',
            '002': '2',
            'OUT': 'Output Fader'
        }[match.group(2).decode()]

        outputVal = str(int(match.group(1).decode()))

        qualifier = {
            'Input':    inputVal,
            'Output':   outputVal
        }

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(3).decode()]

        self.WriteStatus('MixerMute', value, qualifier)

    def SetMute(self, value, qualifier):

        typeVal = {
            'Input':    'INP',
            'Output':   'OUT'
        }[qualifier['Type']]

        channelVal = {
            '1': '001',
            '2': '002'
        }[qualifier['Channel']]

        state = {
            'On':   '1',
            'Off':  '0'
        }[value]

        MuteCmdString = '\xD0DFR22{id}{type}{ch}M00{val}\xD1'.format(id=self._DeviceID,
                                                                     type=typeVal,
                                                                     ch=channelVal,
                                                                     val=state).encode(encoding='iso-8859-1')
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        typeVal = {
            'INP': 'Input',
            'OUT': 'Output'
        }[match.group(1).decode()]

        channelVal = str(int(match.group(2).decode()))

        qualifier = {
            'Type':     typeVal,
            'Channel':  channelVal
        }

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(3).decode()]

        self.WriteStatus('Mute', value, qualifier)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetCmdString = '\xD0DFR22{id}PRE{val:03d}\xD1'.format(id=self._DeviceID,
                                                                     val=int(value)).encode(encoding='iso-8859-1')
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '\xD0DFR22{}QRY\xD1'.format(self._DeviceID).encode(encoding='iso-8859-1')
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):


        value = str(int(match.group(1).decode()))
        self.WriteStatus('Preset', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

