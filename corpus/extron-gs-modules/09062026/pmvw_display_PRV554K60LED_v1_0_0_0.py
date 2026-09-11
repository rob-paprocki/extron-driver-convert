from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemoteLock': {'Status': {}},
            'KeyLock': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControl': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 254:
            self._DeviceID = int(value)
        else:
            self.Error(['Device ID should be a value between 1 to 254 or Broadcast.'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x17, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        AudioMuteCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x17)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x61, 0x01)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 0x02,
            'DisplayPort': 0x06
        }

        InputCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x01, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x02: 'HDMI',
            0x06: 'DisplayPort'
        }

        InputCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x01)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        IRRemoteLockCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x36, ValueStateValues[value])
        self.__SetHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def UpdateIRRemoteLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        IRRemoteLockCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x36)
        res = self.__UpdateHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('IRRemoteLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Lock: Invalid/unexpected response'])

    def SetKeyLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        KeyLockCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x35, ValueStateValues[value])
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def UpdateKeyLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        KeyLockCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x35)
        res = self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('KeyLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Key Lock: Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PictureInPictureCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x13, ValueStateValues[value])
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        PictureInPictureCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x13)
        res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture In Picture: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 0x02,
            'DisplayPort': 0x06
        }

        PIPInputCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x14, ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            0x02: 'HDMI',
            0x06: 'DisplayPort'
        }

        PIPInputCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x14)
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03
        }

        PIPPositionCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x16, ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            0x00: '1',
            0x01: '2',
            0x02: '3',
            0x03: '4'
        }

        PIPPositionCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x16)
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02
        }

        PIPSizeCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x15, ValueStateValues[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            0x00: '1',
            0x01: '2',
            0x02: '3'
        }

        PIPSizeCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x15)
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0xFE, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        PowerCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0xFE)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRemoteControl(self, value, qualifier):

        ValueStateValues = {
            'Input': 0x13,
            'PR+': 0x47,
            'PR-': 0x4B,
            'Vol Up': 0x53,
            'Vol Down': 0x57,
            'Mute': 0x03,
            'Sound Standard': 0x4A,
            'Picture Standard': 0x07,
            'Menu': 0x43,
            'Status': 0x06,
            'PIP On': 0x08,
            'PIP Pos': 0x48,
            'Still': 0x0A,
            'PIC Size': 0x4D,
            'Exit': 0x50,
            'PC': 0x58,
            '0': 0x1E,
            '1': 0x1D,
            '2': 0x1C,
            '3': 0x46,
            '4': 0x15,
            '5': 0x13,
            '6': 0x45,
            '7': 0x00,
            '8': 0x1F,
            '9': 0x1B,
            'Enter': 0x04,
            'Sleep': 0x0B
        }

        RemoteControlCmdString = pack('5B', 0xF4, 0x88, self._DeviceID, 0xFD, ValueStateValues[value])
        self.__SetHelper('RemoteControl', RemoteControlCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        VideoMuteCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x62, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        VideoMuteCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x62)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('6B', 0xF5, 0x88, self._DeviceID, 0xFE, 0x66, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('5B', 0xF4, 0x89, self._DeviceID, 0xFC, 0x66)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[1]
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=2)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=2)
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
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)


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
