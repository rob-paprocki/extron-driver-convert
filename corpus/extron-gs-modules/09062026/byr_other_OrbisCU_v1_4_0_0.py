from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import time


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutMode': {'Status': {}},
            'ClearButton': {'Parameters': ['Mic ID'], 'Status': {}},
            'ClearButtonStatus': {'Parameters': ['Mic ID'], 'Status': {}},
            'ConferenceMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'FuncButton': {'Parameters': ['Mic ID'], 'Status': {}},
            'FuncButtonStatus': {'Parameters': ['Mic ID'], 'Status': {}},
            'Microphone': {'Parameters': ['Mic ID'], 'Status': {}},
            'MicrophoneMode': {'Parameters': ['Mic ID'], 'Status': {}},
            'MicsOrRequestsOff': {'Parameters': ['Type'], 'Status': {}},
            'NumberOfMicrophones': {'Status': {}},
            'PCControl': {'Status': {}},
            'Power': {'Status': {}},
            'Priority': {'Status': {}},
            'RecordControl': {'Status': {}},
            'RecordingMode': {'Status': {}},
            'SpeakerOutMode': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x02\x06(\x00|\x01|\x02)\x0D\x0A'), self.__MatchAudioOutMode, None)
            self.AddMatchString(re.compile(b'\x07\x02\x01(\x00|\x01|\x02)\x0D\x0A'), self.__MatchConferenceMode, None)
            self.AddMatchString(re.compile(b'\x01\x05([\x00-\xFF]{3})\x02(\x03|\x02)\x0D\x0A'), self.__MatchFuncButtonStatus, None)
            self.AddMatchString(re.compile(b'[\x02|\x0D]\x04([\x00-\xFF]{3})(\x01|\x00)\x0D\x0A'), self.__MatchMicrophone, None)
            self.AddMatchString(re.compile(b'\x07\x02\x02([\x01-\x08])\x0D\x0A'), self.__MatchNumberOfMicrophones, None)
            self.AddMatchString(re.compile(b'\x07\x02\x08(\x00|\x01])\x0D\x0A'), self.__MatchPCControl, None)
            self.AddMatchString(re.compile(b'\x07\x02\x03(\x00|\x01|\x02)\x0D\x0A'), self.__MatchPriority, None)
            self.AddMatchString(re.compile(b'\x49\x02\\x5B(\x01|\x00)\x0D\x0A'), self.__MatchRecordControl, None)
            self.AddMatchString(re.compile(b'\\x28\x01(\x00|\x01|\x02|\x03)\x0D\x0A'), self.__MatchRecordingMode, None)
            self.AddMatchString(re.compile(b'\x07\x02\x05(\x00|\x01|\x02)\x0D\x0A'), self.__MatchSpeakerOutMode, None)
            self.AddMatchString(re.compile(b'\x04\x03(.*?)\x0D\x0A'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'\x07\x02\x04([\x00-\x0A])\x0D\x0A'), self.__MatchVolume, None)

    def SetAudioOutMode(self, value, qualifier):

        ValueStateValues = {
            'Mix': b'\x03\x02\x06\x00\x0D\x0A',
            'Mic': b'\x03\x02\x06\x01\x0D\x0A',
            'Aux In': b'\x03\x02\x06\x02\x0D\x0A'
        }
        AudioOutModeCmdString = ValueStateValues[value]
        self.__SetHelper('AudioOutMode', AudioOutModeCmdString, value, qualifier)

    def UpdateAudioOutMode(self, value, qualifier):

        AudioOutModeCmdString = b'\x04\x01\x06\x0D\x0A'
        self.__UpdateHelper('AudioOutMode', AudioOutModeCmdString, value, qualifier)

    def __MatchAudioOutMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Mix',
            b'\x01': 'Mic',
            b'\x02': 'Aux In'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioOutMode', value, None)

    def SetClearButton(self, value, qualifier):

        MicID = qualifier['Mic ID']
        if 1 <= MicID <= 4194223:
            Mic = pack('>i', MicID)[1:]
            ClearButtonCmdString = Mic.join([b'\x2B\x03', b'\x0D\x0A'])
            self.__SetHelper('ClearButton', ClearButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClearButton')

    def SetConferenceMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x03\x02\x01\x00\x0D\x0A',
            'FiFo': b'\x03\x02\x01\x01\x0D\x0A',
            'Voice': b'\x03\x02\x01\x02\x0D\x0A'
        }
        ConferenceModeCmdString = ValueStateValues[value]
        self.__SetHelper('ConferenceMode', ConferenceModeCmdString, value, qualifier)

    def UpdateConferenceMode(self, value, qualifier):

        ConferenceModeCmdString = b'\x04\x01\x01\x0D\x0A'
        self.__UpdateHelper('ConferenceMode', ConferenceModeCmdString, value, qualifier)

    def __MatchConferenceMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'FiFo',
            b'\x02': 'Voice'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ConferenceMode', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x10\x04\x00\x00\x01\x01\x0D\x0A',
            'Off': b'\x10\x04\x00\x00\x01\x00\x0D\x0A'
        }
        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = b'\x1C\x00\x0D\x0A'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = [str(Number) for Number in match.group(1)]
        value = '.'.join(value)
        self.WriteStatus('FirmwareVersion', value, None)

    def SetFuncButton(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x0D\x0A',
            'Off': b'\x00\x0D\x0A'
        }
        MicID = qualifier['Mic ID']
        if 1 <= MicID <= 4194223:
            Mic = pack('>i', MicID)[1:]
            FuncButtonCmdString = Mic.join([b'\x6A\x04', ValueStateValues[value]])
            self.__SetHelper('FuncButton', FuncButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFuncButton')

    def __MatchFuncButtonStatus(self, match, tag):

        MicID = unpack('>i', b'\x00' + match.group(1))
        if match.group(2) == b'\x03':
            self.WriteStatus('FuncButtonStatus', 'Pressed', {'Mic ID': MicID[0]})
            time.sleep(.3)
            self.WriteStatus('FuncButtonStatus', 'Reset', {'Mic ID': MicID[0]})
        else:
            self.WriteStatus('ClearButtonStatus', 'Pressed', {'Mic ID': MicID[0]})
            time.sleep(.3)
            self.WriteStatus('ClearButtonStatus', 'Reset', {'Mic ID': MicID[0]})

    def SetMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x0D\x0A',
            'Off': b'\x00\x0D\x0A'
        }
        MicID = qualifier['Mic ID']
        if 1 <= MicID <= 4194223:
            Mic = pack('>i', MicID)[1:]
            MicrophoneCmdString = Mic.join([b'\x01\x04', ValueStateValues[value]])
            self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophone')

    def __MatchMicrophone(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        MicID = unpack('>i', b'\x00' + match.group(1))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Microphone', value, {'Mic ID': MicID[0]})

    def SetMicrophoneMode(self, value, qualifier):

        ValueStateValues = {
            'Normal Delegate': b'\x00\x0D\x0A',
            'Semi-Chairman': b'\x02\x0D\x0A',
            'Locked': b'\x01\x0D\x0A'
        }
        MicID = qualifier['Mic ID']
        if 1 <= MicID <= 4194223:
            Mic = pack('>i', MicID)[1:]
            MicrophoneModeCmdString = Mic.join([b'\x30\x04', ValueStateValues[value]])
            self.__SetHelper('MicrophoneMode', MicrophoneModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def SetMicsOrRequestsOff(self, value, qualifier):

        TypeStates = {
            'All Delegates': b'\x01\x04\x00\x00\x00\x00\x0D\x0A',
            'All Delegates and All Chairman': b'\x01\x04\x00\x00\x01\x00\x0D\x0A'
        }
        type = qualifier['Type']
        if type in TypeStates:
            MicsOrRequestsOffCmdString = TypeStates[type]
            self.__SetHelper('MicsOrRequestsOff', MicsOrRequestsOffCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicsOrRequestsOff')

    def SetNumberOfMicrophones(self, value, qualifier):

        NumberOfMicrophonesCmdString = pack('<B', int(value)).join([b'\x03\x02\x02', b'\x0D\x0A'])
        self.__SetHelper('NumberOfMicrophones', NumberOfMicrophonesCmdString, value, qualifier)

    def UpdateNumberOfMicrophones(self, value, qualifier):

        NumberOfMicrophonesCmdString = b'\x04\x01\x02\x0D\x0A'
        self.__UpdateHelper('NumberOfMicrophones', NumberOfMicrophonesCmdString, value, qualifier)

    def __MatchNumberOfMicrophones(self, match, tag):

        value = str(ord(match.group(1)))
        self.WriteStatus('NumberOfMicrophones', value, None)

    def SetPCControl(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x03\x02\x08\x01\x0D\x0A',
            'Off': b'\x03\x02\x08\x00\x0D\x0A'
        }
        PCControlCmdString = ValueStateValues[value]
        self.__SetHelper('PCControl', PCControlCmdString, value, qualifier)

    def UpdatePCControl(self, value, qualifier):

        PCControlCmdString = b'\x04\x01\x08\x0D\x0A'
        self.__UpdateHelper('PCControl', PCControlCmdString, value, qualifier)

    def __MatchPCControl(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PCControl', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x19\x01\x02\x0D\x0A',
            'Off': b'\x19\x01\x01\x0D\x0A'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetPriority(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x03\x02\x03\x00\x0D\x0A',
            'Mute': b'\x03\x02\x03\x01\x0D\x0A',
            'External Control': b'\x03\x02\x03\x02\x0D\x0A'
        }
        PriorityCmdString = ValueStateValues[value]
        self.__SetHelper('Priority', PriorityCmdString, value, qualifier)

    def UpdatePriority(self, value, qualifier):

        PriorityCmdString = b'\x04\x01\x03\x0D\x0A'
        self.__UpdateHelper('Priority', PriorityCmdString, value, qualifier)

    def __MatchPriority(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Mute',
            b'\x02': 'External Control'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Priority', value, None)

    def SetRecordControl(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\x11\x01\x01\x0D\x0A',
            'Stop': b'\x11\x01\x00\x0D\x0A'
        }
        RecordControlCmdString = ValueStateValues[value]
        self.__SetHelper('RecordControl', RecordControlCmdString, value, qualifier)

    def __MatchRecordControl(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Start',
            b'\x00': 'Stop'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('RecordControl', value, None)

    def SetRecordingMode(self, value, qualifier):

        ValueStateValues = {
            'Disabled': b'\x5F\x01\x00\x0D\x0A',
            'Mic': b'\x5F\x01\x02\x0D\x0A',
            'Aux In': b'\x5F\x01\x01\x0D\x0A',
            'Mix': b'\x5F\x01\x03\x0D\x0A'
        }
        RecordingModeCmdString = ValueStateValues[value]
        self.__SetHelper('RecordingMode', RecordingModeCmdString, value, qualifier)

    def UpdateRecordingMode(self, value, qualifier):

        RecordingModeCmdString = b'\x60\x00\x0D\x0A'
        self.__UpdateHelper('RecordingMode', RecordingModeCmdString, value, qualifier)

    def __MatchRecordingMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Disabled',
            b'\x02': 'Mic',
            b'\x01': 'Aux In',
            b'\x03': 'Mix'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('RecordingMode', value, None)

    def SetSpeakerOutMode(self, value, qualifier):

        ValueStateValues = {
            'Mix': b'\x03\x02\x05\x00\x0D\x0A',
            'Mic': b'\x03\x02\x05\x01\x0D\x0A',
            'Aux In': b'\x03\x02\x05\x02\x0D\x0A'
        }
        SpeakerOutModeCmdString = ValueStateValues[value]
        self.__SetHelper('SpeakerOutMode', SpeakerOutModeCmdString, value, qualifier)

    def UpdateSpeakerOutMode(self, value, qualifier):

        SpeakerOutModeCmdString = b'\x04\x01\x05\x0D\x0A'
        self.__UpdateHelper('SpeakerOutMode', SpeakerOutModeCmdString, value, qualifier)

    def __MatchSpeakerOutMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Mix',
            b'\x01': 'Mic',
            b'\x02': 'Aux In'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('SpeakerOutMode', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('<B', value).join([b'\x03\x02\x04', b'\x0D\x0A'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x04\x01\x04\x0D\x0A'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('>b', match.group(1))[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

            # Check incoming unsolicited data to see if it was matched with device expectancy.

    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
