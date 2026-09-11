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
            'Loudness': {'Status': {}},
            'MainInput': {'Status': {}},
            'MainMute': {'Status': {}},
            'MainOff': {'Status': {}},
            'MainVolume': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'ZoneInput': {'Status': {}},
            'ZoneMute': {'Status': {}},
            'ZoneOff': {'Status': {}},
            'ZoneVolume': {'Status': {}}
        }

    def SetLoudness(self, value, qualifier):

        LoudnessState = {
            'On': b'\xF1\x04\x39\x01\xA5\xF2',
            'Off': b'\xF1\x04\x39\x01\xAB\xF2'
        }

        LoudnessCmdString = LoudnessState[value]
        self.__SetHelper('Loudness', LoudnessCmdString, value, qualifier)

    def SetMainInput(self, value, qualifier):

        MainInputState = {
            'DVD 1': b'\xF1\x04\x39\x01\x20\xF2',
            'DVD 2': b'\xF1\x04\x39\x01\x21\xF2',
            'SAT': b'\xF1\x04\x39\x01\x24\xF2',
            'VCR': b'\xF1\x04\x39\x01\x25\xF2',
            'TV': b'\xF1\x04\x39\x01\x23\xF2',
            'CD': b'\xF1\x04\x39\x01\x26\xF2',
            'Tuner': b'\xF1\x04\x39\x01\x2A\xF2',
            'AUX': b'\xF1\x04\x39\x01\x2B\xF2'
        }

        MainInputCmdString = MainInputState[value]
        self.__SetHelper('MainInput', MainInputCmdString, value, qualifier)

    def UpdateMainInput(self, value, qualifier):

        MainInputState = {
            1: 'DVD 1',
            2: 'DVD 2',
            3: 'SAT',
            4: 'VCR',
            5: 'TV',
            6: 'CD',
            7: 'Tuner',
            8: 'AUX'
        }

        MainInputCmdString = b'\xF1\x03\x3E\x00\xF2'
        res = self.__UpdateHelper('MainInput', MainInputCmdString, value, qualifier)
        if res:
            try:
                value = MainInputState[res[5]]
                self.WriteStatus('MainInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateMainInput')

            try:
                VolValue = res[4]
                if VolValue >= 176:
                    value = VolValue - 256
                else:
                    value = VolValue
                self.WriteStatus('MainVolume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateMainInput')

    def SetMainMute(self, value, qualifier):

        MainMuteCmdString = b'\xF1\x04\x39\x01\x15\xF2'
        self.__SetHelper('MainMute', MainMuteCmdString, value, qualifier)

    def SetMainOff(self, value, qualifier):

        MainOffCmdString = b'\xF1\x04\x39\x01\x99\xF2'
        self.__SetHelper('MainOff', MainOffCmdString, value, qualifier)

    def SetMainVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                cmdValue = 256 + value
            else:
                cmdValue = value
            MainVolumeCmdString = pack('>BBBBBB', 0xF1, 0x04, 0x40, 0x01, cmdValue, 0xF2)
            self.__SetHelper('MainVolume', MainVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMainVolume')
            
    def UpdateMainVolume(self, value, qualifier):
        self.UpdateMainInput(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\xF1\x04\x39\x01\x01\xF2',
            'Down': b'\xF1\x04\x39\x01\x1D\xF2',
            'Left': b'\xF1\x04\x39\x01\x0A\xF2',
            'Right': b'\xF1\x04\x39\x01\x08\xF2'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\xF1\x04\x39\x01\x18\xF2',
            'Off': b'\xF1\x04\x39\x01\x19\xF2'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetZoneInput(self, value, qualifier):

        ZoneInputState = {
            'DVD 1': b'\xF1\x04\x39\x01\x60\xF2',
            'DVD 2': b'\xF1\x04\x39\x01\x61\xF2',
            'SAT': b'\xF1\x04\x39\x01\x64\xF2',
            'VCR': b'\xF1\x04\x39\x01\x65\xF2',
            'TV': b'\xF1\x04\x39\x01\x63\xF2',
            'CD': b'\xF1\x04\x39\x01\x66\xF2',
            'Tuner': b'\xF1\x04\x39\x01\x6A\xF2',
            'AUX': b'\xF1\x04\x39\x01\x6B\xF2'
        }

        ZoneInputCmdString = ZoneInputState[value]
        self.__SetHelper('ZoneInput', ZoneInputCmdString, value, qualifier)

    def UpdateZoneInput(self, value, qualifier):

        ZoneInputState = {
            1: 'DVD 1',
            2: 'DVD 2',
            4: 'SAT',
            5: 'VCR',
            3: 'TV',
            6: 'CD',
            7: 'Tuner',
            8: 'AUX'
        }

        ZoneInputCmdString = b'\xF1\x03\x3F\x00\xF2'
        res = self.__UpdateHelper('ZoneInput', ZoneInputCmdString, value, qualifier)
        if res:
            try:
                value = ZoneInputState[res[5]]
                self.WriteStatus('ZoneInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateZoneInput')

            try:
                VolValue = res[4]
                if VolValue >= 176:
                    value = VolValue - 256
                else:
                    value = VolValue
                self.WriteStatus('ZoneVolume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateZoneInput')

    def SetZoneMute(self, value, qualifier):

        ZoneMuteCmdString = b'\xF1\x04\x39\x01\x55\xF2'
        self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)

    def SetZoneOff(self, value, qualifier):

        ZoneOffCmdString = b'\xF1\x04\x39\x01\x59\xF2'
        self.__SetHelper('ZoneOff', ZoneOffCmdString, value, qualifier)

    def SetZoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                cmdValue = 256 + value
            else:
                cmdValue = value
            ZoneVolumeCmdString = pack('>BBBBBB', 0xF1, 0x04, 0x45, 0x01, cmdValue, 0xF2)
            self.__SetHelper('ZoneVolume', ZoneVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneVolume')

    def UpdateZoneVolume(self, value, qualifier):

        self.UpdateZoneInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00': 'No Ack',
            b'\x01': 'No Error',
            b'\x02': 'Parity Error',
            b'\x03': 'Framing Error',
            b'\x04': 'Overrun Error',
            b'\x05': 'Invalid Packet',
            b'\x06': 'Timeout Error',
            b'\x07': 'Full Buffer Error',
            b'\x10': 'Invalid Count',
            b'\x11': 'Invalid Command',
            b'\x12': 'Invalid Data',
            b'\x13': 'Invalid Address',
            b'\x14': 'Invalid Effect ID',
            b'\x15': 'Invalid Parameter ID',
            b'\x16': 'Invalid Name',
            b'\x17': 'Invalid Input',
            b'\x18': 'Error Read Only'
        }

        if response[0:1] == b'\xE1' and response[3:4] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[3:4]]))

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xF2')
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xF2')
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
