from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack


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
        self._CameraAddress = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutomaticExposure': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'TallyLight': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }
        self._CameraAddress = 0x81


    @property
    def CameraAddress(self):
        return self._CameraAddress

    @CameraAddress.setter
    def CameraAddress(self, value):
        self._CameraAddress = 0x80 + int(value)

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        ApertureCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        AutoFocusCmdString = pack('5B', self._CameraAddress, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutomaticExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B,
            'Bright': 0x0D
        }

        AutomaticExposureCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutomaticExposure', AutomaticExposureCmdString, value, qualifier)

    def UpdateAutomaticExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutomaticExposureCmdString = pack('5B', self._CameraAddress, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutomaticExposure', AutomaticExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutomaticExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Automatic Exposure: Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightModeCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightModeCmdString = pack('5B', self._CameraAddress, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30
        }

        speed_val = qualifier['Speed']
        if 0 <= int(speed_val) <= 15:
            if value == 'Stop':
                FocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x08, 0x00, 0xFF)
            else:
                FocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x08, ValueStateValues[value] + int(speed_val), 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        IrisCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03],
            'Home': 0x04,
            'Reset': 0x05
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']
        if 1 <= int(pan_speed) <= 24 and 1 <= int(tilt_speed) <= 20:
            if value in ('Home', 'Reset'):
                PanTiltCmdString = pack('5B', self._CameraAddress, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('9B', self._CameraAddress, 0x01, 0x06, 0x01, int(pan_speed),
                                        int(tilt_speed), ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [0x00, 0x02],
            'Off': [0x07, 0x00]
        }

        PowerCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Reset': 0x00,
            'Set': 0x01,
            'Recall': 0x02
        }

        action_val = qualifier['Action']
        if action_val in ActionStates and 0 <= int(value) <= 127:
            PresetCmdString = pack('7B', self._CameraAddress, 0x01, 0x04, 0x3F, ActionStates[action_val], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTallyLight(self, value, qualifier):

        ValueStateValues = {
            'Red': [0x02, 0x03],
            'Green': [0x03, 0x02],
            'Off': [0x03, 0x03]
        }

        TallyLightCmdString = pack('9B', self._CameraAddress, 0x01, 0x7E, 0x01, 0x0A, 0x00,
                                   ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
        self.__SetHelper('TallyLight', TallyLightCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        speed_val = qualifier['Speed']
        if 0 <= int(speed_val) <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x07, 0x00, 0xFF)
            else:
                ZoomCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x07, ValueStateValues[value] + int(speed_val), 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x02: 'Syntax Error',
            0x03: 'Command Buffer Full',
            0x04: 'Command Canceled',
            0x05: 'No Socket',
            0x41: 'Command Not Executable',
        }
        if response:
            if (response[2] in DEVICE_ERROR_CODES) and (0x60 <= response[1] <= 0x6F):
                self.Error(['Error in {0}, {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[2]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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
                    except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self._CameraAddress = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutomaticExposure': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PowerOff': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'TallyLight': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self._CameraAddress = 0x81

    @property
    def CameraAddress(self):
        return self._CameraAddress

    @CameraAddress.setter
    def CameraAddress(self, value):
        self._CameraAddress = 0x80 + int(value)

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        ApertureCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetAutomaticExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B,
            'Bright': 0x0D
        }

        AutomaticExposureCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutomaticExposure', AutomaticExposureCmdString, value, qualifier)

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightModeCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30
        }

        speed_val = qualifier['Speed']
        if 0 <= int(speed_val) <= 15:
            if value == 'Stop':
                FocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x08, 0x00, 0xFF)
            else:
                FocusCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x08, ValueStateValues[value] + int(speed_val), 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': 0x00,
            'Up': 0x02,
            'Down': 0x03
        }

        IrisCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03],
            'Home': 0x04,
            'Reset': 0x05
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']
        if 1 <= int(pan_speed) <= 24 and 1 <= int(tilt_speed) <= 20:
            if value in ('Home', 'Reset'):
                PanTiltCmdString = pack('5B', self._CameraAddress, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('9B', self._CameraAddress, 0x01, 0x06, 0x01, int(pan_speed),
                                        int(tilt_speed), ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x07, 0x00, 0xFF)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Reset': 0x00,
            'Set': 0x01,
            'Recall': 0x02
        }

        action_val = qualifier['Action']
        if action_val in ActionStates and 0 <= int(value) <= 127:
            PresetCmdString = pack('7B', self._CameraAddress, 0x01, 0x04, 0x3F, ActionStates[action_val], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTallyLight(self, value, qualifier):

        ValueStateValues = {
            'Red': [0x02, 0x03],
            'Green': [0x03, 0x02],
            'Off': [0x03, 0x03]
        }

        TallyLightCmdString = pack('9B', self._CameraAddress, 0x01, 0x7E, 0x01, 0x0A, 0x00,
                                   ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
        self.__SetHelper('TallyLight', TallyLightCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        speed_val = qualifier['Speed']
        if 0 <= int(speed_val) <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x07, 0x00, 0xFF)
            else:
                ZoomCmdString = pack('6B', self._CameraAddress, 0x01, 0x04, 0x07, ValueStateValues[value] + int(speed_val), 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
            
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
