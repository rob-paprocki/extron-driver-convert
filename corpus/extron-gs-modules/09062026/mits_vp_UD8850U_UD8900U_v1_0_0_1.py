from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from re import search
import hashlib
from binascii import hexlify

class DeviceClass():
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
        self._DeviceID = ';0A;'
        self.devicePassword = 'admin'

        self.Models = {
            'UD8850U': self.mits_1_1261_UD885,
            'UD8900U': self.mits_1_1261_UD890,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio'       : {'Status': {}},
            'ClosedCaption'     : {'Status': {}},
            'DeviceStatus'      : {'Status': {}},
            'FilterTime'        : {'Status': {}},
            'Freeze'            : {'Status': {}},
            'Input'             : {'Status': {}},
            'LampMode'          : {'Status': {}},
            'LampSelect'        : {'Status': {}},
            'LampTime'          : {'Parameters':['Lamp'], 'Status': {}},
            'MenuNavigation'    : {'Status': {}},
            'Power'             : {'Status': {}},
            'VideoMute'         : {'Status': {}}
            }

        self.Authenticated = 'Not Needed'
        self.Certification = 'Not Received'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(SC)([0-4]{0,1})\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(CC)([0-2])\r'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(vER)([0-9A-F]{3})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(vFLTT)([0-9]{5})\r'), self.__MatchFilterTime, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(FRZ)([0-1])\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(vI)([r|v|d][1|2]{0,1})\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(LM)([0-1])\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(LS)([0-3])\r'), self.__MatchLampSelect, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(vLE)([1-2])L([0-9]{4}[0-5][0-9])\r'), self.__MatchLampTime, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(vST)([0-6])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'00(;[0-6][0-9A-Z];){0,1}(MUTE)([0-1])\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(00.*):N\r|(PRV=ERRA)\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value:
            if value == 'All':
                self._DeviceID = ''
            elif 'A' <= value <= 'Z':
                self._DeviceID = ';0{0};'.format(value)
            elif 0 <= int(value) <= 64:
                self._DeviceID = ';{0};'.format(value.zfill(2))
            else:
                self.Discard('Invalid ID')
        else:
            self._DeviceID = ''
        
    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Normal' : '0', 
            '16:9'   : '1', 
            'Native' : '2', 
            'Full'   : '3', 
            'User'   : '4'
        }

        AspectRatioCmdString = '00{0}SC{1}\r'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = '00{0}SC\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            '0' : 'Normal', 
            '1' : '16:9', 
            '2' : 'Native', 
            '3' : 'Full', 
            '4' : 'User'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetClosedCaption(self, value, qualifier):
        ValueStateValues = {
            'CC1' : '1', 
            'CC2' : '2', 
            'Off' : '0'
        }

        ClosedCaptionCmdString = '00{0}CC{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        ClosedCaptionCmdString = '00{0}CC\r'.format(self._DeviceID)
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):
        ValueStateValues = {
            '1' : 'CC1', 
            '2' : 'CC2', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):
        DeviceStatusCmdString = '00{0}vER\r'.format(self._DeviceID)
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):
        ValueStateValues = {
            '000' : 'Normal', 
            '800' : 'Fan Error', 
            '400' : 'Lamp Error', 
            '200' : 'Lamp Life Expired', 
            '100' : 'Lamp Life Expiring', 
            '080' : 'Temp Error', 
            '040' : 'Temp Warning', 
            '020' : 'Lamp Cover Error', 
            '010' : 'Filter Cover Error', 
            '008' : 'Component Abnormality', 
        }
        try:
            value = ValueStateValues[match.group(3).decode()]
        except KeyError:
            value = 'Multiple Errors'
        self.WriteStatus('DeviceStatus', value, None)

    def UpdateFilterTime(self, value, qualifier):
        FilterTimeCmdString = '00{0}vFLTT\r'.format(self._DeviceID)
        self.__UpdateHelper('FilterTime', FilterTimeCmdString, value, qualifier)

    def __MatchFilterTime(self, match, tag):
        value = int(match.group(3).decode())
        self.WriteStatus('FilterTime', value, None)

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        FreezeCmdString = '00{0}FRZ{1}\r'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        FreezeCmdString = '00{0}FRZ\r'.format(self._DeviceID)
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):
        
        InputCmdString = '00{0}_{1}\r'.format(self._DeviceID,self.InputStatesValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputCmdString = '00{0}vI\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        
        value = self.InputStatesNames[match.group(3).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):
        ValueStateValues = {
            'Standard' : '0', 
            'Low'      : '1'
        }

        LampModeCmdString = '00{0}LM{1}\r'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeCmdString = '00{0}LM\r'.format(self._DeviceID)
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        ValueStateValues = {
            '0' : 'Standard', 
            '1' : 'Low'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetLampSelect(self, value, qualifier):
        ValueStateValues = {
            'Dual'   : '0', 
            'Single' : '1', 
            'Lamp 1' : '2', 
            'Lamp 2' : '3'
        }

        LampSelectCmdString = '00{0}LS{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):
        LampSelectCmdString = '00{0}LS\r'.format(self._DeviceID)
        self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def __MatchLampSelect(self, match, tag):
        ValueStateValues = {
            '0' : 'Dual', 
            '1' : 'Single', 
            '2' : 'Lamp 1', 
            '3' : 'Lamp 2'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('LampSelect', value, None)

    def UpdateLampTime(self, value, qualifier):
        LampNumber = int(qualifier['Lamp'])
        if(LampNumber in (1,2)):
            LampTimeCmdString = '00{0}vLE{1}L\r'.format(self._DeviceID, LampNumber)
        self.__UpdateHelper('LampTime', LampTimeCmdString, value, qualifier)

    def __MatchLampTime(self, match, tag):
        LampNumber = match.group(3).decode()
        value = match.group(4).decode()
        qualifier = {'Lamp':str(LampNumber)}
        value = value[:4]
        self.WriteStatus('LampTime', int(value), qualifier)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Left'  : '4f', 
            'Right' : '59', 
            'Up'    : '53', 
            'Down'  : '2b', 
            'Menu'  : '54', 
            'Enter' : '10'
        }

        MenuNavigationCmdString = '00{0}r{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On'  : '!', 
            'Off' : '"', 
        }

        PowerCmdString = '00{0}{1}\r'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)

    def UpdatePower(self, value, qualifier):
        if 'Serial' not in self.ConnectionType and self.Certification == 'Not Received':
            self.UpdatePassword()
        else:
            PowerCmdString = '00{0}vST\r'.format(self._DeviceID)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '2' : 'On', 
            '0' : 'Off', 
            '1' : 'Warming', 
            '3' : 'Cooling',
            '4' : 'Off',
            '5' : 'On',
            '6' : 'On'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Power', value, None)
        if match.group(3).decode() == '6':
            value = 'Awaiting Password Entry'
            self.WriteDeviceStatus(value, None, 'live')

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        VideoMuteCmdString = '00{0}MUTE{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 3)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = '00{0}MUTE\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('VideoMute', value, None)
    
    def UpdatePassword(self):
        res = self.SendAndWait('$AK\r', self.DefaultResponseTimeout, deliTag=b'\r')
        if res:
            MatchString = re.compile(b'\$AK(.{8})\r')
            MatchObject = re.search(MatchString, res)
            if MatchObject is not None:
                inStr = MatchObject.group(1)
                outStr = inStr.decode() + self.devicePassword
                m = hashlib.md5(outStr.encode())
                cmdString = hexlify(m.digest()) + b'00' + self._DeviceID.encode() + b'vST\r'
                self.Authenticated = 'Admin'
                self.Certification = 'Received'
                self.Send(cmdString)
            else:
                self.Certification = 'None'

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True' or self._DeviceID == '':
                print('Inappropriate Command ', command)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        if match.group(1).decode() == 'PRV=ERRA':
            print('Error in the certification data')
            self.Authenticated = 'None'
            self.Certification = 'Not Received'
        else:
            command = match.group(1).decode()
            self.Error(['Error executing command: {0}'.format(command)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Certification = 'Not Received'

    def mits_1_1261_UD885(self):
        self.InputStatesValues = {
            'Computer 1' : 'r1',
            'Computer 2' : 'r2',
            'HDMI'       : 'd1',
            'DVI'        : 'd2',
            'Video'      : 'v1',
            'S-Video'    : 'v2'
        }
        self.InputStatesNames = {
            'r1' : 'Computer 1',
            'r2' : 'Computer 2',
            'd1' : 'HDMI',
            'd2' : 'DVI',
            'v1' : 'Video',
            'v2' : 'S-Video'
        }

    def mits_1_1261_UD890(self):
        self.InputStatesValues = {
            'Computer 1' : 'r1',
            'Computer 2' : 'r2',
            'HDMI'       : 'd1',
            'DVI'        : 'd2',
            'SDI'        : 'd3',
            'Video'      : 'v1',
            'S-Video'    : 'v2'
        }
        self.InputStatesNames = {
            'r1' : 'Computer 1',
            'r2' : 'Computer 2',
            'd1' : 'HDMI',
            'd2' : 'DVI',
            'd3' : 'SDI',
            'v1' : 'Video',
            'v2' : 'S-Video'
        }
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