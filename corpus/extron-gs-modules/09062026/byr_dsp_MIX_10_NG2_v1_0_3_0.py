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
            'ChannelMute': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelVolume': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelVolumeStatus': {'Parameters': ['Channel'], 'Status': {}},
            'Ducker': {'Status': {}},
            'MicDucking': {'Parameters': ['Microphone'], 'Status': {}},
            'MicMute': {'Parameters': ['Microphone'], 'Status': {}},
            'MicVolume': {'Parameters': ['Microphone'], 'Status': {}},
            'MicVolumeStatus': {'Parameters': ['Microphone'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Source': {'Status': {}},
            'StereoGanged': {'Parameters': ['Group'], 'Status': {}},
        }        

    def SetChannelMute(self, value, qualifier):

        ChannelStates = {
            'LINE': b'\x00',
            'SUB-L': b'\x01',
            'SUB-R': b'\x02',
            'MASTER-L': b'\x03',
            'MASTER-R': b'\x04'
        }

        channel = qualifier['Channel']
        if channel in ChannelStates:
            ValueStateValues = {
                'On': b'\x10\x02\x01\x03\xAE\x01' + ChannelStates[channel] + b'\x10\x03',
                'Off': b'\x10\x02\x01\x03\xAE\x00' + ChannelStates[channel] + b'\x10\x03'
            }

            ChannelMuteCmdString = ValueStateValues[value] + bytes([checksum(ValueStateValues[value])])
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }
        ChannelStates = {
            'LINE': b'\x00',
            'SUB-L': b'\x01',
            'SUB-R': b'\x02',
            'MASTER-L': b'\x03',
            'MASTER-R': b'\x04'
        }
        channel = qualifier['Channel']
        if channel in ChannelStates:
            s = b'\x10\x02\x01\x03\xAF\x07' + ChannelStates[channel] + b'\x10\x03'
            ChannelMuteCmdString = s + bytes([checksum(s)])
            res = self.__UpdateHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
            print('res', res)
            if res:
                try:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('ChannelMute', value, {'Channel': channel})
                except (KeyError, IndexError):
                    print('Channel Mute: Invalid/Unexpected response')
            else:
                print('Invalid Command for UpdateChannelMute')

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'LINE': b'\x00',
            'SUB-L': b'\x01',
            'SUB-R': b'\x02',
            'MASTER-L': b'\x03',
            'MASTER-R': b'\x04'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 79
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel in ChannelStates:
            x = b'\x10\x02\x01\x03\xA2' + bytes([value]) + ChannelStates[channel] + b'\x10\x03'
            ChannelVolumeCmdString = x + bytes([checksum(x)])
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):

        ChannelStates = {
            'LINE': b'\x00',
            'SUB-L': b'\x01',
            'SUB-R': b'\x02',
            'MASTER-L': b'\x03',
            'MASTER-R': b'\x04'
        }
        channel = qualifier['Channel']
        if channel in ChannelStates:
            x = b'\x10\x02\x01\x03\xAF\x02' + ChannelStates[channel] + b'\x10\x03'
            ChannelVolumeCmdString = x + bytes([checksum(x)])
            res = self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[5])
                    self.WriteStatus('ChannelVolume', value, {'Channel': channel})
                    self.WriteStatus('ChannelVolumeStatus', volumeFromDevice(value), {'Channel': channel})
                except (ValueError, KeyError, IndexError):
                    print('Invalid/Unexpected response')
            else:
                print('Invalid Command for UpdateChannelVolume')

    def UpdateChannelVolumeStatus(self, value, qualifier):

        self.UpdateChannelVolume(value, qualifier)

    def SetDucker(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x10\x02\x01\x02\xA8\x02\x10\x03\xA8',
            'Off': b'\x10\x02\x01\x02\xA8\x00\x10\x03\xAA'
        }

        DuckerCmdString = ValueStateValues[value]
        self.__SetHelper('Ducker', DuckerCmdString, value, qualifier)

    def SetMicDucking(self, value, qualifier):

        MicrophoneStates = {
            '1': b'\x10',
            '2': b'\x11',
            '3': b'\x12',
            '4': b'\x13',
            '5': b'\x14',
            '6': b'\x15'
        }
        microphone = qualifier['Microphone']
        if microphone in MicrophoneStates:
            ValueStateValues = {
                'On': b'\x10\x02\x01\x03\xA9\x01' + MicrophoneStates[microphone] + b'\x10\x03',
                'Off': b'\x10\x02\x01\x03\xA9\x00' + MicrophoneStates[microphone] + b'\x10\x03'
            }
            MicDuckingCmdString = ValueStateValues[value] + bytes([checksum(ValueStateValues[value])])
            self.__SetHelper('MicDucking', MicDuckingCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicDucking')

    def SetMicMute(self, value, qualifier):

        MicrophoneStates = {
            '1': b'\x10',
            '2': b'\x11',
            '3': b'\x12',
            '4': b'\x13',
            '5': b'\x14',
            '6': b'\x15'
        }
        microphone = qualifier['Microphone']
        if microphone in MicrophoneStates:
            ValueStateValues = {
                'On': b'\x10\x02\x01\x03\xAE\x01' + MicrophoneStates[microphone] + b'\x10\x03',
                'Off': b'\x10\x02\x01\x03\xAE\x00' + MicrophoneStates[microphone] + b'\x10\x03'
            }
            MicMuteCmdString = ValueStateValues[value] + bytes([checksum(ValueStateValues[value])])

            self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        MicrophoneStates = {
            '1': b'\x10',
            '2': b'\x11',
            '3': b'\x12',
            '4': b'\x13',
            '5': b'\x14',
            '6': b'\x15'
        }

        microphone = qualifier['Microphone']
        if microphone in MicrophoneStates:
            s = b'\x10\x02\x01\x03\xAF\x07' + MicrophoneStates[microphone] + b'\x10\x03'
            MicMuteCmdString = s + bytes([checksum(s)])
            res = self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('MicMute', value, {'Microphone': microphone})
                except (KeyError, IndexError):
                    print('Mic Mute: Invalid/Unexpected response')
            else:
                print('Invalid Command for UpdateMicMute')

    def SetMicVolume(self, value, qualifier):

        MicrophoneStates = {
            '1': b'\x10',
            '2': b'\x11',
            '3': b'\x12',
            '4': b'\x13',
            '5': b'\x14',
            '6': b'\x15'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 79
        }
        microphone = qualifier['Microphone']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            x = b'\x10\x02\x01\x03\xA3' + bytes([value]) + MicrophoneStates[microphone] + b'\x10\x03'
            MicVolumeCmdString = x + bytes([checksum(x)])
            self.__SetHelper('MicVolume', MicVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicVolume')

    def UpdateMicVolume(self, value, qualifier):

        MicrophoneStates = {
            '1': b'\x10',
            '2': b'\x11',
            '3': b'\x12',
            '4': b'\x13',
            '5': b'\x14',
            '6': b'\x15'
        }
        microphone = qualifier['Microphone']
        x = b'\x10\x02\x01\x03\xAF\x03' + MicrophoneStates[microphone] + b'\x10\x03'
        MicVolumeCmdString = x + bytes([checksum(x)])
        res = self.__UpdateHelper('MicVolume', MicVolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('MicVolume', value, {'Microphone': microphone})
            except (ValueError, IndexError):
                print('Mic Volume: Invalid/Unexpected response')

            try:
                value = int(res[5])
                self.WriteStatus('MicVolumeStatus', volumeFromDevice(value), {'Microphone': microphone})
            except (ValueError, IndexError):
                print('Mic Volume Status: Invalid/Unexpected response')

    def UpdateMicVolumeStatus(self, value, qualifier):

        self.UpdateMicVolume(value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x10\x02\x01\x03\xAB\x00\x00\x10\x03\xA8',
            '1': b'\x10\x02\x01\x03\xAB\x01\x00\x10\x03\xA9',
            '2': b'\x10\x02\x01\x03\xAB\x02\x00\x10\x03\xAA',
            '3': b'\x10\x02\x01\x03\xAB\x03\x00\x10\x03\xAB'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x10\x02\x01\x03\xAB\x00\x01\x10\x03\xA9',
            '1': b'\x10\x02\x01\x03\xAB\x01\x01\x10\x03\xA8',
            '2': b'\x10\x02\x01\x03\xAB\x02\x01\x10\x03\xAB',
            '3': b'\x10\x02\x01\x03\xAB\x03\x01\x10\x03\xAA'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x10\x02\x01\x02\xA1\x01\x10\x03\xA2',
            '2': b'\x10\x02\x01\x02\xA1\x02\x10\x03\xA1',
            '3': b'\x10\x02\x01\x02\xA1\x03\x10\x03\xA0',
            '4': b'\x10\x02\x01\x02\xA1\x04\x10\x03\xA7',
            'Off': b'\x10\x02\x01\x02\xA1\x00\x10\x03\xA3'
        }

        SourceCmdString = ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            0: 'Off'
        }

        SourceCmdString = b'\x10\x02\x01\x02\xAF\x01\x10\x03\xAC'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                print('Source: Invalid/Unexpected response')

    def SetStereoGanged(self, value, qualifier):

        GroupStates = {
            'Subgroup': b'\x01',
            'Master': b'\x02'
        }
        group = qualifier['Group']
        ValueStateValues = {
            'On': b'\x10\x02\x01\x03\xAA\x01' + GroupStates[group] + b'\x10\x03\xAA',
            'Off': b'\x10\x02\x01\x03\xAA\x00' + GroupStates[group] + b'\x10\x03\xAB'
        }

        StereoGangedCmdString = ValueStateValues[value] + bytes([checksum(ValueStateValues[value])])
        self.__SetHelper('StereoGanged', StereoGangedCmdString, value, qualifier)

    def UpdateStereoGanged(self, value, qualifier):

        GroupStates = {
            'Subgroup': b'\x01',
            'Master': b'\x02'
        }
        group = qualifier['Group']
        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        x = b'\x10\x02\x01\x03\xAF\x06' + GroupStates[group] + b'\x10\x03'
        StereoGangedCmdString = x + bytes([checksum(x)])
        res = self.__UpdateHelper('StereoGanged', StereoGangedCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('StereoGanged', value, {'Group': group})
            except (KeyError, IndexError):
                print('Stereo Ganged: Invalid/Unexpected response')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=9)
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
                
def checksum(x):
    cs = 0
    for i in x:
        cs = cs ^ i
    return cs

def volumeFromDevice(vol):
    vol = int(vol)
    if(vol <= 32):
        vol = vol / -2
    elif(vol <= 64):
        vol = vol * -1 + 16
    elif(vol < 79):
        vol = vol * -2 + 80
    else:
        vol = -76
    return vol
