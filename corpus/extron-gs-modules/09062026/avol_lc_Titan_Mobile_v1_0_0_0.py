from re import compile, search
import urllib.error
import urllib.request


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.FadeTime = ''
        self.FirePlaybackLevel = ''
        self.FireUserNumber = ''
        self.KillUserNumber = ''

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FadeTime': {'Status': {}},
            'FirePlaybackAtLevel': {'Parameters': ['Always Refire'], 'Status': {}},
            'FirePlaybackLevel': {'Status': {}},
            'FireUserNumber': {'Status': {}},
            'KillPlayback': {'Status': {}},
            'KillUserNumber': {'Status': {}},
            'ReleaseAllPlaybacks': {'Parameters': ['Use Master Release Time'], 'Status': {}},
            'SoftwareVersion': {'Status': {}},
        }

        self.MatchSoftwareVersion = compile('"(.+?)"')
        self.MatchNumber = compile(r'^(?:[1-9]\d{0,8})$')
        self.MatchTime = compile(r'^(?:300|[12]\d{2}|[1-9]?\d)$')
        self.MatchLevel = compile(r'^(?:100|[1-9]?\d)$')


    def SetFadeTime(self, value, qualifier):
        self.FadeTime = value


    def SetFirePlaybackAtLevel(self, value, qualifier):

        AlwaysRefireStates = ('True', 'False')

        cmd_str = '/titan/script/2/Playbacks/FirePlaybackAtLevel?handle_userNumber={}&level_level={}&alwaysRefire={}'
        always_refire = qualifier['Always Refire']
        fire_user_number = self.FireUserNumber
        level = self.FirePlaybackLevel
        if (always_refire in AlwaysRefireStates and fire_user_number and self.MatchNumber.match(fire_user_number) and
                level and self.MatchLevel.match(level)):
            FirePlaybackAtLevelCmdString = cmd_str.format(fire_user_number, level, always_refire.lower())
            self.__SetHelper('FirePlaybackAtLevel', value, qualifier, url=FirePlaybackAtLevelCmdString)
        else:
            self.Discard('Invalid Command for SetFirePlaybackAtLevel')


    def SetFirePlaybackLevel(self, value, qualifier):
        self.FirePlaybackLevel = value


    def SetFireUserNumber(self, value, qualifier):
        self.FireUserNumber = value


    def SetKillPlayback(self, value, qualifier):

        cmd_str = '/titan/script/2/Playbacks/KillPlayback?handle_userNumber={}'
        kill_user_number = self.KillUserNumber
        if kill_user_number and self.MatchNumber.match(kill_user_number):
            KillPlaybackCmdString = cmd_str.format(kill_user_number)
            self.__SetHelper('KillPlayback', value, qualifier, url=KillPlaybackCmdString)
        else:
            self.Discard('Invalid Command for SetKillPlayback')


    def SetKillUserNumber(self, value, qualifier):
        self.KillUserNumber = value


    def SetReleaseAllPlaybacks(self, value, qualifier):

        UseMasterReleaseTimeStates = ('True', 'False')

        cmd_str = '/titan/script/2/Playbacks/ReleaseAllPlaybacks?fadeTime={}&useMasterReleaseTime={}'
        fade_time = self.FadeTime
        use_master_release_time = qualifier['Use Master Release Time']
        if fade_time and self.MatchTime.match(fade_time) and use_master_release_time in UseMasterReleaseTimeStates:
            ReleaseAllPlaybacksCmdString = cmd_str.format(fade_time, use_master_release_time.lower())
            self.__SetHelper('ReleaseAllPlaybacks', value, qualifier, url=ReleaseAllPlaybacksCmdString)
        else:
            self.Discard('Invalid Command for SetReleaseAllPlaybacks')

    def UpdateSoftwareVersion(self, value, qualifier):

        SoftwareVersionCmdString = '/titan/get/2/System/SoftwareVersion'
        res = self.__UpdateHelper('SoftwareVersion', value, qualifier, url=SoftwareVersionCmdString)
        if res:
            match_res = self.MatchSoftwareVersion.search(res)
            if match_res:
                self.WriteStatus('SoftwareVersion', match_res.group(1), qualifier)
            else:
                self.Error(['Software Version: Invalid/unexpected response'])


    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode('iso-8859-1')
        return res


    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}/{}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/plain'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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


    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}/{}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/plain'}
        myRequest = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(myRequest, timeout=10)
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


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.FadeTime = ''
        self.FirePlaybackLevel = ''
        self.FireUserNumber = ''
        self.KillUserNumber = ''


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
