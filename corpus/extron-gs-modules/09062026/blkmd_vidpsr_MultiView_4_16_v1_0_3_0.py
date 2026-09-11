from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {
            'MultiView 16': self.blkmd_29_1708_16,
            'MultiView 4': self.blkmd_29_1708_4,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'EmbeddedAudioOutput': {'Parameters':['Input'], 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'Layout': { 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            'SoloLayout': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            if 'Serial' in self.ConnectionType:
                self.AddMatchString(re.compile(b'(S|V):0(?P<output>[0-9A-F]{1,3}),(?P<input>[0-9A-F]{1,3})\r\n'), self.__MatchOutputTieStatus, 'Serial') # Also handles Input Tie Status
                self.AddMatchString(re.compile(b'>'), self.__MatchHeartbeat, None)
            else:
                self.AddMatchString(re.compile(b'ACK\r\n'), self.__MatchHeartbeat, None)
                self.AddMatchString(re.compile(b'NACK\r\n'), self.__MatchError, None)
                self.AddMatchString(re.compile(b'CONFIGURATION:\r\nLayout: (solo|2x2|3x3|4x4)\r\n\r\n'), self.__MatchLayout, None)
                self.AddMatchString(re.compile(b'VIDEO OUTPUT ROUTING:\r\n(?P<routes>[ \d\r\n]+)\r\n\r\n'), self.__MatchOutputTieStatus, 'Tcp')
                self.AddMatchString(re.compile(b'CONFIGURATION:\r\nSolo enabled: (true|false)\r\n\r\n'), self.__MatchSoloLayout, None)
            

    def SetEmbeddedAudioOutput(self, value, qualifier):

        input = int(qualifier['Input'])
        if 1<=input<=self.IOSize:
            if self.IOSize == 4:
                EmbeddedAudioOutputCmdString = 'VIDEO OUTPUT ROUTING:\r\n5 {0}\r\n\r\n'.format(input-1)
            else:
                EmbeddedAudioOutputCmdString = 'VIDEO OUTPUT ROUTING:\r\n17 {0}\r\n\r\n'.format(input-1)
            self.__SetHelper('EmbeddedAudioOutput', EmbeddedAudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEmbeddedAudioOutput')
            
    def UpdateHeartbeat(self, value, qualifier):

        if 'Serial' in self.ConnectionType:
            HeartbeatCmdString = '\r'
        else:
            HeartbeatCmdString = 'PING:\r\n\r\n'
            
        self.__UpdateHelper('Heartbeat', HeartbeatCmdString, value, qualifier)

    def __MatchHeartbeat(self, match, tag):
    
        self.WriteStatus('ConnectionStatus', 'Connected')

    def UpdateInputTieStatus(self, value, qualifier):

        input = qualifier['Input']
        output = qualifier['Output']
        if 1<=int(input)<=self.IOSize and 1<=int(output)<=self.IOSize :
            self.UpdateOutputTieStatus(value, {'Output' : output})
        else:
            self.Discard('Device Is Busy for UpdateInputTieStatus')

    def SetLayout(self, value, qualifier):

        ValueStateValues = {
            'Solo' : 'solo', 
            '2x2'  : '2x2', 
            '3x3'  : '3x3', 
            '4x4'  : '4x4'
         }

        LayoutCmdString = 'CONFIGURATION:\r\nLayout: {0}\r\n\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Layout', LayoutCmdString, value, qualifier)

    def __MatchLayout(self, match, tag):

        ValueStateValues = {
            'solo' : 'Solo', 
            '2x2'  : '2x2', 
            '3x3'  : '3x3', 
            '4x4'  : '4x4'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Layout', value, None)

    def SetMatrixTieCommand(self, value, qualifier):
    
        input = int(qualifier['Input'])
        output = qualifier['Output']
        if 'Serial' in self.ConnectionType:
            if 1<=input<=self.IOSize and 1<=int(output)<=self.IOSize:
                MatrixTieCommandCmdString = '@ X:0/{0:01X},{1:01X}\r'.format(int(output)-1,input-1)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            if 1<=input<=self.IOSize and output in self.MatrixTieOutput:
                MatrixTieCommandCmdString = 'VIDEO OUTPUT ROUTING:\r\n{0} {1}\r\n\r\n'.format(self.MatrixTieOutput[output],input-1)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        
    def UpdateOutputTieStatus(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.IOSize:
            if 'Serial' in self.ConnectionType:
                OutputTieStatusCmdString = '@ X?0{0:01X}\r'.format(int(output)-1)
                self.__UpdateHelper('OutputTieStatus', OutputTieStatusCmdString, value, qualifier)

            else:
                OutputTieStatusCmdString = 'VIDEO OUTPUT ROUTING:\r\n\r\n'
                self.__UpdateHelper('OutputTieStatus', OutputTieStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateOutputTieStatus')

    def __MatchOutputTieStatus(self, match, tag):

        if tag == 'Serial':
            input = match.group('input').decode()
            output = match.group('output').decode()
            input = str(int(input, 16) + 1)
            output = str(int(output, 16) + 1)
            
            self.TieStatusHandler(input, output)
            
        elif tag == 'Tcp':            
            routeIter = re.finditer('(?P<output>\d{1,2}) (?P<input>\d{1,2})', match.group('routes').decode())
            for route in routeIter:                
                input = str(int(route.group('input')) + 1)
                output = str(int(route.group('output')) + 1)                
                self.TieStatusHandler(input, output)
                    
    def TieStatusHandler(self, input, output):        
        
        if 1 <= int(input) <= self.IOSize and 1 <= int(output) <= self.IOSize:
                prevInput = self.OutputStatus[output]
                if input != prevInput:
                    self.WriteStatus('InputTieStatus', 'Tied', {'Input': input, 'Output':output})
                    self.WriteStatus('OutputTieStatus', input, {'Output': output})
                    self.OutputStatus[output] = input
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': prevInput, 'Output':output})

    def SetSoloLayout(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'true', 
            'Disable' : 'false'
        }

        SoloLayoutCmdString = 'CONFIGURATION:\r\nSolo enabled: {0}\r\n\r\n'.format(ValueStateValues[value])
        self.__SetHelper('SoloLayout', SoloLayoutCmdString, value, qualifier)

    def __MatchSoloLayout(self, match, tag):

        ValueStateValues = {
            'true'  : 'Enable', 
            'false' : 'Disable'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoloLayout', value, None)

    def SetEnableStatusReporting(self, value, qualifier):

        self.Send('@ ?\r')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)
        
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Error Occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' in self.ConnectionType:
            self.SetEnableStatusReporting( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        for output in range(1, self.IOSize + 1):
            self.OutputStatus[str(output)] = 'Untied'
            
    def blkmd_29_1708_16(self):
        self.IOSize = 16
        self.MatrixTieOutput= {
            '1'          : '0', 
            '2'          : '1', 
            '3'          : '2', 
            '4'          : '3', 
            '5'          : '4', 
            '6'          : '5', 
            '7'          : '6', 
            '8'          : '7', 
            '9'          : '8', 
            '10'         : '9', 
            '11'         : '10', 
            '12'         : '11', 
            '13'         : '12', 
            '14'         : '13', 
            '15'         : '14', 
            '16'         : '15', 
            'Solo Video' : '16', 
            'Solo Audio' : '17'
        }
        self.lastOutputTieUpdate = {str(out): 0 for out in range(1, self.IOSize + 1)}
        self.OutputStatus = {str(out): 'Untied' for out in range(1, self.IOSize + 1)}
    
    
    def blkmd_29_1708_4(self):
        self.IOSize = 4
        self.lastOutputTieUpdate = {str(out): 0 for out in range(1, self.IOSize + 1)}
        self.OutputStatus = {str(out): 'Untied' for out in range(1, self.IOSize + 1)}
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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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

