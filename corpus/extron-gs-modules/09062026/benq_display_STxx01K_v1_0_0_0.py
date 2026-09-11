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
        self._DeviceID = b'\x30\x31'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Type'], 'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }     

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x77\x30\x30([0-3])\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x67\x30\x30([01])\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72([\x73\x68\x69])\x30\x30([01])\x0D'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x6A([01]0[01267])\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\xB1\x30\x30([0-3])\x0D'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x6C\x30\x30([0-2])\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x66([01][0-9]{2})\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x34[\x30-\x39]{2}\x2D\x0D'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 'Serial' in self.ConnectionType:
            if value == 'Broadcast':
                self._DeviceID = b'\x39\x39'
            elif 1 <= int(value) <= 98:
                self._DeviceID = bytes('{0:02d}'.format(int(value)),'utf-8')
            else:
                self.Error(['Invalid DeviceID. Range is from 1 to 98 or Broadcast'])
        else:
            self.Error(['Ethernet protocol does not allow for any other ID value than 1'])


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x30',
            '4:3': b'\x31',
            '1:1': b'\x32',
            '16:9': b'\x33'
        }

        AspectRatioCmdString = b'\x38' + self._DeviceID + b'\x73\x31\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x38' + self._DeviceID + b'\x67\x77\x30\x30\x30\x0D'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'0': 'Full',
            b'1': '4:3',
            b'2': '1:1',
            b'3': '16:9'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        AudioMuteCmdString = b'\x38' + self._DeviceID + b'\x73\x36\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x38' + self._DeviceID + b'\x67\x67\x30\x30\x30\x0D'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x38' + self._DeviceID + b'\x73\x8F\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Button': b'\x45',
            'IR': b'\x42',
            'Button and IR': b'\x43'
        }

        ValueStateValues = {
            'On': b'\x30',
            'Off': b'\x31'
        }

        ExecutiveModeCmdString = b'\x38' + self._DeviceID + b'\x73' + TypeStates[qualifier['Type']] + b'\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Button': b'\x73',
            'IR': b'\x68',
            'Button and IR': b'\x69'
        }

        ExecutiveModeCmdString = b'\x38' + self._DeviceID + b'\x67' + TypeStates[qualifier['Type']] + b'\x30\x30\x30\x0D'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        TypeStates = {
            b'\x73': 'Button',
            b'\x68': 'IR',
            b'\x69': 'Button and IR'
        }

        ValueStateValues = {
            b'0': 'On',
            b'1': 'Off'
        }

        qualifier = {'Type': TypeStates[match.group(1)]}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x30\x30\x30',
            'HDMI 1': b'\x30\x30\x31',
            'HDMI 2': b'\x30\x30\x32',
            'DVI-D': b'\x30\x30\x36',
            'DisplayPort': b'\x30\x30\x37',
            'Android': b'\x31\x30\x31'
        }

        InputCmdString = b'\x38' + self._DeviceID + b'\x73\x22' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x38' + self._DeviceID + b'\x67\x6A\x30\x30\x30\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'000': 'VGA',
            b'001': 'HDMI 1',
            b'002': 'HDMI 2',
            b'006': 'DVI-D',
            b'007': 'DisplayPort',
            b'101': 'Android'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x30\x31\x30',
            'Down': b'\x30\x31\x31',
            'Left': b'\x30\x31\x32',
            'Right': b'\x30\x31\x33',
            'Ok': b'\x30\x31\x34',
            'Menu': b'\x30\x32\x30',
            'Exit': b'\x30\x32\x32'
        }

        MenuNavigationCmdString = b'\x38' + self._DeviceID + b'\x73\x40' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x30\x30\x30',
            'Bright': b'\x30\x30\x31',
            'Soft': b'\x30\x30\x32',
            'Custom': b'\x30\x30\x33'
        }

        PictureModeCmdString = b'\x38' + self._DeviceID + b'\x73\x81' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x38' + self._DeviceID + b'\x67\xB1\x30\x30\x30\x0D'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            b'0': 'Standard',
            b'1': 'Bright',
            b'2': 'Soft',
            b'3': 'Custom'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30',
            'Android Off': b'\x32'
        }

        PowerCmdString = b'\x38' + self._DeviceID + b'\x73\x21\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x38' + self._DeviceID + b'\x67\x6C\x30\x30\x30\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'Android Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            byteValue = bytes('{0:03d}'.format(value), 'utf-8')
            VolumeCmdString = b'\x38' + self._DeviceID + b'\x73\x35' + byteValue + b'\x0D'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x38' + self._DeviceID + b'\x67\x66\x30\x30\x30\x0D'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
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

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Invalid Command'])

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
        
        # check incoming data if it matched any expected data from device module
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

