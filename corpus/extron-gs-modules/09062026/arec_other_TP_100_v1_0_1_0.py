from json import loads, dumps
import urllib.error
import urllib.request
import base64


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername='Username', devicePassword=None, Model=None):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self._id = base64.b64encode('{}:{}'.format(deviceUsername, devicePassword).encode()).decode()
        else:
            self._id = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Home': {'Status': {}},
            'HorizontalPosition': {'Status': {}},
            'MoveSpeed': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan', 'Tilt'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'TrackingMode': {'Status': {}},
            'VerticalPosition': {'Status': {}},
        }

    def SetHome(self, value, qualifier):

        resource = 'sdk10/home'

        data = {
            'id': self._id,
        }

        self.__SetHelper('Home', value, qualifier, resource, data)

    def SetHorizontalPosition(self, value, qualifier):

        resource = 'sdk10/pan_goto'

        data = {
            'id': self._id,
            'x': value
        }

        if -1750 <= value <= 1750:
            self.__SetHelper('HorizontalPosition', value, qualifier, resource, data)
        else:
            self.Discard('Invalid Command for SetHorizontalPosition')

    def UpdateHorizontalPosition(self, value, qualifier):

        resource = 'sdk10/pan'

        res = self.__UpdateHelper('HorizontalPosition', value, qualifier, resource)
        if res:
            try:
                self.WriteStatus('HorizontalPosition', int(res['x']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Horizontal Position: Invalid/unexpected response'])

    def SetMoveSpeed(self, value, qualifier):

        resource = 'sdk10/speed'

        data = {
            'id': self._id,
            'speed': value,
        }

        if 1 <= value <= 50:
            self.__SetHelper('MoveSpeed', value, qualifier, resource, data)
        else:
            self.Discard('Invalid Command for SetMoveSpeed')

    def UpdateMoveSpeed(self, value, qualifier):

        resource = 'sdk10/speed'

        res = self.__UpdateHelper('MoveSpeed', value, qualifier, resource)
        if res:
            try:
                self.WriteStatus('MoveSpeed', int(res['speed']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Move Speed: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        if value == 'Stop':
            self.__SetHelper('PanTilt', value, qualifier, 'sdk10/stop', {'id': self._id})

        else:

            States = {
                'Left': 0,
                'Right': 1,
                'Up': 1,
                'Down': 0,
                'No Change': 'No Change'
            }

            x = States[qualifier['Pan']]
            y = States[qualifier['Tilt']]

            if value == 'Step':
                if y == 'No Change':
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/pan_move', {'id': self._id, 'direction': x})
                elif x == 'No Change':
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/tilt_move', {'id': self._id, 'direction': y})
                else:
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/pantilt_move', {'id': self._id, 'x': x, 'y': y})

            elif value == 'Continuous':
                if y == 'No Change':
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/pan_move_start', {'id': self._id, 'direction': x})
                elif x == 'No Change':
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/tilt_move_start', {'id': self._id, 'direction': y})
                else:
                    self.__SetHelper('PanTilt', value, qualifier, 'sdk10/pantilt_move_start', {'id': self._id, 'x': x, 'y': y})

    def SetPresetRecall(self, value, qualifier):

        resource = 'sdk10/preset_goto'

        data = {
            'id': self._id,
            'idx': int(value),
        }

        if 0 <= int(value) <= 15:
            self.__SetHelper('PresetRecall', value, qualifier, resource, data)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetTrackingMode(self, value, qualifier):

        States = {
            'Disable': 0,
            'Auto': 1,
            'Horizontal Auto': 2,
            'Student': 3
        }

        resource = 'sdk10/track_method'

        data = {
            'id': self._id,
            'method': States[value],
        }

        self.__SetHelper('TrackingMode', value, qualifier, resource, data)

    def UpdateTrackingMode(self, value, qualifier):

        States = {
            0: 'Disable',
            1: 'Auto',
            2: 'Horizontal Auto',
            3: 'Student'
        }

        resource = 'sdk10/track_method'

        res = self.__UpdateHelper('TrackingMode', value, qualifier, resource)
        if res:
            try:
                self.WriteStatus('TrackingMode', States[res['method']], qualifier)
            except (KeyError, IndexError):
                self.Error(['Tracking Mode: Invalid/unexpected response'])

    def SetVerticalPosition(self, value, qualifier):

        resource = 'sdk10/tilt_goto'

        data = {
            'id': self._id,
            'y': value
        }

        if -250 <= value <= 350:
            self.__SetHelper('VerticalPosition', value, qualifier, resource, data)
        else:
            self.Discard('Invalid Command for SetVerticalPosition')

    def UpdateVerticalPosition(self, value, qualifier):

        resource = 'sdk10/tilt'

        res = self.__UpdateHelper('VerticalPosition', value, qualifier, resource)
        if res:
            try:
                self.WriteStatus('VerticalPosition', int(res['x']), qualifier)
            except (ValueError, IndexError):
                self.Error(['Vertical Position: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        RESPONSE_CODE = {
            0: 'General Error',
            1: 'Authorization Error',
            2: 'Incorrect Format',
            3: 'Incorrect parameter number or type',
            4: 'Incorrect value',
        }

        try:
            res = loads(response.read().decode())
            if 'error' in res:
                err = RESPONSE_CODE[res['error']]
                self.Error(['Command {}, Error {}'.format(sourceCmdName, err)])
                return ''
            else:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True
        
        url = '{}{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json', 'Content-Length': len(data)}
        data = dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        
        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        url = '{}{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            res = self.Opener.open(my_request, timeout=10)
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
