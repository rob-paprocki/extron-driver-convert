from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 3.0
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelStep': {'Status': {}},
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

        if self.Unidirectional == 'False' or self.ConnectionType != 'Serial':
            self.AddMatchString(re.compile(b'Username:'), self.__MatchLoginAdmin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchLoginPass, None)

    def __MatchLoginAdmin(self, match, tag):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchLoginPass(self, match, tag):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')
       
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
            'Original': 'WIDE11  \r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectStateValues = {
            '1' : 'Side Bar',
            '2' : 'S.Stretch',
            '3' : 'Zoom [AV]',
            '4' : 'Stretch [AV]',
            '5' : 'Normal [PC]',
            '6' : 'Zoom [PC]',
            '7' : 'Stretch [PC]',
            '8' : 'Dot by Dot [PC]',
            '9' : 'Full Screen [AV]',
            '10' : 'Auto',
            '11' : 'Original'
        }
        cmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', cmdString, value, qualifier)
        if res:
            value = AspectStateValues[str(int(res))]
            self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE1   \r',
            'Off': 'MUTE2   \r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            '1' : 'On', 
            '2' : 'Off'
        }
        cmdString = 'MUTE????\r'
        res = self.__UpdateHelper('AudioMute', cmdString, value, qualifier)
        if res:
            value = AudioMuteStateValues[str(int(res))]
            self.WriteStatus('AudioMute', value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP1   \r',
            'Down': 'CHDW0   \r'
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetChannelTVCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 1 <= int(tempValue) <= 135:
                ChannelTVCommandCmdString = 'DCCH{0:03d} \r'.format(int(tempValue))
                self.__SetHelper('ChannelTVCommand', ChannelTVCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetChannelTVCommand')
        else:
            print('Invalid Command for SetChannelTVCommand')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP1   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDigitalAirCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 100 <= int(tempValue) <= 9999:
                DigitalAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalAirCommand', DigitalAirCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalAirCommand')
        else:
            print('Invalid Command for SetDigitalAirCommand')

    def SetDigitalCableCommand1(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 9999:
                DigitalCableCommand1CmdString = 'DC10{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalCableCommand1', DigitalCableCommand1CmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableCommand1')
        else:
            print('Invalid Command for SetDigitalCableCommand1')

    def SetDigitalCableCommand2(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 6383:
                DigitalCableCommand2CmdString = 'DC11{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalCableCommand2', DigitalCableCommand2CmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableCommand2')
        else:
            print('Invalid Command for SetDigitalCableCommand2')

    def SetDigitalCableMajorCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 1 <= int(tempValue) <= 999:
                DigitalCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(tempValue))
                self.__SetHelper('DigitalCableMajorCommand', DigitalCableMajorCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDigitalCableMajorCommand')
        else:
            print('Invalid Command for SetDigitalCableMajorCommand')

    def SetDigitalCableMinorCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 999:
                DigitalCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(tempValue))
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
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateValues = {
            '1' : 'HDMI 1', 
            '2' : 'HDMI 2', 
            '3' : 'HDMI 3', 
            '4' : 'HDMI 4', 
            '5' : 'Component', 
            '6' : 'Video 1', 
            '7' : 'Video 2', 
            '8' : 'PC', 
        }
        cmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', cmdString, value, qualifier)
        if res:
            value = InputStateValues[str(int(res))]
            self.WriteStatus('Input', value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'RCKY41  \r',
            'Down': 'RCKY42  \r',
            'Left': 'RCKY43  \r',
            'Right': 'RCKY44  \r',
            'Enter': 'RCKY40  \r',
            'Exit': 'RCKY46  \r',
            'Menu': 'RCKY38  \r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'On_Serial': '1',
            'On_LAN': '2'
        }

        if value == 'On':
            PowerCmdString = 'POWR{0}   \r'.format(ValueStateValues['On'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            if 'Serial' in self.ConnectionType:
                CmdString = 'RSPW{0:4}\r'.format(ValueStateValues['On_Serial'])
            else:
                CmdString = 'RSPW{0:4}\r'.format(ValueStateValues['On_LAN'])
            PowerCmdString = 'POWR0   \r'
            self.__SetHelper('Power', CmdString, value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        cmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', cmdString, value, qualifier)
        if res:
            value = PowerStateValues[str(int(res))]
            self.WriteStatus('Power', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:02d}  \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        cmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', cmdString, value, qualifier)
        if res:
            value = int(res)
            self.WriteStatus('Volume', value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERR\x0D': 'Communication error or incorrect command',
            }
        if response:
            if response[0:5] in DEVICE_ERROR_CODES:
                ErrorString = sourceCmdName + ': ' + DEVICE_ERROR_CODES[response[0:5]]
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, CmdDefaultResponseTimeout=0.3):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, CmdDefaultResponseTimeout, deliTag=b'\r').decode()
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
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
                result = re.search(regexString, self._ReceiveBuffer)
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