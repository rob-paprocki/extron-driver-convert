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
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampSelect': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }


        
        self.AddMatchString(re.compile(b'OP ASPECT = (0|1|2|3|4|5|6|7|8)\r\n'), self.__MatchAspectRatio, None)
        self.AddMatchString(re.compile(b'OP ERRCODE = (0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38)\r\n'), self.__MatchDeviceStatus, None)
        self.AddMatchString(re.compile(b'OP INPUT.SEL = (0|1|2|3|4|5|6|7|8)\r\n'), self.__MatchInput, None)
        self.AddMatchString(re.compile(b'OP LAMP(1|2).STAT = (1|0)\r\n'), self.__MatchLampStatus, None)
        self.AddMatchString(re.compile(b'OP LAMP.MODE = (0|1|2)\r\n'), self.__MatchLampMode, None)
        self.AddMatchString(re.compile(b'OP LAMPS = (1|0)\r\n'), self.__MatchLampSelect, None)
        self.AddMatchString(re.compile(b'OP LAMP(1|2).HOURS = ([0-9]{1,4}) HRS\r\n'), self.__MatchLampUsage, None)
        self.AddMatchString(re.compile(b'OP PROJ.RUNTIME = ([0-9]{1,4}) HRS\r\n'), self.__MatchOperationHours, None)
        self.AddMatchString(re.compile(b'OP STATUS = (0|1|2|3|4)\r\n'), self.__MatchPower, None)
        self.AddMatchString(re.compile(b'OP PICTURE.MUTE = (1|0)\r\n'), self.__MatchVideoMute, None)



    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
           '5:4' : '0',
           '4:3' : '1',
           '16:10' : '2',
           '16:9' : '3',
           '1.88' : '4',
           '2.35' : '5',
           'Letterbox' : '6',
           'Native' : '7',
           'Unscaled' : '8'
           }
        
        AspectRatioCmdString = 'op aspect = {0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = 'op aspect ?\r'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
           '0' : '5:4',
           '1' : '4:3',
           '2' : '16:10',
           '3' : '16:9',
           '4' : '1.88',
           '5' : '2.35',
           '6' : 'Letterbox',
           '7' : 'Native',
           '8' : 'Unscaled'
           }

        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'op auto.img\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)



    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'op errcode ?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        
    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusNames = {
           '0' : 'Inlet Temp Over',
           '1' : 'DMD Error',
           '2' : 'Lamp Overheat',
           '3' : 'Lamp Overheat',
           '4' : 'Lamp Ballast Overheated',
           '5' : 'Lamp Ballast Overheated',
           '6' : 'Fan Error',
           '7' : 'Fan Error',
           '8' : 'Fan Error',
           '9' : 'Fan Error',
           '10' : 'Fan Error',
           '11' : 'Fan Error',
           '12' : 'Fan Error',
           '13' : 'Fan Error',
           '14' : 'Fan Error',
           '15' : 'DMD Error',
           '16' : 'Lamp does not ignite',
           '17' : 'Lamp Ignition Failure',
           '18' : 'Ballast Communication Error',
           '19' : 'GPIO Failure',
           '20' : 'Interlock',
           '21' : 'No Signal Present',
           '22' : 'System Error',
           '23' : 'Software I2C Failure',
           '24' : 'EEPROM Failure',
           '25' : 'EDID Failure',
           '26' : 'EEP Version Failure',
           '27' : 'RST Gennum',
           '28' : 'Fan Error',
           '29' : 'Fan Error',
           '30' : 'Fan Error',
           '31' : 'Fan Error',
           '32' : 'Lamp Ignition Failure',
           '33' : 'Ballast Communication Error',
           '34' : 'Inlet Temp Over',
           '35' : 'DMD Error',
           '36' : 'Temp Sensor Failure',
           '37' : 'Temp Sensor Failure',
           '38' : 'System Failure'
           }

        value = DeviceStatusNames[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
           'HDMI 1' : '0',
           'HDMI 2' : '1',
           'RGB' : '2',
           'YUV 1' : '3',
           'YUV 2' : '4',
           'Composite' : '5',
           'S-Video' : '6',
           'RGBS' : '7',
           'HD SDI' : '8'
           }
        InputCmdString = 'op input.sel = {0}\r'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = 'op input.sel ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputNames = {
           '0' : 'HDMI 1',
           '1' : 'HDMI 2',
           '2' : 'RGB',
           '3' : 'YUV 1',
           '4' : 'YUV 2',
           '5' : 'Composite',
           '6' : 'S-Video',
           '7' : 'RGBS',
           '8' : 'HD SDI',
           }

        value = InputNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampStatus(self, value, qualifier):

        status = qualifier['Lamp']
        if status not in ['1','2']:
            self.Discard('Invalid Command for UpdateLampStatus')
        else:
            LampStatusCmdString = 'op lamp{0}.stat ?\r'.format(status)
            self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)

    def __MatchLampStatus(self, match, tag):

        LampStatusNames = {
           '1' : 'On',
           '0' : 'Off'
           }
        
        value = LampStatusNames[match.group(2).decode()]
        qualifier = {'Lamp' : match.group(1).decode()}
        self.WriteStatus('LampStatus', value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
           'Eco' : '0',
           'Standard' : '1',
           'Low' : '2'
           }
        LampModeCmdString = 'op lamp.mode = {0}\r'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'op lamp.mode ?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeNames = {
           '0' : 'Eco',
           '1' : 'Standard',
           '2' : 'Low'
           }

        value = LampModeNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetLampSelect(self, value, qualifier):

        LampSelectState = {
           'Single' : '0',
           'Dual' : '1'
           }
        LampSelectCmdString = 'op lamps = {0}\r'.format(LampSelectState[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)
    def UpdateLampSelect(self, value, qualifier):

        LampSelectCmdString = 'op lamps ?\r'
        self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def __MatchLampSelect(self, match, tag):

        LampSelectNames = {
           '0' : 'Single',
           '1' : 'Dual'
           }

        value = LampSelectNames[match.group(1).decode()]
        self.WriteStatus('LampSelect', value, None)

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if lamp not in ['1','2']:
            self.Discard('Invalid Command for UpdateLampUsage')
        else:
            LampUsageCmdString = 'op lamp{0}.hours ?\r'.format(lamp)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        
    def __MatchLampUsage(self, match, tag):

        value = int(match.group(2).decode())
        qualifier = {'Lamp' : match.group(1).decode()}
        self.WriteStatus('LampUsage', value, qualifier)
        
    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'op proj.runtime ?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        
    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)
        
    def SetPower(self, value, qualifier):

        PowerState = {
           'On' : 'op power.on\r',
           'Off' : 'op power.off\r'
           }
        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'op status ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        
    def __MatchPower(self, match, tag):

        PowerNames = {
           '2' : 'On',
           '0' : 'Off',
           '1' : 'Warming',
           '3' : 'Cooling',
           '4' : 'Warning'
           }

        value = PowerNames[match.group(1).decode()]
        if value == 'Warning':
            self.UpdateDeviceStatus( None, None)
        else:
            self.WriteStatus('DeviceStatus', 'Normal', None)
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
           'On' : '1',
           'Off' : '0'
           }
        VideoMuteCmdString = 'op picture.mute = {0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'op picture.mute ?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
           '1' : 'On',
           '0' : 'Off'
           }

        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

