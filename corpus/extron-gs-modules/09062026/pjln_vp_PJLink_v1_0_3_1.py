from extronlib.interface import EthernetClientInterface
from extronlib.system import ProgramLog
import hashlib
from binascii import hexlify
from re import compile, search, findall

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
        self.devicePassword = None
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters': ['Type'], 'Status': {}},
            'ErrorStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampHour': {'Parameters': ['Lamp'], 'Status': {}},
            'Power': {'Status': {}},
            'Resolution': {'Parameters': ['Type'], 'Status': {}},
            'Volume': {'Parameters': ['Device'], 'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None)
            self.UpdateAVMuteMatch = compile('%1AVMT=([1-3][0-1])\r')
            self.UpdateErrorStatus = compile('%1ERST=([0-3]{6})\r')
            self.SetInputMatch = compile('(RGB|Video|Digital|Storage|Network) ([1-9])')
            self.UpdateInputMatch = compile('%1INPT=([1-5])([1-9])\r')
            self.UpdateLampHourMatch = compile('([0-9]{1,5}) [0-1]')
            self.UpdatePowerMatch = compile('%1POWR=([0-3])\r')
            self.ErrorMatchString = compile('ERR([1-4]|A)')

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        AVMuteQualifierValues = {
            'Audio': '2',
            'Video': '1',
            'Audio Video': '3'
        }
        AVMuteCmdString = '%1AVMT {0}{1}\r'.format(AVMuteQualifierValues[qualifier['Type']], AVMuteStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            '11': {'Audio': 'Off', 'Video': 'On', 'Audio Video': 'Off'},
            '21': {'Audio': 'On', 'Video': 'Off', 'Audio Video': 'Off'},
            '31': {'Audio': 'On', 'Video': 'On', 'Audio Video': 'On'},
            '30': {'Audio': 'Off', 'Video': 'Off', 'Audio Video': 'Off'}
        }
        AVMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                matchObject = search(self.UpdateAVMuteMatch, res)
                if matchObject:
                    AVMuteValues = AVMuteStateNames[matchObject.group(1)]
                    for Type in ['Audio', 'Video', 'Audio Video']:
                        qualifier = {'Type': Type}
                        value = AVMuteValues[Type]
                        self.WriteStatus('AVMute', value, qualifier)
            except KeyError:
                self.Error(['AV Mute: Invalid/unexpected response'])

    def UpdateErrorStatus(self, value, qualifier):

        ErrorWarningNames = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            4: 'Cover',
            5: 'Filter',
            6: 'Other'
        }
        ErrorStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)
        if res:
            try:
                matchObject = search(self.UpdateErrorStatus, res)
                if matchObject:
                    ErrorStrings = matchObject.group(1)
                    if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                        value = 'Normal'
                    elif ErrorStrings.count('1') + ErrorStrings.count('2') > 2:
                        value = 'Multiple Errors/Warnings'
                    elif ErrorStrings.count('1') == 1:
                        index = ErrorStrings.index('1')
                        value = '{0} Warning'.format(ErrorWarningNames[index + 1])
                    elif ErrorStrings.count('2') == 1:
                        index = ErrorStrings.index('2')
                        value = '{0} Error'.format(ErrorWarningNames[index + 1])
                    self.WriteStatus('ErrorStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Error Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '%2FILT ?\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '%2FREZ 1\r',
            'Off': '%2FREZ 0\r'
        }
        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        FreezeCmdString = '%2FREZ ?\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'RGB': '1',
            'Video': '2',
            'Digital': '3',
            'Storage': '4',
            'Network': '5'
        }
        matchObject = search(self.SetInputMatch, value)
        InputCmdString = '%1INPT {0}{1}\r'.format(InputStateValues[matchObject.group(1)], matchObject.group(2))
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            '1': 'RGB',
            '2': 'Video',
            '3': 'Digital',
            '4': 'Storage',
            '5': 'Network'
        }
        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = search(self.UpdateInputMatch, res)
                if matchObject:
                    value = '{0} {1}'.format(InputStateNames[matchObject.group(1)], matchObject.group(2))
                    self.WriteStatus('Input', value, None)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampHour(self, value, qualifier):

        LampHourCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampHour', LampHourCmdString, value, qualifier)
        if res:
            try:
                matchList = findall(self.UpdateLampHourMatch, res)
                if matchList:
                    for lampnumber, lampusage in enumerate(matchList, 1):
                        qualifier = {'Lamp': str(lampnumber)}
                        value = int(lampusage)
                        self.WriteStatus('LampHour', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Hour: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '1',
            'Off': '0'
        }
        PowerCmdString = '%1POWR {0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warm Up',
            '2': 'Cooling'
        }
        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = search(self.UpdatePowerMatch, res)
                if matchObject:
                    value = PowerStateNames[matchObject.group(1)]
                    self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateResolution(self, value, qualifier):

        TypeStates = {
            'Actual': '%2IRES ?\r',
            'Recommended': '%2RRES ?\r',
        }
        Type = qualifier['Type']
        if Type in TypeStates:
            ResolutionCmdString = TypeStates[Type]
            res = self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)
            if res:
                try:
                    value = res[7:-1]
                    self.WriteStatus('Resolution', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Resolution: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateResolution')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            inStr = match.group(1).decode()
            outStr = inStr + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest()) + b'\x251POWR ?\r'
            self.Authenticated = 'Admin'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetVolume(self, value, qualifier):

        DeviceStates = {
            'Speaker': 'S',
            'Microphone': 'M'
        }
        ValueStateValues = {
            'Up': '%2{}VOL 1\r',
            'Down': '%2{}VOL 0\r'
        }
        Device = qualifier['Device']
        if Device in DeviceStates:
            VolumeCmdString = ValueStateValues[value].format(DeviceStates[Device])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            MatchObject = search(self.ErrorMatchString, response)
            if MatchObject:
                MatchNames = {
                    '1': 'Undefined Command',
                    '2': 'Out of Parameter',
                    '3': 'Unavailable Time',
                    '4': 'Projector Failure',
                    'A': 'Invalid Password'
                }
                self.Error(['Error = {0}; Command = {1}'.format(MatchNames[MatchObject.group(1)], sourceCmdName)])
                if 'ERRA' in response:
                    self.Authenticated = 'None'
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
        if isinstance(res, bytes):
            res = res.decode()
        res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated == 'None':
            self.Discard('Inappropriate Command ' + command)
            return ''
        elif self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
                result = search(regexString, self._ReceiveBuffer)
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

