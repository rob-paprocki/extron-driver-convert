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
        self.Init_Flag = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Input': { 'Status': {}},
            'IREmulation': { 'Status': {}},
            'Power': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x40\x89\x01\x49\x50(\x36|\x37)\x0A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x50\x57(\x30|\x31|\x32|\x34)\x0A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'PJ_OK'), self.__MatchOnConnectedString, None)
            self.AddMatchString(re.compile(b'PJACK'), self.__MatchReceive, None)
            
        
    def __MatchOnConnectedString(self, match, tag):
        self.Send('PJREQ')

    def __MatchReceive(self, match, tag):

        value = match.group(0).decode()
        if value == 'PJACK':
            self.Init_Flag = True
            self.UpdatePower( None, None)
        else:
            self.Init_Flag = False

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : b'\x21\x89\x01\x49\x50\x36\x0A', 
            'HDMI 2' : b'\x21\x89\x01\x49\x50\x37\x0A'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x3F\x89\x01\x49\x50\x0A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x36' : 'HDMI 1', 
            '\x37' : 'HDMI 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'Standby'        : b'\x21\x89\x01\x52\x43\x37\x33\x30\x36\x0A', 
            'On'             : b'\x21\x89\x01\x52\x43\x37\x33\x30\x35\x0A', 
            'HDMI 1'         : b'\x21\x89\x01\x52\x43\x37\x33\x37\x30\x0A', 
            'HDMI 2'         : b'\x21\x89\x01\x52\x43\x37\x33\x37\x31\x0A', 
            'Info'           : b'\x21\x89\x01\x52\x43\x37\x33\x37\x34\x0A', 
            'Mode 1'         : b'\x21\x89\x01\x52\x43\x37\x33\x44\x38\x0A', 
            'Mode 2'         : b'\x21\x89\x01\x52\x43\x37\x33\x44\x39\x0A', 
            'Mode 3'         : b'\x21\x89\x01\x52\x43\x37\x33\x44\x41\x0A', 
            'Lens Control'   : b'\x21\x89\x01\x52\x43\x37\x33\x33\x30\x0A', 
            'Lens AP.'       : b'\x21\x89\x01\x52\x43\x37\x33\x32\x30\x0A', 
            'ANAMO.'         : b'\x21\x89\x01\x52\x43\x37\x33\x43\x35\x0A', 
            'Hide'           : b'\x21\x89\x01\x52\x43\x37\x33\x31\x44\x0A', 
            'Up'             : b'\x21\x89\x01\x52\x43\x37\x33\x30\x31\x0A', 
            'Down'           : b'\x21\x89\x01\x52\x43\x37\x33\x30\x32\x0A', 
            'Right'          : b'\x21\x89\x01\x52\x43\x37\x33\x33\x34\x0A', 
            'Left'           : b'\x21\x89\x01\x52\x43\x37\x33\x33\x36\x0A', 
            'OK'             : b'\x21\x89\x01\x52\x43\x37\x33\x32\x46\x0A', 
            'Menu'           : b'\x21\x89\x01\x52\x43\x37\x33\x32\x45\x0A', 
            'Back'           : b'\x21\x89\x01\x52\x43\x37\x33\x30\x33\x0A', 
            'Natural'        : b'\x21\x89\x01\x52\x43\x37\x33\x36\x41\x0A', 
            'Cinema'         : b'\x21\x89\x01\x52\x43\x37\x33\x36\x38\x0A', 
            'Picture Mode'   : b'\x21\x89\x01\x52\x43\x37\x33\x46\x34\x0A', 
            'Color Profile'  : b'\x21\x89\x01\x52\x43\x37\x33\x38\x38\x0A', 
            'Gamma Settings' : b'\x21\x89\x01\x52\x43\x37\x33\x46\x35\x0A', 
            'MPC'            : b'\x21\x89\x01\x52\x43\x37\x33\x46\x30\x0A', 
            'C.M.D'          : b'\x21\x89\x01\x52\x43\x37\x33\x38\x41\x0A', 
            'Advanced Menu'  : b'\x21\x89\x01\x52\x43\x37\x33\x37\x33\x0A', 
            'Gamma'          : b'\x21\x89\x01\x52\x43\x37\x33\x37\x35\x0A', 
            'Color Temp'     : b'\x21\x89\x01\x52\x43\x37\x33\x37\x36\x0A', 
            '3D Format'      : b'\x21\x89\x01\x52\x43\x37\x33\x44\x36\x0A', 
            'Pic. Adj'       : b'\x21\x89\x01\x52\x43\x37\x33\x37\x32\x0A'
        }

        IREmulationCmdString = ValueStateValues[value]
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x21\x89\x01\x50\x57\x31\x0A', 
            'Off' : b'\x21\x89\x01\x50\x57\x30\x0A', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

            
        PowerCmdString = b'\x3F\x89\x01\x50\x57\x0A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x31' : 'On', 
            '\x30' : 'Off', 
            '\x32' : 'Cooling Down', 
            '\x34' : 'Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

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

            if self.Init_Flag or 'Serial' in self.ConnectionType:
                self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Init_Flag = False 
        
        
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

