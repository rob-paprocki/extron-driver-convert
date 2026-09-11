from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Header = b'\x00'
        self.Models = {}

        self.Commands = {
            'Control': {'Parameters': ['Tally 1', 'Tally 2', 'Tally 3', 'Tally 4', 'Brightness'], 'Status': {}},
        }

    @property
    def DisplayAddress(self):
        return self.Header

    @DisplayAddress.setter
    def DisplayAddress(self, value):
        temp = int(value)
        if 0 <= temp <= 126:
            self.Header = pack('>B', temp + 0x80)

    def SetControl(self, value, qualifier):

        TallyStates = {
            'On': '1',
            'Off': '0'
        }

        BrightnessStates = {
            '0': '00',
            '1/7': '10',
            '1/2': '01',
            'Full': '11'
        }

        tally1 = TallyStates[qualifier['Tally 1']]
        tally2 = TallyStates[qualifier['Tally 2']]
        tally3 = TallyStates[qualifier['Tally 3']]
        tally4 = TallyStates[qualifier['Tally 4']]
        brightness = BrightnessStates[qualifier['Brightness']]
        displayData = qualifier['DisplayDataString']
        if tally1 in ['1', '0'] and tally2 in ['1', '0'] and tally3 in ['1', '0'] and tally4 in ['1', '0'] and brightness and len(displayData) == 16:
            controlByte = pack('>B', int('00{0}{1}{2}{3}{4}'.format(brightness, tally4, tally3, tally2, tally1), 2))
            ControlCmdString = self.Header + controlByte + displayData.encode()
            self.__SetHelper('Control', ControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControl')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

        ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
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
