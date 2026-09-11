from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import urllib.error
import urllib.request
import json
from extronlib import Version

class DeviceClass:
    def __init__(self, ipAddress, port, devicePassword, SSLVerifyMode='On'):
        
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AIMode': {'Parameters':['Camera ID'], 'Status': {}},
            'DivisibleMeetingRoom': {'Parameters':['Requestor ID'], 'Status': {}},
            'FirmwareVersion': {'Parameters':['Camera ID'], 'Status': {}},
            'LayoutPosition': {'Parameters':['Camera ID'], 'Status': {}},
            'LayoutSwitch': { 'Status': {}},
            'LayoutType': { 'Status': {}},
            'PanTilt': {'Parameters':['Camera ID'], 'Status': {}},
            'Preset': {'Parameters':['Camera ID','Action'], 'Status': {}},
            'Zoom': {'Parameters':['Camera ID'], 'Status': {}},
        }

        self.Token = None

    def TokenRequest(self, value, qualifier):

        self._TokenRequestHandler()

    def _TokenRequestHandler(self):

        path = 'centralcontrol/authentication'
        body = {"password": self.devicePassword}
        res = self.__SetHelper('TokenRequest', None, None, url=path, data=body)
        if res:
            try:
                self.Token = res["data"]["token"]
            except KeyError:
                self.Error(['Failed to obtain token'])

    def SetAIMode(self, value, qualifier):

        ValueStateValues = {
            'PTZ': 'ptz',
            'Auto Frame': 'auto-frame',
            'View Cropping': 'view-cropping',
            'Multi-screen': 'multi-screen',
            'Smart Gallery': 'smart-gallery',
            'PIP': 'pip',
            'Multi-PIP': 'multi-pip',
            'Speaker Tracking': 'speaker-tracking',
            'Presenter Tracking' : 'presenter-tracking'
            }

        if qualifier['Camera ID'] and value in ValueStateValues:
            path = 'centralcontrol/camera/ai-mode'
            body = {"type": ValueStateValues[value], "sn": qualifier['Camera ID']}
            self.__SetHelper('AIMode', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetAIMode')

    def SetDivisibleMeetingRoom(self, value, qualifier):

        ValueStateValues = {
            'Disable': 0,
            'Standalone Mode': 1,
            'Merged Room': 2,
            'Master Room': 3
            }

        if value in ValueStateValues:
            path = 'centralcontrol/splitroom/status'
            body = {"value": ValueStateValues[value]}
            if qualifier['Requestor ID']:
                body["sn"] = qualifier['Requestor ID']
            self.__SetHelper('DivisibleMeetingRoom', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetDivisibleMeetingRoom')

    def UpdateFirmwareVersion(self, value, qualifier):

        if qualifier['Camera ID']:
            path = 'centralcontrol/camera/detail'
            body = {"sn": qualifier['Camera ID']}
            res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=path, data=body)
            if res:
                try:
                    value = res["data"]["firmware"]
                    self.WriteStatus('FirmwareVersion', value, qualifier)
                except KeyError:
                    self.Error(['Firmware Version: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFirmwareVersion')

    def SetLayoutPosition(self, value, qualifier):

        if qualifier['Camera ID'] and 0 <= int(value) <= 8:
            path = 'centralcontrol/camera-layout/position'
            body = {"sn": qualifier['Camera ID'], "position": int(value)}
            self.__SetHelper('LayoutPosition', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetLayoutPosition')

    def SetLayoutSwitch(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
            }

        if value in ValueStateValues:
            path = 'centralcontrol/camera-layout/switch'
            body = {"status": ValueStateValues[value]}
            self.__SetHelper('LayoutSwitch', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetLayoutSwitch')

    def SetLayoutType(self, value, qualifier):

        ValueStateValues = {
            'One-Sided Fullscreen': 'fullscreen',
            'Two-Split Screen': 'div2',
            'Three-Split Screen': 'div3',
            'Four-Split Screen': 'div4',
            'Five-Split Screen': 'div5',
            'Six-Split Screen': 'div6',
            'Seven-Split Screen': 'div7',
            'Eight-Split Screen': 'div8',
            'Nine-Split Screen': 'div9',
            '1x1': '1x1',
            '1x2': '1x2',
            '1x3': '1x3',
            '1x4': '1x4',
            '1x5': '1x5',
            '1x6': '1x6',
            '1x7': '1x7',
            '1x8': '1x8'
            }

        if value in ValueStateValues:
            path = 'centralcontrol/camera-layout/type'
            body = {"type": ValueStateValues[value]}
            self.__SetHelper('LayoutType', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetLayoutType')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Stop': 'stop'
            }

        if qualifier['Camera ID'] and value in ValueStateValues:
            path = 'centralcontrol/camera/move'
            body = {"direction": ValueStateValues[value], "sn": qualifier['Camera ID']}
            self.__SetHelper('PanTilt', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': '',
            'Recall': '/recall'
            }

        if qualifier['Camera ID'] and qualifier['Action'] in ActionStates and 0 <= int(value) <= 98:
            path = 'centralcontrol/camera/preset{}'.format(ActionStates[qualifier['Action']])
            body = {"id": int(value), "sn": qualifier['Camera ID']}
            self.__SetHelper('Preset', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'in',
            'Wide': 'out',
            'Stop': 'stop'
            }

        if qualifier['Camera ID'] and value in ValueStateValues:
            path = 'centralcontrol/camera/zoom'
            body = {"direction": ValueStateValues[value], "sn": qualifier['Camera ID']}
            self.__SetHelper('Zoom', value, qualifier, url=path, data=body)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            res = json.loads(response.read().decode())
            if res["status"] != 200:
                self.Error(['{}: Invalid/unexpected status code {}'.format(sourceCmdName, res["status"])])
                res = ''
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        if self.Token or command == 'TokenRequest':
            url = '{0}{1}'.format(self.RootURL, url)
            if data is not None:
                data = json.dumps(data).encode()
            if command == 'TokenRequest':
                headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            else:
                headers = {'Authorization': 'Bearer {}'.format(self.Token), 'Content-Type': 'application/json', 'Accept': 'application/json'}

            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
            except urllib.error.URLError as err: # received if can't reach the server (times out)
                self.Error(['{0} {1}'.format(command, err.reason)])
                res = ''
            except Exception as err: # includes HTTP status code 100 and any invalid status code
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.Token:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            url = '{0}{1}'.format(self.RootURL, url)
            if data is not None:
                data = json.dumps(data).encode()
            headers = {'Authorization': 'Bearer {}'.format(self.Token), 'Content-Type': 'application/json', 'Accept': 'application/json'}

            my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

            try:
                res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
            except urllib.error.URLError as err: # received if can't reach the server (times out)
                self.Error(['{0} {1}'.format(command, err.reason)])
                res = ''
            except Exception as err: # includes HTTP status code 100 and any invalid status code
                res = ''
            else:
                if res.status not in (200, 202):
                    self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                    res = ''
                else:
                    res = self.__CheckResponseForErrors(command, res)
            return res
        else:
            self.Discard('Inappropriate Command ' + command)
            self.TokenRequest(None, None)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Token = None

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
    def __init__(self, ipAddress, port, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, devicePassword, SSLVerifyMode)
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