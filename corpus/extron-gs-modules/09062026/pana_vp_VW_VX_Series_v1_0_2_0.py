from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):


        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PT-VX405KEA': self.pana_1_379_Base,
            'PT-VX45KEA': self.pana_1_379_Base,
            'PT-VW440E': self.pana_1_379_Base,
            'PT-VX510E': self.pana_1_379_Base,
            'PT-VW440EA': self.pana_1_379_Base,
            'PT-VX510EA': self.pana_1_379_Base,
            'PT-VW440U': self.pana_1_379_Base,
            'PT-VX510U': self.pana_1_379_Base,
            'PT-VW431DE': self.pana_1_379_VW431D,
            'PT-VW431DEA': self.pana_1_379_VW431D,
            'PT-VW431DU': self.pana_1_379_VW431D,
            'PT-VW435NE': self.pana_1_379_435N505N,
            'PT-VX505NE': self.pana_1_379_435N505N,
            'PT-VW435NEA': self.pana_1_379_435N505N,
            'PT-VX505NEA': self.pana_1_379_435N505N,
            'PT-VW435NU': self.pana_1_379_435N505N,
            'PT-VX505NU': self.pana_1_379_435N505N,
            'PT-VW430E': self.pana_1_379_Base,
            'PT-VX500E': self.pana_1_379_Base,
            'PT-VW430EA': self.pana_1_379_Base,
            'PT-VX500EA': self.pana_1_379_Base,
            'PT-VX501EA': self.pana_1_379_Base,
            'PT-VW430U': self.pana_1_379_Base,
            'PT-VX500U': self.pana_1_379_Base,
            'PT-VX501U': self.pana_1_379_Base,
            }

        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
        

    def SetAspectRatio(self, value, qualifier):


        AspectRatioStateValues = {
            '16:10' : '\x02VSF:0\x03',
            '16:9'  : '\x02VSF:1\x03',
            '4:3'   : '\x02VSF:2\x03'
            }

        AspectRatioCmdString = AspectRatioStateValues[value]

        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):        

        AspectRatioStateNames = {
            '0'  : '16:10',
            '1'  : '16:9',
            '2'  : '4:3'
            }

        AspectRatioCmdString = '\x02QSF\x03'     
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[1]]       
                self.WriteStatus('AspectRatio', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetAVMute(self, value, qualifier):


        AVMuteStateValues = {
            'Off' : '\x02OSH:0\x03',
            'On'  : '\x02OSH:1\x03'
            }
        
        AVMuteCmdString = AVMuteStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)  

    def UpdateAVMute(self, value, qualifier):        
        AVMuteStateNames = {
            '0'  : 'Off',
            '1'  : 'On'
            }
        
        AVMuteCmdString = '\x02QSH\x03'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = AVMuteStateNames[res[1]]   
                self.WriteStatus('AVMute', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):


        ClosedCaptionStateValues = {
            'CC1' : '\x02OCC:1\x03',
            'CC2' : '\x02OCC:2\x03',
            'CC3' : '\x02OCC:3\x03',
            'CC4' : '\x02OCC:4\x03',
            'Off' : '\x02OCC:0\x03'
            }
        
        ClosedCaptionCmdString = ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)  

    def UpdateClosedCaption(self, value, qualifier):        
        ClosedCaptionStateNames = {
            '1' : 'CC1',
            '2' : 'CC2',
            '3' : 'CC3',
            '4' : 'CC4',
            '0' : 'Off' 
            }
        
        ClosedCaptionCmdString = '\x02QCC\x03' 
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[1]]   
                self.WriteStatus('ClosedCaption', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On'  : '\x02OFZ:1\x03',
            'Off' : '\x02OFZ:0\x03',
            }
        
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)  

    def UpdateFreeze(self, value, qualifier):        
        FreezeStateNames = {
            '1' : 'On',
            '0' : 'Off' 
            }
        
        FreezeCmdString = '\x02QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1]]   
                self.WriteStatus('Freeze', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):


        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
            

    def UpdateInput(self, value, qualifier):        

        InputCmdString = '\x02QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) <= 5:                
                    value = self.InputStateNames[res[1:4]]
                else:
                    value = self.InputStateNames[res[1:8]]  
                self.WriteStatus('Input', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal'     : '\x02OLP:1\x03',
            'Eco'        : '\x02OLP:0\x03'
            }
        
        LampModeCmdString = LampModeStateValues[value] 
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        
    def UpdateLampMode(self, value, qualifier):        
        LampModeStateNames = {
            '1' : 'Normal',
            '0' : 'Eco'
            }
        
        LampModeCmdString = '\x02QLP\x03'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[1]]   
                self.WriteStatus('LampMode', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):        

        LampUsageCmdString = '\x02Q$L\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])   
                self.WriteStatus('LampUsage', value, qualifier)  
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu'   : '\x02OMN\x03',
            'Up'     : '\x02OCU\x03',
            'Down'   : '\x02OCD\x03',
            'Left'   : '\x02OCL\x03',
            'Right'  : '\x02OCR\x03',
            'Enter'  : '\x02OEN\x03',
            }
        
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : '\x02PON\x03',
            'Off' : '\x02POF\x03'
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):        

        PowerStateNames = {
            '2' : 'On',
            '0' : 'Off',
            '1' : 'Warming Up',
            '3' : 'Cooling Down'
            }

        PowerCmdString = '\x02Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[1]]   
                self.WriteStatus('Power', value, qualifier)  
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 63
            }
  
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
                VolumeCmdString = '\x02AVL:{0:03d}\x03'.format(value)    
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')  
        
    def UpdateVolume(self, value, qualifier):        

        VolumeCmdString = '\x02QAV\x03'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])    
                self.WriteStatus('Volume', value, qualifier)  
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        
        DEVICE_ERROR_CODES = {'\x02ER401\x03': "Invalid Command Reply.",
                              '\x02ER402\x03': 'Invalid Parameter.'}   
        if response:
            response = response.decode()
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''
            return response
        else:
            self.Error(['No Response From Device'])


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_1_379_Base(self):

        self.InputStateValues = {
            'Video'      : '\x02IIS:VID\x03',
            'S-Video'    : '\x02IIS:SVD\x03',
            'Computer 1' : '\x02IIS:RG1\x03',
            'Computer 2' : '\x02IIS:RG2\x03',  
            'HDMI'       : '\x02IIS:HD1\x03',         
            'SCART'      : '\x02IIS:SCT\x03'           
            }

        self.InputStateNames = {
            'VID' : 'Video',     
            'SVD' : 'S-Video',   
            'RG1' : 'Computer 1',
            'RG2' : 'Computer 2',  
            'HD1' : 'HDMI',               
            'SCT' : 'SCART'               
            }


    def pana_1_379_435N505N(self):

        self.InputStateValues = {
            'Video'      : '\x02IIS:VID\x03',
            'S-Video'    : '\x02IIS:SVD\x03',
            'Computer 1' : '\x02IIS:RG1\x03',
            'Computer 2' : '\x02IIS:RG2\x03',  
            'HDMI'       : '\x02IIS:HD1\x03',         
            'SCART'      : '\x02IIS:SCT\x03',
            'Network'    : '\x02IIS:NWP\x03'           
            }

        self.InputStateNames = {
            'VID' : 'Video',     
            'SVD' : 'S-Video',   
            'RG1' : 'Computer 1',
            'RG2' : 'Computer 2',  
            'HD1' : 'HDMI',               
            'SCT' : 'SCART',
            'NWP' : 'Network'               
            }


    def pana_1_379_VW431D(self):

        self.InputStateValues = {
            'Video'                   : '\x02IIS:VID\x03',
            'S-Video'                 : '\x02IIS:SVD\x03',
            'Computer 1'              : '\x02IIS:RG1\x03',
            'Computer 2'              : '\x02IIS:RG2\x03',  
            'HDMI'                    : '\x02IIS:HD1\x03',         
            'SCART'                   : '\x02IIS:SCT\x03',
            'Network'                 : '\x02IIS:NWP\x03',
            'Digital Link'            : '\x02IIS:DL1\x03',
            'Digital Link HDMI 1'     : '\x02IIS:DL1:HD1\x03',
            'Digital Link HDMI 2'     : '\x02IIS:DL1:HD2\x03',
            'Digital Link Computer 1' : '\x02IIS:DL1:PC1\x03',
            'Digital Link Computer 2' : '\x02IIS:DL1:PC2\x03',
            'Digital Link Video'      : '\x02IIS:DL1:VID\x03',
            'Digital Link S-Video'    : '\x02IIS:DL1:SVD\x03'           
            }

        self.InputStateNames = {
            'VID'     : 'Video',     
            'SVD'     : 'S-Video',   
            'RG1'     : 'Computer 1',
            'RG2'     : 'Computer 2',  
            'HD1'     : 'HDMI',               
            'SCT'     : 'SCART',
            'NWP'     : 'Network',
            'DL1'     : 'Digital Link',
            'DL1:HD1' : 'Digital Link HDMI 1',
            'DL1:HD2' : 'Digital Link HDMI 2',
            'DL1:PC1' : 'Digital Link Computer 1',
            'DL1:PC2' : 'Digital Link Computer 2',
            'DL1:VID' : 'Digital Link Video',
            'DL1:SVD' : 'Digital Link S-Video'               
            }    
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

