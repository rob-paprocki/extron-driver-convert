from extronlib.interface import EthernetClientInterface
import re
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputMode': {'Parameters':['Channel'], 'Status': {}},
            'InputStatus': {'Parameters':['Channel','Direction'], 'Status': {}},
            'Output': {'Parameters':['Channel','Duration'], 'Status': {}},
            'OutputByRange': {'Parameters':['Channel','Range'], 'Status': {}},
            'OutputStatus': {'Parameters':['Channel'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\>FN,MODE,([1-4]),(0|1)\n\r'), self.__MatchInputMode, None)
            self.AddMatchString(re.compile(b'\>FN,IN,(ON|OFF),1\n\r\>FN,IN,(ON|OFF),2\n\r\>FN,IN,(ON|OFF),3\n\r\>FN,IN,(ON|OFF),4\n\r\>FN,IN,(ON|OFF),5\n\r\>FN,IN,(ON|OFF),6\n\r\>FN,IN,(ON|OFF),7\n\r\>FN,IN,(ON|OFF),8\n\r', re.DOTALL), self.__MatchInputStatus, None)
            self.AddMatchString(re.compile(b'\>FN,OUT,(UP|DOWN|STOP|TOP|BOTTOM),1.*?\n\r\>FN,OUT,(UP|DOWN|STOP|TOP|BOTTOM),2.*?\n\r\>FN,OUT,(UP|DOWN|STOP|TOP|BOTTOM),3.*?\n\r\>FN,OUT,(UP|DOWN|STOP|TOP|BOTTOM),4.*?\n\r'), self.__MatchStatusRequired, None)

    def SetInputMode(self, value, qualifier):

        ChannelStates = {
            'All' : '0', 
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4'
        }

        ValueStateValues = {
            'Independent' : '1', 
            'Active'      : '0'
        }

        channel = qualifier['Channel']
        if channel in ['All', '1', '2', '3', '4']:
            InputModeCmdString = 'FN,MODE,{0},{1}\r'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('InputMode', InputModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMode')

    def UpdateInputMode(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['1', '2', '3', '4']:
            InputModeCmdString = 'FN,GETMODE,{0}\r'.format(channel)
            self.__UpdateHelper('InputMode', InputModeCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputMode')

    def __MatchInputMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Independent', 
            '1' : 'Active'
        }

        qualifier = {}
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMode', value, qualifier)

    def UpdateInputStatus(self, value, qualifier):

        channel = qualifier['Channel']
        direction = qualifier['Direction']
        if channel in ['1', '2', '3', '4'] and direction in ['Up', 'Down']:
            InputStatusCmdString = 'FN,SRI\r'
            self.__UpdateHelper('InputStatus', InputStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputStatus')

    def __MatchInputStatus(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OFF' : 'Off'
        }

        self.WriteStatus('InputStatus', ValueStateValues[match.group(1).decode()], {'Channel' : '1', 'Direction' : 'Up'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(2).decode()], {'Channel' : '1', 'Direction' : 'Down'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(3).decode()], {'Channel' : '2', 'Direction' : 'Up'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(4).decode()], {'Channel' : '2', 'Direction' : 'Down'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(5).decode()], {'Channel' : '3', 'Direction' : 'Up'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(6).decode()], {'Channel' : '3', 'Direction' : 'Down'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(7).decode()], {'Channel' : '4', 'Direction' : 'Up'})
        self.WriteStatus('InputStatus', ValueStateValues[match.group(8).decode()], {'Channel' : '4', 'Direction' : 'Down'})

    def SetOutput(self, value, qualifier):

        ChannelStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            'All' : '0'
        }

        ValueStateValues = {
            'Up'   : 'UP', 
            'Down' : 'DOWN', 
            'Stop' : 'STOP'
        }

        channel = qualifier['Channel']
        duration = qualifier['Duration']
        if channel in ['All', '1', '2', '3', '4'] and 0 <= duration <= 65536:
            if duration != 0:
                if value == 'Up':
                    OutputCmdString = 'FN,DURUP,{0},{1}\r'.format(ChannelStates[channel], duration)
                elif value == 'Down':
                    OutputCmdString = 'FN,DURDOWN,{0},{1}\r'.format(ChannelStates[channel], duration)
                else:
                    OutputCmdString = ''
            else:
                OutputCmdString = 'FN,{0},{1}\r'.format(ValueStateValues[value], ChannelStates[channel])
            if OutputCmdString:
                self.__SetHelper('Output', OutputCmdString, value, qualifier)

            else:
                print('Invalid Command for SetOutput')
        else:
            print('Invalid Command for SetOutput')

    def SetOutputByRange(self, value, qualifier):

        ChannelStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            'All' : '0'
        }

        ValueStateValues = {
            'Go Up'         : 'GOUPBY', 
            'Go Down'       : 'GODOWNBY', 
            'Goto Position' : 'GOTO'
        }

        channel = qualifier['Channel']
        range = qualifier['Range']
        if 1 <= range <= 100 and channel in ['All', '1', '2', '3', '4']:
            OutputByRangeCmdString = 'FN,{0},{1},{2}\r'.format(ValueStateValues[value], ChannelStates[channel], range)
            self.__SetHelper('OutputByRange', OutputByRangeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputByRange')

    def UpdateOutputStatus(self, value, qualifier):

        StatusRequiredCmdString = 'FN,SRE\r'
        self.__UpdateHelper('OutputStatus', StatusRequiredCmdString, value, qualifier)

    def __MatchStatusRequired(self, match, tag):

        ValueStateValues = {
            'UP'     : 'Up', 
            'DOWN'   : 'Down',
            'STOP'   : 'Stop',
            'TOP'    : 'Top',
            'BOTTOM' : 'Bottom'
        }
        
        self.WriteStatus('OutputStatus', ValueStateValues[match.group(1).decode()], {'Channel' : '1'})
        self.WriteStatus('OutputStatus', ValueStateValues[match.group(2).decode()], {'Channel' : '2'})
        self.WriteStatus('OutputStatus', ValueStateValues[match.group(3).decode()], {'Channel' : '3'})
        self.WriteStatus('OutputStatus', ValueStateValues[match.group(4).decode()], {'Channel' : '4'})


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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
