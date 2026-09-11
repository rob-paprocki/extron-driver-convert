from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
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
        self.Models = {
            'PJD6551W': self.view_1_3093_PJD,
            'PJD7326': self.view_1_3093_PJD7326,
            'PJD7526W': self.view_1_3093_PJD,
            'PJD7720HD': self.view_1_3093_PJD7720HD,
        }

        self.Commands = {
            '3DSync': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.updateRegex = re.compile(b'\x05\x14\x00[\x03|\x06]\x00\x00[\x00-\xFF]{3}')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x04' + self.AspectRatio[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', self.AspectRatioStates[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x61',
            'Off': b'\x00\x60'
        }

        AudioMuteCmdString = b'\x06\x14\x00\x04\x00\x34\x14\x00' + ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def Set3DSync(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00\x7E',
            'Auto': b'\x01\x7F',
            'Frame Sequential': b'\x02\x80',
            'Frame Packing': b'\x03\x81',
            'Top-Bottom': b'\x04\x82',
            'Side-by-Side': b'\x05\x83'
        }

        _3DSyncCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x20' + ValueStateValues[value]
        self.__SetHelper('3DSync', _3DSyncCmdString, value, qualifier)

    def Update3DSync(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            1: 'Auto',
            2: 'Frame Sequential',
            3: 'Frame Packing',
            4: 'Top-Bottom',
            5: 'Side-by-Side'
        }

        _3DSyncCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x20\x7F'
        res = self.__UpdateHelper('3DSync', _3DSyncCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('3DSync', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Sync: Invalid/unexpected response'])

    def Set3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x80',
            'Off': b'\x00\x7F'
        }

        _3DSyncInvertCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x21' + ValueStateValues[value]
        self.__SetHelper('3DSyncInvert', _3DSyncInvertCmdString, value, qualifier)

    def Update3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        _3DSyncInvertCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x21\x80'
        res = self.__UpdateHelper('3DSyncInvert', _3DSyncInvertCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('3DSyncInvert', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Sync Invert: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x60',
            'Off': b'\x00\x5F'
        }

        FreezeCmdString = b'\x06\x14\x00\x04\x00\x34\x13\x00' + ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputCmdString = b'\x06\x14\x00\x04\x00\x34\x13\x01' + self.Inputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStates[res[7]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x00\x6D',
            'Eco': b'\x01\x6E',
            'Dynamic': b'\x02\x6F',
            'SuperEco': b'\x03\x70'
        }

        LampModeCmdString = b'\x06\x14\x00\x04\x00\x34\x11\x10' + ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Eco',
            2: 'Dynamic',
            3: 'SuperEco'
        }

        LampModeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x15\x01\x63'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>H', res[6:8])[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x0F\x61',
            'Exit': b'\x13\x65',
            'Up': b'\x0B\x5D',
            'Down': b'\x0C\x5E',
            'Left': b'\x0D\x5F',
            'Right': b'\x0E\x60',
            'Enter': b'\x15\x67'
        }

        MenuNavigationCmdString = b'\x02\x14\x00\x04\x00\x34\x02\x04' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00\x00\x5D',
            'Off': b'\x01\x00\x5E'
        }

        PowerCmdString = b'\x06\x14\x00\x04\x00\x34\x11' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x68',
            'Off': b'\x00\x67'
        }

        VideoMuteCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x09' + ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 1 <= value <= 20:
            chksum = 0x14 + 0x00 + 0x04 + 0x00 + 0x34 + 0x13 + 0x2A + value
            VolumeCmdString = pack('>10B', 0x06, 0x14, 0x00, 0x04, 0x00, 0x34, 0x13, 0x2A, value, chksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x03\x64'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
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

    def view_1_3093_PJD7326(self):

        self.Inputs = {
            'VGA 1': b'\x00\x60',
            'VGA 2': b'\x08\x68',
            'HDMI 1': b'\x03\x63',
            'HDMI/MHL': b'\x0E\x6E',
            'Video': b'\x05\x65',
            'S-Video': b'\x06\x65'
        }

        self.InputStates = {
            0: 'VGA 1',
            8: 'VGA 2',
            3: 'HDMI 1',
            14: 'HDMI/MHL',
            5: 'Video',
            6: 'S-Video'
        }

        self.AspectRatio = {
            'Auto': b'\x00\x62',
            '4:3': b'\x02\x64',
            '16:9': b'\x03\x65',
            'Anamorphic': b'\x05\x67',
            '2.35:1': b'\x07\x69',
        }

        self.AspectRatioStates = {
            0: 'Auto',
            2: '4:3',
            3: '16:9',
            5: 'Anamorphic',
            7: '2.35:1',
        }

    def view_1_3093_PJD(self):

        self.Inputs = {
            'VGA 1': b'\x00\x60',
            'VGA 2': b'\x08\x68',
            'HDMI 1': b'\x03\x63',
            'HDMI/MHL': b'\x0E\x6E',
            'Video': b'\x05\x65',
            'S-Video': b'\x06\x65'
        }

        self.InputStates = {
            0: 'VGA 1',
            8: 'VGA 2',
            3: 'HDMI 1',
            14: 'HDMI/MHL',
            5: 'Video',
            6: 'S-Video'
        }

        self.AspectRatio = {
            'Auto': b'\x00\x62',
            '4:3': b'\x02\x64',
            '16:9': b'\x03\x65',
            '16:10': b'\x04\x66',
            'Anamorphic': b'\x05\x67',
            '2.35:1': b'\x07\x69',
            'Panorama': b'\x08\x6A'
        }

        self.AspectRatioStates = {
            0: 'Auto',
            2: '4:3',
            3: '16:9',
            4: '16:10',
            5: 'Anamorphic',
            7: '2.35:1',
            8: 'Panorama'
        }

    def view_1_3093_PJD7720HD(self):

        self.Inputs = {
            'VGA 1': b'\x00\x60',
            'HDMI 1': b'\x03\x63',
            'HDMI/MHL': b'\x0E\x6E'
        }

        self.InputStates = {
            0: 'VGA 1',
            3: 'HDMI 1',
            14: 'HDMI/MHL'
        }

        self.AspectRatio = {
            'Auto': b'\x00\x62',
            '4:3': b'\x02\x64',
            '16:9': b'\x03\x65',
            'Anamorphic': b'\x05\x67',
            '2.35:1': b'\x07\x69',
            'Panorama': b'\x08\x6A'
        }

        self.AspectRatioStates = {
            0: 'Auto',
            2: '4:3',
            3: '16:9',
            5: 'Anamorphic',
            7: '2.35:1',
            8: 'Panorama'
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
        self.OnDisconnected
