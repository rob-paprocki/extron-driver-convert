from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampStatus': {'Parameters': ['LampSelect'], 'Status': {}},
            'LampUsage': {'Parameters': ['LampSelect'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Normal': 'NORMAL',
            'Full': 'Full',
            'Zoom': 'ZOOM',
            'True': 'TRUE',
            'Custom': 'CUSTOM',
            'Natural': 'NATURAL'
        }
        AspectRatioCmdString = 'CF SCREEN {0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'R': 'Normal',
            'F': 'Full',
            'Z': 'Zoom',
            'T': 'True',
            'S': 'Custom',
            'U': 'Natural'
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        response = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier).decode()
        if response:
            try:
                value = AspectRatioState[response[-5]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
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
            'F': 'Off',
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
        }

        ClosedCaptionCmdString = 'CR CCAPTIONDISP\r'
        response = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier).decode()

        if response:
            try:
                value = ClosedCaptionState[response[-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': 'KEY',
            'Mode 2': 'RC',
            'Off': 'NONE',
        }

        ExecutiveModeCmdString = 'CF KEYDIS {0}\r'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Y': 'Mode 1',
            'C': 'Mode 2',
            'F': 'Off',
        }

        ExecutiveModeCmdString = 'CR KEYDIS\r'
        response = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier).decode()

        if response:
            try:
                value = ExecutiveModeState[response[-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'
        response = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier).decode()

        if response:
            try:
                value = int(response[-5:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'In': 'C4A\r',
            'Out': 'C4B\r',
        }
        FocusCmdString = FocusStateValues[value]
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
            'N': 'On',
            'F': 'Off',
        }

        FreezeCmdString = 'CR FREEZE\r'
        response = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier).decode()

        if response:
            try:
                value = FreezeState[response[-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Input 1 Ana. RGB': 'CF INPUT1 ANALOG\r',
            'Input 1 DVI (Digital)': 'CF INPUT1 DIGITAL\r',
            'Input 1 DVI (HDCP)': 'CF INPUT1 HDCP\r',
            'Input 1 SCART': 'CF INPUT1 SCART\r',
            'Input 1 HDMI': 'CF INPUT1 HDMI\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 S-Video': 'CF INPUT2 S-VIDEO\r',
            'Input 2 YPbPr': 'CF INPUT2 YPBPR\r',
            'Input 2 YCbCr': 'CF INPUT2 YCBCR\r',
            'Input 3 Digital': 'CF INPUT3 DIGITAL\r',
            'Input 3 RGB': 'CF INPUT3 ANALOG\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 YPbPr': 'CF INPUT3 YPBPR\r',
            'Input 3 YCbCr': 'CF INPUT3 YCBCR\r',
            'Input 3 SDI-1': 'CF INPUT3 S-SDI1\r',
            'Input 3 SDI-2': 'CF INPUT3 S-SDI2\r',
            'Input 3 HDCP': 'CF INPUT3 HDCP\r',
            'Input 3 SCART': 'CF INPUT3 SCART\r',
            'Input 3 HDMI': 'CF INPUT3 HDMI\r',
            'Input 4 DVI-D': 'CF INPUT4 DIGITAL\r',
            'Input 4 RGB': 'CF INPUT4 ANALOG\r',
            'Input 4 Video': 'CF INPUT4 VIDEO\r',
            'Input 4 S-Video': 'CF INPUT4 S-VIDEO\r',
            'Input 4 YCbCr': 'CF INPUT4 YCBCR\r',
            'Input 4 YPbPr': 'CF INPUT4 YPBPR\r',
            'Input 4 SDI-1': 'CF INPUT4 SDI1\r',
            'Input 4 SDI-2': 'CF INPUT4 SDI2\r',
            'Input 4 HDCP': 'CF INPUT4 HDCP\r',
            'Input 4 SCART': 'CF INPUT4 SCART\r',
            'Input 4 HDMI': 'CF INPUT4 HDMI\r',
        }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateValues = {
            '1DIGITAL\r': 'Input 1 DVI (Digital)',
            '1ANALOG\r': 'Input 1 Ana. RGB',
            '1HDCP\r': 'Input 1 DVI (HDCP)',
            '1SCART\r': 'Input 1 SCART',
            '1HDMI\r': 'Input 1 HDMI',
            '2VIDEO\r': 'Input 2 Video',
            '2S-VIDEO\r': 'Input 2 S-Video',
            '2YPbPr\r': 'Input 2 YPbPr',
            '2YCbCr\r': 'Input 2 YCbCr',
            '3DIGITAL\r': 'Input 3 Digital',
            '3ANALOG\r': 'Input 3 RGB',
            '3VIDEO\r': 'Input 3 Video',
            '3S-VIDEO\r': 'Input 3 S-Video',
            '3YPbPr\r': 'Input 3 YPbPr',
            '3YCbCr\r': 'Input 3 YCbCr',
            '3SDI1\r': 'Input 3 SDI-1',
            '3SDI2\r': 'Input 3 SDI-2',
            '3HDCP\r': 'Input 3 HDCP',
            '3SCART\r': 'Input 3 SCART',
            '3HDMI\r': 'Input 3 HDMI',
            '4DIGITAL\r': 'Input 4 DVI-D',
            '4ANALOG\r': 'Input 4 RGB',
            '4VIDEO\r': 'Input 4 Video',
            '4S-VIDEO\r': 'Input 4 S-Video',
            '4YPbPr\r': 'Input 4 YPbPr',
            '4YCbCr\r': 'Input 4 YCbCr',
            '4SDI1\r': 'Input 4 SDI-1',
            '4SDI2\r': 'Input 4 SDI-2',
            '4HDCP\r': 'Input 4 HDCP',
            '4SCART\r': 'Input 4 SCART',
            '4HDMI\r': 'Input 4 HDMI',
        }
        InputNumber = ''
        InputType = ''

        InputTypeCmdString = 'CR SOURCE\r'
        response2 = self.__UpdateHelper('Input', InputTypeCmdString, value, qualifier).decode()
        InputNumberCmdString = 'CR INPUT\r'
        response1 = self.__UpdateHelper('Input', InputNumberCmdString, value, qualifier).decode()
        if response1 and response2:
            try:
                InputNumber = response1[-2]
                InputType = response2[4:]
                value = InputStateValues[InputNumber + InputType]
                self.WriteStatus('Input', value, qualifier)
            except (ValueError, IndexError, KeyError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['LampSelect']
        if lamp in ['1', '2']:
            LampUsageCmdString = 'CR LAMPH\r'
            response = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier).decode()

            if response:
                try:
                    res = response.split()
                    Usage1 = int(res[1])
                    self.WriteStatus('LampUsage', Usage1, {'LampSelect': '1'})

                    Usage2 = int(res[2])
                    self.WriteStatus('LampUsage', Usage2, {'LampSelect': '2'})

                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateLampUsage')
        else:
            print('Invalid Command')

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Full': 'FULL',
            'Lamp 1': 'LAMP1',
            'Lamp 2': 'LAMP2',
        }

        LampModeCmdString = 'CF LAMPMODE {0}\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            'L': 'Full',
            '1': 'Lamp 1',
            '2': 'Lamp 2',
        }

        LampModeCmdString = 'CR LAMPMODE\r'
        response = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier).decode()

        if response:
            try:
                value = LampModeState[response[-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def SetLampPower(self, value, qualifier):

        LampPowerState = {
            'Normal': 'NORMAL',
            'Eco 1': 'ECO1',
            'Eco 2': 'ECO2',
        }

        LampPowerCmdString = 'CF AUTOLAMPCONTRL {0}\r'.format(LampPowerState[value])
        self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)

    def UpdateLampPower(self, value, qualifier):

        LampPowerState = {
            'L': 'Normal',
            '1': 'Eco 1',
            '2': 'Eco 2',
        }

        LampPowerCmdString = 'CR AUTOLAMPCONTRL\r'
        response = self.__UpdateHelper('LampPower', LampPowerCmdString, value, qualifier).decode()

        if response:
            try:
                value = LampPowerState[response[-2]]
                self.WriteStatus('LampPower', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampPower')

    def UpdateLampStatus(self, value, qualifier):

        LampStatusValues = {
            'I': 'Lamp On',
            'O': 'Lamp Off',
            'X': 'Lamp Failure',
        }

        lamp = qualifier['LampSelect']
        if lamp in ['1', '2']:
            LampStatusCmdString = 'CR LAMPSTS\r'
            response = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier).decode()
            if response:
                try:
                    value1 = LampStatusValues[response[5:6]]
                    self.WriteStatus('LampStatus', value1, {'LampSelect': '1'})

                    value2 = LampStatusValues[response[6:7]]
                    self.WriteStatus('LampStatus', value2, {'LampSelect': '2'})

                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateLampStatus')
        else:
            print('Invalid Command')

    def SetLensShift(self, value, qualifier):

        LensShiftStateValues = {
            'Up': 'C5D\r',
            'Down': 'C5E\r',
            'Left': 'C5F\r',
            'Right': 'C60\r',
        }

        LensShiftCmdString = LensShiftStateValues[value]
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': 'CF KEYEMU UP\r',
            'Down': 'CF KEYEMU DN\r',
            'Left': 'CF KEYEMU LEFT\r',
            'Right': 'CF KEYEMU RIGHT\r',
            'Enter': 'CF KEYEMU SELECT\r',
            'Menu On': 'CF MENU ON\r',
            'Menu Off': 'CF MENU OFF\r',
        }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        response = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier).decode()

        if response:
            try:
                value = int(response[-6:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

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
            '40': 'Warming Up',
            '20': 'Cooling Down',
            '10': 'Power Fail',
            '28': 'Cooling Down (Abnormal Temp)',
            '88': 'Standby after Cooling Down (Abnormal Temp)',
            '02': 'Invalid Command',
            '24': 'Power Save (Cooling Down)',
            '04': 'Power Save',
            '21': 'Cooling Down (Lamp Failure)',
            '81': 'Standby after Cooling Down (Lamp Failure)',
            '2C': 'Process Cooling Down after Off (Shutter Mgmt)',
            '8C': 'Standby after Cooling Down (Shutter Mgmt)',
        }

        PowerStatusCmdString = 'CR STATUS\r'
        response = self.__UpdateHelper('Power', PowerStatusCmdString, value, qualifier).decode()
        if response:
            try:
                value = PowerStatusState[response[-3:-1]]
                if value == 'On' or value == 'Off' or value == 'Cooling Down' or value == 'Warming Up' or value == 'Invalid Command':
                    if value == 'Invalid Command':
                        self.WriteStatus('DeviceStatus', value, qualifier)
                    else:
                        self.WriteStatus('Power', value, qualifier)
                        self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                elif value == 'Power Fail' or value == 'Power Save' or value == 'Standby after Cooling Down (Lamp Failure)' or value == 'Standby after Cooling Down (Shutter Mgmt)' or value == 'Standby after Cooling Down (Abnormal Temp)':
                    self.WriteStatus('Power', 'Off', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
                elif value == 'Power Save (Cooling Down)' or value == 'Cooling Down (Lamp Failure)' or value == 'Cooling Down (Abnormal Temp)' or value == 'Process Cooling Down after Off (Shutter Mgmt)':
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': 'ON',
            'Off': 'OFF',
        }

        VideoMuteCmdString = 'CF VMUTE {0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            'N': 'On',
            'F': 'Off',
        }

        VideoMuteCmdString = 'CR VMUTE\r'
        response = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier).decode()
        if response:
            try:
                value = VideoMuteState[response[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'In': 'C47\r',
            'Out': 'C46\r',
        }
        ZoomCmdString = ZoomStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?': 'Received data cannot be decoded or parameter designation error',
            '101': 'The function is not available in the selected Mode',
            '102': 'Selected value is out of range (Not reflected)',
            '103': 'Command mismatched to Hardware',
            '201': 'Incremented or decremented value are beyond upper or lower limits',
            '301': 'Not executable due to screen capturing in process',
            '402': 'Not executable due to a PIN code in operation'
        }

        if response.strip() in DEVICE_ERROR_CODES:
            errorString = '{0} {1} {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response.strip()])
            print(errorString)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
        if not res:
            print('Invalid/unexpected response')
        else:
            res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
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
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
