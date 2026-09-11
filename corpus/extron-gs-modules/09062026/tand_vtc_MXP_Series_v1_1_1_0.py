from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import ProgramLog

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
            'AudioInputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'AudioInputMode': {'Parameters': ['Channel'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallMute': {'Parameters': ['Call'], 'Status': {}},
            'CallOutgoingMute': {'Parameters': ['Call'], 'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'DirectoryDial': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DualMonitor': {'Status': {}},
            'DuoVideo': {'Status': {}},
            'DuoVideoSource': {'Status': {}},
            'FarEndCameraControl': {'Status': {}},
            'FarEndCameraFocus': {'Status': {}},
            'FarEndCameraPanTilt': {'Status': {}},
            'FarEndCameraPresetActivate': {'Status': {}},
            'FarEndCameraPresetStore': {'Status': {}},
            'FarEndCameraSource': {'Status': {}},
            'FarEndCameraZoom': {'Status': {}},
            'Focus': {'Parameters': ['Camera'], 'Status': {}},
            'Hook': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'MicrophoneMode': {'Status': {}},
            'PanTilt': {'Parameters': ['Camera'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearch': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearchSet': {'Status' :{}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type', 'Folder ID'], 'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Reboot': {'Status': {}},
            'ScreenSaver': {'Status': {}},
            'ScreenSaverMode': {'Status': {}},
            'SwitchSource': {'Status': {}},
            'VirtualMonitorSet': {'Parameters': ['Virtual Monitor', 'Picture', 'Call'], 'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Parameters': ['Camera'], 'Status': {}},
        }

        self.Local = PhonebookGenerator()
        self.Corporate = PhonebookGenerator()

        self.StartingEntry = 1
        self.NumberOfButton = 0
        self.dirEntry = compile('directory (\d+) (.+) (tlph|1xh221|2xh221|64|128|192|256|320|384|512|768|1152|1472|1920|2560|3072|4096|max|auto) p\d+ (.*)\r\n')

        self.devicePassword = None

        self.NumberOfButton = 5

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'xConfiguration FECC Mode: (On|Off)'), self.__MatchFarEndCameraControl, None)
            self.AddMatchString(compile(b'Screensaver \(status=(On|Off)\):'), self.__MatchScreenSaver, None)
            self.AddMatchString(compile(b'xConfiguration Screensaver Mode: (On|Off)'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(compile(b'xConfiguration MainVideoSource: (\d)'), self.__MatchInput, None)
            self.AddMatchString(compile(b'xConfiguration DualMonitor Mode: (On|Off)'), self.__MatchDualMonitor, None)
            self.AddMatchString(compile(b'xConfiguration DuoVideoSource: (\d)'), self.__MatchDuoVideoSource, None)
            self.AddMatchString(compile(b'xConfiguration Audio Volume: (\d+)'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'xConfiguration Audio Inputs (.* \d) Level: (\d+)'), self.__MatchAudioInputLevel, None)
            self.AddMatchString(compile(b'xConfiguration Audio Inputs (.* \d) Mode: (On|Off)'), self.__MatchAudioInputMode, None)
            self.AddMatchString(compile(b'xConfiguration Audio Microphones Mode: (On|Off)'), self.__MatchMicrophoneMode, None)
            self.AddMatchString(compile(b'xConfiguration AutoPIP Mode: (On|Off|Auto)'), self.__MatchPictureInPicture, None)
            self.AddMatchString(compile(b'\*P donotdist (on|off)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*S callstatus (1|2) (idle|incoming|outgoing) (idle|speech|extnet|h221|H0|bonding|h323|streaming|h323-voip) (idle|answering|ringing|calling|connected|disconnecting|disconnected|incoming) \d+ \d+Sec'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'RING '), self.__MatchRing, None)
            self.AddMatchString(compile(b'\r\n\*P autoans (on|off|mute)\r\n'), self.__MatchAutoAnswer, None)

            self.AddMatchString(compile(b'\r\n(\r\n\*P directory (\d+) (.+) (tlph|1xh221|2xh221|64|128|192|256|320|384|512|768|1152|1472|1920|2560|3072|4096|max|auto) p\d+ (.*)\r\n)+\r\nOK\r\n'), self.__MatchPhonebookUpdate, 'Local')

            self.AddMatchString(compile(b'ERROR\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self.NumberOfButton

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self.NumberOfButton = value

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword+'\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def SetVirtualMonitorSet(self, value, qualifier):

        vm = int(qualifier['Virtual Monitor'])
        picture = qualifier['Picture']
        call = qualifier['Call']

        PictureValue = ['Local Main', 'Local Duo', 'Still', 'Current', 'Previous', 'Duo', 'Remote Main',
                        'Remote Duo', 'JPEG', 'Tandberg Monitor 1', 'Tandberg Monitor 2', 'Picture Program 1',
                        'Picture Program 2', 'Picture Program 3', 'Picture Program 4', 'None']

        if vm < 1 or vm > 4:
            print('Invalid Command for SetVirtualMonitorSet')
        elif picture not in PictureValue:
            print('Invalid Command for SetVirtualMonitorSet')
        elif call not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 'None']:
            print('Invalid Command for SetVirtualMonitorSet')
        else:
            if call == 'None':
                cmdString = 'xcommand virtualmonitorset virtualmonitor: {0} picture: {1}\r'.format(vm, picture.replace(' ', '').lower())
            else:
                cmdString = 'xcommand virtualmonitorset virtualmonitor: {0} picture: {1} call: {2}\r'.format(vm, picture.replace(' ', '').lower(), call)
            self.__SetHelper('VirtualMonitorSet', cmdString, value, qualifier)

    def SetAutoAnswer(self, value, qualifier):

        if value in ['On', 'Off', 'Mute']:
            self.__SetHelper('AutoAnswer', 'autoans {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        self.__UpdateHelper('AutoAnswer', 'autoans\r', qualifier)

    def __MatchAutoAnswer(self, match, tag):

        self.WriteStatus('AutoAnswer', match.group(1).decode().title(), None)

    def SetPanTilt(self, value, qualifier):

        camera = int(qualifier['Camera'])
        if camera < 1 or camera > 13:
            print('Invalid Command for SetPanTilt')
        elif value in ['Up', 'Down', 'Right', 'Left', 'Stop']:
            if value == 'Stop':
                command = 'camerahalt'
                value = ''
            else:
                command = 'cameramove'
            self.__SetHelper('PanTilt', 'xcommand {0} {1} {2}\r'.format(command, camera, value), value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetZoom(self, value, qualifier):

        camera = int(qualifier['Camera'])
        if camera < 1 or camera > 13:
            print('Invalid Command for SetZoom')
        elif value in ['Stop', 'In', 'Out']:
            if value == 'Stop':
                command = 'camerahalt'
                value = ''
            else:
                command = 'cameramove'
            self.__SetHelper('Zoom', 'xcommand {0} {1} {2}\r'.format(command, camera, value), value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def SetFocus(self, value, qualifier):

        FocusValue = {
            'Near': ['cameramove', 'focusin'],
            'Far': ['cameramove', 'focusout'],
            'Auto': ['camerafocus', 'auto'],
            'Stop': ['camerahalt', ''],
        }

        camera = qualifier['Camera']

        if 0 < int(camera) < 14:
            command = FocusValue[value][0]
            value = FocusValue[value][1]

            self.__SetHelper('Focus', 'xcommand {0} {1} {2}\r'.format(command, camera, value), value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFarEndCameraControl(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('FarEndCameraControl', 'fecc {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraControl')

    def UpdateFarEndCameraControl(self, value, qualifier):

        self.__UpdateHelper('FarEndCameraControl', 'xconfiguration fecc\r', qualifier)

    def __MatchFarEndCameraControl(self, match, qualifier):

        return self.WriteStatus('FarEndCameraControl', match.group(1).decode(), None)

    def SetFarEndCameraPanTilt(self, value, qualifier):

        PanValue = [
            'Up',
            'Down',
            'Right',
            'Left'
        ]

        if value in PanValue:
            self.__SetHelper('FarEndCameraPanTilt', 'xcommand feccmove {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraPanTilt')

    def SetFarEndCameraZoom(self, value, qualifier):

        ZoomValue = [
            'In',
            'Out',
        ]

        if value in ZoomValue:
            self.__SetHelper('FarEndCameraZoom', 'xcommand feccmove {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraZoom')

    def SetFarEndCameraFocus(self, value, qualifier):

        FocusValue = {
            'Near': '+',
            'Far': '-',
        }

        self.__SetHelper('FarEndCameraFocus', 'xcommand feccfocus {0}\r'.format(FocusValue[value]), value, qualifier)

    def SetFarEndCameraPresetActivate(self, value, qualifier):

        if 0 <= int(value) < 16:
            self.__SetHelper('FarEndCameraPresetActivate', 'xcommand feccpresetactivate {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraPresetActivate')

    def SetFarEndCameraPresetStore(self, value, qualifier):

        if 0 <= int(value) < 16:
            self.__SetHelper('FarEndCameraPresetActivate', 'xcommand feccpresetstore {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraPresetStore')

    def SetFarEndCameraSource(self, value, qualifier):

        if 0 <= value < 16:
            self.__SetHelper('FarEndCameraSource', 'xcommand feccselectsource {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetFarEndCameraSource')

    def SetIRRemoteEmulation(self, value, qualifier):

        IRValue = ['Up', 'Down', 'Left', 'Right', 'Ok', 'Cancel', 'Grab',
                   '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#',
                   'Connect', 'Disconnect', 'Selfview', 'Layout', 'Phonebook',
                   'Mic Off', 'Presentation', 'Volume Up', 'Volume Down', 'Zoom In', 'Zoom Out',
                   ]

        if value in IRValue:
            self.__SetHelper('IRRemoteEmulation', 'xcommand keypress {0}\r'.format(value.replace(' ', '')), value, qualifier)
        else:
            print('Invalid Command for SetIRRemoteEmulation')

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'boot\r', value, qualifier)

    def SetScreenSaver(self, value, qualifier):

        ScreenSaverValue = {
            'On': 'Screensaveractivate',
            'Off': 'Screensaverdeactivate',
        }
        self.__SetHelper('ScreenSaver', 'xcommand {0}\r'.format(ScreenSaverValue[value]), value, qualifier)

    def UpdateScreenSaver(self, value, qualifier):

        self.__UpdateHelper('ScreenSaver', 'xstatus screensaver\r', qualifier)

    def __MatchScreenSaver(self, match, qualifier):

        self.WriteStatus('ScreenSaver', match.group(1).decode(), None)

    def SetScreenSaverMode(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('ScreenSaverMode', 'xconfiguration screensaver mode: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetScreenSaverMode')

    def UpdateScreenSaverMode(self, value, qualifier):

        self.__UpdateHelper('ScreenSaverMode', 'xconfiguration screensaver mode\r', qualifier)

    def __MatchScreenSaverMode(self, match, qualifier):

        self.WriteStatus('ScreenSaverMode', match.group(1).decode(), None)

    def SetSwitchSource(self, value, qualifier):

        if value in ['1', '2', '3', '4', '5', '6']:
            self.__SetHelper('SwitchSource', 'xconfiguration switch source: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetSwitchSource')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 14:
            self.__SetHelper('PresetRecall', 'xcommand presetactivate number: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 14:
            self.__SetHelper('PresetSave', 'xcommand presetstore number: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetInput(self, value, qualifier):

        if 0 < int(value) < 7:
            self.__SetHelper('Input', 'xconfiguration mainvideosource:{0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', 'xconfiguration mainvideosource\r', qualifier)

    def __MatchInput(self, match, qualifier):

        self.WriteStatus('Input', match.group(1).decode(), qualifier)

    def SetDualMonitor(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('DualMonitor', 'xconfiguration dualmonitor mode: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetDualMonitor')

    def UpdateDualMonitor(self, value, qualifier):

        self.__UpdateHelper('DualMonitor', 'xconfiguration dualmonitor\r', qualifier)

    def __MatchDualMonitor(self, match, qualifier):

        self.WriteStatus('DualMonitor', match.group(1).decode(), None)

    def SetDuoVideo(self, value, qualifier):

        if value in ['Start', 'Stop']:
            self.__SetHelper('DuoVideo', 'xcommand duovideo{0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetDuoVideo')

    def SetDuoVideoSource(self, value, qualifier):

        if 0 <= int(value) < 7:
            self.__SetHelper('DuoVideoSource', 'xconfiguration duovideosource:{0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetDuoVideoSource')

    def UpdateDuoVideoSource(self, value, qualifier):

        self.__UpdateHelper('DuoVideoSource', 'xconfiguration duovideosource\r', qualifier)

    def __MatchDuoVideoSource(self, match, qualifier):

        self.WriteStatus('DuoVideoSource', match.group(1).decode(), None)

    def SetVolume(self, value, qualifier):

        if 0 <= value < 22:
            self.__SetHelper('Volume', 'xconfiguration audio volume:{0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'xconfiguration audio volume\r', qualifier)

    def __MatchVolume(self, match, qualifier):

        self.WriteStatus('Volume', int(match.group(1)), qualifier)

    def SetAudioInputLevel(self, value, qualifier):

        channel = qualifier['Channel']
        if value < 1 or value > 16:
            print('Invalid Command for SetAudioInputLevel')
        elif channel not in ['Microphone 1', 'Microphone 2', 'Microphone 3', 'Line 1', 'Line 2', 'Line 3']:
            print('Invalid Command for SetAudioInputLevel')
        else:
            self.__SetHelper('AudioInputLevel', 'xconfiguration audio inputs {0} level: {1}\r'.format(channel, value), value, qualifier)

    def UpdateAudioInputLevel(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['Microphone 1', 'Microphone 2', 'Microphone 3', 'Line 1', 'Line 2', 'Line 3']:
            self.__UpdateHelper('AudioInputLevel', 'xconfiguration audio inputs {0} level\r'.format(channel), qualifier)
        else:
            print('Invalid Command for UpdateAudioInputLevel')

    def __MatchAudioInputLevel(self, match, qualifier):

        self.WriteStatus('AudioInputLevel', int(match.group(2)), {self.Commands['AudioInputLevel']['Parameters'][0]: match.group(1).decode()})

    def SetAudioInputMode(self, value, qualifier):

        channel = qualifier['Channel']

        if value not in ['On', 'Off']:
            print('Invalid Command for SetAudioInputMode')
        elif channel not in ['Microphone 1', 'Microphone 2', 'Microphone 3', 'Line 1', 'Line 2', 'Line 3']:
            print('Invalid Command for SetAudioInputMode')
        else:
            self.__SetHelper('AudioInputMode', 'xconfiguration audio inputs {0} mode: {1}\r'.format(channel, value), value, qualifier)

    def UpdateAudioInputMode(self, value, qualifier):

        channel = qualifier['Channel']

        if channel in ['Microphone 1', 'Microphone 2', 'Microphone 3', 'Line 1', 'Line 2', 'Line 3']:
            self.__UpdateHelper('AudioInputMode', 'xconfiguration audio inputs {0} mode\r'.format(channel), qualifier)
        else:
            print('Invalid Command for UpdateAudioInputMode')

    def __MatchAudioInputMode(self, match, qualifier):

        self.WriteStatus('AudioInputMode', match.group(2).decode(), {self.Commands['AudioInputMode']['Parameters'][0]: match.group(1).decode()})

    def SetMicrophoneMode(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('MicrophoneMode', 'xconfiguration audio microphones mode: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetMicrophoneMode')

    def UpdateMicrophoneMode(self, value, qualifier):

        self.__UpdateHelper('MicrophoneMode', 'xconfiguration audio microphones mode\r', qualifier)

    def __MatchMicrophoneMode(self, match, qualifier):

        self.WriteStatus('MicrophoneMode', match.group(1).decode(), None)

    def SetPictureInPicture(self, value, qualifier):

        if value in ['On', 'Off', 'Auto']:
            self.__SetHelper('PictureInPicture', 'xconfiguration autopip mode: {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):

        self.__UpdateHelper('PictureInPicture', 'xconfiguration autopip mode\r', qualifier)

    def __MatchPictureInPicture(self, match, qualifier):

        self.WriteStatus('PictureInPicture', match.group(1).decode(), qualifier)

    def SetDoNotDisturb(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('DoNotDisturb', 'donotdist {0}\r'.format(value), value, qualifier)
        else:
            print('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):

        self.__UpdateHelper('DoNotDisturb', 'donotdist\r', qualifier)

    def __MatchDoNotDisturb(self, match, qualifier):

        self.WriteStatus('DoNotDisturb', match.group(1).decode().title(), qualifier)

    def SetCallMute(self, value, qualifier):

        call = int(qualifier['Call'])
        if call < 1 or call > 2:
            print('Invalid Command for SetCallMute')
        elif value not in ['On', 'Off']:
            print('Invalid Command for SetCallMute')
        else:
            self.__SetHelper('CallMute', 'xcommand callmute {0} {1}\r'.format(call, value), value, qualifier)

    def SetCallOutgoingMute(self, value, qualifier):

        call = int(qualifier['Call'])
        if call < 1 or call > 2:
            print('Invalid Command for SetCallOutgoingMute')
        elif value not in ['On', 'Off']:
            print('Invalid Command for SetCallOutgoingMute')
        else:
            self.__SetHelper('CallMute', 'xcommand callmuteoutgoing {0} {1}\r'.format(call, value), value, qualifier)

    def SetHook(self, value, qualifier):

        if value == 'Dial':
            number = qualifier['Number']
            if number:
                self.__SetHelper('Hook', 'xcommand dial {0}\r'.format(number), value, qualifier)
        elif value == 'Disconnect':
            self.__SetHelper('Hook', 'xcommand Disconnectcall\r', value, qualifier)
        elif value == 'Accept':
            self.__SetHelper('Hook', 'xcommand CallAccept\r', value, qualifier)

    def UpdateCallStatus(self, value, qualifier):

        self.__UpdateHelper('CallStatus', 'call\r', qualifier)

    def __MatchCallStatus(self, match, qualifier):
        self.WriteStatus('CallStatus', match.group(4).decode().title(), {'Call': match.group(1).decode()})

    def __MatchRing(self, match, qualifier):
        self.WriteStatus('CallStatus', 'Incoming', {self.Commands['CallStatus']['Parameters'][0]: 1})

    def SetDirectoryDial(self, value, qualifier):

        if value < 1 or value > 200:
            print('Invalid Command for SetDirectoryDial')
        else:
            self.__SetHelper('DirectoryDial', 'xcommand diallocalentry : {0}\r'.format(value), value, qualifier)

    def SetPhonebookSearch(self, value, qualifier):

        phonebookType = qualifier['Phonebook Type']

        if phonebookType not in ['Local', 'Corporate']:
            print('Invalid Command for SetPhonebookSearch')
        else:

            self.StartingEntry = 1
            if phonebookType == 'Local':
                entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, )
            else:
                entries = self.Corporate.GetEntry(self.StartingEntry, self.NumberOfButton, )
            button = 1
            for v in entries:
                self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Phonebook Type': button})
                button += 1
                
    def SetPhonebookSearchSet(self, value, qualifier):
        self.SetHook('Dial', {'Number' : value})

    def SetPhonebookNavigation(self, value, qualifier):

        phonebookType = qualifier['Phonebook Type']

        if value not in ['Up', 'Down', 'Page Up', 'Page Down'] and phonebookType not in ['Local', 'Corporate']:
            print('Invalid Command for SetPhonebookNavigation')
        else:
            if 'Page' in value:
                NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                tv = self.StartingEntry + NumberOfAdvance
                if tv > 201:
                    start = 200
                else:
                    start = tv
                self.StartingEntry = start
            elif 'Up' in value:
                tv = self.StartingEntry - NumberOfAdvance
                if tv < 1:
                    start = 1
                else:
                    start = tv
                self.StartingEntry = start

            if phonebookType == 'Local':
                entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, )
            elif phonebookType == 'Corporate':
                entries = self.Corporate.GetEntry(self.StartingEntry, self.NumberOfButton, )

            button = 1
            for v in entries:
                self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                button += 1

    def SetPhonebookUpdate(self, value, qualifier):

        phonebookType = qualifier['Phonebook Type']
        if phonebookType in ['Local', 'Corporate']:

            if phonebookType == 'Local':
                PhonebookUpdateCmdString = 'directory all\r'
                self.__SetHelper('PhonebookUpdate', PhonebookUpdateCmdString, None, None)

            elif phonebookType == 'Corporate':
                folderID = qualifier['Folder ID']
                if folderID:
                    folderID = ' path: {0}'.format(folderID)
                else:
                    folderID = ''
                PhonebookUpdateCmdString = 'xcommand CorpDirSearch{0}\r'.format(folderID)
                res = self.__SetHelperSync('PhonebookUpdate', PhonebookUpdateCmdString, None, None)
                if res:
                    self.__PhonebookUpdateHandler(res, 'Corporate')

        else:
            print('Invalid Command for SetPhonebookUpdate')

    def __MatchPhonebookUpdate(self, match, tag):

        self.__PhonebookUpdateHandler(match.group(0).decode(), tag)

    def __PhonebookUpdateHandler(self, res, tag):
        if res != '':
            if tag == 'Local':
                newList = []
                result = findall(self.dirEntry, res)
                for i, number, j, name in result:
                    newList.append('{0} : {1}'.format(name, number))
                self.Local.UpdatePhonebook(newList)
                entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, )
                button = 1
                for v in entries:
                    self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                    button += 1

            elif tag == 'Corporate':

                lineList = res.splitlines()

                newList = []
                lookingFor = ''

                for line in lineList:
                    if line.startswith('Entity '):
                        lookingFor = 'Name:'
                    elif line.startswith(lookingFor):
                        if lookingFor == 'Name:':
                            newList.append(line[7:-1])
                            lookingFor = 'DialString:'
                        elif lookingFor == 'DialString:':
                            newList[len(newList) - 1] += ' : ' + line[13:-1]
                            lookingFor = ''

                self.Corporate.UpdatePhonebook(newList)
                entries = self.Corporate.GetEntry(self.StartingEntry, self.NumberOfButton, )
                button = 1
                for v in entries:
                    self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                    button += 1

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __SetHelperSync(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            
            res = self.SendAndWait(commandstring, 10, deliTag='\r\nOK\r\n').decode(encoding='iso-8859-1')
            if not res:
                print('No Response')

            return res

    def __UpdateHelper(self, command, commandstring, qualifier):
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

    def __MatchError(self, match, tag):

        print(match.group(0).decode())

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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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


class PhonebookGenerator:

    def __init__(self):
        self.Phonebook = []

    def UpdatePhonebook(self, newBook):

        self.Phonebook = sorted(newBook)

    def GetEntry(self, start, number, searchName=None):

        retList = []
        book = []
        end = start + number
        if searchName and searchName != '':
            for k in self.Phonebook:
                if k.lower().find(searchName.lower()) == 0 or k.lower().find(' ' + searchName.lower()) > 0:
                    book.append(k)
        else:
            book = self.Phonebook

        i = 1
        for name in book:
            if start <= i < end:
                retList.append(name)
            i += 1

        retList = sorted(retList)
        if i <= end:
            retList.append('***End of list***')
            i += 1
            for i in range(len(retList), end):
                retList.append('')
        return retList
