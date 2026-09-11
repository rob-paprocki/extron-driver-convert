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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'KeypadLock': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'SourceLock': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['Device ID should be a value between 1 to 99 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '0',
            '16:9': '1',
            'LBX': '2',
            'Native': '3',
            'Auto': '4'
        }

        AspectRatioCmdString = '~{}60 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': '4:3',
            '1': '16:9',
            '2': 'LBX',
            '3': 'Native',
            '4': 'Auto'
        }

        AspectRatioCmdString = '~{}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{}01 1\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~{}02 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1': '1',
            'CC2': '2',
            'Off': '0'
        }

        ClosedCaptionCmdString = '~{}88 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '1',
            'Bright': '2',
            'Movie': '3',
            'sRGB': '4',
            'User': '5',
            'Blackboard': '6',
            '3D': '7'
        }

        DisplayModeCmdString = '~{}20 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '~{}321 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '~{}04 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Film': '1',
            'Video': '2',
            'Graphics': '3',
            'Standard': '4'
        }

        GammaCmdString = '~{}35 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '5',
            'Video': '10',
            'S-Video': '9'
        }

        InputCmdString = '~{}12 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        KeypadLockCmdString = '~{}103 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '10',
            'Down': '14',
            'Left': '11',
            'Right': '13',
            'Enter': '12',
            'Menu': '20'
        }

        MenuNavigationCmdString = '~{}140 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MuteCmdString = '~{}03 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~{}00 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        powerStates = {
            '1': 'On',
            '0': 'Off'
        }

        inputStates = {
            '1': 'VGA',
            '3': 'Video',
            '4': 'S-Video',
            '0': 'None'
        }

        displayStates = {
            '1': 'Presentation',
            '2': 'Bright',
            '3': 'Movie',
            '4': 'sRGB',
            '5': 'User',
            '6': 'Blackboard',
            '7': '3D',
            '0': 'None'
        }

        PowerCmdString = '~{}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = powerStates[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

            try:
                value = inputStates[res[8]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            try:
                value = displayStates[res[13]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode: Invalid/unexpected response'])

            try:
                value = int(res[3:7])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetSourceLock(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        SourceLockCmdString = '~{}100 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('SourceLock', SourceLockCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '18',
            'Down': '17'
        }

        VolumeCmdString = '~{}140 {}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Plus': '6',
            'Minus': '5'
        }

        ZoomCmdString = '~{}0{} 1\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'F' in response:
            self.Error(['Error: {}'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
