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
        self.deviceUsername = 'Username'
        self.devicePassword = '0000'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'HeadphoneVolume': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.Authenticated = False

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'#\*source is (HDMI1|HDMI2|VGA|DP|OPS)[\r\n]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(rb'#\*MUTE (ON|OFF)[\r\n]'), self.__MatchMute, None)
            self.AddMatchString(re.compile(rb'#\*Picture Mode is ([1-5])[\r\n]'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(rb'#\*Quick Standby is (off|on).?[\r\n]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(rb'#\*(headphone volume|volume) level is ([0-9]|[1-9][0-9]|100)[\r\n]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'User security level is not sufficient to run this command!'), self.__MatchPassword, None)  # see 'RE RS232 protocol for SUHD651-L.msg'

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto' 		: 'auto',
            '16:9' 	   	: '16:9',
            'Subtitle' 	: 'subtitle',
            '14:9' 		: '14:9',
            '14:9 Zoom': '14:9zoom',
            '4:3' 		: '4:3',
            'Full' 		: 'full',
            'Cinema' 	: 'cinema'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'PICTUREZOOM {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AUTOPOS\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetHeadphoneVolume(self, value, qualifier):

        if 0 <= value <= 100:
            HeadphoneVolumeCmdString = 'HEADPHONEVOLUME {}\r\n'.format(value)
            self.__SetHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHeadphoneVolume')

    def UpdateHeadphoneVolume(self, value, qualifier):

        HeadphoneVolumeCmdString = 'GETHEADPHONEVOLUME\r\n'
        self.__UpdateHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '7',
            'HDMI 2': '8',
            'DisplayPort': '19',
            'VGA': '12',
            'OPS': '20'
        }

        if value in ValueStateValues:
            InputCmdString = 'SELECTSOURCE {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GETSOURCE\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HDMI1': 'HDMI 1',
            'HDMI2': 'HDMI 2',
            'DP': 'DisplayPort',
            'VGA': 'VGA',
            'OPS': 'OPS'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMute(self, value, qualifier):

        MuteCmdString = 'SETMUTE\r\n'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'GETMUTE\r\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': '1',
            'Natural': '2',
            'Cinema': '3',
            'Game': '4',
            'Sport': '5'
        }

        if value in ValueStateValues:
            PictureModeCmdString = 'PICTUREMODE {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'GETPICTUREMODE\r\n'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '1': 'Dynamic',
            '2': 'Natural',
            '3': 'Cinema',
            '4': 'Game',
            '5': 'Sport'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'off',
            'Off': 'on'
        }

        if value in ValueStateValues:
            PowerCmdString = 'SETQUICKSTANDBY {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GETQUICKSTANDBY\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        self.Authenticated = True

        ValueStateValues = {
            'off': 'On',
            'on': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'STV {}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GETVOLUME\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(2).decode())
        if match.group(1).decode() == 'volume':
            self.WriteStatus('Volume', value, None)
        else:
            self.WriteStatus('HeadphoneVolume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):  # Added 2 seconds query delay based on Christie's timing recommendation
        self.Debug = True
        if not self.Authenticated:
            self.Send('SETUSERSECLEVEL ADMIN ' + self.devicePassword + '\r\n')
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
                
        if not self.Authenticated:
            self.Send('SETUSERSECLEVEL ADMIN ' + self.devicePassword + '\r\n')
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
        self.Authenticated = False
        
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

