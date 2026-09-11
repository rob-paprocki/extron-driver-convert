from extronlib.interface import SerialInterface, EthernetClientInterface
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

        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AdjustmentLock': { 'Status': {}}, 
            'AdjustmentLockTarget': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PIP': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PbyPPosition': { 'Status': {}},
            'PIPMainPosition': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            
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

    def SetAdjustmentLock(self, value, qualifier):  

        AdjustmentLockValues = {
            'Mode 1' : 1,  
            'Mode 2' : 2,  
            'Off'    : 0  
        }
        
        AdjustmentLockCmdString = 'ALCK{0:4}\r'.format(AdjustmentLockValues[value])
        self.__SetHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier)  

    def UpdateAdjustmentLock(self, value, qualifier): 

        AdjustmentLockStateNames = {
            1 : 'Mode 1',  
            2 : 'Mode 2',  
            0 : 'Off'
        }

        AdjustmentLockCmdString = 'ALCK????\r'
        res = self.__UpdateHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier) 
        if res:
            try:
                value = AdjustmentLockStateNames[int(res[:1])]   
                self.WriteStatus('AdjustmentLock', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetAdjustmentLockTarget(self, value, qualifier):  

        AdjustmentLockTargetValues = {
            'Remote Control'  : 0,  
            'Monitor Buttons' : 1,  
            'Both'            : 2  
        }
        
        AdjustmentLockCmdString = 'ALTG{0:4}\r'.format(AdjustmentLockTargetValues[value])
        self.__SetHelper('AdjustmentLockTarget', AdjustmentLockCmdString, value, qualifier)  

    def UpdateAdjustmentLockTarget(self, value, qualifier): 

        AdjustmentLockTargetStateNames = {
            0 : 'Remote Control',  
            1 : 'Monitor Buttons',  
            2 : 'Both'
        }

        AdjustmentLockTargetCmdString = 'ALTG????\r'
        res = self.__UpdateHelper('AdjustmentLockTarget', AdjustmentLockTargetCmdString, value, qualifier) 
        if res:
            try:
                value = AdjustmentLockTargetStateNames[int(res[:1])]   
                self.WriteStatus('AdjustmentLockTarget', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetAspectRatio(self, value, qualifier):  

        AspectRatioValuesPC = {
            'Wide'       : 1,  
            'Zoom 1'     : 4,  
            'Zoom 2'     : 5,  
            'Normal'     : 2,
            'Dot by Dot' : 3
        }

        AspectRatioValuesAV = {
            'Wide'       : 1,  
            'Zoom 1'     : 2,  
            'Zoom 2'     : 3,  
            'Normal'     : 4,
            'Dot by Dot' : 5
        }

        input_ = qualifier['Input']
        if input_:
            if input_[:2] == 'PC':
                AspectRatioCmdString = 'WIDE{0:4}\r'.format(AspectRatioValuesPC[value])
            else:
                AspectRatioCmdString = 'WIDE{0:4}\r'.format(AspectRatioValuesAV[value])

            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)  
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier): 

        AspectRatioStateNamesAV = {
            1 : 'Wide',  
            2 : 'Zoom 1',  
            3 : 'Zoom 2',
            4 : 'Normal',
            5 : 'Dot by Dot'
        }

        AspectRatioStateNamesPC = {
            1 : 'Wide',  
            4 : 'Zoom 1',  
            5 : 'Zoom 2',
            2 : 'Normal',
            3 : 'Dot by Dot'
        }

        input_ = qualifier['Input']
        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier) 
        if res:
            try:
                if input_:
                    if input_[:2] == 'PC':
                        value = AspectRatioStateNamesPC[int(res[:1])]   
                        self.WriteStatus('AspectRatio', value, None)  
                    else:
                        value = AspectRatioStateNamesAV[int(res[:1])]   
                        self.WriteStatus('AspectRatio', value, None)  
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):  

        AutoImageCmdString = 'AGIN{0:4}\r'.format(1)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = 'VLMP{0:4}\r'.format(value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'VLMP????\r'
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Brightness', value, qualifier)
            except (IndexError, ValueError):
                self.Error(['Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'PC DVI-D'     : 1, 
            'PC D-sub'     : 2, 
            'AV Component' : 3, 
            'AV Video'     : 4, 
            'PC RGB'       : 6, 
            'AV DVI-D'     : 7, 
            'AV S-Video'   : 8,
            'AV HDMI'      : 9,
            'PC HDMI'      : 10
        }
        
        InputCmdString = 'INPS{0:4}\r'.format(InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier) 

    def UpdateInput(self, value, qualifier): 
      
        InputStateNames = {
            1  : 'PC DVI-D',
            2  : 'PC D-sub',
            3  : 'AV Component',
            4  : 'AV Video',
            6  : 'PC RGB',
            7  : 'AV DVI-D',
            8  : 'AV S-Video',
            9  : 'AV HDMI',
            10 : 'PC HDMI'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier) 
        if res:
            try:
                value = InputStateNames[int(res)] 
                self.WriteStatus('Input', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])
     
    def SetMute(self, value, qualifier):  

        MuteStateValues = {
            'On'  : 1,  
            'Off' : 0
        }
        
        MuteCmdString = 'MUTE{0:4}\r'.format(MuteStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)  

    def UpdateMute(self, value, qualifier):   
 
        MuteStateNames = {
            0 : 'Off', 
            1 : 'On'   
        }

        MuteCmdString = 'MUTE????\r'  
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier) 
        if res:
            try:
                value = MuteStateNames[int(res[:1])] 
                self.WriteStatus('Mute', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetOnScreenDisplay(self, value, qualifier):  

        OnScreenDisplayStateValues = {
            'On'          : 0,  
            'Off'         : 1,
            'On (Mode 2)' : 2
        }
        
        OnScreenDisplayCmdString = 'LOSD{0:4}\r'.format(OnScreenDisplayStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)  

    def UpdateOnScreenDisplay(self, value, qualifier):   
 
        OnScreenDisplayStateNames = {
            0 : 'On', 
            1 : 'Off',
            2 : 'On (Mode 2)'
        }

        OnScreenDisplayCmdString = 'LOSD????\r'  
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier) 
        if res:
            try:
                value = OnScreenDisplayStateNames[int(res[:1])] 
                self.WriteStatus('OnScreenDisplay', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPbyPPosition(self, value, qualifier):

        PbyPPositionStateValues = {
            'Position 1'   : 0, 
            'Position 2'   : 1, 
            'Position 3'   : 2 
        }
        
        PbyPPositionCmdString = 'MW2P{0:4}\r'.format(PbyPPositionStateValues[value])
        self.__SetHelper('PbyPPosition', PbyPPositionCmdString, value, qualifier)

    def UpdatePbyPPosition(self, value, qualifier): 
      
        PbyPPositionStateNames = {
            0  : 'Position 1',
            1  : 'Position 2',
            2  : 'Position 3'
        }

        PbyPPositionCmdString = 'MW2P????\r'
        res = self.__UpdateHelper('PbyPPosition', PbyPPositionCmdString, value, qualifier) 
        if res:
            try:
                value = PbyPPositionStateNames[int(res)] 
                self.WriteStatus('PbyPPosition', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])
     
    def SetPIP(self, value, qualifier):  

        PIPStateValues = {
            'Off'                 : 0,  
            'Picture in Picture'  : 1, 
            'Side-by-Side Mode 1' : 2, 
            'Side-by-Side Mode 2' : 3
        }
        
        PIPCmdString = 'MWIN{0:4}\r'.format(PIPStateValues[value])
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):   
 
        PIPStateNames = {
            0 : 'Off',
            1 : 'Picture in Picture',
            2 : 'Side-by-Side Mode 1',
            3 : 'Side-by-Side Mode 2'
        }

        PIPCmdString = 'MWIN????\r'  
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier) 
        if res:
            try:
                value = PIPStateNames[int(res[:1])] 
                self.WriteStatus('PIP', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPIPInput(self, value, qualifier):

        PIPInputStateValues = {
            'PC DVI-D'     : 1, 
            'PC D-sub'     : 2, 
            'AV Component' : 3, 
            'AV Video'     : 4, 
            'PC RGB'       : 6, 
            'AV DVI-D'     : 7, 
            'AV S-Video'   : 8,
            'AV HDMI'      : 9,
            'PC HDMI'      : 10
        }
        
        PIPInputCmdString = 'MWIP{0:4}\r'.format(PIPInputStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier) 

    def UpdatePIPInput(self, value, qualifier): 
      
        PIPInputStateNames = {
            1  : 'PC DVI-D',
            2  : 'PC D-sub',
            3  : 'AV Component',
            4  : 'AV Video',
            6  : 'PC RGB',
            7  : 'AV DVI-D',
            8  : 'AV S-Video',
            9  : 'AV HDMI',
            10 : 'PC HDMI'
        }

        PIPInputCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier) 
        if res:
            try:
                value = PIPInputStateNames[int(res)] 
                self.WriteStatus('PIPInput', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])
     
    def SetPIPMainPosition(self, value, qualifier):

        PIPMainPositionStateValues = {
            'Position 1'   : 0, 
            'Position 2'   : 1
        }
        
        PIPMainPositionCmdString = 'MWPP{0:4}\r'.format(PIPMainPositionStateValues[value])
        self.__SetHelper('PIPMainPosition', PIPMainPositionCmdString, value, qualifier) 

    def UpdatePIPMainPosition(self, value, qualifier): 
      
        PIPMainPositionStateNames = {
            0  : 'Position 1',
            1  : 'Position 2'
        }

        PIPMainPositionCmdString = 'MWPP????\r'
        res = self.__UpdateHelper('PIPMainPosition', PIPMainPositionCmdString, value, qualifier) 
        if res:
            try:
                value = PIPMainPositionStateNames[int(res)] 
                self.WriteStatus('PIPMainPosition', value, qualifier) 
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])
     
    def SetPIPSize(self, value, qualifier):  

        PIPSizeConstraints = {
            'Min' : 1,
            'Max' : 64
        }
        
        if PIPSizeConstraints['Min'] <= value <= PIPSizeConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{0:4}\r'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)   
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier): 
 
        PIPSizeCmdString = 'MPSZ????\r'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)  
        if res:
            try:
                value = int(res)  
                self.WriteStatus('PIPSize', value, qualifier)  
            except (IndexError, ValueError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier): 

        PowerStateValues = {
            'On'  : 1,  
            'Off' : 0, 
        }
        
        PowerCmdString = 'POWR{0:4}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):  
   
        PowerStateNames = {
            1 : 'On',
            0 : 'Off',
            2 : 'Input Signal Waiting'
        }

        PowerCmdString = 'POWR????\r'   
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)   
        if res:
            try:
                value = PowerStateNames[int(res[:1])]  
                self.WriteStatus('Power', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):  

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 31
        }
        
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOLM{0:4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier): 
 
        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)  
        if res:
            try:
                value = int(res)  
                self.WriteStatus('Volume', value, qualifier)  
            except (IndexError, ValueError):
                self.Error(['Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} No Relevant Command or Command Cannot Be Executed in Current State'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0.3):

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