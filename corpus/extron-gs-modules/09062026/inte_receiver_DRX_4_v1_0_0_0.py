from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
            'AudioMode': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'ListeningMode': {'Status': {}},
            'Memory': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'PresetMemory': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Preset': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!1SLA(0[2457])\x1A\r?\n?'), self.__MatchAudioMode, None)
            self.AddMatchString(re.compile(b'!1AMT(00|01)\x1A\r?\n?'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'!1SLI([0-9][0-9A-F])\x1A\r?\n?'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'!1LMD([0-9][0-9A-F])\x1A\r?\n?'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'!1PWR(00|01)\x1A\r?\n?'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'!1PRS([0-2][0-9A-F])\x1A\r?\n?'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'!1MVL([0-9A-C][0-9A-F])\x1A\r?\n?'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'!1SLZ([0-9][0-9A-F])\x1A\r?\n?'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'!1ZMT(00|01)\x1A\r?\n?'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'!1ZPW(00|01)\x1A\r?\n?'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'!1PRZ([0-2][0-9A-F])\x1A\r?\n?'), self.__MatchZone2Preset, None)
            self.AddMatchString(re.compile(b'!1ZVL([0-9A-C][0-9A-F])\x1A\r?\n?'), self.__MatchZone2Volume, None)

    def TCPCmdString(self, commandstring):
        Cmdstring = 'ISCP\x00\x00\x00\x10\x00\x00\x00' + pack('>B', len(commandstring)).decode(encoding='iso-8859-1') + '\x01\x00\x00\x00' + commandstring
        return Cmdstring

    def SetAudioMode(self, value, qualifier):

        ValueStateValues = {
            'HDMI': '!1SLA04\r',
            'Coax/Opt': '!1SLA05\r',
            'ARC': '!1SLA07\r',
            'Analog': '!1SLA02\r'
        }
        if self.ConnectionType == 'Tcp':
            AudioModeCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            AudioModeCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMode', AudioModeCmdString, value, qualifier)

    def UpdateAudioMode(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            AudioModeCmdString = self.TCPCmdString('!1SLAQSTN\r')
        else:
            AudioModeCmdString = '!1SLAQSTN\r'
        self.__UpdateHelper('AudioMode', AudioModeCmdString, value, qualifier)

    def __MatchAudioMode(self, match, tag):

        ValueStateValues = {
            '04': 'HDMI',
            '05': 'Coax/Opt',
            '07': 'ARC',
            '02': 'Analog'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMode', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '!1AMT01\r',
            'Off': '!1AMT00\r'
        }
        if self.ConnectionType == 'Tcp':
            AudioMuteCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            AudioMuteCmdString = self.TCPCmdString('!1AMTQSTN\r')
        else:
            AudioMuteCmdString = '!1AMTQSTN\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CBL/SAT': '!1SLI01\r',
            'GAME/TV': '!1SLI02\r',
            'AUX': '!1SLI03\r',
            'PC': '!1SLI05\r',
            'Extra 1': '!1SLI07\r',
            'Extra 2': '!1SLI08\r',
            'Extra 3': '!1SLI09\r',
            'BD/DVD': '!1SLI10\r',
            'STRM BOX': '!1SLI11\r',
            'TV': '!1SLI12\r',
            'Phono': '!1SLI22\r',
            'CD': '!1SLI23\r',
            'FM': '!1SLI24\r',
            'AM': '!1SLI25\r',
            'Tuner': '!1SLI26\r',
            'Front USB': '!1SLI29\r',
            'Network': '!1SLI2B\r',
            'USB (Toggle)': '!1SLI2C\r'

        }

        if self.ConnectionType == 'Tcp':
            InputCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            InputCmdString = self.TCPCmdString('!1SLIQSTN\r')
        else:
            InputCmdString = '!1SLIQSTN\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '01': 'CBL/SAT',
            '02': 'GAME/TV',
            '03': 'AUX',
            '05': 'PC',
            '07': 'Extra 1',
            '08': 'Extra 2',
            '09': 'Extra 3',
            '10': 'BD/DVD',
            '11': 'STRM BOX',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'Front USB',
            '2B': 'Network',
            '2C': 'USB (Toggle)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ValueStateValues = {
            'Stereo': '!1LMD00\r',
            'Direct': '!1LMD01\r',
            'Surround': '!1LMD02\r',
            'Film': '!1LMD03\r',
            'THX': '!1LMD04\r',
            'Action': '!1LMD05\r',
            'Musical': '!1LMD06\r',
            'Orchestra': '!1LMD08\r',
            'Unplugged': '!1LMD09\r',
            'Studio Mix': '!1LMD0A\r',
            'TV Logic': '!1LMD0B\r',
            'All CH Stereo': '!1LMD0C\r',
            'Theater Dimensional': '!1LMD0D\r',
            'Enhanced': '!1LMD0E\r',
            'Mono': '!1LMD0F\r',
            'Full Mono': '!1LMD13\r',
            'Straight Decode': '!1LMD40\r',
            'THX Cinema': '!1LMD42\r',
            'THX Surround EX': '!1LMD43\r',
            'THX Music': '!1LMD44\r',
            'THX Games': '!1LMD45\r',
            'THX Cinema2': '!1LMD50\r',
            'THX Music2': '!1LMD51\r',
            'THX Games Mode': '!1LMD52\r',
            'PLII/PLIIx Movie': '!1LMD80\r',
            'Neo:6 Cinema': '!1LMD82\r',
            'Neo:6 Music': '!1LMD83\r',
            'PLII/PLIIx THX Cinema': '!1LMD84\r',
            'Neo:6/Neo:X THX Cinema': '!1LMD85\r',
            'PLII/PLIIx THX Games': '!1LMD89\r',
            'Neo:6/Neo:X THX Games': '!1LMD8A\r',
            'PLII/PLIIx THX Music': '!1LMD8B\r',
            'Neo:6/Neo:X THX Music': '!1LMD8C\r',

        }

        if self.ConnectionType == 'Tcp':
            ListeningModeCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            ListeningModeCmdString = ValueStateValues[value]
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            ListeningModeCmdString = self.TCPCmdString('!1LMDQSTN\r')
        else:
            ListeningModeCmdString = '!1LMDQSTN\r'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        ValueStateValues = {
            '00': 'Stereo',
            '01': 'Direct',
            '02': 'Surround',
            '03': 'Film',
            '04': 'THX',
            '05': 'Action',
            '06': 'Musical',
            '08': 'Orchestra',
            '09': 'Unplugged',
            '0A': 'Studio Mix',
            '0B': 'TV Logic',
            '0C': 'All CH Stereo',
            '0D': 'Theater Dimensional',
            '0E': 'Enhanced',
            '0F': 'Mono',
            '13': 'Full Mono',
            '40': 'Straight Decode',
            '42': 'THX Cinema',
            '43': 'THX Surround EX',
            '44': 'THX Music',
            '45': 'THX Games',
            '50': 'THX Cinema2',
            '51': 'THX Music2',
            '52': 'THX Games Mode',
            '80': 'PLII/PLIIx Movie',
            '82': 'Neo:6 Cinema',
            '83': 'Neo:6 Music',
            '84': 'PLII/PLIIx THX Cinema',
            '85': 'Neo:6/Neo:X THX Cinema',
            '89': 'PLII/PLIIx THX Games',
            '8A': 'Neo:6/Neo:X THX Games',
            '8B': 'PLII/PLIIx THX Music',
            '8C': 'Neo:6/Neo:X THX Music',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMemory(self, value, qualifier):

        ValueStateValues = {
            'Store': '!1MEMSTR\r',
            'Recall': '!1MEMRCL\r',
            'Lock': '!1MEMLOCK\r',
            'Unlock': '!1MEMUNLK\r'
        }

        if self.ConnectionType == 'Tcp':
            MemoryCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            MemoryCmdString = ValueStateValues[value]
        self.__SetHelper('Memory', MemoryCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '!1OSDMENU\r',
            'Up': '!1OSDUP\r',
            'Down': '!1OSDDOWN\r',
            'Right': '!1OSDRIGHT\r',
            'Left': '!1OSDLEFT\r',
            'Enter': '!1OSDENTER\r',
            'Exit': '!1OSDEXIT\r'
        }

        if self.ConnectionType == 'Tcp':
            MenuNavigationCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '!1PWR01\r',
            'Off': '!1PWR00\r'
        }

        if self.ConnectionType == 'Tcp':
            PowerCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            PowerCmdString = self.TCPCmdString('!1PWRQSTN\r')
        else:
            PowerCmdString = '!1PWRQSTN\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            if self.ConnectionType == 'Tcp':
                PresetCmdString = self.TCPCmdString('!1PRS{0:02X}\r'.format(int(value)))
            else:
                PresetCmdString = '!1PRS{0:02X}\r'.format(int(value))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            PresetCmdString = self.TCPCmdString('!1PRSQSTN\r')
        else:
            PresetCmdString = '!1PRSQSTN\r'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        value = str(int(match.group(1).decode(), 16))
        self.WriteStatus('Preset', value, None)

    def SetPresetMemory(self, value, qualifier):

        if 1 <= int(value) <= 40:
            if self.ConnectionType == 'Tcp':
                PresetMemoryCmdString = self.TCPCmdString('!1PRM{0:02X}\r'.format(int(value)))
            else:
                PresetMemoryCmdString = '!1PRM{0:02X}\r'.format(int(value))
            self.__SetHelper('PresetMemory', PresetMemoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetMemory')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            if self.ConnectionType == 'Tcp':
                VolumeCmdString = self.TCPCmdString('!1MVL{0:02X}\r'.format(int(value * 2)))
            else:
                VolumeCmdString = '!1MVL{0:02X}\r'.format(int(value * 2))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            VolumeCmdString = self.TCPCmdString('!1MVLQSTN\r')
        else:
            VolumeCmdString = '!1MVLQSTN\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16) / 2
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'CBL/SAT': '!1SLZ01\r',
            'GAME/TV': '!1SLZ02\r',
            'Aux': '!1SLZ03\r',
            'PC': '!1SLZ05\r',
            'Extra 1': '!1SLZ07\r',
            'Extra 2': '!1SLZ08\r',
            'Extra 3': '!1SLZ09\r',
            'DVD': '!1SLZ10\r',
            'STRM BOX': '!1SLZ11\r',
            'TV': '!1SLZ12\r',
            'Phono': '!1SLZ22\r',
            'CD': '!1SLZ23\r',
            'FM': '!1SLZ24\r',
            'AM': '!1SLZ25\r',
            'Tuner': '!1SLZ26\r',
            'Front USB': '!1SLZ29\r',
            'Network': '!1SLZ2B\r',
            'USB (Toggle)': '!1SLZ2C\r',
            'Source': '!1SLZ80\r'
        }

        if self.ConnectionType == 'Tcp':
            Zone2InputCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            Zone2InputCmdString = self.TCPCmdString('!1SLZQSTN\r')
        else:
            Zone2InputCmdString = '!1SLZQSTN\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            '01': 'CBL/SAT',
            '02': 'GAME/TV',
            '03': 'Aux',
            '05': 'PC',
            '07': 'Extra 1',
            '08': 'Extra 2',
            '09': 'Extra 3',
            '10': 'DVD',
            '11': 'STRM BOX',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'Front USB',
            '2B': 'Network',
            '2C': 'USB (Toggle)',
            '80': 'Source'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):

        ValueStateValues = {
            'On': '!1ZMT01\r',
            'Off': '!1ZMT00\r'
        }

        if self.ConnectionType == 'Tcp':
            Zone2MuteCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            Zone2MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            Zone2MuteCmdString = self.TCPCmdString('!1ZMTQSTN\r')
        else:
            Zone2MuteCmdString = '!1ZMTQSTN\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': '!1ZPW01\r',
            'Off': '!1ZPW00\r'
        }

        if self.ConnectionType == 'Tcp':
            Zone2PowerCmdString = self.TCPCmdString(ValueStateValues[value])
        else:
            Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            Zone2PowerCmdString = self.TCPCmdString('!1ZPWQSTN\r')
        else:
            Zone2PowerCmdString = '!1ZPWQSTN\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Preset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            if self.ConnectionType == 'Tcp':
                Zone2PresetCmdString = self.TCPCmdString('!1PRZ{0:02X}\r'.format(int(value)))
            else:
                Zone2PresetCmdString = '!1PRZ{0:02X}\r'.format(int(value))
            self.__SetHelper('Zone2Preset', Zone2PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Preset')

    def UpdateZone2Preset(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            Zone2PresetCmdString = self.TCPCmdString('!1PRZQSTN\r')
        else:
            Zone2PresetCmdString = '!1PRZQSTN\r'
        self.__UpdateHelper('Zone2Preset', Zone2PresetCmdString, value, qualifier)

    def __MatchZone2Preset(self, match, tag):

        value = str(int(match.group(1).decode(), 16))
        self.WriteStatus('Zone2Preset', value, None)

    def SetZone2Volume(self, value, qualifier):

        if 0 <= value <= 100:
            if self.ConnectionType == 'Tcp':
                Zone2VolumeCmdString = self.TCPCmdString('!1ZVL{0:02X}\r'.format(int(value * 2)))
            else:
                Zone2VolumeCmdString = '!1ZVL{0:02X}\r'.format(int(value * 2))
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        if self.ConnectionType == 'Tcp':
            Zone2VolumeCmdString = self.TCPCmdString('!1ZVLQSTN\r')
        else:
            Zone2VolumeCmdString = '!1ZVLQSTN\r'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode(), 16) / 2
        self.WriteStatus('Zone2Volume', value, None)

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()