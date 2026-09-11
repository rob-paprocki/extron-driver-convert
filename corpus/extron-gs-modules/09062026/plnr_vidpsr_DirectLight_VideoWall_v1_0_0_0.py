from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
from struct import unpack
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
            'BlackBurst': {'Parameters': ['Display Column', 'Display Row', 'Output ID'], 'Status': {}},
            'LineBlanking': {'Parameters': ['Display Column', 'Display Row', 'Output ID'], 'Status': {}},
            'LoadPreset': {'Parameters': ['Display Column', 'Display Row', 'Output ID'], 'Status': {}},
            'LVIHDMIPort': {'Status': {}},
            'LVIOutputMuteStatus': {'Status': {}},
            'ToggleLVIOutputMute': {'Status': {}},
            'StorePreset': {'Parameters': ['Display Column', 'Display Row', 'Output ID'], 'Status': {}},
        }

        self.OutputIDStates = {
            'Broadcast': b'',
            '1': b'\x19',
            '2': b'\x1A',
            '3': b'\x1B',
            '4': b'\x1C'
        }

        self.updateLength = {
            'LVIHDMIPort': 256,
            'BlackBurst': 128,
        }

        self.setRegex = re.compile(b'(\x06|\x15)')

    def checkRowColID(self, qual):
        return ((qual['Display Column'] == 'Broadcast' and qual['Display Row'] == 'Broadcast') or
                (qual['Display Column'] != 'Broadcast' and qual['Display Row'] != 'Broadcast' and qual['Output ID'] != 'Broadcast') or
                (qual['Display Column'] == '1' and qual['Display Row'] == '1'))

    def SetBlackBurst(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and self.checkRowColID(qualifier):
            if(qualifier['Display Row'] == 'Broadcast'):
                row = b'\x00'
            else:
                row = pack('>B', int(qualifier['Display Row']))
            if(qualifier['Display Column'] == 'Broadcast'):
                column = b'\x00'
            else:
                column = pack('>B', int(qualifier['Display Column']))

            BlackBurstCmdString = b'\x00\x1D' + row + column + b'\x00\x31' + pack('>I', 0) + pack('>H', value) + pack('>QIH', 0, 0, 0)
            checksum = 0
            for i in BlackBurstCmdString:
                checksum = checksum + i
            checksum = checksum & 255
            BlackBurstCmdString = self.OutputIDStates[qualifier['Output ID']] + b'\x55' + BlackBurstCmdString + pack('>B', checksum) + b'\xAA'
            self.__SetHelper('BlackBurst', BlackBurstCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBlackBurst(self, value, qualifier):

        if self.checkRowColID(qualifier):
            if(qualifier['Display Row'] == 'Broadcast'):
                row = b'\x00'
            else:
                row = pack('>B', int(qualifier['Display Row']))
            if(qualifier['Display Column'] == 'Broadcast'):
                column = b'\x00'
            else:
                column = pack('>B', int(qualifier['Display Column']))

            BlackBurstCmdString = b'\x00\x1D' + row + column + b'\x00\x1C' + pack('>IQQ', 0, 0, 0)
            checksum = 0
            for i in BlackBurstCmdString:
                checksum = checksum + i
            checksum = checksum & 255
            BlackBurstCmdString = self.OutputIDStates[qualifier['Output ID']] + b'\x55' + BlackBurstCmdString + pack('>B', checksum) + b'\xAA'

            res = self.__UpdateHelper('BlackBurst', BlackBurstCmdString, value, qualifier)
            if res:
                try:
                    value = int(unpack('>H', res[57:59])[0])
                    self.WriteStatus('BlackBurst', value, qualifier)
                    value = int(unpack('>H', res[59:61])[0])
                    self.WriteStatus('LineBlanking', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/Unexpected Response for UpdateBlackBurst')
        else:
            print('Invalid Command')

    def SetLineBlanking(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and self.checkRowColID(qualifier):
            if(qualifier['Display Row'] == 'Broadcast'):
                row = b'\x00'
            else:
                row = pack('>B', int(qualifier['Display Row']))
            if(qualifier['Display Column'] == 'Broadcast'):
                column = b'\x00'
            else:
                column = pack('>B', int(qualifier['Display Column']))

            LineBlankingCmdString = b'\x00\x1D' + row + column + b'\x00\x32' + pack('>I', 0) + pack('>H', value) + pack('>QIH', 0, 0, 0)
            checksum = 0
            for i in LineBlankingCmdString:
                checksum = checksum + i
            checksum = checksum & 255
            LineBlankingCmdString = self.OutputIDStates[qualifier['Output ID']] + b'\x55' + LineBlankingCmdString + pack('>B', checksum) + b'\xAA'
            self.__SetHelper('LineBlanking', LineBlankingCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateLineBlanking(self, value, qualifier):

        self.UpdateBlackBurst(value, qualifier)

    def SetLoadPreset(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x00',
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04'
        }

        if(self.checkRowColID(qualifier)):
            if(qualifier['Display Row'] == 'Broadcast'):
                row = b'\x00'
            else:
                row = pack('>B', int(qualifier['Display Row']))
            if(qualifier['Display Column'] == 'Broadcast'):
                column = b'\x00'
            else:
                column = pack('>B', int(qualifier['Display Column']))

            LoadPresetCmdString = b'\x00\x1D' + row + column + b'\x00\x2E' + pack('>I', 0) + ValueStateValues[value] + pack('>QIHB', 0, 0, 0, 0)
            checksum = 0
            for i in LoadPresetCmdString:
                checksum = checksum + i
            checksum = checksum & 255
            LoadPresetCmdString = self.OutputIDStates[qualifier['Output ID']] + b'\x55' + LoadPresetCmdString + pack('>B', checksum) + b'\xAA'
            self.__SetHelper('LoadPreset', LoadPresetCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetToggleLVIOutputMute(self, value, qualifier):

        ToggleLVIOutputMuteCmdString = b'\x00\x1D\x01\x01\x02\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        checksum = 0
        for i in ToggleLVIOutputMuteCmdString:
            checksum = checksum + i
        checksum = checksum & 255
        ToggleLVIOutputMuteCmdString = b'\x55' + ToggleLVIOutputMuteCmdString + pack('>B', checksum) + b'\xAA'
        self.__SetHelper('ToggleLVIOutputMute', ToggleLVIOutputMuteCmdString, value, qualifier)

    def SetLVIHDMIPort(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x00',
            'HDMI 2 Only': b'\x01',
            'HDMI 1 Only': b'\x02'
        }

        LVIHDMIPortCmdString = b'\x00\x1D\x01\x01\x04\x02\x00\x00\x00\x00' + ValueStateValues[value] + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        checksum = 0
        for i in LVIHDMIPortCmdString:
            checksum = checksum + i
        checksum = checksum & 255
        LVIHDMIPortCmdString = b'\x55' + LVIHDMIPortCmdString + pack('>B', checksum) + b'\xAA'
        self.__SetHelper('LVIHDMIPort', LVIHDMIPortCmdString, value, qualifier)

    def UpdateLVIHDMIPort(self, value, qualifier):

        LVIOutputMuteValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }
        LVIHDMIPortValues = {
            b'\x00': 'Auto',
            b'\x02': 'HDMI 1 Only',
            b'\x01': 'HDMI 2 Only'
        }

        LVIHDMIPortCmdString = b'\x55\x00\x1D\x01\x01\x02\x72' + pack('>IQQ', 0, 0, 0) + b'\x93\xAA'
        res = self.__UpdateHelper('LVIHDMIPort', LVIHDMIPortCmdString, value, qualifier)
        if res:
            try:
                value = LVIOutputMuteValues[res[31:32]]
                self.WriteStatus('LVIOutputMuteStatus', value, qualifier)
                value = LVIHDMIPortValues[res[32:33]]
                self.WriteStatus('LVIHDMIPort', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLVIHDMIPort')

    def UpdateLVIOutputMuteStatus(self, value, qualifier):

        self.UpdateLVIHDMIPort(value, qualifier)

    def SetStorePreset(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x00',
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04'
        }

        if(self.checkRowColID(qualifier)):
            if(qualifier['Display Row'] == 'Broadcast'):
                row = b'\x00'
            else:
                row = pack('>B', int(qualifier['Display Row']))
            if(qualifier['Display Column'] == 'Broadcast'):
                column = b'\x00'
            else:
                column = pack('>B', int(qualifier['Display Column']))

            StorePresetCmdString = b'\x00\x1D' + row + column + b'\x00\x2F' + pack('>I', 0) + ValueStateValues[value] + pack('>QIHB', 0, 0, 0, 0)
            checksum = 0
            for i in StorePresetCmdString:
                checksum = checksum + i
            checksum = checksum & 255
            StorePresetCmdString = self.OutputIDStates[qualifier['Output ID']] + b'\x55' + StorePresetCmdString + pack('>B', checksum) + b'\xAA'
            self.__SetHelper('StorePreset', StorePresetCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if(response[0] == b'\x15'):
            response = ''
            print('Command Failed.')
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
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
            
            if command == 'BlackBurst':
                if qualifier['Display Row'] == 'Broadcast':
                    print('Inappropriate Command')
                    return ''
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=self.updateLength[command])
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
