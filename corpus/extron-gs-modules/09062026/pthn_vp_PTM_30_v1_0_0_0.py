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
            'AspectRatio': {'Status': {}},
            'AspectRatioMode': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaptionDisplay': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampStatus': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Normal': 'CF SCREEN NORMAL\r',
            'True': 'CF SCREEN TRUE\r',
            'Full': 'CF SCREEN FULL\r',
            'Custom': 'CF SCREEN CUSTOM\r',
            'Natural': 'CF SCREEN NATURAL\r',
            'Zoom': 'CF SCREEN ZOOM\r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'NORMAL': 'Normal',
            'TRUE': 'True',
            'FULL': 'Full',
            'CUSTOM': 'Custom',
            'NATURAL': 'Natural',
            'ZOOM': 'Zoom'
            }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[4:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAspectRatioMode(self, value, qualifier):

        AspectRatioModeState = {
            '4:3': 'CF SCREENASPECT 43MODE\r',
            '16:9': 'CF SCREENASPECT 169MODE\r',
            '16:10': 'CF SCREENASPECT 1610MODE\r'
            }

        AspectRatioModeCmdString = AspectRatioModeState[value]
        self.__SetHelper('AspectRatioMode', AspectRatioModeCmdString, value, qualifier)

    def UpdateAspectRatioMode(self, value, qualifier):

        AspectRatioModeState = {
            '43MODE': '4:3',
            '169MODE': '16:9',
            '1610MODE': '16:10'
            }

        AspectRatioModeCmdString = 'CR SCREENASPECT\r'
        res = self.__UpdateHelper('AspectRatioMode', AspectRatioModeCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioModeState[res[4:-1]]
                self.WriteStatus('AspectRatioMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio Mode : Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': 'CF MUTE ON\r',
            'Off': 'CF MUTE OFF\r'
            }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        AudioMuteCmdString = 'CR MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[4:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaptionDisplay(self, value, qualifier):

        ClosedCaptionDisplayState = {
            'CC1': 'CF CCAPTIONDISP CC1\r',
            'CC2': 'CF CCAPTIONDISP CC2\r',
            'CC3': 'CF CCAPTIONDISP CC3\r',
            'CC4': 'CF CCAPTIONDISP CC4\r',
            'Off': 'CF CCAPTIONDISP OFF\r'
            }

        ClosedCaptionDisplayCmdString = ClosedCaptionDisplayState[value]
        self.__SetHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionDisplay(self, value, qualifier):

        ClosedCaptionDisplayState = {
            'CC1': 'CC1',
            'CC2': 'CC2',
            'CC3': 'CC3',
            'CC4': 'CC4',
            'OFF': 'Off'
            }

        ClosedCaptionDisplayCmdString = 'CR CCAPTIONDISP\r'
        res = self.__UpdateHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionDisplayState[res[4:-1]]
                self.WriteStatus('ClosedCaptionDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Display : Invalid/Unexpected Response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage : Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': 'CF FREEZE ON\r',
            'Off': 'CF FREEZE OFF\r'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[4:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'RGB 1': 'CF INPUT1 ANALOG\r',
            'YPbPr': 'CF INPUT1 YPBPR\r',
            'Scart': 'CF INPUT1 SCART\r',
            'RGB 2': 'CF INPUT2 ANALOG\r',
            'HDMI': 'CF INPUT3 HDMI\r',
            'Video': 'CF INPUT4 VIDEO\r',
            'S-Video': 'CF INPUT5 S-VIDEO\r'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1ANALOG\r': 'RGB 1',
            '1YPBPR\r': 'YPbPr',
            '1SCART\r': 'Scart',
            '2ANALOG\r': 'RGB 2',
            '3HDMI\r': 'HDMI',
            '4VIDEO\r': 'Video',
            '5S-VIDEO\r': 'S-Video'
            }

        InputCmdString = 'CR INPUT\r'
        res1 = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        InputNumber = res1[4:-1]
        InputTypeCmdString = 'CR SRCINP{0}\r'.format(InputNumber)
        res2 = self.__UpdateHelper('Input', InputTypeCmdString, value, qualifier)
        if res1 and res2:
            try:
                value = InputState[res1[-2] + res2[4:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'High': 'CF LAMPMODE HIGH\r',
            'Normal': 'CF LAMPMODE NORMAL\r'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            'HIGH': 'High',
            'NORMAL': 'Normal'
            }

        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[4:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode : Invalid Unexpected Response'])

    def UpdateLampStatus(self, value, qualifier):

        LampStatusState = {
            'I': 'On',
            'O': 'Off',
            'X': 'Failure'
            }

        LampStatusCmdString = 'CR LAMPSTS\r'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = LampStatusState[res[4:-1]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Status : Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage : Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'CF KEYENU UP\r',
            'Down': 'CF KEYENU DN\r',
            'Left': 'CF KEYENU LEFT\r',
            'Right': 'CF KEYENU RIGHT\r',
            'Select': 'CF KEYENU SELECT\r'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[6:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours : Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'CF POWER ON\r',
            'Off': 'CF POWER OFF\r',
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '00': 'On',
            '80': 'Off',
            '40': 'Warming Up',
            '20': 'Cooling Down',
            '10': 'Power Failure',
            '28': 'Cooling down due to abnormal temperature',
            '88': 'Stand by after Cooling down',
            '24': 'Power Saving Cooling down',
            '04': 'Power Saving',
            '21': 'Cooling down due to Lamp Failure',
            '81': 'Stand by after Cooling down due to Lamp Failure'
            }

        PowerCmdString = 'CR STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[4:-1]]
                if value in ['On', 'Off', 'Warming Up', 'Cooling Down']:
                    self.WriteStatus('Power', value, qualifier)
                    self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                elif value == 'Power Failure' or value == 'Stand by after Cooling down' or value == 'Power Saving' or value == 'Stand by after Cooling down due to Lamp Failure':
                    self.WriteStatus('Power', 'Off', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
                elif value == 'Cooling down due to abnormal temperature' or value == 'Power Saving Cooling down' or value == 'Cooling down due to Lamp Failure':
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power and Device Status : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': 'CF VMUTE ON\r',
            'Off': 'CF VMUTE OFF\r'
            }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[4:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'CF VOLUME {0:03d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'CR VOLUME\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?': 'When received data cannot be decoded.',
            '101': 'When the function selected is not available under current condition.',
            '102': 'Selected value is out of range.',
            '103': 'Command mismatched to Hardware.',
            '201': 'When reached upper or lower limit of increasing or decreasing data.',
            '301': 'Command cannot be executed during capturing display.',
            '302': 'Command cannot be executed during Auto setup operation.',
            '402': 'Command cannot be executed during PIN code operation.'
            }

        if response[0:-1] in DEVICE_ERROR_CODES:
            errorString = '{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:-1]])
            self.Error([errorString])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
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