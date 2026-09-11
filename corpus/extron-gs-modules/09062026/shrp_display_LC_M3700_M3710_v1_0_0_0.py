from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AspectRatio': {'Parameters': ['Input Type'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'CauseofError': {'Status': {}},
            'ControlLock': {'Status': {}},
            'Input1Selection': {'Status': {}},
            'Input2Selection': {'Status': {}},
            'Input3Selection': {'Status': {}},
            'InputSelect': {'Status': {}},
            'MenuLock': {'Status': {}},
            'PCInputSelection': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        AVValueStateValues = {
            'Normal': 'WIDE   1\r\n',
            'Full 14:9': 'WIDE   2\r\n',
            'Zoom 14:9': 'WIDE   3\r\n',
            'Panorama': 'WIDE   4\r\n',
            'Cinema 14:9': 'WIDE   5\r\n',
            'Cinema 16:9': 'WIDE   6\r\n',
            'Full': 'WIDE   7\r\n',
            'Underscan': 'WIDE   8\r\n'
        }

        PCValueStateValues = {
            'Normal': 'WIDE   1\r\n',
            'Full': 'WIDE   2\r\n',
            'Cinema': 'WIDE   3\r\n',
            'D by D': 'WIDE   4\r\n'
        }

        InputType = qualifier['Input Type']

        if InputType not in ['PC', 'AV']:
            print('Invalid Command for SetAspectRatio')
        else:
            if InputType == 'AV':
                AspectRatioCmdString = AVValueStateValues[value]
            elif InputType == 'PC':
                AspectRatioCmdString = PCValueStateValues[value]

            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AVValueStateValues = {
            1: 'Normal',
            2: 'Full 14:9',
            3: 'Zoom 14:9',
            4: 'Panorama',
            5: 'Cinema 14:9',
            6: 'Cinema 16:9',
            7: 'Full',
            8: 'Underscan'
        }

        PCValueStateValues = {
            1: 'Normal',
            2: 'Full',
            3: 'Cinema',
            4: 'D by D'
        }

        InputType = qualifier['Input Type']

        AspectRatioCmdString = 'WIDE????\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if InputType == 'PC':
                    value = PCValueStateValues[int(res)]
                elif InputType == 'AV':
                    value = AVValueStateValues[int(res)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, ValueError):
                print('Update Aspect Ratio has provided an invalid/unexpected response')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE   1\r\n',
            'Off': 'MUTE   0\r\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, ValueError):
                print('Update Audio Mute has provided an invalid/unexpected response')

    def UpdateCauseofError(self, value, qualifier):

        ValueStateValues = {
            0: 'No detectable error has occurred',
            1: 'Invalid input has continued for a long time during PC display',
            2: 'Internal bus error',
            3: 'Abnormal temperature',
            4: 'Board connection error',
            5: 'Lamp error',
            7: 'Electrical system error',
            8: 'Error in communication with microcomputer'
        }

        CauseofErrorCmdString = 'ERCA????\r\n'
        res = self.__UpdateHelper('CauseofError', CauseofErrorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('CauseofError', value, qualifier)
            except (KeyError, ValueError):
                print('Update Cause of Error has provided an invalid/unexpected response')

    def SetControlLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'LBTN   1\r\n',
            'Off': 'LBTN   0\r\n'
        }

        ControlLockCmdString = ValueStateValues[value]
        self.__SetHelper('ControlLock', ControlLockCmdString, value, qualifier)

    def UpdateControlLock(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        ControlLockCmdString = 'LBTN????\r\n'
        res = self.__UpdateHelper('ControlLock', ControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('ControlLock', value, qualifier)
            except (KeyError, ValueError):
                print('Update Control Lock has provided an invalid/unexpected response')

    def SetInput1Selection(self, value, qualifier):

        ValueStateValues = {
            'Input 1': 'INP1   0\r\n',
            'AV': 'INP1   1\r\n',
            'Y/C': 'INP1   2\r\n'
        }

        Input1SelectionCmdString = ValueStateValues[value]
        self.__SetHelper('Input1Selection', Input1SelectionCmdString, value, qualifier)

    def UpdateInput1Selection(self, value, qualifier):

        ValueStateValues = {
            1: 'AV',
            2: 'Y/C'
        }

        Input1SelectionCmdString = 'INP1????\r\n'
        res = self.__UpdateHelper('Input1Selection', Input1SelectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input1Selection', value, qualifier)
            except (KeyError, ValueError):
                print('Update Input 1 Selection has provided an invalid/unexpected response')

    def SetInput2Selection(self, value, qualifier):

        ValueStateValues = {
            'Input 2': 'INP2   0\r\n',
            'Input': 'INP2   1\r\n',
            'Output': 'INP2   9\r\n'
        }

        Input2SelectionCmdString = ValueStateValues[value]
        self.__SetHelper('Input2Selection', Input2SelectionCmdString, value, qualifier)

    def UpdateInput2Selection(self, value, qualifier):

        ValueStateValues = {
            1: 'Input',
            9: 'Output'
        }

        Input2SelectionCmdString = 'INP2????\r\n'
        res = self.__UpdateHelper('Input2Selection', Input2SelectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input2Selection', value, qualifier)
            except (KeyError, ValueError):
                print('Update Input 2 Selection has provided an invalid/unexpected response')

    def SetInput3Selection(self, value, qualifier):

        ValueStateValues = {
            'Input 3': 'INP3   0\r\n',
            'Component': 'INP3   1\r\n',
            'RGB': 'INP3   2\r\n'
        }

        Input3SelectionCmdString = ValueStateValues[value]
        self.__SetHelper('Input3Selection', Input3SelectionCmdString, value, qualifier)

    def UpdateInput3Selection(self, value, qualifier):

        ValueStateValues = {
            1: 'Component',
            2: 'RGB'
        }

        Input3SelectionCmdString = 'INP3????\r\n'
        res = self.__UpdateHelper('Input3Selection', Input3SelectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input3Selection', value, qualifier)
            except (KeyError, ValueError):
                print('Update Input 3 Selection has provided an invalid/unexpected response')

    def SetInputSelect(self, value, qualifier):

        ValueStateValues = {
            'Video Input 1': 'INPS   1\r\n',
            'S-Video Input 1': 'INPS   2\r\n',
            'Video Input 2': 'INPS   4\r\n',
            'Input 3': 'INPS   5\r\n',
            'D-Sub PC': 'INPS   6\r\n',
            'DVI PC': 'INPS   7\r\n'
        }

        InputSelectCmdString = ValueStateValues[value]
        self.__SetHelper('InputSelect', InputSelectCmdString, value, qualifier)

    def UpdateInputSelect(self, value, qualifier):

        ValueStateValues = {
            1: 'Video Input 1',
            2: 'S-Video Input 1',
            4: 'Video Input 2',
            5: 'Input 3',
            6: 'D-Sub PC',
            7: 'DVI PC'
        }

        InputSelectCmdString = 'INPS????\r\n'
        res = self.__UpdateHelper('InputSelect', InputSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('InputSelect', value, qualifier)
            except (KeyError, ValueError):
                print('Update Input Select has provided an invalid/unexpected response')

    def SetMenuLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'LMNU   1\r\n',
            'Off': 'LMNU   0\r\n'
        }

        MenuLockCmdString = ValueStateValues[value]
        self.__SetHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def UpdateMenuLock(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        MenuLockCmdString = 'LMNU????\r\n'
        res = self.__UpdateHelper('MenuLock', MenuLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('MenuLock', value, qualifier)
            except (KeyError, ValueError):
                print('Update Menu Lock has provided an invalid/unexpected response')

    def SetPCInputSelection(self, value, qualifier):

        ValueStateValues = {
            'PC': 'INPC   0\r\n',
            'Analog': 'INPC   1\r\n',
            'Digital': 'INPC   2\r\n'
        }

        PCInputSelectionCmdString = ValueStateValues[value]
        self.__SetHelper('PCInputSelection', PCInputSelectionCmdString, value, qualifier)

    def UpdatePCInputSelection(self, value, qualifier):

        ValueStateValues = {
            1: 'Analog',
            2: 'Digital'
        }

        PCInputSelectionCmdString = 'INPC????\r\n'
        res = self.__UpdateHelper('PCInputSelection', PCInputSelectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('PCInputSelection', value, qualifier)
            except (KeyError, ValueError):
                print('Update PC Input Selection has provided an invalid/unexpected response')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWR   1\r\n',
            'Off': 'POWR   0\r\n',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            2: 'Power Standby State'
        }

        PowerCmdString = 'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, ValueError):
                print('Update Power has provided an invalid/unexpected response')

    def SetRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'LREM   1\r\n',
            'Off': 'LREM   0\r\n'
        }

        RemoteControlLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)

    def UpdateRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        RemoteControlLockCmdString = 'LREM????\r\n'
        res = self.__UpdateHelper('RemoteControlLock', RemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('RemoteControlLock', value, qualifier)
            except (KeyError, ValueError):
                print('Update Remote Control Lock has provided an invalid/unexpected response')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:02d}  \r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError):
                print('Update Volume has provided an invalid/unexpected response')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                print('{0} no relevant command or command cannot be used in the current state of the device'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                print('No response or Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

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
