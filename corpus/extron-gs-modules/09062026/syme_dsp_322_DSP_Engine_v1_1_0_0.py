from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

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
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Gain': {'Parameters': ['Channel', 'Type'], 'Status': {}},
            'MuteAllOutputs': {'Status': {}},
            'MuteOutput': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceID = value
        if DeviceID == 'Broadcast':
            DeviceID = 0
        DeviceID = int(DeviceID)
        if 0 <= DeviceID <= 250:
            self._DeviceID = DeviceID
        else:
            print('Module Parameter Device ID must be in range 0 - 250.')

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            0x00: 'Normal',
            0x01: 'Invalid Data',
            0x02: 'Invalid Command Code',
            0x03: 'Device Locked',
            0x04: 'Device Unlocked',
            0x05: 'Channels Muted',
            0x06: 'Channels Unmuted',
            0x07: 'Checksum Error',
            0x10: 'Flash Write Error',
            0x12: 'Invalid Password',
            0x13: 'Command Failed',
            0x14: 'Password Required',
            0x15: 'Insufficient DSP Resources'
        }

        DeviceStatusCmdString = pack('>BBBBBB', 0xFB, self._DeviceID, 0x00, 0x02, 0x00, 0xFE)
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusState[res[8]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Lock': 0x85,
            'Unlock': 0x86
        }

        cks = 0x19 + ExecutiveModeState[value]
        cks = cks & 0xFF
        cks = 0x0100 - cks & 0xFF
        ExecutiveModeCmdString = pack('>BBBBBB', 0xFB, self._DeviceID, 0x00, 0x19, ExecutiveModeState[value], cks)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 187
        }
        ChannelTypeStates = {
            'Input1': 0xC1,
            'Input2': 0xC2,
            'Output1': 0xC4,
            'Output2': 0xC6
        }
        Channel = qualifier['Type'] + qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Channel in ChannelTypeStates:
            Channel = ChannelTypeStates[Channel]
            cks = 0xA5 + Channel + value
            cks = cks & 0xFF
            cks = 0x0100 - cks & 0xFF
            GainCmdString = pack('>9B', 0xFB, self._DeviceID, 0x00, 0x05, 0xA0, 0x00, Channel, value, cks)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGain')

    def SetMuteAllOutputs(self, value, qualifier):

        MuteAllOutputsState = {
            'On': 0x89,
            'Off': 0x8A
        }

        cks = 0x02 + MuteAllOutputsState[value]
        cks = cks & 0xFF
        cks = 0x0100 - cks & 0xFF
        MuteAllOutputsCmdString = pack('>BBBBBB', 0xFB, self._DeviceID, 0x00, 0x02, MuteAllOutputsState[value], cks)
        self.__SetHelper('MuteAllOutputs', MuteAllOutputsCmdString, value, qualifier)

    def SetMuteOutput(self, value, qualifier):

        MuteOutputState = {
            'On': 0x87,
            'Off': 0x88
        }

        output = int(qualifier['Output'])

        cks = 0x03 + MuteOutputState[value] + output
        cks = cks & 0xFF
        cks = 0x0100 - cks & 0xFF
        MuteOutputCmdString = pack('>BBBBBBB', 0xFB, self._DeviceID, 0x00, 0x03, MuteOutputState[value], output, cks)
        self.__SetHelper('MuteOutput', MuteOutputCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        PresetRecallState = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04
        }

        cks = 0x85 + PresetRecallState[value]
        cks = cks & 0xFF
        cks = 0x0100 - cks & 0xFF
        PresetRecallCmdString = pack('>BBBBBBB', 0xFB, self._DeviceID, 0x00, 0x03, 0x82, PresetRecallState[value], cks)
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveState = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04
        }

        cks = 0x86 + PresetSaveState[value]
        cks = cks & 0xFF
        cks = 0x0100 - cks & 0xFF
        PresetSaveCmdString = pack('>BBBBBBB', 0xFB, self._DeviceID, 0x00, 0x03, 0x83, PresetSaveState[value], cks)
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            if not res:
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            print('Inappropriate Command ', command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
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
