from extronlib.interface import EthernetClientInterface
import re
from struct import pack

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
            'ERT-30': self.arthlm_20_6238_30,
            'ERT-60': self.arthlm_20_6238_60,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ButtonLock': {'Parameters':['Device ID'], 'Status': {}},
            'MicrophoneMute': {'Parameters':['Device ID'], 'Status': {}},
            'Move': {'Parameters':['Device ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFB([\x01-\x3C])\x14([\x00-\xFF])[\x00-\xFF]'), self.__MatchButtonLock, None)

    def idCheck(self, DeviceID):
        try:
            if DeviceID == 'Broadcast':
                return 0xF7
            elif 1 <= int(DeviceID) <= self.IDMax:
                return int(DeviceID)
            else:
                return
        except ValueError:
            return
        
    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
            }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            ButtonLockCmdString = pack('5B', 0xFA, DeviceID, 0x04, ValueStateValues[value], 0x00)
            self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonLock')

    def UpdateButtonLock(self, value, qualifier):

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID not in [None, 0xF7]:
            ButtonLockCmdString = pack('5B', 0xFA, DeviceID, 0x14, 0x00, 0x00)
            self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateButtonLock')

    def __MatchButtonLock(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            }
            
        qualifier = {'Device ID': str(match.group(1)[0])}

        bin_val = bin(int(match.group(2)[0]))[2:].zfill(8)
        
        button_value = ValueStateValues[bin_val[4]]
        self.WriteStatus('ButtonLock', button_value, qualifier)
        
        mic_value = ValueStateValues[bin_val[5]]       
        self.WriteStatus('MicrophoneMute', mic_value, qualifier)
        
        if bin_val[6] == '1':
            self.WriteStatus('Move', 'Down', qualifier)
        elif bin_val[7] == '1':
            self.WriteStatus('Move', 'Up', qualifier)

    def SetMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
            }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            MicrophoneMuteCmdString = pack('5B', 0xFA, DeviceID, 0x02, ValueStateValues[value], 0x00)
            self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMute')

    def UpdateMicrophoneMute(self, value, qualifier):

        self.UpdateButtonLock(value, qualifier)

    def SetMove(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x01,
            'Down': 0x00
            }

        DeviceID = self.idCheck(qualifier['Device ID'])
        if DeviceID is not None and value in ValueStateValues:
            MoveCmdString = pack('5B', 0xFA, DeviceID, 0x01, ValueStateValues[value], 0x00)
            self.__SetHelper('Move', MoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMove')

    def UpdateMove(self, value, qualifier):

        self.UpdateButtonLock(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
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

    def arthlm_20_6238_30(self):
        self.IDMax = 30

    def arthlm_20_6238_60(self):
        self.IDMax = 60

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

