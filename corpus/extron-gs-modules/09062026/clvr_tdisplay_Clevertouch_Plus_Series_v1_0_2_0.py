from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aspect': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channels': {'Status': {}},
            'FunctionsofRemoteControl': {'Status': {}},
            'InputStatus': {'Status': {}},
            'Power': {'Status': {}},
            'PowerofPC': {'Status': {}},
            'TVchannels': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspect(self, value, qualifier):

        ValueStateValues = {
            '16:9': (0x08, 0x00, 0x00, 0x08),
            '4:3': (0x08, 0x01, 0x00, 0x09),
            'Point to point': (0x08, 0x07, 0x00, 0x0F)
        }

        Values = ValueStateValues[value]
        AspectCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Aspect', AspectCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': (0x03, 0x01, 0x00, 0x04),
            'Off': (0x03, 0x01, 0x01, 0x05)
        }

        Values = ValueStateValues[value]
        AudioMuteCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        AudioMuteCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x03, 0x03, 0x00, 0x06, 0xDD, 0xEE, 0xFF)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetChannels(self, value, qualifier):

        ValueStateValues = {
            'TV': (0x02, 0x01, 0x00, 0x03),
            'CVBS': (0x02, 0x02, 0x00, 0x04),
            'VGA3': (0x02, 0x0B, 0x00, 0x0D),
            'VGA1': (0x02, 0x03, 0x00, 0x05),
            'VGA2': (0x02, 0x04, 0x00, 0x06),
            'HDMI1': (0x02, 0x06, 0x00, 0x08),
            'HDMI2': (0x02, 0x07, 0x00, 0x09),
            'HDMI3': (0x02, 0x05, 0x00, 0x07),
            'PC': (0x02, 0x08, 0x00, 0x0A),
            'HDMI (4K*2K)': (0x02, 0x0D, 0x00, 0x0F),
            'Android': (0x02, 0x0A, 0x00, 0x0C)
        }

        Values = ValueStateValues[value]
        ChannelsCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Channels', ChannelsCmdString, value, qualifier)

    def SetFunctionsofRemoteControl(self, value, qualifier):

        ValueStateValues = {
            'WIN': (0x07, 0x0B, 0x00, 0x12),
            'Space': (0x07, 0x46, 0x00, 0x4D),
            'Alt+Tab': (0x07, 0x1D, 0x00, 0x24),
            'Alt+F4': (0x07, 0x1F, 0x00, 0x26),
            'NUM_1': (0x07, 0x00, 0x00, 0x07),
            'NUM_2': (0x07, 0x10, 0x00, 0x17),
            'NUM_3': (0x07, 0x11, 0x00, 0x18),
            'NUM_4': (0x07, 0x13, 0x00, 0x1A),
            'NUM_5': (0x07, 0x14, 0x00, 0x1B),
            'NUM_6': (0x07, 0x15, 0x00, 0x1C),
            'NUM_7': (0x07, 0x17, 0x00, 0x1E),
            'NUM_8': (0x07, 0x18, 0x00, 0x1F),
            'NUM_9': (0x07, 0x19, 0x00, 0x20),
            'NUM_0': (0x07, 0x1B, 0x00, 0x22),
            'Display': (0x07, 0x1C, 0x00, 0x23),
            'Refresh': (0x07, 0x4C, 0x00, 0x53),
            'Input': (0x07, 0x07, 0x00, 0x0E),
            'Home': (0x07, 0x48, 0x00, 0x4F),
            'Menu': (0x07, 0x0D, 0x00, 0x14),
            'Delete': (0x07, 0x40, 0x00, 0x47),
            'Energy': (0x07, 0x4E, 0x00, 0x55),
            'UP': (0x07, 0x47, 0x00, 0x4E),
            'DOWN': (0x07, 0x4D, 0x00, 0x54),
            'LEFT': (0x07, 0x49, 0x00, 0x50),
            'RIGHT': (0x07, 0x4B, 0x00, 0x52),
            'ENTER': (0x07, 0x4A, 0x00, 0x51),
            'Point': (0x07, 0x06, 0x00, 0x0D),
            'Back': (0x07, 0x0A, 0x00, 0x11),
            'CH+': (0x07, 0x02, 0x00, 0x09),
            'CH-': (0x07, 0x09, 0x00, 0x10),
            'VOL+': (0x07, 0x03, 0x00, 0x0A),
            'VOL-': (0x07, 0x41, 0x00, 0x48),
            'PageUp': (0x07, 0x42, 0x00, 0x49),
            'PageDown': (0x07, 0x0F, 0x00, 0x16),
            'F1': (0x07, 0x45, 0x00, 0x4C),
            'F2': (0x07, 0x12, 0x00, 0x19),
            'F3': (0x07, 0x51, 0x00, 0x58),
            'F4': (0x07, 0x5B, 0x00, 0x62),
            'F5': (0x07, 0x44, 0x00, 0x4B),
            'F6': (0x07, 0x50, 0x00, 0x57),
            'F7': (0x07, 0x43, 0x00, 0x4A),
            'F8': (0x07, 0x1A, 0x00, 0x21),
            'F9': (0x07, 0x04, 0x00, 0x0B),
            'F10': (0x07, 0x59, 0x00, 0x60),
            'F11': (0x07, 0x57, 0x00, 0x5E),
            'F12': (0x07, 0x08, 0x00, 0x0F),
            'RED': (0x07, 0x5C, 0x00, 0x63),
            'GREEN': (0x07, 0x5D, 0x00, 0x64),
            'YELLOW': (0x07, 0x5E, 0x00, 0x65),
            'BLUE': (0x07, 0x5F, 0x00, 0x66)
        }

        Values = ValueStateValues[value]
        FunctionsofRemoteControlCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('FunctionsofRemoteControl', FunctionsofRemoteControlCmdString, value, qualifier)

    def UpdateInputStatus(self, value, qualifier):

        ValueStateValues = {
            0x01: 'TV',
            0x02: 'AV',
            0x03: 'VGA 1',
            0x04: 'VGA 2',
            0x0B: 'VGA 3',
            0x06: 'HDMI 1',
            0x07: 'HDMI 2',
            0x05: 'HDMI 3',
            0x08: 'PC',
            0x0A: 'Android',
            0x0D: 'HDMI (4K*2K)',
            0x0C: 'WHDI'
        }

        InputStatusCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x02, 0x00, 0x00, 0x02, 0xDD, 0xEE, 0xFF)
        res = self.__UpdateHelper('InputStatus', InputStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('InputStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInputStatus')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': (0x01, 0x00, 0x00, 0x01),
            'Off': (0x01, 0x01, 0x00, 0x02)
        }

        Values = ValueStateValues[value]
        PowerCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        PowerCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x01, 0x02, 0x00, 0x03, 0xDD, 0xEE, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPowerofPC(self, value, qualifier):

        ValueStateValues = {
            'On': (0x09, 0x01, 0x00, 0x0A),
            'Off': (0x09, 0x00, 0x00, 0x09)
        }

        Values = ValueStateValues[value]
        PowerofPCCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, Values[0], Values[1], Values[2], Values[3], 0xDD, 0xEE, 0xFF)
        self.__SetHelper('PowerofPC', PowerofPCCmdString, value, qualifier)

    def UpdatePowerofPC(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off',
            0x02: 'Sleep',
            0x03: 'Hibernate'
        }

        PowerofPCCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x09, 0x02, 0x00, 0x0B, 0xDD, 0xEE, 0xFF)
        res = self.__UpdateHelper('PowerofPC', PowerofPCCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('PowerofPC', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePowerofPC')

    def SetTVchannels(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            crc = 0x05 + 0x00 + value
            TVchannelsCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x05, 0x00, value, crc, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('TVchannels', TVchannelsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTVchannels')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            crc = 0x03 + 0x00 + value
            VolumeCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x03, 0x00, value, crc, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('>BBBBBBBBBB', 0xAA, 0xBB, 0xCC, 0x03, 0x02, 0x00, 0x05, 0xDD, 0xEE, 0xFF)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
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
