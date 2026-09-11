# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Zone'], 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AudioSourceStatus': { 'Status': {}},
            'AudioZone': { 'Status': {}},
            'AutoPower': { 'Status': {}},
            'AutoSourceScan': { 'Status': {}},
            'CurrentZoneLayout': { 'Status': {}},
            'EcoMode': { 'Status': {}},
            'EDID': {'Parameters':['Input'], 'Status': {}},
            'EDIDZone': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Input': {'Parameters':['Zone'], 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MultiSourceLayout': { 'Status': {}},
            'Overscan': {'Parameters':['Zone'], 'Status': {}},
            'PIPSize': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zone': { 'Status': {}}
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT(?:\((ZONE\.[1-4])\))?:(AUTO|16X9|4X3|FILL|NATIVE|LETTERBOX)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AUDIO\.MUTE:(ON|OFF)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'AUDIO\.INPUT:(USBC|HDMI\.[1-2]|DP\.[1-2])\r'), self.__MatchAudioSourceStatus, None)
            self.AddMatchString(re.compile(b'AUDIO\.ZONE:(ZONE\.[1-4])\r'), self.__MatchAudioZone, None)
            self.AddMatchString(re.compile(b'AUTO\.ON:(ON|OFF)\r'), self.__MatchAutoPower, None)
            self.AddMatchString(re.compile(b'SOURCE\.SCAN:(ON|OFF)\r'), self.__MatchAutoSourceScan, None)
            self.AddMatchString(re.compile(b'CURRENT\.ZONE\.LAYOUT:(S\.1|P\.[UL][RL]\.[12]|D\.L\.[12]||Q\.[1-4])\r'), self.__MatchCurrentZoneLayout, None)
            self.AddMatchString(re.compile(b'POWER\.SAVE\.MODE:(DISABLED|LOW\.POWER|WAKE\.ON\.SIGNAL)\r'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'EDID\.TIMING\((USBC|HDMI\.[1-2]|DP\.[1-2]) TYPE\):(4K60|4K30|1080P)\r'), self.__MatchEDID, None)
            self.AddMatchString(re.compile(b'EDID\.SELECTEDCONNECTOR:(USBC|HDMI\.[1-2]|DP\.[1-2])\r'), self.__MatchEDIDZone, None)
            self.AddMatchString(re.compile(b'BUILD\.INFO:(.*)\r'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'SOURCE\.SELECT(?:\((ZONE\.[1-4]|ALL)\))?:(USBC|HDMI\.[1-2]|DP\.[1-2])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LAYOUT:(SINGLE|PIP\.U[RL]|PIP\.L[LR]|DUAL\.L|QUAD)\r'), self.__MatchMultiSourceLayout, None)
            self.AddMatchString(re.compile(b'OVERSCAN(?:\((ZONE\.[1-4])\))?:(0|[1-9]|1\d|20)\r'), self.__MatchOverscan, None)
            self.AddMatchString(re.compile(b'PIP\.SIZE:(SMALL|MEDIUM|LARGE)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'SYSTEM\.STATE:(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SERIAL\.NUMBER=(.*)\r'), self.__MatchSerialNumber, None)
            self.AddMatchString(re.compile(b'AUDIO\.VOLUME:(\d{1,2}|100)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'CURRENT\.ZONE:(ZONE\.[1-4])\r'), self.__MatchZone, None)
            self.AddMatchString(re.compile(b'ERR ([1-6])\r'), self.__MatchError, None)

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

        if qualifier['Zone'] in ZoneStates and value in ValueStateValues:
            if ZoneStates[qualifier['Zone']] == '':
                AspectRatioCmdString = 'ASPECT={0}\r'.format(ValueStateValues[value])
            else:
                AspectRatioCmdString = 'ASPECT({1})={0}\r'.format(ValueStateValues[value], ZoneStates[qualifier['Zone']])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4'
            }

        if qualifier['Zone'] in ZoneStates:
            if ZoneStates[qualifier['Zone']] == '':
                AspectRatioCmdString = 'ASPECT?\r'
            else:
                AspectRatioCmdString = 'ASPECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ZoneStates = {
            'ZONE.1' : '1', 
            'ZONE.2' : '2', 
            'ZONE.3' : '3', 
            'ZONE.4' : '4'
        }

        ValueStateValues = {
            'AUTO' : 'Auto', 
            '16X9' : '16:9', 
            '4X3' : '4:3', 
            'FILL' : 'Fill', 
            'NATIVE' : 'Native', 
            'LETTERBOX' : 'Letterbox'
        }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
            }

        if value in ValueStateValues:
            AudioMuteCmdString = 'AUDIO.MUTE={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'AUDIO.MUTE?\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateAudioSourceStatus(self, value, qualifier):

        AudioSourceStatusCmdString = 'AUDIO.INPUT?\r'
        self.__UpdateHelper('AudioSourceStatus', AudioSourceStatusCmdString, value, qualifier)

    def __MatchAudioSourceStatus(self, match, tag):

        ValueStateValues = {
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'DP': 'DisplayPort',
            'DP.2': 'DisplayPort 2',
            'USBC': 'USB-C'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioSourceStatus', value, None)

    def SetAudioZone(self, value, qualifier):

        ValueStateValues = {
            '1' : 'ZONE.1', 
            '2' : 'ZONE.2', 
            '3' : 'ZONE.3', 
            '4' : 'ZONE.4'
        }

        if value in ValueStateValues:
            AudioZoneCmdString = 'AUDIO.ZONE={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioZone', AudioZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioZone')

    def UpdateAudioZone(self, value, qualifier):

        AudioZoneCmdString = 'AUDIO.ZONE?\r'
        self.__UpdateHelper('AudioZone', AudioZoneCmdString, value, qualifier)

    def __MatchAudioZone(self, match, tag):

        ValueStateValues = {
            'ZONE.1' : '1', 
            'ZONE.2' : '2', 
            'ZONE.3' : '3', 
            'ZONE.4' : '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioZone', value, None)

    def SetAutoPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off' : 'OFF'
        }

        if value in ValueStateValues:
            AutoPowerCmdString = 'AUTO.ON={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoPower', AutoPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoPower')

    def UpdateAutoPower(self, value, qualifier):

        AutoPowerCmdString = 'AUTO.ON?\r'
        self.__UpdateHelper('AutoPower', AutoPowerCmdString, value, qualifier)

    def __MatchAutoPower(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoPower', value, None)

    def SetAutoSourceScan(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off' : 'OFF'
        }

        if value in ValueStateValues:
            AutoSourceScanCmdString = 'SOURCE.SCAN={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSourceScan', AutoSourceScanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSourceScan')

    def UpdateAutoSourceScan(self, value, qualifier):

        AutoSourceScanCmdString = 'SOURCE.SCAN?\r'
        self.__UpdateHelper('AutoSourceScan', AutoSourceScanCmdString, value, qualifier)

    def __MatchAutoSourceScan(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
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
            'Q.1': 'Quad View in Zone 1',
            'Q.2': 'Quad View in Zone 2',
            'Q.3': 'Quad View in Zone 3',
            'Q.4': 'Quad View in Zone 4'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CurrentZoneLayout', value, None)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Off' : 'DISABLED', 
            'On' : 'LOW.POWER', 
            'Wake On Signal' : 'WAKE.ON.SIGNAL'
        }

        if value in ValueStateValues:
            EcoModeCmdString = 'POWER.SAVE.MODE={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEcoMode')

    def UpdateEcoMode(self, value, qualifier):

        EcoModeCmdString = 'POWER.SAVE.MODE?\r'
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):

        ValueStateValues = {
            'DISABLED' : 'Off', 
            'LOW.POWER' : 'On', 
            'WAKE.ON.SIGNAL' : 'Wake On Signal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EcoMode', value, None)

    def SetEDID(self, value, qualifier):

        InputStates = {
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'DisplayPort': 'DP',
            'DisplayPort 2': 'DP.2',
            'USB-C': 'USBC'
            }

        ValueStateValues = {
            '4K60' : '4K60', 
            '4K30' : '4K30', 
            '1080p' : '1080P'
        }

        if qualifier['Input'] in InputStates and value in ValueStateValues:
            EDIDCmdString = 'EDID.TIMING({0},TYPE)={1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('EDID', EDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEDID')

    def UpdateEDID(self, value, qualifier):

        InputStates = {
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'DisplayPort': 'DP',
            'DisplayPort 2': 'DP.2',
            'USB-C': 'USBC'
            }

        if qualifier['Input'] in InputStates:
            EDIDCmdString = 'EDID.TIMING({0},TYPE)?\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('EDID', EDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDID')

    def __MatchEDID(self, match, tag):

        InputStates = {
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'DP': 'DisplayPort',
            'DP.2': 'DisplayPort 2',
            'USBC': 'USB-C'
            }

        ValueStateValues = {
            '4K60' : '4K60', 
            '4K30' : '4K30', 
            '1080P' : '1080p'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('EDID', value, qualifier)

    def SetEDIDZone(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'DisplayPort': 'DP',
            'DisplayPort 2': 'DP.2',
            'USB-C': 'USBC'
            }

        if value in ValueStateValues:
            EDIDZoneCmdString = 'EDID.SELECTEDCONNECTOR={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('EDIDZone', EDIDZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEDIDZone')

    def UpdateEDIDZone(self, value, qualifier):

        EDIDZoneCmdString = 'EDID.SELECTEDCONNECTOR?\r'
        self.__UpdateHelper('EDIDZone', EDIDZoneCmdString, value, qualifier)

    def __MatchEDIDZone(self, match, tag):

        ValueStateValues = {
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'DP': 'DisplayPort',
            'DP.2': 'DisplayPort 2',
            'USBC': 'USB-C'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EDIDZone', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'BUILD.INFO?\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode().strip('"')
        self.WriteStatus('FirmwareVersion', value, None)

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
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'DisplayPort': 'DP',
            'DisplayPort 2': 'DP.2',
            'USB-C': 'USBC'
            }

        if qualifier['Zone'] in ZoneStates and value in ValueStateValues:
            if ZoneStates[qualifier['Zone']] == '':
                InputCmdString = 'SOURCE.SELECT={0}\r'.format(ValueStateValues[value])
            else:
                InputCmdString = 'SOURCE.SELECT({1})={0}\r'.format(ValueStateValues[value], ZoneStates[qualifier['Zone']])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
            }

        if qualifier['Zone'] in ZoneStates:
            if ZoneStates[qualifier['Zone']] == '':
                InputCmdString = 'SOURCE.SELECT?\r'
            else:
                InputCmdString = 'SOURCE.SELECT({0})?\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ZoneStates = { 
            'ZONE.1' : '1', 
            'ZONE.2' : '2', 
            'ZONE.3' : '3', 
            'ZONE.4' : '4', 
            'ALL' : 'All'
        }

        ValueStateValues = {
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'DP': 'DisplayPort',
            'DP.2': 'DisplayPort 2',
            'USBC': 'USB-C'
            }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = 'KEY=KEY.{0}\r'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up' : 'UP', 
            'Down' : 'DOWN', 
            'Left' : 'LEFT', 
            'Right' : 'RIGHT', 
            'Enter' : 'ENTER', 
            'Exit' : 'EXIT', 
            'Back' : 'PREV', 
            'Menu' : 'MENU', 
            'Top' : 'TOP'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'KEY={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMultiSourceLayout(self, value, qualifier):

        ValueStateValues = {
            'Single': 'SINGLE',
            'PIP Upper Left': 'PIP.UL',
            'PIP Upper Right': 'PIP.UR',
            'PIP Lower Left': 'PIP.LL',
            'PIP Lower Right': 'PIP.LR',
            'Dual Left/Right': 'DUAL.L',
            'Quad': 'QUAD'
            }

        if value in ValueStateValues:
            MultiSourceLayoutCmdString = 'LAYOUT={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MultiSourceLayout', MultiSourceLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiSourceLayout')

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
            'DUAL.L': 'Dual Left/Right',
            'QUAD': 'Quad'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MultiSourceLayout', value, None)

    def SetOverscan(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
            }

        if qualifier['Zone'] in ZoneStates and 0 <= value <= 20:
            if ZoneStates[qualifier['Zone']] == '':
                OverscanCmdString = 'OVERSCAN={0}\r'.format(value)
            else:
                OverscanCmdString = 'OVERSCAN({1})={0}\r'.format(value, ZoneStates[qualifier['Zone']])
            self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverscan')

    def UpdateOverscan(self, value, qualifier):

        ZoneStates = {
            'Current': '',
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            '3': 'ZONE.3',
            '4': 'ZONE.4',
            'All': 'ALL'
            }

        if qualifier['Zone'] in ZoneStates:
            if ZoneStates[qualifier['Zone']] == '':
                OverscanCmdString = 'OVERSCAN?\r'
            else:
                OverscanCmdString = 'OVERSCAN({0})?\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOverscan')

    def __MatchOverscan(self, match, tag):

        ZoneStates = {
            'ZONE.1' : '1', 
            'ZONE.2' : '2', 
            'ZONE.3' : '3', 
            'ZONE.4' : '4'
            }

        qualifier = {}
        if match.group(1):
            qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        else:
            qualifier['Zone'] = 'Current'
        value = int(match.group(2).decode())
        if 0 <= value <= 20:
            self.WriteStatus('Overscan', value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small' : 'SMALL', 
            'Medium' : 'MEDIUM', 
            'Large' : 'LARGE'
        }

        if value in ValueStateValues:
            PIPSizeCmdString = 'PIP.SIZE={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'PIP.SIZE?\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            'SMALL' : 'Small', 
            'MEDIUM' : 'Medium', 
            'LARGE' : 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'PIP.SWAP\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON', 
            'Off' : 'OFF', 
        }

        if value in ValueStateValues:
            PowerCmdString = 'DISPLAY.POWER={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'SYSTEM.STATE?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'STANDBY' : 'Off', 
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 10:
            PresetRecallCmdString = 'PRESET.RECALL({0})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 10:
            PresetSaveCmdString = 'PRESET.SAVE({0})\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = 'SERIAL.NUMBER?\r'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = match.group(1).decode().strip('"')
        self.WriteStatus('SerialNumber', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'AUDIO.VOLUME={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'AUDIO.VOLUME?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

    def SetZone(self, value, qualifier):

        ValueStateValues = {
            '1' : 'ZONE.1', 
            '2' : 'ZONE.2', 
            '3' : 'ZONE.3', 
            '4' : 'ZONE.4'
        }

        if value in ValueStateValues:
            ZoneCmdString = 'CURRENT.ZONE={0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Zone', ZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone')

    def UpdateZone(self, value, qualifier):

        ZoneCmdString = 'CURRENT.ZONE?\r'
        self.__UpdateHelper('Zone', ZoneCmdString, value, qualifier)

    def __MatchZone(self, match, tag):

        ValueStateValues = {
            'ZONE.1' : '1', 
            'ZONE.2' : '2', 
            'ZONE.3' : '3', 
            'ZONE.4' : '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone', value, None)

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

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            '1' : 'Invalid syntax',
            '2' : 'Unknown error occurred',
            '3' : 'Command not recognized',
            '4' : 'Invalid modifier',
            '5' : 'Invalid operands',
            '6' : 'Invalid operator'
        }

        self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()