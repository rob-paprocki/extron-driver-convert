from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DeviceID = '01'
        self.Commands = {
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PowerOff': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            print('Invalid DeviceID. Range is from 1 to 99 or Broadcast.')


    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Original': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1A',
            'Cinema Zoom 12': '1B',
            'Cinema Zoom 13': '1C',
            'Cinema Zoom 14': '1D',
            'Cinema Zoom 15': '1E',
            'Cinema Zoom 16': '1F'
        }

        CmdString = 'kc {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self.DeviceID), value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'DTV': '00',
            'CADTV': '01',
            'ATV': '10',
            'CATV': '11',
            'Component': '40',
            'HDMI 1': '90',
            'HDMI 2': '91',
            'HDMI 3': '92',
        }

        CmdString = 'xb {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Enter': '44',
            'Exit': '5B',
            'Back': '28'
        }

        CmdString = 'mc {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        self.__SetHelper('PowerOff', 'ka {0} 00\r'.format(self.DeviceID), value, qualifier)

    def SetVideoMute(self, value, qualifier):

        States = {
            'Off': '00',
            'On (Without OSD)': '01',
            'On (With OSD)': '10',
        }

        CmdString = 'kd {0} {1}\r'.format(self.DeviceID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
