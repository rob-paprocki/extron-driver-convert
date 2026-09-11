from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'InputGain': {'Parameters':['Channel'], 'Status': {}},
            'InputMute': {'Parameters':['Channel'], 'Status': {}},
            'Mode': {'Status': {}},
            'OutputLevel': {'Parameters':['Channel'], 'Status': {}},
            'OutputMute': {'Parameters':['Channel'], 'Status': {}},
            'PhantomPower': {'Parameters':['Channel'], 'Status': {}},
            'Scene': {'Status': {}},
            }

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On'  : 1, 
            'Off' : 0
        }

        State = States[value]

        Chk = 0x44 + 0x53 + 0x01 + 0x37 + State
        Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
        CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x37' + bytes([State, Chk]) + b'\x55\xAA'
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetInputGain(self, value, qualifier):
        Channel = int(qualifier['Channel'])

        if 0 <= value <= 31 and 1 <= Channel <= 8:
            DataNo = Channel + 8
            Chk = 0x44 + 0x53 + 0x01 + DataNo + value
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01' + bytes([DataNo, value, Chk]) + b'\x55\xAA'
            self.__SetHelper('InputGain', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def SetInputMute(self, value, qualifier):
        Channel = int(qualifier['Channel'])

        States = {
            'On'  : 1, 
            'Off' : 0
        }

        State = States[value]

        if 1 <= Channel <= 8:
            DataNo = Channel + 24
            Chk = 0x44 + 0x53 + 0x01 + DataNo + State
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01' + bytes([DataNo, State, Chk]) + b'\x55\xAA'
            self.__SetHelper('InputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMute')


    def SetMode(self, value, qualifier):

        States = {
            'Mic'   : b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x31\x00\x37\x55\xAA', 
            'A'     : b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x31\x01\x36\x55\xAA', 
            'B'     : b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x31\x02\x35\x55\xAA',  
            'C'     : b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x31\x03\x34\x55\xAA',  
            'D'     : b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x31\x04\x33\x55\xAA',  
        }

        self.__SetHelper('Mode', States[value], value, qualifier)


    def SetOutputLevel(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        if 0 <= value <= 31 and 1 <= Channel <= 8:
            DataNo = Channel + 32
            Chk = 0x44 + 0x53 + 0x01 + DataNo + value
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01' + bytes([DataNo, value, Chk]) + b'\x55\xAA'
            self.__SetHelper('OutputLevel', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLevel')

    def SetOutputMute(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        States = {
            'On'  : 1, 
            'Off' : 0
        }

        State = States[value]

        if 1 <= Channel <= 8:
            DataNo = Channel + 40
            Chk = 0x44 + 0x53 + 0x01 + DataNo + State
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01' + bytes([DataNo, State, Chk]) + b'\x55\xAA'
            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def SetPhantomPower(self, value, qualifier):

        Channel = int(qualifier['Channel'])

        States = {
            'On'  : 1, 
            'Off' : 0
        }

        State = States[value]

        if 1 <= Channel <= 8:
            DataNo = Channel + 55
            Chk = 0x44 + 0x53 + 0x01 + DataNo + State
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01' + bytes([DataNo, State, Chk]) + b'\x55\xAA'
            self.__SetHelper('PhantomPower', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPhantomPower')

    def SetScene(self, value, qualifier):

        Scene = int(value)

        if 0 <= Scene <= 19:
            Chk = 0x44 + 0x53 + 0x01 + 0x32 + Scene
            Chk = ( (Chk ^ 0xFF) + 1 ) & 0xFF
            CmdString = b'\xAA\x55\x00\x05\x00\x00\x00\x01\x44\x53\x01\x32' + bytes([Scene, Chk]) + b'\x55\xAA'
            self.__SetHelper('Scene', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetScene')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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