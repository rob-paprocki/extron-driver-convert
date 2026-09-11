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
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'OutputResolution': { 'Status': {}},
            'OutputScalingMode': { 'Status': {}},
            'OutputSignalType': { 'Status': {}},
            'USBConnect': { 'Status': {}},
            'USBConnectionStatus': { 'Status': {}},
            'VideoStreamID': { 'Status': {}},
            'VideoWallLayout': {'Parameters':['Number of Column','Number of Row','Column Position','Row Position','Screen Width','Screen Height','Horizontal Gap','Vertical Gap','Top Bezel','Bottom Bezel','Left Bezel','Right Bezel'], 'Status': {}},
            'VideoWallName': { 'Status': {}},
            'WorkingMode': { 'Status': {}},
            }
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'pr /MEDIA/VIDEO/O1\.Resolution=([0-9ix@.]+Hz)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'pw /MEDIA/VIDEO/O1/SCALER\.ScalingMode=(OFF|EDID|MANUAL)\r\n'), self.__MatchOutputScalingMode, None)
            self.AddMatchString(re.compile(b'pw /MEDIA/VIDEO/O1/SCALER\.SignalType=(DVI|HDMI)\r\n'), self.__MatchOutputSignalType, None)
            self.AddMatchString(re.compile(b'pr /MEDIA/KM\.Controlling=(0|1|false|true)\r\n'), self.__MatchUSBConnectionStatus, None)
            self.AddMatchString(re.compile(b'pw /SYS/MB/PHY\.VideoChannelId=([0-9]{1,4})\r\n'), self.__MatchVideoStreamID, None)
            self.AddMatchString(re.compile(b'pw /MANAGEMENT/MULTICAST\.MulticastMode=(0|1|false|true)\r\n'), self.__MatchWorkingMode, None)
            self.AddMatchString(re.compile(b'pE[\s\S]+%E[0-9]{3}[\s\S]+\r\n'), self.__MatchError, None)

    def SetLogin(self, value, qualifier):

        if self.devicePassword:
            LoginCmdString = 'CALL /LOGIN:login({})\r\n'.format(self.devicePassword)
            self.Send(LoginCmdString)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480@50Hz'       : '81004054', 
            '640x480@60Hz'       : '80000001', 
            '640x480@72Hz'       : '81004004', 
            '640x480@75Hz'       : '81004005', 
            '720x480@60Hz'       : '81000002', 
            '720x576@50Hz'       : '80000011', 
            '800x600@50Hz'       : '81004059', 
            '800x600@60Hz'       : '8100405A', 
            '800x600@72Hz'       : '81004009', 
            '800x600@75Hz'       : '8100400A', 
            '1024x768@50Hz'      : '8100405E', 
            '1024x768@60Hz'      : '8100405F', 
            '1024x768@75Hz'      : '81004060', 
            '1152x864@60Hz'      : '8100403E', 
            '1280x720@50Hz'      : '80000013', 
            '1280x720@60Hz'      : '80000004', 
            '1280x720@75Hz'      : '81004089', 
            '1280x768@50Hz'      : '8100407B', 
            '1280x768@60Hz'      : '8100407C', 
            '1280x768@75Hz'      : '81004015', 
            '1280x800@60Hz'      : '81004040', 
            '1280x800@75Hz'      : '81004042', 
            '1280x960@50Hz'      : '81004063', 
            '1280x960@60Hz'      : '81004064', 
            '1280x1024@50Hz'     : '81004076', 
            '1280x1024@60Hz'     : '81004077', 
            '1280x1024@75Hz'     : '81004078', 
            '1360x768@50Hz'      : '8100408C', 
            '1360x768@60Hz'      : '8100408D', 
            '1360x768@75Hz'      : '8100408E', 
            '1366x768@60Hz'      : '81004048', 
            '1440x900@60Hz'      : '81004021', 
            '1440x900@75Hz'      : '81004023', 
            '1600x900@60Hz'      : '8100404E', 
            '1600x1024@60Hz'     : '810040EF', 
            '1600x1200@50Hz'     : '8100406A', 
            '1600x1200@60Hz'     : '8100406B', 
            '1680x1050@50Hz'     : '810040C1', 
            '1680x1050@60Hz'     : '810040C2', 
            '1920x1080i@25Hz'    : '80000014', 
            '1920x1080i@29.97Hz' : '80000005', 
            '1920x1080@50Hz'     : '8000001F', 
            '1920x1080@60Hz'     : '80000010', 
            '1920x1200@50Hz'     : '810040C8', 
            '1920x1200@60Hz'     : '81004032', 
            '2560x1080@24Hz'     : '81000071', 
            '2560x1080@25Hz'     : '81000072', 
            '2560x1080@30Hz'     : '81000073', 
            '2560x1080@50Hz'     : '81000074', 
            '2560x1080@60Hz'     : '81000075', 
            '2560x1200@30Hz'     : '810040F0', 
            '2560x1200@60Hz'     : '810040F1', 
            '2560x1600@60Hz'     : '81004053', 
            '3840x2160@24Hz'     : '8000005D', 
            '3840x2160@25Hz'     : '8000005E', 
            '3840x2160@30Hz'     : '8000005F', 
            '4096x2160@24Hz'     : '80000062', 
            '4096x2160@25Hz'     : '80000063', 
            '4096x2160@30Hz'     : '80000064'
        }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'SET /MEDIA/VIDEO/O1/SCALER.OutputResolution={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'GET /MEDIA/VIDEO/O1.Resolution\r\n'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('OutputResolution', value, None)

    def SetOutputScalingMode(self, value, qualifier):

        ValueStateValues = {
            'Pass Through' : 'OFF', 
            'Auto'         : 'EDID', 
            'Manual'       : 'MANUAL'
        }

        if value in ValueStateValues:
            OutputScalingModeCmdString = 'SET /MEDIA/VIDEO/O1/SCALER.ScalingMode={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('OutputScalingMode', OutputScalingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputScalingMode')

    def UpdateOutputScalingMode(self, value, qualifier):

        OutputScalingModeCmdString = 'GET /MEDIA/VIDEO/O1/SCALER.ScalingMode\r\n'
        self.__UpdateHelper('OutputScalingMode', OutputScalingModeCmdString, value, qualifier)

    def __MatchOutputScalingMode(self, match, tag):

        ValueStateValues = {
            'OFF'    : 'Pass Through', 
            'EDID'   : 'Auto', 
            'MANUAL' : 'Manual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputScalingMode', value, None)

    def SetOutputSignalType(self, value, qualifier):

        ValueStateValues = {
            'HDMI' : 'HDMI', 
            'DVI'  : 'DVI'
        }

        if value in ValueStateValues:
            OutputSignalTypeCmdString = 'SET /MEDIA/VIDEO/O1/SCALER.SignalType={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('OutputSignalType', OutputSignalTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputSignalType')

    def UpdateOutputSignalType(self, value, qualifier):

        OutputSignalTypeCmdString = 'GET /MEDIA/VIDEO/O1/SCALER.SignalType\r\n'
        self.__UpdateHelper('OutputSignalType', OutputSignalTypeCmdString, value, qualifier)

    def __MatchOutputSignalType(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('OutputSignalType', value, None)

    def SetUSBConnect(self, value, qualifier):

        USBConnectCmdString = 'CALL /MEDIA/KM:acquireControl(true)\r\n'
        self.__SetHelper('USBConnect', USBConnectCmdString, value, qualifier)

    def UpdateUSBConnectionStatus(self, value, qualifier):

        USBConnectionStatusCmdString = 'GET /MEDIA/KM.Controlling\r\n'
        self.__UpdateHelper('USBConnectionStatus', USBConnectionStatusCmdString, value, qualifier)

    def __MatchUSBConnectionStatus(self, match, tag):

        ValueStateValues = {
            '1'     : 'Connected', 
            'true'  : 'Connected', 
            '0'     : 'Disconnected',
            'false' : 'Disconnected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBConnectionStatus', value, None)

    def SetVideoStreamID(self, value, qualifier):

        if 1 <= value <= 9999:
            VideoStreamIDCmdString = 'SET /SYS/MB/PHY.VideoChannelId={}\r\n'.format(value)
            self.__SetHelper('VideoStreamID', VideoStreamIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoStreamID')

    def UpdateVideoStreamID(self, value, qualifier):

        VideoStreamIDCmdString = 'GET /SYS/MB/PHY.VideoChannelId\r\n'
        self.__UpdateHelper('VideoStreamID', VideoStreamIDCmdString, value, qualifier)

    def __MatchVideoStreamID(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VideoStreamID', value, None)

    def SetVideoWallLayout(self, value, qualifier):

        ColNum = qualifier['Number of Column']
        RowNum = qualifier['Number of Row']
        ColPos = qualifier['Column Position']
        RowPos = qualifier['Row Position']
        SWidth = qualifier['Screen Width']
        SHeight = qualifier['Screen Height']
        HGap = qualifier['Horizontal Gap']
        VGap = qualifier['Vertical Gap']
        TBezel = qualifier['Top Bezel']
        BBezel = qualifier['Bottom Bezel']
        LBezel = qualifier['Left Bezel']
        RBezel = qualifier['Right Bezel']

        if ColNum and RowNum and ColPos and RowPos and SWidth and SHeight and HGap and VGap and TBezel and BBezel and LBezel and RBezel:
            VideoWallLayoutCmdString = 'SET /MEDIA/VIDEO/O1/VIDEOWALL.Layout={};{};{};{};{};{};{};{};{};{};{};{};\r\n'.format(ColNum, RowNum,
                                        ColPos, RowPos, SWidth, SHeight, HGap, VGap, TBezel, BBezel, LBezel, RBezel)
            self.__SetHelper('VideoWallLayout', VideoWallLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallLayout')

    def SetVideoWallName(self, value, qualifier):

        if value:
            VideoWallNameCmdString = 'SET /MEDIA/VIDEO/O1/VIDEOWALL.Name={}\r\n'.format(value)
            self.__SetHelper('VideoWallName', VideoWallNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallName')

    def SetWorkingMode(self, value, qualifier):

        ValueStateValues = {
            'Unicast'   : '0', 
            'Multicast' : '1'
        }

        if value in ValueStateValues:
            WorkingModeCmdString = 'SET /MANAGEMENT/MULTICAST.MulticastMode={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('WorkingMode', WorkingModeCmdString, value, qualifier)
            self.Send('CALL /MANAGEMENT/MULTICAST:applySettings(1)\r\n')  #This command must be sent to change working mode
        else:
            self.Discard('Invalid Command for SetWorkingMode')

    def UpdateWorkingMode(self, value, qualifier):

        WorkingModeCmdString = 'GET /MANAGEMENT/MULTICAST.MulticastMode\r\n'
        self.__UpdateHelper('WorkingMode', WorkingModeCmdString, value, qualifier)

    def __MatchWorkingMode(self, match, tag):

        ValueStateValues = {
            '0'     : 'Unicast', 
            'false' : 'Unicast', 
            '1'     : 'Multicast',
            'true'  : 'Multicast'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WorkingMode', value, None)

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

        self.Error(['There is error in the command or response.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' not in self.ConnectionType:
            self.SetLogin(None, None)
    
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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