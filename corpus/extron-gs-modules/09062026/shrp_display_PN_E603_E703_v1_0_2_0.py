from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
from re import compile, search

class DeviceClass():
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input Type'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MainPosition': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PbyP2Position': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSource': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}

            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
         self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
         self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        self.Send(self.deviceUsername + '\r')

    def SetPassword(self, value, qualifier):
        self.Send(self.devicePassword + '\r')

    def SetAspectRatio(self, value, qualifier):
        PCAspectRatioStateValues = {
            'Wide': 'WIDE   1\r',
            'Normal': 'WIDE   2\r',
            'Dot by Dot': 'WIDE   3\r',
            'Zoom 1': 'WIDE   4\r',
            'Zoom 2': 'WIDE   5\r',
            }

        AVAspectRatioStateValues = {
            'Wide': 'WIDE   1\r',
            'Normal': 'WIDE   4\r',
            'Dot by Dot': 'WIDE   5\r',
            'Zoom 1': 'WIDE   2\r',
            'Zoom 2': 'WIDE   3\r',
            }

        InputType = qualifier['Input Type']

        if InputType not in ['PC', 'AV']:
            print('Invalid Command for SetAspectRatio')
        else:
            if InputType == 'PC':
                AspectRatioCmdString = PCAspectRatioStateValues[value]
            elif InputType == 'AV':
                AspectRatioCmdString = AVAspectRatioStateValues[value]

                self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        PCAspectRatioStateNames = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot',
            '4': 'Zoom 1',
            '5': 'Zoom 2',
           }

        AVAspectRatioStateNames = {
            '1': 'Wide',
            '4': 'Normal',
            '5': 'Dot by Dot',
            '2': 'Zoom 1',
            '3': 'Zoom 2',
           }

        InputType = qualifier['Input Type']

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if InputType == 'PC':
                    value = PCAspectRatioStateNames[res[0]]
                elif InputType == 'AV':
                    value = AVAspectRatioStateNames[res[0]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for AspectRatio')

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            'Off': 'ALCK   0\r',
            'On 1': 'ALCK   1\r',
            'On 2': 'ALCK   2\r'
        }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            '0': 'Off',
            '1': 'On 1',
            '2': 'On 2'
        }

        ExecutiveModeCmdString = 'ALCK????\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeStateValues[res[0]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for ExecutiveMode')

    def SetInput(self, value, qualifier):
        InputStateValues = {
            'DVI-I': 'INPS   1\r',
            'D-SUB[RGB]': 'INPS   2\r',
            'D-SUB[COMPONENT]': 'INPS   3\r',
            'D-SUB[VIDEO]': 'INPS   4\r',
            'HDMI 1[AV]': 'INPS   9\r',
            'HDMI 1[PC]': 'INPS  10\r',
            'HDMI 2[AV]': 'INPS  12\r',
            'HDMI 2[PC]': 'INPS  13\r',
            'DisplayPort': 'INPS  14\r'
        }

        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputStateValues = {
            1: 'DVI-I',
            2: 'D-SUB[RGB]',
            3: 'D-SUB[COMPONENT]',
            4: 'D-SUB[VIDEO]',
            9: 'HDMI 1[AV]',
            10: 'HDMI 1[PC]',
            12: 'HDMI 2[AV]',
            13: 'HDMI 2[PC]',
            14: 'DisplayPort'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateValues[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Input')

    def SetMainPosition(self, value, qualifier):
        MainPositionStateValues = {
            'Position 1': 'MWPP   0\r',
            'Position 2': 'MWPP   1\r'
        }

        MainPositionCmdString = MainPositionStateValues[value]
        self.__SetHelper('MainPosition', MainPositionCmdString, value, qualifier)

    def UpdateMainPosition(self, value, qualifier):
        MainPositionStateValues = {
            '0': 'Position 1',
            '1': 'Position 2'
        }

        MainPositionCmdString = 'MWPP????\r'
        res = self.__UpdateHelper('MainPosition', MainPositionCmdString, value, qualifier)
        if res:
            try:
                value = MainPositionStateValues[res[0]]
                self.WriteStatus('MainPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for MainPosition')

    def SetMute(self, value, qualifier):
        MuteStateValues = {
            'On': 'MUTE   1\r',
            'Off': 'MUTE   0\r',
            }

        MuteCmdString = MuteStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteStateNames = {
            '1': 'On',
            '0': 'Off',
           }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteStateNames[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Mute')

    def SetOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayStateValues = {
            'On 1': 'LOSD   0\r',
            'On 2': 'LOSD   2\r',
            'Off': 'LOSD   1\r'
        }

        OnScreenDisplayCmdString = OnScreenDisplayStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayStateValues = {
            '0': 'On 1',
            '2': 'On 2',
            '1': 'Off'
        }

        OnScreenDisplayCmdString = 'LOSD????\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateValues[res[0]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for OnScreenDisplay')

    def SetPbyP2Position(self, value, qualifier):
        PbyP2PositionStateValues = {
            'Position 1': 'MW2P   0\r',
            'Position 2': 'MW2P   1\r',
            'Position 3': 'MW2P   2\r'
        }

        PbyP2PositionCmdString = PbyP2PositionStateValues[value]
        self.__SetHelper('PbyP2Position', PbyP2PositionCmdString, value, qualifier)

    def UpdatePbyP2Position(self, value, qualifier):
        PbyP2PositionStateValues = {
            '0': 'Position 1',
            '1': 'Position 2',
            '2': 'Position 3'
        }

        PbyP2PositionCmdString = 'MW2P????\r'
        res = self.__UpdateHelper('PbyP2Position', PbyP2PositionCmdString, value, qualifier)
        if res:
            try:
                value = PbyP2PositionStateValues[res[0]]
                self.WriteStatus('PbyP2Position', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for PbyP2Position')

    def SetPIPMode(self, value, qualifier):
        PIPModeStateValues = {
            'PIP': 'MWIN   1\r',
            'PbyP 1': 'MWIN   2\r',
            'PbyP 2': 'MWIN   3\r',
            'Off': 'MWIN   0\r',
            }

        PIPModeCmdString = PIPModeStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        PIPModeStateNames = {
            '1': 'PIP',
            '2': 'PbyP 1',
            '3': 'PbyP 2',
            '0': 'Off',
           }

        PIPModeCmdString = 'MWIN????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeStateNames[res[0]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for PIPMode')

    def SetPIPSize(self, value, qualifier):
        PIPSizeConstraints = {
            'Min': 1,
            'Max': 64
            }

        if PIPSizeConstraints['Min'] <= value <= PIPSizeConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{0: >4}\r'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):
        PIPSizeCmdString = 'MPSZ????\r'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('PIPSize', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for PIPSize')

    def SetPIPSource(self, value, qualifier):
        PIPSourceStateValues = {
            'DVI-I': 'MWIP   1\r',
            'D-SUB[RGB]': 'MWIP   2\r',
            'D-SUB[COMPONENT]': 'MWIP   3\r',
            'D-SUB[VIDEO]': 'MWIP   4\r',
            'HDMI 1[AV]': 'MWIP   9\r',
            'HDMI 1[PC]': 'MWIP  10\r',
            'HDMI 2[AV]': 'MWIP  12\r',
            'HDMI 2[PC]': 'MWIP  13\r',
            'DisplayPort': 'MWIP  14\r'
        }

        PIPSourceCmdString = PIPSourceStateValues[value]
        self.__SetHelper('PIPSource', PIPSourceCmdString, value, qualifier, 3)

    def UpdatePIPSource(self, value, qualifier):
        PIPSourceStateValues = {
            1: 'DVI-I',
            2: 'D-SUB[RGB]',
            3: 'D-SUB[COMPONENT]',
            4: 'D-SUB[VIDEO]',
            9: 'HDMI 1[AV]',
            10: 'HDMI 1[PC]',
            12: 'HDMI 2[AV]',
            13: 'HDMI 2[PC]',
            14: 'DisplayPort'
        }

        PIPSourceCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPSource', PIPSourceCmdString, value, qualifier)
        if res:
            try:
                value = PIPSourceStateValues[int(res)]
                self.WriteStatus('PIPSource', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for PIPSource')

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On': 'POWR   1\r',
            'Off': 'POWR   0\r'
        }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input Signal Waiting Mode',
           }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Power')

    def SetVolume(self, value, qualifier):
        VolumeConstraints = {
            'Min': 0,
            'Max': 31
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOLM{0: >4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
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
                print('Invalid Response for Volume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            if response[:3] == 'ERR':
                print('{0} no relevant command or command cannot be used in the current state of the device'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())
         
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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        #try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        #except AttributeError:
           # print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        #try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        #except AttributeError:
        #    print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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
