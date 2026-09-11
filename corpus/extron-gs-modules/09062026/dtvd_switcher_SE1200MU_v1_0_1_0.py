from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceEthernetClass:

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
            'AuxBus': {'Status': {}},
            'FaderToBlack': {'Status': {}},
            'Preset': {'Status': {}},
            'Program': {'Status': {}},
            'TransitionControl': {'Parameters': ['Type'], 'Status': {}},
            'TransitionType': {'Status': {}},
        }

    def SetAuxBus(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        AuxBusCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x14, 0x00, 0x02, 0x00, ValueStateValues[value], 0x00, 0x00, 0x00)
        self.__SetHelper('AuxBus', AuxBusCmdString, value, qualifier)

    def UpdateAuxBus(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Black',
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x11: 'Matte'
        }

        AuxBusCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x14, 0x00, 0x02, 0x00)
        res = self.__UpdateHelper('AuxBus', AuxBusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('AuxBus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAuxBus')

    def SetFaderToBlack(self, value, qualifier):

        ValueStateValues = {
            'Enable': 0x01,
            'Disable': 0x00
        }

        FaderToBlackCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x85, 0x00, 0x02, 0x00, ValueStateValues[value], 0x00, 0x00, 0x00)
        self.__SetHelper('FaderToBlack', FaderToBlackCmdString, value, qualifier)

    def UpdateFaderToBlack(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Enable',
            0x00: 'Disable'
        }

        FaderToBlackCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x85, 0x00, 0x02, 0x00)
        res = self.__UpdateHelper('FaderToBlack', FaderToBlackCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('FaderToBlack', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFaderToBlack')

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        PresetCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x57, 0x00, 0x02, 0x00, ValueStateValues[value], 0x00, 0x00, 0x00)
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def UpdatePreset(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Black',
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x11: 'Matte'
        }

        PresetCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x57, 0x00, 0x02, 0x00)
        res = self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('Preset', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePreset')

    def SetProgram(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        ProgramCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x56, 0x00, 0x02, 0x00, ValueStateValues[value], 0x00, 0x00, 0x00)
        self.__SetHelper('Program', ProgramCmdString, value, qualifier)

    def UpdateProgram(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Black',
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x11: 'Matte'
        }

        ProgramCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x56, 0x00, 0x02, 0x00)
        res = self.__UpdateHelper('Program', ProgramCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('Program', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateProgram')

    def SetTransitionControl(self, value, qualifier):

        TypeStates = {
            'Background': 0x4f,
            'Key 1': 0x50,
            'Key 2': 0x51,
            'Priority': 0x52,
            'Preview': 0x53,
            'Reverse': 0x54,
            'Nm/Rv': 0x55
        }

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }
        type_ = qualifier['Type']
        if type_ in TypeStates:
            TransitionControlCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, TypeStates[type_], 0x00, 0x02, 0x00, ValueStateValues[value], 0x00, 0x00, 0x00)
            self.__SetHelper('TransitionControl', TransitionControlCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateTransitionControl(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }
        TypeStates = {
            'Background': 0x4f,
            'Key 1': 0x50,
            'Key 2': 0x51,
            'Priority': 0x52,
            'Preview': 0x53,
            'Reverse': 0x54,
            'Nm/Rv': 0x55
        }

        type_ = qualifier['Type']

        if type_ in TypeStates:
            TransitionControlCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, TypeStates[type_], 0x00, 0x02, 0x00)
            res = self.__UpdateHelper('TransitionControl', TransitionControlCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[12]]
                    self.WriteStatus('TransitionControl', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateTransitionControl')
        else:
            print('Invalid Command')

    def SetTransitionType(self, value, qualifier):

        ValueStateValues = {
            'Mix': (0x58, 0x02, 0x00),
            'Wipe': (0x58, 0x02, 0x01),
            'Cut': (0x07, 0x05, 0x00),
            'Auto': (0x00, 0x07, 0x01)
        }

        TransitionTypeCmdString = pack('>16B', 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, ValueStateValues[value][0], 0x00, ValueStateValues[value][1], 0x00, ValueStateValues[value][2], 0x00, 0x00, 0x00)
        self.__SetHelper('TransitionType', TransitionTypeCmdString, value, qualifier)

    def UpdateTransitionType(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Mix',
            0x01: 'Wipe',
        }

        TransitionTypeCmdString = pack('>12B', 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x58, 0x00, 0x02, 0x00)
        res = self.__UpdateHelper('TransitionType', TransitionTypeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('TransitionType', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTransitionType')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] not in [0x08, 0x10, 0x18]:
            print('{0} Invalid Command'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=16)
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

class DeviceSerialClass:

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
            'AuxBus': {'Status': {}},
            'FaderToBlack': {'Status': {}},
            'Preset': {'Status': {}},
            'Program': {'Status': {}},
            'TransitionControl': {'Parameters': ['Type'], 'Status': {}},
            'TransitionType': {'Status': {}},
        }

    def SetAuxBus(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        AuxBusCmdString = pack('>4B', 0x03, 0x00, 0xC4, ValueStateValues[value])
        self.__SetHelper('AuxBus', AuxBusCmdString, value, qualifier)

    def SetFaderToBlack(self, value, qualifier):

        FaderToBlackCmdString = pack('>4B', 0x03, 0x00, 0xC6, 0x1F)
        self.__SetHelper('FaderToBlack', FaderToBlackCmdString, value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        PresetCmdString = pack('>4B', 0x03, 0x00, 0xC2, ValueStateValues[value])
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def UpdatePreset(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Black',
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x11: 'Matte'
        }

        PresetCmdString = pack('>3B', 0x02, 0x00, 0x42)
        res = self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Preset', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePreset')

    def SetProgram(self, value, qualifier):

        ValueStateValues = {
            'Black': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            'Matte': 0x11
        }

        ProgramCmdString = pack('>4B', 0x03, 0x00, 0xC1, ValueStateValues[value])
        self.__SetHelper('Program', ProgramCmdString, value, qualifier)

    def UpdateProgram(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Black',
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x11: 'Matte'
        }

        ProgramCmdString = pack('>3B', 0x02, 0x00, 0x41)
        res = self.__UpdateHelper('Program', ProgramCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Program', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateProgram')

    def SetTransitionControl(self, value, qualifier):

        TypeStates = {
            'Background': 0x48,
            'Key 1': 0x49,
            'Key 2': 0x4B,
            'Preview': 0x4C,
            'Reverse': 0x1D
        }

        Tran = qualifier['Type']
        if Tran:
            TransitionControlCmdString = pack('>4B', 0x03, 0x00, 0xFB, TypeStates[Tran])
            self.__SetHelper('TransitionControl', TransitionControlCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetTransitionType(self, value, qualifier):

        ValueStateValues = {
            'Mix': 0x0F,
            'Wipe': 0x0E,
            'Cut': 0x4A,
            'Auto': 0x0B
        }

        TransitionTypeCmdString = pack('>4B', 0x03, 0x00, 0xC6, ValueStateValues[value])
        self.__SetHelper('TransitionType', TransitionTypeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=2)
            if not res:
                print('No Response')
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
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
                
class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

