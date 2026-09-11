from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AutoImage': {'Status': {}},
            'BacklightBrightness': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MicrophoneMute': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'SwitchCameras': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStep': {'Status': {}},
            'Whiteboard': {'Status': {}},
        }

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBacklightBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BacklightBrightnessCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x09' + value.to_bytes(1, 'big') + b'\xCF'
            self.__SetHelper('BacklightBrightness', BacklightBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightBrightness')

    def UpdateBacklightBrightness(self, value, qualifier):

        BacklightBrightnessCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x49\xCF'
        res = self.__UpdateHelper('BacklightBrightness', BacklightBrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('BacklightBrightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Backlight Brightness: Invalid/unexpected response'])

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x07\x00\xCF',
            'Bright': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x07\x01\xCF',
            'Soft': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x07\x02\xCF',
            'Custom': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x07\x03\xCF'
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x06\x00\xCF',
            'Eco': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x06\x01\xCF'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Standard',
            1: 'Eco'
        }

        EcoModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x35\xCF'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['EcoMode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x3B\xCF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI Front': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF',
            'HDMI Rear': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF',
            'OPS': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x38\xCF',
            'VGA': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            23: 'HDMI Front',
            24: 'HDMI Rear',
            25: 'OPS',
            0: 'VGA'
        }

        InputCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x32\xCF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Page Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x13\xCF',
            'Page Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x14\xCF',
            'Menu': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1B\xCF',
            'Home Page': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1C\xCF',
            'Return (Exit)': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1D\xCF',
            'OK': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2B\xCF',
            'Left': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2C\xCF',
            'Right': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2D\xCF',
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2E\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2F\xCF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicrophoneMute(self, value, qualifier):

        MicrophoneMuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x41\xCF'
        self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def UpdateMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off'
        }

        MicrophoneMuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x45\xCF'
        res = self.__UpdateHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[10])]
                self.WriteStatus('MicrophoneMute', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Microphone Mute: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x02\xCF'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        self.UpdateVolume(value, qualifier)

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

        PowerCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x37\xCF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSwitchCameras(self, value, qualifier):

        ValueStateValues = {
            'Top Camera': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x08\x01\xCF',
            'Bottom Camera': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x08\x02\xCF'
        }

        SwitchCamerasCmdString = ValueStateValues[value]
        self.__SetHelper('SwitchCameras', SwitchCamerasCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x05' + value.to_bytes(1, 'big') + b'\xCF'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x33\xCF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

            try:
                value = res[-2]
                if value == 0:
                    self.WriteStatus('Mute', 'On', None)
                else:
                    self.WriteStatus('Mute', 'Off', None)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x18\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x17\xCF'
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def SetWhiteboard(self, value, qualifier):

        WhiteboardCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x07\xCF'
        self.__SetHelper('Whiteboard', WhiteboardCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xCF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(commandstring.strip(), res)

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
