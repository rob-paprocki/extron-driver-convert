from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'NewWindow'			: {'Parameters': ['Type', 'Window ID'], 'Status': {}},
            'SelectWindowInput'	: {'Parameters': ['Window ID'], 'Status': {}},
            'SetWindowChannel'	: {'Parameters': ['Type', 'Window ID'], 'Status': {}},
            'SetWindowState'	: {'Parameters': ['Window ID', 'X Coordinate', 'Y Coordinate', 'Horizontal Size', 'Vertical Size'], 'Status': {}},
            'StartWindow'		: {'Parameters': ['Window ID'], 'Status': {}},
        }        

    def SetNewWindow(self, value, qualifier):

        typeVal = {
            'Live Video': 'LiveVideoSys',
            'RGB': 'RGBSys'
        }[qualifier['Type']]

        winID = qualifier['Window ID']

        WindowIDConstraints = {
            'Min': 0,
            'Max': 10000
        }

        if WindowIDConstraints['Min'] <= winID <= WindowIDConstraints['Max']:
            NewWindowCmdString = '+{0} NewWindowWithId '.format(typeVal) + '\x7B' + ' {0} '.format(winID) + '\x7D\r\n'
            self.__SetHelper('NewWindow', NewWindowCmdString, value, qualifier)
        else:
            print('Invalid Command for SetNewWindow')

    def SetSelectWindowInput(self, value, qualifier):

        WindowIDConstraints = {
            'Min': 0,
            'Max': 10000
        }

        winID = qualifier['Window ID']
        if WindowIDConstraints['Min'] <= winID <= WindowIDConstraints['Max']:
            InputCmdString = '+GalWinSys SelectInput ' + '\x7B' + ' {0} '.format(winID) + '\x7D' + ' \"{0}\"\r\n'.format(value)
            self.__SetHelper('SelectWindowInput', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSelectWindowInput')

    def SetSetWindowChannel(self, value, qualifier):

        typeVal = {
            'Live Video': 'LiveVideoSys',
            'RGB': 'RGBSys'
        }[qualifier['Type']]

        winID = qualifier['Window ID']

        WindowIDConstraints = {
            'Min': 0,
            'Max': 10000
        }

        if WindowIDConstraints['Min'] <= winID <= WindowIDConstraints['Max'] and 1 <= int(value) <= 255:
            SetWindowChannelCmdString = '+{0} SetChannel '.format(typeVal) + '\x7B' + ' {0} '.format(winID) + '\x7D' + ' {0}\r\n'.format(value)
            self.__SetHelper('SetWindowChannel', SetWindowChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetWindowChannel')

    def SetSetWindowState(self, value, qualifier):

        winID = qualifier['Window ID']

        xVal = qualifier['X Coordinate']
        yVal = qualifier['Y Coordinate']

        hSize = qualifier['Horizontal Size']
        vSize = qualifier['Vertical Size']

        if 0 <= winID <= 10000 and 0 <= xVal <= 4095 and 0 <= yVal <= 1535 and 0 <= hSize <= 4095 and 0 <= vSize <= 1535:
            SetWindowStateCmdString = '+Window SetState ' + '\x7B \x7B' + ' {0} '.format(winID) + '\x7D 2 1 7183' + ' {0} {1} {2} {3} '.format(xVal, yVal, hSize, vSize) + '\x7B -1 \x7D \x7D\r\n'
            self.__SetHelper('SetWindowState', SetWindowStateCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetWindowState')

    def SetStartWindow(self, value, qualifier):

        WindowIDConstraints = {
            'Min': 0,
            'Max': 10000
        }

        winID = qualifier['Window ID']
        if WindowIDConstraints['Min'] <= winID <= WindowIDConstraints['Max']:
            StartWindowCmdString = '+GalWinSys Start ' + '\x7B' + ' {0} '.format(winID) + '\x7D\r\n'
            self.__SetHelper('StartWindow', StartWindowCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStartWindow')

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
