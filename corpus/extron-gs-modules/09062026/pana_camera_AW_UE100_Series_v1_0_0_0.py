from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import GetUnverifiedContext
import re
from extronlib.system import Wait, ProgramLog
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
            'ColorBar': {'Status': {}},
            'Detail': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'PresetRecallStatus': {'Status': {}},
            'ResetPanTiltPosition': {'Status': {}},
            'ResetZoom': {'Status': {}},
            'SceneFileControl': {'Status': {}},
            'Tally': {'Status': {}},
            'TallyEnable': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02(?:OBR|DCB):([01])\x03'), self.__MatchColorBar, None)
            self.AddMatchString(re.compile(b'\x02ODT:([012])\x03'), self.__MatchDetail, None)
            self.AddMatchString(re.compile(b'd1([01])\r'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(rb'iC(\d{2})\r'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'd3([01])\r'), self.__MatchIrisMode, None)
            self.AddMatchString(re.compile(b'p([01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(rb's(\d{2})\r'), self.__MatchPresetRecallStatus, None)
            self.AddMatchString(re.compile(b'\x02OSF:([0-3])\x03'), self.__MatchSceneFileControl, None)
            self.AddMatchString(re.compile(b'dA([01])\r'), self.__MatchTally, None)
            self.AddMatchString(re.compile(b'tAE([01])\r'), self.__MatchTallyEnable, None)
            self.AddMatchString(re.compile(b'eR([1-3])', re.I), self.__MatchError, None)
            # Ignore case to match both eRn and \x02ERn\x03 responses, where n is error number

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
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
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorBar', value, None)

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On (1)': '1',
            'On (2)': '2',
            'Off': '0',
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
            '1': 'On (1)',
            '2': 'On (2)',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Detail', value, None)

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Far', 'Near', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Far':
                focus_spd = 50 + SpeedConstraints['Value']
            elif value == 'Near':
                focus_spd = 50 - SpeedConstraints['Value']
            else:
                focus_spd = 50
            FocusCmdString = '#F{:02d}\r'.format(focus_spd)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Manual': '0',
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

        ValueConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            IrisCmdString = '#I{:02d}\r'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = '#I\r'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Iris', value, None)

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Manual': '0',
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
            '0': 'Manual',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IrisMode', value, None)

    def SetPanTilt(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Left':
                PanTiltCmdString = '#P{:02d}\r'.format(50 - SpeedConstraints['Value'])
            elif value == 'Right':
                PanTiltCmdString = '#P{:02d}\r'.format(50 + SpeedConstraints['Value'])
            elif value == 'Up':
                PanTiltCmdString = '#T{:02d}\r'.format(50 + SpeedConstraints['Value'])
            elif value == 'Down':
                PanTiltCmdString = '#T{:02d}\r'.format(50 - SpeedConstraints['Value'])
            else:
                PanTiltCmdString = '#PTS5050\r'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
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
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save': 'M',
            'Recall': 'R',
            'Delete': 'C',
        }

        ValueConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(value) if value.isdigit() else -1,
        }

        action_type = qualifier['Type']
        if self.__constraint_checker(ValueConstraints) and action_type in TypeStates:
            PresetCmdString = '#{}{:02d}\r'.format(TypeStates[action_type], ValueConstraints['Value'] - 1)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        PresetRecallStatusCmdString = '#S\r'
        self.__UpdateHelper('PresetRecallStatus', PresetRecallStatusCmdString, value, qualifier)

    def __MatchPresetRecallStatus(self, match, tag):

        value = int(match.group(1).decode()) + 1
        self.WriteStatus('PresetRecallStatus', value, None)

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = '#APC80008000\r'
        self.__SetHelper('ResetPanTiltPosition', ResetPanTiltPositionCmdString, value, qualifier)

    def SetResetZoom(self, value, qualifier):

        ResetZoomCmdString = '#AXZ555\r'
        self.__SetHelper('ResetZoom', ResetZoomCmdString, value, qualifier)

    def SetSceneFileControl(self, value, qualifier):

        ValueStateValues = {
            'Scene 1': '1',
            'Scene 2': '2',
            'Scene 3': '3',
            'Scene 4': '4',
        }

        if value in ValueStateValues:
            SceneFileControlCmdString = '\x02XSF:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('SceneFileControl', SceneFileControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneFileControl')

    def UpdateSceneFileControl(self, value, qualifier):

        SceneFileControlCmdString = '\x02QSF\x03'
        self.__UpdateHelper('SceneFileControl', SceneFileControlCmdString, value, qualifier)

    def __MatchSceneFileControl(self, match, tag):

        ValueStateValues = {
            '0': 'Scene 1',
            '1': 'Scene 2',
            '2': 'Scene 3',
            '3': 'Scene 4',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SceneFileControl', value, None)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            TallyCmdString = '#DA{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        TallyCmdString = '#DA\r'
        self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)

    def __MatchTally(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Tally', value, None)

    def SetTallyEnable(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            TallyEnableCmdString = '#TAE{}\r'.format(ValueStateValues[value])
            self.__SetHelper('TallyEnable', TallyEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTallyEnable')

    def UpdateTallyEnable(self, value, qualifier):

        TallyEnableCmdString = '#TAE\r'
        self.__UpdateHelper('TallyEnable', TallyEnableCmdString, value, qualifier)

    def __MatchTallyEnable(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TallyEnable', value, None)

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Tele':
                zoom_spd = 50 + SpeedConstraints['Value']
            elif value == 'Wide':
                zoom_spd = 50 - SpeedConstraints['Value']
            else:
                zoom_spd = 50
            ZoomCmdString = '#Z{:02d}\r'.format(zoom_spd)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        ErrorStateNames = {
            '1': 'The Command is not supported by Camera.',
            '2': 'Camera is in Standby (Power Off) or in busy status.',
            '3': 'Data is out of range.',
        }

        value = match.group(1).decode()
        self.Error(['Device Error: {}'.format(ErrorStateNames[value])])

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
        
        # check incoming data if it matched any expected data from device module
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

class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='Off'):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self._context = GetUnverifiedContext()

        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.IPPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ColorBar': {'Status': {}},
            'Detail': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'PresetRecallStatus': {'Status': {}},
            'ResetPanTiltPosition': {'Status': {}},
            'ResetZoom': {'Status': {}},
            'SceneFileControl': {'Status': {}},
            'Tally': {'Status': {}},
            'TallyEnable': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.ColorBar = re.compile('OBR:([01])')
        self.Detail = re.compile('ODT:([012])')
        self.FocusMode = re.compile('d1([01])')
        self.Iris = re.compile('iC(\d{2})')
        self.IrisMode = re.compile('d3([01])')
        self.Power = re.compile('p([01])')
        self.PresetRecallStatus = re.compile('s(\d{2})')
        self.SceneFileControl = re.compile('OSF:([0-3])')
        self.Tally = re.compile('dA([01])')
        self.TallyEnable = re.compile('tAE([01])')

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            ColorBarCmdString = 'cmd=DCB:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', value, qualifier, url='', data=ColorBarCmdString)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ColorBarCmdString = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url='', data=ColorBarCmdString)
        if res:
            try:
                match_grp = self.ColorBar.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('ColorBar', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Color Bar: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On (1)': '1',
            'On (2)': '2',
            'Off':    '0',
        }

        if value in ValueStateValues:
            DetailCmdString = 'cmd=ODT:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Detail', value, qualifier, url='', data=DetailCmdString)
        else:
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        ValueStateValues = {
            '1': 'On (1)',
            '2': 'On (2)',
            '0': 'Off',
        }

        DetailCmdString = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url='', data=DetailCmdString)
        if res:
            try:
                match_grp = self.Detail.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('Detail', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Detail: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Far', 'Near', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Far':
                focus_spd = 50 + SpeedConstraints['Value']
            elif value == 'Near':
                focus_spd = 50 - SpeedConstraints['Value']
            else:
                focus_spd = 50
            FocusCmdString = 'cmd=%23F{:02d}&res=1'.format(focus_spd)
            self.__SetHelper('Focus', value, qualifier, url='', data=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':   '1',
            'Manual': '0',
        }

        if value in ValueStateValues:
            FocusModeCmdString = 'cmd=%23D1{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('FocusMode', value, qualifier, url='', data=FocusModeCmdString)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Auto',
            '0': 'Manual',
        }

        FocusModeCmdString = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('FocusMode', value, qualifier, url='', data=FocusModeCmdString)
        if res:
            try:
                match_grp = self.FocusMode.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('FocusMode', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            IrisCmdString = 'cmd=%23I{:02d}&res=1'.format(value)
            self.__SetHelper('Iris', value, qualifier, url='', data=IrisCmdString)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = 'cmd=%23I&res=1'
        res = self.__UpdateHelper('Iris', value, qualifier, url='', data=IrisCmdString)
        if res:
            try:
                match_grp = self.Iris.search(res)
                if match_grp:
                    value = int(match_grp.group(1))
                    self.WriteStatus('Iris', value, qualifier)
                else:
                    raise KeyError
            except (ValueError, IndexError):
                self.Error(['Iris: Invalid/unexpected response'])

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':   '1',
            'Manual': '0',
        }

        if value in ValueStateValues:
            IrisModeCmdString = 'cmd=%23D3{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('IrisMode', value, qualifier, url='', data=IrisModeCmdString)
        else:
            self.Discard('Invalid Command for SetIrisMode')

    def UpdateIrisMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Auto',
            '0': 'Manual',
        }

        IrisModeCmdString = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('IrisMode', value, qualifier, url='', data=IrisModeCmdString)
        if res:
            try:
                match_grp = self.IrisMode.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('IrisMode', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Iris Mode: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Left':
                PanTiltCmdString = 'cmd=%23P{:02d}&res=1'.format(50 - SpeedConstraints['Value'])
            elif value == 'Right':
                PanTiltCmdString = 'cmd=%23P{:02d}&res=1'.format(50 + SpeedConstraints['Value'])
            elif value == 'Up':
                PanTiltCmdString = 'cmd=%23T{:02d}&res=1'.format(50 + SpeedConstraints['Value'])
            elif value == 'Down':
                PanTiltCmdString = 'cmd=%23T{:02d}&res=1'.format(50 - SpeedConstraints['Value'])
            else:
                PanTiltCmdString = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url='', data=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            PowerCmdString = 'cmd=%23O{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url='', data=PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        PowerCmdString = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url='', data=PowerCmdString)
        if res:
            try:
                match_grp = self.Power.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('Power', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save':   'M',
            'Recall': 'R',
            'Delete': 'C',
        }

        ValueConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(value) if value.isdigit() else -1,
        }

        action_type = qualifier['Type']
        if self.__constraint_checker(ValueConstraints) and action_type in TypeStates:
            PresetCmdString = 'cmd=%23{}{:02d}&res=1'.format(TypeStates[action_type], ValueConstraints['Value'] - 1)
            self.__SetHelper('Preset', value, qualifier, url='', data=PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        PresetRecallStatusCmdString = 'cmd=%23S&res=1'
        res = self.__UpdateHelper('PresetRecallStatus', value, qualifier, url='', data=PresetRecallStatusCmdString)
        if res:
            try:
                match_grp = self.PresetRecallStatus.search(res)
                if match_grp:
                    value = int(match_grp.group(1)) + 1
                    self.WriteStatus('PresetRecallStatus', value, qualifier)
                else:
                    raise ValueError
            except (ValueError, IndexError):
                self.Error(['Preset Recall Status: Invalid/unexpected response'])

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url='', data=ResetPanTiltPositionCmdString)

    def SetResetZoom(self, value, qualifier):

        ResetZoomCmdString = 'cmd=%23AXZ555&res=1'
        self.__SetHelper('ResetZoom', value, qualifier, url='', data=ResetZoomCmdString)

    def SetSceneFileControl(self, value, qualifier):

        ValueStateValues = {
            'Scene 1': '1',
            'Scene 2': '2',
            'Scene 3': '3',
            'Scene 4': '4',
        }

        if value in ValueStateValues:
            SceneFileControlCmdString = 'cmd=XSF:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('SceneFileControl', value, qualifier, url='', data=SceneFileControlCmdString)
        else:
            self.Discard('Invalid Command for SetSceneFileControl')

    def UpdateSceneFileControl(self, value, qualifier):

        ValueStateValues = {
            '0': 'Scene 1',
            '1': 'Scene 2',
            '2': 'Scene 3',
            '3': 'Scene 4',
        }

        SceneFileControlCmdString = 'cmd=QSF&res=1'
        res = self.__UpdateHelper('SceneFileControl', value, qualifier, url='', data=SceneFileControlCmdString)
        if res:
            try:
                match_grp = self.SceneFileControl.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('SceneFileControl', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Scene File Control: Invalid/unexpected response'])

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            TallyCmdString = 'cmd=%23DA{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Tally', value, qualifier, url='', data=TallyCmdString)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        TallyCmdString = 'cmd=%23DA&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url='', data=TallyCmdString)
        if res:
            try:
                match_grp = self.Tally.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('Tally', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Tally: Invalid/unexpected response'])

    def SetTallyEnable(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues:
            TallyEnableCmdString = 'cmd=%23TAE{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('TallyEnable', value, qualifier, url='', data=TallyEnableCmdString)
        else:
            self.Discard('Invalid Command for SetTallyEnable')

    def UpdateTallyEnable(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        TallyEnableCmdString = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('TallyEnable', value, qualifier, url='', data=TallyEnableCmdString)
        if res:
            try:
                match_grp = self.TallyEnable.search(res)
                if match_grp:
                    value = ValueStateValues[match_grp.group(1)]
                    self.WriteStatus('TallyEnable', value, qualifier)
                else:
                    raise KeyError
            except (KeyError, IndexError):
                self.Error(['Tally Enable: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 49,
            'Value': qualifier['Speed'],
        }

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if value in ValueStateValues and self.__constraint_checker(SpeedConstraints):
            if value == 'Tele':
                zoom_spd = 50 + SpeedConstraints['Value']
            elif value == 'Wide':
                zoom_spd = 50 - SpeedConstraints['Value']
            else:
                zoom_spd = 50
            ZoomCmdString = 'cmd=%23Z{:02d}&res=1'.format(zoom_spd)
            self.__SetHelper('Zoom', value, qualifier, url='', data=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        DEVICE_ERROR_CODES = {
            'ER1': 'The Command is not supported by Camera.',
            'ER2': 'Camera is in Standby (Power Off) or in busy status.',
            'ER3': 'Data is out of range.',
        }

        if res[0:3].upper() in DEVICE_ERROR_CODES:
            self.Error(['Command: {}, Device Error: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[res[0:3].upper()])])
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        if command in ['ColorBar', 'Detail', 'SceneFileControl']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)

        my_request = urllib.request.Request(url)

        try:
            res = urllib.request.urlopen(my_request, context=self._context, timeout=10)
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

        if command in ['ColorBar', 'Detail', 'SceneFileControl']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)

        my_request = urllib.request.Request(url)

        try:
            res = urllib.request.urlopen(my_request, context=self._context, timeout=10)
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
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='Off'):
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