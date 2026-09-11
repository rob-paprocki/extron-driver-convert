from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DeviceID = '01'

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 99:
            self._DeviceID = '{0:02d}'.format(int(value))
        else:
            self.Error(['Device ID out of range.'])

    def SetAspectRatio(self, value, qualifier):

        Values = {
            'Auto': '0',
            '4:3': '1',
            '16:9': '2',
            '14:9': '3',
            'Zoom 1': '4',
            'Zoom 2': '5',
            'Spectacle': '6'
        }

        CmdString = 'kc {0} 0{1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        Values = {'On': '1', 'Off': '0'}
        CmdString = 'km {0} 0{1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        Values = {
            'PC': '7',
            'HDMI 1': '9',
            'HDMI 2': 'a',
            'HDMI 3': 'b',
            'DisplayPort': 'c'
        }

        CmdString = 'kb {0} 0{1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        Values = {
            'Menu': '95',
            'Enter': '8c',
            'Exit': '96',
            'Left': '8f',
            'Right': '90',
            'Up': '8d',
            'Down': '8e'
        }

        CmdString = 'mc {0} {1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        Values = {'On': '0', 'Off': '1'}
        CmdString = 'ke {0} 0{1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('Mute', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Values = {'On': '1', 'Off': '0'}
        CmdString = 'ka {0} 0{1}'.format(self._DeviceID, Values[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}'.format(self._DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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
