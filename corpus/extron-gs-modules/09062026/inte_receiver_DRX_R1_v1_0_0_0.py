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

            'Zone3Input': {'Status': {}},
            'Zone3Mute': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3Preset': {'Status': {}},
            'Zone3Volume': {'Status': {}},

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

            self.AddMatchString(re.compile(b'!1SL3([0-9][0-9A-F])\x1A\r?\n?'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'!1MT3(00|01)\x1A\r?\n?'), self.__MatchZone3Mute, None)
            self.AddMatchString(re.compile(b'!1PW3(00|01)\x1A\r?\n?'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'!1PR3([0-2][0-9A-F])\x1A\r?\n?'), self.__MatchZone3Preset, None)
            self.AddMatchString(re.compile(b'!1VL3([0-9A-C][0-9A-F])\x1A\r?\n?'), self.__MatchZone3Volume, None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '!1PWR01\r',
            'Off': '!1PWR00\r'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', '!1PWRQSTN\r', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '!1AMT01\r',
            'Off': '!1AMT00\r'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '!1AMTQSTN\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '!1MVL{0:02X}\r'.format(int(value * 2))
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '!1MVLQSTN\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode(), 16) / 2, None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': 'MENU',
            'Up': 'UP',
            'Down': 'DOWN',
            'Right': 'RIGHT',
            'Left': 'LEFT',
            'Enter': 'ENTER',
            'Exit': 'EXIT',
        }

        CmdString = '!1OSD{0}\r'.format(States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetMemory(self, value, qualifier):

        States = {
            'Store': 'STR',
            'Recall': 'RCL',
            'Lock': 'LOCK',
            'Unlock': 'UNLK'
        }

        CmdString = '!1MEM{0}\r'.format(States[value])
        self.__SetHelper('Memory', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {

            'CBL/SAT': '01',
            'GAME/TV': '02',
            'AUX': '03',
            'PC': '05',
            'Extra 1': '07',
            'Extra 2': '08',
            'Extra 3': '09',

            'BD/DVD': '10',
            'STRM BOX': '11',
            'TV': '12',

            'Phono': '22',
            'CD': '23',
            'FM': '24',
            'AM': '25',
            'Tuner': '26',
            'Front USB': '29',
            'Network': '2B',
            'USB (Toggle)': '2C'
        }

        CmdString = '!1SLI{0}\r'.format(States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '!1SLIQSTN\r', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {

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

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetAudioMode(self, value, qualifier):

        States = {
            'Analog': '02',
            'HDMI': '04',
            'Coax/Opt': '05',
            'ARC': '07',
        }

        CmdString = '!1SLA{0}\r'.format(States[value])
        self.__SetHelper('AudioMode', CmdString, value, qualifier)

    def UpdateAudioMode(self, value, qualifier):
        self.__UpdateHelper('AudioMode', '!1SLAQSTN\r', value, qualifier)

    def __MatchAudioMode(self, match, tag):

        States = {
            '02': 'Analog',
            '04': 'HDMI',
            '05': 'Coax/Opt',
            '07': 'ARC'
        }

        self.WriteStatus('AudioMode', States[match.group(1).decode()], None)

    def SetListeningMode(self, value, qualifier):

        States = {

            'Stereo': '00',
            'Direct': '01',
            'Surround': '02',
            'Film': '03',
            'THX': '04',
            'Action': '05',
            'Musical': '06',
            'Orchestra': '08',
            'Unplugged': '09',
            'Studio Mix': '0A',
            'TV Logic': '0B',
            'All CH Stereo': '0C',
            'Theater Dimensional': '0D',
            'Enhanced': '0E',
            'Mono': '0F',

            'Full Mono': '13',
            'Whole House Mode': '1F',

            'Straight Decode': '40',
            'THX Cinema': '42',
            'THX Music': '44',
            'THX Games': '45',

            'THX Cinema2': '50',
            'THX Music2': '51',
            'THX Games Mode': '52',

            'PLII/PLIIx Movie': '80',
            'Neo:6 Cinema': '82',
            'PLII/PLIIx THX Cinema': '84',
            'Neo:6/Neo:X THX Cinema': '85',
            'PLII/PLIIx THX Games': '89',
            'Neo:6/Neo:X THX Games': '8A',
            'PLII/PLIIx THX Music': '8B',
            'Neo:6/Neo:X THX Music': '8C',
        }

        CmdString = '!1LMD{0}\r'.format(States[value])
        self.__SetHelper('ListeningMode', CmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):
        self.__UpdateHelper('ListeningMode', '!1LMDQSTN\r', value, qualifier)

    def __MatchListeningMode(self, match, tag):

        States = {

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
            '1F': 'Whole House Mode',

            '40': 'Straight Decode',
            '42': 'THX Cinema',
            '44': 'THX Music',
            '45': 'THX Games',

            '50': 'THX Cinema2',
            '51': 'THX Music2',
            '52': 'THX Games Mode',

            '80': 'PLII/PLIIx Movie',
            '82': 'Neo:6 Cinema',
            '84': 'PLII/PLIIx THX Cinema',
            '85': 'Neo:6/Neo:X THX Cinema',
            '89': 'PLII/PLIIx THX Games',
            '8A': 'Neo:6/Neo:X THX Games',
            '8B': 'PLII/PLIIx THX Music',
            '8C': 'Neo:6/Neo:X THX Music',
        }

        self.WriteStatus('ListeningMode', States[match.group(1).decode()], None)

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

    def SetZone2Power(self, value, qualifier):

        States = {
            'On': '!1ZPW01\r',
            'Off': '!1ZPW00\r'
        }

        self.__SetHelper('Zone2Power', States[value], value, qualifier)

    def UpdateZone2Power(self, value, qualifier):
        self.__UpdateHelper('Zone2Power', '!1ZPWQSTN\r', value, qualifier)

    def __MatchZone2Power(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Zone2Power', States[match.group(1).decode()], None)

    def SetZone2Mute(self, value, qualifier):

        States = {
            'On': '!1ZMT01\r',
            'Off': '!1ZMT00\r'
        }

        self.__SetHelper('Zone2Mute', States[value], value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):
        self.__UpdateHelper('Zone2Mute', '!1ZMTQSTN\r', value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Zone2Mute', States[match.group(1).decode()], None)

    def SetZone2Volume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '!1ZVL{0:02X}\r'.format(int(value * 2))
            self.__SetHelper('Zone2Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):
        self.__UpdateHelper('Zone2Volume', '!1ZVLQSTN\r', value, qualifier)

    def __MatchZone2Volume(self, match, tag):
        self.WriteStatus('Zone2Volume', int(match.group(1).decode(), 16) / 2, None)

    def SetZone2Input(self, value, qualifier):

        States = {

            'CBL/SAT': '01',
            'GAME/TV': '02',
            'Aux': '03',
            'PC': '05',
            'Extra 1': '07',
            'Extra 2': '08',
            'Extra 3': '09',

            'DVD': '10',
            'STRM BOX': '11',
            'TV': '12',

            'Phono': '22',
            'CD': '23',
            'FM': '24',
            'AM': '25',
            'Tuner': '26',
            'Front USB': '29',
            'Network': '2B',
            'USB (Toggle)': '2C',

            'Source': '80'
        }

        CmdString = '!1SLZ{0}\r'.format(States[value])
        self.__SetHelper('Zone2Input', CmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):
        self.__UpdateHelper('Zone2Input', '!1SLZQSTN\r', value, qualifier)

    def __MatchZone2Input(self, match, tag):

        States = {

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

        self.WriteStatus('Zone2Input', States[match.group(1).decode()], None)

    def SetZone2Preset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            CmdString = '!1PRZ{0:02X}\r'.format(int(value))
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Preset')

    def UpdateZone2Preset(self, value, qualifier):
        self.__UpdateHelper('Zone2Preset', '!1PRZQSTN\r', value, qualifier)

    def __MatchZone2Preset(self, match, tag):
        self.WriteStatus('Zone2Preset', str(int(match.group(1).decode(), 16)), None)

    def SetZone3Power(self, value, qualifier):

        States = {
            'On': '!1PW301\r',
            'Off': '!1PW300\r'
        }

        self.__SetHelper('Zone3Power', States[value], value, qualifier)

    def UpdateZone3Power(self, value, qualifier):
        self.__UpdateHelper('Zone3Power', '!1PW3QSTN\r', value, qualifier)

    def __MatchZone3Power(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Zone3Power', States[match.group(1).decode()], None)

    def SetZone3Mute(self, value, qualifier):

        States = {
            'On': '!1MT301\r',
            'Off': '!1MT300\r'
        }

        self.__SetHelper('Zone3Mute', States[value], value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):
        self.__UpdateHelper('Zone3Mute', '!1MT3QSTN\r', value, qualifier)

    def __MatchZone3Mute(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Zone3Mute', States[match.group(1).decode()], None)

    def SetZone3Volume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '!1VL3{0:02X}\r'.format(int(value * 2))
            self.__SetHelper('Zone3Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):
        self.__UpdateHelper('Zone3Volume', '!1VL3QSTN\r', value, qualifier)

    def __MatchZone3Volume(self, match, tag):
        self.WriteStatus('Zone3Volume', int(match.group(1).decode(), 16) / 2, None)

    def SetZone3Input(self, value, qualifier):

        States = {

            'CBL/SAT': '01',
            'GAME/TV': '02',
            'PC': '05',
            'Extra 1': '07',
            'Extra 2': '08',
            'Extra 3': '09',

            'DVD': '10',
            'STRM BOX': '11',
            'TV': '12',

            'Phono': '22',
            'CD': '23',
            'FM': '24',
            'AM': '25',
            'Tuner': '26',
            'Front USB': '29',
            'Network': '2B',
            'USB (Toggle)': '2C',

            'Source': '80'
        }

        CmdString = '!1SL3{0}\r'.format(States[value])
        self.__SetHelper('Zone3Input', CmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):
        self.__UpdateHelper('Zone3Input', '!1SL3QSTN\r', value, qualifier)

    def __MatchZone3Input(self, match, tag):

        States = {

            '01': 'CBL/SAT',
            '02': 'GAME/TV',
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

        self.WriteStatus('Zone3Input', States[match.group(1).decode()], None)

    def SetZone3Preset(self, value, qualifier):

        if 1 <= int(value) <= 40:
            CmdString = '!1PR3{0:02X}\r'.format(int(value))
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone3Preset')

    def UpdateZone3Preset(self, value, qualifier):
        self.__UpdateHelper('Zone3Preset', '!1PR3QSTN\r', value, qualifier)

    def __MatchZone3Preset(self, match, tag):
        self.WriteStatus('Zone3Preset', str(int(match.group(1).decode(), 16)), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.ConnectionType == 'Tcp':
            commandstring = 'ISCP\x00\x00\x00\x10\x00\x00\x00' + pack('>B', len(commandstring)).decode(encoding='iso-8859-1') + '\x01\x00\x00\x00' + commandstring

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
            if self.ConnectionType == 'Tcp':
                commandstring = 'ISCP\x00\x00\x00\x10\x00\x00\x00' + pack('>B', len(commandstring)).decode(encoding='iso-8859-1') + '\x01\x00\x00\x00' + commandstring

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

    
