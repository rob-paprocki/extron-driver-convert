import base64
from json import loads, dumps
import urllib.error
import urllib.request
from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog
from struct import pack

class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {
            'FWD-55X85G/T': self.sony_10_4546_B,
            'FWD-43X80G/T': self.sony_10_4546_A,
            'FWD-49X80G/T': self.sony_10_4546_A,
            'FWD-65X85G/T': self.sony_10_4546_B,
            'FWD-75X85G/T': self.sony_10_4546_B,
            'FWD-85X85G/T': self.sony_10_4546_B,
            'FWD-75X80G': self.sony_10_4546_A,
            'FWD-55X80G': self.sony_10_4546_A,
            'FWD-65X80G': self.sony_10_4546_A,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'PowerSavingMode': {'Status': {}},
            'Reboot': {'Status': {}},
            'Volume': {'Status': {}},
            'WakeOnLan': {'Status': {}},
            }

        self.lastUpdate = 0

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': True,
            'Off': False
        }

        AudioMuteCmdString = '/sony/audio'
        data = dumps({"method": "setAudioMute",
                      "id": 601,
                      "params": [{"status": ValueStateValues[value]}],
                      "version": "1.0"})
        self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, data.encode())

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateVolume(value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = '/sony/avContent'
        data = dumps({"method": "setPlayContent",
                      "id": 101,
                      "params": [{"uri": self.Inputs[value]}],
                      "version": "1.0"})
        self.__SetHelper('Input', value, qualifier, InputCmdString, data.encode())

    def UpdateInput(self, value, qualifier):

        InputCmdString = '/sony/avContent'
        data = dumps({"method": "getPlayingContentInfo",
                      "id": 103,
                      "params": [],
                      "version": "1.0"})
        res = self.__UpdateHelper('Input', value, qualifier, InputCmdString, data.encode())
        if res:
            try:
                value = self.InputStates[res['result'][0]['uri']]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': True,
            'Sleep': False
        }

        PowerCmdString = '/sony/system'
        data = dumps({"method": "setPowerStatus",
                      "id": 55,
                      "params": [{"status": ValueStateValues[value]}],
                      "version": "1.0"})
        self.__SetHelper('Power', value, qualifier, PowerCmdString, data.encode())

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'active': 'On',
            'standby': 'Sleep'
        }

        PowerCmdString = '/sony/system'
        data = dumps({"method": "getPowerStatus",
                      "id": 50,
                      "params": [],
                      "version": "1.0"})
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['status']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'off',
            'Low': 'low',
            'High': 'high',
            'Picture Off': 'pictureOff'
        }

        PowerSavingModeCmdString = '/sony/system'
        data = dumps({"method": "setPowerSavingMode",
                      "id": 52,
                      "params": [{"mode": ValueStateValues[value]}],
                      "version": "1.0"})
        self.__SetHelper('PowerSavingMode', value, qualifier, PowerSavingModeCmdString, data.encode())

    def UpdatePowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            'off': 'Off',
            'low': 'Low',
            'high': 'High',
            'pictureOff': 'Picture Off'
        }

        PowerSavingModeCmdString = '/sony/system'
        data = dumps({"method": "getPowerSavingMode",
                      "id": 51,
                      "params": [],
                      "version": "1.0"})
        res = self.__UpdateHelper('PowerSavingMode', value, qualifier, PowerSavingModeCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['mode']]
                self.WriteStatus('PowerSavingMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Saving Mode: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = '/sony/system'
        data = dumps({"method": "requestReboot",
                      "id": 10,
                      "params": [],
                      "version": "1.0"})
        self.__SetHelper('Reboot', value, qualifier, RebootCmdString, data.encode())

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '/sony/audio'
            data = dumps({"method": "setAudioVolume",
                        "id": 601,
                        "params": [{
                                    "volume": str(value),
                                    "target": "speaker"
                                }],
                        "version": "1.0"})
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        AudioMuteStates = {
            True: 'On',
            False: 'Off'
        }
        
        VolumeCmdString = '/sony/audio'
        data = dumps({"method": "getVolumeInformation",
                        "id": 33,
                        "params": [],
                        "version": "1.0"})
        res = self.__UpdateHelper('Volume', value, qualifier, VolumeCmdString, data.encode())
        if res:
            try:
                value = int(res['result'][0][0]['volume'])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])
            try:
                value = AudioMuteStates[res['result'][0][0]['mute']]
                self.WriteStatus('AudioMute', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])
        

    def SetWakeOnLan(self, value, qualifier):

        ValueStateValues = {
            'Enable': True,
            'Disable': False
        }

        WakeOnLanCmdString = '/sony/system'
        data = dumps({"method": "setWolMode",
                        "id": 55,
                        "params": [{"enabled": ValueStateValues[value]}],
                        "version": "1.0"})
        self.__SetHelper('WakeOnLan', value, qualifier, WakeOnLanCmdString, data.encode())

    def UpdateWakeOnLan(self, value, qualifier):

        ValueStateValues = {
            True: 'Enable',
            False: 'Disable'
        }

        WakeOnLanCmdString = '/sony/system'
        data = dumps({"method": "getWolMode",
                      "id": 50,
                      "params": [],
                      "version": "1.0"})
        res = self.__UpdateHelper('WakeOnLan', value, qualifier, WakeOnLanCmdString, data.encode())
        if res:
            try:
                value = ValueStateValues[res['result'][0]['enabled']]
                self.WriteStatus('WakeOnLan', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Wake On Lan: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = loads(response.read().decode())
        return res

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True

        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
                
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')  # method defaults to GET when data is None

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
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

    def sony_10_4546_A(self):
        self.Inputs = {
            'TV/DVB': 'tv:dvbt',  # Refer DR# 58433
            'HDMI 1': 'extInput:hdmi?port=1',
            'HDMI 2': 'extInput:hdmi?port=2',
            'HDMI 3': 'extInput:hdmi?port=3',
            'HDMI 4': 'extInput:hdmi?port=4',
            'Composite': 'extInput:composite?port=1'
        }
        self.InputStates = {
            'tv:dvbt': 'TV/DVB',
            'extInput:hdmi?port=1': 'HDMI 1',
            'extInput:hdmi?port=2': 'HDMI 2',
            'extInput:hdmi?port=3': 'HDMI 3',
            'extInput:hdmi?port=4': 'HDMI 4',
            'extInput:composite?port=1': 'Composite'
        }

    def sony_10_4546_B(self):
        self.Inputs = {
            'TV/DVB': 'tv:dvbt',  # Refer DR# 58433
            'HDMI 1': 'extInput:hdmi?port=1',
            'HDMI 2': 'extInput:hdmi?port=2',
            'HDMI 3': 'extInput:hdmi?port=3',
            'HDMI 4': 'extInput:hdmi?port=4',
            'Composite': 'extInput:composite?port=1',
            'Component': 'extInput:component?port=1'
        }
        self.InputStates = {
            'tv:dvbt': 'TV/DVB',
            'extInput:hdmi?port=1': 'HDMI 1',
            'extInput:hdmi?port=2': 'HDMI 2',
            'extInput:hdmi?port=3': 'HDMI 3',
            'extInput:hdmi?port=4': 'HDMI 4',
            'extInput:composite?port=1': 'Composite',
            'extInput:component?port=1': 'Component'
        }

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'FWD-55X80G': self.sony_10_4546_A,
            'FWD-65X80G': self.sony_10_4546_A,
            'FWD-43X80G/T': self.sony_10_4546_A,
            'FWD-49X80G/T': self.sony_10_4546_A,
            'FWD-55X85G/T': self.sony_10_4546_B,
            'FWD-65X85G/T': self.sony_10_4546_B,
            'FWD-75X80G': self.sony_10_4546_A,
            'FWD-75X85G/T': self.sony_10_4546_B,
            'FWD-85X85G/T': self.sony_10_4546_B,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.SetRegex = re.compile(b'\x70[\x00-\x04][\x00-\xFF]')
        self.UpdateRegex = re.compile(b'\x70[\x00-\x02][\x02][\x00-\x01][\x00-\xFF]|\x70[\x00-\x02][\x03][\x01-\x07][\x00-\xFF]{2}|\x70[\x01-\x04][\x00-\xFF]')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x8C\x00\x44\x03\x01\x00\xD4',
            'Zoom': b'\x8C\x00\x44\x03\x01\x02\xD6',
            'Normal': b'\x8C\x00\x44\x03\x01\x03\xD7',
            'Normal (PC)': b'\x8C\x00\x44\x03\x01\x05\xD9',
            'Full 1': b'\x8C\x00\x44\x03\x01\x01\xD5',
            'Full 2': b'\x8C\x00\x44\x03\x01\x06\xDA',
            'Full 3': b'\x8C\x00\x44\x03\x01\x07\xDB'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x8C\x00\x06\x03\x01\x01\x97',
            'Off': b'\x8C\x00\x06\x03\x01\x00\x96'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.Inputs[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x83\x00\x02\xFF\xFF\x83'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[2:4] == b'\x02\x01':  # Refer sony_10_4495
                    value = 'TV/DVB'
                else:
                    value = self.InputStates[res[3:5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x8C\x00\x67\x03\x01\x00\xF7',
            '2': b'\x8C\x00\x67\x03\x01\x01\xF8',
            '3': b'\x8C\x00\x67\x03\x01\x02\xF9',
            '4': b'\x8C\x00\x67\x03\x01\x03\xFA',
            '5': b'\x8C\x00\x67\x03\x01\x04\xFB',
            '6': b'\x8C\x00\x67\x03\x01\x05\xFC',
            '7': b'\x8C\x00\x67\x03\x01\x06\xFD',
            '8': b'\x8C\x00\x67\x03\x01\x07\xFE',
            '9': b'\x8C\x00\x67\x03\x01\x08\xFF',
            '0': b'\x8C\x00\x67\x03\x01\x09\x00'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x8C\x00\x67\x03\x01\x74\x6B',
            'Down': b'\x8C\x00\x67\x03\x01\x75\x6C',
            'Left': b'\x8C\x00\x67\x03\x01\x34\x2B',
            'Right': b'\x8C\x00\x67\x03\x01\x33\x2A',
            'Return': b'\x8C\x00\x67\x03\x97\x23\xB0',
            'Home': b'\x8C\x00\x67\x03\x01\x60\x57',
            'Select': b'\x8C\x00\x67\x03\x01\x65\x5C'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x8C\x00\x00\x02\x01\x8F',
            'Off': b'\x8C\x00\x00\x02\x00\x8E'
        }

        PowerCmdString = ValueStateValues[value]
        if value == 'Off':
            self.__SetHelper('Power', b'\x8C\x00\x01\x02\x01\x90', value, qualifier)  # Standby Enable command
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        PowerCmdString = b'\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x8C\x00\x0D\x03\x01\x01\x9E', 
            'Off' : b'\x8C\x00\x0D\x03\x01\x00\x9D'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        VideoMuteCmdString = b'\x83\x00\x0D\xFF\xFF\x8E'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            cks = value + 149
            VolumeCmdString = pack('>BBBBBBB', 0x8C, 0x00, 0x05, 0x03, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x83\x00\x05\xFF\xFF\x86'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-2])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1 : 'Limit Over (Abnormal End - over max value)',
            2 : 'Limit Over (Abnormal End - under min value)',
            3 : 'Command Canceled (Abnormal End)',
            4 : 'Parse Error (Data Format Error)'
        }

        if len(response) == 3 and response[1] in DEVICE_ERROR_CODES:
            self.Error(['ERROR:{0}'.format(DEVICE_ERROR_CODES[response[1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.SetRegex)
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.UpdateRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)           

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def sony_10_4546_B(self):
        self.Inputs ={
            'TV/DVB'    : b'\x8C\x00\x02\x02\x01\x91', # Refer sony_10_4495
            'HDMI 1'    : b'\x8C\x00\x02\x03\x04\x01\x96', 
            'HDMI 2'    : b'\x8C\x00\x02\x03\x04\x02\x97', 
            'HDMI 3'    : b'\x8C\x00\x02\x03\x04\x03\x98', 
            'HDMI 4'    : b'\x8C\x00\x02\x03\x04\x04\x99', 
            'Composite' : b'\x8C\x00\x02\x03\x02\x01\x94', 
            'Component' : b'\x8C\x00\x02\x03\x03\x01\x95'
        }
        self.InputStates ={
            b'\x04\x01' : 'HDMI 1', 
            b'\x04\x02' : 'HDMI 2', 
            b'\x04\x03' : 'HDMI 3', 
            b'\x04\x04' : 'HDMI 4', 
            b'\x02\x01' : 'Composite', 
            b'\x03\x01' : 'Component'
        }


    def sony_10_4546_A(self):
        self.Inputs ={
            'TV/DVB'    : b'\x8C\x00\x02\x02\x01\x91', # Refer sony_10_4495
            'HDMI 1'    : b'\x8C\x00\x02\x03\x04\x01\x96', 
            'HDMI 2'    : b'\x8C\x00\x02\x03\x04\x02\x97', 
            'HDMI 3'    : b'\x8C\x00\x02\x03\x04\x03\x98', 
            'HDMI 4'    : b'\x8C\x00\x02\x03\x04\x04\x99', 
            'Composite' : b'\x8C\x00\x02\x03\x02\x01\x94'
        }
        self.InputStates ={
            b'\x04\x01' : 'HDMI 1', 
            b'\x04\x02' : 'HDMI 2', 
            b'\x04\x03' : 'HDMI 3', 
            b'\x04\x04' : 'HDMI 4', 
            b'\x02\x01' : 'Composite'
        }

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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
