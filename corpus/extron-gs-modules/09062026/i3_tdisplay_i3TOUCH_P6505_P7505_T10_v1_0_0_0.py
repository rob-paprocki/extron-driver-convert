from extronlib.interface import EthernetClientInterface, SerialInterface


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DeviceID = '1'

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if value == 'Broadcast 1':
                self._DeviceID = '0'
            elif value == 'Broadcast 2':
                self._DeviceID = '9'
            elif 1 <= int(value) <= 8:
                self.DeviceID = value
        except:
            print('DeviceID is set to an invalid value: {}'.format(value))

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = 'S{0}030{1:03}EN'.format(self._DeviceID, value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBrightness')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'OPS': '3',
            'DisplayPort': '4',
            'WB': '5',
            'Android': '6'
        }

        InputCmdString = 'S{0}02000{1}EN'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = 'S{0}01000{1}EN'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'S{0}050{1:03}EN'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

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
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
