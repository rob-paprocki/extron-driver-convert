from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.devicePassword = None
        self.Models = {}

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

        self.AVMuteRegex         = re.compile('MUTE=(ON|OFF)\r:')
        self.DeviceStatusRegex   = re.compile('ERR=(00|01|03|04|06|07|08|09|0A|0B|0C|0D|0E|0F|10|11|12|13|14|15|16|17|18)\r:')
        self.FreezeRegex         = re.compile('FREEZE=(ON|OFF)\r:')
        self.InputRegex          = re.compile('SOURCE=(10|20|30|A0|52|53|56|59|80)\r:')
        self.LampModeRegex       = re.compile('LUMINANCE=(0[0145])\r:')
        self.LampUsageRegex      = re.compile('LAMP=(\d+)\r:')
        self.OperationHoursRegex = re.compile('ONTIME=(\d+)\r:')
        self.PowerRegex          = re.compile('PWR=(0[0-59])\r:')
        self.VolumeRegex         = re.compile('VOL=(\d{1,3})\r:')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto':     '30',
            'Full':     '40',
            'H-Zoom':   '50',
            'V-Zoom':   'A0',
            'Native':   '60'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'ASPECT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '30': 'Auto',
                    '40': 'Full',
                    '50': 'H-Zoom',
                    'A0': 'V-Zoom',
                    '60': 'Native'
                    }

                value = ValueStateValues[res[-4:-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

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
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'ON': 'On',
                    'OFF': 'Off'
                    }

                valueMatch = self.AVMuteRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
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

                valueMatch = self.DeviceStatusRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        if value in ['On', 'Off']:
            FreezeCmdString = 'FREEZE {}\r'.format(value.upper())
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'ON': 'On',
                    'OFF': 'Off'
                    }

                valueMatch = self.FreezeRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1':           '10',
            'Computer 2':           '20',
            'HDMI 1':               '30',
            'HDMI 2':               'A0',
            'USB':                  '52',
            'LAN':                  '53',
            'Screen Mirroring 1':   '56',
            'Screen Mirroring 2':   '59',
            'HDBaseT':              '80'
        }

        if value in ValueStateValues:
            InputCmdString = 'SOURCE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '10': 'Computer 1',
                    '20': 'Computer 2',
                    '30': 'HDMI 1',
                    'A0': 'HDMI 2',
                    '52': 'USB',
                    '53': 'LAN',
                    '56': 'Screen Mirroring 1',
                    '59': 'Screen Mirroring 2',
                    '80': 'HDBaseT'
                    }

                valueMatch = self.InputRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal':   '00',
            'Quiet':    '01',
            'Extended': '04',
            'Custom':   '05',
        }

        if value in ValueStateValues:
            LampModeCmdString = 'LUMINANCE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '00': 'Normal',
                    '01': 'Quiet',
                    '04': 'Extended',
                    '05': 'Custom'
                    }

                valueMatch = self.LampModeRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.LampUsageRegex.match(res)
                value = int(valueMatch.group(1))
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':     '03',
            'Up':       '35',
            'Down':     '36',
            'Left':     '37',
            'Right':    '38', 
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
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.OperationHoursRegex.match(res)
                value = int(valueMatch.group(1))
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        if value in ['On', 'Off']:
            PowerCmdString = 'PWR {}\r'.format(value.upper())
            self.__SetHelper('Power', PowerCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '01': 'On',             # Lamp ON
                    '00': 'Off',            # Standby Mode (Network OFF)
                    '04': 'Off',            # Standby Mode (Network ON)
                    '02': 'Warming Up',     # Warmup
                    '03': 'Cooling Down',   # Cooldown
                    '05': 'Off',            # Abnormality standby
                    '09': 'Off'             # A/V standby
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

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
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.VolumeRegex.match(res)
                value = int(valueMatch.group(1)) // 12
                if 0 <= value <= 20:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response == 'ERR\r:':
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b':')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                if 'ERR' in res.decode():
                    self.Error(['{}: An error occurred.'.format(command)])
                
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b':')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
            if not self.devicePassword:
                self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
            else:
                password = bytes('{:<16}'.format(self.devicePassword), 'utf-8')
                connectString = b'ESC/VP.net\x10\x03\x00\x00\x00\x01\x01\x01'
                self.Send(b''.join([connectString, password]))
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
