from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'IRLock': {'Status': {}},
            'KeyLock': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteFunctions': {'Status': {}},
            'Touch': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x07([\x00-\x03])[\x47-\x4A]\xDD\xEE\xFF'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x01(\x00|\x01)[\x83\x84]\xDD\xEE\xFF'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x81([\x02-\x11])\x00[\x83-\x92]\xDD\xEE\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x01(\x00|\x01)[\x42\x41]\xDD\xEE\xFF'), self.__MatchIRLock, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x00(\x01|\x00)[\x40\x41]\xDD\xEE\xFF'), self.__MatchKeyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x83([\x00-\x03])\x00[\x83-\x86]\xDD\xEE\xFF'), self.__MatchPCPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x80(\x01|\x00)\x00[\x80\x81]\xDD\xEE\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x12(\x00|\x01)[\x52\x53]\xDD\xEE\xFF'), self.__MatchTouch, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x35\x03(\x00|\x01)[\x38\x39]\xDD\xEE\xFF'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x00([\x00-\x64])[\x82-\xE6]\xDD\xEE\xFF'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\xAA\xBB\xCC\x08\x01\x00\x09\xDD\xEE\xFF',
            '16:9': b'\xAA\xBB\xCC\x08\x00\x00\x08\xDD\xEE\xFF',
            'PTP': b'\xAA\xBB\xCC\x08\x07\x00\x0F\xDD\xEE\xFF'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xAA\xBB\xCC\x39\x07\x00\x40\xDD\xEE\xFF'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '4:3',
            '\x02': '16:9',
            '\x03': 'PTP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x03\x01\x00\x04\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x03\x01\x01\x05\xDD\xEE\xFF'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xAA\xBB\xCC\x03\x03\x00\x06\xDD\xEE\xFF'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x00': 'On',
            '\x01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF',
            'HDMI 1': b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF',
            'HDMI 2': b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF',
            'HDMI 3': b'\xAA\xBB\xCC\x02\x05\x00\x07\xDD\xEE\xFF',
            'AV': b'\xAA\xBB\xCC\x02\x02\x00\x04\xDD\xEE\xFF',
            'DisplayPort': b'\xAA\xBB\xCC\x02\x11\x00\x13\xDD\xEE\xFF',
            'PC': b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF',
            'Android': b'\xAA\xBB\xCC\x02\x0A\x00\x0C\xDD\xEE\xFF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xAA\xBB\xCC\x02\x00\x00\x02\xDD\xEE\xFF'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x03': 'VGA',
            '\x06': 'HDMI 1',
            '\x07': 'HDMI 2',
            '\x05': 'HDMI 3',
            '\x11': 'DisplayPort',
            '\x02': 'AV',
            '\x08': 'PC',
            '\x0A': 'Android'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetIRLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x38\x05\x01\x3E\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x38\x05\x00\x3D\xDD\xEE\xFF'

        }

        IRLockCmdString = ValueStateValues[value]
        self.__SetHelper('IRLock', IRLockCmdString, value, qualifier)

    def UpdateIRLock(self, value, qualifier):

        IRLockCmdString = b'\xAA\xBB\xCC\x39\x01\x00\x3A\xDD\xEE\xFF'
        self.__UpdateHelper('IRLock', IRLockCmdString, value, qualifier)

    def __MatchIRLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IRLock', value, None)

    def SetKeyLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x38\x04\x01\x3D\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x38\x04\x00\x3C\xDD\xEE\xFF'
        }

        KeyLockCmdString = ValueStateValues[value]
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def UpdateKeyLock(self, value, qualifier):

        KeyLockCmdString = b'\xAA\xBB\xCC\x39\x00\x00\x39\xDD\xEE\xFF'
        self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def __MatchKeyLock(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('KeyLock', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xAA\xBB\xCC\x07\x1B\x00\x22\xDD\xEE\xFF',
            '1': b'\xAA\xBB\xCC\x07\x00\x00\x07\xDD\xEE\xFF',
            '2': b'\xAA\xBB\xCC\x07\x10\x00\x17\xDD\xEE\xFF',
            '3': b'\xAA\xBB\xCC\x07\x11\x00\x18\xDD\xEE\xFF',
            '4': b'\xAA\xBB\xCC\x07\x13\x00\x1A\xDD\xEE\xFF',
            '5': b'\xAA\xBB\xCC\x07\x14\x00\x1B\xDD\xEE\xFF',
            '6': b'\xAA\xBB\xCC\x07\x15\x00\x1C\xDD\xEE\xFF',
            '7': b'\xAA\xBB\xCC\x07\x17\x00\x1E\xDD\xEE\xFF',
            '8': b'\xAA\xBB\xCC\x07\x18\x00\x1F\xDD\xEE\xFF',
            '9': b'\xAA\xBB\xCC\x07\x19\x00\x20\xDD\xEE\xFF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xAA\xBB\xCC\x07\x0D\x00\x14\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x07\x47\x00\x4E\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x4D\x00\x54\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x07\x49\x00\x50\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x07\x4B\x00\x52\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x07\x4A\x00\x51\xDD\xEE\xFF',
            'Back / Escape': b'\xAA\xBB\xCC\x07\x0A\x00\x11\xDD\xEE\xFF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x09\x01\x00\x0A\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x09\x00\x00\x09\xDD\xEE\xFF',
        }

        PCPowerCmdString = ValueStateValues[value]
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def UpdatePCPower(self, value, qualifier):

        PCPowerCmdString = b'\xAA\xBB\xCC\x09\x02\x00\x0B\xDD\xEE\xFF'
        self.__UpdateHelper('PCPower', PCPowerCmdString, value, qualifier)

    def __MatchPCPower(self, match, tag):

        ValueStateValues = {
            '\x00': 'On',
            '\x01': 'Off',
            '\x02': 'Sleep',
            '\x03': 'Hibernate'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PCPower', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x01\x00\x00\x01\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x01\x01\x00\x02\xDD\xEE\xFF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xAA\xBB\xCC\x01\x02\x00\x03\xDD\xEE\xFF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x00': 'On',
            '\x01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRemoteFunctions(self, value, qualifier):

        ValueStateValues = {
            'WIN': b'\xAA\xBB\xCC\x07\x0B\x00\x12\xDD\xEE\xFF',
            'Space': b'\xAA\xBB\xCC\x07\x46\x00\x4D\xDD\xEE\xFF',
            'Alt + Tab': b'\xAA\xBB\xCC\x07\x1D\x00\x24\xDD\xEE\xFF',
            'Alt + F4': b'\xAA\xBB\xCC\x07\x1F\x00\x26\xDD\xEE\xFF',
            'Display': b'\xAA\xBB\xCC\x07\x4C\x00\x53\xDD\xEE\xFF',
            'Home': b'\xAA\xBB\xCC\x07\x48\x00\x4F\xDD\xEE\xFF',
            'Backspace': b'\xAA\xBB\xCC\x07\x40\x00\x47\xDD\xEE\xFF',
            'Page Up': b'\xAA\xBB\xCC\x07\x42\x00\x49\xDD\xEE\xFF',
            'Page Down': b'\xAA\xBB\xCC\x07\x0F\x00\x16\xDD\xEE\xFF',
            'F1': b'\xAA\xBB\xCC\x07\x45\x00\x4C\xDD\xEE\xFF',
            'F2': b'\xAA\xBB\xCC\x07\x12\x00\x19\xDD\xEE\xFF',
            'F3': b'\xAA\xBB\xCC\x07\x51\x00\x58\xDD\xEE\xFF',
            'F4': b'\xAA\xBB\xCC\x07\x5B\x00\x62\xDD\xEE\xFF',
            'F5': b'\xAA\xBB\xCC\x07\x44\x00\x4B\xDD\xEE\xFF',
            'F6': b'\xAA\xBB\xCC\x07\x50\x00\x57\xDD\xEE\xFF',
            'F7': b'\xAA\xBB\xCC\x07\x43\x00\x4A\xDD\xEE\xFF',
            'F8': b'\xAA\xBB\xCC\x07\x1A\x00\x21\xDD\xEE\xFF',
            'F9': b'\xAA\xBB\xCC\x07\x04\x00\x0B\xDD\xEE\xFF',
            'F10': b'\xAA\xBB\xCC\x07\x59\x00\x60\xDD\xEE\xFF',
            'F11': b'\xAA\xBB\xCC\x07\x57\x00\x5E\xDD\xEE\xFF',
            'F12': b'\xAA\xBB\xCC\x07\x08\x00\x0F\xDD\xEE\xFF',
            'Shift + F10': b'\xAA\xBB\xCC\x07\x16\x00\x1D\xDD\xEE\xFF',
            'Red': b'\xAA\xBB\xCC\x07\x5C\x00\x63\xDD\xEE\xFF',
            'Green': b'\xAA\xBB\xCC\x07\x5D\x00\x64\xDD\xEE\xFF',
            'Yellow': b'\xAA\xBB\xCC\x07\x5E\x00\x65\xDD\xEE\xFF',
            'Blue': b'\xAA\xBB\xCC\x07\x5F\x00\x66\xDD\xEE\xFF'
        }

        RemoteFunctionsCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteFunctions', RemoteFunctionsCmdString, value, qualifier)

    def SetTouch(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x38\x07\x01\x40\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x38\x07\x00\x3F\xDD\xEE\xFF'
        }

        TouchCmdString = ValueStateValues[value]
        self.__SetHelper('Touch', TouchCmdString, value, qualifier)

    def UpdateTouch(self, value, qualifier):

        TouchCmdString = b'\xAA\xBB\xCC\x39\x12\x00\x4B\xDD\xEE\xFF'
        self.__UpdateHelper('Touch', TouchCmdString, value, qualifier)

    def __MatchTouch(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Touch', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xAA\xBB\xCC\x07\x4E\x00\x55\xDD\xEE\xFF'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xAA\xBB\xCC\x35\x02\x00\x37\xDD\xEE\xFF'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = 0x03 + value
            VolumeCmdString = pack('10B', 0xAA, 0xBB, 0xCC, 0x03, 0x00, value, checksum, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xAA\xBB\xCC\x03\x02\x00\x05\xDD\xEE\xFF'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1)[0]
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

