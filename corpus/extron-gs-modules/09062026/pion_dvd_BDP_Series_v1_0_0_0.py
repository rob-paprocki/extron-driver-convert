from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ExecutiveMode': {'Status': {}},
            'MenuCall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Repeat': {'Status': {}},
            'Transport': {'Status': {}},
        }

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '/A181AF22/RU\r'
        if self.ConnectionType == 'Ethernet':
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetMenuCall(self, value, qualifier):

        MenuCallStateValues = {
            'Menu': '/A181AFB0/RU\r',
            'Pop-Up Menu': '/A181AFB9/RU\r',
            'Top Menu': '/A181AFB4/RU\r',
            'Return': '/A181AFF4/RU\r',
        }
        MenuCallCmdString = MenuCallStateValues[value]
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': '/A184FFFF/RU\r',
            'Down': '/A185FFFF/RU\r',
            'Left': '/A187FFFF/RU\r',
            'Right': '/A186FFFF/RU\r',
            'Enter': '/A181AFEF/RU\r',
            'Exit': '/A181AF20/RU\r',
            'Function': '/A181AFB3/RU\r',
        }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '/A181AFBA/RU\r',
            'Off': '/A181AFBB/RU\r',
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        RepeatCmdString = '/A181AFE8/RU\r'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        TransportStateValues = {
            'Play': '/A181AF39/RU\r',
            'Stop': '/A181AF38/RU\r',
            'Pause': '/A181AF3A/RU\r',
            'FFwd': '/A181AFE9/RU\r',
            'Rew': '/A181AFEA/RU\r',
            'Next': '/A181AF3D/RU\r',
            'Previous': '/A181AF3E/RU\r',
            'Open/Close': '/A181AFB6/RU\r',
        }
        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
