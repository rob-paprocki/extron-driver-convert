from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re

class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Zone'], 'Status': {}},
            'AudioSourceStatus': {'Status': {}},
            'AudioZone': {'Status': {}},
            'AutoPower': {'Status': {}},
            'AutoSourceScan': {'Status': {}},
            'CurrentZoneLayout': {'Status': {}},
            'EcoMode': {'Status': {}},
            'EDID': {'Parameters': ['Input'], 'Status': {}},
            'EDIDZone': {'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiSourceLayout': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Reboot': {'Status': {}},
            'TouchControl': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT(?:\((ZONE\.[1-4])\))?:(AUTO|16X9|4X3|FILL|NATIVE|LETTERBOX)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AUDIO\.INPUT:(OPS|HDMI\.[1-4]|DP)\r'), self.__MatchAudioSourceStatus, None)
            self.AddMatchString(re.compile(b'AUDIO\.ZONE:(ZONE\.[1-4])\r'), self.__MatchAudioZone, None)
            self.AddMatchString(re.compile(b'AUTO\.ON:(ON|OFF)\r'), self.__MatchAutoPower, None)
            self.AddMatchString(re.compile(b'SOURCE\.SCAN:(ON|OFF)\r'), self.__MatchAutoSourceScan, None)
            self.AddMatchString(re.compile(b'CURRENT\.ZONE\.LAYOUT:(S\.1|P\.[UL][RL]\.[12]|D\.[LT]\.[12]|T\.[LRTBM]\.[1-3]|Q\.[1-4])\r'), self.__MatchCurrentZoneLayout, None)
            self.AddMatchString(re.compile(b'POWER\.SAVE\.MODE:(DISABLED|LOW\.POWER|WAKE\.ON\.SIGNAL)\r'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'EDID\.TIMING\((OPS|HDMI\.[1-4]|DP|ALL) TYPE\):(4K60|4K30|1080P)\r'), self.__MatchEDID, None)
            self.AddMatchString(re.compile(b'EDID\.SELECTEDCONNECTOR:(OPS|HDMI\.[1-4]|DP|ALL)\r'), self.__MatchEDIDZone, None)
            self.AddMatchString(re.compile(b'SOURCE\.SELECT(?:\((ZONE\.[1-4]|ALL)\))?:(OPS|HDMI\.[1-4]|DP)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LAYOUT:(SINGLE|PIP\.U[RL]|PIP\.L[LR]|DUAL\.[TL]|TRIPLE\.[LRTBM]|QUAD)\r'), self.__MatchMultiSourceLayout, None)
            self.AddMatchString(re.compile(b'AUDIO\.MUTE:(ON|OFF)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PIP\.SIZE:(SMALL|MEDIUM|LARGE)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'SYSTEM\.STATE:(POWERING\.ON|POWERING\.DOWN|ON|BACKLIGHT\.OFF|STANDBY|FAULT)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'TOUCH\.CONTROL:(AUTO|EXTERNAL|OPS)\r'), self.__MatchTouchControl, None)
            self.AddMatchString(re.compile(b'AUDIO\.VOLUME:(\d{1,2}|100)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'CURRENT\.ZONE:(ZONE\.[1-4])\r'), self.__MatchZone, None)
            self.AddMatchString(re.compile(b'ERR \d\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):
        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4'
        }

        ValueStateValues = {
            'Auto': 'AUTO',
            '16:9': '16X9',
            '4:3': '4X3',
            'Fill': 'FILL',
            'Native': 'NATIVE',
            'Letterbox': 'LETTERBOX'
        }

        if ZoneStates[qualifier['Zone']] == '':
            AspectRatioCmdString = 'ASPECT={0}\r'.format(ValueStateValues[value])
        else:
            AspectRatioCmdString = 'ASPECT({1})={0}\r'.format(ValueStateValues[value], ZoneStates[qualifier['Zone']])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4'
        }

        if ZoneStates[qualifier['Zone']] == '':
            AspectRatioCmdString = 'ASPECT?\r'
        else:
            AspectRatioCmdString = 'ASPECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ZoneStates = {
            'ZONE.1': '1',
            'ZONE.2': '2',
            'ZONE.3': '3',
            'ZONE.4': '4'
        }

        ValueStateValues = {
            'AUTO': 'Auto',
            '16X9': '16:9',
            '4X3': '4:3',
            'FILL': 'Fill',
            'NATIVE': 'Native',
            'LETTERBOX': 'Letterbox'
        }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def UpdateAudioSourceStatus(self, value, qualifier):
        AudioSourceStatusCmdString = 'AUDIO.INPUT?\r'
        self.__UpdateHelper('AudioSourceStatus', AudioSourceStatusCmdString, value, qualifier)

    def __MatchAudioSourceStatus(self, match, tag):
        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'HDMI.3': 'HDMI 3',
            'HDMI.4': 'HDMI 4',
            'DP': 'DisplayPort'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioSourceStatus', value, None)

    def SetAudioZone(self, value, qualifier):
        ValueStateValues = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4'
        }

        AudioZoneCmdString = 'AUDIO.ZONE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioZone', AudioZoneCmdString, value, qualifier)

    def UpdateAudioZone(self, value, qualifier):
        AudioZoneCmdString = 'AUDIO.ZONE?\r'
        self.__UpdateHelper('AudioZone', AudioZoneCmdString, value, qualifier)

    def __MatchAudioZone(self, match, tag):
        ValueStateValues = {
            'ZONE.1': '1',
            'ZONE.2': '2',
            'ZONE.3': '3',
            'ZONE.4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioZone', value, None)

    def SetAutoPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AutoPowerCmdString = 'AUTO.ON={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoPower', AutoPowerCmdString, value, qualifier)

    def UpdateAutoPower(self, value, qualifier):
        AutoPowerCmdString = 'AUTO.ON?\r'
        self.__UpdateHelper('AutoPower', AutoPowerCmdString, value, qualifier)

    def __MatchAutoPower(self, match, tag):
        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoPower', value, None)

    def SetAutoSourceScan(self, value, qualifier):
        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AutoSourceScanCmdString = 'SOURCE.SCAN={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoSourceScan', AutoSourceScanCmdString, value, qualifier, 3)

    def UpdateAutoSourceScan(self, value, qualifier):
        AutoSourceScanCmdString = 'SOURCE.SCAN?\r'
        self.__UpdateHelper('AutoSourceScan', AutoSourceScanCmdString, value, qualifier)

    def __MatchAutoSourceScan(self, match, tag):
        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSourceScan', value, None)

    def UpdateCurrentZoneLayout(self, value, qualifier):
        CurrentZoneLayoutCmdString = 'CURRENT.ZONE.LAYOUT?\r'
        self.__UpdateHelper('CurrentZoneLayout', CurrentZoneLayoutCmdString, value, qualifier)

    def __MatchCurrentZoneLayout(self, match, tag):
        ValueStateValues = {
            'S.1': 'Single View',
            'P.UL.1': 'PIP, Upper Left in Zone 1',
            'P.UL.2': 'PIP, Upper Left in Zone 2',
            'P.UR.1': 'PIP, Upper Right in Zone 1',
            'P.UR.2': 'PIP, Upper Right in Zone 2',
            'P.LL.1': 'PIP, Lower Left in Zone 1',
            'P.LL.2': 'PIP, Lower Left in Zone 2',
            'P.LR.1': 'PIP, Lower Right in Zone 1',
            'P.LR.2': 'PIP, Lower Right in Zone 2',
            'D.L.1': 'Dual View, Left/Right in Zone 1',
            'D.L.2': 'Dual View, Left/Right in Zone 2',
            'D.T.1': 'Dual View, Top/Bottom in Zone 1',
            'D.T.2': 'Dual View, Top/Bottom in Zone 2',
            'T.L.1': 'Triple View, One Left/Two Right in Zone 1',
            'T.L.2': 'Triple View, One Left/Two Right in Zone 2',
            'T.L.3': 'Triple View, One Left/Two Right in Zone 3',
            'T.R.1': 'Triple View, Two Left/One Right in Zone 1',
            'T.R.2': 'Triple View, Two Left/One Right in Zone 2',
            'T.R.3': 'Triple View, Two Left/One Right in Zone 3',
            'T.T.1': 'Triple View, One Top/Two Bottom in Zone 1',
            'T.T.2': 'Triple View, One Top/Two Bottom in Zone 2',
            'T.T.3': 'Triple View, One Top/Two Bottom in Zone 3',
            'T.B.1': 'Triple View, Two Top/One Bottom in Zone 1',
            'T.B.2': 'Triple View, Two Top/One Bottom in Zone 2',
            'T.B.3': 'Triple View, Two Top/One Bottom in Zone 3',
            'T.M.1': 'Triple View, Side by Side in Zone 1',
            'T.M.2': 'Triple View, Side by Side in Zone 2',
            'T.M.3': 'Triple View, Side by Side in Zone 3',
            'Q.1': 'Quad View in Zone 1',
            'Q.2': 'Quad View in Zone 2',
            'Q.3': 'Quad View in Zone 3',
            'Q.4': 'Quad View in Zone 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CurrentZoneLayout', value, None)

    def SetEcoMode(self, value, qualifier):
        ValueStateValues = {
            'Off': 'DISABLED',
            'On': 'LOW.POWER',
            'Wake On Signal': 'WAKE.ON.SIGNAL'
        }

        EcoModeCmdString = 'POWER.SAVE.MODE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):
        EcoModeCmdString = 'POWER.SAVE.MODE?\r'
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):
        ValueStateValues = {
            'DISABLED': 'Off',
            'LOW.POWER': 'On',
            'WAKE.ON.SIGNAL': 'Wake On Signal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EcoMode', value, None)

    def SetEDID(self, value, qualifier):
        InputStates = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'HDMI 3': 'HDMI.3',
            'HDMI 4': 'HDMI.4',
            'DisplayPort': 'DP',
            'All': 'ALL'
        }

        ValueStateValues = {
            '4K60': '4K60',
            '4K30': '4K30',
            '1080p': '1080P'
        }

        EDIDCmdString = 'EDID.TIMING({0},TYPE)={1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('EDID', EDIDCmdString, value, qualifier, 3)

    def UpdateEDID(self, value, qualifier):
        InputStates = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'HDMI 3': 'HDMI.3',
            'HDMI 4': 'HDMI.4',
            'DisplayPort': 'DP',
            'All': 'ALL'
        }

        EDIDCmdString = 'EDID.TIMING({0},TYPE)?\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('EDID', EDIDCmdString, value, qualifier)

    def __MatchEDID(self, match, tag):
        InputStates = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'HDMI.3': 'HDMI 3',
            'HDMI.4': 'HDMI 4',
            'DP': 'DisplayPort',
            'ALL': 'All'
        }

        ValueStateValues = {
            '4K60': '4K60',
            '4K30': '4K30',
            '1080P': '1080p'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('EDID', value, qualifier)

    def SetEDIDZone(self, value, qualifier):
        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'HDMI 3': 'HDMI.3',
            'HDMI 4': 'HDMI.4',
            'DisplayPort': 'DP',
            'All': 'ALL'
        }

        EDIDZoneCmdString = 'EDID.SELECTEDCONNECTOR={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('EDIDZone', EDIDZoneCmdString, value, qualifier)

    def UpdateEDIDZone(self, value, qualifier):
        EDIDZoneCmdString = 'EDID.SELECTEDCONNECTOR?\r'
        self.__UpdateHelper('EDIDZone', EDIDZoneCmdString, value, qualifier)

    def __MatchEDIDZone(self, match, tag):
        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'HDMI.3': 'HDMI 3',
            'HDMI.4': 'HDMI 4',
            'DP': 'DisplayPort',
            'ALL': 'All'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EDIDZone', value, None)

    def SetInput(self, value, qualifier):
        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
        }

        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'HDMI 3': 'HDMI.3',
            'HDMI 4': 'HDMI.4',
            'DisplayPort': 'DP'
        }

        if ZoneStates[qualifier['Zone']] == '':
            InputCmdString = 'SOURCE.SELECT={0}\r'.format(ValueStateValues[value])
        else:
            InputCmdString = 'SOURCE.SELECT({1})={0}\r'.format(ValueStateValues[value], ZoneStates[qualifier['Zone']])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
        }

        if ZoneStates[qualifier['Zone']] == '':
            InputCmdString = 'SOURCE.SELECT?\r'
        else:
            InputCmdString = 'SOURCE.SELECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ZoneStates = {
            'ZONE.1': '1',
            'ZONE.2': '2',
            'ZONE.3': '3',
            'ZONE.4': '4',
            'ALL': 'All'
        }

        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'HDMI.3': 'HDMI 3',
            'HDMI.4': 'HDMI 4',
            'DP': 'DisplayPort'
        }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetKeypad(self, value, qualifier):
        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9'
        }

        KeypadCmdString = 'KEY=KEY.{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier, 3)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Enter': 'ENTER',
            'Exit': 'EXIT',
            'Back': 'PREV',
            'Menu': 'MENU',
            'Top': 'TOP'
        }

        MenuNavigationCmdString = 'KEY={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMultiSourceLayout(self, value, qualifier):
        ValueStateValues = {
            'Single': 'SINGLE',
            'PIP Upper Left': 'PIP.UL',
            'PIP Upper Right': 'PIP.UR',
            'PIP Lower Left': 'PIP.LL',
            'PIP Lower Right': 'PIP.LR',
            'Dual Top/Bottom': 'DUAL.T',
            'Dual Left/Right': 'DUAL.L',
            'Triple Left': 'TRIPLE.L',
            'Triple Right': 'TRIPLE.R',
            'Triple Top': 'TRIPLE.T',
            'Triple Bottom': 'TRIPLE.B',
            'Triple Middle': 'TRIPLE.M',
            'Quad': 'QUAD'
        }

        MultiSourceLayoutCmdString = 'LAYOUT={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MultiSourceLayout', MultiSourceLayoutCmdString, value, qualifier)

    def UpdateMultiSourceLayout(self, value, qualifier):
        MultiSourceLayoutCmdString = 'LAYOUT?\r'
        self.__UpdateHelper('MultiSourceLayout', MultiSourceLayoutCmdString, value, qualifier)

    def __MatchMultiSourceLayout(self, match, tag):
        ValueStateValues = {
            'SINGLE': 'Single',
            'PIP.UL': 'PIP Upper Left',
            'PIP.UR': 'PIP Upper Right',
            'PIP.LL': 'PIP Lower Left',
            'PIP.LR': 'PIP Lower Right',
            'DUAL.T': 'Dual Top/Bottom',
            'DUAL.L': 'Dual Left/Right',
            'TRIPLE.L': 'Triple Left',
            'TRIPLE.R': 'Triple Right',
            'TRIPLE.T': 'Triple Top',
            'TRIPLE.B': 'Triple Bottom',
            'TRIPLE.M': 'Triple Middle',
            'QUAD': 'Quad'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MultiSourceLayout', value, None)

    def SetMute(self, value, qualifier):
        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        MuteCmdString = 'AUDIO.MUTE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteCmdString = 'AUDIO.MUTE?\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):
        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPIPSize(self, value, qualifier):
        ValueStateValues = {
            'Small': 'SMALL',
            'Medium': 'MEDIUM',
            'Large': 'LARGE'
        }

        PIPSizeCmdString = 'PIP.SIZE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):
        PIPSizeCmdString = 'PIP.SIZE?\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):
        ValueStateValues = {
            'SMALL': 'Small',
            'MEDIUM': 'Medium',
            'LARGE': 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):
        PIPSwapCmdString = 'PIP.SWAP\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        PowerCmdString = 'DISPLAY.POWER={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = 'SYSTEM.STATE?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            'ON': 'On',
            'STANDBY': 'Off',
            'POWERING.ON': 'Powering Up',
            'POWERING.DOWN': 'Powering Down',
            'BACKLIGHT.OFF': 'Backlight Off',
            'FAULT': 'Fault'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):
        ActionStates = {
            'Delete': 'DELETE',
            'Save': 'SAVE',
            'Recall': 'RECALL'
        }

        ValueConstraints = {
            'Min': 1,
            'Max': 1000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetCmdString = 'PRESET.{0}({1})\r'.format(ActionStates[qualifier['Action']], value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetPreset')

    def SetReboot(self, value, qualifier):
        RebootCmdString = 'SYSTEM.REBOOT\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier, 5)

    def SetTouchControl(self, value, qualifier):
        ValueStateValues = {
            'OPS': 'OPS',
            'External': 'EXTERNAL',
            'Auto': 'AUTO'
        }

        TouchControlCmdString = 'TOUCH.CONTROL={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def UpdateTouchControl(self, value, qualifier):
        TouchControlCmdString = 'TOUCH.CONTROL?\r'
        self.__UpdateHelper('TouchControl', TouchControlCmdString, value, qualifier)

    def __MatchTouchControl(self, match, tag):
        ValueStateValues = {
            'OPS': 'OPS',
            'EXTERNAL': 'External',
            'AUTO': 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TouchControl', value, None)

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AUDIO.VOLUME={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'AUDIO.VOLUME?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetZone(self, value, qualifier):
        ValueStateValues = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4'
        }

        ZoneCmdString = 'CURRENT.ZONE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Zone', ZoneCmdString, value, qualifier)

    def UpdateZone(self, value, qualifier):
        ZoneCmdString = 'CURRENT.ZONE?\r'
        self.__UpdateHelper('Zone', ZoneCmdString, value, qualifier)

    def __MatchZone(self, match, tag):
        ValueStateValues = {
            'ZONE.1': '1',
            'ZONE.2': '2',
            'ZONE.3': '3',
            'ZONE.4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
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


    def __MatchError(self, match, tag):
        ERR_List = {
            '1': 'Invalid syntax',
            '2': 'Error Occured',
            '3': 'Command not recognized',
            '4': 'Invalid modifier',
            '5': 'Invalid operands',
            '6': 'Invalid operator'
        }
        match_value = ERR_List[match.group(1).decode()]
        value = 'ERR {0}: {1}'.format(match.group(1).decode(), match_value)
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        
################################################################
# HELPER METHODS SECTION
################################################################

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
