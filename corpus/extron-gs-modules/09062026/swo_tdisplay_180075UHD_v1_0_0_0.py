from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ATVChannelCommand': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Color': {'Status': {}},
            'DTVChannelCommand': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControlFunctions': {'Status': {}},
            'Volume': {'Status': {}}
        }       

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\xAA\xBB\xCC\x08\x00\x00\x08\xDD\xEE\xFF',
            '4:3': b'\xAA\xBB\xCC\x08\x01\x00\x09\xDD\xEE\xFF',
            'Zoom 1': b'\xAA\xBB\xCC\x08\x02\x00\x0A\xDD\xEE\xFF',
            'Zoom 2': b'\xAA\xBB\xCC\x08\x03\x00\x0B\xDD\xEE\xFF',
            'Auto': b'\xAA\xBB\xCC\x08\x04\x00\x0C\xDD\xEE\xFF',
            '14:9': b'\xAA\xBB\xCC\x08\x05\x00\x0D\xDD\xEE\xFF',
            'Panorama': b'\xAA\xBB\xCC\x08\x06\x00\x0E\xDD\xEE\xFF',
            'Point to Point': b'\xAA\xBB\xCC\x08\x07\x00\x0F\xDD\xEE\xFF',
            'Just Scan': b'\xAA\xBB\xCC\x08\x08\x00\x10\xDD\xEE\xFF'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetATVChannelCommand(self, value, qualifier):

        tempValue = value
        if tempValue and (0 <= int(tempValue) <= 99):
            CheckSum = int(tempValue) + 0x05
            ATVChannelCommandCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x05, 0x00, int(tempValue), CheckSum, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('ATVChannelCommand', ATVChannelCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetATVChannelCommand')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x03\x01\x00\x04\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x03\x01\x01\x05\xDD\xEE\xFF'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xAA\xBB\xCC\x07\x19\x00\x20\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x1A\x00\x21\xDD\xEE\xFF'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Red': b'\xAA\xBB\xCC\x07\x24\x00\x2B\xDD\xEE\xFF',
            'Green': b'\xAA\xBB\xCC\x07\x25\x00\x2C\xDD\xEE\xFF',
            'Yellow': b'\xAA\xBB\xCC\x07\x26\x00\x2D\xDD\xEE\xFF',
            'Blue': b'\xAA\xBB\xCC\x07\x27\x00\x2E\xDD\xEE\xFF'

        }

        ColorCmdString = ValueStateValues[value]
        self.__SetHelper('Color', ColorCmdString, value, qualifier)

    def SetDTVChannelCommand(self, value, qualifier):

        DTVChannelCommandCmdString = ''
        tempValue = value
        if tempValue and 0 <= float(tempValue) <= 100:
            if '.' in tempValue:
                tempValue = tempValue.split('.')
                if tempValue[0] and tempValue[1]:
                    CheckSum = int(tempValue[0]) + int(tempValue[1]) + 6
                    DTVChannelCommandCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x06, int(tempValue[0]), int(tempValue[1]), CheckSum, 0xDD, 0xEE, 0xFF)
            else:
                val = float(tempValue)
                CheckSum = val + 6
                DTVChannelCommandCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x06, 0x00, int(val), int(CheckSum), 0xDD, 0xEE, 0xFF)
            if DTVChannelCommandCmdString:
                self.__SetHelper('DTVChannelCommand', DTVChannelCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDTVChannelCommand')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'ATV': b'\xAA\xBB\xCC\x02\x01\x00\x03\xDD\xEE\xFF',
            'DTV': b'\xAA\xBB\xCC\x02\x02\x00\x04\xDD\xEE\xFF',
            'AV': b'\xAA\xBB\xCC\x02\x09\x00\x0B\xDD\xEE\xFF',
            'YPbPr': b'\xAA\xBB\xCC\x02\x0B\x00\x0D\xDD\xEE\xFF',
            'VGA 1': b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF',
            'VGA 2': b'\xAA\xBB\xCC\x02\x04\x00\x06\xDD\xEE\xFF',
            'HDMI 1': b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF',
            'HDMI 2': b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF',
            'USB': b'\xAA\xBB\xCC\x02\x05\x00\x07\xDD\xEE\xFF',
            'PC': b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF',
            'SV': b'\xAA\xBB\xCC\x02\x0A\x00\x0C\xDD\xEE\xFF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xAA\xBB\xCC\x07\x0D\x00\x14\xDD\xEE\xFF',
            '1': b'\xAA\xBB\xCC\x07\x04\x00\x0B\xDD\xEE\xFF',
            '2': b'\xAA\xBB\xCC\x07\x05\x00\x0C\xDD\xEE\xFF',
            '3': b'\xAA\xBB\xCC\x07\x06\x00\x0D\xDD\xEE\xFF',
            '4': b'\xAA\xBB\xCC\x07\x07\x00\x0E\xDD\xEE\xFF',
            '5': b'\xAA\xBB\xCC\x07\x08\x00\x0F\xDD\xEE\xFF',
            '6': b'\xAA\xBB\xCC\x07\x09\x00\x10\xDD\xEE\xFF',
            '7': b'\xAA\xBB\xCC\x07\x0A\x00\x11\xDD\xEE\xFF',
            '8': b'\xAA\xBB\xCC\x07\x0B\x00\x12\xDD\xEE\xFF',
            '9': b'\xAA\xBB\xCC\x07\x0C\x00\x13\xDD\xEE\xFF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xAA\xBB\xCC\x07\x12\x00\x19\xDD\xEE\xFF',
            'Exit': b'\xAA\xBB\xCC\x07\x13\x00\x1A\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x07\x14\x00\x1B\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x15\x00\x1C\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x07\x16\x00\x1D\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x07\x17\x00\x1E\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x07\x18\x00\x1F\xDD\xEE\xFF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x09\x01\x00\x0A\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x09\x00\x00\x09\xDD\xEE\xFF'
        }

        PCPowerCmdString = ValueStateValues[value]
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x01\x00\x00\x01\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x01\x01\x00\x02\xDD\xEE\xFF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRemoteControlFunctions(self, value, qualifier):

        ValueStateValues = {
            'SLEEP': b'\xAA\xBB\xCC\x07\x00\x00\x07\xDD\xEE\xFF',
            'DISPLAY': b'\xAA\xBB\xCC\x07\x01\x00\x08\xDD\xEE\xFF',
            'P.MODE': b'\xAA\xBB\xCC\x07\x02\x00\x09\xDD\xEE\xFF',
            'S.MODE': b'\xAA\xBB\xCC\x07\x03\x00\x0A\xDD\xEE\xFF',
            '-/--': b'\xAA\xBB\xCC\x07\x0E\x00\x15\xDD\xEE\xFF',
            'CH_RETURN': b'\xAA\xBB\xCC\x07\x0F\x00\x16\xDD\xEE\xFF',
            'FAV': b'\xAA\xBB\xCC\x07\x1D\x00\x24\xDD\xEE\xFF',
            'EPG': b'\xAA\xBB\xCC\x07\x1E\x00\x25\xDD\xEE\xFF',
            'TV/R': b'\xAA\xBB\xCC\x07\x1F\x00\x26\xDD\xEE\xFF',
            'NICAM': b'\xAA\xBB\xCC\x07\x20\x00\x27\xDD\xEE\xFF',
            'RECORD': b'\xAA\xBB\xCC\x07\x21\x00\x28\xDD\xEE\xFF',
            'SUBTITLE': b'\xAA\xBB\xCC\x07\x22\x00\x29\xDD\xEE\xFF',
            'AUTO': b'\xAA\xBB\xCC\x07\x23\x00\x2A\xDD\xEE\xFF',
            'TTX_MODE': b'\xAA\xBB\xCC\x07\x28\x00\x2F\xDD\xEE\xFF',
            'TTX_UPDATE': b'\xAA\xBB\xCC\x07\x29\x00\x30\xDD\xEE\xFF',
            'TTX_SIZE': b'\xAA\xBB\xCC\x07\x2A\x00\x31\xDD\xEE\xFF',
            'TTX_HOLD': b'\xAA\xBB\xCC\x07\x2B\x00\x32\xDD\xEE\xFF',
            'TTX_INDEX': b'\xAA\xBB\xCC\x07\x2C\x00\x33\xDD\xEE\xFF',
            'TTX_REVEAL': b'\xAA\xBB\xCC\x07\x2D\x00\x34\xDD\xEE\xFF',
            'TTX_SUBPAGE': b'\xAA\xBB\xCC\x07\x2E\x00\x35\xDD\xEE\xFF',
            'TTX_PAGE_UP': b'\xAA\xBB\xCC\x07\x2F\x00\x36\xDD\xEE\xFF',
            'TTX_PAGE_DOWN': b'\xAA\xBB\xCC\x07\x30\x00\x37\xDD\xEE\xFF',
            'TTX_MIX': b'\xAA\xBB\xCC\x07\x31\x00\x38\xDD\xEE\xFF',
            'PAUSE': b'\xAA\xBB\xCC\x07\x32\x00\x39\xDD\xEE\xFF',
            'STOP': b'\xAA\xBB\xCC\x07\x33\x00\x3A\xDD\xEE\xFF',
            'BACKWARD': b'\xAA\xBB\xCC\x07\x34\x00\x3B\xDD\xEE\xFF',
            'FORWARD': b'\xAA\xBB\xCC\x07\x35\x00\x3C\xDD\xEE\xFF',
            'PREV': b'\xAA\xBB\xCC\x07\x36\x00\x3D\xDD\xEE\xFF',
            'NEXT': b'\xAA\xBB\xCC\x07\x37\x00\x3E\xDD\xEE\xFF',
            'REPEAT': b'\xAA\xBB\xCC\x07\x38\x00\x3F\xDD\xEE\xFF',
            'GOTO': b'\xAA\xBB\xCC\x07\x39\x00\x40\xDD\xEE\xFF'
        }

        RemoteControlFunctionsCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteControlFunctions', RemoteControlFunctionsCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CheckSum = value + 0x03
            VolumeCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x03, 0x00, value, CheckSum, 0xDD, 0xEE, 0xFF)
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
