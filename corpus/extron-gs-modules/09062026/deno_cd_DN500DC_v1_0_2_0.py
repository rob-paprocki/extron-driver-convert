from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Unidirectional = 'False'
        self.Models = {}

        self.Commands = {
            'Keypad': {'Parameters': ['CD Number'], 'Status': {}},
            'MediaType': {'Parameters': ['CD Number'], 'Status': {}},
            'Mute': {'Parameters': ['CD Number'], 'Status': {}},
            'PlayMode': {'Parameters': ['CD Number'], 'Status': {}},
            'Transport': {'Parameters': ['CD Number'], 'Status': {}},
        }

    def SetKeypad(self, value, qualifier):

        CDNumberStates = {
            '1': 'A',
            '2': 'B'
        }

        if 0 <= int(value) <= 9:
            KeypadCmdString = 'E{0}{1}\r'.format(CDNumberStates[qualifier['CD Number']], value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMediaType(self, value, qualifier):

        CDNumberStates = {
            '1': 'A',
            '2': 'B'
        }

        ValueStateValues = {
            'CD': 'S',
            'SD Card': 'R',
            'USB': 'T'
        }

        MediaTypeCmdString = 'E{0}{1}\r'.format(CDNumberStates[qualifier['CD Number']], ValueStateValues[value])
        self.__SetHelper('MediaType', MediaTypeCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        CDNumberStates = {
            '1': 'A',
            '2': 'B'
        }

        MuteCmdString = 'E{0}K\r'.format(CDNumberStates[qualifier['CD Number']])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPlayMode(self, value, qualifier):

        CDNumberStates = {
            '1': 'A',
            '2': 'B'
        }

        ValueStateValues = {
            'Play 1': 'U',
            'Repeat': 'L',
            'A-B': 'O'
        }

        PlayModeCmdString = 'E{0}{1}\r'.format(CDNumberStates[qualifier['CD Number']], ValueStateValues[value])
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        CDNumberStates = {
            '1': 'A',
            '2': 'B'
        }

        ValueStateValues = {
            'Play/Pause': 'F',
            'Stop': 'E',
            'Eject': 'G',
            'Up': 'D',
            'Down': 'C',
            'Folder Skip +': 'B',
            'Folder Skip -': 'A',
            'Prog': 'H',
            'ID3': 'I',
            'Find': 'J',
            'Funct': 'M',
            'Display': 'N',
            'Remain': 'V'
        }

        TransportCmdString = 'E{0}{1}\r'.format(CDNumberStates[qualifier['CD Number']], ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if '\x15' or 'BDERBUSY' or '+ER' in response:
            self.Error(['Error in Command {0}'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if res:
                res = self.__CheckResponseForErrors(command, res)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

