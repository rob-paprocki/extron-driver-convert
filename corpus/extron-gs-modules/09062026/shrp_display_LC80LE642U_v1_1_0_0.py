from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ATVChannelDirectCommand': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'DTVChannelAirCommand': {'Status': {}},
            'DTVChannelCable2Command': {'Status': {}},
            'DTVChannelCable3Command': {'Status': {}},
            'DTVChannelCableMajorCommand': {'Status': {}},
            'DTVChannelCableMinorCommand': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.deviceUsername = None
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Username:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Toggle (AV)': 'WIDE0   \r',
            'Side Bar (AV)': 'WIDE1   \r',
            'S.Stretch (AV)': 'WIDE2   \r',
            'Zoom (AV)': 'WIDE3   \r',
            'Stretch (AV)': 'WIDE4   \r',
            'Normal (PC)': 'WIDE5   \r',
            'Zoom (PC)': 'WIDE6   \r',
            'Stretch (PC)': 'WIDE7   \r',
            'Dot by Dot': 'WIDE8   \r',
            'Full Screen': 'WIDE9   \r',
            'Auto': 'WIDE10  \r',
            'Original': 'WIDE11  \r',
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            '1': 'Side Bar (AV)',
            '2': 'S.Stretch (AV)',
            '3': 'Zoom (AV)',
            '4': 'Stretch (AV)',
            '5': 'Normal (PC)',
            '6': 'Zoom (PC)',
            '7': 'Stretch (PC)',
            '8': 'Dot by Dot',
            '9': 'Full Screen',
            '10': 'Auto',
            '11': 'Original',
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetATVChannelDirectCommand(self, value, qualifier):

        temp = value
        if temp:
            if 1 <= int(temp) <= 135:
                ATVChannelDirectCommandCmdString = 'DCCH{0} \r'.format(temp.zfill(3))
                self.__SetHelper('ATVChannelDirectCommand', ATVChannelDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetATVChannelDirectCommand')
        else:
            print('Invalid Command for SetATVChannelDirectCommand')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r',
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            '2': 'Off',
            '1': 'On',
        }

        AudioMuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[0:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetChannelStep(self, value, qualifier):

        ChannelStepState = {
            'Up': 'RCKY34  \r',
            'Down': 'RCKY35  \r',
        }

        ChannelStepCmdString = ChannelStepState[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDTVChannelAirCommand(self, value, qualifier):

        temp = value
        if temp:
            if 100 <= int(temp) <= 9999:
                DTVChannelAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(temp))
                self.__SetHelper('DTVChannelAirCommand', DTVChannelAirCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelAirCommand')

    def SetDTVChannelCable2Command(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 9999:
                DTVChannelCable2CommandCmdString = 'DC10{0:04d}\r'.format(int(temp))
                self.__SetHelper('DTVChannelCable2Command', DTVChannelCable2CommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelCable2Command')
        else:
            print('Invalid Command for SetDTVChannelCable2Command')

    def SetDTVChannelCable3Command(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 6383:
                DTVChannelCable3CommandCmdString = 'DC11{0:04d}\r'.format(int(temp))
                self.__SetHelper('DTVChannelCable3Command', DTVChannelCable3CommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelCable3Command')
        else:
            print('Invalid Command for SetDTVChannelCable3Command')

    def SetDTVChannelCableMajorCommand(self, value, qualifier):

        temp = value
        if temp:
            if 1 <= int(temp) <= 999:
                DTVChannelCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(temp))
                self.__SetHelper('DTVChannelCableMajorCommand', DTVChannelCableMajorCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelCableMajorCommand')
        else:
            print('Invalid Command for SetDTVChannelCableMajorCommand')

    def SetDTVChannelCableMinorCommand(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 999:
                DTVChannelCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(temp))
                self.__SetHelper('DTVChannelCableMinorCommand', DTVChannelCableMinorCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelCableMinorCommand')
        else:
            print('Invalid Command for SetDTVChannelCableMinorCommand')

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'RCKY54  \r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'Toggle': 'ITGD0   \r',
            'TV': 'ITVD0   \r',
            'HDMI 1': 'IAVD1   \r',
            'HDMI 2': 'IAVD2   \r',
            'HDMI 3': 'IAVD3   \r',
            'HDMI 4': 'IAVD4   \r',
            'Component': 'IAVD5   \r',
            'Video 1': 'IAVD6   \r',
            'Video 2': 'IAVD7   \r',
            'PC': 'IAVD8   \r',
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4',
            '5': 'Component',
            '6': 'Video 1',
            '7': 'Video 2',
            '8': 'PC',
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[0:1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'RCKY41  \r',
            'Down': 'RCKY42  \r',
            'Left': 'RCKY43  \r',
            'Right': 'RCKY44  \r',
            'Menu': 'RCKY38  \r',
            'Enter': 'RCKY40  \r',
            'Return': 'RCKY45  \r',
            'Exit': 'RCKY46  \r',
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r',
        }

        PowerCmdString = PowerState[value]
        PowerControlCmdString1 = 'RSPW1   \x0D'
        PowerControlCmdString2 = 'RSPW2   \x0D'
        if value == 'On':
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        elif 'Serial' in self.ConnectionType and value == 'Off':
            self.__SetHelper('Power', PowerControlCmdString1, value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.__SetHelper('Power', PowerControlCmdString2, value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '1': 'On',
            '0': 'Off',
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            if value == 100:
                VolumeCmdString = 'VOLM{0} \r'.format(value)
            else:
                VolumeCmdString = 'VOLM{0:02d}  \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                print('{0} Communication error or incorrect command'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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
