from extronlib.interface import EthernetClientInterface
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'BlackOutMode': {'Parameters':['Scene','Page'], 'Status': {}},
            'EmulateButton': {'Parameters':['Event'], 'Status': {}},
            'EmulateSlider': {'Status': {}},
            'SceneColor': {'Parameters':['Scene','Page','Red','Green','Blue'], 'Status': {}},
            'SceneDimmer': {'Parameters':['Scene','Page'], 'Status': {}},
            'SceneMode': {'Parameters':['Scene','Page'], 'Status': {}},
            'ScenePause': {'Parameters':['Scene','Page'], 'Status': {}},
            'SceneReset': {'Parameters':['Scene','Page'], 'Status': {}},
            'SceneSpeed': {'Parameters':['Scene','Page'], 'Status': {}},
            }

    def SetBlackOutMode(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ValueStateValues = {
            'On' : 9,
            'Off' : 8
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and PageConstraints['Min'] <= Page <= PageConstraints['Max']:
            BlackOutModeCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,ValueStateValues[value],0,0,0,0,0)
            self.__SetHelper('BlackOutMode', BlackOutModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBlackOutMode')

    def SetEmulateButton(self, value, qualifier):

        EventStates = {
            'Single Click'     : 1, 
            'Touched'          : 2, 
            'Released'         : 3, 
            'Double Click'     : 4, 
            'Long Touch'       : 5, 
            'Ultra Long Touch' : 6, 
            'Semi Touch'       : 7
        }
        ValueStateValues = {
            'Set'    : 0, 
            'Toggle' : 1, 
            'Right'  : 2, 
            'Scene'  : 3, 
            'Speed'  : 4, 
            'Undo'   : 5, 
            'Cancel' : 6, 
            'Left'   : 7, 
            'Dimmer' : 8, 
            'Color'  : 9
        }
        Event = qualifier['Event']
        if Event in EventStates:
            EmulateButtonCmdString = pack('<8s4B',b'Stick_3A',101,ValueStateValues[value],EventStates[Event],0)
            self.__SetHelper('EmulateButton', EmulateButtonCmdString, value, qualifier)
        else:
            print('Invalid Command for SetEmulateButton')

    def SetEmulateSlider(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            EmulateSliderCmdString = pack('<8s4B',b'Stick_3A',101,10,8,value)
            self.__SetHelper('EmulateSlider', EmulateSliderCmdString, value, qualifier)
        else:
            print('Invalid Command for SetEmulateSlider')

    def SetSceneColor(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ColorConstraints = {
            'Min' : 0, 
            'Max' : 255
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        Red = int(qualifier['Red'])
        Green = int(qualifier['Green'])
        Blue = int(qualifier['Blue'])
        if (SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and
            PageConstraints['Min'] <= Page <= PageConstraints['Max'] and
            ColorConstraints['Min'] <= Red <= ColorConstraints['Max'] and
            ColorConstraints['Min'] <= Green <= ColorConstraints['Max'] and
                ColorConstraints['Min'] <= Blue <= ColorConstraints['Max']):
            SceneColorCmdString = pack('<8sHHBBHH6B',b'Stick_3A',109,Page*50+Scene,0,7,0,0,0,0,Red,Green,Blue,0)
            self.__SetHelper('SceneColor', SceneColorCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneColor')

    def SetSceneDimmer(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ValueConstraints = {
            'Min' : 0,
            'Max' : 65535
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if (SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and
            PageConstraints['Min'] <= Page <= PageConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            SceneDimmerCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,5,value,0,0,0,0)
            self.__SetHelper('SceneDimmer', SceneDimmerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneDimmer')

    def SetSceneMode(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ValueStateValues = {
            'On'  : 1, 
            'Off' : 0
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and PageConstraints['Min'] <= Page <= PageConstraints['Max']:
            SceneModeCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,ValueStateValues[value],0,0,0,0,0)
            self.__SetHelper('SceneMode', SceneModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneMode')

    def SetScenePause(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ValueStateValues = {
            'On'  : 3, 
            'Off' : 2
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and PageConstraints['Min'] <= Page <= PageConstraints['Max']:
            ScenePauseCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,ValueStateValues[value],0,0,0,0,0)
            self.__SetHelper('ScenePause', ScenePauseCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScenePause')

    def SetSceneReset(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and PageConstraints['Min'] <= Page <= PageConstraints['Max']:
            SceneResetCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,4,0,0,0,0,0)
            self.__SetHelper('SceneReset', SceneResetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneReset')

    def SetSceneSpeed(self, value, qualifier):

        SceneConstraints = {
            'Min' : 1, 
            'Max' : 50
        }
        PageConstraints = {
            'Min' : 0, 
            'Max' : 9
        }
        ValueConstraints = {
            'Min' : 0,
            'Max' : 65535
        }
        Scene = int(qualifier['Scene'])
        Page = int(qualifier['Page'])
        if (SceneConstraints['Min'] <= Scene <= SceneConstraints['Max'] and
            PageConstraints['Min'] <= Page <= PageConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            SceneSpeedCmdString = pack('<8sHHBBHHBBL',b'Stick_3A',109,Page*50+Scene,0,6,0,value,0,0,0)
            self.__SetHelper('SceneSpeed', SceneSpeedCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneSpeed')

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
