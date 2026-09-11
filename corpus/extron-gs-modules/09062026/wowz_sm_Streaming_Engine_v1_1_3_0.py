import base64
from json import loads, dumps
import urllib.error
import urllib.request
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if deviceUsername and devicePassword:
            authentication = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authentication.add_password(None, self.RootURL, deviceUsername, devicePassword)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(authentication))
        else:
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfStreamTargetSearch = 5
        self._ServerName = ''
        self._VHostName = ''
        self._ApplicationName = ''
        self.IPAddress = ipAddress
        self.IPPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FileNameString': {'Parameters': ['Date & Time'], 'Status': {}},
            'Recording': {'Parameters': ['Instance', 'Recorder Name', 'Output Path'], 'Status': {}},
            'ServerName': {'Status': {}},
            'StreamFile': {'Parameters': ['Instance'], 'Status': {}},
            'StreamFilename': {'Status': {}},
            'StreamTarget': {'Status': {}},
            'StreamTargetItemName': {'Parameters': ['Button'], 'Status': {}},
            'StreamTargetItemStatus': {'Parameters': ['Button'], 'Status': {}},
            'StreamTargetNavigation': {'Status': {}},
            'StreamTargetSearchSet': {'Status': {}},
        }

        self.SearchResults = []
        self.StartingEntry = 0
        self.NumberOfButton = 0
        self.ListNumber = {}
        self.Advance = True
        self.fileNameString = {'Include' : '', 'Exclude' : ''}
        self.dateTime = ''

    @property
    def NumberOfStreamTargetSearch(self):
        return self._NumberOfStreamTargetSearch

    @NumberOfStreamTargetSearch.setter
    def NumberOfStreamTargetSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfStreamTargetSearch = int(value)

    @property
    def ServerName(self):
        return self._ServerName

    @ServerName.setter
    def ServerName(self, value):
        self._ServerName = value

    @property
    def VHostName(self):
        return self._VHostName

    @VHostName.setter
    def VHostName(self, value):
        self._VHostName = value

    @property
    def ApplicationName(self):
        return self._ApplicationName

    @ApplicationName.setter
    def ApplicationName(self, value):
        self._ApplicationName = value

    def SetFilenameString(self, value, qualifier):

        DateTimeStates = ('Include', 'Exclude')
        if qualifier['Date & Time'] in DateTimeStates:
            self.dateTime = qualifier['Date & Time']
            self.fileNameString[qualifier['Date & Time']] = value
        else:
            self.Discard('Invalid Command')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Split': 'splitRecording',
            'Stop': 'stopRecording',
        }

        RecordingCmdString = ''
        data = ''
        final_filename = ''
        instance_name = qualifier['Instance']
        recorder_name = qualifier['Recorder Name']
        if value == 'Start':
            output_path = qualifier['Output Path']
            fileName = self.fileNameString[self.dateTime]
            if fileName and self.dateTime == 'Include':
                final_filename = ''.join([fileName, '_', time.strftime("%Y%m%d_%H%M%S")])
            elif fileName and self.dateTime == 'Exclude':
                final_filename = fileName
            else:
                final_filename = ''
            if instance_name and recorder_name:
                RecordingCmdString = 'v2/servers/{0}/vhosts/{1}/applications/{2}/instances/{3}/streamrecorders/{4}'.format(
                    self._ServerName.replace(' ', '%20'), self._VHostName.replace(' ', '%20'),
                    self._ApplicationName.replace(' ', '%20'), instance_name.replace(' ', '%20'),
                    recorder_name.replace(' ', '%20'))
                data = dumps({
                    "recorderName": recorder_name,
                          "currentSize": 0,
                          "startOnKeyFrame": True,
                          "outputPath": output_path,
                          "baseFile": final_filename,
                          "recordData": False,
                          "moveFirstVideoFrameToZero": False,
                          "segmentSize": 0,
                          "backBufferTime": 0,
                          "segmentationType": "",
                          "fileFormat": "",
                          "option": ""
                        })
                if data and RecordingCmdString:
                    self.__SetHelper('Recording', value, qualifier, RecordingCmdString, data.encode('iso-8859-1'), method='POST')
                else:
                    self.Discard('Invalid Command for SetRecording')
            else:
                self.Discard('Invalid Command for SetRecording')
        else:
            if value in ValueStateValues and instance_name and recorder_name:
                RecordingCmdString = 'v2/servers/{0}/vhosts/{1}/applications/{2}/instances/{3}/streamrecorders/{4}/actions/{5}'.format(
                    self._ServerName.replace(' ', '%20'), self._VHostName.replace(' ', '%20'),
                    self._ApplicationName.replace(' ', '%20'), instance_name.replace(' ', '%20'),
                    recorder_name.replace(' ', '%20'), ValueStateValues[value])
                if RecordingCmdString:
                    self.__SetHelper('Recording', value, qualifier, RecordingCmdString, data=None, method='PUT')
                else:
                    self.Discard('Invalid Command for SetRecording')
            else:
                self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        ValueStateValues = {
            'recording in progress': 'Recording in Progress',
            'waiting for stream': 'Waiting for Stream',
        }

        instance_name = qualifier['Instance']
        recorder_name = qualifier['Recorder Name']
        if instance_name and recorder_name:
            RecordingCmdString = 'v2/servers/{0}/vhosts/{1}/applications/{2}/instances/{3}/streamrecorders'.format(
                self._ServerName.replace(' ', '%20'), self._VHostName.replace(' ', '%20'),
                self._ApplicationName.replace(' ', '%20'), instance_name.replace(' ', '%20'))
            res = self.__UpdateHelper('Recording', value, qualifier, RecordingCmdString)
            if res:
                try:
                    if res["streamrecorder"]:
                        qualifier_list = []
                        for val in res["streamrecorder"]:
                            qualifier1 = {}
                            qualifier1['Instance'] = val["instanceName"]
                            qualifier1['Recorder Name'] = val["recorderName"]
                            qualifier_list.append(qualifier1)
                            value = ValueStateValues[val["recorderState"].lower()]
                            self.WriteStatus('Recording', value, qualifier1)
                        if qualifier not in qualifier_list:
                            self.WriteStatus('Recording', 'No Recorder Created', qualifier)
                    else:
                        self.WriteStatus('Recording', 'No Recorder Created', qualifier)
                except (KeyError, IndexError):
                    self.Error(['Recording Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecording')

    def UpdateServerName(self, value, qualifier):

        ServerNameCmdString = 'v2/servers/{0}/vhosts/{1}/applications/{2}/pushpublish/mapentries'.format(
            self._ServerName.replace(' ', '%20'), self._VHostName.replace(' ', '%20'),
            self._ApplicationName.replace(' ', '%20'))
        res = self.__UpdateHelper('ServerName', value, qualifier, ServerNameCmdString)
        if res:
            try:
                value = res['serverName']
                self.ServerName = value
                self.WriteStatus('ServerName', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Server Name: Invalid/unexpected response'])

            try:
                self.SearchResults = res['mapEntries']
                self.Advance = True
                self.SetStreamTargetNavigation(None, None)
            except (ValueError, IndexError):
                self.Error(['Stream Target Item Name: Invalid/unexpected response'])

    def SetStreamFile(self, value, qualifier):

        ValueStateValues = ('Connect', 'Disconnect')

        instance_name = qualifier['Instance']
        stream_filename = qualifier['Filename']
        if value in ValueStateValues and instance_name and stream_filename:
            common_url = 'v2/servers/{}/vhosts/{}/applications/{}/'.format(self._ServerName.replace(' ', '%20'),
                                                                           self._VHostName.replace(' ', '%20'),
                                                                           self._ApplicationName.replace(' ', '%20'))
            if value == 'Connect':
                end_url = 'streamfiles/{}/actions/connect?connectAppName={}&appInstance={}&mediaCasterType=rtp'.format(
                    stream_filename.replace(' ', '%20'), self._ApplicationName.replace(' ', '%20'),
                    instance_name.replace(' ', '%20')
                )
            else:
                end_url = 'instances/{}/incomingstreams/{}.stream/actions/disconnectStream'.format(
                    instance_name.replace(' ', '%20'), stream_filename.replace(' ', '%20')
                )
            StreamFileCmdString = common_url + end_url
            self.__SetHelper('StreamFile', value, qualifier, StreamFileCmdString, data=None, method='PUT')
        else:
            self.Discard('Invalid Command for SetStreamFile')

    def SetStreamTarget(self, value, qualifier):

        ValueStateValues = {
            'Enable': 1,
            'Disable': 0,
        }

        StreamTargetCmdString = ''
        data = ''
        if self.ListNumber:
            StreamTargetCmdString = 'v2/servers/{0}/vhosts/{1}/applications/{2}/pushpublish/mapentries/{3}'.format(
                self._ServerName.replace(' ', '%20'), self._VHostName.replace(' ', '%20'),
                self._ApplicationName.replace(' ', '%20'), self.ListNumber["entryName"].replace(' ', '%20'))
            data = dumps({
                "serverName": self.ServerName,
                "sourceStreamName": self.ListNumber["sourceStreamName"],
                "entryName": self.ListNumber["entryName"],
                "profile": self.ListNumber["profile"],
                "host": self.ListNumber["host"],
                "application": self.ListNumber["application"],
                "streamName": self.ListNumber["streamName"],
                "rtpWrap": self.ListNumber["rtpWrap"],
                "enabled": bool(ValueStateValues[value])
            })
            if data and StreamTargetCmdString:
                self.__SetHelper('StreamTarget', value, qualifier, StreamTargetCmdString, data.encode('iso-8859-1'), method='PUT')
            else:
                self.Discard('Invalid Command for SetStreamTarget')
        else:
            self.Discard('Invalid Command for SetStreamTarget')

    def SetStreamTargetNavigation(self, value, qualifier):

        ValueStateValues = {
            True: 'Enabled',
            False: 'Disabled',
        }

        if 'Page Up' == value:
            self.StartingEntry -= self.NumberOfButton
        elif 'Page Down' == value and self.Advance:
            self.StartingEntry += self.NumberOfButton

        if self.StartingEntry >= len(self.SearchResults):
            self.StartingEntry = len(self.SearchResults) - 1

        if self.StartingEntry < 0:
            self.StartingEntry = 0

        self.Advance = True

        Button = 1
        for a in self.SearchResults[self.StartingEntry:]:
            self.WriteStatus('StreamTargetItemName', a['entryName'], {'Button': Button})
            self.WriteStatus('StreamTargetItemStatus', ValueStateValues[a['enabled']], {'Button': Button})
            Button += 1
            if Button == self.NumberOfButton + 1:
                break

        for a in range(Button, self.NumberOfButton + 1):
            self.Advance = False
            self.WriteStatus('StreamTargetItemName', '<empty>', {'Button': a})
            self.WriteStatus('StreamTargetItemStatus', '<empty>', {'Button': a})

    def SetStreamTargetSearchSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 15,
        }

        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
                self.SearchResults and
                self.StartingEntry + value <= len(self.SearchResults)):
            self.ListNumber = self.SearchResults[self.StartingEntry + value - 1]
        else:
            self.Discard('Invalid Command for SetStreamTargetSearchSet')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode('iso-8859-1').replace('\\', '/'))

    def __SetHelper(self, command, value, qualifier, url, data, method):
        self.Debug = True

        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json; charset=utf-8'}
        url = ''.join([self.RootURL, url])

        my_request = urllib.request.Request(url, data, headers=headers, method=method)
        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json; charset=utf-8'}
        url = ''.join([self.RootURL, url])
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
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

        self.SearchResults = []
        self.StartingEntry = 0
        self.NumberOfButton = 0
        self.ListNumber = {}
        self.Advance = True
        self.fileNameString = {'Include' : '', 'Exclude' : ''}
        self.dateTime = ''

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