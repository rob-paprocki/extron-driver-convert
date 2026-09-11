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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Auto'  : 'AUTO', 
            '4:3'   : '4:3', 
            '16:9'  : '16:9', 
            '16:10' : '16:10', 
            'Zoom'  : 'ZOOM', 
            'True'  : 'TRUE'
            }

        AspectRatioCmdString = 'ASPECT={0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'AUTO' : 'Auto', 
            '4:3' : '4:3', 
            '16:9' : '16:9', 
            '16:10' : '16:10', 
            'ZOOM' : 'Zoom', 
            'TRUE' : 'True'
            }

        AspectRatioCmdString = 'GET ASPECT\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[9:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On' : 'ON', 
            'Off' : 'OFF'
            }

        AudioMuteCmdString = 'MUTE={0}\r'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        AudioMuteCmdString = 'GET MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[7:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'RC=AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            'NO_ERROR' : 'Normal', 
            'ABNORMAL_TEMPERATURE' : 'Abnormal Temperature', 
            'FAULTY_LAMP' : 'Lamp Error',
            'FAULTY_LAMP_COVER' : 'Lamp Cover Error',
            'FAULTY_COOLING_FAN' : 'Fan Error',
            'FAULTY_POWER_SUPPLY' : 'Power Supply Error',
            'FAULTY_AIR_FILTER' : 'Filter Error',
            'FAULTY_POWER_ZOOM' : 'Zoom Error',
            'FAULTY_POWER_FOCUS' : 'Focus Error',
            'FAULTY_POWER_LENS_SHIFT' : 'Lens Shift Error',
            'FAULTY_LENS_CONNECTOR' : 'Lens Connector Error'
            }

        DeviceStatusCmdString = 'GET ERR\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusState[res[6:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status : Invalid/Unexpected Response'])

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Keypad Lock' : 'MAIN', 
            'Remote Lock' : 'RC', 
            'Off' : 'OFF'
            }

        ExecutiveModeCmdString = 'KEYLOCK={0}\r'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'MAIN' : 'Keypad Lock', 
            'RC' : 'Remote Lock', 
            'OFF' : 'Off'
            }

        ExecutiveModeCmdString = 'GET KEYLOCK\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeState[res[10:-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode : Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On' : 'ON', 
            'Off' : 'OFF'
            }

        FreezeCmdString = 'FREEZE={0}\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        FreezeCmdString = 'GET FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[9:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'HDMI'          : 'HDMI', 
            'DVI'           : 'D-RGB', 
            'USB'           : 'USB', 
            'Component'     : 'COMP', 
            'Analog RGB 1'  : 'A-RGB1', 
            'Analog RGB 2'  : 'A-RGB2', 
            'LAN'           : 'LAN', 
            'HDBaseT'       : 'HDBT', 
            'DisplayPort'   : 'DP'
            }

        InputCmdString = 'INPUT={0}\r'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            'HDMI' : 'HDMI', 
            'DVI' : 'DVI', 
            'USB' : 'USB', 
            'COMP' : 'Component', 
            'A-RGB1' : 'Analog RGB 1', 
            'A-RGB2' : 'Analog RGB 2', 
            'LAN' : 'LAN', 
            'HDBT' : 'HDBaseT', 
            'DP' : 'DisplayPort'
            }

        InputCmdString = 'GET INPUT\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[8:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Eco 1' : 'ECO1', 
            'Eco 2' : 'ECO2', 
            'Full' : 'FULL'
            }

        LampModeCmdString = 'LAMP={0}\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            'ECO1' : 'Eco 1', 
            'ECO2' : 'Eco 2', 
            'FULL' : 'Full'
            }

        LampModeCmdString = 'GET LAMP\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[7:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode : Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'GET LMPT\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-4])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage : Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up'    : 'RC UP\r', 
            'Down'  : 'RC DOWN\r', 
            'Left'  : 'RC LEFT\r', 
            'Right' : 'RC RIGHT\r', 
            'Ok'    : 'RC OK\r', 
            'Menu'  : 'RC MENU\r'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On' : 'ON', 
            'Off' : 'OFF', 
            }

        PowerCmdString = 'POWER={0}\r'.format(PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerState = {
            'ON' : 'On', 
            'OFF' : 'Off',
            'PMM' : 'Off', 
            'OFF2ON' : 'Warming Up',
            'PMM2ON' : 'Warming Up',
            'ON2OFF' : 'Cooling Down',
            'ON2PMM' : 'Cooling Down'
            }

        PowerCmdString = 'GET POWER\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[8:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On' : 'ON', 
            'Off' : 'OFF'
            }

        VideoMuteCmdString = 'BLANK={0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            'ON' : 'On', 
            'OFF' : 'Off'
            }

        VideoMuteCmdString = 'GET BLANK\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[8:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AVOL={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET AVOL\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            '0002' : 'Invalid Command',
            '000A' : 'Invalid Parameter',
            'F001' : 'Internal Error',
            '0005' : 'No Power Supplied',
            '1011' : 'Function Not Available',
            '201F' : 'Invalid Signal'
            }

        if 'BUSY' in response:
            errorstring = 'Cannot Execute: Device is Busy'
            response = ''
            self.Error([errorstring])  
        elif 'e:' in response:
            errorstring = 'ERROR: {0}'.format(ErrorStates[response[2:6]])
            response = ''
            self.Error([errorstring])      
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} : Invalid/Unexpected command'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if res:
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

