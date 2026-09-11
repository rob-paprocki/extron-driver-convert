from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

import json
import struct
from base64 import encodebytes as base64encode
import random
import array
import re

from uuid import uuid4
import hashlib

from extronlib import Version

try:
    from Extron import Platform
    platform = Platform()
except ImportError:
    platform = 'Pro'

minimumVersion = (3, 4, 6)
version = tuple(int(i) for i in Version().split('.'))

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

STREAM = 0x0
TEXT = 0x1
BINARY = 0x2
CLOSE = 0x8
PING = 0x9
PONG = 0xA

def _mask(_m, _d):
    for i in range(len(_d)):
        _d[i] ^= _m[i % 4]
    return _d.tobytes()

class DeviceClass:

    def __init__(self, IPAddress):

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
        self._devicePassword = 'Bose123!'
        self.password_md5 = hashlib.md5(self._devicePassword.encode(encoding='iso-8859-1')).hexdigest().upper()
        self.Models = {
            'VB1': self.bose_19_5035_vb1,
            'VB-S': self.bose_19_5035_vbs,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Autoframing': { 'Status': {}},
            'AutoframingBorderSize': { 'Status': {}},
            'AutoframingHeadroomAdjustment': { 'Status': {}},
            'AutoframingPanTiltSpeed': { 'Status': {}},
            'AutoframingZoomSpeed': { 'Status': {}},
            'Bluetooth': { 'Status': {}},
            'BluetoothButton': { 'Status': {}},
            'BluetoothConnection': { 'Status': {}},
            'BluetoothPairing': { 'Status': {}},
            'BluetoothStream': { 'Status': {}},
            'Building': { 'Status': {}},
            'CameraState': { 'Status': {}},
            'EthernetMACAddress': { 'Status': {}},
            'EthernetState': { 'Status': {}},
            'EthernetStaticIPAddress': { 'Status': {}},
            'Floor': { 'Status': {}},
            'GPIMute': { 'Status': {}},
            'HDMIEnable': { 'Status': {}},
            'LoudspeakerLevel': { 'Status': {}},
            'LoudspeakerMute': { 'Status': {}},
            'LoudspeakerVolume': { 'Status': {}},
            'MicrophoneLevel': { 'Status': {}},
            'MicrophoneMute': { 'Status': {}},
            'Pan': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'Room': { 'Status': {}},
            'SystemFirmwareVersion': { 'Status': {}},
            'SystemName': { 'Status': {}},
            'SystemReady': { 'Status': {}},
            'SystemSerialNumber': { 'Status': {}},
            'Tilt': { 'Status': {}},
            'UltrasoundCommand': { 'Status': {}},
            'USBCallStatus': { 'Status': {}},
            'USBConnection': { 'Status': {}},
            'WiFiMACAddress': { 'Status': {}},
            'WiFiState': { 'Status': {}},
            'WiFiStaticIPAddress': { 'Status': {}},
            'Zoom': { 'Status': {}}
        }

        # Websocket Variables
        self.Authenticated = False
        self.ipAddress = IPAddress
        self.uri = '/websocket'
        self._ReceiveSocketData = None
        self.ReceiveData = self.__ReceiveData
        self._receiveBuffer = None

        self._handshake = (
            "GET %(uri)s HTTP/1.1\r\n"
            "Host: %(ipAddress)s\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Origin: https://%(origin)s\r\n"
            "Sec-WebSocket-Key: %(randomstring)s\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"autoframing":{"19":"([01])"}}'), self.__MatchAutoframing, None)
            self.AddMatchString(re.compile(b'{"autoframing":{"84":"(small|normal|large)"}}'), self.__MatchAutoframingBorderSize, None)
            self.AddMatchString(re.compile(b'{"autoframing":{"85":"(sitting|standing)"}}'), self.__MatchAutoframingHeadroomAdjustment, None)
            self.AddMatchString(re.compile(b'{"autoframing":{"82":"(slow|normal|fast)"}}'), self.__MatchAutoframingPanTiltSpeed, None)
            self.AddMatchString(re.compile(b'{"autoframing":{"83":"(slow|normal|fast)"}}'), self.__MatchAutoframingZoomSpeed, None)
            self.AddMatchString(re.compile(b'{"behavior":{"3A":"([01])"}}'), self.__MatchBluetooth, None)
            self.AddMatchString(re.compile(b'{"behavior":{"3C":"([01])"}}'), self.__MatchBluetoothButton, None)
            self.AddMatchString(re.compile(b'{"bluetooth":{"6B":"([01])"}}'), self.__MatchBluetoothConnection, None)
            self.AddMatchString(re.compile(b'{"bluetooth":{"14":"([01])"}}'), self.__MatchBluetoothPairing, None)
            self.AddMatchString(re.compile(b'{"bluetooth":{"C2":"([01])"}}'), self.__MatchBluetoothStream, None)
            self.AddMatchString(re.compile(b'{"system":{"28":"(.*?)"}}'), self.__MatchBuilding, None)
            self.AddMatchString(re.compile(b'{"camera":{"60":"(active|inactive|upgrading)"}}'), self.__MatchCameraState, None)
            self.AddMatchString(re.compile(b'{"network":{"80":"(.*?)"}}'), self.__MatchEthernetMACAddress, None)
            self.AddMatchString(re.compile(b'{"network":{"7F":"(idle|failure|association|configuration|ready|disconnect|online)"}}'), self.__MatchEthernetState, None)
            self.AddMatchString(re.compile(b'{"network":{"75":"(.*?)"}}'), self.__MatchEthernetStaticIPAddress, None)
            self.AddMatchString(re.compile(b'{"system":{"27":"(.*?)"}}'), self.__MatchFloor, None)
            self.AddMatchString(re.compile(b'{"system":{"C7":"([01])"}}'), self.__MatchGPIMute, None)
            self.AddMatchString(re.compile(b'{"behavior":{"C9":"([01])"}}'), self.__MatchHDMIEnable, None)
            self.AddMatchString(re.compile(b'{"audio":{"48":"(\d+)"}}'), self.__MatchLoudspeakerLevel, None)
            self.AddMatchString(re.compile(b'{"audio":{"33":"([01])"}}'), self.__MatchLoudspeakerMute, None)
            self.AddMatchString(re.compile(b'{"audio":{"3":"(\d+)"}}'), self.__MatchLoudspeakerVolume, None)
            self.AddMatchString(re.compile(b'{"audio":{"47":"(\d+)"}}'), self.__MatchMicrophoneLevel, None)
            self.AddMatchString(re.compile(b'{"audio":{"2":"([01])"}}'), self.__MatchMicrophoneMute, None)
            self.AddMatchString(re.compile(b'{"camera":{"7":"(-?\d+)"}}'), self.__MatchPan, None)
            self.AddMatchString(re.compile(b'{"system":{"26":"(.*?)"}}'), self.__MatchRoom, None)
            self.AddMatchString(re.compile(b'{"system":{"16":"(.*?)"}}'), self.__MatchSystemFirmwareVersion, None)
            self.AddMatchString(re.compile(b'{"system":{"25":"(.*?)"}}'), self.__MatchSystemName, None)
            self.AddMatchString(re.compile(b'{"system":{"BF":"([01])"}}'), self.__MatchSystemReady, None)
            self.AddMatchString(re.compile(b'{"system":{"10":"(.*?)"}}'), self.__MatchSystemSerialNumber, None)
            self.AddMatchString(re.compile(b'{"camera":{"8":"(-?\d+)"}}'), self.__MatchTilt, None)
            self.AddMatchString(re.compile(b'{"usb":{"37":"([01])"}}'), self.__MatchUSBCallStatus, None)
            self.AddMatchString(re.compile(b'{"usb":{"36":"([01])"}}'), self.__MatchUSBConnection, None)
            self.AddMatchString(re.compile(b'{"wifi":{"AC":"(.*?)"}}'), self.__MatchWiFiMACAddress, None)
            self.AddMatchString(re.compile(b'{"wifi":{"B0":"(idle|failure|association|configuration|ready|disconnect|online)"}}'), self.__MatchWiFiState, None)
            self.AddMatchString(re.compile(b'{"wifi":{"A2":"(.*?)"}}'), self.__MatchWiFiStaticIPAddress, None)
            self.AddMatchString(re.compile(b'{"camera":{"6":"(\d+)"}}'), self.__MatchZoom, None)

            self.AddMatchString(re.compile(b'{"behavior":{"45":"([01])"}}'), self.__MatchMeterEvents, None)

        self.meter_events_enabled = False

    @property
    def devicePassword(self):
        return self._devicePassword

    @devicePassword.setter
    def devicePassword(self, value):
        if value:
            self._devicePassword = value
            self.password_md5 = hashlib.md5(self._devicePassword.encode(encoding='iso-8859-1')).hexdigest().upper()
        else:
            self.print('Password required.')

    def SetLoginHandShake(self, value, url):
        handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
        self.Send(handshake)

    def getID(self):
        if self.Model == 'VB1':
            return 'WEB-{}'.format(uuid4().hex[:4])
        else:
            return 'TST-{}'.format(hex(random.randint(0, 0xFFFFFF))[2:])

    def build(self, action, data):

        to_return = {
            'action':   action,
            'password': self.password_md5,
            'id':       self.getID(),
            'data':     data
        }

        return to_return

    def enable_meter_events(self):
        if not self.meter_events_enabled:
            data = {
                'behavior': {
                    '45': '1'
                }
            }

            self.meter_events_enabled = True
            return json.dumps(self.build('perform', data))
        else:
            data = {
                'behavior': {
                    '45': ''
                }
            }
            return json.dumps(self.build('retrieve', data))

    def __MatchMeterEvents(self, match, tag):

        ValueStateValues = {
            '1': True,
            '0': False
        }

        self.meter_events_enabled = ValueStateValues[match.group(1).decode()]

    def SetAutoframing(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'autoframing': {
                    '19': '{}'.format(ValueStateValues[value])
                }
            }

            AutoframingCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('Autoframing', AutoframingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframing')

    def UpdateAutoframing(self, value, qualifier):

        data = {
            'autoframing': {
                '19': ''
            }
        }
        AutoframingCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Autoframing', AutoframingCmdString, value, qualifier)

    def __MatchAutoframing(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Autoframing', value, None)

    def SetAutoframingBorderSize(self, value, qualifier):

        ValueStateValues = [
            'Small',
            'Normal',
            'Large'
        ]

        if value in ValueStateValues:
            data = {
                'autoframing': {
                    '84': '{}'.format(value.lower())
                }
            }

            AutoframingBorderSizeCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('AutoframingBorderSize', AutoframingBorderSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframingBorderSize')

    def UpdateAutoframingBorderSize(self, value, qualifier):

        data = {
            'autoframing': {
                '84': ''
            }
        }

        AutoframingBorderSizeCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('AutoframingBorderSize', AutoframingBorderSizeCmdString, value, qualifier)

    def __MatchAutoframingBorderSize(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoframingBorderSize', value, None)

    def SetAutoframingHeadroomAdjustment(self, value, qualifier):

        ValueStateValues = [
            'Sitting',
            'Standing'
        ]

        if value in ValueStateValues:
            data = {
                'autoframing': {
                    '85': '{}'.format(value.lower())
                }
            }

            AutoframingHeadroomAdjustmentCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('AutoframingHeadroomAdjustment', AutoframingHeadroomAdjustmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframingHeadroomAdjustment')

    def UpdateAutoframingHeadroomAdjustment(self, value, qualifier):

        data = {
            'autoframing': {
                '85': ''
            }
        }

        AutoframingHeadroomAdjustmentCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('AutoframingHeadroomAdjustment', AutoframingHeadroomAdjustmentCmdString, value, qualifier)

    def __MatchAutoframingHeadroomAdjustment(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoframingHeadroomAdjustment', value, None)

    def SetAutoframingPanTiltSpeed(self, value, qualifier):

        ValueStateValues = [
            'Slow',
            'Normal',
            'Fast'
        ]

        if value in ValueStateValues:
            data = {
                'autoframing': {
                    '82': '{}'.format(value.lower())
                }
            }

            AutoframingPanTiltSpeedCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('AutoframingPanTiltSpeed', AutoframingPanTiltSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframingPanTiltSpeed')

    def UpdateAutoframingPanTiltSpeed(self, value, qualifier):

        data = {
            'autoframing': {
                '82': ''
            }
        }

        AutoframingPanTiltSpeedCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('AutoframingPanTiltSpeed', AutoframingPanTiltSpeedCmdString, value, qualifier)

    def __MatchAutoframingPanTiltSpeed(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoframingPanTiltSpeed', value, None)

    def SetAutoframingZoomSpeed(self, value, qualifier):

        ValueStateValues = [
            'Slow',
            'Normal',
            'Fast'
        ]

        if value in ValueStateValues:
            data = {
                'autoframing': {
                    '83': '{}'.format(value.lower())
                }
            }

            AutoframingZoomSpeedCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('AutoframingZoomSpeed', AutoframingZoomSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoframingZoomSpeed')

    def UpdateAutoframingZoomSpeed(self, value, qualifier):

        data = {
            'autoframing': {
                '83': ''
            }
        }

        AutoframingZoomSpeedCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('AutoframingZoomSpeed', AutoframingZoomSpeedCmdString, value, qualifier)

    def __MatchAutoframingZoomSpeed(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoframingZoomSpeed', value, None)

    def SetBluetooth(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'behavior': {
                    '3A': '{}'.format(ValueStateValues[value])
                }
            }

            BluetoothCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('Bluetooth', BluetoothCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetooth')

    def UpdateBluetooth(self, value, qualifier):

        data = {
            'behavior': {
                '3A': ''
            }
        }

        BluetoothCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Bluetooth', BluetoothCmdString, value, qualifier)

    def __MatchBluetooth(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Bluetooth', value, None)

    def SetBluetoothButton(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'behavior': {
                    '3C': '{}'.format(ValueStateValues[value])
                }
            }

            BluetoothButtonCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('BluetoothButton', BluetoothButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetoothButton')

    def UpdateBluetoothButton(self, value, qualifier):

        data = {
            'behavior': {
                '3C': ''
            }
        }

        BluetoothButtonCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('BluetoothButton', BluetoothButtonCmdString, value, qualifier)

    def __MatchBluetoothButton(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothButton', value, None)

    def UpdateBluetoothConnection(self, value, qualifier):

        data = {
            'bluetooth': {
                '6B': ''
            }
        }

        BluetoothConnectionCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('BluetoothConnection', BluetoothConnectionCmdString, value, qualifier)

    def __MatchBluetoothConnection(self, match, tag):

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothConnection', value, None)

    def SetBluetoothPairing(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'bluetooth': {
                    '14': '{}'.format(ValueStateValues[value])
                }
            }

            BluetoothPairingCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('BluetoothPairing', BluetoothPairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetoothPairing')

    def UpdateBluetoothPairing(self, value, qualifier):

        data = {
            'bluetooth': {
                '14': ''
            }
        }

        BluetoothPairingCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('BluetoothPairing', BluetoothPairingCmdString, value, qualifier)

    def __MatchBluetoothPairing(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothPairing', value, None)

    def UpdateBluetoothStream(self, value, qualifier):

        data = {
            'bluetooth': {
                'C2': ''
            }
        }

        BluetoothStreamCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('BluetoothStream', BluetoothStreamCmdString, value, qualifier)

    def __MatchBluetoothStream(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothStream', value, None)

    def UpdateBuilding(self, value, qualifier):

        data = {
            'system': {
                '28': ''
            }
        }

        BuildingCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Building', BuildingCmdString, value, qualifier)

    def __MatchBuilding(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Building', value, None)

    def UpdateCameraState(self, value, qualifier):

        data = {
            'camera': {
                '60': ''
            }
        }

        CameraStateCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('CameraState', CameraStateCmdString, value, qualifier)

    def __MatchCameraState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('CameraState', value, None)

    def UpdateEthernetMACAddress(self, value, qualifier):

        if self.Model == 'VB1':
            data = {
                'network': {
                    '80': ''
                }
            }

            EthernetMACAddressCmdString = json.dumps(self.build('retrieve', data))
            self.__UpdateHelper('EthernetMACAddress', EthernetMACAddressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEthernetMACAddress')

    def __MatchEthernetMACAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('EthernetMACAddress', value, None)

    def UpdateEthernetState(self, value, qualifier):

        if self.Model == 'VB1':
            data = {
                'network': {
                    '7F': ''
                }
            }

            EthernetStateCmdString = json.dumps(self.build('retrieve', data))
            self.__UpdateHelper('EthernetState', EthernetStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEthernetState')

    def __MatchEthernetState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('EthernetState', value, None)

    def UpdateEthernetStaticIPAddress(self, value, qualifier):

        if self.Model == 'VB1':
            data = {
                'network': {
                    '75': ''
                }
            }

            EthernetStaticIPAddressCmdString = json.dumps(self.build('retrieve', data))
            self.__UpdateHelper('EthernetStaticIPAddress', EthernetStaticIPAddressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEthernetStaticIPAddress')

    def __MatchEthernetStaticIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('EthernetStaticIPAddress', value, None)

    def UpdateFloor(self, value, qualifier):

        data = {
            'system': {
                '27': ''
            }
        }

        FloorCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Floor', FloorCmdString, value, qualifier)

    def __MatchFloor(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Floor', value, None)

    def UpdateGPIMute(self, value, qualifier):

        if self.Model == 'VB1':
            data = {
                'system': {
                    'C7': ''
                }
            }

            GPIMuteCmdString = json.dumps(self.build('retrieve', data))
            self.__UpdateHelper('GPIMute', GPIMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGPIMute')

    def __MatchGPIMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GPIMute', value, None)

    def SetHDMIEnable(self, value, qualifier):
        if self.Model == 'VB1':
            ValueStateValues = {
                'On':   '1',
                'Off':  '0'
            }

            if value in ValueStateValues:
                data = {
                    'behavior': {
                        'C9': '{}'.format(ValueStateValues[value])
                    }
                }

                HDMIEnableCmdString = json.dumps(self.build('update', data))
                self.__SetHelper('HDMIEnable', HDMIEnableCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetHDMIEnable')
        else:
            self.Discard('Invalid Command for SetHDMIEnable')

    def UpdateHDMIEnable(self, value, qualifier):

        if self.Model == 'VB1':
            data = {
                'behavior': {
                    'C9': ''
                }
            }

            HDMIEnableCmdString = json.dumps(self.build('retrieve', data))
            self.__UpdateHelper('HDMIEnable', HDMIEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIEnable')

    def __MatchHDMIEnable(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIEnable', value, None)

    def UpdateLoudspeakerLevel(self, value, qualifier):

        data = {
            'audio': {
                '48': ''
            }
        }

        LoudspeakerLevelCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('LoudspeakerLevel', LoudspeakerLevelCmdString, value, qualifier)
        cmd = self.enable_meter_events()
        if cmd:
            self.__UpdateHelper('LoudspeakerLevel', cmd, value, qualifier)

    def __MatchLoudspeakerLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LoudspeakerLevel', value, None)

    def SetLoudspeakerMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'audio': {
                    '33': '{}'.format(ValueStateValues[value])
                }
            }

            LoudspeakerMuteCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('LoudspeakerMute', LoudspeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoudspeakerMute')

    def UpdateLoudspeakerMute(self, value, qualifier):

        data = {
            'audio': {
                '33': ''
            }
        }

        LoudspeakerMuteCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('LoudspeakerMute', LoudspeakerMuteCmdString, value, qualifier)

    def __MatchLoudspeakerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LoudspeakerMute', value, None)

    def SetLoudspeakerVolume(self, value, qualifier):

        if 0 <= value <= 100:
            data = {
                'audio': {
                    '3': '{}'.format(value)
                }
            }

            LoudspeakerVolumeCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('LoudspeakerVolume', LoudspeakerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoudspeakerVolume')

    def UpdateLoudspeakerVolume(self, value, qualifier):

        data = {
            'audio': {
                '3': ''
            }
        }

        LoudspeakerVolumeCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('LoudspeakerVolume', LoudspeakerVolumeCmdString, value, qualifier)

    def __MatchLoudspeakerVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LoudspeakerVolume', value, None)

    def UpdateMicrophoneLevel(self, value, qualifier):

        data = {
            'audio': {
                '47': ''
            }
        }

        MicrophoneLevelCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('MicrophoneLevel', MicrophoneLevelCmdString, value, qualifier)
        cmd = self.enable_meter_events()
        if cmd:
            self.__UpdateHelper('MicrophoneLevel', cmd, value, qualifier)

    def __MatchMicrophoneLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('MicrophoneLevel', value, None)

    def SetMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            data = {
                'audio': {
                    '2': '{}'.format(ValueStateValues[value])
                }
            }

            MicrophoneMuteCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMute')

    def UpdateMicrophoneMute(self, value, qualifier):

        data = {
            'audio': {
                '2': ''
            }
        }

        MicrophoneMuteCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def __MatchMicrophoneMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MicrophoneMute', value, None)

    def SetPan(self, value, qualifier):

        if -10 <= value <= 10:
            data = {
                'camera': {
                    '7': '{}'.format(value)
                }
            }

            PanCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def UpdatePan(self, value, qualifier):

        data = {
            'camera': {
                '7': ''
            }
        }

        PanCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Pan', PanCmdString, value, qualifier)

    def __MatchPan(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Pan', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            'Home':     '1',
            'Preset 1': '2',
            'Preset 2': '3'
        }

        if value in ValueStateValues:
            data = {
                'camera': {
                    '13': '{}'.format(ValueStateValues[value])
                }
            }

            PresetRecallCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
            data = {
                'camera': {
                    '0F': ''
                }
            }

            PresetRecallCmdString = json.dumps(self.build('perform', data))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            'Home':     '12',
            'Preset 1': '17',
            'Preset 2': '18'
        }

        if value in ValueStateValues:
            data = {
                'camera': {
                    '{}'.format(ValueStateValues[value]): ''
                }
            }

            PresetSaveCmdString = json.dumps(self.build('perform', data))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetReboot(self, value, qualifier):

        data = {
            'system': {
                '32': ''
            }
        }

        RebootCmdString = json.dumps(self.build('perform', data))
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)
    def UpdateRoom(self, value, qualifier):

        data = {
            'system': {
                '26': ''
            }
        }

        RoomCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Room', RoomCmdString, value, qualifier)

    def __MatchRoom(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Room', value, None)

    def UpdateSystemFirmwareVersion(self, value, qualifier):

        data = {
            'system': {
                '16': ''
            }
        }

        SystemFirmwareVersionCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('SystemFirmwareVersion', SystemFirmwareVersionCmdString, value, qualifier)

    def __MatchSystemFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemFirmwareVersion', value, None)

    def UpdateSystemName(self, value, qualifier):

        data = {
            'system': {
                '25': ''
            }
        }

        SystemNameCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('SystemName', SystemNameCmdString, value, qualifier)

    def __MatchSystemName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemName', value, None)

    def UpdateSystemReady(self, value, qualifier):

        data = {
            'system': {
                'BF': ''
            }
        }

        SystemReadyCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('SystemReady', SystemReadyCmdString, value, qualifier)

    def __MatchSystemReady(self, match, tag):

        ValueStateValues = {
            '1': 'Ready',
            '0': 'Not Ready'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SystemReady', value, None)

    def UpdateSystemSerialNumber(self, value, qualifier):

        data = {
            'system': {
                '10': ''
            }
        }

        SystemSerialNumberCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('SystemSerialNumber', SystemSerialNumberCmdString, value, qualifier)

    def __MatchSystemSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemSerialNumber', value, None)

    def SetTilt(self, value, qualifier):

        if -10 <= value <= 10:
            data = {
                'camera': {
                    '8': '{}'.format(value)
                }
            }

            TiltCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def UpdateTilt(self, value, qualifier):

        data = {
            'camera': {
                '8': ''
            }
        }

        TiltCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Tilt', TiltCmdString, value, qualifier)

    def __MatchTilt(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Tilt', value, None)

    def SetUltrasoundCommand(self, value, qualifier):

        string = value

        if string is not None and string.strip():
            data = {
                'audio': {
                    'C1': '{}'.format(string.strip())
                }
            }

            UltrasoundCommandCmdString = json.dumps(self.build('perform', data))
            self.__SetHelper('UltrasoundCommand', UltrasoundCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUltrasoundCommand')

    def UpdateUSBCallStatus(self, value, qualifier):

        data = {
            'usb': {
                '37': ''
            }
        }

        USBCallStatusCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('USBCallStatus', USBCallStatusCmdString, value, qualifier)

    def __MatchUSBCallStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBCallStatus', value, None)

    def UpdateUSBConnection(self, value, qualifier):

        data = {
            'usb': {
                '36': ''
            }
        }

        USBConnectionCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('USBConnection', USBConnectionCmdString, value, qualifier)

    def __MatchUSBConnection(self, match, tag):

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBConnection', value, None)

    def UpdateWiFiMACAddress(self, value, qualifier):

        data = {
            'wifi': {
                'AC': ''
            }
        }

        WiFiMACAddressCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('WiFiMACAddress', WiFiMACAddressCmdString, value, qualifier)

    def __MatchWiFiMACAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('WiFiMACAddress', value, None)

    def UpdateWiFiState(self, value, qualifier):

        data = {
            'wifi': {
                'B0': ''
            }
        }

        WiFiStateCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('WiFiState', WiFiStateCmdString, value, qualifier)

    def __MatchWiFiState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('WiFiState', value, None)

    def UpdateWiFiStaticIPAddress(self, value, qualifier):

        data = {
            'wifi': {
                'A2': ''
            }
        }

        WiFiStaticIPAddressCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('WiFiStaticIPAddress', WiFiStaticIPAddressCmdString, value, qualifier)

    def __MatchWiFiStaticIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('WiFiStaticIPAddress', value, None)

    def SetZoom(self, value, qualifier):

        if -10 <= value <= 10:
            data = {
                'camera': {
                    '6': '{}'.format(value)
                }
            }

            ZoomCmdString = json.dumps(self.build('update', data))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        data = {
            'camera': {
                '6': ''
            }
        }
        ZoomCmdString = json.dumps(self.build('retrieve', data))
        self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)

    def __MatchZoom(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Zoom', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.send_text(commandstring)

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

            self.send_text(commandstring)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLoginHandShake(None, None)
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.meter_events_enabled = False

    def CheckMatchedString(self):
        for regexString in self.__matchStringDict:
            while True:
                result = re.search(regexString, self._receiveBuffer)

                if result:
                    self.__matchStringDict[regexString]['callback'](result, self.__matchStringDict[regexString]['para'])
                    self._receiveBuffer = self._receiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    def generatestring(self):
        return base64encode('{}'.format(random.randint(-27555755, 666333366)).zfill(16).encode()).decode('utf-8').strip()

    def get_mask_key(self):
        return '{}'.format(random.randint(0, 6553)).zfill(4).encode()

    def try_decode_UTF8(self, data):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return False
        except Exception as e:
            raise (e)

    def encode_to_UTF8(self, data):
        try:
            return data.encode('utf-8', 'ignore')
        except UnicodeEncodeError as e:
            return False
        except Exception as e:
            raise (e)

    def mask(self, mask_key, data):

        if data is None:
            data = ""

        _m = array.array("B", mask_key)
        _d = array.array("B", data)
        return _mask(_m, _d)

    def ReceiveSocketData(self):
        return self._ReceiveSocketData

    def ReceiveSocketData(self, value):
        if callable(value):
            self._receiveBuffer += value

            # check incoming data if it matched any expected data from devicle module
            if self.CheckMatchedString() and len(self._receiveBuffer) > 10000:
                self._receiveBuffer = b''

    def send_pong(self, message):
        self.send_text(message, PONG)

    def SendSocket(self, message):
        if self.Authenticated:
            self.send_text(message)
        else:
            handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
            self.Send(handshake)

    def _get_masked(self, mask_key, message):
        s = self.mask(mask_key, message)
        return mask_key + s

    def send_text(self, message, masked=True, opcode=TEXT):

        if isinstance(message, bytes):
            message = self.try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
            if not message:
                return False

        header = bytearray()
        payload = self.encode_to_UTF8(message)
        payload_length = len(payload)
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(1 << 7 | payload_length)
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))

        else:
            raise Exception("Message is too big. Consider breaking it into chunks.")

        if masked:
            mask_key = self.get_mask_key()
            self.Send(bytes(header + self._get_masked(mask_key, payload)))
        else:
            self.Send(bytes(header + payload))

    def read_bytes(self, num):
        tempt = self._receiveBuffer[:num]
        self._receiveBuffer = self._receiveBuffer[num:]
        return tempt[:num]

    def read_message(self, data):
        self._receiveBuffer = data
        try:
            b1, b2 = self.read_bytes(2)
        except ValueError as e:
            b1, b2 = 0, 0

        fin = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN
        if masked:
            if payload_length == 126:
                payload_length = struct.unpack(">H", self.read_bytes(2))[0]
            elif payload_length == 127:
                payload_length = struct.unpack(">Q", self.read_bytes(8))[0]

            masks = self.read_bytes(4)

            decoded = ""
            for char in self.read_bytes(payload_length):
                char ^= masks[len(decoded) % 4]
                decoded += chr(char)

            if opcode == TEXT:
                if callable(self.ReceiveSocketData):
                    self.ReceiveSocketData(decoded)
            elif opcode == PING:
                self.send_text(decoded, PONG)
        else:
            if opcode == TEXT:
                if callable(self.ReceiveSocketData):
                    self.ReceiveSocketData(self._receiveBuffer)
            elif opcode == PING:
                self.send_text("", PONG)

    def authentication_check(self, hashdata):
        pass

    def __ReceiveData(self, interface, data):
        try:
            if self.Authenticated:
                self.read_message(data)
            if b'101' in data:  # add check for hash
                self.Authenticated = True
                print('Bose handshaking performed')
        except UnicodeDecodeError as e:
            pass

    def bose_19_5035_vb1(self):

        self.Model = 'VB1'

    def bose_19_5035_vbs(self):

        self.Model = 'VB-S'

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
        
        # check incoming data if it matched any expected data from device module
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)

        if platform == 'Pro' and version < minimumVersion:
            self.Error(['Minimum API version not met. Needs to be >= 3.4.6'])
        else:
            EthernetClientInterface.SSLWrap(self, certificate=None, cert_reqs='CERT_NONE', ssl_version='TLSv2', ca_certs= None)

        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Hostname)
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