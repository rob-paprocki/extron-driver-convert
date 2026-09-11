from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AlwaysOnTop': {'Status': {}},
            'FrameRate': {'Status': {}},
            'MaintainAspectRatio': {'Parameters': ['Width', 'Height'], 'Status': {}},
            'MenuBar': {'Status': {}},
            'ShowState': {'Status': {}},
            'WindowID': {'Status': {}},
            'WindowStyle': {'Status': {}},
            'WindowWall': {'Parameters': ['Top', 'Left', 'Width', 'Height'], 'Status': {}}
        }

    def SetAlwaysOnTop(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        AlwaysOnTopCmdString = 'AlwaysOnTop={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AlwaysOnTop', AlwaysOnTopCmdString, value, qualifier)

    def SetFrameRate(self, value, qualifier):

        ValueStateValues = {
            'Show': 'On',
            'Hide': 'Off'
        }

        FrameRateCmdString = 'ShowFrameRate={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('FrameRate', FrameRateCmdString, value, qualifier)

    def SetMaintainAspectRatio(self, value, qualifier):

        if value == 'Source' and 1 <= qualifier['Width'] <= 65535 and 1 <= qualifier['Height'] <= 65535:
            MaintainAspectRatioCmdString = 'AspectRatio={0},{1},{2}\r\n'.format(value, qualifier['Width'], qualifier['Height'])
            self.__SetHelper('MaintainAspectRatio', MaintainAspectRatioCmdString, value, qualifier)
        elif value in ['On', 'Off'] and qualifier['Width'] == 0 and qualifier['Height'] == 0:
            MaintainAspectRatioCmdString = 'AspectRatio={0},,\r\n'.format(value)
            self.__SetHelper('MaintainAspectRatio', MaintainAspectRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMaintainAspectRatio')

    def SetMenuBar(self, value, qualifier):

        ValueStateValues = {
            'Show': 'On',
            'Hide': 'Off'
        }

        MenuBarCmdString = 'ShowMenuBar={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuBar', MenuBarCmdString, value, qualifier)

    def SetShowState(self, value, qualifier):

        ValueStateValues = {
            'Minimize': 'Minimised',
            'Restore': 'Restored',
            'Maximize': 'Maximised',
            'Show': 'Show',
            'Hide': 'Hide'
        }

        ShowStateCmdString = 'ShowState={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('ShowState', ShowStateCmdString, value, qualifier)

    def SetWindowID(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 65535
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            WindowIDCmdString = 'ID={0}\r\n'.format(value)
            self.__SetHelper('WindowID', WindowIDCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWindowID')

    def SetWindowStyle(self, value, qualifier):

        ValueStateValues = {
            'Border & Title Bar': 'BorderAndTitleBar',
            'Border': 'BorderOnly',
            'No Border or Title Bar': 'NoBorderOrTitleBar'
        }

        WindowStyleCmdString = 'WindowStyle={0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('WindowStyle', WindowStyleCmdString, value, qualifier)

    def SetWindowWall(self, value, qualifier):

        if -65535 <= qualifier['Top'] <= 65535 and -65535 <= qualifier['Left'] <= 65535 and 1 <= qualifier['Width'] <= 65535 and 1 <= qualifier['Height'] <= 65535:
            WindowWallCmdString = 'Window={0},{1},{2},{3}\r\n'.format(qualifier['Top'], qualifier['Left'], qualifier['Width'], qualifier['Height'])
            self.__SetHelper('WindowWall', WindowWallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWindowWall')

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
