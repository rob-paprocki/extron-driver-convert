from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 10
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AVMode': {'Status': {}},
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
            'Surround': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Side Bar': 'WIDE1   \r',
            'S.Strech': 'WIDE2   \r',
            'Zoom(AV)': 'WIDE3   \r',
            'Stretch': 'WIDE4   \r',
            'Normal(PC)': 'WIDE5   \r',
            'Zoom(PC)': 'WIDE6   \r',
            'Stretch(PC)': 'WIDE7   \r',
            'DotByDot(PC)': 'WIDE8   \r',
            'FullScreen': 'WIDE9   \r',
            'Auto': 'WIDE10  \r',
            'Original': 'WIDE11  \r'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1 ': 'Side Bar',
            '2 ': 'S.Strech',
            '3 ': 'Zoom(AV)',
            '4 ': 'Stretch',
            '5 ': 'Normal(PC)',
            '6 ': 'Zoom(PC)',
            '7 ': 'Stretch(PC)',
            '8 ': 'DotByDot(PC)',
            '9 ': 'FullScreen',
            '10': 'Auto',
            '11': 'Original'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '2': 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': 'AVMD001 \r',
            'Movie': 'AVMD002 \r',
            'User': 'AVMD004 \r',
            'Dynamic': 'AVMD005 \r',
            'Dynamic(Fixed)': 'AVMD006 \r',
            'PC': 'AVMD007 \r'
        }

        if value in ValueStateValues:
            AVModeCmdString = ValueStateValues[value]
            self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMode')

    def UpdateAVMode(self, value, qualifier):
        ValueStateValues = {
            '1': 'Standard',
            '2': 'Movie',
            '4': 'User',
            '5': 'Dynamic',
            '6': 'Dynamic(Fixed)',
            '7': 'PC'
        }

        AVModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAVMode')

    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP0   \r',
            'Down': 'CHDW0   \r'
        }

        if value in ValueStateValues:
            ChannelTVCmdString = ValueStateValues[value]
            self.__SetHelper('ChannelTV', ChannelTVCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelTV')

    def SetChannelTVCommand(self, value, qualifier):

        temp = value
        if temp:
            if 1 <= int(temp) <= 135:
                ChannelTVCommandCmdString = 'DCCH{0:03d} \r'.format(int(temp))
                self.__SetHelper('ChannelTVCommand', ChannelTVCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetChannelTVCommand')
        else:
            print('Invalid Command for SetChannelTVCommand')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDigitalAirCommand(self, value, qualifier):

        temp = value
        if temp:
            if 100 <= int(temp) <= 9999:
                DigitalAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(temp))
                self.__SetHelper('DigitalAirCommand', DigitalAirCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalAirCommand')
        else:
            print('Invalid Command for SetDigitalAirCommand')

    def SetDigitalCableCommand1(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 9999:
                DigitalCableCommand1CmdString = 'DC10{0:04d}\r'.format(int(temp))
                self.__SetHelper('DigitalCableCommand1', DigitalCableCommand1CmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableCommand1')
        else:
            print('Invalid Command for SetDigitalCableCommand1')

    def SetDigitalCableCommand2(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 6383:
                DigitalCableCommand2CmdString = 'DC11{0:04d}\r'.format(int(temp))
                self.__SetHelper('DigitalCableCommand2', DigitalCableCommand2CmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableCommand2')
        else:
            print('Invalid Command for SetDigitalCableCommand2')

    def SetDigitalCableMajorCommand(self, value, qualifier):

        temp = value
        if temp:
            if 1 <= int(temp) <= 999:
                DigitalCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(temp))
                self.__SetHelper('DigitalCableMajorCommand', DigitalCableMajorCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableMajorCommand')
        else:
            print('Invalid Command for SetDigitalCableMajorCommand')

    def SetDigitalCableMinorCommand(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 999:
                DigitalCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(temp))
                self.__SetHelper('DigitalCableMinorCommand', DigitalCableMinorCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableMinorCommand')
        else:
            print('Invalid Command for SetDigitalCableMinorCommand')

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'RCKY54  \r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': 'ITVD0   \r',
            'HDMI 1': 'IAVD1   \r',
            'HDMI 2': 'IAVD2   \r',
            'HDMI 3': 'IAVD3   \r',
            'Video': 'IAVD4   \r',
            'Component': 'IAVD5   \r',
            'PC/VGA': 'IAVD6   \r',
            'USB': 'IAVD7   \r',
            'Home Network': 'IAVD8   \r'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            '0': 'TV',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'Video',
            '5': 'Component',
            '6': 'PC/VGA',
            '7': 'USB',
            '8': 'Home Network'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')
                
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'RCKY38  \r',
            'Up': 'RCKY41  \r',
            'Down': 'RCKY42  \r',
            'Left': 'RCKY43  \r',
            'Right': 'RCKY44  \r',
            'Enter': 'RCKY40  \r',
            'Exit': 'RCKY46  \r',
            'Return': 'RCKY45  \r'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            if 'Off' in value:
                if 'Serial' in self.ConnectionType:
                    self.__SetHelper('Power', 'RSPW1   \r', value, qualifier)
                else:
                    self.__SetHelper('Power', 'RSPW2   \r', value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetSurround(self, value, qualifier):

        ValueStateValues = {
            'On': 'ACSU1   \r',
            'Off': 'ACSU2   \r'
        }

        if value in ValueStateValues:
            SurroundCmdString = ValueStateValues[value]
            self.__SetHelper('Surround', SurroundCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurround')

    def UpdateSurround(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '2': 'Off'
        }

        SurroundCmdString = 'ACSU????\r'
        res = self.__UpdateHelper('Surround', SurroundCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Surround', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSurround')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        
        if 'ERR' in response:
            self.Error(['{}: Error occurred.'.format(sourceCmdName)])
            response = ''
        elif 'WAIT' in response:
            self.Error([sourceCmdName + ' : Waiting for a response.'])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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