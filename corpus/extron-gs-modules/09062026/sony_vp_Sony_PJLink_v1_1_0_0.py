from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import hashlib
from binascii import hexlify
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters': ['Type'], 'Status': {}},
            'ErrorStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            }

        self.Authenticated = 'Not Needed'        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%1AVMT=(11|21|31|30)\r'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'%1ERST=(0|1|2)(0|1|2)(0|1|2)(0|1|2)(0|1|2)(0|1|2)\r'), self.__MatchErrorStatus, None)
            self.AddMatchString(re.compile(b'%1INPT=(21|22|31|32|33|34|35|36|41|51)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'%1LAMP=(\d{1,4})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'%1POWR=(0|1|2|3)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ERR(1|2|3|4|A)\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        inStr = match.group(1).decode()
        outStr = inStr + self.Password
        m = hashlib.md5(outStr.encode())
        self.PasswordString = hexlify(m.digest()) + b'\x251POWR ?\r'
        self.Authenticated = 'Admin'
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAVMute(self, value, qualifier):

        Value = {
            'On': '1',
            'Off': '0'
        }[value]

        Type = {
            'Audio': '2',
            'Video': '1',
            'Audio Video': '3'
        }[qualifier['Type']]

        CmdString = '%1AVMT {0}{1}\r'.format(Type, Value)
        self.__SetHelper('AVMute', CmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):
        self.__UpdateHelper('AVMute', '%1AVMT ?\r', value, qualifier)

    def __MatchAVMute(self, match, tag):

        Value = match.group(1).decode()
        if Value == '11':
            self.WriteStatus('AVMute', 'Off', {'Type': 'Audio'})
            self.WriteStatus('AVMute', 'On', {'Type': 'Video'})
            self.WriteStatus('AVMute', 'Off', {'Type': 'Audio Video'})
        elif Value == '21':
            self.WriteStatus('AVMute', 'On', {'Type': 'Audio'})
            self.WriteStatus('AVMute', 'Off', {'Type': 'Video'})
            self.WriteStatus('AVMute', 'Off', {'Type': 'Audio Video'})
        elif Value == '30':
            self.WriteStatus('AVMute', 'Off', {'Type': 'Audio'})
            self.WriteStatus('AVMute', 'Off', {'Type': 'Video'})
            self.WriteStatus('AVMute', 'Off', {'Type': 'Audio Video'})
        elif Value == '31':
            self.WriteStatus('AVMute', 'On', {'Type': 'Audio'})
            self.WriteStatus('AVMute', 'On', {'Type': 'Video'})
            self.WriteStatus('AVMute', 'On', {'Type': 'Audio Video'})

    def UpdateErrorStatus(self, value, qualifier):
        self.__UpdateHelper('ErrorStatus', '%1ERST ?\r', value, qualifier)

    def __MatchErrorStatus(self, match, tag):

        ErrorWarningNames = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            4: 'Cover',
            5: 'Filter',
            6: 'Other'
        }

        FanErr = match.group(1).decode()
        LampErr = match.group(2).decode()
        TempErr = match.group(3).decode()
        CoverErr = match.group(4).decode()
        FilterErr = match.group(5).decode()
        OtherErr = match.group(6).decode()

        Errors = [FanErr, LampErr, TempErr, CoverErr, FilterErr, OtherErr]

        if Errors.count('0') == 6:
            self.WriteStatus('ErrorStatus', 'Normal', None)
        elif Errors.count('0') <= 4:
            self.WriteStatus('ErrorStatus', 'Multiple Errors/Warnings', None)
        elif Errors.count('1') == 1:
            index = Errors.index('1')
            value = '{0} Warning'.format(ErrorWarningNames[index + 1])
            self.WriteStatus('ErrorStatus', value, None)
        elif Errors.count('2') == 1:
            index = Errors.index('2')
            value = '{0} Error'.format(ErrorWarningNames[index + 1])
            self.WriteStatus('ErrorStatus', value, None)

    def SetInput(self, value, qualifier):

        Value = {
            'Video': '%1INPT 21\r',
            'S-Video': '%1INPT 22\r',
            'Input A': '%1INPT 31\r',
            'Input B': '%1INPT 32\r',
            'Input C': '%1INPT 33\r',
            'Input D': '%1INPT 34\r',
            'Input E': '%1INPT 35\r',
            'Input F': '%1INPT 36\r',
            'USB': '%1INPT 41\r',
            'Network': '%1INPT 51\r'
        }[value]

        self.__SetHelper('Input', Value, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '%1INPT ?\r', value, qualifier)

    def __MatchInput(self, match, tag):

        Values = {
            '21': 'Video',
            '22': 'S-Video',
            '31': 'Input A',
            '32': 'Input B',
            '33': 'Input C',
            '34': 'Input D',
            '35': 'Input E',
            '36': 'Input F',
            '41': 'USB',
            '51': 'Network'
        }[match.group(1).decode()]

        self.WriteStatus('Input', Values, None)

    def UpdateLampUsage(self, value, qualifier):

        self.__UpdateHelper('LampUsage', '%1LAMP ?\r', value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetPower(self, value, qualifier):

        Value = {
            'On': '%1POWR 1\r',
            'Off': '%1POWR 0\r',
        }[value]

        self.__SetHelper('Power', Value, value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '%1POWR ?\r', value, qualifier)

    def __MatchPower(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warming Up',
            '2': 'Cooling Down'
        }[match.group(1).decode()]

        self.WriteStatus('Power', Values, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Authenticated not in ['Admin', 'Not Needed']:
            print('Inappropriate Command ', command)
        elif self.Unidirectional == 'True':
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

        Errors = {
            '1': 'Undefined Command',
            '2': 'Out of Parameter',
            '3': 'Unavailable Time',
            '4': 'Projector Failure',
            'A': 'Invalid Password'
        }   [match.group(1).decode()]

        if match.group(1).decode() == 'A':
            self.Authenticated = 'None'

        print('Error = {0}', Errors)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'Not Needed'      
    
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