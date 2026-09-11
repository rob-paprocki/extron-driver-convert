from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import json
import base64
from extronlib import Version

class DeviceClass:
    def __init__(self, ipAddress, port, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.base64Auth = ''

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        if devicePassword is not None:
            self.base64Auth = 'Basic {}'.format(base64.b64encode('api'.encode() + b':' + devicePassword.encode()).decode())
        else:
            self.base64Auth = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogOutputGain': { 'Status': {}},
            'AnalogOutputSource': { 'Status': {}},
            'BeamDirection': {'Parameters':['Type'], 'Status': {}},
            'DeviceName': { 'Status': {}},
            'ExclusionZoneAzimuth': {'Parameters':['Zone','Min','Max'], 'Status': {}},
            'ExclusionZoneAzimuthStatus': {'Parameters':['Zone','Type'], 'Status': {}},
            'ExclusionZoneElevation': {'Parameters':['Zone','Min','Max'], 'Status': {}},
            'ExclusionZoneElevationStatus': {'Parameters':['Zone','Type'], 'Status': {}},
            'ExclusionZoneMode': {'Parameters':['Zone'], 'Status': {}},
            'FarEndOutputDelay': { 'Status': {}},
            'FarEndOutputGain': { 'Status': {}},
            'FarEndOutputSoundProfile': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'IdentifyDevice': { 'Status': {}},
            'InputLevelGain': { 'Status': {}},
            'InstallationType': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDSettings': {'Parameters':['Mode'], 'Status': {}},
            'LEDSettingsCustom': { 'Status': {}},
            'LEDShowFarEndActivity': { 'Status': {}},
            'LocalOutputDelay': { 'Status': {}},
            'LocalOutputGain': { 'Status': {}},
            'LocalOutputSoundProfile': { 'Status': {}},
            'Mute': { 'Status': {}},
            'MuteIntervalTime': { 'Status': {}},
            'MuteThreshold': { 'Status': {}},
            'NoiseGateHoldTime': { 'Status': {}},
            'NoiseGateMode': { 'Status': {}},
            'NoiseGateThreshold': { 'Status': {}},
            'PriorityZoneAzimuth': {'Parameters':['Min','Max'], 'Status': {}},
            'PriorityZoneAzimuthStatus': {'Parameters':['Type'], 'Status': {}},
            'PriorityZoneElevation': {'Parameters':['Min','Max'], 'Status': {}},
            'PriorityZoneElevationStatus': {'Parameters':['Type'], 'Status': {}},
            'PriorityZoneMode': { 'Status': {}},
            'SensitivityThreshold': { 'Status': {}},
            'TruVoiceliftMode': { 'Status': {}},
        }

    def SetAnalogOutputGain(self, value, qualifier):

        if -18 <= value <= 0:
            data = {
                'gain' : value
            }

            AnalogOutputGainCmdString = 'api/audio/outputs/analog'
            self.__SetHelper('AnalogOutputGain', value, qualifier, url=AnalogOutputGainCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAnalogOutputGain')

    def UpdateAnalogOutputGain(self, value, qualifier):

        AnalogOutputGainCmdString = 'api/audio/outputs/analog'
        res = self.__UpdateHelper('AnalogOutputGain', value, qualifier, url=AnalogOutputGainCmdString)
        if res:
            try:
                value = int(res['gain'])
                if -18 <= value <= 0:
                    self.WriteStatus('AnalogOutputGain', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Analog Output Gain: Invalid/unexpected response'])
            try:
                ValueStateValues = {
                    'LocalOutput'  : 'Local Output',
                    'FarendOutput' : 'Far End Output'
                }
                value = ValueStateValues[res['switch']]
                self.WriteStatus('AnalogOutputSource', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Analog Output Source: Invalid/unexpected response'])

    def SetAnalogOutputSource(self, value, qualifier):

        ValueStateValues = {
            'Local Output'   : 'LocalOutput',
            'Far End Output' : 'FarendOutput'
        }

        if value in ValueStateValues:
            data = {
                'switch' : ValueStateValues[value]
            }

            AnalogOutputSourceCmdString = 'api/audio/outputs/analog'
            self.__SetHelper('AnalogOutputSource', value, qualifier, url=AnalogOutputSourceCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAnalogOutputSource')

    def UpdateAnalogOutputSource(self, value, qualifier):

        self.UpdateAnalogOutputGain(value, None)

    def UpdateBeamDirection(self, value, qualifier):
            
        if qualifier['Type'] in ['Azimuth', 'Elevation']:
            BeamDirectionCmdString = 'api/audio/inputs/microphone/beam/direction'
            res = self.__UpdateHelper('BeamDirection', value, qualifier, url=BeamDirectionCmdString)
            if res:
                try:
                    azimuth = res['azimuth']
                    elevation = res['elevation']
                    if 0 <= azimuth <= 360 and 0 <= elevation <= 360:
                        self.WriteStatus('BeamDirection', azimuth, {'Type' : 'Azimuth'})
                        self.WriteStatus('BeamDirection', elevation, {'Type' : 'Elevation'})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Beam Direction: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBeamDirection')

    def UpdateDeviceName(self, value, qualifier):

        DeviceNameCmdString = 'api/device/site'
        res = self.__UpdateHelper('DeviceName', value, qualifier, url=DeviceNameCmdString)
        if res:
            try:
                value = res['deviceName']
                self.WriteStatus('DeviceName', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device Name: Invalid/unexpected response'])

    def SetExclusionZoneAzimuth(self, value, qualifier):

        if 1 <= int(qualifier['Zone']) <= 5 and 0 <= qualifier['Min'] <= 355 and 0 <= qualifier['Max'] <= 355:
            data = {
                'azimuth' : {
                    'min' : qualifier['Min'],
                    'max' : qualifier['Max']
                }
            }
            ExclusionZoneAzimuthCmdString = 'api/audio/inputs/microphone/exclusionZones/{}'.format(int(qualifier['Zone']) - 1)
            self.__SetHelper('ExclusionZoneAzimuth', value, qualifier, url=ExclusionZoneAzimuthCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetExclusionZoneAzimuth')

    def UpdateExclusionZoneAzimuthStatus(self, value, qualifier):

        self.UpdateExclusionZoneMode(value, {'Zone' : qualifier['Zone']})

    def SetExclusionZoneElevation(self, value, qualifier):

        if 1 <= int(qualifier['Zone']) <= 5 and 0 <= qualifier['Min'] <= 90 and 0 <= qualifier['Max'] <= 90:
            data = {
                'elevation' : {
                    'min' : qualifier['Min'],
                    'max' : qualifier['Max']
                }
            }
            ExclusionZoneElevationCmdString = 'api/audio/inputs/microphone/exclusionZones/{}'.format(int(qualifier['Zone']) - 1)
            self.__SetHelper('ExclusionZoneElevation', value, qualifier, url=ExclusionZoneElevationCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetExclusionZoneElevation')

    def UpdateExclusionZoneElevationStatus(self, value, qualifier):

        self.UpdateExclusionZoneMode(value, {'Zone' : qualifier['Zone']})

    def SetExclusionZoneMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if 1 <= int(qualifier['Zone']) <= 5 and value in ValueStateValues:
            data = {
                'enabled' : ValueStateValues[value]
            }
            ExclusionZoneModeCmdString = 'api/audio/inputs/microphone/exclusionZones/{}'.format(int(qualifier['Zone']) - 1)
            self.__SetHelper('ExclusionZoneMode', value, qualifier, url=ExclusionZoneModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetExclusionZoneMode')

    def UpdateExclusionZoneMode(self, value, qualifier):

        if 1 <= int(qualifier['Zone']) <= 5:
            ExclusionZoneAzimuthStatusCmdString = 'api/audio/inputs/microphone/exclusionZones/{}'.format(int(qualifier['Zone']) - 1)
            res = self.__UpdateHelper('ExclusionZoneAzimuthStatus', value, qualifier, url=ExclusionZoneAzimuthStatusCmdString)
            if res:
                try:
                    ValueStateValues = {
                        True  : 'On',
                        False : 'Off'
                    }

                    value = ValueStateValues[res['enabled']]
                    self.WriteStatus('ExclusionZoneMode', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Exclusion Zone Azimuth Mode: Invalid/unexpected response'])

                try:
                    min = int(res['azimuth']['min'])
                    max = int(res['azimuth']['max'])
                    if 0 <= min <= 355 and 0 <= max <= 355:
                        self.WriteStatus('ExclusionZoneAzimuthStatus', min, {'Zone' : qualifier['Zone'], 'Type' : 'Min'})
                        self.WriteStatus('ExclusionZoneAzimuthStatus', max, {'Zone' : qualifier['Zone'], 'Type' : 'Max'})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Exclusion Zone Azimuth Status: Invalid/unexpected response'])

                try:
                    min = int(res['elevation']['min'])
                    max = int(res['elevation']['max'])
                    if 0 <= min <= 90 and 0 <= max <= 90:
                        self.WriteStatus('ExclusionZoneElevationStatus', min, {'Zone' : qualifier['Zone'], 'Type' : 'Min'})
                        self.WriteStatus('ExclusionZoneElevationStatus', max, {'Zone' : qualifier['Zone'], 'Type' : 'Max'})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Exclusion Zone Elevation Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateExclusionZoneMode')

    def SetFarEndOutputDelay(self, value, qualifier):

        if 0 <= value <= 100:
            data = {
                'delay' : value
            }
            FarEndOutputDelayCmdString = 'api/audio/outputs/dante/farEnd'
            self.__SetHelper('FarEndOutputDelay', value, qualifier, url=FarEndOutputDelayCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetFarEndOutputDelay')

    def UpdateFarEndOutputDelay(self, value, qualifier):

        self.UpdateFarEndOutputGain(value, None)

    def SetFarEndOutputGain(self, value, qualifier):

        if 0 <= value <= 24:
            data = {
                'gain' : value
            }
            FarEndOutputGainCmdString = 'api/audio/outputs/dante/farEnd'
            self.__SetHelper('FarEndOutputGain', value, qualifier, url=FarEndOutputGainCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetFarEndOutputGain')

    def UpdateFarEndOutputGain(self, value, qualifier):

        FarEndOutputGainCmdString = 'api/audio/outputs/dante/farEnd'
        res = self.__UpdateHelper('FarEndOutputGain', value, qualifier, url=FarEndOutputGainCmdString)
        if res:
            try:
                value = int(res['gain'])
                if 0 <= value <= 24:
                    self.WriteStatus('FarEndOutputGain', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Far End Output Gain: Invalid/unexpected response'])

            try:
                value = int(res['delay'])
                if 0 <= value <= 100:
                    self.WriteStatus('FarEndOutputDelay', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Far End Output Delay: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['equalizerEnabled']]
                self.WriteStatus('FarEndOutputSoundProfile', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Far End Output Sound Profile: Invalid/unexpected response'])

    def SetFarEndOutputSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'equalizerEnabled' : ValueStateValues[value]
            }
            FarEndOutputSoundProfileCmdString = 'api/audio/outputs/dante/farEnd'
            self.__SetHelper('FarEndOutputSoundProfile', value, qualifier, url=FarEndOutputSoundProfileCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetFarEndOutputSoundProfile')

    def UpdateFarEndOutputSoundProfile(self, value, qualifier):

        self.UpdateFarEndOutputGain(value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'api/firmware/update/state'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:
            try:
                value = res['deviceVersion']
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetIdentifyDevice(self, value, qualifier):

        data = {
            'visual' : True
        }
        IdentifyDeviceCmdString = 'api/device/identification'
        self.__SetHelper('IdentifyDevice', value, qualifier, url=IdentifyDeviceCmdString, data=data)

    def SetInputLevelGain(self, value, qualifier):

        if -60 <= value <= 9:
            data = {
                'gain' : value
            }
            InputLevelGainCmdString = 'api/audio/inputs/dante/reference'
            self.__SetHelper('InputLevelGain', value, qualifier, url=InputLevelGainCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetInputLevelGain')

    def UpdateInputLevelGain(self, value, qualifier):

        InputLevelGainCmdString = 'api/audio/inputs/dante/reference'
        res = self.__UpdateHelper('InputLevelGain', value, qualifier, url=InputLevelGainCmdString)
        if res:
            try:
                value = int(res['gain'])
                if -60 <= value <= 9:
                    self.WriteStatus('InputLevelGain', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Input Level Gain: Invalid/unexpected response'])

    def SetInstallationType(self, value, qualifier):

        ValueStateValues = {
            'Flush Mount'       : 'FlushMounted',
            'Suspended Mount'   : 'Suspended',
            'Surface Mount'     : 'SurfaceMounted'
        }

        if value in ValueStateValues:
            data = {
                'installationType' : ValueStateValues[value]
            }
            InstallationTypeCmdString = 'api/audio/inputs/microphone/beam'
            self.__SetHelper('InstallationType', value, qualifier, url=InstallationTypeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetInstallationType')

    def UpdateInstallationType(self, value, qualifier):

        InstallationTypeCmdString = 'api/audio/inputs/microphone/beam'
        res = self.__UpdateHelper('InstallationType', value, qualifier, url=InstallationTypeCmdString)
        if res:
            try:
                ValueStateValues = {
                    'FlushMounted'   : 'Flush Mount',
                    'Suspended'      : 'Suspended Mount',
                    'SurfaceMounted' : 'Surface Mount'
                }

                value = ValueStateValues[res['installationType']]
                self.WriteStatus('InstallationType', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Installation Type: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    'QuietRoom'  : 'Quiet',
                    'NormalRoom' : 'Normal',
                    'LoudRoom'   : 'Loud'
                }

                value = ValueStateValues[res['sourceDetectionThreshold']]
                self.WriteStatus('SensitivityThreshold', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Sensitivity Threshold: Invalid/unexpected response'])

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Off' : 0,
            '1'   : 1,
            '2'   : 2,
            '3'   : 3,
            '4'   : 4,
            '5'   : 5
        }

        if value in ValueStateValues:
            data = {
                'brightness' : ValueStateValues[value]
            }
            LEDBrightnessCmdString = 'api/device/leds/ring'
            self.__SetHelper('LEDBrightness', value, qualifier, url=LEDBrightnessCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):
            
        LEDBrightnessCmdString = 'api/device/leds/ring'
        res = self.__UpdateHelper('LEDBrightness', value, qualifier, url=LEDBrightnessCmdString)
        if res:
            try:
                ValueStateValues = {
                    0 : 'Off',
                    1 : '1',
                    2 : '2',
                    3 : '3',
                    4 : '4',
                    5 : '5'
                }

                value = ValueStateValues[res['brightness']]
                self.WriteStatus('LEDBrightness', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['LED Brightness: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    'Blue'      : 'Blue',
                    'Cyan'      : 'Cyan',
                    'Green'     : 'Green',
                    'Orange'    : 'Orange',
                    'Pink'      : 'Pink',
                    'Red'       : 'Red',
                    'LightGreen': 'Light Green',
                    'Yellow'    : 'Yellow'
                }

                micOn = ValueStateValues[res['micOn']['color']]
                micMute = ValueStateValues[res['micMute']['color']]
                micCustom = ValueStateValues[res['micCustom']['color']]
                self.WriteStatus('LEDSettings', micOn, {'Mode' : 'Mic On'})
                self.WriteStatus('LEDSettings', micMute, {'Mode' : 'Mic Mute'})
                self.WriteStatus('LEDSettings', micCustom, {'Mode' : 'Custom'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['LED Settings: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Enable',
                    False : 'Disable'
                }

                value = ValueStateValues[res['micCustom']['enabled']]
                self.WriteStatus('LEDSettingsCustom', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['LED Settings Custom: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['showFarendActivity']]
                self.WriteStatus('LEDShowFarEndActivity', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['LED Show Far End Activity: Invalid/unexpected response'])

    def SetLEDSettings(self, value, qualifier):

        ModeStates = {
            'Mic On'   : 'micOn',
            'Mic Mute' : 'micMute',
            'Custom'   : 'micCustom'
        }

        ValueStateValues = {
            'Blue': 'Blue',
            'Cyan': 'Cyan',
            'Green': 'Green',
            'Orange': 'Orange',
            'Pink': 'Pink',
            'Red': 'Red',
            'Light Green': 'LightGreen',
            'Yellow': 'Yellow'
        }

        if qualifier['Mode'] in ModeStates and value in ValueStateValues:
            data = {
                ModeStates[qualifier['Mode']] : {
                    'color' : ValueStateValues[value]
                }
            }
            LEDSettingsCmdString = 'api/device/leds/ring'
            self.__SetHelper('LEDSettings', value, qualifier, url=LEDSettingsCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLEDSettings')

    def UpdateLEDSettings(self, value, qualifier):

        self.UpdateLEDBrightness(value, None)

    def SetLEDSettingsCustom(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : True,
            'Disable' : False
        }

        if value in ValueStateValues:
            data = {
                'micCustom' : {
                    'enabled' : ValueStateValues[value]
                }
            }
            LEDSettingsCustomCmdString = 'api/device/leds/ring'
            self.__SetHelper('LEDSettingsCustom', value, qualifier, url=LEDSettingsCustomCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLEDSettingsCustom')

    def UpdateLEDSettingsCustom(self, value, qualifier):

        self.UpdateLEDBrightness(value, None)

    def SetLEDShowFarEndActivity(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'showFarendActivity' : ValueStateValues[value]
            }
            LEDShowFarEndActivityCmdString = 'api/device/leds/ring'
            self.__SetHelper('LEDShowFarEndActivity', value, qualifier, url=LEDShowFarEndActivityCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLEDShowFarEndActivity')

    def UpdateLEDShowFarEndActivity(self, value, qualifier):

        self.UpdateLEDBrightness(value, None)

    def SetLocalOutputDelay(self, value, qualifier):

        if 0 <= value <= 100:
            data = {
                'delay' : value
            }
            LocalOutputDelayCmdString = 'api/audio/outputs/dante/local'
            self.__SetHelper('LocalOutputDelay', value, qualifier, url=LocalOutputDelayCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLocalOutputDelay')

    def UpdateLocalOutputDelay(self, value, qualifier):

        self.UpdateLocalOutputGain(value, None)

    def SetLocalOutputGain(self, value, qualifier):

        if 0 <= value <= 24:
            data = {
                'gain' : value
            }
            LocalOutputGainCmdString = 'api/audio/outputs/dante/local'
            self.__SetHelper('LocalOutputGain', value, qualifier, url=LocalOutputGainCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLocalOutputGain')

    def UpdateLocalOutputGain(self, value, qualifier):
            
        LocalOutputGainCmdString = 'api/audio/outputs/dante/local'
        res = self.__UpdateHelper('LocalOutputGain', value, qualifier, url=LocalOutputGainCmdString)
        if res:
            try:
                value = int(res['gain'])
                if 0 <= value <= 24:
                    self.WriteStatus('LocalOutputGain', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Local Output Gain: Invalid/unexpected response'])

            try:
                value = int(res['delay'])
                if 0 <= value <= 100:
                    self.WriteStatus('LocalOutputDelay', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Local Output Delay: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['noiseGateEnabled']]
                self.WriteStatus('NoiseGateMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Noise Gate Mode: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['equalizerEnabled']]
                self.WriteStatus('LocalOutputSoundProfile', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Local Output Sound Profile: Invalid/unexpected response'])

            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['voiceLiftEnabled']]
                self.WriteStatus('TruVoiceliftMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['TruVoicelift Mode: Invalid/unexpected response'])

    def SetLocalOutputSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'equalizerEnabled' : ValueStateValues[value]
            }
            LocalOutputSoundProfileCmdString = 'api/audio/outputs/dante/local'
            self.__SetHelper('LocalOutputSoundProfile', value, qualifier, url=LocalOutputSoundProfileCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetLocalOutputSoundProfile')

    def UpdateLocalOutputSoundProfile(self, value, qualifier):

        self.UpdateLocalOutputGain(value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'enabled' : ValueStateValues[value]
            }
            MuteCmdString = 'api/audio/outputs/global/mute'
            self.__SetHelper('Mute', value, qualifier, url=MuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'api/audio/outputs/global/mute'
        res = self.__UpdateHelper('Mute', value, qualifier, url=MuteCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetMuteIntervalTime(self, value, qualifier):

        if 1 <= value <= 30:
            data = {
                'emergencyMuteTime' : value
            }
            MuteIntervalTimeCmdString = 'api/audio/voiceLift'
            self.__SetHelper('MuteIntervalTime', value, qualifier, url=MuteIntervalTimeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMuteIntervalTime')

    def UpdateMuteIntervalTime(self, value, qualifier):

        MuteIntervalTimeCmdString = 'api/audio/voiceLift'
        res = self.__UpdateHelper('MuteIntervalTime', value, qualifier, url=MuteIntervalTimeCmdString)
        if res:
            try:
                value = int(res['emergencyMuteTime'])
                if 1 <= value <= 30:
                    self.WriteStatus('MuteIntervalTime', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Mute Interval Time: Invalid/unexpected response'])

            try:
                value = int(res['emergencyMuteThreshold'])
                if -50 <= value <= -3:
                    self.WriteStatus('MuteThreshold', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Mute Threshold: Invalid/unexpected response'])

    def SetMuteThreshold(self, value, qualifier):

        if -50 <= value <= -3:
            data = {
                'emergencyMuteThreshold' : value
            }
            MuteThresholdCmdString = 'api/audio/voiceLift'
            self.__SetHelper('MuteThreshold', value, qualifier, url=MuteThresholdCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMuteThreshold')

    def UpdateMuteThreshold(self, value, qualifier):

        self.UpdateMuteIntervalTime(value, None)

    def SetNoiseGateHoldTime(self, value, qualifier):

        if 50 <= value <= 1000:
            data = {
                'holdTime' : value
            }
            NoiseGateHoldTimeCmdString = 'api/audio/noiseGate'
            self.__SetHelper('NoiseGateHoldTime', value, qualifier, url=NoiseGateHoldTimeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetNoiseGateHoldTime')

    def UpdateNoiseGateHoldTime(self, value, qualifier):

        NoiseGateHoldTimeCmdString = 'api/audio/noiseGate'
        res = self.__UpdateHelper('NoiseGateHoldTime', value, qualifier, url=NoiseGateHoldTimeCmdString)
        if res:
            try:
                value = int(res['holdTime'])
                if 50 <= value <= 1000:
                    self.WriteStatus('NoiseGateHoldTime', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Noise Gate Hold Time: Invalid/unexpected response'])

            try:
                value = int(res['threshold'])
                if -90 <= value <= -40:
                    self.WriteStatus('NoiseGateThreshold', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Noise Gate Threshold: Invalid/unexpected response'])

    def SetNoiseGateMode(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'noiseGateEnabled' : ValueStateValues[value]
            }
            NoiseGateModeCmdString = 'api/audio/outputs/dante/local'
            self.__SetHelper('NoiseGateMode', value, qualifier, url=NoiseGateModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetNoiseGateMode')

    def UpdateNoiseGateMode(self, value, qualifier):

        self.UpdateLocalOutputGain(value, None)
            
    def SetNoiseGateThreshold(self, value, qualifier):

        if -90 <= value <= -40:
            data = {
                'threshold' : value
            }
            NoiseGateThresholdCmdString = 'api/audio/noiseGate'
            self.__SetHelper('NoiseGateThreshold', value, qualifier, url=NoiseGateThresholdCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetNoiseGateThreshold')

    def UpdateNoiseGateThreshold(self, value, qualifier):

        self.UpdateNoiseGateHoldTime(value, None)

    def SetPriorityZoneAzimuth(self, value, qualifier):

        if 0 <= qualifier['Min'] <= 355 and 0 <= qualifier['Max'] <= 355:
            data = {
                "azimuth": {
                    "min": qualifier['Min'],
                    "max": qualifier['Max']
                }
            }
            PriorityZoneAzimuthCmdString = 'api/audio/inputs/microphone/priorityZones/0'
            self.__SetHelper('PriorityZoneAzimuth', value, qualifier, url=PriorityZoneAzimuthCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPriorityZoneAzimuth')

    def UpdatePriorityZoneAzimuthStatus(self, value, qualifier):

        self.UpdatePriorityZoneMode(value, None)

    def SetPriorityZoneElevation(self, value, qualifier):

        if 0 <= qualifier['Min'] <= 90 and 0 <= qualifier['Max'] <= 90:
            data = {
                "elevation": {
                    "min": qualifier['Min'],
                    "max": qualifier['Max']
                }
            }
            PriorityZoneElevationCmdString = 'api/audio/inputs/microphone/priorityZones/0'
            self.__SetHelper('PriorityZoneElevation', value, qualifier, url=PriorityZoneElevationCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPriorityZoneElevation')

    def UpdatePriorityZoneElevationStatus(self, value, qualifier):

        self.UpdatePriorityZoneMode(value, None)

    def SetPriorityZoneMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if value in ValueStateValues:
            data = {
                'enabled' : ValueStateValues[value]
            }
            PriorityZoneModeCmdString = 'api/audio/inputs/microphone/priorityZones/0'
            self.__SetHelper('PriorityZoneMode', value, qualifier, url=PriorityZoneModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPriorityZoneMode')

    def UpdatePriorityZoneMode(self, value, qualifier):
        
        PriorityZoneModeCmdString = 'api/audio/inputs/microphone/priorityZones/0'
        res = self.__UpdateHelper('PriorityZoneMode', value, qualifier, url=PriorityZoneModeCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'On',
                    False : 'Off'
                }
                value = ValueStateValues[res['enabled']]
                self.WriteStatus('PriorityZoneMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Priority Zone Mode: Invalid/unexpected response'])

            try:
                min = int(res['azimuth']['min'])
                max = int(res['azimuth']['max'])
                if 0 <= min <= 355 and 0 <= max <= 355:
                    self.WriteStatus('PriorityZoneAzimuthStatus', min, {'Type' : 'Min'})
                    self.WriteStatus('PriorityZoneAzimuthStatus', max, {'Type' : 'Max'})
            except (ValueError, IndexError, AttributeError):
                self.Error(['Priority Zone Azimuth Status: Invalid/unexpected response'])

            try:
                min = int(res['elevation']['min'])
                max = int(res['elevation']['max'])
                if 0 <= min <= 90 and 0 <= max <= 90:
                    self.WriteStatus('PriorityZoneElevationStatus', min, {'Type' : 'Min'})
                    self.WriteStatus('PriorityZoneElevationStatus', max, {'Type' : 'Max'})
            except (ValueError, IndexError, AttributeError):
                self.Error(['Priority Zone Elevation Status: Invalid/unexpected response'])

    def SetSensitivityThreshold(self, value, qualifier):

        ValueStateValues = {
            'Quiet'  : 'QuietRoom',
            'Normal' : 'NormalRoom',
            'Loud'   : 'LoudRoom'
        }

        if value in ValueStateValues:
            data = {
                'sourceDetectionThreshold' : ValueStateValues[value]
            }
            SensitivityThresholdCmdString = 'api/audio/inputs/microphone/beam'
            self.__SetHelper('SensitivityThreshold', value, qualifier, url=SensitivityThresholdCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSensitivityThreshold')

    def UpdateSensitivityThreshold(self, value, qualifier):

        self.UpdateInstallationType(value, None)

    def SetTruVoiceliftMode(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            data = {
                'voiceLiftEnabled' : ValueStateValues[value]
            }
            TruVoiceliftModeCmdString = 'api/audio/outputs/dante/local'
            self.__SetHelper('TruVoiceliftMode', value, qualifier, url=TruVoiceliftModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetTruVoiceliftMode')

    def UpdateTruVoiceliftMode(self, value, qualifier):

        self.UpdateLocalOutputGain(value, None)    

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Accept' : 'application/json',
            'Authorization' : self.base64Auth
        }

        if data:
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Accept' : 'application/json',
            'Authorization' : self.base64Auth
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, devicePassword, SSLVerifyMode)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])