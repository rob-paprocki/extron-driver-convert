from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PL6610': self.acer_1_4159_B,
            'PL6510': self.acer_1_4159_B,
            'PL6310W': self.acer_1_4159_B,
            'PL6610T': self.acer_1_4159_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DMode': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '* 0 IR 060\r',
            'Side by Side': '* 0 IR 062\r',
            'Top and Bottom': '* 0 IR 064\r',
            'Frame Sequential': '* 0 IR 066\r'
        }

        ThreeDFormatCmdString = ValueStateValues[value]
        self.__SetHelper('3DFormat', ThreeDFormatCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'On': '* 0 IR 056\r',
            'Off': '* 0 IR 057\r'
        }

        ThreeDModeCmdString = ValueStateValues[value]
        self.__SetHelper('3DMode', ThreeDModeCmdString, value, qualifier)

    def Set3DSyncInvert(self, value, qualifier):

        ThreeDSyncInvertCmdString = '* 0 IR 065\r'
        self.__SetHelper('3DSyncInvert', ThreeDSyncInvertCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '* 0 IR 022\r',
            'Letterbox': '* 0 IR 040\r',
            'Native': '* 0 IR 041\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '* 0 IR 014\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '* 0 IR 007\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.Inputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '* 0 Lamp\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:4])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '* 0 IR 009\r',
            'Down': '* 0 IR 010\r',
            'Left': '* 0 IR 012\r',
            'Right': '* 0 IR 011\r',
            'Menu': '* 0 IR 008\r',
            'Enter': '* 0 IR 013\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = '* 0 IR 006\r'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '* 0 IR 001\r',
            'Off': '* 0 IR 002\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '* 0 Lamp ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '* 0 IR 023\r',
            'Down': '* 0 IR 024\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if '*001' in response:
            self.Error(['{0} has invalid response'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

    def acer_1_4159_A(self):
        self.Inputs = {
            'HDMI 1': '* 0 IR 050\r',
            'HDMI 2': '* 0 IR 068\r',
            'VGA 1': '* 0 IR 015\r',
            'VGA 2': '* 0 IR 077\r',
            'S-Video': '* 0 IR 018\r',
            'Video': '* 0 IR 019\r',
            'HDBaseT': '* 0 IR 070\r'
        }

    def acer_1_4159_B(self):
        self.Inputs = {
            'HDMI 1': '* 0 IR 050\r',
            'HDMI 2': '* 0 IR 068\r',
            'VGA 1': '* 0 IR 015\r',
            'VGA 2': '* 0 IR 077\r',
            'S-Video': '* 0 IR 018\r',
            'Video': '* 0 IR 019\r'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'PL6510': self.acer_1_4159_B,
            'PL6310W': self.acer_1_4159_B,
            'PL6610T': self.acer_1_4159_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DMode': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PowerOff': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '* 0 IR 060\r',
            'Side by Side': '* 0 IR 062\r',
            'Top and Bottom': '* 0 IR 064\r',
            'Frame Sequential': '* 0 IR 066\r'
        }

        ThreeDFormatCmdString = ValueStateValues[value]
        self.__SetHelper('3DFormat', ThreeDFormatCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'On': '* 0 IR 056\r',
            'Off': '* 0 IR 057\r'
        }

        ThreeDModeCmdString = ValueStateValues[value]
        self.__SetHelper('3DMode', ThreeDModeCmdString, value, qualifier)

    def Set3DSyncInvert(self, value, qualifier):

        ThreeDSyncInvertCmdString = '* 0 IR 065\r'
        self.__SetHelper('3DSyncInvert', ThreeDSyncInvertCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '* 0 IR 022\r',
            'Letterbox': '* 0 IR 040\r',
            'Native': '* 0 IR 041\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '* 0 IR 014\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '* 0 IR 007\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.Inputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '* 0 IR 009\r',
            'Down': '* 0 IR 010\r',
            'Left': '* 0 IR 012\r',
            'Right': '* 0 IR 011\r',
            'Menu': '* 0 IR 008\r',
            'Enter': '* 0 IR 013\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = '* 0 IR 006\r'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '* 0 IR 002\r'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '* 0 IR 023\r',
            'Down': '* 0 IR 024\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def acer_1_4159_A(self):

        self.Inputs = {
            'HDMI 1': '* 0 IR 050\r',
            'HDMI 2': '* 0 IR 068\r',
            'VGA 1': '* 0 IR 015\r',
            'VGA 2': '* 0 IR 077\r',
            'S-Video': '* 0 IR 018\r',
            'Video': '* 0 IR 019\r',
            'HDBaseT': '* 0 IR 070\r'
        }

    def acer_1_4159_B(self):

        self.Inputs = {
            'HDMI 1': '* 0 IR 050\r',
            'HDMI 2': '* 0 IR 068\r',
            'VGA 1': '* 0 IR 015\r',
            'VGA 2': '* 0 IR 077\r',
            'S-Video': '* 0 IR 018\r',
            'Video': '* 0 IR 019\r'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
