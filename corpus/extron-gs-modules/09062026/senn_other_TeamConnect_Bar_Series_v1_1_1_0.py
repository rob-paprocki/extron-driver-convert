from extronlib.system import GetUnverifiedContext
from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
import base64
import json

class DeviceClass:
    def __init__(self, ipAddress, port, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if devicePassword:
            self.auth = base64.b64encode('api'.encode() + b':' + devicePassword.encode()).decode()
        else:
            self.auth = None
            self.Error(['Missing Password.'])
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
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
            'BluetoothInputLevel': { 'Status': {}},
            'BluetoothMode': { 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'DeviceProduct': { 'Status': {}},
            'DeviceSerialNumber': { 'Status': {}},
            'DeviceState': { 'Status': {}},
            'ExclusionZoneMode': {'Parameters':['Zone'], 'Status': {}},
            'Identify': { 'Status': {}},
            'InternalMicBeam': { 'Status': {}},
            'InternalMicCustomEQ': {'Parameters':['125','250','500','1K','2K','4K','8K'], 'Status': {}},
            'InternalMicCustomEQStatus': {'Parameters':['Frequency'], 'Status': {}},
            'InternalMicLevel': { 'Status': {}},
            'InternalMicNoiseGateMode': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'MicrophoneMute': { 'Status': {}},
            'Pan': { 'Status': {}},
            'PanTiltSpeed': { 'Status': {}},
            'PriorityZoneMode': { 'Status': {}},
            'SoundProfile': { 'Status': {}},
            'SpeakerCustomEQ': {'Parameters':['125','250','500','1K','2K','4K','8K'], 'Status': {}},
            'SpeakerCustomEQStatus': {'Parameters':['Frequency'], 'Status': {}},
            'SpeakerOutput': { 'Status': {}},
            'Tilt': { 'Status': {}},
            'USBInputLevel': { 'Status': {}},
            'Zoom': { 'Status': {}},
            'ZoomSpeed': { 'Status': {}}
        }

    def UpdateBluetoothInputLevel(self, value, qualifier):

        BluetoothInputLevelCmdString = 'api/audio/inputs/bluetooth'
        res = self.__UpdateHelper('BluetoothInputLevel', value, qualifier, url=BluetoothInputLevelCmdString)
        if res:
            try:
                value = int(res['level'])
                if -60 <= value <= 0:
                    self.WriteStatus('BluetoothInputLevel', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Bluetooth Input Level: Invalid/unexpected response'])

    def SetBluetoothMode(self, value, qualifier):

        ValueStateValues = {
            'Enabled'  : True,
            'Disabled' : False
        }

        if value in ValueStateValues:
            BluetoothModeCmdString = 'api/interfaces/bluetooth'
            data = {
                'enabled' : ValueStateValues[value]
            }
            self.__SetHelper('BluetoothMode', value, qualifier, url=BluetoothModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetBluetoothMode')

    def UpdateBluetoothMode(self, value, qualifier):

        BluetoothModeCmdString = 'api/interfaces/bluetooth'
        res = self.__UpdateHelper('BluetoothMode', value, qualifier, url=BluetoothModeCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'Enabled',
                    False : 'Disabled'
                }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('BluetoothMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Bluetooth Mode: Invalid/unexpected response'])

    def UpdateDeviceLocation(self, value, qualifier):

        DeviceLocationCmdString = 'api/device/site'
        res = self.__UpdateHelper('DeviceLocation', value, qualifier, url=DeviceLocationCmdString)
        if res:
            try:
                value = res['location']
                self.WriteStatus('DeviceLocation', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device Location: Invalid/unexpected response'])
            try:
                value = res['deviceName']
                self.WriteStatus('DeviceName', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device Name: Invalid/unexpected response'])

    def UpdateDeviceName(self, value, qualifier):

        self.UpdateDeviceLocation(value, qualifier)

    def UpdateDeviceProduct(self, value, qualifier):
            
        DeviceProductCmdString = 'api/device/identity'
        res = self.__UpdateHelper('DeviceProduct', value, qualifier, url=DeviceProductCmdString)
        if res:
            try:
                value = res['product']
                self.WriteStatus('DeviceProduct', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device Product: Invalid/unexpected response'])
            try:
                value = res['serial']
                self.WriteStatus('DeviceSerialNumber', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device Serial Number: Invalid/unexpected response'])

    def UpdateDeviceSerialNumber(self, value, qualifier):

        self.UpdateDeviceProduct(value, qualifier)

    def UpdateDeviceState(self, value, qualifier):

        DeviceStateCmdString = 'api/device/state'
        res = self.__UpdateHelper('DeviceState', value, qualifier, url=DeviceStateCmdString)
        if res:
            try:
                value = res['state']
                self.WriteStatus('DeviceState', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Device State: Invalid/unexpected response'])

    def SetExclusionZoneMode(self, value, qualifier):

        ZoneStates = {
            '1' : '0',
            '2' : '1',
            '3' : '2'
        }

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if qualifier['Zone'] in ZoneStates and value in ValueStateValues:
            ExclusionZoneModeCmdString = 'api/audio/inputs/internalMic/exclusionZones/{0}'.format(ZoneStates[qualifier['Zone']])
            data = {
                "enabled": ValueStateValues[value]
            }
            self.__SetHelper('ExclusionZoneMode', value, qualifier, url=ExclusionZoneModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetExclusionZoneMode')

    def UpdateExclusionZoneMode(self, value, qualifier):

        ZoneStates = {
            '1' : '0',
            '2' : '1',
            '3' : '2'
        }

        if qualifier['Zone'] in ZoneStates:
            ExclusionZoneModeCmdString = 'api/audio/inputs/internalMic/exclusionZones/{0}'.format(ZoneStates[qualifier['Zone']])
            res = self.__UpdateHelper('ExclusionZoneMode', value, qualifier, url=ExclusionZoneModeCmdString)
            if res:
                try:
                    ValueStateValues = {
                        True  : 'On',
                        False : 'Off'
                    }

                    value = ValueStateValues[res['enabled']]
                    self.WriteStatus('ExclusionZoneMode', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Exclusion Zone Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateExclusionZoneMode')

    def SetIdentify(self, value, qualifier):

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if value in ValueStateValues:
            IdentifyCmdString = 'api/device/identification'
            data = {
                "visual": ValueStateValues[value]
            }
            self.__SetHelper('Identify', value, qualifier, url=IdentifyCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetIdentify')

    def UpdateIdentify(self, value, qualifier):

        IdentifyCmdString = 'api/device/identification'
        res = self.__UpdateHelper('Identify', value, qualifier, url=IdentifyCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'On',
                    False : 'Off'
                }

                value = ValueStateValues[res['visual']]
                self.WriteStatus('Identify', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Identify: Invalid/unexpected response'])

    def UpdateInternalMicBeam(self, value, qualifier):

        InternalMicBeamCmdString = 'api/audio/inputs/internalMic/beam'
        res = self.__UpdateHelper('InternalMicBeam', value, qualifier, url=InternalMicBeamCmdString)
        if res:
            try:
                value = int(res['position'])
                if 16 <= value <= 165:
                    self.WriteStatus('InternalMicBeam', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Internal Mic Beam: Invalid/unexpected response'])

    def SetInternalMicCustomEQ(self, value, qualifier):

        if -8 <= qualifier['125'] <= 8 and -8 <= qualifier['250'] <= 8 and -8 <= qualifier['500'] <= 8 and -8 <= qualifier['1K'] <= 8 and -8 <= qualifier['2K'] <= 8 and -8 <= qualifier['4K'] <= 8 and -8 <= qualifier['8K'] <= 8:
            InternalMicCustomEQCmdString = 'api/audio/inputs/internalMic/customEq'
            data = [qualifier['125'], qualifier['250'], qualifier['500'], qualifier['1K'], qualifier['2K'], qualifier['4K'], qualifier['8K']]
            self.__SetHelper('InternalMicCustomEQ', value, qualifier, url=InternalMicCustomEQCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetInternalMicCustomEQ')

    def UpdateInternalMicCustomEQStatus(self, value, qualifier):

        FrequencyStates = ['125', '250', '500', '1K', '2K', '4K', '8K']
        if qualifier['Frequency'] in FrequencyStates:
            InternalMicCustomEQStatusCmdString = 'api/audio/inputs/internalMic/customEq'
            res = self.__UpdateHelper('InternalMicCustomEQStatus', value, qualifier, url=InternalMicCustomEQStatusCmdString)
            if res:
                try:
                    for index in range(len(res)):
                        self.WriteStatus('InternalMicCustomEQStatus', res[index], {'Frequency' : FrequencyStates[index]})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Internal Mic Custom EQ Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInternalMicCustomEQStatus')

    def UpdateInternalMicLevel(self, value, qualifier):

        InternalMicLevelCmdString = 'api/audio/inputs/internalMic/level'
        res = self.__UpdateHelper('InternalMicLevel', value, qualifier, url=InternalMicLevelCmdString)
        if res:
            try:
                value = int(res['peak'])
                if -60 <= value <= 0:
                    self.WriteStatus('InternalMicLevel', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Internal Mic Level: Invalid/unexpected response'])

    def SetInternalMicNoiseGateMode(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            InternalMicNoiseGateModeCmdString = 'api/audio/inputs/internalMic/noiseGate'
            data = {
                'enabled' : ValueStateValues[value]
            }
            self.__SetHelper('InternalMicNoiseGateMode', value, qualifier, url=InternalMicNoiseGateModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetInternalMicNoiseGateMode')

    def UpdateInternalMicNoiseGateMode(self, value, qualifier):

        InternalMicNoiseGateModeCmdString = 'api/audio/inputs/internalMic/noiseGate'
        res = self.__UpdateHelper('InternalMicNoiseGateMode', value, qualifier, url=InternalMicNoiseGateModeCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('InternalMicNoiseGateMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Internal Mic Noise Gate Mode: Invalid/unexpected response'])

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
            LEDBrightnessCmdString = 'api/device/leds/ring'
            data = {
                'brightness' : ValueStateValues[value]
            }
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

    def SetMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            'Activated'   : True,
            'Deactivated' : False
        }

        if value in ValueStateValues:
            MicrophoneMuteCmdString = 'api/audio/inputs/internalMic/mute'
            data = {
                'enabled' : ValueStateValues[value]
            }
            self.__SetHelper('MicrophoneMute', value, qualifier, url=MicrophoneMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMicrophoneMute')

    def UpdateMicrophoneMute(self, value, qualifier):

        MicrophoneMuteCmdString = 'api/audio/inputs/internalMic/mute'
        res = self.__UpdateHelper('MicrophoneMute', value, qualifier, url=MicrophoneMuteCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'Activated',
                    False : 'Deactivated'
                }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('MicrophoneMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Microphone Mute: Invalid/unexpected response'])

    def SetPan(self, value, qualifier):

        if -25 <= value <= 25:
            PanCmdString = 'api/video/input/internalCamera/movement'
            data = {
                'panPosition' : value
            }
            self.__SetHelper('Pan', value, qualifier, url=PanCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPan')

    def UpdatePan(self, value, qualifier):

        self.UpdatePanTiltSpeed(value, qualifier)

    def SetPanTiltSpeed(self, value, qualifier):

        ValueStateValues = ['Slow', 'Medium', 'Fast']

        if value in ValueStateValues:
            PanTiltSpeedCmdString = 'api/video/input/internalCamera/movement'
            data = {
                'panTiltSpeed' : value
            }
            self.__SetHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPanTiltSpeed')

    def UpdatePanTiltSpeed(self, value, qualifier):

        PanTiltSpeedCmdString = 'api/video/input/internalCamera/movement'
        res = self.__UpdateHelper('PanTiltSpeed', value, qualifier, url=PanTiltSpeedCmdString)
        if res:
            try:
                value = int(res['panPosition'])
                if -25 <= value <= 25:
                    self.WriteStatus('Pan', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Pan: Invalid/unexpected response'])
            try:
                ValueStateValues = ['Slow', 'Medium', 'Fast']

                value = res['panTiltSpeed']
                if value in ValueStateValues:
                    self.WriteStatus('PanTiltSpeed', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Pan Tilt Speed: Invalid/unexpected response'])
            try:
                value = int(res['tiltPosition'])
                if -25 <= value <= 25:
                    self.WriteStatus('Tilt', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Tilt: Invalid/unexpected response'])
            try:
                value = int(res['zoomPosition'])
                if 100 <= value <= 500:
                    self.WriteStatus('Zoom', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Zoom: Invalid/unexpected response'])
            try:
                ValueStateValues = ['Slow', 'Medium', 'Fast']
                value = res['zoomSpeed']
                if value in ValueStateValues:
                    self.WriteStatus('ZoomSpeed', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Zoom Speed: Invalid/unexpected response'])

    def SetPriorityZoneMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if value in ValueStateValues:
            PriorityZoneModeCmdString = 'api/audio/inputs/internalMic/priorityZones/0'
            data = {
                "enabled" : ValueStateValues[value]
            }
            self.__SetHelper('PriorityZoneMode', value, qualifier, url=PriorityZoneModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPriorityZoneMode')

    def UpdatePriorityZoneMode(self, value, qualifier):

        PriorityZoneModeCmdString = 'api/audio/inputs/internalMic/priorityZones'
        res = self.__UpdateHelper('PriorityZoneMode', value, qualifier, url=PriorityZoneModeCmdString)
        if res:
            try:
                ValueStateValues = {
                    True  : 'On',
                    False : 'Off'
                }

                value = ValueStateValues[res[0]['enabled']]
                self.WriteStatus('PriorityZoneMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Priority Zone Mode: Invalid/unexpected response'])

    def SetSoundProfile(self, value, qualifier):

        ValueStateValues = {
            'Wallmount'     : 'Wallmount',
            'Table Top'     : 'TableTop',
            'Under Display' : 'UnderDisplay',
            'Above Display' : 'AboveDisplay',
            'Free Standing' : 'FreeStanding',
            'Custom'        : 'Custom'
        }

        if value in ValueStateValues:
            SoundProfileCmdString = 'api/audio/soundProfile'
            data = {
                "preset": ValueStateValues[value]
            }
            self.__SetHelper('SoundProfile', value, qualifier, url=SoundProfileCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSoundProfile')

    def UpdateSoundProfile(self, value, qualifier):

        SoundProfileCmdString = 'api/audio/soundProfile'
        res = self.__UpdateHelper('SoundProfile', value, qualifier, url=SoundProfileCmdString)
        if res:
            try:
                ValueStateValues = {
                    'Wallmount'     : 'Wallmount',
                    'TableTop'      : 'Table Top',
                    'UnderDisplay'  : 'Under Display',
                    'AboveDisplay'  : 'Above Display',
                    'FreeStanding'  : 'Free Standing',
                    'Custom'        : 'Custom'
                }

                value = ValueStateValues[res['preset']]
                self.WriteStatus('SoundProfile', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Sound Profile: Invalid/unexpected response'])

    def SetSpeakerCustomEQ(self, value, qualifier):

        if -8 <= qualifier['125'] <= 8 and -8 <= qualifier['250'] <= 8 and -8 <= qualifier['500'] <= 8 and -8 <= qualifier['1K'] <= 8 and -8 <= qualifier['2K'] <= 8 and -8 <= qualifier['4K'] <= 8 and -8 <= qualifier['8K'] <= 8:
            SpeakerCustomEQCmdString = 'api/audio/outputs/speaker/customEq'
            data = [qualifier['125'], qualifier['250'], qualifier['500'], qualifier['1K'], qualifier['2K'], qualifier['4K'], qualifier['8K']]
            self.__SetHelper('SpeakerCustomEQ', value, qualifier, url=SpeakerCustomEQCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSpeakerCustomEQ')

    def UpdateSpeakerCustomEQStatus(self, value, qualifier):

        FrequencyStates = ['125', '250', '500', '1K', '2K', '4K', '8K']

        if qualifier['Frequency'] in FrequencyStates:
            SpeakerCustomEQStatusCmdString = 'api/audio/outputs/speaker/customEq'
            res = self.__UpdateHelper('SpeakerCustomEQStatus', value, qualifier, url=SpeakerCustomEQStatusCmdString)
            if res:
                try:
                    for index in range(len(res)):
                        self.WriteStatus('SpeakerCustomEQStatus', res[index], {'Frequency' : FrequencyStates[index]})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Speaker Custom EQ Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerCustomEQStatus')

    def SetSpeakerOutput(self, value, qualifier):

        if 0 <= value <= 100:
            SpeakerOutputCmdString = 'api/audio/outputs/speaker'
            data = {
                "volume": value
            }
            self.__SetHelper('SpeakerOutput', value, qualifier, url=SpeakerOutputCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSpeakerOutput')

    def UpdateSpeakerOutput(self, value, qualifier):

        SpeakerOutputCmdString = 'api/audio/outputs/speaker'
        res = self.__UpdateHelper('SpeakerOutput', value, qualifier, url=SpeakerOutputCmdString)
        if res:
            try:
                value = int(res['volume'])
                if 0 <= value <= 100:
                    self.WriteStatus('SpeakerOutput', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Speaker Output: Invalid/unexpected response'])

    def SetTilt(self, value, qualifier):

        if -25 <= value <= 25:
            TiltCmdString = 'api/video/input/internalCamera/movement'
            data = {
                'tiltPosition' : value
            }
            self.__SetHelper('Tilt', value, qualifier, url=TiltCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetTilt')

    def UpdateTilt(self, value, qualifier):

        self.UpdatePanTiltSpeed(value, qualifier)

    def UpdateUSBInputLevel(self, value, qualifier):

        USBInputLevelCmdString = 'api/audio/inputs/usb'
        res = self.__UpdateHelper('USBInputLevel', value, qualifier, url=USBInputLevelCmdString)
        if res:
            try:
                value = int(res['level'])
                if -60 <= value <= 0:
                    self.WriteStatus('USBInputLevel', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['USB Input Level: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        if 100 <= value <= 500:
            ZoomCmdString = 'api/video/input/internalCamera/movement'
            data = {
                'zoomPosition' : value
            }
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        self.UpdatePanTiltSpeed(value, qualifier)

    def SetZoomSpeed(self, value, qualifier):

        ValueStateValues = ['Slow', 'Medium', 'Fast']

        if value in ValueStateValues:
            ZoomSpeedCmdString = 'api/video/input/internalCamera/movement'
            data = {
                'zoomSpeed' : value
            }
            self.__SetHelper('ZoomSpeed', value, qualifier, url=ZoomSpeedCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetZoomSpeed')

    def UpdateZoomSpeed(self, value, qualifier):

        self.UpdatePanTiltSpeed(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        if res:
            res = json.loads(res)
        else:
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'

        headers = {
            'Accept'        : 'application/json',
            'Content-Type'  : 'application/json',
            'Authorization' : 'Basic {}'.format(self.auth)
        }

        if data:
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'

        headers = {
            'Accept'        : 'application/json',
            'Authorization' : 'Basic {}'.format(self.auth)
        }        
        
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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