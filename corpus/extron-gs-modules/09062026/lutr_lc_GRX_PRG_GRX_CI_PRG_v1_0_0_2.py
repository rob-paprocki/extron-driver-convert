from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import time 

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
        self.deviceUsername = 'nwk'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Schedule': { 'Status': {}},
            'SelectScene': {'Parameters': ['Control Unit'], 'Status': {}},
            'Zone': {'Parameters': ['Control Unit', 'Zone'], 'Status': {}},
                        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login: '), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'~:ss ([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)([1-9]|[A-F]|M)\r\n'), self.__MatchSelectScene, None)
            self.AddMatchString(re.compile(b':rs (0|1|2)\r\n'), self.__MatchSchedule, None)
            self.AddMatchString(re.compile(b'~ERROR #(1|2|6|13|14|15|16|20|21|22|24|25|26|31|80|100|101|102|103|255) [1-9]* OK\r\n'), self.__MatchError, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername and self.deviceUsername in ['nwk','nwk2']:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.Error(['Username is Incorrect or Missing'])

    def __MatchUsername(self, match, qualifier):

        self.SetUsername(None, None)
    def SetSelectScene(self, value, qualifier):

        Scene = {
                  'Off' : '0',
                  '1' : '1',
                  '2' : '2',
                  '3' : '3',
                  '4' : '4',
                  '5' : '5',
                  '6' : '6',
                  '7' : '7',
                  '8' : '8',
                  '9' : '9',
                  '10' : 'A',
                  '11' : 'B',
                  '12' : 'C',
                  '13' : 'D',
                  '14' : 'E',
                  '15' : 'F',
                }

        ControlUnit = qualifier['Control Unit']

        if 0 < int(ControlUnit) < 9:
            CommandString = ':A{0}{1}\r'.format(Scene[value], ControlUnit)
            self.__SetHelper('SelectScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelectScene')

    def UpdateSelectScene(self, value, qualifier):

        CommandString = ':G\r'
        self.__UpdateHelper('SelectScene', CommandString, value, qualifier)

    def __MatchSelectScene(self, match, qualifier):

        SceneName = {
                      'M' : 'Off',
                      '1' : '1',
                      '2' : '2',
                      '3' : '3',
                      '4' : '4',
                      '5' : '5',
                      '6' : '6',
                      '7' : '7',
                      '8' : '8',
                      '9' : '9',
                      'A' : '10',
                      'B' : '11',
                      'C' : '12',
                      'D' : '13',
                      'E' : '14',
                      'F' : '15'
                    }
              
        for x in range(8):
            value = SceneName[match.group(x+1).decode()]
            self.WriteStatus('SelectScene', value, {'Control Unit' : str(x+1)})

    def SetSchedule(self, value, qualifier):

        Schedule  = {
                      'Suspend' : '0',
                      'Weekday' : '1',
                      'Weekend' : '2'
                    }

        CommandString = ':SS{0}\r'.format(Schedule[value])

        self.__SetHelper('Schedule', CommandString, value, qualifier)

    def UpdateSchedule(self, value, qualifier):

        CommandString = ':RS\r'
        self.__UpdateHelper('Schedule', CommandString, value, qualifier)

    def __MatchSchedule(self, match, tag):

        Schedule = {
                     '0' : 'Suspend',
                     '1' : 'Weekday',
                     '2' : 'Weekend'
                   }

        value = Schedule[match.group(1).decode()]
        self.WriteStatus('Schedule', value, None)

    def SetZone(self, value, qualifier):

        ZoneControls = {
                         'Up' : ':B{0}{1}\r',
                         'Down' : ':D{0}{1}\r',
                         'Up Stop' : ':B{0}\r',
                         'Down Stop' : ':D{0}\r'
                       }

        ControlUnit = qualifier['Control Unit']
        Zone = qualifier['Zone']

        if 0 < int(ControlUnit) < 9:
            if 0 < int(Zone) < 9:
                CommandString = ZoneControls[value].format(ControlUnit, Zone)
                self.__SetHelper('Zone', CommandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetZone')
        else:
            self.Discard('Invalid Command for SetZone')

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

        DEVICE_ERROR_CODES = {
                               '1' : 'Control Unit Raise/Lower error',
                               '2' : 'Invalid scene selected',
                               '3' : 'Bad command was sent',
                               '13' : 'Not a timeclock unit (GRX-ATC or GRX-PRG)',
                               '14' : 'Illegal time was entered',
                               '15' : 'Invalid schedule',
                               '16' : 'No Super Sequence has been loaded',
                               '20' : 'Command was missing Control Units',
                               '21' : 'Command was missing data',
                               '22' : 'Error in command argument (improper hex value)',
                               '24' : 'Invalid Control Unit',
                               '25' : 'Invalid value, outside range of acceptable values',
                               '26' : 'Invalid Accessory Controls',
                               '31' : 'Network address illegaly formatted; 4 octets required (xxx.xxx.xxx.xxx)',
                               '80' : 'Time-out error, no response received',
                               '100' : 'Invalid Telnet login number',
                               '101' : 'Invalid Telnet login',
                               '102' : 'Telnet login name exceeds 8 characters',
                               '103' : 'Invalid number of arguments',
                               '255' : 'GRX-PRG must be in programming mode for specific commands'
                            }

        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error([value])

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

