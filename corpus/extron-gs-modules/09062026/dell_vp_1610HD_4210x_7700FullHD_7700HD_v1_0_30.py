from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


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

        self.Models = {
            '1610HD': self.dell_1_707_other,
            '4210x': self.dell_1_707_other,
            '7700FullHD': self.dell_1_707_7700,
            '7700HD': self.dell_1_707_7700,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\x00\x32(\x00|\x01|\x02)'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'\x00\x5D(\x01|\x02)'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'\x00\x26([\x00-\x12])'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\x00\x83(\x00|\x01)'), self.__MatchLampMode, None)
            self.AddMatchString(compile(b'\x00\x2F(..)'), self.__MatchLampUsage, None)
            self.AddMatchString(compile(b'\x00\x61(\x00|\x01)'), self.__MatchMute, None)
            self.AddMatchString(compile(b'\x00\x84(..)'), self.__MatchOperationHours, None)
            self.AddMatchString(compile(b'\x00\xFF([\x01-\x04])'), self.__MatchPower, None)
            self.AddMatchString(compile(b'\x00\x65(\x00|\x01)'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'\x00\x4F([\x00-\x14])'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x08\x7E\x17'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xD3\xBF\x32'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Original',
            b'\x01': '4:3',
            b'\x02': 'Wide'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xC4\x7F\x07'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': 0,
            'CC1': 1,
            'CC2': 2,
            'CC3': 3,
            'CC4': 4
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = pack('<BBBBBBBBBBBBB', 0xBE, 0xEF, 0x10, 0x06, 0x00, 0x2A, 0x7E, 0x11, 0x11, 0x02, 0x00, 0x6F, ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x1D\x3E\x24',
            'Off': b'\xDD\xFF\x25'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\xFF\xFF\x5D'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x02': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xC2\xBF\x0E',
            'Off': b'\xEF\xBF\x62'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        if value in self.InputValues:
            InputCmdString = self.InputValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xDC\xBF\x26'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputNames[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {

            'Normal': b'\x19\x7E\x2B',
            'Eco': b'\xD9\xBF\x2A'
        }

        if value in ValueStateValues:
            LampModeCmdString = ValueStateValues[value]
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\xA7\x7F\x83'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Eco',
            b'\x01': 'Normal'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xDA\x7F\x2F'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = unpack('<H', match.group(1))[0]
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xC7\xBF\x02',
            'Up': b'\x07\x7E\x03',
            'Down': b'\xC5\x3F\x04',
            'Left': b'\x05\xFE\x05',
            'Right': b'\x04\xBE\x06',
            'Enter': b'\xF6\x3F\x40',
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xC3\xFF\x0D',
            'Off': b'\x3E\x7E\x5F'
        }

        if value in ValueStateValues:
            MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteCmdString = b'\xEE\xFF\x61'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Mute', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x65\x3E\x84'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = unpack('<H', match.group(1))[0]
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {

            'On': b'\xC6\xFF\x01',
            'Off': b'\x0C\x3E\x18',
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x46\x7E\xFF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x03': 'On',
            b'\x01': 'Off',
            b'\x02': 'Warming Up',
            b'\x04': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {

            'On': b'\x02\x7E\x0F',
            'Off': b'\xED\x3F\x64'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x2D\xFE\x65'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('<BBBBBBBBBBBBB', 0xBE, 0xEF, 0x10, 0x06, 0x00, 0x18, 0xDB, 0x11, 0x11, 0x02, 0x00, 0x68, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xF2\x7F\x4F'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1)[0]
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if command not in ['Volume', 'ClosedCaption']:
            commandstring = b'\xBE\xEF\x10\x05\x00' + commandstring[0:2] + b'\x11\x11\x01\x00' + commandstring[2:]

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = b'\xBE\xEF\x10\x05\x00' + commandstring[0:2] + b'\x11\x11\x01\x00' + commandstring[2:3]
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
        pass

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dell_1_707_7700(self):

        self.InputValues = {
            'VGA 1'             :   b'\xCC\xFF\x19', 
            'VGA 2'             :   b'\x28\xFE\x69', 
            'HDMI'              :   b'\x3A\x3E\x50',
            'HDMI 2'            :   b'\xE9\x7F\x6B',
            'Component'         :   b'\xDE\x3F\x20',
            'Wireless Display'  :   b'\x61\x7E\x8B',
            'USB Display'       :   b'\x62\xBE\x8E',
            'USB Viewer'        :   b'\xA2\x7F\x8F',
            'S-Video'           :   b'\x1F\xBE\x22', 
            'Video'             :   b'\xDF\x7F\x23'
        }

        self.InputNames = {
            b'\x00' :   'None',
            b'\x01' :   'VGA 1', 
            b'\x02' :   'VGA 2', 
            b'\x03' :   'HDMI',
            b'\x10' :   'HDMI 2',
            b'\x11' :   'Component', 
            b'\x04' :   'S-Video', 
            b'\x05' :   'Video',
            b'\x07' :   'Wireless Display',
            b'\x08' :   'USB Display',
            b'\x09' :   'USB Viewer'
        }

    def dell_1_707_other(self):

        self.InputValues = {
            'VGA 1'             :   b'\xCC\xFF\x19', 
            'VGA 2'             :   b'\x28\xFE\x69', 
            'HDMI'              :   b'\x3A\x3E\x50',
            'S-Video'           :   b'\x1F\xBE\x22', 
            'Video'             :   b'\xDF\x7F\x23'
        }

        self.InputNames = {
            b'\x00' :   'None',
            b'\x01' :   'VGA 1', 
            b'\x02' :   'VGA 2', 
            b'\x03' :   'HDMI',
            b'\x04' :   'S-Video', 
            b'\x05' :   'Video',
        }

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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
