from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
        self.devicePassword = None
        self.deviceUsername = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AdjustmentLock': {'Status': {}},
            'AdjustmentLockTarget': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'MainPosition': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PbyP2Position': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        
        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAdjustmentLock(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': 1,
            'Mode 2': 2,
            'Off': 0
        }

        AdjustmentLockCmdString = 'ALCK{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier)

    def UpdateAdjustmentLock(self, value, qualifier):

        ValueStateValues = {
            1: 'Mode 1',
            2: 'Mode 2',
            0: 'Off'
        }

        AdjustmentLockCmdString = 'ALCK????\r'
        res = self.__UpdateHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AdjustmentLock', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAdjustmentLock')

    def SetAdjustmentLockTarget(self, value, qualifier):

        ValueStateValues = {
            'Remote Control': 0,
            'Monitor Buttons': 1,
            'Both': 2
        }

        AdjustmentLockTargetCmdString = 'ALTG{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('AdjustmentLockTarget', AdjustmentLockTargetCmdString, value, qualifier)

    def UpdateAdjustmentLockTarget(self, value, qualifier):

        ValueStateValues = {
            0: 'Remote Control',
            1: 'Monitor Buttons',
            2: 'Both'
        }

        AdjustmentLockTargetCmdString = 'ALTG????\r'
        res = self.__UpdateHelper('AdjustmentLockTarget', AdjustmentLockTargetCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AdjustmentLockTarget', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAdjustmentLockTarget')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioValuesPC = {
            'Wide': 1,
            'Zoom 1': 4,
            'Zoom 2': 5,
            'Normal': 2,
            'Dot by Dot': 3
            }

        AspectRatioValuesAV = {
            'Wide': 1,
            'Zoom 1': 2,
            'Zoom 2': 3,
            'Normal': 4,
            'Dot by Dot': 5
            }
        type = qualifier['Input']
        if type in ['PC', 'AV']:
            if type == 'PC':
                AspectRatioCmdString = 'WIDE{0:4}\r'.format(AspectRatioValuesPC[value])
            else:
                AspectRatioCmdString = 'WIDE{0:4}\r'.format(AspectRatioValuesAV[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNamesAV = {
            1: 'Wide',
            2: 'Zoom 1',
            3: 'Zoom 2',
            4: 'Normal',
            5: 'Dot by Dot'
            }

        AspectRatioStateNamesPC = {
            1: 'Wide',
            4: 'Zoom 1',
            5: 'Zoom 2',
            2: 'Normal',
            3: 'Dot by Dot'
            }
        type = qualifier['Input']
        if type in ['PC', 'AV']:
            AspectRatioCmdString = 'WIDE????\r'
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    if type == 'PC':
                        self.WriteStatus('AspectRatio', AspectRatioStateNamesPC[value], qualifier)
                    else:
                        self.WriteStatus('AspectRatio', AspectRatioStateNamesAV[value], qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAspectRatio')
        else:
            print('Invalid Command for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AGIN{0:4}\r'.format(1)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1 (PC)': 10,
            'HDMI 2 (PC)': 13,
            'HDMI 3 (PC)': 18,
            'D-Sub 1 (Component)': 3,
            'D-Sub 1 (Video)': 4,
            'DisplayPort': 14,
            'D-Sub 1 (RGB)': 2,
            'D-Sub 2': 16,
            'HDMI 1 (AV)': 9,
            'HDMI 2 (AV)': 12,
            'HDMI 3 (AV)': 17
        }

        InputCmdString = 'INPS{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            10: 'HDMI 1 (PC)',
            13: 'HDMI 2 (PC)',
            18: 'HDMI 3 (PC)',
            3: 'D-Sub 1 (Component)',
            4: 'D-Sub 1 (Video)',
            14: 'DisplayPort',
            2: 'D-Sub 1 (RGB)',
            16: 'D-Sub 2',
            9: 'HDMI 1 (AV)',
            12: 'HDMI 2 (AV)',
            17: 'HDMI 3 (AV)'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMainPosition(self, value, qualifier):

        ValueStateValues = {
            'Position 1': 0,
            'Position 2': 1
        }

        MainPositionCmdString = 'MWPP{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('MainPosition', MainPositionCmdString, value, qualifier)

    def UpdateMainPosition(self, value, qualifier):

        ValueStateValues = {
            0: 'Position 1',
            1: 'Position 2'
        }

        MainPositionCmdString = 'MWPP????\r'
        res = self.__UpdateHelper('MainPosition', MainPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('MainPosition', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMainPosition')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        MuteCmdString = 'MUTE{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Mute', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On 1': 0,
            'Off': 1,
            'On 2': 2
        }

        OnScreenDisplayCmdString = 'LOSD{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            0: 'On 1',
            1: 'Off',
            2: 'On 2'
        }

        OnScreenDisplayCmdString = 'LOSD????\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPbyP2Position(self, value, qualifier):

        ValueStateValues = {
            'Position 1': 0,
            'Position 2': 1,
            'Position 3': 2
        }

        PbyP2PositionCmdString = 'MW2P{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('PbyP2Position', PbyP2PositionCmdString, value, qualifier)

    def UpdatePbyP2Position(self, value, qualifier):

        ValueStateValues = {
            0: 'Position 1',
            1: 'Position 2',
            2: 'Position 3'
        }

        PbyP2PositionCmdString = 'MW2P????\r'
        res = self.__UpdateHelper('PbyP2Position', PbyP2PositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('PbyP2Position', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePbyP2Position')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1 (PC)': 10,
            'HDMI 2 (PC)': 13,
            'HDMI 3 (PC)': 18,
            'D-Sub 1 (Component)': 3,
            'D-Sub 1 (Video)': 4,
            'DisplayPort': 14,
            'D-Sub 1 (RGB)': 2,
            'D-Sub 2': 16,
            'HDMI 1 (AV)': 9,
            'HDMI 2 (AV)': 12,
            'HDMI 3 (AV)': 17
        }

        PIPInputCmdString = 'MWIP{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            10: 'HDMI 1 (PC)',
            13: 'HDMI 2 (PC)',
            18: 'HDMI 3 (PC)',
            3: 'D-Sub 1 (Component)',
            4: 'D-Sub 1 (Video)',
            14: 'DisplayPort',
            2: 'D-Sub 1 (RGB)',
            16: 'D-Sub 2',
            9: 'HDMI 1 (AV)',
            12: 'HDMI 2 (AV)',
            17: 'HDMI 3 (AV)'
        }

        PIPInputCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('PIPInput', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 0,
            'PIP': 1,
            'PbyP 1': 2,
            'PbyP 2': 3
        }

        PIPModeCmdString = 'MWIN{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            1: 'PIP',
            2: 'PbyP 1',
            3: 'PbyP 2'
        }

        PIPModeCmdString = 'MWIN????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('PIPMode', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{0:4}\r'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
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
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0,
        }

        PowerCmdString = 'POWR{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            2: 'Input Signal Waiting'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:4}\r'.format(value)
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
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERR': 'Communcation error or incorrect command',
            'LOC': 'RS232C control is disabled. Please refer to communication sheet on how to enable RS232C.',
            'WAI': 'Execution of the command is taking some time.'
        }
        if response:
            if response[0:3] in DEVICE_ERROR_CODES:
                ErrorString = '{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:3]])
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n').decode()
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n').decode()
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='None', CharDelay=0, Model=None):
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
