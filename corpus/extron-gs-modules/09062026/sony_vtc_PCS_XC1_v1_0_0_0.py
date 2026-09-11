from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack
from re import compile, findall, DOTALL, match, search


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
        self.Models = {}

        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallStatus': {'Status': {}},
            'DisplayLayout': {'Status': {}},
            'EnableRecording': {'Status': {}},
            'EnableStreaming': {'Status': {}},
            'FarEndCameraControl': {'Status': {}},
            'FarEndCameraPreset': {'Status': {}},
            'Hook': {'Status': {}},
            'InputFar': {'Status': {}},
            'InputNear': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'NearEndCameraControl': {'Status': {}},
            'NearEndCameraPreset': {'Status': {}},
            'Power': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(ring manual|connect complete|connect status\x0D\x0D\x0A2|connect status\x0D\x0D\x0A3|disconnect|dial cancel)'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'status power (power-on|stand-by)'), self.__MatchPower, None)
            self.AddMatchString(compile(b'status macstatus\r\r\n(CAMERA|HDMI)\r'), self.__MatchInputNear, None)
            self.AddMatchString(compile(b'(not init|busy|syntax error|socket error|execute error|buffer full|not supported|not power on|on networ test|not communication|on update|not connect|timeout|preset type error|preset no memory|error)\r'), self.__MatchError, None)

            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

        self.AddMatchString(compile(b'\xFF\xFD\x18'), self.__MatchTelnetInitiate, None)

    def __MatchTelnetInitiate(self, match, qualifier):
        self.SetMatchTelnetInitiate(None, None)

    def SetMatchTelnetInitiate(self, value, qualifier):
        self.Send('\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F')
        self.Send('\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E')
        self.Send('\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        if self.deviceUsername:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAutoAnswer(self, value, qualifier):

        States = {
            'On': 'setup save answer autoincome-on\r\n',
            'Off': 'setup save answer autoincome-off\r\n'
        }

        self.__SetHelper('AutoAnswer', States[value], value, qualifier)

    def __MatchCallStatus(self, match, tag):

        States = {
            'ring manual': 'Incoming',
            'connect complete': 'Connected',
            'connect status\x0D\x0D\x0A3': 'Connecting',
            'disconnect': 'Disconnected',
            'dial cancel': 'Dial Cancelled',
            'connect status\x0D\x0D\x0A2': 'Outgoing',

        }

        self.WriteStatus('CallStatus', States[match.group(1).decode()], None)

    def SetDisplayLayout(self, value, qualifier):

        States = {
            'Full': 'full',
            'Side By Side': 'sidebyside',
            'Picture And Picture': 'pandp',
            'PIP - Upper Right': 'pinp-upright',
            'PIP - Upper Left': 'pinp-upleft',
            'PIP - Lower Right': 'pinp-downright',
            'PIP - Lower Left': 'pinp-downleft',
            'PIP - Bottom Most Left': 'pinp-downrightside'
        }

        self.__SetHelper('DisplayLayout', 'layout {0}\r\n'.format(States[value]), value, qualifier)

    def SetEnableRecording(self, value, qualifier):

        States = {
            'Enable': 'setup save admin recording-on\r\n',
            'Disable': 'setup save admin recording-off\r\n'
        }

        self.__SetHelper('EnableRecording', States[value], value, qualifier)

    def SetEnableStreaming(self, value, qualifier):

        States = {
            'Enable': 'setup save admin streaming-on\r\n',
            'Disable': 'setup save admin streaming-off\r\n'
        }

        self.__SetHelper('EnableStreaming', States[value], value, qualifier)

    def SetFarEndCameraControl(self, value, qualifier):

        States = {
            'Zoom Stop': 'far camera zoom-stop\r\n',
            'Zoom Tele': 'far camera zoom-tele\r\n',
            'Zoom Wide': 'far camera zoom-wide\r\n',
            'Tilt Up': 'far camera up\r\n',
            'Tilt Down': 'far camera down\r\n',
            'Pan Left': 'far camera left\r\n',
            'Pan Right': 'far camera right\r\n',
            'PanTilt Stop': 'far camera pantilt-stop\r\n',
            'Focus Stop': 'far camera focus-stop\r\n',
            'Focus Far': 'far camera focus-far\r\n',
            'Focus Near': 'far camera focus-near\r\n',
        }

        self.__SetHelper('FarEndCameraControl', States[value], value, qualifier)

    def SetFarEndCameraPreset(self, value, qualifier):

        Preset = qualifier['Preset'] if 0 <= int(qualifier['Preset']) <= 6 else ''

        if Preset:

            States = {
                'Recall': 'far camera move /{}/\r\n'.format(Preset),
                'Save': 'far camera save /{}/\r\n'.format(Preset),
            }

            self.__SetHelper('FarEndCameraPreset', States[value], value, qualifier)

        else:
            self.Discard('Invalid Command for SetFarEndCameraPreset')

    def SetHook(self, value, qualifier):

        States = {
            'Hang Up': 'disconnect\r\n',
            'Answer Call': 'answer accept\r\n',
            'Reject Call': 'answer reject\r\n',
        }

        DialString = qualifier['Number']

        if value == 'Dial':
            if DialString:
                self.__SetHelper('Hook', 'dial /{0}/\r\n'.format(DialString), value, qualifier)
            else:
                self.Discard('Invalid Command for SetHook')
        else:
            self.__SetHelper('Hook', States[value], value, qualifier)

    def SetInputFar(self, value, qualifier):

        States = {
            'Main Camera': 'far video camera\r\n',
            'HDMI': 'far video hdmi\r\n'
        }

        self.__SetHelper('InputFar', States[value], value, qualifier)

    def SetInputNear(self, value, qualifier):

        States = {
            'Main Camera': 'video camera\r\n',
            'HDMI': 'video hdmi\r\n'
        }

        self.__SetHelper('InputNear', States[value], value, qualifier)

    def UpdateInputNear(self, value, qualifier):
        self.__UpdateHelper('InputNear', 'status macstatus\r\n', value, qualifier)

    def __MatchInputNear(self, match, tag):

        States = {
            'CAMERA': 'Main Camera',
            'HDMI': 'HDMI'
        }

        self.WriteStatus('InputNear', States[match.group(1).decode()], None)

    def SetIRRemoteEmulation(self, value, qualifier):

        States = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '0': '9',
            '*': '10',
            '#': '11',
            'Mic': '16',
            'Connect': '17',
            'Volume Up': '18',
            'Volume Down': '19',
            'Power': '21',
            'Camera': '23',
            'Zoom Out': '30',
            'Zoom In': '31',
            'Disconnect': '45',
            'Back': '52',
            'Tools': '58',
            'Video': '65',
            'F1': '95',
            'F2': '96',
            'F3': '97',
            'F4': '98',
            'Return': '102',
            'Layout': '104',
            'Presentation': '107',
            'Enter': '110',
            'Up': '111',
            'Down': '119',
            'Left': '123',
            'Right': '115',
            'Stop': '144',
            'Long Press 1': '192',
            'Long Press 2': '193',
            'Long Press 3': '194',
            'Long Press 4': '195',
            'Long Press 5': '196',
            'Long Press 6': '197',
        }

        self.__SetHelper('IRRemoteEmulation', 'remcom {0}\r\n'.format(States[value]), value, qualifier)

    def SetNearEndCameraControl(self, value, qualifier):

        FocusSpeed = qualifier['Focus Speed'] if 0 <= int(qualifier['Focus Speed']) <= 7 else ''
        PanSpeed = qualifier['Pan Speed'] if 0 <= int(qualifier['Pan Speed']) <= 18 else ''
        TiltSpeed = qualifier['Tilt Speed'] if 0 <= int(qualifier['Tilt Speed']) <= 14 else ''
        ZoomSpeed = qualifier['Zoom Speed'] if 0 <= int(qualifier['Zoom Speed']) <= 7 else ''

        if FocusSpeed and PanSpeed and TiltSpeed and ZoomSpeed:

            States = {
                'Zoom Tele': 'camera zoom-tele /{}/\r\n'.format(ZoomSpeed),
                'Zoom Wide': 'camera zoom-wide /{}/\r\n'.format(ZoomSpeed),
                'Zoom Stop': 'camera zoom-stop\r\n',
                'PanTilt Up': 'camera up /{}/\r\n'.format(TiltSpeed),
                'PanTilt Down': 'camera down /{}/\r\n'.format(TiltSpeed),
                'PanTilt Left': 'camera left /{}/\r\n'.format(PanSpeed),
                'PanTilt Right': 'camera right /{}/\r\n'.format(PanSpeed),
                'PanTilt UpRight': 'camera upright /{}/{}/\r\n'.format(TiltSpeed, PanSpeed),
                'PanTilt UpLeft': 'camera upleft /{}/{}/\r\n'.format(TiltSpeed, PanSpeed),
                'PanTilt DownRight': 'camera downright /{}/{}/\r\n'.format(TiltSpeed, PanSpeed),
                'PanTilt DownLeft': 'camera downleft /{}/{}/\r\n'.format(TiltSpeed, PanSpeed),
                'PanTilt Stop': 'camera pantilt-stop\r\n',
                'Focus Near': 'camera focus-near /{}/\r\n'.format(FocusSpeed),
                'Focus Far': 'camera focus-far /{}/\r\n'.format(FocusSpeed),
                'Focus Stop': 'camera focus-stop\r\n',
                'Focus Auto': 'camera focus-auto\r\n'
            }

            self.__SetHelper('NearEndCameraControl', States[value], value, qualifier)

        else:
            self.Discard('Invalid Command for SetNearEndCameraControl')

    def SetNearEndCameraPreset(self, value, qualifier):

        Preset = qualifier['Preset'] if 0 <= int(qualifier['Preset']) <= 100 else ''

        if Preset:

            States = {
                'Recall': 'camera move /{}/\r\n'.format(Preset),
                'Save': 'camera save /{}/\r\n'.format(Preset),
                'Reset': 'camera reset /{}/\r\n'.format(Preset),
            }

            self.__SetHelper('NearEndCameraPreset', States[value], value, qualifier)

        else:
            self.Discard('Invalid Command for SetNearEndCameraPreset')

    def SetPower(self, value, qualifier):

        State = {
            'On': 'power-on',
            'Off': 'stand-by',
        }

        self.__SetHelper('Power', '{0}\r\n'.format(State[value]), value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'status power\r\n', value, qualifier)

    def __MatchPower(self, match, tag):

        State = {
            'power-on': 'On',
            'stand-by': 'Off'
        }

        self.WriteStatus('Power', State[match.group(1).decode()], None)

    def __MatchError(self, match, tag):

        Errors = {
            'syntax error': 'Syntax Error',
            'status error': 'Status Error',
            'socket error': 'Socket Error',
            'not init': 'Not Initialized',
            'busy': 'Under Execution',
            'execute error': 'Execution Error',
            'buffer full': 'Buffer full',
            'not supported': 'Not Supported',
            'not power on': 'Power error',
            'on network test': 'During network measurement',
            'not communication': 'Not communicated (far control)',
            'on update': 'During Updating',
            'not connect': 'No Camera Connected',
            'timeout': 'Time out',
            'preset type error': 'Preset Type Error',
            'preset no memory': 'No preset setting registered',
            'error': 'Error Type: Other',
        }

        self.Error([Errors[match.group(1).decode()]])    

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