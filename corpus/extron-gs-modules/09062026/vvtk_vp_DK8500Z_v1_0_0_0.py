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
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LaserHours': { 'Status': {}},
            'LaserMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'RemoteLock': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OP ASPECT = (0|1|2|3|4|5|6|7|8)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'OP FREEZE = (0|1)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'OP INPUT\.SEL = (0|1|3|4)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'OP LASER\.HOURS = (\d+)\r'), self.__MatchLaserHours, None)
            self.AddMatchString(re.compile(b'OP LASER\.MODE = (0|1|2)\r'), self.__MatchLaserMode, None)
            self.AddMatchString(re.compile(b'OP PIP\.SEL = (0|1|3|4)\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'OP PIP = (0|1)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'OP PIP\.POS = (0|1|2|3|4)\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'OP STATUS = (0|1|2|3|4)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'OP IR\.ENABLE = (0|1)\r'), self.__MatchRemoteLock, None)
            self.AddMatchString(re.compile(b'OP BLANK = (0|1)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'NA\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '5:4'       : '0', 
            '4:3'       : '1', 
            '16:10'     : '2', 
            '16:9'      : '3', 
            '1.88'      : '4', 
            '2.35'      : '5', 
            'LetterBox' : '6', 
            'Source'    : '7', 
            'Native'    : '8'
            }

        AspectRatioCmdString = 'op aspect = {0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'op aspect ?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '0' : '5:4', 
            '1' : '4:3', 
            '2' : '16:10', 
            '3' : '16:9', 
            '4' : '1.88', 
            '5' : '2.35', 
            '6' : 'LetterBox', 
            '7' : 'Source', 
            '8' : 'Native'
            }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'op auto.mg\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On'    : '1', 
            'Off'   : '0'
            }

        FreezeCmdString = 'op freeze = {0}\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'op freeze ?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'HDMI 1'    : '0', 
            'HDMI 2'    : '1', 
            'HDBaseT'   : '3', 
            '3G-SDI'    : '4'
            }

        InputCmdString = 'op input.sel = {0}\r'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = 'op input.sel ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '0' : 'HDMI 1', 
            '1' : 'HDMI 2', 
            '3' : 'HDBaseT', 
            '4' : '3G-SDI'
            }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = 'op laser.hours ?\r'
        self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)

    def __MatchLaserHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserHours', value, None)

    def SetLaserMode(self, value, qualifier):

        LaserModeState = {
            'Eco'       : '0', 
            'Normal'    : '1', 
            'Custom'    : '2'
            }

        LaserModeCmdString = 'op laser.mode = {0}\r'.format(LaserModeState[value])
        self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)
    def UpdateLaserMode(self, value, qualifier):

        LaserModeCmdString = 'op laser.mode ?\r'
        self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def __MatchLaserMode(self, match, tag):

        LaserModeState = {
            '0' : 'Eco', 
            '1' : 'Normal', 
            '2' : 'Custom'
            }

        value = LaserModeState[match.group(1).decode()]
        self.WriteStatus('LaserMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up'    : 'ky up\r', 
            'Down'  : 'ky down\r', 
            'Left'  : 'ky left\r', 
            'Right' : 'ky right\r', 
            'Enter' : 'ky enter\r', 
            'Menu'  : 'ky menu\r', 
            'Exit'  : 'ky exit\r'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'HDMI 1'    : '0', 
            'HDMI 2'    : '1', 
            'HDBaseT'   : '3', 
            '3G-SDI'    : '4'
            }

        PIPInputCmdString = 'op pip.sel = {0}\r'.format(PIPInputState[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'op pip.sel ?\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPInputState = {
            '0' : 'HDMI 1', 
            '1' : 'HDMI 2', 
            '3' : 'HDBaseT', 
            '4' : '3G-SDI'
            }

        value = PIPInputState[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On'    : '1', 
            'Off'   : '0'
            }

        PIPModeCmdString = 'op pip = {0}\r'.format(PIPModeState[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = 'op pip ?\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = PIPModeState[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Top Left'      : '0', 
            'Top Right'     : '1', 
            'Bottom Left'   : '2', 
            'Bottom Right'  : '3', 
            'PBP'           : '4'
            }

        PIPPositionCmdString = 'op pip.pos = {0}\r'.format(PIPPositionState[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = 'op pip.pos ?\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionState = {
            '0' : 'Top Left', 
            '1' : 'Top Right', 
            '2' : 'Bottom Left', 
            '3' : 'Bottom Right', 
            '4' : 'PBP'
            }

        value = PIPPositionState[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : 'op power.on\r', 
            'Off'   : 'op power.off\r', 
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'op status ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '2' : 'On', 
            '0' : 'Off', 
            '1' : 'Warming Up', 
            '3' : 'Cooling Down', 
            '4' : 'Warning'
            }


        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRemoteLock(self, value, qualifier):

        RemoteLockState = {
            'On'    : '1', 
            'Off'   : '0'
            }

        RemoteLockCmdString = 'op ir.enable = {0}\r'.format(RemoteLockState[value])
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)
    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = 'op ir.enable ?\r'
        self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def __MatchRemoteLock(self, match, tag):

        RemoteLockState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = RemoteLockState[match.group(1).decode()]
        self.WriteStatus('RemoteLock', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On'    : '1', 
            'Off'   : '0'
            }

        VideoMuteCmdString = 'op blank = {0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'op blank ?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = VideoMuteState[match.group(1).decode()]
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

            

    def __MatchError(self, match, tag):

        value = match.group(0).decode()
        self.Error(['Failed to execute command : {0}'.format(value)])

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

