from extronlib.interface import SerialInterface, EthernetClientInterface
class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio'       : {'Status': {}},
            'AutoImage'         : {'Status': {}},
            'Channel'           : {'Status': {}},
            'EnergySaving'      : {'Status': {}},
            'EPG'               : {'Status': {}},
            'Input'             : {'Status': {}},
            'MenuNavigation'    : {'Status': {}},
            'Multimedia'        : {'Status': {}},
            'Mute'              : {'Status': {}},
            'PictureMode'       : {'Status': {}},
            'Power'             : {'Status': {}},
            'ScreenDisplay'     : {'Status': {}},
            'Screenshot'        : {'Status': {}},
            'SeparateListening' : {'Status': {}},
            'Sleep'             : {'Status': {}},
            'SoundMode'         : {'Status': {}},
            'Volume'            : {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x99\x01\x1E\x01\xE1\xAA'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x99\x01\x1F\x01\xE0\xAA'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x99\x01\x19\x01\xE6\xAA', 
            'Down' : b'\x99\x01\x1A\x01\xE5\xAA'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetEnergySaving(self, value, qualifier):

        EnergySavingCmdString = b'\x99\x01\x15\x01\xEA\xAA'
        self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)

    def SetEPG(self, value, qualifier):

        EPGCmdString = b'\x99\x01\x21\x01\xDE\xAA'
        self.__SetHelper('EPG', EPGCmdString, value, qualifier)


    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : b'\x99\x01\x0E\x01\xF1\xAA', 
            'HDMI 2' : b'\x99\x01\x0F\x01\xF0\xAA', 
            'HDMI 3' : b'\x99\x01\x10\x01\xEF\xAA', 
            'VGA 1'  : b'\x99\x01\x0B\x01\xF4\xAA', 
            'VGA 2'  : b'\x99\x01\x0C\x01\xF3\xAA', 
            'VGA 3'  : b'\x99\x01\x0D\x01\xF2\xAA', 
            'PC'     : b'\x99\x01\x11\x01\xEE\xAA', 
            'AV 1'   : b'\x99\x01\x08\x01\xF7\xAA', 
            'AV 2'   : b'\x99\x01\x09\x01\xF6\xAA', 
            'YPbPr'  : b'\x99\x01\x0A\x01\xF5\xAA', 
            'DTV'    : b'\x99\x01\x06\x01\xF9\xAA', 
            'ATV'    : b'\x99\x01\x07\x01\xF8\xAA'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)


    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x99\x01\x22\x01\xDD\xAA', 
            'Down'  : b'\x99\x01\x23\x01\xDC\xAA', 
            'Left'  : b'\x99\x01\x24\x01\xDB\xAA', 
            'Right' : b'\x99\x01\x25\x01\xDA\xAA', 
            'Enter' : b'\x99\x01\x26\x01\xD9\xAA', 
            'Menu'  : b'\x99\x01\x12\x01\xED\xAA', 
            'Exit'  : b'\x99\x01\x14\x01\xEB\xAA', 
            'Home'  : b'\x99\x01\x00\x01\xFF\xAA'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetMultimedia(self, value, qualifier):

        MultimediaCmdString = b'\x99\x01\x27\x01\xD8\xAA'
        self.__SetHelper('Multimedia', MultimediaCmdString, value, qualifier)


    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x99\x01\x02\x01\xFD\xAA'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)


    def SetPictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x99\x01\x04\x01\xFB\xAA'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        PowerCmdString = b'\x99\xA2\x01\x01\x27\xAA\xAA\xAA'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)


    def SetScreenDisplay(self, value, qualifier):

        ScreenDisplayCmdString = b'\x99\x01\x1C\x01\xE3\xAA'
        self.__SetHelper('ScreenDisplay', ScreenDisplayCmdString, value, qualifier)


    def SetScreenshot(self, value, qualifier):

        ScreenshotCmdString = b'\x99\x01\x1B\x01\xE4\xAA'
        self.__SetHelper('Screenshot', ScreenshotCmdString, value, qualifier)


    def SetSeparateListening(self, value, qualifier):

        SeparateListeningCmdString = b'\x99\x01\x16\x01\xE9\xAA'
        self.__SetHelper('SeparateListening', SeparateListeningCmdString, value, qualifier)


    def SetSleep(self, value, qualifier):

        SleepCmdString = b'\x99\x01\x1D\x01\xE2\xAA'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)


    def SetSoundMode(self, value, qualifier):

        SoundModeCmdString = b'\x99\x01\x03\x01\xFC\xAA'
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)


    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x99\x01\x17\x01\xE8\xAA', 
            'Down' : b'\x99\x01\x18\x01\xE7\xAA'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)


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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
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
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()