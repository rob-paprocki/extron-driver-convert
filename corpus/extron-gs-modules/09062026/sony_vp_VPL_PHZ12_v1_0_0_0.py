from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import json
import hashlib
import binascii


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
        self.deviceUsername = 'Username'
        self.devicePassword = 'Projector'
        self.Models = {}

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
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.lastLampUsageUpdate = 0
        self.sha256hash = ''
        self.Authenticated = True        

        if 'Serial' not in self.ConnectionType:

            self.Authenticated = False
            self.AddMatchString(re.compile(b'([a-zA-Z0-9]{8})\r\n'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'NOKEY\r\n|OK\r\n'), self.__MatchAuthentication, False)
            
    def __MatchAuthentication(self, match, tag):
        if not tag:
            self.Authenticated = True
        else:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.sha256(full_str.encode())
            self.sha256hash = binascii.hexlify(code_hash.digest()).decode()
            self.SetAuthentication(None, None)

    def SetAuthentication(self, value, qualifier):
        self.Send(self.sha256hash + '\r\n')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '"4_3"',
            '16:9': '"16_9"',
            'Full': '"full"',
            'Zoom': '"zoom"',
            'Full 1': '"full1"',
            'Full 2': '"full2"',
            'Full 3': '"full3"',
            'Normal': '"normal"'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'aspect {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '"4_3"': '4:3',
            '"16_9"': '16:9',
            '"full"': 'Full',
            '"zoom"': 'Zoom',
            '"full1"': 'Full 1',
            '"full2"': 'Full 2',
            '"full3"': 'Full 3',
            '"normal"': 'Normal'
        }

        AspectRatioCmdString = 'aspect ?\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '"on"',
            'Off': '"off"'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'muting {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '"on"': 'On',
            '"off"': 'Off'
        }

        AudioMuteCmdString = 'muting ?\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'apa_exec\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '"off"',
            'CC1': '"cc1"',
            'CC2': '"cc2"',
            'CC3': '"cc3"',
            'CC4': '"cc4"',
            'Text1': '"text1"',
            'Text2': '"text2"',
            'Text3': '"text3"',
            'Text4': '"text4"'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = 'cc_display {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '"off"': 'Off',
            '"cc1"': 'CC1',
            '"cc2"': 'CC2',
            '"cc3"': 'CC3',
            '"cc4"': 'CC4',
            '"text1"': 'Text1',
            '"text2"': 'Text2',
            '"text3"': 'Text3',
            '"text4"': 'Text4'
        }

        ClosedCaptionCmdString = 'cc_display ?\r\n'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'no_err': 'No Error',
            'err_power': 'Power Supply Error',
            'err_power2': 'Power Supply (D5V) Error',
            'err_system2': 'System Error 2',
            'err_cover': 'Cover Error',
            'err_light_src': 'Light-source Error',
            'err_lens_cover': 'Lens Cover Error',
            'err_nolens': 'Lens Not Attached Error',
            'err_shock': 'Shock Error',
            'err_attitude': 'Installation Angle Error',
            'err_temp': 'Temperature Error',
            'err_fan': 'Fan Error',
            'err_wheel': 'Wheel Rotation Error',
            'err_light_over': 'Luminance Error',
            'err_assy': 'Assembling Error',
            'err_lens_shift': 'Lens Shift Error',
            'err_shutter': 'Shutter Error'
        }

        DeviceStatusCmdString = 'error ?\r\n'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                response = json.loads(res)
                if len(response) > 1:
                    value = 'Multiple Errors'
                else:
                    value = ValueStateValues[response[0]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError, TypeError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '"off"',
            'On': '"on"'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'controlkey_lock {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '"off"': 'Off',
            '"on"': 'On'
        }

        ExecutiveModeCmdString = 'controlkey_lock ?\r\n'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '"on"',
            'Off': '"off"'
        }

        if value in ValueStateValues:
            FreezeCmdString = 'freeze {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '"on"': 'On',
            '"off"': 'Off'
        }

        FreezeCmdString = 'freeze ?\r\n'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB': '"rgb1"',
            'HDMI 1': '"hdmi1"',
            'HDMI 2': '"hdmi2"',
            'HDBaseT': '"hdbaset1"',
            'Video': '"video1"',
            'USB B': '"usb_b"',
            'Network': '"network"'
        }

        if value in ValueStateValues:
            InputCmdString = 'input {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '"rgb1"': 'RGB',
            '"hdmi1"': 'HDMI 1',
            '"hdmi2"': 'HDMI 2',
            '"hdbaset1"': 'HDBaseT',
            '"video1"': 'Video',
            '"usb_b"': 'USB B',
            '"network"': 'Network'
        }

        InputCmdString = 'input ?\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'timer ?\r\n'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                response = json.loads(res)
                value = response[1]['light_src']
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError, KeyError, TypeError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

            try:
                response = json.loads(res)
                value = response[0]['operation']
                self.WriteStatus('OperationHours', value, qualifier)
            except (KeyError, IndexError, ValueError, TypeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])
       
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '"up"',
            'Down': '"down"',
            'Left': '"left"',
            'Right': '"right"',
            'Enter': '"enter"',
            'Menu': '"menu"',
            'Return': '"return"'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'key {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateLampUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '"on"',
            'Off': '"off"'
        }

        if value in ValueStateValues:
            PowerCmdString = 'power {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '"on"': 'On',
            '"startup"': 'Startup',
            '"cooling1"': 'Cooling 1',
            '"cooling2"': 'Cooling 2',
            '"saving_cooling1"': 'Power Saving Cooling 1',
            '"saving_cooling2"': 'Power Saving Cooling 2',
            '"saving_standby"': 'Power Saving Standby',
            '"standby"': 'Off'
        }

        PowerCmdString = 'power_status ?\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '"on"',
            'Off': '"off"'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'blank {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '"on"': 'On',
            '"off"': 'Off'
        }

        VideoMuteCmdString = 'blank ?\r\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'volume {}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)  # Query delay not needed. Tested on v1_0_0
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume ?\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'err_cmd\r\n': 'Command format error.',
            'err_option\r\n': 'Command option error.',
            'err_inactive\r\n': 'Invalid error.',
            'err_val\r\n': 'Command value error.',
            'err_auth\r\n': 'Network authentication error.',
            'err_internal1\r\n': 'Internal communication error 1 of the projector.',
            'err_internal2\r\n': 'Internal communication error 2 of the projector.'
        }

        if response and response.lower() in DEVICE_ERROR_CODES:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[response.lower()])])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if self.Authenticated:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
            else:
                self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated:
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
                    
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.sha256hash = ''
        if 'Serial' not in self.ConnectionType:
            self.Authenticated = False
        else:
            self.Authenticated = True
            
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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
