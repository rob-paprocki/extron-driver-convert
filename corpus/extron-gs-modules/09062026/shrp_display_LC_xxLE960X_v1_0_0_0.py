from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AVMode': {'Status': {}},
            'ChannelDTV': {'Status': {}},
            'ChannelDTVStep': {'Status': {}},
            'ChannelTV': {'Status': {}},
            'ChannelTVStep': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def Set3D(self, value, qualifier):

        ValueStateValues = {
            '3D Off': 'TDCH0   \r',
            '2D to 3D': 'TDCH1   \r',
            'Side By Side': 'TDCH2   \r',
            'Top and Bottom': 'TDCH3   \r',
            '3D to 2D (Side By Side)': 'TDCH4   \r',
            '3D to 2D (Top and Bottom)': 'TDCH5   \r',
            '3D Auto': 'TDCH6   \r',
            '3D to 2D': 'TDCH7   \r'
        }

        CmdString = ValueStateValues[value]
        self.__SetHelper('3D', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'WIDE1   \r',
            'Zoom 14:9': 'WIDE2   \r',
            'Panorama': 'WIDE3   \r',
            'Full': 'WIDE4   \r',
            'Cinema 16:9': 'WIDE5   \r',
            'Cinema 14:9': 'WIDE6   \r',
            'Normal (PC)': 'WIDE7   \r',
            'Cinema (PC)': 'WIDE8   \r',
            'Full (PC)': 'WIDE9   \r',
            'Dot by Dot': 'WIDE10  \r',
            'Underscan': 'WIDE11  \r',
            'Auto': 'WIDE12  \r',
            'Original': 'WIDE13  \r'

        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Normal',
            '2': 'Zoom 14:9',
            '3': 'Panorama',
            '4': 'Full',
            '5': 'Cinema 16:9',
            '6': 'Cinema 14:9',
            '7': 'Normal (PC)',
            '8': 'Cinema (PC)',
            '9': 'Full (PC)',
            '10': 'Dot by Dot',
            '11': 'Underscan',
            '12': 'Auto',
            '13': 'Original'

        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '2': 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': 'AVMD1   \r',
            'Movie': 'AVMD2   \r',
            'Game': 'AVMD3   \r',
            'User': 'AVMD4   \r',
            'Dynamic (Fixed)': 'AVMD5   \r',
            'Dynamic': 'AVMD6   \r',
            'PC': 'AVMD7   \r',
            'xv Colour': 'AVMD8   \r',
            'Standard (3D)': 'AVMD14  \r',
            'Game (3D)': 'AVMD16  \r',
            'Movie Thx': 'AVMD17  \r',
            'Auto': 'AVMD100 \r'
        }

        AVModeCmdString = ValueStateValues[value]
        self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)

    def UpdateAVMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Standard',
            '2': 'Movie',
            '3': 'Game',
            '4': 'User',
            '5': 'Dynamic (Fixed)',
            '6': 'Dynamic',
            '7': 'PC',
            '8': 'xv Colour',
            '14': 'Standard (3D)',
            '16': 'Game (3D)',
            '17': 'Movie Thx',
            '100': 'Auto'
        }

        AVModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAVMode')

    def SetChannelDTV(self, value, qualifier):

        if 1 <= int(value) <= 999:
            SetChannelDTVDiscreteCmdString = 'DTVD{0:03d} \r'.format(int(value))
            self.__SetHelper('ChannelDTV', SetChannelDTVDiscreteCmdString, value, qualifier)
        else:
            print('Invalid Command for ChannelDTV')

    def SetChannelDTVStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'DTUP    \r',
            'Down': 'DTDW    \r'
        }

        ChannelDTVStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelDTVStep', ChannelDTVStepCmdString, value, qualifier)

    def SetChannelTV(self, value, qualifier):

        if 1 <= int(value) <= 99:
            ChannelTVDiscreteCmdString = 'DCCH{0:02d}  \r'.format(int(value))
            self.__SetHelper('ChannelTV', ChannelTVDiscreteCmdString, value, qualifier)
        else:
            print('Invalid Command for ChannelTV')

    def SetChannelTVStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP    \r',
            'Down': 'CHDW    \r'
        }

        ChannelTVStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelTVStep', ChannelTVStepCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IAVD1   \r',
            'HDMI 2': 'IAVD2   \r',
            'HDMI 3': 'IAVD3   \r',
            'HDMI 4': 'IAVD4   \r',
            'Input 5': 'IAVD5   \r',
            'Input 6': 'IAVD6   \r',
            'PC': 'IAVD7   \r',
            'Toggle': 'ITGD    \r',
            'TV': 'ITVD    \r',
            'DTV': 'IDTV    \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4',
            '5': 'Input 5',
            '6': 'Input 6',
            '7': 'PC'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response == 'ERR\r':
                ErrorString = 'Communication error or incorrect command'
                print(ErrorString)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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
