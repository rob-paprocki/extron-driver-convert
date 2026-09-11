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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControl': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x08\x00\x00\x08',
            '4:3': b'\x08\x01\x00\x09',
            'PTP': b'\x08\x07\x00\x0F'
        }

        self.__SetHelper('AspectRatio', ValueStateValues[value], value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x03\x01\x00\x04',
            'Off': b'\x03\x01\x01\x05'
        }

        self.__SetHelper('AudioMute', ValueStateValues[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('AudioMute', b'\x03\x03\x00\x06', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', ValueStateValues[res[5]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Audio Mute'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x02\x03\x00\x05',
            'HDMI 1': b'\x02\x06\x00\x08',
            'HDMI 2': b'\x02\x07\x00\x09',
            'HDMI 3': b'\x02\x05\x00\x07',
            'PC': b'\x02\x08\x00\x0A',
            'Android': b'\x02\x0A\x00\x0C',
            'Android +': b'\x02\x0E\x00\x10',
            'DisplayPort': b'\x02\x11\x00\x13'
        }

        self.__SetHelper('Input', ValueStateValues[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x03: 'VGA',
            0x06: 'HDMI 1',
            0x07: 'HDMI 2',
            0x05: 'HDMI 3',
            0x08: 'PC',
            0x0A: 'Android',
            0x0E: 'Android +',
            0x11: 'DisplayPort'
        }

        res = self.__UpdateHelper('Input', b'\x02\x00\x00\x02', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', ValueStateValues[res[4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Input'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x07\x1B\x00\x22',
            '1': b'\x07\x00\x00\x07',
            '2': b'\x07\x10\x00\x17',
            '3': b'\x07\x11\x00\x18',
            '4': b'\x07\x13\x00\x1A',
            '5': b'\x07\x14\x00\x1B',
            '6': b'\x07\x15\x00\x1C',
            '7': b'\x07\x17\x00\x1E',
            '8': b'\x07\x18\x00\x1F',
            '9': b'\x07\x19\x00\x20'
        }

        self.__SetHelper('Keypad', ValueStateValues[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x07\x0D\x00\x14',
            'Up': b'\x07\x47\x00\x4E',
            'Down': b'\x07\x4D\x00\x54',
            'Left': b'\x07\x49\x00\x50',
            'Right': b'\x07\x4B\x00\x52',
            'Enter': b'\x07\x4A\x00\x51',
            'Back': b'\x07\x0A\x00\x11'
        }

        self.__SetHelper('MenuNavigation', ValueStateValues[value], value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\x01\x00\x0A',
            'Off': b'\x09\x00\x00\x09',
        }

        self.__SetHelper('PCPower', ValueStateValues[value], value, qualifier)

    def UpdatePCPower(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            1: 'Off',
            2: 'Sleep',
            3: 'Hibernate'
        }

        res = self.__UpdateHelper('PCPower', b'\x09\x02\x00\x0B', value, qualifier)
        if res:
            try:
                self.WriteStatus('PCPower', ValueStateValues[res[4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for PC Power'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x00\x00\x01',
            'Off': b'\x01\x01\x00\x02'
        }

        self.__SetHelper('Power', ValueStateValues[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            1: 'Off'
        }

        res = self.__UpdateHelper('Power', b'\x01\x02\x00\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', ValueStateValues[res[4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Power'])

    def SetRemoteControl(self, value, qualifier):

        ValueStateValues = {
            'WIN': 0x0B,
            'Space': 0x46,
            'Alt + Tab': 0x1D,
            'Alt + F4': 0x1F,
            'Display': 0x1C,
            'Refresh': 0x4C,
            'Input': 0x07,
            'Home': 0x48,
            'Delete': 0x40,
            'Energy': 0x4E,
            'Point': 0x06,
            'Channel Up': 0x02,
            'Channel Down': 0x09,
            'Volume Up': 0x03,
            'Volume Down': 0x41,
            'Page Up': 0x42,
            'Page Down': 0x0F,
            'F1': 0x45,
            'F2': 0x12,
            'F3': 0x51,
            'F4': 0x5B,
            'F5': 0x44,
            'F6': 0x50,
            'F7': 0x43,
            'F8': 0x1A,
            'F9': 0x04,
            'F10': 0x59,
            'F11': 0x57,
            'F12': 0x08,
            'Red': 0x5C,
            'Green': 0x5D,
            'Yellow': 0x5E,
            'Blue': 0x5F
        }

        self.__SetHelper('RemoteControl', bytes([7, ValueStateValues[value], 0, 7 + ValueStateValues[value]]), value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', bytes([3, 0, value, 3 + value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', b'\x03\x02\x00\x05', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res[5]), qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response for Volume'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = b'\xAA\xBB\xCC' + commandstring + b'\xDD\xEE\xFF'

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = b'\xAA\xBB\xCC' + commandstring + b'\xDD\xEE\xFF'

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
