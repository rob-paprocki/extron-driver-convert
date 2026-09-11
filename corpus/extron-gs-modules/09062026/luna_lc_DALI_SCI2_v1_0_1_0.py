from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DirectArcPower': {'Parameters':['Address'], 'Status': {}},
            'Mode': {'Parameters':['Address'], 'Status': {}},
        }

        self.AddMatchString(re.compile(b'\x31[\x00-\xFF]{3}([\x00-\xFF])'), self.__MatchError, None)

    def SetDirectArcPower(self, value, qualifier):

        if (qualifier['Address'] in ['Group 0', 'Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5', 
                                     'Group 6', 'Group 7', 'Group 8', 'Group 9', 'Group 10', 'Group 11', 
                                     'Group 12', 'Group 13', 'Group 14', 'Group 15'] or 
                                     0 <= int(qualifier['Address']) <= 63) and 0 <= value <= 254:
            
            if 'Group' in qualifier['Address']:
                addr_val = (int(qualifier['Address'][6:]) * 2) + 128
            else:
                addr_val = int(qualifier['Address']) * 2

            checksum_val = 0x34 ^ 0x04 ^ 0 ^ 0x03 ^ addr_val ^ value
            DirectArcPowerCmdString = pack('8B', 0x59, 0x34, 0x04, 0x00, 0x03, addr_val, value, checksum_val)
            self.__SetHelper('DirectArcPower', DirectArcPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDirectArcPower')

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Off'                    : 0x00,
            'Up'                     : 0x01,
            'Down'                   : 0x02,
            'Step Up'                : 0x03,
            'Step Down'              : 0x04,
            'Recall Max'             : 0x05,
            'Recall Min'             : 0x06,
            'Step Down and Off'      : 0x07,
            'On and Step Up'         : 0x08,
            'Enable DAP Sequence'    : 0x09,
            'Go To Last Active Level': 0x0A,
            'Scene 0'                : 0x10,
            'Scene 1'                : 0x11,
            'Scene 2'                : 0x12,
            'Scene 3'                : 0x13,
            'Scene 4'                : 0x14,
            'Scene 5'                : 0x15,
            'Scene 6'                : 0x16,
            'Scene 7'                : 0x17,
            'Scene 8'                : 0x18,
            'Scene 9'                : 0x19,
            'Scene 10'               : 0x1A,
            'Scene 11'               : 0x1B,
            'Scene 12'               : 0x1C,
            'Scene 13'               : 0x1D,
            'Scene 14'               : 0x1E,
            'Scene 15'               : 0x1F,
            'Reset'                  : 0x20
        }

        if (qualifier['Address'] in ['Group 0', 'Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5', 
                                     'Group 6', 'Group 7', 'Group 8', 'Group 9', 'Group 10', 'Group 11', 
                                     'Group 12', 'Group 13', 'Group 14', 'Group 15'] or 
                                     0 <= int(qualifier['Address']) <= 63) and value in ValueStateValues:
            
            if 'Group' in qualifier['Address']:
                addr_val = (int(qualifier['Address'][6:]) * 2) + 129
            else:
                addr_val = (int(qualifier['Address']) * 2) + 1

            checksum_val = 0x34 ^ 0x04 ^ 0 ^ 0x03 ^ addr_val ^ ValueStateValues[value]
            ModeCmdString = pack('8B', 0x59, 0x34, 0x04, 0x00, 0x03, addr_val, ValueStateValues[value], checksum_val)
            self.__SetHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMode')

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorValues = {
            '00': 'Event: DALI-Frame was sent',
            '01': 'Event: Response to the sent DALI frame was received',
            '10': 'Event: DALI-Frame was received',
            '11': 'Event: Other events',
        }
        value = '{0:08b}'.format(match.group(1)[0])
        self.Error([ErrorValues[value[0:2]]])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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