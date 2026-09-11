from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import base64
from struct import pack, unpack
import re
import urllib.error
import urllib.request
import json

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x81
        self.Models = {
            'CR-N300': self.cano_19_5331_300,
            'CR-N500': self.cano_19_5331_500,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = value
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAutoExposure(self, value, qualifier):

        if value in self.SetAutoExposure_ValueStateValues:
            AutoExposureCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x39, self.SetAutoExposure_ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateAutoExposure_ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        AutoFocusCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        BacklightCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }

        if value in ValueStateValues:
            GainCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')
    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }

        if value in ValueStateValues:
            IrisCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303,
            'Home':         0x04,
            'Reset':        0x05
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = pack('>5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }
        PowerCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save':     0x01,
            'Recall':   0x02,
            'Reset':    0x00
        }
        action = qualifier['Action']

        if action in ActionStates and 1 <= int(value) <= 100:
            PresetCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, ActionStates[action], int(value) - 1, 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }

        if value in ValueStateValues:
            ShutterCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            errors = {
                0x01: 'Message Length Error',
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }

            address, errorbyte, errorcode, terminator = unpack('>4B', response)
            if errorbyte & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, errors.get(errorcode, 'Unknown Error'))])
                return b''

            return response

        return b''

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def cano_19_5331_300(self):

        self.SetAutoExposure_ValueStateValues = {
            'Program AE':       0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority':    0x0B
        }

        self.UpdateAutoExposure_ValueStateValues = {
            0x00: 'Program AE',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority'
        }

    def cano_19_5331_500(self):

        self.SetAutoExposure_ValueStateValues = {
            'Program AE':   0x00,
            'Manual':       0x03
        }

        self.UpdateAutoExposure_ValueStateValues = {
            0x00: 'Program AE',
            0x03: 'Manual'
        }

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

class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {
            'CR-N300': self.cano_19_5331_300,
            'CR-N500': self.cano_19_5331_500,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoTracking': { 'Status': {}},
            'AutoTrackingTargetSize': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.AutoFocusRegex = re.compile('c\.1\.focus:=(auto|manual)')
        self.PowerRegex = re.compile('f\.standby:=(idle|standby)')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   'auto',
            'Off':  'manual'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = '-wvhttp-01-/control.cgi?c.1.focus={}'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, url=AutoFocusCmdString)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            AutoTrackingCmdString = 'cgi-addon/Auto_Tracking_RA-AT001/app_ctrl/update_config.cgi?trackingEnable={}'.format(ValueStateValues[value])
            self.__SetHelper('AutoTracking', value, qualifier, url=AutoTrackingCmdString)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def UpdateAutoTracking(self, value, qualifier):
        
        AutoTrackingCmdString = 'cgi-addon/Auto_Tracking_RA-AT001/app_ctrl/get_config.cgi?keys=trackingEnable,targetSizeLevel'
        res = self.__UpdateHelper('AutoTracking', value, qualifier, url=AutoTrackingCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                }

                value = ValueStateValues[res['trackingEnable']]
                self.WriteStatus('AutoTracking', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Tracking: Invalid/unexpected response'])
            try:
                value = res['targetSizeLevel']
                if 1 <= int(value) <= 5:
                    self.WriteStatus('AutoTrackingTargetSize', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Tracking Target Size: Invalid/unexpected response'])

    def SetAutoTrackingTargetSize(self, value, qualifier):

        if 1 <= int(value) <= 5:
            AutoTrackingTargetSizeCmdString = 'cgi-addon/Auto_Tracking_RA-AT001/app_ctrl/update_config.cgi?targetSizeLevel={}'.format(int(value))
            self.__SetHelper('AutoTrackingTargetSize', value, qualifier, url=AutoTrackingTargetSizeCmdString)
        else:
            self.Discard('Invalid Command for SetAutoTrackingTargetSize')

    def UpdateAutoTrackingTargetSize(self, value, qualifier):

        self.UpdateAutoTracking(value, None)

    def SetFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = [
            'Far',
            'Near',
            'Stop'
        ]

        if 0 <= speed <= 63 and value in ValueStateValues:
            FocusCmdString = '-wvhttp-01-/control.cgi?c.1.focus.action={}'.format(value.lower())
            if value != 'Stop':
                FocusCmdString += '&c.1.focus.speed={}'.format(speed)

            self.__SetHelper('Focus', value, qualifier, url=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           'c.1.tilt=up&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=stop',
            'Down':         'c.1.tilt=down&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=stop',
            'Left':         'c.1.pan=left&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual&c.1.tilt=stop',
            'Right':        'c.1.pan=right&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual&c.1.tilt=stop',
            'Up Left':      'c.1.tilt=up&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=left&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual',
            'Up Right':     'c.1.tilt=up&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=right&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual',
            'Down Left':    'c.1.tilt=down&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=left&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual',
            'Down Right':   'c.1.tilt=down&c.1.tilt.speed.dir={t}&c.1.tilt.speed.mode.dir=manual&c.1.pan=right&c.1.pan.speed.dir={p}&c.1.pan.speed.mode.dir=manual',
            'Stop':         'c.1.pan=stop&c.1.tilt=stop'
        }

        if self.pan_tilt_min <= pan_speed <= 10000 and self.pan_tilt_min <= tilt_speed <= 10000 and value in ValueStateValues:
            PanTiltCmdString = '-wvhttp-01-/control.cgi?' + ValueStateValues[value].format(**{'p': pan_speed, 't': tilt_speed})
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'idle',
            'Off':  'standby'
        }

        if value in ValueStateValues:
            PowerCmdString = '-wvhttp-01-/standby.cgi?cmd={}'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url=PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '-wvhttp-01-/info.cgi?item=f.standby,c.1.focus,f.standby.!,c.1.focus.!'
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                ValueStateValues = {
                    'idle':     'On',
                    'standby':  'Off'
                }

                value = ValueStateValues[self.PowerRegex.search(res).group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])
            try:
                ValueStateValues = {
                    'auto':     'On',
                    'manual':   'Off'
                }

                value = ValueStateValues[self.AutoFocusRegex.search(res).group(1)]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save':     '-wvhttp-01-/preset/set?p={}&all=enabled',
            'Recall':   '-wvhttp-01-/control.cgi?p={}',
            'Reset':    '-wvhttp-01-/preset/set?p={}&cmd=delete'
        }
        action = qualifier['Action']

        if action in ActionStates and 1 <= value <= 100:
            PresetCmdString = ActionStates[action].format(value)
            self.__SetHelper('Preset', value, qualifier, url=PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = [
            'Tele',
            'Wide',
            'Stop'
        ]

        if 0 <= speed <= 127 and value in ValueStateValues:
            ZoomCmdString = '-wvhttp-01-/control.cgi?c.1.zoom={}'.format(value.lower())
            if value != 'Stop':
                ZoomCmdString += '&c.1.zoom.speed={}'.format(speed)

            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            res = response.read().decode()

            if sourceCmdName in ['AutoTracking', 'AutoTrackingTargetSize']:                
                res = json.loads(res)

                if isinstance(res, dict) and res.get('status_code', '').startswith('E'):
                    self.Error(['{}: {}'.format(sourceCmdName, res['status_code'])])
                    return ''
                else:
                    return res
            else:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        
        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization' : self.authentication
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization' : self.authentication
        }

        # Create Request object
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            self.WriteDeviceResponseStatus('Good', None, 'Live')
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

    def cano_19_5331_300(self):

        self.pan_tilt_min = 20

    def cano_19_5331_500(self):

        self.pan_tilt_min = 10

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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