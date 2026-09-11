from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

import re
import json
import struct
from base64 import encodebytes as base64encode
import random
import array
import re
from collections import defaultdict
import time

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
    return _d.tostring()

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
        self.Models = {
            'Connect 352D': self.leap_25_4731_2,
            'Connect 702D': self.leap_25_4731_2,
            'Connect 704D': self.leap_25_4731_4,
            'Connect 164D': self.leap_25_4731_4,
            'Connect 354D': self.leap_25_4731_4,
            'Connect 84D': self.leap_25_4731_4,
            'Connect 88D': self.leap_25_4731_8,
            'Connect 168D': self.leap_25_4731_8,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelStandby': {'Parameters': ['Channel'], 'Status': {}},
            'CrossoverDelay': {'Parameters': ['Channel'], 'Status': {}},
            'CrossoverGain': {'Parameters': ['Channel'], 'Status': {}},
            'CrossoverPolarity': {'Parameters': ['Channel'], 'Status': {}},
            'Firmware': { 'Status': {}},
            'InputFader': {'Parameters': ['Channel', 'Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Channel', 'Type'], 'Status': {}},
            'OutputFader': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputStatus': {'Parameters': ['Channel'], 'Status': {}},
            'OverrideMode': {'Parameters': ['Channel'], 'Status': {}},
            'PrimaryInput': {'Parameters': ['Channel'], 'Status': {}},
            'SecondaryInput': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.match_functions = {}

        # Websocket Variables
        self.Authenticated = False
        self.ipAddress = IPAddress
        self.uri = '/'
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
            self.AddMatchString(re.compile(b'({\s+?"leaApi": "\S+?",\s+?"url": "\S+?",\s+?"result": {[^{]+?"firmwareVersion": "\S+?"[^{]+?},\s+?"id": [01]\n})'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'({\s+?"leaApi": "\S+?",\s+?"url": "\S+?",\s+?"result": {[^{]+?},\s+?"id": 1\n})'), self.__Match, 'result')
            self.AddMatchString(re.compile(b'({\s+?"leaApi": "\S+?",\s+?"url": "\S+?",\s+?"method": "notify",\s+?"params": {[\s\S]+?}\n})'), self.__Match, 'params')
            self.AddMatchString(re.compile(b'({\s+?"leaApi": "\S+?",\s+?"error": {\s+?"message": "[^{]+?"\s+?}(?:,\s+?"id": [01])?\n})'), self.__MatchError, None)

    def SetLoginHandShake(self, value, url):

        handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
        self.Send(handshake)

    def subscribe(self, command, url, name, value, qualifier, match):

        self.match_functions['{}/{}'.format(url, name)] = match

        data = {
            'leaApi': '1.0',
            'url': url,
            'method': 'subscribe',
            'params': {},
            'id': 1
        }

        self.__UpdateHelper(command, json.dumps(data), value, qualifier)

    def __Match(self, match, tag):
        res = json.loads(match.group(1).decode())
        self.route(res['url'] if res['url'] != '/' else '', res[tag])

    def route(self, url, values):
        if url in self.match_functions:
            self.match_functions[url](url, values)
        elif isinstance(values, dict):
            for k in values.keys():
                self.route('{}/{}'.format(url, k), values[k])

    def SetChannelStandby(self, value, qualifier):

        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if 1 <= int(channel) <= self.ChannelSize and value in ValueStateValues:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/output'.format(channel),
                'method': 'set',
                'params': {
                    'enable': ValueStateValues[value]
                }
            }

            ChannelStandbyCmdString = json.dumps(data)
            self.__SetHelper('ChannelStandby', ChannelStandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStandby')

    def UpdateChannelStandby(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('ChannelStandby', '/amp/channels/{}/output'.format(channel), 'enable', value, qualifier, self.__MatchChannelStandby)
        else:
            self.Discard('Invalid Command for UpdateChannelStandby')

    def __MatchChannelStandby(self, url, value):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }

        qualifier = {
            'Channel': url.split('/')[3]
        }

        value = ValueStateValues[value]
        self.WriteStatus('ChannelStandby', value, qualifier)

    def SetCrossoverDelay(self, value, qualifier):

        channel = qualifier['Channel']

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if 1 <= int(channel) <= self.ChannelSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel),
                'method': 'set',
                'params': {
                    'delay': value
                }
            }

            CrossoverDelayCmdString = json.dumps(data)
            self.__SetHelper('CrossoverDelay', CrossoverDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverDelay')

    def UpdateCrossoverDelay(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('CrossoverDelay', '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel), 'delay', value, qualifier, self.__MatchCrossoverDelay)
        else:
            self.Discard('Invalid Command for UpdateCrossoverDelay')

    def __MatchCrossoverDelay(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('CrossoverDelay', value, qualifier)

    def SetCrossoverGain(self, value, qualifier):

        channel = qualifier['Channel']

        ValueConstraints = {
            'Min': -15,
            'Max': 15
        }

        if 1 <= int(channel) <= self.ChannelSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel),
                'method': 'set',
                'params': {
                    'gain': value
                }
            }

            CrossoverGainCmdString = json.dumps(data)
            self.__SetHelper('CrossoverGain', CrossoverGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverGain')

    def UpdateCrossoverGain(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('CrossoverGain', '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel), 'gain', value, qualifier, self.__MatchCrossoverGain)
        else:
            self.Discard('Invalid Command for UpdateCrossoverGain')

    def __MatchCrossoverGain(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('CrossoverGain', value, qualifier)

    def SetCrossoverPolarity(self, value, qualifier):

        channel = qualifier['Channel']

        ValueStateValues = {
            'Positive': False,
            'Negative': True
        }

        if 1 <= int(channel) <= self.ChannelSize and value in ValueStateValues:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel),
                'method': 'set',
                'params': {
                    'invert': ValueStateValues[value]
                }
            }

            CrossoverPolarityCmdString = json.dumps(data)
            self.__SetHelper('CrossoverPolarity', CrossoverPolarityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverPolarity')

    def UpdateCrossoverPolarity(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('CrossoverPolarity', '/amp/channels/{}/crossover/bandGainAndDelay'.format(channel), 'invert', value, qualifier, self.__MatchCrossoverPolarity)
        else:
            self.Discard('Invalid Command for UpdateCrossoverPolarity')

    def __MatchCrossoverPolarity(self, url, value):

        ValueStateValues = {
            False:  'Positive',
            True:   'Negative'
        }

        qualifier = {
            'Channel': url.split('/')[3]
        }

        value = ValueStateValues[value]
        self.WriteStatus('CrossoverPolarity', value, qualifier)

    def UpdateFirmware(self, value, qualifier):

        data = {
            'leaApi': '1.0',
            'url': '/amp/deviceInfo',
            'method': 'get',
            'params': {},
            'id': 0
        }
        FirmwareCmdString = json.dumps(data)
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = json.loads(match.group(1).decode())['result']['firmwareVersion']
        self.WriteStatus('Firmware', value, None)

    def SetInputFader(self, value, qualifier):

        channel = qualifier['Channel']
        type_ = qualifier['Type']

        TypeStates = ['Primary', 'Secondary']

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }

        if 1 <= int(channel) <= self.ChannelSize and type_ in TypeStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/inputSelector'.format(channel),
                'method': 'set',
                'params': {
                    '{}Fader'.format(type_.lower()): value
                }
            }

            InputFaderCmdString = json.dumps(data)
            self.__SetHelper('InputFader', InputFaderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputFader')

    def UpdateInputFader(self, value, qualifier):

        channel = qualifier['Channel']
        type_ = qualifier['Type']

        TypeStates = ['Primary', 'Secondary']

        if 1 <= int(channel) <= self.ChannelSize and type_ in TypeStates:
            self.subscribe('InputFader', '/amp/channels/{}/inputSelector'.format(channel), '{}Fader'.format(type_.lower()), value, qualifier, self.__MatchInputFader)
        else:
            self.Discard('Invalid Command for UpdateInputFader')

    def __MatchInputFader(self, url, value):

        TypeStates = {
            'primaryFader':     'Primary',
            'secondaryFader':   'Secondary'
        }

        qualifier = {
            'Channel':  url.split('/')[3],
            'Type':     TypeStates[url.split('/')[5]]
        }

        self.WriteStatus('InputFader', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        channel = qualifier['Channel']
        type_ = qualifier['Type']

        TypeStates = ['Primary', 'Secondary']

        if 1 <= int(channel) <= self.ChannelSize and type_ in TypeStates:

            if type_ == 'Primary':
                self.subscribe('InputSignalStatus', '/amp/channels/{}/inputSelector'.format(channel), 'primarySignalDetect', value, qualifier, self.__MatchInputSignalStatus)
            else:
                self.subscribe('InputSignalStatus', '/amp/channels/{}/inputSelector'.format(channel), 'secondarySignalDetect', value, qualifier, self.__MatchInputSignalStatus)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, url, value):

        TypeStates = {
            'primarySignalDetect':      'Primary',
            'secondarySignalDetect':    'Secondary'
        }

        qualifier = {
            'Channel':  url.split('/')[3],
            'Type':     TypeStates[url.split('/')[5]]
        }


        ValueStateValues = {
            True:   'Active',
            False:  'Not Active'
        }

        value = ValueStateValues[value]
        self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetOutputFader(self, value, qualifier):

        channel = qualifier['Channel']

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }

        if 1 <= int(channel) <= self.ChannelSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/output'.format(channel),
                'method': 'set',
                'params': {
                    'fader': value
                }
            }

            OutputFaderCmdString = json.dumps(data)
            self.__SetHelper('OutputFader', OutputFaderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFader')

    def UpdateOutputFader(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('OutputFader', '/amp/channels/{}/output'.format(channel), 'fader', value, qualifier, self.__MatchOutputFader)
        else:
            self.Discard('Invalid Command for UpdateOutputFader')

    def __MatchOutputFader(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('OutputFader', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if 1 <= int(channel) <= self.ChannelSize and value in ValueStateValues:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/output'.format(channel),
                'method': 'set',
                'params': {
                    'mute': ValueStateValues[value]
                }
            }

            OutputMuteCmdString = json.dumps(data)
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('OutputMute', '/amp/channels/{}/output'.format(channel), 'mute', value, qualifier, self.__MatchOutputMute)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, url, value):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }

        qualifier = {
            'Channel': url.split('/')[3]
        }

        value = ValueStateValues[value]
        self.WriteStatus('OutputMute', value, qualifier)

    def UpdateOutputStatus(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('OutputStatus', '/amp/channels/{}/output'.format(channel), 'status', value, qualifier, self.__MatchOutputStatus)
        else:
            self.Discard('Invalid Command for UpdateOutputStatus')

    def __MatchOutputStatus(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('OutputStatus', value, qualifier)

    def SetOverrideMode(self, value, qualifier):

        channel = qualifier['Channel']

        ValueStateValues = {
            'Auto Override Primary input':  'Override',
            'Signal Sensing Override':      'Backup'
        }

        if 1 <= int(channel) <= self.ChannelSize and value in ValueStateValues:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/inputSelector'.format(channel),
                'method': 'set',
                'params': {
                    'mode': ValueStateValues[value]
                }
            }

            OverrideModeCmdString = json.dumps(data)
            self.__SetHelper('OverrideMode', OverrideModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverrideMode')

    def UpdateOverrideMode(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('OverrideMode', '/amp/channels/{}/inputSelector'.format(channel), 'mode', value, qualifier, self.__MatchOverrideMode)
        else:
            self.Discard('Invalid Command for UpdateOverrideMode')

    def __MatchOverrideMode(self, url, value):

        ValueStateValues = {
            'Override': 'Auto Override Primary input',
            'Backup':   'Signal Sensing Override'
        }

        qualifier = {
            'Channel': url.split('/')[3]
        }

        value = ValueStateValues[value]
        self.WriteStatus('OverrideMode', value, qualifier)

    def SetPrimaryInput(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize and value in self.PrimaryInputStates:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/inputSelector'.format(channel),
                'method': 'set',
                'params': {
                    'primary': value
                }
            }

            PrimaryInputCmdString = json.dumps(data)
            self.__SetHelper('PrimaryInput', PrimaryInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPrimaryInput')

    def UpdatePrimaryInput(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('PrimaryInput', '/amp/channels/{}/inputSelector'.format(channel), 'primary', value, qualifier, self.__MatchPrimaryInput)
        else:
            self.Discard('Invalid Command for UpdatePrimaryInput')

    def __MatchPrimaryInput(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('PrimaryInput', value, qualifier)

    def SetSecondaryInput(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(channel) <= self.ChannelSize and value in self.SecondaryInputStates:
            data = {
                'leaApi': '1.0',
                'url': '/amp/channels/{}/inputSelector'.format(channel),
                'method': 'set',
                'params': {
                    'secondary': value
                }
            }

            SecondaryInputCmdString = json.dumps(data)
            self.__SetHelper('SecondaryInput', SecondaryInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSecondaryInput')

    def UpdateSecondaryInput(self, value, qualifier):

        channel = qualifier['Channel']

        if 1 <= int(channel) <= self.ChannelSize:
            self.subscribe('SecondaryInput', '/amp/channels/{}/inputSelector'.format(channel), 'secondary', value, qualifier, self.__MatchSecondaryInput)
        else:
            self.Discard('Invalid Command for UpdateSecondaryInput')

    def __MatchSecondaryInput(self, url, value):

        qualifier = {
            'Channel': url.split('/')[3]
        }

        self.WriteStatus('SecondaryInput', value, qualifier)

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

    def __MatchError(self, match, tag):

        self.counter = 0
        try:
            self.Error(['An error occurred: {}.'.format(json.loads(match.group(1).decode())['error']['message'])])
        except:
            self.Error(['An error occurred.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLoginHandShake(None, None)
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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
            self._ReceiveSocketData = value

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
                print('Handshaking performed')
        except UnicodeDecodeError as e:
            pass

    def leap_25_4731_2(self):

        self.ChannelSize = 2
        self.PrimaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            ]
        self.SecondaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            'None'
            ]

    def leap_25_4731_4(self):

        self.ChannelSize = 4
        self.PrimaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Analog 3',
            'Analog 4',
            'Analog 3+4',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            ]
        self.SecondaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Analog 3',
            'Analog 4',
            'Analog 3+4',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            'None'
            ]

    def leap_25_4731_8(self):

        self.ChannelSize = 8
        self.PrimaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Analog 3',
            'Analog 4',
            'Analog 3+4',
            'Analog 5',
            'Analog 6',
            'Analog 5+6',
            'Analog 7',
            'Analog 8',
            'Analog 7+8',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            ]
        self.SecondaryInputStates = [
            'Analog 1',
            'Analog 2',
            'Analog 1+2',
            'Analog 3',
            'Analog 4',
            'Analog 3+4',
            'Analog 5',
            'Analog 6',
            'Analog 5+6',
            'Analog 7',
            'Analog 8',
            'Analog 7+8',
            'Dante 1',
            'Dante 2',
            'Dante 1+2',
            'Dante 3',
            'Dante 4',
            'Dante 3+4',
            'Dante 5',
            'Dante 6',
            'Dante 5+6',
            'Dante 7',
            'Dante 8',
            'Dante 7+8',
            'None'
            ]

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

        version = tuple(int(i) for i in Version().split('.'))
        if version >= minimumVersion :
            EthernetClientInterface.SSLWrap(self, certificate=None, cert_reqs='CERT_NONE', ssl_version='TLSv2', ca_certs= None)
        else:
            self.Error(['Minimum API version not met. Needs to be >= 3.4.6'])

        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Hostname) 
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