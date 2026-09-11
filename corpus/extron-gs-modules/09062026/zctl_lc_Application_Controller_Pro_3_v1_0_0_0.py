from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

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
        self._Address = 0
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Level': {'Parameters':['Address'], 'Status': {}},
            'LevelStatus': {'Parameters':['Address'], 'Status': {}},
            'Mode': {'Parameters':['Address'], 'Status': {}},
            'Recall': {'Parameters':['Address'], 'Status': {}},
            'Scene': {'Parameters':['Address'], 'Status': {}},
            'Serial': {'Parameters':['Address'], 'Status': {}},
        }

        self.deliLen = {
            'Heartbeat' : 12,
            'Serial' : 12,
            'LevelStatus' : 5
        }

    def address_convert(self, a):
        addresses = {
            'Group 0':  64,
            'Group 1':  65,
            'Group 2':  66,
            'Group 3':  67,
            'Group 4':  68,
            'Group 5':  69,
            'Group 6':  70,
            'Group 7':  71,
            'Group 8':  72,
            'Group 9':  73,
            'Group 10': 74,
            'Group 11': 75,
            'Group 12': 76,
            'Group 13': 77,
            'Group 14': 78,
            'Group 15': 79,
            'Broadcast': 127
        }

        if a in addresses:
            return addresses[a]
        elif 0 <= int(a) <= 63:
            return int(a)
        else:
            return None
        
    def checksum(self, data):
        result = 0
        for byte in data:
            result ^= byte

        return data + result.to_bytes(1, byteorder='big')
    
    def SetLevel(self, value, qualifier):

        address = self.address_convert(qualifier['Address'])

        if address is not None and 0 <= value <= 254:
            LevelCmdString = self.checksum(pack('>7B', 0x04, 0x00, 0xA2, address, 0x00, 0x00, value))
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')

    def UpdateLevelStatus(self, value, qualifier):

        address = self.address_convert(qualifier['Address'])

        if address is not None:
            LevelStatusCmdString = self.checksum(pack('>7B', 0x04, 0x00, 0xAA, address, 0x00, 0x00, 0x00))
            res = self.__UpdateHelper('LevelStatus', LevelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3])
                    self.WriteStatus('LevelStatus', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Level Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLevelStatus')

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'On, Step Up'   : 0xA3,
            'Off, Step Down': 0xA4,
            'Up'            : 0xA5,
            'Down'          : 0xA6,
            'Off'           : 0xA9
        }

        address = self.address_convert(qualifier['Address'])
        if address is not None and value in ValueStateValues:
            ModeCmdString = self.checksum(pack('>7B', 0x04, 0x00, ValueStateValues[value], address, 0x00, 0x00, 0x00))
            self.__SetHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMode')
    def SetRecall(self, value, qualifier):

        ValueStateValues = {
            'Min' : 0xA7,
            'Max' : 0xA8
        }
        
        address = self.address_convert(qualifier['Address'])
        if address is not None and value in ValueStateValues:
            RecallCmdString = self.checksum(pack('>7B', 0x04, 0x00, ValueStateValues[value], address, 0x00, 0x00, 0x00))
            self.__SetHelper('Recall', RecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecall')
    def SetScene(self, value, qualifier):

        address = self.address_convert(qualifier['Address'])
        if address is not None and 0 <= int(value) <= 15:
            SceneCmdString = self.checksum(pack('>7B', 0x04, 0x00, 0xA1, address, 0x00, 0x00, int(value)))
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')
    def UpdateSerial(self, value, qualifier):

        address = self.address_convert(qualifier['Address'])
        if address is not None:
            SerialCmdString = self.checksum(pack('>7B', 0x04, 0x00, 0xB9, address, 0x00, 0x00, 0x00))
            res = self.__UpdateHelper('Serial', SerialCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1]
                    value = str(int.from_bytes(value, byteorder='big'))
                    self.WriteStatus('Serial', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Serial: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSerial')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = self.deliLen[command])
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])