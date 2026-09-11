from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AudioMute': {'Parameters': ['Zone'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'Power': {'Parameters': ['Zone'], 'Status': {}},
            'VolumeMainZoneSections': {'Parameters': ['Section'], 'Status': {}},
            'VolumeMainZone': {'Status': {}},
            'VolumeZone2and3': {'Parameters': ['Zone'], 'Status': {}}
        }

        self.ZoneNames = {
            'Main': '1',
            'Zone 2': '2',
            'Zone 3': '3'
        }

        self.ZoneDecode = {
            '1': 'Main',
            '2': 'Zone 2',
            '3': 'Zone 3'
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'P(1|2|3)S(0|1|2|3|4|5|d|e|f|6|g|h|i|7|j|8|9|c)V(\-|\+)(\d{2}).(\d{1,2})M(1|0)'), self.__MatchZoneStatus, None)
            self.AddMatchString(re.compile(b'P1V(F|C|R|B) ?(\+|\-)(\d{1,2}).(\d{1,2})'), self.__MatchVolumeMainZoneSections, None)
            self.AddMatchString(re.compile(b'P(1|2|3)P(1|0)\n'), self.__MatchPower, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        ZoneNum = self.ZoneNames[qualifier['Zone']]

        AudioMuteCmdString = 'P{0}M{1}\n'.format(ZoneNum, AudioMuteStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On': 'FPL1\n',
            'Off': 'FPL0\n'
        }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'CD': '0',
            '2-Ch BAL': '1',
            '6-Ch S/E': '2',
            'Tape': '3',
            'FM/AM': '4',
            'DVD1': '5',
            'DVD2': 'd',
            'DVD3': 'e',
            'DVD4': 'f',
            'TV1': '6',
            'TV2': 'g',
            'TV3': 'h',
            'TV4': 'i',
            'VCR': '8',
            'SAT1': '7',
            'SAT2': 'j',
            'Aux': '9',
            'Main': 'c',
        }
        ZoneNum = self.ZoneNames[qualifier['Zone']]

        InputCmdString = 'P{0}S{1}\n'.format(ZoneNum, InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '1',
            'Off': '0',
        }

        ZoneNum = self.ZoneNames[qualifier['Zone']]

        PowerCmdString = 'P{0}P{1}\n'.format(ZoneNum, PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ZoneNum = self.ZoneNames[qualifier['Zone']]
        PowerCmdString = 'P{0}P?\n'.format(ZoneNum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',
        }
        qualifier = {'Zone': self.ZoneDecode[str(int(match.group(1).decode()))]}
        value = PowerStateNames[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def SetVolumeMainZoneSections(self, value, qualifier):

        SectionStates = {
            'Front': 'P1VF{0}\n',
            'Center': 'P1VC{0}\n',
            'Surround': 'P1VR{0}\n',
            'Back': 'P1VB{0}\n'
        }

        ValueConstraints = {
            'Min': -10,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeMainZoneSectionsCmdString = SectionStates[qualifier['Section']].format(value)
            self.__SetHelper('VolumeMainZoneSections', VolumeMainZoneSectionsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolumeMainZoneSections')

    def UpdateVolumeMainZoneSections(self, value, qualifier):

        SectionStates = {
            'Front': 'P1VF?\n',
            'Center': 'P1VC?\n',
            'Surround': 'P1VR?\n',
            'Back': 'P1VB?\n'
        }
        VolumeMainZoneSectionsCmdString = SectionStates[qualifier['Section']]
        self.__UpdateHelper('VolumeMainZoneSections', VolumeMainZoneSectionsCmdString, value, qualifier)

    def __MatchVolumeMainZoneSections(self, match, tag):

        SectionStates = {
            'F': 'Front',
            'C': 'Center',
            'R': 'Surround',
            'B': 'Back'
        }

        qualifier = {'Section': SectionStates[match.group(1).decode()]}
        value = int(match.group(3).decode())
        if(match.group(2).decode() == '-'):
            value = -value

        if -10 <= value <= 10:
            self.WriteStatus('VolumeMainZoneSections', value, qualifier)
        else:
            print('Invalid/unexpected response')

    def SetVolumeMainZone(self, value, qualifier):

        VolumeConstraints = {
            'Min': -95.5,
            'Max': 31.5
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'P1VM{0}\n'.format(value)
            self.__SetHelper('VolumeMainZone', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolumeMainZone')

    def UpdateVolumeMainZone(self, value, qualifier):

        VolumeZone1CmdString = 'P1?\n'
        self.__UpdateHelper('VolumeMainZone', VolumeZone1CmdString, value, qualifier)

    def SetVolumeZone2and3(self, value, qualifier):

        VolumeConstraints = {
            'Min': -70,
            'Max': 10
        }
        ZoneNum = self.ZoneNames[qualifier['Zone']]
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'P{0}V{1}\n'.format(ZoneNum, value)
            self.__SetHelper('VolumeZone2and3', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolumeZone2and3')

    def UpdateVolumeZone2and3(self, value, qualifier):

        if qualifier['Zone'] in ['Zone 2', 'Zone 3']:
            VolumeZone23CmdString = 'P{0}?\n'.format(self.ZoneNames[qualifier['Zone']])
            self.__UpdateHelper('VolumeZone2and3', VolumeZone23CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateVolumeZone2and3')

    def __MatchZoneStatus(self, match, tag):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        InputStateValues = {
            '0': 'CD',
            '1': '2-Ch BAL',
            '2': '6-Ch S/E',
            '3': 'Tape',
            '4': 'FM/AM',
            '5': 'DVD1',
            'd': 'DVD2',
            'e': 'DVD3',
            'f': 'DVD4',
            '6': 'TV1',
            'g': 'TV2',
            'h': 'TV3',
            'i': 'TV4',
            '8': 'VCR',
            '7': 'SAT1',
            'j': 'SAT2',
            '9': 'Aux',
            'c': 'Main'
        }

        Zone = int(match.group(1).decode())

        input_ = InputStateValues[match.group(2).decode()]

        volume = float(match.group(4).decode() + '.' + match.group(5).decode())
        if match.group(3).decode() == '-':
            volume = -volume

        mute = MuteState[match.group(6).decode()]

        if Zone == 1:

            self.WriteStatus('Input', input_, {'Zone': 'Main'})
            self.WriteStatus('AudioMute', mute, {'Zone': 'Main'})
            self.WriteStatus('VolumeMainZone', volume, None)

        elif Zone == 2:

            self.WriteStatus('Input', input_, {'Zone': 'Zone 2'})
            self.WriteStatus('AudioMute', mute, {'Zone': 'Zone 2'})
            self.WriteStatus('VolumeZone2and3', volume, {'Zone': 'Zone 2'})

        elif Zone == 3:

            self.WriteStatus('Input', input_, {'Zone': 'Zone 3'})
            self.WriteStatus('AudioMute', mute, {'Zone': 'Zone 3'})
            self.WriteStatus('VolumeZone2and3', volume, {'Zone': 'Zone 3'})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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
