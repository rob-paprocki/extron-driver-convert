from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import hashlib
import binascii

class DeviceClass:
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
        self.devicePassword = None
        self.Models = {
            'ZRCT-100': self.sony_20_3593_100,
            'ZRCT-200': self.sony_20_3593_200,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'DynamicRange': {'Parameters':['Input'], 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
        }
        
        self.sha256hash = ''
        self.StartQuery = True
        
        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
            self.AddMatchString(re.compile(b'([a-zA-Z0-9]{8})\r\n'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'NOKEY\r\n'), self.__MatchNoAuthentication, None)

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\"(no_err)\"|\"err_(controller|u[0-9]{4})_([\w]+)\"'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\"(dvi1_2_3_4]|dp1|dp1_2|hdmi1|hdmi2)\"\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\"(on|standby|updating|startup|shutting_down|initializing)\"\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'err_(cmd|option|inactive|val|auth|internal1|internal2)\r\n'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        if self.devicePassword is None:
            self.MissingCredentialsLog('Password')
        else:
            self.StartQuery = True
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.sha256(full_str.encode())
            self.sha256hash = binascii.hexlify(code_hash.digest()).decode()
            self.SetAuthentication( None, None)

    def SetAuthentication(self, value, qualifier):
        self.Send(self.sha256hash + '\r\n')

    def __MatchNoAuthentication(self, match, tag):
        self.StartQuery = True

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'error ?\r\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        if match.group(1):
            value = self.DeviceStates[match.group(1).decode()]
        else:
            value = self.DeviceStates[match.group(3).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetDynamicRange(self, value, qualifier):


        InputStates = {
            'DisplayPort 1'  : 'dp1',
            'DisplayPort 2'  : 'dp1_2',
            'HDMI 1'         : 'hdmi1',
            'HDMI 2'         : 'hdmi2'
        }

        ValueStateValues = {
            'Auto'   : 'auto',
            'Limited': 'limited',
            'Full'   : 'full'
        }

        if qualifier['Input'] in InputStates:
            DynamicRangeCmdString = 'dynamic_range --{} "{}"\r\n'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('DynamicRange', DynamicRangeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDynamicRange')

    def UpdateDynamicRange(self, value, qualifier):


        InputStates = {
            'DisplayPort 1'  : 'dp1',
            'DisplayPort 2'  : 'dp1_2',
            'HDMI 1'         : 'hdmi1',
            'HDMI 2'         : 'hdmi2'
        }

        ValueStateValues = {
            'auto'   : 'Auto',
            'limited': 'Limited',
            'full'   : 'Full'
        }

        if qualifier['Input'] in InputStates and self.StartQuery:
            DynamicRangeCmdString = 'dynamic_range --{}\r\n'.format(InputStates[qualifier['Input']])
            res = self.SendAndWait(DynamicRangeCmdString, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if res:
                try:
                    res = res.decode()
                    value = res[1:-3]
                    if 'err' in value:
                        self.Error(['Error: {}'.format(value)])
                    elif value in ValueStateValues:
                        self.WriteStatus('DynamicRange', ValueStateValues[value], qualifier)
                    else:
                        self.Error(['DynamicRange: Invalid/uexpected response'])
                except(KeyError, IndexError):
                    self.Error(['DynamicRange: Invalid/uexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDynamicRange')

    def SetInput(self, value, qualifier):


        InputCmdString = 'input "{}"\r\n'.format(self.InputStates[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):


        InputCmdString = 'input ?\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):


        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):


        ValueStateValues = {
            'On' : 'on', 
            'Off': 'off',
        }

        PowerCmdString = 'power "{}"\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):



        PowerCmdString = 'power_status ?\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            'on'           : 'On',
            'standby'      : 'Off',
            'startup'      : 'Starting Up',
            'shutting_down': 'Shutting Down',
            'initializing' : 'Initializing', 
            'updating'     : 'Updating'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.StartQuery:
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
        else:
            self.Discard('Inappropriate Command ' + command)

            

    def __MatchError(self, match, tag):
        self.counter = 0


        DEVICE_ERROR_CODES = {
            'cmd'       : 'Command format error',
            'option'    : 'Command option error',
            'inactive'  : 'Invalid error',
            'val'       : 'Value error',
            'auth'      : 'Network authentication error',
            'internal1' : 'Internal communication error 1 of the controller',
            'internal2' : 'Internal communication error 2 of the controller'
        }

        ErrorValue = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error([ErrorValue])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.sha256hash = ''

        if 'Serial' not in self.ConnectionType:
            self.StartQuery = False
        else:
            self.StartQuery = True
    def sony_20_3593_100(self):
        self.DeviceStates = {
            'no_err'        : 'No Error',
            'power_cpu'     : 'Power supply error CPU board',
            'power_dif'     : 'Power supply error DIF board',
            'power_pif'     : 'Power supply error PIF board',
            'temp_dif'      : 'Temperature error DIF board',
            'temp_pif'      : 'Temperature error PIF board',
            'temp_unit'     : 'Temperature error Display Unit',
            'version'       : 'System version mismatch',
            'power_vdd1'    : 'Port and Unit Number error',
            'power_vdd2'    : 'Power supply error Display Unit (Vdd1)',
            'power_ac'      : 'Power supply error Display Unit (AC)',
            'temp_uc'       : 'Temperature error Display Unit (UC board)',
            'temp_atmos'    : 'Temperature error Display Unit (Atmos)',
            'temp_cell1_1'  : 'Temperature error Display Unit (cell1)',
            'temp_cell1_2'  : 'Temperature error Display Unit (cell2)',
            'temp_cell1_3'  : 'Temperature error Display Unit (cell3)',
            'temp_cell1_4'  : 'Temperature error Display Unit (cell4)',
            'temp_cell2_1'  : 'Temperature error Display Unit (cell5)',
            'temp_cell2_2'  : 'Temperature error Display Unit (cell6)',
            'temp_cell2_3'  : 'Temperature error Display Unit (cell7)',
            'temp_cell2_4'  : 'Temperature error Display Unit (cell8)',
            'temp_cell3_1'  : 'Temperature error Display Unit (cell9)',
            'temp_cell3_2'  : 'Temperature error Display Unit (cell10)',
            'temp_cell3_3'  : 'Temperature error Display Unit (cell11)',
            'temp_cell3_4'  : 'Temperature error Display Unit (cell12)',
            'uc_board_1'    : 'UC Board error Display Unit 1',
            'uc_board_2'    : 'UC Board error Display Unit 2',
            'uc_board_3'    : 'UC Board error Display Unit 3',
            'uc_board_4'    : 'UC Board error Display Unit 4',
            'uc_board_5'    : 'UC Board error Display Unit 5',
            'uc_board_6'    : 'UC Board error Display Unit 6',
            'up_board_1'    : 'UP Board error Display Unit 1',
            'up_board_2'    : 'UP Board error Display Unit 2',
            'up_board_3'    : 'UP Board error Display Unit 3',
            'up_board_4'    : 'UP Board error Display Unit 4',
            'up_board_5'    : 'UP Board error Display Unit 5',
            'up_board_6'    : 'UP Board error Display Unit 6',
            'up_board_7'    : 'UP Board error Display Unit 7',
            'up_board_8'    : 'UP Board error Display Unit 8',
            'up_board_9'    : 'UP Board error Display Unit 9',
            'up_board_10'   : 'UP Board error Display Unit 10',
            'up_board_11'   : 'UP Board error Display Unit 11',
            'up_board_12'   : 'UP Board error Display Unit 12',
            'comm_internal' : 'Internal connection error',
            'comm_rs485'    : 'RS485 communication error',
            'picture'       : 'Video input error'
        }

        self.InputStates = {
            'DVI 1'        : 'dvi1',
            'DVI 2'        : 'dvi2',
            'DVI 3'        : 'dvi3',
            'DVI 4'        : 'dvi4',
            'DisplayPort 1': 'dp1',
            'DisplayPort 2': 'dp1_2'
        }

        self.InputValues = {
            'dvi1' : 'DVI 1',
            'dvi2' : 'DVI 2',
            'dvi3' : 'DVI 3',
            'dvi4' : 'DVI 4',
            'dp1'  : 'DisplayPort 1',
            'dp1_2': 'DisplayPort 2'
        }




    def sony_20_3593_200(self):

        self.DeviceStates = {
            'no_err'        : 'No Error',
            'power_cpu'     : 'Power supply error CPU board',
            'power_dif'     : 'Power supply error DIF board',
            'power_vif'     : 'Power supply error VIF board',
            'temp_dif'      : 'Temperature error DIF board',
            'temp_vif'      : 'Temperature error VIF board',
            'temp_unit'     : 'Temperature error Display Unit',
            'version'       : 'System version mismatch',
            'power_vdd1'    : 'Port and Unit Number error',
            'power_vdd2'    : 'Power supply error Display Unit (Vdd1)',
            'power_ac'      : 'Power supply error Display Unit (AC)',
            'temp_uc'       : 'Temperature error Display Unit (UC board)',
            'temp_atmos'    : 'Temperature error Display Unit (Atmos)',
            'temp_cell1_1'  : 'Temperature error Display Unit (cell1)',
            'temp_cell1_2'  : 'Temperature error Display Unit (cell2)',
            'temp_cell1_3'  : 'Temperature error Display Unit (cell3)',
            'temp_cell1_4'  : 'Temperature error Display Unit (cell4)',
            'temp_cell2_1'  : 'Temperature error Display Unit (cell5)',
            'temp_cell2_2'  : 'Temperature error Display Unit (cell6)',
            'temp_cell2_3'  : 'Temperature error Display Unit (cell7)',
            'temp_cell2_4'  : 'Temperature error Display Unit (cell8)',
            'temp_cell3_1'  : 'Temperature error Display Unit (cell9)',
            'temp_cell3_2'  : 'Temperature error Display Unit (cell10)',
            'temp_cell3_3'  : 'Temperature error Display Unit (cell11)',
            'temp_cell3_4'  : 'Temperature error Display Unit (cell12)',
            'uc_board_1'    : 'UC Board error Display Unit 1',
            'uc_board_2'    : 'UC Board error Display Unit 2',
            'uc_board_3'    : 'UC Board error Display Unit 3',
            'uc_board_4'    : 'UC Board error Display Unit 4',
            'uc_board_5'    : 'UC Board error Display Unit 5',
            'uc_board_6'    : 'UC Board error Display Unit 6',
            'up_board_1'    : 'UP Board error Display Unit 1',
            'up_board_2'    : 'UP Board error Display Unit 2',
            'up_board_3'    : 'UP Board error Display Unit 3',
            'up_board_4'    : 'UP Board error Display Unit 4',
            'up_board_5'    : 'UP Board error Display Unit 5',
            'up_board_6'    : 'UP Board error Display Unit 6',
            'up_board_7'    : 'UP Board error Display Unit 7',
            'up_board_8'    : 'UP Board error Display Unit 8',
            'up_board_9'    : 'UP Board error Display Unit 9',
            'up_board_10'   : 'UP Board error Display Unit 10',
            'up_board_11'   : 'UP Board error Display Unit 11',
            'up_board_12'   : 'UP Board error Display Unit 12',
            'comm_internal' : 'Internal connection error',
            'comm_rs485'    : 'RS485 communication error',
            'picture'       : 'Video input error'
        }

        self.InputStates = {
            'DisplayPort 1'  : 'dp1',
            'DisplayPort 2'  : 'dp1_2',
            'HDMI 1'         : 'hdmi1',
            'HDMI 2'         : 'hdmi2'
        }

        self.InputValues = {
            'dp1'  : 'DisplayPort 1',
            'dp1_2': 'DisplayPort 2',
            'hdmi1': 'HDMI 1',
            'hdmi2': 'HDMI 2'
        }

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

