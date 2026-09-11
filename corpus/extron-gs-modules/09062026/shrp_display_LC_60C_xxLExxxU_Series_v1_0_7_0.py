from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
from re import compile, search

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
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},   
            'AudioMute': { 'Status': {}}, 
            'AudioInput': { 'Status': {}}, 
            'ClosedCaption': { 'Status': {}}, 
            'ChannelDTVAirDiscrete': { 'Status': {}}, 
            'ChannelDTVAirStatus': { 'Status': {}}, 
            'ChannelDTVCable2Discrete': { 'Status': {}},
            'ChannelDTVCable2Status': { 'Status': {}}, 
            'ChannelDTVCable3Discrete': { 'Status': {}},
            'ChannelDTVCable3Status': { 'Status': {}}, 
            'ChannelDTVCableMajorDiscrete': { 'Status': {}},
            'ChannelDTVCableMajorStatus': { 'Status': {}}, 
            'ChannelDTVCableMinorDiscrete': { 'Status': {}},
            'ChannelDTVCableMinorStatus': { 'Status': {}},        
            'ChannelTVDiscrete': { 'Status': {}},   
            'ChannelTVStatus': { 'Status': {}}, 
            'ChannelStep': { 'Status': {}}, 
            'Freeze': { 'Status': {}}, 
            'Input': { 'Status': {}},  
            'MenuNavigation': { 'Status': {}},  
            'Power': { 'Status': {}},   
            'SetChannelDTVAirDiscrete': { 'Status': {}}, 
            'SetChannelDTVCable2Discrete': { 'Status': {}},  
            'SetChannelDTVCable3Discrete': { 'Status': {}},       
            'SetChannelDTVCableMajorDiscrete': { 'Status': {}},
            'SetChannelDTVCableMinorDiscrete': { 'Status': {}}, 
            'SetChannelTVDiscrete': { 'Status': {}},   
            'Volume': { 'Status': {}}, 
            }
        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'enter password :'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
         self.SetUsername( None, None)

    def __MatchPassword(self, match, tag):
         self.SetPassword( None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Side Bar' 		  :'WIDE1   \x0D',
            'S.Stretch'		  :'WIDE2   \x0D',
            'Zoom [AV]'		  :'WIDE3   \x0D',
            'Stretch [AV]'    :'WIDE4   \x0D',
            'Normal [PC]'	  :'WIDE5   \x0D',
            'Zoom [PC]'		  :'WIDE6   \x0D',
            'Stretch [PC]'	  :'WIDE7   \x0D',
            'Dot by Dot [PC]' :'WIDE8   \x0D',
            'Full Screen [AV]':'WIDE9   \x0D',
            'Auto'			  :'WIDE10  \x0D',
            'Original'		  :'WIDE11  \x0D',      
                                                                                             
            }

        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):     

        AspectRatioStateNames = {
             '1 ':'Side Bar',
             '2 ':'S.Stretch',
             '3 ':'Zoom [AV]',
             '4 ':'Stretch [AV]',
             '5 ':'Normal [PC]',
             '6 ':'Zoom [PC]',
             '7 ':'Stretch [PC]',
             '8 ':'Dot by Dot [PC]',
             '9 ':'Full Screen [AV]',
             '10':'Auto',
             '11':'Original',                                                                                      
            }                                                                   
            
        AspectRatioCmdString = 'WIDE????\x0D'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)  

        if res:
            try:
                value= AspectRatioStateNames[res[0:2]]
                self.WriteStatus('AspectRatio', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for AspectRatio'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On' : 'MUTE1   \x0D',
            'Off': 'MUTE2   \x0D',
            }
        AudioMuteCmdString = AudioMuteStateValues[value] 
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)  
       
    def UpdateAudioMute(self, value, qualifier): 
    
        AudioMuteStateNames = {
            '2' : 'Off',
            '1' : 'On',
        }  

        AudioMuteCmdString = 'MUTE????\x0D'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)  

        if res:
            try:
                value = AudioMuteStateNames[res[0:1]] 
                self.WriteStatus('AudioMute', value, qualifier)  
            except  (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for AudioMute'])

    def SetAudioInput(self, value, qualifier):
        
        AudioInputCmdString = 'ACHA0   \x0D'
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)  

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \x0D'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)      
        
    def UpdateChannelDTVAirStatus(self, value, qualifier):
             
        ChannelDTVAirStatusCmdString = 'DA2P????\x0D'
        res = self.__UpdateHelper('ChannelDTVAirStatus', ChannelDTVAirStatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelDTVAirStatus', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelDTVAirStatus'])   
        
    def UpdateChannelDTVCable2Status(self, value, qualifier):
             
        ChannelDTVCable2StatusCmdString = 'DC10????\x0D'
        res = self.__UpdateHelper('ChannelDTVCable2Status', ChannelDTVCable2StatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelDTVCable2Status', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelDTVCable2Status'])   
        
    def UpdateChannelDTVCable3Status(self, value, qualifier):
             
        ChannelDTVCable3StatusCmdString = 'DC11????\x0D'
        res = self.__UpdateHelper('ChannelDTVCable3Status', ChannelDTVCable3StatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelDTVCable3Status', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelDTVCable3Status'])
        
    def UpdateChannelTVStatus(self, value, qualifier):
             
        ChannelTVStatusCmdString = 'DCCH????\x0D'
        res = self.__UpdateHelper('ChannelTVStatus', ChannelTVStatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelTVStatus', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelTVStatus'])   
         
    def UpdateChannelDTVCableMajorStatus(self, value, qualifier):
             
        ChannelDTVCableMajorStatusCmdString = 'DC2U????\x0D'
        res = self.__UpdateHelper('ChannelDTVCableMajorStatus', ChannelDTVCableMajorStatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelDTVCableMajorStatus', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelDTVCableMajorStatus'])   
        
    def UpdateChannelDTVCableMinorStatus(self, value, qualifier):
             
        ChannelDTVCableMinorStatusCmdString = 'DC2L????\x0D'
        res = self.__UpdateHelper('ChannelDTVCableMinorStatus', ChannelDTVCableMinorStatusCmdString, value, qualifier)   
        if res:
            try:
                self.WriteStatus('ChannelDTVCableMinorStatus', str(int(res)), qualifier)
            except(KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for ChannelDTVCableMinorStatus'])

    def SetChannelStep(self, value, qualifier):

        ChannelStepStateValues = {
            'Up'  : 'RCKY34  \x0D',
            'Down': 'RCKY35  \x0D',
            }
        ChannelStepCmdString = ChannelStepStateValues[value] 
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)    
             
    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'RCKY54  \x0D'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)  

    def SetInput(self, value, qualifier):


        InputStateValues = {
            'TV'       :'ITVD0   \x0D', 
            'HDMI 1'   :'IAVD1   \x0D',
            'HDMI 2'   :'IAVD2   \x0D',
            'HDMI 3'   :'IAVD3   \x0D',
            'HDMI 4'   :'IAVD4   \x0D',
            'Component':'IAVD5   \x0D',
            'Video 1'  :'IAVD6   \x0D',
            'Video 2'  :'IAVD7   \x0D',
            'PC'	   :'IAVD8   \x0D',                                                                     
            }

        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)  
       
    def UpdateInput(self, value, qualifier):     

        InputStateNames = {
            '1':'HDMI 1',
            '2':'HDMI 2',
            '3':'HDMI 3',
            '4':'HDMI 4',
            '5':'Component',
            '6':'Video 1',
            '7':'Video 2',
            '8':'PC',                                                                                  
            }                                                                   
        
    
        InputCmdString = 'IAVD????\x0D'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)  

        if res:
            try:
                value= InputStateNames[res[0:1]]
                self.WriteStatus('Input', value, qualifier)  
            except  (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Input'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up'    :'RCKY41  \x0D',  
            'Down'  :'RCKY42  \x0D',
            'Left'  :'RCKY43  \x0D',
            'Right' :'RCKY44  \x0D',
            'Menu'  :'RCKY38  \x0D', 
            'Enter' :'RCKY40  \x0D',  
            'Exit'  :'RCKY46  \x0D',                                                                     
            }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)     
            
    def SetPower(self, value, qualifier):
       
        PowerStateValues = {
            'On':'POWR1   \x0D',
            'Off':'POWR0   \x0D',                         
            }   
        
        PowerCmdString = PowerStateValues[value]
        PowerControlCmdString1 = 'RSPW1   \x0D'
        PowerControlCmdString2 = 'RSPW2   \x0D'
        if value == 'On':
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        elif value == 'Off':
            if 'Serial' in self.ConnectionType:
                self.__SetHelper('Power', PowerControlCmdString1, value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
            else:
                self.__SetHelper('Power', PowerControlCmdString2, value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)                    
         
    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',  
           }

        PowerCmdString = 'POWR????\x0D'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)   
        if res:
            try:
                value = PowerStateNames[res[0:1]]  
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Power'])
                            
    def SetChannelDTVAir(self, value, qualifier):

        if value and 100 <= int(value) <= 9999:
            ChannelDTVAirDiscreteCmdString = 'DA2P{0:04d}\x0D'.format(int(value))
            self.__SetHelper('SetChannelDTVAirDiscrete', ChannelDTVAirDiscreteCmdString, value, qualifier)         
        else:
            self.Discard('Invalid Command for SetSetChannelDTVAirDiscrete')

    def SetChannelDTVCable2(self, value, qualifier):

        if value and 0 <= int(value) <= 9999:
            ChannelDTVCable2DiscreteCmdString = 'DC10{0:04d}\x0D'.format(int(value))
            self.__SetHelper('SetChannelDTVCable2Discrete', ChannelDTVCable2DiscreteCmdString, value, qualifier)         
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCable2Discrete')

    def SetChannelDTVCable3(self, value, qualifier):

        if value:
            if 0 <= int(value) <= 6383:
                ChannelDTVCable3DiscreteCmdString = 'DC11{0:04d}\x0D'.format(int(value))
                self.__SetHelper('SetChannelDTVCable3Discrete', ChannelDTVCable3DiscreteCmdString, value, qualifier)         
            else:
                self.Discard('Invalid Command for SetSetChannelDTVCable3Discrete')
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCable3Discrete')

    def SetChannelDTVCableMajor(self, value, qualifier):

        if value and 1 <= int(value) <= 999:
            ChannelDTVCableMajorDiscreteCmdString = 'DC2U{0:03d} \x0D'.format(int(value))
            self.__SetHelper('SetChannelDTVCableMajorDiscrete', ChannelDTVCableMajorDiscreteCmdString, value, qualifier)         
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCableMajorDiscrete')

    def SetChannelDTVCableMinor(self, value, qualifier):

        if value and 0 <= int(value) <= 999:
            ChannelDTVCableMinorDiscreteCmdString = 'DC2L{0:03d} \x0D'.format(int(value))
            self.__SetHelper('SetChannelDTVCableMinorDiscrete', ChannelDTVCableMinorDiscreteCmdString, value, qualifier)         
        else:
            self.Discard('Invalid Command for SetSetChannelDTVCableMinorDiscrete')

    def SetChannelTV(self, value, qualifier):

        if value and 0 <= int(value) < 136:
            ChannelTVDiscreteCmdString = 'DCCH{0:03d} \x0D'.format(int(value))
            self.__SetHelper('SetChannelTVDiscrete', ChannelTVDiscreteCmdString, value, qualifier)         
        else:
            self.Discard('Invalid Command for SetSetChannelTVDiscrete') 

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }    
        if VolumeConstraints['Min'] <= value < VolumeConstraints['Max']:   
            VolumeCmdString = 'VOLM{0:03d} \x0D'.format(value)    
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume') 
          
    def UpdateVolume(self, value, qualifier): 
          
        VolumeCmdString = 'VOLM????\x0D'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)  
        if res:
            try:   
                value = res[0:3]
                self.WriteStatus('Volume', int(value), qualifier)  
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response for Volume'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        
        DEVICE_ERROR_CODES = {            
            'ERR\x0D': 'Communication error or incorrect command',            
            }   
        if response:
            if response[0:3] in DEVICE_ERROR_CODES:
                ErrorString = sourceCmdName + DEVICE_ERROR_CODES[response[0:3]]
                self.Error([ErrorString])
                response = ''            
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True  
        if self.Unidirectional == 'True':  
            self.Send(commandstring)       
        else: 
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r') 
            if not res:
                self.Error(['Invalid/Unexpected Response'])
            else: 
                res = self.__CheckResponseForErrors(command + ':' + str(commandstring.strip()), res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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
                result = search(regexString, self._ReceiveBuffer)
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

