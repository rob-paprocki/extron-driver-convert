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
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }
        
        if self.Unidirectional == 'False' and self._DeviceID != '00':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(0[1269]|2[01])x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK(0[01])x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK(0[01])x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(00|01|10|11|20|90|91|92)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9a-f]{2} OK(0[01])x'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK(0[01])x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK(01|00|10)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([cembladf]) ([0-9a-f]{2}) NG(.*)x'), self.__MatchError, None)

            self.setRegex = re.compile(b'(OK|NG)[0-9a-fA-F]{2}x')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Original': '06',
            'Just Scan': '09'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '06': 'Original',
            '09': 'Just Scan',
            '20': 'Vertical Zoom',
            '21': 'All-Direction Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ke {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '00': 'On',
            '01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '00',
            'Down': '01'
        }

        if value in ValueStateValues:
            ChannelCmdString = 'mc {} {}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'mc {} 39\r'.format(self._DeviceID)
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'km {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DTV': '00',
            'CADTV': '01',
            'ATV': '10',
            'CATV': '11',
            'AV': '20',
            'HDMI 1': '90',
            'HDMI 2': '91',
            'HDMI 3': '92'
        }

        if value in ValueStateValues:
            InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '00': 'DTV',
            '01': 'CADTV',
            '10': 'ATV',
            '11': 'CATV',
            '20': 'AV',
            '90': 'HDMI 1',
            '91': 'HDMI 2',
            '92': 'HDMI 3'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '-': '4C'
        }

        if value in ValueStateValues:
            KeypadCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = 'kl {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = 'kl {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            PowerCmdString = 'ka {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Off':              '00',
            'On':               '01',
            'On (With OSD)':    '10'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': 'On',
            '10': 'On (With OSD)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'NG' in response:
            self.Error(['An error occurred: {}.'.format(sourceCmdName)])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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

        CommandCode = {
            'c': 'Aspect Ratio/Channel/Closed Caption/Keypad/Menu Navigation',
            'e': 'Audio Mute',
            'm': 'Executive Mode',
            'b': 'Input',
            'l': 'On Screen Display',
            'a': 'Power',
            'd': 'Video Mute',
            'f': 'Volume'
        }

        errorstring = 'An error occurred: {0}: value {2} at display {1}.'.format(CommandCode[match.group(1).decode()], match.group(2).decode().upper(), match.group(3).decode())
        self.Error([errorstring])

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

