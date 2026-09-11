from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
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
        self.Models = {
            'TX-NR708': self.onky_27_296_NR,
            'TX-NR808': self.onky_27_296_NR,
            'TX-RZ800': self.onky_27_296_RZ,
            'TX-RZ900': self.onky_27_296_RZ,
            'TX-RZ810': self.onky_27_296_RZ810,
            }

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
            'Zone3Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'!1AMT(00|01)\x1A'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'!1SLI([0-E]{1,2})\x1A'), self.__MatchInput, None)
            self.AddMatchString(compile(b'!1LMD([0-F]{1,2})\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(compile(b'!1RES([0-7]{1,2})\x1A'), self.__MatchResolution, None)
            self.AddMatchString(compile(b'!1PRS([0-F]{1,2})\x1A'), self.__MatchPreset, None)
            self.AddMatchString(compile(b'!1PWR(00|01)\x1A'), self.__MatchPower, None)
            self.AddMatchString(compile(b'!1VPM([0-6]{1,2})\x1A'), self.__MatchVideoPictureMode, None)
            self.AddMatchString(compile(b'!1VWM([0-5]{1,2})\x1A'), self.__MatchVideoWideMode, None)
            self.AddMatchString(compile(b'!1MVL([0-F]{1,2})\x1A'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'!1SLZ([0-E]{1,2})\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(compile(b'!1ZMT(00|01)\x1A'), self.__MatchZone2Mute, None)
            self.AddMatchString(compile(b'!1ZPW(00|01)\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(compile(b'!1ZVL([0-F]{1,2})\x1A'), self.__MatchZone2Volume, None)
            self.AddMatchString(compile(b'!1SL3([0-E]{1,2})\x1A'), self.__MatchZone3Input, None)
            self.AddMatchString(compile(b'!1MT3(00|01)\x1A'), self.__MatchZone3Mute, None)
            self.AddMatchString(compile(b'!1PW3(00|01)\x1A'), self.__MatchZone3Power, None)
            self.AddMatchString(compile(b'!1VL3([0-F]{1,2})\x1A'), self.__MatchZone3Volume, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'Off': '!1AMT00\r',
            'On': '!1AMT01\r'
            }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        AudioMuteCmdString = '!1AMTQSTN\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!1SLIQSTN\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ListeningModeStateValues = {
            'STEREO': '!1LMD00\r',
            'DIRECT': '!1LMD01\r',
            'SURROUND': '!1LMD02\r',
            'FILM': '!1LMD03\r',
            'THX': '!1LMD04\r',
            'ACTION': '!1LMD05\r',
            'MUSICAL': '!1LMD06\r',
            'ORCHESTRA': '!1LMD08\r',
            'UNPLUGGED': '!1LMD09\r',
            'STUDIO-MIX': '!1LMD0A\r',
            'TV LOGIC': '!1LMD0B\r',
            'ALL CH STEREO': '!1LMD0C\r',
            'THEARTER-DIMENSIONAL': '!1LMD0D\r',
            'ENHANCED 7': '!1LMD0E\r',
            'MONO': '!1LMD0F\r',
            'PURE AUDIO': '!1LMD11\r',
            'FULL MONO': '!1LMD13\r',
            'Audyssey DSX': '!1LMD16\r',
            'Straight Decode': '!1LMD40\r',
            'Dolby EX': '!1LMD41\r',
            'THX Cinema': '!1LMD42\r',
            'THX Surround EX': '!1LMD43\r',
            'THX Music': '!1LMD44\r',
            'THX Games': '!1LMD45\r',
            'U2/S2': '!1LMD50\r',
            'Music Mode': '!1LMD51\r',
            'Games Mode': '!1LMD52\r',
            'PLII/PLIIx Movie': '!1LMD80\r',
            'PLII/PLIIx Music': '!1LMD81\r',
            'Neo:6 Cinema': '!1LMD82\r',
            'Neo:6 Music': '!1LMD83\r',
            'PLII/PLIIx THX Cinema': '!1LMD84\r',
            'Neo:6 THX Cinema': '!1LMD85\r',
            'PLII/PLIIx Game': '!1LMD86\r',
            'PLII/PLIIx THX Game': '!1LMD89\r',
            'Neo:6 THX Games': '!1LMD8A\r',
            'PLII/PLIIx THX Music': '!1LMD8B\r',
            'Neo:6 THX Music': '!1LMD8C\r',
            'PLIIz Height': '!1LMD90\r',
            'PLIIz Height + THX Cinema': '!1LMD94\r',
            'PLIIz Height + THX Music': '!1LMD95\r',
            'PLIIz Height + THX Games': '!1LMD96\r',
            'PLIIx/PLII Movie + Audyssey DSX': '!1LMDA0\r',
            'PLIIx/PLII Music + Audyssey DSX': '!1LMDA1\r',
            'PLIIx/PLII Game + Audyssey DSX': '!1LMDA2\r',
            'Neo:6 Cinema + Audyssey DSX': '!1LMDA3\r',
            'Neo:6 Music + Audyssey DSX': '!1LMDA4\r'
            }

        ListeningModeCmdString = ListeningModeStateValues[value]
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def UpdateListeningMode(self, value, qualifier):

        ListeningModeCmdString = '!1LMDQSTN\r'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        ListeningModeStateNames = {
            '00': 'STEREO',
            '01': 'DIRECT',
            '02': 'SURROUND',
            '03': 'FILM',
            '04': 'THX',
            '05': 'ACTION',
            '06': 'MUSICAL',
            '08': 'ORCHESTRA',
            '09': 'UNPLUGGED',
            '0A': 'STUDIO-MIX',
            '0B': 'TV LOGIC',
            '0C': 'ALL CH STEREO',
            '0D': 'THEARTER-DIMENSIONAL',
            '0E': 'ENHANCED 7',
            '0F': 'MONO',
            '11': 'PURE AUDIO',
            '13': 'FULL MONO',
            '16': 'Audyssey DSX',
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
            'A3': 'Neo:6 Cinema + Audyssey DSX',
            'A4': 'Neo:6 Music + Audyssey DSX',
            }

        value = ListeningModeStateNames[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMemory(self, value, qualifier):

        MemoryStateValues = {
            'Store': '!1MEMSTR\r',
            'Recall': '!1MEMRCL\r',
            'Lock': '!1MEMLOCK\r',
            'Unlock': '!1MEMUNLK\r'
            }

        MemoryCmdString = MemoryStateValues[value]
        self.__SetHelper('Memory', MemoryCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': '!1OSDMENU\r',
            'Up': '!1OSDUP\r',
            'Down': '!1OSDDOWN\r',
            'Right': '!1OSDRIGHT\r',
            'Left': '!1OSDLEFT\r',
            'Enter': '!1OSDENTER\r',
            'Exit': '!1OSDEXIT\r'
            }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': '!1PWR00\r',
            'On': '!1PWR01\r'
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '!1PWRQSTN\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        PresetConstraints = {
            'Min': 1,
            'Max': 40
            }

        if PresetConstraints['Min'] <= int(value) <= PresetConstraints['Max']:
            PresetCmdString = '!1PRS{0:0{1}x}\r'.format(int(value), 2)
            self.__SetHelper('Preset', PresetCmdString.upper(), value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '!1PRSQSTN\r'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        value = int(match.group(1).decode(), 16)
        value = str(value)
        self.WriteStatus('Preset', value, None)

    def SetResolution(self, value, qualifier):

        ResolutionStateValues = {
           'Through': '!1RES00',
           'Auto': '!1RES01',
           '480p': '!1RES02',
           '720p': '!1RES03',
           '1080i': '!1RES04',
           '1080p': '!1RES05'
           }

        ResolutionCmdString = ResolutionStateValues[value]
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        ResolutionCmdString = '!1RESQSTN\r'
        self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        ResolutionStateNames = {
           '00': 'Through',
           '01': 'Auto',
           '02': '480p',
           '03': '720p',
           '04': '1080i',
           '05': '1080p'
           }

        value = ResolutionStateNames[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)

    def SetVideoPictureMode(self, value, qualifier):

        VideoPictureModeStateValues = {
           'Through': '!1VPM00\r',
           'Custom': '!1VPM01\r',
           'Cinema': '!1VPM02\r',
           'Game': '!1VPM03\r'
           }

        VideoPictureModeCmdString = VideoPictureModeStateValues[value]
        self.__SetHelper('VideoPictureMode', VideoPictureModeCmdString, value, qualifier)

    def UpdateVideoPictureMode(self, value, qualifier):

        VideoPictureModeCmdString = '!1VPMQSTN\r'
        self.__UpdateHelper('VideoPictureMode', VideoPictureModeCmdString, value, qualifier)

    def __MatchVideoPictureMode(self, match, tag):

        VideoPictureModeStateNames = {
           '00': 'Through',
           '01': 'Custom',
           '02': 'Cinema',
           '03': 'Game'
           }

        value = VideoPictureModeStateNames[match.group(1).decode()]
        self.WriteStatus('VideoPictureMode', value, None)

    def SetVideoWideMode(self, value, qualifier):

        VideoWideModeStateValues = {
           'Auto': '!1VWM00\r',
           '4:3': '!1VWM01\r',
           'Full': '!1VWM02\r',
           'Zoom': '!1VWM03\r',
           'Wide Zoom': '!1VWM04\r'
           }

        VideoWideModeCmdString = VideoWideModeStateValues[value]
        self.__SetHelper('VideoWideMode', VideoWideModeCmdString, value, qualifier)

    def UpdateVideoWideMode(self, value, qualifier):

        VideoWideModeCmdString = '!1VWMQSTN\r'
        self.__UpdateHelper('VideoWideMode', VideoWideModeCmdString, value, qualifier)

    def __MatchVideoWideMode(self, match, tag):

        VideoWideModeStateNames = {
           '00': 'Auto',
           '01': '4:3',
           '02': 'Full',
           '03': 'Zoom',
           '04': 'Wide Zoom'
           }

        value = VideoWideModeStateNames[match.group(1).decode()]
        self.WriteStatus('VideoWideMode', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }

        value = int(value)
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '!1MVL{0:0{1}x}\r'.format(value, 2)
            self.__SetHelper('Volume', VolumeCmdString.upper(), value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '!1MVLQSTN\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        Zone2InputCmdString = self.Zone2InputStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZQSTN\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        value = self.Zone2InputStateNames[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):

        Zone2MuteStateValues = {
            'Off': '!1ZMT00\r',
            'On': '!1ZMT01\r'
            }

        Zone2MuteCmdString = Zone2MuteStateValues[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = '!1ZMTQSTN\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):

        Zone2MuteStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = Zone2MuteStateNames[match.group(1).decode()]
        self.WriteStatus('Zone2Mute', value, None)

    def SetZone2Power(self, value, qualifier):

        Zone2PowerStateValues = {
            'Off': '!1ZPW00\r',
            'On': '!1ZPW01\r'
            }

        Zone2PowerCmdString = Zone2PowerStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = '!1ZPWQSTN\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        Zone2PowerStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = Zone2PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        Zone2VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }

        value = int(value)
        if Zone2VolumeConstraints['Min'] <= value <= Zone2VolumeConstraints['Max']:
            Zone2VolumeCmdString = '!1ZVL{0:0{1}x}\r'.format(value, 2)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString.upper(), value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = '!1ZVLQSTN\r'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Zone2Volume', value, None)

    def SetZone3Input(self, value, qualifier):

        Zone3InputCmdString = self.Zone3InputStateValues[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        Zone3InputCmdString = '!1SL3QSTN\r'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):

        value = self.Zone3InputStateNames[match.group(1).decode()]
        self.WriteStatus('Zone3Input', value, None)

    def SetZone3Mute(self, value, qualifier):

        Zone3MuteStateValues = {
            'Off': '!1MT300\r',
            'On': '!1MT301\r'
            }

        Zone3MuteCmdString = Zone3MuteStateValues[value]
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = '!1MT3QSTN\r'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def __MatchZone3Mute(self, match, tag):

        Zone3MuteStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = Zone3MuteStateNames[match.group(1).decode()]
        self.WriteStatus('Zone3Mute', value, None)

    def SetZone3Power(self, value, qualifier):

        Zone3PowerStateValues = {
            'Off': '!1PW300\r',
            'On': '!1PW301\r'
            }

        Zone3PowerCmdString = Zone3PowerStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = '!1PW3QSTN\r'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        Zone3PowerStateNames = {
            '00': 'Off',
            '01': 'On'
            }

        value = Zone3PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Zone3Power', value, None)

    def SetZone3Volume(self, value, qualifier):

        Zone3VolumeConstraints = {
            'Min': 0,
            'Max': 100
            }

        value = int(value)
        if Zone3VolumeConstraints['Min'] <= value <= Zone3VolumeConstraints['Max']:
            Zone3VolumeCmdString = '!1VL3{0:0{1}x}\r'.format(value, 2)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString.upper(), value, qualifier)
        else:
            print('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = '!1VL3QSTN\r'
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

    def onky_27_296_NR(self):
    

        self.InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SLI00\r',
            'VIDEO 2 CBL/SAT' : '!1SLI01\r',
            'VIDEO 3 GAME/TV' : '!1SLI02\r',
            'VIDEO 4 AUX1'    : '!1SLI03\r',
            'VIDEO 6 PC'      : '!1SLI05\r',
            'DVD'             : '!1SLI10\r',
            'PHONO'           : '!1SLI22\r',
            'TV/CD'           : '!1SLI23\r',
            'FM'              : '!1SLI24\r',
            'AM'              : '!1SLI25\r',
            'TUNER'           : '!1SLI26\r',
            'MUSIC SERVER'    : '!1SLI27\r',
            'INTERNET RADIO'  : '!1SLI28\r',
            'USB'             : '!1SLI29\r',
            'UNIVERSAL PORT'  : '!1SLI40\r',
            'SIRIUS'          : '!1SLI32\r'
            }
        self.InputStateNames = {
           '00' : 'VIDEO 1 VCR/DVR',
           '01' : 'VIDEO 2 CBL/SAT',
           '02' : 'VIDEO 3 GAME/TV',
           '03' : 'VIDEO 4 AUX1',
           '05' : 'VIDEO 6 PC',
           '10' : 'DVD',
           '22' : 'PHONO',
           '23' : 'TV/CD',
           '24' : 'FM',
           '25' : 'AM',
           '26' : 'TUNER',
           '27' : 'MUSIC SERVER', 
           '28' : 'INTERNET RADIO',
           '29' : 'USB',
           '40' : 'UNIVERSAL PORT',
           '32' : 'SIRIUS'         
            }
            
        self.Zone2InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SLZ00\r',
            'VIDEO 2 CBL/SAT' : '!1SLZ01\r',
            'VIDEO 3 GAME/TV' : '!1SLZ02\r',
            'VIDEO 4 AUX1'     : '!1SLZ03\r',
            'VIDEO 6 PC'      : '!1SLZ05\r',
            'DVD'             : '!1SLZ10\r',
            'PHONO'           : '!1SLZ22\r',
            'TV/CD'           : '!1SLZ23\r',
            'FM'              : '!1SLZ24\r',
            'AM'              : '!1SLZ25\r',
            'TUNER'           : '!1SLZ26\r',
            'MUSIC SERVER'    : '!1SLZ27\r',
            'INTERNET RADIO'  : '!1SLZ28\r',
            'USB'             : '!1SLZ29\r',
            'UNIVERSAL PORT'  : '!1SLZ40\r',
            'SIRIUS'          : '!1SLZ32\r',
            'SOURCE'          : '!1SLZ80\r'
            }
        self.Zone2InputStateNames = {
           '00' : 'VIDEO 1 VCR/DVR',
           '01' : 'VIDEO 2 CBL/SAT',
           '02' : 'VIDEO 3 GAME/TV',
           '03' : 'VIDEO 4 AUX1',
           '05' : 'VIDEO 6 PC',
           '10' : 'DVD',
           '22' : 'PHONO',
           '23' : 'TV/CD',
           '24' : 'FM',
           '25' : 'AM',
           '26' : 'TUNER',
           '27' : 'MUSIC SERVER',
           '28' : 'INTERNET RADIO',
           '29' : 'USB',
           '40' : 'UNIVERSAL PORT',
           '32' : 'SIRIUS',
           '80' : 'SOURCE'         
            }
            
        self.Zone3InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SL300\r',
            'VIDEO 2 CBL/SAT' : '!1SL301\r',
            'VIDEO 3 GAME/TV' : '!1SL302\r',
            'VIDEO 4 AUX1'    : '!1SL303\r',
            'VIDEO 5 AUX2'    : '!1SL304\r',
            'VIDEO 6 PC'      : '!1SL305\r',
            'DVD'             : '!1SL310\r',
            'PHONO'           : '!1SL322\r',
            'TV/CD'           : '!1SL323\r',
            'FM'              : '!1SL324\r',
            'AM'              : '!1SL325\r',
            'TUNER'           : '!1SL326\r',
            'MUSIC SERVER'    : '!1SL327\r',
            'INTERNET RADIO'  : '!1SL328\r',
            'USB'             : '!1SL329\r',
            'UNIVERSAL PORT'  : '!1SL340\r',
            'SIRIUS'          : '!1SL332\r',
            'SOURCE'          : '!1SL380\r'
            }
        self.Zone3InputStateNames = {
           '00' : 'VIDEO 1 VCR/DVR',
           '01' : 'VIDEO 2 CBL/SAT',
           '02' : 'VIDEO 3 GAME/TV',
           '03' : 'VIDEO 4 AUX1',
           '04' : 'VIDEO 5 AUX2',
           '05' : 'VIDEO 6 PC',
           '10' : 'DVD',
           '22' : 'PHONO',
           '23' : 'TV/CD',
           '24' : 'FM',
           '25' : 'AM',
           '26' : 'TUNER',
           '27' : 'MUSIC SERVER',
           '28' : 'INTERNET RADIO',
           '29' : 'USB',
           '40' : 'UNIVERSAL PORT',
           '32' : 'SIRIUS',
           '80' : 'SOURCE'         
            }
            
    def onky_27_296_RZ(self):
    

        self.InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SLI00\r',
            'VIDEO 2 CBL/SAT' : '!1SLI01\r',
            'VIDEO 3 GAME/TV' : '!1SLI02\r',
            'VIDEO 4 AUX1'    : '!1SLI03\r',
            'VIDEO 6 PC'      : '!1SLI05\r',
            'DVD'             : '!1SLI10\r',
            'PHONO'           : '!1SLI22\r',
            'TV/CD'           : '!1SLI23\r',
            'FM'              : '!1SLI24\r',
            'AM'              : '!1SLI25\r',
            'TUNER'           : '!1SLI26\r',
            'MUSIC SERVER'    : '!1SLI27\r',
            'INTERNET RADIO'  : '!1SLI28\r',
            'USB'             : '!1SLI29\r',
            'UNIVERSAL PORT'  : '!1SLI40\r',
            'SIRIUS'          : '!1SLI32\r',
            'Airplay'         : '!1SLI2D\r'
            }
        self.InputStateNames = {
            '00' : 'VIDEO 1 VCR/DVR',
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '03' : 'VIDEO 4 AUX1',
            '05' : 'VIDEO 6 PC',
            '10' : 'DVD',
            '22' : 'PHONO',
            '23' : 'TV/CD',
            '24' : 'FM',
            '25' : 'AM',
            '26' : 'TUNER',
            '27' : 'MUSIC SERVER', 
            '28' : 'INTERNET RADIO',
            '29' : 'USB',
            '40' : 'UNIVERSAL PORT',
            '32' : 'SIRIUS',
            '2D' : 'Airplay'
            }
            
        self.Zone2InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SLZ00\r',
            'VIDEO 2 CBL/SAT' : '!1SLZ01\r',
            'VIDEO 3 GAME/TV' : '!1SLZ02\r',
            'VIDEO 4 AUX1'    : '!1SLZ03\r',
            'VIDEO 6 PC'      : '!1SLZ05\r',
            'DVD'             : '!1SLZ10\r',
            'PHONO'           : '!1SLZ22\r',
            'TV/CD'           : '!1SLZ23\r',
            'FM'              : '!1SLZ24\r',
            'AM'              : '!1SLZ25\r',
            'TUNER'           : '!1SLZ26\r',
            'MUSIC SERVER'    : '!1SLZ27\r',
            'INTERNET RADIO'  : '!1SLZ28\r',
            'USB'             : '!1SLZ29\r',
            'UNIVERSAL PORT'  : '!1SLZ40\r',
            'SIRIUS'          : '!1SLZ32\r',
            'SOURCE'          : '!1SLZ80\r',
            'Airplay'         : '!1SLZ2D\r'
            }

        self.Zone2InputStateNames = {
            '00' : 'VIDEO 1 VCR/DVR',
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '03' : 'VIDEO 4 AUX1',
            '05' : 'VIDEO 6 PC',
            '10' : 'DVD',
            '22' : 'PHONO',
            '23' : 'TV/CD',
            '24' : 'FM',
            '25' : 'AM',
            '26' : 'TUNER',
            '27' : 'MUSIC SERVER',
            '28' : 'INTERNET RADIO',
            '29' : 'USB',
            '40' : 'UNIVERSAL PORT',
            '32' : 'SIRIUS',
            '80' : 'SOURCE',
            '2D' : 'Airplay'
            }
            
        self.Zone3InputStateValues = {
            'VIDEO 1 VCR/DVR' : '!1SL300\r',
            'VIDEO 2 CBL/SAT' : '!1SL301\r',
            'VIDEO 3 GAME/TV' : '!1SL302\r',
            'VIDEO 4 AUX1'    : '!1SL303\r',
            'VIDEO 5 AUX2'    : '!1SL304\r',
            'VIDEO 6 PC'      : '!1SL305\r',
            'DVD'             : '!1SL310\r',
            'PHONO'           : '!1SL322\r',
            'TV/CD'           : '!1SL323\r',
            'FM'              : '!1SL324\r',
            'AM'              : '!1SL325\r',
            'TUNER'           : '!1SL326\r',
            'MUSIC SERVER'    : '!1SL327\r',
            'INTERNET RADIO'  : '!1SL328\r',
            'USB'             : '!1SL329\r',
            'UNIVERSAL PORT'  : '!1SL340\r',
            'SIRIUS'          : '!1SL332\r',
            'SOURCE'          : '!1SL380\r',
            'Airplay'         : '!1SL32D\r'
            }

        self.Zone3InputStateNames = {
            '00' : 'VIDEO 1 VCR/DVR',
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '03' : 'VIDEO 4 AUX1',
            '04' : 'VIDEO 5 AUX2',
            '05' : 'VIDEO 6 PC',
            '10' : 'DVD',
            '22' : 'PHONO',
            '23' : 'TV/CD',
            '24' : 'FM',
            '25' : 'AM',
            '26' : 'TUNER',
            '27' : 'MUSIC SERVER',
            '28' : 'INTERNET RADIO',
            '29' : 'USB',
            '40' : 'UNIVERSAL PORT',
            '32' : 'SIRIUS',
            '80' : 'SOURCE',
            '2D' : 'Airplay'
            }

    def onky_27_296_RZ810(self):

    

        self.InputStateValues = {
            'VIDEO 2 CBL/SAT' : '!1SLI01\r',
            'VIDEO 3 GAME/TV' : '!1SLI02\r',
            'VIDEO 4 AUX1'    : '!1SLI03\r',
            'VIDEO 6 PC'      : '!1SLI05\r',
            'DVD'             : '!1SLI10\r',
            'STRM BOX'        : '!1SLI11\r',
            'TV'              : '!1SLI12\r',
            'PHONO'           : '!1SLI22\r',
            'TV/CD'           : '!1SLI23\r',
            'FM'              : '!1SLI24\r',
            'AM'              : '!1SLI25\r',
            'TUNER'           : '!1SLI26\r',
            'USB Front'       : '!1SLI29\r',
            'NETWORK'         : '!1SLI2B\r',
            'USB Toggle'      : '!1SLI2C\r',
            'Bluetooth'       : '!1SLI2E\r',
            }

        self.InputStateNames = {
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '03' : 'VIDEO 4 AUX1',   
            '05' : 'VIDEO 6 PC',     
            '10' : 'DVD',            
            '11' : 'STRM BOX',       
            '12' : 'TV',             
            '22' : 'PHONO',          
            '23' : 'TV/CD',          
            '24' : 'FM',             
            '25' : 'AM',             
            '26' : 'TUNER',          
            '29' : 'USB Front',      
            '2B' : 'NETWORK',        
            '2C' : 'USB Toggle',     
            '2E' : 'Bluetooth'
            }
            
        self.Zone2InputStateValues = {
            'VIDEO 2 CBL/SAT' : '!1SLZ01\r',
            'VIDEO 3 GAME/TV' : '!1SLZ02\r',
            'VIDEO 4 AUX1'    : '!1SLZ03\r',
            'VIDEO 6 PC'      : '!1SLZ05\r',
            'DVD'             : '!1SLZ10\r',
            'STRM BOX'        : '!1SLZ11\r',
            'TV'              : '!1SLZ12\r',
            'PHONO'           : '!1SLZ22\r',
            'TV/CD'           : '!1SLZ23\r',
            'FM'              : '!1SLZ24\r',
            'AM'              : '!1SLZ25\r',
            'TUNER'           : '!1SLZ26\r',
            'USB Front'       : '!1SLZ29\r',
            'NETWORK'         : '!1SLZ2B\r',
            'USB Toggle'      : '!1SLZ2C\r',
            'Bluetooth'       : '!1SLZ2E\r',
            'Source'          : '!1SLZ80\r'
            }

        self.Zone2InputStateNames = {
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '03' : 'VIDEO 4 AUX1',   
            '05' : 'VIDEO 6 PC',     
            '10' : 'DVD',            
            '11' : 'STRM BOX',       
            '12' : 'TV',             
            '22' : 'PHONO',          
            '23' : 'TV/CD',          
            '24' : 'FM',             
            '25' : 'AM',             
            '26' : 'TUNER',          
            '29' : 'USB Front',      
            '2B' : 'NETWORK',        
            '2C' : 'USB Toggle',     
            '2E' : 'Bluetooth',
            '80' : 'Source'
            }
            
        self.Zone3InputStateValues = {
            'VIDEO 2 CBL/SAT' : '!1SL301\r',
            'VIDEO 3 GAME/TV' : '!1SL302\r',
            'VIDEO 6 PC'      : '!1SL305\r',
            'DVD'             : '!1SL310\r',
            'STRM BOX'        : '!1SL311\r',
            'TV'              : '!1SL312\r',
            'PHONO'           : '!1SL322\r',
            'TV/CD'           : '!1SL323\r',
            'FM'              : '!1SL324\r',
            'AM'              : '!1SL325\r',
            'TUNER'           : '!1SL326\r',
            'USB Front'       : '!1SL329\r',
            'NETWORK'         : '!1SL32B\r',
            'USB Toggle'      : '!1SL32C\r',
            'Bluetooth'       : '!1SL32E\r',
            'Source'          : '!1SL380\r'
            }

        self.Zone3InputStateNames = {
            '01' : 'VIDEO 2 CBL/SAT',
            '02' : 'VIDEO 3 GAME/TV',
            '05' : 'VIDEO 6 PC',     
            '10' : 'DVD',            
            '11' : 'STRM BOX',       
            '12' : 'TV',             
            '22' : 'PHONO',          
            '23' : 'TV/CD',          
            '24' : 'FM',             
            '25' : 'AM',             
            '26' : 'TUNER',          
            '29' : 'USB Front',      
            '2B' : 'NETWORK',        
            '2C' : 'USB Toggle',     
            '2E' : 'Bluetooth',
            '80' : 'Source'
            }


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
