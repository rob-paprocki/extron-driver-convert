from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re

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
            'BroadcastLevel': {'Status': {}},
            'BroadcastPower': {'Status': {}},
            'BroadcastRecallLevel': {'Status': {}},
            'GroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'GroupPower': {'Parameters': ['Group'], 'Status': {}},
            'RecallGroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'RecallScene': {'Parameters': ['Address'], 'Status': {}},
            'RecallBroadcastScene': {'Status': {}},
            'RecallGroupScene': {'Parameters': ['Group'], 'Status': {}},
            'RecallShortLevel': {'Parameters': ['Address'], 'Status': {}},
            'ShortLevel': {'Parameters': ['Address'], 'Status': {}},
            'ShortPower': {'Parameters': ['Address'], 'Status': {}},
        }       

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(\x02|\x03)(\x6C|\x70|\x71|[\x73-\x75]).*'), self.__MatchError, None)

    def SetBroadcastLevel(self, value, qualifier):
        LevelRange = {
            'Min': 0,
            'Max': 254
        }

        if LevelRange['Min'] <= value <= LevelRange['Max']:
            CommandString = b'\x03\x51\xFE' + value.to_bytes(1, 'big')
            self.__SetHelper('BroadcastLevel', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetBroadcastLevel')

    def SetBroadcastPower(self, value, qualifier):
        PowerControlsDic = {
            'On': b'\x08',
            'Off': b'\x07'
        }

        CommandString = b'\x03\x51\xFF' + PowerControlsDic[value]
        self.__SetHelper('BroadcastPower', CommandString, value, qualifier)

    def SetBroadcastRecallLevel(self, value, qualifier):
        RecallLevelDic = {
            'Minimum': b'\x06',
            'Maximum': b'\x05'
        }

        CommandString = b'\x03\x51\xFF' + RecallLevelDic[value]
        self.__SetHelper('BroadcastRecallLevel', CommandString, value, qualifier)

    def SetGroupLevel(self, value, qualifier):
        GroupDic = {
            '1': b'\x80',
            '2': b'\x82',
            '3': b'\x84',
            '4': b'\x86',
            '5': b'\x88',
            '6': b'\x8A',
            '7': b'\x8C',
            '8': b'\x8E',
            '9': b'\x90',
            '10': b'\x92',
            '11': b'\x94',
            '12': b'\x96',
            '13': b'\x98',
            '14': b'\x9A',
            '15': b'\x9C',
            '16': b'\x9E'
        }

        LevelRange = {
            'Min': 0,
            'Max': 254
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            if LevelRange['Min'] <= value <= LevelRange['Max']:
                CommandString = b'\x03\x51' + GroupDic[Group] + value.to_bytes(1, 'big')
                self.__SetHelper('GroupLevel', CommandString, value, qualifier)
            else:
                print('Invalid Command for SetGroupLevel')
        else:
            print('Invalid Command for SetGroupLevel')

    def SetGroupPower(self, value, qualifier):
        PowerControlsDic = {
            'On': b'\x08',
            'Off': b'\x07'
        }

        GroupDic = {
            '1': b'\x81',
            '2': b'\x83',
            '3': b'\x85',
            '4': b'\x87',
            '5': b'\x89',
            '6': b'\x8B',
            '7': b'\x8D',
            '8': b'\x8F',
            '9': b'\x91',
            '10': b'\x93',
            '11': b'\x95',
            '12': b'\x97',
            '13': b'\x99',
            '14': b'\x9B',
            '15': b'\x9D',
            '16': b'\x9F'
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            CommandString = b'\x03\x51' + GroupDic[Group] + PowerControlsDic[value]
            self.__SetHelper('GroupPower', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetGroupPower')

    def SetRecallGroupLevel(self, value, qualifier):
        RecallLevelDic = {
            'Minimum': b'\x06',
            'Maximum': b'\x05'
        }

        GroupDic = {
            '1': b'\x81',
            '2': b'\x83',
            '3': b'\x85',
            '4': b'\x87',
            '5': b'\x89',
            '6': b'\x8B',
            '7': b'\x8D',
            '8': b'\x8F',
            '9': b'\x91',
            '10': b'\x93',
            '11': b'\x95',
            '12': b'\x97',
            '13': b'\x99',
            '14': b'\x9B',
            '15': b'\x9D',
            '16': b'\x9F'
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            CommandString = b'\x03\x51' + GroupDic[Group] + RecallLevelDic[value]
            self.__SetHelper('RecallGroupLevel', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetRecallGroupLevel')

    def SetRecallBroadcastScene(self, value, qualifier):
        scene_limits = {
                'min': 1,
                'max': 16
                }

        scene = int(value)

        ok = scene_limits['min'] <= scene <= scene_limits['max']

        if ok:
                scene = (scene - 1) | 0x10

                CommandString = b'\x03\x51\xFF' + scene.to_bytes(1, 'big')
                self.__SetHelper('RecallBroadcastScene', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetRecallBroadcastScene')

    def SetRecallGroupScene(self, value, qualifier):
        GroupDic = {
            '1': b'\x81',
            '2': b'\x83',
            '3': b'\x85',
            '4': b'\x87',
            '5': b'\x89',
            '6': b'\x8B',
            '7': b'\x8D',
            '8': b'\x8F',
            '9': b'\x91',
            '10': b'\x93',
            '11': b'\x95',
            '12': b'\x97',
            '13': b'\x99',
            '14': b'\x9B',
            '15': b'\x9D',
            '16': b'\x9F'
        }

        scene_limits = {
                'min': 1,
                'max': 16
                }

        Group = qualifier['Group']
        scene = int(value)

        ok = Group in GroupDic
        ok &= scene_limits['min'] <= scene <= scene_limits['max']

        if ok:
                scene = (scene - 1) | 0x10

                CommandString = b'\x03\x51' + GroupDic[Group] + scene.to_bytes(1, 'big')
                self.__SetHelper('RecallGroupScene', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetRecallGroupScene')

    def SetRecallScene(self, value, qualifier):
        addr_limits = {
                'min': 1,
                'max': 63
                }

        scene_limits = {
                'min': 1,
                'max': 16
                }

        addr = int(qualifier['Address'])
        scene = int(value)

        ok = addr_limits['min'] <= addr <= addr_limits['max']
        ok &= scene_limits['min'] <= scene <= scene_limits['max']

        if ok:
            addr = ((addr - 1) << 1) | 0x01                
            scene = (scene - 1) | 0x10

            CommandString = b'\x03\x51' + addr.to_bytes(1, 'big') + scene.to_bytes(1, 'big')
            self.__SetHelper('RecallScene', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetRecallScene')

    def SetRecallShortLevel(self, value, qualifier):
        RecallLevelDic = {
            'Minimum': b'\x06',
            'Maximum': b'\x05'
        }

        short = int(qualifier['Address'])

        if short != 1:
            short = short - 1
            short = short << 1
            short = short | 1

        if 1 <= int(qualifier['Address']) <= 63:
            CommandString = b'\x03\x51' + short.to_bytes(1, 'big') + RecallLevelDic[value]
            self.__SetHelper('RecallShortLevel', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetRecallShortLevel')

    def SetShortLevel(self, value, qualifier):
        LevelRange = {
            'Min': 0,
            'Max': 254
        }

        short = int(qualifier['Address'])

        short = short - 1
        short = short << 1

        if 1 <= int(qualifier['Address']) <= 63:
            if LevelRange['Min'] <= value <= LevelRange['Max']:
                CommandString = b'\x03\x51' + short.to_bytes(1, 'big') + value.to_bytes(1, 'big')
                self.__SetHelper('ShortLevel', CommandString, value, qualifier)
            else:
                print('Invalid Command for SetShortLevel')
        else:
            print('Invalid Command for SetShortLevel')

    def SetShortPower(self, value, qualifier):
        PowerControlDic = {
            'On': b'\x08',
            'Off': b'\x07'
        }

        short = int(qualifier['Address'])

        if short != 1:
            short = short - 1
            short = short << 1
            short = short | 1

        if 1 <= int(qualifier['Address']) <= 63:
            CommandString = b'\x03\x51' + short.to_bytes(1, 'big') + PowerControlDic[value]
            self.__SetHelper('ShortPower', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetShortPower')

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

    def __MatchError(self, match, tag):
        ErrorCodes = {
            b'\x6C': 'Query response error',
            b'\x70': 'Failure transmitting a DALI message',
            b'\x71': 'Illegal DALI frame received',
            b'\x73': 'Unknown command',
            b'\x74': 'Already transmitting and cannot accept further data',
            b'\x75': 'DALI line held low for too long'
        }

        try:
            value = ErrorCodes[match.group(2)]
            print(value)
        except KeyError:
            print('Unknown Error')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetOnConnectedString( None, None)

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
