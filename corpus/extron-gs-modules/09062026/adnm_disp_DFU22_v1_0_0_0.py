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
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


        self.AddMatchString(re.compile(b'(\x48\x44\x4D\x49\x2D\x31|\x48\x44\x4D\x49\x2D\x32|\x48\x44\x4D\x49\x2D\x33|\x43\x4F\x4D\x50\x4F\x4E\x45\x4E\x54|\x44\x4D\x50)\x0D\x0A'), self.__MatchInput, None)
        self.AddMatchString(re.compile(b'\xBB\x00\x20\x02(\x02|\x03)\x7F\xA3'), self.__MatchPower, None)



    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'    : b'\xBB\x00\x20\x02\x00\x30\x52', 
            '16:9'   : b'\xBB\x00\x20\x02\x00\x31\x53', 
            'Zoom 1' : b'\xBB\x00\x20\x02\x00\x32\x54', 
            'Zoom 2' : b'\xBB\x00\x20\x02\x00\x33\x55'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)


    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'    : b'\xBB\x00\x0B\x03\x1C\x00\x01\x2B', 
            'HDMI 2'    : b'\xBB\x00\x0B\x03\x1C\x00\x00\x2A', 
            'HDMI 3'    : b'\xBB\x00\x0B\x03\x1C\x00\x02\x2C', 
            'Component' : b'\xBB\x00\x0B\x03\x1C\x00\x03\x2D', 
            'DMP'       : b'\xBB\x00\x0B\x03\x1C\x00\x07\x31'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBB\x00\x20\x02\x00\x7E\xA0'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x48\x44\x4D\x49\x2D\x31'             : 'HDMI 1', 
            '\x48\x44\x4D\x49\x2D\x32'             : 'HDMI 2', 
            '\x48\x44\x4D\x49\x2D\x33'             : 'HDMI 3', 
            '\x43\x4F\x4D\x50\x4F\x4E\x45\x4E\x54' : 'Component', 
            '\x44\x4D\x50'                         : 'DMP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : b'\xBB\x00\x20\x02\x00\x28\x4A', 
            '1' : b'\xBB\x00\x20\x02\x00\x21\x43', 
            '2' : b'\xBB\x00\x20\x02\x00\x22\x44', 
            '3' : b'\xBB\x00\x20\x02\x00\x23\x45', 
            '4' : b'\xBB\x00\x20\x02\x00\x25\x47', 
            '5' : b'\xBB\x00\x20\x02\x00\x26\x48', 
            '6' : b'\xBB\x00\x20\x02\x00\x27\x49', 
            '7' : b'\xBB\x00\x20\x02\x00\x29\x4B', 
            '8' : b'\xBB\x00\x20\x02\x00\x2A\x4C', 
            '9' : b'\xBB\x00\x20\x02\x00\x2B\x4D'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)


    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'      : b'\xBB\x00\x20\x02\x00\x01\x23', 
            'Down'    : b'\xBB\x00\x20\x02\x00\x02\x24', 
            'Left'    : b'\xBB\x00\x20\x02\x00\x00\x22', 
            'Right'   : b'\xBB\x00\x20\x02\x00\x04\x26', 
            'OK/Info' : b'\xBB\x00\x20\x02\x00\x03\x25', 
            'Exit'    : b'\xBB\x00\x20\x02\x00\x48\x6A'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetMute(self, value, qualifier):

        MuteCmdString = b'\xBB\x00\x20\x02\x00\x06\x28'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)


    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = b'\xBB\x00\x20\x02\x00\x05\x27'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBB\x00\x1F\x01\x00\x20', 
            'Off' : b'\xBB\x00\x1F\x01\x01\x21', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        PowerCmdString = b'\xBB\x00\x20\x02\x00\x7F\xA1'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x03' : 'On', 
            '\x02' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)


    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\xBB\x00\x20\x02\x00\x04\x26', 
            'Down' : b'\xBB\x00\x20\x02\x00\x00\x22'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)


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