from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AutoPosition': {'Status': {}},
            'AutoOff': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampTime': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'00(SC)(0|1|2|[0-2]{0,1}:N)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'00(APOF)(00|05|10|15|30|60|([0|1|3|6][0|5]){0,1}:N)\r'), self.__MatchAutoOff, None)
            self.AddMatchString(re.compile(b'00(MUTE)(0|1|[0-1]{0,1}:N)\r'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'00(CC)(0|1|2|[0-2]{0,1}:N)\r'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'00(vER)([0-9A-F]{3})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'00(vI)([r|v|d][1|2]|([r|v|d][1|2]){0,1}:N)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'00(LM)(0|1|[0-1]{0,1}:N)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'00(vLE)([0-9]{4})([0-5][0-9])\r'), self.__MatchLampTime, None)
            self.AddMatchString(re.compile(b'00(vST)([0-6]|[0-6]{0,1}:N)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'00(VL)([0-2][0-9]|([0-2][0-9]){0,1}:N)\r'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            '16:9': '1',
            'Full': '2',
            'Normal': '0'
            }
        AspectRatioCmdString = '00SC{0}\r'.format(AspectRatioStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '00SC\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioStateNames = {
           '1': '16:9',
           '2': 'Full',
           '0': 'Normal'
           }
        try:
            value = AspectRatioStateNames[match.group(2).decode()]
            self.WriteStatus('AspectRatio', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def SetAutoPosition(self, value, qualifier):

        AutoPositionCmdString = '00r09\r'
        self.__SetHelper('AutoPosition', AutoPositionCmdString, value, qualifier)

    def SetAutoOff(self, value, qualifier):

        AutoOffStateValues = {
            'Off': '00',
            '5': '05',
            '10': '10',
            '15': '15',
            '30': '30',
            '60': '60'
            }
        AutoOffCmdString = '00APOF{0}\r'.format(AutoOffStateValues[value])
        self.__SetHelper('AutoOff', AutoOffCmdString, value, qualifier)

    def UpdateAutoOff(self, value, qualifier):

        AutoOffCmdString = '00APOF\r'
        self.__UpdateHelper('AutoOff', AutoOffCmdString, value, qualifier)

    def __MatchAutoOff(self, match, tag):

        AutoOffStateNames = {
            '00': 'Off',
            '05': '5',
            '10': '10',
            '15': '15',
            '30': '30',
            '60': '60'
            }
        try:
            value = AutoOffStateNames[match.group(2).decode()]
            self.WriteStatus('AutoOff', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'On': '1',
            'Off': '0'
            }
        AVMuteCmdString = '00MUTE{0}\r'.format(AVMuteStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = '00MUTE\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        AVMuteStateNames = {
           '1': 'On',
           '0': 'Off'
           }
        try:
            value = AVMuteStateNames[match.group(2).decode()]
            self.WriteStatus('AVMute', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'CC1': '1',
            'CC2': '2',
            'Off': '0'
            }
        ClosedCaptionCmdString = '00CC{0}\r'.format(ClosedCaptionStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = '00CC\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionStateNames = {
           '1': 'CC1',
           '2': 'CC2',
           '0': 'Off'
           }
        try:
            value = ClosedCaptionStateNames[match.group(2).decode()]
            self.WriteStatus('ClosedCaption', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '00vER\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusNames = {
            '000': 'Normal',
            '800': 'Fan Error',
            '400': 'Lamp Error',
            '200': 'Lamp Life Expired',
            '100': 'Lamp Life Expiring',
            '080': 'Temp Error',
            '040': 'Temp Warning',
            '020': 'Lamp Cover Error',
            '008': 'Component Abnormality'
            }
        if match.group(2).decode() != ':N':
            try:
                DecimalString = '{0:03d}'.format(int(match.group(2).decode(), 16))
                value = DeviceStatusNames[DecimalString]
            except KeyError:
                value = 'Multiple Errors'
            self.WriteStatus('DeviceStatus', value, None)
        else:
            self.__MatchError(match, tag)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '00ra4\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Computer 1': 'r1',
            'Computer 2': 'r2',
            'Video': 'v1',
            'S-Video': 'v2',
            'HDMI': 'd1'
            }
        InputCmdString = '00_{0}\r'.format(InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '00vI\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
            'r1': 'Computer 1',
            'r2': 'Computer 2',
            'v1': 'Video',
            'v2': 'S-Video',
            'd1': 'HDMI'
           }
        try:
            value = InputStateNames[match.group(2).decode()]
            self.WriteStatus('Input', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Standard': '0',
            'Low': '1'
            }
        LampModeCmdString = '00LM{0}\r'.format(LampModeStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '00LM\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeStateNames = {
           '1': 'Low',
           '0': 'Standard'
           }
        try:
            value = LampModeStateNames[match.group(2).decode()]
            self.WriteStatus('LampMode', value, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def UpdateLampTime(self, value, qualifier):

        LampTimeCmdString = '00vLE\r'
        self.__UpdateHelper('LampTime', LampTimeCmdString, value, qualifier)

    def __MatchLampTime(self, match, tag):

        value = int(match.group(2))
        self.WriteStatus('LampTime', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Left': '4f',
            'Right': '59',
            'Up': '53',
            'Down': '2b',
            'Menu': '54',
            'Enter': '10'
            }
        MenuNavigationCmdString = '00r{0}\r'.format(MenuNavigationValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '!',
            'Off': '"'
            }
        PowerCmdString = '00{0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '00vST\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
           '0': 'Off',
           '1': 'Warming',
           '2': 'On',
           '3': 'Cooling',
           '4': 'Off',
           '5': 'On',
           '6': 'On'
           }
        try:
            value = PowerStateNames[match.group(2).decode()]
            self.WriteStatus('Power', value, None)
            if match.group(2).decode() == '6':
                self.SetPassword(None, None)
        except KeyError as key:
            if str(key) == "':N'":
                self.__MatchError(match, tag)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 21
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '00VL{0:02d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '00VL\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        if match.group(2).decode() != ':N':
            value = int(match.group(2))
            self.WriteStatus('Volume', value, None)
        else:
            self.__MatchError(match, tag)

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

        commandList = {
            'SC' : 'AspectRatio',
            'APOF' : 'AutoOff',
            'MUTE' : 'AVMute',
            'CC' : 'ClosedCaption',
            'vER' : 'Device Status',
            'vI' : 'Input',
            'LM' : 'Lamp Mode',
            'vLE' : 'Lamp Time',
            'vST' : 'Power',
            'VL' : 'Volume'
            }
            
        command = commandList[match.group(1).decode()]
        print('Error executing command: {0}'.format(command))

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
