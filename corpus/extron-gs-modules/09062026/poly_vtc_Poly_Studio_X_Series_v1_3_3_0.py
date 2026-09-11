# Copyright 2026, Extron. All rights reserved.

from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import urllib.error
import urllib.request
import json
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

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
        self._NumberofCameraNearResults = 5
        self._NumberofCameraFarResults = 5
        self._NumberofPhonebookResults = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallInfoHeartbeat': { 'Status': {}},
            'CallInfoName': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoNumber': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoState': {'Parameters': ['Call'], 'Status': {}},
            'CameraFarList': {'Parameters': ['Position'], 'Status': {}},
            'CameraFarListNavigation': { 'Status': {}},
            'CameraFarListUpdate': { 'Status': {}},
            'CameraFarPanTilt': {'Parameters': ['Position'], 'Status': {}},
            'CameraFarZoom': {'Parameters': ['Position'], 'Status': {}},
            'CameraNearFocus': {'Parameters': ['Position'], 'Status': {}},
            'CameraNearList': {'Parameters': ['Position'], 'Status': {}},
            'CameraNearListNavigation': { 'Status': {}},
            'CameraNearListUpdate': { 'Status': {}},
            'CameraNearPanTilt': {'Parameters': ['Position'], 'Status': {}},
            'CameraNearPreset': {'Parameters': ['Action'], 'Status': {}},
            'CameraNearTracking': {'Parameters': ['Position'], 'Status': {}},
            'CameraNearZoom': {'Parameters': ['Position'], 'Status': {}},
            'CollaborationSessionContentSave': {'Parameters': ['PIN'], 'Status': {}},
            'CollaborationSessionContentSaveStatus': {'Parameters': ['PIN'], 'Status': {}},
            'CollaborationSessionEnd': { 'Status': {}},
            'CollaborationSessionStatus': { 'Status': {}},
            'DeviceMode': { 'Status': {}},
            'DTMF': { 'Status': {}},
            'Hook': {'Parameters': ['Dial String'], 'Status': {}},
            'MicMute': { 'Status': {}},
            'MicrosoftTeamsMeetingStatus': { 'Status': {}},
            'PhonebookDial': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookNavigation': { 'Status': {}},
            'PhonebookResults': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookUpdate': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'SystemState': { 'Status': {}},
            'SystemStatus': {'Parameters': ['Status'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'ZoomRoomsMeetingStatus': { 'Status': {}}
        }
        
        self.CameraFarScroller = Scroller([], self._NumberofCameraFarResults, end='*** End of List ***')
        self.CameraNearScroller = Scroller([], self._NumberofCameraNearResults, end='*** End of List ***')
        self.PhonebookScroller = Scroller([], self._NumberofPhonebookResults, end='*** End of List ***')

        self.CallInfoScroller = Scroller([], 5, mark_end=False, fill={})

        self.cookie_jar = urllib.request.HTTPCookieProcessor()
        self.Opener.add_handler(self.cookie_jar)
        self.x_xsrf_token = None
        self.virtual_disable = False
        self.lastLoginResponse = 0

    def SetLogin(self, value, qualifier):

        self.cookie_jar.cookiejar.clear()
        self.x_xsrf_token = None
    
        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
            return
        url = '{}rest/session'.format(self.RootURL)
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps({'user': self.deviceUsername, 'password': self.devicePassword}, separators=(',', ':')).encode(encoding='iso-8859-1')

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format('Login', err.code, err.reason)])

            if err.code == 403:
                res = json.loads(err.read().decode())
                if res['reason'] == 'SessionInvalidUserNamePassword':
                    self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
                    self.virtual_disable = True

                elif res['reason'] == 'SessionMaxActiveSessionsReached':
                    self.Error(['Login failed: Max active sessions reached.'])
                
                else:
                    self.Error(['Login failed: {}'.format(res['reason'])])

        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format('Login', err.reason)])
        except Exception as err:
            pass
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format('Login', res.status, res.msg)])
            else:

                try:
                    res = json.loads(res.read().decode())

                    if res['success'] == True:
                        for cookie in self.cookie_jar.cookiejar:
                            if cookie.name.lower() == 'xsrf-token':
                                self.x_xsrf_token = cookie.value
                                break
                        self.lastLoginResponse = 0
                        self.Error(['Login success.'])
                            
                        return
                    else:
                        self.Error(['Login failed.'])
                except:
                    self.Error(['Login: Invalid/unexpected response'])
        self.lastLoginResponse = time.monotonic()

    @property
    def NumberofCameraNearResults(self):
        return self._NumberofCameraNearResults

    @NumberofCameraNearResults.setter
    def NumberofCameraNearResults(self, value):
        self._NumberofCameraNearResults = value
        self.CameraNearScroller = Scroller([], self._NumberofCameraNearResults, end='*** End of List ***')

    @property
    def NumberofCameraFarResults(self):
        return self._NumberofCameraFarResults

    @NumberofCameraFarResults.setter
    def NumberofCameraFarResults(self, value):
        self._NumberofCameraFarResults = value
        self.CameraFarScroller = Scroller([], self._NumberofCameraFarResults, end='*** End of List ***')

    @property
    def NumberofPhonebookResults(self):
        return self._NumberofPhonebookResults

    @NumberofPhonebookResults.setter
    def NumberofPhonebookResults(self, value):
        self._NumberofPhonebookResults = value
        self.PhonebookScroller = Scroller([], self._NumberofPhonebookResults, end='*** End of List ***')

    def SetLogin(self, value, qualifier):
        
        self.cookie_jar.cookiejar.clear()
        self.x_xsrf_token = None
    
        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
            return
        url = '{}rest/session'.format(self.RootURL)
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps({'user': self.deviceUsername, 'password': self.devicePassword}, separators=(',', ':')).encode(encoding='iso-8859-1')

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format('Login', err.code, err.reason)])

            if err.code == 403:
                res = json.loads(err.read().decode())
                if res['reason'] == 'SessionInvalidUserNamePassword':
                    self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
                    self.virtual_disable = True

                elif res['reason'] == 'SessionMaxActiveSessionsReached':
                    self.Error(['Login failed: Max active sessions reached.'])
                
                else:
                    self.Error(['Login failed: {}'.format(res['reason'])])

        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format('Login', err.reason)])
        except Exception as err:
            pass
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format('Login', res.status, res.msg)])
            else:

                try:
                    res = json.loads(res.read().decode())

                    if res['success'] == True:
                        for cookie in self.cookie_jar.cookiejar:
                            if cookie.name.lower() == 'xsrf-token':
                                self.x_xsrf_token = cookie.value
                                break
                        self.lastLoginResponse = 0
                        self.Error(['Login success.'])
                            
                        return
                    else:
                        self.Error(['Login failed.'])
                except:
                    self.Error(['Login: Invalid/unexpected response'])
        self.lastLoginResponse = time.monotonic()

    def WriteCameraFarListStatus(self):
        for position, camera in enumerate(self.CameraFarScroller, 1):
            if isinstance(camera, dict):
                name = camera.get('name', '')
                if not name:
                    name = 'Camera Index {}'.format(camera['cameraIndex'])
            else:
                name = camera

            self.WriteStatus('CameraFarList', name, {'Position': str(position)})

    def WriteCameraNearListStatus(self):
        for position, camera in enumerate(self.CameraNearScroller, 1):
            if isinstance(camera, dict):
                name = camera.get('name', '')
                if not name:
                    name = 'Camera Index {}'.format(camera['cameraIndex'])
            else:
                name = camera

            self.WriteStatus('CameraNearList', name, {'Position': str(position)})
    
    def WritePhonebookStatus(self):
        for position, contact in enumerate(self.PhonebookScroller, 1):
            if isinstance(contact, dict):
                name = contact.get('displayName', 'Unknown')
            else:
                name = contact

            self.WriteStatus('PhonebookResults', name, {'Position': str(position)})

    def UpdateCallInfoHeartbeat(self, value, qualifier):

        CallInfoHeartbeatCmdString = 'conferences'
        res = self.__UpdateHelper('CallInfoHeartbeat', value, qualifier, url=CallInfoHeartbeatCmdString)
        if res:
            try:
                self.CallInfoScroller.clear()
                for call in json.loads(res):
                    for connection in call['connections']:
                        new_call = {}

                        new_call['call_id'] = call['id']
                        new_call['conn_id'] = connection['id']
                        new_call['state'] = connection['state']
                        new_call['name'] = connection['address'] # default name to address
                        new_call['address'] = connection['address']
                        for terminal in call['terminals']:
                            if terminal['parentConfId'] == new_call['call_id'] and terminal['parentConnectionId'] == new_call['conn_id']:
                                if terminal['name']:
                                    new_call['name'] = terminal['name']
                                elif terminal['callerID']:
                                    new_call['name'] = terminal['callerID']

                                if terminal['address']:
                                    new_call['address'] = terminal['address']
                                
                                break

                        self.CallInfoScroller.append(new_call)
                
                for call, info in enumerate(self.CallInfoScroller, 1):
                    self.WriteStatus('CallInfoName', info.get('name', ''), {'Call': call})
                    self.WriteStatus('CallInfoNumber', info.get('address', ''), {'Call': call})
                    self.WriteStatus('CallInfoState', info.get('state', 'Idle').title(), {'Call': call})

                    if call >=5:
                        break
            except json.decoder.JSONDecodeError:
                self.Error(['Call Info: Invalid/unexpected response'])

    def SetCameraFarListNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.CameraFarScroller.previous,
            'Down':         self.CameraFarScroller.next,
            'Page Up':      self.CameraFarScroller.previous_page,
            'Page Down':    self.CameraFarScroller.next_page
        }

        if value in ValueStateValues and self.CameraFarScroller.current_size > 0:
            ValueStateValues[value]()
            self.WriteCameraFarListStatus()
        else:
            self.Discard('Invalid Command for SetCameraFarListNavigation')

    def SetCameraFarListUpdate(self, value, qualifier):

        CameraFarListUpdateCmdString = 'cameras/far/all'
        res = self.__UpdateHelper('CameraFarListUpdate', value, qualifier, url=CameraFarListUpdateCmdString)
        if res:
            self.CameraFarScroller.clear()

            try:
                self.CameraFarScroller.overwrite(json.loads(res))
            except json.decoder.JSONDecodeError:
                self.Error(['Camera Far List Update: Invalid/unexpected response'])
        
            self.WriteCameraFarListStatus()

    def SetCameraFarPanTilt(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'Up':       {'action': 'moveStart', 'direction': 'MOVE_UP', 'message': 'BothCamera', 'withImage': 'No'},
            'Down':     {'action': 'moveStart', 'direction': 'MOVE_DOWN', 'message': 'BothCamera', 'withImage': 'No'},
            'Left':     {'action': 'moveStart', 'direction': 'MOVE_LEFT', 'message': 'BothCamera', 'withImage': 'No'},
            'Right':    {'action': 'moveStart', 'direction': 'MOVE_RIGHT', 'message': 'BothCamera', 'withImage': 'No'},
            'Stop':     {'action': 'moveStop', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'}
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraFarScroller.offset + position <= self.CameraFarScroller.current_size:
                CameraFarPanTiltCmdString = 'cameras/far/{}'.format(self.CameraFarScroller[position - 1]['cameraIndex'])
                data = json.dumps(ValueStateValues[value]).encode()

                self.__SetHelper('CameraFarPanTilt', value, qualifier, url=CameraFarPanTiltCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetCameraFarPanTilt')
        else:
            self.Discard('Invalid Command for SetCameraFarPanTilt')

    def SetCameraFarZoom(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'In':   {'action': 'moveStart', 'direction': 'MOVE_ZOOMIN', 'message': 'BothCamera', 'withImage': 'No'},
            'Out':  {'action': 'moveStart', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'},
            'Stop': {'action': 'moveStop', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'}
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraFarScroller.offset + position <= self.CameraFarScroller.current_size:
                CameraFarZoomCmdString = 'cameras/far/{}'.format(self.CameraFarScroller[position - 1]['cameraIndex'])
                data = json.dumps(ValueStateValues[value]).encode()

                self.__SetHelper('CameraFarZoom', value, qualifier, url=CameraFarZoomCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetCameraFarZoom')
        else:
            self.Discard('Invalid Command for SetCameraFarZoom')

    def SetCameraNearFocus(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'Near': {'action': 'moveStart', 'direction': 'MOVE_FOCUSNEAR', 'message': 'BothCamera', 'withImage': 'No'},
            'Far':  {'action': 'moveStart', 'direction': 'MOVE_FOCUSFAR', 'message': 'BothCamera', 'withImage': 'No'},
            'Stop': {'action': 'moveStop', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'}
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraNearScroller.offset + position <= self.CameraNearScroller.current_size:
                CameraNearFocusCmdString = 'cameras/near/{}'.format(self.CameraNearScroller[position - 1]['cameraIndex'])
                data = json.dumps(ValueStateValues[value]).encode()

                self.__SetHelper('CameraNearFocus', value, qualifier, url=CameraNearFocusCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetCameraNearFocus')
        else:
            self.Discard('Invalid Command for SetCameraNearFocus')

    def SetCameraNearListNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.CameraNearScroller.previous,
            'Down':         self.CameraNearScroller.next,
            'Page Up':      self.CameraNearScroller.previous_page,
            'Page Down':    self.CameraNearScroller.next_page
        }

        if value in ValueStateValues and self.CameraNearScroller.current_size > 0:
            ValueStateValues[value]()
            self.WriteCameraNearListStatus()
        else:
            self.Discard('Invalid Command for SetCameraNearListNavigation')

    def SetCameraNearListUpdate(self, value, qualifier):

        CameraNearListUpdateCmdString = 'cameras/near/all'
        res = self.__UpdateHelper('CameraNearListUpdate', value, qualifier, url=CameraNearListUpdateCmdString)
        if res:
            self.CameraNearScroller.clear()

            try:
                self.CameraNearScroller.overwrite(json.loads(res))
            except json.decoder.JSONDecodeError:
                self.Error(['Camera Near List Update: Invalid/unexpected response'])
        
            self.WriteCameraNearListStatus()

    def SetCameraNearPanTilt(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'Up':       {'action': 'moveStart', 'direction': 'MOVE_UP', 'message': 'BothCamera', 'withImage': 'No'},
            'Down':     {'action': 'moveStart', 'direction': 'MOVE_DOWN', 'message': 'BothCamera', 'withImage': 'No'},
            'Left':     {'action': 'moveStart', 'direction': 'MOVE_LEFT', 'message': 'BothCamera', 'withImage': 'No'},
            'Right':    {'action': 'moveStart', 'direction': 'MOVE_RIGHT', 'message': 'BothCamera', 'withImage': 'No'},
            'Stop':     {'action': 'moveStop', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'}
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraNearScroller.offset + position <= self.CameraNearScroller.current_size:
                CameraNearPanTiltCmdString = 'cameras/near/{}'.format(self.CameraNearScroller[position - 1]['cameraIndex'])
                data = json.dumps(ValueStateValues[value]).encode()

                self.__SetHelper('CameraNearPanTilt', value, qualifier, url=CameraNearPanTiltCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetCameraNearPanTilt')
        else:
            self.Discard('Invalid Command for SetCameraNearPanTilt')

    def SetCameraNearPreset(self, value, qualifier):

        ActionStates = {
            'Clear':                {'action': 'clear', 'withImage': 'Yes'},
            'Recall':               {'action': 'activate', 'withImage': 'Yes'},
            'Save with Image':      {'action': 'store', 'withImage': 'Yes'},
            'Save without Image':   {'action': 'store', 'withImage': 'No'}
        }
        action = qualifier['Action']
        if action in ActionStates and 1 <= int(value) <= 10:
            CameraNearPresetCmdString = 'cameras/near/presets/{}'.format(int(value) - 1)
            data = json.dumps(ActionStates[action]).encode()

            self.__SetHelper('CameraNearPreset', value, qualifier, url=CameraNearPresetCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetCameraNearPreset')

    def SetCameraNearTracking(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'On':   'POST',
            'Off':  'DELETE'
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraNearScroller.offset + position <= self.CameraNearScroller.current_size:
                CameraNearTrackingCmdString = 'cameras/near/{}/control/tracking'.format(self.CameraNearScroller[position - 1]['cameraIndex'])
                self.__SetHelper('CameraNearTracking', value, qualifier, url=CameraNearTrackingCmdString, data=None, method=ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetCameraNearTracking')

    def SetCameraNearZoom(self, value, qualifier):

        position = int(qualifier['Position'])

        ValueStateValues = {
            'In':   {'action': 'moveStart', 'direction': 'MOVE_ZOOMIN', 'message': 'BothCamera', 'withImage': 'No'},
            'Out':  {'action': 'moveStart', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'},
            'Stop': {'action': 'moveStop', 'direction': 'MOVE_ZOOMOUT', 'message': 'BothCamera', 'withImage': 'No'}
        }

        if 1 <= position <= 10 and value in ValueStateValues:
            if self.CameraNearScroller.offset + position <= self.CameraNearScroller.current_size:
                CameraNearZoomCmdString = 'cameras/near/{}'.format(self.CameraNearScroller[position - 1]['cameraIndex'])
                data = json.dumps(ValueStateValues[value]).encode()

                self.__SetHelper('CameraNearZoom', value, qualifier, url=CameraNearZoomCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetCameraNearZoom')
        else:
            self.Discard('Invalid Command for SetCameraNearZoom')

    def SetCollaborationSessionContentSave(self, value, qualifier):

        pin_string = qualifier['PIN']
        
        if pin_string:
            CollaborationSessionContentSaveCmdString = 'collaboration/content?pin={}'.format(pin_string)
            self.__SetHelper('CollaborationSessionContentSave', value, qualifier, url=CollaborationSessionContentSaveCmdString, method='POST')
        else:
            self.Discard('Invalid Command for SetCollaborationSessionContentSave')

    def SetCollaborationSessionContentSaveStatus(self, value, qualifier):

        pin_string = qualifier['PIN']

        ValueStateValues = {
            'Enable':   'True',
            'Disable':  'False'
        }
        
        if pin_string and value in ValueStateValues:
            CollaborationSessionContentSaveStatusCmdString = 'collaboration/contentsavestatus?pin={}&status={}'.format(pin_string, ValueStateValues[value])
            self.__SetHelper('CollaborationSessionContentSaveStatus', value, qualifier, url=CollaborationSessionContentSaveStatusCmdString)
        else:
            self.Discard('Invalid Command for SetCollaborationSessionContentSaveStatus')

    def SetCollaborationSessionEnd(self, value, qualifier):

        CollaborationSessionEndCmdString = 'collaboration'
        data = json.dumps({'action': 'END'}).encode()

        self.__SetHelper('CollaborationSessionEnd', value, qualifier, url=CollaborationSessionEndCmdString, data=data)

    def UpdateCollaborationSessionStatus(self, value, qualifier):

        ValueStateValues = {
            'ACTIVE':           'Active',
            'INACTIVE':         'Not Active',
            'READY':            'Ready',
            'DISCONNECTING':    'Disconnecting'
        }
        CollaborationSessionStatusCmdString = 'collaboration'
        res = self.__UpdateHelper('CollaborationSessionStatus', value, qualifier, url=CollaborationSessionStatusCmdString)
        if res:
            try:
                value = ValueStateValues[json.loads(res)['state']]
                self.WriteStatus('CollaborationSessionStatus', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Collaboration Session Status: Invalid/unexpected response'])

    def SetDeviceMode(self, value, qualifier):

        ValueStateValues = {
            'On':   'POST',
            'Off':  'DELETE'
        }

        if value in ValueStateValues:
            DeviceModeCmdString = 'system/mode/device'
            self.__SetHelper('DeviceMode', value, qualifier, url=DeviceModeCmdString, method=ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetDeviceMode')

    def UpdateDeviceMode(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        DeviceModeCmdString = 'system/mode/device'
        res = self.__UpdateHelper('DeviceMode', value, qualifier, url=DeviceModeCmdString)
        if res:
            try:
                value = ValueStateValues[json.loads(res)['result']]
                self.WriteStatus('DeviceMode', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Device Mode: Invalid/unexpected response'])

    def SetDTMF(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#', '.']:
            DTMFCmdString = 'audio/playdtmf'
            data = json.dumps({'dtmfChar': value}).encode()
            
            self.__SetHelper('DTMF', value, qualifier, url=DTMFCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Dial Auto',
            'Dial Video',
            'Dial Audio',
            'Answer',
            'Ignore',
            'Hangup 1',
            'Hangup 2',
            'Hangup 3',
            'Hangup 4',
            'Hangup 5'
        }

        if value in ValueStateValues:
            if 'Dial' in value:
                dial_string = qualifier['Dial String']
                if dial_string:
                    dial_type = value.split()[1]

                    HookCmdString = 'conferences'
                    data = {
                        'address': dial_string,
                        'dialType': 'VOICE' if dial_type == 'Audio' else dial_type.upper(),
                        'rate': 0
                    }
                else:
                    self.Discard('Invalid Command for SetHook')
                    return
            elif value in ['Answer', 'Ignore']:
                for call in self.CallInfoScroller:
                    if call.get('call_id', None) == 'PENDING':
                        HookCmdString = 'conferences/callaction'
                        data = {
                            'id': call['conn_id'],
                            'callActionType': value.upper()
                        }
                        break
                else:
                    self.Discard('Invalid Command for SetHook')
                    return
            elif 'Hangup' in value:
                call = int(value.split()[1])
                if self.CallInfoScroller.offset + call <= self.CallInfoScroller.current_size:
                    HookCmdString = 'conferences/callaction'
                    data = {
                        'id': self.CallInfoScroller[call - 1]['conn_id'],
                        'callActionType': 'HANGUP'
                    }
                else:
                    self.Discard('Invalid Command for SetHook')
                    return
                
            self.__SetHelper('Hook', value, qualifier, url=HookCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetHook')

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            MicMuteCmdString = 'audio/muted'
            data = json.dumps(ValueStateValues[value]).encode()

            self.__SetHelper('MicMute', value, qualifier, url=MicMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        MicMuteCmdString = 'audio/muted'
        res = self.__UpdateHelper('MicMute', value, qualifier, url=MicMuteCmdString)
        if res:
            try:
                self.WriteStatus('MicMute', ValueStateValues[json.loads(res)], qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Mic Mute: Invalid/unexpected response'])

    def UpdateMicrosoftTeamsMeetingStatus(self, value, qualifier):

        ValueStateValues = {
            True:   'Connected',
            False:  'Idle'
        }
        
        MicrosoftTeamsMeetingStatusCmdString = 'system/apps/state'
        res = self.__UpdateHelper('MicrosoftTeamsMeetingStatus', value, qualifier, url=MicrosoftTeamsMeetingStatusCmdString)
        if res:
            try:
                res = json.loads(res)

                for app in res:
                    if app['appPackageName'] == 'com.microsoft.skype.teams.ipphone':
                        self.WriteStatus('MicrosoftTeamsMeetingStatus', ValueStateValues[app['inMeeting']], qualifier)
                        break
            except (json.decoder.JSONDecodeError, KeyError, TypeError):
                self.Error(['Microsoft Teams Meeting Status: Invalid/unexpected response'])

    def SetPhonebookDial(self, value, qualifier):

        position = int(qualifier['Position'])

        if 1 <= position <= 10:
            if self.PhonebookScroller.offset + position <= self.PhonebookScroller.current_size:
                PhonebookDialCmdString = 'directory/local/entries/{}'.format(self.PhonebookScroller[position - 1]['id'])
                data=json.dumps({'action': 'dial'}).encode()

                self.__SetHelper('PhonebookDial', value, qualifier, url=PhonebookDialCmdString, data=data)
            else:
                self.Discard('Invalid Command for SetPhonebookDial')
        else:
            self.Discard('Invalid Command for SetPhonebookDial')

    def SetPhonebookNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.PhonebookScroller.previous,
            'Down':         self.PhonebookScroller.next,
            'Page Up':      self.PhonebookScroller.previous_page,
            'Page Down':    self.PhonebookScroller.next_page
        }

        if value in ValueStateValues and self.PhonebookScroller.current_size > 0:
            ValueStateValues[value]()
            self.WritePhonebookStatus()
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookUpdate(self, value, qualifier):
        PhonebookUpdateCmdString = 'directory/queries/initial'
        res = self.__SetHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString)
        if res:
            try:
                self.PhonebookScroller.clear()
                query = 'directory/queries/{}?start={{}}&limit=100'.format(json.loads(res)['id'])
                while True:
                    current_query = query.format(self.PhonebookScroller.all_size + 1)
                    res = self.__SetHelper('PhonebookUpdate', value, qualifier, url=current_query)
                    if res:
                        try:
                            res = json.loads(res)
                            self.PhonebookScroller.extend(res['entries'])
                            
                            if res['next'] is None:
                                break
                        except (json.decoder.JSONDecodeError, KeyError):
                            self.Error(['Phonebook Update: Invalid/unexpected response'])
                            break
                    else:
                        self.Error(['Phonebook Update: Invalid/unexpected response'])
                        break
        
                self.WritePhonebookStatus()
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Phonebook Update: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'system/reboot'
        data = json.dumps({'restartAll': True}).encode()

        self.__SetHelper('Reboot', value, qualifier, url=RebootCmdString, data=data)

    def UpdateSystemState(self, value, qualifier):

        ValueStateValues = {
            'INITIALIZING':     'Initializing',
            'READY':            'Ready',
            'SHUTTING_DOWN':    'Shutting Down',
            'DOWN':             'Down',
            'UPDATING':         'Updating',
            'ASLEEP':           'Sleep'
        }
        SystemStateCmdString = 'system'
        res = self.__UpdateHelper('SystemState', value, qualifier, url=SystemStateCmdString)
        if res:
            try:
                res = json.loads(res)

                value = ValueStateValues[res['state']]
                self.WriteStatus('SystemState', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['System State: Invalid/unexpected response'])

    def UpdateSystemStatus(self, value, qualifier):

        StatusStates = [
            'LAN Network',
            'Built-In Camera',
            'Cameras',
            'Provisioning Service',
            'Microphones',
            'Remote Control',
            'Log Threshold',
            'Auto Answer Point-to-Point Video',
            'SIP Registrar Server',
            'Gatekeeper',
            'Global Directory Server',
            'Calendaring Service'
        ]
        status = qualifier['Status']

        name_to_status = {
            'system.status.ipnetwork':          'LAN Network',
            'system.status.trackablecamera':    'Built-In Camera',
            'system.status.mr.camera':          'Cameras',
            'system.status.provisioning':       'Provisioning Service',
            'system.status.mr.audio':           'Microphones',
            'system.status.remotecontrol':      'Remote Control',
            'system.status.logthreshold':       'Log Threshold',
            'system.status.autoanswerp2p':      'Auto Answer Point-to-Point Video',
            'system.status.sipserver':          'SIP Registrar Server',
            'system.status.gatekeeper':         'Gatekeeper',
            'system.status.globaldirectory':    'Global Directory Server',
            'system.status.calendar':           'Calendaring Service'
        }

        ValueStateValues = {
            'up':       'Up',
            'all_up':   'All Up',
            'none_up':  'None Up',
            'down':     'Down',
            'off':      'Off',
            'some_up':  'Some Up'
        }

        if status in StatusStates:
            SystemStatusCmdString = 'system/status'
            res = self.__UpdateHelper('SystemStatus', value, qualifier, url=SystemStatusCmdString)
            if res:
                try:
                    res = json.loads(res)
                    for status in res:
                        try:
                            if status['name'] in name_to_status:
                                qualifier = {
                                    'Status': name_to_status[status['name']]
                                }
                                value = ValueStateValues[status['stateList'][0]]
                                
                                self.WriteStatus('SystemStatus', value, qualifier)
                        except (KeyError, IndexError):
                            self.Error(['System Status: Invalid/unexpected response'])
                except json.decoder.JSONDecodeError:
                    self.Error(['System Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSystemStatus')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'video/local/mute'
            data=json.dumps({'mute': ValueStateValues[value]}).encode()

            self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        VideoMuteCmdString = 'video/local/mute'
        res = self.__UpdateHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)
        if res:
            try:
                value = ValueStateValues[json.loads(res)['result']]
                self.WriteStatus('VideoMute', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'audio/volume'
            data = json.dumps(value).encode()
            
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'audio/volume'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                value = int(json.loads(res))
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (json.decoder.JSONDecodeError, ValueError):
                self.Error(['Volume: Invalid/unexpected response'])

    def UpdateZoomRoomsMeetingStatus(self, value, qualifier):

        ValueStateValues = {
            True:   'Connected',
            False:  'Idle'
        }
        
        ZoomRoomsMeetingStatusCmdString = 'system/apps/state'
        res = self.__UpdateHelper('ZoomRoomsMeetingStatus', value, qualifier, url=ZoomRoomsMeetingStatusCmdString)
        if res:
            try:
                res = json.loads(res)

                for app in res:
                    if app['appPackageName'] == 'us.zoom.zoompresence':
                        self.WriteStatus('ZoomRoomsMeetingStatus', ValueStateValues[app['inMeeting']], qualifier)
                        break
            except (json.decoder.JSONDecodeError, KeyError, TypeError):
                self.Error(['Zoom Rooms Meeting Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None, method=None):

        self.Debug = True

        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
            return
        if time.monotonic() - self.lastLoginResponse < 1:
            self.Error(['Login: Device Is Busy'])
            return
        
        url = '{}rest/{}'.format(self.RootURL, url)
        headers = {}

        if not method:
            method = 'POST' if data else 'GET'

        if method == 'POST' and data is not None:
            headers['Content-Type'] = 'application/json'

        if self.x_xsrf_token and method in {'POST', 'PUT', 'DELETE'}:
            headers['X-XSRF-Token'] = self.x_xsrf_token

        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

            if err.code == 403:
                self.SetLogin( None, None)

            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 201, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None, method='GET'):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.virtual_disable:
            self.Error(['Login failed: Credentials invalid. Please supply valid login credentials and reinitialize the driver.'])
            return
        if time.monotonic() - self.lastLoginResponse < 1:
            self.Error(['Login: Device Is Busy'])
            return
        
        url = '{}rest/{}'.format(self.RootURL, url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])

            if err.code == 403:
                self.SetLogin( None, None)

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
        self.lastLoginResponse = 0

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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
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

class Scroller:
    def __init__(self, items, window, mark_end=True, end='', fill=''):

        self.__all_items = list(items)
        self.__filtered_items = []
        self.__filter_key = None
        self.__current_items = self.__all_items
        self.__offset = 0
        self.__window = max(1, window)
        self.__mark_end = mark_end
        self.__end = end
        self.__fill = fill
    
    def __getitem__(self, index):

        return self.view()[index]
 
    def __iter__(self):

        stop = min(self.offset + self.window, self.current_size)
 
        for item in self.__current_items[self.offset:stop]:
            yield item
 
        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                yield self.end
 
            for i in range(fill_count - int(self.mark_end)):
                yield self.fill
 
    def __str__(self):

        s = 'Offset {}/{}, viewing ({{}}) {}/{} items ({})'.format(self.offset, self.max_offset, self.window, self.current_size, self.view())
 
        if not self.filtered:
            return s.format('all')
        else:
            return s.format('filtered')
    
    @property
    def current_items(self):

        return self.__current_items.copy()
 
    @property
    def all_items(self):

        return self.__all_items.copy()
 
    @property
    def filtered_items(self):

        return self.__filtered_items.copy()
 
    @property
    def current_size(self):

        return len(self.__current_items)
 
    @property
    def all_size(self):

        return len(self.__all_items)
 
    @property
    def filtered_size(self):

        return len(self.__filtered_items)
 
    @property
    def offset(self):

        self.__offset = min(self.__offset, self.max_offset)
        return self.__offset
 
    @offset.setter
    def offset(self, offset):

        if 0 <= offset <= self.max_offset:
            self.__offset = offset
            return
 
        raise Exception('offset value \'{}\' is out of range [0, {}]'.format(offset, self.max_offset))
 
    @property
    def window(self):

        return self.__window
 
    @property
    def mark_end(self):

        return self.__mark_end
 
    @property
    def end(self):

        return self.__end
 
    @property
    def fill(self):

        return self.__fill
 
    @property
    def filtered(self):

        return self.__filter_key is not None
 
    @property
    def max_offset(self):

        return max(0, self.current_size - self.window + int(self.mark_end))
 
    def view(self):

        return list(self.__iter__())
 
    def format(self, key):

        items = []
 
        stop = min(self.offset + self.window, self.current_size)
 
        for item in self.__current_items[self.offset:stop]:
            items.append(key(item))
 
        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                items.append(self.end)
 
            for i in range(fill_count - int(self.mark_end)):
                items.append(self.fill)
 
        return items
    
    def clear(self):

        self.__all_items.clear()
 
        self.__filtered_items.clear()
        self.__filter_key = None
 
        self.__current_items = self.__all_items
 
        self.offset = 0
 
    def overwrite(self, items):

        self.clear()
        self.extend(items)
 
    def append(self, item):

        self.__all_items.append(item)
 
        if self.__filter_key is not None and self.__filter_key(item):
            self.__filtered_items.append(item)
 
    def extend(self, items):

        self.__all_items.extend(items)
 
        if self.__filter_key is not None:
            for item in items:
                if self.__filter_key(item):
                    self.__filtered_items.append(item)
 
    def filter(self, key):

        self.__filter_key = key
 
        if self.__filter_key is not None:
            self.__filtered_items = [item for item in self.__all_items if self.__filter_key(item)]
            self.__current_items = self.__filtered_items
        else:
            self.__filtered_items.clear()
            self.__current_items = self.__all_items
 
        self.offset = 0
    
    def scroll(self, steps):

        self.offset = max(0, min(self.offset + steps, self.max_offset))
    
    def previous(self):

        self.scroll(-1)
 
    def next(self):

        self.scroll(1)
 
    def previous_page(self):

        self.scroll(-self.window)
 
    def next_page(self):

        self.scroll(self.window)
 
    def first(self):

        self.offset = 0
 
    def last(self):

        self.offset = self.max_offset