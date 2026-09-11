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
        self._DeviceID = b'\x01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FadeMode': {'Parameters':['Type'], 'Status': {}},
            'Input': { 'Status': {}},
            'InputBrightness': {'Parameters':['Input Board'], 'Status': {}},
            'MultiWindow': {'Parameters':['Window 1','Window 2','Window 3','Window 4'], 'Status': {}},
            'MultiWindowSignalSwitching': {'Parameters':['Window 1 Signal','Window 2 Signal','Window 3 Signal','Window 4 Signal'], 'Status': {}},
            'OutputDisplayMode': {'Parameters':['Mode'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'OutputSelection': {'Parameters':['Mode'], 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': {'Parameters':['Input Board'], 'Status': {}},
            }
                                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x3A\x01\x04\x01\x00\xFE\x1A\x00\x00[\x00-\xFF]{10}([\x00-\xFF])[\x00-\xFF]{6}'), self.__MatchOutputResolution, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <=250:
            self._DeviceID = bytes([int(value)])

    def SetFadeMode(self, value, qualifier):

        TypeStates = {
            'Fade In'  : b'\x80', 
            'Fade Out' : b'\x81'
        }

        ValueStateValues = {
            'Seamless Switching' : b'\x00\x3A', 
            '1s'                 : b'\x01\x3A', 
            '2s'                 : b'\x02\x3A', 
            '3s'                 : b'\x03\x3A'
        }

        type_ = qualifier['Type']
        if type_ in TypeStates:
            FadeModeCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x1D\x0A' + TypeStates[type_] + ValueStateValues[value]
            self.__SetHelper('FadeMode', FadeModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFadeMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'SDI 1'         : b'\x00\x04\x3A', 
            'HDMI 1'        : b'\x00\x03\x3A', 
            'CVBS 1'        : b'\x00\x01\x3A', 
            'SDI 2'         : b'\x01\x04\x3A', 
            'HDMI 4'        : b'\x01\x03\x3A', 
            'CVBS 2'        : b'\x01\x01\x3A', 
            'HDMI 2'        : b'\x02\x05\x3A', 
            'HDMI 3'        : b'\x02\x06\x3A', 
            'DisplayPort 1' : b'\x02\x07\x3A', 
            'HDMI 5'        : b'\x03\x05\x3A', 
            'HDMI 6'        : b'\x03\x06\x3A', 
            'DisplayPort 2' : b'\x03\x07\x3A'
        }

        InputCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x01\x0A' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetInputBrightness(self, value, qualifier):

        InputBoardStates = {
            'A' : b'\x00', 
            'B' : b'\x01'
        }

        InBoard = qualifier['Input Board']
        if 0 <= value <= 100 and InBoard in InputBoardStates:
            InputBrightnessCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x09\x0A' + bytes([value, 0x3A])
            self.__SetHelper('InputBrightness', InputBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputBrightness')

    def SetMultiWindow(self, value, qualifier):

        WindowStates = {
            'On'  : '1', 
            'Off' : '0'
        }

        win1 = qualifier['Window 1']
        win2 = qualifier['Window 2']
        win3 = qualifier['Window 3']
        win4 = qualifier['Window 4']
        if win1 in WindowStates and win2 in WindowStates and win3 in WindowStates and win4 in WindowStates:
            byte7 = int('0000{}{}{}{}'.format(WindowStates[win4], WindowStates[win3], WindowStates[win2], WindowStates[win1]),2)
            MultiWindowCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x14\x09'+ bytes([byte7, 0x3A])
            self.__SetHelper('MultiWindow', MultiWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiWindow')

    def SetMultiWindowSignalSwitching(self, value, qualifier):

        Window12States = {
            'In C' : b'\x02', 
            'In D' : b'\x03'
        }

        Window34States = {
            'In A' : b'\x00', 
            'In B' : b'\x01'
        }

        win1 = qualifier['Window 1 Signal']
        win2 = qualifier['Window 2 Signal']
        win3 = qualifier['Window 3 Signal']
        win4 = qualifier['Window 4 Signal']
        if win1 in Window12States and win2 in Window12States and win3 in Window34States and win4 in Window34States:
            MultiWindowSignalSwitchingCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x13\x0C' + Window12States[win1]\
                                                + Window12States[win2] + Window34States[win3] + Window34States[win4] + b'\x3A'
            self.__SetHelper('MultiWindowSignalSwitching', MultiWindowSignalSwitchingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiWindowSignalSwitching')

    def SetOutputDisplayMode(self, value, qualifier):

        ModeStates = {
            'Multi Window' : b'\x00', 
            'Output'       : b'\x80'
        }

        mode = qualifier['Mode']
        if mode in ModeStates and 0 <= int(value) <= 12:
            OutputDisplayModeCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x11\x0A'+ ModeStates[mode] + bytes([int(value), 0x3A])
            self.__SetHelper('OutputDisplayMode', OutputDisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputDisplayMode')

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '1440x1440@60Hz' : b'\x01\x3A', 
            '1920x1080@60Hz' : b'\x06\x3A', 
            '2160x960@60Hz'  : b'\x0A\x3A', 
            '1200x1600@60Hz' : b'\x0B\x3A', 
            '1600x1344@60Hz' : b'\x0C\x3A', 
            '2160x1160@50Hz' : b'\x10\x3A', 
            '2048x1200@50Hz' : b'\x11\x3A', 
            '1920x1200@50Hz' : b'\x13\x3A', 
            '1920x1080@50Hz' : b'\x14\x3A', 
            '1680x1440@50Hz' : b'\x15\x3A', 
            '1440x1680@50Hz' : b'\x17\x3A', 
            '1200x1960@50Hz' : b'\x18\x3A',
            'Custom'         : b'\x09\x3A'
        }

        OutputResolutionCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x1F\x0A\x0D' + ValueStateValues[value] 
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\xFE\x0A\x00\x00\x3A'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            8   : '1440x1440@60Hz', 
            24  : '1920x1080@60Hz', 
            40  : '2160x960@60Hz', 
            88  : '1200x1600@60Hz', 
            96  : '1600x1344@60Hz', 
            128 : '2160x1160@50Hz', 
            136 : '2048x1200@50Hz', 
            152 : '1920x1200@50Hz', 
            160 : '1920x1080@50Hz', 
            168 : '1680x1440@50Hz', 
            184 : '1440x1680@50Hz', 
            216 : '1200x1960@50Hz',
            48  : 'Custom'
        }

        temp = (ord(match.group(1)) & 0xF8).decode()
        value = ValueStateValues[temp]
        self.WriteStatus('OutputResolution', value, None)

    def SetOutputSelection(self, value, qualifier):

        ModeStates = {
            'Multi Window' : b'\x00', 
            'Output A'     : b'\x80', 
            'Output B'     : b'\xC0'
        }

        ValueStateValues = {
            '1' : b'\x00\x3A', 
            '2' : b'\x01\x3A', 
            '3' : b'\x02\x3A', 
            '4' : b'\x03\x3A'
        }

        mode = qualifier['Mode']
        if mode in ModeStates:
            OutputSelectionCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x10\x0A' + ModeStates[mode] + ValueStateValues[value] 
            self.__SetHelper('OutputSelection', OutputSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputSelection')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'SDI 1'   : b'\x00\x04\x3A', 
            'HDMI 1' : b'\x00\x03\x3A', 
            'CVBS 1' : b'\x00\x01\x3A', 
            'SDI 2'   : b'\x01\x04\x3A', 
            'HDMI 4' : b'\x01\x03\x3A', 
            'CVBS 2' : b'\x01\x01\x3A'
        }

        PIPInputCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x03\x0A' + ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        InputBoardStates = {
            'A' : b'\x00', 
            'B' : b'\x01'
        }

        ValueStateValues = {
            'On'  : b'\x01\x3A', 
            'Off' : b'\x00\x3A'
        }

        InBoard = qualifier['Input Board']
        if InBoard in InputBoardStates:
            PIPModeCmdString = b'\x3A' + self.DeviceID + b'\x04\x01\x00\x02\x0A' + InputBoardStates[InBoard] + ValueStateValues[value]
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

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

