from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from struct import pack, unpack
import re
import urllib.error
import urllib.request

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PTZAutoFraming': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x03: 'Off'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : 0x20,
            'Near' : 0x30,
            'Stop' : 0x00
        }

        speed = qualifier['Speed']
        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]
                
            FocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'        : 0x0301,
            'Down'      : 0x0302,
            'Left'      : 0x0103,
            'Right'     : 0x0203,
            'Up Left'   : 0x0101,
            'Up Right'  : 0x0201,
            'Down Left' : 0x0102,
            'Down Right': 0x0202,
            'Stop'      : 0x0303,
            'Home'      : 0x04,
            'Reset'     : 0x05
        }

        panSpeed = int(qualifier['Pan Speed'])
        tiltSpeed = int(qualifier['Tilt Speed'])

        if 1 <= panSpeed <= 24 and 1 <= tiltSpeed <= 23 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = pack('>5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, panSpeed, tiltSpeed, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02 : 'On',
                    0x03 : 'Off'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 100:
            PresetRecallCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, preset - 1, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 100:
            PresetResetCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x00, preset - 1, 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 100:
            PresetSaveCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, preset - 1, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPTZAutoFraming(self, value, qualifier):

        ValueStateValues = {
            'Start' : 0x01,
            'Stop'  : 0x00
        }

        if value in ValueStateValues:
            PTZAutoFramingCmdString = pack('>7B', self._DeviceID, 0x01, 0x7E, 0x04, 0x3A, ValueStateValues[value], 0xFF)
            self.__SetHelper('PTZAutoFraming', PTZAutoFramingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPTZAutoFraming')

    def UpdatePTZAutoFraming(self, value, qualifier):

        PTZAutoFramingCmdString = pack('>6B', self._DeviceID, 0x09, 0x7E, 0x04, 0x3A, 0xFF)
        res = self.__UpdateHelper('PTZAutoFraming', PTZAutoFramingCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01 : 'Start',
                    0x00 : 'Stop'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('PTZAutoFraming', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['PTZ Auto Framing: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        speed = qualifier['Speed']
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
            error_map = {
                0x01: 'Message Length Error',
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }

            address, error_byte, error_code, terminator = unpack('>4B', response)
            if error_byte & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map.get(error_code, 'Unknown Error'))])
                response = ''

        return response

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
        if deviceUsername and devicePassword:
            authentication = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authentication.add_password(None, self.RootURL, deviceUsername, devicePassword)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(authentication))
        else:
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler())

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': {'Parameters':['Name','Thumbnail'], 'Status': {}},
            'PTZAutoFraming': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'auto',
            'Off' : 'manual'
        }

        if value in ValueStateValues:
            AutoFocusCmdString ='command/ptzf.cgi?FocusMode={0}'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, AutoFocusCmdString)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = 'command/inquiry.cgi?inq=ptzf'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, AutoFocusCmdString)
        if res:
            try:
                ValueStateValues = {
                    'auto'   : 'On',
                    'manual' : 'Off'
                }

                valueMatch = re.search('FocusMode="?(auto|manual)"?', res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = ['Far', 'Near', 'Stop']

        if 0 <= qualifier['Speed'] <= 8 and value in ValueStateValues:
            if value == 'Stop':
                FocusCmdString = 'command/ptzf.cgi?Move=stop,focus'
            else:
                FocusCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(value.lower(), qualifier['Speed'])

            self.__SetHelper('Focus', value, qualifier, FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'        : 'up', 
            'Down'      : 'down', 
            'Left'      : 'left', 
            'Right'     : 'right', 
            'Up Left'   : 'up-left', 
            'Up Right'  : 'up-right', 
            'Down Left' : 'down-left', 
            'Down Right': 'down-right', 
            'Stop'      : 'stop',
            'Home'      : 'home',
            'Reset'     : 'reset'
        }

        if 0 <= qualifier['Speed'] <= 24 and value in ValueStateValues:
            if value == 'Stop':
                PanTiltCmdString = 'command/ptzf.cgi?Move=stop,pantilt'
            elif value == 'Home':
                PanTiltCmdString = 'command/presetposition.cgi?HomePos=recall'
            elif value == 'Reset':
                PanTiltCmdString = 'command/ptzf.cgi?PanTiltReset=on'
            else:
                PanTiltCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(ValueStateValues[value], qualifier['Speed'])
            self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on',
            'Off' : 'standby'
        }

        if value in ValueStateValues:
            PowerCmdString = 'command/main.cgi?System={0}'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'command/inquiry.cgi?inq=sysinfo'
        res = self.__UpdateHelper('Power', value, qualifier, PowerCmdString)
        if res:
            try:
                ValueStateValues = {
                    'on'     : 'On',
                    'standby': 'Off'
                }

                valueMatch = re.search('Power="?(on|standby)"?', res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 256:
            PresetRecallCmdString = 'command/presetposition.cgi?PresetCall={0}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 1 <= value <= 256:
            PresetResetCmdString = 'command/presetposition.cgi?PresetClear={0}'.format(value)
            self.__SetHelper('PresetReset', value, qualifier, PresetResetCmdString)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        ThumbnailStates = ['On', 'Off']

        name = qualifier['Name']
        if 0 <= len(name) <= 32 and qualifier['Thumbnail'] in ThumbnailStates and 1 <= value <= 256:
            PresetSaveCmdString = 'command/presetposition.cgi?PresetSet={0},{1},{2}'.format(value, qualifier['Name'], qualifier['Thumbnail'].lower())
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPTZAutoFraming(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'on',
            'Stop'  : 'off'
        }

        if value in ValueStateValues:
            PTZAutoFramingCmdString = 'analytics/ptzautoframing.cgi?PtzAutoFraming={0}'.format(ValueStateValues[value])
            self.__SetHelper('PTZAutoFraming', value, qualifier, PTZAutoFramingCmdString)
        else:
            self.Discard('Invalid Command for SetPTZAutoFraming')

    def UpdatePTZAutoFraming(self, value, qualifier):

        PTZAutoFramingCmdString = 'command/inquiry.cgi?inq=ptzautoframing'
        res = self.__UpdateHelper('PTZAutoFraming', value, qualifier, PTZAutoFramingCmdString)
        if res:
            try:
                ValueStateValues = {
                    'on'  : 'Start',
                    'off' : 'Stop'
                }

                valueMatch = re.search('PtzAutoFraming="?(on|off)"?', res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('PTZAutoFraming', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['PTZ Auto Framing: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = ['Tele', 'Wide', 'Stop']
        if 0 <= qualifier['Speed'] <= 8 and value in ValueStateValues:
            if value == 'Stop':
                ZoomCmdString = 'command/ptzf.cgi?Move=stop,zoom'
            else:
                ZoomCmdString = 'command/ptzf.cgi?Move={0},{1}'.format(value.lower(), qualifier['Speed'])
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = ''.join([self.RootURL,url])
        headers = {
            'Content-Type': 'text/plain',
            'Referer': 'http://{}/\\r\\n'.format(self.IPAddress)
        }
        my_request = urllib.request.Request(url, data=None, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful            
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

        url = ''.join([self.RootURL,url])
        headers = {
            'Content-Type': 'text/plain',
            'Referer': 'http://{}/\\r\\n'.format(self.IPAddress)
        }
        my_request = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
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