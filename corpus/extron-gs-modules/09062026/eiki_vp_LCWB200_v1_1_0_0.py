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
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PiPMode': {'Status': {}},
            'PiPPosition': {'Status': {}},
            'PiPSize': {'Status': {}},
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

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            print('Log in failed. Please supply proper Admin password')
        self.Authenticated = 'None'
        self.SetPassword(None, None)

    def __MatchAuthenticated(self, match, tag):

        self.Authenticated = 'Authenticated'
        self.PasswdPromptCount = 0

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'NORMAL',
            'Full': 'FULL',
            'Wide': 'WIDE',
            'Zoom': 'ZOOM',
            'True': 'TRUE',
            'Custom': 'CUSTOM',
            'D. Zoom Up': 'DZOOM UP',
            'D. Zoom Down': 'DZOOM DN'
        }

        AspectRatioCmdString = 'CF SCREEN {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'NORMAL': 'Normal',
            'FULL': 'Full',
            'WIDE': 'Wide',
            'ZOOM': 'Zoom',
            'TRUE': 'True',
            'CUSTOM': 'Custom'
        }

        AspectRatioCmdString = 'CR SCREEN\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AudioMuteCmdString = 'CF MUTE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        AudioMuteCmdString = 'CR MUTE\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r\n'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = 'CF FREEZE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        FreezeCmdString = 'CR FREEZE\r\n'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': 'COMPUTER1 ANALOG',
            'Component': 'COMPUTER1 YPBPR',
            'SCART': 'COMPUTER1 SCART',
            'RGB 2': 'COMPUTER2 ANALOG',
            'Video': 'VIDEO VIDEO',
            'S-Video': 'S-VIDEO S-VIDEO',
            'HDMI': 'HDMI HDMI'
        }

        InputCmdString = 'CF INPUT {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'RGB 1',
            '2': 'RGB 2',
            '3': 'HDMI',
            '4': 'Video',
            '5': 'S-Video'
        }

        InputCmdString = 'CR INPUT\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                RGB1Values = {
                    'ANALOG': 'RGB 1',
                    'YPBPR': 'Component',
                    'SCART': 'SCART'
                }

                if res[4] == '1':
                    res = self.__UpdateHelper('Input', 'CR SOURCE\r\n', value, qualifier)
                    if res:
                        try:
                            value = RGB1Values[res[4:-1]]
                        except (KeyError, IndexError):
                            print('Invalid/unexpected response for UpdateInput')
                else:
                    value = ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Normal': 'NORMAL',
            'Eco 1': 'ECO1',
            'Eco 2': 'ECO2'
        }

        LampModeCmdString = 'CF LAMPMODE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'AUTO': 'Auto',
            'NORMAL': 'Normal',
            'ECO1': 'Eco 1',
            'ECO2': 'Eco 2'
        }

        LampModeCmdString = 'CR LAMPMODE\r\n'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR3\r\n'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On': '1C',
            'Menu Off': '1D',
            'Right': '3A',
            'Left': '3B',
            'Up': '3C',
            'Down': '3D',
            'Enter': '3F'
        }

        MenuNavigationCmdString = 'C{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'DYNAMIC',
            'Standard': 'STAND',
            'Real': 'REAL',
            'Cinema': 'CINEMA',
            'Blackboard': 'BLACKBOARD',
            'Colorboard': 'COLORBOARD',
            'Custom 1': 'CUSTOM1',
            'Custom 2': 'CUSTOM2',
            'Custom 3': 'CUSTOM3',
            'Custom 4': 'CUSTOM4'
        }

        PictureModeCmdString = 'CF IMAGE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYNAMIC': 'Dynamic',
            'STAND': 'Standard',
            'REAL': 'Real',
            'CINEMA': 'Cinema',
            'BLACKBOARD': 'Blackboard',
            'COLORBOARD': 'Colorboard',
            'CUSTOM1': 'Custom 1',
            'CUSTOM2': 'Custom 1',
            'CUSTOM3': 'Custom 1',
            'CUSTOM4': 'Custom 4'
        }

        PictureModeCmdString = 'CR IMAGE\r\n'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPiPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'OFF',
            'PiP': 'PINP',
            'PbP': 'PBYP'
        }

        PiPModeCmdString = 'CF PIP {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PiPMode', PiPModeCmdString, value, qualifier)

    def UpdatePiPMode(self, value, qualifier):

        ValueStateValues = {
            'OFF': 'Off',
            'PINP': 'PiP',
            'PBYP': 'PbP'
        }

        PiPModeCmdString = 'CR PIP\r\n'
        res = self.__UpdateHelper('PiPMode', PiPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('PiPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePiPMode')

    def SetPiPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Right': 'BTMRIGHT',
            'Bottom Left': 'BTMLEFT',
            'Top Right': 'TOPRIGHT',
            'Top Left': 'TOPLEFT'
        }

        PiPPositionCmdString = 'CF PIPPOSITION {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PiPPosition', PiPPositionCmdString, value, qualifier)

    def UpdatePiPPosition(self, value, qualifier):

        ValueStateValues = {
            'BTMRIGHT': 'Bottom Right',
            'BTMLEFT': 'Bottom Left',
            'TOPRIGHT': 'Top Right',
            'TOPLEFT': 'Top Left'
        }

        PiPPositionCmdString = 'CR PIPPOSITION\r\n'
        res = self.__UpdateHelper('PiPPosition', PiPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('PiPPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePiPPosition')

    def SetPiPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': 'SMALL',
            'Middle': 'MIDDLE',
            'Large': 'LARGE'
        }

        PiPSizeCmdString = 'CF PIPSIZE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PiPSize', PiPSizeCmdString, value, qualifier)

    def UpdatePiPSize(self, value, qualifier):

        ValueStateValues = {
            'SMALL': 'Small',
            'MIDDLE': 'Middle',
            'LARGE': 'Large'
        }

        PiPSizeCmdString = 'CR PIPSIZE\r\n'
        res = self.__UpdateHelper('PiPSize', PiPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('PiPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePiPSize')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01',
        }

        PowerCmdString = 'C{0}\r\n'.format(ValueStateValues[value])
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

        PowerCmdString = 'CR STATUS\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                deviceStatusVal = ValueStateValues[res[4:-1]][1]
                self.WriteStatus('DeviceStatus', deviceStatusVal, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

            try:
                value = ValueStateValues[res[4:-1]][0]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        VideoMuteCmdString = 'CF VMUTE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE\r\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'CF VOLUME {0}\r\n'.format(str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'CR VOLUME\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?\r': 'Received data cannot be decoded.',
            '101\r': 'The function is not available in the selected Mode.',
            '102\r': 'Selected value is out of range.',
            '103\r': 'Command mismatched to hardware.',
            '201\r': 'Upper or lower data limit reached.',
            '301\r': 'Command cannot be executed during capturing display.',
            '302\r': 'Command cannot be executed during auto PC Operation.',
            '402\r': 'Command cannot be executed during PIN code operation.'
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
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
                if not res:
                    print('No Response')
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            print('Inappropriate	Command')

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
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            print('Inappropriate Command ', command)

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
