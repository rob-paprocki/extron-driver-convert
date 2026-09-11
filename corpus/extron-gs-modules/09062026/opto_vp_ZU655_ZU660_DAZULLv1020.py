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
            '3DFormat': {'Status': {}},
            '3DInvert': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'DLPLink': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
        }

    def Set3DFormat(self, value, qualifier):

        States = {
            'Frame Packing': '7',
            'Side by Side': '1',
            'Top and Bottom': '2',
            'Frame Sequential': '3'
        }

        CmdString = '~00405 {0}\r'.format(States[value])
        self.__SetHelper('3DFormat', CmdString, value, qualifier)

    def Set3DInvert(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '~00231 {0}\r'.format(States[value])
        self.__SetHelper('3DInvert', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Auto': '7',
            '4:3': '1',
            '16:9': '2',
            '16:10': '3',
            'Native': '6'
        }

        AspectRatioCmdString = '~0060 {0}\r'.format(States[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStates = {
            '7': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '6': 'Native'
        }
        AspectRatioCmdString = '~00127 1\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStates[res[2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAVMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~00325 {0}\r'.format(States[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):
        AVMuteStates = {
            '1': 'On',
            '0': 'Off'
        }

        CmdString = '~00355 1\r'
        res = self.__UpdateHelper('AVMute', CmdString, value, qualifier)
        if res:
            try:
                value = AVMuteStates[res[2:-1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/Unexpected Response'])

    def SetDisplayMode(self, value, qualifier):

        States = {
            'Bright': '2',
            'Presentation': '1',
            'Movie': '3',
            'sRGB': '4',
            'Blending': '19',
            'DICOM SIM.': '13',
            'User': '5'
        }

        DisplayModeCmdString = '~0020 {0}\r'.format(States[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        DisplayModeStates = {
            '2': 'Bright',
            '1': 'Presentation',
            '3': 'Movie',
            '4': 'sRGB',
            '19': 'Blending',
            '13': 'DICOM SIM.',
            '5': 'User'
        }
        DisplayModeCmdString = '~00123 1\r'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = DisplayModeStates[res[2:-1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode: Invalid/Unexpected Response'])

    def SetDLPLink(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('DLPLink', '~00230 {0}\r'.format(States[value]), value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('Freeze', '~0004 {0}\r'.format(States[value]), value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'VGA': '5',
            'HDMI 1': '1',
            'HDMI 2': '3',
            'DVI-D': '2',
            'HDBaseT': '21'
        }
        self.__SetHelper('Input', '~0012 {0}\r'.format(States[value]), value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputStates = {
            '2': 'VGA',
            '7': 'HDMI 1',
            '3': 'HDMI 2',
            '1': 'DVI-D',
            '12': 'HDBaseT'
        }
        InputCmdString = '~00121 1\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStates[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '~00108 1\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '10',
            'Down': '14',
            'Left': '11',
            'Right': '13',
            'Enter': '12',
            'Menu': '20',
            'Exit': '72'
        }

        self.__SetHelper('MenuNavigation', '~00140 {0}\r'.format(States[value]), value, qualifier)

    def SetPIPInput(self, value, qualifier):

        States = {
            'VGA': '2',
            'HDMI 1': '1',
            'HDMI 2': '3',
            'DVI-D': '9',
            'HDBaseT': '10'
        }

        PIPInputCmdString = '~00305 {0}\r'.format(States[value])
        self.__SetHelper('MenuNavigation', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputStates = {
            '2': 'VGA',
            '7': 'HDMI 1',
            '3': 'HDMI 2',
            '1': 'DVI-D',
            '16': 'HDBaseT'
        }
        PIPInputCmdString = '~00131 1\r'
        res = self.__UpdateHelper('LampUsage', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPInputStates[res[2:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/Unexpected Response'])

    def SetPIPMode(self, value, qualifier):

        States = {
            'Picture In Picture': '2',
            'Picture By Picture': '1',
            'Off': '0'
        }

        self.__SetHelper('PIPMode', '~00302 {0}\r'.format(States[value]), value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }
        self.__SetHelper('Power', '~0000 {0}\r'.format(States[value]), value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStates = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '~00124 1\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStates[res[2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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
