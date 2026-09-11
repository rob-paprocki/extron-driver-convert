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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'InputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'MuteAll': {'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Route': {'Parameters': ['Input', 'Output'], 'Status': {}},
        }

    def escaped(self, Data):
        List = []
        Escaped = {
            0x02: [0x1B, 0x81],
            0x03: [0x1B, 0x82],
            0x06: [0x1B, 0x85],
            0x15: [0x1B, 0x94],
            0x1B: [0x1B, 0x9A]
        }

        for d in Data:
            List.extend(Escaped.get(d, [d]))
        return List

    def conversion(self, List):
        cmdStr = []
        for i in List:
            cmdStr.append(pack('>B', i))
        return b''.join(cmdStr)

    def reescaped(self, Data):
        Reescaped = {
            0x81: 0x02,
            0x82: 0x03,
            0x85: 0x06,
            0x94: 0x15,
            0x9A: 0x1B
        }

        List = []
        for d in Data.replace(b'\x1B', b''):
            List.append(Reescaped.get(d, d))
        return List

    def SetInputMute(self, value, qualifier):

        ChannelStates = {
            '1': 1,
            '2': 3,
            '3': 2,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7
        }

        ValueStateValues = {
            'On': 0x07,
            'Off': 0x08
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            temp = [0x05, 0x00, ValueStateValues[value], ChannelStates[channel]]
            list_ = self.escaped(temp)
            InputMuteCmdString = b''.join([b'\x02', self.conversion(list_), b'\x03'])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = qualifier['Channel']
        if 1 <= int(channel) <= 7:
            InputMuteCmdString = b'\x02\x05\x00\x1D\x03'
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    res = self.reescaped(res)
                    if res[3] == 0x1E:
                        temp1 = bin(res[4])[2:].zfill(7)
                        temp2 = bin(res[5])[2:].zfill(4)

                        self.WriteStatus('InputMute', ValueStateValues[temp1[0]], {'Channel': '7'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[1]], {'Channel': '6'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[2]], {'Channel': '5'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[3]], {'Channel': '4'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[4]], {'Channel': '2'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[5]], {'Channel': '3'})
                        self.WriteStatus('InputMute', ValueStateValues[temp1[6]], {'Channel': '1'})

                        self.WriteStatus('OutputMute', ValueStateValues[temp2[0]], {'Channel': '4'})
                        self.WriteStatus('OutputMute', ValueStateValues[temp2[1]], {'Channel': '2'})
                        self.WriteStatus('OutputMute', ValueStateValues[temp2[2]], {'Channel': '3'})
                        self.WriteStatus('OutputMute', ValueStateValues[temp2[3]], {'Channel': '1'})

                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputMute')
        else:
            print('Invalid Command')

    def SetInputVolume(self, value, qualifier):

        ChannelStates = {
            '1': 1,
            '2': 3,
            '3': 2,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7
        }

        ValueConstraints = {
            'Min': -62,
            'Max': 0
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel in ChannelStates:
            temp = [0x05, 0x00, 0x02, ChannelStates[channel], -value]
            list_ = self.escaped(temp)
            InputVolumeCmdString = b''.join([b'\x02', self.conversion(list_), b'\x03'])
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateInputVolume(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(channel) <= 7:
            InputVolumeCmdString = b'\x02\x05\x00\x1A\x03'
            res = self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
            if res:
                try:
                    res = self.reescaped(res)
                    if res[3] == 0x1B:
                        self.WriteStatus('InputVolume', -int(res[4]), {'Channel': '1'})
                        self.WriteStatus('InputVolume', -int(res[5]), {'Channel': '3'})
                        self.WriteStatus('InputVolume', -int(res[6]), {'Channel': '2'})
                        self.WriteStatus('InputVolume', -int(res[7]), {'Channel': '4'})
                        self.WriteStatus('InputVolume', -int(res[8]), {'Channel': '5'})
                        self.WriteStatus('InputVolume', -int(res[9]), {'Channel': '6'})
                        self.WriteStatus('InputVolume', -int(res[10]), {'Channel': '7'})

                        self.WriteStatus('OutputVolume', -int(res[11]), {'Channel': '1'})
                        self.WriteStatus('OutputVolume', -int(res[12]), {'Channel': '3'})
                        self.WriteStatus('OutputVolume', -int(res[13]), {'Channel': '2'})
                        self.WriteStatus('OutputVolume', -int(res[14]), {'Channel': '4'})

                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateInputVolume')
        else:
            print('Invalid Command')

    def SetMuteAll(self, value, qualifier):

        MuteAllCmdString = b'\x02\x05\x00\x10\x03'
        self.__SetHelper('MuteAll', MuteAllCmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ChannelStates = {
            '1': 1,
            '2': 3,
            '3': 2,
            '4': 4
        }

        ValueStateValues = {
            'On': 0x0E,
            'Off': 0x0F
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            temp = [0x05, 0x00, ValueStateValues[value], ChannelStates[channel]]
            list_ = self.escaped(temp)
            OutputMuteCmdString = b''.join([b'\x02', self.conversion(list_), b'\x03'])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateOutputMute(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(channel) <= 4:
            self.UpdateInputMute(value, {'Channel': channel})
        else:
            print('Invalid Command')

    def SetOutputVolume(self, value, qualifier):

        ChannelStates = {
            '1': 1,
            '2': 3,
            '3': 2,
            '4': 4
        }

        ValueConstraints = {
            'Min': -62,
            'Max': 0
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel in ChannelStates:
            temp = [0x05, 0x00, 0x04, ChannelStates[channel], -value]
            list_ = self.escaped(temp)
            OutputVolumeCmdString = b''.join([b'\x02', self.conversion(list_), b'\x03'])
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateOutputVolume(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(channel) <= 4:
            self.UpdateInputVolume(value, {'Channel': channel})
        else:
            print('Invalid Command')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\x02\x05\x00\x52\x03'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\x02\x05\x00\x51\x03'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def SetRoute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        input_channel = qualifier['Input']
        otput_channel = qualifier['Output']
        if 1 <= int(input_channel) <= 7 and 1 <= int(otput_channel) <= 4:
            temp = [0x05, 0x00, 0x05, int(input_channel), int(otput_channel), ValueStateValues[value]]
            list_ = self.escaped(temp)
            RouteCmdString = b''.join([b'\x02', self.conversion(list_), b'\x03'])
            self.__SetHelper('Route', RouteCmdString, value, qualifier)
        else:
            print('Invalid Command')
            
    def UpdateRoute(self, value, qualifier):

        RouteStates = {
            '0': 'On',
            '1': 'Off'
        }

        RequiredCommandCmdString = b'\x02\x05\x00\x17\x03'
        res = self.__UpdateHelper('Route', RequiredCommandCmdString, value, qualifier)
        if res:
            try:
                res = self.reescaped(res)
                if res[3] == 0x18:
                    for output in range(1, 5):
                        temp1 = bin(res[3 + output])[2:].zfill(7)
                        for input_number, bit_value in enumerate(temp1):
                            self.WriteStatus('Route', RouteStates[bit_value], {'Input': str(7 - input_number), 'Output': str(output)})

            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateRoute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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

