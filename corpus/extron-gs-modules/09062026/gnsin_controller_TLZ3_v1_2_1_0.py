from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack
from functools import reduce
from operator import add

class DeviceClass:
    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AllMicsOff': { 'Status': {}},
            'Microphone': {'Parameters': ['Unit ID'], 'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x81\x01\x04\\x3F\x02\x05\xFF'), self.__MatchAllMicsOff, None)
            self.AddMatchString(re.compile(b'\xAA\xAA([\x00-\xFF])(\x32|\x33|\x34)\xFF[\x00-\xFF]{5}'), self.__MatchMicrophone, None)

    def __ConstraintChecker(self, *args):
        try:
            for x in args:
                if not(x['Min'] <= int(x['Value']) <= x['Max']):
                    return False
            return True
        except (ValueError, KeyError):
            return False

    def __MatchAllMicsOff(self, match, tag):

        self.WriteStatus('AllMicsOff', 'True', None)
        
    def SetMicrophone(self, value, qualifier):

        UnitIDStates = {
            'Min': 2,
            'Max': 255
        }
        
        ValueStateValues = {
            'Open':  0x0D,
            'Close': 0x0C
        }
        
        UnitIDStates['Value'] = qualifier['Unit ID']
        if self.__ConstraintChecker(UnitIDStates):
            MicrophoneCmdString = list([0xAA, 0xAA, 0xFB, int(UnitIDStates['Value']),
                                        ValueStateValues[value], 0, 0, 0, 0])
            MicrophoneCmdString.append(reduce(add,MicrophoneCmdString[2:]) & 0xFF)
            MicrophoneCmdString = bytes(MicrophoneCmdString)
            self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophone')

    def __MatchMicrophone(self, match, tag):

        ValueStateValues = {
            b'\x32' : 'Open', #Unit is switched ON by hardware button
            b'\x33' : 'Open', #Unit is switched ON by Control system
            b'\x34' : 'Close' #Unit is switched OFF by hardware button
        }

        unitID = unpack('B', match.group(1))[0]
        value =  ValueStateValues[match.group(2)]
        self.WriteStatus('Microphone', value, {'Unit ID' : str(unitID)})
        
        if value == 'Open':
            self.WriteStatus('AllMicsOff', 'False', None)
        
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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

