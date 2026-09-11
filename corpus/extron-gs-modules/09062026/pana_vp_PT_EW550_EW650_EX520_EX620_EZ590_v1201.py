from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
import binascii
from extronlib.system import ProgramLog



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
        
        self.__maxBufferSize = 2048
        self.__receiveBuffer = b''
        self.__matchStringDict = {}

        self.Models = {
            'PT-EZ590': self.pana_1_2193_A,
            'PT-EW650': self.pana_1_2193_A,
            'PT-EX620': self.pana_1_2193_A,
            'PT-EW550': self.pana_1_2193_B,
            'PT-EX520': self.pana_1_2193_B,
        }

        self.Commands = {
            'ConnectionStatus'  : {'Status': {}},
            'AspectRatio'		: {'Status': {}},
            'AudioMute'		    : {'Status': {}},
            'AVMute'			: {'Status': {}},
            'Freeze'		    : {'Status': {}},
            'Keypad'		    : {'Status': {}},
            'Input'				: {'Status': {}},
            'MenuNavigation'    : {'Status': {}},
            'LampStatus'		: {'Status': {}},
            'LampUsage'			: {'Status': {}},
            'Power'				: {'Status': {}},
            'Shutter'			: {'Status': {}},
            'Volume'	        : {'Status': {}},
            'VolumeStep'	    : {'Status': {}},
        }

        self.md5hash = ''
        self.Security = False
        self._DeviceID = b'AD01'

        if self.ConnectionType == 'Ethernet':
            self.deviceUsername = 'admin1'
            self.devicePassword = 'panasonic'
            self.tag = b'\x0D'
            self.index = 2
        else:
            self.tag = b'\x03'
            self.index = 1

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'NTCONTROL 0\r'), self.__MatchNoAuthentication, None)

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
            print('Device ID must between 1 and 64 or All.')

    def __MatchAuthentication(self, match, tag):
        
        if self.deviceUsername is not None:
            if self.devicePassword is not None:
                rand_num = match.group(1).decode()
                full_str = ''.join([self.deviceUsername, ':', self.devicePassword, ':', rand_num])
                code_hash = hashlib.md5(full_str.encode())
                self.md5hash = binascii.hexlify(code_hash.digest())
                self.Security = True
            else:
                self.MissingCredentialsLog('Password')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def CommandStringBuild(self, command, commandstring):

        if self.ConnectionType == 'Ethernet':
            if self.Security:
                commandstring = b''.join([self.md5hash, b'00', self._DeviceID, b';', commandstring, b'\x0D'])
            else:
                commandstring = b''.join([b'00', self._DeviceID, b';', commandstring, b'\x0D'])
        else:
            commandstring = b''.join([b'\x02', self._DeviceID, b';', commandstring, b'\x03'])
        return commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Normal': '1',
            'Wide': '2',
            'Native': '5',
            'Full': '6',
            'H Fit': '9',
            'V Fit': '10'
        }

        AspectRatioCmdString = b''.join([b'VSE:', ValueStateValues[value].encode()])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Normal',
            '2': 'Wide',
            '5': 'Native',
            '6': 'Full',
            '9': 'H Fit',
            '10': 'V Fit'
        }

        AspectRatioCmdString = b'QS1'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = b''.join([b'AMT:', ValueStateValues[value].encode()])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = b'QMT'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAVMute')

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = b''.join([b'OSH:', ValueStateValues[value].encode()])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AVMuteCmdString = b'QSH'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAVMute')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = b''.join([b'OFZ:', ValueStateValues[value].encode()])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = b'QFZ'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAVMute')
    
    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = b''.join([b'ONK:', str(value).encode()])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Stand-by',
            '1': 'Lamp On (Control Active)',
            '2': 'Lamp On',
            '3': 'Lamp Off (Control Active)'
        }

        StatusCmdString = b'Q$S'
        res = self.__UpdateHelper('LampStatus', StatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampStatus')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'   : 'MN',
            'Return' : 'BK',
            'Enter'  : 'EN',
            'Up'     : 'CU',
            'Down'   : 'CD',
            'Left'   : 'CL',
            'Right'  : 'CR'
        }
        MenuNavigationCmdString = b''.join([b'O',  ValueStateValues[value].encode()])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = b''.join([b'IIS:', self.InputValues[value].encode()])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'QIN'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputStates[res[self.index:-1].decode()]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected command for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'Q$L'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[self.index:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = ValueStateValues[value].encode()
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '001': 'On',
            '000': 'Off'
        }

        PowerCmdString = b'QPW'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShutterCmdString = b''.join([b'OSH:', ValueStateValues[value].encode()])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ShutterCmdString = b'QSH'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateShutter')

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 63
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolValue = '{0:03d}'.format(value)
            VolumeCmdString = b''.join([b'AVL', VolValue.encode()])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'QAV'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[self.index:-1].decode())
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 'U',
            'Down' : 'D'
        }

        VolumeStepCmdString = b''.join([b'AU', ValueStateValues[value].encode()])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if self.ConnectionType == 'Ethernet':
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

        if response in DEVICE_ERROR_CODES.keys():
            print('{0} ERROR: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = self.CommandStringBuild(command, commandstring)
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.tag)
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
            
        commandstring = self.CommandStringBuild(command, commandstring)
        if self.Unidirectional == 'True' or self._DeviceID == b'ADZZ':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.tag)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.md5hash = ''
        self.Security = False

    def pana_1_2193_A(self):

        self.InputValues = {
            'Video'  		: 'VID',
            'RGB 1'  		: 'RG1',
            'RGB 2'  		: 'RG2',
            'HDMI 1' 		: 'HD1',
            'HDMI 2' 		: 'HD2',
            'Digital Link' 	: 'DL1',
            'Network' 		: 'NWP'
        }

        self.UpdateInputStates = {
            'VID': 'Video',
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'DL1': 'Digital Link',
            'NWP': 'Network'
        }

    def pana_1_2193_B(self):

        self.InputValues = {
            'Video'  		: 'VID',
            'RGB 1'  		: 'RG1',
            'RGB 2'  		: 'RG2',
            'HDMI 1' 		: 'HD1',
            'HDMI 2' 		: 'HD2',
            'Network' 		: 'NWP'
        }

        self.UpdateInputStates = {
            'VID': 'Video',
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'NWP': 'Network'
        }
    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    
    # Send Control Commands
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
            
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

