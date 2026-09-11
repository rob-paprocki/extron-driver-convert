from extronlib.interface import EthernetClientInterface
import uuid

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Cut': {'Parameters': ['Destination Manager', 'Screen Destination'], 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'RoutingVideoSource': {'Parameters': ['Layer', 'Screen Destination', 'Destination Manager', 'Source'], 'Status': {}},
        }

    def SetCut(self, value, qualifier):

        x = uuid.uuid4()
        destMgr = int(qualifier['Destination Manager'])
        screenDest = int(qualifier['Screen Destination'])
        if 1 <= destMgr <= 100 and 1 <= screenDest <= 16:
            CutCmdString = '<System id="0" GUID="{0}">' \
                '<DestMgr id="{1}"><ScreenDestCol id="0"><ScreenDest id="{2}">' \
                '<Transition id="0"><Cut></Cut></Transition></ScreenDest>' \
                '</ScreenDestCol></DestMgr></System>'.format(x, destMgr - 1, screenDest - 1)
            self.__SetHelper('Cut', CutCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCut')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 's',
            'Recall': 'r',
            'Recall and Auto Transition': 'a'
        }

        action = qualifier['Action']
        if action in ActionStates and 1 <= value <= 1000:
            PresetCmdString = 'PRESET -{0} {1}\r\n'.format(ActionStates[action], value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetRoutingVideoSource(self, value, qualifier):

        layer = int(qualifier['Layer'])
        destMgr = int(qualifier['Destination Manager'])
        screenDest = int(qualifier['Screen Destination'])
        source = int(qualifier['Source'])
        x = uuid.uuid4()

        if 1 <= layer <= 64 and 1 <= destMgr <= 100 and 1 <= screenDest <= 16 and 1 <= source <= 100:
            RoutingVideoSourceCmdString = '<System id="0" GUID="{0}"><DestMgr id="{1}"><ScreenDestCol id="0"><ScreenDest id="{2}">' \
                                          '<LayerCollection id="0"><Layer id="{3}"><SrcIdx>{4}</SrcIdx></Layer></LayerCollection>' \
                                          '</ScreenDest></ScreenDestCol></DestMgr></System>'.format(x, destMgr - 1, screenDest - 1, layer - 1, source - 1)
            self.__SetHelper('RoutingVideoSource', RoutingVideoSourceCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRoutingVideoSource')

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
