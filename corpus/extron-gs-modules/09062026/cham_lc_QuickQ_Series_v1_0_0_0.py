from extronlib.interface import EthernetClientInterface


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ActivatePlayback': { 'Status': {}},
            'ActivatePlaybackat100': { 'Status': {}},
            'ReleasePlayback': { 'Status': {}},
            'ReleasePlaybackat100': { 'Status': {}},
            'Toggle10SceneButton': { 'Status': {}},
        }

    def SetActivatePlayback(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1A',
            '2'  : '2A',
            '3'  : '3A',
            '4'  : '4A',
            '5'  : '5A',
            '6'  : '6A',
            '7'  : '7A',
            '8'  : '8A',
            '9'  : '9A',
            '10' : '10A'
        }

        if value in ValueStateValues:
            ActivatePlaybackCmdString = ValueStateValues[value]
            self.__SetHelper('ActivatePlayback', ActivatePlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActivatePlayback')

    def SetActivatePlaybackat100(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1T',
            '2'  : '2T',
            '3'  : '3T',
            '4'  : '4T',
            '5'  : '5T',
            '6'  : '6T',
            '7'  : '7T',
            '8'  : '8T',
            '9'  : '9T',
            '10' : '10T'
        }

        if value in ValueStateValues:
            ActivatePlaybackat100CmdString = ValueStateValues[value]
            self.__SetHelper('ActivatePlaybackat100', ActivatePlaybackat100CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActivatePlaybackat100')

    def SetReleasePlayback(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1R',
            '2'  : '2R',
            '3'  : '3R',
            '4'  : '4R',
            '5'  : '5R',
            '6'  : '6R',
            '7'  : '7R',
            '8'  : '8R',
            '9'  : '9R',
            '10' : '10R'
        }

        if value in ValueStateValues:
            ReleasePlaybackCmdString = ValueStateValues[value]
            self.__SetHelper('ReleasePlayback', ReleasePlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleasePlayback')

    def SetReleasePlaybackat100(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1U',
            '2'  : '2U',
            '3'  : '3U',
            '4'  : '4U',
            '5'  : '5U',
            '6'  : '6U',
            '7'  : '7U',
            '8'  : '8U',
            '9'  : '9U',
            '10' : '10U'
        }

        if value in ValueStateValues:
            ReleasePlaybackat100CmdString = ValueStateValues[value]
            self.__SetHelper('ReleasePlaybackat100', ReleasePlaybackat100CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleasePlaybackat100')

    def SetToggle10SceneButton(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1X',
            '2'  : '2X',
            '3'  : '3X',
            '4'  : '4X',
            '5'  : '5X',
            '6'  : '6X',
            '7'  : '7X',
            '8'  : '8X',
            '9'  : '9X',
            '10' : '10X'
        }

        if value in ValueStateValues:
            Toggle10SceneButtonCmdString = ValueStateValues[value]
            self.__SetHelper('Toggle10SceneButton', Toggle10SceneButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetToggle10SceneButton')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
