from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface
from struct import pack
import re

class DeviceClass(): 
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.SetDelim = {
                'AspectRatio': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})',
                'AudioMute': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})',
                'AutoImage': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})',
                'Freeze': b'([\xA1][\x00-\xFF]{7})|([\x21][\x00-\xFF]{6})',
                'Input': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})',
                'LampMode': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})',
                'MenuNavigation': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})',
                'OnScreenDisplay': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})',
                'Power': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})',
                'VideoMute': b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})',
                'Volume': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})'
                }
            self.SetDelimRegex = {k: re.compile(v) for k, v in self.SetDelim.items()}
            self.UpdateDelim = {
            'AspectRatio': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})',
            'DeviceStatus': b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{17})',
            'LampMode': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})',
            'OperationHours': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{103})',
            'OnScreenDisplay': b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{133})',
            'Power': b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{21})',
            'Volume': b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})'
            }
            self.UpdtaeDelimRegex = {k: re.compile(v) for k, v in self.UpdateDelim.items()}

    def SetAspectRatio(self, value, qualifier):
        AspectRatioState = {   
            'Auto'   : 0x0F, 
            '4:3'    : 0x00, 
            '5:4'    : 0x0B, 
            '16:9'   : 0x02, 
            '15:9'   : 0x0D, 
            '16:10'  : 0x0C, 
            'Full'   : 0x06, 
            'Native' : 0x0E,
            'Letterbox' : 0x01
        }           

        cks = 0x30 + AspectRatioState[value]
        AspectRatioCmdString = pack('>BBBBBBBBBBB',0x03,0x10,0x00,0x00,0x05,0x18,0x00,0x00,AspectRatioState[value],0x00,cks)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioState = {
            b'\x0F' : 'Auto', 
            b'\x00' : '4:3', 
            b'\x0B' : '5:4', 
            b'\x02' : '16:9', 
            b'\x0D' : '15:9', 
            b'\x0C' : '16:10', 
            b'\x06' : 'Full', 
            b'\x0E' : 'Native',
            b'\x01' : 'Letterbox'
           }

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = AspectRatioState[res[12:13]]
                    self.WriteStatus('AspectRatio', value, None)
                else:
                    self.Discard('Invalid/unexpected response for UpdateAspectRatio')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):
        AudioMuteState = {
           'On' : b'\x02\x12\x00\x00\x00\x14',
           'Off' : b'\x02\x13\x00\x00\x00\x15'
           }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    
    def UpdateAudioMute(self, value, qualifier):
        self.UpdateOnScreenDisplay(value,qualifier)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def UpdateDeviceStatus(self, value, qualifier):
        DeviceStatusState = {
           b'\x00\x00\x00\x00' : 'Normal',
           b'\x01\x00\x00\x00' : 'Lamp Cover Error',
           b'\x02\x00\x00\x00' : 'Temp Error',
           b'\x10\x00\x00\x00' : 'Fan Error',
           b'\x20\x00\x00\x00' : 'Power Error',
           b'\x40\x00\x00\x00' : 'Lamp Error',
           b'\x08\x00\x00\x00' : 'Lamp Life Expired',
           b'\x00\x01\x00\x00' : 'Lamp Life Expired',
           b'\x00\x02\x00\x00' : 'Format Error',
           b'\x00\x00\x02\x00' : 'FPGA Error',
           b'\x00\x00\x04\x00' : 'Temp Sensor Failure',
           b'\x00\x00\x08\x00' : 'Lamp Housing Error',
           b'\x00\x00\x10\x00' : 'Lamp Data Error',
           b'\x00\x00\x20\x00' : 'Mirror Cover Error',
           b'\x00\x00\x00\x04' : 'High Temperature',
           b'\x00\x00\x00\x08' : 'Sensor Error',
           b'\x00\x00\x00\x10' : 'Pump Error',
           }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = DeviceStatusState.get(res[5:9], 'Multiple Errors')                    
                    self.WriteStatus('DeviceStatus', value, None)
                else: 
                    self.Discard('Invalid/unexpected response for UpdateDeviceStatus')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateDeviceStatus')
    
    def UpdateFilterUsage(self, value, qualifier):
        self.UpdateOperationHours(value,qualifier)

    def SetFreeze(self, value, qualifier):
        FreezeState = {
           'Off' : b'\x01\x98\x00\x00\x01\x02\x9C',
           'On' : b'\x01\x98\x00\x00\x01\x01\x9B'
           }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)


    def UpdateFreeze(self, value, qualifier):
        self.UpdateOnScreenDisplay(value,qualifier)

    def SetInput(self, value, qualifier):
        InputState = {
           'HDMI 1' : 0xA1,
           'HDMI 2' : 0xA2,
           'Display Port' : 0xA6,
           'BNC' : 0x02,
           'BNC (CV)'     : 0x06,
           'BNC (Y/C)'    : 0x0B,
           'Video' : 0x06,
           'S-Video' : 0x0B,
           'Computer' : 0x01,
           'HDBaseT' : 0x20
           }

        cks = 0x08 + InputState[value]
        InputCmdString = pack('>BBBBBBBB',0x02,0x03,0x00,0x00,0x02,0x01,InputState[value],cks)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdateOnScreenDisplay(value,qualifier)

    def SetLampMode(self, value, qualifier):
        LampModeState = {
           'Normal' : 0x00,
           'Eco' : 0x01
           }

        cks = 0xBD + LampModeState[value]
        LampModeCmdString = pack('>BBBBBBBB',0x03,0xB1,0x00,0x00,0x02,0x07,LampModeState[value],cks)
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeState = {
           b'\x00' : 'Normal',
           b'\x01' : 'Eco'
           }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if res[0:2] == b'\x23\xB0':
                    value = LampModeState[res[6:7]]
                    self.WriteStatus('LampMode', value, None)
                else:
                    self.Discard('Invalid/unexpected response for UpdateLampMode')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):
        self.UpdateOperationHours(value,qualifier)

    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationState = {
           'Up' : 0x07,
           'Down' : 0x08,
           'Left' : 0x0A,
           'Right' : 0x09,
           'Enter' : 0x0B,
           'Menu' : 0x06,
           'Cancel' : 0x0C
           }

        cks = 0x13 + MenuNavigationState[value]
        MenuNavigationCmdString = pack('>BBBBBBBB',0x02,0x0F,0x00,0x00,0x02,MenuNavigationState[value],0x00,cks)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayState = {
           'On' : b'\x02\x14\x00\x00\x00\x16',
           'Off' : b'\x02\x15\x00\x00\x00\x17'
           }

        OnScreenDisplayCmdString = OnScreenDisplayState[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
    
    def UpdateOnScreenDisplay(self, value, qualifier):
        InputState = {
           b'\x01\x21' : 'HDMI 1',
           b'\x02\x21' : 'HDMI 2',
           b'\x01\x22' : 'Display Port',
           b'\x02\x01' : 'BNC',
           b'\x01\x02' : 'BNC (CV)',
           b'\x01\x03' : 'BNC (Y/C)',
           b'\x01\x02' : 'Video',
           b'\x01\x03' : 'S-Video',
           b'\x01\x01' : 'Computer',
           b'\x02\x07' : 'HDBaseT'
           }
        AudioMuteState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }
        VideoMuteState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }
        FreezeState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }
        OSDState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }

        OnScreenDisplayCmdString = b'\x00\xC0\x00\x00\x00\xC0'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 134:
                    audioValue = AudioMuteState[res[34:35]]
                    inputValue = InputState[res[11:13]]
                    videoValue = VideoMuteState[res[33:34]]
                    freezeValue = FreezeState[res[36:37]]
                    OSDValue = OSDState[res[71:72]]                    
                    
                    self.WriteStatus('Input', inputValue, None)
                    self.WriteStatus('AudioMute', audioValue, None)
                    self.WriteStatus('VideoMute', videoValue, None)
                    self.WriteStatus('Freeze', freezeValue, None)
                    self.WriteStatus('OnScreenDisplay', OSDValue, None)
                else:
                    self.Discard('Invalid/unexpected response for Input/AudioMute/Videomute/Freeze/OnScreenDisplay')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateOnScreenDisplay')

    def UpdateOperationHours(self, value, qualifier):
        OperationHoursCmdString = b'\x03\x8A\x00\x00\x00\x8D'                                 
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 104:
                    operationHoursValue = int(((res[102]<<24) + (res[101]<<16) + (res[100]<<8) + res[99])/3600)
                    self.WriteStatus('OperationHours', operationHoursValue, None)
                    filterHoursValue = int(((res[94]<<24) + (res[93]<<16) + (res[92]<<8) + res[91])/3600)
                    self.WriteStatus('FilterUsage', filterHoursValue, None)
                    lampHoursValue = int(((res[90]<<24) + (res[89]<<16) + (res[88]<<8) + res[87])/3600)
                    self.WriteStatus('LampUsage', lampHoursValue, None)
                else:
                    self.Discard('Invalid/unexpected response for UpdateOperationHours')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateOperationHours')

    def SetPower(self, value, qualifier):
        PowerState = {
           'On' : (b'\x02\x00\x00\x00\x00\x02'),
           'Off' : (b'\x02\x01\x00\x00\x00\x03'),
           }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)


    def UpdatePower(self, value, qualifier):
        PowerState = {
           b'\x04' : 'On',
           b'\x00' : 'Off',
           b'\x06' : 'Off',
           b'\x10' : 'Off',
           b'\x0F' : 'Off',
           b'\x02' : 'Warming Up',
           b'\x01' : 'Warming Up',
           b'\x05' : 'Cooling Down'
           }

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    powerValue = PowerState[res[10:11]]
                    self.WriteStatus('Power', powerValue, None)                               
                else:
                    self.Discard('Invalid/unexpected response for UpdatePower')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):
        VideoMuteState = {
           'On' : b'\x02\x10\x00\x00\x00\x12',
           'Off' : b'\x02\x11\x00\x00\x00\x13'
           }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)


    def UpdateVideoMute(self, value, qualifier):
        self.UpdateOnScreenDisplay(value,qualifier)

    def SetVolume(self, value, qualifier):
        VolumeConstraints = {
            'Min' : 0,
            'Max' : 31
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            CKS = 0x1D + value
            VolumeCmdString = pack('>BBBBBBBBBBB',0x03,0x10,0x00,0x00,0x05,0x05,0x00,0x00,value,0x00,CKS)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = res[12]
                    self.WriteStatus('Volume', value, None)
                else:                    
                    self.Discard('Invalid/unexpected response for UpdateVolume')
            except (KeyError, IndexError):
                self.Discard('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, command, response):
        DEVICE_ERROR_CODES = {
            b'\x00\x00' : 'Unknown command.',
            b'\x00\x01' : 'This current model does not support this function.',
            b'\x01\x00' : 'Invalid values specificed.',
            b'\x01\x01' : 'Specified terminal is unavailable or cannot be selected.',
            b'\x01\x02' : 'Selected lanugage is not available.',
            b'\x02\x00' : 'Available memory reservation error.',
            b'\x02\x02' : 'Operating memory.',
            b'\x02\x03' : 'Setting not possible.',
            b'\x02\x04' : 'On forced on-screen mute mode.',
            b'\x02\x06' : 'Displaying a signal other than PC Viewer.', 
            b'\x02\x07' : 'No Signal.',
            b'\x02\x08' : 'Displaying a test pattern or PC Card fills screen.',
            b'\x02\x09' : 'No PC card is inserted.',
            b'\x02\x0A' : 'Memory operation failed.',
            b'\x02\x0C' : 'Displaying the Entry List.',
            b'\x02\x0D' : 'Power Off inhibited.',
            b'\x02\x0E' : 'Execution error.',
            b'\x02\x0F' : 'No operation authority.',
            b'\x03\x00' : 'Specified gain number is wrong.',
            b'\x03\x01' : 'Selected gain is not available.',
            b'\x03\x02' : 'Adjustment failed.'
            }
        if response[0:1] in[b'\xA0', b'\xA1', b'\xA2', b'\xA3']:
            if response[5:7] in DEVICE_ERROR_CODES:
                errorString = command + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]]
                self.Error([errorString])
            response = ''
        return response
    
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        regex = self.SetDelimRegex[command]

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            res = b''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                self.Discard('No Response or Invalid/unexpected response for Set' + command)
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        regex = self.UpdtaeDelimRegex[command]

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command, module is set to Unidirectional')
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                return b''
            else:                
                return self.__CheckResponseForErrors(command, res)           

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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