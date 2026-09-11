from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import time
from re import search

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

        self.Models = {
            'kapp iQ Pro 55': self.smrt_38_2156_non_75,
            'kapp iQ Pro 65': self.smrt_38_2156_non_75,
            'kapp iQ Pro 75': self.smrt_38_2156_75,
            'kapp iQ 75': self.smrt_38_2156_75,
            'kapp iQ 65': self.smrt_38_2156_non_75,
            'kapp iQ 55': self.smrt_38_2156_non_75,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Input': {'Status': {}},
            'MultiWindowAudioInput': {'Status': {}},
            'MultiWindowInput': {'Parameters': ['Input'], 'Status': {}},
            'MultiWindowMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On': 'set mute=on\r',
            'Off': 'set mute=off\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        ValueStateValues = {
            'on>': 'On',
            'off>': 'Off'
        }

        AudioMuteCmdString = 'get mute\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.replace('\r','').split('=')[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'set picturereset=yes\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetDisplayMode(self, value, qualifier):
        ValueStateValues = {
            'Standard' : 'set displaymode=standard\r',
            'User'     : 'set displaymode=user\r',
            'Dynamic'  : 'set displaymode=dynamic\r'
        }
        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        ValueStateValues = {
            'standard>' : 'Standard',
            'user>' : 'User',
            'dynamic>' : 'Dynamic'
        }

        DisplayModeCmdString = 'get displaymode\r'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.replace('\r','').split('=')[1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateDisplayMode')

    def SetInput(self, value, qualifier):
        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputCmdString = 'get input\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res.replace('\r','').split('=')[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMultiWindowAudioInput(self, value, qualifier):
        ValueStateValues = {
            'Window 1' : 'set mwaudioinput=window1\r',
            'Window 2' : 'set mwaudioinput=window2\r',
            'Window 3' : 'set mwaudioinput=window3\r',
            'Window 4' : 'set mwaudioinput=window4\r'
        }
        MultiWindowAudioInputCmdString = ValueStateValues[value]
        self.__SetHelper('MultiWindowAudioInput', MultiWindowAudioInputCmdString, value, qualifier)

    def UpdateMultiWindowAudioInput(self, value, qualifier):
        ValueStateValues = {
            'window1>' : 'Window 1',
            'window2>' : 'Window 2',
            'window3>' : 'Window 3',
            'window4>' : 'Window 4'
        }

        MultiWindowAudioInputCmdString = 'get mwaudioinput\r'
        res = self.__UpdateHelper('MultiWindowAudioInput', MultiWindowAudioInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.replace('\r','').split('=')[1]]
                self.WriteStatus('MultiWindowAudioInput', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateMultiWindowAudioInput')

    def SetMultiWindowInput(self, value, qualifier):
        ValueStateValues = {
            'HDMI 1'               : 'hdmi1',
            'HDMI 2'               : 'hdmi2',
            'DisplayPort'          : 'displayport',
            'OPS/HDMI'             : 'opshdmi',
            'OPS/HDMI/DisplayPort' : 'opshdmidisplayport'
        }
        if 1 <= int(qualifier['Input']) <= 4:
            MultiWindowInputCmdString = 'set mwwindow{0}input={1}\r'.format(qualifier['Input'],ValueStateValues[value])
            self.__SetHelper('MultiWindowInput', MultiWindowInputCmdString, value, qualifier, 3)

    def UpdateMultiWindowInput(self, value, qualifier):
        ValueStateValues = {
            'hdmi1>'              : 'HDMI 1',
            'hdmi2>'              : 'HDMI 2',
            'displayport>'        : 'DisplayPort',
            'opshdmi>'            : 'OPS/HDMI',
            'opshdmidisplayport>' : 'OPS/HDMI/DisplayPort'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            MultiWindowInputCmdString = 'get mwwindow{0}input\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('MultiWindowInput', MultiWindowInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.replace('\r','').split('=')[1]]
                    self.WriteStatus('MultiWindowInput', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    print('Invalid/unexpected response for UpdateMultiWindowInput')

    def SetMultiWindowMode(self, value, qualifier):
        ValueStateValues = {
            'Off'  : 'set mw=off\r',
            'Dual' : 'set mw=dual\r',
            'Quad' : 'set mw=quad\r'
        }
        MultiWindowModeCmdString = ValueStateValues[value]
        self.__SetHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)

    def UpdateMultiWindowMode(self, value, qualifier):
        ValueStateValues = {
            'off>'  : 'Off',
            'dual>' : 'Dual',
            'quad>' : 'Quad'
        }

        MultiWindowModeCmdString = 'get mw\r'
        res = self.__UpdateHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.replace('\r','').split('=')[1]]
                self.WriteStatus('MultiWindowMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateMultiWindowMode')

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On'      : 'set powerstate=on\r',
            'Off'     : 'set powerstate=off\r',
            'Standby' : 'set powerstate=standby\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            'on>' : 'On',
            'off>' : 'Off',
            'standby>' : 'Standby'
        }

        PowerCmdString = 'get powerstate\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.replace('\r','').split('=')[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'set volume={0}\r'.format(value)
            VolumeCmdString = 'set volume={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'get volume\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res.replace('\r','').split('=')[1][:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if b'invalid cmd' in response:
            print('invalid command:{0}'.format(response.split('=')[1]))
            response = ''
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
            if not res:
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

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
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

    def smrt_38_2156_75(self):
        self.InputStateValues = {
            'HDMI 1'          : 'set input=HDMI1\r',
            'HDMI 2'          : 'set input=hdmi2\r',
            'DisplayPort'     : 'set input=displayport\r',
            'OPS/HDMI'        : 'set input=ops/hdmi\r',
            'OPS/DisplayPort' : 'set input=ops/displayport\r'
        }
        self.InputStateNames = {
            'hdmi1>'           : 'HDMI 1',
            'HDMI1>'           : 'HDMI 1',
            'hdmi2>'           : 'HDMI 2',
            'displayport>'     : 'DisplayPort',
            'ops/hdmi>'        : 'OPS/HDMI',
            'ops/displayport>' : 'OPS/DisplayPort',
        }

    def smrt_38_2156_non_75(self):
        self.InputStateValues = {
            'HDMI 1'     : 'set input=HDMI1\r',            
            'OPS/HDMI 2' : 'set input=ops/hdmi2\r'
        }
        self.InputStateNames = {
            'hdmi1>'     : 'HDMI 1',
            'HDMI1>'     : 'HDMI 1',
            'ops/hdmi2>' : 'OPS/HDMI 2',
        }

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
