from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ATVChannelAirCommand': {'Status': {}},
            'ATVChannelCableCommand': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AVMode': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'DTVChannelAirCommand': {'Status': {}},
            'DTVChannelCableCommand': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'Login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchLogin(self, match, tag):
        self.Send(self.deviceUsername + '\r')

    def __MatchPassword(self, match, tag):
        self.Send(self.devicePassword + '\r')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide': '1',
            'Normal': '2',
            'Dot by Dot': '3',
            'Zoom': '4'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'WIDE{:>4}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            1: 'Wide',
            2: 'Normal',
            3: 'Dot by Dot',
            4: 'Zoom'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetATVChannelAirCommand(self, value, qualifier):

        chnl = value
        if chnl and 2 <= int(chnl) <= 69:
            ATVChannelAirCommandCmdString = 'ATDC0{}\r'.format(chnl.zfill(3))
            self.__SetHelper('ATVChannelAirCommand', ATVChannelAirCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATVChannelAirCommand')

    def SetATVChannelCableCommand(self, value, qualifier):

        chnl = value
        if chnl and 1 <= int(chnl) <= 135:
            ATVChannelCableCommandCmdString = 'ATDC1{}\r'.format(chnl.zfill(3))
            self.__SetHelper('ATVChannelCableCommand', ATVChannelCableCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATVChannelCableCommand')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'MUTE{:>4}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Dynamic': '2',
            'PC': '5',
            'Movie': '6',
            'Game': '7',
            'Custom': '8'
        }

        if value in ValueStateValues:
            AVModeCmdString = 'BMOD{:>4}\r'.format(ValueStateValues[value])
            self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMode')

    def UpdateAVMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Standard',
            2: 'Dynamic',
            5: 'PC',
            6: 'Movie',
            7: 'Game',
            8: 'Custom'
        }

        AVModeCmdString = 'BMOD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['AV Mode: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP   0\r',
            'Down': 'CHDW   0\r'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = ValueStateValues[value]
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetDTVChannelAirCommand(self, value, qualifier):

        major = value.split('.')[0]
        minor = value.split('.')[1]
        if major and 1 <= int(major) <= 65535 and minor and 0 <= int(minor) <= 9999:
            DTVChannelAirCommandCmdString = 'DTDC0{}{}\r'.format(major.zfill(5), minor.zfill(4))
            self.__SetHelper('DTVChannelAirCommand', DTVChannelAirCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelAirCommand')

    def SetDTVChannelCableCommand(self, value, qualifier):

        major = value.split('.')[0]
        minor = value.split('.')[1]
        if major and 0 <= int(major) <= 65535 and minor and 0 <= int(minor) <= 9999:
            DTVChannelCableCommandCmdString = 'DTDC1{}{}\r'.format(major.zfill(5), minor.zfill(4))
            self.__SetHelper('DTVChannelCableCommand', DTVChannelCableCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelCableCommand')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'D-Sub': '2',
            'HDMI 1': '10',
            'HDMI 2': '13',
            'USB': '11',
            'TV': '25'
        }

        if value in ValueStateValues:
            InputCmdString = 'INPS{:>4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            2: 'D-Sub',
            10: 'HDMI 1',
            13: 'HDMI 2',
            11: 'USB',
            25: 'TV'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerCmdString = 'POWR{:>4}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'VOLM{:>4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Login' in response:
            self.__MatchLogin(None, None)
            response = ''
        elif 'Password' in response:
            self.__MatchPassword(None, None)
            response = ''
        elif 'ERR' in response:
            self.Error(['{}: Error occurred.'.format(sourceCmdName)])
            response = ''
        elif 'WAIT' in response:
            self.Error(['{0}: Waiting for response.'.format(sourceCmdName)])
        elif 'LOCKED' in response:
            self.Error(['{0}: Control via LAN is locked.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0} Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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