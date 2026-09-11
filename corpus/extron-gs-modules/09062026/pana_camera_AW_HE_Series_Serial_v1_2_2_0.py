from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
from re import compile, search


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},

            'AutoFocus': {'Status': {}},
            'ExtenderAFControl': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'Pan': {'Parameters': ['Pan Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'Tally': {'Status': {}},
            'TallyEnable': {'Status': {}},
            'Tilt': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'd3(0|1)'), self.__MatchIrisMode, None)
            self.AddMatchString(compile(b'd1(0|1)'), self.__MatchExtenderAFControl, None)
            self.AddMatchString(compile(b'iC([0-9]{2})'), self.__MatchIris, None)
            self.AddMatchString(compile(b'p(0|1|f|n|2|3)'), self.__MatchPower, None)
            self.AddMatchString(compile(b'dA(0|1)'), self.__MatchTally, None)
            self.AddMatchString(compile(b'tAE(0|1)'), self.__MatchTallyEnable, None)
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

        tempFocusSpeed = int(qualifier['Focus Speed'])

        if 1 <= tempFocusSpeed <= 49:
            if value == 'Stop':
                focusSpeed = 50
            elif value == 'Far':
                focusSpeed = 50 + tempFocusSpeed
            elif value == 'Near':
                focusSpeed = 50 - tempFocusSpeed
            FocusCmdString = '#F{0}\r'.format(str(focusSpeed).zfill(2))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):
        IrisConstraints = {
            'Min': 1,
            'Max': 99
            }

        if value < IrisConstraints['Min'] or value > IrisConstraints['Max']:
            print('Invalid Command for SetIris')
        else:
            IrisCmdString = '#I{0}\r'.format(str(value).zfill(2))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier, 1)

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

        tempPanSpeed = int(qualifier['Pan Speed'])

        if 1 <= tempPanSpeed <= 49:
            if value == 'Stop':
                panSpeed = 50
            elif value == 'Right':
                panSpeed = 50 + tempPanSpeed
            elif value == 'Left':
                panSpeed = 50 - tempPanSpeed
            PanCmdString = '#P{0}\r'.format(str(panSpeed).zfill(2))
            self.__SetHelper('Pan', PanCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetPan')

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On': '1',
            'Off': '0'
            }

        PowerCmdString = '#O{0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

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

        if value < PresetConstraints['Min'] or value > PresetConstraints['Max']:
            print('Invalid Command for SetPreset')
        else:
           PresetCmdString = '#{0}{1:02d}\r'.format(SaveRecallValues[SaveRecall], (value - 1))
           self.__SetHelper('Preset', PresetCmdString, value, qualifier, 1)

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

        tempTiltSpeed = int(qualifier['Tilt Speed'])

        if 1 <= tempTiltSpeed <= 49:
            if value == 'Stop':
                tiltSpeed = 50
            elif value == 'Up':
                tiltSpeed = 50 + tempTiltSpeed
            elif value == 'Down':
                tiltSpeed = 50 - tempTiltSpeed
            TiltCmdString = '#T{0}\r'.format(str(tiltSpeed).zfill(2))
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        tempZoomSpeed = int(qualifier['Zoom Speed'])

        if 1 <= tempZoomSpeed <= 49:
            if value == 'Stop':
                zoomSpeed = 50
            elif value == 'Tele':
                zoomSpeed = 50 + tempZoomSpeed
            elif value == 'Wide':
                zoomSpeed = 50 - tempZoomSpeed
            ZoomCmdString = '#Z{0}\r'.format(str(zoomSpeed).zfill(2))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
        print(ErrorStateNames[value])

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()


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