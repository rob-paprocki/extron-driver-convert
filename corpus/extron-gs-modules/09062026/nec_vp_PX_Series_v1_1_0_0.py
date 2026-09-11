from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re
from itertools import cycle


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
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AspectRatio_Set = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')
            self.AutoImage_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
            self.Freeze_Set = re.compile(b'(\x21\x98[\x00-xFF]{5})|(\xA1\x98[\x00-\xFF]{6})')
            self.Input_Set = re.compile(b'(\x22\x03[\x00-\xFF]{5})|(\xA2\x03[\x00-\xFF]{6})')
            self.LampMode_Set = re.compile(b'(\x23\xB1[\x00-\xFF]{6})|(\xA3\xB1[\x00-\xFF]{6})')
            self.MenuNavigation_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
            self.Power_Set = re.compile(b'(\x22[\x00|\x01][\x00-\xFF]{4})|(\xA2[\x00|\x01][\x00-\xFF]{5})')
            self.VideoMute_Set = re.compile(b'(\x22[\x10|\x11][\x00-\xFF]{4})|(\xA2[\x10|\x11][\x00-\xFF]{5})')

            self.AspectRatio_Update = re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})')
            self.DeviceStatus_Update = re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})')
            self.FilterUsage_Update = re.compile(b'(\x23\x8A[\x00-\xFF]{102})|(\xA3\x8A[\x00-\xFF]{6})')
            self.LampMode_Update = re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})')
            self.LampUsage_Update = re.compile(b'(\x23\x96[\x00-\xFF]{10}|\xA3\x96[\x00-\xFF]{6})')
            self.Power_Update = re.compile(b'(\x20\xBF[\x00-\xFF]{20})|(\xA0\xBF[\x00-\xFF]{6})')
            self.SignalStatus_Update = re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            'Normal': 0x00,
            'Letterbox': 0x01,
            '16:9': 0x02,
            'Wide Zoom': 0x03,
            '4:3 Fill': 0x04,
            '5:4': 0x0B,
            '16:10': 0x0C,
            '15:9': 0x0D,
            'Native': 0x0E
        }
        CKS = 0x30 + AspectRatioValues[value]
        AspectRatioCmdString = pack('>BBBBBBBBBBB', 0x03, 0x10, 0x00, 0x00, 0x05, 0x18, 0x00, 0x00, AspectRatioValues[value], 0x00, CKS)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioStates = {
            0x00: 'Normal',
            0x01: 'Letterbox',
            0x02: '16:9',
            0x03: 'Wide Zoom',
            0x04: '4:3 Fill',
            0x0B: '5:4',
            0x0C: '16:10',
            0x0D: '15:9',
            0x0E: 'Native'
        }
        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStates[res[12]]
                self.WriteStatus('AspectRatio', value, None)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Aspect Ratio')])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        DeviceStatusStateNames = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp cover error',
            b'\x02\x00\x00\x00': 'Temp error (bimetal)',
            b'\x10\x00\x00\x00': 'Fan error',
            b'\x20\x00\x00\x00': 'Power error',
            b'\x40\x00\x00\x00': 'Lamp 1 error',
            b'\x80\x00\x00\x00': 'Lamp 1 end of life',

            b'\x00\x01\x00\x00': 'Lamp 1 beyond limit',
            b'\x00\x02\x00\x00': 'Formatter error',
            b'\x00\x04\x00\x00': 'Lamp 2 error',

            b'\x00\x00\x02\x00': 'FPGA error',
            b'\x00\x00\x04\x00': 'Temp error (sensor)',
            b'\x00\x00\x08\x00': 'Lamp 1 housing error',
            b'\x00\x00\x10\x00': 'Lamp 1 data error',
            b'\x00\x00\x20\x00': 'Mirror cover error',
            b'\x00\x00\x40\x00': 'Lamp 2 end of life',
            b'\x00\x00\x80\x00': 'Lamp 2 beyond limit',

            b'\x00\x00\x00\x01': 'Lamp 2 housing error',
            b'\x00\x00\x00\x02': 'Lamp 2 data error',
            b'\x00\x00\x00\x04': 'High temp due to dust',
            b'\x00\x00\x00\x08': 'Foreign object sensor error',
            b'\x00\x00\x00\x10': 'Pump error',
        }
        res = self.__UpdateHelper('DeviceStatus', b'\x00\x88\x00\x00\x00\x88', value, qualifier)
        if res:
            try:
                value = DeviceStatusStateNames.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Device Status')])

    def UpdateFilterUsage(self, value, qualifier):
        res = self.__UpdateHelper('FilterUsage', b'\x03\x8A\x00\x00\x00\x8D', value, qualifier)
        if res:
            try:
                filterHoursValue = int(((res[94] << 24) + (res[93] << 16) + (res[92] << 8) + res[91]) / 3600)
                operationHoursValue = int(((res[102] << 24) + (res[101] << 16) + (res[100] << 8) + res[99]) / 3600)

                self.WriteStatus('FilterUsage', filterHoursValue, None)
                self.WriteStatus('OperationHours', operationHoursValue, None)
            except (ValueError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Filter Usage')])

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C',
            'On': b'\x01\x98\x00\x00\x01\x01\x9B'
        }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'HDMI': 0x1A,
            'Computer 1': 0x01,
            'Computer 2': 0x02,
            'Computer 3': 0x03,
            'DisplayPort': 0x1B,
            'Video': 0x06,
            'S-Video': 0x0B,
            'USB Viewer': 0x1F,
            'Network': 0x20
        }
        CKS = 0x08 + InputStateValues[value]
        InputCmdString = pack('>BBBBBBBB', 0x02, 0x03, 0x00, 0x00, 0x02, 0x01, InputStateValues[value], CKS)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeValues = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE'
        }
        LampModeCmdString = LampModeValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeStates = {
            0x00: 'Normal',
            0x01: 'Eco'
        }

        res = self.__UpdateHelper('LampMode', b'\x03\xB0\x00\x00\x01\x07\xBB', value, qualifier)
        if res:
            try:
                value = LampModeStates[res[6]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Lamp Mode')])

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdStrings = {
            '1': b'\x03\x96\x00\x00\x02\x00\x01\x9C',
            '2': b'\x03\x96\x00\x00\x02\x01\x01\x9D'
        }
        lampNum = qualifier['Lamp']
        res = self.__UpdateHelper('LampUsage', LampUsageCmdStrings[lampNum], value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(((res[10] << 24) + (res[9] << 16) + (res[8] << 8) + res[7]) / 3600), {'Lamp': lampNum})
            except (KeyError, IndexError, ValueError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Lamp Usage')])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Menu': 0x06,
            'Up': 0x07,
            'Down': 0x08,
            'Left': 0x0A,
            'Right': 0x09,
            'Enter': 0x0B,
            'Cancel': 0x0C
        }
        CKS = 0x13 + MenuNavigationValues[value]
        MenuNavigationCmdString = pack('>BBBBBBBB', 0x02, 0x0F, 0x00, 0x00, 0x02, MenuNavigationValues[value], 0x00, CKS)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateFilterUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': b'\x02\x01\x00\x00\x00\x03',
            'On': b'\x02\x00\x00\x00\x00\x02'
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            0x00: 'Off',
            0x02: 'Warming Up',
            0x03: 'Warming Up',
            0x04: 'On',
            0x05: 'Cooling Down',
            0x07: 'Cooling Down'
        }

        InputStateNames = {
            b'\x01\x06': 'HDMI',
            b'\x01\x01': 'Computer 1',
            b'\x02\x01': 'Computer 2',
            b'\x03\x01': 'Computer 3',
            b'\x02\x06': 'DisplayPort',
            b'\x01\x02': 'Video',
            b'\x01\x03': 'S-Video',
            b'\x01\x07': 'USB Viewer',
            b'\x02\x07': 'Network'
        }

        VideoMuteStateNames = {
            0x00: 'Off',
            0x01: 'On'
        }

        res = self.__UpdateHelper('Power', b'\x00\xBF\x00\x00\x01\x02\xC2', value, qualifier)
        if res:
            try:
                powerValue = PowerStateNames[res[6]]
                self.WriteStatus('Power', powerValue, None)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Power')])
            try:
                inputValue = InputStateNames[res[8:10]]
                self.WriteStatus('Input', inputValue, None)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Input')])
            try:
                videoMuteValue = VideoMuteStateNames[res[11]]
                self.WriteStatus('VideoMute', videoMuteValue, None)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Video Mute')])

    def UpdateSignalStatus(self, value, qualifier):
        SignalStatusStates = {
            0x01: 'No signal',
            0x00: 'Picture signal displaying',
            0x02: 'Viewer displaying',
            0x03: 'Test pattern displaying',
            0x04: 'LAN displaying'
        }

        res = self.__UpdateHelper('SignalStatus', b'\x00\x85\x00\x00\x01\x02\x88', value, qualifier)
        if res:
            try:
                value = SignalStatusStates[res[13]]
                self.WriteStatus('SignalStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Update Signal Status')])

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'Off': b'\x02\x11\x00\x00\x00\x13',
            'On': b'\x02\x10\x00\x00\x00\x12'
        }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def __CheckResponseForErrors(self, command, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'Unknown command.',
            b'\x00\x01': 'This current model does not support this function.',
            b'\x01\x00': 'Invalid values specificed.',
            b'\x01\x01': 'Specified terminal is unavailable or cannot be selected.',
            b'\x01\x02': 'Selected lanugage is not available.',
            b'\x02\x00': 'Available memory reservation error.',
            b'\x02\x02': 'Operating memory.',
            b'\x02\x03': 'Setting not possible.',
            b'\x02\x04': 'On forced on-screen mute mode.',
            b'\x02\x06': 'Displaying a signal other than PC Viewer.',
            b'\x02\x07': 'No signal.',
            b'\x02\x08': 'Displaying a test pattern or PC Card fills screen.',
            b'\x02\x09': 'No PC card is inserted.',
            b'\x02\x0A': 'Memory operation failed.',
            b'\x02\x0C': 'Displaying the Entry List.',
            b'\x02\x0D': 'Power Off inhibited.',
            b'\x02\x0E': 'Execution error.',
            b'\x02\x0F': 'No operation authority.',
            b'\x03\x00': 'Specified gain number is wrong.',
            b'\x03\x01': 'Selected gain is not available.',
            b'\x03\x02': 'Adjustment failed.'
        }
        if response[5:7] in DEVICE_ERROR_CODES and (response[0:1] in [b'\xA0', b'\xA1', b'\xA2', b'\xA3']):
            errorString = command + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]]
            self.Error([errorString])
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        SetDelim = {
            'AspectRatio': self.AspectRatio_Set,
            'AutoImage': self.AutoImage_Set,
            'Freeze': self.Freeze_Set,
            'Input': self.Input_Set,
            'LampMode': self.LampMode_Set,
            'MenuNavigation': self.MenuNavigation_Set,
            'Power': self.Power_Set,
            'VideoMute': self.VideoMute_Set,
        }

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
            res = b''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=SetDelim[command])
            if not res:
                self.Error(['Set {0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        UpdateDelim = {
            'AspectRatio': self.AspectRatio_Update,
            'DeviceStatus': self.DeviceStatus_Update,
            'FilterUsage': self.FilterUsage_Update,
            'LampMode': self.LampMode_Update,
            'LampUsage': self.LampUsage_Update,
            'Power': self.Power_Update,
            'SignalStatus': self.SignalStatus_Update,
        }

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=UpdateDelim[command])
            if not res:
                return ''
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
