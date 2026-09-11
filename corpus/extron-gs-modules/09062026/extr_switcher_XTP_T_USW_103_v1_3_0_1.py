from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': { 'Status': {}},
            'AudioInputFormat': { 'Status': {}}, 
            'AutoImage': { 'Status': {}}, 
            'AutoSwitchMode': { 'Status': {}}, 
            'BlackSignal': { 'Status': {}}, 
            'BlackSignalResolution': { 'Status': {}}, 
            'ColorBar': { 'Status': {}}, 
            'ExecutiveMode': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HorizontalShift': { 'Status': {}}, 
            'Input': { 'Status': {}}, 
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}}, 
            'PixelPhase': { 'Status': {}},
            'PresetRecall': { 'Status': {}}, 
            'PresetSave': { 'Status': {}},  
            'VerticalShift': { 'Status': {}}, 
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aud([-+]\d{2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'AfmtI([0-2])\r\n'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'AfmtB([01])\r\n'), self.__MatchBlackSignal, None)
            self.AddMatchString(re.compile(b'AfmtA([246])\r\n'), self.__MatchBlackSignalResolution, None)
            self.AddMatchString(re.compile(b'Tst0([0135])\r\n'), self.__MatchColorBar, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE([12])\*([01])'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'Hctr(\d+)\r\n'), self.__MatchHorizontalShift, None)
            self.AddMatchString(re.compile(b'In([123])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Frq([01])([01])([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Phas(\d{3})\r\n'), self.__MatchPixelPhase, None)
            self.AddMatchString(re.compile(b'Vctr(\d+)\r\n'), self.__MatchVerticalShift, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                AudioGainAttenuationCmdString = str(abs(value)) + 'g'
            else:
                AudioGainAttenuationCmdString = str(abs(value)) + 'G'
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        AudioGainAttenuationCmdString = 'G'
        self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AudioGainAttenuation', value, None)

    def SetAudioInputFormat(self, value, qualifier):

        AudioInputFormatState = {
            'Auto'      : '\x1BI0AFMT\r',
            'Analog'    : '\x1BI2AFMT\r',
            'Digital'   : '\x1BI1AFMT\r',
            }

        AudioInputFormatCmdString = AudioInputFormatState[value]
        self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        AudioInputFormatCmdString = 'wIAFMT\r'
        self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, tag):

        AudioInputFormatState = {
            '0' : 'Auto',
            '1' : 'Digital',
            '2' : 'Analog',
            }

        value = AudioInputFormatState[match.group(1).decode()]
        self.WriteStatus('AudioInputFormat', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '1A'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeState = {
            'Off'                   : '\x1B0AUSW\r',
            'Highest Active Input'  : '\x1B1AUSW\r',
            'Lowest Active Input'   : '\x1B2AUSW\r',
            }
        
        AutoSwitchModeCmdString = AutoSwitchModeState[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = '\x1BAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeState = {
            '0' : 'Off',
            '1' : 'Highest Active Input',
            '2' : 'Lowest Active Input',
            }

        value = AutoSwitchModeState[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetBlackSignal(self, value, qualifier):

        BlackSignalState = {
            'Enable'    : '\x1BB1AFMT\r',
            'Disable'   : '\x1BB0AFMT\r',
            }

        BlackSignalCmdString = BlackSignalState[value]
        self.__SetHelper('BlackSignal', BlackSignalCmdString, value, qualifier)

    def UpdateBlackSignal(self, value, qualifier):

        BlackSignalCmdString = '\x1BBAFMT\r'
        self.__UpdateHelper('BlackSignal', BlackSignalCmdString, value, qualifier)

    def __MatchBlackSignal(self, match, tag):

        BlackSignalState = {
            '1' : 'Enable',
            '0' : 'Disable'
            }

        value = BlackSignalState[match.group(1).decode()]
        self.WriteStatus('BlackSignal', value, None)

    def SetBlackSignalResolution(self, value, qualifier):

        BlackSignalResolutionState = {
            '720p @ 50Hz'   : '\x1BA2AFMT\r',
            '720p @ 60Hz'   : '\x1BA4AFMT\r',
            '1080p @ 60Hz'  : '\x1BA6AFMT\r',
            }

        BlackSignalResolutionCmdString = BlackSignalResolutionState[value]
        self.__SetHelper('BlackSignalResolution', BlackSignalResolutionCmdString, value, qualifier)

    def UpdateBlackSignalResolution(self, value, qualifier):

        BlackSignalResolutionCmdString = '\x1BAAFMT\r'
        self.__UpdateHelper('BlackSignalResolution', BlackSignalResolutionCmdString, value, qualifier)

    def __MatchBlackSignalResolution(self, match, tag):

        BlackSignalResolutionState = {
            '2' : '720p @ 50Hz',
            '4' : '720p @ 60Hz',
            '6' : '1080p @ 60Hz',
            }

        value = BlackSignalResolutionState[match.group(1).decode()]
        self.WriteStatus('BlackSignalResolution', value, None)

    def SetColorBar(self, value, qualifier):

        ColorBarState = {
            'Disable'       : '0J',
            '720p @ 50Hz'   : '1J',
            '720p @ 60Hz'   : '3J',
            '1080p @ 60Hz'  : '5J',
            }

        ColorBarCmdString = ColorBarState[value]
        self.__SetHelper('ColorBar', ColorBarCmdString, value, qualifier)

    def UpdateColorBar(self, value, qualifier):

        ColorBarCmdString = 'J'
        self.__UpdateHelper('ColorBar', ColorBarCmdString, value, qualifier)

    def __MatchColorBar(self, match, tag):

        ColorBarState = {
            '0' : 'Disable',
            '1' : '720p @ 50Hz',
            '3' : '720p @ 60Hz',
            '5' : '1080p @ 60Hz',
            }

        value = ColorBarState[match.group(1).decode()]
        self.WriteStatus('ColorBar', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On'    : '1X',
            'Off'   : '0X',
            }

        ExecutiveModeCmdString = ExecutiveModeState[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):


        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeState = {
            '1' : 'On',
            '0' : 'Off'
            }


        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        Input = {
            '2': '1',
            '3': '2'}[qualifier['Input']]

        HDCPInputAuthorizationState = {
            'On'    : '1',
            'Off'   : '0'
            }

        HDCPInputAuthorizationCmdString = '\x1BE{0}*{1}HDCP\r'.format(Input, HDCPInputAuthorizationState[value])
        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        Input = {
            '2': '1',
            '3': '2'}[qualifier['Input']]

        HDCPInputAuthorizationCmdString = '\x1BE{0}HDCP\r'.format(Input)
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        InputState = {
            '1': '2',
            '2': '3'
            }

        HDCPInputAuthorizationState = {
            '1' : 'On',
            '0' : 'Off'
            }

        value = HDCPInputAuthorizationState[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input' : InputState[match.group(1).decode()]})

    def SetHorizontalShift(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            HorizontalShiftCmdString = '\x1B' + str(value+32640) + 'HCTR\r'
            self.__SetHelper('HorizontalShift', HorizontalShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalShift')

    def UpdateHorizontalShift(self, value, qualifier):

        HorizontalShiftCmdString = '\x1BHCTR\r'
        self.__UpdateHelper('HorizontalShift', HorizontalShiftCmdString, value, qualifier)

    def __MatchHorizontalShift(self, match, tag):

        value = int(match.group(1).decode()) - 32640
        self.WriteStatus('HorizontalShift', value, None)

    def SetInput(self, value, qualifier):

        if 1 <= int(value) <= 3:
            InputCmdString = '{0}!'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatusState = {
            '1' : 'Active',
            '0' : 'Not Active',
            }

        self.WriteStatus('InputSignalStatus', InputSignalStatusState[match.group(1).decode()], {'Input' : '1'})
        self.WriteStatus('InputSignalStatus', InputSignalStatusState[match.group(2).decode()], {'Input' : '2'})
        self.WriteStatus('InputSignalStatus', InputSignalStatusState[match.group(3).decode()], {'Input' : '3'})

    def SetPixelPhase(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255  # max range is correct even though listed otherwise in XTP software (PD says software will be updated from 63 to 255)
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PixelPhaseCmdString = '\x1B{0}PHAS\r'.format(value)
            self.__SetHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPixelPhase')

    def UpdatePixelPhase(self, value, qualifier):

        PixelPhaseCmdString = '\x1BPHAS\r'
        self.__UpdateHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)

    def __MatchPixelPhase(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('PixelPhase', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 8:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 8:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVerticalShift(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VerticalShiftCmdString = '\x1B' + str(value+32640) + 'VCTR\r'
            self.__SetHelper('VerticalShift', VerticalShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalShift')

    def UpdateVerticalShift(self, value, qualifier):

        VerticalShiftCmdString = '\x1BVCTR\r'
        self.__UpdateHelper('VerticalShift', VerticalShiftCmdString, value, qualifier)

    def __MatchVerticalShift(self, match, tag):

        value = int(match.group(1).decode()) - 32640
        self.WriteStatus('VerticalShift', value, None)

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

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input number',
            '06' : 'Invalid switch attempt in this mode',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type'
            }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: '+ match.group(0).decode()]) 

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
            print(command, 'does not exist in the module')

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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
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