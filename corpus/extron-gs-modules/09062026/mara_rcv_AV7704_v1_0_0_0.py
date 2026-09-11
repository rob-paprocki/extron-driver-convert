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
            'AspectRatio': {'Status': {}},
            'Input': {'Status': {}},
            'MainZone': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelButtonLock': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
            'SurroundMode': {'Status': {}},
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
            self.AddMatchString(re.compile(b'VSASP(NRM|FUL)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'SI(PHONO|CD|DVD|BD|TV|SAT/CBL|MPLAY|GAME|TUNER|RADIO|AUX1|AUX2|NET|BT)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZone, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'(MU|Z2MU|Z3MU)(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MS([\s\S]+)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\rZ2(CD|BT)\rZ2([0-9]{2})\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z3(ON|OFF)\rZ3(CD|BT)\rZ3([0-9]{2})\r'), self.__MatchZone3Power, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3': 'VSASPNRM\r',
            '16:9': 'VSASPFUL\r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'VSASP?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            'NRM': '4:3',
            'FUL': '16:9'
            }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'Phono': 'SIPHONO\r',
            'CD': 'SICD\r',
            'DVD': 'SIDVD\r',
            'BD': 'SIBD\r',
            'TV': 'SITV\r',
            'SAT/CBL': 'SISAT/CBL\r',
            'Media Player': 'SIMPLAY\r',
            'Game': 'SIGAME\r',
            'Tuner': 'SITUNER\r',
            'Radio': 'SIRADIO\r',
            'AUX 1': 'SIAUX1\r',
            'AUX 2': 'SIAUX2\r',
            'Online Music': 'SINET\r',
            'Bluetooth': 'SIBT\r'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            'PHONO': 'Phono',
            'CD': 'CD',
            'DVD': 'DVD',
            'BD': 'BD',
            'TV': 'TV',
            'SAT/CBL': 'SAT/CBL',
            'MPLAY': 'Media Player',
            'GAME': 'Game',
            'TUNER': 'Tuner',
            'RADIO': 'Radio',
            'AUX1': 'AUX 1',
            'AUX2': 'AUX 2',
            'NET': 'Online Music',
            'BT': 'Bluetooth'
            }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZone(self, value, qualifier):

        MainZoneState = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r'
            }

        MainZoneCmdString = MainZoneState[value]
        self.__SetHelper('MainZone', MainZoneCmdString, value, qualifier)

    def UpdateMainZone(self, value, qualifier):

        MainZoneCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZone', MainZoneCmdString, value, qualifier)

    def __MatchMainZone(self, match, tag):

        MainZoneState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = MainZoneState[match.group(1).decode()]
        self.WriteStatus('MainZone', value, None)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = 'MV{0:02}\r'.format(value + 80)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = int(match.group(1).decode()) - 80
        self.WriteStatus('MasterVolume', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'MNCUP\r',
            'Down': 'MNCDN\r',
            'Left': 'MNCLT\r',
            'Right': 'MNCRT\r',
            'Enter': 'MNENT\r',
            'Return': 'MNRTN\r'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        OutputMuteState = {
            'On': 'MUON\r',
            'Off': 'MUOFF\r'
            }

        OutputMuteCmdString = OutputMuteState[value]
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'MU?\r'
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        OutputMuteState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        if match.group(1).decode() == 'MU':
            value = OutputMuteState[match.group(2).decode()]
            self.WriteStatus('OutputMute', value, None)
        elif match.group(1).decode() == 'Z2MU':
            value = OutputMuteState[match.group(2).decode()]
            self.WriteStatus('Zone2Mute', value, None)
        elif match.group(1).decode() == 'Z3MU':
            value = OutputMuteState[match.group(2).decode()]
            self.WriteStatus('Zone3Mute', value, None)

    def SetPanelButtonLock(self, value, qualifier):

        PanelButtonState = {
            'Mode 1': 'SYPANEL LOCK ON\r',
            'Mode 2': 'SYPANEL+V LOCK ON\r',
            'Off': 'SYPANEL LOCK OFF\r'
            }

        PanelButtonLockCmdString = PanelButtonState[value]
        self.__SetHelper('PanelButtonLock', PanelButtonLockCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'PWON\r',
            'Off': 'PWSTANDBY\r'
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            'ON': 'On',
            'STANDBY': 'Off'
            }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        PresetRecallState = {
            '1': 'MSSMART1\r',
            '2': 'MSSMART2\r',
            '3': 'MSSMART3\r',
            '4': 'MSSMART4\r',
            '5': 'MSSMART5\r'
            }

        PresetRecallCmdString = PresetRecallState[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveState = {
            '1': 'MSSMART1 MEMORY\r',
            '2': 'MSSMART2 MEMORY\r',
            '3': 'MSSMART3 MEMORY\r',
            '4': 'MSSMART4 MEMORY\r',
            '5': 'MSSMART5 MEMORY\r'
            }

        PresetSaveCmdString = PresetSaveState[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetRemoteControlLock(self, value, qualifier):

        RemoteControlLockState = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
            }

        RemoteControlLockCmdString = RemoteControlLockState[value]
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        SurroundModeState = {
            'Movie': 'MSMOVIE\r',
            'Music': 'MSMUSIC\r',
            'Game': 'MSGAME\r',
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO\r',
            'Auto': 'MSAUTO\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'Dolby Surround': 'MSDOLBY SURROUND\r',
            'Dolby Atmos': 'MSDOLBY ATMOS\r',
            'Dolby D+DS': 'MSDOLBY D+DS\r',
            'Dolby D+ Neural': 'MSDOLBY D+NEURAL:X\r',
            'Dolby D+': 'MSDOLBY D+\r',
            'Dolby D++DS': 'MSDOLBY D+ +DS\r',
            'Dolby D++Neural': 'MSDOLBY D+ +NEURAL:X\r',
            'Dolby HD': 'MSDOLBY HD\r',
            'Dolby HD+DS': 'MSDOLBY HD+DS\r',
            'Dolby HD+Neural': 'MSDOLBY HD+NEURAL:X\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'Neural': 'MSNEURAL:X\r',
            'DTS ES DSCRT6.1': 'MSDTS ES DSCRT6.1\r',
            'DTS ES MTRX6.1': 'MSDTS ES MTRX6.1\r',
            'DTS DS': 'MSDTS+DS\r',
            'DTS Neural': 'MSDTS+NEURAL:X\r',
            'DTS ES MTRX Neural': 'MSDTS ES MTRX+NEURAL:X\r',
            'DTS ES DSCRT Neural': 'MSDTS ES DSCRT+NEURAL:X\r',
            'DTS 96/24': 'MSDTS96/24\r',
            'DTS 96 ES MTRX': 'MSDTS96 ES MTRX\r',
            'DTS HD': 'MDTS HD\r',
            'DTS HD Master': 'MDTS HD MSTR\r',
            'DTS HD DS': 'MSDTS HD+DS\r',
            'DTS HD Neural': 'MSDTS HD+NEURAL:X\r',
            'DTS X': 'MSDTS:X\r',
            'DTS X Master': 'MSDTS:X MSTR\r',
            'DTS Express': 'MSDTS EXPRESS\r',
            'DTS ES 8CH DSCRT': 'MSDTS ES 8CH DSCRT\r',
            'Multi Channel In': 'MSMULTI CH IN\r',
            'M Channel In+DS': 'MSM CH IN+DS\r',
            'M Channel In+Neural': 'MSM CH IN+NEURAL\r',
            'Multi Channel In 7.1': 'MSMULTI CH IN 7.1\r',
            }

        SurroundModeCmdString = SurroundModeState[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        SurroundModeState = {
            'MOVIE': 'Movie',
            'MUSIC': 'Music',
            'GAME': 'Game',
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'AUTO': 'Auto',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DOLBY SURROUND': 'Dolby Surround',
            'DOLBY ATMOS': 'Dolby Atmos',
            'DOLBY D+DS': 'Dolby D+DS',
            'DOLBY D+NEURAL': 'Dolby D+ Neural',
            'DOLBY D+': 'Dolby D+',
            'DOLBY D+ +DS': 'Dolby D+ +DS',
            'DOLBY D+ +NEURAL:X': 'Dolby D+ +Neural',
            'DOLBY HD': 'Dolby HD',
            'DOLBY HD+DS': 'Dolby HD+DS',
            'DOLBY HD+NEURAL:X': 'Dolby HD+Neural',
            'DTS SURROUND': 'DTS Surround',
            'NEURAL:X': 'Neural',
            'DTS ES DSCRT6.1': 'DTS ES DSCRT6.1',
            'DTS ES MTRX6.1': 'DTS ES MTRX6.1',
            'DTS+DS': 'DTS DS',
            'DTS+NEURAL:X': 'DTS Neural',
            'DTS ES MTRX+NEURAL:X': 'DTS ES MTRX Neural',
            'DTS ES DSCRT+NEURAL:X': 'DTS ES DSCRT Neural',
            'DTS96/24': 'DTS 96/24',
            'DTS 96 ES MTRX': 'DTS 96 ES MTRX',
            'DTS HD': 'DTS HD',
            'DTS HD MSTR': 'DTS HD Master',
            'DTS HD+DS': 'DTS HD DS',
            'DTS HD+NEURAL:X': 'DTS HD Neural',
            'DTS:X': 'DTS X',
            'DTS:X MSTR': 'DTS X Master',
            'DTS EXPRESS': 'DTS Express',
            'DTS ES 8CH DSCRT': 'DTS ES 8CH DSCRT',
            'MULTI CH IN': 'Multi Channel In',
            'M CH IN+DS': 'M Channel In+DS',
            'M CH IN+NEURAL': 'M Channel In+Neural',
            'MULTI CH IN7.1': 'Multi Channel In 7.1'
            }

        value = SurroundModeState[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetZone2Input(self, value, qualifier):

        Z2InputState = {
            'CD': 'Z2CD\r',
            'Bluetooth': 'Z2BT\r'
            }

        Zone2InputCmdString = Z2InputState[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        self.UpdateZone2Power(value, qualifier)

    def SetZone2Mute(self, value, qualifier):

        Zone2MuteState = {
            'On': 'Z2MUON\r',
            'Off': 'Z2MUOFF\r'
            }

        Zone2MuteCmdString = Zone2MuteState[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        Zone2MuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def SetZone2Power(self, value, qualifier):

        Zone2PowerState = {
            'On': 'Z2ON\r',
            'Off': 'Z2OFF\r'
            }

        Zone2PowerCmdString = Zone2PowerState[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        Zone2PowerState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        Zone2InputState = {
            'CD': 'CD',
            'BT': 'Bluetooth'
            }

        PowerValue = Zone2PowerState[match.group(1).decode()]
        self.WriteStatus('Zone2Power', PowerValue, None)

        InputValue = Zone2InputState[match.group(2).decode()]
        self.WriteStatus('Zone2Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone2Volume', VolValue, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = 'Z2{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        self.UpdateZone2Power(value, qualifier)

    def SetZone3Input(self, value, qualifier):

        Zone3InputState = {
            'CD': 'Z3CD\r',
            'Bluetooth': 'Z3BT\r'
            }

        Zone3InputCmdString = Zone3InputState[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):

        self.UpdateZone3Power(value, qualifier)

    def SetZone3Mute(self, value, qualifier):

        Zone3MuteState = {
            'On': 'Z3MUON\r',
            'Off': 'Z3MUOFF\r'
            }

        Zone3MuteCmdString = Zone3MuteState[value]
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):

        Zone3MuteCmdString = 'Z3MU?\r'
        self.__UpdateHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def SetZone3Power(self, value, qualifier):

        Zone3PowerState = {
            'On': 'Z3ON\r',
            'Off': 'Z3OFF\r'
            }

        Zone3PowerCmdString = Zone3PowerState[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = 'Z3?\r'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        Zone3PowerState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        Zone3InputState = {
            'CD': 'CD',
            'BT': 'Bluetooth'
            }

        PowerValue = Zone3PowerState[match.group(1).decode()]
        self.WriteStatus('Zone3Power', PowerValue, None)

        InputValue = Zone3InputState[match.group(2).decode()]
        self.WriteStatus('Zone3Input', InputValue, None)

        VolValue = int(match.group(3).decode()) - 80
        self.WriteStatus('Zone3Volume', VolValue, None)

    def SetZone3Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone3VolumeCmdString = 'Z3{0:02}\r'.format(value + 80)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        self.UpdateZone3Power(value, qualifier)

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

