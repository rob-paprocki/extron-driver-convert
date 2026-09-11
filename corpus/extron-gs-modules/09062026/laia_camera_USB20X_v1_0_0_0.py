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
        self._DeviceID = b'\x81'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposureMode': {'Status': {}},
            'AutoFocusMode': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Status': {}},
            'Iris': {'Status': {}},
            'IRReceiver': {'Status': {}},
            'PanTilt': {'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Shutter': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if self.ConnectionType == 'Serial':
            if 1 <= int(value) <= 7:
                self._DeviceID = pack('B', 0x80 + int(value))
            else:
                self.Error(['Device ID should be a value between 1 to 7.'])
        else:
            self.Error(['Device ID is not changeable for Ethernet control.'])

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetAutoExposureMode(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': b'\x00',
            'Manual': b'\x03',
            'Shutter Priority': b'\x0A',
            'Iris Priority': b'\x0B',
            'Bright': b'\x0D',
        }

        AutoExposureModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x39', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('AutoExposureMode', AutoExposureModeCmdString, value, qualifier)

    def UpdateAutoExposureMode(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright',
        }

        AutoExposureModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x39\xFF'])
        res = self.__UpdateHelper('AutoExposureMode', AutoExposureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure Mode: Invalid/unexpected response'])

    def SetAutoFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x02',
            'Manual': b'\x03',
        }

        AutoFocusModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('AutoFocusMode', AutoFocusModeCmdString, value, qualifier)

    def UpdateAutoFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto',
            0x03: 'Manual',
        }

        AutoFocusModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('AutoFocusMode', AutoFocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus Mode: Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03',
        }

        BacklightModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off',
        }

        BacklightModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x33\xFF'])
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        FocusSpeedConstraints = {
            'Min': 0,
            'Max': 15,
            'Value': qualifier['Focus Speed']
        }

        ValueStateValues = {
            'Near': 0x30,
            'Far': 0x20,
            'Stop': 0x00,
        }

        if value in ValueStateValues and self.__constraint_checker(FocusSpeedConstraints):
            if value != 'Stop':
                focus_speed = FocusSpeedConstraints['Value'] + ValueStateValues[value]
            else:
                focus_speed = ValueStateValues[value]
            FocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x08', pack('B', focus_speed), b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up': b'\x02',
            'Down': b'\x03',
        }

        IrisCmdString = b''.join([self._DeviceID, b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIRReceiver(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        IRReceiverCmdString = b''.join([self._DeviceID, b'\x01\x06\x08', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 24,
            'Value': qualifier['Pan Speed']
        }

        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 20,
            'Value': qualifier['Tilt Speed']
        }

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03',
        }

        if value in ValueStateValues and self.__constraint_checker(PanSpeedConstraints, TiltSpeedConstraints):
            PanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x01',
                                         pack('BB', PanSpeedConstraints['Value'], TiltSpeedConstraints['Value']),
                                         ValueStateValues[value], b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03',
        }

        PowerCmdString = b''.join([self._DeviceID, b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off',
        }

        PowerCmdString = b''.join([self._DeviceID, b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        ValueStateContsraints = {
            'Min': 0,
            'Max': 254,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueStateContsraints):
            RecallPresetCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x02',
                                              pack('B', ValueStateContsraints['Value']), b'\xFF'])
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        ValueStateContsraints = {
            'Min': 0,
            'Max': 254,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueStateContsraints):
            SavePresetCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x01',
                                            pack('B', ValueStateContsraints['Value']), b'\xFF'])
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Reset': b'\x00',
        }

        ShutterCmdString = b''.join([self._DeviceID, b'\x01\x04\x0A', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomSpeedConstraints = {
            'Min': 0,
            'Max': 15,
            'Value': qualifier['Zoom Speed']
        }

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00,
        }

        if value in ValueStateValues and self.__constraint_checker(ZoomSpeedConstraints):
            if value != 'Stop':
                zoom_speed = ZoomSpeedConstraints['Value'] + ValueStateValues[value]
            else:
                zoom_speed = ValueStateValues[value]
            ZoomCmdString = b''.join([self._DeviceID, b'\x01\x04\x07', pack('B', zoom_speed), b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) > 3:
            ErrorCodes = {
                b'\x60\x02': 'Syntax Error',
                b'\x61\x41': 'Command Not Executable'
            }
            if response[-3:-1] in ErrorCodes:
                self.Error([ErrorCodes[response[-3:-1]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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
