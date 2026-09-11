from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re
from json import loads


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.devicePassword = '1234'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Call': {'Status': {}},
            'CallInStatus': {'Status': {}},
            'CallOutStatus': {'Status': {}},
            'CameraMoveContinuous': {'Status': {}},
            'CameraMoveStep': {'Status': {}},
            'CameraMoveStop': {'Status': {}},
            'CameraPreset': {'Parameters': ['Action'], 'Status': {}},
            'CameraSelect': {'Status': {}},
            'CameraSource': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MicrophoneGain': {'Status': {}},
            'MicrophoneInput': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.PhonebookList = ListNavigation()
        self.PhonebookList.Max = 5
        self.Phonebook = {}

    @property
    def MaxPhonebookLines(self):
        return self.PhonebookList.Max

    @MaxPhonebookLines.setter
    def MaxPhonebookLines(self, value):
        self.PhonebookList.Max = int(value)

    def SetLogin(self, value, qualifier):
    
        if self.devicePassword:
            self.Send(self.devicePassword.join(['login ', '\r\n']))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'set System/AspectRatio 0\r\n',
            '1024 x 768 (4:3)': b'set System/AspectRatio 1\r\n',
            '1280 x 720 (16:9)': b'set System/AspectRatio 2\r\n'
        }
        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Auto',
            b'1': '1024 x 768 (4:3)',
            b'2': '1280 x 720 (16:9)'
        }
        AspectRatioCmdString = b'get System/AspectRatio\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(b'"')[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetCall(self, value, qualifier):

        ValueStateValues = {
            'Answer': b'action Call/AnswerCall\r\n',
            'Cancel Call Out': b'action Call/CallOutCancel\r\n',
            'Disconnect All': b'action Call/DisconnectAll\r\n',
            'Mute': b'action Call/Mute\r\n',
            'Reject': b'action Call/RejectCall\r\n',
            'Hang Up': b'action UI/IR/hangup\r\n'
        }
        if value == 'Call Out':
            DialString = qualifier['Number']
            if DialString:
                CallCmdString = 'action Call/CallOutTo {}\r\n'.format(DialString).encode()
            else:
                self.Discard('Invalid Command for SetCall')
                return
        else:
            CallCmdString = ValueStateValues[value]
        self.__SetHelper('Call', CallCmdString, value, qualifier)

    def UpdateCallInStatus(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Busy',
            b'1': 'Done'
        }
        CallInStatusCmdString = b'get Call/CallInStatus\r\n'
        res = self.__UpdateHelper('CallInStatus', CallInStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(b'"')[1]]
                self.WriteStatus('CallInStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Call In Status: Invalid/unexpected response'])

    def UpdateCallOutStatus(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Busy',
            b'1': 'Success',
            b'2': 'Failed'
        }
        CallOutStatusCmdString = b'get Call/CallOutStatus\r\n'
        res = self.__UpdateHelper('CallOutStatus', CallOutStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(b'"')[1]]
                self.WriteStatus('CallOutStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Call Out Status: Invalid/unexpected response'])

    def SetCameraMoveContinuous(self, value, qualifier):

        ValueStateValues = {
            'Down': b'action Camera/ContinuousMove/Down\r\n',
            'Left': b'action Camera/ContinuousMove/Left\r\n',
            'Right': b'action Camera/ContinuousMove/Right\r\n',
            'Up': b'action Camera/ContinuousMove/Up\r\n',
            'Zoom In': b'action Camera/ContinuousMove/ZoomIn\r\n',
            'Zoom Out': b'action Camera/ContinuousMove/ZoomOut\r\n'
        }
        CameraMoveContinuousCmdString = ValueStateValues[value]
        self.__SetHelper('CameraMoveContinuous', CameraMoveContinuousCmdString, value, qualifier)

    def SetCameraMoveStep(self, value, qualifier):

        ValueStateValues = {
            'Down': b'action Camera/StepMove/Down\r\n',
            'Left': b'action Camera/StepMove/Left\r\n',
            'Right': b'action Camera/StepMove/Right\r\n',
            'Up': b'action Camera/StepMove/Up\r\n',
            'Zoom In': b'action Camera/StepMove/ZoomIn\r\n',
            'Zoom Out': b'action Camera/StepMove/ZoomOut\r\n'
        }
        CameraMoveStepCmdString = ValueStateValues[value]
        self.__SetHelper('CameraMoveStep', CameraMoveStepCmdString, value, qualifier)

    def SetCameraMoveStop(self, value, qualifier):

        CameraMoveStopCmdString = b'action Camera/StopMove\r\n'
        self.__SetHelper('CameraMoveStop', CameraMoveStopCmdString, value, qualifier)

    def SetCameraPreset(self, value, qualifier):

        ActionStates = {
            'Save': 'set Camera/SavePreset {}\r\n',
            'Restore': 'set Camera/LoadPreset {}\r\n'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }
        Action = qualifier['Action']
        if Action in ActionStates and ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetCmdString = ActionStates[Action].format(value).encode()
            self.__SetHelper('CameraPreset', CameraPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPreset')

    def SetCameraSelect(self, value, qualifier):

        ValueStateValues = {
            'VC': b'set Camera/CameraSelector 0\r\n',
            'HDMI': b'set Camera/CameraSelector 1\r\n'
        }
        CameraSelectCmdString = ValueStateValues[value]
        self.__SetHelper('CameraSelect', CameraSelectCmdString, value, qualifier)

    def UpdateCameraSelect(self, value, qualifier):

        ValueStateValues = {
            b'0': 'VC',
            b'1': 'HDMI'
        }
        CameraSelectCmdString = b'get Camera/CameraSelector\r\n'
        res = self.__UpdateHelper('CameraSelect', CameraSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(b'"')[1]]
                self.WriteStatus('CameraSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Camera Select: Invalid/unexpected response'])

    def SetCameraSource(self, value, qualifier):

        ValueStateValues = {
            'First': b'action Camera/SwitchSrc/1stCam\r\n',
            'HDMI': b'action Camera/SwitchSrc/HDMICam\r\n',
            'None': b'action Camera/SwitchSrc/NoCam\r\n'
        }
        CameraSourceCmdString = ValueStateValues[value]
        self.__SetHelper('CameraSource', CameraSourceCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'action UI/IR/0\r\n',
            '1': b'action UI/IR/1\r\n',
            '2': b'action UI/IR/2\r\n',
            '3': b'action UI/IR/3\r\n',
            '4': b'action UI/IR/4\r\n',
            '5': b'action UI/IR/5\r\n',
            '6': b'action UI/IR/6\r\n',
            '7': b'action UI/IR/7\r\n',
            '8': b'action UI/IR/8\r\n',
            '9': b'action UI/IR/9\r\n',
            'Dot': b'action UI/IR/dot\r\n'
        }
        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'action UI/IR/left\r\n',
            'Up': b'action UI/IR/up\r\n',
            'Down': b'action UI/IR/down\r\n',
            'Right': b'action UI/IR/right\r\n',
            'Home': b'action UI/IR/home\r\n',
            'Back': b'action UI/IR/back\r\n',
            'Enter': b'action UI/IR/enter\r\n'
        }
        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicrophoneGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 8
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneGainCmdString = 'set Audio/MicGain {}\r\n'.format(value).encode()
            self.__SetHelper('MicrophoneGain', MicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneGain')

    def UpdateMicrophoneGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 8
        }
        MicrophoneGainCmdString = b'get Audio/MicGain\r\n'
        res = self.__UpdateHelper('MicrophoneGain', MicrophoneGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res.split(b'"')[1])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('MicrophoneGain', value, qualifier)
                else:
                    self.Error(['Microphone Gain: value outside of expected range'])
            except IndexError:
                self.Error(['Microphone Gain: Invalid/unexpected response'])

    def SetMicrophoneInput(self, value, qualifier):

        ValueStateValues = {
            'MIC In': b'set Audio/MicInput 0\r\n',
            'Audio In with AEC': b'set Audio/MicInput 1\r\n',
            'Audio In without AEC': b'set Audio/MicInput 2\r\n'
        }
        MicrophoneInputCmdString = ValueStateValues[value]
        self.__SetHelper('MicrophoneInput', MicrophoneInputCmdString, value, qualifier)

    def UpdateMicrophoneInput(self, value, qualifier):

        ValueStateValues = {
            b'0': 'MIC In',
            b'1': 'Audio In with AEC',
            b'2': 'Audio In without AEC'
        }
        MicrophoneInputCmdString = b'get Audio/MicInput\r\n'
        res = self.__UpdateHelper('MicrophoneInput', MicrophoneInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split(b'"')[1]]
                self.WriteStatus('MicrophoneInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Microphone Input: Invalid/unexpected response'])

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True
        self.PhonebookList.Navigate(value, self.WriteStatus, 'PhonebookResult')

    def SetPhonebookSet(self, value, qualifier):
        self.Debug = True

        ValueConstraints = {
            'Min': 1,
            'Max': self.PhonebookList.Max
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Name = self.ReadStatus('PhonebookResult', {'Button': value})
            if Name not in self.PhonebookList.InvalidLines and Name in self.Phonebook:
                self.SetCall('Call Out', {'Number': Name})
        else:
            self.Discard('Invalid Command for SetPhonebookSet')

    def SetPhonebookUpdate(self, value, qualifier):

        PhonebookUpdateCmdString = b'query Phonebook/ContactList\r\n'
        res = self.__UpdateHelper('PhonebookUpdate', PhonebookUpdateCmdString, value, qualifier)
        if res:
            try:
                Lines = res.decode().splitlines()
                self.PhonebookList.Clear()
                self.Phonebook.clear()
                Lines = Lines[3:-3]
                for Line in Lines:
                    DictLine = loads(Line.split(' alias=')[1].strip('"'))
                    self.Phonebook[DictLine['name']] = DictLine
                    self.PhonebookList.Append(DictLine['name'])
                if Lines:
                    self.PhonebookList.End()
                else:
                    self.PhonebookList.Empty()

                self.SetPhonebookNavigation(None, None)
            except (AttributeError, IndexError, KeyError):
                self.Error(['Phonebook Update: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 32
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'set Audio/Volume {}\r\n'.format(value).encode()
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 32
        }
        VolumeCmdString = b'get Audio/Volume\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res.split(b'"')[1])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    self.Error(['Volume: value outside of expected range'])
            except (ValueError, AttributeError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b' error ' in response:
            ErrorMessage = response.splitlines()[1].lstrip(b'*r ')
            self.Error([ErrorMessage.decode()])
            response = b''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'**end\r\n\r\n')
            if not res:
                return ''
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'**end\r\n\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetLogin(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def Navigate(self, Direction, WriteFunction, FunctionName):
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

        for Button, Line in enumerate(self.List[self.StartingEntry:self.StartingEntry + self.Max], 1):
            WriteFunction(FunctionName, Line, {'Button': Button})
        for Button in range(Button + 1, self.Max + 1):
            WriteFunction(FunctionName, '', {'Button': Button})