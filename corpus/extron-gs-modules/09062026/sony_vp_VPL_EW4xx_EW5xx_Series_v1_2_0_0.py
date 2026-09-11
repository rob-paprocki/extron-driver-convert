from extronlib.interface import SerialInterface, EthernetClientInterface
from json import loads
import re
import hashlib
import binascii


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'VPL-EW575': self.sony_1_3223_EW,
            'VPL-EW578': self.sony_1_3223_EW_HD,
            'VPL-EW455': self.sony_1_3223_EW,
            'VPL-EW435': self.sony_1_3223_EW,
            'VPL-EX575': self.sony_1_3223_EX,
            'VPL-EX570': self.sony_1_3223_EX,
            'VPL-EX455': self.sony_1_3223_EX,
            'VPL-EX450': self.sony_1_3223_EX,
            'VPL-EX435': self.sony_1_3223_EX,
            'VPL-EX430': self.sony_1_3223_EX,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.devicePassword = 'Projector'
        self.sha256hash = ''
        self.StartQuery = True

        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
            self.AddMatchString(re.compile(b'([a-zA-Z0-9]{8})\r\n'), self.__MatchAuthentication, None)

    def __MatchAuthentication(self, match, tag):
        self.StartQuery = True
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.sha256(full_str.encode())
        self.sha256hash = binascii.hexlify(code_hash.digest()).decode()
        self.Send(self.sha256hash + '\r\n')

    def SetAspectRatio(self, value, qualifier):

        self.__SetHelper('AspectRatio', 'aspect "{}"\r\n'.format(self.aspect_states[value]), value, qualifier)

    def SetAudioMute(self, value, qualifier):

        self.__SetHelper('AudioMute', 'muting "{}"\r\n'.format(value.lower()), value, qualifier)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'apa_exec\r\n', value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        self.__SetHelper('ClosedCaption', 'cc_display "{}"\r\n'.format(value.lower()), value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        res = self.__UpdateHelper('DeviceStatus', 'error ?\r\n', value, qualifier)
        if res:
            try:
                value = {
                    'no_err': 'Normal',
                    'err_power': 'Power Supply Error',
                    'err_power2': 'Power Supply (D5V) Error',
                    'err_system2': 'System Error',
                    'err_cover': 'Cover Error',
                    'err_light_src': 'Light-Source Error',
                    'err_lens_cover': 'Lens Cover Error',
                    'err_shock': 'Shock Error',
                    'err_nolens': 'Lens (not attached) Error',
                    'err_attitude': 'Installation Angle Error',
                    'err_temp': 'Temperature Error',
                    'err_fan': 'Fan Error',
                    'err_wheel': 'Wheel Rotation Error',
                    'err_light_over': 'Luminance Error',
                    'err_assy': 'Assembling Error',
                    'err_lens_shift': 'Lens Shift Error',
                    'err_shutter': 'Shutter Error'
                }[loads(res)[0]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DeviceStatus: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        self.__SetHelper('ExecutiveMode', 'controlkey_lock "{}"\r\n'.format(value.lower()), value, qualifier)

    def SetFreeze(self, value, qualifier):

        self.__SetHelper('Freeze', 'freeze "{}"\r\n'.format(value.lower()), value, qualifier)

    def SetInput(self, value, qualifier):

        self.__SetHelper('Input', 'input "{}"\r\n'.format(self.input_states[value]), value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'input ?\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.input_names[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        state = {
            'High': 'high',
            'Standard': 'mid',
            'Low': 'low',
            'Auto': 'auto'
        }[value]
        self.__SetHelper('LampMode', 'light_output_mode "{}"\r\n'.format(state), value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'timer ?\r\n', value, qualifier)
        if res:
            try:
                value = loads(res)[0]['light_src']
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['LampUsage: Invalid/unexpected response'])

            try:
                value = loads(res)[1]['operation']
                self.WriteStatus('OperationHours', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['OperationHours: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):
        self.__SetHelper('MenuNavigation', 'key "{}"\r\n'.format(value.lower()), value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateLampUsage(value, qualifier)

    def SetPictureMode(self, value, qualifier):
        self.__SetHelper('PictureMode', 'picture_mode "{}"\r\n'.format(value.lower()), value, qualifier)

    def SetPower(self, value, qualifier):

        self.__SetHelper('Power', 'power "{}"\r\n'.format(value.lower()), value, qualifier)

    def UpdatePower(self, value, qualifier):

        res = self.__UpdateHelper('Power', 'power_status ?\r\n', value, qualifier)
        if res:
            try:
                value = {
                    'on': 'On',
                    'standby': 'Off',
                    'startup': 'Warming Up',
                    'cooling1': 'Cooling Down 1',
                    'cooling2': 'Cooling Down 2',
                    'saving_cooling1': 'Cooling Down 1',
                    'saving_cooling2': 'Cooling Down 2',
                    'saving_standby': 'Off'
                }[res[1:-3]]

                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        self.__SetHelper('VideoMute', 'blank "{}"\r\n'.format(value.lower()), value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        if 'Serial' not in self.ConnectionType:
            VideoMuteState = {
                '"on"': 'On',
                '"off"': 'Off'
            }

            VideoMuteCmdString = 'blank ?\r\n'
        else:
            VideoMuteState = {
                1: 'On',
                0: 'Off'
            }

            VideoMuteCmdString = b'\xA9\x00\x30\x01\x00\x00\x31\x9A'

        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                if 'Serial' not in self.ConnectionType:
                    value = VideoMuteState[res[:-2]]
                else:
                    value = VideoMuteState[res[5]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'volume {}\r\n'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '"err_cmd"\r\n': 'Command format error.',
            '"err_option"\r\n': 'Command option error.',
            '"err_inactive"\r\n': 'Invalid error.',
            '"err_val"\r\n': 'Command value error.',
            '"err_auth"\r\n': 'Network authentication error.',
            '"err_internal1"\r\n': 'Internal communication error 1 of the projector.',
            '"err_internal2"\r\n': 'Internal communication error 2 of the projector.'
        }
        if response:
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''

        if sourceCmdName == 'VideoMute' and 'Serial' in self.ConnectionType:
            return response.encode('iso-8859-1')
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.StartQuery:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    self.Error(['{}: Invalid/Unexpected Response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode('iso-8859-1'))
        else:
            self.Error(['Ethernet: Waiting to Authenticate with the device'])

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.StartQuery:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command == 'VideoMute' and 'Serial' in self.ConnectionType:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=8)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')

            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode('iso-8859-1'))
        else:
            self.Error(['Ethernet: Waiting to Authenticate with the device'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.sha256hash = ''
        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
        else:
            self.StartQuery = True

    def sony_1_3223_EW(self):

        self.aspect_states = {
            '4:3': '4_3',
            '16:9': '16_9',
            'Full 1': 'full1',
            'Full 2': 'full2',
            'Full 3': 'full3',
            'Normal': 'normal',
            'Full': 'full',
            'Zoom': 'zoom'
        }

        self.input_states = {
            'Video': 'video1',
            'S-Video': 'svideo1',
            'Input A': 'rgb1',
            'Input B': 'rgb2',
            'Input C': 'hdmi1',
            'Input D': 'hdmi2',
            'Network': 'network',
            'USB A': 'usb_a',
            'USB B': 'usb_b'
        }
        self.input_names = {
            '"video1"': 'Video',
            '"svideo1"': 'S-Video',
            '"rgb1"': 'Input A',
            '"rgb2"': 'Input B',
            '"hdmi1"': 'Input C',
            '"hdmi2"': 'Input D',
            '"network"': 'Network',
            '"usb_a"': 'USB A',
            '"usb_b"': 'USB B'
        }

    def sony_1_3223_EW_HD(self):

        self.aspect_states = {
            '4:3': '4_3',
            '16:9': '16_9',
            'Full 1': 'full1',
            'Full 2': 'full2',
            'Full 3': 'full3',
            'Normal': 'normal',
            'Full': 'full',
            'Zoom': 'zoom'
        }

        self.input_states = {
            'Video': 'video1',
            'S-Video': 'svideo1',
            'Input A': 'rgb1',
            'Input B': 'rgb2',
            'Input C': 'hdmi1',
            'Input D': 'hdmi2',
            'Network': 'network',
            'USB A': 'usb_a',
            'USB B': 'usb_b',
            'Input E': 'hdbaset1'
        }
        self.input_names = {
            '"video1"': 'Video',
            '"svideo1"': 'S-Video',
            '"rgb1"': 'Input A',
            '"rgb2"': 'Input B',
            '"hdmi1"': 'Input C',
            '"hdmi2"': 'Input D',
            '"network"': 'Network',
            '"usb_a"': 'USB A',
            '"usb_b"': 'USB B',
            '"hdbaset1"': 'Input E'
        }

    def sony_1_3223_EX(self):

        self.aspect_states = {
            '4:3': '4_3',
            '16:9': '16_9',
            'Full 1': 'full1',
            'Normal': 'normal',
            'Zoom': 'zoom'
        }

        self.input_states = {
            'Video': 'video1',
            'S-Video': 'svideo1',
            'Input A': 'rgb1',
            'Input B': 'rgb2',
            'Input C': 'hdmi1',
            'Input D': 'hdmi2',
            'Network': 'network',
            'USB A': 'usb_a',
            'USB B': 'usb_b'
        }
        self.input_names = {
            'video1': 'Video',
            'svideo1': 'S-Video',
            'rgb1': 'Input A',
            'rgb2': 'Input B',
            'hdmi1': 'Input C',
            'hdmi2': 'Input D',
            'network': 'Network',
            'usb_a': 'USB A',
            'usb_b': 'USB B'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
