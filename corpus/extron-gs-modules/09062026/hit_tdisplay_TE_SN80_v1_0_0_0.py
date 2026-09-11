from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Sleep': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'Source': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }


    def SetChannel(self, value, qualifier):


        ValueStateValues = {
            'Up'   : '\x5A\x4B\x43\x48\x41\x2B',
            'Down' : '\x5A\x4B\x43\x48\x41\x2D'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):


        ValueStateValues = {
            'HDMI 1' : '\x5A\x4B\x53\x48\x44\x31',
            'HDMI 2' : '\x5A\x4B\x53\x48\x44\x32',
            'TV'     : '\x5A\x4B\x53\x41\x54\x56',
            'AV'     : '\x5A\x4B\x53\x44\x41\x56',
            'YPbPr'  : '\x5A\x59\x50\x42\x50\x52',
            'VGA 1'  : '\x5A\x56\x47\x41\x2D\x31',
            'VGA 2'  : '\x5A\x56\x47\x41\x2D\x32',
            'PC'     : '\x5A\x4B\x53\x48\x44\x34',
            'USB'    : '\x5A\x4B\x48\x44\x4D\x50'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):


        if 0 <= int(value) <= 9:
            KeypadCmdString = '\x5A\x43\x48\x55\x4E{}'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):


        ValueStateValues = {
            'Menu'  : '\x5A\x4B\x4D\x45\x4E\x55',
            'Up'    : '\x5A\x4B\x41\x52\x55\x50',
            'Down'  : '\x5A\x4B\x41\x52\x44\x4E',
            'Enter' : '\x5A\x4B\x45\x4E\x54\x52',
            'Left'  : '\x5A\x4B\x41\x52\x4C\x46',
            'Right' : '\x5A\x4B\x41\x52\x47\x57',
            'Exit'  : '\x5A\x4B\x45\x58\x49\x54',
            'Info'  : '\x5A\x4B\x49\x4E\x46\x4F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):


        MuteCmdString = '\x5A\x4B\x4D\x55\x54\x45'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):


        PictureModeCmdString = '\x5A\x4B\x50\x49\x43\x4D'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def SetPowerOff(self, value, qualifier):


        PowerOffCmdString = '\x5A\x4B\x50\x57\x4F\x46'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)
    def SetSleep(self, value, qualifier):


        SleepCmdString = '\x5A\x4B\x53\x4C\x45\x50'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)
    def SetSoundMode(self, value, qualifier):


        SoundModeCmdString = '\x5A\x4B\x41\x55\x54\x4F'
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)
    def SetSource(self, value, qualifier):


        SourceCmdString = '\x5A\x4B\x53\x55\x52\x43'
        self.__SetHelper('Source', SourceCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):


        ValueStateValues = {
            'Up'   : '\x5A\x4B\x56\x4F\x4C\x2B',
            'Down' : '\x5A\x4B\x56\x4F\x4C\x2D'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def SetZoom(self, value, qualifier):


        ZoomCmdString = '\x5A\x4B\x41\x53\x50\x43'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):


        pass

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

