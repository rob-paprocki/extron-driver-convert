# Copyright 2026, Extron. All rights reserved.
# Derived from Extron's onebynd_sm_Automate_VX_Series_v1_0_11_0.py by
# experiments/automate_vx_threeway/build_avx_cs.py. Fixes E2-E11 and additions A1-A6 are
# marked [E#] / [A#] where they occur; everything else is Extron's code, unchanged.
# Not tested on an Automate VX: see experiments/automate_vx_threeway/BUILD.md.

from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import json

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
        
        self.Models = {}

        self.Commands = {
            'AutoSwitch' : {'Status': {}},
            'ConnectionStatus' : {'Status': {}},
            'CameraPresetRecall' : {'Parameters':['Camera'], 'Status': {}},
            'CameraPresetSave' : {'Parameters':['Camera'], 'Status': {}},
            'ForceRoomConfiguration' : {'Status': {}},
            'HomeShotPreset' : {'Status': {}},
            'ISORecording' : {'Status': {}},
            'Layout' : {'Status': {}},
            'Output' : {'Status': {}},
            'PanTilt' : {'Parameters':['Camera'], 'Status': {}},
            'Record' : {'Status': {}},
            'RoomConfiguration' : {'Status': {}},
            'Scenario' : {'Parameters':['ID'], 'Status': {}},
            'Sleep' : {'Status': {}},
            'Stream' : {'Status': {}},
            'SwitchCamera' : {'Status': {}},
            'Wake' : {'Status': {}},
            'Zoom' : {'Parameters':['Camera'], 'Status': {}},
            # [A2-A6] status-only commands for documented calls Extron's driver did not make.
            # Qualifier values are strings ('1', 'A'), as in Extron's camera preset commands.
            'ActiveTalker' : {'Parameters':['Talker'], 'Status': {}},
            'CameraCount' : {'Status': {}},
            'CameraModel' : {'Parameters':['Camera'], 'Status': {}},
            'DefaultShot' : {'Status': {}},
            'HealthStatus' : {'Status': {}},
            'LayoutName' : {'Parameters':['Layout'], 'Status': {}},
            'RecordingSpace' : {'Parameters':['Type'], 'Status': {}},
            'RoomConfigurationName' : {'Parameters':['RoomConfiguration'], 'Status': {}},
            'ScenarioName' : {'Parameters':['Scenario'], 'Status': {}}
        }

        self.Authenticated = False
        self.Token = None
        self.base64Auth = base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode()).decode()

    def TokenRequest(self, value, qualifier):

        self.TokenRequestHandler()

    def TokenRequestHandler(self):

        cmdString = 'get-token' # login command
        res = self.__SetHelper('TokenRequest', None, None, url=cmdString)
        if res:
            try:
                # [E6] X24: a reply without a token asked again at once, with no limit, and a
                # null or empty token counted as logged in. The next Set or Update retries.
                token = res['token']
                if not token:
                    raise KeyError('token')
                self.Token = token # store token
                self.Authenticated = True # set to True if token in response
            except (KeyError, TypeError):
                self.Error(['Failed to obtain token'])

    def SetAutoSwitch(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'api/StartAutoSwitch',
            'Off' : 'api/StopAutoSwitch'
        }

        self.__SetHelper('AutoSwitch', value, qualifier, ValueStateValues[value])

    def UpdateAutoSwitch(self, value, qualifier):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
            True    : 'On',
            False   : 'Off'
        }

        AutoSwitchCmdString = 'api/AutoSwitchStatus'
        res = self.__UpdateHelper('AutoSwitch', value, qualifier, AutoSwitchCmdString)
        if res:
            try:
                value = ValueStateValues[res['results']]
                self.WriteStatus('AutoSwitch', value, qualifier)
            except (KeyError, TypeError):  # [E11]
                self.Error(['Auto Switch: Invalid/unexpected response'])

    def SetCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 255 and 1 <= int(qualifier['Camera']) <= 255:
            data = {
                'cam' : qualifier['Camera'],
                'pre' : value
            }

            CameraPresetRecallCmdString = 'api/CallCameraPreset'
            self.__SetHelper('CameraPresetRecall', value, qualifier, CameraPresetRecallCmdString, data)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):
    
        if 1 <= int(qualifier['Camera']) <= 255 and 1 <= int(value) <= 255:
            data = {
                'cam' : qualifier['Camera'],
                'pre' : value
            }

            CameraPresetSaveCmdString = 'api/SaveCameraPreset'
            self.__SetHelper('CameraPresetSave', value, qualifier, CameraPresetSaveCmdString, data)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetForceRoomConfiguration(self, value, qualifier):

        if 1 <= int(value) <= 99:
            data = {
                'id' : value
            }
            ForceRoomConfigurationCmdString = 'api/ForceChangeRoomConfig'
            self.__SetHelper('ForceRoomConfiguration', value, qualifier, ForceRoomConfigurationCmdString, data)
        else:
            self.Discard('Invalid Command for SetForceRoomConfiguration')

    def SetHomeShotPreset(self, value, qualifier):
    
        HomeShotPresetCmdString = 'api/GoHome'
        self.__SetHelper('HomeShotPreset', value, qualifier, url=HomeShotPresetCmdString)

    def SetISORecording(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'api/StartISORecord',
            'Stop'  : 'api/StopISORecord'
        }

        self.__SetHelper('ISORecording', value, qualifier, ValueStateValues[value])

    def UpdateISORecording(self, value, qualifier):

        ValueStateValues = {
            'true'  : 'Start',
            'false' : 'Stop',
            True    : 'Start',
            False   : 'Stop'
        }

        ISORecordingCmdString = 'api/ISORecordStatus'
        res = self.__UpdateHelper('ISORecording', value, qualifier, ISORecordingCmdString)
        if res:
            try:
                value = ValueStateValues[res['results']]
                self.WriteStatus('ISORecording', value, qualifier)
            except (KeyError, TypeError):  # [E11]
                self.Error(['ISO Recording: Invalid/unexpected response'])

    def SetLayout(self, value, qualifier):

        if value in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                     'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            data = {
                'id' : value
            }

            LayoutCmdString = 'api/ChangeLayout'
            self.__SetHelper('Layout', value, qualifier, LayoutCmdString, data)
        else:
            self.Discard('Invalid Command for SetLayout')

    def SetOutput(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'api/StartOutput',
            'Off' : 'api/StopOutput'
        }

        if value in ValueStateValues:
            self.__SetHelper('Output', value, qualifier, ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetOutput')

    def UpdateOutput(self, value, qualifier):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
            True    : 'On',
            False   : 'Off'
        }

        OutputCmdString = 'api/OutputStatus'
        res = self.__UpdateHelper('Output', value, qualifier, OutputCmdString)
        if res:
            try:
                value = ValueStateValues[res['results']]
                self.WriteStatus('Output', value, qualifier)
            except (KeyError, TypeError):  # [E11]
                self.Error(['Output: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': '0',
            'Up Right': '1',
            'Right': '2',
            'Down Right': '3',
            'Down': '4',
            'Down Left': '5',
            'Left': '6',
            'Up Left': '7',
            'Stop': ''
            }

        if 1 <= qualifier['Camera'] <= 255 and value in ValueStateValues:
            if value == 'Stop':
                PanTiltCmdString = 'api/StopPT'
                data = {
                    'cam': qualifier['Camera'],
                }
            else:

                PanTiltCmdString = 'api/StartPT'
                data = {
                    'cam' : qualifier['Camera'],
                    'ptDir' : ValueStateValues[value]
                }
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'api/StartRecord',
            'Stop'  : 'api/StopRecord',
            'Pause' : 'api/PauseRecord'  # [A1] documented: no body, {"status":"OK",...}
        }

        if value in ValueStateValues:
            self.__SetHelper('Record', value, qualifier, ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetRecord')
        
    def UpdateRecord(self, value, qualifier):

        ValueStateValues = {
            'true'  : 'Start',
            'false' : 'Stop',
            True    : 'Start',
            False   : 'Stop'
        }

        RecordCmdString = 'api/RecordStatus'
        res = self.__UpdateHelper('Record', value, qualifier, RecordCmdString)
        if res:
            try:
                value = ValueStateValues[res['results']]
                self.WriteStatus('Record', value, qualifier)
            except (KeyError, TypeError):  # [E11]
                self.Error(['Record: Invalid/unexpected response'])

    def SetRoomConfiguration(self, value, qualifier):

        if 1 <= int(value) <= 99:
            data = {
                'id' : value
            }

            RoomConfigurationCmdString = 'api/ChangeRoomConfiguration'
            self.__SetHelper('RoomConfiguration', value, qualifier, RoomConfigurationCmdString, data)
        else:
            self.Discard('Invalid Command for SetRoomConfiguration')

    def UpdateRoomConfiguration(self, value, qualifier):
    
        RoomConfigurationCmdString = 'api/RoomConfigStatus'
        res = self.__UpdateHelper('RoomConfiguration', value, qualifier, url=RoomConfigurationCmdString)
        if res:
            try:
                # [E3] X14: the RoomConfigStatus page shows a list, GetAllStatus a single object
                if 'roomConfigs' in res:
                    value = str(res['roomConfigs'][0]['id'])
                else:
                    value = str(res['roomConfig']['id'])
                self.WriteStatus('RoomConfiguration', value, qualifier)
            except (KeyError, IndexError, AttributeError, TypeError):
                self.Error(['Room Configuration: Invalid/unexpected response'])

    def SetScenario(self, value, qualifier):

        # [E2] X25: the help sheet passes the ID as a qualifier with Value None, and a string
        # Value raised TypeError here. Accept either; discard anything that is not a whole number.
        if value is None and qualifier:
            value = qualifier.get('ID')
        try:
            number = int(value)
            if isinstance(value, bool) or (not isinstance(value, str) and number != value):
                number = 0
        except (TypeError, ValueError, OverflowError, ArithmeticError):
            number = 0
        value = number
        if 1 <= value:
            data = {
                'id' : str(value)
            }

            ScenarioCmdString = 'api/GoToScenario'
            self.__SetHelper('Scenario', value, qualifier, url=ScenarioCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetScenario')

    def UpdateScenario(self, value, qualifier):
    
        ScenarioCmdString = 'api/ScenarioStatus'
        res = self.__UpdateHelper('Scenario', value, qualifier, url=ScenarioCmdString)
        if res:
            try:
                value = str(res['scenario']['id'])
                self.WriteStatus('Scenario', value, qualifier)
            except (KeyError, TypeError, ValueError, IndexError, AttributeError):  # [E4] X17
                self.Error(['Scenario: Invalid/unexpected response'])

    def SetSleep(self, value, qualifier):

        SleepCmdString = 'api/Sleep'
        self.__SetHelper('Sleep', value, qualifier, url=SleepCmdString)

    def SetStream(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'api/StartStream',
            'Stop'  : 'api/StopStream'
        }

        if value in ValueStateValues:
            self.__SetHelper('Stream', value, qualifier, ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetStream')
        
    def UpdateStream(self, value, qualifier):

        ValueStateValues = {
            'true'  : 'Start',
            'false' : 'Stop',
            True    : 'Start',
            False   : 'Stop'
        }

        StreamCmdString = 'api/StreamStatus'
        res = self.__UpdateHelper('Stream', value, qualifier, StreamCmdString)
        if res:
            try:
                value = ValueStateValues[res['results']]
                self.WriteStatus('Stream', value, qualifier)
            except (KeyError, TypeError):  # [E11]
                self.Error(['Stream: Invalid/unexpected response'])

    def SetSwitchCamera(self, value, qualifier):

        if 1 <= int(value) <= 255:
            data = {
                'address' : value
            }

            SwitchCameraCmdString = 'api/ManualSwitchCamera'
            self.__SetHelper('SwitchCamera', value, qualifier, SwitchCameraCmdString, data)
        else:
            self.Discard('Invalid Command for SetSwitchCamera')

    def UpdateSwitchCamera(self, value, qualifier):

        SwitchCameraCmdString = 'api/CameraStatus'
        res = self.__UpdateHelper('SwitchCamera', value, qualifier, url=SwitchCameraCmdString)
        if res:
            try:
                # [E10] X16: the page shows a string, GetAllStatus a number; store '1'-'255' either way
                address = res['address']
                number = int(address)
                if isinstance(address, bool) or (not isinstance(address, str) and number != address):
                    raise ValueError(address)
                value = str(number)
                if 1 <= int(value) <= 255:
                    self.WriteStatus('SwitchCamera', value, qualifier)
            except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError):
                self.Error(['Switch Camera: Invalid/unexpected response'])

    def SetWake(self, value, qualifier):

        WakeCmdString = 'api/Wake'
        self.__SetHelper('Wake', value, qualifier, url=WakeCmdString)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': '0',
            'Out': '1',
            'Stop': ''
            }

        if 1 <= qualifier['Camera'] <= 255 and value in ValueStateValues:
            if value == 'Stop':
                ZoomCmdString = 'api/StopZ'
                data = {
                    'cam': qualifier['Camera']
                }
            else:
                ZoomCmdString = 'api/StartZ'
                data = {
                    'cam': qualifier['Camera'],
                    'zDir': ValueStateValues[value]
                }
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetZoom')

    # ---- [A2-A6] documented status calls -----------------------------------------------------
    # Each reply is parsed completely before anything is written, so a subscriber's callback
    # sees a consistent set and a callback's own error is not reported as a bad reply. Shapes
    # are the ones the API pages and the GetAllStatus example document; where they disagree,
    # both are accepted. None of it has been seen on a unit.

    def UpdateLayout(self, value, qualifier):  # [A2]

        res = self.__UpdateHelper('Layout', value, qualifier, 'api/LayoutStatus')
        if res:
            try:
                layout = res['layout']
                if isinstance(layout, list):  # the page shows a list, GetAllStatus an object
                    layout = layout[0]
                value = str(layout['id'])
            except (KeyError, IndexError, TypeError):
                self.Error(['Layout: Invalid/unexpected response'])
                return
            if len(value) == 1 and 'A' <= value <= 'Z':
                self.WriteStatus('Layout', value, qualifier)

    def __UpdateActiveTalkers(self, command, value, qualifier):  # [A3] firmware 6.3 and later

        res = self.__UpdateHelper(command, value, qualifier, 'api/GetActiveTalkers')
        if res:
            try:
                talkers = res['talkers']
                if isinstance(talkers, str):  # documented as a string: "[5,]", "[5,8]", "[ ]"
                    talkers = [t for t in talkers.strip().strip('[]').split(',') if t.strip()]
                positions = [str(int(t)) for t in talkers]
                flag = res.get('defaultShot', res.get('defaultshot'))  # the page spells it both ways
            except (KeyError, ValueError, TypeError):
                self.Error(['Active Talker: Invalid/unexpected response'])
                return
            if flag in (0, 1):
                self.WriteStatus('DefaultShot', 'On' if flag else 'Off')
            for slot in (1, 0):
                self.WriteStatus('ActiveTalker', positions[slot] if slot < len(positions) else 'None',
                                 {'Talker': str(slot + 1)})

    def UpdateActiveTalker(self, value, qualifier):  # [A3]

        self.__UpdateActiveTalkers('ActiveTalker', value, qualifier)

    def UpdateDefaultShot(self, value, qualifier):  # [A3]

        self.__UpdateActiveTalkers('DefaultShot', value, qualifier)

    def UpdateRecordingSpace(self, value, qualifier):  # [A4]

        res = self.__UpdateHelper('RecordingSpace', value, qualifier, 'api/RecordingSpaceAvail')
        if res:
            try:  # the page shows quoted strings, the GetAllStatus example numbers
                available = int(float(res['available_gigabytes']))
                total = int(float(res['total_gigabytes']))
            except (KeyError, ValueError, TypeError, OverflowError):
                self.Error(['Recording Space: Invalid/unexpected response'])
                return
            self.WriteStatus('RecordingSpace', total, {'Type': 'Total'})
            self.WriteStatus('RecordingSpace', available, {'Type': 'Available'})

    def UpdateHealthStatus(self, value, qualifier):  # [A5] top-level status only ('Healthy')

        res = self.__UpdateHelper('HealthStatus', value, qualifier, 'api/HealthStatus')
        if res:
            try:
                value = str(res['status'])
            except (KeyError, TypeError):
                self.Error(['Health Status: Invalid/unexpected response'])
                return
            self.WriteStatus('HealthStatus', value)

    def __ReadNames(self, res, listKey, label, nameKeys=('name',)):  # [A6]

        try:
            names = {}
            for item in res[listKey]:
                name = ''
                for key in nameKeys:
                    if key in item:
                        name = str(item[key])
                        break
                names[str(item['id'])] = name
            return names
        except (KeyError, TypeError):
            self.Error(['{0}: Invalid/unexpected response'.format(label)])
            return None

    def __WriteNames(self, command, qualifierKey, names):  # [A6] also blanks entries no longer listed

        for key in names:
            self.WriteStatus(command, names[key], {qualifierKey: key})
        for key in [k for k in self.Commands[command]['Status'] if k != 'Live' and k not in names]:
            self.WriteStatus(command, '', {qualifierKey: key})

    def UpdateLayoutName(self, value, qualifier):  # [A6]

        res = self.__UpdateHelper('LayoutName', value, qualifier, 'api/GetLayouts')
        if res:
            names = self.__ReadNames(res, 'layouts', 'Layout Name')
            if names is not None:
                self.__WriteNames('LayoutName', 'Layout', names)

    def UpdateRoomConfigurationName(self, value, qualifier):  # [A6] ids quoted on the page, numbers in GetAllStatus

        res = self.__UpdateHelper('RoomConfigurationName', value, qualifier, 'api/GetRoomConfigs')
        if res:
            names = self.__ReadNames(res, 'roomConfigs', 'Room Configuration Name')
            if names is not None:
                self.__WriteNames('RoomConfigurationName', 'RoomConfiguration', names)

    def UpdateScenarioName(self, value, qualifier):  # [A6]

        res = self.__UpdateHelper('ScenarioName', value, qualifier, 'api/GetScenarios')
        if res:
            names = self.__ReadNames(res, 'scenarios', 'Scenario Name')
            if names is not None:
                self.__WriteNames('ScenarioName', 'Scenario', names)

    def __UpdateCameras(self, command, value, qualifier):  # [A6] the page's "name" is a model name

        res = self.__UpdateHelper(command, value, qualifier, 'api/GetCameras')
        if res:
            models = self.__ReadNames(res, 'cameras', 'Camera Model', nameKeys=('name', 'model'))
            if models is not None:
                self.__WriteNames('CameraModel', 'Camera', models)
                self.WriteStatus('CameraCount', len(models))

    def UpdateCameraModel(self, value, qualifier):  # [A6]

        self.__UpdateCameras('CameraModel', value, qualifier)

    def UpdateCameraCount(self, value, qualifier):  # [A6]

        self.__UpdateCameras('CameraCount', value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        # [E5] a non-JSON, status-less or truncated reply raised into the caller, and the
        # device's error reason was never printed (Error prints only its first item)
        try:
            res = json.loads(response.read().decode())
            if res['status'] == 'Error':
                self.Error(['Error: {0}'.format(res.get('err'))])
                return ''
            return res
        except Exception:
            self.Error(['Invalid Response'])

    def __SetHelper(self, command, value, qualifier, url='', data=None, retried=False):

        self.Debug = True
        retryArgs = (command, value, qualifier, url, data)  # [E7] to repeat once after a new login

        if self.Authenticated or command == 'TokenRequest':
            url = '{0}{1}'.format(self.RootURL, url)
            if data: # if command body exists
                data = json.dumps(data).encode() # encode it

            if command == 'TokenRequest':  # if login command, don't include token
                headers = {
                    'Content-Type'      : 'application/json',
                    'Authorization'     : self.base64Auth
                }
            else:
                headers = {
                    'Content-Type'      : 'application/json',
                    'Authorization'     : self.Token
                }
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
                # [E7] a rejected token: log in again and repeat this request once. A fresh token
                # refused as well means this request is not permitted, so the login is kept.
                if err.code == 401 and command != 'TokenRequest' and not retried:
                    self.Authenticated = False
                    self.TokenRequest(None, None)
                    if self.Authenticated:
                        return self.__SetHelper(*retryArgs, retried=True)
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
        else:
            # [E8] X26: the first Set after start-up, or after the module declared Disconnected,
            # was thrown away. Log in, then send it.
            self.TokenRequest(None, None)
            if self.Authenticated:
                return self.__SetHelper(command, value, qualifier, url, data)
            self.Discard('Invalid Command')

    def __UpdateHelper(self, command, value, qualifier, url='', data=None, retried=False):

        retryArgs = (command, value, qualifier, url, data)  # [E7] to repeat once after a new login
        if self.Authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            url = '{0}{1}'.format(self.RootURL, url)
            headers = {
                'Content-Type'      : 'application/json',
                'Authorization'     : self.Token
            }
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
                # [E7] a rejected token: log in again and repeat this request once (see __SetHelper)
                if err.code == 401 and not retried:
                    self.Authenticated = False
                    self.TokenRequest(None, None)
                    if self.Authenticated:
                        return self.__UpdateHelper(*retryArgs, retried=True)
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
            self.Error(['Token not obtained'])
            # [E9] a unit that was off, or refused the login, from start-up never set Connection Status
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.TokenRequest(None, None)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.TokenRequest(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Token = None
        self.Authenticated = False

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
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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