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
            'Input': {'Status': {}},
            'ListeningMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'PresetMemory': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Preset': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Mute': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3Preset': {'Status': {}},
            'Zone3Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x211SLI(00|01|02|03|05|10|22|23|26|29|2B)\x1A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x211LMD([0-9][0-9A-F])\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'\x211AMT0(0|1)\x1A'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'\x211PWR0(0|1)\x1A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x211MVL([0-6][0-9A-F])\x1A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x211SLZ(00|01|02|03|05|10|22|23|26|29|2B|80)\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'\x211ZMT0(0|1)\x1A'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'\x211ZPW0(0|1)\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'\x211PRS([0-2][0-9A-F])\x1A'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'\x211PRZ([0-2][0-9A-F])\x1A'), self.__MatchZone2Preset, None)
            self.AddMatchString(re.compile(b'\x211ZVL([0-6][0-9A-F])\x1A'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'\x211SL3(00|01|02|03|05|10|22|23|26|29|2B|80)\x1A'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'\x211MT30(0|1)\x1A'), self.__MatchZone3Mute, None)
            self.AddMatchString(re.compile(b'\x211PW30(0|1)\x1A'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'\x211PR3([0-2][0-9A-F])\x1A'), self.__MatchZone3Preset, None)
            self.AddMatchString(re.compile(b'\x211VL3([0-6][0-9A-F])\x1A'), self.__MatchZone3Volume, None)

    def SetInput(self, value, qualifier):

        state = {
            'STB/DVR': '00',
            'CBL/SAT': '01',
            'Game': '02',
            'AUX': '03',
            'PC': '05',
            'BD/DVD': '10',
            'Phono': '22',
            'TV/CD': '23',
            'Tuner': '26',
            'USB': '29',
            'Network': '2B'
        }[value]

        InputCmdString = '!1SLI{0}\r\n'.format(state)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!1SLIQSTN\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'Game',
            '03': 'AUX',
            '05': 'PC',
            '10': 'BD/DVD',
            '22': 'Phono',
            '23': 'TV/CD',
            '26': 'Tuner',
            '29': 'USB',
            '2B': 'Network'
        }[match.group(1).decode()]

        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ValueStateValues = {
            'Stereo': '00',
            'Direct': '01',
            'Surround': '02',
            'Film': '03',
            'THX': '04',
            'Action': '05',
            'Musical': '06',
            'Orchestra': '08',
            'Unplugged': '09',
            'Studio-Mix': '0A',
            'TV Logic': '0B',
            'All CH Stereo': '0C',
            'Theater-Dimensional': '0D',
            'Enhanced 7/Enhance': '0E',
            'Mono': '0F',
            'Audyssey DSX': '16',
            'Straight Decode': '40',
            'Dolby EX2': '41',
            'THX Cinema': '42',
            'THX Surround EX': '43',
            'THX Music': '44',
            'THX Games': '45',
            'US/S2 Cinema/Cinema2': '50',
            'MusicMode U2/S2 Music': '51',
            'GamesMode U2/S2 Games': '52',
            'PLII/PLIIx Movie': '80',
            'PLII/PLIIx Music': '81',
            'Neo:6 Cinema': '82',
            'Neo:6 Music': '83',
            'PLII/PLIIx THX Cinema': '84',
            'Neo:6 THX Cinema': '85',
            'PLII/PLIIx Game': '86',
            'Neural THX/Neural Surround': '88',
            'PLII/PLIIx THX Games': '89',
            'Neo6: THX Games': '8A',
            'PLII/PLIIx THX Music': '8B',
            'Neo:6 THX Music': '8C',
            'Neural THX Cinema': '8D',
            'Neural THX Music': '8E',
            'Neural THX Games': '8F',
            'PLIIz Height': '90',
            'Neural Digital Music': '93',
            'PLIIz Height + THX Cinema': '94',
            'PLIIz Height + THX Music': '95',
            'PLIIz Height + THX Games': '96',
            'PLIIz Height + THX U2/S2 Cinema': '97',
            'PLIIz Height + THX U2/S2 Music': '98',
            'PLIIz Height + THX U2/S2 Games': '99',
            'PLIIx/PLII Movie + Audyssey DSX': 'A0',
            'PLIIx/PLII Music + Audyssey DSX': 'A1',
            'PLIIx/PLII Game + Audyssey DSX': 'A2',
            'Neo:6 Cinema + Audyssey DSX': 'A3',
            'Neo:6 Music + Audyssey DSX': 'A4',
            'Full Mono': '13',
        }

        ListeningModeCmdString = '!1LMD{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

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
            '0A': 'Studio-Mix',
            '0B': 'TV Logic',
            '0C': 'All CH Stereo',
            '0D': 'Theater-Dimensional',
            '0E': 'Enhanced 7/Enhance',
            '0F': 'Mono',
            '16': 'Audyssey DSX',
            '40': 'Straight Decode',
            '41': 'Dolby EX2',
            '42': 'THX Cinema',
            '43': 'THX Surround EX',
            '44': 'THX Music',
            '45': 'THX Games',
            '50': 'US/S2 Cinema/Cinema2',
            '51': 'MusicMode U2/S2 Music',
            '52': 'GamesMode U2/S2 Games',
            '80': 'PLII/PLIIx Movie',
            '81': 'PLII/PLIIx Music',
            '82': 'Neo:6 Cinema',
            '83': 'Neo:6 Music',
            '84': 'PLII/PLIIx THX Cinema',
            '85': 'Neo:6 THX Cinema',
            '86': 'PLII/PLIIx Game',
            '88': 'Neural THX/Neural Surround',
            '89': 'PLII/PLIIx THX Games',
            '8A': 'Neo6: THX Games',
            '8B': 'PLII/PLIIx THX Music',
            '8C': 'Neo:6 THX Music',
            '8D': 'Neural THX Cinema',
            '8E': 'Neural THX Music',
            '8F': 'Neural THX Games',
            '90': 'PLIIz Height',
            '93': 'Neural Digital Music',
            '94': 'PLIIz Height + THX Cinema',
            '95': 'PLIIz Height + THX Music',
            '96': 'PLIIz Height + THX Games',
            '97': 'PLIIz Height + THX U2/S2 Cinema',
            '98': 'PLIIz Height + THX U2/S2 Music',
            '99': 'PLIIz Height + THX U2/S2 Games',
            'A0': 'PLIIx/PLII Movie + Audyssey DSX',
            'A1': 'PLIIx/PLII Music + Audyssey DSX',
            'A2': 'PLIIx/PLII Game + Audyssey DSX',
            'A3': 'Neo:6 Cinema + Audyssey DSX',
            'A4': 'Neo:6 Music + Audyssey DSX',
            '13': 'Full Mono'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        if value in ['Menu', 'Up', 'Down', 'Right', 'Left', 'Enter', 'Exit']:
            MenuNavigationCmdString = '!1OSD{0}\r\n'.format(value.upper())
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        MuteCmdString = '!1AMT{0}\r\n'.format(state)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '!1AMTQSTN\r\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Mute', value, None)

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

        if 1 <= int(value) <= 40:
            CmdString = '!1PRS{0:02X}\r'.format(int(value))
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        self.__UpdateHelper('Preset', '!1PRSQSTN\r', value, qualifier)

    def __MatchPreset(self, match, tag):

        self.WriteStatus('Preset', str(int(match.group(1).decode(), 16)), None)

    def SetPresetMemory(self, value, qualifier):

        if 1 <= int(value) <= 40:
            CmdString = '!1PRM{0:02X}\r'.format(int(value))
            self.__SetHelper('PresetMemory', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetMemory')

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
            'STB/DVR': '00',
            'CBL/SAT': '01',
            'Game': '02',
            'AUX': '03',
            'PC': '05',
            'BD/DVD': '10',
            'Phono': '22',
            'TV/CD': '23',
            'Tuner': '26',
            'USB': '29',
            'Network': '2B',
            'Source': '80'
        }[value]

        Zone2InputCmdString = '!1SLZ{0}\r\n'.format(state)
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZQSTN\r\n'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'Game',
            '03': 'AUX',
            '05': 'PC',
            '10': 'BD/DVD',
            '22': 'Phono',
            '23': 'TV/CD',
            '26': 'Tuner',
            '29': 'USB',
            '2B': 'Network',
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

    def SetZone2Preset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            CmdString = '!1PRZ{0:02X}\r'.format(int(value))
            self.__SetHelper('Zone2Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Preset')

    def UpdateZone2Preset(self, value, qualifier):

        self.__UpdateHelper('Zone2Preset', '!1PRZQSTN\r', value, qualifier)

    def __MatchZone2Preset(self, match, tag):

        self.WriteStatus('Zone2Preset', str(int(match.group(1).decode(), 16)), None)

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

    def SetZone3Input(self, value, qualifier):

        state = {
            'STB/DVR': '00',
            'CBL/SAT': '01',
            'Game': '02',
            'AUX': '03',
            'PC': '05',
            'BD/DVD': '10',
            'Phono': '22',
            'TV/CD': '23',
            'Tuner': '26',
            'USB': '29',
            'Network': '2B',
            'Source': '80'
        }[value]

        Zone3InputCmdString = '!1SL3{0}\r\n'.format(state)
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = '!1SL3QSTN\r\n'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):

        value = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'Game',
            '03': 'AUX',
            '05': 'PC',
            '10': 'BD/DVD',
            '22': 'Phono',
            '23': 'TV/CD',
            '26': 'Tuner',
            '29': 'USB',
            '2B': 'Network',
            '80': 'Source'
        }[match.group(1).decode()]

        self.WriteStatus('Zone3Input', value, None)

    def SetZone3Mute(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        Zone3MuteCmdString = '!1MT3{0}\r\n'.format(state)
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = '!1MT3QSTN\r\n'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def __MatchZone3Mute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Zone3Mute', value, None)

    def SetZone3Power(self, value, qualifier):

        state = {
            'On': '01',
            'Off': '00'
        }[value]

        Zone3PowerCmdString = '!1PW3{0}\r\n'.format(state)
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = '!1PW3QSTN\r\n'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('Zone3Power', value, None)

    def SetZone3Preset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            CmdString = '!1PR3{0:02X}\r'.format(int(value))
            self.__SetHelper('Zone3Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone3Preset')

    def UpdateZone3Preset(self, value, qualifier):

        self.__UpdateHelper('Zone3Preset', '!1PR3QSTN\r', value, qualifier)

    def __MatchZone3Preset(self, match, tag):

        self.WriteStatus('Zone3Preset', str(int(match.group(1).decode(), 16)), None)

    def SetZone3Volume(self, value, qualifier):

        if 0 <= value <= 100:
            Zone3VolumeCmdString = '!1VL3{0:02X}\r\n'.format(value)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = '!1VL3QSTN\r\n'
        self.__UpdateHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Zone3Volume', value, None)

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
