from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Parameters': ['Monitor'], 'Status': {}},
            'AudioChannel': {'Parameters': ['Monitor'], 'Status': {}},
            'LoadLUT': {'Parameters': ['Monitor'], 'Status': {}},
            'ScopeSelect': {'Parameters': ['Monitor'], 'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'SD in 16:9': 'ON',
            'SD in 4:3': 'OFF'
        }

        if qualifier['Monitor'] in ['A', 'B']:
            AspectRatioCmdString = 'MONITOR {0}:\rWidescreenSD: {1}\r'.format(qualifier['Monitor'], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioChannel(self, value, qualifier):

        ValueStateValues = {
            'Channels 1 and 2': '0',
            'Channels 3 and 4': '1',
            'Channels 5 and 6': '2',
            'Channels 7 and 8': '3',
            'Channels 9 and 10': '4',
            'Channels 11 and 12': '5',
            'Channels 13 and 14': '6',
            'Channels 15 and 16': '7'
        }

        if qualifier['Monitor'] in ['A', 'B']:
            AudioChannelCmdString = 'MONITOR {0}:\rAudioChannel: {1}\r'.format(qualifier['Monitor'], ValueStateValues[value])
            self.__SetHelper('AudioChannel', AudioChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioChannel')

    def SetLoadLUT(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            'Disable': 'NONE'
        }

        if qualifier['Monitor'] in ['A', 'B']:
            LoadLUTCmdString = 'MONITOR {0}:\rLUT: {1}\r'.format(qualifier['Monitor'], ValueStateValues[value])
            self.__SetHelper('LoadLUT', LoadLUTCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadLUT')

    def SetScopeSelect(self, value, qualifier):

        ValueStateValues = {
            'Audio Dbfs': 'AudioDbfs',
            'Audio Dbvu': 'AudioDbvu',
            'Histogram': 'Histogram',
            'Parade RGB': 'ParadeRGB',
            'Parade YUV': 'ParadeYUV',
            'Picture (Video Monitor)': 'Picture',
            'Vector 100': 'Vector100',
            'Vector 75': 'Vector75',
            'Waveform Luma': 'WaveformLuma'
        }

        if qualifier['Monitor'] in ['A', 'B']:
            ScopeSelectCmdString = 'MONITOR {0}:\rScopeMode: {1}\r'.format(qualifier['Monitor'], ValueStateValues[value])
            self.__SetHelper('ScopeSelect', ScopeSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScopeSelect')

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
