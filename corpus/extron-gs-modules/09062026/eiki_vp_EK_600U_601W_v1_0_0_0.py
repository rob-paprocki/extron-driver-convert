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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DInvert': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'DMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        Values = {
            '4:3': 'CF_ASPECT_1\r',
            '16:10': 'CF_ASPECT_3\r',
            'Letterbox': 'CF_ASPECT_5\r',
            'Native': 'CF_ASPECT_6\r'
        }

        self.__SetHelper('AspectRatio', Values[value], value, qualifier)

    def SetAudioMute(self, value, qualifier):

        Values = {
            'On': 'CF_MUTE_1\r',
            'Off': 'CF_MUTE_0\r'
        }

        self.__SetHelper('AudioMute', Values[value], value, qualifier)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'C89\r', value, qualifier)

    def SetAVMute(self, value, qualifier):

        Values = {
            'On': 'CF_KYAVMUTE_1\r',
            'Off': 'CF_KYAVMUTE_0\r'
        }

        self.__SetHelper('AVMute', Values[value], value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        Values = {
            'Off': 'CF_CCAPTIONDISP_0\r',
            '1': 'CF_CCAPTIONDISP_1\r',
            '2': 'CF_CCAPTIONDISP_2\r'
        }

        self.__SetHelper('ClosedCaption', Values[value], value, qualifier)

    def SetDInvert(self, value, qualifier):

        Values = {
            'On': 'CF_3D-INVERT_1\r',
            'Off': 'CF_3D-INVERT_0\r'
        }

        self.__SetHelper('DInvert', Values[value], value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        Values = {
            'Presentation': 'CF_IMAGE_0\r',
            'Bright': 'CF_IMAGE_1\r',
            'Movie': 'CF_IMAGE_2\r',
            'sRGB': 'CF_IMAGE_3\r',
            'Blackboard': 'CF_IMAGE_4\r',
            'DICOM SIM': 'CF_IMAGE_6\r',
            'User': 'CF_IMAGE_7\r',
            '3D': 'CF_IMAGE_5\r'
        }

        self.__SetHelper('DisplayMode', Values[value], value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        Values = {
            '0': 'Presentation',
            '1': 'Bright',
            '2': 'Movie',
            '3': 'sRGB',
            '4': 'Blackboard',
            '6': 'DICOM SIM',
            '7': 'User',
            '5': '3D'
        }

        res = self.__UpdateHelper('DisplayMode', 'CR_IMAGE\r', value, qualifier)
        if res:
            res = res.decode()
            try:
                self.WriteStatus('DisplayMode', Values[res[0]], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateDisplayMode')

    def SetDMode(self, value, qualifier):

        Values = {
            'DLP-Link': 'CF_3D-MODE_1\r',
            'VESA 3D': 'CF_3D-MODE_2\r',
            'Off': 'CF_3D-MODE_0\r'
        }

        self.__SetHelper('DMode', Values[value], value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        Values = {
            'On': 'CF_KEYPADLOCK_1\r',
            'Off': 'CF_KEYPADLOCK_0\r'
        }

        self.__SetHelper('ExecutiveMode', Values[value], value, qualifier)

    def SetInput(self, value, qualifier):

        Values = {
            'HDMI 1': 'C36\r',
            'HDMI 2': 'C38\r',
            'DisplayPort': 'C17\r',
            'VGA 1': 'C05\r',
            'VGA 2': 'C06\r',
            'Video': 'C07\r',
            'S-Video': 'C34\r'
        }

        self.__SetHelper('Input', Values[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        Values = {
            '1': 'VGA 1',
            '2': 'VGA 2',
            '3': 'HDMI 1',
            '4': 'HDMI 2',
            '5': 'Video',
            '6': 'S-Video',
            '7': 'DisplayPort',
            '8': 'HDBaseT'
        }

        res = self.__UpdateHelper('Input', 'CR1\r', value, qualifier)
        if res:
            res = res.decode()
            try:
                self.WriteStatus('Input', Values[res[0]], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'CR3\r', value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res)
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        Values = {
            'Up': 'C3C\r',
            'Down': 'C3B\r',
            'Left': 'C3A\r',
            'Right': 'C3D\r',
            'Enter': 'C3F\r',
            'Menu': 'CF_KYMENU\r'
        }

        self.__SetHelper('MenuNavigation', Values[value], value, qualifier)

    def SetPower(self, value, qualifier):

        Values = {
            'On': 'C00\r',
            'Off': 'C01\r',
        }

        self.__SetHelper('Power', Values[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        Values = {
            '0': 'Reset',
            '1': 'Off',
            '2': 'On',
            '3': 'Cooling Down',
            '4': 'Warming Up',
            '5': 'Power Up'
        }

        res = self.__UpdateHelper('Power', 'CR0\r', value, qualifier)
        if res:
            res = res.decode()
            try:
                value = Values[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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