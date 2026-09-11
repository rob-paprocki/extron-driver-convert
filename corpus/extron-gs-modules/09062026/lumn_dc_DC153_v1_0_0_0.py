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
            'Brightness': {'Status': {}},
            'Capture': {'Status': {}},
            'Flip': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'ImageMode': {'Status': {}},
            'Input': {'Status': {}},
            'Lamp': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PlayBack': {'Status': {}},
            'Power': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01',
            'Down': b'\x00'
        }

        BrightnessCmdString = b''.join([b'\xA0\x39', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetCapture(self, value, qualifier):

        CaptureCmdString = b'\xA0\xB2\x00\x00\x00\xAF'
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)

    def SetFlip(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x01',
            'Disable': b'\x00'
        }

        FlipCmdString = b''.join([b'\xA0\xB5', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Flip', FlipCmdString, value, qualifier)

    def UpdateFlip(self, value, qualifier):

        ValueStateValues = {
            1: 'Enable',
            0: 'Disable'
        }

        FlipCmdString = b'\xA0\x79\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Flip', FlipCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Flip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Flip: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': b'\x01',
            'Near': b'\x00'
        }

        FocusCmdString = b''.join([b'\xA0\x3B', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        FreezeCmdString = b''.join([b'\xA0\x2C', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x00',
            'Gray': b'\x01',
            'Film': b'\x02',
            'Positive': b'\x03',
            'Microscope': b'\x04'
        }

        ImageModeCmdString = b''.join([b'\xA0\x36', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def UpdateImageMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Gray',
            2: 'Film',
            3: 'Positive',
            4: 'Microscope'
        }

        ImageModeCmdString = b'\xA0\x87\x00\x00\x00\xAF'
        res = self.__UpdateHelper('ImageMode', ImageModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('ImageMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Image Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Camera': b'\x00',
            'PC': b'\x01'
        }

        InputCmdString = b''.join([b'\xA0\x37', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        LampCmdString = b''.join([b'\xA0\x38', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x06',
            'Up': b'\x02',
            'Down': b'\x03',
            'Left': b'\x04',
            'Right': b'\x05',
            'Enter': b'\x01'
        }

        MenuNavigationCmdString = b''.join([b'\xA0\xA0', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPlayBack(self, value, qualifier):

        PlayBackCmdString = b'\xA0\xB3\x00\x00\x00\xAF'
        self.__SetHelper('PlayBack', PlayBackCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b''.join([b'\xA0\xB1', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetSharpness(self, value, qualifier):

        ValueStateValues = {
            'Photo': b'\x01',
            'Text': b'\x00'
        }

        SharpnessCmdString = b''.join([b'\xA0\xA7', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)

    def UpdateSharpness(self, value, qualifier):

        ValueStateValues = {
            1: 'Photo',
            0: 'Text'
        }

        SharpnessCmdString = b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Sharpness', SharpnessCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Sharpness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Sharpness: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': b'\x01',
            'Out': b'\x00'
        }

        ZoomCmdString = b''.join([b'\xA0\x3A', ValueStateValues[value], b'\x00\x00\xAF'])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response[-2]
        error_states = {1: 'NAK (No Action)', 2: 'Ignore (Command is not in the command list)'}
        if response:
            if res in error_states:
                self.Error(['{0}:{1}'.format(sourceCmdName, error_states[res])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
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
