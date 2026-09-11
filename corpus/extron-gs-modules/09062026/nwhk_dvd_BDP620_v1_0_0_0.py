from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Angle': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Color': {'Status': {}},
            'HDMIOutput': {'Status': {}},
            'Info': {'Status': {}},
            'InputMediaCenter': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Repeat': {'Status': {}},
            'SubtitleLanguage': {'Status': {}},
            'Transport': {'Status': {}},
        }

    
    def SetAngle(self, value, qualifier):

        AngleCmdString = 'IC23'
        self.__SetHelper('Angle', AngleCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'IC39'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Red': 'IC10',
            'Green': 'IC11',
            'Blue': 'IC13',
            'Yellow': 'IC12'
        }

        ColorCmdString = ValueStateValues[value]
        self.__SetHelper('Color', ColorCmdString, value, qualifier)

    def SetHDMIOutput(self, value, qualifier):

        HDMIOutputCmdString = 'IC38'
        self.__SetHelper('HDMIOutput', HDMIOutputCmdString, value, qualifier)

    def SetInfo(self, value, qualifier):

        InfoCmdString = 'IC37'
        self.__SetHelper('Info', InfoCmdString, value, qualifier)

    def SetInputMediaCenter(self, value, qualifier):

        InputMediaCenterCmdString = 'IC22'
        self.__SetHelper('InputMediaCenter', InputMediaCenterCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 'IC00',
            '1': 'IC01',
            '2': 'IC02',
            '3': 'IC03',
            '4': 'IC04',
            '5': 'IC05',
            '6': 'IC06',
            '7': 'IC07',
            '8': 'IC08',
            '9': 'IC09',
            'Clear': 'IC33',
            'GoTo': 'IC34'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'IC31',
            'Top Menu': 'IC32',
            'Return': 'IC30',
            'Up': 'IC27',
            'Down': 'IC26',
            'Left': 'IC25',
            'Right': 'IC42',
            'Home': 'IC29',
            'Enter': 'IC28'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        PIPModeCmdString = 'IC21'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerCmdString = 'IC41'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        RepeatCmdString = 'IC35'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def SetSubtitleLanguage(self, value, qualifier):

        SubtitleLanguageCmdString = 'IC24'
        self.__SetHelper('SubtitleLanguage', SubtitleLanguageCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'IC18',
            'Stop': 'IC20',
            'Rew': 'IC14',
            'FFwd': 'IC15',
            'Next': 'IC17',
            'Previous': 'IC16',
            'Slow': 'IC19',
            'Open/Close': 'IC40',
            'A-B': 'IC36'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

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
