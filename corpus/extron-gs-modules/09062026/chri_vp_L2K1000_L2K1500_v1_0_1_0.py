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
        self.devicePassword = None
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LampMode': {'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}},
            }

        if self.ConnectionType == 'Ethernet':
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
         self.SetPassword()

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Normal': 'NORMAL',
            'Full': 'FULL',
            'Wide': 'WIDE',
            'Zoom': 'ZOOM',
            'True': 'TRUE',
            'Custom': 'CUSTOM',
            'DZoom +': 'DZOOM UP',
            'DZoom -': 'DZOOM DN'
            }

        AspectRatioCmdString = 'CF SCREEN {0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'NORMAL': 'Normal',
            'FULL': 'Full',
            'WIDE': 'Wide',
            'ZOOM': 'Zoom',
            'TRUE': 'True',
            'CUSTOM': 'Custom',
            }

        AspectRatioCmdString = 'CR SCREEN\r'
        response = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if response:
            try:
               value = AspectRatioState[response[4:-1]]
               self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'CF KEYEMU AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'Off': 'OFF',
            'CC1': 'CC1',
            'CC2': 'CC2',
            'CC3': 'CC3',
            'CC4': 'CC4',
            }

        ClosedCaptionCmdString = 'CF CCAPTIONDISP {0}\r'.format(ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'OFF': 'Off',
            'CC1': 'CC1',
            'CC2': 'CC2',
            'CC3': 'CC3',
            'CC4': 'CC4',
            }

        ClosedCaptionCmdString = 'CR CCAPTIONDISP\r'
        response = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if response:
            try:
               value = ClosedCaptionState[response[4:-1]]
               self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption : Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'
        response = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if response:
            try:
               value = int(response[4:-1])
               self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage : Invalid/Unexpected Response'])

    def SetFocus(self, value, qualifier):

        FocusState = {
            'Near': 'C4A\r',
            'Far': 'C4B\r',
            }

        FocusCmdString = FocusState[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': 'ON',
            'Off': 'OFF',
            }

        FreezeCmdString = 'CF FREEZE {0}\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
            'ON': 'On',
            'OFF': 'Off',
            }

        FreezeCmdString = 'CR FREEZE\r'
        response = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if response:
            try:
               value = FreezeState[response[4:-1]]
               self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'Input 1 Digital': 'CF INPUT1 DIGITAL\r',
            'Input 1 HDMI': 'CF INPUT1 HDMI\r',
            'Input 1 Analog': 'CF INPUT1 ANALOG\r',
            'Input 1 SCART': 'CF INPUT1 SCART\r',
            'Input 1 HDCP': 'CF INPUT1 HDCP\r',
            'Input 2 S-Video': 'CF INPUT2 S-VIDEO\r',
            'Input 2 YPbPr': 'CF INPUT2 YPBPR\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 RGB': 'CF INPUT2 ANALOG\r',
            'Input 3 Digital': 'CF INPUT3 DIGITAL\r',
            'Input 3 Analog': 'CF INPUT3 ANALOG\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 SDI 1': 'CF INPUT3 SDI1\r',
            'Input 3 SDI 2': 'CF INPUT3 SDI2\r',
            'Input 3 SCART': 'CF INPUT3 SCART\r',
            'Input 3 YPbPr': 'CF INPUT3 YPBPR\r',
            'Input 3 HDCP': 'CF INPUT3 HDCP\r',
            'Input 3 HDMI': 'CF INPUT3 HDMI\r',
            'Input 4 Digital': 'CF INPUT4 DIGITAL\r',
            'Input 4 Analog': 'CF INPUT4 ANALOG\r',
            'Input 4 Video': 'CF INPUT4 VIDEO\r',
            'Input 4 S-Video': 'CF INPUT4 S-VIDEO\r',
            'Input 4 SCART': 'CF INPUT4 SCART\r',
            'Input 4 YPbPr': 'CF INPUT4 YPBPR\r',
            'Input 4 SDI 1': 'CF INPUT4 SDI1\r',
            'Input 4 SDI 2': 'CF INPUT4 SDI2\r',
            'Input 4 HDCP': 'CF INPUT4 HDCP\r',
            'Input 4 HDMI': 'CF INPUT4 HDMI\r',
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1DIGITAL\r': 'Input 1 Digital',
            '1HDMI\r': 'Input 1 HDMI',
            '1ANALOG\r': 'Input 1 Analog',
            '1SCART\r': 'Input 1 SCART',
            '1HDCP\r': 'Input 1 HDCP',
            '2S-VIDEO\r': 'Input 2 S-Video',
            '2YPBPR\r': 'Input 2 YPbPr',
            '2VIDEO\r': 'Input 2 Video',
            '2RGB\r': 'Input 2 RGB',
            '3DIGITAL\r': 'Input 3 Digital',
            '3ANALOG\r': 'Input 3 Analog',
            '3VIDEO\r': 'Input 3 Video',
            '3S-VIDEO\r': 'Input 3 S-Video',
            '3SDI1\r': 'Input 3 SDI 1',
            '3SDI2\r': 'Input 3 SDI 2',
            '3SCART\r': 'Input 3 SCART',
            '3YPbPr\r': 'Input 3 YPbPr',
            '3HDCP\r': 'Input 3 HDCP',
            '3HDMI\r': 'Input 3 HDMI',
            '4DIGITAL\r': 'Input 4 Digital',
            '4ANALOG\r': 'Input 4 Analog',
            '4VIDEO\r': 'Input 4 Video',
            '4S-VIDEO\r': 'Input 4 S-Video',
            '4SCART\r': 'Input 4 SCART',
            '4YPBPR\r': 'Input 4 YPbPr',
            '4SDI1\r': 'Input 4 SDI 1',
            '4SDI2\r': 'Input 4 SDI 2',
            '4HDCP\r': 'Input 4 HDCP',
            '4HDMI\r': 'Input 4 HDMI',
            }

        InputNumberCmdString = 'CR INPUT\r'
        res1 = self.__UpdateHelper('Input', InputNumberCmdString, value, qualifier)
        InputTypeCmdString = 'CR SOURCE\r'
        res2 = self.__UpdateHelper('Input', InputTypeCmdString, value, qualifier)
        if res1 and res2:
            try:
                value = InputState[res1[-2] + res2[4:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        response = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if response:
            try:
                Usage1 = int(response[4:9])
                self.WriteStatus('LampUsage', Usage1, {'Lamp': '1'})
            except (ValueError, IndexError):
                self.Error(['Lamp Usage : Invalid/Unexpected Response'])

            try:
                Usage2 = int(response[10:15])
                self.WriteStatus('LampUsage', Usage2, {'Lamp': '2'})
            except (ValueError, IndexError):
                self.Error(['Lamp Usage : Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': 'NORMAL',
            'Eco 1': 'ECO1',
            'Eco 2': 'ECO2',
            'Auto': 'AUTO',
            }

        LampModeCmdString = 'CF AUTOLAMPCONTRL {0}\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            'NORMAL': 'Normal',
            'ECO1': 'Eco 1',
            'ECO2': 'Eco 2',
            'AUTO': 'Auto',
            }

        LampModeCmdString = 'CR AUTOLAMPCONTRL\r'
        response = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if response:
            try:
               value = LampModeState[response[4:-1]]
               self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode : Invalid/Unexpected Response'])

    def UpdateLampStatus(self, value, qualifier):

        LampStatusState = {
            'I': 'On',
            'O': 'Off',
            'X': 'Failure'
            }

        LampStatusCmdString = 'CR LAMPSTS\r'
        response = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if response:
            try:
                value = LampStatusState[response[5:6]]
                self.WriteStatus('LampStatus', value, {'Lamp': '1'})
            except (KeyError, IndexError):
                self.Error(['Lamp Status : Invalid/Unexpected Response'])

            try:
                value = LampStatusState[response[6:7]]
                self.WriteStatus('LampStatus', value, {'Lamp': '2'})
            except (KeyError, IndexError):
                self.Error(['Lamp Status : Invalid/Unexpected Response'])

    def SetLensShift(self, value, qualifier):

        LensShiftState = {
            'Up': 'C5D\r',
            'Down': 'C5E\r',
            'Left': 'C5F\r',
            'Right': 'C60\r',
            }

        LensShiftCmdString = LensShiftState[value]
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'CF KEYEMU UP\r',
            'Down': 'CF KEYEMU DN\r',
            'Left': 'CF KEYEMU LEFT\r',
            'Right': 'CF KEYEMU RIGHT\r',
            'Enter': 'CF KEYEMU SELECT\r',
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayState = {
            'On': 'CF MENU ON\r',
            'Off': 'CF MENU OFF\r',
            }

        OnScreenDisplayCmdString = OnScreenDisplayState[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    # Operation Hours

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        response = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if response:
            try:
               value = int(response[-8:-1])
               self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours : Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'CF POWER ON\r',
            'Off': 'CF POWER OFF\r'
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStatusState = {
            '00': 'On',
            '80': 'Off',
            '20': 'Cooling Down',
            '40': 'Warming Up',
            '10': 'Power Fail',
            '88': 'Standby after Cooling Down (Abnormal Temp)',
            '24': 'Power Save (Cooling Down)',
            '04': 'Power Save',
            '21': 'Process Cooling Down after Off (Lamp Failure)',
            '28': 'Process Cooling Down (Abnormal Temperature)',
            '8C': 'Standby after Cooling Down (Shutter Mgmt)',
            '2C': 'Process Cooling Down after Off (Shutter Mgmt)',
            '81': 'Standby after Cooling Down (Lamp Failure)',
            }

        PowerStatusCmdString = 'CR STATUS\r'
        response = self.__UpdateHelper('Power', PowerStatusCmdString, value, qualifier)
        if response:
            try:
               value = PowerStatusState[response[-3:-1]]
               if value == 'On' or value == 'Off' or value == 'Cooling Down' or value == 'Warming Up':
                   self.WriteStatus('Power', value, qualifier)
                   self.WriteStatus('DeviceStatus', 'Normal', qualifier)
               elif value == 'Power Fail' or value == 'Power Save' or value == 'Standby after Cooling Down (Lamp Failure)' or value == 'Standby after Cooling Down (Shutter Mgmt)' or value == 'Standby after Cooling Down (Abnormal Temp)':
                   self.WriteStatus('Power', 'Off', qualifier)
                   self.WriteStatus('DeviceStatus', value, qualifier)
               elif value == 'Power Save (Cooling Down)' or value == 'Process Cooling Down after Off (Lamp Failure)' or value == 'Process Cooling Down (Abnormal Temperature)' or value == 'Process Cooling Down after Off (Shutter Mgmt)':
                   self.WriteStatus('Power', 'Cooling Down', qualifier)
                   self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': 'ON',
            'Off': 'OFF',
            }

        VideoMuteCmdString = 'CF VMUTE {0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            'ON': 'On',
            'OFF': 'Off',
            }

        VideoMuteCmdString = 'CR VMUTE\r'
        response = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if response:
            try:
               value = VideoMuteState[response[4:-1]]
               self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetZoom(self, value, qualifier):

        ZoomState = {
            'In': b'C47\r',
            'Out': b'C46\r',
            }

        ZoomCmdString = ZoomState[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?\r': 'Received data cannot be decoded or parameter designation error',
            '101\r': 'The function is not available in the selected Mode',
            '102\r': 'Selected value is out of range (Not reflected)',
            '103\r': 'Command mismatched to Hardware',
            '201\r': 'Incremented or decremented value are beyond upper or lower limits',
            '301\r': 'Not executable due to screen capturing in process',
            '402\r': 'Not executable due to a PIN code in operation'
            }

        if response in DEVICE_ERROR_CODES:
            segments = response.split('-')
            self.Error(['Error with {0} - Error Code: {1}: {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response])])
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

