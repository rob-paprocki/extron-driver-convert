# Copyright 2026, Extron. All rights reserved.

from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import json
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

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

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self._emulated_status = {}
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiviewCommand': {'Status': {}},
            'MultiviewString': {'Status': {}},
            'Power': {'Status': {}},
            'RefreshToken': {'Status': {}},
            'Volume': {'Status': {}},
            }

        pass
        self.AccessToken = None
        self.authenticated = False

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {'4:3': '4:3', '16:9': '16:9'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'pictureSizeControl', 'params': {'AccessToken': self.AccessToken, 'pictureSize': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('AspectRatio', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'pictureSizeControl', 'params': {'AccessToken': self.AccessToken}, 'id': 1}
        res = self.__UpdateHelper('AspectRatio', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {'4:3': '4:3', '16:9': '16:9'}
                value = ValueStateValues[str(res['result']['pictureSize'])]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {'On': 'muteOn', 'Off': 'muteOff'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'muteControl', 'params': {'AccessToken': self.AccessToken, 'mute': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('AudioMute', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'muteControl', 'params': {'AccessToken': self.AccessToken}, 'id': 1}
        res = self.__UpdateHelper('AudioMute', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {'muteOn': 'On', 'muteOff': 'Off'}
                value = ValueStateValues[str(res['result']['mute'])]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):
        ValueStateValues = {'Up': 'channelUp', 'Down': 'channelDn'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'channelUpDnControl', 'params': {'AccessToken': self.AccessToken, 'control': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('ChannelStep', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetInput(self, value, qualifier):
        ValueStateValues = {'TV': 'TV', 'HDMI 1': 'HDMI1', 'HDMI 2': 'HDMI2', 'HDMI 3': 'HDMI3', 'HDMI 4': 'HDMI4'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'inputSourceControl', 'params': {'AccessToken': self.AccessToken, 'inputSource': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('Input', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'inputSourceControl', 'params': {'AccessToken': self.AccessToken}, 'id': 1}
        res = self.__UpdateHelper('Input', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {'TV': 'TV', 'HDMI1': 'HDMI 1', 'HDMI2': 'HDMI 2', 'HDMI3': 'HDMI 3', 'HDMI4': 'HDMI 4'}
                value = ValueStateValues[str(res['result']['inputSource'])]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):
        ValueStateValues = {'0': 'number0', '1': 'number1', '2': 'number2', '3': 'number3', '4': 'number4', '5': 'number5', '6': 'number6', '7': 'number7', '8': 'number8', '9': 'number9'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'remoteKeyControl', 'params': {'AccessToken': self.AccessToken, 'remoteKey': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('Keypad', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {'Up': 'cursorUp', 'Down': 'cursorDn', 'Left': 'cursorLeft', 'Right': 'cursorRight', 'Menu': 'menu', 'Enter': 'enter', 'Return': 'return', 'Exit': 'exit', 'Home': 'firstScreen'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'remoteKeyControl', 'params': {'AccessToken': self.AccessToken, 'remoteKey': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('MenuNavigation', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMultiviewCommand(self, value, qualifier):
        mode = self.ReadMultiviewString(qualifier, 'Emulated')
        data = {'jsonrpc': '2.0', 'method': 'multiviewControl', 'params': {'AccessToken': self.AccessToken, 'multiviewMode': mode}, 'id': 1}
        self.__SetHelper('MultiviewCommand', value, qualifier, data)

    def SetMultiviewString(self, value, qualifier):
        pass

    def SetPower(self, value, qualifier):
        ValueStateValues = {'On': 'powerOn', 'Off': 'powerOff'}
        if value in ValueStateValues and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'powerControl', 'params': {'AccessToken': self.AccessToken, 'power': ValueStateValues[value]}, 'id': 1}
            self.__SetHelper('Power', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'powerControl', 'params': {'AccessToken': self.AccessToken}, 'id': 1}
        res = self.__UpdateHelper('Power', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {'powerOn': 'On', 'powerOff': 'Off'}
                value = ValueStateValues[str(res['result']['power'])]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRefreshToken(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'createAccessToken', 'id': 1}
        res = self.__SetHelper('RefreshToken', value, qualifier, data)
        if res:
            try:
                self.AccessToken = res['result']['AccessToken']
                self.authenticated = True
            except KeyError:
                self.Error(['Refresh Token: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):
        if 0 <= value <= 100 and self.AccessToken:
            data = {'jsonrpc': '2.0', 'method': 'directVolumeControl', 'params': {'AccessToken': self.AccessToken, 'volume': value}, 'id': 1}
            self.__SetHelper('Volume', value, qualifier, data)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        data = {'jsonrpc': '2.0', 'method': 'directVolumeControl', 'params': {'AccessToken': self.AccessToken}, 'id': 1}
        res = self.__UpdateHelper('Volume', value, qualifier, data)
        if res:
            try:
                value = int(res['result']['volume'])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def WriteMultiviewString(self, value, qualifier, context):
        self._emulated_status['MultiviewString'] = value

    def ReadMultiviewString(self, qualifier, context):
        return self._emulated_status.get('MultiviewString')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        try:
            res = json.loads(response.read().decode())
            if 'error' in res:
                self.Error(['{0}: {1}'.format(sourceCmdName, res['error']['message'])])
                return ''
            return res
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])

    def __SetHelper(self, command, value, qualifier, data=None):
        if command == 'RefreshToken':
            responseTimeout = 30
        else:
            responseTimeout = 1
        url = self.RootURL.replace('http', 'https')
        data = json.dumps(data).encode()
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=responseTimeout)
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

    def __UpdateHelper(self, command, value, qualifier, data=None):
        url = self.RootURL.replace('http', 'https')
        data = json.dumps(data).encode()
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.authenticated:
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
            try:
                res = self.Opener.open(my_request, timeout=1)
            except urllib.error.HTTPError as err:
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
            except urllib.error.URLError as err:
                self.Error(['{0} {1}'.format(command, err.reason)])
                if command == 'Power':
                    pass
                res = ''
            except Exception as err:
                if command == 'Power':
                    pass
                res = ''
            else:
                if res.status not in (200, 202):
                    self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                    res = ''
                else:
                    res = self.__CheckResponseForErrors(command, res)
            return res
        else:
            self.Discard('Inappropriate Command')

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='Off'):
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.DefaultPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])
