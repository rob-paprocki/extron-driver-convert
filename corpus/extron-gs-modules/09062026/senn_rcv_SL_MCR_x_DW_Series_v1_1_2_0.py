from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import json
import time

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
        self.Models = {
            'SL MCR 2 DW': self.senn_27_4873_2C,
            'SL MCR 4 DW': self.senn_27_4873_4C,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMatesStatus': {'Parameters': ['Channel'], 'Status': {}},
            'AudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioLevel': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryBars': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryLifetime': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryType': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryVoltageLevel': {'Parameters': ['Channel'], 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'DeviceProduct': { 'Status': {}},
            'DeviceSerialNumber': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Identify': {'Parameters': ['Channel'], 'Status': {}},
            'LED': {'Parameters': ['Channel'], 'Status': {}},
            'LowCut': {'Parameters': ['Channel'], 'Status': {}},
            'MuteMode': {'Parameters': ['Channel'], 'Status': {}},
            'MuteSwitch': {'Parameters': ['Channel'], 'Status': {}},
            'Pairing': {'Parameters': ['Channel'], 'Status': {}},
            'RFQuality': {'Parameters': ['Channel'], 'Status': {}},
            'SoundProfile': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterType': {'Parameters': ['Channel'], 'Status': {}},
            'WarningStatus': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.errorReg = '(\d{3})'

        ActiveMatesRegex        = re.compile(b'{"mates":{"tx([1-4])":{"active":(true|false)}}}')
        AudioGainRegex          = re.compile(b'{"audio":{"rx([1-4])":{"gain":(-?\d+)}}}')
        AudioLevelRegex         = re.compile(b'{"m":{"rx([1-4])":{"level":(-?\d+)}}}')
        DeviceLocationRegex     = re.compile(b'{"device":{"location":"(.*?)"}}')
        DeviceNameRegex         = re.compile(b'{"device":{"name":"(.*?)"}}')
        DeviceProductRegex      = re.compile(b'{"device":{"identity":{"product":"(.*?)"}}}')
        DeviceSerialNumberRegex = re.compile(b'{"device":{"identity":{"serial":"(.*?)"}}}')
        FirmwareRegex           = re.compile(b'{"device":{"identity":{"version":"(\d+\.\d+\.\d+)"}}}')
        IdentifyRegex           = re.compile(b'{"rx([1-4])":{"identification":{"visual":(true|false)}}}')
        LowCutRegex             = re.compile(b'{"audio":{"rx([1-4])":{"low_cut":(true|false)}}}')
        MuteModeRegex           = re.compile(b'{"rx([1-4])":{"mute_mode":"(ON|PUSH_TO_TALK|PUSH_TO_MUTE|ROOM_MUTE|OFF)"}}')
        MuteSwitchRegex         = re.compile(b'{"rx([1-4])":{"mute_state":(true|false)}}')
        PairingRegex            = re.compile(b'{"rx([1-4])":{"pair":{"enable":(true|false)}}}')
        RFQualityRegex          = re.compile(b'{"rx([1-4])":{"rf_quality":(\d+)}}')
        SoundProfileRegex       = re.compile(b'{"audio":{"rx([1-4])":{"equalizer":{"preset":"(OFF|FEMALE_SPEECH|MALE_SPEECH|MEDIA|CUSTOM)"}}}}')
        BatteryBarsRegex        = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"bat_bars":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"bat_bars":([0-6])}}})')
        BatteryLifetimeRegex    = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"bat_lifetime":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"bat_lifetime":(\d+)}}})')
        BatteryTypeRegex        = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"bat_type":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"bat_type":"(RECHARGEABLE|BATTERY)"}}})')
        BatteryVoltageRegex     = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"bat_gauge":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"bat_gauge":(\d+)}}})')
        LEDRegex                = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"led_active":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"led_active":(true|false)}}})')
        TransmitterTypeRegex    = re.compile(b'(?:{"osc":{"error":\[{"mates":{"tx([1-4])":{"device_type":([\s\S]+?)}}|'
                                            b'{"mates":{"tx([1-4])":{"device_type":"(HANDHELD|BODYPACK|TABLE-STAND|BOUNDARY)"}}})')
        WarningStatusRegex      = re.compile(b'{"mates":{"tx([1-4])":{"warnings":\["?([\s\S]+?)?"?\]}}}')
        ErrorRegex              = re.compile(b'{"osc":{"error":([\s\S]+?)}}')
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(ActiveMatesRegex, self.__MatchActiveMatesStatus, None)
            self.AddMatchString(AudioGainRegex, self.__MatchAudioGain, None)
            self.AddMatchString(AudioLevelRegex, self.__MatchAudioLevel, None)
            self.AddMatchString(BatteryBarsRegex, self.__MatchBatteryBars, None)
            self.AddMatchString(BatteryLifetimeRegex, self.__MatchBatteryLifetime, None)
            self.AddMatchString(BatteryTypeRegex, self.__MatchBatteryType, None)
            self.AddMatchString(BatteryVoltageRegex, self.__MatchBatteryVoltageLevel, None)
            self.AddMatchString(DeviceLocationRegex, self.__MatchDeviceLocation, None)
            self.AddMatchString(DeviceNameRegex, self.__MatchDeviceName, None)
            self.AddMatchString(DeviceProductRegex, self.__MatchDeviceProduct, None)
            self.AddMatchString(DeviceSerialNumberRegex, self.__MatchDeviceSerialNumber, None)
            self.AddMatchString(FirmwareRegex, self.__MatchFirmwareVersion, None)
            self.AddMatchString(IdentifyRegex, self.__MatchIdentify, None)
            self.AddMatchString(LEDRegex, self.__MatchLED, None)
            self.AddMatchString(LowCutRegex, self.__MatchLowCut, None)
            self.AddMatchString(MuteModeRegex, self.__MatchMuteMode, None)
            self.AddMatchString(MuteSwitchRegex, self.__MatchMuteSwitch, None)
            self.AddMatchString(PairingRegex, self.__MatchPairing, None)
            self.AddMatchString(RFQualityRegex, self.__MatchRFQuality, None)
            self.AddMatchString(SoundProfileRegex, self.__MatchSoundProfile, None)
            self.AddMatchString(TransmitterTypeRegex, self.__MatchTransmitterType, None)
            self.AddMatchString(WarningStatusRegex, self.__MatchWarningStatus, None)
            self.AddMatchString(ErrorRegex, self.__MatchError, None)

    def subscribe(self, j):
        return json.dumps({'osc': {'state': {'subscribe': [j]}}}, separators=(',', ':')) + '\r'
    
    def UpdateActiveMatesStatus(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            ActiveMatesStatusCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'active': None}}})
            self.__UpdateHelper('ActiveMatesStatus', ActiveMatesStatusCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateActiveMatesStatus')
            
    def __MatchActiveMatesStatus(self, match, tag):

        ValueStateValues = {
            'true' :    'Yes', 
            'false' :   'No'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ActiveMatesStatus', value, qualifier)

    def SetAudioGain(self, value, qualifier):

        Values = (-24, -18, -12, -6, 0, 6, 12)

        channel_val = qualifier['Channel']

        if value in Values and 1 <= int(channel_val) <= self.ChannelSize:
            AudioGainCmdString = ''.join(['{"audio":{"rx', channel_val, '":{"gain":', str(value), '}}}\r'])
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        channel_val = qualifier['Channel']
        if 1 <= int(channel_val) <= self.ChannelSize:
            AudioGainCmdString = self.subscribe({'audio': {'rx{}'.format(channel_val): {'gain': None}}})
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        Values = (-24, -18, -12, -6, 0, 6, 12)
        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = int(match.group(2).decode())
        if value in Values:
            self.WriteStatus('AudioGain', value, qualifier)

    def UpdateAudioLevel(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            AudioLevelCmdString = self.subscribe({'m': {'rx{}'.format(channel_val): {'level': None}}})
            self.__UpdateHelper('AudioLevel', AudioLevelCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateAudioLevel')

    def __MatchAudioLevel(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = int(match.group(2).decode())
        if -60 <= value <= 0:
            self.WriteStatus('AudioLevel', value, qualifier)

    def UpdateBatteryBars(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            BatteryBarsCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'bat_bars': None}}})
            self.__UpdateHelper('BatteryBars', BatteryBarsCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateBatteryBars')

    def __MatchBatteryBars(self, match, tag):

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('BatteryBars', 'Not Found', qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }

            value = match.group(4).decode()
            self.WriteStatus('BatteryBars', value, qualifier)

    def UpdateBatteryLifetime(self, value, qualifier):

        channel_val = qualifier['Channel']
        
        if 1 <= int(channel_val) <= self.ChannelSize:
            BatteryLifetimeCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'bat_lifetime': None}}})
            self.__UpdateHelper('BatteryLifetime', BatteryLifetimeCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateBatteryLifetime')

    def __MatchBatteryLifetime(self, match, tag):

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('BatteryLifetime', 'Not Found', qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }

            value = time.strftime("%H:%M:%S", time.gmtime(int(match.group(4).decode())))
            self.WriteStatus('BatteryLifetime', value, qualifier)

    def UpdateBatteryType(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            BatteryTypeCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'bat_type': None}}})
            self.__UpdateHelper('BatteryType', BatteryTypeCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateBatteryType')

    def __MatchBatteryType(self, match, tag):

        ValueStateValues = {
            'BATTERY'      : 'Normal', 
            'RECHARGEABLE' : 'Rechargeable'
        }

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('BatteryType', 'Not Found', qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }

            value = ValueStateValues[match.group(4).decode()]
            self.WriteStatus('BatteryType', value, qualifier)

    def UpdateBatteryVoltageLevel(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            BatteryVoltageLevelCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'bat_gauge': None}}})
            self.__UpdateHelper('BatteryVoltageLevel', BatteryVoltageLevelCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateBatteryVoltageLevel')

    def __MatchBatteryVoltageLevel(self, match, tag):

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('BatteryVoltageLevel', 0, qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }
            
            value = int(match.group(4).decode())

            if 0 <= value <= 100:
                self.WriteStatus('BatteryVoltageLevel', value, qualifier)

    def UpdateDeviceLocation(self, value, qualifier):

        DeviceLocationCmdString = self.subscribe({'device': {'location': None}})
        self.__UpdateHelper('DeviceLocation', DeviceLocationCmdString, value, qualifier)

    def __MatchDeviceLocation(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceLocation', value, None)

    def UpdateDeviceName(self, value, qualifier):

        DeviceNameCmdString = self.subscribe({'device': {'name': None}})
        self.__UpdateHelper('DeviceName', DeviceNameCmdString, value, qualifier)

    def __MatchDeviceName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceName', value, None)

    def UpdateDeviceProduct(self, value, qualifier):

        DeviceProductCmdString = '{"device":{"identity":{"product":null}}}\r'
        self.__UpdateHelper('DeviceProduct', DeviceProductCmdString, value, qualifier)

    def __MatchDeviceProduct(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceProduct', value, None)

    def UpdateDeviceSerialNumber(self, value, qualifier):

        DeviceSerialNumberCmdString = '{"device":{"identity":{"serial":null}}}\r'
        self.__UpdateHelper('DeviceSerialNumber', DeviceSerialNumberCmdString, value, qualifier)

    def __MatchDeviceSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceSerialNumber', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '{"device":{"identity":{"version":null}}}\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        
        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetIdentify(self, value, qualifier):

        channel_val = qualifier['Channel']

        ValueStateValues = {
            'Enable':   'true',
            'Disable':  'false'
        }

        if 1 <= int(channel_val) <= self.ChannelSize and value in ValueStateValues:
            IdentifyCmdString = ''.join(['{"rx', channel_val, '":{"identification":{"visual":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('Identify', IdentifyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIdentify')

    def UpdateIdentify(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            IdentifyCmdString = self.subscribe({'rx{}'.format(channel_val): {'identification': {'visual': None}}})
            self.__UpdateHelper('Identify', IdentifyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIdentify')

    def __MatchIdentify(self, match, tag):

        ValueStateValues = {
            'true':     'Enable',
            'false':    'Disable'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Identify', value, qualifier)

    def SetLED(self, value, qualifier):

        channel_val = qualifier['Channel']

        ValueStateValues = {
            'Enable':   'true',
            'Disable':  'false'
        }

        if 1 <= int(channel_val) <= self.ChannelSize and value in ValueStateValues:
            LEDCmdString = ''.join(['{"mates":{"tx', channel_val, '":{"led_active":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('LED', LEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLED')

    def UpdateLED(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            LEDCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'led_active': None}}})
            self.__UpdateHelper('LED', LEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLED')

    def __MatchLED(self, match, tag):

        ValueStateValues = {
            'true':     'Enable',
            'false':    'Disable'
        }

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('LED', 'Not Found', qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }

            value = ValueStateValues[match.group(4).decode()]
            self.WriteStatus('LED', value, qualifier)

    def SetLowCut(self, value, qualifier):

        channel_val = qualifier['Channel']

        ValueStateValues = {
            'Enable':   'true',
            'Disable':  'false'
        }

        if 1 <= int(channel_val) <= self.ChannelSize and value in ValueStateValues:
            LowCutCmdString = ''.join(['{"audio":{"rx', channel_val, '":{"low_cut":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('LowCut', LowCutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLowCut')

    def UpdateLowCut(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            LowCutCmdString = self.subscribe({'audio': {'rx{}'.format(channel_val): {'low_cut': None}}})
            self.__UpdateHelper('LowCut', LowCutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLowCut')

    def __MatchLowCut(self, match, tag):

        ValueStateValues = {
            'true':     'Enable',
            'false':    'Disable'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LowCut', value, qualifier)

    def SetMuteMode(self, value, qualifier):

        channel_val = qualifier['Channel']

        ValueStateValues = {
            'On':           'ON',
            'Push To Talk': 'PUSH_TO_TALK',
            'Push To Mute': 'PUSH_TO_MUTE',
            'Room Mute':    'ROOM_MUTE',
            'Off':          'OFF'
        }

        if 1 <= int(channel_val) <= self.ChannelSize and value in ValueStateValues:
            MuteModeCmdString = ''.join(['{"rx', channel_val, '":{"mute_mode":"', ValueStateValues[value], '"}}\r'])
            self.__SetHelper('MuteMode', MuteModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteMode')

    def UpdateMuteMode(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(qualifier['Channel']) <= self.ChannelSize:
            MuteModeCmdString = self.subscribe({'rx{}'.format(channel_val): {'mute_mode': None}})
            self.__UpdateHelper('MuteMode', MuteModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMuteMode')

    def __MatchMuteMode(self, match, tag):

        ValueStateValues = {
            'ON':           'On',
            'PUSH_TO_TALK': 'Push To Talk',
            'PUSH_TO_MUTE': 'Push To Mute',
            'ROOM_MUTE':    'Room Mute',
            'OFF':          'Off'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MuteMode', value, qualifier)

    def SetMuteSwitch(self, value, qualifier):

        ValueStateValues = {
            'Enable':   'true', 
            'Disable':  'false'
        }

        channel_val = qualifier['Channel']

        if value in ValueStateValues and 1 <= int(channel_val) <= self.ChannelSize:
            MuteSwitchCmdString = ''.join(['{"rx', channel_val, '":{"mute_state":', ValueStateValues[value], '}}\r'])
            self.__SetHelper('MuteSwitch', MuteSwitchCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetMuteSwitch')

    def UpdateMuteSwitch(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            MuteSwitchCmdString = self.subscribe({'rx{}'.format(channel_val): {'mute_state': None}})
            self.__UpdateHelper('MuteSwitch', MuteSwitchCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateMuteSwitch')

    def __MatchMuteSwitch(self, match, tag):

        ValueStateValues = {
            'true':     'Enable', 
            'false':    'Disable'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MuteSwitch', value, qualifier)

    def SetPairing(self, value, qualifier):

        ValueStateValues = {
            'Start':    'true', 
            'Stop':     'false'
        }

        channel_val = qualifier['Channel']

        if value in ValueStateValues and 1 <= int(channel_val) <= self.ChannelSize:
            PairingCmdString = ''.join(['{"rx', channel_val, '":{"pair":{"enable":', ValueStateValues[value], '}}}\r'])
            self.__SetHelper('Pairing', PairingCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetPairing')

    def UpdatePairing(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            PairingCmdString = self.subscribe({'rx{}'.format(channel_val): {'pair': {'enable': None}}})
            self.__UpdateHelper('Pairing', PairingCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdatePairing')

    def __MatchPairing(self, match, tag):

        ValueStateValues = {
            'true':     'Start', 
            'false':    'Stop'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Pairing', value, qualifier)

    def UpdateRFQuality(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            RFQualityCmdString = self.subscribe({'rx{}'.format(channel_val): {'rf_quality': None}})
            self.__UpdateHelper('RFQuality', RFQualityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRFQuality')

    def __MatchRFQuality(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('RFQuality', value, qualifier)

    def SetSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Off':              'OFF', 
            'Female Speech':    'FEMALE_SPEECH', 
            'Male Speech':      'MALE_SPEECH', 
            'Media':            'MEDIA', 
            'Custom':           'CUSTOM'
        }

        channel_val = qualifier['Channel']

        if value in ValueStateValues and 1 <= int(channel_val) <= self.ChannelSize:
            SoundProfileCmdString = ''.join(['{"audio":{"rx', channel_val, '":{"equalizer":{"preset":"', ValueStateValues[value], '"}}}}\r'])
            self.__SetHelper('SoundProfile', SoundProfileCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for SetSoundProfile')

    def UpdateSoundProfile(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            SoundProfileCmdString = self.subscribe({'audio': {'rx{}'.format(channel_val): {'equalizer': {'preset': None}}}})
            self.__UpdateHelper('SoundProfile', SoundProfileCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateSoundProfile')

    def __MatchSoundProfile(self, match, tag):

        ValueStateValues = {
            'OFF':              'Off', 
            'FEMALE_SPEECH':    'Female Speech', 
            'MALE_SPEECH':      'Male Speech', 
            'MEDIA':            'Media', 
            'CUSTOM':           'Custom'
        }

        qualifier = {
            'Channel': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SoundProfile', value, qualifier)

    def UpdateTransmitterType(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            TransmitterTypeCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'device_type': None}}})
            self.__UpdateHelper('TransmitterType', TransmitterTypeCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateTransmitterType')

    def __MatchTransmitterType(self, match, tag):

        ValueStateValues = {
            'HANDHELD'    : 'Handheld', 
            'BODYPACK'    : 'Bodypack', 
            'TABLE-STAND' : 'Tablestand', 
            'BOUNDARY'    : 'Boundary'
        }

        if b'error' in match.group(0):
            qualifier = {
                'Channel': match.group(1).decode()
            }

            self.WriteStatus('TransmitterType', 'Not Found', qualifier)
        else:    
            qualifier = {
                'Channel': match.group(3).decode()
            }

            value = ValueStateValues[match.group(4).decode()]
            self.WriteStatus('TransmitterType', value, qualifier)

    def UpdateWarningStatus(self, value, qualifier):

        channel_val = qualifier['Channel']

        if 1 <= int(channel_val) <= self.ChannelSize:
            WarningStatusCmdString = self.subscribe({'mates': {'tx{}'.format(channel_val): {'warnings': None}}})
            self.__UpdateHelper('WarningStatus', WarningStatusCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateWarningStatus')

    def __MatchWarningStatus(self, match, tag):

        qualifier = {
            'Channel': match.group(1).decode()
        }

        if match.group(2):
            if b'reason' in match.group(2):
                self.WriteStatus('WarningStatus', 'Not Found', qualifier)
            else:
                self.WriteStatus('WarningStatus', match.group(2).decode().title(), qualifier)
        else:
            self.WriteStatus('WarningStatus', 'No Warnings', qualifier)

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

        ErrorStates = {
            '310': 'Error 310: Subscription Terminates',
            '400': 'Error 400: Bad Request',
            '401': 'Error 401: Unauthorized',
            '403': 'Error 403: Forbidden',
            '404': 'Error 404: Not Found',
            '406': 'Error 406: Not Acceptable',
            '408': 'Error 408: Request Timeout',
            '409': 'Error 409: Conflict',
            '410': 'Error 410: Gone',
            '413': 'Error 413: Request Entity Too Large',
            '414': 'Error 414: Request Too Complex',
            '422': 'Error 422: Unprocessable Entity',
            '423': 'Error 423: Locked',
            '424': 'Error 424: Failed Dependency',
            '450': 'Error 450: Answer Too Long',
            '454': 'Error 454: Parameter Address Not Found',
            '500': 'Error 500: Internal Server Error',
            '501': 'Error 501: Not Implemented',
            '503': 'Error 503: Service Unavailable'
        }
        value = match.group(1).decode()
        err_code = re.findall(self.errorReg, value)
        if err_code and err_code[0] in ErrorStates:
            self.Error([ErrorStates[err_code[0]]])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def senn_27_4873_4C(self):

        self.ChannelSize = 4

    def senn_27_4873_2C(self):

        self.ChannelSize = 2

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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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