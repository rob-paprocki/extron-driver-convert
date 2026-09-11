from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.Models = {
            'SW2 HDMI': self.extr_2_70_sw2,
            'SW4 HDMI': self.extr_2_70_sw4,
            'SW6 HDMI': self.extr_2_70_sw6,
            'SW8 HDMI': self.extr_2_70_sw8,
            'SW2 HDMI w/Contact Closure': self.extr_2_70_sw2,
            'SW4 HDMI w/Contact Closure': self.extr_2_70_sw4,
            'SW6 HDMI w/Contact Closure': self.extr_2_70_sw6,
            'SW8 HDMI w/Contact Closure': self.extr_2_70_sw8,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'Input': { 'Status': {}},
            'IRSensor': { 'Status': {}},
            'InputSignalStatus': { 'Parameters':['Input'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            } 

        self.SignalStatusRegex = re.compile(b'Sig([ 01]+)\*[01]\r\n')
        self.HDCPStatusRegex = re.compile(b'HdcpE([ 01]+)\r\n')

    def SetAudioMute(self, value, qualifier):
        AudioMuteStateValues = {
            'On' : '1Z',
            'Off': '0Z',
            }
        AudioMuteCmdString = AudioMuteStateValues[value] 
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    
    def UpdateAudioMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            'On': '1X', 
            'Off' : '0X'
            }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value] 
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)  

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeStateNames = {
            b'1' : 'On',
            b'0' : 'Off',                            
            }
             
        ExecutiveModeCmdString = b'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)   
        if res:
            try:
                value = ExecutiveModeStateNames[res[0:1]]  
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetHDCPInputAuthorization(self, value, qualifier):
        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        input = int(qualifier['Input'])
        if 1 <= int(input) <= self.InputSize:
            HDCPInputAuthorizationCmdString = '\x1BE{0}*{1}HDCP\r'.format(input, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):
        ValueStateValues = {
           b'1' : 'On', 
           b'0' : 'Off'
        }

        HDCPInputAuthorizationCmdString = b'\x1BEHDCP\r'
        res = self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        if res:
            try:
                valueList = re.search(self.HDCPStatusRegex, res)
                index = 1
                for value in valueList.group(1).split():
                    self.WriteStatus('HDCPInputAuthorization', ValueStateValues[value], {'Input' : str(index)})
                    index += 1
            except (KeyError, IndexError, AttributeError):
                    self.Error(['HDCP Input Authorization: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):
        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
     
    def UpdateInput(self, value, qualifier):
        MuteStateNames = {
            b'0' : 'Off',
            b'1' : 'On',
            }

        InputCmdString = b'I'  
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)   
        if res:
            try:
                value = self.InputStateNames[res[0:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            try:
                value = MuteStateNames[res[14:15]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

            try:
                value = MuteStateNames[res[9:10]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])
                            
    def SetIRSensor(self, value, qualifier):
        IRSensorStateValues = {
            'Off' : '0*65#',
            'On': '1*65#',
            }

        IRSensorCmdString = IRSensorStateValues[value] 
        self.__SetHelper('IRSensor', IRSensorCmdString, value, qualifier)  

    def UpdateIRSensor(self, value, qualifier):
        IRSensorStateNames = {
            b'0' : 'Off',
            b'1' : 'On',                   
            }
             
        IRSensorCmdString = b'65#'
        res = self.__UpdateHelper('IRSensor', IRSensorCmdString, value, qualifier)    
        if res:
            try:
                value = IRSensorStateNames[res[0:1]]  
                self.WriteStatus('IRSensor', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Sensor: Invalid/unexpected response'])
        
    def UpdateInputSignalStatus(self, value, qualifier):  
        SignalStatusStateNames = {
            b'0' : 'Not Active',
            b'1' : 'Active',
            }
        
        SignalStatusCmdString = b'\x1BLS\x0D'
        res = self.__UpdateHelper('InputSignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                valueList = re.search(self.SignalStatusRegex, res)
                index = 1
                for value in valueList.group(1).split():
                    self.WriteStatus('InputSignalStatus', SignalStatusStateNames[value], {'Input' : str(index)})
                    index += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input Signal Status: Invalid/unexpected response'])        

    def SetVideoMute(self, value, qualifier):
        VideoMuteStateValues = {
            'On' : '1B',
            'Off': '0B',
            }
        VideoMuteCmdString = VideoMuteStateValues[value] 
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    
    def UpdateVideoMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):        
        DEVICE_ERROR_CODES = {
            b'E01': 'Invalid input channel number (out of range)',
            b'E06': 'Invalid input selection during auto-input switching',   
            b'E10': 'Invalid Command',
            b'E13': 'Invalid value(out of range)'
            }   

        if response[0:3] in DEVICE_ERROR_CODES:
            ErrorString = '{0} error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:3]])
            self.Error([ErrorString])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
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
        
    def extr_2_70_sw2(self):
        self.InputSize = 2
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '0' : '0!'
            }

        self.InputStateNames = {
            b'V1' : '1',
            b'V2' : '2',
            b'V0' : '0'
            }

    def extr_2_70_sw4(self):
        self.InputSize = 4
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '3' : '3!',
            '4' : '4!',
            '0' : '0!'
            }

        self.InputStateNames = {
            b'V1' : '1',
            b'V2' : '2',
            b'V3' : '3',
            b'V4' : '4',
            b'V0' : '0'
            }

    def extr_2_70_sw6(self):
        self.InputSize = 6
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '3' : '3!',
            '4' : '4!',
            '5' : '5!',
            '6' : '6!',
            '0' : '0!'
            }

        self.InputStateNames = {
            b'V1' : '1',
            b'V2' : '2',
            b'V3' : '3',
            b'V4' : '4',
            b'V5' : '5',
            b'V6' : '6',
            b'V0' : '0'
            }

    def extr_2_70_sw8(self):
        self.InputSize = 8
        self.InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '3' : '3!',
            '4' : '4!',
            '5' : '5!',
            '6' : '6!',
            '7' : '7!',
            '8' : '8!',
            '0' : '0!'
            }

        self.InputStateNames = {
            b'V1' : '1',
            b'V2' : '2',
            b'V3' : '3',
            b'V4' : '4',
            b'V5' : '5',
            b'V6' : '6',
            b'V7' : '7',
            b'V8' : '8',
            b'V0' : '0'
            }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

