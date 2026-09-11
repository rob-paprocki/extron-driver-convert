from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog



class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
        self.deviceUsername = 'admin'
        self.devicePassword = 'HDVC_admin'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoAnswer': { 'Status': {}},
            'Call': { 'Status': {}},
            'CameraPresetRecall': {'Parameters':['Target Site'], 'Status': {}},
            'CameraPresetSave': { 'Status': {}},
            'DialPad': { 'Status': {}},
            'Focus': {'Parameters':['Control Site','Mode'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MicMute': { 'Status': {}},
            'PanTilt': {'Parameters':['Target Site','Mode'], 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': {'Parameters':['Target Site','Mode'], 'Status': {}},
            }

        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'aspect = (0|1|2)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'incoming = (0|1)\r'), self.__MatchAutoAnswer, None)
            self.AddMatchString(re.compile(b'micmutemode = (0|1)\r'), self.__MatchMicMute, None)
            self.AddMatchString(re.compile(b'defaultvol = ([0-9]{1,2})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Login incorrect\r', re.I), self.__MatchFailedLogin, None)
            self.AddMatchString(re.compile(b'(invalid argument|command not found|permission denied|command not available)\r', re.I), self.__MatchError, None)
            
    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, tag):
        self.SetUsername( match, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
            self.Authenticated = True
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        self.SetPassword( match, None)
        
    def __MatchFailedLogin(self, value, qualifier):

        self.Authenticated = False
        self.Error(['Log in failed. Please supply proper Login Credentials.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'  : '2', 
            '16:9' : '1', 
            'Auto' : '0'
        }

        AspectRatioCmdString = 'aspect set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
            
        AspectRatioCmdString = 'aspect get\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '2' : '4:3', 
            '1' : '16:9', 
            '0' : 'Auto'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        AutoAnswerCmdString = 'incoming set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'incoming get\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetCall(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'button callstart\r', 
            'End'   : 'button callend\r'
        }

        CallCmdString = ValueStateValues[value]
        self.__SetHelper('Call', CallCmdString, value, qualifier)
        
    def SetCameraPresetRecall(self, value, qualifier):

        TargetSiteStates = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3'
        }

        target = qualifier['Target Site']
        if target in TargetSiteStates and 1 <= int(value) <= 9:
            CameraPresetRecallCmdString = 'camerapresetcall target {0} number {1}\r'.format(TargetSiteStates[target], value)
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')
            
    def SetCameraPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 9:
            CameraPresetSaveCmdString = 'camerapresetstore number {0}\r'.format(value)
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')
            
    def SetDialPad(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '0' : '0', 
            '*' : 'asterisk', 
            '#' : 'sharp'
        }

        DialPadCmdString = 'button {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DialPad', DialPadCmdString, value, qualifier)
        
    def SetFocus(self, value, qualifier):

        ControlSiteStates = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3'
        }

        ModeStates = {
            'Start'  : 'start', 
            'Stop'   : 'stop', 
            'Adjust' : 'adjust'
        }

        ValueStateValues = {
            'Near' : 'near', 
            'Far'  : 'far'
        }

        target = qualifier['Control Site']
        mode = qualifier['Mode']
        if target in ControlSiteStates and mode in ModeStates:
            FocusCmdString = 'camerafocuslevel target {0} mode {1} direction {2}\r'.format(ControlSiteStates[target], ModeStates[mode], ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
            
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'button menu\r', 
            'Enter' : 'button enter\r', 
            'Left'  : 'button left\r', 
            'Right' : 'button right\r', 
            'Up'    : 'button up\r', 
            'Down'  : 'button down\r', 
            'Home'  : 'button home\r', 
            'Back'  : 'button back\r',
            'Blue'  : 'button blue\r',
            'Red'   : 'button red\r',
            'Green' : 'button green\r',
            'Yellow': 'button yellow\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        
    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        MicMuteCmdString = 'micmutemode set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)

    def UpdateMicMute(self, value, qualifier):

        MicMuteCmdString = 'micmutemode get\r'
        self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)

    def __MatchMicMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MicMute', value, None)

    def SetPanTilt(self, value, qualifier):

        TargetSiteStates = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3'
        }

        ModeStates = {
            'Start'  : 'start', 
            'Stop'   : 'stop', 
            'Adjust' : 'adjust'
        }

        ValueStateValues = {
            'Up'    : 'up', 
            'Down'  : 'down', 
            'Left'  : 'left', 
            'Right' : 'right'
        }

        target = qualifier['Target Site']
        mode = qualifier['Mode']
        if target in TargetSiteStates and mode in ModeStates:
            PanTiltCmdString = 'cameramove target {0} mode {1} direction {2}\r'.format(TargetSiteStates[target], ModeStates[mode], ValueStateValues[value])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')
            
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'defaultvol set level {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'defaultvol get level\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        TargetSiteStates = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3'
        }

        ModeStates = {
            'Start'  : 'start', 
            'Stop'   : 'stop', 
            'Adjust' : 'adjust'
        }

        ValueStateValues = {
            'In'   : 'in', 
            'Out'  : 'out'
        }

        target = qualifier['Target Site']
        mode = qualifier['Mode']
        if target in TargetSiteStates and mode in ModeStates:
            ZoomCmdString = 'camerazoom target {0} mode {1} direction {2}\r'.format(TargetSiteStates[target], ModeStates[mode], ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
            
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.Authenticated:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.Send(commandstring)
            else:
                self.Error(['Authentication Failed'])

    def __MatchError(self, match, tag):

        ErrorCodes = {
            'invalid argument'      : 'Invalid Argument',      
            'command not found'     : 'Command not Found',    
            'permission denied'     : 'Permission Denied' ,   
            'command not available' : 'Command not Available'
            }

        self.Error([ErrorCodes[match.group(1).decode().lower()]])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

