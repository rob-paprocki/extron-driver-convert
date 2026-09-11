from extronlib.interface import SerialInterface, EthernetClientInterface


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
            'AutoFocus': {'Status': {}},
            'ColorBW': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'ImageRecall': {'Status': {}},
            'ImageRotation': {'Status': {}},
            'ImageSave': {'Status': {}},
            'Iris': {'Status': {}},
            'IrisMode': {'Status': {}},
            'Lamp': {'Status': {}},
            'PositiveNegative': {'Status': {}},
            'Zoom': {'Status': {}}
        }

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = 'AF0'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetColorBW(self, value, qualifier):

        ValueStateValues = {
            'Color': 'CB0',
            'B&W': 'CB1'
        }

        ColorBWCmdString = ValueStateValues[value]
        self.__SetHelper('ColorBW', ColorBWCmdString, value, qualifier)

    def UpdateColorBW(self, value, qualifier):
        self.UpdateLamp(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'LL1',
            'Off': 'LL0'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.UpdateLamp(value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Up': 'FO+',
            'Down': 'FO-',
            'Stop': 'FO0'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'FZ1',
            'Off': 'FZ0'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        self.UpdateLamp(value, qualifier)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            '1.0': 'GN0',
            '0.9': 'GN1',
            '0.8': 'GN2',
            '0.7': 'GN3',
            '0.6': 'GN4',
            '0.5': 'GN5',
            '0.4': 'GN6',
            '0.3': 'GN7'
        }

        GammaCmdString = ValueStateValues[value]
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        GammaStateValues = {
            '0': '1.0',
            '1': '0.9',
            '2': '0.8',
            '3': '0.7',
            '4': '0.6',
            '5': '0.5',
            '6': '0.4',
            '7': '0.3'
        }

        ImageRotStateValues = {
            '0': '0 degrees',
            '1': '90 degrees',
            '2': '180 degrees',
            '3': '270 degrees'
        }

        GammaCmdString = 'QS2'
        res = self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)

        if res:
            try:
                value = GammaStateValues[res[2]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                print('Gamma: Invalid/unexpected response')
            try:
                value = ImageRotStateValues[res[3]]
                self.WriteStatus('ImageRotation', value, qualifier)
            except (KeyError, IndexError):
                print('Image Rotation: Invalid/unexpected response')

    def SetImageRecall(self, value, qualifier):

        ValueStateValues = {
            '1': 'IC1',
            '2': 'IC2',
            '3': 'IC3',
            '4': 'IC4',
            '5': 'IC5',
            '6': 'IC6',
            '7': 'IC7',
            '8': 'IC8'
        }

        ImageRecallCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRecall', ImageRecallCmdString, value, qualifier)

    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            '0 degrees': 'RO0',
            '90 degrees': 'RO1',
            '180 degrees': 'RO2',
            '270 degrees': 'RO3'
        }

        ImageRotationCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def UpdateImageRotation(self, value, qualifier):

        self.UpdateGamma(value, qualifier)

    def SetImageSave(self, value, qualifier):

        ValueStateValues = {
            '1': 'IS1',
            '2': 'IS2',
            '3': 'IS3',
            '4': 'IS4',
            '5': 'IS5',
            '6': 'IS6',
            '7': 'IS7',
            '8': 'IS8'
        }

        ImageSaveCmdString = ValueStateValues[value]
        self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open': 'IR+',
            'Close': 'IR-',
            'Stop': 'IR0'
        }

        IrisCmdString = ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'IR1',
            'Manual': 'IR2'
        }

        IrisModeCmdString = ValueStateValues[value]
        self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On': 'PL1',
            'Off': 'PL0'
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        LampStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PosNegStateValues = {
            '0': 'Positive',
            '1': 'Negative'
        }

        ColorBWStateValues = {
            '0': 'Color',
            '1': 'B&W'
        }

        FreezeStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecModeStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        LampCmdString = 'QS0'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)

        if res:
            try:
                value = LampStateValues[res[1]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                print('Lamp: Invalid/unexpected response')
            try:
                value = PosNegStateValues[res[3]]
                self.WriteStatus('PositiveNegative', value, qualifier)
            except (KeyError, IndexError):
                print('Positive Negative: Invalid/unexpected response')
            try:
                value = ColorBWStateValues[res[4]]
                self.WriteStatus('ColorBW', value, qualifier)
            except (KeyError, IndexError):
                print('Color BW: Invalid/unexpected response')
            try:
                value = FreezeStateValues[res[7]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Freeze: Invalid/unexpected response')
            try:
                value = ExecModeStateValues[res[8]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Executive Mode: Invalid/unexpected response')

    def SetPositiveNegative(self, value, qualifier):

        ValueStateValues = {
            'Positive': 'NP0',
            'Negative': 'NP1'
        }

        PositiveNegativeCmdString = ValueStateValues[value]
        self.__SetHelper('PositiveNegative', PositiveNegativeCmdString, value, qualifier)

    def UpdatePositiveNegative(self, value, qualifier):
        self.UpdateLamp(value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'ZO+',
            'Wide': 'ZO-',
            'Stop': 'ZO0'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'NAK' in response:
            print('{0}: Negative Acknowledgement'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            commandstring = '\x02{0}  \x03'.format(commandstring)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('{0}: Invalid/unexpected response'.format(command))
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

            commandstring = '\x02{0}  \x03'.format(commandstring)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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
