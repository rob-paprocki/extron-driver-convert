from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 3.0
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentStatus': {'Parameters': ['Device ID'], 'Status': {}},
            'EmergencyOff': {'Parameters': ['Device ID'], 'Status': {}},
            'Enumerate': {'Status': {}},
            'OutletControl': {'Parameters': ['Device ID', 'BankSelect'], 'Status': {}},
            'OutletControlCNMP': {'Parameters': ['Device ID'], 'Status': {}},
            'PowerStatus': {'Parameters': ['Device ID'], 'Status': {}},
            'PowerStatusRequired': {'Status': {}},
            'PowerStatusVA': {'Parameters': ['Device ID'], 'Status': {}},
            'Reset': {'Parameters': ['Device ID'], 'Status': {}},
            'SequenceControl': {'Parameters': ['Device ID'], 'Status': {}},
            'VoltageStatus': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.deviceIDRex = re.compile('\$ACK ([0-9]{1,2})')
        self.bankIDRex = re.compile('BANK([1-3])=(ON|OFF)')
        self.currentRex = re.compile('CURRENT=([0-9.]{0,7})')
        self.powerRex = re.compile('WATTS=([0-9]{0,4})')
        self.powerVARex = re.compile('VA=([0-9]{0,3})')
        self.voltageRex = re.compile('VOLTAGE=([0-9.]{0,7})')

    def UpdateCurrentStatus(self, value, qualifier):

        devID = qualifier['Device ID']
        if 'All' == devID or 0 <= int(devID) <= 32:
            CurrentStatusCmdString = '?CURRENT {0}\r'.format(devID)
            res = self.__UpdateHelper('CurrentStatus', CurrentStatusCmdString, value, qualifier)
            if res:
                try:
                    deviceID = re.match(self.deviceIDRex, res).group(1)
                    value = re.search(self.currentRex, res).group(1)
                    self.WriteStatus('CurrentStatus', value, {'Device ID': deviceID})
                except(ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateCurrentStatus')
        else:
            print('Invalid Command for UpdateCurrentStatus')

    def SetEmergencyOff(self, value, qualifier):

        devID = qualifier['Device ID']

        if 'All' == devID or 0 <= int(devID) <= 32:
            if devID != 'All':
                EmergencyOffCmdString = '!ALL_OFF {0}\r'.format(devID)
            else:
                EmergencyOffCmdString = '!ALL_OFF\r'

            self.__SetHelper('EmergencyOff', EmergencyOffCmdString, value, qualifier)
        else:
            print('Invalid Command for SetEmergencyOff')

    def SetEnumerate(self, value, qualifier):

        EnumerateCmdString = '!ENUMERATE\r'
        self.__SetHelper('Enumerate', EnumerateCmdString, value, qualifier)

    def SetOutletControlCNMP(self, value, qualifier):

        OutletControlStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        devID = qualifier['Device ID']

        if 'All' == devID or 0 <= int(devID) <= 32:
            if devID != 'All':
                OutletControlCmdString = '!BANK_{0} {1} 1\r'.format(OutletControlStateValues[value], devID)
            else:
                OutletControlCmdString = '!BANK_{0} 1\r'.format(OutletControlStateValues[value])

            self.__SetHelper('OutletControlCNMP', OutletControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutletControlCNMP')

    def UpdateOutletControlCNMP(self, value, qualifier):

        self.SetBankUpdateHandler(value, qualifier)

    def SetOutletControl(self, value, qualifier):

        OutletControlStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        devID = qualifier['Device ID']
        qRange = int(qualifier['BankSelect'])

        if 'All' == devID or 0 <= int(devID) <= 32:
            if 0 < qRange <= 3:
                if devID != 'All':
                    OutletControlCmdString = '!BANK_{0} {1} {2}\r'.format(OutletControlStateValues[value], devID, qRange)
                else:
                    OutletControlCmdString = '!BANK_{0} {1}\r'.format(OutletControlStateValues[value], qRange)

                self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutletControl')

    def UpdateOutletControl(self, value, qualifier):

        self.SetBankUpdateHandler(value, qualifier)

    def SetBankUpdateHandler(self, value, qualifier):

        OutletControlStateNames = {
            'ON': 'On',
            'OFF': 'Off',
        }

        devID = qualifier['Device ID']
        if 'All' == devID or 0 <= int(devID) <= 32:
            OutletControlCmdString = '?BANK_STAT {0}\r'.format(devID)

            res = self.__UpdateHelper('OutletControl', OutletControlCmdString, value, qualifier)
            if res:
                deviceID = re.findall(self.deviceIDRex, res)
                bankID = re.findall(self.bankIDRex, res)
                for bank, value in bankID:
                    if bank == '1':
                        self.WriteStatus('OutletControlCNMP', OutletControlStateNames[value], {'Device ID': str(deviceID[0])})
                    self.WriteStatus('OutletControl', OutletControlStateNames[value], {'Device ID': str(deviceID[0]), 'BankSelect': str(bank)})
            else:
                print('Invalid Command for SetBankUpdateHandler')
        else:
            print('Invalid Command for SetBankUpdateHandler')

    def UpdatePowerStatus(self, value, qualifier):

        devID = qualifier['Device ID']
        if 'All' == devID or 0 <= int(devID) <= 32:
            PowerStatusCmdString = '?POWER {0}\r'.format(devID)
            res = self.__UpdateHelper('PowerStatus', PowerStatusCmdString, value, qualifier)
            if res:
                try:
                    deviceID = re.match(self.deviceIDRex, res).group(1)
                    value = re.search(self.powerRex, res).group(1)
                    self.WriteStatus('PowerStatus', value, {'Device ID': deviceID})
                except(ValueError, IndexError):
                    print('Invalid/unexpected response for UpdatePowerStatus')
        else:
            print('Invalid Command for UpdatePowerStatus')

    def UpdatePowerStatusRequired(self, value, qualifier):

        PowerStatusCmdString = '?POWER {0}\r'.format(self.DeviceID)
        res = self.__UpdateHelper('PowerStatusRequired', PowerStatusCmdString, value, qualifier)
        if res:
            try:
                deviceID = re.match(self.deviceIDRex, res).group(1)
                value = re.search(self.powerRex, res).group(1)
                self.WriteStatus('PowerStatus', value, {'Device ID': deviceID})
            except(ValueError, IndexError):
                print('Invalid/unexpected response for UpdatePowerStatusRequired')

    def UpdatePowerStatusVA(self, value, qualifier):

        devID = qualifier['Device ID']

        if 'All' == devID or 0 <= int(devID) <= 32:
            PowerStatusVACmdString = '?POWER_VA {0}\r'.format(devID)
            res = self.__UpdateHelper('PowerStatusVA', PowerStatusVACmdString, value, qualifier)
            if res:
                try:
                    deviceID = re.match(self.deviceIDRex, res).group(1)
                    value = re.search(self.powerVARex, res).group(1)
                    self.WriteStatus('PowerStatusVA', value, {'Device ID': deviceID})
                except(ValueError, IndexError):
                    print('Invalid/unexpected response for UpdatePowerStatusVA')
        else:
            print('Invalid Command for UpdatePowerStatusVA')

    def SetReset(self, value, qualifier):

        devID = qualifier['Device ID']

        if 'All' == devID or 0 <= int(devID) <= 32:
            if 'All' != devID and 0 <= int(devID) <= 32:
                ResetCmdString = '!RESET {0}\r'.format(devID)
            else:
                ResetCmdString = '!RESET\r'
            self.__SetHelper('Reset', ResetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetReset')

    def SetSequenceControl(self, value, qualifier):

        SequenceNames = {
            'On': 'ON',
            'Off': 'OFF',
        }
        devID = qualifier['Device ID']

        if 'All' == devID or 0 <= int(devID) <= 32:
            if devID != 'All':
                SequenceControlCmdString = '!SEQ_{0} {1}\r'.format(SequenceNames[value], devID)
            else:
                SequenceControlCmdString = '!SEQ_{0}\r'.format(SequenceNames[value])

            self.__SetHelper('SequenceControl', SequenceControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSequenceControl')

    def UpdateVoltageStatus(self, value, qualifier):

        devID = qualifier['Device ID']
        if 'All' == devID or 0 <= int(devID) <= 32:
            VoltageStatusCmdString = '?VOLTAGE {0}\r'.format(devID)
            res = self.__UpdateHelper('VoltageStatus', VoltageStatusCmdString, value, qualifier)
            if res:
                try:
                    deviceID = re.match(self.deviceIDRex, res).group(1)
                    value = re.search(self.voltageRex, res).group(1)
                    self.WriteStatus('VoltageStatus', value, {'Device ID': deviceID})
                except(ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateVoltageStatus')
        else:
            print('Invalid Command for UpdateVoltageStatus')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command == 'Enumerate':
                tag = '\x04'
            else:
                tag = '\x0D\x0A'
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=tag).decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'All':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if 'OutletControl' in command:
                timeOut = 3.0
            else:
                timeOut = 1.0
            res = self.SendAndWait(commandstring, timeOut).decode()
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
