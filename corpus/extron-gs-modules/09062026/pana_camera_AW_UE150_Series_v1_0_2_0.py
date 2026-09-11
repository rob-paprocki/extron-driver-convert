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
            'AutoFocus': { 'Status': {}},
            'ExtenderAFControl': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'IrisMode': { 'Status': {}},
            'Pan': {'Parameters':['Pan Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'Tally': { 'Status': {}},
            'TallyEnable': { 'Status': {}},
            'Tilt': {'Parameters':['Tilt Speed'], 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'd1([01])\r'), self.__MatchExtenderAFControl, None)
            self.AddMatchString(re.compile(b'iC([0-9]{2})\r'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'd3([01])\r'), self.__MatchIrisMode, None)
            self.AddMatchString(re.compile(b'p([0-3fn])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'dA([01])\r'), self.__MatchTally, None)
            self.AddMatchString(re.compile(b'tAE([01])\r'), self.__MatchTallyEnable, None)
            self.AddMatchString(re.compile(b'eR([1-3])', re.I), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0',
            'One Touch Focus' : '1'
        }

        if value in ValueStateValues:
            if value == 'One Touch Focus':
                AutoFocusCmdString = '\x02OSE:69:1\x03'
            else:
                AutoFocusCmdString = '\x02OAF:{0}\x03'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def SetExtenderAFControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            ExtenderAFControlCmdString = '#D1{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('ExtenderAFControl', ExtenderAFControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExtenderAFControl')

    def UpdateExtenderAFControl(self, value, qualifier):

        ExtenderAFControlCmdString = '#D1\r'
        self.__UpdateHelper('ExtenderAFControl', ExtenderAFControlCmdString, value, qualifier)

    def __MatchExtenderAFControl(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExtenderAFControl', value, None)

    def SetFocus(self, value, qualifier):

        tempFocusSpeed = int(qualifier['Focus Speed'])
        if 1 <= tempFocusSpeed <= 49 and value in ['Stop', 'Far', 'Near']:
            if value == 'Stop':
                focusSpeed = 50
            elif value == 'Far':
                focusSpeed = 50 + tempFocusSpeed
            elif value == 'Near':
                focusSpeed = 50 - tempFocusSpeed
            FocusCmdString = '#F{0}\r'.format(str(focusSpeed).zfill(2))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        if 1 <= value <= 99:
            IrisCmdString = '#I{0}\r'.format(str(value).zfill(2))
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
            'Manual' : '0',
            'Auto'   : '1'
        }

        if value in ValueStateValues:
            IrisModeCmdString = '#D3{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIrisMode')

    def UpdateIrisMode(self, value, qualifier):

        IrisModeCmdString = '#D3\r'
        self.__UpdateHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def __MatchIrisMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Manual',
            '1' : 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IrisMode', value, None)

    def SetPan(self, value, qualifier):

        tempPanSpeed = int(qualifier['Pan Speed'])
        if 1 <= tempPanSpeed <= 49 and value in ['Stop', 'Right', 'Left']:
            if value == 'Stop':
                panSpeed = 50
            elif value == 'Right':
                panSpeed = 50 + tempPanSpeed
            elif value == 'Left':
                panSpeed = 50 - tempPanSpeed
            PanCmdString = '#P{0}\r'.format(str(panSpeed).zfill(2))
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0',
        }

        if value in ValueStateValues:
            PowerCmdString = '#O{0}\r'.format(ValueStateValues[value])
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
            'f': 'Off',
            'n': 'On',
            '2': 'On',
            '3': 'Starting'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save'   : 'M',
            'Recall' : 'R',
            'Delete' : 'C'
        }

        if 1 <= int(value) <= 100 and qualifier['Type'] in TypeStates:
            PresetCmdString = '#{0}{1:02d}\r'.format(TypeStates[qualifier['Type']], (int(value) - 1))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            TallyCmdString = '#DA{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        TallyCmdString = '#DA\r'
        self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)

    def __MatchTally(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Tally', value, None)

    def SetTallyEnable(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            TallyEnableCmdString = '#TAE{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('TallyEnable', TallyEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTallyEnable')

    def UpdateTallyEnable(self, value, qualifier):

        TallyEnableCmdString = '#TAE\r'
        self.__UpdateHelper('TallyEnable', TallyEnableCmdString, value, qualifier)

    def __MatchTallyEnable(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TallyEnable', value, None)

    def SetTilt(self, value, qualifier):

        tempTiltSpeed = int(qualifier['Tilt Speed'])
        if 1 <= tempTiltSpeed <= 49 and value in ['Stop', 'Up', 'Down']:
            if value == 'Stop':
                tiltSpeed = 50
            elif value == 'Up':
                tiltSpeed = 50 + tempTiltSpeed
            elif value == 'Down':
                tiltSpeed = 50 - tempTiltSpeed
            TiltCmdString = '#T{0}\r'.format(str(tiltSpeed).zfill(2))
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        tempZoomSpeed = int(qualifier['Zoom Speed'])

        if 1 <= tempZoomSpeed <= 49 and value in ['Stop', 'Tele', 'Wide']:
            if value == 'Stop':
                zoomSpeed = 50
            elif value == 'Tele':
                zoomSpeed = 50 + tempZoomSpeed
            elif value == 'Wide':
                zoomSpeed = 50 - tempZoomSpeed
            ZoomCmdString = '#Z{0}\r'.format(str(zoomSpeed).zfill(2))
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
            '1': 'The Command is not supported by CAMERA.',
            '2': 'CAMERA can not process the command for running the other processing.',
            '3': 'Data is out of range.'
        }

        value = match.group(1).decode()
        self.Error([ErrorStateNames[value]])

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

class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

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
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Installation': { 'Status': {}},
            'IrisPosition': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'PresetRecallStatus': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'ResetZoom': { 'Status': {}},
            'SceneFileControl': { 'Status': {}},
            'Tally': { 'Status': {}},
            'TallyInput': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        self.AutoFocus = re.compile('d1([01])')
        self.AutoIris = re.compile('d3([01])')
        self.ColorBar = re.compile('OBR:([01])')
        self.Detail = re.compile('ODT:([012])')
        self.Power = re.compile('p([013])')
        self.Preset = re.compile('s([0-9]{2})')
        self.SceneFileControl = re.compile('OSF:([0-3])')
        self.Tally = re.compile('dA([01])')
        self.TallyInput = re.compile('tAE([01])')
        
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : '1',
            'Manual' : '0',
            'One Touch Focus' : '1'
        }

        if value in ValueStateValues:
            if value == 'One Touch Focus':
                AutoFocusCmdString = 'cmd=OSE:69:1&res=1'
            else:
                AutoFocusCmdString = 'cmd=%23D1{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, url='', data=AutoFocusCmdString)
        else:
            self.Discard('Invalid Command')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Auto',
            '0' : 'Manual'
        }

        AutoFocusCmdString = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, url='', data=AutoFocusCmdString)
        if res:
            try:
                mGroup = self.AutoFocus.search(res)
                if mGroup is not None:
                    AutoFocus50Value = mGroup.group(1)
                else:
                    AutoFocus50Value = ''
                value = ValueStateValues[AutoFocus50Value]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            AutoIrisCmdString = 'cmd=%23D3{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoIris', value, qualifier, url='', data=AutoIrisCmdString)
        else:
            self.Discard('Invalid Command for SetAutoIris')

    def UpdateAutoIris(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        AutoIrisCmdString = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('AutoIris', value, qualifier, url='', data=AutoIrisCmdString)
        if res:
            try:
                mGroup = self.AutoIris.search(res)
                if mGroup is not None:
                    AutoIrisValue = mGroup.group(1)
                else:
                    AutoIrisValue = ''
                value = ValueStateValues[AutoIrisValue]
                self.WriteStatus('AutoIris', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Iris: Invalid/unexpected response'])

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            ColorBarCmdString = 'cmd=DCB:{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', value, qualifier, url='', data=ColorBarCmdString)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        ColorBarCmdString = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url='', data=ColorBarCmdString)
        if res:
            try:
                mGroup = self.ColorBar.search(res)
                if mGroup is not None:
                    ColorBarValue = mGroup.group(1)
                else:
                    ColorBarValue = ''
                value = ValueStateValues[ColorBarValue]
                self.WriteStatus('ColorBar', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color Bar: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            DetailCmdString = 'cmd=ODT:{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Detail', value, qualifier, url='', data=DetailCmdString)
        else:
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        DetailCmdString = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url='', data=DetailCmdString)
        if res:
            try:
                mGroup = self.Detail.search(res)
                if mGroup is not None:
                    DetailValue = mGroup.group(1)
                else:
                    DetailValue = ''
                value = ValueStateValues[DetailValue]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Detail: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        Speed = qualifier['Speed']
        if value in ['Near', 'Far', 'Stop'] and 1 <= Speed <= 49:
            if value == 'Near':
                FocusCmdString = 'cmd=%23F{0}&res=1'.format(str(50-Speed).zfill(2))
            elif value == 'Far':
                FocusCmdString = 'cmd=%23F{0}&res=1'.format(str(50+Speed).zfill(2))
            else:
                FocusCmdString = 'cmd=%23F50&res=1'
            self.__SetHelper('Focus', value, qualifier, url='', data=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetInstallation(self, value, qualifier):

        ValueStateValues = {
            'Desktop' : '0',
            'Hanging' : '1'
        }

        if value in ValueStateValues:
            InstallationCmdString = 'cmd=%23INS{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Installation', value, qualifier, url='', data=InstallationCmdString)
        else:
            self.Discard('Invalid Command for SetInstallation')

    def SetIrisPosition(self, value, qualifier):

        if 0 <= value <= 20:
            hexvalue = hex(1365 + value * 136)
            IrisPositionCmdString = 'cmd=%23AXI{0}&res=1'.format(hexvalue[2:].upper())
            self.__SetHelper('IrisPosition', value, qualifier, url='', data=IrisPositionCmdString)
        else:
            self.Discard('Invalid Command for SetIrisPosition')

    def SetPanTilt(self, value, qualifier):

        Speed = qualifier['Speed']
        if value in ['Left', 'Right', 'Up', 'Down', 'Stop'] and 1 <= Speed <= 49:
            if value == 'Left':
                PanTiltCmdString = 'cmd=%23P{0}&res=1'.format(str(50 - Speed).zfill(2))
            elif value == 'Right':
                PanTiltCmdString = 'cmd=%23P{0}&res=1'.format(str(50 + Speed).zfill(2))
            elif value == 'Up':
                PanTiltCmdString = 'cmd=%23T{0}&res=1'.format(str(50 + Speed).zfill(2))
            elif value == 'Down':
                PanTiltCmdString = 'cmd=%23T{0}&res=1'.format(str(50 - Speed).zfill(2))
            else:
                PanTiltCmdString = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url='', data=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'      : '1',
            'Standby' : '0',
        }

        if value in ValueStateValues:
            PowerCmdString = 'cmd=%23O{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url='', data=PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Standby',
            '3' : 'Starting'
        }

        PowerCmdString = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url='', data=PowerCmdString)
        if res:
            try:
                mGroup = self.Power.search(res)
                if mGroup is not None:
                    PowerValue = mGroup.group(1)
                else:
                    PowerValue = ''
                value = ValueStateValues[PowerValue]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Save'   : 'M',
            'Recall' : 'R',
            'Delete' : 'C'
        }

        if 1 <= int(value) <= 100 and qualifier['Type'] in TypeStates:
            PresetCmdString = 'cmd=%23{0}{1}&res=1'.format(TypeStates[qualifier['Type']], str(int(value) - 1).zfill(2))
            self.__SetHelper('Preset', value, qualifier, url='', data=PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        PresetRecallStatusCmdString = 'cmd=%23S&res=1'
        res = self.__UpdateHelper('PresetRecallStatus', value, qualifier, url='', data=PresetRecallStatusCmdString)
        if res:
            try:
                mGroup = self.Preset.search(res)
                if mGroup is not None:
                    PresetValue = int(mGroup.group(1)) + 1
                    self.WriteStatus('PresetRecallStatus', PresetValue, qualifier)
                else:
                    return
            except ValueError:
                self.Error(['Preset Recall Status: Invalid/unexpected response'])

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url='', data=ResetPanTiltPositionCmdString)

    def SetResetZoom(self, value, qualifier):

        ResetZoomCmdString = 'cmd=%23AXZ555&res=1'
        self.__SetHelper('ResetZoom', value, qualifier, url='', data=ResetZoomCmdString)

    def SetSceneFileControl(self, value, qualifier):

        ValueStateValues = {
            'Scene 1' : '1',
            'Scene 2' : '2',
            'Scene 3' : '3',
            'Scene 4' : '4',
        }

        if value in ValueStateValues:
            data = 'cmd=XSF:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('SceneFileControl', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetSceneFileControl')

    def UpdateSceneFileControl(self, value, qualifier):

        ValueStateValues = {
            '0': 'Scene 1',
            '1': 'Scene 2',
            '2': 'Scene 3',
            '3': 'Scene 4'
        }

        data = 'cmd=QSF&res=1'
        res = self.__UpdateHelper('SceneFileControl', value, qualifier, url='', data=data)
        if res:
            try:
                search_res = self.SceneFileControl.search(res)
                if search_res:
                    grp_res = search_res.group(1)
                else:
                    grp_res = ''
                value = ValueStateValues[grp_res]
                self.WriteStatus('SceneFileControl', value, qualifier)
            except KeyError:
                self.Error(['Scene File Control: Invalid/unexpected response'])

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            TallyCmdString = 'cmd=%23DA{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Tally', value, qualifier, url='', data=TallyCmdString)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        TallyCmdString = 'cmd=%23DA&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url='', data=TallyCmdString)
        if res:
            try:
                mGroup = self.Tally.search(res)
                if mGroup is not None:
                    TallyValue = mGroup.group(1)
                else:
                    TallyValue = ''
                value = ValueStateValues[TallyValue]
                self.WriteStatus('Tally', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tally: Invalid/unexpected response'])

    def SetTallyInput(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if value in ValueStateValues:
            TallyInputCmdString = 'cmd=%23TAE{0}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('TallyInput', value, qualifier, url='', data=TallyInputCmdString)
        else:
            self.Discard('Invalid Command for SetTallyInput')

    def UpdateTallyInput(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Enable',
            '0' : 'Disable'
        }

        TallyInputCmdString = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('TallyInput', value, qualifier, url='', data=TallyInputCmdString)
        if res:
            try:
                mGroup = self.TallyInput.search(res)
                if mGroup is not None:
                    TallyInputValue = mGroup.group(1)
                else:
                    TallyInputValue = ''
                value = ValueStateValues[TallyInputValue]
                self.WriteStatus('TallyInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tally Input: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        Speed = qualifier['Speed']
        if value in ['Wide', 'Tele', 'Stop'] and 1 <= Speed <= 49:
            if value == 'Wide':
                ZoomCmdString = 'cmd=%23Z{0}&res=1'.format(str(50 - Speed).zfill(2))
            elif value == 'Tele':
                ZoomCmdString = 'cmd=%23Z{0}&res=1'.format(str(50 + Speed).zfill(2))
            else:
                ZoomCmdString = 'cmd=%23Z50&res=1'
            self.__SetHelper('Zoom', value, qualifier, url='', data=ZoomCmdString)
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

        if command in ['ColorBar', 'Detail', 'SceneFileControl']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            if command == 'AutoFocus' and value == 'One Touch Focus':
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

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
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