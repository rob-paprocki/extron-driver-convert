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
        self._DeviceID = 1
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        else:
            self._DeviceID = int(value)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '1',
            '16:9': '2',
            'Letterbox': '5',
            'Native': '6'
        }

        AspectRatioCmdString = '~{0:02}60 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': '4:3',
            '1': '16:9',
            '2': 'Letterbox',
            '3': 'Native'
        }

        AspectRatioCmdString = '~{0:02}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '~{0:02}80 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{0:02}01 1\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~{0:02}02 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '1',
            'Bright': '2',
            'Movie': '3',
            'sRGB': '4',
            'User 1': '5',
            'User 2': '6',
            'Blackboard': '8',
            'Classroom': '7'
        }

        DisplayModeCmdString = '~{0:02}20 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Presentation',
            '2': 'Bright',
            '3': 'Movie',
            '4': 'sRGB',
            '7': 'User 1',
            '8': 'User 2',
            '6': 'Blackboard',
            '5': 'Classroom'
        }

        DisplayModeCmdString = '~{0:02}123 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDisplayMode')

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '~{0:02}04 {1}\r'.format(self._DeviceID, FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '1',
            'HDMI 2': '15',
            'VGA': '5',
            'VGA SCART': '7',
            'VGA Component': '8',
            'Component': '14',
            'S-Video': '9',
            'Video': '10'
        }

        InputCmdString = '~{0:02}12 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'VGA',
            '6': 'Component',
            '4': 'S-Video',
            '5': 'Video'
        }

        InputCmdString = '~{0:02}121 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Standard': '2',
            'Bright': '1'
        }

        LampModeCmdString = '~{0:02}110 {1}\r'.format(self._DeviceID, LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '12',
            'Up': '3',
            'Down': '7',
            'Left': '4',
            'Right': '6',
            'Enter': '5'
        }

        MenuNavigationCmdString = '~{0:02}140 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~{0:02}00 {1}\r'.format(self._DeviceID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '~{0:02}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', PowerState[res[2]], qualifier)
                self.WriteStatus('LampUsage', int(res[3:7]), qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 10
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '~{0:02}81 {1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        response = response.decode()
        if response[0] == 'F':
            print('Failed to execute command')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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