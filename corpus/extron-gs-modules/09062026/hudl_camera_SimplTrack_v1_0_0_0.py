from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

    def SetAutoExposure(self, value, qualifier):

        AutoExposureState = {
            'Full Auto': b'\x81\x01\x04\x39\x00\xFF',
            'Manual': b'\x81\x01\x04\x39\x03\xFF',
            'Shutter Priority': b'\x81\x01\x04\x39\x0A\xFF',
            'Iris Priority': b'\x81\x01\x04\x39\x0B\xFF',
            'Bright': b'\x81\x01\x04\x39\x0D\xFF'
        }

        AutoExposureCmdString = AutoExposureState[value]
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureState = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter Priority',
            b'\x0B': 'Iris Priority',
            b'\x0D': 'Bright'
        }

        AutoExposureCmdString = b'\x81\x09\x04\x39\xFF'
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = AutoExposureState[res[2:3]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusState = {
            'Auto': b'\x81\x01\x04\x38\x02\xFF',
            'Manual': b'\x81\x01\x04\x38\x03\xFF'
        }

        AutoFocusCmdString = AutoFocusState[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusState = {
            b'\x02': 'Auto',
            b'\x03': 'Manual'
        }

        AutoFocusCmdString = b'\x81\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = AutoFocusState[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        BacklightState = {
            'On': b'\x81\x01\x04\x33\x02\xFF',
            'Off': b'\x81\x01\x04\x33\x03\xFF'
        }

        BacklightCmdString = BacklightState[value]
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusConstraints = {
            'Min': 0,
            'Max': 7
        }

        FocusState = {
            'Far': 0x20,
            'Near': 0x30
        }

        FocusSpeed = int(qualifier['Focus Speed'])
        if FocusConstraints['Min'] <= FocusSpeed <= FocusConstraints['Max']:
            if value == 'Stop':
                FocusValue = 0x00
            else:
                FocusValue = FocusSpeed + FocusState[value]
            FocusCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x08, FocusValue, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetFocus')

    def SetIris(self, value, qualifier):

        IrisState = {
            'Up': b'\x81\x01\x04\x0B\x02\xFF',
            'Down': b'\x81\x01\x04\x0B\x03\xFF',
            'Reset': b'\x81\x01\x04\x0B\x00\xFF'
        }

        IrisCmdString = IrisState[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanConstraints = {
            'Min': 0,
            'Max': 24
        }

        TiltConstraints = {
            'Min': 0,
            'Max': 20
        }

        PanTiltState = {
            'Up': 0x0301,
            'Down': 0x0302,
            'Left': 0x0103,
            'Right': 0x0203,
            'Up Left': 0x0101,
            'Up Right': 0x0201,
            'Down Left': 0x0102,
            'Down Right': 0x0202,
            'Stop': 0x0303,
            'Home': 0x04,
            'Reset': 0x05
        }

        PanSpeed = int(qualifier['Pan Speed'])
        TiltSpeed = int(qualifier['Tilt Speed'])
        if PanConstraints['Min'] <= PanSpeed <= PanConstraints['Max'] and TiltConstraints['Min'] <= TiltSpeed <= TiltConstraints['Max']:
            if value in ('Home', 'Reset'):
                PanTiltCmdString = pack('>5B', 0x81, 0x01, 0x06, PanTiltState[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', 0x81, 0x01, 0x06, 0x01, PanSpeed, TiltSpeed, PanTiltState[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x81\x01\x04\x00\x02\xFF',
            'Off': b'\x81\x01\x04\x00\x03\xFF',
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):  # page 25 of the protocol manual

        PowerState = {
            b'\x02': 'On',
            b'\x03': 'Off',
            b'\x04': 'Internal power circuit error'
        }

        PowerCmdString = b'\x81\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 255:
            PresetRecallCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 255:
            PresetSaveCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ShutterState = {
            'Up': b'\x81\x01\x04\x0A\x02\xFF',
            'Down': b'\x81\x01\x04\x0A\x03\xFF',
            'Reset': b'\x81\x01\x04\x0A\x00\xFF'
        }

        ShutterCmdString = ShutterState[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            'Auto': b'\x81\x01\x04\x35\x00\xFF',
            'Indoor': b'\x81\x01\x04\x35\x01\xFF',
            'Outdoor': b'\x81\x01\x04\x35\x02\xFF',
            'One Push WB': b'\x81\x01\x04\x35\x03\xFF',
            'Manual': b'\x81\x01\x04\x35\x05\xFF'
        }

        WhiteBalanceCmdString = WhiteBalanceState[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):  # page 25 of the protocol manual

        WhiteBalanceState = {
            b'\x00': 'Auto',
            b'\x01': 'Indoor',
            b'\x02': 'Outdoor',
            b'\x03': 'One Push WB',
            b'\x05': 'Manual'
        }

        WhiteBalanceCmdString = b'\x81\x09\x04\x35\xFF'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = WhiteBalanceState[res[2:3]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min': 0,
            'Max': 7
        }

        ZoomState = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        ZoomSpeed = int(qualifier['Zoom Speed'])
        if ZoomConstraints['Min'] <= ZoomSpeed <= ZoomConstraints['Max']:
            if value == 'Stop':
                ZoomValue = 0x00
            else:
                ZoomValue = ZoomSpeed + ZoomState[value]
            ZoomCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x07, ZoomValue, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorCodes = {
            0x02: 'Syntax Error',
            0x03: 'Command Buffer Full',
            0x04: 'Command Canceled',
            0x05: 'No Socket',
            0x41: 'Command Not Executable'
        }

        if response and len(response) == 4:
            address, errorByte, errorCode, terminator = unpack('>4B', response)
            errorByte = errorByte & 0x60
            if errorByte == 0x60:
                self.Error([sourceCmdName + ': ' + ErrorCodes[errorCode]])
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
