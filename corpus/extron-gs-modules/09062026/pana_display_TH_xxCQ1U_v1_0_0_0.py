from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import hashlib
from binascii import hexlify

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
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {}



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogAirChannel': { 'Status': {}},
            'AnalogCableChannel': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},                                                                                                     
            'Backlight': { 'Status': {}},
            'ChannelTV': { 'Status': {}},
            'DigitalChannel': {'Parameters': ['Channel'], 'Status': {}},
            'Input': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }            


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(?P<value>FULL|NORM|NATV|ZOOM)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(?P<value>[01])\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QPC:BLT0(?P<value>[0-4][0-9]|50)\x03'), self.__MatchBacklight, None)
            self.AddMatchString(re.compile(b'\x02QMI:(?P<value>TV1|HM1|HM2|PC1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(?P<value>DYN|GRH|SPT|CNM|STD|CTM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:(?P<value>[01])\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QAV:(?P<value>0[0-9]{2}|100)\x03'), self.__MatchVolume, None)

        if 'Serial' not in self.ConnectionType:
            self.Delim = '\x0D'
            self.PasswdPromptCount = 0
            self.Authenticated = 'Needed'
            self.AddMatchString(re.compile(b'PDPCONTROL 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PDPCONTROL 0\r'), self.__MatchNoAuthentication, None)
            self.AddMatchString(re.compile(b'ERRA\r|Login incorrect'), self.__MatchFaliedPassword, None)
        else:
            self.Delim = ''
            self.Authenticated = 'Not Needed'
            self.AddMatchString(re.compile(b'ER401'), self.__MatchError, None)

    def __MatchNoAuthentication(self, match, tag):
        self.Authenticated = 'Not Needed'

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.SetAuthentication( None, None)
        self.Authenticated = 'Admin'

    def SetAuthentication(self, value, qualifier):
        cmdString = self.md5hash + '\x02QPW\x03\x0D'.encode()
        self.Send(cmdString)

    def __MatchFaliedPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper User name and Password'])
        self.Authenticated = 'None'

    def SetAnalogAirChannel(self, value, qualifier):

        temp = value
        if temp and 2 <= int(temp) <= 69:
            self.__SetHelper('AnalogAirChannel', '\x02STV:AGC0{}\x03{}'.format(temp.zfill(3), self.Delim), None, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAirChannelCommand')

    def SetAnalogCableChannel(self, value, qualifier):


        temp = value
        if temp and 1 <= int(temp) <= 135:
            self.__SetHelper('AnalogCableChannel', '\x02STV:AGC1{}\x03{}'.format(temp.zfill(3), self.Delim), None, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogCableChannelCommand')

    def SetAspectRatio(self, value, qualifier):


        ValueStateValues = {
            'Full'  : 'FULL',
            'Normal': 'NORM',
            'Native': 'NATV',
            'Zoom'  : 'ZOOM'
        }

        if value in ValueStateValues:
            self.__SetHelper('AspectRatio', '\x02DAM:{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):


        self.__UpdateHelper('AspectRatio', '\x02QAS\x03{}'.format(self.Delim), value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'NATV': 'Native',
            'ZOOM': 'Zoom'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('AudioMute', '\x02AMT:{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', '\x02QAM\x03{}'.format(self.Delim), value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBacklight(self, value, qualifier):

        if 0 <= value <= 50:
            self.__SetHelper('Backlight', '\x02VPC:BLT{}\x03{}'.format(str(value).zfill(3), self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        self.__UpdateHelper('Backlight', '\x02QPC:BLT\x03{}'.format(self.Delim), value, qualifier)

    def __MatchBacklight(self, match, tag):

        value = int(match.group('value').decode())
        self.WriteStatus('Backlight', value, None)

    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            'Up'  : 'UP',
            'Down': 'DN'
        }

        if value in ValueStateValues:
            self.__SetHelper('ChannelTV', '\x02STV:C{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelTV')

    def SetDigitalChannel(self, value, qualifier):

        ChannelStates = {
            'Air'  : '0',
            'Cable': '1'
        }

        channel = value.split('.')
        majorCh = channel[0]
        minorCh = channel[1]

        if majorCh and minorCh and 0 <= int(majorCh) <= 65535 and 1 <= int(minorCh) <= 9999 and qualifier['Channel'] in ChannelStates:
            self.__SetHelper('DigitalChannel', '\x02STV:DLC{}{}{}\x03{}'.format(ChannelStates[qualifier['Channel']], majorCh.zfill(5), minorCh.zfill(4), self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalChannelCommand')
    def SetInput(self, value, qualifier):


        ValueStateValues = {
            'TV'    : 'TV1',
            'HDMI 1': 'HM1',
            'HDMI 2': 'HM2',
            'PC'    : 'PC1',
            'USB'   : 'UD1'
        }

        if value in ValueStateValues:
            self.__SetHelper('Input', '\x02IMS:{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):


        self.__UpdateHelper('Input', '\x02QMI\x03{}'.format(self.Delim), value, qualifier)

    def __MatchInput(self, match, tag):


        ValueStateValues = {
            'TV1': 'TV',
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'PC1': 'PC',
            'UD1': 'USB'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('Input', value, None)

    def SetPictureMode(self, value, qualifier):


        ValueStateValues = {
            'Dynamic' : 'DYN', 
            'Graphic' : 'GRH', 
            'Sports'  : 'SPT',
            'Cinema'  : 'CNM',
            'Standard': 'STD',
            'Custom'  : 'CTM'
        }

        if value in ValueStateValues:
            self.__SetHelper('PictureMode', '\x02VPC:MEN{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):


        self.__UpdateHelper('PictureMode', '\x02QPC:MEN\x03{}'.format(self.Delim), value, qualifier)

    def __MatchPictureMode(self, match, tag):


        ValueStateValues = {
            'DYN': 'Dynamic',
            'GRH': 'Graphic',
            'SPT': 'Sports',
            'CNM': 'Cinema',
            'STD': 'Standard',
            'CTM': 'Custom'
        }

        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):


        ValueStateValues = {
            'On' : 'ON',
            'Off': 'OF'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', '\x02P{}\x03{}'.format(ValueStateValues[value], self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):



        self.__UpdateHelper('Power', '\x02QPW\x03{}'.format(self.Delim), value, qualifier)

    def __MatchPower(self, match, tag):


        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }


        value = ValueStateValues[match.group('value').decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):


        if 0 <= value <= 100:
            self.__SetHelper('Volume', '\x02AVL:{}\x03{}'.format(str(value).zfill(3), self.Delim), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):


        self.__UpdateHelper('Volume', '\x02QAV\x03{}'.format(self.Delim), value, qualifier)

    def __MatchVolume(self, match, tag):


        value = int(match.group('value').decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command')
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                self.Send(commandstring)
        else:
            self.Error(['Device not authenticated.'])

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Error occurred.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False        
        if 'Serial' not in self.ConnectionType:
            self.PasswdPromptCount = 0
            self.Authenticated = 'Needed'
        else:
            self.Authenticated = 'Not Needed'

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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

