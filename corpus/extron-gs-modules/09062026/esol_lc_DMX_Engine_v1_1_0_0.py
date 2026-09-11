from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
            'AddScene': {'Parameters':['Channel','Time'], 'Status': {}},
            'BuildScene': {'Parameters':['Channel','Time'], 'Status': {}},
            'ChannelLevel': {'Parameters':['Channel','Fade Speed'], 'Status': {}},
            'DMXChannelValue': {'Parameters':['Channel'], 'Status': {}},
            'HaltChannel': { 'Status': {}},
            'Jog': {'Parameters':['Channel','Number'], 'Status': {}},
            'Ping': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RecallScene': {'Parameters':['Time'], 'Status': {}},
            'StoreScene': { 'Status': {}},
            }





                    

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'([0-9]{1,3})\s?=\s?([0-9]{1,3})\r'), self.__MatchDMXChannelValue, None)





    def SetAddScene(self, value, qualifier):

        TimeConstraints = {
            'Min' : 0,
            'Max' : 999
            }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        channel = int(qualifier['Channel'])
        time = int(qualifier['Time'])
        if (ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']) and (1 <= channel <= 512) and (TimeConstraints['Min'] <= time <= TimeConstraints['Max']):
            AddSceneCmdString = 'A{0:03d}@{1:03d}:{2:03d}\r'.format(channel, int(value), time)
            self.__SetHelper('AddScene', AddSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAddScene')



    def SetBuildScene(self, value, qualifier):

        TimeConstraints = {
            'Min' : 0,
            'Max' : 999
            }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        channel = int(qualifier['Channel'])
        time = int(qualifier['Time'])
        if (ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']) and (1 <= channel <= 512) and (TimeConstraints['Min'] <= time <= TimeConstraints['Max']):
            BuildSceneCmdString = 'F{0:03d}@{1:03d}:{2:03d}\r'.format(channel, int(value), time)
            self.__SetHelper('BuildScene', BuildSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBuildScene')



    def SetChannelLevel(self, value, qualifier):

        ChannelConstraints = {
            'Min' : 0,
            'Max' : 512
        }

        FadeSpeedConstraints = {
            'Min' : 0,
            'Max' : 999
            }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        channel = int(qualifier['Channel'])
        fadeSpeed = qualifier['Fade Speed']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and ChannelConstraints['Min'] <= channel <= ChannelConstraints['Max'] and FadeSpeedConstraints['Min'] <= fadeSpeed <= FadeSpeedConstraints['Max'] :
            ChannelLevelCmdString = 'Z{0:03d}@{1:03d}:{2:03d}\r'.format(channel, value, fadeSpeed)
            self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelLevel')
    def UpdateDMXChannelValue(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 512:
            DMXChannelValueCmdString = 'Q{0:03d}-{0:03d}\r'.format(channel)
            self.__UpdateHelper('DMXChannelValue', DMXChannelValueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDMXChannelValue')

    def __MatchDMXChannelValue(self, match, tag):

        if int(match.group(1).decode()) == 1:
            qualifier = {}
            qualifier['Channel'] = str(int(match.group(1).decode()))
            value = int(match.group(2).decode())
            self.WriteStatus('DMXChannelValue', value, qualifier)

    def SetHaltChannel(self, value, qualifier):

        HaltChannelCmdString = 'H{0:03d}\r'.format(int(value))
        self.__SetHelper('HaltChannel', HaltChannelCmdString, value, qualifier)



    def SetJog(self, value, qualifier):

        ChannelConstraints = {
            'Min' : 0,
            'Max' : 512
        }

        NumberConstraints = {
            'Min' : 0,
            'Max' : 255
        }
        
        ValueStateValues = {
            'Up'   : '+', 
            'Down' : '-'
        }

        channel = int(qualifier['Channel'])
        number = qualifier['Number']
        if NumberConstraints['Min'] <= number <= NumberConstraints['Max'] and ChannelConstraints['Min'] <= channel <= ChannelConstraints['Max']:
            JogCmdString = 'J{}:{}{}\r'.format(channel, ValueStateValues[value], number)
            self.__SetHelper('Jog', JogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetJog')



    def UpdatePing(self, value, qualifier):


        PingCmdString = 'Q001-001\r'
        self.__UpdateHelper('Ping', PingCmdString, value, qualifier)
    


    def SetReboot(self, value, qualifier):

        RebootCmdString = 'I\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)



    def SetRecallScene(self, value, qualifier):

        TimeConstraints = {
            'Min' : 0,
            'Max' : 999
            }

        time = int(qualifier['Time'])
        if TimeConstraints['Min'] <= time <= TimeConstraints['Max']:
            RecallSceneCmdString = 'S{0:03d}:{1:03d}\r'.format(int(value), time)
            self.__SetHelper('RecallScene', RecallSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallScene')



    def SetStoreScene(self, value, qualifier):

        StoreSceneCmdString = 'M{0:03d}\r'.format(int(value))
        self.__SetHelper('StoreScene', StoreSceneCmdString, value, qualifier)


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

