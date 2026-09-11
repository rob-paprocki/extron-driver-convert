from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Capture': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'FactoryReset': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'ImageMode': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'Lamp': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Record': {'Status': {}},
            'SlideShow': {'Status': {}},
            'Zoom': {'Status': {}}
        }

    def SetCapture(self, value, qualifier):

        CaptureCmdString = b'\xA0\xB2\x00\x00\x00\xAF'
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Photo': b'\xA0\xA7\x00\x00\x00\xAF',
            'Text': b'\xA0\xA7\x01\x00\x00\xAF',
            'Gray': b'\xA0\xA7\x02\x00\x00\xAF'
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Photo',
            b'\x01': 'Text',
            b'\x02': 'Gray'
        }

        DisplayModeCmdString = b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDisplayMode')

    def SetFactoryReset(self, value, qualifier):

        FactoryResetCmdString = b'\xA0\x03\x01\x00\x00\xAF'
        self.__SetHelper('FactoryReset', FactoryResetCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': b'\x00',
            'Near': b'\x01'
        }

        speed = qualifier['Speed']
        if 0 <= int(speed) <= 6:
            if value == 'Stop':
                FocusCmdString = b'\xA0\x19\x00\x00\x00\xAF'
            else:
                FocusCmdString = b'\xA0\x19' + ValueStateValues[value] + pack('<B', int(speed)) + b'\x00\xAF'
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command')

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
                print('Invalid/unexpected response for UpdateFreeze')

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
            '180': b'\xA0\xB4\x01\x00\x00\xAF',
            'Flip': b'\xA0\xB4\x02\x00\x00\xAF',
            'Mirror': b'\xA0\xB4\x03\x00\x00\xAF'
        }

        ImageRotationCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\xC1\x01\x00\x00\xAF',
            'Off': b'\xA0\xC1\x00\x00\x00\xAF'
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLamp')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA0\xA0\x02\x00\x00\xAF',
            'Down': b'\xA0\xA0\x03\x00\x00\xAF',
            'Left': b'\xA0\xA0\x04\x00\x00\xAF',
            'Right': b'\xA0\xA0\x05\x00\x00\xAF',
            'Menu': b'\xA0\xA0\x06\x00\x00\xAF',
            'Enter': b'\xA0\xA0\x01\x00\x00\xAF',
            'Page Up': b'\xA0\x4A\x00\x00\x00\xAF',
            'Page Down': b'\xA0\x4A\x01\x00\x00\xAF'
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
                if res[2:3] == b'\x00':
                    self.WriteStatus('Power', 'Not Ready', qualifier)
                else:
                    self.WriteStatus('Power', ValueStateValues[res[3:4]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\xA0\x03\x00\x00\x00\xAF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\xA0\x03\x00\x01\x00\xAF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetRecord(self, value, qualifier):

        RecordCmdString = b'\xA0\xB2\x01\x00\x00\xAF'
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def SetSlideShow(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\x04\x01\x00\x00\xAF',
            'Off': b'\xA0\x04\x00\x00\x00\xAF'
        }

        SlideShowCmdString = ValueStateValues[value]
        self.__SetHelper('SlideShow', SlideShowCmdString, value, qualifier)

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
            print(DEVICE_ERROR_CODES[temp[6:8]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
