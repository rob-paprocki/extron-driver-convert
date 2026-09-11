from extronlib.interface import EthernetClientInterface, SerialInterface
from extronlib.system import ProgramLog
from re import compile, search
import base64
import urllib.error
import urllib.request


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
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

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())        

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Backlight': {'Status': {}},
            'ChromaLevel': {'Status': {}},
            'MenuControl': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetClear': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Scene': {'Status': {}},
            'Tally': {'Status': {}},
            'TallyInput': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

        self._backlight_status = compile('OSE:73:([01])')
        self._chroma_level_status = compile('OCG:(0[3-9A-D])')
        self._menu_status = compile('OUS:([01])')
        self._power_status = compile('p([01])')
        self._preset_status = compile('s([0-9]{2})')
        self._scene_status = compile('OSF:([0-3])')
        self._tally_status = compile('dA([01])')
        self._tally_inp_status = compile('tAE([01])')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('Backlight', value, qualifier, url='cam?cmd=OSE:73:{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('Backlight', value, qualifier, url='cam?cmd=QSE:73')
        if res:
            try:
                temp = self._backlight_status.search(res)
                backlight = temp.group(1) if temp else ''
                value = ValueStateValues[backlight]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetChromaLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.__SetHelper('ChromaLevel', value, qualifier, url='cam?cmd=OCG:{}'.format('%0.2X' % (value + 3)))
        else:
            self.Discard('Invalid Command for SetChromaLevel')

    def UpdateChromaLevel(self, value, qualifier):

        res = self.__UpdateHelper('ChromaLevel', value, qualifier, url='cam?cmd=QCG')
        if res:
            try:
                temp = self._chroma_level_status.search(res)
                chroma_level = temp.group(1) if temp else ''
                value = int(chroma_level, 16) - 3
                self.WriteStatus('ChromaLevel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Chroma Level: Invalid/unexpected response'])

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuControl', value, qualifier, url='cam?cmd=DUS:{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetMenuControl')

    def UpdateMenuControl(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('MenuControl', value, qualifier, url='cam?cmd=QUS')
        if res:
            try:
                temp = self._menu_status.search(res)
                menu = temp.group(1) if temp else ''
                value = ValueStateValues[menu]
                self.WriteStatus('MenuControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Menu Control: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'DUP:1',
            'Down': 'DDW:1',
            'Right': 'DRT:1',
            'Left': 'DLT:1',
            'Enter': 'DIT:1',
            'Cancel': 'DPG:1'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuNavigation', value, qualifier, url='cam?cmd={}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPanTilt(self, value, qualifier):

        pan_tilt_speed = int(qualifier['Pan Tilt Speed'])

        ValueStateValues = {
            'Up': '%23T{}'.format(str(50 + pan_tilt_speed).zfill(2)),
            'Down': '%23T{}'.format(str(50 - pan_tilt_speed).zfill(2)),
            'Left': '%23P{}'.format(str(50 - pan_tilt_speed).zfill(2)),
            'Right': '%23P{}'.format(str(50 + pan_tilt_speed).zfill(2)),
            'Stop': '%23PTS5050'
        }

        if value in ValueStateValues and 1 <= pan_tilt_speed <= 49:
            self.__SetHelper('PanTilt', value, qualifier, url='ptz?cmd={}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', value, qualifier, url='ptz?cmd=%23O{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('Power', value, qualifier, url='ptz?cmd=%23O')
        if res:
            try:
                temp = self._power_status.search(res)
                power = temp.group(1) if temp else ''
                value = ValueStateValues[power]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetClear(self, value, qualifier):

        if 1 <= int(value) <= 100:
            self.__SetHelper('PresetClear', value, qualifier, url='ptz?cmd=%23C{}'.format(str(int(value) - 1).zfill(2)))
        else:
            self.Discard('Invalid Command for SetPresetClear')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            self.__SetHelper('PresetRecall', value, qualifier, url='ptz?cmd=%23R{}'.format(str(int(value) - 1).zfill(2)))
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        res = self.__UpdateHelper('PresetRecall', value, qualifier, url='ptz?cmd=%23S')
        if res:
            try:
                temp = self._preset_status.search(res)
                preset = temp.group(1) if temp else ''
                value = str(int(preset) + 1)
                self.WriteStatus('PresetRecall', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Preset Recall: Invalid/unexpected response'])

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            self.__SetHelper('PresetSave', value, qualifier, url='ptz?cmd=%23M{}'.format(str(int(value) - 1).zfill(2)))
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetScene(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': '1',
            'Shutter Priority': '2',
            'Manual': '3'
        }

        if value in ValueStateValues:
            self.__SetHelper('Scene', value, qualifier, url='cam?cmd=XSF:{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetScene')

    def UpdateScene(self, value, qualifier):

        ValueStateValues = {
            '0': 'Full Auto',
            '1': 'Shutter Priority',
            '2': 'Manual'
        }

        res = self.__UpdateHelper('Scene', value, qualifier, url='cam?cmd=QSF')
        if res:
            try:
                temp = self._scene_status.search(res)
                scene = temp.group(1) if temp else ''
                value = ValueStateValues[scene]
                self.WriteStatus('Scene', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Scene: Invalid/unexpected response'])

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('Tally', value, qualifier, url='ptz?cmd=%23DA{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('Tally', value, qualifier, url='ptz?cmd=%23DA')
        if res:
            try:
                temp = self._tally_status.search(res)
                tally = temp.group(1) if temp else ''
                value = ValueStateValues[tally]
                self.WriteStatus('Tally', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tally: Invalid/unexpected response'])

    def SetTallyInput(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('TallyInput', value, qualifier, url='ptz?cmd=%23TAE{}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetTallyInput')

    def UpdateTallyInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        res = self.__UpdateHelper('TallyInput', value, qualifier, url='ptz?cmd=%23TAE')
        if res:
            try:
                temp = self._tally_inp_status.search(res)
                tally = temp.group(1) if temp else ''
                value = ValueStateValues[tally]
                self.WriteStatus('TallyInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tally Input: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Zoom Speed'])

        ValueStateValues = {
            'Wide': '%23Z{}'.format(str(50 - zoom_speed).zfill(2)),
            'Tele': '%23Z{}'.format(str(50 + zoom_speed).zfill(2)),
            'Stop': '%23Z50'
        }

        if value in ValueStateValues and 1 <= zoom_speed <= 49:
            self.__SetHelper('Zoom', value, qualifier, url='ptz?cmd={}'.format(ValueStateValues[value]))
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        DEVICE_ERROR_CODES = {
            'ER1': 'Unsupported command',
            'ER2': 'Busy',
            'ER3': 'Outside acceptable range'
        }

        if res[0:3].upper() in DEVICE_ERROR_CODES:
            self.Error(['Device Error: {0}, Command: {1}'.format(DEVICE_ERROR_CODES[res[0:3].upper()], sourceCmdName)])
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}cgi-bin/aw_{}&res=1'.format(self.RootURL, url)
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': self.authentication
        }
        my_request = urllib.request.Request(url, data=data, headers=headers)

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        
        url = '{}cgi-bin/aw_{}&res=1'.format(self.RootURL, url)
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': self.authentication
        }
        my_request = urllib.request.Request(url, data=data, headers=headers)

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
