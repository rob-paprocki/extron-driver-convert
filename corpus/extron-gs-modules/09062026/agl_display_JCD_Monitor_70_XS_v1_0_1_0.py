from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'BacklightBrightness': { 'Status': {}},
            'Input': { 'Status': {}},
            'KeyLock': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x01\x00\x41\x53\x50([\x01\x02\x04])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x4D\x55\x54([\x00\x01])\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x42\x4C\x43([\x00-\x01])\x08'), self.__MatchBacklight, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x42\x52\x49([\x00-\x64])\x08'), self.__MatchBacklightBrightness, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x4D\x49\x4E([\x00\x01\x09\x0D])\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x4B\x4C\x43([\x00\x01])\x08'), self.__MatchKeyLock, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x50\x4F\x57([\x00\x01])\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x56\x4F\x4C([\x00-\x64])\x08'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen' : '\x01',
            'Pillar Box'  : '\x02',
            'Auto'        : '\x04'
        }

        AspectRatioCmdString = '\x07\x01\x02\x41\x53\x50' + ValueStateValues[value] + '\x08'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x07\x01\x01\x41\x53\x50\x08'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01' : 'Full Screen',
            '\x02' : 'Pillar Box',
            '\x04' : 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x01',
            'Off' : '\x00'
        }

        AudioMuteCmdString = '\x07\x01\x02\x4D\x55\x54' + ValueStateValues[value] + '\x08'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x07\x01\x01\x4D\x55\x54\x08'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On',
            '\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x07\x01\x02\x41\x44\x4A\x00\x08'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'Off': '\x00',
            'On' : '\x01'
        }

        BacklightCmdString = '\x07\x01\x02\x42\x4C\x43' + ValueStateValues[value] + '\x08'
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = '\x07\x01\x01\x42\x4C\x43\x08'
        self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)

    def __MatchBacklight(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Backlight', value, None)

    def SetBacklightBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            BacklightBrightnessCmdString = '\x07\x01\x02\x42\x52\x49' + pack('>B', value).decode() + '\x08'
            self.__SetHelper('BacklightBrightness', BacklightBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightBrightness')

    def UpdateBacklightBrightness(self, value, qualifier):

        BacklightBrightnessCmdString = '\x07\x01\x01\x42\x52\x49\x08'
        self.__UpdateHelper('BacklightBrightness', BacklightBrightnessCmdString, value, qualifier)

    def __MatchBacklightBrightness(self, match, tag):

        value = unpack('>B', match.group(1))[0]
        self.WriteStatus('BacklightBrightness', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'         : '\x00',
            'Digital DVI' : '\x01',
            'HDMI'        : '\x09',
            'DisplayPort' : '\x0D'
        }

        InputCmdString = '\x07\x01\x02\x4D\x49\x4E' + ValueStateValues[value] + '\x08'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x07\x01\x01\x4D\x49\x4E\x08'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x00' : 'VGA',
            '\x01' : 'Digital DVI',
            '\x09' : 'HDMI',
            '\x0D' : 'DisplayPort'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeyLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x01',
            'Off' : '\x00'
        }

        KeyLockCmdString = '\x07\x01\x02\x4B\x4C\x43' + ValueStateValues[value] + '\x08'
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def UpdateKeyLock(self, value, qualifier):

        KeyLockCmdString = '\x07\x01\x01\x4B\x4C\x43\x08'
        self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def __MatchKeyLock(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On',
            '\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('KeyLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '\x00',
            'Up'    : '\x02',
            'Down'  : '\x03',
            'Left'  : '\x04',
            'Right' : '\x05',
            'Enter' : '\x06',
            'Exit'  : '\x07'
        }

        MenuNavigationCmdString = '\x07\x01\x02\x52\x43\x55' + ValueStateValues[value] + '\x08'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x01',
            'Off' : '\x00'
        }

        PowerCmdString = '\x07\x01\x02\x50\x4F\x57' + ValueStateValues[value] + '\x08'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '\x07\x01\x01\x50\x4F\x57\x08'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On',
            '\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x07\x01\x02\x56\x4F\x4C' + pack('>B', value).decode() + '\x08'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x07\x01\x01\x56\x4F\x4C\x08'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>B', match.group(1))[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}class SerialClass(SerialInterface, DeviceClass):

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

