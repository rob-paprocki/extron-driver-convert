from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
            'BatteryCapacity': {'Status': {}},
            'BatteryVoltage': {'Status': {}},
            'CabinetTemperature': {'Status': {}},
            'NonCriticalBank': {'Status': {}},
            'OutletState': {'Parameters': ['Outlet'], 'Status': {}},
            'OutputLoad': {'Status': {}},
            'OutputVoltage': {'Status': {}},
            'Power': {'Status': {}},
            'PowerAllOutlets': {'Status': {}},
            'RemainingBatteryTime': {'Status': {}},
            'UtilityVoltage': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.regex = compile(b'\{[0-9X]{1,8}\}|\[[1-3]\]|\[[0-9]{2}\]')

    def UpdateBatteryCapacity(self, value, qualifier):

        BatteryCapacityCmdString = '(008)'
        res = self.__UpdateHelper('BatteryCapacity', BatteryCapacityCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('BatteryCapacity', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Battery Capacity: Invalid/unexpected response'])

    def UpdateBatteryVoltage(self, value, qualifier):

        BatteryVoltageCmdString = '(009)'
        res = self.__UpdateHelper('BatteryVoltage', BatteryVoltageCmdString, value, qualifier)
        if res:
            try:
                value = float(int(res[1:-1]) / 10)
                self.WriteStatus('BatteryVoltage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Battery Voltage: Invalid/unexpected response'])

    def UpdateCabinetTemperature(self, value, qualifier):

        CabinetTemperatureCmdString = '(012)'
        res = self.__UpdateHelper('CabinetTemperature', CabinetTemperatureCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('CabinetTemperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Cabinet Temperature: Invalid/unexpected response'])

    def SetNonCriticalBank(self, value, qualifier):

        NonCriticalBankStateValues = {
            'On': '<8>',
            'Off': '<7>'
        }

        NonCriticalBank1CmdString = '(094)'
        NonCriticalBank2CmdString = NonCriticalBankStateValues[value]
        self.__SetHelper('NonCriticalBank', NonCriticalBank1CmdString, NonCriticalBank2CmdString, value, qualifier)

    def UpdateNonCriticalBank(self, value, qualifier):

        NonCriticalBankStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        NonCriticalBankCmdString = '(024)'
        res = self.__UpdateHelper('NonCriticalBank', NonCriticalBankCmdString, value, qualifier)
        if res:
            try:
                value = NonCriticalBankStateValues[res[1]]
                self.WriteStatus('NonCriticalBank', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Non Critical Bank: Invalid/unexpected response'])

    def SetOutletState(self, value, qualifier):

        OutletStateStateValues = {
            '1': {'On': '<1XXXXXXX>', 'Off': '<0XXXXXXX>'},
            '2': {'On': '<X1XXXXXX>', 'Off': '<X0XXXXXX>'},
            '3': {'On': '<XX1XXXXX>', 'Off': '<XX0XXXXX>'},
            '4': {'On': '<XXX1XXXX>', 'Off': '<XXX0XXXX>'},
            '5': {'On': '<XXXX1XXX>', 'Off': '<XXXX0XXX>'},
            '6': {'On': '<XXXXX1XX>', 'Off': '<XXXXX0XX>'},
            '7': {'On': '<XXXXXX1X>', 'Off': '<XXXXXX0X>'},
            '8': {'On': '<XXXXXXX1>', 'Off': '<XXXXXXX0>'},
        }

        Outlet = qualifier['Outlet']

        OutletState1CmdString = '(123)'
        if Outlet in ['1', '2', '3', '4', '5', '6', '7', '8']:
            OutletState2CmdString = OutletStateStateValues[Outlet][value]
            self.__SetHelper('OutletState', OutletState1CmdString, OutletState2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletState')

    def UpdateOutletState(self, value, qualifier):

        OutletStateStateValues = {
            '1': 'On',
            '0': 'Off',
            'X': 'Outlet not supported'
        }


        Outlet = qualifier['Outlet']
        if Outlet in ['1', '2', '3', '4', '5', '6', '7', '8']:
            OutletStateCmdString = '(123)'
            res = self.__UpdateHelper('OutletState', OutletStateCmdString, value, qualifier)
            if res:
                try:
                    for i in range(0, 8):
                        value = OutletStateStateValues[res[1:-1][i]]
                        self.WriteStatus('OutletState', value, {'Outlet': str(i + 1)})
                except (KeyError, IndexError):
                    self.Error(['Outlet State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletState')

    def UpdateOutputLoad(self, value, qualifier):

        OutputLoadCmdString = '(007)'
        res = self.__UpdateHelper('OutputLoad', OutputLoadCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('OutputLoad', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Output Load: Invalid/unexpected response'])

    def UpdateOutputVoltage(self, value, qualifier):

        OutputVoltageCmdString = '(003)'
        res = self.__UpdateHelper('OutputVoltage', OutputVoltageCmdString, value, qualifier)
        if res:
            try:
                value = float(int(res[1:-1]) / 10)
                self.WriteStatus('OutputVoltage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Output Voltage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Standby Mode': '<2>',
            'Recover from Standby Mode': '<3>',
            'Reboot UPS': '<4>'
        }

        Power1CmdString = '(094)'
        Power2CmdString = PowerStateValues[value]
        self.__SetHelper('Power', Power1CmdString, Power2CmdString, value, qualifier)

    def SetPowerAllOutlets(self, value, qualifier):

        PowerAllOutletsStateValues = {
            'On': '<11111111>',
            'Off': '<00000000>',
        }

        PowerAllOutlets1CmdString = '(123)'
        PowerAllOutlets2CmdString = PowerAllOutletsStateValues[value]
        self.__SetHelper('PowerAllOutlets', PowerAllOutlets1CmdString, PowerAllOutlets2CmdString, value, qualifier)

    def UpdateRemainingBatteryTime(self, value, qualifier):

        RemainingBatteryTimeCmdString = '(010)'
        res = self.__UpdateHelper('RemainingBatteryTime', RemainingBatteryTimeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('RemainingBatteryTime', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Remaining Battery Time: Invalid/unexpected response'])

    def UpdateUtilityVoltage(self, value, qualifier):

        UtilityVoltageCmdString = '(001)'
        res = self.__UpdateHelper('UtilityVoltage', UtilityVoltageCmdString, value, qualifier)
        if res:
            try:
                value = float(int(res[1:-1]) / 10)
                self.WriteStatus('UtilityVoltage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Utility Voltage: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '[1]': 'Successful, but operation will not take effect.',
            '[2]': 'Successful, but the writing value will be adjusted to fit.',
            '[3]': 'Successful, but it will take effect after rebooting.',
            '[10]': 'The UPS does not support this function.',
            '[11]': 'The setting value is out of range.',
            '[12]': 'Invalid setting format.',
            '[13]': 'This item is not allowed.',
            '[14]': 'This field is not allowed in flag operation.',
            '[15]': 'The operation is denied.',
            '[16]': 'Not in command mode, (send (103) then <65535>)',
            '[17]': 'The parameter is invalid.',
            '[19]': 'The second parameter is invalid.',
            '[20]': 'The third parameter is invalid.',
            '[25]': 'UPS is in unsolicited mode. All operations are prohibited except 104.',
        }

        if response:
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring1, commandstring2, value, qualifier):
        self.Debug = True

        self.SendAndWait('(103)', 0.3, deliTag='}')
        self.SendAndWait('<65535>', 0.3, deliTag=']')
        if self.Unidirectional == 'True':
            self.SendAndWait(commandstring1, 0.3)
            self.SendAndWait(commandstring2, 0.3)
        else:
            self.SendAndWait(commandstring1, 0.3, deliTag=b'}')
            res = self.SendAndWait(commandstring2, 0.3, deliTag=b']')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
