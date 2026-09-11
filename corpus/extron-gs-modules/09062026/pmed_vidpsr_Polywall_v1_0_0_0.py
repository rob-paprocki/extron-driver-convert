from extronlib.interface import EthernetClientInterface
class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ScenarioNavigation': {'Status': {}},
            'ScenarioPlay': {'Status': {}},
            'ScenarioPlayNameSet': {'Status': {}},
            'ScenarioResultName': {'Parameters':['Button'], 'Status': {}},
            'ScenarioResultStatus': {'Parameters':['Button'], 'Status': {}},
            'ScenarioStop': {'Status': {}},
            'SceneNavigation': {'Status': {}},
            'ScenePlay': {'Status': {}},
            'ScenePlayNameSet': {'Status': {}},
            'SceneResultName': {'Parameters':['Button'], 'Status': {}},
            'SceneResultStatus': {'Parameters':['Button'], 'Status': {}},
            }

        self.ScenarioName = ListNavigation()
        self.ScenarioStatus = ListNavigation()
        self.SceneName = ListNavigation()
        self.SceneStatus = ListNavigation()
        self.PlayState = {
            '1' : 'Playing', 
            '0' : 'Stopped'
        }

        self.MaxScene = 5
        self.MaxScenario = 5

    @property
    def MaxScene(self):
        return self.SceneName.Max

    @MaxScene.setter
    def MaxScene(self, value):
        MaxScene = int(value)
        if 1 <= MaxScene <= 15:
            self.SceneName.Max = MaxScene
            self.SceneStatus.Max = MaxScene
        else:
            print('Invalid MaxScene')

    @property
    def MaxScenario(self):
        return self.ScenarioName.Max

    @MaxScenario.setter
    def MaxScenario(self, value):
        MaxScenario = int(value)
        if 1 <= MaxScenario <= 15:
            self.ScenarioName.Max = MaxScenario
            self.ScenarioStatus.Max = MaxScenario
        else:
            print('Invalid MaxScenario')

    def UpdateScenarioResultName(self, value, qualifier):

        RequiredCommandCmdString = b'xStatus Scenarios\r'
        self.CurrentScenarios = self.__UpdateHelper('ScenarioResultName', RequiredCommandCmdString, value, qualifier)
        if self.CurrentScenarios != self.PreviousScenarios:
            self.PreviousScenarios = self.CurrentScenarios
            self.ScenarioName.Clear()
            self.ScenarioStatus.Clear()
            try:
                Lines = self.CurrentScenarios.decode().splitlines()
                if Lines[-1] == '** end': del Lines[-1]
                for Line in Lines:
                    self.ScenarioName.Append(Line.split('"')[1])
                    self.ScenarioStatus.Append(self.PlayState[Line[-1]])
                if Lines:
                    self.ScenarioName.End()
                    self.ScenarioStatus.End()
                else:
                    self.ScenarioName.Empty()
                    self.ScenarioStatus.Empty()
            except (TypeError, AttributeError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateScenarioResultName')

            self.SetScenarioNavigation(None, None)

    def UpdateScenarioResultStatus(self, value, qualifier):
        self.UpdateScenarioResultName(value, qualifier)

    def SetScenarioNavigation(self, value, qualifier):

        self.ScenarioName.Navigate(value, self.WriteStatus, 'ScenarioResultName')
        self.ScenarioStatus.Navigate(value, self.WriteStatus, 'ScenarioResultStatus')

    def SetScenarioPlay(self, value, qualifier):

        Name = value
        if Name:
            ScenarioPlayCmdString = 'xCommand Scenarios Scenario "{}" Play\r'.format(Name).encode()
            self.__SetHelper('ScenarioPlay', ScenarioPlayCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScenarioPlay')

    def SetScenarioPlayNameSet(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self.ScenarioName.Max
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line = self.ReadStatus('ScenarioResultName', {'Button' : value})
            if Line not in self.ScenarioName.InvalidLines:
                self.SetScenarioPlay(Line, None)
        else:
            print('Invalid Command for SetScenarioPlayNameSet')

    def SetScenarioStop(self, value, qualifier):

        ScenarioStopCmdString = b'xCommand Scenarios Stop\r'
        self.__SetHelper('ScenarioStop', ScenarioStopCmdString, value, qualifier)

    def SetSceneNavigation(self, value, qualifier):

        self.SceneName.Navigate(value, self.WriteStatus, 'SceneResultName')
        self.SceneStatus.Navigate(value, self.WriteStatus, 'SceneResultStatus')

    def SetScenePlay(self, value, qualifier):

        Name = value
        if Name:
            ScenePlayCmdString = 'xCommand ActiveScenes Scene "{}" Play\r'.format(Name).encode()
            self.__SetHelper('ScenePlay', ScenePlayCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScenePlay')

    def SetScenePlayNameSet(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self.SceneName.Max
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line = self.ReadStatus('SceneResultName', {'Button' : value})
            if Line not in self.SceneName.InvalidLines:
                self.SetScenePlay(Line, None)
        else:
            print('Invalid Command for SetScenePlayNameSet')

    def UpdateSceneResultName(self, value, qualifier):

        SceneResultNameCmdString = b'xStatus ActiveScenes\r'
        self.CurrentScenes = self.__UpdateHelper('SceneResultName', SceneResultNameCmdString, value, qualifier)
        if self.CurrentScenes != self.PreviousScenes:
            self.PreviousScenes = self.CurrentScenes
            self.SceneName.Clear()
            self.SceneStatus.Clear()
            try:
                Lines = self.CurrentScenes.decode().splitlines()
                if Lines[-1] == '** end': del Lines[-1]
                for Line in Lines:
                    self.SceneName.Append(Line.split('"')[1])
                    self.SceneStatus.Append(self.PlayState[Line[-1]])
                if Lines:
                    self.SceneName.End()
                    self.SceneStatus.End()
                else:
                    self.SceneName.Empty()
                    self.SceneStatus.Empty()
            except (TypeError, AttributeError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSceneResultName')

            self.SetSceneNavigation( None, None)

    def UpdateSceneResultStatus(self, value, qualifier):

        self.UpdateSceneResultName( value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'** end\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.PreviousScenarios = b''
        self.PreviousScenes = b''

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)            

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None

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

class ListNavigation:

    EndofList = '***End of list***'
    EmptyList = '***Not Available***'
    InvalidLines = (EndofList, EmptyList, None, '')
    StartingEntry = 0
    Max = 1

    def __init__(self):
        self.Empty()

    def Empty(self):
        self.List = [self.EmptyList]

    def Clear(self):
        self.List.clear()

    def Append(self, Line):
        if Line not in self.InvalidLines:
            self.List.append(Line)

    def End(self):
        self.List.append(self.EndofList)

    def Navigate(self, Direction, WriteFunction, command):
        if Direction == 'Page Up':
            self.StartingEntry -= self.Max
        elif Direction == 'Page Down':
            self.StartingEntry += self.Max
        elif Direction == 'Up':
            self.StartingEntry -= 1
        elif Direction == 'Down':
            self.StartingEntry += 1

        if self.StartingEntry + self.Max >= len(self.List):
            self.StartingEntry = len(self.List) - self.Max

        if self.StartingEntry < 0:
            self.StartingEntry = 0

        Button = 0
        for Button,Line in enumerate(self.List[self.StartingEntry:self.StartingEntry+self.Max],1):
            WriteFunction(command, Line, {'Button': Button})
        for Button in range(Button + 1, self.Max + 1):
            WriteFunction(command, '', {'Button': Button})
