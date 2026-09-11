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
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DMode': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            '3Dto2D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenType': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02d}'.format(int(value))
        else:
            print('Device ID is an invalid value')

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'SBS': '1',
            'Top and Bottom': '2',
            'Frame Sequential': '3'
        }

        FormatCmdString = '~{0}405 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'DLP-Link': '1'
        }

        ModeCmdString = '~{0}230 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Set3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        SyncInvertCmdString = '~{0}231 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DSyncInvert', SyncInvertCmdString, value, qualifier)

    def Set3Dto2D(self, value, qualifier):

        ValueStateValues = {
            '3D': '0',
            'Left': '1',
            'Right': '2'
        }

        to2DCmdString = '~{0}400 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3Dto2D', to2DCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '1',
            '16:9': '2',
            '16:10': '3',
            'LBX': '5',
            'Native': '6',
            'Auto': '7'
        }

        AspectRatioCmdString = '~{0}60 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': '4:3',
            '1': '16:9',
            '2': '16:10',
            '3': 'LBX',
            '4': 'Native',
            '5': 'Auto'
        }

        AspectRatioCmdString = '~{0}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Default': '0',
            'Audio 1': '1',
            'Audio 2': '3'
        }

        AudioInputCmdString = '~{0}89 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '~{0}03 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{0}01 1\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~{0}02 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'CC1': '1',
            'CC2': '2'
        }

        ClosedCaptionCmdString = '~{0}88 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '1',
            'Bright': '2',
            'Movie': '3',
            'sRGB': '4',
            'User': '5',
            'Blackboard': '7',
            '3D': '9',
        }

        DisplayModeCmdString = '~{0}20 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ExecutiveModeCmdString = '~{0}103 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '~{0}321 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:6])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '~{0}04 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': '1',
            'VGA 1': '5',
            'VGA 2': '6',
            'S-Video': '9',
            'Video': '10',
            'VGA 1 Component': '8',
            'VGA 2 Component': '13'
        }

        InputCmdString = '~{0}12 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': '1',
            'Eco': '2',
            'Eco+': '3',
            'Dynamic': '4'
        }

        LampModeCmdString = '~{0}110 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

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

        MenuNavigationCmdString = '~{0}140 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~{0}00 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        InputStateValues = {
            '05': 'HDMI',
            '01': 'VGA 1',
            '02': 'VGA 2',
            '04': 'S-Video',
            '03': 'Video',
            '00': 'No Input'
        }
        DisplayModeStateValues = {
            '1': 'Presentation',
            '2': 'Bright',
            '3': 'Movie',
            '4': 'sRGB',
            '5': 'User',
            '6': 'Blackboard',
            '7': '3D',
            '0': 'No Display Mode'
        }

        PowerCmdString = '~{0}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:

                Power = ValueStateValues[res[2]]
                self.WriteStatus('Power', Power, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')
            else:
                if Power == 'On':
                    try:

                        lamp_hours = int(res[3:7])
                        self.WriteStatus('LampUsage', lamp_hours, qualifier)
                    except (ValueError, IndexError):
                        print('Invalid/unexpected response for UpdateLampUsage')

                    try:

                        InputValue = InputStateValues[res[7:9]]
                        self.WriteStatus('Input', InputValue, qualifier)
                    except (KeyError, IndexError):
                        print('Invalid/unexpected response for UpdateInput')

                    try:

                        Display = DisplayModeStateValues[res[13:14]]
                        self.WriteStatus('DisplayMode', Display, qualifier)
                    except (KeyError, IndexError):
                        print('Invalid/unexpected response for UpdateDisplay')

    def SetScreenType(self, value, qualifier):

        ValueStateValues = {
            '16:10': '1',
            '16:9': '0'
        }

        ScreenTypeCmdString = '~{0}90 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ScreenType', ScreenTypeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '~{0}81 {1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == 'F\r':
            print('Error message received from device')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Model=None):
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
