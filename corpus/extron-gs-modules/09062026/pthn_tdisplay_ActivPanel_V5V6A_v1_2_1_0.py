from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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
            'ActivPanel V5 70 HD': self.pthn_39_3011_A,
            'ActivPanel V5 75 HD': self.pthn_39_3011_A,
            'ActivPanel V6 75 4K': self.pthn_39_3011_B,
            'ActivPanel V6 86 4K': self.pthn_39_3011_B,
            'ActivPanel V6 65 4K': self.pthn_39_3011_A,
            'ActivPanel V6 70 HD': self.pthn_39_3011_A,
            'ActivPanel V5 75 4K': self.pthn_39_3011_B,
            'ActivPanel V5 86 4K': self.pthn_39_3011_B,
            'AP5-70': self.pthn_39_3011_A,
            'AP5-75': self.pthn_39_3011_A,
            'AP6-70': self.pthn_39_3011_A,
            'AP5-75-4K': self.pthn_39_3011_B,
            'AP5-86-4K': self.pthn_39_3011_B,
            'AP6-65-4K': self.pthn_39_3011_A,
            'AP6-75-4K': self.pthn_39_3011_B,
            'AP6-86-4K': self.pthn_39_3011_B,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xF6\x02\x00\x01\xF9\x6F',
            'Off': b'\xF6\x02\x00\x00\xF8\x6F'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\xF6\x02\x02\x00\xFA\x6F'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xF6\x37\x01\x00\x2E\x6F',
            'Off': b'\xF6\x37\x01\x01\x2F\x6F'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        ExecutiveModeCmdString = b'\xF6\x37\x02\x00\x2F\x6F'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode : Invalid/Unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xF6\x32\x01\x01\x2A\x6F',
            'Off': b'\xF6\x32\x01\x02\x2B\x6F'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\xF6\x32\x02\x00\x2A\x6F'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/Unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self.Inputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xF6\x30\x02\x00\x28\x6F'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStates[res[3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xF6\x40\x00\x0C\x42\x6F',
            'Up': b'\xF6\x40\x00\x0E\x44\x6F',
            'Down': b'\xF6\x40\x00\x0F\x45\x6F',
            'Left': b'\xF6\x40\x00\x11\x47\x6F',
            'Right': b'\xF6\x40\x00\x10\x46\x6F',
            'Enter': b'\xF6\x40\x00\x12\x48\x6F',
            'Exit': b'\xF6\x40\x00\x0D\x43\x6F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xF6\x01\x01\x01\xF9\x6F',
            'Off': b'\xF6\x01\x01\x00\xF8\x6F'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off'
        }

        PowerCmdString = b'\xF6\x01\x02\x00\xF9\x6F'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xF6\x35\x01\x00\x2C\x6F',
            'Off': b'\xF6\x35\x01\x01\x2D\x6F'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b'\xF6\x35\x02\x00\x2D\x6F'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            chksum = 0x03 + value
            VolumeCmdString = pack('>6B', 0xF6, 0x0C, 0x01, value, chksum, 0x6F)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xF6\x0C\x02\x00\x04\x6F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x6F')
            if not res:
                self.Error(['{} : Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x6F')
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

    def pthn_39_3011_A(self):

        self.Inputs = {
            'CVBS': b'\xF6\x30\x01\x01\x28\x6F',
            'YPbPr': b'\xF6\x30\x01\x06\x2D\x6F',
            'VGA': b'\xF6\x30\x01\x08\x2F\x6F',
            'HDMI 1': b'\xF6\x30\x01\x09\x30\x6F',
            'HDMI 2': b'\xF6\x30\x01\x0A\x31\x6F',
            'HDMI 3': b'\xF6\x30\x01\x13\x3A\x6F',
            'OPS': b'\xF6\x30\x01\x12\x39\x6F',
            'Multi-Media': b'\xF6\x30\x01\x0B\x32\x6F'
        }

        self.InputStates = {
            1: 'CVBS',
            6: 'YPbPr',
            8: 'VGA',
            9: 'HDMI 1',
            10: 'HDMI 2',
            19: 'HDMI 3',
            18: 'OPS',
            11: 'Multi-Media'
        }

    def pthn_39_3011_B(self):

        self.Inputs = {
            'CVBS': b'\xF6\x30\x01\x01\x28\x6F',
            'YPbPr': b'\xF6\x30\x01\x06\x2D\x6F',
            'VGA': b'\xF6\x30\x01\x08\x2F\x6F',
            'HDMI 1': b'\xF6\x30\x01\x09\x30\x6F',
            'HDMI 2': b'\xF6\x30\x01\x0A\x31\x6F',
            'HDMI 3': b'\xF6\x30\x01\x13\x3A\x6F',
            'HDMI 4': b'\xF6\x30\x01\x14\x3B\x6F',
            'OPS': b'\xF6\x30\x01\x12\x39\x6F',
            'Multi-Media': b'\xF6\x30\x01\x0B\x32\x6F'
        }

        self.InputStates = {
            1: 'CVBS',
            6: 'YPbPr',
            8: 'VGA',
            9: 'HDMI 1',
            10: 'HDMI 2',
            19: 'HDMI 3',
            20: 'HDMI 4',
            18: 'OPS',
            11: 'Multi-Media'
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
