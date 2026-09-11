from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Models = {
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Display'           : {'Status': {}},
            'Eject'             : {'Status': {}},
            'ESP'               : {'Status': {}},
            'Find'              : {'Status': {}},
            'Function'          : {'Status': {}},
            'Keypad'            : {'Status': {}},
            'Mute'              : {'Status': {}},
            'Program'           : {'Status': {}},
            'Repeat'            : {'Status': {}},
            'Transport'         : {'Status': {}},
            'UserDefinedString' : {'Status': {}}
            }

    def SetDisplay(self, value, qualifier):

        DisplayCmdString = b'EAN\r\n'
        self.__SetHelper('Display', DisplayCmdString, value, qualifier)


    def SetEject(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'EAQ\r\n', 
            'Disable' : 'EAP\r\n'
        }

        EjectCmdString = ValueStateValues[value]
        self.__SetHelper('Eject', EjectCmdString, value, qualifier)

    def SetESP(self, value, qualifier):

        ESPCmdString = 'EAI\r\n'
        self.__SetHelper('ESP', ESPCmdString, value, qualifier)

    def SetFind(self, value, qualifier):

        FindCmdString = 'EAJ\r\n'
        self.__SetHelper('Find', FindCmdString, value, qualifier)

    def SetFunction(self, value, qualifier):

        FunctionCmdString = 'EAM\r\n'
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : 'EA0\r\n', 
            '1' : 'EA1\r\n', 
            '2' : 'EA2\r\n', 
            '3' : 'EA3\r\n', 
            '4' : 'EA4\r\n', 
            '5' : 'EA5\r\n', 
            '6' : 'EA6\r\n', 
            '7' : 'EA7\r\n', 
            '8' : 'EA8\r\n', 
            '9' : 'EA9\r\n'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = 'EAK\r\n'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetProgram(self, value, qualifier):

        ProgramCmdString = 'EAH\r\n'
        self.__SetHelper('Program', ProgramCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        RepeatCmdString = 'EAL\r\n'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Folder Previous' : 'EAA\r\n', 
            'Folder Next'     : 'EAB\r\n', 
            'Skip REV'        : 'EAC\r\n', 
            'Skip CUE'        : 'EAD\r\n', 
            'Stop'            : 'EAE\r\n', 
            'Play/Pause'      : 'EAF\r\n', 
            'Eject'           : 'EAG\r\n'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)
    
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