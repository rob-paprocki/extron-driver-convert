from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from hashlib import md5
from binascii import hexlify

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
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.md5hash = ''
        self.Security = False

        if 'Serial' not in self.ConnectionType:
            self.tag = b'\x0D'
            self.index = 2
        else:
            self.tag = b'\x03'
            self.index = 1

        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
                self.AddMatchString(compile(b'NTCONTROL 0\r'), self.__MatchNoAuthentication, None)
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'All':
            self._DeviceID = b'ADZZ'
        elif 1 <= int(value) <= 64:
            self._DeviceID = b''.join([b'AD', value.zfill(2).encode()])
        else:
            self.Error(['Device ID Out of Range'])

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = ':'.join([self.deviceUsername, self.devicePassword, rand_num])
        code_hash = md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def command_string_build(self, command_string):
        if 'Serial' not in self.ConnectionType:
            if self.Security:
                command_string = b''.join([self.md5hash, b'00', self.DeviceID, b';', command_string, b'\x0D'])
            else:
                command_string = b''.join([b'00', self.DeviceID, b';', command_string, b'\x0D'])
        else:
            command_string = b''.join([b'\x02', self.DeviceID, b';', command_string, b'\x03'])
        return command_string

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto':   '0',
            'Normal': '1', 
            'Wide':   '2', 
            'Native': '5', 
            'Full':   '6',
            'H Fit':  '9',
            'V Fit':  '10',
        }

        AspectRatioCmdString = b''.join([b'VSE:', ValueStateValues[value].encode()])
        AspectRatioCmdString = self.command_string_build(AspectRatioCmdString)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0':  'Auto',
            '1':  'Normal',
            '2':  'Wide',
            '5':  'Native',
            '6':  'Full',
            '9':  'H Fit',
            '10': 'V Fit',
        }

        AspectRatioCmdString = b'QS1'
        AspectRatioCmdString = self.command_string_build(AspectRatioCmdString)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        AudioMuteCmdString = b''.join([b'AMT:', ValueStateValues[value].encode()])
        AudioMuteCmdString = self.command_string_build(AudioMuteCmdString)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        AudioMuteCmdString = b'QMT'
        AudioMuteCmdString = self.command_string_build(AudioMuteCmdString)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        AVMuteCmdString = b''.join([b'OSH:', ValueStateValues[value].encode()])
        AVMuteCmdString = self.command_string_build(AVMuteCmdString)
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        AVMuteCmdString = b'QSH'
        AVMuteCmdString = self.command_string_build(AVMuteCmdString)
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        FreezeCmdString = b''.join([b'OFZ:', ValueStateValues[value].encode()])
        FreezeCmdString = self.command_string_build(FreezeCmdString)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        FreezeCmdString = b'QFZ'
        FreezeCmdString = self.command_string_build(FreezeCmdString)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video':   'VID',
            'RGB 1':   'RG1',
            'RGB 2':   'RG2',
            'HDMI 1':  'HD1',
            'HDMI 2':  'HD2',
            'Network': 'NWP',
        }

        InputCmdString = b''.join([b'IIS:', ValueStateValues[value].encode()])
        InputCmdString = self.command_string_build(InputCmdString)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'VID': 'Video',
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'NWP': 'Network',
        }

        InputCmdString = b'QIN'
        InputCmdString = self.command_string_build(InputCmdString)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = tuple(str(x) for x in range(10))

        if value in ValueStateValues:
            KeypadCmdString = b''.join([b'ONK:', value.encode()])
            KeypadCmdString = self.command_string_build(KeypadCmdString)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')
    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'Q$L'
        LampUsageCmdString = self.command_string_build(LampUsageCmdString)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[self.index:-1])
                if 1 <= value <= 99999:
                    self.WriteStatus('LampUsage', value, qualifier)
                else:
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':   'MN',
            'Return': 'BK',
            'Enter':  'EN',
            'Up':     'CU',
            'Down':   'CD',
            'Left':   'CL',
            'Right':  'CR',
        }

        MenuNavigationCmdString = b''.join([b'O', ValueStateValues[value].encode()])
        MenuNavigationCmdString = self.command_string_build(MenuNavigationCmdString)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  'PON',
            'Off': 'POF',
        }

        PowerCmdString = ValueStateValues[value].encode()
        PowerCmdString = self.command_string_build(PowerCmdString)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '001': 'On',
            '000': 'Off',
        }

        PowerCmdString = b'QPW'
        PowerCmdString = self.command_string_build(PowerCmdString)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up':   'U',
            'Down': 'D',
        }

        VolumeCmdString = b''.join([b'AU', ValueStateValues[value].encode()])
        VolumeCmdString = self.command_string_build(VolumeCmdString)
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Serial' not in self.ConnectionType:
            DEVICE_ERROR_CODES = {
                b'00ERR1\x0D': 'Undefined Control Command.',
                b'00ERR2\x0D': 'Out of Parameter Range.',
                b'00ERR3\x0D': 'Busy State or No-acceptable Period.',
                b'00ERR4\x0D': 'Timeout or No-acceptable Period.',
                b'00ERR5\x0D': 'Wrong Data Length.',
                b'00ERRA\x0D': 'Password Mismatch.',
            }
        else:
            DEVICE_ERROR_CODES = {
                b'\x02ER402\x03': 'Inappropriate Command.',
                b'\x02ER401\x03': 'Invalid Command Reply.'
            }

        if response:
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or self.DeviceID == b'ADZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.tag)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == b'ADZZ':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.tag)
            return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.md5hash = ''
            self.Security = False
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
                result = search(regexString, self._ReceiveBuffer)
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

