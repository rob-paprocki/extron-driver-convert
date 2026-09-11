from extronlib.interface import SerialInterface, EthernetClientInterface

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
            'BassGain': {'Status': {}},
            'BassGainStatus': {'Status': {}},
            'Input': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MICGainStatus': {'Status': {}},
            'MICVolume': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'TrebleGain': {'Status': {}},
            'TrebleGainStatus': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetBassGain(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA5\x0C\x0C',
            'Down': b'\xA5\x12\x12'
        }

        BassGainCmdString = ValueStateValues[value]
        self.__SetHelper('BassGain', BassGainCmdString, value, qualifier)

    def UpdateBassGainStatus(self, value, qualifier):

        BassGainStatusCmdString = 'BD3490FV_B_GAIN_GET'
        res = self.__UpdateHelper('BassGainStatus', BassGainStatusCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[0])
                self.WriteStatus('BassGainStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateBassGainStatus')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xA5\x01\x01',
            '2': b'\xA5\x09\x09',
            '3': b'\xA5\x10\x10',
            '4': b'\xA5\x02\x02'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4'
        }

        InputCmdString = 'BD3490FV_SELECT'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 28
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = bytes([165, 80 + value, 80 + value])
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'BD3490FV_GAIN_GET'
        res = self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[0])
                self.WriteStatus('MasterVolume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateMasterVolume')

    def UpdateMICGainStatus(self, value, qualifier):

        MICGainStatusCmdString = 'PT2259_GAIN_GET'
        res = self.__UpdateHelper('MICGainStatus', MICGainStatusCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[0])
                self.WriteStatus('MICGainStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateMICGainStatus')

    def SetMICVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA5\x07\x07',
            'Down': b'\xA5\x0B\x0B'
        }

        MICVolumeCmdString = ValueStateValues[value]
        self.__SetHelper('MICVolume', MICVolumeCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\xA5\x05\x05'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteCmdString = 'MUTE'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA5\x11\x11',
            'Off': b'\xA5\x15\x15'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetTrebleGain(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA5\x08\x08',
            'Down': b'\xA5\x0D\x0D'
        }

        TrebleGainCmdString = ValueStateValues[value]
        self.__SetHelper('TrebleGain', TrebleGainCmdString, value, qualifier)

    def UpdateTrebleGainStatus(self, value, qualifier):

        TrebleGainStatusCmdString = 'BD3490FV_T_GAIN_GET'
        res = self.__UpdateHelper('TrebleGainStatus', TrebleGainStatusCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[0])
                self.WriteStatus('TrebleGainStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTrebleGainStatus')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 28
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = bytes([165, 76 - value, 76 - value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout).decode()
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

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
