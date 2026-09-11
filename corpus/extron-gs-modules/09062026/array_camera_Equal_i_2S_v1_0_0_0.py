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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.devicePassword = 'ATEquali'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BackEndOperatingMode': { 'Status': {}},
            'BalanceBoxPosition': { 'Status': {}},
            'ColorGain': {'Parameters':['Camera'], 'Status': {}},
            'FrontEndOperatingMode': { 'Status': {}},
            'Gamma': { 'Status': {}},
            'IntegrationTime': {'Parameters':['Camera'], 'Status': {}},
            'Pan': {'Parameters':['Camera','Direction'], 'Status': {}},
            'Power': { 'Status': {}},
            'SensorGain': {'Parameters':['Camera'], 'Status': {}},
            'WhiteBalanceBoxes': { 'Status': {}},
            }
                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OPMODEBE=([1-3])\r'), self.__MatchBackEndOperatingMode, None)
            self.AddMatchString(re.compile(b'BALBOXPOS=(\d+)\r'), self.__MatchBalanceBoxPosition, None)
            self.AddMatchString(re.compile(b'COLGAIN=(\d+),(R|L)\r'), self.__MatchColorGain, None)
            self.AddMatchString(re.compile(b'OPMODEFE=(\d+)\r'), self.__MatchFrontEndOperatingMode, None)
            self.AddMatchString(re.compile(b'GAMMA=([1-6])\r'), self.__MatchGamma, None)
            self.AddMatchString(re.compile(b'INTTIME=(\d+),(R|L)\r'), self.__MatchIntegrationTime, None)
            self.AddMatchString(re.compile(b'(HOR|VERT)PAN=(\d+),(R|L)\r'), self.__MatchPan, None)
            self.AddMatchString(re.compile(b'SLEEP=([01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SENSGAIN=([1-4]),(R|L)\r'), self.__MatchSensorGain, None)
            self.AddMatchString(re.compile(b'BALBOXES=([01])\r'), self.__MatchWhiteBalanceBoxes, None)
            self.AddMatchString(re.compile(b'ERR(.*)\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'password',re.I), self.__MatchPassword, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword( None, None)

    def SetBackEndOperatingMode(self, value, qualifier):

        ValueStateValues = {
            'Passthrough'               : '1', 
            'Immersive Mode Receive'    : '2', 
            'Immersive PTZ'             : '3'
        }

        BackEndOperatingModeCmdString = ':OPMODEBE={}\r'.format(ValueStateValues[value])
        self.__SetHelper('BackEndOperatingMode', BackEndOperatingModeCmdString, value, qualifier)

    def UpdateBackEndOperatingMode(self, value, qualifier):

        BackEndOperatingModeCmdString = ':OPMODEBE?\r'
        self.__UpdateHelper('BackEndOperatingMode', BackEndOperatingModeCmdString, value, qualifier)

    def __MatchBackEndOperatingMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Passthrough', 
            '2' : 'Immersive Mode Receive', 
            '3' : 'Immersive PTZ'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BackEndOperatingMode', value, None)

    def SetBalanceBoxPosition(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BalanceBoxPositionCmdString = ':BALBOXPOS={}\r'.format(value)
            self.__SetHelper('BalanceBoxPosition', BalanceBoxPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBalanceBoxPosition')

    def UpdateBalanceBoxPosition(self, value, qualifier):

        BalanceBoxPositionCmdString = ':BALBOXPOS?\r'
        self.__UpdateHelper('BalanceBoxPosition', BalanceBoxPositionCmdString, value, qualifier)

    def __MatchBalanceBoxPosition(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BalanceBoxPosition', value, None)

    def SetColorGain(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }

        if 0 <= value <= 65535:
            ColorGainCmdString = ':COLGAIN={},{}\r'.format(value,CameraStates[qualifier['Camera']])
            self.__SetHelper('ColorGain', ColorGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorGain')

    def UpdateColorGain(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }
        ColorGainCmdString = ':COLGAIN?{}\r'.format(CameraStates[qualifier['Camera']])
        self.__UpdateHelper('ColorGain', ColorGainCmdString, value, qualifier)

    def __MatchColorGain(self, match, tag):

        CameraStates = {
            'L' : 'Left', 
            'R' : 'Right'
        }

        qualifier = {}
        qualifier['Camera'] = CameraStates[match.group(2).decode()]
        value = int(match.group(1).decode())
        self.WriteStatus('ColorGain', value, qualifier)

    def SetFrontEndOperatingMode(self, value, qualifier):

        ValueStateValues = {
            'Immersive Mode'        : '1', 
            'Video+Content'         : '2', 
            'Stack'                 : '3', 
            'Immersive Everywhere'  : '4'
        }

        FrontEndOperatingModeCmdString = ':OPMODEFE={}\r'.format(ValueStateValues[value])
        self.__SetHelper('FrontEndOperatingMode', FrontEndOperatingModeCmdString, value, qualifier)

    def UpdateFrontEndOperatingMode(self, value, qualifier):

        FrontEndOperatingModeCmdString = ':OPMODEFE?\r'
        self.__UpdateHelper('FrontEndOperatingMode', FrontEndOperatingModeCmdString, value, qualifier)

    def __MatchFrontEndOperatingMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Immersive Mode', 
            '2' : 'Video+Content', 
            '3' : 'Stack', 
            '4' : 'Immersive Everywhere'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FrontEndOperatingMode', value, None)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6'
        }

        GammaCmdString = ':GAMMA={}\r'.format(ValueStateValues[value])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        GammaCmdString = ':GAMMA?\r'
        self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)

    def __MatchGamma(self, match, tag):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Gamma', value, None)

    def SetIntegrationTime(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }

        if 1 <= value <= 1640:
            IntegrationTimeCmdString = ':INTTIME={},{}\r'.format(value,CameraStates[qualifier['Camera']])
            self.__SetHelper('IntegrationTime', IntegrationTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIntegrationTime')

    def UpdateIntegrationTime(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }

        IntegrationTimeCmdString = ':INTTIME?{}\r'.format(CameraStates[qualifier['Camera']])
        self.__UpdateHelper('IntegrationTime', IntegrationTimeCmdString, value, qualifier)

    def __MatchIntegrationTime(self, match, tag):

        CameraStates = {
            'L' : 'Left', 
            'R' : 'Right'
        }

        qualifier = {}
        qualifier['Camera'] = CameraStates[match.group(2).decode()]
        value = int(match.group(1).decode())
        self.WriteStatus('IntegrationTime', value, qualifier)

    def SetPan(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }

        DirectionStates = {
            'Horizontal' : 'HOR', 
            'Vertical' : 'VERT'
        }

        if 1 <= value <= 1000:
            PanCmdString = ':{}PAN={},{}\r'.format(DirectionStates[qualifier['Direction']],value,CameraStates[qualifier['Camera']])
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def UpdatePan(self, value, qualifier):

        CameraStates = {
            'Left'  : 'L', 
            'Right' : 'R'
        }

        DirectionStates = {
            'Horizontal' : 'HOR', 
            'Vertical' : 'VERT'
        }

        PanCmdString = ':{}PAN?{}\r'.format(DirectionStates[qualifier['Direction']],CameraStates[qualifier['Camera']])
        self.__UpdateHelper('Pan', PanCmdString, value, qualifier)

    def __MatchPan(self, match, tag):

        CameraStates = {
            'L' : 'Left', 
            'R' : 'Right'
        }

        DirectionStates = {
            'HOR'  : 'Horizontal', 
            'VERT' : 'Vertical'
        }

        qualifier = {}
        qualifier['Camera'] = CameraStates[match.group(3).decode()]
        qualifier['Direction'] = DirectionStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('Pan', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '0', 
            'Off' : '1'
        }

        PowerCmdString = ':SLEEP={}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = ':SLEEP?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSensorGain(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }

        ValueStateValues = {
            'x1' : '1', 
            'x2' : '2', 
            'x4' : '3', 
            'x8' : '4'
        }
        SensorGainCmdString = ':SENSGAIN={},{}\r'.format(ValueStateValues[value],CameraStates[qualifier['Camera']])
        self.__SetHelper('SensorGain', SensorGainCmdString, value, qualifier)

    def UpdateSensorGain(self, value, qualifier):

        CameraStates = {
            'Left' : 'L', 
            'Right' : 'R'
        }
        SensorGainCmdString = ':SENSGAIN?{}\r'.format(CameraStates[qualifier['Camera']])
        self.__UpdateHelper('SensorGain', SensorGainCmdString, value, qualifier)

    def __MatchSensorGain(self, match, tag):

        CameraStates = {
            'L' : 'Left', 
            'R' : 'Right'
        }

        ValueStateValues = {
            '1' : 'x1', 
            '2' : 'x2', 
            '3' : 'x4', 
            '4' : 'x8'
        }

        qualifier = {}
        qualifier['Camera'] = CameraStates[match.group(2).decode()]
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SensorGain', value, qualifier)

    def SetWhiteBalanceBoxes(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        WhiteBalanceBoxesCmdString = ':BALBOXES={}\r'.format(ValueStateValues[value])
        self.__SetHelper('WhiteBalanceBoxes', WhiteBalanceBoxesCmdString, value, qualifier)

    def UpdateWhiteBalanceBoxes(self, value, qualifier):

        WhiteBalanceBoxesCmdString = ':BALBOXES?\r'
        self.__UpdateHelper('WhiteBalanceBoxes', WhiteBalanceBoxesCmdString, value, qualifier)

    def __MatchWhiteBalanceBoxes(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WhiteBalanceBoxes', value, None)

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

        value = 'Error occurred {}'.format(match.group(1).decode())
        self.Error([value])

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
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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

