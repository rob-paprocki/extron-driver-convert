from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import base64
from functools import reduce
from operator import xor
from re import compile
from json import dumps, loads
import urllib.error
import urllib.request


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
            '43HFL5014/12': self.phil_10_4510_4014_5014,
            '50HFL5014/12': self.phil_10_4510_4014_5014,
            '32HFL5014/12': self.phil_10_4510_4014_5014,
            '65HFL6014U/12': self.phil_10_4510_6014U,
            '55HFL6014U/12': self.phil_10_4510_6014U,
            '50HFL6014U/12': self.phil_10_4510_6014U,
            '43HFL6014U/12': self.phil_10_4510_6014U,
            '50HFL4014/12': self.phil_10_4510_4014_5014,
            '43HFL4014/12': self.phil_10_4510_4014_5014,
            '32HFL4014/12': self.phil_10_4510_4014_5014,
            '28HFL4014/12': self.phil_10_4510_4014_5014,
            '40HFL3011T/12': self.phil_10_4510_3011T,
            '32HFL3011T/12': self.phil_10_4510_3011T,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Keypad': {'Status': {}},
            'LocalOSDSuppress': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureFormat': {'Status': {}},
            'Power': {'Status': {}},
            'SmartPicture': {'Status': {}},
            'Source': {'Status': {}},
            'UserInputControl': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.set_regex = compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:\x00\x16|\x01\x17|\x02\x14)\xA5\xA5')
        self.get_regex = {
            'Power': compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                        br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x18'
                                        br'[\x00-\x03][\x38-\x3B])\xA5\xA5'),
            'SmartPicture': compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                        br'\x00\x16\xA5\xA5\x0E\x13\x00\x00\x05\x0A\x00\x0C\x22\x36'
                                        br'[\x00-\x04\x06][\x00-\xFF]{6})\xA5\xA5'),
            'Source': compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                        br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\xAC'
                                        br'[\x01\x03\x05\x07-\x11][\x00-\xFF])\xA5\xA5'),
            'UserInputControl': compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                        br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x1C'
                                        br'[\x00-\x05][\x00-\xFF])\xA5\xA5'),
            'Volume': compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                        br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x44'
                                        br'[\x00-\x64][\x00-\xFF])\xA5\xA5'),
        }

    @staticmethod
    def _createstring(payload):
        payload.append(reduce(xor, payload))
        result = [0x0E, len(payload) + 10, 0, 0, 5, len(payload) + 1, 0, 0x0C]
        result.extend(payload)
        result.extend([0xA5, 0xA5])
        return bytes(result)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0,
        }

        payload = [0x20, 0x46, ValueStateValues[value]]
        AudioMuteCmdString = self._createstring(payload)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 1,
            'Down': 2,
        }

        payload = [0x20, 0x1B, 0xFF, 0xFF, 0xFF, ValueStateValues[value], 0xFF]
        ChannelCmdString = self._createstring(payload)
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        payload = [0x20, 0x1B, 0x00, int(value), 0xFF, 0xFF, 0xFF]
        KeypadCmdString = self._createstring(payload)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLocalOSDSuppress(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0,
        }

        payload = [0x20, 0x1F, ValueStateValues[value]]
        LocalOSDSuppressCmdString = self._createstring(payload)
        self.__SetHelper('LocalOSDSuppress', LocalOSDSuppressCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': 84,
            'OK': 92,
            'Right': 91,
            'Left': 90,
            'Up': 88,
            'Down': 89,
            'Back': 10
        }

        payload = [0x20, 0x1B, 0xFF, ValueStateValues[value], 0xFF, 0xFF, 0xFF]
        MenuNavigationCmdString = self._createstring(payload)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureFormat(self, value, qualifier):

        ValueStateValues = {
            'Wide Screen': 4,
            'Super Zoom/Auto Zoom': 5,
            'Auto': 7,
            'Unscaled': 8,
        }

        payload = [0x20, 0x3A, ValueStateValues[value]]
        PictureFormatCmdString = self._createstring(payload)
        self.__SetHelper('PictureFormat', PictureFormatCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Standby': 0,
        }

        payload = [0x20, 0x18, ValueStateValues[value]]
        PowerCmdString = self._createstring(payload)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Standby',
            2: 'Transiting Standby to On',
            3: 'Transiting On to Standby',
        }

        payload = [0x21, 0x18]
        PowerCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSmartPicture(self, value, qualifier):

        ValueStateValues = {
            'Personal': 0,
            'Standard': 1,
            'Vivid': 2,
            'Cinema': 3,
            'Natural': 4,
            'Game': 6,
        }

        payload = [0x20, 0x36, ValueStateValues[value], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        SmartPictureCmdString = self._createstring(payload)
        self.__SetHelper('SmartPicture', SmartPictureCmdString, value, qualifier)

    def UpdateSmartPicture(self, value, qualifier):

        ValueStateValues = {
            0: 'Personal',
            1: 'Standard',
            2: 'Vivid',
            3: 'Cinema',
            4: 'Natural',
            6: 'Game',
        }

        payload = [0x21, 0x36]
        SmartPictureCmdString = self._createstring(payload)
        res = self.__UpdateHelper('SmartPicture', SmartPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23]]
                self.WriteStatus('SmartPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Smart Picture: Invalid/unexpected response'])

    def SetSource(self, value, qualifier):
        
        payload = [0x20, 0xAC, self.SetSourceValues[value]]
        SourceCmdString = self._createstring(payload)
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):
        
        payload = [0x21, 0xAC]
        SourceCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = self.GetSource[res[23]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def SetUserInputControl(self, value, qualifier):

        ValueStateValues = {
            'Lock both IR and all LKB': 0,
            'Enable IR but lock all LKB': 1,
            'Enable LKB but lock IR': 2,
            'Enable both LKB and IR': 3,
            'Lock both IR and all LKB except for power LKB': 4,
            'Enable IR but lock all LKB except for power LKB': 5,
        }

        payload = [0x20, 0x1C, ValueStateValues[value]]
        UserInputControlCmdString = self._createstring(payload)
        self.__SetHelper('UserInputControl', UserInputControlCmdString, value, qualifier)

    def UpdateUserInputControl(self, value, qualifier):

        ValueStateValues = {
            0: 'Lock both IR and all LKB',
            1: 'Enable IR but lock all LKB',
            2: 'Enable LKB but lock IR',
            3: 'Enable both LKB and IR',
            4: 'Lock both IR and all LKB except for power LKB',
            5: 'Enable IR but lock all LKB except for power LKB',
        }

        payload = [0x21, 0x1C]
        UserInputControlCmdString = self._createstring(payload)
        res = self.__UpdateHelper('UserInputControl', UserInputControlCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23]]
                self.WriteStatus('UserInputControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['User Input Control: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0,
        }

        payload = [0x20, 0x34, ValueStateValues[value]]
        VideoMuteCmdString = self._createstring(payload)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            payload = [0x20, 0x44, value]
            VolumeCmdString = self._createstring(payload)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        payload = [0x21, 0x44]
        VolumeCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[23]
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_codes = {
            0x01: 'NACK: payload checksum failure or a malformed payload.',
            0x02: 'NAV: command received is not implemented by the TV set.'
        }
        if response and response[9] in error_codes:
            self.Error(['{} produced the error: {}'.format(sourceCmdName, error_codes[response[9]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex[command])
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

    def phil_10_4510_6014U(self):

        self.SetSourceValues = {
            'Main Tuner': 1,
            'VGA':        7,
            'HDMI1':      8,
            'HDMI2':      9,
            'HDMI3':      10,
            'USB':        11,
        }

        self.GetSource = {
            1:  'Main Tuner',
            7:  'VGA',
            8:  'HDMI1',
            9:  'HDMI2',
            10: 'HDMI3',
            11: 'USB',
        }

    def phil_10_4510_4014_5014(self):
        self.SetSourceValues = {
            'Main Tuner': 1,
            'HDMI1':      8,
            'HDMI2':      9,
            'USB':        11,
        }

        self.GetSource = {
            1:  'Main Tuner',
            8:  'HDMI1',
            9:  'HDMI2',
            11: 'USB',
        }

    def phil_10_4510_3011T(self):
        self.SetSourceValues = {
            'Main Tuner':   1,
            'AV1 / Scart1': 3,
            'YPbPr1':       5,
            'HDMI1':        8,
            'HDMI2':        9,
            'HDMI3':        10,
            'USB':          11,
        }

        self.GetSource = {
            1:  'Main Tuner',
            3:  'AV1 / Scart1',
            5:  'YPbPr1',
            8:  'HDMI1',
            9:  'HDMI2',
            10: 'HDMI3',
            11: 'USB',
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
            '43HFL5014/12': self.phil_10_4510_4014_5014,
            '32HFL5014/12': self.phil_10_4510_4014_5014,
            '50HFL5014/12': self.phil_10_4510_4014_5014,
            '65HFL6014U/12': self.phil_10_4510_6014U,
            '55HFL6014U/12': self.phil_10_4510_6014U,
            '50HFL6014U/12': self.phil_10_4510_6014U,
            '43HFL6014U/12': self.phil_10_4510_6014U,
            '50HFL4014/12': self.phil_10_4510_4014_5014,
            '43HFL4014/12': self.phil_10_4510_4014_5014,
            '32HFL4014/12': self.phil_10_4510_4014_5014,
            '28HFL4014/12': self.phil_10_4510_4014_5014,
            '40HFL3011T/12': self.phil_10_4510_3011T,
            '32HFL3011T/12': self.phil_10_4510_3011T,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureFormat': { 'Status': {}},
            'Power': { 'Status': {}},
            'ServicesOn': { 'Status': {}},
            'SmartPicture': { 'Status': {}},
            'Source': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }    

        self.lastPictureFormatUpdate = 0

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "AudioService",
            "CommandDetails":
                {
                    "AudioMute": "{}".format(value)
                }
        })
        if data and AudioMuteCmdString:
            self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetAudioMute')
    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up':   32,
            'Down': 33,
        }

        ChannelCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "UserInputService",
            "CommandDetails":
                {
                    "SendRCKeyCode": {
                        "RCProtocol": "RC6",
                        "RCCode": ValueStateValues[value],
                        "RCSystem": 0

                    }
                }
        })
        if data and ChannelCmdString:
            self.__SetHelper('Channel', value, qualifier, ChannelCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetChannel')
            
    def SetKeypad(self, value, qualifier):

        KeypadCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "UserInputService",
            "CommandDetails":
                {
                    "SendRCKeyCode": {
                        "RCProtocol": "RC6",
                        "RCCode": int(value),
                        "RCSystem": 0

                    }
                }
        })
        if data and KeypadCmdString:
            self.__SetHelper('Keypad', value, qualifier, KeypadCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetKeypad')
            
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home':  84,
            'OK':    92,
            'Right': 91,
            'Left':  90,
            'Up':    88,
            'Down':  89,
            'Back':  10,
        }

        MenuNavigationCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "UserInputService",
            "CommandDetails":
                {
                    "SendRCKeyCode": {
                        "RCProtocol": "RC6",
                        "RCCode": ValueStateValues[value],
                        "RCSystem": 0

                    }
                }
        })
        if data and MenuNavigationCmdString:
            self.__SetHelper('MenuNavigation', value, qualifier, MenuNavigationCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
            
    def SetPictureFormat(self, value, qualifier):

        ValueStateValues = {
            'Wide Screen': 'WideScreen',
            'Auto':        'Auto',
            'Unscaled':    'Unscaled',
        }

        PictureFormatCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "PictureService",
            "CommandDetails":
                {
                    "PictureFormat": ValueStateValues[value]
                }
        })
        if data and PictureFormatCmdString:
            self.__SetHelper('PictureFormat', value, qualifier, PictureFormatCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetPictureFormat')
            
    def UpdatePictureFormat(self, value, qualifier):

        PictureFormatStateValues = {
            'WideScreen': 'Wide Screen',
            'Auto':       'Auto',
            'Unscaled':   'Unscaled',
        }

        
        PictureFormatCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Request",
            "Fun": "PictureService",
            "CommandDetails": {
                "PictureServiceParameters": [
                    "PictureFormat",
                    "SmartPicture",
                    "VideoMute"
                ]
            }
        })

        res = self.__UpdateHelper('PictureFormat', value, qualifier, PictureFormatCmdString, data.encode('iso-8859-1'))
        if res:
            try:
                value = PictureFormatStateValues[res['CommandDetails']['PictureFormat']]
                self.WriteStatus('PictureFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Format: Invalid/unexpected response'])
            try:
                value = res['CommandDetails']['SmartPicture']
                self.WriteStatus('SmartPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Smart Picture: Invalid/unexpected response'])
            try:
                value = res['CommandDetails']['VideoMute']
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])      

    def SetPower(self, value, qualifier):

        PowerCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "PowerService",
            "CommandDetails":
                {
                    "ToPowerState": value,
                    "WebListeningServiceParameters": {}
                }
        })
        if data and PowerCmdString:
            self.__SetHelper('Power', value, qualifier, PowerCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 293,
            "CmdType": "Request",
            "Fun": "PowerService"
        })

        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString, data.encode('iso-8859-1'))
        if res:
            try:
                value = res['CommandDetails']['PowerServiceParameters']['CurrentPowerState']
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetServicesOn(self, value, qualifier):

        ServicesOnCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "EnablerService",
            "CommandDetails":
                {
                    "WebListeningServicesEnablerParameters":
                        {
                            "AmbiLightService": "On",
                            "ApplicationControlService": "On",
                            "AudioService": "On",
                            "ChannelSelectionService": "On",
                            "ClockService": "On",
                            "IPUpgradeService": "On",
                            "MyChoiceService": "On",
                            "PMSService": "On",
                            "PictureService": "On",
                            "PowerService": "On",
                            "ProfessionalSettingsService": "On",
                            "RegionandLanguageService": "On",
                            "SourceService": "On",
                            "SubtitleService": "On",
                            "TVDiscoveryService": "On",
                            "UserInputService": "On"
                        }
                }
        })
        if data and ServicesOnCmdString:
            self.__SetHelper('ServicesOn', value, qualifier, ServicesOnCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetServicesOn')
            
    def SetSmartPicture(self, value, qualifier):

        SmartPictureCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "PictureService",
            "CommandDetails":
                {
                    "SmartPicture": "{}".format(value)
                }
        })
        if data and SmartPictureCmdString:
            self.__SetHelper('SmartPicture', value, qualifier, SmartPictureCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetSmartPicture')

    def UpdateSmartPicture(self, value, qualifier):

        self.UpdatePictureFormat( None, None)

    def SetSource(self, value, qualifier):

        SourceCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "SourceService",
            "CommandDetails":
                {
                    "SourceServiceParameters":
                    {
                        "TuneToSource": "{}".format(self.SetSourceValues[value])
                    }
                }
        })
        if data and SourceCmdString:
            self.__SetHelper('Source', value, qualifier, SourceCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetSource')
            
    def UpdateSource(self, value, qualifier):

        SourceCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": 4.0,
            "Cookie": 395,
            "CmdType": "Request",
            "Fun": "SourceService"
        })

        res = self.__UpdateHelper('Source', value, qualifier, SourceCmdString, data.encode('iso-8859-1'))
        if res:
            try:
                value = self.GetSource[res['CommandDetails']['SourceServiceParameters']['TunedSource']]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'WIXP'
        data = dumps({
            "Svc": "WebListeningServices",
            "SvcVer": "4.0",
            "Cookie": 295,
            "CmdType": "Change",
            "Fun": "PictureService",
            "CommandDetails":
                {
                    "VideoMute": "{}".format(value)
                }
        })
        if data and VideoMuteCmdString:
            self.__SetHelper('VideoMute', value, qualifier, VideoMuteCmdString, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        self.UpdatePictureFormat( None, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'WIXP'
            data = dumps({
                "Svc": "WebListeningServices",
                "SvcVer": "4.0",
                "Cookie": 295,
                "CmdType": "Change",
                "Fun": "AudioService",
                "CommandDetails":
                    {
                        "Volume": value
                    }
            })
            if data and VolumeCmdString:
                self.__SetHelper('Volume', value, qualifier, VolumeCmdString, data.encode('iso-8859-1'))
            else:
                self.Discard('Invalid Command for SetVolume')
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True



        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json; charset=utf-8'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json; charset=utf-8'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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
            else:
                res = self.__CheckResponseForErrors(command, res)        
        return res                

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetServicesOn( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def phil_10_4510_6014U(self):
        self.SetSourceValues = {
            'Main Tuner': 'MainTuner',
            'VGA':        'VGA',
            'HDMI1':      'HDMI1',
            'HDMI2':      'HDMI2',
            'HDMI3':      'HDMI3',
            'USB':        'None',
        }

        self.GetSource = {
            'MainTuner': 'Main Tuner',
            'VGA':       'VGA',
            'HDMI1':     'HDMI1',
            'HDMI2':     'HDMI2',
            'HDMI3':     'HDMI3',
            'None':      'USB',
        }

    def phil_10_4510_4014_5014(self):
        self.SetSourceValues = {
            'Main Tuner': 'MainTuner',
            'HDMI1':      'HDMI1',
            'HDMI2':      'HDMI2',
            'USB':        'None',
        }

        self.GetSource = {
            'MainTuner': 'Main Tuner',
            'HDMI1':     'HDMI1',
            'HDMI2':     'HDMI2',
            'None':      'USB',
        }

    def phil_10_4510_3011T(self):
        self.SetSourceValues = {
            'Main Tuner':   'MainTuner',
            'AV1 / Scart1': 'Scart1',
            'YPbPr1':       'YPbPr1',
            'HDMI1':        'HDMI1',
            'HDMI2':        'HDMI2',
            'HDMI3':        'HDMI3',
            'USB':          'None',
        }

        self.GetSource = {
            'MainTuner': 'Main Tuner',
            'Scart1':    'AV1 / Scart1',
            'YPbPr1':    'YPbPr1',
            'HDMI1':     'HDMI1',
            'HDMI2':     'HDMI2',
            'HDMI3':     'HDMI3',
            'None':      'USB',
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
