from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'AudioMute'			: {'Status': {}},
            'AudioSelect'		: {'Status': {}},
            'Input'				: {'Status': {}},
            'ListeningMode'		: {'Status': {}},
            'MenuNavigation'	: {'Status': {}},
            'NetworkOperation'	: {'Status': {}},
            'Power'				: {'Status': {}},
            'Preset'			: {'Status': {}},
            'Volume'			: {'Status': {}},
            'Zone2Input'		: {'Status': {}},
            'Zone2Mute'			: {'Status': {}},
            'Zone2Power'		: {'Status': {}},
            'Zone2Volume'		: {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x211AMT0(0|1)\x1A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x211SLA0(2|4|5|7)\x1A'), self.__MatchAudioSelect, None)
            self.AddMatchString(re.compile(b'\x211SLI(01|02|03|05|10|11|12|22|23|24|25|26|29|2B|2E)\x1A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x211LMD(00|01|02|03|05|06|08|09|0A|0B|0C|0D|0E|0F|11|13|40|80|82|83)\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'\x211PWR0(0|1)\x1A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x211MVL([0-6][0-9A-F])\x1A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x211SLZ(01|02|03|05|10|11|12|22|23|24|25|26|29|2B|2E|80)\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'\x211ZMT0(0|1)\x1A'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'\x211ZPW0(0|1)\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'\x211ZVL([0-6][0-9A-F])\x1A'), self.__MatchZone2Volume, None)

    def SetAudioMute(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        AudioMuteCmdString = '!1AMT{0}\r\n'.format(state)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '!1AMTQSTN\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('AudioMute', value, None)

    def SetAudioSelect(self, value, qualifier):

        state = {
            'Analog': '02',
            'HDMI': '04',
            'Coax/Opt': '05',
            'Arc': '07'
        }[value]

        AudioSelectCmdString = '!1SLA{0}\r\n'.format(state)
        self.__SetHelper('AudioSelect', AudioSelectCmdString, value, qualifier)

    def UpdateAudioSelect(self, value, qualifier):

        AudioSelectCmdString = '!1SLAQSTN\r\n'
        self.__UpdateHelper('AudioSelect', AudioSelectCmdString, value, qualifier)

    def __MatchAudioSelect(self, match, tag):

        value = {
            '2': 'Analog',
            '4': 'HDMI',
            '5': 'Coax/Opt',
            '7': 'Arc'
        }[match.group(1).decode()]

        self.WriteStatus('AudioSelect', value, None)

    def SetInput(self, value, qualifier):

        state = {
            'Cable/SAT': '01',
            'Game' 		: '02',
            'Aux' 		: '03',
            'PC' 		: '05',
            'BD/DVD' 	: '10',
            'Strm Box': '11',
            'TV' 		: '12',
            'Phono' 	: '22',
            'CD' 		: '23',
            'FM' 		: '24',
            'AM' 		: '25',
            'Tuner' 	: '26',
            'USB' 		: '29',
            'Network' 	: '2B',
            'Bluetooth': '2E'
        }[value]

        InputCmdString = '!1SLI{0}\r\n'.format(state)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!1SLIQSTN\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = {
            '01': 'Cable/SAT',
            '02': 'Game',
            '03': 'Aux',
            '05': 'PC',
            '10': 'BD/DVD',
            '11': 'Strm Box',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'USB',
            '2B': 'Network',
            '2E': 'Bluetooth'
        }[match.group(1).decode()]

        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        state = {
            'Stereo': '00',
            'Direct': '01',
            'Surround': '02',
            'Film': '03',
            'Action': '05',
            'Musical': '06',
            'Orchestra': '08',
            'Unplugged': '09',
            'Studio-Mix': '0A',
            'TV Logic': '0B',
            'All Ch Stereo': '0C',
            'Theater-Dimensional': '0D',
            'Enhanced 7/Enhance': '0E',
            'Mono': '0F',
            'Pure Audio': '11',
            'Full Mono': '13',
            'Straight Decode': '40',
            'Dolby Atmos/Dolby Surround': '80',
            'DTS:X/Neural:X': '82',
            'Neo:6 Music/Neo:X Music': '83'
        }[value]

        ListeningModeCmdString = '!1LMD{0}\r\n'.format(state)
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

        ListeningModeCmdString = '!1LMDQSTN\r\n'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        value = {
            '00': 'Stereo',
            '01': 'Direct',
            '02': 'Surround',
            '03': 'Film',
            '05': 'Action',
            '06': 'Musical',
            '08': 'Orchestra',
            '09': 'Unplugged',
            '0A': 'Studio-Mix',
            '0B': 'TV Logic',
            '0C': 'All Ch Stereo',
            '0D': 'Theater-Dimensional',
            '0E': 'Enhanced 7/Enhance',
            '0F': 'Mono',
            '11': 'Pure Audio',
            '13': 'Full Mono',
            '40': 'Straight Decode',
            '80': 'Dolby Atmos/Dolby Surround',
            '82': 'DTS:X/Neural:X',
            '83': 'Neo:6 Music/Neo:X Music'
        }[match.group(1).decode()]

        self.WriteStatus('ListeningMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        if value in ['Menu', 'Up', 'Down', 'Right', 'Left', 'Enter', 'Exit', 'Quick Setup']:
            if 'Quick' in value:
            	value = 'Quick'
            MenuNavigationCmdString = '!1OSD{0}\r\n'.format(value.upper())
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMenuNavigation')

    def SetNetworkOperation(self, value, qualifier):

        state = {
            'Play': 'PLAY',
            'Stop': 'STOP',
            'Pause': 'PAUSE',
            'Play/Pause': 'P/P',
            'Track Up': 'TRUP',
            'Track Down': 'TRDN',
            'Ch Up': 'CHUP',
            'Ch Down': 'CHDN',
            'Repeat': 'REPEAT',
            'Random': 'RANDOM',
            'Repeat/Shuffle': 'REP/SHF',
            'Display': 'DISPLAY',
            'Memory': 'MEMORY',
            'Mode': 'MODE',
            'Right': 'RIGHT',
            'Left': 'LEFT',
            'Up': 'UP',
            'Down': 'DOWN',
            'Select': 'SELECT',
            'Return': 'RETURN'
        }[value]

        NetworkOperationCmdString = '!1NTZ{0}\r\n'.format(state)
        self.__SetHelper('NetworkOperation', NetworkOperationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        PowerCmdString = '!1PWR{0}\r\n'.format(state)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '!1PWRQSTN\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 40:
            PresetCmdString = '!1PRS{0:02X}\r\n'.format(preset)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '!1MVL{0:02X}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '!1MVLQSTN\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        state = {
            'Cable/SAT': '01',
            'Game' 		: '02',
            'Aux' 		: '03',
            'PC' 		: '05',
            'BD/DVD' 	: '10',
            'Strm Box': '11',
            'TV' 		: '12',
            'Phono' 	: '22',
            'CD' 		: '23',
            'FM' 		: '24',
            'AM' 		: '25',
            'Tuner' 	: '26',
            'USB' 		: '29',
            'Network' 	: '2B',
            'Bluetooth': '2E',
            'Source' 	: '80'
        }[value]

        Zone2InputCmdString = '!1SLZ{0}\r\n'.format(state)
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZQSTN\r\n'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = {
            '01': 'Cable/SAT',
            '02': 'Game',
            '03': 'Aux',
            '05': 'PC',
            '10': 'BD/DVD',
            '11': 'Strm Box',
            '12': 'TV',
            '22': 'Phono',
            '23': 'CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'Tuner',
            '29': 'USB',
            '2B': 'Network',
            '2E': 'Bluetooth',
            '80': 'Source'
        }[match.group(1).decode()]

        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        Zone2MuteCmdString = '!1ZMT{0}\r\n'.format(state)
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = '!1ZMTQSTN\r\n'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Power(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        Zone2PowerCmdString = '!1ZPW{0}\r\n'.format(state)
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = '!1ZPWQSTN\r\n'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        if 0 <= value <= 100:
            Zone2VolumeCmdString = '!1ZVL{0:02X}\r\n'.format(value)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = '!1ZVLQSTN\r\n'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Zone2Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
