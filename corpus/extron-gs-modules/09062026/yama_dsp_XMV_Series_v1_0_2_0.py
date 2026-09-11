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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'XMV4280': self.yama_25_2452_4CH,
            'XMV4140': self.yama_25_2452_4CH,
            'XMV4280-D': self.yama_25_2452_4CH,
            'XMV4140-D': self.yama_25_2452_4CH,
            'XMV8280': self.yama_25_2452_8CH,
            'XMV8140': self.yama_25_2452_8CH,
            'XMV8280-D': self.yama_25_2452_8CH,
            'XMV8140-D': self.yama_25_2452_8CH,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Mute': {'Parameters': ['Channel'], 'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}}
            }


        self.RunModeDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/1/4/([0-7])/0/2/0 0 0 ([01])\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/1/6/0/0/0/0 0 0 ([01])\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/1/4/([0-7])/0/0/0 0 0 ([-+]?\d{1,2})\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'OK devstatus runmode "normal"\n'), self.__MatchRunMode, None)

    def __MatchRunMode(self, match, tag):
        self.RunModeDisabled = False

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))
        
    def SetMute(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': self.MaxChannels,
            'Value': int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        }

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        if value in ValueStateValues and self.__constraint_checker(ChannelConstraints):
            MuteCmdString = 'set MTX:mem_512/1/4/{}/0/2/0 0 0 {}\n'.format(ChannelConstraints['Value'],
                                                                               ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': self.MaxChannels,
            'Value': int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        }
        
        if self.__constraint_checker(ChannelConstraints):
            MuteCmdString = 'get MTX:mem_512/1/4/{}/0/2/0 0 0\n'.format(ChannelConstraints['Value'])
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
 
        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '0',
            'Off': '1',
        }

        if value in ValueStateValues:
            PowerCmdString = 'set MTX:mem_512/1/6/0/0/0/0 0 0 {}\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if self.RunModeDisabled:
            self.Send(b'devstatus runmode\n')


        PowerCmdString = 'get MTX:mem_512/1/6/0/0/0/0 0 0\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': self.MaxChannels,
            'Value': int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': -99,
            'Max': 0,
            'Value': value
        }

        if self.__constraint_checker(ChannelConstraints, ValueConstraints):
            VolumeCmdString = 'set MTX:mem_512/1/4/{}/0/0/0 0 0 {}\n'.format(ChannelConstraints['Value'],
                                                                             ValueConstraints['Value'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': self.MaxChannels,
            'Value': int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        }

        if self.__constraint_checker(ChannelConstraints):
            VolumeCmdString = 'get MTX:mem_512/1/4/{}/0/0/0 0 0\n'.format(ChannelConstraints['Value'])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = dict()
        qualifier['Channel'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.RunModeDisabled:
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

        self.RunModeDisabled = True
    def yama_25_2452_4CH(self):

        self.MaxChannels = 3



    def yama_25_2452_8CH(self):

        self.MaxChannels = 7

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

