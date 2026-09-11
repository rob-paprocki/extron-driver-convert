from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Flat': {'Status': {}},
            'Input': {'Status': {}},
            'Loudness': {'Status': {}},
            'Power': {'Status': {}},
            'Speaker': {'Parameters': ['Type'], 'Status': {}},
            'SpeakerToggle': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.regex = re.compile(b'\x01\x05\xC4\x64[\x00-\xFF]{4}')

    def SetFlat(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x03\xC4\x7B\x02\x45',
            'Off': b'\x01\x03\xC4\x47\x02\x11'
        }

        FlatCmdString = ValueStateValues[value]
        self.__SetHelper('Flat', FlatCmdString, value, qualifier)

    def UpdateFlat(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Disc': b'\x01\x03\xC4\x6A\x02\x34',
            'Aux': b'\x01\x03\xC4\x5E\x02\x28',
            'TV': b'\x01\x03\xC4\x59\x02\x23',
            'Tuner': b'\x01\x03\xC4\x46\x02\x10',
            'Tape': b'\x01\x03\xC4\x49\x02\x13'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLoudness(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x03\xC4\x75\x02\x3F',
            'Off': b'\x01\x03\xC4\x55\x02\x1F'
        }

        LoudnessCmdString = ValueStateValues[value]
        self.__SetHelper('Loudness', LoudnessCmdString, value, qualifier)

    def UpdateLoudness(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x03\xC4\x57\x02\x21',
            'Off': b'\x01\x03\xC4\x7A\x02\x44'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = b'\x01\x03\xC4\x64\x02\x2E'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerResult = '{0:08b}'.format(res[6])[0]
                value = ValueStateValues[PowerResult]
                self.WriteStatus('Power', value, qualifier)

                LoudResult = '{0:08b}'.format(res[6])[7]
                value = ValueStateValues[LoudResult]
                self.WriteStatus('Loudness', value, qualifier)

                FlatResult = '{0:08b}'.format(res[6])[6]
                value = ValueStateValues[FlatResult]
                self.WriteStatus('Flat', value, qualifier)

                SpeakerResult = '{0:08b}'.format(res[4])[6]
                value1 = ValueStateValues[SpeakerResult]
                self.WriteStatus('Speaker', value1, {'Type': 'A'})

                SpeakerResult = '{0:08b}'.format(res[4])[5]
                value2 = ValueStateValues[SpeakerResult]
                self.WriteStatus('Speaker', value2, {'Type': 'B'})

                SpeakerResult = '{0:08b}'.format(res[4])[4]
                value3 = ValueStateValues[SpeakerResult]
                self.WriteStatus('Speaker', value3, {'Type': 'C'})

                SpeakerResult = '{0:08b}'.format(res[4])[3]
                value4 = ValueStateValues[SpeakerResult]
                self.WriteStatus('Speaker', value4, {'Type': 'D'})

            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetSpeaker(self, value, qualifier):

        TypeStates = {
            'A': [0x68, 0x48],
            'B': [0x58, 0x78],
            'C': [0x6C, 0x4C],
            'D': [0x5C, 0x7C]
        }
        PowerState = ('On', 'Off')
        type1 = qualifier['Type']
        SpeakerCmdString = None
        if 'On' in PowerState and type1 in TypeStates:
            checksum = (0x01 + 0x03 + 0xC4 + TypeStates[type1][0] + 0x02) & 0xFF
            SpeakerCmdString = pack('>6B', 0x01, 0x03, 0xC4, TypeStates[type1][0], 0x02, checksum)
        elif 'Off' in PowerState and type1 in TypeStates:
            checksum = (0x01 + 0x03 + 0xC4 + TypeStates[type1][1] + 0x02) & 0xFF
            SpeakerCmdString = pack('>6B', 0x01, 0x03, 0xC4, TypeStates[type1][1], 0x02, checksum)
        else:
            print('Invalid Command')
        if SpeakerCmdString:
            self.__SetHelper('Speaker', SpeakerCmdString, value, qualifier)

    def UpdateSpeaker(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetSpeakerToggle(self, value, qualifier):

        SpeakerToggleCmdString = b'\x01\x03\xC4\x13\x02\xDD'
        self.__SetHelper('SpeakerToggle', SpeakerToggleCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x03\xC4\x00\x02\xCA',
            'Down': b'\x01\x03\xC4\x20\x02\xEA'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response, delimit):

        if response[-1] == delimit - 1:
            print('Command Ignored due to System busy')
            response = ''
        elif response[-1] == delimit - 2:
            self.Error(['Command not executed'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            delimit = commandstring[-1]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=2)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res, delimit)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                return ''
            else:
                return res

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
