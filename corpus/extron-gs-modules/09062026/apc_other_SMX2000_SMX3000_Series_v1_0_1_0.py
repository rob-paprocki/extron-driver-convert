from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BatteryVoltage': {'Status': {}},
            'InternalTemperature': {'Status': {}},
            'LoadPower': {'Status': {}},
            'OutputVoltage': {'Status': {}},
            'Power': {'Status': {}},
            'RuntimeRemaining': {'Status': {}},
            'TripRegisterStatus': {'Status': {}},
            'UPSStatus': {'Status': {}},
        }

        self.SmartMode = False


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SM'), self.__MatchSmartMode, None)
            self.AddMatchString(re.compile(b'BYE'), self.__MatchSimpleMode, None)
            self.AddMatchString(re.compile(b'\?'), self.__MatchPowerOn, None)

        self.Rex_Set = re.compile(b'OK|NA|\*|\?|SM|BYE')
        self.Rex_Update = re.compile(b'NA|\?|SM|BYE|.+\r\n')

    def __MatchSmartMode(self, match, qualifier):
        self.SmartMode = True

    def __MatchSimpleMode(self, match, qualifier):
        self.SmartMode = False
        self.Send('Y')

    def __MatchPowerOn(self, match, qualifier):
        if not self.SmartMode:
            self.Send('Y')

    def UpdateBatteryVoltage(self, value, qualifier):

        BatteryVoltageCmdString = 'B'
        res = self.__UpdateHelper('BatteryVoltage', BatteryVoltageCmdString, value, qualifier)
        if res:
            try:
                value = round(float(res[:-2]))
                self.WriteStatus('BatteryVoltage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateBatteryVoltage')

    def UpdateInternalTemperature(self, value, qualifier):

        InternalTemperatureCmdString = 'C'
        res = self.__UpdateHelper('InternalTemperature', InternalTemperatureCmdString, value, qualifier)
        if res:
            try:
                value = round(float(res[:-2]))
                self.WriteStatus('InternalTemperature', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateInternalTemperature')

    def UpdateLoadPower(self, value, qualifier):

        LoadPowerCmdString = 'P'
        res = self.__UpdateHelper('LoadPower', LoadPowerCmdString, value, qualifier)
        if res:
            try:
                value = round(float(res[:-2]))
                self.WriteStatus('LoadPower', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLoadPower')

    def UpdateOutputVoltage(self, value, qualifier):

        OutputVoltageCmdString = 'O'
        res = self.__UpdateHelper('OutputVoltage', OutputVoltageCmdString, value, qualifier)
        if res:
            try:
                value = round(float(res[:-2]))
                self.WriteStatus('OutputVoltage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOutputVoltage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x0E',
            'Off': 'Z',
            'Off on Battery': 'S',
            'Off on Delay': 'K'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdateRuntimeRemaining(self, value, qualifier):

        RuntimeRemainingCmdString = 'j'
        res = self.__UpdateHelper('RuntimeRemaining', RuntimeRemainingCmdString, value, qualifier)
        if res:
            try:
                value = int(res[:-3])
                self.WriteStatus('RuntimeRemaining', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateRuntimeRemaining')

    def UpdateTripRegisterStatus(self, value, qualifier):

        ValueStateValues = {
            '01': 'Output unpowered due to low battery shut down',
            '02': 'Unable to transfer to on-battery operation due to overload',
            '04': 'UPS Turned off',
            '08': 'UPS in Sleep Mode',
            '10': 'UPS in Shut Down mode',
            '20': 'Battery charger failure'
        }

        TripRegisterStatusCmdString = '8'
        res = self.__UpdateHelper('TripRegisterStatus', TripRegisterStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('TripRegisterStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTripRegisterStatus')

    def UpdateUPSStatus(self, value, qualifier):

        ValueStateValues = {
            '01': 'Run time calibration running',
            '02': 'SmartTrim mode of operation',
            '04': 'SmartBoost mode of operation',
            '08': 'Online mode of operation',
            '10': 'On Battery mode of operation',
            '20': 'Overloaded output condition',
            '40': 'Low battery condition',
            '80': 'Reserved for Future Use'
        }

        UPSStatusCmdString = 'Q'
        res = self.__UpdateHelper('UPSStatus', UPSStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('UPSStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateUPSStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response in ['NA']:
            errorString = sourceCmdName + ' Error : Conflicts with the other command in process'
            print(errorString)
            return ''
        elif response in ['\?']:
            self.__MatchPowerOn
            response = ''
        elif response in ['SM']:
            self.__MatchSmartMode
            response = ''
        elif response in ['BYE']:
            self.__MatchSimpleMode
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif self.SmartMode == False:
            self.Send('Y')
        else:
            if command == 'Power' and value != 'Off on Battery':
                res = self.SendAndWait(commandstring, 1.5)
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Rex_Set).decode()
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Rex_Set).decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        elif self.SmartMode == False:
            self.Send('Y')
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Rex_Update).decode()
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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