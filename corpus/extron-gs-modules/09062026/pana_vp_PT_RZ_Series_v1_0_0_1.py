from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import binascii
import hashlib

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = '01'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'SubMemory': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ZZ'
        elif 'Group' in value:
            self._DeviceID = value.split()[1].zfill(2)
        elif 1 <= int(value) <= 64:
            self._DeviceID = '{:02d}'.format(int(value))
        else:
            initError.append('Invalid Device ID Parameter.')       

    def construct_command(self, command, value=''):

        if value:
            return '\x02AD{};{}:{}\x03'.format(self._DeviceID, command, value)
        return '\x02AD{};{}\x03'.format(self._DeviceID, command)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'AUTO'   : '0',
            '4:3'    : '1',
            '16:9'   : '2',
            'THROUGH': '5',
            'HV FIT' : '6',
            'H FIT'  : '9',
            'V FIT'  : '10'
        }

        AspectRatioCmdString = self.construct_command('VSE', ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0' : 'AUTO',
            '1' : '4:3',
            '2' : '16:9',
            '5' : 'THROUGH',
            '6' : 'HV FIT',
            '9' : 'H FIT',
            '10': 'V FIT'
        }

        AspectRatioCmdString = self.construct_command('QSE')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1'       : 'RG1',
            'RGB 2'       : 'RG2',
            'DVI-D'       : 'DVI',
            'HDMI'        : 'HD1',
            'DIGITAL LINK': 'DL1',
            'SDI'         : 'SD1'
        }

        InputCmdString = self.construct_command('IIS', ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'PON',
            'Off': 'POF'
        }

        PowerCmdString = self.construct_command(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = self.construct_command('QPW')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open' : '0', 
            'Close': '1'
        }

        ShutterCmdString = self.construct_command('OSH', ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        ShutterCmdString = self.construct_command('QSH')
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetSubMemory(self, value, qualifier):

        if 1 <= int(value) <= 96:
            SubMemoryCmdString = self.construct_command('OCS', value.zfill(2))
            self.__SetHelper('SubMemory', SubMemoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSubMemory')

    def UpdateSubMemory(self, value, qualifier):

        SubMemoryCmdString = self.construct_command('QSB')
        res = self.__UpdateHelper('SubMemory', SubMemoryCmdString, value, qualifier)
        if res:
            try:
                value = str(int(res[1:-1]))
                self.WriteStatus('SubMemory', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Sub Memory: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            '\x02ER401\x03': 'Invalid command',
            '\x02ER402\x03': 'Invalid parameter'
        }

        if response in error_map:
            self.Error(
                ['An error occurred: {command}: {error}.'.format(command=sourceCmdName, error=error_map[response])])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())            

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
class DeviceEthernetClass:
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
        self.deviceUsername = None
        self.devicePassword = '@Panasonic'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': {'Parameters':['Lamp'], 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
        }
        self.__authenticated = False
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchAuthentication, False)
            self.AddMatchString(re.compile(b'%1ERST=([012]{6})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'%2FREZ=([01])\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'%1INPT=(11|12|31|32|33|34)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'%1LAMP=(\d{4}) ([01]) (\d{4}) ([01])\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'%1POWR=([012])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'%1AVMT=3([01])\r'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'ERR[1-4]\r|PJLINK ERRA\r'), self.__MatchError, None)    

    def __MatchAuthentication(self, match, tag):
        if tag:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.md5hash = binascii.hexlify(code_hash.digest()).decode()
            self.Send(self.md5hash + '%1POWR ?\r')
        else:
            self.md5hash = ''
            self.__authenticated = True

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = self.md5hash + '%1ERST ?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '000000': 'Normal',
            '100000': 'Fan Warning',
            '200000': 'Fan Error',
            '010000': 'Lamp Warning',
            '020000': 'Lamp Error',
            '001000': 'Temperature Warning',
            '002000': 'Temperature Error',
            '000010': 'Filter Warning',
            '000020': 'Filter Error',
            '000001': 'Other Warning',
            '000002': 'Other Error'
        }

        value = ValueStateValues.get(match.group(1).decode(), 'Multiple Warnings/Errors')
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }

        FreezeCmdString = self.md5hash + '%2FREZ {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = self.md5hash + '%2FREZ ?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1'       : '11',
            'RGB 2'       : '12',
            'DVI-D'       : '31',
            'HDMI'        : '32',
            'DIGITAL LINK': '33',
            'SDI'         : '34'
        }

        InputCmdString = self.md5hash + '%1INPT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.md5hash + '%1INPT ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '11': 'RGB 1',
            '12': 'RGB 2',
            '31': 'DVI-D',
            '32': 'HDMI',
            '33': 'DIGITAL LINK',
            '34': 'SDI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampMode(self, value, qualifier):
       
        LampModeCmdString = self.md5hash + '%1LAMP ?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)        

    def __MatchLampMode(self, match, tag):

        lamp1_usage = int(match.group(1).decode())
        self.WriteStatus('LampUsage', lamp1_usage, {'Lamp': '1'})

        lamp1_mode = 'On' if match.group(2).decode() == '1' else 'Off'
        self.WriteStatus('LampMode', lamp1_mode, {'Lamp': '1'})

        lamp2_usage = int(match.group(3).decode())
        self.WriteStatus('LampUsage', lamp2_usage, {'Lamp': '2'})

        lamp2_mode = 'On' if match.group(4).decode() == '1' else 'Off'
        self.WriteStatus('LampMode', lamp2_mode, {'Lamp': '2'})

    def UpdateLampUsage(self, value, qualifier):

        self.UpdateLampMode(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        PowerCmdString = self.md5hash + '%1POWR {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.md5hash + '%1POWR ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        if not self.__authenticated:
            self.__authenticated = True

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Cooling Down'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open' : '30',
            'Close': '31'
        }

        ShutterCmdString = self.md5hash + '%1AVMT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = self.md5hash + '%1AVMT ?\r'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        if self.__authenticated:
            self.Send(commandstring)
        else:
            self.Discard('Not Authenticated')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.__authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
        else:
            self.Discard('Not Authenticated')

    def __MatchError(self, match, tag):
        self.counter = 0
        err = match.group(0).decode().strip()
        if err == 'PJLINK ERRA':
            self.Error(['Log in failed. Please supply proper password.'])
            self.__authenticated = False
            return

        error_map = {
            'ERR1': 'Undefined command',
            'ERR2': 'Out of parameter',
            'ERR3': 'Unavailable time',
            'ERR4': 'Projector failure'
        }

        self.Error(['An error occurred: {}: {}'.format(err, error_map[err])])

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}    def MissingCredentialsLog(self, credential_type):
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
class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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