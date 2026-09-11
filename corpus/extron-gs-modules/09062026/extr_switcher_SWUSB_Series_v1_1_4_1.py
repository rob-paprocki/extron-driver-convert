from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
        
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
        self.Models = {
            'SW2 USB': self.extr_2_62_sw2,
            'SW4 USB': self.extr_2_62_sw4,
            'SW4 USB Plus': self.extr_2_62_sw4,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'OutputSignalStatus': {'Parameters': ['Output'], 'Status': {}},
            'PassThrough': {'Status': {}},
            'USBInput': {'Status': {}},
        }

        self.Regex = {
            'ExecutiveMode': re.compile(b'([01])\r\n|(E01|E10|E13)\r\n'),
            'Input': re.compile(b'Chn([0-4]) InACT([01]+) OutACT([01]+) ?(?:Emul([01]+))?\r\n|(E01|E10|E13)\r\n'),
            'PassThrough': re.compile(b'Loop([01])\r\n|(E01|E10|E13)\r\n')
        }     

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On': '1X',
            'Off': '0X'
        }

        if value in ExecutiveModeStateValues:
            ExecutiveModeCmdString = ExecutiveModeStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeStateNames = {
            '1': 'On',
            '0': 'Off'
        }  

        ExecutiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeStateNames[res[0:1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ExecutiveMode: Invalid/unexpected response'])   

    def SetInput(self, value, qualifier):

        if value in self.InputStateValues:
            InputCmdString = self.InputStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        SignalStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        InputCmdString = 'I'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                inputValue = self.InputStateNames[res[0:4]]
                resIn = res.split(' ')[1]
                resOut = res.split(' ')[2]
                for i in range(0, 4):
                    if i < self.InputSize:
                        inputSignalvalue = SignalStateValues[resIn[i + 5]]
                        self.WriteStatus('InputSignalStatus', inputSignalvalue, {'Input': str(i + 1)})
                    outputSignalvalue = SignalStateValues[resOut[i + 6]]
                    self.WriteStatus('OutputSignalStatus', outputSignalvalue, {'Output': str(i + 1)})
                self.WriteStatus('USBInput', inputValue, None)
                self.WriteStatus('Input', inputValue, None)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])
        
    def UpdateInputSignalStatus(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def UpdateOutputSignalStatus(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetPassThrough(self, value, qualifier):

        PassThroughStateValues = {
            'Off': '\x1B1LOOP\x0D',
            'On': '\x1B0LOOP\x0D'
        }

        if value in PassThroughStateValues:
            PassThroughCmdString = PassThroughStateValues[value]
            self.__SetHelper('PassThrough', PassThroughCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPassThrough')

    def UpdatePassThrough(self, value, qualifier):

        PassThroughStateNames = {
            '1': 'Off',
            '0': 'On'
        }

        PassThroughCmdString = '\x1BLOOP\x0D'
        res = self.__UpdateHelper('PassThrough', PassThroughCmdString, value, qualifier)
        if res:
            try:
                value = PassThroughStateNames[res[4:5]]
                self.WriteStatus('PassThrough', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PassThrough: Invalid/unexpected response'])

    def SetUSBInput(self, value, qualifier):

        if value in self.USBInputStateValues:
            USBInputCmdString = self.USBInputStateValues[value]
            self.__SetHelper('USBInput', USBInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBInput')

    def UpdateUSBInput(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'E01': 'Invalid input channel number',
                              b'E10': 'Invalid Command',
                              b'E13': 'Invalid value(out of range)'}
        if response:
            if response[0:3] == b'E01' or response[0:3] == b'E10' or response[0:3] == b'E13':
                ErrorString = sourceCmdName + DEVICE_ERROR_CODES[response[0:3]]
                self.Error([ErrorString])
                response = ''
            elif response[0] == '\n':
                response = response.lstrip('\n')
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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

        self.lastInputUpdate = 0
        
    def extr_2_62_sw2(self):

        self.InputSize = 2
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '0' : '0!'    
        } 

        self.USBInputStateValues = {
            '1' : '1^',
            '2' : '2^',
            '0' : '0^'
        }  
        
        self.InputStateNames = {
            'Chn1' : '1',
            'Chn2' : '2',
            'Chn0' : '0'                           
        }
        
    def extr_2_62_sw4(self):

        self.InputSize = 4
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '3' : '3!',
            '4' : '4!',
            '0' : '0!'      
        } 

        self.USBInputStateValues = {
            '1' : '1^',
            '2' : '2^',
            '3' : '3^',
            '4' : '4^',
            '0' : '0^'
        }  

        self.InputStateNames = {
            'Chn1' : '1',
            'Chn2' : '2',
            'Chn3' : '3',
            'Chn4' : '4',
            'Chn0' : '0'                         
        }

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

