from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'Brightness': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Sleep': { 'Status': {}},
            'Volume': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            '25%'   : b'\xA0\xF0\x55\xFF\x26\xD9',
            '50%'   : b'\xA0\xF0\x55\xFF\x27\xD8',
            '75%'   : b'\xA0\xF0\x55\xFF\x28\xD7',
            '100%'  : b'\xA0\xF0\x55\xFF\x29\xD6'
        }

        if value in ValueStateValues:
            BrightnessCmdString = ValueStateValues[value]
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\xA0\xF0\x55\xFF\x55\xAA',
            'Down'  : b'\xA0\xF0\x55\xFF\x5A\xA5'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = ValueStateValues[value]
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV'            : b'\xA0\xF0\x55\xFF\xED\x12',
            'VGA'           : b'\xA0\xF0\x55\xFF\xEA\x15',
            'HDMI 1'        : b'\xA0\xF0\x55\xFF\xDE\x21',
            'HDMI 2'        : b'\xA0\xF0\x55\xFF\xDF\x20',
            'HDMI 3'        : b'\xA0\xF0\x55\xFF\xE0\x1F',
            'DisplayPort'   : b'\xA0\xF0\x55\xFF\xE4\x1B',
            'TV'            : b'\xA0\xF0\x55\xFF\xE8\x17',
            'DTV'           : b'\xA0\xF0\x55\xFF\xE9\x16',
            'Component'     : b'\xA0\xF0\x55\xFF\xE7\x18',
            'USB'           : b'\xA0\xF0\x55\xFF\x57\xA8'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\xA0\xF0\x55\xFF\x42\xBD',
            '2' : b'\xA0\xF0\x55\xFF\x43\xBC',
            '3' : b'\xA0\xF0\x55\xFF\x0F\xF0',
            '4' : b'\xA0\xF0\x55\xFF\x1E\xE1',
            '5' : b'\xA0\xF0\x55\xFF\x1D\xE2',
            '6' : b'\xA0\xF0\x55\xFF\x1C\xE3',
            '7' : b'\xA0\xF0\x55\xFF\x18\xE7',
            '8' : b'\xA0\xF0\x55\xFF\x45\xBA',
            '9' : b'\xA0\xF0\x55\xFF\x4C\xB3',
            '0' : b'\xA0\xF0\x55\xFF\x56\xA9'
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : b'\xA0\xF0\x55\xFF\x4E\xB1',
            'Right' : b'\xA0\xF0\x55\xFF\x05\xFA',
            'Ok'    : b'\xA0\xF0\x55\xFF\x02\xFD',
            'Down'  : b'\xA0\xF0\x55\xFF\x0D\xF2',
            'Up'    : b'\xA0\xF0\x55\xFF\x17\xE8',
            'Left'  : b'\xA0\xF0\x55\xFF\x0C\xF3',
            'Exit'  : b'\xA0\xF0\x55\xFF\x1B\xE4'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\xA0\xF0\x55\xFF\x14\xEB'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\xF0\x55\xFF\xAE\x51',
            'Off'   : b'\xA0\xF0\x55\xFF\xAD\x52'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetSleep(self, value, qualifier):

        SleepCmdString = b'\xA0\xF0\x55\xFF\x53\xAC'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            '25%'   : b'\xA0\xF0\x55\xFF\x21\xDE',
            '50%'   : b'\xA0\xF0\x55\xFF\x22\xDD',
            '75%'   : b'\xA0\xF0\x55\xFF\x23\xDC',
            '100%'  : b'\xA0\xF0\x55\xFF\x24\xDB'
        }

        if value in ValueStateValues:
            VolumeCmdString = ValueStateValues[value]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\xA0\xF0\x55\xFF\x0A\xF5',
            'Down'  : b'\xA0\xF0\x55\xFF\x40\xBF'
        }

        if value in ValueStateValues:
            VolumeStepCmdString = ValueStateValues[value]
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def SetZoom(self, value, qualifier):

        ZoomCmdString = b'\xA0\xF0\x55\xFF\x51\xAE'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

