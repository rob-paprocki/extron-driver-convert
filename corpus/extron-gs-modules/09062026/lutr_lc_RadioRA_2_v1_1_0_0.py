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
        
        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ButtonControl': {'Status': {}},
            'LEDControl': {'Parameters':['Integration ID','LED Number'], 'Status': {}},
            'LiftControl': {'Status': {}},
            'MasterOccupancyGroup': { 'Status': {}},
            'OccupancyGroup': {'Parameters':['Integration ID'], 'Status': {}},
            'TiltControl': {'Status': {}},
            'ZoneControl': {'Status': {}},
            'ZoneLevel': {'Parameters':['Integration ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z]+|0x[a-fA-F0-9]{8,10}),([0-9]{3}),9,([01])\r\n'), self.__MatchLEDControl, None)
            self.AddMatchString(re.compile(b'~GROUP,([0-9a-zA-Z]+|0x[a-fA-F0-9]{8,10}),3,(3|4|255)\r\n'), self.__MatchOccupancyGroup, None)
            self.AddMatchString(re.compile(b'~OUTPUT,([0-9a-zA-Z]+|0x[a-fA-F0-9]{8,10}),1,([\d]{1,3}\.[\d]{2})\r\n'), self.__MatchZoneLevel, None)
            self.AddMatchString(re.compile(b'~ERROR,([1-6])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Login:',re.I), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:',re.I), self.__MatchPassword, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
    
        self.SetPassword( match, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, tag):
        
        self.SetUsername(None, None)

    def SetButtonControl(self, value, qualifier):

        ValueStateValues = {
            'Press'   : '3', 
            'Release' : '4'
        }

        if 1 <= qualifier['Button Number'] <= 100 and 1 <= qualifier['Integration ID'] <= 1000000000:
            ButtonControlCmdString = '#DEVICE,{0},{1},{2}\r\n'.format(qualifier['Integration ID'], qualifier['Button Number'], ValueStateValues[value])
            self.__SetHelper('ButtonControl', ButtonControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonControl')

    def SetLEDControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if 1 <= qualifier['LED Number'] <= 100 and 1 <= qualifier['Integration ID'] <= 1000000000:
            led_number = qualifier['LED Number'] + 100
            LEDControlCmdString = '#DEVICE,{0},{1},9,{2}\r\n'.format(qualifier['Integration ID'], led_number, ValueStateValues[value])
            self.__SetHelper('LEDControl', LEDControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDControl')

    def UpdateLEDControl(self, value, qualifier):

        if 1 <= qualifier['LED Number'] <= 100 and 1 <= qualifier['Integration ID'] <= 1000000000:
            led_number = qualifier['LED Number'] + 100
            LEDControlCmdString = '?DEVICE,{0},{1},9\r\n'.format(qualifier['Integration ID'], led_number)
            self.__UpdateHelper('LEDControl', LEDControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDControl')

    def __MatchLEDControl(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        integrationID = int(match.group(1).decode())
        LEDQual = int(match.group(2).decode()) - 100
        if 1 <= LEDQual <= 100 and 1 <= integrationID <= 1000000000:
            qualifier = {'Integration ID' : integrationID, 'LED Number' : LEDQual}
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('LEDControl', value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetLiftControl(self, value, qualifier):

        ValueStateValues = {
            'Raise' : '14',
            'Lower' : '15',
            'Stop'  : '16'
        }

        if 1 <= qualifier['Integration ID'] <= 1000000000:
            LiftControlCmdString = '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value])
            self.__SetHelper('LiftControl', LiftControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLiftControl')

    def UpdateOccupancyGroup(self, value, qualifier):

        if 1 <= qualifier['Integration ID'] <= 1000000000:
            OccupancyGroupCmdString = '?GROUP,{0},3\r\n'.format(qualifier['Integration ID'])
            self.__UpdateHelper('OccupancyGroup', OccupancyGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOccupancyGroup')
            
    def __MatchOccupancyGroup(self, match, tag):

        ValueStateValues = {
            '3'   : 'Occupied', 
            '4'   : 'Unoccupied',
            '255' : 'Unknown'
        }

        qualifier = {'Integration ID' : int(match.group(1).decode())}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OccupancyGroup', value, qualifier)

    def SetTiltControl(self, value, qualifier):

        ValueStateValues = {
            'Raise' : '11',
            'Lower' : '12',
            'Stop'  : '13'
        }

        if 1 <= qualifier['Integration ID'] <= 1000000000:
            TiltControlCmdString = '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value])
            self.__SetHelper('TiltControl', TiltControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTiltControl')
    def SetZoneControl(self, value, qualifier):

        ValueStateValues = {
            'Raise' : '2',
            'Lower' : '3',
            'Stop'  : '4'
        }

        if 1 <= qualifier['Integration ID'] <= 1000000000:
            ZoneControlCmdString = '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value])
            self.__SetHelper('ZoneControl', ZoneControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneControl')
    def SetZoneLevel(self, value, qualifier):

        if 0 <= value <= 100 and 1 <= qualifier['Integration ID'] <= 1000000000:
            ZoneLevelCmdString = '#OUTPUT,{0},1,{1}\r\n'.format(qualifier['Integration ID'], '%.2f' % value)
            self.__SetHelper('ZoneLevel', ZoneLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneLevel')

    def UpdateZoneLevel(self, value, qualifier):

        if 1 <= qualifier['Integration ID'] <= 1000000000:
            ZoneLevelCmdString = '?OUTPUT,{0}\r\n'.format(qualifier['Integration ID'])
            self.__UpdateHelper('ZoneLevel', ZoneLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneLevel')

    def __MatchZoneLevel(self, match, tag):

        qualifier = {'Integration ID' : int(match.group(1).decode())}
        value = float(match.group(2).decode())
        self.WriteStatus('ZoneLevel', value, qualifier)

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
            '1' : 'Parameter count mismatch',
            '2' : 'Object does not exist',
            '3' : 'Invalid action number',
            '4' : 'Parameter data out of range',
            '5' : 'Parameter data malformed',
            '6' : 'Unsupported Command'
        }

        self.Error(['Error: {0}'.format(DEVICE_ERROR_CODES.get(match.group(1).decode()))])

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


    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 


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