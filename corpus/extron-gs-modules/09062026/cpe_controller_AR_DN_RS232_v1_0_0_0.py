from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'CircuitLevel': {'Parameters': ['Local Code', 'Circuit', 'Fade Time'], 'Status': {}},
            'CircuitLower': {'Parameters': ['Local Code', 'Circuit'], 'Status': {}},
            'CircuitRaise': {'Parameters': ['Local Code', 'Circuit'], 'Status': {}},
            'Override': {'Parameters': ['Type', 'Area/Local Code', 'Scene'], 'Status': {}},
            'OverrideRelease': {'Parameters': ['Type', 'Area/Local Code', 'Scene'], 'Status': {}},
            'SceneLower': {'Parameters': ['Type', 'Area/Local Code', 'Scene'], 'Status': {}},
            'SceneRaise': {'Parameters': ['Type', 'Area/Local Code', 'Scene'], 'Status': {}},
            'SceneSave': {'Parameters': ['Type', 'Area/Local Code'], 'Status': {}},
            'SceneSelect': {'Parameters': ['Type', 'Area/Local Code', 'Fade Time'], 'Status': {}},
            'StopCircuitFade': {'Parameters': ['Type', 'Area/Local Code'], 'Status': {}},
            'StopSceneFade': {'Parameters': ['Type', 'Area/Local Code'], 'Status': {}},
        }

    def SetCircuitLevel(self, value, qualifier):

        LocalCodeAndCircuitConstraints = {
            'Min': 0,
            'Max': 999
        }
        FadeTimeConstraints = {
            'Min': 0,
            'Max': 59
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        LocalCode = qualifier['Local Code']
        Circuit = qualifier['Circuit']
        FadeTime = qualifier['Fade Time']
        if (LocalCodeAndCircuitConstraints['Min'] <= LocalCode <= LocalCodeAndCircuitConstraints['Max'] and
                LocalCodeAndCircuitConstraints['Min'] <= Circuit <= LocalCodeAndCircuitConstraints['Max'] and
                FadeTimeConstraints['Min'] <= FadeTime <= FadeTimeConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            CircuitLevelCmdString = '#SC-L{:03}-C{:03}-V{:03}-F{:04}S.'.format(LocalCode, Circuit, value, FadeTime)
            self.__SetHelper('CircuitLevel', CircuitLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCircuitLevel')

    def SetCircuitLower(self, value, qualifier):

        LocalCodeAndCircuitConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        LocalCode = qualifier['Local Code']
        Circuit = qualifier['Circuit']
        if (LocalCodeAndCircuitConstraints['Min'] <= LocalCode <= LocalCodeAndCircuitConstraints['Max'] and
                LocalCodeAndCircuitConstraints['Min'] <= Circuit <= LocalCodeAndCircuitConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            CircuitLowerCmdString = '#CL-L{:03}-C{:03}-V{:03}.'.format(LocalCode, Circuit, value)
            self.__SetHelper('CircuitLower', CircuitLowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCircuitLower')

    def SetCircuitRaise(self, value, qualifier):

        LocalCodeAndCircuitConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        LocalCode = qualifier['Local Code']
        Circuit = qualifier['Circuit']
        if (LocalCodeAndCircuitConstraints['Min'] <= LocalCode <= LocalCodeAndCircuitConstraints['Max'] and
                LocalCodeAndCircuitConstraints['Min'] <= Circuit <= LocalCodeAndCircuitConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            CircuitRaiseCmdString = '#CR-L{:03}-C{:03}-V{:03}.'.format(LocalCode, Circuit, value)
            self.__SetHelper('CircuitRaise', CircuitRaiseCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCircuitRaise')

    def SetOverride(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueStateValues = ('On', 'Off')
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        Scene = qualifier['Scene']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= Scene <= Area_LocalCodeAndSceneConstraints['Max'] and
                value in ValueStateValues):
            if value == 'On':
                OverrideCmdString = '#ON-{}{:03}.'.format(TypeStates[Type], Area_LocalCode)
            else:
                OverrideCmdString = '#OF-{}{:03}-S{:03}.'.format(TypeStates[Type], Area_LocalCode, Scene)
            self.__SetHelper('Override', OverrideCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOverride')

    def SetOverrideRelease(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueStateValues = {
            'On': 'ONR',
            'Off': 'OFR'
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        Scene = qualifier['Scene']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= Scene <= Area_LocalCodeAndSceneConstraints['Max']):
            OverrideReleaseCmdString = '#{}-{}{:03}-S{:03}.'.format(ValueStateValues[value], TypeStates[Type], Area_LocalCode, Scene)
            self.__SetHelper('OverrideRelease', OverrideReleaseCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOverrideRelease')

    def SetSceneLower(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        Scene = qualifier['Scene']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= Scene <= Area_LocalCodeAndSceneConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            SceneLowerCmdString = '#SL-{}{:03}-S{:03}-V{:03}.'.format(TypeStates[Type], Area_LocalCode, Scene, value)
            self.__SetHelper('SceneLower', SceneLowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneLower')

    def SetSceneRaise(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        Scene = qualifier['Scene']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= Scene <= Area_LocalCodeAndSceneConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            SceneRaiseCmdString = '#SR-{}{:03}-S{:03}-V{:03}.'.format(TypeStates[Type], Area_LocalCode, Scene, value)
            self.__SetHelper('SceneRaise', SceneRaiseCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneRaise')

    def SetSceneSave(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= value <= Area_LocalCodeAndSceneConstraints['Max']):
            SceneSaveCmdString = '#SA-{}{:03}-S{:03}.'.format(TypeStates[Type], Area_LocalCode, value)
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneSave')

    def SetSceneSelect(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        FadeTimeConstraints = {
            'Min': 0,
            'Max': 59
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        FadeTime = qualifier['Fade Time']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                FadeTimeConstraints['Min'] <= FadeTime <= FadeTimeConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= value <= Area_LocalCodeAndSceneConstraints['Max']):
            SceneSelectCmdString = '#SS-{}{:03}-S{:03}-F{:04}S.'.format(TypeStates[Type], Area_LocalCode, value, FadeTime)
            self.__SetHelper('SceneSelect', SceneSelectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneSelect')

    def SetStopCircuitFade(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndCircuitConstraints = {
            'Min': 0,
            'Max': 999
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        if (Type in TypeStates and
                Area_LocalCodeAndCircuitConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndCircuitConstraints['Max'] and
                Area_LocalCodeAndCircuitConstraints['Min'] <= value <= Area_LocalCodeAndCircuitConstraints['Max']):
            StopCircuitFadeCmdString = '#SF-{}{:03}-C{:03}.'.format(TypeStates[Type], Area_LocalCode, value)
            self.__SetHelper('StopCircuitFade', StopCircuitFadeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStopCircuitFade')

    def SetStopSceneFade(self, value, qualifier):

        TypeStates = {
            'Area': 'A',
            'Local': 'L'
        }
        Area_LocalCodeAndSceneConstraints = {
            'Min': 0,
            'Max': 999
        }
        Type = qualifier['Type']
        Area_LocalCode = qualifier['Area/Local Code']
        if (Type in TypeStates and
                Area_LocalCodeAndSceneConstraints['Min'] <= Area_LocalCode <= Area_LocalCodeAndSceneConstraints['Max'] and
                Area_LocalCodeAndSceneConstraints['Min'] <= value <= Area_LocalCodeAndSceneConstraints['Max']):
            StopSceneFadeCmdString = '#SF-{}{:03}-S{:03}.'.format(TypeStates[Type], Area_LocalCode, value)
            self.__SetHelper('StopSceneFade', StopSceneFadeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStopSceneFade')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

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
