from extronlib.interface import SerialInterface, EthernetClientInterface

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
        self.DeviceID = '1'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BatteryStatus': {'Status': {}},
            'CurrentAudioLevelStatus': {'Status': {}},
            'Mute': {'Status': {}},
            'RemoteControlFunction': {'Status': {}},
            'RFStatus': {'Parameters': ['Antenna'], 'Status': {}},
            'Squelch': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceID = value
        if DeviceID == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(DeviceID) <= 64:
            self._DeviceID = DeviceID.zfill(2)

    def UpdateBatteryStatus(self, value, qualifier):

        BatteryStatus = {
            '25': 0,
            '21': 25,
            '1D': 50,
            '18': 75,
            '13': 100
        }
        BatteryStatusCmdString = '%{}N\r'.format(self._DeviceID)
        res = self.__UpdateHelper('BatteryStatus', BatteryStatusCmdString, value, qualifier)
        if res:
            try:
                value = BatteryStatus[res[9:11]]
                self.WriteStatus('BatteryStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Update Battery Status has provided an Invalid/unexpected response for UpdateBatteryStatus')

            try:
                value = int(res[5:7], 16)
                if 0 <= value <= 41:
                    self.WriteStatus('RFStatus', '0%', {'Antenna': 'A'})
                elif 42 <= value <= 60:
                    self.WriteStatus('RFStatus', '33%', {'Antenna': 'A'})
                elif 61 <= value <= 102:
                    self.WriteStatus('RFStatus', '66%', {'Antenna': 'A'})
                elif 103 <= value <= 255:
                    self.WriteStatus('RFStatus', '100%', {'Antenna': 'A'})
            except (ValueError, IndexError):
                print('Update RF Status for Antenna A has provided an Invalid/unexpected response')

            try:
                value = int(res[7:9], 16)
                if 0 <= value <= 41:
                    self.WriteStatus('RFStatus', '0%', {'Antenna': 'B'})
                elif 42 <= value <= 60:
                    self.WriteStatus('RFStatus', '33%', {'Antenna': 'B'})
                elif 61 <= value <= 102:
                    self.WriteStatus('RFStatus', '66%', {'Antenna': 'B'})
                elif 103 <= value <= 255:
                    self.WriteStatus('RFStatus', '100%', {'Antenna': 'B'})
            except (ValueError, IndexError):
                print('Update RF Status for Antenna B has provided an Invalid/unexpected response')

            try:
                value = int(res[3:5], 16)
                if 0 <= value <= 96:
                    self.WriteStatus('CurrentAudioLevelStatus', '0%', qualifier)
                elif 97 <= value <= 105:
                    self.WriteStatus('CurrentAudioLevelStatus', '25%', qualifier)
                elif 106 <= value <= 153:
                    self.WriteStatus('CurrentAudioLevelStatus', '50%', qualifier)
                elif 154 <= value <= 169:
                    self.WriteStatus('CurrentAudioLevelStatus', '75%', qualifier)
                elif 170 <= value <= 184:
                    self.WriteStatus('CurrentAudioLevelStatus', '100%', qualifier)
                elif 185 <= value <= 255:
                    self.WriteStatus('CurrentAudioLevelStatus', 'Overload', qualifier)
            except (ValueError, IndexError):
                print('Update Current Audio Level Status has provided an Invalid/unexpected response')

    def UpdateCurrentAudioLevelStatus(self, value, qualifier):
        self.UpdateBatteryStatus(value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '#{}B1\r'.format(self._DeviceID),
            'Off': '#{}B0\r'.format(self._DeviceID)
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetRemoteControlFunction(self, value, qualifier):

        ValueStateValues = {
            'On': '#{}A1\r'.format(self._DeviceID),
            'Off': '#{}A0\r'.format(self._DeviceID)
        }

        RemoteControlFunctionCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteControlFunction', RemoteControlFunctionCmdString, value, qualifier)

    def UpdateRFStatus(self, value, qualifier):
        self.UpdateBatteryStatus(value, None)

    def SetSquelch(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SquelchCmdString = '#{}F{}\r'.format(self._DeviceID, hex(value)[2:].zfill(2))
            self.__SetHelper('Squelch', SquelchCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSquelch')

    def UpdateSquelch(self, value, qualifier):

        SquelchCmdString = '%{}F\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Squelch', SquelchCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:7], 16)
                self.WriteStatus('Squelch', value, qualifier)
            except (ValueError, IndexError):
                print('Update Squelch has provided an Invalid/unexpected response for UpdateSquelch')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            0: '00',
            -10: '01',
            -20: '02',
            -30: '03'
        }

        if value in ValueStateValues:
            VolumeCmdString = '#{}G{}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueStateValues = {
            '0': 0,
            '1': -10,
            '2': -20,
            '3': -30
        }
        VolumeCmdString = '%{}G\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Update Volume has provided an Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        response = response.decode()
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' and self._DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('Setting {} does not provide any response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' and self._DeviceID == '00':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
            return None


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
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
