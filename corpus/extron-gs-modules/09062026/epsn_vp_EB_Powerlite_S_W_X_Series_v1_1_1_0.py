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
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenLeftInput': {'Status': {}},
            'SplitScreenMode': {'Status': {}},
            'SplitScreenRightInput': {'Status': {}},
            'SplitScreenSwap': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(00 30|[0-2]0)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(00|11|12)\r'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR=(00|01|04|03|07|06|08|09|0A|0B|0C|0D|0E|0F|10|11)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(1F|2F|11|21|14|24|41|42|30|51|52|53)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,4})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(00|01|02|03|04|05|09)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        Value = {
            '4:3': b'ASPECT 10\r',
            '16:9': b'ASPECT 20\r',
            'Normal': b'ASPECT 00\r',
            'Auto': b'ASPECT 30\r'
        }[value]

        self.__SetHelper('AspectRatio', Value, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', b'ASPECT?\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Values = {
            b'10': '4:3',
            b'20': '16:9',
            b'00': 'Normal',
            b'00 30': 'Auto',
        }[match.group(1)]

        self.WriteStatus('AspectRatio', Values, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        Value = {
            'On': b'MUTE ON\r',
            'Off': b'MUTE OFF\r'
        }[value]

        self.__SetHelper('AVMute', Value, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        self.__UpdateHelper('AVMute', b'MUTE?\r', value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        Value = {
            'CC1': b'CCAP 11\r',
            'CC2': b'CCAP 12\r',
            'Off': b'CCAP 00\r'
        }[value]

        self.__SetHelper('ClosedCaption', Value, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        self.__UpdateHelper('ClosedCaption', b'CCAP?\r', value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        Values = {
            b'11': 'CC1',
            b'12': 'CC2',
            b'00': 'Off'
        }[match.group(1)]

        self.WriteStatus('ClosedCaption', Values, None)

    def UpdateDeviceStatus(self, value, qualifier):
        self.__UpdateHelper('DeviceStatus', b'ERR?\r', value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        Values = {
            b'00': 'Normal',
            b'01': 'Fan Error',
            b'04': 'Internal temperature is abnormally high',
            b'03': 'Lamp Burnt-out',
            b'07': 'Lamp Cover Error',
            b'06': 'Lamp Error',
            b'08': 'Cinema Filter Error',
            b'09': 'Dual Layered Capacitor Disconnected',
            b'0A': 'Auto Iris Error',
            b'0B': 'Subsystem Error',
            b'0D': 'Sensor Error',
            b'0E': 'Power Supply Error',
            b'0F': 'Shutter Failure',
            b'10': 'Cooling System Error',
            b'11': 'Cooling System Error (Pump)'
        }[match.group(1)]

        self.WriteStatus('DeviceStatus', Values, None)

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': b'FREEZE ON\r',
            'Off': b'FREEZE OFF\r'
        }[value]

        self.__SetHelper('Freeze', Value, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        self.__UpdateHelper('Freeze', b'FREEZE?\r', value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        Value = {
            'PC1 Auto': b'SOURCE 1F\r',
            'PC2 Auto': b'SOURCE 2F\r',
            'PC1 RGB': b'SOURCE 11\r',
            'PC2 RGB': b'SOURCE 21\r',
            'PC1 Component': b'SOURCE 14\r',
            'PC2 Component': b'SOURCE 24\r',
            'HDMI': b'SOURCE 30\r',
            'USB Display': b'SOURCE 51\r',
            'USB': b'SOURCE 52\r',
            'LAN': b'SOURCE 53\r',
            'Video': b'SOURCE 41\r',
            'S-Video': b'SOURCE 42\r'
        }[value]

        self.__SetHelper('Input', Value, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', b'SOURCE?\r', value, qualifier)

    def __MatchInput(self, match, tag):

        Values = {
            b'1F': 'PC1 Auto',
            b'2F': 'PC2 Auto',
            b'11': 'PC1 RGB',
            b'21': 'PC2 RGB',
            b'14': 'PC1 Component',
            b'24': 'PC2 Component',
            b'30': 'HDMI',
            b'51': 'USB Display',
            b'52': 'USB',
            b'53': 'LAN',
            b'41': 'Video',
            b'42': 'S-Video'
        }[match.group(1)]

        self.WriteStatus('Input', Values, None)

    def SetLampMode(self, value, qualifier):

        Values = {
            'Normal': b'LUMINANCE 00\r',
            'Eco': b'LUMINANCE 01\r'
        }[value]

        self.__SetHelper('LampMode', Values, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        self.__UpdateHelper('LampMode', b'LUMINANCE?\r', value, qualifier)

    def __MatchLampMode(self, match, tag):

        Values = {
            b'00': 'Normal',
            b'01': 'Eco'
        }[match.group(1)]

        self.WriteStatus('LampMode', Values, None)

    def UpdateLampUsage(self, value, qualifier):
        self.__UpdateHelper('LampUsage', b'LAMP?\r', value, qualifier)

    def __MatchLampUsage(self, match, tag):
        self.WriteStatus('LampUsage', int(match.group(1).decode()), None)

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Up': b'KEY 35\r',
            'Down': b'KEY 36\r',
            'Left': b'KEY 37\r',
            'Right': b'KEY 38\r',
            'Enter': b'KEY 16\r',
            'Menu': b'KEY 03\r',
        }[value]

        self.__SetHelper('MenuNavigation', Value, value, qualifier)

    def SetPower(self, value, qualifier):

        Value = {
            'On': b'PWR ON\r',
            'Off': b'PWR OFF\r'
        }[value]

        self.__SetHelper('Power', Value, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', b'PWR?\r', value, qualifier)

    def __MatchPower(self, match, tag):

        Values = {
            b'01': 'On',
            b'00': 'Off',
            b'04': 'Off',
            b'05' : 'Off',
            b'09' : 'Off',
            b'02': 'Warming Up',
            b'03': 'Cooling Down'
        }[match.group(1)]

        self.WriteStatus('Power', Values, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On': b'SPS 01 01\r',
            'Off': b'SPS 01 00\r'
        }

        SplitScreenCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def SetSplitScreenLeftInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 Auto': b'SPS 03 1F\r',
            'PC2 Auto': b'SPS 03 2F\r',
            'PC1 RGB': b'SPS 03 11\r',
            'PC2 RGB': b'SPS 03 21\r',
            'PC1 Component': b'SPS 03 14\r',
            'PC2 Component': b'SPS 03 24\r',
            'HDMI': b'SPS 03 30\r',
            'USB Display': b'SPS 03 51\r',
            'USB': b'SPS 03 52\r',
            'LAN': b'SPS 03 53\r',
            'Video': b'SPS 03 41\r',
            'S-Video': b'SPS 03 42\r'
        }

        SplitScreenLeftInputCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreenLeftInput', SplitScreenLeftInputCmdString, value, qualifier)

    def SetSplitScreenMode(self, value, qualifier):

        ValueStateValues = {
            'Size 1': b'SPS 02 00\r',
            'Size 2': b'SPS 02 01\r',
            'Size 3': b'SPS 02 02\r'
        }

        SplitScreenModeCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreenMode', SplitScreenModeCmdString, value, qualifier)

    def SetSplitScreenRightInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 Auto': b'SPS 04 1F\r',
            'PC2 Auto': b'SPS 04 2F\r',
            'PC1 RGB': b'SPS 04 11\r',
            'PC2 RGB': b'SPS 04 21\r',
            'PC1 Component': b'SPS 04 14\r',
            'PC2 Component': b'SPS 04 24\r',
            'HDMI': b'SPS 04 30\r',
            'USB Display': b'SPS 04 51\r',
            'USB': b'SPS 04 52\r',
            'LAN': b'SPS 04 53\r',
            'Video': b'SPS 04 41\r',
            'S-Video': b'SPS 04 42\r'
        }

        SplitScreenRightInputCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreenRightInput', SplitScreenRightInputCmdString, value, qualifier)

    def SetSplitScreenSwap(self, value, qualifier):

        SplitScreenSwapCmdString = b'SPS 05\r'
        self.__SetHelper('SplitScreenSwap', SplitScreenSwapCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeTable = {
            0: b'VOL 0\r',
            1: b'VOL 12\r',
            2: b'VOL 24\r',
            3: b'VOL 36\r',
            4: b'VOL 48\r',
            5: b'VOL 60\r',
            6: b'VOL 73\r',
            7: b'VOL 85\r',
            8: b'VOL 97\r',
            9: b'VOL 109\r',
            10: b'VOL 121\r',
            11: b'VOL 134\r',
            12: b'VOL 146\r',
            13: b'VOL 158\r',
            14: b'VOL 170\r',
            15: b'VOL 182\r',
            16: b'VOL 195\r',
            17: b'VOL 207\r',
            18: b'VOL 219\r',
            19: b'VOL 231\r',
            20: b'VOL 243\r'
        }[value]

        self.__SetHelper('Volume', VolumeTable, value, qualifier)

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', b'VOL?\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()) // 12, None)

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

        self.Error(['An error occured'])

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
