from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
import re


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'AutoFocus': {'Status': {}},
            'ExtenderAFControl': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'Tally': {'Status': {}},
            'TallyEnable': {'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'd3([01])'), self.__MatchIrisMode, None)
            self.AddMatchString(compile(b'd1([01])'), self.__MatchExtenderAFControl, None)
            self.AddMatchString(compile(b'iC([0-9]{2})'), self.__MatchIris, None)
            self.AddMatchString(compile(b'p([01fn23])'), self.__MatchPower, None)
            self.AddMatchString(compile(b'dA([01])'), self.__MatchTally, None)
            self.AddMatchString(compile(b'tAE([01])'), self.__MatchTallyEnable, None)
            self.AddMatchString(compile(b'eR([1-3])|\x02ER([1-3])\x03'), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        FocusValues = {
            'On': '1',
            'Off': '0'
        }

        AutoFocusCmdString = '\x02OAF:{0}\x03'.format(FocusValues[value])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetExtenderAFControl(self, value, qualifier):

        ExtenderAFControlStateValues = {
            'Off': '0',
            'On': '1'
        }

        ExtenderAFControlCmdString = '#D1{0}\r'.format(ExtenderAFControlStateValues[value])
        self.__SetHelper('ExtenderAFControl', ExtenderAFControlCmdString, value, qualifier)

    def UpdateExtenderAFControl(self, value, qualifier):

        ExtenderAFControlCmdString = '#D1\r'
        self.__UpdateHelper('ExtenderAFControl', ExtenderAFControlCmdString, value, qualifier)

    def __MatchExtenderAFControl(self, match, qualifier):

        ExtenderAFControlStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        value = ExtenderAFControlStateNames[match.group(1).decode()]
        self.WriteStatus('ExtenderAFControl', value, None)

    def SetFocus(self, value, qualifier):

        tempFocusSpeed = int(qualifier['Speed'])

        if 1 <= tempFocusSpeed <= 49:
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

        IrisConstraints = {
            'Min': 1,
            'Max': 99
        }

        if IrisConstraints['Min'] <= value <= IrisConstraints['Max']:
            IrisCmdString = '#I{0}\r'.format(str(value).zfill(2))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = '#I\r'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, qualifier):

        value = int(match.group(1).decode())
        self.WriteStatus('Iris', value, None)

    def SetIrisMode(self, value, qualifier):

        IrisModeStateValues = {
            'Manual': '0',
            'Auto': '1'
        }

        IrisModeCmdString = '#D3{0}\r'.format(IrisModeStateValues[value])
        self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def UpdateIrisMode(self, value, qualifier):

        IrisModeCmdString = '#D3\r'
        self.__UpdateHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def __MatchIrisMode(self, match, qualifier):

        IrisModeStateNames = {
            '0': 'Manual',
            '1': 'Auto'
        }
        value = IrisModeStateNames[match.group(1).decode()]
        self.WriteStatus('IrisMode', value, None)

    def SetPan(self, value, qualifier):

        tempPanSpeed = int(qualifier['Speed'])

        if 1 <= tempPanSpeed <= 49:
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

        PowerStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '#O{0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '#O\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',
            'f': 'Off',
            'n': 'On',
            '2': 'On',
            '3': 'Starting'
        }

        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        SaveRecall = qualifier['Type']

        SaveRecallValues = {
            'Save': 'M',
            'Recall': 'R'
        }

        PresetConstraints = {
            'Min': 1,
            'Max': 50
        }

        if PresetConstraints['Min'] <= int(value) <= PresetConstraints['Max']:
            PresetCmdString = '#{0}{1:02d}\r'.format(SaveRecallValues[SaveRecall], (int(value) - 1))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTally(self, value, qualifier):

        TallyStateValues = {
            'Off': '0',
            'On': '1'
        }

        TallyCmdString = '#DA{0}\r'.format(TallyStateValues[value])
        self.__SetHelper('Tally', TallyCmdString, value, qualifier)

    def UpdateTally(self, value, qualifier):

        TallyCmdString = '#DA\r'
        self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)

    def __MatchTally(self, match, qualifier):

        TallyStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        value = TallyStateNames[match.group(1).decode()]
        self.WriteStatus('Tally', value, None)

    def SetTallyEnable(self, value, qualifier):

        TallyEnableStateValues = {
            'Off': '0',
            'On': '1'
        }

        TallyEnableCmdString = '#TAE{0}\r'.format(TallyEnableStateValues[value])
        self.__SetHelper('TallyEnable', TallyEnableCmdString, value, qualifier)

    def UpdateTallyEnable(self, value, qualifier):

        TallyEnableCmdString = '#TAE\r'
        self.__UpdateHelper('TallyEnable', TallyEnableCmdString, value, qualifier)

    def __MatchTallyEnable(self, match, qualifier):

        TallyEnableStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        value = TallyEnableStateNames[match.group(1).decode()]
        self.WriteStatus('TallyEnable', value, None)

    def SetTilt(self, value, qualifier):

        tempTiltSpeed = int(qualifier['Speed'])

        if 1 <= tempTiltSpeed <= 49:
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

        tempZoomSpeed = int(qualifier['Speed'])

        if 1 <= tempZoomSpeed <= 49:
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
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
        Command = self.Commands[command]
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class DeviceEthernetClass:

    def __init__(self, ipAddress, port, deviceUsername='Username', devicePassword=None):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'ColorBar': {'Status': {}},
            'Detail': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Installation': {'Status': {}},
            'IrisPosition': {'Status': {}},
            'PanTilt': {'Parameters': ['Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'PresetRecallStatus': {'Status': {}},
            'ResetPanTiltPosition': {'Status': {}},
            'ResetZoom': {'Status': {}},
            'Tally': {'Status': {}},
            'TallyInput': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.Detail = compile('ODT:([012])')  # not supported for HE2 models
        self.ColorBar = compile('OBR:([01])')
        self.AutoIris = compile('d3([01])')
        self.AutoFocus = compile('d1([01])')  # not supported for HE2 models
        self.Power = compile('p([01])')
        self.Preset = compile('s([0-99]{2})')
        self.TallyInput = compile('tAE([01])')
        self.Tally = compile('dA([01])')
        self.Err = compile('ER([123])')

    def SetAutoFocus(self, value, qualifier):

        FocusValues = {
            'Auto': '1',
            'Manual': '0'
        }

        data = 'cmd=%23D1{0}&res=1'.format(FocusValues[value])
        self.__SetHelper('AutoFocus', value, qualifier, url='', data=data)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusStateNames = {
            '0': 'Manual',
            '1': 'Auto'
        }
        data = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.AutoFocus.search(res)
                if mGroup is not None:
                    AutoFocus50Value = mGroup.group(1)
                else:
                    AutoFocus50Value = ''
                self.WriteStatus('AutoFocus', AutoFocusStateNames[AutoFocus50Value], None)
            except KeyError:
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoIris(self, value, qualifier):

        AutoIrisValues = {
            'On': '1',
            'Off': '0'
        }

        data = 'cmd=%23D3{0}&res=1'.format(AutoIrisValues[value])
        self.__SetHelper('AutoIris', value, qualifier, url='', data=data)

    def UpdateAutoIris(self, value, qualifier):

        AutoIrisStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        data = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('AutoIris', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.AutoIris.search(res)
                if mGroup is not None:
                    AutoIrisValue = mGroup.group(1)
                else:
                    AutoIrisValue = ''
                self.WriteStatus('AutoIris', AutoIrisStateNames[AutoIrisValue], None)
            except KeyError:
                self.Error(['Auto Iris: Invalid/unexpected response'])

    def SetColorBar(self, value, qualifier):

        ColorBarValues = {
            'On': '1',
            'Off': '0'
        }
        data = 'cmd=DCB:{0}&res=1'.format(ColorBarValues[value])
        self.__SetHelper('ColorBar', value, qualifier, url='', data=data)

    def UpdateColorBar(self, value, qualifier):

        ColorBarStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        data = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.ColorBar.search(res)
                if mGroup is not None:
                    ColorBarValue = mGroup.group(1)
                else:
                    ColorBarValue = ''
                self.WriteStatus('ColorBar', ColorBarStateNames[ColorBarValue], None)
            except KeyError:
                self.Error(['Color Bar: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        DetailValues = {
            'On': '1',
            'Off': '0'
        }

        data = 'cmd=ODT:{0}&res=1'.format(DetailValues[value])
        self.__SetHelper('Detail', value, qualifier, url='', data=data)

    def UpdateDetail(self, value, qualifier):

        DetailStateNames = {
            '0': 'Off',
            '1': 'On',
            '2': 'On'
        }

        data = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Detail.search(res)
                if mGroup is not None:
                    DetailValue = mGroup.group(1)
                else:
                    DetailValue = ''

                self.WriteStatus('Detail', DetailStateNames[DetailValue], None)
            except KeyError:
                self.Error(['Set Detail: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        FocusConstraints = {
            'Min': 1,
            'Max': 49
        }

        Speed = qualifier['Speed']
        if Speed < FocusConstraints['Min'] or Speed > FocusConstraints['Max']:
            self.Discard('Invalid Command for SetFocus')
        else:
            if value == 'Near':
                data = 'cmd=%23F{0}&res=1'.format(str(50 - Speed).zfill(2))
            elif value == 'Far':
                data = 'cmd=%23F{0}&res=1'.format(str(50 + Speed).zfill(2))
            else:
                data = 'cmd=%23F50&res=1'
            self.__SetHelper('Focus', value, qualifier, url='', data=data)

    def SetInstallation(self, value, qualifier):

        InstallationValues = {
            'Desktop': '0',
            'Hanging': '1'
        }

        data = 'cmd=%23INS{0}&res=1'.format(InstallationValues[value])
        self.__SetHelper('Installation', value, qualifier, url='', data=data)

    def SetIrisPosition(self, value, qualifier):

        IrisConstraints = {
            'Min': 0,
            'Max': 20
        }
        if value < IrisConstraints['Min'] or value > IrisConstraints['Max']:
            self.Discard('Invalid Command for SetIrisPosition')
        else:
            hexvalue = hex(1365 + value * 136)
            data = 'cmd=%23AXI{0}&res=1'.format(hexvalue[2:].upper())
            self.__SetHelper('IrisPosition', value, qualifier, url='', data=data)

    def SetPanTilt(self, value, qualifier):

        PanTiltConstraints = {
            'Min': 1,
            'Max': 49
        }
        Speed = qualifier['Speed']

        if PanTiltConstraints['Min'] <= Speed <= PanTiltConstraints['Max']:
            if value == 'Left':
                data = 'cmd=%23P{0}&res=1'.format(str(50 - Speed).zfill(2))
            elif value == 'Right':
                data = 'cmd=%23P{0}&res=1'.format(str(50 + Speed).zfill(2))
            elif value == 'Up':
                data = 'cmd=%23T{0}&res=1'.format(str(50 + Speed).zfill(2))
            elif value == 'Down':
                data = 'cmd=%23T{0}&res=1'.format(str(50 - Speed).zfill(2))
            else:
                data = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        PowerValues = {
            'On': '1',
            'Standby': '0',
        }

        data = 'cmd=%23O{0}&res=1'.format(PowerValues[value])
        self.__SetHelper('Power', value, qualifier, url='', data=data)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '0': 'Standby',
            '1': 'On'
        }

        data = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Power.search(res)
                if mGroup is not None:
                    PowerValue = mGroup.group(1)
                else:
                    PowerValue = ''
                self.WriteStatus('Power', PowerStateNames[PowerValue], None)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        PresetConstraints = {
            'Min': 1,
            'Max': 100
        }

        SaveRecallValues = {
            'Save': 'M',
            'Recall': 'R'
        }

        SaveRecall = qualifier['Type']
        if PresetConstraints['Min'] <= int(value) <= PresetConstraints['Max']:
            preset = int(value) - 1
            data = 'cmd=%23{0}{1}&res=1'.format(SaveRecallValues[SaveRecall], str(preset).zfill(2))
            self.__SetHelper('Preset', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        data = 'cmd=%23S&res=1'
        res = self.__UpdateHelper('PresetRecallStatus', value, qualifier, url='', data=data)
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
        data = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url='', data=data)

    def SetResetZoom(self, value, qualifier):
        data = 'cmd=%23AXZ555&res=1'
        self.__SetHelper('ResetZoom', value, qualifier, url='', data=data)

    def SetTallyInput(self, value, qualifier):

        TallyInputValues = {
            'Disable': '0',
            'Enable': '1'
        }

        data = 'cmd=%23TAE{0}&res=1'.format(TallyInputValues[value])
        self.__SetHelper('TallyInput', value, qualifier, url='', data=data)

    def UpdateTallyInput(self, value, qualifier):

        TallyInputStateNames = {
            '0': 'Disable',
            '1': 'Enable'
        }
        data = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('TallyInput', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.TallyInput.search(res)
                if mGroup is not None:
                    TallyInputValue = mGroup.group(1)
                else:
                    TallyInputValue = ''
                self.WriteStatus('TallyInput', TallyInputStateNames[TallyInputValue], None)
            except KeyError:
                self.Error(['Tally Input: Invalid/unexpected response'])

    def SetTally(self, value, qualifier):

        TallyValues = {
            'On': '1',
            'Off': '0'
        }

        data = 'cmd=%23DA{0}&res=1'.format(TallyValues[value])
        self.__SetHelper('Tally', value, qualifier, url='', data=data)

    def UpdateTally(self, value, qualifier):

        TallyStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        data = 'cmd=%23DA&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Tally.search(res)
                if mGroup is not None:
                    TallyValue = mGroup.group(1)
                else:
                    TallyValue = ''
                self.WriteStatus('Tally', TallyStateNames[TallyValue], None)
            except KeyError:
                self.Error(['Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min': 1,
            'Max': 49
        }

        Speed = qualifier['Speed']
        if ZoomConstraints['Min'] <= Speed <= ZoomConstraints['Max']:
            if value == 'Wide':
                data = 'cmd=%23Z{0}&res=1'.format(str(50 - Speed).zfill(2))
            elif value == 'Tele':
                data = 'cmd=%23Z{0}&res=1'.format(str(50 + Speed).zfill(2))
            else:
                data = 'cmd=%23Z50&res=1'
            self.__SetHelper('Zoom', value, qualifier, url='', data=data)
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

        if command in ['ColorBar', 'Detail', 'MainPinPMode', 'PinP', 'PinPDisplayPosition']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)
        my_request = urllib.request.Request(url)

        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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

        if command in ['ColorBar', 'Detail', 'MainPinPMode', 'PinP', 'PinPDisplayPosition']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)
        my_request = urllib.request.Request(url)

        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
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
        Command = self.Commands[command]
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


class HTTPClass(DeviceEthernetClass):

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceEthernetClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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