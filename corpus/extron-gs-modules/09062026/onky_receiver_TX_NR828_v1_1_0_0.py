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
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'ListeningMode': {'Status': {}},
            'Memory': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'Resolution': {'Status': {}},
            'VideoPictureMode': {'Status': {}},
            'VideoWideMode': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Mute': {'Status': {}},
            'Zone3Power': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!1AMT0(0|1)\x1A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'!1SLI([0-9A-F]{2})\x1A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'!1LMD([0-9A-F]{2})\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'!1PWR0(0|1)\x1A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'!1PRS([0-9A-F]{2})\x1A'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'!1RES0([0-8])\x1A'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(b'!1VPM0([0-8])\x1A'), self.__MatchVideoPictureMode, None)
            self.AddMatchString(re.compile(b'!1VWM0([0-4])\x1A'), self.__MatchVideoWideMode, None)
            self.AddMatchString(re.compile(b'!1MVL([0-9A-F]{2})\x1A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'!1SLZ([0-9A-F]{2})\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'!1ZMT0(0|1)\x1A'), self.__MatchZone2Mute, None)
            self.AddMatchString(re.compile(b'!1ZPW0(0|1)\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'!1ZVL([0-9A-F]{2})\x1A'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'!1SL3([0-9A-F]{2})\x1A'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'!1MT30(0|1)\x1A'), self.__MatchZone3Mute, None)
            self.AddMatchString(re.compile(b'!1PW30(0|1)\x1A'), self.__MatchZone3Power, None)

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
            '1': 'On',
            '0': 'Off'
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
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '!1MVL{0:02X}\r'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '!1MVLQSTN\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode(), 16), None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': '!1OSDMENU\r',
            'Up': '!1OSDUP\r',
            'Down': '!1OSDDOWN\r',
            'Right': '!1OSDRIGHT\r',
            'Left': '!1OSDLEFT\r',
            'Enter': '!1OSDENTER\r',
            'Exit': '!1OSDEXIT\r',
            'Home': '!1OSDHOME\r'
        }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def SetMemory(self, value, qualifier):

        States = {
            'Store': '!1MEMSTR\r',
            'Recall': '!1MEMRCL\r',
            'Lock': '!1MEMLOCK\r',
            'Unlock': '!1MEMUNLK\r'
        }

        self.__SetHelper('Memory', States[value], value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'STB/DVR': '!1SLI00\r',
            'CBL/SAT': '!1SLI01\r',
            'GAME1': '!1SLI02\r',
            'AUX': '!1SLI03\r',
            'GAME2': '!1SLI04\r',
            'PC': '!1SLI05\r',

            'BD/DVD': '!1SLI10\r',

            'PHONO': '!1SLI22\r',
            'TV/CD': '!1SLI23\r',
            'FM': '!1SLI24\r',
            'AM': '!1SLI25\r',
            'TUNER': '!1SLI26\r',
            'Music Server': '!1SLI27\r',
            'Internet Radio': '!1SLI28\r',
            'USB': '!1SLI29\r',

            'NET': '!1SLI2B\r',

            'Bluetooth': '!1SLI2E\r',
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '!1SLIQSTN\r', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'GAME1',
            '03': 'AUX',
            '04': 'GAME2',
            '05': 'PC',

            '10': 'BD/DVD',

            '22': 'PHONO',
            '23': 'TV/CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'TUNER',
            '27': 'Music Server',
            '28': 'Internet Radio',
            '29': 'USB',

            '2B': 'NET',
            '2E': 'Bluetooth',
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetResolution(self, value, qualifier):

        States = {
            'Through': '!1RES00\r',
            'Auto': '!1RES01\r',
            '480p': '!1RES02\r',
            '720p': '!1RES03\r',
            '1080i': '!1RES04\r',
            '1080p': '!1RES05\r',
            '4K Upscaling': '!1RES08\r',
        }

        self.__SetHelper('Resolution', States[value], value, qualifier)

    def UpdateResolution(self, value, qualifier):
        self.__UpdateHelper('Resolution', '!1RESQSTN\r', value, qualifier)

    def __MatchResolution(self, match, tag):

        States = {
            '0': 'Through',
            '1': 'Auto',
            '2': '480p',
            '3': '720p',
            '4': '1080i',
            '5': '1080p',
            '8': '4K Upscaling'
        }

        self.WriteStatus('Resolution', States[match.group(1).decode()], None)

    def SetVideoWideMode(self, value, qualifier):

        States = {
            'Auto': '!1VWM00\r',
            '4:3': '!1VWM01\r',
            'Full': '!1VWM02\r',
            'Zoom': '!1VWM03\r',
            'Wide Zoom': '!1VWM04\r'
        }

        self.__SetHelper('VideoWideMode', States[value], value, qualifier)

    def UpdateVideoWideMode(self, value, qualifier):
        self.__UpdateHelper('VideoWideMode', '!1VWMQSTN\r', value, qualifier)

    def __MatchVideoWideMode(self, match, tag):

        States = {
            '0': 'Auto',
            '1': '4:3',
            '2': 'Full',
            '3': 'Zoom',
            '4': 'Wide Zoom'
        }

        self.WriteStatus('VideoWideMode', States[match.group(1).decode()], None)

    def SetVideoPictureMode(self, value, qualifier):

        States = {
            'Through': '!1VPM00\r',
            'Custom': '!1VPM01\r',
            'Cinema': '!1VPM02\r',
            'Game': '!1VPM03\r',
            'Direct Bypass': '!1VPM08\r'
        }

        self.__SetHelper('VideoPictureMode', States[value], value, qualifier)

    def UpdateVideoPictureMode(self, value, qualifier):
        self.__UpdateHelper('VideoPictureMode', '!1VPMQSTN\r', value, qualifier)

    def __MatchVideoPictureMode(self, match, tag):

        States = {
            '0': 'Through',
            '1': 'Custom',
            '2': 'Cinema',
            '3': 'Game',
            '8': 'Direct Bypass'
        }

        self.WriteStatus('VideoPictureMode', States[match.group(1).decode()], None)

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
            'Studio-Mix': '0A',
            'TV Logic': '0B',
            'All Ch Stereo': '0C',
            'Theater-Dimensional': '0D',
            'Enhanced': '0E',
            'Mono': '0F',

            'Pure Audio': '11',
            'Full Mono': '13',
            'Audyssey DSX': '16',
            'Whole House Mode': '1F',

            'Straight Decode': '40',
            'Dolby EX': '41',
            'THX Cinema': '42',
            'THX Surround EX': '43',
            'THX Music': '44',
            'THX Games': '45',

            'U2/S2': '50',
            'Music Mode': '51',
            'Games Mode': '52',

            'PLII/PLIIx Movie': '80',
            'PLII/PLIIx Music': '81',
            'Neo:6 Cinema': '82',
            'Neo:6 Music': '83',
            'PLII/PLIIx THX Cinema': '84',
            'Neo:6 THX Cinema': '85',
            'PLII/PLIIx Game': '86',
            'PLII/PLIIx THX Game': '89',
            'Neo:6 THX Games': '8A',
            'PLII/PLIIx THX Music': '8B',
            'Neo:6 THX Music': '8C',

            'PLIIz Height': '90',
            'PLIIz Height + THX Cinema': '94',
            'PLIIz Height + THX Music': '95',
            'PLIIz Height + THX Games': '96',

            'PLIIx/PLII Movie + Audyssey DSX': 'A0',
            'PLIIx/PLII Music + Audyssey DSX': 'A1',
            'PLIIx/PLII Game + Audyssey DSX': 'A2',
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
            '0A': 'Studio-Mix',
            '0B': 'TV Logic',
            '0C': 'All Ch Stereo',
            '0D': 'Theater-Dimensional',
            '0E': 'Enhanced',
            '0F': 'Mono',

            '11': 'Pure Audio',
            '13': 'Full Mono',
            '16': 'Audyssey DSX',
            '1F': 'Whole House Mode',

            '40': 'Straight Decode',
            '41': 'Dolby EX',
            '42': 'THX Cinema',
            '43': 'THX Surround EX',
            '44': 'THX Music',
            '45': 'THX Games',

            '50': 'U2/S2',
            '51': 'Music Mode',
            '52': 'Games Mode',

            '80': 'PLII/PLIIx Movie',
            '81': 'PLII/PLIIx Music',
            '82': 'Neo:6 Cinema',
            '83': 'Neo:6 Music',
            '84': 'PLII/PLIIx THX Cinema',
            '85': 'Neo:6 THX Cinema',
            '86': 'PLII/PLIIx Game',
            '89': 'PLII/PLIIx THX Game',
            '8A': 'Neo:6 THX Games',
            '8B': 'PLII/PLIIx THX Music',
            '8C': 'Neo:6 THX Music',

            '90': 'PLIIz Height',
            '94': 'PLIIz Height + THX Cinema',
            '95': 'PLIIz Height + THX Music',
            '96': 'PLIIz Height + THX Games',

            'A0': 'PLIIx/PLII Movie + Audyssey DSX',
            'A1': 'PLIIx/PLII Music + Audyssey DSX',
            'A2': 'PLIIx/PLII Game + Audyssey DSX',
        }

        self.WriteStatus('ListeningMode', States[match.group(1).decode()], None)

    def SetPreset(self, value, qualifier):
        Preset = int(value)
        if 1 <= Preset <= 40:
            CmdString = '!1PRS{0}\r'.format(hex(Preset)[2:].zfill(2).upper())
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):
        self.__UpdateHelper('Preset', '!1PRSQSTN\r', value, qualifier)

    def __MatchPreset(self, match, tag):
        value = str(int(match.group(1).decode(), 16))
        self.WriteStatus('Preset', value, None)

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
            '1': 'On',
            '0': 'Off'
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
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Zone2Mute', States[match.group(1).decode()], None)

    def SetZone2Input(self, value, qualifier):

        States = {
            'STB/DVR': '00',
            'CBL/SAT': '01',
            'GAME1': '02',
            'AUX': '03',
            'PC': '05',

            'BD/DVD': '10',

            'PHONO': '22',
            'TV/CD': '23',
            'FM': '24',
            'AM': '25',
            'TUNER': '26',
            'Music Server': '27',
            'Internet Radio': '28',
            'USB': '29',
            'NET': '2B',
        }

        CmdString = '!1SLZ{0}\r'.format(States[value])
        self.__SetHelper('Zone2Input', CmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):
        self.__UpdateHelper('Zone2Input', '!1SLZQSTN\r', value, qualifier)

    def __MatchZone2Input(self, match, tag):

        States = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'GAME1',
            '03': 'AUX',
            '05': 'PC',

            '10': 'BD/DVD',

            '22': 'PHONO',
            '23': 'TV/CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'TUNER',
            '27': 'Music Server',
            '28': 'Internet Radio',
            '29': 'USB',
            '2B': 'NET'
        }

        self.WriteStatus('Zone2Input', States[match.group(1).decode()], None)

    def SetZone2Volume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '!1ZVL{0:02X}\r'.format(value)
            self.__SetHelper('Zone2Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):
        self.__UpdateHelper('Zone2Volume', '!1ZVLQSTN\r', value, qualifier)

    def __MatchZone2Volume(self, match, tag):
        self.WriteStatus('Zone2Volume', int(match.group(1).decode(), 16), None)

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
            '1': 'On',
            '0': 'Off'
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
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Zone3Mute', States[match.group(1).decode()], None)

    def SetZone3Input(self, value, qualifier):

        States = {
            'STB/DVR': '00',
            'CBL/SAT': '01',
            'GAME1': '02',
            'AUX': '03',
            'PC': '05',

            'BD/DVD': '10',

            'PHONO': '22',
            'TV/CD': '23',
            'FM': '24',
            'AM': '25',
            'TUNER': '26',
            'Music Server': '27',
            'Internet Radio': '28',
            'USB': '29',
            'NET': '2B'
        }

        CmdString = '!1SL3{0}\r'.format(States[value])
        self.__SetHelper('Zone3Input', CmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):
        self.__UpdateHelper('Zone3Input', '!1SL3QSTN\r', value, qualifier)

    def __MatchZone3Input(self, match, tag):

        States = {
            '00': 'STB/DVR',
            '01': 'CBL/SAT',
            '02': 'GAME1',
            '03': 'AUX',
            '05': 'PC',

            '10': 'BD/DVD',

            '22': 'PHONO',
            '23': 'TV/CD',
            '24': 'FM',
            '25': 'AM',
            '26': 'TUNER',
            '27': 'Music Server',
            '28': 'Internet Radio',
            '29': 'USB',
            '2B': 'NET'
        }

        self.WriteStatus('Zone3Input', States[match.group(1).decode()], None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.ConnectionType == 'Ethernet':
            commandstring = 'ISCP\x00\x00\x00\x10\x00\x00\x00\x08\x01\x00\x00\x00' + commandstring

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

            if self.ConnectionType == 'Ethernet':
                commandstring = 'ISCP\x00\x00\x00\x10\x00\x00\x00\x08\x01\x00\x00\x00' + commandstring
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
