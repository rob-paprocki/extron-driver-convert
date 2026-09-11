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
        self.Models = {
            'TruTouch 650': self.new_39_464_Other,
            'TruTouch 470': self.new_39_464_Other,
            'TT-5514B': self.new_39_464_Other,
            'TruTouch 840': self.new_39_464_840,
            'TT-6514B': self.new_39_464_Other,
            'TT-7014B': self.new_39_464_Other,
            'TT-8014B': self.new_39_464_Other,
            'TT-8414B': self.new_39_464_Other,
            'TruTouch 700': self.new_39_464_Other,
            'TruTouch 550': self.new_39_464_Other,
            'TruTouch 800': self.new_39_464_Other,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'EcoMode': {'Status': {}},
            'EcoModeStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenShot': {'Status': {}},
            'Volume': {'Status': {}},
            'WhiteboardFunction': {'Status': {}},
            'WiFi': {'Status': {}},
        }

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1A\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x19\xCF'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        EcoModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x16\xCF'
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoModeStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Eco',
            0: 'Standard',
            2: 'Auto'
        }

        EcoModeStatusCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xff\x01\x35\xCF'
        res = self.__UpdateHelper('EcoModeStatus', EcoModeStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10]]
                self.WriteStatus('EcoModeStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x3B\xCF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.SetInputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x32\xCF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.GetInputs[res[10]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x21\xCF',
            '2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x22\xCF',
            '3': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x23\xCF',
            '4': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x24\xCF',
            '5': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x25\xCF',
            '6': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x26\xCF',
            '7': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x27\xCF',
            '8': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x28\xCF',
            '9': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x29\xCF',
            '0': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2A\xCF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'OK': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2B\xCF',
            'Source': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x06\xCF',
            'Cursor Right': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2D\xCF',
            'Cursor Left': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2C\xCF',
            'Cursor Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2E\xCF',
            'Cursor Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2F\xCF',
            'Menu': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1B\xCF',
            'Page Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x13\xCF',
            'Page Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x14\xCF',
            'Back': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1D\xCF',
            'Home': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1C\xCF',
            'Search': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1E\xCF',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x02\xCF'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetScreenShot(self, value, qualifier):

        ScreenShotCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1F\xCF'
        self.__SetHelper('ScreenShot', ScreenShotCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x00\xCF',
            'Off': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x01\xCF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xff\x01\x37\xCF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('>BBBBBBBBBBB', 0x7F, 0x08, 0x99, 0xA2, 0xB3, 0xC4, 0x02, 0xFF, 0x05, value, 0xCF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x33\xCF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/unexpected response'])

    def SetWhiteboardFunction(self, value, qualifier):

        WhiteboardFunctionCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x07\xCF'
        self.__SetHelper('WhiteboardFunction', WhiteboardFunctionCmdString, value, qualifier)

    def SetWiFi(self, value, qualifier):
        WiFiCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x04\xCF'
        self.__SetHelper('WiFi', WiFiCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
            if not res:
                self.Error(['{0} Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
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

    def new_39_464_Other(self):

        self.SetInputs = {
            'OPS Computer': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0C\xCF',
            'VGA 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF',
            'VGA 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0E\xCF',
            'HDMI 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF',
            'HDMI 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF',
            'S-Video': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x10\xCF',
            'Video 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x11\xCF',
            'Video 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x12\xCF'
        }

        self.GetInputs = {
            0x19: 'OPS Computer',
            0x00: 'VGA 1',
            0x11: 'VGA 2',
            0x17: 'HDMI 1',
            0x18: 'HDMI 2',
            0x0B: 'S-Video',
            0x02: 'Video 1',
            0x03: 'Video 2'
        }

    def new_39_464_840(self):

        self.SetInputs = {
            'OPS Computer': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x38\xCF',
            'VGA 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF',
            'VGA 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0E\xCF',
            'HDMI 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF',
            'HDMI 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF',
            'HDMI 3': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0C\xCF',
            'S-Video': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x10\xCF',
            'Video 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x11\xCF',
            'Video 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x12\xCF'
        }

        self.GetInputs = {
            0x19: 'OPS Computer',
            0x00: 'VGA 1',
            0x11: 'VGA 2',
            0x17: 'HDMI 1',
            0x18: 'HDMI 2',
            0x20: 'HDMI 3',
            0x0B: 'S-Video',
            0x02: 'Video 1',
            0x03: 'Video 2'
        }

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
    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
