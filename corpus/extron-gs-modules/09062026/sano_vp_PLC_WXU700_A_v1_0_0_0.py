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
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = '0000'

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Hello'), self.__MatchAuthenticated, None)   

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            print('Log in failed. Please supply proper Admin password')
        self.Authenticated = 'None'
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchAuthenticated(self, match, tag):

        self.Authenticated = 'Authenticated'
        self.PasswdPromptCount = 0

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'NORMAL',
            'True': 'TRUE',
            'Full': 'FULL',
            'Natural': 'NATURAL',
            'Custom': 'CUSTOM',
            'Zoom': 'ZOOM',
            'Wide': 'WIDE',
            'Zoom Up': 'DZOOM UP',
            'Zoom Down': 'DZOOM DN'
        }

        AspectRatioCmdString = 'CF SCREEN {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'R': 'Normal',
            'T': 'True',
            'F': 'Full',
            'U': 'Natural',
            'S': 'Custom',
            'Z': 'Zoom',
            'W': 'Wide'
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-5]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'C0B\r',
            'Off': 'C0C\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            'N': 'On',
            'F': 'Off'
        }

        AudioMuteCmdString = 'CR MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1': 'CC1',
            'CC2': 'CC2',
            'CC3': 'CC3',
            'CC4': 'CC4',
            'Off': 'OFF'
        }

        ClosedCaptionCmdString = 'CF CCAPTIONDISP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            'F': 'Off'
        }

        ClosedCaptionCmdString = 'CR CCAPTIONDISP\r'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'C43\r',
            'Off': 'C44\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'N': 'On',
            'F': 'Off'
        }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': 'C05\r',
            'Computer 2': 'C06\r',
            'Video': 'C07\r',
            'S-Video': 'C34\r',
            'HDMI': 'C04\r',
            'Network': 'C08\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'Computer 1',
            '2': 'Computer 2',
            '4': 'Video',
            '5': 'S-Video',
            '3': 'HDMI',
            '6': 'Network'
        }

        InputCmdString = 'CR1\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'High': 'HIGH',
            'Normal': 'NORMAL',
            'Eco': 'ECO',
            'Auto': 'AUTO'
        }

        LampModeCmdString = 'CF LAMPMODE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'G': 'High',
            'A': 'Normal',
            'C': 'Eco',
            'T': 'Auto'
        }

        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'C00\r',
            'Off': 'C01\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '00': ['On', 'Normal'],
            '80': ['Off', 'Normal'],
            '40': ['Warming Up', 'Normal'],
            '20': ['Cooling Down', 'Normal'],
            '10': ['Off', 'Power Failure'],
            '28': ['Cooling Down', 'Cooling Down (Temperature Anomaly)'],
            '88': ['Warming Up', 'Coming Back (Temperature Anomaly)'],
            '24': ['Cooling Down', 'Power Save (Cooling Down)'],
            '04': ['Off', 'Power Save'],
            '21': ['Cooling Down', 'Cooling Down (Lamp Failure)'],
            '81': ['Off', 'Standby after Cooling Down (Lamp Failure)']
        }

        PowerCmdString = 'CR0\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                deviceStatusValue = ValueStateValues[res[-3:-1]][1]
                self.WriteStatus('DeviceStatus', deviceStatusValue, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

            try:
                value = ValueStateValues[res[-3:-1]][0]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'C0D\r',
            'Off': 'C0E\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'N': 'On',
            'F': 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'CF VOLUME 0{0:02d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'CR VOLUME\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?\r': 'Received data cannot be decoded or parameter designation error',
            '101\r': 'The function is not available in the selected Mode',
            '102\r': 'Selected value is out of range (Not reflected)',
            '103\r': 'Command mismatched to Hardware',
            '201\r': 'Incremented or decremented value are beyond upper or lower limits',
            '301\r': 'Not executable due to screen capturing in process',
            '302\r': 'Not executable due to an Auto PC in operation',
            '303\r': 'Not executable due to a Memory Card Viewer in operation',
            '402\r': 'Not executable due to a PIN code in operation'
        }

        if response:
            if response in DEVICE_ERROR_CODES:
                print(DEVICE_ERROR_CODES[response])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Authenticated in ['Authenticated', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
                if not res:
                    print('No Response')
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Authenticated', 'Not Needed']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False
    
                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            print('Inappropriate Command ', command)
            return ''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
