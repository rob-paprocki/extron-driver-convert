from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.DefaultResponseTimeout = 0.3
        self.Commands = {
            'ChannelControl': {'Parameters': ['Unit ID', 'Channel Number', 'Fade Time'], 'Status': {}},
            'ChannelPreset': {'Parameters': ['Unit ID', 'Channel Number', 'Intensity', 'Fade Time'], 'Status': {}},
            'ChannelTimeDefault': {'Parameters': ['Fade Time'], 'Status': {}},
            'SceneControl': {'Parameters': ['Scene Number', 'Fade Time'], 'Status': {}},
        }


    def SetChannelControl(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CU',
            'Down': 'CD',
            'Stop': 'CS'
        }

        unitID = int(qualifier['Unit ID'])
        channelNumber = int(qualifier['Channel Number'])
        fadeTime = qualifier['Fade Time']

        if 0 <= unitID <= 31 and 1 <= channelNumber <= 12 and 0 <= fadeTime <= 125:
            if value == 'Stop':
                ChannelControlCmdString = '~!0 CS {0} {1}\r'.format(unitID, channelNumber)
            else:
                ChannelControlCmdString = '~!0 {0} {1} {2} {3}\r'.format(ValueStateValues[value], unitID, channelNumber, fadeTime)
            self.__SetHelper('ChannelControl', ChannelControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelControl')

    def SetChannelPreset(self, value, qualifier):

        unitID = int(qualifier['Unit ID'])
        channelNumber = int(qualifier['Channel Number'])
        intensity = qualifier['Intensity']
        fadeTime = qualifier['Fade Time']

        if 0 <= unitID <= 31 and 1 <= channelNumber <= 12 and 0 <= intensity <= 100 and 0 <= fadeTime <= 125:
            ChannelPresetCmdString = '~!0 CP {0} {1} {2} {3}\r'.format(unitID, channelNumber, intensity, fadeTime)
            self.__SetHelper('ChannelPreset', ChannelPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelPreset')

    def SetChannelTimeDefault(self, value, qualifier):

        fadeTime = qualifier['Fade Time']

        if 0 <= fadeTime <= 125:
            ChannelTimeDefaultCmdString = '~!0 CF {0}\r'.format(fadeTime)
            self.__SetHelper('ChannelTimeDefault', ChannelTimeDefaultCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelTimeDefault')

    def SetSceneControl(self, value, qualifier):

        ValueStateValues = {
            'Up': 'SU',
            'Down': 'SD',
            'Stop': 'SS'
        }

        if qualifier['Scene Number'] == 'Off':
            sceneNumber = 0
        else:
            sceneNumber = int(qualifier['Scene Number'])
        fadeTime = qualifier['Fade Time']

        if 0 <= sceneNumber <= 64 and 0 <= fadeTime <= 125:
            if value == 'Stop':
                SceneControlCmdString = '~!0 SS {0}\r'.format(sceneNumber)
            else:
                SceneControlCmdString = '~!0 {0} {1} {2}\r'.format(ValueStateValues[value], sceneNumber, fadeTime)
            self.__SetHelper('SceneControl', SceneControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneControl')

    def __CheckResponseForErrors(self, sourceCmdName, response):        
        
        if response[0:1] == b'!':
            self.Error(['Invalid Command: ' + sourceCmdName ])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
        print('res', res)
        if not res:
            self.Error(['{0} Invalid/unexpected response'.format(command)])
        else:
            res = self.__CheckResponseForErrors(command, res)

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model=None):
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
