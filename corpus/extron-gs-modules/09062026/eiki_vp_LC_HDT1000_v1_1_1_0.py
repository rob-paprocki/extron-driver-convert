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
        self.deviceUsername = 'Username'
        self.devicePassword = '0000'
        self.Models = {}


        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}}, 
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampSelect': { 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': { 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }
              
        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Authenticated'            
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPasswordPrompt, None)
            self.AddMatchString(re.compile(b'Hello'), self.__MatchLoginSuccess, None)
        else:
            self.Authenticated = 'Not Needed'

    def __MatchPasswordPrompt(self, match, tag):
        self.Authenticated = 'Not Authenticated'
        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginSuccess(self, match, tag):
        self.Authenticated = 'Authenticated'
    
    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
           'Full' : 'FULL',
           '4:3' : '43MODE',
           '16:9' : '169MODE',
           '16:10' : '1610MODE'
           }

        AspectRatioCmdString = 'CF SCREENASPECT {0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
           'FULL' : 'Full',
           '43MODE' : '4:3',
           '169MODE' : '16:9',
           '1610MODE' : '16:10'
           }

        AspectRatioCmdString = 'CR SCREENASPECT\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[4:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
           'CC1' : 'CC1',
           'CC2' : 'CC2',
           'CC3' : 'CC3',
           'CC4' : 'CC4',
           'Off' : 'OFF'
           }

        ClosedCaptionCmdString = 'CF CCAPTIONDISP {0}\r'.format(ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
           'CC1' : 'CC1',
           'CC2' : 'CC2',
           'CC3' : 'CC3',
           'CC4' : 'CC4',
           'OFF' : 'Off'
           }

        ClosedCaptionCmdString = 'CR CCAPTIONDISP\r'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionState[res[4:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def updateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
           'Mode 1' : 'RC',
           'Mode 2' : 'KEY',
           'Off' : 'NONE'
           }

        ExecutiveModeCmdString = 'CF KEYDIS {0}\r'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
           'RC' : 'Mode 1',
           'KEY' : 'Mode 2',
           'NONE' : 'Off'
           }

        ExecutiveModeCmdString = 'CR KEYDIS\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeState[res[4:-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
           'On' : 'ON',
           'Off' : 'OFF'
           }

        FreezeCmdString = 'CF FREEZE {0}\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
           'ON' : 'On',
           'OFF' : 'Off'
           }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[4:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputState = {
           'Input 1 Digital' : '1 DIGITAL',
           'Input 1 Analog' : '1 ANALOG',
           'Input 1 Video' : '1 VIDEO',
           'Input 1 S-Video' : '1 S-VIDEO',
           'Input 1 YPbPr' : '1 YPBPR',
           'Input 1 YCbCr' : '1 YCBCR',
           'Input 1 SDI 1' : '1 SDI1',
           'Input 1 SDI 2' : '1 SDI2',
           'Input 1 Scart' : '1 SCART',
           'Input 1 HDCP' : '1 HDCP',
           'Input 1 HDMI' : '1 HDMI',
           'Input 2 Digital' : '2 DIGITAL',
           'Input 2 Analog' : '2 ANALOG',
           'Input 2 Video' : '2 VIDEO',
           'Input 2 S-Video' : '2 S-VIDEO',
           'Input 2 YPbPr' : '2 YPBPR',
           'Input 2 YCbCr' : '2 YCBCR',
           'Input 2 SDI 1' : '2 SDI1',
           'Input 2 SDI 2' : '2 SDI2',
           'Input 2 Scart' : '2 SCART',
           'Input 2 HDCP' : '2 HDCP',
           'Input 2 HDMI' : '2 HDMI',
           'Input 3 Digital' : '3 DIGITAL',
           'Input 3 Analog' : '3 ANALOG',
           'Input 3 Video' : '3 VIDEO',
           'Input 3 S-Video' : '3 S-VIDEO',
           'Input 3 YPbPr' : '3 YPBPR',
           'Input 3 YCbCr' : '3 YCBCR',
           'Input 3 SDI 1' : '3 SDI1',
           'Input 3 SDI 2' : '3 SDI2',
           'Input 3 Scart' : '3 SCART',
           'Input 3 HDCP' : '3 HDCP',
           'Input 3 HDMI' : '3 HDMI',
           'Input 4 Digital' : '4 DIGITAL',
           'Input 4 Analog' : '4 ANALOG',
           'Input 4 Video' : '4 VIDEO',
           'Input 4 S-Video' : '4 S-VIDEO',
           'Input 4 YPbPr' : '4 YPBPR',
           'Input 4 YCbCr' : '4 YCBCR',
           'Input 4 SDI 1' : '4 SDI1',
           'Input 4 SDI 2' : '4 SDI2',
           'Input 4 Scart' : '4 SCART',
           'Input 4 HDCP' : '4 HDCP',
           'Input 4 HDMI' : '4 HDMI'
           }

        InputCmdString = 'CF INPUT{0}\r'.format(InputState[value])
        if 'YCbCr' not in value:
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
           'DIGITAL' : 'Digital',
           'ANALOG' : 'Analog',
           'VIDEO' : 'Video',
           'S-VIDEO' : 'S-Video',
           'YPBPR' : 'YPbPr',
           'SDI1' : 'SDI 1',
           'SDI2' : 'SDI 2',
           'SCART' : 'Scart',
           'HDCP' : 'HDCP',
           'HDMI' : 'HDMI'
           }

        InputCmdString = 'CR INPUT\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if 1 <= int(res[4:-1]) <= 4:
                    input_ = res[4:-1]
            except (ValueError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

        InputCmdString = 'CR SOURCE\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = 'Input {0} {1}'.format(input_, InputState[res[4:-1]])
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, NameError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
           'Normal' : 'NORMAL',
           'Eco 1' : 'ECO1',
           'Eco 2' : 'ECO2',
           'Auto' : 'AUTO'
           }

        LampModeCmdString = 'CF AUTOLAMPCONTRL {0}\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
           'NORMAL' : 'Normal',
           'ECO1' : 'Eco 1',
           'ECO2' : 'Eco 2',
           'AUTO' : 'Auto'
           }

        LampModeCmdString = 'CR AUTOLAMPCONTRL\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[4:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:9])
                self.WriteStatus('LampUsage', value, {'Lamp':'1'})

                value = int(res[10:15])
                self.WriteStatus('LampUsage', value, {'Lamp':'2'})
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetLampSelect(self, value, qualifier):

        LampSelectState = {
           'Lamp 1' : '1LAMP1',
           'Lamp 2' : '1LAMP2',
           'Lamp 1 and 2' : '2LAMP',
           'Auto' : '1LAMPAUTO',
           'Constant' : 'CONSTANT'
           }

        LampSelectCmdString = 'CF LAMPMODE {0}\r'.format(LampSelectState[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        LampSelectState = {
           '1LAMP1' : 'Lamp 1',
           '1LAMP2' : 'Lamp 2',
           '2LAMP' : 'Lamp 1 and 2',
           '1LAMPAUTO' : 'Auto',
           'CONSTANT' : 'Constant'
           }

        LampSelectCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = LampSelectState[res[4:-1]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Select: Invalid/unexpected response'])

    def SetLensShift(self, value, qualifier):

        LensShiftState = {
            'Up' : 'C5D',
            'Down' : 'C5E',
            'Left' : 'C5F',
            'Right' : 'C60'
            }

        LensShiftCmdString = LensShiftState[value]
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)
    def SetMenuCall(self, value, qualifier):

        MenuCallState = {
            'On' : 'ON',
            'Off' : 'OFF'
            }

        MenuCallCmdString = 'CF MENU {0}\r'.format(MenuCallState[value])
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up' : 'UP',
            'Down' : 'DN',
            'Left' : 'LEFT',
            'Right' : 'RIGHT',
            'Enter' : 'SELECT'
            }

        MenuNavigationCmdString = 'CF KEYEMU {0}\r'.format(MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerState = {
           'On' : 'ON',
           'Off' : 'OFF'
           }

        PowerCmdString = 'CF POWER {0}\r'.format(PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
           '00' : 'On',
           '80' : 'Off',
           '40' : 'Warming Up',
           '20' : 'Cooling Down',
           '10' : 'Power Fail',
           '24' : 'Power Save (Cooling Down)',
           '28' : 'Process Cooling Down (Abnormal Temperature)',
           '81' : 'Process Cooling Down after Off (Lamp Failure)',
           '2C' : 'Process Cooling Down after Off (Shutter Mgmt)',
           '88' : 'Standby after Cooling Down (Abnormal Temperature)',
           '21' : 'Standby after Cooling Down (Lamp Failure)',
           '8C' : 'Standby after Cooling Down (Shutter Mgmt)'
           }

        PowerCmdString = 'CR STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[4:-1]]
                if value == 'On' or value == 'Off' or value == 'Cooling Down' or value == 'Warming Up':
                   self.WriteStatus('Power', value, qualifier)
                   self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                elif value == 'Power Fail' or value == 'Standby after Cooling Down (Abnormal Temperature)' or value == 'Standby after Cooling Down (Shutter Mgmt)' or value == 'Standby after Cooling Down (Lamp Failure)':
                   self.WriteStatus('Power', 'Off', qualifier)
                   self.WriteStatus('DeviceStatus', value, qualifier)
                elif value == 'Process Cooling Down (Abnormal Temperature)' or value == 'Power Save (Cooling Down)' or value == 'Process Cooling Down after Off (Lamp Failure)' or value == 'Process Cooling Down after Off (Shutter Mgmt)':
                   self.WriteStatus('Power', 'Cooling Down', qualifier)
                   self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
           'On' : 'ON',
           'Off' : 'OFF'
           }

        VideoMuteCmdString = 'CF VMUTE {0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
           'ON' : 'On',
           'OFF' : 'Off'
           }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[4:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?' : 'Received data cannot be decoded',
            '101' : 'Specified function not available in selected mode',
            '102' : 'Specified value is out of range',
            '103' : 'Command mismatched to hardware',
            '201' : 'Incremented or decremented value(s) beyond upper or lower limit(s)',
            '301' : 'Not executable due to screen capturing in process',
            '402' : 'Not executable due to PIN code on operation'
        }

        if response.strip() in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response.strip()])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Not Needed', 'Authenticated']:
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
                    return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)           

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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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

