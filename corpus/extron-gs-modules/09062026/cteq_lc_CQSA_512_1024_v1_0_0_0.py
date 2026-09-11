from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Color': {'Status': {}},
            'ColorMode': {'Status': {}},
            'CurrentZone': {'Status': {}},
            'Dimmer': {'Status': {}},
            'DimmerConstrained': {'Parameters': ['Dimmer value'], 'Status': {}},
            'Pause': {'Status': {}},
            'Play': {'Status': {}},
            'Speed': {'Status': {}},
            'SpeedConstrained': {'Parameters': ['Speed value'], 'Status': {}},
            'StartScene': {'Parameters': ['Scene'], 'Status': {}},
            'StopScene': {'Status': {}},
        }


    def SetColor(self, value, qualifier):

        Values = {
            'Min': 0,
            'Max': 99
        }

        if Values['Min'] <= int(value) <= Values['Max']:
            ColorCmdString = '\x02CLR{0:02}\x03'.format(int(value))
            self.__SetHelper('Color', ColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColor')

    def SetColorMode(self, value, qualifier):

        Values = {
            'Min': 1,
            'Max': 8
        }

        if Values['Min'] <= int(value) <= Values['Max']:
            ColorModeCmdString = '\x02COLR{0}\x03'.format(value)
            self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorMode')

    def SetCurrentZone(self, value, qualifier):

        ValueStateValues = {
            'A': 'a',
            'B': 'b',
            'C': 'c',
            'D': 'd',
            'E': 'e',
            'F': 'f'
        }

        CurrentZoneCmdString = '\x02ZONE{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('CurrentZone', CurrentZoneCmdString, value, qualifier)

    def SetDimmer(self, value, qualifier):

        ValueStateValues = {
            'Up': '++',
            'Down': '--'
        }

        DimmerCmdString = '\x02DIM{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)

    def SetDimmerConstrained(self, value, qualifier):

        DimmerValues = {
            'Min': 0,
            'Max': 9
        }

        ValueStateValues = {
            'Up': '+',
            'Down': '-'
        }

        dim_val = qualifier['Dimmer value']
        if DimmerValues['Min'] <= int(dim_val) <= DimmerValues['Max']:
            DimmerConstrainedCmdString = '\x02DIM{0}{1}\x03'.format(ValueStateValues[value], dim_val)
            self.__SetHelper('DimmerConstrained', DimmerConstrainedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmerConstrained')

    def SetPause(self, value, qualifier):

        PauseCmdString = '\x02PAUSE\x03'
        self.__SetHelper('Pause', PauseCmdString, value, qualifier)

    def SetPlay(self, value, qualifier):

        PlayCmdString = '\x02PLAY0\x03'
        self.__SetHelper('Play', PlayCmdString, value, qualifier)

    def SetSpeed(self, value, qualifier):

        ValueStateValues = {
            'Up': '++',
            'Down': '--'
        }

        SpeedCmdString = '\x02SPD{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Speed', SpeedCmdString, value, qualifier)

    def SetSpeedConstrained(self, value, qualifier):

        SpeedValues = {
            'Min': 0,
            'Max': 9
        }

        ValueStateValues = {
            'Up': '+',
            'Down': '-'
        }

        speed_val = qualifier['Speed value']
        if SpeedValues['Min'] <= int(speed_val) <= SpeedValues['Max']:
            SpeedConstrainedCmdString = '\x02SPD{0}{1}\x03'.format(ValueStateValues[value], speed_val)
            self.__SetHelper('SpeedConstrained', SpeedConstrainedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedConstrained')

    def SetStartScene(self, value, qualifier):

        SceneValues = {
            'Min': 1,
            'Max': 255
        }

        scene = int(qualifier['Scene'])
        if SceneValues['Min'] <= scene <= SceneValues['Max']:
            StartSceneCmdString = '\x02SC{0:03}\x03'.format(scene)
            self.__SetHelper('StartScene', StartSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStartScene')

    def SetStopScene(self, value, qualifier):

        StopSceneCmdString = '\x02STOP0\x03'
        self.__SetHelper('StopScene', StopSceneCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=2, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
