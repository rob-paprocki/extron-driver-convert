from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass(): 
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.Channel_Values = {
            'Channel In 1': '1',
            'Channel In 2': '2',
            'Channel In 3': '3',
            'Channel In 4': '4',
            'Channel In 5': '5',
            'Channel In 6': '6',
            'Channel In 7': '7',
            'Channel In 8': '8',
            'Aux Input': '9',
            'Channel Out 1': '10',
            'Channel Out 2': '11',
            'Channel Out 3': '12',
            'Channel Out 4': '13',
            'Channel Out 5': '14',
            'Channel Out 6': '15',
            'Channel Out 7': '16',
            'Channel Out 8': '17',
            'Mix A': '18',
            'Mix B': '19'
        }

        self.Ch_Match_Values = {
            '1': 'Channel In 1',
            '2': 'Channel In 2',
            '3': 'Channel In 3',
            '4': 'Channel In 4',
            '5': 'Channel In 5',
            '6': 'Channel In 6',
            '7': 'Channel In 7',
            '8': 'Channel In 8',
            '9': 'Aux Input',
            '10': 'Channel Out 1',
            '11': 'Channel Out 2',
            '12': 'Channel Out 3',
            '13': 'Channel Out 4',
            '14': 'Channel Out 5',
            '15': 'Channel Out 6',
            '16': 'Channel Out 7',
            '17': 'Channel Out 8',
            '18': 'Mix A',
            '19': 'Mix B',
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\<\s*REP\s*([0-9]|[1][0-9])\s*AUDIO_GAIN_HI_RES\s*([0-9]{4})\s*\>'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'\<\s*REP\s*([0-9]|[1][0-9])\s*AUDIO_MUTE\s*(ON|OFF)\s*\>'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\<\s*REP\s*ERR\s*[0-9a-zA-Z ]+\s*\>'), self.__MatchError, None)



    def SetAudioGain(self, value, qualifier):

        Ch_Value = qualifier['Channel']
        channel = self.Channel_Values[Ch_Value]

        if int(value) >= 0 and int(value) <= 1280:
            aud_val = str(value).zfill(4)            
            CmdString = '< SET {0} AUDIO_GAIN_HI_RES {1} >'.format(channel, aud_val)
 
            self.__SetHelper('AudioGain', CmdString, value, qualifier,3)
        else:
            print('Invalid Command for SetAudioGain')


    def UpdateAudioGain(self, value, qualifier):

        Ch_Value = qualifier['Channel']
        channel = self.Channel_Values[Ch_Value]

        CmdString = '< GET {0} AUDIO_GAIN_HI_RES >'.format(channel)
        self.__UpdateHelper('AudioGain', CmdString, value, qualifier)             


    def __MatchAudioGain(self, match, tag):

        value = int(match.group(2).decode())
        channel = self.Ch_Match_Values[match.group(1).decode()]
        qualifier = {'Channel':channel}
        self.WriteStatus('AudioGain', value, qualifier)


    def SetAudioMute(self, value, qualifier):

        Ch_Value = qualifier['Channel']
        channel = self.Channel_Values[Ch_Value]

        CmdString = '< SET {0} AUDIO_MUTE {1} >'.format(channel, value.upper())
 
        self.__SetHelper('AudioMute', CmdString, value, qualifier,3)


    def UpdateAudioMute(self, value, qualifier):

        Ch_Value = qualifier['Channel']
        channel = self.Channel_Values[Ch_Value]

        CmdString = '< GET {0} AUDIO_MUTE >'.format(channel)
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)


    def __MatchAudioMute(self, match, tag):

        Mute_Value = {
            "ON"   : 'On',
            "OFF"  : 'Off',
        }

        value = Mute_Value[match.group(2).decode()]
        channel = self.Ch_Match_Values[match.group(1).decode()]
        qualifier = {'Channel':channel}
        self.WriteStatus('AudioMute', value, qualifier)


    def __MatchError(self, match, tag):

        print('Error command is not able to be implemented')


    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
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
            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
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
                result = re.search(regexString, self._ReceiveBuffer)                
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
        if self.connectionFlag == False:
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
