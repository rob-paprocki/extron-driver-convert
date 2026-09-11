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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Real': 'TRUE'
        }

        AspectRatioCmdString = 'ASPECT={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'AUTO': 'Auto',
            'TRUE': 'Real'
        }

        AspectRatioCmdString = 'GET=ASPECT\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[9:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AudioMuteCmdString = 'MUTE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        AudioMuteCmdString = 'GET=MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'NO_ERROR': 'No Error',
            'ABNORMAL_TEMPERATURE': 'Temperature Error',
            'FAULTY_LIGHT': 'Light Error',
            'FAULTY_COOLING_FAN': 'Cooling Fan Error',
            'FAULTY_POWER_SUPPLY': 'Power Supply Error',
            'FAULTY_AIR_FILTER': 'Air Filter Error',
            'FAULTY_POWER_ZOOM': 'Zoom Error',
            'FAULTY_POWER_FOCUS': 'Focus Error',
            'FAULTY_POWER_LENS_SHIFT': 'Lens Shift Error',
            'FAULTY_LENS_SHIFT_CONNECTOR': 'Lens Shift Connector Error'
        }

        DeviceStatusCmdString = 'GET=ERR\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[6:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = 'FREEZE={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        FreezeCmdString = 'GET=FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[9:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'HDMI1',
            'HDMI 2': 'HDMI2',
            'HDMI 1x2': 'HDMI1X2',
            'DVI 1': 'D-RGB1',
            'DVI 2': 'D-RGB2',
            'DVI 3': 'D-RGB3',
            'DVI 4': 'D-RGB4',
            'DVI 1x2': 'D-RGB1X2',
            'DVI 2x2': 'D-RGB2X2',
            'DVI 1x4': 'D-RGB1X4'
        }

        InputCmdString = 'INPUT={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI1': 'HDMI 1',
            'HDMI2': 'HDMI 2',
            'HDMI1X2': 'HDMI 1x2',
            'D-RGB1': 'DVI 1',
            'D-RGB2': 'DVI 2',
            'D-RGB3': 'DVI 3',
            'D-RGB4': 'DVI 4',
            'D-RGB1X2': 'DVI 1x2',
            'D-RGB2X2': 'DVI 2x2',
            'D-RGB1X4': 'DVI 1x4'
        }

        InputCmdString = 'GET=INPUT\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9'
        }

        KeypadCmdString = 'RC=NUM_{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MENU',
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Ok': 'OK',
            'Exit': 'EXIT'
        }

        MenuNavigationCmdString = 'RC={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }

        PowerCmdString = 'POWER={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
            'OFF2ON': 'Warming Up',
            'ON2OFF': 'Cooling Down',
            'PMM': 'Off',
            'PMM2ON': 'Warming Up',
            'ON2PMM': 'Cooling Down'
        }

        PowerCmdString = 'GET=POWER\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'GET=PJUSGT\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[9:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        VideoMuteCmdString = 'BLANK={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        VideoMuteCmdString = 'GET=BLANK\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AVOL={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET=AVOL\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[7:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            '0002': 'Invalid Command',
            '000A': 'Invalid Parameter',
            'F001': 'Internal Error',
            '0005': 'No Power Supplied',
            '1011': 'Function Not Available',
            '201F': 'Invalid Signal'
        }

        if 'BUSY' in response.decode():
            errorstring = 'Cannot Execute: Device is Busy'
            response = ''
            print(errorstring)
        elif 'e:' in response.decode():
            errorstring = 'ERROR: {0}'.format(ErrorStates[response[2:6].decode()])
            response = ''
            print(errorstring)
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('Invalid/unexpected response')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
