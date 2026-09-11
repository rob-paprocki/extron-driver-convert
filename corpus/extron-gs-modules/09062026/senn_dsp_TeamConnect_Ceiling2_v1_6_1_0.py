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
            'AudioLevel': { 'Status': {}},
            'Azimuth': { 'Status': {}},
            'BeamOffset': { 'Status': {}},
            'BeamVisual': { 'Status': {}},
            'CustomLEDMode': { 'Status': {}},
            'DanteOutputGain': { 'Status': {}},
            'DeviceButtonDescription': { 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'DeviceSerialNumber': { 'Status': {}},
            'Elevation': { 'Status': {}},
            'EqualizerGainCommand': {'Parameters':['Band 1','Band 2','Band 3','Band 4','Band 5','Band 6','Band 7'], 'Status': {}},
            'EqualizerGainStatus': { 'Status': {}},
            'ExclusionCommand': {'Parameters':['Zone 1','Zone 2','Zone 3','Zone 4','Zone 5'], 'Status': {}},
            'ExclusionStatus': {'Parameters':['Zone'], 'Status': {}},
            'Firmware': { 'Status': {}},
            'FirmwareUpdate': { 'Status': {}},
            'FirmwareUpdateErrorStatus': { 'Status': {}},
            'FirmwareUpdateStatus': { 'Status': {}},
            'Identify': { 'Status': {}},
            'InstallationType': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDSettings': {'Parameters':['Mode'], 'Status': {}},
            'Mute': { 'Status': {}},
            'NoiseGate': { 'Status': {}},
            'OSCStatus': {'Parameters':['Type'], 'Status': {}},
            'OutputLevel': { 'Status': {}},
            'Priority': { 'Status': {}},
            'ResetButtonStatus': { 'Status': {}},
            'ResetLabelStatus': { 'Status': {}},
            'Restart': { 'Status': {}},
            'RoomNoiseLevel': { 'Status': {}},
            'SoundProfile': { 'Status': {}},
            'VoiceLift': { 'Status': {}},
            'ZoneAzimuthCommand': {'Parameters':['Number','Min','Max'], 'Status': {}},
            'ZoneAzimuthStatus': {'Parameters':['Number'], 'Status': {}},
            'ZoneElevationCommand': {'Parameters':['Min','Max'], 'Status': {}},
            'ZoneElevationStatus': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"m":{"in1":{"peak":(-?\d{1,2})}}}'), self.__MatchAudioLevel, None)
            self.AddMatchString(re.compile(b'{"m":{"beam":{"azimuth":(\d{1,3})}}}'), self.__MatchAzimuth, None)
            self.AddMatchString(re.compile(b'{"beam":{"orientation":{"offset":(0|90|180|270)}}}'), self.__MatchBeamOffset, None)
            self.AddMatchString(re.compile(b'{"beam":{"orientation":{"visual":(true|false)}}}'), self.__MatchBeamVisual, None)
            self.AddMatchString(re.compile(b'{"device":{"led":{"custom":{"active":(true|false)}}}}'), self.__MatchCustomLEDMode, None)
            self.AddMatchString(re.compile(b'{"audio":{"out2":{"gain":(\d{1,2})}}}'), self.__MatchDanteOutputGain, None)
            self.AddMatchString(re.compile(b'{"device":{"button":{"description":"([\S ]+)"}}}'), self.__MatchDeviceButtonDescription, None)
            self.AddMatchString(re.compile(b'{"device":{"location":"([\S ]{1,100})"}}'), self.__MatchDeviceLocation, None)
            self.AddMatchString(re.compile(b'{"device":{"name":"([\S ]{1,8})"}}'), self.__MatchDeviceName, None)
            self.AddMatchString(re.compile(b'{"device":{"identity":{"serial":"([\S ]+)"}}}'), self.__MatchDeviceSerialNumber, None)
            self.AddMatchString(re.compile(b'{"m":{"beam":{"elevation":(\d{1,2})}}}'), self.__MatchElevation, None)
            self.AddMatchString(re.compile(b'{"audio":{"equalizer":{"custom":(\[[0-8-.,]+])}}}'), self.__MatchEqualizerGainStatus, None)
            self.AddMatchString(re.compile(b'{"audio":{"exclusion":{"active":\[(true|false),(true|false),(true|false),(true|false),(true|false)]}}}'), self.__MatchExclusionStatus, None)
            self.AddMatchString(re.compile(b'{"device":{"identity":{"version":"([\d.]+)"}}}'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'{"device":{"update":{"enable":(true|false)}}}'), self.__MatchFirmwareUpdate, None)
            self.AddMatchString(re.compile(b'{"device":{"update":{"error":"([\S ]+)"}}}'), self.__MatchFirmwareUpdateErrorStatus, None)
            self.AddMatchString(re.compile(b'{"device":{"update":{"progress":(\d{1,2}|100)}}}'), self.__MatchFirmwareUpdateStatus, None)
            self.AddMatchString(re.compile(b'{"audio":{"installation_type":"(suspended|flush_mount)"}}'), self.__MatchInstallationType, None)
            self.AddMatchString(re.compile(b'{"device":{"led":{"brightness":([0-5])}}}'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'{"device":{"led":{"(mic_mute|mic_on|custom)":{"color":"(LIGHT GREEN|GREEN|BLUE|RED|YELLOW|ORANGE|CYAN|PINK)"}}}}'), self.__MatchLEDSettings, None)
            self.AddMatchString(re.compile(b'{"audio":{"mute":(true|false)}}'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'{"audio":{"noise_gate":{"active":(true|false)}}}'), self.__MatchNoiseGate, None)
            self.AddMatchString(re.compile(b'{"osc":{"state":{"(auth)":{"access":([\S ]+)}}}}'), self.__MatchOSCStatus, None)
            self.AddMatchString(re.compile(b'{"osc":{"(limits|schema|version|xid|ping)":([\S ]+)}}'), self.__MatchOSCStatus, None)
            self.AddMatchString(re.compile(b'{"osc":{"(?:state|feature)":{"(prettyprint|close|subscribe|timetag|baseaddr|subscription|pattern)":([\S ]+)}}}\r?\n?'), self.__MatchOSCStatus, None)
            self.AddMatchString(re.compile(b'{"audio":{"out1":{"attenuation":(-?\d{1,2})}}}'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'{"audio":{"priority":{"active":\[(true|false)]}}}'), self.__MatchPriority, None)
            self.AddMatchString(re.compile(b'{"device":{"button":{"state":(true|false)}}}'), self.__MatchResetButtonStatus, None)
            self.AddMatchString(re.compile(b'{"device":{"button":{"label":"([\S ]+)"}}}'), self.__MatchResetLabelStatus, None)
            self.AddMatchString(re.compile(b'{"audio":{"source_detection":{"threshold":"(quiet|normal|loud)_room"}}}'), self.__MatchRoomNoiseLevel, None)
            self.AddMatchString(re.compile(b'{"audio":{"equalizer":{"preset":"(OFF|CUSTOM)"}}}'), self.__MatchSoundProfile, None)
            self.AddMatchString(re.compile(b'{"audio":{"voice_lift":{"active":(true|false)}}}'), self.__MatchVoiceLift, None)
            self.AddMatchString(re.compile(b'{"audio":{"exclusion_zone":{"azimuth":{"([1-3])":(\[\d+,\d+\])}}}}'), self.__MatchZoneAzimuthStatus, None)
            self.AddMatchString(re.compile(b'{"audio":{"exclusion_zone":{"elevation":{"1":(\[\d+,\d+\])}}}}'), self.__MatchZoneElevationStatus, None)
            self.AddMatchString(re.compile(b'{"osc":{"error":\[([1-5][0125][0-9]),{"desc":"([\S ]+)"}]}}'), self.__MatchError, None)

    def UpdateAudioLevel(self, value, qualifier):

        AudioLevelCmdString = '{"osc":{"state":{"subscribe":[{"m":{"in1":{"peak":null}}}]}}}\r'
        self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)

    def __MatchAudioLevel(self, match, tag):

        value = int(match.group(1).decode())
        if -90 <= value <= 0:
            self.WriteStatus('AudioLevel', value, None)

    def UpdateAzimuth(self, value, qualifier):

        AzimuthCmdString = '{"osc":{"state":{"subscribe":[{"m":{"beam":{"azimuth":null}}}]}}}\r'
        self.__UpdateHelper('Azimuth', AzimuthCmdString, value, qualifier)

    def __MatchAzimuth(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 359:
            self.WriteStatus('Azimuth', value, None)

    def SetBeamOffset(self, value, qualifier):

        ValueStateValues = {
            '0'   : '0', 
            '90'  : '90', 
            '180' : '180', 
            '270' : '270'
        }

        BeamOffsetCmdString = ''.join(['{"beam":{"orientation":{"offset":', ValueStateValues[value], '}}}\r'])
        self.__SetHelper('BeamOffset', BeamOffsetCmdString, value, qualifier)

    def UpdateBeamOffset(self, value, qualifier):

        BeamOffsetCmdString = '{"osc":{"state":{"subscribe":[{"beam":{"orientation":{"offset":null}}}]}}}\r'
        self.__UpdateHelper('BeamOffset', BeamOffsetCmdString, value, qualifier)

    def __MatchBeamOffset(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('BeamOffset', value, None)

    def SetBeamVisual(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'true',
            'Off' : 'false'
        }

        BeamVisualCmdString = ''.join(['{"beam":{"orientation":{"visual":', ValueStateValues[value], '}}}\r'])
        self.__SetHelper('BeamVisual', BeamVisualCmdString, value, qualifier)

    def UpdateBeamVisual(self, value, qualifier):

        BeamVisualCmdString = '{"osc":{"state":{"subscribe":[{"beam":{"orientation":{"visual":null}}}]}}}\r'
        self.__UpdateHelper('BeamVisual', BeamVisualCmdString, value, qualifier)

    def __MatchBeamVisual(self, match, tag):

        ValueStateValues = {
            'true'  : 'On', 
            'false' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BeamVisual', value, None)

    def SetCustomLEDMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'true',
            'Off' : 'false'
        }

        if value in ValueStateValues:
            CustomLEDModeCmdString = ''.join(['{"device":{"led":{"custom":{"active":', ValueStateValues[value], '}}}}\r'])
            self.__SetHelper('CustomLEDMode', CustomLEDModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCustomLEDMode')

    def UpdateCustomLEDMode(self, value, qualifier):

        CustomLEDModeCmdString = '{"osc":{"state":{"subscribe":[ {"device":{"led":{"custom":{"active":null}}}}]}}}\r'
        self.__UpdateHelper('CustomLEDMode', CustomLEDModeCmdString, value, qualifier)

    def __MatchCustomLEDMode(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CustomLEDMode', value, None)

    def SetDanteOutputGain(self, value, qualifier):

        if 0 <= value <= 24:
            DanteOutputGainCmdString = ''.join(['{"audio":{"out2":{"gain":', str(value),'}}}\r'])
            self.__SetHelper('DanteOutputGain', DanteOutputGainCmdString, value, qualifier) #Query delay not needed, tested with device
        else:
            self.Discard('Invalid Command for SetDanteOutputGain')

    def UpdateDanteOutputGain(self, value, qualifier):

        DanteOutputGainCmdString = '{"osc":{"state":{"subscribe":[ {"audio":{"out2":{"gain":null}}}]}}}\r'
        self.__UpdateHelper('DanteOutputGain', DanteOutputGainCmdString, value, qualifier)

    def __MatchDanteOutputGain(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('DanteOutputGain', value, None)

    def UpdateDeviceButtonDescription(self, value, qualifier):

        DeviceButtonDescriptionCmdString = '{"device":{"button":{"description":null}}}\r'
        self.__UpdateHelper('DeviceButtonDescription', DeviceButtonDescriptionCmdString, value, qualifier)

    def __MatchDeviceButtonDescription(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceButtonDescription', value, None)

    def UpdateDeviceLocation(self, value, qualifier):

        DeviceLocationCmdString = '{"osc":{"state":{"subscribe":[ {"device":{"location":null}}]}}}\r'
        self.__UpdateHelper('DeviceLocation', DeviceLocationCmdString, value, qualifier)

    def __MatchDeviceLocation(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceLocation', value, None)

    def UpdateDeviceName(self, value, qualifier):

        DeviceNameCmdString = '{"osc":{"state":{"subscribe":[ {"device":{"name":null}}]}}}\r'
        self.__UpdateHelper('DeviceName', DeviceNameCmdString, value, qualifier)

    def __MatchDeviceName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceName', value, None)

    def UpdateDeviceSerialNumber(self, value, qualifier):

        DeviceSerialNumberCmdString = '{"device":{"identity":{"serial":null}}}\r'
        self.__UpdateHelper('DeviceSerialNumber', DeviceSerialNumberCmdString, value, qualifier)

    def __MatchDeviceSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceSerialNumber', value, None)

    def UpdateElevation(self, value, qualifier):

        ElevationCmdString = '{"osc":{"state":{"subscribe":[{"m":{"beam":{"elevation":null}}}]}}}\r'
        self.__UpdateHelper('Elevation', ElevationCmdString, value, qualifier)

    def __MatchElevation(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 90:
            self.WriteStatus('Elevation', value, None)

    def SetEqualizerGainCommand(self, value, qualifier):

        if -8 <= qualifier['Band 1'] <= 8 and -8 <= qualifier['Band 2'] <= 8 and -8 <= qualifier['Band 3'] <= 8 \
                and -8 <= qualifier['Band 4'] <= 8 and -8 <= qualifier['Band 5'] <= 8 and -8 <= qualifier['Band 6'] <= 8 \
                and -8 <= qualifier['Band 7'] <= 8:
            
            band_val = '[{0},{1},{2},{3},{4},{5},{6}]'.format(qualifier['Band 1'], qualifier['Band 2'], qualifier['Band 3'],
                                                              qualifier['Band 4'], qualifier['Band 5'], qualifier['Band 6'],
                                                              qualifier['Band 7'])
            EqualizerGainCommandCmdString = ''.join(['{"audio":{"equalizer":{"custom":', band_val, '}}}\r'])
            self.__SetHelper('EqualizerGainCommand', EqualizerGainCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEqualizerGainCommand')

    def UpdateEqualizerGainStatus(self, value, qualifier):

        EqualizerGainStatusCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"equalizer":{"custom":null}}}]}}}\r'
        self.__UpdateHelper('EqualizerGainStatus', EqualizerGainStatusCmdString, value, qualifier)

    def __MatchEqualizerGainStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('EqualizerGainStatus', value, None)

    def SetExclusionCommand(self, value, qualifier):

        ZoneStates = {
            'Activate'   : 'true',
            'Deactivate' : 'false'
        }

        if qualifier['Zone 1'] in ZoneStates and qualifier['Zone 2'] in ZoneStates and qualifier['Zone 3'] in ZoneStates and \
                qualifier['Zone 4'] in ZoneStates and qualifier['Zone 5'] in ZoneStates:
            zoneVariable = '{0},{1},{2},{3},{4}'.format(ZoneStates[qualifier['Zone 1']], ZoneStates[qualifier['Zone 2']], ZoneStates[qualifier['Zone 3']], ZoneStates[qualifier['Zone 4']], ZoneStates[qualifier['Zone 5']])
            ExclusionCommandCmdString = ''.join(['{"audio":{"exclusion":{"active":[', zoneVariable,']}}}\r'])
            self.__SetHelper('ExclusionCommand', ExclusionCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExclusionCommand')

    def UpdateExclusionStatus(self, value, qualifier):

        if qualifier['Zone'] in ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']:
            ExclusionStatusCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"exclusion":{"active":null}}}]}}}\r'
            self.__UpdateHelper('ExclusionStatus', ExclusionStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExclusionStatus')

    def __MatchExclusionStatus(self, match, tag):

        ValueStateValues = {
            'true'  : 'Activated',
            'false' : 'Deactivated'
        }

        for zone in range(1, 6):
            if match.group(zone):
                qualifier = {'Zone' : 'Zone {}'.format(str(zone))}
                value = ValueStateValues[match.group(zone).decode()]
                self.WriteStatus('ExclusionStatus', value, qualifier)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = '{"device":{"identity":{"version":null}}}\r'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetFirmwareUpdate(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'true', 
            'Disable' : 'false'
        }

        FirmwareUpdateCmdString = ''.join(['{"device":{"update":{"enable":', ValueStateValues[value], '}}}\r'])
        self.__SetHelper('FirmwareUpdate', FirmwareUpdateCmdString, value, qualifier)

    def UpdateFirmwareUpdate(self, value, qualifier):

        FirmwareUpdateCmdString = '{"osc":{"state":{"subscribe":[{"device":{"update":{"enable":null}}}]}}}\r'
        self.__UpdateHelper('FirmwareUpdate', FirmwareUpdateCmdString, value, qualifier)

    def __MatchFirmwareUpdate(self, match, tag):

        ValueStateValues = {
            'true' : 'Enable', 
            'false' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FirmwareUpdate', value, None)

    def UpdateFirmwareUpdateErrorStatus(self, value, qualifier):

        FirmwareUpdateErrorStatusCmdString = '{"device":{"update":{"error":null}}}\r'
        self.__UpdateHelper('FirmwareUpdateErrorStatus', FirmwareUpdateErrorStatusCmdString, value, qualifier)

    def __MatchFirmwareUpdateErrorStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareUpdateErrorStatus', value, None)

    def UpdateFirmwareUpdateStatus(self, value, qualifier):

        FirmwareUpdateStatusCmdString = '{"device":{"update":{"progress":null}}}\r'
        self.__UpdateHelper('FirmwareUpdateStatus', FirmwareUpdateStatusCmdString, value, qualifier)

    def __MatchFirmwareUpdateStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('FirmwareUpdateStatus', value, None)

    def SetIdentify(self, value, qualifier):

        IdentifyCmdString = '{"device":{"identification":{"visual":true}}}\r'
        self.__SetHelper('Identify', IdentifyCmdString, value, qualifier)
        
    def SetInstallationType(self, value, qualifier):

        ValueStateValues = {
            'Flush Mount'       : 'flush_mount',
            'Suspended Mount'   : 'suspended'
        }

        if value in ValueStateValues:
            InstallationTypeCmdString = ''.join(['{"audio":{"installation_type":"', ValueStateValues[value], '"}}\r'])
            self.__SetHelper('InstallationType', InstallationTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInstallationType')

    def UpdateInstallationType(self, value, qualifier):

        InstallationTypeCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"installation_type":null}}]}}}\r'
        self.__UpdateHelper('InstallationType', InstallationTypeCmdString, value, qualifier)

    def __MatchInstallationType(self, match, tag):

        ValueStateValues = {
            'flush_mount'   : 'Flush Mount',
            'suspended'     : 'Suspended Mount'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InstallationType', value, None)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Off'   : '0',
            '1'     : '1',
            '2'     : '2',
            '3'     : '3',
            '4'     : '4',
            '5'     : '5'
        }

        if value in ValueStateValues:
            LEDBrightnessCmdString = ''.join(['{"device":{"led":{"brightness":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = '{"osc":{"state":{"subscribe":[{"device":{"led":{"brightness":null}}}]}}}\r'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LEDBrightness', value, None)

    def SetLEDSettings(self, value, qualifier):

        ModeStates = {
            'Mic On'    : 'mic_on',
            'Mic Mute'  : 'mic_mute',
            'Custom'    : 'custom'
        }

        ValueStateValues = {
            'Light Green'   : 'LIGHT GREEN',
            'Green'         : 'GREEN',
            'Blue'          : 'BLUE',
            'Red'           : 'RED',
            'Yellow'        : 'YELLOW',
            'Orange'        : 'ORANGE',
            'Cyan'          : 'CYAN',
            'Pink'          : 'PINK'
        }

        if qualifier['Mode'] in ModeStates and value in ValueStateValues:
            LEDSettingsCmdString = ''.join(['{"device":{"led":{"', ModeStates[qualifier['Mode']],'":{"color":"', ValueStateValues[value], '"}}}}\r'])
            self.__SetHelper('LEDSettings', LEDSettingsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDSettings')

    def UpdateLEDSettings(self, value, qualifier):

        ModeStates = {
            'Mic On': 'mic_on',
            'Mic Mute': 'mic_mute',
            'Custom': 'custom'
        }

        if qualifier['Mode'] in ModeStates:
            LEDSettingsCmdString = ''.join(['{"osc":{"state":{"subscribe":[ {"device":{"led":{"', ModeStates[qualifier['Mode']],'":{"color":null}}}}]}}}\r'])
            self.__UpdateHelper('LEDSettings', LEDSettingsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDSettings')

    def __MatchLEDSettings(self, match, tag):

        ModeStates = {
            'mic_on'    : 'Mic On',
            'mic_mute'  : 'Mic Mute',
            'custom'    : 'Custom'
        }

        qualifier = {'Mode' : ModeStates[match.group(1).decode()]}
        value = match.group(2).decode().title()
        self.WriteStatus('LEDSettings', value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'Activated'     : 'true',
            'Deactivated'   : 'false'
        }

        if value in ValueStateValues:
            MuteCmdString = ''.join(['{"audio":{"mute":', ValueStateValues[value], '}}\r'])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"mute":null}}]}}}\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'true'  : 'Activated',
            'false' : 'Deactivated'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetNoiseGate(self, value, qualifier):

        ValueStateValues = {
            'Activate'   : 'true',
            'Deactivate' : 'false'
        }

        if value in ValueStateValues:
            NoiseGateCmdString = ''.join(['{"audio":{"noise_gate":{"active":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('NoiseGate', NoiseGateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNoiseGate')

    def UpdateNoiseGate(self, value, qualifier):

        NoiseGateCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"noise_gate":{"active":null}}}]}}}\r'
        self.__UpdateHelper('NoiseGate', NoiseGateCmdString, value, qualifier)

    def __MatchNoiseGate(self, match, tag):

        ValueStateValues = {
            'true'  : 'Activate',
            'false' : 'Deactivate'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('NoiseGate', value, None)

    def UpdateOSCStatus(self, value, qualifier):

        TypeStates = {
            'Authorization Access' : '{"osc":{"state":{"auth":{"access":null}}}}\r', 
            'Pretty Print'         : '{"osc":{"state":{"prettyprint":null}}}\r', 
            'Close'                : '{"osc":{"state":{"close":null}}}\r', 
            'Subscribe'            : '{"osc":{"state":{"subscribe":null}}}\r', 
            'Time Tag'             : '{"osc":{"feature":{"timetag":null}}}\r', 
            'Base Address'         : '{"osc":{"feature":{"baseaddr":null}}}\r', 
            'Subscription'         : '{"osc":{"feature":{"subscription":null}}}\r', 
            'Pattern'              : '{"osc":{"feature":{"pattern":null}}}\r', 
            'Limits'               : '{"osc":{"limits":null}}\r', 
            'Schema'               : '{"osc":{"schema":null}}\r', 
            'Version'              : '{"osc":{"version":null}}\r', 
            'Transaction ID'       : '{"osc":{"xid":null}}\r', 
            'Ping'                 : '{"osc":{"ping":null}}\r', 
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            OSCStatusCmdString = TypeStates[type_val]
            self.__UpdateHelper('OSCStatus', OSCStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOSCStatus')

    def __MatchOSCStatus(self, match, tag):

        TypeStates = {
            'auth'         : 'Authorization Access', 
            'prettyprint'  : 'Pretty Print', 
            'close'        : 'Close', 
            'subscribe'    : 'Subscribe', 
            'timetag'      : 'Time Tag', 
            'baseaddr'     : 'Base Address', 
            'subscription' : 'Subscription', 
            'pattern'      : 'Pattern', 
            'limits'       : 'Limits', 
            'schema'       : 'Schema', 
            'version'      : 'Version', 
            'xid'          : 'Transaction ID', 
            'ping'         : 'Ping', 
        }

        if match.group(1).decode() in TypeStates:
            qualifier = {}
            qualifier['Type'] = TypeStates[match.group(1).decode()]
            value = match.group(2).decode().title()
            self.WriteStatus('OSCStatus', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        if -18 <= value <= 0:
            OutputLevelCmdString = ''.join(['{"audio":{"out1":{"attenuation":', str(value), '}}}\r'])
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier) # Query delay not needed. Tested with the device
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        OutputLevelCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"out1":{"attenuation":null}}}]}}}\r'
        self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchOutputLevel(self, match, tag):

        value = int(match.group(1).decode())
        if -90 <= value <= 0:
            self.WriteStatus('OutputLevel', value, None)

    def SetPriority(self, value, qualifier):

        ValueStateValues = {
            'Activate'   : 'true',
            'Deactivate' : 'false'
        }

        if value in ValueStateValues:
            PriorityCmdString = ''.join(['{"audio":{"priority":{"active":[', ValueStateValues[value], ']}}}\r'])
            self.__SetHelper('Priority', PriorityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPriority')

    def UpdatePriority(self, value, qualifier):

        PriorityCmdString = '{"osc":{"state":{"subscribe":[ {"audio":{"priority":{"active":null}}}]}}}\r'
        self.__UpdateHelper('Priority', PriorityCmdString, value, qualifier)

    def __MatchPriority(self, match, tag):

        ValueStateValues = {
            'true'  : 'Activate',
            'false' : 'Deactivate'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Priority', value, None)

    def UpdateResetButtonStatus(self, value, qualifier):

        ResetButtonStatusCmdString = '{"osc":{"state":{"subscribe":[{"device":{"button":{"state":null}}}]}}}\r'
        self.__UpdateHelper('ResetButtonStatus', ResetButtonStatusCmdString, value, qualifier)

    def __MatchResetButtonStatus(self, match, tag):

        ValueStateValues = {
            'true'  : 'On', 
            'false' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ResetButtonStatus', value, None)

    def UpdateResetLabelStatus(self, value, qualifier):

        ResetLabelStatusCmdString = '{"device":{"button":{"label":null}}}\r'
        self.__UpdateHelper('ResetLabelStatus', ResetLabelStatusCmdString, value, qualifier)

    def __MatchResetLabelStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ResetLabelStatus', value, None)

    def SetRestart(self, value, qualifier):

        RestartCmdString = '{"device":{"restart":true}}\r'
        self.__SetHelper('Restart', RestartCmdString, value, qualifier)

    def SetRoomNoiseLevel(self, value, qualifier):

        ValueStateValues = {
            'Quiet'     : 'quiet_room',
            'Normal'    : 'normal_room',
            'Loud'      : 'loud_room'
        }

        if value in ValueStateValues:
            RoomNoiseLevelCmdString = ''.join(['{"audio":{"source_detection":{"threshold":"', ValueStateValues[value], '"}}}\r'])
            self.__SetHelper('RoomNoiseLevel', RoomNoiseLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomNoiseLevel')

    def UpdateRoomNoiseLevel(self, value, qualifier):

        RoomNoiseLevelCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"source_detection":{"threshold":null}}}]}}}\r'
        self.__UpdateHelper('RoomNoiseLevel', RoomNoiseLevelCmdString, value, qualifier)

    def __MatchRoomNoiseLevel(self, match, tag):

        ValueStateValues = {
            'quiet'    : 'Quiet',
            'normal'   : 'Normal',
            'loud'     : 'Loud'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RoomNoiseLevel', value, None)

    def SetSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Off'    : 'OFF',
            'Custom' : 'CUSTOM'
        }

        if value in ValueStateValues:
            SoundProfileCmdString = ''.join(['{"audio":{"equalizer":{"preset":"', ValueStateValues[value], '"}}}\r'])
            self.__SetHelper('SoundProfile', SoundProfileCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSoundProfile')

    def UpdateSoundProfile(self, value, qualifier):

        SoundProfileCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"equalizer":{"preset":null}}}]}}}\r'
        self.__UpdateHelper('SoundProfile', SoundProfileCmdString, value, qualifier)

    def __MatchSoundProfile(self, match, tag):

        ValueStateValues = {
            'OFF' : 'Off', 
            'CUSTOM' : 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundProfile', value, None)

    def SetVoiceLift(self, value, qualifier):

        ValueStateValues = {
            'Activate'   : 'true',
            'Deactivate' : 'false'
        }

        if value in ValueStateValues:
            VoiceLiftCmdString = ''.join(['{"audio":{"voice_lift":{"active":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('VoiceLift', VoiceLiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoiceLift')

    def UpdateVoiceLift(self, value, qualifier):

        VoiceLiftCmdString = '{"osc":{"state":{"subscribe":[ {"audio":{"voice_lift":{"active":null}}}]}}}\r'
        self.__UpdateHelper('VoiceLift', VoiceLiftCmdString, value, qualifier)

    def __MatchVoiceLift(self, match, tag):

        ValueStateValues = {
            'true'  : 'Activate',
            'false' : 'Deactivate'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VoiceLift', value, None)

    def SetZoneAzimuthCommand(self, value, qualifier):

        if 1 <= int(qualifier['Number']) <= 3 and 0 <= qualifier['Min'] <= 360 and 0 <= qualifier['Max'] <= 360 and \
                qualifier['Min'] < qualifier['Max'] and (qualifier['Max'] - qualifier['Min'] >= 5):
            ZoneAzimuthCommandCmdString = ''.join(['{"audio":{"exclusion_zone":{"azimuth":{"', qualifier['Number'],'":[', str(qualifier['Min']), ',', str(qualifier['Max']), ']}}}}\r'])
            self.__SetHelper('ZoneAzimuthCommand', ZoneAzimuthCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneAzimuthCommand')
            
    def UpdateZoneAzimuthStatus(self, value, qualifier):

        number_val = qualifier['Number']
        if number_val in ['1', '2', '3']:
            ZoneAzimuthStatusCmdString = ''.join(['{"audio":{"exclusion_zone":{"azimuth":{"', number_val, '":null}}}}\r'])
            self.__UpdateHelper('ZoneAzimuthStatus', ZoneAzimuthStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneAzimuthStatus')

    def __MatchZoneAzimuthStatus(self, match, tag):

        qualifier = {'Number' : match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('ZoneAzimuthStatus', value, qualifier)

    def SetZoneElevationCommand(self, value, qualifier):

        if 0 <= qualifier['Min'] <= 75 and 0 <= qualifier['Max'] <= 75 and qualifier['Min'] < qualifier['Max'] and \
                (qualifier['Max'] - qualifier['Min'] >= 5):
            ZoneElevationCommandCmdString = ''.join(['{"audio":{"exclusion_zone":{"elevation":{"1":[',
                                                     str(qualifier['Min']), ',', str(qualifier['Max']), ']}}}}\r'])
            self.__SetHelper('ZoneElevationCommand', ZoneElevationCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneElevationCommand')
            
    def UpdateZoneElevationStatus(self, value, qualifier):

        ZoneElevationStatusCmdString = '{"osc":{"state":{"subscribe":[{"audio":{"exclusion_zone":{"elevation":{"1":null}}}}]}}}\r'
        self.__UpdateHelper('ZoneElevationStatus', ZoneElevationStatusCmdString, value, qualifier)

    def __MatchZoneElevationStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ZoneElevationStatus', value, None)

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

        self.Error(['Error {}: {}'.format(match.group(1).decode(), match.group(2).decode())])

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