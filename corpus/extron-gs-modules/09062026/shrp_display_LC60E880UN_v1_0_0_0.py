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
            'ATVChannelDirectCommand': {'Status': {}},
            'AVMode': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DTVChannelAirCommand': {'Status': {}},
            'DTVChannelCable1Command': {'Status': {}},
            'DTVChannelCable2Command': {'Status': {}},
            'InputA': {'Status': {}},
            'InputB': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Side Bar (AV)': 'WIDE1   \r',
            'S. Stretch (AV)': 'WIDE2   \r',
            'Zoom (AV)': 'WIDE3   \r',
            'Stretch (AV)': 'WIDE4   \r',
            'Normal (PC)': 'WIDE5   \r',
            'Zoom (PC)': 'WIDE6   \r',
            'Stretch (PC)': 'WIDE7   \r',
            'Dot by Dot': 'WIDE8   \r',
            'Full Screen (AV)': 'WIDE9   \r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '1': 'Side Bar (AV)',
            '2': 'S. Stretch (AV)',
            '3': 'Zoom (AV)',
            '4': 'Stretch (AV)',
            '5': 'Normal (PC)',
            '6': 'Zoom (PC)',
            '7': 'Stretch (PC)',
            '8': 'Dot by Dot',
            '9': 'Full Screen (AV)'
            }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetATVChannelDirectCommand(self, value, qualifier):

        if 1 <= int(value) <= 135:
            ATVChannelDirectCommandCmdString = 'DCCH{0} \r'.format(value.zfill(3))
            self.__SetHelper('ATVChannelDirectCommand', ATVChannelDirectCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATVChannelDirectCommand')

    def SetAVMode(self, value, qualifier):

        AVModeState = {
            'Standard': 'AVMD1   \r',
            'Movie': 'AVMD2   \r',
            'Game': 'AVMD3   \r',
            'User': 'AVMD4   \r',
            'Dynamic (Fixed)': 'AVMD5   \r',
            'Dynamic': 'AVMD6   \r',
            'PC': 'AVMD7   \r',
            'Auto': 'AVMD100 \r'
            }

        AVModeCmdString = AVModeState[value]
        self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)

    def UpdateAVMode(self, value, qualifier):

        AVModeState = {
            '1': 'Standard',
            '2': 'Movie',
            '3': 'Game',
            '4': 'User',
            '5': 'Dynamic (Fixed)',
            '6': 'Dynamic',
            '7': 'PC',
            '100': 'Auto'
            }

        AVModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = AVModeState[res[0:-1]]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mode: Invalid/Unexpected Response'])

    def SetChannelStep(self, value, qualifier):

        ChannelStepState = {
            'Up': 'CHUP1   \r',
            'Down': 'CHDW1   \r'
            }

        ChannelStepCmdString = ChannelStepState[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDTVChannelAirCommand(self, value, qualifier):

        if 100 <= int(value) <= 9999:
            DTVChannelAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(value))
            self.__SetHelper('DTVChannelAirCommand', DTVChannelAirCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelAirCommand')

    def SetDTVChannelCable1Command(self, value, qualifier):

        if value.__contains__('.'):
            major, minor = value.split('.')
        else:
            major = value
            minor = '0'

        if 1 <= int(major) <= 999 and 0 <= int(minor) <= 999:
            DTVChannelCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(major))
            DTVChannelCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(minor))
            self.__SetHelper('DTVChannelCable1Command', DTVChannelCableMajorCommandCmdString, value, qualifier)
            self.__SetHelper('DTVChannelCable1Command', DTVChannelCableMinorCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelCable1Command')

    def SetDTVChannelCable2Command(self, value, qualifier):

        if 0 <= int(value) <= 16383:
            DTVChannelCable2CommandCmdString = 'DC1{0:05d}\r'.format(int(value))
            self.__SetHelper('DTVChannelCable2Command', DTVChannelCable2CommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTVChannelCable2Command')

    def SetInputA(self, value, qualifier):

        InputAState = {
            'TV': 'ITVD0   \r',
            'Component 1': 'IAVD1   \r',
            'Component 2': 'IAVD2   \r',
            'Video': 'IAVD3   \r',
            'PC': 'IAVD4   \r',
            'HDMI 1': 'IAVD5   \r',
            'HDMI 2': 'IAVD6   \r',
            'HDMI 3': 'IAVD7   \r',
            'HDMI 4': 'IAVD8   \r'
            }

        InputACmdString = InputAState[value]
        self.__SetHelper('InputA', InputACmdString, value, qualifier)

    def UpdateInputA(self, value, qualifier):

        InputAState = {
            '1': 'Component 1',
            '2': 'Component 2',
            '3': 'Video',
            '4': 'PC',
            '5': 'HDMI 1',
            '6': 'HDMI 2',
            '7': 'HDMI 3',
            '8': 'HDMI 4'
            }

        InputACmdString = 'IAVD????\r'
        res = self.__UpdateHelper('InputA', InputACmdString, value, qualifier)
        if res:
            try:
                value = InputAState[res[0:-1]]
                self.WriteStatus('InputA', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input A: Invalid/Unexpected Response'])

    def SetInputB(self, value, qualifier):

        InputBState = {
            'Auto': 'INP10   \r',
            'Video': 'INP11   \r',
            'Component': 'INP12   \r'
            }

        InputBCmdString = InputBState[value]
        self.__SetHelper('InputB', InputBCmdString, value, qualifier)

    def UpdateInputB(self, value, qualifier):

        InputBState = {
            '0': 'Auto',
            '1': 'Video',
            '2': 'Component'
            }

        InputBCmdString = 'INP1????\r'
        res = self.__UpdateHelper('InputB', InputBCmdString, value, qualifier)
        if res:
            try:
                value = InputBState[res[0:-1]]
                self.WriteStatus('InputB', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input B: Invalid/Unexpected Response'])

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r'
            }

        MuteCmdString = MuteState[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteState = {
            '1': 'On',
            '2': 'Off'
            }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteState[res[0:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r'
            }

        PowerCmdString = PowerState[value]
        if value == 'On':
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.__SetHelper('Power', 'RSPW1   \r', value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '1': 'On',
            '0': 'Off'
            }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:02d}  \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} Communication error or incorrect command'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} Invalid/Unexpected Response'.format(command)])
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
