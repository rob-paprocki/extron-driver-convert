from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'CallState': {'Status': {}},
            'CrosspointGain': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMute': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Parameters': ['Number'],'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PhoneLine': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }

    def UpdateCallState(self, value, qualifier):

        CallStatusState = {
            '1': 'Active',
            '0': 'Inactive'
        }

        CallStateCmdString = 'telringing\r'
        res = self.__UpdateHelper('CallState', CallStateCmdString, value, qualifier)
        if res:
            try:
                value = CallStatusState[res[3]]
                self.WriteStatus('CallState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Call State: Invalid/Unexpected Response'])

    def SetCrosspointGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        InputVal = qualifier['Input']
        MixBusVal = qualifier['Mix Bus']

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(InputVal) <= 3 and 1 <= int(MixBusVal) <= 24:
            CrosspointGainCmdString = 'xpgn({0},{1})={2}\r'.format(InputVal, MixBusVal, value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointGain')

    def UpdateCrosspointGain(self, value, qualifier):

        InputVal = qualifier['Input']
        MixBusVal = qualifier['Mix Bus']

        if 1 <= int(InputVal) <= 3 and 1 <= int(MixBusVal) <= 24:
            CrosspointGainCmdString = 'xpgn({0},{1})?\r'.format(InputVal, MixBusVal)
            res = self.__UpdateHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('CrosspointGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Crosspoint Gain: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointGain')

    def SetCrosspointMute(self, value, qualifier):

        CrosspointMuteState = {
            'On': '1',
            'Off': '0'
        }

        InputVal = qualifier['Input']
        MixBusVal = qualifier['Mix Bus']

        if 1 <= int(InputVal) <= 3 and 1 <= int(MixBusVal) <= 24:
            CrosspointMuteCmdString = 'xpmt({0},{1})={2}\r'.format(InputVal, MixBusVal, CrosspointMuteState[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        CrosspointMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        InputVal = qualifier['Input']
        MixBusVal = qualifier['Mix Bus']

        if 1 <= int(InputVal) <= 3 and 1 <= int(MixBusVal) <= 24:
            CrosspointMuteCmdString = 'xpmt({0},{1})?\r'.format(InputVal, MixBusVal)
            res = self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
            if res:
                try:
                    value = CrosspointMuteState[res[-3]]
                    self.WriteStatus('CrosspointMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Crosspoint Mute: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMute')

    def SetDTMF(self, value, qualifier):

        DTMFState = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '0': '0',
            '*': '*',
            '#': '#',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D'
        }

        DTMFCmdString = 'teldtmf="{0}"\r'.format(DTMFState[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        HookState = {
            'Dial': 'teldial=',
            'Flash': 'telflash?\r',
            'Redial': 'telredial\r'
        }

        if value == 'Dial':
            num = qualifier['Number']
            if num:
                HookCmdString = '{0}"{1}" \r'.format(HookState[value], num)
                self.__SetHelper('Hook', HookCmdString, value, qualifier)
        else:
            HookCmdString = HookState[value]
            self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -20,
            'Max': 20
        }

        InputVal = qualifier['Input']

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(InputVal) <= 3:
            InputGainCmdString = 'ingn({0})={1}\r'.format(InputVal, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputVal = qualifier['Input']

        if 1 <= int(InputVal) <= 3:
            InputGainCmdString = 'ingn({0})?\r'.format(InputVal)
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input Gain: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def SetInputMute(self, value, qualifier):

        InputMuteState = {
            'On': '1',
            'Off': '0'
        }

        InputVal = qualifier['Input']

        if 1 <= int(InputVal) <= 3:
            InputMuteCmdString = 'inmt({0})={1}\r'.format(InputVal, InputMuteState[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        InputVal = qualifier['Input']

        if 1 <= int(InputVal) <= 3:
            InputMuteCmdString = 'inmt({0})?\r'.format(InputVal)
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = InputMuteState[res[-3]]
                    self.WriteStatus('InputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Mute: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        OutputVal = qualifier['Output']

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(OutputVal) <= 24:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(OutputVal, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        OutputVal = qualifier['Output']

        if 1 <= int(OutputVal) <= 24:
            OutputGainCmdString = 'outgn({0})?\r'.format(OutputVal)
            res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('OutputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Output Gain: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputMute(self, value, qualifier):

        OutputMuteState = {
            'On': '1',
            'Off': '0'
        }

        OutputVal = qualifier['Output']

        if 1 <= int(OutputVal) <= 3:
            OutputMuteCmdString = 'outmt({0})={1}\r'.format(OutputVal, OutputMuteState[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        OutputVal = qualifier['Output']

        if 1 <= int(OutputVal) <= 3:
            OutputMuteCmdString = 'outmt({0})?\r'.format(OutputVal)
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = OutputMuteState[res[-3]]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Output Mute: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetPhoneLine(self, value, qualifier):

        PhoneLineState = {
            'Connected': 'telconn=1\r',
            'Disconnected': 'telconn=0\r'
        }

        PhoneLineCmdString = PhoneLineState[value]
        self.__SetHelper('PhoneLine', PhoneLineCmdString, value, qualifier)

    def UpdatePhoneLine(self, value, qualifier):

        PhoneLineState = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        PhoneLineCmdString = 'telconn?\r'
        res = self.__UpdateHelper('PhoneLine', PhoneLineCmdString, value, qualifier)
        if res:
            try:
                value = PhoneLineState[res[-3]]
                self.WriteStatus('PhoneLine', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Phone Line: Invalid/Unexpected Response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetRecallCmdString = 'recall({0})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetSaveCmdString = 'store({0})\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                return ''
            else:
                return res.decode()

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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
