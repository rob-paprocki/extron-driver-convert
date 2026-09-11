from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile


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
            '3DSync': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ColorMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'HDMIFormat': {'Status': {}},
            'HDMIRange': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'QuickPowerOff': {'Status': {}},
            'Reset': {'Parameters': ['Type'], 'Status': {}},
            'SplashScreen': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},

        }

        self.UpdateRegex = compile(b'[\x05][\x14][\x00][\x03][\x00][\x00][\x00][\x00-\xFF][\x00-\xFF]')

    def SetPower(self, value, qualifier):

        Value = {
            'On': b'\x06\x14\x00\x04\x00\x34\x11\x00\x00\x5D',
            'Off': b'\x06\x14\x00\x04\x00\x34\x11\x01\x00\x5E'
        }[value]

        self.__SetHelper('Power', Value, value, qualifier)

    def UpdatePower(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Power'])

    def SetReset(self, value, qualifier):

        Value = {
            'All Settings': b'\x06\x14\x00\x04\x00\x34\x11\x02\x00\x5F',
            'Color Settings': b'\x06\x14\x00\x04\x00\x34\x11\x2A\x00\x87'
        }[qualifier['Type']]

        self.__SetHelper('Reset', Value, value, qualifier)

    def SetSplashScreen(self, value, qualifier):

        Value = {
            'Black': b'\x06\x14\x00\x04\x00\x34\x11\x0A\x00\x67',
            'Blue': b'\x06\x14\x00\x04\x00\x34\x11\x0A\x01\x68',
            'Viewsonic': b'\x06\x14\x00\x04\x00\x34\x11\x0A\x02\x69',
            'Screen Capture': b'\x06\x14\x00\x04\x00\x34\x11\x0A\x03\x6A',
            'Off': b'\x06\x14\x00\x04\x00\x34\x11\x0A\x04\x6B'
        }[value]

        self.__SetHelper('SplashScreen', Value, value, qualifier)

    def UpdateSplashScreen(self, value, qualifier):

        Values = {
            0: 'Black',
            1: 'Blue',
            2: 'Viewsonic',
            3: 'Screen Capture',
            4: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x0A\x68'
        res = self.__UpdateHelper('SplashScreen', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('SplashScreen', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for SplashScreen'])

    def SetQuickPowerOff(self, value, qualifier):

        Value = {
            'On': b'\x06\x14\x00\x04\x00\x34\x11\x0B\x00\x68',
            'Off': b'\x06\x14\x00\x04\x00\x34\x11\x0B\x01\x69'
        }[value]

        self.__SetHelper('QuickPowerOff', Value, value, qualifier)

    def UpdateQuickPowerOff(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x0B\x69'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('QuickPowerOff', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected responsefor QuickPowerOff'])

    def SetLampMode(self, value, qualifier):

        Value = {
            'Normal': b'\x06\x14\x00\x04\x00\x34\x11\x10\x00\x6D',
            'Economic': b'\x06\x14\x00\x04\x00\x34\x11\x10\x01\x6E',
            'Dynamic': b'\x06\x14\x00\x04\x00\x34\x11\x10\x02\x6F',
            'Sleep': b'\x06\x14\x00\x04\x00\x34\x11\x10\x03\x70',
        }[value]

        self.__SetHelper('LampMode', Value, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        Values = {
            0: 'Normal',
            1: 'Economic',
            2: 'Dynamic',
            3: 'Sleep'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E'
        res = self.__UpdateHelper('LampMode', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for LampMode'])

    def Set3DSync(self, value, qualifier):

        Value = {
            'Off': b'\x06\x14\x00\x04\x00\x34\x12\x20\x00\x7E',
            'Auto': b'\x06\x14\x00\x04\x00\x34\x12\x20\x01\x7F',
            'Frame Sequential': b'\x06\x14\x00\x04\x00\x34\x12\x20\x02\x80',
            'Frame Packing': b'\x06\x14\x00\x04\x00\x34\x12\x20\x03\x81',
            'Top-Bottom': b'\x06\x14\x00\x04\x00\x34\x12\x20\x04\x82',
            'Side-by-Side': b'\x06\x14\x00\x04\x00\x34\x12\x20\x05\x83',
        }[value]

        self.__SetHelper('3DSync', Value, value, qualifier)

    def Update3DSync(self, value, qualifier):

        Values = {
            0: 'Off',
            1: 'Auto',
            2: 'Frame Sequential',
            3: 'Frame Packing',
            4: 'Top-Bottom',
            5: 'Side-by-Side'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x20\x7F'
        res = self.__UpdateHelper('3DSync', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('3DSync', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for 3DSync'])

    def Set3DSyncInvert(self, value, qualifier):

        Value = {
            'Off': b'\x06\x14\x00\x04\x00\x34\x12\x21\x00\x7F',
            'On': b'\x06\x14\x00\x04\x00\x34\x12\x21\x01\x80'
        }[value]

        self.__SetHelper('3DSyncInvert', Value, value, qualifier)

    def Update3DSyncInvert(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x21\x80'
        res = self.__UpdateHelper('3DSyncInvert', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('3DSyncInvert', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for 3DSyncInvert'])

    def SetAspectRatio(self, value, qualifier):

        Value = {
            'Auto': b'\x06\x14\x00\x04\x00\x34\x12\x04\x00\x62',
            '4:3': b'\x06\x14\x00\x04\x00\x34\x12\x04\x02\x64',
            '16:9': b'\x06\x14\x00\x04\x00\x34\x12\x04\x03\x65',
            '16:10': b'\x06\x14\x00\x04\x00\x34\x12\x04\x04\x66',
            'Anamorphic': b'\x06\x14\x00\x04\x00\x34\x12\x04\x05\x67',
            'Wide': b'\x06\x14\x00\x04\x00\x34\x12\x04\x06\x68'
        }[value]

        self.__SetHelper('AspectRatio', Value, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        Values = {
            0: 'Auto',
            2: '4:3',
            3: '16:9',
            4: '16:10',
            5: 'Anamorphic',
            6: 'Wide'
        }

        AspectRatioCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for AspectRatio'])

    def SetAutoImage(self, value, qualifier):

        CmdString = b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': b'\x06\x14\x00\x04\x00\x34\x12\x09\x01\x68',
            'Off': b'\x06\x14\x00\x04\x00\x34\x12\x09\x00\x67'
        }[value]

        self.__SetHelper('VideoMute', Value, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68'
        res = self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for VideoMute'])

    def SetColorMode(self, value, qualifier):

        Value = {
            'Brightest': b'\x06\x14\x00\x04\x00\x34\x12\x0B\x00\x69',
            'Movie': b'\x06\x14\x00\x04\x00\x34\x12\x0B\x01\x6A',
            'PC': b'\x06\x14\x00\x04\x00\x34\x12\x0B\x04\x6D',
            'ViewMatch': b'\x06\x14\x00\x04\x00\x34\x12\x0B\x05\x6E',
            'Dynamic': b'\x06\x14\x00\x04\x00\x34\x12\x0B\x08\x71',
        }[value]

        self.__SetHelper('ColorMode', Value, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        Values = {
            0: 'Brightest',
            1: 'Movie',
            4: 'PC',
            5: 'ViewMatch',
            8: 'Dynamic',
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x0B\x6A'
        res = self.__UpdateHelper('ColorMode', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('ColorMode', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for ColorMode'])

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': b'\x06\x14\x00\x04\x00\x34\x13\x00\x01\x60',
            'Off': b'\x06\x14\x00\x04\x00\x34\x13\x00\x00\x5F'
        }[value]

        self.__SetHelper('Freeze', Value, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60'
        res = self.__UpdateHelper('Freeze', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Freeze'])

    def SetInput(self, value, qualifier):

        Value = {
            'VGA 1': b'\x06\x14\x00\x04\x00\x34\x13\x01\x00\x60',
            'VGA 2': b'\x06\x14\x00\x04\x00\x34\x13\x01\x08\x68',
            'HDMI 1': b'\x06\x14\x00\x04\x00\x34\x13\x01\x03\x63',
            'HDMI 2': b'\x06\x14\x00\x04\x00\x34\x13\x01\x07\x67',
            'Composite': b'\x06\x14\x00\x04\x00\x34\x13\x01\x05\x65',
            'S-Video': b'\x06\x14\x00\x04\x00\x34\x13\x01\x06\x66'
        }[value]

        self.__SetHelper('Input', Value, value, qualifier)

    def UpdateInput(self, value, qualifier):

        Values = {
            0: 'VGA 1',
            8: 'VGA 2',
            3: 'HDMI 1',
            7: 'HDMI 2',
            5: 'Composite',
            6: 'S-Video'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61'
        res = self.__UpdateHelper('Input', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Input'])

    def SetAudioMute(self, value, qualifier):

        Value = {
            'On': b'\x06\x14\x00\x04\x00\x34\x14\x00\x01\x61',
            'Off': b'\x06\x14\x00\x04\x00\x34\x14\x00\x00\x60'
        }[value]

        self.__SetHelper('AudioMute', Value, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        Values = {
            1: 'On',
            0: 'Off'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61'
        res = self.__UpdateHelper('AudioMute', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for AudioMute'])

    def SetVolume(self, value, qualifier):

        Value = {
            'Increase': b'\x06\x14\x00\x04\x00\x34\x14\x01\x00\x61',
            'Decrease': b'\x06\x14\x00\x04\x00\x34\x14\x02\x00\x62'
        }[value]

        self.__SetHelper('Volume', Value, value, qualifier)

    def SetHDMIFormat(self, value, qualifier):

        Value = {
            'RGB': b'\x06\x14\x00\x04\x00\x34\x11\x28\x00\x85',
            'YUV': b'\x06\x14\x00\x04\x00\x34\x11\x28\x01\x86',
            'Auto': b'\x06\x14\x00\x04\x00\x34\x11\x28\x02\x87'
        }[value]

        self.__SetHelper('HDMIFormat', Value, value, qualifier)

    def UpdateHDMIFormat(self, value, qualifier):

        Values = {
            0: 'RGB',
            1: 'YUV',
            2: 'Auto'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x28\x86'
        res = self.__UpdateHelper('HDMIFormat', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('HDMIFormat', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for HDMIFormat'])

    def SetHDMIRange(self, value, qualifier):

        Value = {
            'Enhanced': b'\x06\x14\x00\x04\x00\x34\x11\x29\x00\x86',
            'Normal': b'\x06\x14\x00\x04\x00\x34\x11\x29\x01\x87',
            'Auto': b'\x06\x14\x00\x04\x00\x34\x11\x29\x02\x88',
        }[value]

        self.__SetHelper('HDMIRange', Value, value, qualifier)

    def UpdateHDMIRange(self, value, qualifier):

        Values = {
            0: 'Enhanced',
            1: 'Normal',
            2: 'Auto'
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x29\x87'
        res = self.__UpdateHelper('HDMIRange', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('HDMIRange', Values[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for HDMIRange'])

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Menu': b'\x02\x14\x00\x04\x00\x34\x02\x04\x0F\x61',
            'Exit': b'\x02\x14\x00\x04\x00\x34\x02\x04\x13\x65',
            'Up': b'\x02\x14\x00\x04\x00\x34\x02\x04\x0B\x5D',
            'Down': b'\x02\x14\x00\x04\x00\x34\x02\x04\x0C\x5E',
            'Left': b'\x02\x14\x00\x04\x00\x34\x02\x04\x0D\x5F',
            'Right': b'\x02\x14\x00\x04\x00\x34\x02\x04\x0E\x60',
            'Enter': b'\x02\x14\x00\x04\x00\x34\x02\x04\x15\x67',
        }[value]

        self.__SetHelper('MenuNavigation', Value, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        regex = self.UpdateRegex

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
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
