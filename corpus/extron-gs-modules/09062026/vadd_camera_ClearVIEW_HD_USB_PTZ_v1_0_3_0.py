from extronlib.interface import EthernetClientInterface, SerialInterface
import re
from struct import pack, unpack
from extronlib.system import ProgramLog

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Home': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'ResetPanTilt': {'Status': {}},
            'ResetPreset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }

        self.cameraID = 0x81

    @property
    def DeviceID(self):
        return str(self.cameraID - 128)

    @DeviceID.setter
    def DeviceID(self, value):
        if int(value) >= 1 and int(value) <= 7:
            self.cameraID = 0x80 + int(value)
        else:
            print('DeviceID must be between 1 and 7')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusString = pack('>BBBBBB', self.cameraID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusString, value, qualifier)

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightString = pack('>BBBBBB', self.cameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        BacklightString = pack('>BBBBB', self.cameraID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('BacklightMode', BacklightString, value, qualifier)
        if len(res) != 0:
            respID, queryByte, queryData, terminator = unpack('>BBBB', res)
            if (queryByte == 0x50) and (queryData == 0x02):
                self.WriteStatus('BacklightMode', 'On', None)
            elif (queryByte == 0x50) and (queryData == 0x03):
                self.WriteStatus('BacklightMode', 'Off', None)
            else:
                print('Invalid/unexpected response for UpdateBacklightMode')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 0x20,
            'Far': 0x30
        }

        if 0 <= int(qualifier['Focus Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = 0x00
            else:
                focusSpeed = int(qualifier['Focus Speed']) + ValueStateValues[value]
            FocusString = pack('>BBBBBB', self.cameraID, 0x01, 0x04, 0x08, focusSpeed, 0xFF)
            self.__SetHelper('Focus', FocusString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetHome(self, value, qualifier):

        HomeCmdString = pack('>BBBBB', self.cameraID, 0x01, 0x06, 0x04, 0xFF)
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03]
        }

        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if not 1 <= PanSpd <= 24:
            print('Invalid Command for SetPanTilt')
        elif not 1 <= TiltSpd <= 20:
            print('Invalid Command for SetPanTilt')
        else:
            PanTiltString = pack('>BBBBBBBBB', self.cameraID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        PowerCmdString = pack('>BBBBBB', self.cameraID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerString = pack('>BBBBB', self.cameraID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerString, value, qualifier)
        if not len(res) == 0:
            respID, queryByte, queryData, terminator = unpack('>BBBB', res)
            if (queryByte == 0x50) and (queryData == 0x02):
                self.WriteStatus('Power', 'On', None)
            elif (queryByte == 0x50) and (queryData == 0x03):
                self.WriteStatus('Power', 'Off', None)
            else:
                print('Invalid/unexpected response for UpdatePower')
                
    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 6:
            cmdValue = int(value)
            PresetString = pack('>BBBBBBB', self.cameraID, 0x01, 0x04, 0x3F, 0x02, cmdValue, 0xFF)
            self.__SetHelper('PresetRecall', PresetString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetResetPosition(self, value, qualifier):

        ResetPanTiltString = pack('>BBBBB', self.cameraID, 0x01, 0x06, 0x05, 0xFF)
        self.__SetHelper('ResetPosition', ResetPanTiltString, value, qualifier)

    def SetResetPreset(self, value, qualifier):

        if 1 <= int(value) <= 6:
            cmdValue = int(value)
            PresetString = pack('>BBBBBBB', self.cameraID, 0x01, 0x04, 0x3F, 0x00, cmdValue, 0xFF)
            self.__SetHelper('ResetPreset', PresetString, value, qualifier)
        else:
            print('Invalid Command for SetResetPreset')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 6:
            cmdValue = int(value)
            PresetString = pack('>BBBBBBB', self.cameraID, 0x01, 0x04, 0x3F, 0x01, cmdValue, 0xFF)
            self.__SetHelper('PresetSave', PresetString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': 0x20,
            'Out': 0x30
        }

        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomString = pack('>BBBBBB', self.cameraID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            address, errorByte, errorCode, terminator = unpack('>BBBB', response)

            if (errorByte == 0x06) and (errorCode == 0x02):
                print(sourceCmdName + ' Syntax Error')
                response = ''
            elif (errorByte == 0x06) and (errorCode == 0x03):
                self.Error([sourceCmdName + ' Command Buffer Full'])
                response = ''
            elif (errorByte == 0x06) and (errorCode == 0x41):
                self.Error([sourceCmdName + ' Command Not Executable'])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False
    
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
        
class DeviceEthernetClass:

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
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Heartbeat': {'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'ResetPosition': {'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'Product Version:'), self.__MatchVersion, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)

    def UpdateHeartbeat(self, value, qualifier):

        HeartbeatCmdString = 'version\r'
        self.__UpdateHelper('Heartbeat', HeartbeatCmdString, value, qualifier)
        
    def __MatchVersion(self, match, tag):
        self.WriteStatus('Heartbeat', '', None)

    def SetPan(self, value, qualifier):

        SpeedStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24'
        }

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right',
            'Stop': 'stop'
        }

        if value == 'Stop':
            PanCmdString = 'camera pan stop\r'
        else:
            PanCmdString = 'camera pan {0} {1}\r'.format(ValueStateValues[value], SpeedStates[qualifier['Speed']])
        self.__SetHelper('Pan', PanCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6'
        }

        PresetRecallCmdString = 'camera preset recall {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6'
        }

        PresetSaveCmdString = 'camera preset store {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetResetPosition(self, value, qualifier):
        ResetPositionCmdString = 'camera home\r'
        self.__SetHelper('ResetPosition', ResetPositionCmdString, value, qualifier)

    def SetTilt(self, value, qualifier):


        SpeedStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16', 
            '17' : '17', 
            '18' : '18', 
            '19' : '19', 
            '20' : '20'
        }

        ValueStateValues = {
            'Up' : 'up', 
            'Down' : 'down', 
            'Stop' : 'stop'
        }

        if value == 'Stop':
            TiltCmdString = 'camera tilt stop\r'
        else:
            TiltCmdString = 'camera tilt {0} {1}\r'.format(ValueStateValues[value], SpeedStates[qualifier['Speed']])
        self.__SetHelper('Tilt', TiltCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):


        SpeedStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7'
        }

        ValueStateValues = {
            'In'    : 'in', 
            'Out'   : 'out', 
            'Stop'  : 'stop'
        }

        if value == 'Stop':
            ZoomCmdString = 'camera zoom stop\r'
        else:
            ZoomCmdString = 'camera zoom {0} {1}\r'.format(ValueStateValues[value], SpeedStates[qualifier['Speed']])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def SetSendPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')
        
    def SetSendUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchSendUsername(self, match, tag):

        self.SetSendUsername( None, None)
        self.SetSendPassword( None, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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
        print('Error')

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')
            else:
                self.Models[Model]()

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')
            else:
                self.Models[Model]()

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
