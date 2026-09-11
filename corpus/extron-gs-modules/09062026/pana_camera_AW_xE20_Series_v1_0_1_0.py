from extronlib.system import Wait, ProgramLog
import re
import base64
import base64
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            authHandler = '{0}:{1}'.format(deviceUsername, devicePassword).encode()
            self.authentication = base64.b64encode(authHandler).decode("ascii")
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
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'PresetRecallStatus': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'ResetZoom': { 'Status': {}},
            'Tally': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }
        
        self.ColorBarRegex           = re.compile('OBR:([01])')
        self.DetailRegex             = re.compile('ODT:([012])')
        self.FocusModeRegex          = re.compile('d1([01])')
        self.PowerRegex              = re.compile('p([01])')
        self.PresetRecallStatusRegex = re.compile('s(\d{2})')
        self.TallyRegex              = re.compile('tAE([01])')
        self.ErrorRegex              = re.compile('ER([123])', re.I)

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=DCB:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        data = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.ColorBarRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('ColorBar', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Color Bar: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On (1)': '1',
            'On (2)': '2',
            'Off':    '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=ODT:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Detail', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        data = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On (1)',
                    '2': 'On (2)',
                    '0': 'Off'
                    }

                valueMatch = self.DetailRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Detail: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = ('Far', 'Near', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Far':
                focus_spd = 50 + qualifier['Speed']
            elif value == 'Near':
                focus_spd = 50 - qualifier['Speed']
            else:
                focus_spd = 50
                
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23F{:02d}&res=1'.format(focus_spd)
            self.__SetHelper('Focus', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Manual': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23D1{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('FocusMode', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('FocusMode', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'Auto',
                    '0': 'Manual'
                    }

                valueMatch = self.FocusModeRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            if value == 'Left':
                data = 'cmd=%23P{:02d}&res=1'.format(50 - qualifier['Speed'])
            elif value == 'Right':
                data = 'cmd=%23P{:02d}&res=1'.format(50 + qualifier['Speed'])
            elif value == 'Up':
                data = 'cmd=%23T{:02d}&res=1'.format(50 + qualifier['Speed'])
            elif value == 'Down':
                data = 'cmd=%23T{:02d}&res=1'.format(50 - qualifier['Speed'])
            else:
                data = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23O{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save':   'M',
            'Recall': 'R',
            'Delete': 'C'
            }

        if qualifier['Type'] in TypeStates and 1 <= int(value) <= 100:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23{}{:02d}&res=1'.format(TypeStates[qualifier['Type']], int(value) - 1)
            self.__SetHelper('Preset', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23S&res=1'
        res = self.__UpdateHelper('PresetRecallStatus', value, qualifier, url=url, data=data)
        if res:
            try:
                valueMatch = self.PresetRecallStatusRegex.match(res)
                value = int(valueMatch.group(1)) + 1
                self.WriteStatus('PresetRecallStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Preset Recall Status: Invalid/unexpected response'])

    def SetResetPanTiltPosition(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url=url, data=data)

    def SetResetZoom(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23AXZ555&res=1'
        self.__SetHelper('ResetZoom', value, qualifier, url=url, data=data)

    def SetTally(self, value, qualifier):

        ValueStateValues = { 
            'Enable':  '1',
            'Disable': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23TAE{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Tally', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'Enable',
                    '0': 'Disable'
                    }

                valueMatch = self.TallyRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Tally', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Tally: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Tele':
                zoom_spd = 50 + qualifier['Speed']
            elif value == 'Wide':
                zoom_spd = 50 - qualifier['Speed']
            else:
                zoom_spd = 50
                
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23Z{:02d}&res=1'.format(zoom_spd)
            self.__SetHelper('Zoom', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
                '1': 'The Command is not supported by Camera.',
                '2': 'Camera is in Standby (Power Off) or in busy status.',
                '3': 'Data is out of range.',
            }
        try:
            res = response.read().decode()
            valueMatch = self.ErrorRegex.match(res)
            if valueMatch:
                self.Error(['{}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[valueMatch.group(1)])])
                return ''
            else:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        _headers = {}
        _headers['Authorization'] = 'Basic {}'.format(self.authentication)
        url = '{}{}{}'.format(self.RootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'
        my_request = urllib.request.Request(url, headers=_headers)

        try:
            res = urllib.request.urlopen(my_request, timeout=10)
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        _headers = {}

        _headers['Authorization'] = 'Basic {}'.format(self.authentication)
        url = '{}{}{}'.format(self.RootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'
        my_request = urllib.request.Request(url, headers=_headers)

        try:
            res = urllib.request.urlopen(my_request, timeout=10)
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