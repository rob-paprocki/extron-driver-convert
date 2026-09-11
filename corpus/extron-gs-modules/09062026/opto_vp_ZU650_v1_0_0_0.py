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
        self.ProjectorID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
        }

    @property
    def ProjectorID(self):
        return self._ProjectorID

    @ProjectorID.setter
    def ProjectorID(self, ProjectorID):
        if ProjectorID == 'Broadcast':
            self._ProjectorID = '00'
        elif 1 <= int(ProjectorID) <= 99:
            self._ProjectorID = ProjectorID.zfill(2)
        else:
            print('Projector ID set to an invalid value: {}'.format(ProjectorID))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '1',
            '16:10': '3',
            'Native': '6',
            'Auto': '7'
        }

        AspectRatioCmdString = '~{0}60 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': '4:3',
            '3': '16:10',
            '6': 'Native',
            '7': 'Auto'
        }

        AspectRatioCmdString = '~{0}127 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{0}01 1\r'.format(self._ProjectorID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~{0}325 {1}'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AVMuteCmdString = '~{0}355 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAVMute')

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '1',
            'Video': '3',
            'Bright': '2',
            'DICOM SIM': '13',
            'Blending': '4',
            'User': '5'
        }

        DisplayModeCmdString = '~{0}20 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Presentation',
            '3': 'Video',
            '2': 'Bright',
            '13': 'DICOM SIM',
            '4': 'Blending',
            '5': 'User'
        }

        DisplayModeCmdString = '~{0}123 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDisplayMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '~{0}04 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '5',
            'HDMI': '1',
            'Component': '14',
            'HDBaseT': '21',
            'DVI-D': '2'
        }

        InputCmdString = '~{0}12 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '2': 'VGA',
            '7': 'HDMI',
            '11': 'Component',
            '16': 'HDBaseT',
            '1': 'DVI-D'
        }

        InputCmdString = '~{0}121 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '60',
            '1': '51',
            '2': '52',
            '3': '53',
            '4': '54',
            '5': '55',
            '6': '56',
            '7': '57',
            '8': '58',
            '9': '59'
        }

        KeypadCmdString = '~{0}140 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '10',
            'Down': '14',
            'Left': '11',
            'Right': '13',
            'Enter': '12',
            'Menu': '20',
            'Exit': '72'
        }

        MenuNavigationCmdString = '~{0}140 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '~{0}108 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '2',
            'HDMI': '1',
            'Component': '3',
            'HDBaseT': '9',
            'DVI-D': '10'
        }

        PIPInputCmdString = '~{0}305 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '2': 'VGA',
            '7': 'HDMI',
            '11': 'Component',
            '16': 'HDBaseT',
            '1': 'DVI-D'
        }

        PIPInputCmdString = '~{0}131 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PIPModeCmdString = '~{0}302 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': '1',
            'Top Right': '2',
            'Bottom Left': '3',
            'Bottom Right': '4',
            'PBP Main Left': '5',
            'PBP Main Top': '6',
            'PBP Main Right': '7',
            'PBP Main Bottom': '8'
        }

        PIPPositionCmdString = '~{0}303 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '3',
            'Medium': '2',
            'Large': '1'
        }

        PIPSizeCmdString = '~{0}304 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '~{0}306\r'.format(self._ProjectorID)
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~{0}00 {1}\r'.format(self._ProjectorID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '~{0}124 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            print('Failed to execute command.')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._ProjectorID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._ProjectorID == '00':
            print('Inappropriate Command ', command)
            return ''
        else:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
