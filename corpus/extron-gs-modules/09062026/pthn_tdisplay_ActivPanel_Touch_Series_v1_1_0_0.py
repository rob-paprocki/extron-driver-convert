from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:

    def __init__(self):
        self.Unidirectional = 'False'
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Lan': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'LAN Not Enable'), self.__MatchError, None)

    def SetInit(self, value, qualifier):
        self.Send(b'\x69\x34\x62')

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x89\x55\x06\x1B'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : b'\x89\x65\x05\x0C', 
            'HDMI 2' : b'\x89\x65\x07\x0A', 
            'HDMI 3' : b'\x89\x65\x09\x08', 
            'HDMI 4' : b'\x89\x65\x0B\x06', 
            'VGA'    : b'\x89\x65\x03\x0E', 
            'AV'     : b'\x89\x55\x0D\x14', 
            'YPbPr'  : b'\x89\x55\x04\x1D'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLan(self, value, qualifier):

        LanCmdString = b'\x69\x34\x62'
        self.__SetHelper('Lan', LanCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : b'\x69\x80\x16', 
            'Left'  : b'\x69\x63\x33', 
            'Right' : b'\x69\x66\x30', 
            'Up'    : b'\x69\x46\x50', 
            'Down'  : b'\x69\x43\x53', 
            'Enter' : b'\x69\x07\x8F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x69\x53\x43', 
            'Off' : b'\x69\x76\x20'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)


    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x69\x82\x14', 
            'Down' : b'\x69\x85\x11'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.SetInit(None, None)

    
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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