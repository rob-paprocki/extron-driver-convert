from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import urllib.error
import urllib.request


class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocusOrIris': {'Status': {}},
            'CameraSwitching': {'Status': {}},
            'CameraSwitchingwithGroupPort': {'Parameters': ['Port'], 'Status': {}},
            'ExtenderAFControl': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Installation': {'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetDelete': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'ResetPanTiltPosition': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

    def SetAutoFocusOrIris(self, value, qualifier):

        FocusValues = {
            'On': '1',
            'Off': '0'
        }

        if value in FocusValues:
            AutoFocusOrIrisCmdString = 'OAF:{0}\r'.format(FocusValues[value])
            self.__SetHelper('AutoFocusOrIris', AutoFocusOrIrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocusOrIris')

    def SetCameraSwitching(self, value, qualifier):

        if 1 <= int(value) <= 100:
            CameraSwitchingCmdString = 'XCN:01:{0}\r'.format(value)
            self.__SetHelper('CameraSwitching', CameraSwitchingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraSwitching')

    def SetCameraSwitchingwithGroupPort(self, value, qualifier):

        port = int(qualifier['Port'])
        if 1 <= port <= 10 and 1 <= int(value) <= 10:
            CameraSwitchingwithGroupPortCmdString = 'XCN:02:{0}:{1}\r'.format(value, port)
            self.__SetHelper('CameraSwitchingwithGroupPort', CameraSwitchingwithGroupPortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraSwitchingwithGroupPort')

    def SetExtenderAFControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            ExtenderAFControlCmdString = '#D1{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExtenderAFControl', ExtenderAFControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExtenderAFControl')

    def SetFocus(self, value, qualifier):

        Speed = qualifier['Speed']
        if 1 <= Speed <= 49:
            if value == 'Near':
                FocusCmdString = '#F{0}\r'.format(str(50 - Speed).zfill(2))
            elif value == 'Far':
                FocusCmdString = '#F{0}\r'.format(str(50 + Speed).zfill(2))
            else:
                FocusCmdString = '#F50\r'

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetInstallation(self, value, qualifier):

        ValueStateValues = {
            'Desktop': '0',
            'Hanging': '1'
        }

        if value in ValueStateValues:
            InstallationCmdString = '#INS{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Installation', InstallationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInstallation')

    def SetPanTilt(self, value, qualifier):

        Speed = qualifier['Speed']
        if 1 <= Speed <= 49:
            if value == 'Left':
                PanTiltCmdString = '#P{0}\r'.format(str(50 - Speed).zfill(2))
            elif value == 'Right':
                PanTiltCmdString = '#P{0}\r'.format(str(50 + Speed).zfill(2))
            elif value == 'Up':
                PanTiltCmdString = '#T{0}\r'.format(str(50 + Speed).zfill(2))
            elif value == 'Down':
                PanTiltCmdString = '#T{0}\r'.format(str(50 - Speed).zfill(2))
            else:
                PanTiltCmdString = '#PTS5050\r'

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerCmdString = '#O{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPresetDelete(self, value, qualifier):

        if 1 <= int(value) <= 100:
            preset = int(value) - 1
            PresetDeleteCmdString = '#C{0}\r'.format(str(preset).zfill(2))
            self.__SetHelper('PresetDelete', PresetDeleteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetDelete')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            preset = int(value) - 1
            PresetRecallCmdString = '#R{0}\r'.format(str(preset).zfill(2))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            preset = int(value) - 1
            PresetSaveCmdString = '#M{0}\r'.format(str(preset).zfill(2))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = '#APC80008000\r'
        self.__SetHelper('ResetPanTiltPosition', ResetPanTiltPositionCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        Speed = qualifier['Speed']
        if 1 <= Speed <= 49:
            if value == 'Wide':
                ZoomCmdString = '#Z{0}\r'.format(str(50 - Speed).zfill(2))
            elif value == 'Tele':
                ZoomCmdString = '#Z{0}\r'.format(str(50 + Speed).zfill(2))
            else:
                ZoomCmdString = '#Z50\r'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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


class DeviceHTTPClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'AW-RP120': self.pana_20_1707_RP120,
            'AW-RP120G': self.pana_20_1707_RP120,
            'AW-RP120GJ': self.pana_20_1707_RP120,
            'AW-RP150GJ': self.pana_20_1707_RP150,
            'AW-RP60GJ': self.pana_20_1707_RP60,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CameraSwitching': {'Status': {}},
            'CameraSwitchingwithGroupPort': {'Parameters': ['Port'], 'Status': {}},
            'PresetRecall': {'Status': {}},
        }

        self.Cam = re.compile('XQC:01:([0-9]{1,3})')
        self.Port = re.compile('XQC:02:([0-9]{1,2}):([0-9]{1,2})')

    def SetCameraSwitching(self, value, qualifier):

        if 1 <= int(value) <= self.cameraSwitchingSize:
            data = 'cmd=XCN:01:{0}&res=1'.format(value)
            self.__SetHelper('CameraSwitching', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetCameraSwitching')

    def UpdateCameraSwitching(self, value, qualifier):

        data = 'cmd=XQC:01&res=1'
        res = self.__UpdateHelper('CameraSwitching', value, qualifier, url='', data=data)
        if res:
            try:
                cam = self.Cam.search(res)
                if cam is not None:
                    value = cam.group(1)
                    self.WriteStatus('CameraSwitching', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Camera Switching: Invalid/unexpected response'])

    def SetCameraSwitchingwithGroupPort(self, value, qualifier):

        port = int(qualifier['Port'])
        if 1 <= port <= self.portSize and 1 <= int(value) <= self.groupSize:
            data = 'cmd=XCN:02:{0}:{1}&res=1'.format(value, port)
            self.__SetHelper('CameraSwitchingwithGroupPort', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetCameraSwitchingwithGroupPort')

    def UpdateCameraSwitchingwithGroupPort(self, value, qualifier):

        data = 'cmd=XQC:02&res=1'
        res = self.__UpdateHelper('CameraSwitchingwithGroupPort', value, qualifier, url='', data=data)
        if res:
            try:
                temp = self.Port.search(res)
                if temp is not None:
                    value = temp.group(1)
                    qualifier['Port'] = temp.group(2)
                    self.WriteStatus('CameraSwitchingwithGroupPort', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Camera Switching with Group Port: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 100:
            data = 'cmd=XPM:01:{0}&res=1'.format(preset)
            self.__SetHelper('Preset', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def __CheckResponseForErrors(self, sourceCmdName, res):

        return res.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        headers = {'Content-Type': 'text/html'}
        my_request = urllib.request.Request(url, headers=headers)

        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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

        url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        headers = {'Content-Type': 'text/html'}
        my_request = urllib.request.Request(url, headers=headers)

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

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_20_1707_RP120(self):
        self.cameraSwitchingSize = 100
        self.groupSize = 10
        self.portSize = 10

    def pana_20_1707_RP150(self):
        self.cameraSwitchingSize = 200
        self.groupSize = 20
        self.portSize = 10

    def pana_20_1707_RP60(self):
        self.cameraSwitchingSize = 200
        self.groupSize = 40
        self.portSize = 5

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port)
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
