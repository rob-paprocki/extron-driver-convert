from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import GetUnverifiedContext
from extronlib.system import Wait, ProgramLog
import re
import base64
import urllib.error
import urllib.request

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoTracking': { 'Status': {}},
            'AutoTrackingAngle': { 'Status': {}},
            'AutoTrackingHomePosition': { 'Status': {}},
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IrisMode': { 'Status': {}},
            'PanPositionStatus': { 'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'PanTiltAbsolutePosition': {'Parameters':['Pan','Tilt'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'PresetRecallStatus': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'ResetZoom': { 'Status': {}},
            'Tally': { 'Status': {}},
            'TiltPositionStatus': { 'Status': {}},
            'Tracking': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            'ZoomPosition': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02OSL:B6:([01])\x03'), self.__MatchAutoTracking, None)
            self.AddMatchString(re.compile(b'\x02OSL:B7:([012])\x03'), self.__MatchAutoTrackingAngle, None)
            self.AddMatchString(re.compile(b'\x02OSL:C2:([0-3])\x03'), self.__MatchAutoTrackingHomePosition, None)
            self.AddMatchString(re.compile(b'\x02(?:OBR|DCB):([01])\x03'), self.__MatchColorBar, None)
            self.AddMatchString(re.compile(b'\x02ODT:([01])\x03'), self.__MatchDetail, None)
            self.AddMatchString(re.compile(b'd1([01])\r'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'iC(\d{2})\r'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'd3([01])\r'), self.__MatchIrisMode, None)
            self.AddMatchString(re.compile(b'pTV([\w]{4})(\w{4})(\w{3})\w{6}\r'), self.__MatchPanPositionStatus, None)
            self.AddMatchString(re.compile(b'p([01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b's(\d{2})\r'), self.__MatchPresetRecallStatus, None)
            self.AddMatchString(re.compile(b'tAE([01])\r'), self.__MatchTally, None)
            self.AddMatchString(re.compile(b'eR([1-3])', re.I), self.__MatchError, None)

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            AutoTrackingCmdString = '\x02OSL:B6:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def UpdateAutoTracking(self, value, qualifier):

        AutoTrackingCmdString = '\x02QSL:B6\x03'
        self.__UpdateHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)

    def __MatchAutoTracking(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoTracking', value, None)

    def SetAutoTrackingAngle(self, value, qualifier):

        ValueStateValues = {
            'Upper Body':   '2',
            'Full Body':    '1',
            'Off':          '0'
        }

        if value in ValueStateValues:
            AutoTrackingAngleCmdString = '\x02OSL:B7:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('AutoTrackingAngle', AutoTrackingAngleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTrackingAngle')

    def UpdateAutoTrackingAngle(self, value, qualifier):

        AutoTrackingAngleCmdString = '\x02QSL:B7\x03'
        self.__UpdateHelper('AutoTrackingAngle', AutoTrackingAngleCmdString, value, qualifier)

    def __MatchAutoTrackingAngle(self, match, tag):

        ValueStateValues = {
            '2': 'Upper Body',
            '1': 'Full Body',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoTrackingAngle', value, None)

    def SetAutoTrackingHomePosition(self, value, qualifier):

        ValueStateValues = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            'None': '3'
        }

        if value in ValueStateValues:
            AutoTrackingHomePositionCmdString = '\x02OSL:C2:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('AutoTrackingHomePosition', AutoTrackingHomePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTrackingHomePosition')

    def UpdateAutoTrackingHomePosition(self, value, qualifier):

        AutoTrackingHomePositionCmdString = '\x02QSL:C2\x03'
        self.__UpdateHelper('AutoTrackingHomePosition', AutoTrackingHomePositionCmdString, value, qualifier)

    def __MatchAutoTrackingHomePosition(self, match, tag):

        ValueStateValues = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': 'None'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoTrackingHomePosition', value, None)

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ColorBarCmdString = '\x02DCB:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', ColorBarCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        ColorBarCmdString = '\x02QBR\x03'
        self.__UpdateHelper('ColorBar', ColorBarCmdString, value, qualifier)

    def __MatchColorBar(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorBar', value, None)

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            DetailCmdString = '\x02ODT:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('Detail', DetailCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        DetailCmdString = '\x02QDT\x03'
        self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)

    def __MatchDetail(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Detail', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = ('Far', 'Near', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Far':
                focus_spd = 50 + qualifier['Speed']
            elif value == 'Near':
                focus_spd = 50 - qualifier['Speed']
            else:
                focus_spd = 50
            FocusCmdString = '#F{:02d}\r'.format(focus_spd)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':   '1',
            'Manual': '0'
            }

        if value in ValueStateValues:
            FocusModeCmdString = '#D1{}\r'.format(ValueStateValues[value])
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        FocusModeCmdString = '#D1\r'
        self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def __MatchFocusMode(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '0': 'Manual'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FocusMode', value, None)

    def SetIris(self, value, qualifier):

        if 1 <= value <= 99:
            IrisCmdString = '#I{:02d}\r'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = '#I\r'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 99:
            self.WriteStatus('Iris', value, None)

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Manual': '0'
            }

        if value in ValueStateValues:
            IrisModeCmdString = '#D3{}\r'.format(ValueStateValues[value])
            self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIrisMode')

    def UpdateIrisMode(self, value, qualifier):

        IrisModeCmdString = '#D3\r'
        self.__UpdateHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def __MatchIrisMode(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '0': 'Manual'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IrisMode', value, None)

    def UpdatePanPositionStatus(self, value, qualifier):
            
        PanPositionStatusCmdString = '#PTV\r'
        self.__UpdateHelper('PanPositionStatus', PanPositionStatusCmdString, value, qualifier)

    def __MatchPanPositionStatus(self, match, tag):

        pan = int(match.group(1).decode(), 16)
        tilt = int(match.group(2).decode(), 16)
        zoom = int(match.group(3).decode(), 16)

        if 0 <= pan <= 65535:
            self.WriteStatus('PanPositionStatus', pan, None)
        if 0 <= tilt <= 65535:
            self.WriteStatus('TiltPositionStatus', tilt, None)
        if 1365 <= zoom <= 4095:
            self.WriteStatus('ZoomPosition', zoom, None)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Left':
                PanTiltCmdString = '#P{:02d}\r'.format(50 - qualifier['Speed'])
            elif value == 'Right':
                PanTiltCmdString = '#P{:02d}\r'.format(50 + qualifier['Speed'])
            elif value == 'Up':
                PanTiltCmdString = '#T{:02d}\r'.format(50 + qualifier['Speed'])
            elif value == 'Down':
                PanTiltCmdString = '#T{:02d}\r'.format(50 - qualifier['Speed'])
            else:
                PanTiltCmdString = '#PTS5050\r'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPanTiltAbsolutePosition(self, value, qualifier):

        if 0 <= qualifier['Pan'] <= 65535 and 0 <= qualifier['Tilt'] <= 65535:
            PanTiltAbsolutePositionCmdString = '#APC{0:04X}{1:04X}\r'.format(qualifier['Pan'], qualifier['Tilt'])
            self.__SetHelper('PanTiltAbsolutePosition', PanTiltAbsolutePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltAbsolutePosition')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            PowerCmdString = '#O{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '#O\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save':   'M',
            'Recall': 'R',
            'Delete': 'C'
            }

        if qualifier['Type'] in TypeStates and 1 <= int(value) <= 100:
            PresetCmdString = '#{}{:02d}\r'.format(TypeStates[qualifier['Type']], int(value) - 1)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        PresetRecallStatusCmdString = '#S\r'
        self.__UpdateHelper('PresetRecallStatus', PresetRecallStatusCmdString, value, qualifier)

    def __MatchPresetRecallStatus(self, match, tag):

        value = int(match.group(1).decode()) + 1
        if 1 <= value <= 100:
            self.WriteStatus('PresetRecallStatus', value, None)

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = '#APC80008000\r'
        self.__SetHelper('ResetPanTiltPosition', ResetPanTiltPositionCmdString, value, qualifier)

    def SetResetZoom(self, value, qualifier):

        ResetZoomCmdString = '#AXZ555\r'
        self.__SetHelper('ResetZoom', ResetZoomCmdString, value, qualifier)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'Enable':  '1',
            'Disable': '0'
            }

        if value in ValueStateValues:
            TallyCmdString = '#TAE{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        TallyCmdString = '#TAE\r'
        self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)

    def __MatchTally(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Tally', value, None)

    def UpdateTiltPositionStatus(self, value, qualifier):

        self.UpdatePanPositionStatus(value, qualifier)

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'Start':    '1',
            'Stop':     '0'
        }

        if value in ValueStateValues:
            TrackingCmdString = '\x02OSL:BC:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTracking')

    def SetZoom(self, value, qualifier):

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Tele':
                zoom_spd = 50 + qualifier['Speed']
            elif value == 'Wide':
                zoom_spd = 50 - qualifier['Speed']
            else:
                zoom_spd = 50
            ZoomCmdString = '#Z{:02d}\r'.format(zoom_spd)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def SetZoomPosition(self, value, qualifier):

        if 1365 <= value <= 4095:
            ZoomPositionCmdString = '#AXZ{0:03X}\r'.format(value)
            self.__SetHelper('ZoomPosition', ZoomPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomPosition')

    def UpdateZoomPosition(self, value, qualifier):

        self.UpdatePanPositionStatus(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '1': 'Command not supported',
            '2': 'Camera in standby or busy',
            '3': 'Data out of range',
        }

        value = match.group(1).decode()
        self.Error([DEVICE_ERROR_CODES[value]])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        if port == 80:
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        else:
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
            
        urllib.request.install_opener(self.Opener)

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
            'AutoTracking': { 'Status': {}},
            'AutoTrackingAngle': { 'Status': {}},
            'AutoTrackingHomePosition': { 'Status': {}},
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IrisMode': { 'Status': {}},
            'PanPositionStatus': { 'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'PanTiltAbsolutePosition': {'Parameters':['Pan','Tilt'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'PresetRecallStatus': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'ResetZoom': { 'Status': {}},
            'Tally': { 'Status': {}},
            'TiltPositionStatus': { 'Status': {}},
            'Tracking': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            'ZoomPosition': { 'Status': {}}
        }
            
        self.AutoTrackingRegex              = re.compile('OSL:B6:([01])')
        self.AutoTrackingAngleRegex         = re.compile('OSL:B7:([012])')
        self.AutoTrackingHomePositionRegex  = re.compile('OSL:C2:([0-3])')
        self.ColorBarRegex                  = re.compile('OBR:([01])')
        self.DetailRegex                    = re.compile('ODT:([01])')
        self.FocusModeRegex                 = re.compile('d1([01])')
        self.IrisRegex                      = re.compile('iC(\d{2})')
        self.IrisModeRegex                  = re.compile('d3([01])')
        self.PanPositionStatusRegex         = re.compile('pTV([\w]{4})(\w{4})(\w{3})')
        self.PowerRegex                     = re.compile('p([01])')
        self.PresetRecallStatusRegex        = re.compile('s(\d{2})')
        self.TallyRegex                     = re.compile('tAE([01])')
        self.ErrorRegex                     = re.compile('ER([123])', re.I)

    def __GetBasicAuthHeader(self):

        authHandler = '{0}:{1}'.format(self.deviceUsername, self.devicePassword).encode()
        authHeader = base64.b64encode(authHandler).decode("ascii")
        return authHeader
    
    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=OSL:B6:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoTracking', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def UpdateAutoTracking(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        data = 'cmd=QSL:B6&res=1'
        res = self.__UpdateHelper('AutoTracking', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                }

                valueMatch = self.AutoTrackingRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoTracking', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Tracking: Invalid/unexpected response'])

    def SetAutoTrackingAngle(self, value, qualifier):

        ValueStateValues = {
            'Upper Body':   '2',
            'Full Body':    '1',
            'Off':          '0'
        }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=OSL:B7:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoTrackingAngle', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetAutoTrackingAngle')

    def UpdateAutoTrackingAngle(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        data = 'cmd=QSL:B7&res=1'
        res = self.__UpdateHelper('AutoTrackingAngle', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '2': 'Upper Body',
                    '1': 'Full Body',
                    '0': 'Off'
                }

                valueMatch = self.AutoTrackingAngleRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoTrackingAngle', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Tracking Angle: Invalid/unexpected response'])

    def SetAutoTrackingHomePosition(self, value, qualifier):

        ValueStateValues = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            'None': '3'
        }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=OSL:C2:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoTrackingHomePosition', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetAutoTrackingHomePosition')

    def UpdateAutoTrackingHomePosition(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        data = 'cmd=QSL:C2&res=1'
        res = self.__UpdateHelper('AutoTrackingHomePosition', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '0': '1',
                    '1': '2',
                    '2': '3',
                    '3': 'None'
                }

                valueMatch = self.AutoTrackingHomePositionRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoTrackingHomePosition', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Tracking Home Position: Invalid/unexpected response'])

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
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
            'On':  '1',
            'Off': '0'
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
                    '1': 'On',
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

    def SetIris(self, value, qualifier):

        if 1 <= value <= 99:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23I{:02d}&res=1'.format(value)
            self.__SetHelper('Iris', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23I&res=1'
        res = self.__UpdateHelper('Iris', value, qualifier, url=url, data=data)
        if res:
            try:
                valueMatch = self.IrisRegex.match(res)
                value = int(valueMatch.group(1))
                self.WriteStatus('Iris', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Iris: Invalid/unexpected response'])

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':   '1',
            'Manual': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23D3{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('IrisMode', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetIrisMode')

    def UpdateIrisMode(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('IrisMode', value, qualifier, url=url, data=data)
        if res:
            try:
                ValueStateValues = {
                    '1': 'Auto',
                    '0': 'Manual'
                    }

                valueMatch = self.IrisModeRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('IrisMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Iris Mode: Invalid/unexpected response'])

    def UpdatePanPositionStatus(self, value, qualifier):
            
        PanPositionStatusCmdString = 'cgi-bin/aw_ptz?'
        data = 'cmd=%23PTV&res=1'
        res = self.__UpdateHelper('PanPositionStatus', value, qualifier, url=PanPositionStatusCmdString, data=data)
        if res:
            valueMatch = self.PanPositionStatusRegex.match(res)
            try:
                value = int(valueMatch.group(1), 16)
                if 0 <= value <= 65535:
                    self.WriteStatus('PanPositionStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Pan Position Status: Invalid/unexpected response'])

            try:
                value = int(valueMatch.group(2), 16)
                self.WriteStatus('TiltPositionStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Tilt Position Status: Invalid/unexpected response'])

            try:
                value = int(valueMatch.group(3), 16)
                self.WriteStatus('ZoomPosition', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Zoom Position: Invalid/unexpected response'])

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

    def SetPanTiltAbsolutePosition(self, value, qualifier):

        if 0 <= qualifier['Pan'] <= 65535 and 0 <= qualifier['Tilt'] <= 65535:
            PanTiltAbsolutePositionCmdString = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23APC{0:04X}{1:04X}&res=1'.format(qualifier['Pan'], qualifier['Tilt'])
            self.__SetHelper('PanTiltAbsolutePosition', value, qualifier, url=PanTiltAbsolutePositionCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPanTiltAbsolutePosition')

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
            'Save': 'M',
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

    def UpdateTiltPositionStatus(self, value, qualifier):

        self.UpdatePanPositionStatus(value, qualifier)

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'Start':    '1',
            'Stop':     '0'
        }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            data = 'cmd=OSL:BC:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Tracking', value, qualifier, url=url, data=data)
        else:
            self.Discard('Invalid Command for SetTracking')

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

    def SetZoomPosition(self, value, qualifier):

        if 1365 <= value <= 4095:
            ZoomPositionCmdString = 'cgi-bin/aw_ptz?'
            data = 'cmd=%23AXZ{0:03X}&res=1'.format(value)
            self.__SetHelper('ZoomPosition', value, qualifier, url=ZoomPositionCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetZoomPosition')

    def UpdateZoomPosition(self, value, qualifier):

        self.UpdatePanPositionStatus(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '1': 'Command not supported',
            '2': 'Camera in standby or busy',
            '3': 'Data out of range',
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

        rootURL = self.RootURL
        url = '{}{}{}'.format(rootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'
        
        headers = {}
        headers['Authorization'] = 'Basic {}'.format(self.__GetBasicAuthHeader())
        my_request = urllib.request.Request(url, headers=headers, method='GET')

        try:
            if self.DefaultPort == 443:
                res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
            else:
                res = urllib.request.urlopen(my_request, timeout=1)
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

        rootURL = self.RootURL
        url = '{}{}{}'.format(rootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'

        headers = {}
        headers['Authorization'] = 'Basic {}'.format(self.__GetBasicAuthHeader())
        my_request = urllib.request.Request(url, headers=headers, method='GET')

        try:
            if self.DefaultPort == 443:
                res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
            else:
                res = urllib.request.urlopen(my_request, timeout=1)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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