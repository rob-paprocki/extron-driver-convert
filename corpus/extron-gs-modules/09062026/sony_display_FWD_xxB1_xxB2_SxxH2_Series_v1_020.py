from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'PictureinPicture': {'Status': {}},
            'PIPMainInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSubInput': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Wide Zoom': b'\x8C\x20\x04\x02\x00\xB2',
            'Zoom': b'\x8C\x20\x04\x02\x01\xB3',
            'Full': b'\x8C\x20\x04\x02\x02\xB4',
            'Normal': b'\x8C\x20\x04\x02\x04\xB6',
            'Full 1': b'\x8C\x20\x04\x02\x05\xB7',
            'Full 2': b'\x8C\x20\x04\x02\x06\xB8'
        }
        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            b'\x00': 'Wide Zoom',
            b'\x01': 'Zoom',
            b'\x02': 'Full',
            b'\x04': 'Normal',
            b'\x05': 'Full 1',
            b'\x06': 'Full 2'
        }

        AspectRatioCmdString = b'\x83\x20\x04\xFF\xFF\xA5'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[-2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': b'\x8C\x00\x03\x02\x01\x92',
            'Off': b'\x8C\x00\x03\x02\x00\x91'
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\x83\x00\x03\xFF\xFF\x84'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[-2:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'RGB': b'\x8C\x00\x01\x02\x08\x97',
            'YUV': b'\x8C\x00\x01\x02\x09\x98',
            'Component': b'\x8C\x00\x01\x02\x0F\x9A',
            'DVI': b'\x8C\x00\x01\x02\x20\xAF',
            'Video': b'\x8C\x00\x01\x02\x30\xBF',
            'HDMI': b'\x8C\x00\x01\x02\x44\xD3',
            'SDI': b'\x8C\x00\x01\x02\x84\x13'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            b'\x08': 'RGB',
            b'\x09': 'YUV',
            b'\x0F': 'Component',
            b'\x20': 'DVI',
            b'\x30': 'Video',
            b'\x44': 'HDMI',
            b'\x84': 'SDI'
        }

        InputCmdString = b'\x83\x00\x01\xFF\xFF\x82'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[-2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPictureinPicture(self, value, qualifier):

        PictureinPictureState = {
            'On': b'\x8C\x00\x30\x02\x02\xC0',
            'Off': b'\x8C\x00\x30\x02\x00\xBE'
        }

        PictureinPictureCmdString = PictureinPictureState[value]
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def UpdatePictureinPicture(self, value, qualifier):

        PictureinPictureState = {
            b'\x02': 'On',
            b'\x00': 'Off'
        }

        PictureinPictureCmdString = b'\x83\x00\x30\xFF\xFF\xB1'
        res = self.__UpdateHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)
        if res:
            try:
                value = PictureinPictureState[res[-2:-1]]
                self.WriteStatus('PictureinPicture', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Picture in Picture: Invalid/unexpected response'])

    def SetPIPMainInput(self, value, qualifier):

        PIPMainInputState = {
            'RGB': b'\x8C\x00\x35\x02\x08\xCB',
            'YUV': b'\x8C\x00\x35\x02\x09\xCC',
            'Component': b'\x8C\x00\x35\x02\x0F\xCE',
            'DVI': b'\x8C\x00\x35\x02\x20\xE3',
            'Video': b'\x8C\x00\x35\x02\x30\xF3',
            'HDMI': b'\x8C\x00\x35\x02\x44\x07',
            'SDI': b'\x8C\x00\x35\x02\x84\x47'
        }

        PIPMainInputCmdString = PIPMainInputState[value]
        self.__SetHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)

    def UpdatePIPMainInput(self, value, qualifier):

        PIPMainInputState = {
            b'\x08': 'RGB',
            b'\x09': 'YUV',
            b'\x0F': 'Component',
            b'\x20': 'DVI',
            b'\x30': 'Video',
            b'\x44': 'HDMI',
            b'\x84': 'SDI'
        }

        PIPMainInputCmdString = b'\x83\x00\x35\xFF\xFF\xB6'
        res = self.__UpdateHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPMainInputState[res[-2:-1]]
                self.WriteStatus('PIPMainInput', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Main Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'Main': b'\x8C\x00\x31\x02\x00\xBF',
            'Sub': b'\x8C\x00\x31\x02\x01\xC0'
        }

        PIPModeCmdString = PIPModeState[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeState = {
            b'\x00': 'Main',
            b'\x01': 'Sub'
        }

        PIPModeCmdString = b'\x83\x00\x31\xFF\xFF\xB2'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeState[res[-2:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPSubInput(self, value, qualifier):

        PIPSubInputState = {
            'RGB': b'\x8C\x00\x35\x02\x08\xCB',
            'YUV': b'\x8C\x00\x35\x02\x09\xCC',
            'Component': b'\x8C\x00\x35\x02\x0F\xCE',
            'DVI': b'\x8C\x00\x35\x02\x20\xE3',
            'Video': b'\x8C\x00\x35\x02\x30\xF3',
            'HDMI': b'\x8C\x00\x35\x02\x44\x07',
            'SDI': b'\x8C\x00\x35\x02\x84\x47'
        }

        PIPSubInputCmdString = PIPSubInputState[value]
        self.__SetHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)

    def UpdatePIPSubInput(self, value, qualifier):

        PIPSubInputState = {
            b'\x08': 'RGB',
            b'\x09': 'YUV',
            b'\x0F': 'Component',
            b'\x20': 'DVI',
            b'\x30': 'Video',
            b'\x44': 'HDMI',
            b'\x84': 'SDI'
        }

        PIPSubInputCmdString = b'\x83\x00\x36\xFF\xFF\xB7'
        res = self.__UpdateHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPSubInputState[res[-2:-1]]
                self.WriteStatus('PIPSubInput', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Main Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x8C\x00\x00\x02\x01\x8F',
            'Off': b'\x8C\x00\x00\x02\x00\x8E'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100,
        }
        if VolumeConstraints['Min'] <= int(value) <= VolumeConstraints['Max']:
            checksum = (0xCE + value) % 0xFF
            VolumeCmdString = b'\x8C\x10\x30\x02' + value.to_bytes(1, 'big') + checksum.to_bytes(1, 'big')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x83\x10\x30\xFF\xFF\xC1'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[-2:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x70\x01\x71': 'Limit Over',
            b'\x70\x02\x72': 'Limit Under',
            b'\x70\x03\x73': 'Command Cancelled'
        }
        if response.strip() in DEVICE_ERROR_CODES:
            errorString = '{0} {1} {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response.strip()])
            self.Error([errorString])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['Invalid/unexpected response for Set{}'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=5)
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
