from extronlib.system import ProgramLog, Wait
import base64
import urllib.error
import urllib.request
from json import loads, dumps
import hashlib

class DeviceClass:
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioSource': {'Parameters': ['Input'], 'Status': {}},
            'CurrentLayoutStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'Layout': {'Parameters': ['Window 1 Input', 'Window 2 Input', 'Window 3 Input', 'Window 4 Input'], 'Status': {}},
            'Record': {'Parameters': ['Input', 'Record', 'Encoder'], 'Status': {}},
            'RecordSettings': {'Parameters': ['Input', 'Record', 'File Name', 'File Type', 'File Content'], 'Status': {}},
            'SessionID': {'Status': {}},
            'Stream': {'Parameters': ['Input', 'Stream', 'Encoder', 'Type'], 'Status': {}},
            'VideoSource': {'Status': {}},
        }

        self.sessionID = None
        self.md5string = None

    def md5stringGenerate(self):
        string = '{}:myrealm:{}'.format(self.deviceUsername, self.devicePassword)
        result = hashlib.md5(string.encode())
        self.md5string = str(result.hexdigest())

    def SetAudioSource(self, value, qualifier):

        InputStates = {
            '1': '/_dev0',
            '2': '/_dev1',
            '3': '/_dev2',
            '4': '/_dev3'
        }

        ValueStateValues = {
            'Embedded': 0,
            'Line in': 1,
            'Microphone': 2
        }

        _input = qualifier['Input']
        if self.sessionID and _input in InputStates and value in ValueStateValues:
            AudioSourceCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_SET_AUDIO_SOURCE",
                                    "sessid": self.sessionID,
                                    "AudioSource": ValueStateValues[value]
                })
            self.__SetHelper('AudioSource', value, qualifier, AudioSourceCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetAudioSource')

    def UpdateAudioSource(self, value, qualifier):

        InputStates = {
            '1': '/_dev0',
            '2': '/_dev1',
            '3': '/_dev2',
            '4': '/_dev3'
        }

        ValueStateValues = {
            0: 'Embedded',
            1: 'Line in',
            2: 'Microphone'
        }

        _input = qualifier['Input']
        if self.sessionID and _input in InputStates:
            AudioSourceCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_GET_AUDIO_SOURCE",
                                    "sessid": self.sessionID
                })
            res = self.__UpdateHelper('AudioSource', value, qualifier, AudioSourceCmdString, jsonData.encode())
            if res:
                try:
                    value = ValueStateValues[int(res['AudioSource'])]
                    self.WriteStatus('AudioSource', value, {'Input': _input})
                except (KeyError, IndexError):
                    self.Error(['Audio Source: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioSource')

    def UpdateFirmwareVersion(self, value, qualifier):

        if self.sessionID:
            FirmwareVersionCmdString = '/_dev0'
            jsonData = dumps({
                "Function": "SYSTEM_GET_VERSION_INFO",
                                "sessid": self.sessionID
                })
            res = self.__UpdateHelper('FirmwareVersion', value, qualifier, FirmwareVersionCmdString, jsonData.encode())
            if res:
                try:
                    value = str(res['FirmwareVersion'])
                    self.WriteStatus('FirmwareVersion', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Firmware Version: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFirmwareVersion')

    def UpdateCurrentLayoutStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Quad Screen',
            1: 'Picture over Picture',
            2: 'Picture in Picture',
            3: 'Full Screen',
            5: 'Picture by Picture'
        }

        if self.sessionID:
            CurrentLayoutStatusCmdString = '/_dev0'
            jsonData = dumps({
                "Function": "APPS_GET_PGM_STATUS",
                                    "sessid": self.sessionID
                })
            res = self.__UpdateHelper('CurrentLayoutStatus', value, qualifier, CurrentLayoutStatusCmdString, jsonData.encode())
            if res:
                try:
                    value = ValueStateValues[int(res['PgmType'])]
                    self.WriteStatus('CurrentLayoutStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Current Layout Status: Invalid/unexpected response'])

    def SetLayout(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': 0,
            'HDMI 2': 1,
            'HDMI 3': 2,
            'HDMI 4': 3
        }

        ValueStateValues = {
            'Quad Screen': 0,
            'Picture over Picture': 1,
            'Picture in Picture': 2,
            'Full Screen': 3,
            'Picture by Picture': 5
        }

        Win1In = qualifier['Window 1 Input']
        Win2In = qualifier['Window 2 Input']
        Win3In = qualifier['Window 3 Input']
        Win4In = qualifier['Window 4 Input']
        if self.sessionID and Win1In in InputStates and Win2In in InputStates and Win3In in InputStates and Win4In in InputStates:
            LayoutCmdString = '/_dev0'
            jsonData = dumps({
                "Function": "APPS_SET_PGM_STATUS",
                "PgmType": ValueStateValues[value],
                                "PgmArg1": InputStates[Win1In],
                                    "PgmArg2": InputStates[Win2In],
                                    "PgmArg3": InputStates[Win3In],
                                    "PgmArg4": InputStates[Win4In],
                                    "sessid": self.sessionID
                })
            self.__SetHelper('Layout', value, qualifier, LayoutCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetLayout')

    def SetRecord(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': '/_dev0',
            'HDMI 2': '/_dev1',
            'HDMI 3': '/_dev2',
            'HDMI 4': '/_dev3',
            'PGM': '/_dev4'
        }

        RecordStates = {
            'Main': 1,
            'Sub': 2
        }

        EncoderStates = {
            'Main': 0,
            'Sub': 1
        }

        ValueStateValues = {
            'Start': 1,
            'Stop': 0
        }

        _input = qualifier['Input']
        record = qualifier['Record']
        encoder = qualifier['Encoder']
        if (self.sessionID and _input in InputStates and record in RecordStates and encoder in EncoderStates and
            value in ValueStateValues):
            RecordCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_SET_RECORD_STATUS",
                "sessid": self.sessionID,
                                "RecordNum": RecordStates[record],
                                "EncoderNum": EncoderStates[encoder],
                                "Status": ValueStateValues[value]
                })
            self.__SetHelper('Record', value, qualifier, RecordCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetRecord')

    def UpdateRecord(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': '/_dev0',
            'HDMI 2': '/_dev1',
            'HDMI 3': '/_dev2',
            'HDMI 4': '/_dev3',
            'PGM': '/_dev4'
        }

        RecordStates = {
            'Main': 1,
            'Sub': 2
        }

        EncoderStates = {
            0: 'Main',
            1: 'Sub'
        }

        ValueStateValues = {
            1: 'Start',
            0: 'Stop'
        }

        _input = qualifier['Input']
        record = qualifier['Record']
        if self.sessionID and _input in InputStates and record in RecordStates:
            RecordCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_GET_RECORD_STATUS",
                                    "sessid": self.sessionID,
                "RecordNum": RecordStates[record]
                            })
            res = self.__UpdateHelper('Record', value, qualifier, RecordCmdString, jsonData.encode())
            if res:
                try:
                    value = ValueStateValues[int(res['Status'])]
                    encoder = EncoderStates[int(res['EncoderNum'])]
                    self.WriteStatus('Record', value, {'Input': _input, 'Record': record, 'Encoder': encoder})
                except (KeyError, IndexError):
                    self.Error(['Record: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecord')

    def SetRecordSettings(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': '/_dev0',
            'HDMI 2': '/_dev1',
            'HDMI 3': '/_dev2',
            'HDMI 4': '/_dev3',
            'PGM': '/_dev4'
        }

        RecordStates = {
            'Main': 1,
            'Sub': 2
        }

        FileTypeStates = {
            'AVI': 0,
            'MP4': 1,
            'TS': 2,
            'MOV': 3
        }

        FileContentStates = {
            'Video and Audio': 0,
            'Video Only': 1,
            'Audio Only': 2
        }

        _input = qualifier['Input']
        record = qualifier['Record']
        fileName = qualifier['File Name']
        fileType = qualifier['File Type']
        fileContent = qualifier['File Content']
        if (self.sessionID and _input in InputStates and record in RecordStates and fileName and
            fileType in FileTypeStates and fileContent in FileContentStates):
            RecordSettingsCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_SET_RECORD_PROPERTY",
                                    "sessid": self.sessionID,
                "RecordNum": RecordStates[record],
                                "FileName": fileName,
                                "FileType": FileTypeStates[fileType],
                                "FileContent": FileContentStates[fileContent]
                            })
            self.__SetHelper('RecordSettings', value, qualifier, RecordSettingsCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetRecordSettings')

    def UpdateSessionID(self, value, qualifier):

        if not self.md5string:
            self.md5stringGenerate()

        if self.deviceUsername and self.md5string:
            SessionIDCmdString = '/_dev0'
            jsonData = dumps(
                {"login": "{}:myrealm:{}".format(self.deviceUsername, self.md5string)}
                )
            res = self.__UpdateHelper('SessionID', value, qualifier, SessionIDCmdString, jsonData.encode())
            if res:
                try:
                    self.sessionID = str(res['sessid'])
                    self.WriteStatus('SessionID', self.sessionID, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Session ID: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSessionID')

    def SetStream(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': '/_dev0',
            'HDMI 2': '/_dev1',
            'HDMI 3': '/_dev2',
            'HDMI 4': '/_dev3',
            'PGM': '/_dev4'
        }

        StreamStates = {
            'Main': 1,
            'Sub': 2
        }

        EncoderStates = {
            'Main': 0,
            'Sub': 1,
            'Disable': 9
        }

        TypeStates = {
            'RTSP': 0,
            'RTMP': 1,
            'TS over UDP': 2,
            'HLS': 3,
            'TS over RTSP': 4,
            'NDI': 5
        }

        ValueStateValues = {
            'Start': 1,
            'Stop': 0
        }

        _input = qualifier['Input']
        stream = qualifier['Stream']
        encoder = qualifier['Encoder']
        _type = qualifier['Type']
        if (self.sessionID and _input in InputStates and stream in StreamStates and encoder in EncoderStates
            and _type in TypeStates and value in ValueStateValues):
            StreamCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_SET_STREAMING_STATUS",
                "sessid": self.sessionID,
                                "StreamNum": StreamStates[stream],
                                "EncoderNum": EncoderStates[encoder],
                                "StreamType": TypeStates[_type],
                                "Status": ValueStateValues[value]
                })
            self.__SetHelper('Stream', value, qualifier, StreamCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetStream')

    def UpdateStream(self, value, qualifier):

        InputStates = {
            'HDMI 1/SDI': '/_dev0',
            'HDMI 2': '/_dev1',
            'HDMI 3': '/_dev2',
            'HDMI 4': '/_dev3',
            'PGM': '/_dev4'
        }

        StreamStates = {
            'Main': 1,
            'Sub': 2
        }

        EncoderStates = {
            0: 'Main',
            1: 'Sub',
            9: 'Disable'
        }

        TypeStates = {
            0: 'RTSP',
            1: 'RTMP',
            2: 'TS over UDP',
            3: 'HLS',
            4: 'TS over RTSP',
            5: 'NDI'
        }

        ValueStateValues = {
            1: 'Start',
            0: 'Stop'
        }

        _input = qualifier['Input']
        stream = qualifier['Stream']
        if self.sessionID and _input in InputStates and stream in StreamStates:
            StreamCmdString = InputStates[_input]
            jsonData = dumps({
                "Function": "APPS_GET_STREAMING_STATUS",
                                    "sessid": self.sessionID,
                "StreamNum": StreamStates[stream]
                })
            res = self.__UpdateHelper('Stream', value, qualifier, StreamCmdString, jsonData.encode())
            if res:
                try:
                    value = ValueStateValues[int(res['Status'])]
                    encoder = EncoderStates[int(res['EncoderNum'])]
                    _type = TypeStates[int(res['StreamType'])]
                    self.WriteStatus('Stream', value, {'Input': _input, 'Stream': stream, 'Encoder': encoder, 'Type': _type})
                except (KeyError, IndexError):
                    self.Error(['Stream: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStream')

    def SetVideoSource(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 2,
            'SDI': 6
        }

        if self.sessionID and value in ValueStateValues:
            VideoSourceCmdString = '/_dev0'
            jsonData = dumps({
                "Function": "APPS_SET_VIDEO_SOURCE",
                                    "sessid": self.sessionID,
                "VideoSource": ValueStateValues[value]
                })
            self.__SetHelper('VideoSource', value, qualifier, VideoSourceCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetVideoSource')

    def UpdateVideoSource(self, value, qualifier):

        ValueStateValues = {
            2: 'HDMI',
            6: 'SDI'
        }

        if self.sessionID:
            VideoSourceCmdString = '/_dev0'
            jsonData = dumps({
                "Function": "APPS_GET_VIDEO_SOURCE",
                                    "sessid": self.sessionID
                })
            res = self.__UpdateHelper('VideoSource', value, qualifier, VideoSourceCmdString, jsonData.encode())
            if res:
                try:
                    value = ValueStateValues[int(res['VideoSource'])]
                    self.WriteStatus('VideoSource', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Source: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoSource')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = loads(response.read().decode('utf-8', 'ignore'))
        return res

    def __SetHelper(self, command, value, qualifier, resource, data=None):

        self.Debug = True

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'application/json'}
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
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')  # method defaults to GET when data is None

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
        print('ON CONNECTED')
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


class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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
