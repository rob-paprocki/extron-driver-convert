from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
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
        self._devicePassword = 'admin'

        self.Models = {
            'EB-PU2116W': self.epsn_1_5651_PU21xxW,
            'CB-PU2116W': self.epsn_1_5651_PU21xxW,
            'EB-PU2113W': self.epsn_1_5651_PU21xxW,
            'CB-PU2113W': self.epsn_1_5651_PU21xxW,
            'EB-PU2120W': self.epsn_1_5651_PU21xxW,
            'CB-PU2120W': self.epsn_1_5651_PU21xxW,
            'EB-PU2120S': self.epsn_1_5651_PU21xxW,
            'CB-PU2220B': self.epsn_1_5651_PU22xxB,
            'EB-PU2216B': self.epsn_1_5651_PU22xxB,
            'CB-PU2216B': self.epsn_1_5651_PU22xxB,
            'EB-PU2213B': self.epsn_1_5651_PU22xxB,
            'CB-PU2213B': self.epsn_1_5651_PU22xxB,
            'EB-PU2220S': self.epsn_1_5651_PU22xxB,
            'EB-PU2220B': self.epsn_1_5651_PU22xxB,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.authenticated = True
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=([0123456A]0)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'ASPECT=[0123456A]0 (30)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'ERR=(00|01|03|04|06|07|08|09|0A|0B|0C|0D|0E|0F|10|11|12|13|14|15|16|17|18)\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(10|30|52|53|60|80|A0)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[01245])\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=(\d+)\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'ONTIME=(\d+)\r:'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'PWR=(0[0123459])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=(\d{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:|ESC/VP.net\x10\x03\x00\x00(\x41|\x43)\x00'), self.__MatchError, None)

    @property
    def devicePassword(self):
        return self._devicePassword
    
    @devicePassword.setter
    def devicePassword(self, value):
        self._devicePassword = value

    # For ethernet control, this string needs to be sent prior to
    # sending other commands, otherwise the EB-PU2116W will close
    # the connection.
    def SetOnConnectedString(self, value, qualifier):
        if self._devicePassword == '':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        else: # if password passed in GS and not on projector, this password connect string still authenticates
            password = bytes('{:<16}'.format(self._devicePassword), 'utf-8')
            connectString = b'ESC/VP.net\x10\x03\x00\x00\x00\x01\x01\x01'
            self.Send(b''.join([connectString, password]))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal':   '00',
            '4:3':      '10',
            '16:9':     '20',
            'Auto':     '30',
            'Full':     '40',
            'H-Zoom':   '50',
            'Native':   '60',
            'V-Zoom':   'A0'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'ASPECT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '10': '4:3',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'H-Zoom',
            '60': 'Native',
            'A0': 'V-Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        if value in ['On', 'Off']:
            AVMuteCmdString = 'MUTE {}\r'.format(value.upper())
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AVMute', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan Error',
            '03': 'Lamp Failure at Power On',
            '04': 'High Internal Temperature Error',
            '06': 'Lamp Error',
            '07': 'Open Lamp Cover Door Error',
            '08': 'Cinema Filter Error',
            '09': 'Electric Dual-Layered Capacitor is Disconnected',
            '0A': 'Auto Iris Error',
            '0B': 'Subsystem Error',
            '0C': 'Low Air Flow Error',
            '0D': 'Air Filter Air Flow Sensor Error',
            '0E': 'Power Supply Unit Error (Ballast)',
            '0F': 'Shutter Error',
            '10': 'Cooling System Error (Peltiert Element)',
            '11': 'Cooling System Error (Pump)',
            '12': 'Static Iris Error',
            '13': 'Power Supply Unit Error (Disagreement of Ballast)',
            '14': 'Exhaust Shutter Error',
            '15': 'Obstacle Detection Error',
            '16': 'IF Board Discernment Error',
            '17': 'Communication Error of "Stack Projection Function"',
            '18': 'I2C Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        if value in ['On', 'Off']:
            FreezeCmdString = 'FREEZE {}\r'.format(value.upper())
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        if value in self.InputStates:
            InputCmdString = 'SOURCE {}\r'.format(self.InputStates[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal':   '00',
            'Quiet':    '01',
            'Extended': '04',
            'Custom':   '05'
        }

        if value in ValueStateValues:
            LampModeCmdString = 'LUMINANCE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Quiet',
            '04': 'Extended',
            '05': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       '35',
            'Down':     '36',
            'Left':     '37',
            'Right':    '38',
            'Menu':     '03',
            'Enter':    '16',
            'ESC':      '05'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'KEY {}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'ONTIME?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'ON',
            'Off':  'OFF'
        }

        if value in ValueStateValues:
            PowerCmdString = 'PWR {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',            # Standby Mode (Network Communication Off)
            '04': 'Off',            # Standby Mode (Network Communication On)
            '02': 'Warming Up',
            '03': 'Cooling Down',
            '05': 'Off',            # Abnormality standby
            '09': 'Off'             # A/V standby
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        VolumeStateTable = {
            0: 0,
            1: 12,
            2: 24,
            3: 36,
            4: 48,
            5: 60,
            6: 73,
            7: 85,
            8: 97,
            9: 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
        }

        if 0 <= value <= 20:
            VolumeCmdString = 'VOL {}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12

        if 0 <= value <= 20:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.authenticated:
            self.Send(commandstring)
        else:
            self.Discard('Not Authenticated')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
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

                self.Send(commandstring)
        else:
            self.Discard('Not Authenticated')

    def __MatchError(self, match, tag):

        self.counter = 0

        error_map = {
            b'C': 'Incorrect Password',
            b'A': 'Password Required'
        }
        if match.group(1): # None or \x43 or \x41 (password related)
            self.authenticated = False # Set auth flag to False to prevent OnConnectedString from repeatedly sending
            self.Error(['An error occurred: {}.'.format(error_map[match.group(1)])])
        else: 
            self.Error(['An error occurred.']) # ERR\r:

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_5651_PU21xxW(self):

        self.InputStates = {
            'Computer': '10',
            'HDMI':     '30',
            'USB':      '52',
            'LAN':      '53',
            'HDBaseT':  '80',
            'DVI-D':    'A0'
        }

        self.InputValues = {
            '10': 'Computer',
            '30': 'HDMI',
            '52': 'USB',
            '53': 'LAN',
            '80': 'HDBaseT',
            'A0': 'DVI-D'
        }

    def epsn_1_5651_PU22xxB(self):
        
        self.InputStates = {
            'Computer': '10',
            'HDMI':     '30',
            'USB':      '52',
            'LAN':      '53',
            'SDI':      '60',
            'HDBaseT':  '80',
            'DVI-D':    'A0'
        }

        self.InputValues = {
            '10': 'Computer',
            '30': 'HDMI',
            '52': 'USB',
            '53': 'LAN',
            '60': 'SDI',
            '80': 'HDBaseT',
            'A0': 'DVI-D'
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.SetOnConnectedString(None, None)
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()