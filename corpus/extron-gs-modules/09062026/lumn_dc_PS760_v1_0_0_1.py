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
            'Capture': {'Status': {}},
            'CaptureMode': {'Status': {}},
            'FactoryReset': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'ImageMode': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'Input': {'Status': {}},
            'Lamp': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetCapture(self, value, qualifier):

        ValueStateValues = {
            'Capture': b'\xA0\xB2\x00\x00\x00\xAF',
            'Record': b'\xA0\xB2\x01\x00\x00\xAF',
            'Single': b'\xA0\x96\x00\x00\x00\xAF',
            'Continous': b'\xA0\x96\x01\x00\x00\xAF',
            'Disable': b'\xA0\x96\x02\x00\x00\xAF'
        }

        CaptureCmdString = ValueStateValues[value]
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)

    def SetCaptureMode(self, value, qualifier):

        ValueStateValues = {
            'Photo': b'\xA0\x95\x00\x00\x00\xAF',
            'Video': b'\xA0\x95\x01\x00\x00\xAF'
        }

        CaptureModeCmdString = ValueStateValues[value]
        self.__SetHelper('CaptureMode', CaptureModeCmdString, value, qualifier)

    def SetFactoryReset(self, value, qualifier):

        FactoryResetCmdString = b'\xA0\x03\x01\x00\x00\xAF'
        self.__SetHelper('FactoryReset', FactoryResetCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 0,
            'Far': 1
        }
        speed = qualifier['Speed']
        if 0 <= int(speed) <= 7:
            if value == 'Stop':
                FocusCmdString = b'\xA0\x19\x00\x00\x00\xAF'
            else:
                FocusCmdString = pack('>6B', 0xA0, 0x1A, ValueStateValues[value], int(speed), 0x00, 0xAF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\x2C\x01\x00\x00\xAF',
            'Off': b'\xA0\x2C\x00\x00\x00\xAF'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\xA0\xA9\x00\x00\x00\xAF',
            'Slide': b'\xA0\xA9\x01\x00\x00\xAF',
            'Film': b'\xA0\xA9\x02\x00\x00\xAF',
            'Microscope': b'\xA0\xA9\x03\x00\x00\xAF'
        }

        ImageModeCmdString = ValueStateValues[value]
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xA0\xB4\x00\x00\x00\xAF',
            '180': b'\xA0\xB4\x02\x00\x00\xAF',
            '90': b'\xA0\xB4\x01\x00\x00\xAF',
            '270': b'\xA0\xB4\x03\x00\x00\xAF'
        }

        ImageRotationCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': b'\xA0\x3A\x01\x00\x00\xAF',
            'VGA 2': b'\xA0\x3A\x02\x00\x00\xAF',
            'Camera': b'\xA0\x3A\x00\x00\x00\xAF',
            'C-Video': b'\xA0\x3A\x03\x00\x00\xAF',
            'S-Video': b'\xA0\x3A\x04\x00\x00\xAF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\xA0\xC1\x00\x00\x00\xAF',
            'Arm Light': b'\xA0\xC1\x01\x00\x00\xAF',
            'Backlight': b'\xA0\xC1\x02\x00\x00\xAF'
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Arm Light',
            b'\x02': 'Backlight'
        }

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA0\xA0\x02\x00\x00\xAF',
            'Down': b'\xA0\xA0\x03\x00\x00\xAF',
            'Left': b'\xA0\xA0\x04\x00\x00\xAF',
            'Right': b'\xA0\xA0\x05\x00\x00\xAF',
            'Menu': b'\xA0\xA0\x06\x00\x00\xAF',
            'Enter': b'\xA0\xA0\x01\x00\x00\xAF',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\x4B\x01\x00\x00\xAF',
            'Off': b'\xA0\x4B\x00\x00\x00\xAF'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\xB1\x01\x00\x00\xAF',
            'Off': b'\xA0\xB1\x00\x00\x00\xAF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Save': b'\xA0\x03\x00\x01\x00\xAF',
            'Load': b'\xA0\x03\x00\x00\x00\xAF'
        }

        PresetCmdString = ValueStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def SetSharpness(self, value, qualifier):

        ValueStateValues = {
            'Photo': b'\xA0\xA7\x00\x00\x00\xAF',
            'Text': b'\xA0\xA7\x01\x00\x00\xAF',
            'Gray': b'\xA0\xA7\x02\x00\x00\xAF'
        }

        SharpnessCmdString = ValueStateValues[value]
        self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)

    def UpdateSharpness(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Photo',
            b'\x01': 'Text',
            b'\x02': 'Gray'
        }

        SharpnessCmdString = b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Sharpness', SharpnessCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Sharpness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 16
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('>6B', 0xA0, 0xD6, value, 0x00, 0x00, 0xAF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xA0\xD7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>B', res[2:3])[0]
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': b'\xA0\x11\x00\x00\x00\xAF',
            'Wide': b'\xA0\x11\x01\x00\x00\xAF',
            'Stop': b'\xA0\x10\x00\x00\x00\xAF'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'01': "Command not Acknowleged.",
                              '10': "Command Ignored or Unsupported command.",
                              '11': "Command not used."
                              }
        temp = '{0:08b}'.format(response[4])
        if temp[6:8] in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[temp[6:8]]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                self.Error(['Invalid/unexpected response'])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
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
