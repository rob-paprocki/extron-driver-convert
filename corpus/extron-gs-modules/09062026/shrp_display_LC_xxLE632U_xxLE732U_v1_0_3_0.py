from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
from re import compile, search

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
            'AspectRatio': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'ChannelTV': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'ChannelDTVAir': { 'Status': {}},
            'ChannelDTVCable2': { 'Status': {}},
            'ChannelDTVCable3': { 'Status': {}},
            'ChannelDTVCableMajor': { 'Status': {}},
            'ChannelDTVCableMinor': { 'Status': {}},
            'ChannelTV': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'enter password :'), self.__MatchPassword, None)

        self.RegexVal = compile(b'Login:|enter password :|\d+ *\r|ERR\r|OK\r')

    def __MatchUsername(self, match, tag):
         self.Authenticated = 'User'
         self.SetUsername( None, None)

    def __MatchPassword(self, match, tag):
         self.Authenticated = 'Admin'
         self.SetPassword( None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Side Bar (AV)'     :'WIDE1   \r',
            'S.Stretch (AV)'    :'WIDE2   \r',
            'Zoom (AV)'         :'WIDE3   \r',
            'Stretch (AV)'      :'WIDE4   \r',
            'Normal (PC)'       :'WIDE5   \r',
            'Zoom (PC)'         :'WIDE6   \r',
            'Stretch (PC)'      :'WIDE7   \r',
            'Dot by Dot (PC)'   :'WIDE8   \r',
            'Full Screen (AV)'  :'WIDE9   \r',
            'Auto'              :'WIDE10  \r',
            'Original'          :'WIDE11  \r',                                                                                             
        }

        if value in AspectRatioStateValues:
            AspectRatioCmdString = AspectRatioStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier): 

        AspectRatioStateNames = {
             '1 ':'Side Bar (AV)',
             '2 ':'S.Stretch (AV)',
             '3 ':'Zoom (AV)',
             '4 ':'Stretch (AV)',
             '5 ':'Normal (PC)',
             '6 ':'Zoom (PC)',
             '7 ':'Stretch (PC)',
             '8 ':'Dot by Dot (PC)',
             '9 ':'Full Screen (AV)',
             '10':'Auto',
             '11':'Original',                                                                                      
        }
            
        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value= AspectRatioStateNames[res[0:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        MuteStateValues = {
            'On' : 'MUTE1   \r',
            'Off': 'MUTE2   \r',
        }

        if value in MuteStateValues:
            MuteCmdString = MuteStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')
       
    def UpdateMute(self, value, qualifier): 

        MuteStateNames = {
            '2' : 'Off',
            '1' : 'On',
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteStateNames[res[0:1]] 
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetChannelDTVAir(self, value, qualifier):

        if 0 <= int(value) <= 9999:
            SetChannelDTVAirCmdString = 'DA2P{0:04d}\r'.format(int(value))
            self.__SetHelper('SetChannelDTVAir', SetChannelDTVAirCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelDTVAir')

    def SetChannelDTVCable2(self, value, qualifier):

        if 0 <= int(value) <= 9999:
            SetChannelDTVCable2CmdString = 'DC10{0:04d}\r'.format(int(value))
            self.__SetHelper('SetChannelDTVCable2', SetChannelDTVCable2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCable2')

    def SetChannelDTVCable3(self, value, qualifier):

        if 0 <= int(value) <= 6383:
            SetChannelDTVCable3CmdString = 'DC11{0:04d}\r'.format(int(value))
            self.__SetHelper('SetChannelDTVCable3', SetChannelDTVCable3CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCable3')

    def SetChannelDTVCableMajor(self, value, qualifier):

        if 0 <= int(value) <= 999:
            SetChannelDTVCableMajorCmdString = 'DC2U{0:03d} \r'.format(int(value))
            self.__SetHelper('SetChannelDTVCableMajor', SetChannelDTVCableMajorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCableMajor')

    def SetChannelDTVCableMinor(self, value, qualifier):

        if 0 <= int(value) <= 999:
            SetChannelDTVCableMinorCmdString = 'DC2L{0:03d} \r'.format(int(value))
            self.__SetHelper('SetChannelDTVCableMinor', SetChannelDTVCableMinorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCableMinor')

    def SetChannelTV(self, value, qualifier):

        if 0 <= int(value) <= 135:
            SetChannelTVCmdString = 'DCCH{0:03d} \r'.format(int(value))
            self.__SetHelper('SetChannelTV', SetChannelTVCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannelTV')

    def SetChannelStep(self, value, qualifier):

        ChannelStepStateValues = {
            'Up'  : 'CHUP1  \r',
            'Down': 'CHDW1  \r',
        }

        if value in ChannelStepStateValues:
            ChannelStepCmdString = ChannelStepStateValues[value]
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'TV'        :'ITVD0   \r', 
            'HDMI 1'    :'IAVD1   \r',
            'HDMI 2'    :'IAVD2   \r',
            'HDMI 3'    :'IAVD3   \r',
            'HDMI 4'    :'IAVD4   \r',
            'Component' :'IAVD5   \r',
            'Video 1'   :'IAVD6   \r',
            'Video 2'   :'IAVD7   \r',
        }

        if value in InputStateValues:
            InputCmdString = InputStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier): 

        InputStateNames = {
            '1':'HDMI 1',
            '2':'HDMI 2',
            '3':'HDMI 3',
            '4':'HDMI 4',
            '5':'Component',
            '6':'Video 1',
            '7':'Video 2',
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value= InputStateNames[res[0:1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On' :'POWR1   \r',
            'Off':'POWR0   \r',                         
        }

        if value in PowerStateValues:
            PowerCmdString = PowerStateValues[value]
            if value == 'On':
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
            elif 'Serial' in self.ConnectionType and value == 'Off':
                self.__SetHelper('Power', 'RSPW1   \r', value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
            else:
                self.__SetHelper('Power', 'RSPW2   \r', value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
           
    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',  
       }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)   
        if res:
            try:
                value = PowerStateNames[res[0:1]]  
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 60:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)    
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
                          
    def UpdateVolume(self, value, qualifier): 

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)  
        if res:
            try:   
                value = res[0:3]
                self.WriteStatus('Volume', int(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Login:' in response:
            self.Authenticated = 'User'
            self.SetUsername( None, None)
        elif 'enter password :' in response:
            self.Authenticated = 'Admin'
            self.SetPassword( None, None)
        elif 'ERR' in response:
            self.Authenticated = 'None'
            self.Error(['{0}: Communication error or incorrect command'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
  
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.RegexVal)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())
                
    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.RegexVal)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)
            return ''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'

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
                result = search(regexString, self.__receiveBuffer)
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