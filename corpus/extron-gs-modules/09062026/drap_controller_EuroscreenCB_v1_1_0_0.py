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
        self._DeviceID = b'\x01'
        self._ChannelID = b'\x01\x00'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ControlCommand': {'Status': {}},
            'CurrentStatus': {'Status': {}},
            'FunctionSetting': {'Status': {}},
            'IDandChannel': {'Status': {}},
            'LimitSet': {'Status': {}},
            'LimitStatus': {'Parameters': ['Type'], 'Status': {}},
            'MotorStatus': {'Status': {}},
            'Position': {'Status': {}},
            'MotorHighestSpeed': {'Status': {}},
            'SpeedStatus': {'Status': {}},
            'VoltageStatus': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = pack('B', int(value))
        else:
            print('Invalid DeviceID, range is from 1 to 99 and Broadcast')


    @property
    def ChannelID(self):
        return self._ChannelID

    @ChannelID.setter
    def ChannelID(self, value):
        if 1 <= int(value) <= 16:
            self._ChannelID = pack('<H', 2 ** (int(value) - 1))
        else:
            print('Invalid ChannelID, range is from 1 to 99 and Broadcast')

    def calcChkSum(self, commandstring):
        ChkSum = 0
        for i in range(0, len(commandstring)):
            ChkSum = ChkSum ^ commandstring[i]
        return pack('B', int(ChkSum))

    def SetControlCommand(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xDD',
            'Stop': b'\xCC',
            'Down': b'\xEE',
            'Dot Move Up': b'\x0D',
            'Dot Move Down': b'\x0E',
            'Learn': b'\xAA',
            'Delete': b'\xA6',
            'Move to the Middle Limit 1': b'\x01',
            'Move to the Middle Limit 2': b'\x02',
            'Move to the Middle Limit 3': b'\x03',
            'Move to the Middle Limit 4': b'\x04'
        }

        ControlCommandCmdString = b''.join([self._DeviceID, self._ChannelID, b'\x0A', ValueStateValues[value]])
        checkSum = self.calcChkSum(ControlCommandCmdString)
        ControlCommandCmdString = b''.join([b'\x9A', ControlCommandCmdString, checkSum])
        self.__SetHelper('ControlCommand', ControlCommandCmdString, value, qualifier)

    def SetFunctionSetting(self, value, qualifier):

        ValueStateValues = {
            'No Light Touch Move, Default Direction, Dot Move': b'\x00',
            'No Light Touch Move, Default Direction, Continues Move': b'\x04',
            'No Light Touch Move, Opposite Direction, Dot Move': b'\x02',
            'No Light Touch Move, Opposite Direction, Continues Move': b'\x06',
            'With Light Touch Move, Default Direction, Dot Move': b'\x01',
            'With Light Touch Move, Default Direction, Continues Move': b'\x05',
            'With Light Touch Move, Opposite Direction, Dot Move': b'\x03',
            'With Light Touch Move, Opposite Direction, Continues Move': b'\x07'
        }

        FunctionSettingCmdString = b''.join([self._DeviceID, self._ChannelID, b'\xD5', ValueStateValues[value]])
        checkSum = self.calcChkSum(FunctionSettingCmdString)
        FunctionSettingCmdString = b''.join([b'\x9A', FunctionSettingCmdString, checkSum])
        self.__SetHelper('FunctionSetting', FunctionSettingCmdString, value, qualifier)

    def SetIDandChannel(self, value, qualifier):

        ValueStateValues = {
            'Select': b'\xAA',
            'Delete': b'\xA6'
        }

        IDandChannelCmdString = b''.join([self._DeviceID, self._ChannelID, ValueStateValues[value], ValueStateValues[value]])
        checkSum = self.calcChkSum(IDandChannelCmdString)
        IDandChannelCmdString = b''.join([b'\x9A', IDandChannelCmdString, checkSum])
        self.__SetHelper('IDandChannel', IDandChannelCmdString, value, qualifier)

    def SetLimitSet(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xDD',
            'Middle': b'\xCC',
            'Down': b'\xEE',
            'Keep': b'\xAA',
            'Delete Single': b'\xA6',
            'Delete All': b'\x00'
        }

        LimitSetCmdString = b''.join([self._DeviceID, self._ChannelID, b'\xDA', ValueStateValues[value]])
        checkSum = self.calcChkSum(LimitSetCmdString)
        LimitSetCmdString = b''.join([b'\x9A', LimitSetCmdString, checkSum])
        self.__SetHelper('LimitSet', LimitSetCmdString, value, qualifier)

    def SetMotorHighestSpeed(self, value, qualifier):

        ValueConstraints = {
            'Min': 50,
            'Max': 150
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MotorHighestSpeedCmdString = b''.join([self._DeviceID, self._ChannelID, b'\xD9', bytes([value])])
            checkSum = self.calcChkSum(MotorHighestSpeedCmdString)
            MotorHighestSpeedCmdString = b''.join([b'\x9A', MotorHighestSpeedCmdString, checkSum])
            self.__SetHelper('MotorHighestSpeed', MotorHighestSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotorHighestSpeed')

    def UpdateCurrentStatus(self, value, qualifier):
        self.UpdateMotorStatus(value, qualifier)
        
    def UpdateVoltageStatus(self, value, qualifier):
        self.UpdateMotorStatus(value, qualifier)
        
    def UpdateSpeedStatus(self, value, qualifier):
        self.UpdateMotorStatus(value, qualifier)
        
    def UpdatePosition(self, value, qualifier):
        self.UpdateMotorStatus(value, qualifier)
        
    def UpdateLimitStatus(self, value, qualifier):
        self.UpdateMotorStatus(value, qualifier)
    
    def UpdateMotorStatus(self, value, qualifier):

        LimitStatusValues = {
            '1': 'Set',
            '0': 'Not Set'
        }
        MotorStatusValues = {
            '1': 'Running',
            '0': 'Stopped'
        }
        PositionStateValues = {
            100: 'Close/Up Limit',
            0: 'Open/Down Limit'
        }

        MotorStatusCmdString = b''.join([self._DeviceID, self._ChannelID, b'\xCC\x00'])
        checkSum = self.calcChkSum(MotorStatusCmdString)
        MotorStatusCmdString = b''.join([b'\x9A', MotorStatusCmdString, checkSum])
        res = self.__UpdateHelper('MotorStatus', MotorStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4]
                self.WriteStatus('CurrentStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current Status: Invalid/unexpected response'])
            try:
                value = res[5]
                self.WriteStatus('VoltageStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Voltage Status: Invalid/unexpected response'])
            try:
                value = res[6]
                self.WriteStatus('SpeedStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Speed Status: Invalid/unexpected response'])

            try:
                value = PositionStateValues[res[7]]
                self.WriteStatus('Position', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Position: Invalid/unexpected response'])
            try:
                temp_byte = bin(res[8])[2:].zfill(8)
                value = MotorStatusValues[temp_byte[7]]
                self.WriteStatus('MotorStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Motor Status: Invalid/unexpected response'])
            try:
                temp_byte = bin(res[8])[2:].zfill(8)
                self.WriteStatus('LimitStatus', LimitStatusValues[temp_byte[6]], {'Type': 'Down Limit'})
                self.WriteStatus('LimitStatus', LimitStatusValues[temp_byte[5]], {'Type': 'Middle Limit 1'})
                self.WriteStatus('LimitStatus', LimitStatusValues[temp_byte[4]], {'Type': 'Middle Limit 2'})
                self.WriteStatus('LimitStatus', LimitStatusValues[temp_byte[3]], {'Type': 'Middle Limit 3'})
                self.WriteStatus('LimitStatus', LimitStatusValues[temp_byte[2]], {'Type': 'Middle Limit 4'})
            except (KeyError, IndexError):
                self.Error(['Limit Status: Invalid/unexpected response'])

    def SetPosition(self, value, qualifier):

        ValueStateValues = {
            'Close/Up Limit': b'\x64',
            'Open/Down Limit': b'\x00'
        }

        PositionCmdString = b''.join([self._DeviceID, self._ChannelID, b'\xDD', ValueStateValues[value]])
        checkSum = self.calcChkSum(PositionCmdString)
        PositionCmdString = b''.join([b'\x9A', PositionCmdString, checkSum])
        self.__SetHelper('Position', PositionCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            if not res:
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

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

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
