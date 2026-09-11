from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ATOutputGain': {'Parameters':['Output'], 'Status': {}},
            'ATOutputMute': {'Parameters':['Output'], 'Status': {}},
            'DigitalInputStatus': {'Parameters':['Digital I/O Port'], 'Status': {}},
            'DigitalOutputMode': {'Parameters':['Digital I/O Port', 'Channel'], 'Status': {}},
            'InputGainAnalog': {'Parameters':['Input'], 'Status': {}},
            'InputGainDigital': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PhantomPower': {'Parameters':['Input'], 'Status': {}}
        }

        self.InputStates = {
                '1' : '40000', 
                '2' : '40001', 
                '3' : '40002', 
                '4' : '40003', 
                '5' : '40004'
            }
        
        self.OutputStates = {
                '1' : '40100', 
                '2' : '40101', 
                '3' : '40102', 
                '4' : '40103', 
                '5' : '40104'
            }
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DsG(40[01]0[0-4])\*(-?[0-9]{1,4})\r\n'), self.__MatchInputGainAnalog, None)
            self.AddMatchString(re.compile(b'DsH(4000[0-4])\*(-?[0-9]{1,3})\r\n'), self.__MatchInputGainDigital, None)
            self.AddMatchString(re.compile(b'Gpi([1-5])\*(0|1)\r\n'), self.__MatchDigitalInputStatus, None)
            self.AddMatchString(re.compile(b'Gpot([1-5])\*(1|2)\*([0-3])\r\n'), self.__MatchDigitalOutputMode, None)
            self.AddMatchString(re.compile(b'DsM(40[01]0[0-4])\*(0|1)\r\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'(60-\d{3,4}-\w{2,})\r?\n'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'DsZ(4000[0-4])\*(0|1)\r\n'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'(E[12][0-8])\n\x00'), self.__MatchError, None)

    def SetATOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ATOutputGainCmdString = '\x1Bg{0}*{1:.0f}AU\r'.format(self.OutputStates[qualifier['Output']], value*10 )
            self.__SetHelper('ATOutputGain', ATOutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATOutputGain')

    def UpdateATOutputGain(self, value, qualifier):

        ATOutputGainCmdString = '\x1Bg{0}AU\r'.format(self.OutputStates[qualifier['Output']])
        self.__UpdateHelper('ATOutputGain', ATOutputGainCmdString, value, qualifier)

    def SetATOutputMute(self, value, qualifier):


        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            ATOutputMuteCmdString = '\x1Bm{0}*{1}AU\r'.format(self.OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('ATOutputMute', ATOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATOutputMute')

    def UpdateATOutputMute(self, value, qualifier):

        ATOutputMuteCmdString = '\x1Bm{0}AU\r'.format(self.OutputStates[qualifier['Output']])
        self.__UpdateHelper('ATOutputMute', ATOutputMuteCmdString, value, qualifier)
 
    def UpdateDigitalInputStatus(self, value, qualifier):

        DigitalIOPortStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4',
            '5' : '5'
        }
        
        DigitalInputStatusCmdString = '\x1B{0}GPI\r'.format(DigitalIOPortStates[qualifier['Digital I/O Port']])
        self.__UpdateHelper('DigitalInputStatus', DigitalInputStatusCmdString, value, qualifier)

    def __MatchDigitalInputStatus(self, match, tag):

        DigitalIOPortStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4',
            '5' : '5'
        }

        ValueStateValues = {
            '0' : 'Low', 
            '1' : 'High'
        }

        qualifier = {}
        qualifier['Digital I/O Port'] = DigitalIOPortStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DigitalInputStatus', value, qualifier)
        
    def SetDigitalOutputMode(self, value, qualifier):

        DigitalIOPortStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5'
        }
        
        ChannelStates = {
            '1' : '1',
            '2' : '2'
        }

        ValueStateValues = {
            'Low'                   : '1', 
            'High'                  : '0', 
            'Follow Mute'           : '2', 
            'Follow Mute, Inverted' : '3'
        }

        if value in ValueStateValues:
            DigitalOutputModeCmdString = '\x1B{0}*{1}*{2}GPOT\r'.format(DigitalIOPortStates[qualifier['Digital I/O Port']], ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('DigitalOutputMode', DigitalOutputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalOutputMode')

    def UpdateDigitalOutputMode(self, value, qualifier):

        DigitalIOPortStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5'
        }
        
        ChannelStates = {
            '1' : '1',
            '2' : '2'
        }
        
        DigitalOutputModeCmdString = '\x1B{0}*{1}GPOT\r'.format(DigitalIOPortStates[qualifier['Digital I/O Port']], ChannelStates[qualifier['Channel']])
        self.__UpdateHelper('DigitalOutputMode', DigitalOutputModeCmdString, value, qualifier)

    def __MatchDigitalOutputMode(self, match, tag):

        DigitalIOPortStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5'
        }
        
        ChannelStates = {
            '1' : '1',
            '2' : '2'
        }

        ValueStateValues = {
            '1' : 'Low', 
            '0' : 'High', 
            '2' : 'Follow Mute', 
            '3' : 'Follow Mute, Inverted'
        }

        qualifier = {}
        qualifier['Digital I/O Port'] = DigitalIOPortStates[match.group(1).decode()]
        qualifier['Channel'] = ChannelStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('DigitalOutputMode', value, qualifier)
        
    def SetInputGainAnalog(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 80
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainAnalogCmdString = '\x1Bg{0}*{1:.0f}AU\r'.format(self.InputStates[qualifier['Input']], value*10 )
            self.__SetHelper('InputGainAnalog', InputGainAnalogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGainAnalog')

    def UpdateInputGainAnalog(self, value, qualifier):

        InputGainAnalogCmdString = '\x1Bg{0}AU\r'.format(self.InputStates[qualifier['Input']])
        self.__UpdateHelper('InputGainAnalog', InputGainAnalogCmdString, value, qualifier)

    def __MatchInputGainAnalog(self, match, tag):
                
        port = int(match.group(1).decode())
        value = int(match.group(2).decode()) / 10
        
        if 40000 <= port <= 40004:
            self.WriteStatus('InputGainAnalog', value, {'Input' : str(port - 39999)})
        elif 40100 <= port <= 40104:
            self.WriteStatus('ATOutputGain', value, {'Output' : str(port - 40099)})
        
    def SetInputGainDigital(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainDigitalCmdString = '\x1Bh{0}*{1:.0f}AU\r'.format(self.InputStates[qualifier['Input']], value*10 )
            self.__SetHelper('InputGainDigital', InputGainDigitalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGainDigital')

    def UpdateInputGainDigital(self, value, qualifier):

        InputGainDigitalCmdString = '\x1Bh{0}AU\r'.format(self.InputStates[qualifier['Input']])
        self.__UpdateHelper('InputGainDigital', InputGainDigitalCmdString, value, qualifier)

    def __MatchInputGainDigital(self, match, tag):
                
        port = int(match.group(1).decode())
        value = int(match.group(2).decode()) / 10
        
        if 40000 <= port <= 40004:
            self.WriteStatus('InputGainDigital', value, {'Input' : str(port - 39999)})
        
    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            InputMuteCmdString = '\x1Bm{0}*{1}AU\r'.format(self.InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputMuteCmdString = '\x1Bm{0}AU\r'.format(self.InputStates[qualifier['Input']])
        self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
 
    def __MatchMute(self, match, tag):
         
        MuteStates = {
            '1' : 'On',
            '0' : 'Off'
        }
         
        port = int(match.group(1).decode())
        value = MuteStates[match.group(2).decode()]
         
        if 40000 <= port <= 40004:
            self.WriteStatus('InputMute', value, {'Input' : str(port - 39999)})
        elif 40100 <= port <= 40104:
            self.WriteStatus('ATOutputMute', value, {'Output' : str(port - 40099)})

    def UpdatePartNumber(self, value, qualifier):

        PartNumberCmdString = '\x1Bcpn\r'
        self.__UpdateHelper('PartNumber', PartNumberCmdString, value, qualifier)
        
    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def SetPhantomPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            PhantomPowerCmdString = '\x1BZ{0}*{1}AU\r'.format(self.InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhantomPower')

    def UpdatePhantomPower(self, value, qualifier):

        PhantomPowerCmdString = '\x1BZ{0}AU\r'.format(self.InputStates[qualifier['Input']])
        self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)

    def __MatchPhantomPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        port = int(match.group(1).decode())
        value = ValueStateValues[match.group(2).decode()]
        if 40000 <= port <= 40004:
            self.WriteStatus('PhantomPower', value, {'Input' : str(port - 39999)})

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
            
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            self.Send(commandstring)
    
    def __MatchError(self, match, tag):

        self.counter = 0

        ErrorCodes = {
                      'E10' : 'Invalid command',
                      'E11' : 'Invalid preset',
                      'E12' : 'Invalid port number',
                      'E13' : 'Invalid parameter (number is out of range)',
                      'E14' : 'Not valid for this configuration',
                      'E17' : 'System timed out',
                      'E22' : 'Busy',
                      'E24' : 'Privilege violation',
                      'E25' : 'Device is not present',
                      'E26' : 'Maximum number of connections exceeded',
                      'E27' : 'Invalid event number',
                      'E28' : 'Bad filename or file not found'
        }
        
        self.Error([ErrorCodes.get(match.group(1).decode(), 'Error')])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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