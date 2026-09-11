import base64
import re
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.connectionCounter = 15

        self.IPAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.auth_handler = urllib.request.HTTPBasicAuthHandler()
        self.Opener = urllib.request.build_opener(self.auth_handler)

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ControlMode': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'Rate': {'Parameters': ['Speed'], 'Status': {}},
            'RateStatus': {'Status': {}},
            'RepeatMode': {'Status': {}},
            'SessionID': {'Status': {}},
            'ShuffleMode': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.Sessionid = None
        self.UpdateRegEx = re.compile(r'.*FS_OK.*<value>.*?>(\d+)<.*</value>.*?')
        self.SessionIDRegEx = re.compile(r'.*FS_OK.*<sessionId>(\d+)</sessionId>.*?')


    def UpdateSessionID(self, value, qualifier):

        SessionIDCmdString = '/fsapi/CREATE_SESSION?pin={0}'.format(self.devicePassword)
        res = self.__UpdateHelper('SessionID', value, qualifier, url=SessionIDCmdString)
        if res:
            try:
                temp = self.SessionIDRegEx.findall(res.decode())
                self.Sessionid = temp[0]
                self.WriteStatus('SessionID', self.Sessionid, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '/fsapi/SET/netRemote.sys.audio.mute?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '/fsapi/GET/netRemote.sys.audio.mute?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetControlMode(self, value, qualifier):

        ValueStateValues = {
            'Play': '1',
            'Pause': '2',
            'Next': '3',
            'Previous': '4'
        }

        ControlModeCmdString = '/fsapi/SET/netRemote.play.control?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('ControlMode', value, qualifier, url=ControlModeCmdString)

    def UpdateControlMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Play',
            '2': 'Pause',
            '3': 'Next',
            '4': 'Previous'
        }

        ControlModeCmdString = '/fsapi/GET/netRemote.play.control?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('ControlMode', value, qualifier, url=ControlModeCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('ControlMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Ethernet Radio': '0',
            'Music Player': '1',
            'FM Radio': '2'
        }

        InputCmdString = '/fsapi/SET/netRemote.sys.mode?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('Input', value, qualifier, url=InputCmdString)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Ethernet Radio',
            '1': 'Music Player',
            '2': 'FM Radio'
        }

        InputCmdString = '/fsapi/GET/netRemote.sys.mode?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('Input', value, qualifier, url=InputCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        PowerCmdString = '/fsapi/SET/netRemote.sys.power?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('Power', value, qualifier, url=PowerCmdString)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        if self.Sessionid == '':
            self.UpdateSessionID(None, None)
        PowerCmdString = '/fsapi/GET/netRemote.sys.power?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        PresetCmdString = '/fsapi/SET/netRemote.sys.audio.eqpreset?value={0}&pin={1}&sid={2}'.format(value, self.devicePassword, self.Sessionid)
        self.__SetHelper('Preset', value, qualifier, url=PresetCmdString)

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '/fsapi/GET/netRemote.sys.audio.eqpreset?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('Preset', value, qualifier, url=PresetCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = temp[0]
                self.WriteStatus('Preset', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetRate(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 126
        }

        speed = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max'] and value in ['Play', 'Pause', 'Rewind', 'Fast Forward']:
            if value == 'Play':
                RateCmdString = '/fsapi/SET/netRemote.play.rate?value=1&pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
            elif value == 'Pause':
                RateCmdString = '/fsapi/SET/netRemote.play.rate?value=0&pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
            elif value == 'Rewind':
                RateCmdString = '/fsapi/SET/netRemote.play.rate?value={0}&pin={1}&sid={2}'.format(-speed, self.devicePassword, self.Sessionid)
            else:
                RateCmdString = '/fsapi/SET/netRemote.play.rate?value={0}&pin={1}&sid={2}'.format(speed + 1, self.devicePassword, self.Sessionid)
            self.__SetHelper('Rate', value, qualifier, url=RateCmdString)
        else:
            self.Discard('Invalid Command for SetRate')

    def UpdateRateStatus(self, value, qualifier):

        RateStatusCmdString = '/fsapi/GET/netRemote.play.rate?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('RateStatus', value, qualifier, url=RateStatusCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = temp[0]
                if -127 <= int(value) <= -1:
                    self.WriteStatus('RateStatus', 'Rewind', qualifier)
                elif 2 <= int(value) <= 127:
                    self.WriteStatus('RateStatus', 'Fast Forward', qualifier)
                elif int(value) == 0:
                    self.WriteStatus('RateStatus', 'Pause', qualifier)
                elif int(value) == 1:
                    self.WriteStatus('RateStatus', 'Play', qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetRepeatMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        RepeatModeCmdString = '/fsapi/SET/netRemote.play.repeat?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('RepeatMode', value, qualifier, url=RepeatModeCmdString)

    def UpdateRepeatMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        RepeatModeCmdString = '/fsapi/GET/netRemote.play.repeat?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('RepeatMode', value, qualifier, url=RepeatModeCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('RepeatMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetShuffleMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShuffleModeCmdString = '/fsapi/SET/netRemote.play.shuffle?value={0}&pin={1}&sid={2}'.format(ValueStateValues[value], self.devicePassword, self.Sessionid)
        self.__SetHelper('ShuffleMode', value, qualifier, url=ShuffleModeCmdString)

    def UpdateShuffleMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ShuffleModeCmdString = '/fsapi/GET/netRemote.play.shuffle?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('ShuffleMode', value, qualifier, url=ShuffleModeCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = ValueStateValues[temp[0]]
                self.WriteStatus('ShuffleMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 32
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '/fsapi/SET/netRemote.sys.audio.volume?value={0}&pin={1}&sid={2}'.format(value, self.devicePassword, self.Sessionid)
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '/fsapi/GET/netRemote.sys.audio.volume?pin={0}&sid={1}'.format(self.devicePassword, self.Sessionid)
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                temp = self.UpdateRegEx.findall(res.decode())
                value = int(temp[0])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, res):

        return res.read()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        my_request = urllib.request.Request('{0}{1}'.format(self.RootURL.rstrip('/'), url), data=data, headers={'Content-Type': 'text/xml'})

        try:
            res = self.Opener.open(my_request)
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        my_request = urllib.request.Request('{0}{1}'.format(self.RootURL.rstrip('/'), url), data=data, headers={'Content-Type': 'text/xml'})

        try:
            res = self.Opener.open(my_request)
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
        self.Sessionid = None

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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