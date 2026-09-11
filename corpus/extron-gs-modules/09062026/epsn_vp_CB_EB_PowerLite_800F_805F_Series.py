from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenSize': {'Status': {}},
            'SplitScreenSource': {'Parameters': ['Side'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(?:.{2}) (30)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'ASPECT=([456]0)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(00|11|12)\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR=(00|01|03|04|06|07|08|09|0A|0B|0C|0D|0E|0F|10|11|12|13|14|15|16|17|18)\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(30|A0|C0|10|20|53|56|80|40|41|52|54)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[0145])\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=(\d+)\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'ONTIME=(\d+)\r:'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'PWR=(0[0123459])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=(\d{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '30',
            'Full': '40',
            'Zoom': '50',
            'Native': '60'
        }

        AspectRatioCmdString = 'ASPECT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AVMuteCmdString = 'MUTE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'CC1': '11',
            'CC2': '12'
        }

        ClosedCaptionCmdString = 'CCAP {}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '11': 'CC1',
            '12': 'CC2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

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

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = 'FREEZE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '30',
            'HDMI 2': 'A0',
            'HDMI 3': 'C0',
            'Computer 1': '10',
            'Computer 2': '20',
            'LAN': '53',
            'Screen Mirroring': '56',
            'HDBaseT': '80',
            'Video': '40',
            'Video (RCA)': '41',
            'USB 1': '52',
            'USB 2': '54'
        }

        InputCmdString = 'SOURCE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '30': 'HDMI 1',
            'A0': 'HDMI 2',
            'C0': 'HDMI 3',
            '10': 'Computer 1',
            '20': 'Computer 2',
            '53': 'LAN',
            '56': 'Screen Mirroring',
            '80': 'HDBaseT',
            '40': 'Video',
            '41': 'Video (RCA)',
            '52': 'USB 1',
            '54': 'USB 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '00',
            'Quiet': '01',
            'Extended': '04',
            'Custom': '05'
        }

        LampModeCmdString = 'LUMINANCE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

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
            'Menu': '03',
            'Up': '35',
            'Down': '36',
            'Left': '37',
            'Right': '38',
            'Enter': '16',
            'Esc': '05'
        }

        MenuNavigationCmdString = 'KEY {}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'ONTIME?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        PowerCmdString = 'PWR {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',             # Lamp ON
            '00': 'Off',            # Standby Mode (Network OFF)
            '04': 'Off',            # Standby Mode (Network ON)
            '02': 'Warming Up',     # Warmup
            '03': 'Cooling Down',   # Cooldown
            '05': 'Off',            # Abnormality standby
            '09': 'Off'             # A/V standby
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        SplitScreenCmdString = 'SPS 01 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def SetSplitScreenSize(self, value, qualifier):

        ValueStateValues = {
            'Equal': '00',
            'Larger Left': '01',
            'Larger Right': '02'
        }

        SplitScreenSizeCmdString = 'SPS 02 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('SplitScreenSize', SplitScreenSizeCmdString, value, qualifier)

    def SetSplitScreenSource(self, value, qualifier):

        SideStates = {
            'Left': '03',
            'Right': '04'
        }

        ValueStateValues = {
            'HDMI 1': '30',
            'HDMI 2': 'A0',
            'HDMI 3': 'C0',
            'Computer 1': '10',
            'Computer 2': '20',
            'LAN': '53',
            'Screen Mirroring': '56',
            'HDBaseT': '80',
            'Video (RCA)': '41',
            'USB 1': '52',
            'USB 2': '54'
        }

        SplitScreenSourceCmdString = 'SPS {} {}\r'.format(SideStates[qualifier['Side']], ValueStateValues[value])
        self.__SetHelper('SplitScreenSource', SplitScreenSourceCmdString, value, qualifier)

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

        ValueConstraints = {
            'Min': 0,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOL {}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12
        self.WriteStatus('Volume', value, None)

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

        self.Error(['An error occurred.'])

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
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()