from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ShadeControl': {'Parameters': ['Shade Group'], 'Status': {}},
            'ShadePreset': {'Parameters': ['Shade Group'], 'Status': {}},
        }

    def SetShadeControl(self, value, qualifier):

        state = {
            'Stop': '28',
            'Extend': '4E',
            'Retract': '4B',
            'Clear Override': '4C'
        }[value]

        shade = qualifier['Shade Group']
        if 1 <= int(shade) <= 99:
            ShadeControlCmdString = ':{}06000100{}--\r\n'.format(shade.zfill(2), state)
            self.__SetHelper('ShadeControl', ShadeControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShadeControl')

    def SetShadePreset(self, value, qualifier):

        state = {
            '1': '1E',
            '2': '1F',
            '3': '20',
            '4': '21',
            '5': '22',
            '6': '23',
            '7': '24',
            '8': '25',
            '9': '26',
            '10': '27',
            'Next': '4F',
            'Previous': '50'
        }[value]

        shade = qualifier['Shade Group']
        if 1 <= int(shade) <= 99:
            ShadePresetCmdString = ':{}06000100{}--\r\n'.format(shade.zfill(2), state)
            self.__SetHelper('ShadePreset', ShadePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShadePreset')

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
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
