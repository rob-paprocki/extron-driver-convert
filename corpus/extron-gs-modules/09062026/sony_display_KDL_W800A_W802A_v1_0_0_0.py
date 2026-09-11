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
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberPad': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '\x2ASCAMUT000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '\x2ASEAMUT################\x0A'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '3',
            'Down': '4'
        }

        ChannelCmdString = '\x2ASCIRCC000000000000003{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Composite 1': '1',
            'Composite 2': '2'
        }
        HDMIStateValues = {
            'HDMI 1': '1',
            'HDMI 2': '2',
            'HDMI 3': '3',
            'HDMI 4': '4'
        }

        InputCmdString = ''
        if value == 'TV':
            InputCmdString = '\x2ASCINPT0000000000000000\x0A'
        elif value == 'Component':
            InputCmdString = '\x2ASCINPT0000000400000001\x0A'
        elif value in ['HDMI 1', 'HDMI 2', 'HDMI 3', 'HDMI 4']:
            InputCmdString = '\x2ASCINPT000000010000000{0}\x0A'.format(HDMIStateValues[value])
        else:
            InputCmdString = '\x2ASCINPT000000030000000{0}\x0A'.format(ValueStateValues[value])

        if InputCmdString:
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'TV',
            '4': 'Component'
        }
        CompositeStateValues = {
            '1': 'Composite 1',
            '2': 'Composite 2'
        }
        HDMIStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4'
        }

        InputCmdString = '\x2ASEINPT################\x0A'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                temp = res[14:15]
                if temp == '1':
                    self.WriteStatus('Input', HDMIStateValues[res[22:-1]], qualifier)
                elif temp == '3':
                    self.WriteStatus('Input', CompositeStateValues[res[22:-1]], qualifier)
                else:
                    self.WriteStatus('Input', ValueStateValues[temp], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': '12',
            'Right': '11',
            'Up': '09',
            'Down': '10',
            'Home': '06',
            'Return': '08',
            'Confirm': '13',
            'Options': '07'
        }

        MenuNavigationCmdString = '\x2ASCIRCC00000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberPad(self, value, qualifier):

        ValueStateValues = {
            '0': '27',
            '1': '18',
            '2': '19',
            '3': '20',
            '4': '21',
            '5': '22',
            '6': '23',
            '7': '24',
            '8': '25',
            '9': '26',
            '11': '28',
            '12': '29',
            'Dot': '38'
        }

        NumberPadCmdString = '\x2ASCIRCC00000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('NumberPad', NumberPadCmdString, value, qualifier)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        PIPCmdString = '\x2ASCPIPI000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        PIPCmdString = '\x2ASEPIPI################\x0A'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIP')

    def SetPIPPosition(self, value, qualifier):

        PIPPositionCmdString = '\x2ASCTPPP################\x0A'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '\x2ASCPOWR000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '\x2ASEPOWR################\x0A'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '\x2ASCPMUT000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '\x2ASEPMUT################\x0A'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x2ASCVOLU0000000000000{0:03d}\x0A'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x2ASEVOLU################\x0A'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[20:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[7] == 'F':
            print('{0} command has an error.'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x0A')
            if not res:
                print('Invalid/Unexpected Response')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x0A')
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
