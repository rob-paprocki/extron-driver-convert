from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self._MonitorID = pack('>B', 1)
        self._GroupID = pack('>B', 0)
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            }

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x03\x0BSONY[\x00-\x63][\x00-\x63]\x01\xB0\x00[\x00-\x11]STATret POWER (ON|OFF)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x03\x0BSONY[\x00-\x63][\x00-\x63]\x00\xB0\x00[\x00-\xFF]{1,2}([\x00-\xFF]{2})'), self.__MatchError, None)
        self.Header = b'\x03\x0BSONY' + self._GroupID + self._MonitorID + b'\x00\xB0\x00'
        

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Broadcast':
            self._GroupID = b'\xFF'
        elif 0 <= int(value) <= 99:
            self._GroupID = pack('>B', int(value))
        else:
            self.Error(['Invalid GroupID value, range is from 0 to 99 or Broadcast.'])
        self.Header = b'\x03\x0BSONY' + self._GroupID + self._MonitorID + b'\x00\xB0\x00'

    @property
    def MonitorID(self):
        return self._MonitorID

    @MonitorID.setter
    def MonitorID(self, value):
        if value == 'Broadcast':
            self._MonitorID = b'\xFF'
        elif 0 <= int(value) <= 99:
            self._MonitorID = pack('>B', int(value))
        else:
            self.Error(['Invalid MonitorID value, range is from 0 to 99 or Broadcast.'])
        self.Header = b'\x03\x0BSONY' + self._GroupID + self._MonitorID + b'\x00\xB0\x00'

    def SetKeypad(self, value, qualifier):

        if value in ['Enter', 'Delete']:
            dataLength = b'\x10' if value == 'Enter' else b'\x11'
        elif 0 <= int(value) <= 9:
            dataLength = b'\x0C'
        else:
            self.Discard('Invalid Command for SetKeypad')

        KeypadCmdString = self.Header + dataLength + b'INFObutton ' + value.upper().encode()
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': [b'\x0F', b'MENU'],
            'Up': [b'\x11', b'MENUUP'],
            'Down': [b'\x13', b'MENUDOWN'],
            'Enter': [b'\x12', b'MENUENT']
        }

        MenuNavigationCmdString = self.Header + ValueStateValues[value][0] + b'INFObutton ' + ValueStateValues[value][1]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x10', b'ON'],
            'Off': [b'\x11', b'OFF']
        }

        PowerCmdString = self.Header + ValueStateValues[value][0] + b'STATset POWER ' + ValueStateValues[value][1]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.Header + b'\x0D' + b'STATget POWER'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._GroupID == b'\xFF' or self._MonitorID == b'\xFF':
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

        ErrorCodes = {
            b'\x01\x01': 'Item Error: Item No. is not supported.',
            b'\x01\x02': 'Item Error: Item No. is supported, but Request is not supported.',
            b'\x01\x03': 'Item Error: Data Length is large.',
            b'\x01\x04': 'Item Error: Data is invalid.',
            b'\x01\x11': 'Item Error: Data size is not sufficient for Data Length.',
            b'\x01\x80': 'Item Error: Item No. is not acceptable (monitor is in sleep mode or rejecting VMC)',
            b'\x02\x01': 'Community Error: Community is invalid.',
            b'\x10\x01': 'Request Error: Version in Header is not supported.',
            b'\x10\x02': 'Request Error: Category in Header is invalid.',
            b'\x10\x03': 'Request Error: Request is invalid.',
            b'\x10\x11': 'Request Error: Header size is not sufficient.',
            b'\x10\x12': 'Request Error: Community size is not sufficient.',
            b'\x10\x13': 'Request Error: Command size is not sufficient.',
            b'\x10\x20': 'Request Error: Another client was operating a monitor and a request was discarded.',
            b'\x10\x21': 'Request Error: Unit ID or Group ID in a TCP communication packet is invalid.',
            b'\xF0\x01': 'Communication Error: Communication was not smooth for a certain period of time.'
        }

        if match.group(1) in ErrorCodes:
            self.Error([ErrorCodes[match.group(1)]])
        else:
            self.Error(['Unknown error occurred: ' + match.group(1).decode(encoding='iso-8859-1')])
        return ''

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

