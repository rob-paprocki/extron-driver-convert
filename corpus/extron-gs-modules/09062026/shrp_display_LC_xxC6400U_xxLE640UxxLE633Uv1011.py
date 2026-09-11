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
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelTV': {'Status': {}},
            'ChannelTVCommand': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DigitalAirCommand': {'Status': {}},
            'DigitalCableCommand1': {'Status': {}},
            'DigitalCableCommand2': {'Status': {}},
            'DigitalCableMajorCommand': {'Status': {}},
            'DigitalCableMinorCommand': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self.InitialStart = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Side Bar': 'WIDE1   \r',
            'S.Stretch': 'WIDE2   \r',
            'Zoom [AV]': 'WIDE3   \r',
            'Stretch [AV]': 'WIDE4   \r',
            'Normal [PC]': 'WIDE5   \r',
            'Zoom [PC]': 'WIDE6   \r',
            'Stretch [PC]': 'WIDE7   \r',
            'Dot by Dot [PC]': 'WIDE8   \r',
            'Full Screen [AV]': 'WIDE9   \r',
            'Auto': 'WIDE10  \r',
            'Original': 'WIDE11  \r',
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            '1 ': 'Side Bar',
            '2 ': 'S.Stretch',
            '3 ': 'Zoom [AV]',
            '4 ': 'Stretch [AV]',
            '5 ': 'Normal [PC]',
            '6 ': 'Zoom [PC]',
            '7 ': 'Stretch [PC]',
            '8 ': 'Dot by Dot [PC]',
            '9 ': 'Full Screen [AV]',
            '10': 'Auto',
            '11': 'Original',
        }

        res = self.__UpdateHelper('AspectRatio', 'WIDE????\r', value, qualifier)
        try:
            value = AspectRatioStateValues[res[0:2]]
            self.WriteStatus('AspectRatio', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Invalid/Unexpected response for AspectRatio'])

    def SetAudioInput(self, value, qualifier):

        AudioInputCmdString = 'ACHA0   \r'
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            '1': 'On',
            '2': 'Off'
        }

        res = self.__UpdateHelper('AudioMute', 'MUTE????\r', value, qualifier)
        try:
            value = AudioMuteStateValues[res[0]]
            self.WriteStatus('AudioMute', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Invalid/Unexpected response for AudioMute'])

    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP0   \r',
            'Down': 'CHDW0   \r'
        }

        ChannelTVCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelTV', ChannelTVCmdString, value, qualifier, 0.3)

    def SetChannelTVCommand(self, value, qualifier):

        if 1 <= int(value) <= 135:
            ChannelTVCommandCmdString = 'DCCH{0:03d} \r'.format(int(value))
            self.__SetHelper('ChannelTVCommand', ChannelTVCommandCmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetChannelTVCommand')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDigitalAirCommand(self, value, qualifier):

        if 100 <= int(value) <= 9999:
            DigitalAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(value))
            self.__SetHelper('DigitalAirCommand', DigitalAirCommandCmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetDigitalAirCommand')

    def SetDigitalCableCommand1(self, value, qualifier):

        if 0 <= int(value) <= 9999:
            DigitalCableCommand1CmdString = 'DC10{0:04d}\r'.format(int(value))
            self.__SetHelper('DigitalCableCommand1', DigitalCableCommand1CmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetDigitalCableCommand1')

    def SetDigitalCableCommand2(self, value, qualifier):

        if 0 <= int(value) <= 6383:
            DigitalCableCommand2CmdString = 'DC11{0:04d}\r'.format(int(value))
            self.__SetHelper('DigitalCableCommand2', DigitalCableCommand2CmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetDigitalCableCommand2')

    def SetDigitalCableMajorCommand(self, value, qualifier):

        if 1 <= int(value) <= 999:
            DigitalCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(value))
            self.__SetHelper('DigitalCableMajorCommand', DigitalCableMajorCommandCmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetDigitalCableMajorCommand')

    def SetDigitalCableMinorCommand(self, value, qualifier):

        if 0 <= int(value) <= 999:
            DigitalCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(value))
            self.__SetHelper('DigitalCableMinorCommand', DigitalCableMinorCommandCmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetDigitalCableMinorCommand')

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'RCKY54  \r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IAVD1   \r',
            'HDMI 2': 'IAVD2   \r',
            'HDMI 3': 'IAVD3   \r',
            'HDMI 4': 'IAVD4   \r',
            'Component': 'IAVD5   \r',
            'Video 1': 'IAVD6   \r',
            'Video 2': 'IAVD7   \r',
            'PC': 'IAVD8   \r',
            'TV': 'ITVD0   \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 0.3)

    def UpdateInput(self, value, qualifier):
        InputStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4',
            '5': 'Component',
            '6': 'Video 1',
            '7': 'Video 2',
            '8': 'PC',
            }
        res = self.__UpdateHelper('Input', 'IAVD????\r', value, qualifier)
        try:
            value = InputStateValues[res[0]]
            self.WriteStatus('Input', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Invalid/Unexpected response for Input'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'RCKY41  \r',
            'Down': 'RCKY42  \r',
            'Left': 'RCKY43  \r',
            'Right': 'RCKY44  \r',
            'Menu': 'RCKY38  \r',
            'Enter': 'RCKY40  \r',
            'Exit': 'RCKY46  \r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 0.3)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r'
        }

        PowerCmdString = ValueStateValues[value]
        if 'Off' in value and self.InitialStart:
            if self.ConnectionType == 'Serial':
                self.__SetHelper('Power', 'RSPW1   \r', value, qualifier, .5)
            else:
                self.__SetHelper('Power', 'RSPW2   \r', value, qualifier, .5)
            self.InitialStart = False
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 0.3)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('Power', 'POWR????\r', value, qualifier)
        try:
            value = PowerStateValues[res[0]]
            self.WriteStatus('Power', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Invalid/Unexpected response for Power'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 0.3)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'VOLM????\r', value, qualifier)
        try:
            value = res[0:3]
            self.WriteStatus('Volume', int(value), qualifier)
        except (ValueError, IndexError):
            self.Error(['Invalid/Unexpected response for Volume'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'ERR\r': 'Communication Error or Incorrect Command'}
        if response:
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, CmdDefaultResponseTimeout=0.3):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, CmdDefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['Invalid/unexpected response for' + command])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command. Unidirectional mode.')
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
        self.InitialStart = True

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

