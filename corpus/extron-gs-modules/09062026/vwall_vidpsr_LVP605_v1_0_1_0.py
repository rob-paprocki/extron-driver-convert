from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
        self._DeviceID = 1
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'FadeMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Saturation': {'Status': {}},
            'Sharpness': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x00
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            print('Parameter DeviceID set to an invalid value. Range is from 1 to 255 and Broadcast')

    def calcChkSum(self, commandstring):
        ChkSum = 0
        for i in range(0, len(commandstring)):
            ChkSum = ChkSum ^ commandstring[i]
        return ChkSum.to_bytes(1, 'big')
    
    def SetAudioInput(self, value, qualifier):

        AudioState = {
            'V1': 0x00,
            'V2': 0x01,
            'V3': 0x02,
            'S-Video': 0x04,
            'VGA 1': 0x05,
            'VGA 2': 0x06,
            'DVI': 0x07,
            'HDMI': 0x08,
            'SDI': 0x09,
            'YPbPr': 0x0A
        }

        CurrentAudioInput1 = qualifier['Input 1']  # current audio input value when qualifier = 1
        CurrentAudioInput2 = qualifier['Input 2']  # current audio input value when qualifier = 2
        try:
            if CurrentAudioInput1 and CurrentAudioInput2:
                AudioInputCmdString = pack('>12B', 0x05, self._DeviceID, 0x94, AudioState[CurrentAudioInput1], AudioState[CurrentAudioInput2], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
                ChkSum = self.calcChkSum(AudioInputCmdString)
                AudioInputCmdString = AudioInputCmdString + ChkSum
                self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetAudioInput. Requires both qualifiers: Input 1 and Input 2')
        except KeyError:
            self.Discard('Invalid Command for SetAudioInput. Requires both qualifiers: Input 1 and Input 2')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = pack('>12B', 0x05, self._DeviceID, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(AutoImageCmdString)
        AutoImageCmdString = AutoImageCmdString + ChkSum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = pack('>12B', 0x05, self._DeviceID, 0x90, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
            ChkSum = self.calcChkSum(BrightnessCmdString)
            BrightnessCmdString = BrightnessCmdString + ChkSum
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        SharpnessStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Sharp'
        }
        AudioState1 = {
            0: 'V1',
            16: 'V2',
            32: 'V3',
            64: 'S-Video',
            80: 'VGA 1',
            96: 'VGA 2',
            112: 'DVI',
            128: 'HDMI',
            144: 'SDI',
            160: 'YPbPr'
        }

        AudioState2 = {
            0: 'V1',
            1: 'V2',
            2: 'V3',
            4: 'S-Video',
            5: 'VGA 1',
            6: 'VGA 2',
            7: 'DVI',
            8: 'HDMI',
            9: 'SDI',
            10: 'YPbPr'
        }

        BrightnessCmdString = pack('>12B', 0x05, self._DeviceID, 0x97, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(BrightnessCmdString)
        BrightnessCmdString = BrightnessCmdString + ChkSum
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3])  # Brightness
                self.WriteStatus('Brightness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])
            try:
                value = int(res[4])  # Contrast
                self.WriteStatus('Contrast', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])
            try:
                value = int(res[5])  # Saturation
                self.WriteStatus('Saturation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Saturation: Invalid/unexpected response'])
            try:
                value = SharpnessStateValues[res[6:7]]  # Sharpness
                self.WriteStatus('Sharpness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Sharpness: Invalid/unexpected response'])
            try:
                value = int(res[7]) & 0xF0  # Audio Input 1 uses byte 7, bits 4-7
                value = AudioState1[value]
                self.WriteStatus('AudioInput', value, {'Input': '1'})
                value = int(res[7]) & 0x0F  # Audio Input 2 uses byte 7, bits 0-3
                value = AudioState2[value]
                self.WriteStatus('AudioInput', value, {'Input': '2'})
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ContrastCmdString = pack('>12B', 0x05, self._DeviceID, 0x91, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
            ChkSum = self.calcChkSum(ContrastCmdString)
            ContrastCmdString = ContrastCmdString + ChkSum
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def SetFadeMode(self, value, qualifier):

        ValueStateValues = {
            'Seamless Switching': 0x00,
            '0.5s': 0x01,
            '1.0s': 0x02,
            '1.5s': 0x03
        }

        FadeModeCmdString = pack('>12B', 0x05, self._DeviceID, 0x99, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(FadeModeCmdString)
        FadeModeCmdString = FadeModeCmdString + ChkSum
        self.__SetHelper('FadeMode', FadeModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        FreezeCmdString = pack('>12B', 0x05, self._DeviceID, 0x87, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(FreezeCmdString)
        FreezeCmdString = FreezeCmdString + ChkSum
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateValues = {
            4: 'On',
            0: 'Off'
        }

        FadeModeStateValues = {
            b'\x00': 'Seamless Switching',
            b'\x01': '0.5s',
            b'\x02': '1.0s',
            b'\x03': '1.5s'
        }

        InputStateValues = {
            0: 'V1',
            1: 'V2',
            2: 'V3',
            4: 'S-Video',
            5: 'VGA 1',
            6: 'VGA 2',
            7: 'DVI',
            8: 'HDMI',
            9: 'EXT',
            10: 'YPbPr'
        }

        PIPInputStateValues = {
            0: 'V1',
            16: 'V2',
            32: 'V3',
            64: 'S-Video',
            80: 'VGA 1',
            96: 'VGA 2',
            112: 'DVI',
            128: 'HDMI',
            144: 'EXT'
        }

        FreezeCmdString = pack('>12B', 0x05, self._DeviceID, 0x97, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(FreezeCmdString)
        FreezeCmdString = FreezeCmdString + ChkSum
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[6]) & 0x04  # Freeze uses byte 6, bit 2
                value = FreezeStateValues[value]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])
            try:
                value = FadeModeStateValues[res[5:6]]  # Fade Mode
                self.WriteStatus('FadeMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Fade Mode: Invalid/unexpected response'])
            try:
                value = int(res[7]) & 0x0F  # Input uses byte 7, bits 0-3
                value = InputStateValues[value]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])
            try:
                value = int(res[7]) & 0xF0  # PIP Input uses byte 7, bits 4-7
                value = PIPInputStateValues[value]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'V1': 0x00,
            'V2': 0x01,
            'V3': 0x02,
            'S-Video': 0x04,
            'VGA 1': 0x05,
            'VGA 2': 0x06,
            'DVI': 0x07,
            'HDMI': 0x08,
            'EXT': 0x09,
            'YPbPr': 0x0A
        }

        InputCmdString = pack('>12B', 0x05, self._DeviceID, 0x80, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(InputCmdString)
        InputCmdString = InputCmdString + ChkSum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '1024x768@60Hz': 0x00,
            '1024x768@75Hz': 0x01,
            '1280x1024@60Hz': 0x02,
            '1280x1024@75Hz': 0x03,
            '1600x1200@60Hz': 0x04,
            '1920x1080@50Hz': 0x05,
            '1920x1080@60Hz': 0x06,
            '1366x768@60Hz': 0x07,
            '1440x900@60Hz': 0x08,
            '2048x1152@60Hz': 0x09
        }

        OutputResolutionCmdString = pack('>12B', 0x05, self._DeviceID, 0x89, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(OutputResolutionCmdString)
        OutputResolutionCmdString = OutputResolutionCmdString + ChkSum
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x00': '1024x768@60Hz',
            b'\x01': '1024x768@75Hz',
            b'\x02': '1280x1024@60Hz',
            b'\x03': '1280x1024@75Hz',
            b'\x04': '1600x1200@60Hz',
            b'\x05': '1920x1080@50Hz',
            b'\x06': '1920x1080@60Hz',
            b'\x07': '1366x768@60Hz',
            b'\x08': '1440x900@60Hz',
            b'\x09': '2048x1152@60Hz'
        }

        OutputResolutionCmdString = pack('>12B', 0x05, self._DeviceID, 0x97, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(OutputResolutionCmdString)
        OutputResolutionCmdString = OutputResolutionCmdString + ChkSum
        res = self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('OutputResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Output Resolution: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'V1': 0x00,
            'V2': 0x01,
            'V3': 0x02,
            'S-Video': 0x04,
            'VGA 1': 0x05,
            'VGA 2': 0x06,
            'DVI': 0x07,
            'HDMI': 0x08,
            'EXT': 0x09
        }

        PIPInputCmdString = pack('>12B', 0x05, self._DeviceID, 0x82, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(PIPInputCmdString)
        PIPInputCmdString = PIPInputCmdString + ChkSum
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PIPModeCmdString = pack('>12B', 0x05, self._DeviceID, 0x81, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(PIPModeCmdString)
        PIPModeCmdString = PIPModeCmdString + ChkSum
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetSaturation(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SaturationCmdString = pack('>12B', 0x05, self._DeviceID, 0x92, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
            ChkSum = self.calcChkSum(SaturationCmdString)
            SaturationCmdString = SaturationCmdString + ChkSum
            self.__SetHelper('Saturation', SaturationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaturation')

    def SetSharpness(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0x00,
            'Sharp': 0x01
        }

        SharpnessCmdString = pack('>12B', 0x05, self._DeviceID, 0x93, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        ChkSum = self.calcChkSum(SharpnessCmdString)
        SharpnessCmdString = SharpnessCmdString + ChkSum
        self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        for i in range(0, len(response)):
            if response[i] == 255:
                self.Error(['Device response = {0} {1}'.format(sourceCmdName, 'Command Failed')])
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=13)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' and self._DeviceID == 0x00:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=13)
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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
