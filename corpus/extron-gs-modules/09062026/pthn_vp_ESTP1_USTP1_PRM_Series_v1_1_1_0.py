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
        self.Models = {
            'PRM 35': self.pthn_1_819_other,
            'EST-P1': self.pthn_1_819_other,
            'UST-P1': self.pthn_1_819_ust,
            'PRM-32': self.pthn_1_819_other,
            'PRM-45': self.pthn_1_819_other,
            'PRM-45A': self.pthn_1_819_a,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampHours': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            'Fill': '~sA0\r',
            '4:3': '~sA1\r',
            '16:9': '~sA2\r',
            'LetterBox': '~sA3\r',
            'Native': '~sA4\r'
        }

        AspectRatioCmdString = AspectRatioValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioValues = {
            'Fill\r': 'Fill',
            '4:3\r': '4:3',
            '16:9\r': '16:9',
            'LetterBox\r': 'LetterBox',
            'Native\r': 'Native'
        }

        AspectRatioCmdString = '~qA\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AspectRatio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~AI\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '~rF\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'On\r': 'On',
            'Off\r': 'Off'
        }

        FreezeCmdString = '~qZ\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '~qS\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputNames[res]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '~qL\r'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('LampHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['LampHours: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Menu': '~rM\r',
            'Up': '~rU\r',
            'Down': '~rD\r',
            'Left': '~rL\r',
            'Right': '~rR\r',
            'Enter': '~rN\r'
        }

        MenuNavigationCmdString = MenuNavigationValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = '~rT\r'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            'On\r': 'On',
            'Off\r': 'Off'
        }

        MuteCmdString = '~qU\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerValues = {
            'On': '~PN\r',
            'Off': '~PF\r'
        }

        PowerCmdString = PowerValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerValues = {
            'On\r': 'On',
            'Off\r': 'Off'
        }

        PowerCmdString = '~qP\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerValues[res]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = '~rB\r'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On\r': 'On',
            'Off\r': 'Off'
        }

        VideoMuteCmdString = '~qK\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '~rV\r',
            'Down': '~rW\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = '~qM\r'
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['VolumeStatus: Invalid/unexpected response'])

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pthn_1_819_a(self):

        self.InputValues = {
            'RGB 1': '~SR\r',
            'RGB 2': '~SG\r',
            'Video': '~SV\r',
            'S-Video': '~SS\r',
            'HDMI 1': '~SH\r',
            'HDMI 2': '~SI\r'
        }

        self.InputNames = {
            'RGB\r': 'RGB 1',
            'RGB2\r': 'RGB 2',
            'Video\r': 'Video',
            'S-Video\r': 'S-Video',
            'HDMI\r': 'HDMI 1',
            'HDMI2\r': 'HDMI 2',
            'NoSignal\r': 'No Signal'
        }

    def pthn_1_819_other(self):

        self.InputValues = {
            'RGB 1': '~SR\r',
            'RGB 2': '~SG\r',
            'Video': '~SV\r',
            'S-Video': '~SS\r',
            'HDMI': '~SH\r',
        }

        self.InputNames = {
            'RGB\r': 'RGB 1',
            'RGB2\r': 'RGB 2',
            'Video\r': 'Video',
            'S-Video\r': 'S-Video',
            'HDMI\r': 'HDMI',
            'NoSignal\r': 'No Signal'
        }

    def pthn_1_819_ust(self):

        self.InputValues = {
            'RGB 1': '~SR\r',
            'RGB 2': '~SG\r',
            'Video': '~SV\r',
            'HDMI': '~SH\r',
        }

        self.InputNames = {
            'RGB\r': 'RGB 1',
            'RGB2\r': 'RGB 2',
            'Video\r': 'Video',
            'HDMI\r': 'HDMI',
            'NoSignal\r': 'No Signal'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    #  Send Control Commands
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
