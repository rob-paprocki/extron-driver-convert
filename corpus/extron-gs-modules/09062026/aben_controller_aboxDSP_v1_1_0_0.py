from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionFlag = True
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'

        self.Commands = {
            'CodecControl': {'Status': {}},
            'ConnectedDevice': {'Parameters': ['Input'], 'Status': {}},
            'InternalMatrix': {'Parameters': ['Input'], 'Status': {}},
            'Input': {'Parameters':['Screen'], 'Status': {}},
            'Screen': {'Parameters': ['Screen'], 'Status': {}},
            'SystemInput': {'Status': {}},
            'SystemOff': {'Status': {}},
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Box(\d{2})\.Screen(1|2): ?(NoSignal|SignalHDMI|SignalDVI|SwitchHDMI|SwitchDVI|SwitchToVGA)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Box(\d{2})\.(HDMI|VGA)Sync (On|Off)'), self.__MatchConnectedDevice, None)
            self.AddMatchString(re.compile(b'Box(\d{2})\.Screen(1|2): ?(On|Off)'), self.__MatchScreen, None)
            self.AddMatchString(re.compile(b'Box(\d{2})\.Error: Command not found'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):        
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)
        else:
            print('Invalid DeviceID (must be between 1 and 99 or Broadcast).')

    def SetCodecControl(self, value, qualifier):

        ValueStateValues = {
            'Sleep': '1',
            'Wake': '0'
        }

        CodecControlCmdString = 'Box{0:02d}.COD000{1}\x0d\x0a'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('CodecControl', CodecControlCmdString, value, qualifier)

    def __MatchConnectedDevice(self, match, tag):

        ValueStateValues = {
            'On': 'Connected',
            'Off': 'Disconnected',
        }
        if int(match.group(1).decode()) == self._DeviceID:
            self.WriteStatus('ConnectedDevice', ValueStateValues[match.group(3).decode()], {'Input': match.group(2).decode()})

    def __MatchError(self, match, tag):
        if int(match.group(1).decode()) == self._DeviceID:
            print('Error from device: command not found')

    def SetInternalMatrix(self, value, qualifier):

        InputStates = {
            'Aux 1': {
                'VC Out': '3',
                'Screen Out': '4'
            },
            'Aux 2': {
                'VC Out': '5',
                'Screen Out': '6'
            }
        }

        InternalMatrixCmdString = 'Box{0:02d}.INNA{1}00\x0d\x0a'.format(self._DeviceID, InputStates[qualifier['Input']][value])
        self.__SetHelper('InternalMatrix', InternalMatrixCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1' : {
                'DVI' : 'V0', 
                'HDMI' : 'H0', 
                'VGA' : 'G0'
            },
            '2' : {
                'DVI' : '2V', 
                'HDMI' : '2H', 
                'VGA' : '2G'
            }
        }

        InputCmdString = 'Box{0:02d}.SCR{1}00\x0d\x0a'.format(self.DeviceID,ValueStateValues[qualifier['Screen']][value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'NoSignal': 'No Signal',
            'SignalHDMI': 'HDMI',
            'SwitchHDMI': 'HDMI',
            'SignalDVI': 'DVI',
            'SwitchDVI': 'DVI',
            'SwitchToVGA': 'VGA'
        }
        if int(match.group(1).decode()) == self._DeviceID:
            self.WriteStatus('Input', ValueStateValues[match.group(3).decode()], {'Screen' : match.group(2).decode()})

    def SetScreen(self, value, qualifier):

        ScreenStates = {
            '1': {
                'On': '10',
                'Off': '00'
            },
            '2': {
                'On': '20',
                'Off': '21'
            }
        }

        ScreenCmdString = 'Box{0:02d}.SCR{1}00\x0d\x0a'.format(self._DeviceID, ScreenStates[qualifier['Screen']][value])
        self.__SetHelper('Screen', ScreenCmdString, value, qualifier)

    def __MatchScreen(self, match, tag):
        if int(match.group(1).decode()) == self._DeviceID:
            self.WriteStatus('Screen', match.group(3).decode(), {'Screen': match.group(2).decode()})

    def SetSystemInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI Laptop': 'L1',
            'VGA Laptop': 'L2',
            'Aux 1': 'A1',
            'Aux 2': 'A2'
        }

        SystemInputCmdString = 'Box{0:02d}.INN{1}00\x0d\x0a'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('SystemInput', SystemInputCmdString, value, qualifier)

    def SetSystemOff(self, value, qualifier):

        SystemOffCmdString = 'Box{0:02d}.OFF\x0d\x0a'.format(self._DeviceID)
        self.__SetHelper('SystemOff', SystemOffCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)    

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
        # Send Update Commands
   
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
