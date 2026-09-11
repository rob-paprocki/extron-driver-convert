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
        self.Models = {
            'SS-R200': self.tasc_31_400_C,
            'SS-CDR200': self.tasc_31_400_A,
            'SS-R1': self.tasc_31_400,
            'SS-CDR1': self.tasc_31_400_B,
            'SS-R100': self.tasc_31_400_C,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceSelect': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'DirectTrackSearchPreset': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'TrackNumber': { 'Status': {}},
            'Transport': { 'Status': {}},
        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\n0FF010(0|1|2|3)\r'), self.__MatchDeviceSelect, None)
            self.AddMatchString(re.compile(b'\n0D0(00|01|10|11|12|80|81|82|83)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\n0CC0(0|1)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\n0B70(0|1)\r'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'\n0D5(00|01)([0-9]{4})\r'), self.__MatchTrackNumber, None)



    def SetDeviceSelect(self, value, qualifier):

        self.__SetHelper('DeviceSelect', self.DeviceStates[value] , value, qualifier)
    def UpdateDeviceSelect(self, value, qualifier):
        self.__UpdateHelper('DeviceSelect', '\n07F\r', value, qualifier)

    def __MatchDeviceSelect(self, match, qualifier):
        self.WriteStatus('DeviceSelect',  self.DeviceStateStates[match.group(1).decode()] , None)

    def UpdateDeviceStatus(self, value, qualifier):
        self.__UpdateHelper('DeviceStatus', '\n050\r' , value, qualifier)

    def __MatchDeviceStatus(self, match, qualifier):

        States = {
            '00': 'No Media Inserted',
            '01': 'Eject',
            '10': 'Stop',
            '11': 'Playing',
            '12': 'Ready',
            '80': 'Input Monitor',
            '81': 'Recording',
            '82': 'Record Ready',
            '83': 'Information Writing'
        }


        self.WriteStatus('DeviceStatus',  States[match.group(1).decode()] , None)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Only Remote'           : b'\n04C00\r',
            'Remote and Front Key'  : b'\n04C01\r'
        }

        self.__SetHelper('ExecutiveMode', States[value] , value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('ExecutiveMode', '\n04CFF\r' , value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        States = {
            '0': 'Only Remote',
            '1': 'Remote and Front Key'
        }

        self.WriteStatus('ExecutiveMode',  States[match.group(1).decode()] , None)

    def SetRepeat(self, value, qualifier):

        States = {
            'On'    : b'\n03701\r',
            'Off'   : b'\n03700\r'
        }

        self.__SetHelper('Repeat', States[value] , value, qualifier)
    def UpdateRepeat(self, value, qualifier):
        self.__UpdateHelper('Repeat', '\n037FF\r' , value, qualifier)

    def __MatchRepeat(self, match, qualifier):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Repeat',  States[match.group(1).decode()] , None)

    def SetDirectTrackSearchPreset(self, value, qualifier):

        if value:
            if 0 <= int(value) <= 9999:
                tempValue = value.zfill(4).encode()
                CmdString = b'\n023' + tempValue[2:3] + tempValue[3:4] + tempValue[0:1] + tempValue[1:2] + b'\r'
                self.__SetHelper('SetSetDirectTrackSearchPreset', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetSetDirectTrackSearchPreset')
        else:
            self.Discard('Invalid Command for SetSetDirectTrackSearchPreset')


    def UpdateTrackNumber(self, value, qualifier):

        self.__UpdateHelper('TrackNumber', b'\n055\r' , value, qualifier)

    def __MatchTrackNumber(self, match, qualifier):
        res = match.group(2).decode()
        value = int(res[2] + res[3] + res[0] + res[1])
        self.WriteStatus('TrackNumber', value, None)

    def SetTransport(self, value, qualifier):

        States = {
            'Play'                  : b'\n012\r',
            'Stop'                  : b'\n010\r',
            'Ready'                 : b'\n01401\r',
            'Previous'              : b'\n01A01\r',
            'Next'                  : b'\n01A00\r',
            'Record'                : b'\n01301\r',
            'Record - Input Monitor': b'\n01310\r',
            'Record - Track Mark'   : b'\n01302\r',
            'Shuttle Forward'       : b'\n01600\r',
            'Shuttle Rewind'        : b'\n01601\r'
        }

        self.__SetHelper('Transport', States[value] , value, qualifier)


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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        

    def tasc_31_400(self):
        pass

    def tasc_31_400_A(self):


        self.DeviceStates = {
            'USB'           : b'\n07F0102\r',
            'SD'            : b'\n07F0103\r',
            'Compact Flash' : b'\n07F0100\r',
            'CD'            : b'\n07F0101\r',
        }

        self.DeviceStateStates = {
            '2': 'USB',
            '3': 'SD',
            '0': 'Compact Flash',
            '1': 'CD',
        }


    def tasc_31_400_B(self):


        self.DeviceStates = {
            'Compact Flash' : b'\n07F0100\r',
            'CD'            : b'\n07F0101\r',
        }

        self.DeviceStateStates = {
            '0': 'Compact Flash',
            '1': 'CD',
        }


    def tasc_31_400_C(self):


        self.DeviceStates = {
            'USB'           : b'\n07F0102\r',
            'SD'            : b'\n07F0103\r',
            'Compact Flash' : b'\n07F0100\r',
        }

        self.DeviceStateStates = {
            '2': 'USB',
            '3': 'SD',
            '0': 'Compact Flash',
        }


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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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