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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Blank': { 'Status': {}},
            'ButtonandIRControl': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerSaving': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
                            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x77(000|002)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x67(000|001)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x43(000|001)\r'), self.__MatchButtonandIRControl, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6A(000|001|002|007|021|101|102)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x6C(000|001|002)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\xD9(000|001|002)\r'), self.__MatchPowerSaving, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r\x66([0-9]{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}\x2D[\x00-\xFF]{4}\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast': # Broadcast
            self._DeviceID = b'\x39\x39'
        elif 1 <= int(value) <= 98:
            self._DeviceID = bytes('{0:02d}'.format(int(value)), 'utf-8')

    def SetAspectRatio(self, value, qualifier):

        States = {
            '16:9'  : b'000', 
            'PTP'   : b'002'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x31' + States[value] + b'\r'
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\x77' + b'000\r'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '000' : '16:9', 
            '002' : 'PTP'
        }

        self.WriteStatus('AspectRatio',  States[match.group(1).decode()] , None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'    : b'001', 
            'Off'   : b'000'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x36' + States[value] + b'\r'
        self.__SetHelper('AudioMute', CmdString, value, qualifier)
        
    def UpdateAudioMute(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\x67' + b'000\r'
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '001' : 'On', 
            '000' : 'Off'
        }

        self.WriteStatus('AudioMute',  States[match.group(1).decode()] , None)

    def SetAutoImage(self, value, qualifier):

        CmdString = b'\x38' + self._DeviceID + b's\x8F' + b'000\r'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetBlank(self, value, qualifier):

        CmdString = b'\x38' + self._DeviceID + b's\x40' + b'031\r'
        self.__SetHelper('Blank', CmdString, value, qualifier)

    def SetButtonandIRControl(self, value, qualifier):

        States = {
            'On'    : b'001', 
            'Off'   : b'000'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x43' + States[value] + b'\r'
        self.__SetHelper('ButtonandIRControl', CmdString, value, qualifier)
    def UpdateButtonandIRControl(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\x43' + b'000\r'
        self.__UpdateHelper('ButtonandIRControl', CmdString, value, qualifier)

    def __MatchButtonandIRControl(self, match, tag):

        States = {
            '001' : 'On', 
            '000' : 'Off'
        }

        self.WriteStatus('ButtonandIRControl',  States[match.group(1).decode()] , None)

    def SetFreeze(self, value, qualifier):

        CmdString = b'\x38' + self._DeviceID + b's\x40' + b'032\r'
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'VGA'           : b'000', 
            'HDMI 1'        : b'001', 
            'HDMI 2'        : b'002', 
            'HDMI 3'        : b'021', 
            'DisplayPort'   : b'007', 
            'Android'       : b'101', 
            'OPS'           : b'102'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x22' + States[value] + b'\r'
        self.__SetHelper('Input', CmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\x6A' + b'000\r'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '000' : 'VGA', 
            '001' : 'HDMI 1', 
            '002' : 'HDMI 2', 
            '021' : 'HDMI 3', 
            '007' : 'DisplayPort', 
            '101' : 'Android', 
            '102' : 'OPS'
        }

        self.WriteStatus('Input',  States[match.group(1).decode()] , None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up'        : b'010', 
            'Down'      : b'011', 
            'Left'      : b'012', 
            'Right'     : b'013', 
            'OK'        : b'014', 
            'Menu'      : b'020', 
            'Exit'      : b'022'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x40' + States[value] + b'\r'
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On'    : b'001', 
            'Off'   : b'002'
        }

        CmdString = b'\x38' + self._DeviceID + b's\x21' + States[value] + b'\r'
        self.__SetHelper('Power', CmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        CmdString = b'\x38' + self._DeviceID + b'g\x6C' + b'000\r'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '001' : 'On', 
            '002' : 'Off',
            '000' : 'Off',
        }

        self.WriteStatus('Power',  States[match.group(1).decode()] , None)

    def SetPowerSaving(self, value, qualifier):

        States = {
            'Off'   : b'000', 
            'Low'   : b'001', 
            'High'  : b'002'
        }

        CmdString = b'\x38' + self._DeviceID + b's\xA9' + States[value] + b'\r'
        self.__SetHelper('PowerSaving', CmdString, value, qualifier)
    def UpdatePowerSaving(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\xD9' + b'000\r'
        self.__UpdateHelper('PowerSaving', CmdString, value, qualifier)

    def __MatchPowerSaving(self, match, tag):

        States = {
            '000' : 'Off', 
            '001' : 'Low', 
            '002' : 'High'
        }

        self.WriteStatus('PowerSaving',  States[match.group(1).decode()] , None)

    def SetVolume(self, value, qualifier):


        if 0 <= value <= 100:
            CmdString = b'\x38' + self._DeviceID + b's\x35' + str(value).zfill(3).encode() + b'\r'
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):
        CmdString = b'\x38' + self._DeviceID + b'g\x66' + b'000\r'
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume',  int(match.group(1).decode()) , None)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x39\x39':
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
        self.Error(['Invalid command condition.'])

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
            raise AttributeError(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)
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

