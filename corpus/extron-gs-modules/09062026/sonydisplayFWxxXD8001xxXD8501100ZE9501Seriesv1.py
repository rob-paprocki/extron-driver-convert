from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from functools import reduce
from operator import add


class DeviceSerialClass:
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
            'FW-85XD8501': self.sony_10_3495_8501,
            'FW-65XD8501': self.sony_10_3495_8501,
            'FW-55XD8501': self.sony_10_3495_8501,
            'FW-75XD8501': self.sony_10_3495_8501,
            'FW-43XD8001': self.sony_10_3495_8001,
            'FW-49XD8001': self.sony_10_3495_8001,
            'FWD-100ZD9501': self.sony_10_3495_8001,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.UpdateRegex = re.compile(b'\x70[\x00-\x04][\x02][\x00-\x01][\x00-\xFF]|\x70[\x00-\x04][\x03][\x01-\x04][\x01-\x04][\x00-\xFF]|\x70[\x03-\x04][\x00-\xFF]')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x8C\x00\x44\x03\x01\x00\xD4',
            'Full': b'\x8C\x00\x44\x03\x01\x01\xD5',
            'Zoom': b'\x8C\x00\x44\x03\x01\x02\xD6',
            'Normal': b'\x8C\x00\x44\x03\x01\x03\xD7',
            'PC Normal': b'\x8C\x00\x44\x03\x01\x05\xD9',
            'PC Full 1': b'\x8C\x00\x44\x03\x01\x06\xDA',
            'PC Full 2': b'\x8C\x00\x44\x03\x01\x07\xDB'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x8C\x00\x06\x03\x01\x01\x97',
            'Off': b'\x8C\x00\x06\x03\x01\x00\x96'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x83\x00\x06\xFF\xFF\x87'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x8C\x00\x67\x03\x01\x10\x07',
            'Down': b'\x8C\x00\x67\x03\x01\x11\x08'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x83\x00\x02\xFF\xFF\x83'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[3] == 1:
                    self.WriteStatus('Input', 'TV', qualifier)
                else:
                    value = self.InputStateNames[res[3:5]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x8C\x00\x67\x03\x01\x09\x00',
            '1': b'\x8C\x00\x67\x03\x01\x00\xF7',
            '2': b'\x8C\x00\x67\x03\x01\x01\xF8',
            '3': b'\x8C\x00\x67\x03\x01\x02\xF9',
            '4': b'\x8C\x00\x67\x03\x01\x03\xFA',
            '5': b'\x8C\x00\x67\x03\x01\x04\xFB',
            '6': b'\x8C\x00\x67\x03\x01\x05\xFC',
            '7': b'\x8C\x00\x67\x03\x01\x06\xFD',
            '8': b'\x8C\x00\x67\x03\x01\x07\xFE',
            '9': b'\x8C\x00\x67\x03\x01\x08\xFF',
            'Dot': b'\x8C\x00\x67\x03\x97\x1D\xAA',
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': b'\x8C\x00\x67\x03\x01\x60\x57',
            'Up': b'\x8C\x00\x67\x03\x01\x74\x6B',
            'Down': b'\x8C\x00\x67\x03\x01\x75\x6C',
            'Left': b'\x8C\x00\x67\x03\x01\x34\x2B',
            'Right': b'\x8C\x00\x67\x03\x01\x33\x2A',
            'Select': b'\x8C\x00\x67\x03\x01\x65\x5C',
            'Return': b'\x8C\x00\x67\x03\x97\x23\xB0'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x8C\x00\x00\x02\x01\x8F',
            'Off': b'\x8C\x00\x00\x02\x00\x8E',
        }

        PowerCmdString = ValueStateValues[value]
        if value == 'Off':
            self.__SetHelper('Power', b'\x8C\x00\x01\x02\x01\x90', value, qualifier)  # Enable Standby Command
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x8C\x00\x0D\x03\x01\x01\x9E',
            'Off': b'\x8C\x00\x0D\x03\x01\x00\x9D'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = bytes((0x8C, 0, 5, 3, 1, value))
            VolumeCmdString += (reduce(add, VolumeCmdString) & 255).to_bytes(1, 'big')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: 'Limit Over (Abnormal End - over max value)',
            2: 'Limit Over (Abnormal End - under min value)',
            3: 'Command Canceled (Abnormal End)',
            4: 'Parse Error (Data Format Error)'
        }
        if response[1] in DEVICE_ERROR_CODES:
            self.Error(['{0} Error:{1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['{0}: No response received'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
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

    def sony_10_3495_8501(self):

        self.InputStateValues = {
            'TV': b'\x8C\x00\x02\x02\x01\x91',
            'Video': b'\x8C\x00\x02\x03\x02\x01\x94',
            'Component': b'\x8C\x00\x02\x03\x03\x01\x95',
            'HDMI 1': b'\x8C\x00\x02\x03\x04\x01\x96',
            'HDMI 2': b'\x8C\x00\x02\x03\x04\x02\x97',
            'HDMI 3': b'\x8C\x00\x02\x03\x04\x03\x98',
            'HDMI 4': b'\x8C\x00\x02\x03\x04\x04\x99'
        }
        self.InputStateNames = {
            b'\x02\x01': 'Video',
            b'\x03\x01': 'Component',
            b'\x04\x01': 'HDMI 1',
            b'\x04\x02': 'HDMI 2',
            b'\x04\x03': 'HDMI 3',
            b'\x04\x04': 'HDMI 4'
        }

    def sony_10_3495_8001(self):

        self.InputStateValues = {
            'TV': b'\x8C\x00\x02\x02\x01\x91',
            'Video': b'\x8C\x00\x02\x03\x02\x01\x94',
            'HDMI 1': b'\x8C\x00\x02\x03\x04\x01\x96',
            'HDMI 2': b'\x8C\x00\x02\x03\x04\x02\x97',
            'HDMI 3': b'\x8C\x00\x02\x03\x04\x03\x98',
            'HDMI 4': b'\x8C\x00\x02\x03\x04\x04\x99'
        }
        self.InputStateNames = {
            b'\x02\x01': 'Video',
            b'\x04\x01': 'HDMI 1',
            b'\x04\x02': 'HDMI 2',
            b'\x04\x03': 'HDMI 3',
            b'\x04\x04': 'HDMI 4'
        }

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


class DeviceEthernetClass:
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
            'FW-43XD8001': self.sony_10_3495_8001,
            'FW-49XD8001': self.sony_10_3495_8001,
            'FWD-100ZD9501': self.sony_10_3495_8001,
            'FW-55XD8501': self.sony_10_3495_8501,
            'FW-65XD8501': self.sony_10_3495_8501,
            'FW-75XD8501': self.sony_10_3495_8501,
            'FW-85XD8501': self.sony_10_3495_8501,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCAMUT0000000000000001\n',
            'Off': '*SCAMUT0000000000000000\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '*SEAMUT################\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '*SCIRCC0000000000000033\n',
            'Down': '*SCIRCC0000000000000034\n'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        HDMIStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4'
        }

        InputCmdString = '*SEINPT################\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                temp = res[14]
                if temp == '1':
                    self.WriteStatus('Input', HDMIStateValues[res[22]], qualifier)
                else:
                    self.WriteStatus('Input', self.InputStateNames[temp], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '*SCIRCC0000000000000027\n',
            '1': '*SCIRCC0000000000000018\n',
            '2': '*SCIRCC0000000000000019\n',
            '3': '*SCIRCC0000000000000020\n',
            '4': '*SCIRCC0000000000000021\n',
            '5': '*SCIRCC0000000000000022\n',
            '6': '*SCIRCC0000000000000023\n',
            '7': '*SCIRCC0000000000000024\n',
            '8': '*SCIRCC0000000000000025\n',
            '9': '*SCIRCC0000000000000026\n',
            '11': '*SCIRCC0000000000000028\n',
            '12': '*SCIRCC0000000000000029\n',
            'Dot': '*SCIRCC0000000000000038\n'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '*SCIRCC0000000000000009\n',
            'Down': '*SCIRCC0000000000000010\n',
            'Left': '*SCIRCC0000000000000012\n',
            'Right': '*SCIRCC0000000000000011\n',
            'Confirm': '*SCIRCC0000000000000013\n',
            'Home': '*SCIRCC0000000000000006\n',
            'Return': '*SCIRCC0000000000000008\n',
            'Top Menu': '*SCIRCC0000000000000088\n',
            'Popup Menu': '*SCIRCC0000000000000089\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPIPI0000000000000001\n',
            'Off': '*SCPIPI0000000000000000\n'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PIPModeCmdString = '*SEPIPI################\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode : Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPOWR0000000000000001\n',
            'Off': '*SCPOWR0000000000000000\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '*SEPOWR################\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPMUT0000000000000001\n',
            'Off': '*SCPMUT0000000000000000\n'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '*SEPMUT################\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '*SCVOLU0000000000000' + '{0:03d}'.format(value) + '\n'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'FFFFFFFFFFFFFFFF': 'Invalid Parameter',
            'NNNNNNNNNNNNNNNN': 'The command does not exist',
        }

        if response[7:-1] in DEVICE_ERROR_CODES:
            self.Error(['ERROR:{0}'.format(DEVICE_ERROR_CODES[response[7:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
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

    def sony_10_3495_8501(self):

        self.InputStateValues = {
            'TV': '*SCINPT0000000000000000\n',
            'Video': '*SCINPT0000000300000001\n',
            'Component': '*SCINPT0000000400000001\n',
            'HDMI 1': '*SCINPT0000000100000001\n',
            'HDMI 2': '*SCINPT0000000100000002\n',
            'HDMI 3': '*SCINPT0000000100000003\n',
            'HDMI 4': '*SCINPT0000000100000004\n',
            'SCART': '*SCINPT0000000200000001\n'
        }
        self.InputStateNames = {
            '0': 'TV',
            '3': 'Video',
            '4': 'Component',
            '2': 'SCART'
        }

    def sony_10_3495_8001(self):

        self.InputStateValues = {
            'TV': '*SCINPT0000000000000000\n',
            'Video': '*SCINPT0000000300000001\n',
            'HDMI 1': '*SCINPT0000000100000001\n',
            'HDMI 2': '*SCINPT0000000100000002\n',
            'HDMI 3': '*SCINPT0000000100000003\n',
            'HDMI 4': '*SCINPT0000000100000004\n',
            'SCART': '*SCINPT0000000200000001\n'
        }
        self.InputStateNames = {
            '0': 'TV',
            '3': 'Video',
            '2': 'SCART'
        }

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
