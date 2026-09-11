from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Input': {'Status': {}},
            'Power': {'Status': {}},
        }

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x42\x30\x30\x30\x30\x03\x1C\x0D',
            'DVI': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x42\x30\x30\x30\x31\x03\x1D\x0D',
            'HDMI': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x42\x30\x30\x30\x32\x03\x1E\x0D',
            'Display Port': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x42\x30\x30\x30\x33\x03\x1F\x0D'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x30\x30\x33\x30\x30\x30\x31\x03\x1D\x0D',
            'Off': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x30\x30\x33\x30\x30\x30\x30\x03\x1C\x0D'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

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
