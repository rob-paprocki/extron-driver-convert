from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'ContactTallyMode': { 'Status': {}},
            'ContactPort': {'Parameters':['Port'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'TallyPort': {'Parameters':['Port'], 'Status': {}},
            'VideoMute': { 'Status': {}},
        }

        self.InputSize = 4
        self.index = 5

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Asw([01])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE((([01]) ([01]))|(([01]) ([01]) ([01]) ([01])))\r\n'), self.__MatchHDCPInputAuthorization, 'Update')
            self.AddMatchString(re.compile(b'HdcpE([1-4])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'In([0-8]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig([ 01]+)\*([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Vmt([012])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Sts([1-6])\*([01])\r\n'), self.__MatchContactPort, None)
            self.AddMatchString(re.compile(b'Mode([0123])\r\n'), self.__MatchContactTallyMode, None)
            self.AddMatchString(re.compile(b'Taly([1-6])\*([01])\r\n'), self.__MatchTallyPort, None)
            self.AddMatchString(re.compile(b'(E01|E06|E10|E13)\r\n'), self.__MatchError, None)
            self.InputQueryPattern = re.compile('V([0-8]) A([0-8]) F[012] Vmt[01] Amt[01]\r\n')
        
        self.VerboseEnabled = True
        
    def __MatchVerboseMode(self, match, tag):
        self.OnConnected()
        self.VerboseEnabled = False

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1Z', 
            'Off' : '0Z'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AudioMuteCmdString = '72#'
        self.__UpdateHelper('AutoSwitchMode', AudioMuteCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def UpdateContactPort(self, value, qualifier):

        ValueStateValues = {
            '0':'Open', 
            '1' : 'Closed'
        }

        ContactClosureInputCmdString = 'S'
        res = self.__UpdateHelperSync('ContactPort', ContactClosureInputCmdString, value, qualifier)
        if res:
            try:
                for x in range(1,7):
                    qualifier = {'Port' : str(x)}
                    value = ValueStateValues[res[x+2]]
                    self.WriteStatus('ContactPort', value, qualifier)
            except (KeyError, IndexError) as e:
                self.Error(['Contact Port: Invalid/unexpected response'])

    def __MatchContactPort(self, match, tag):

        ValueStateValues = {
            '0':'Open', 
            '1' : 'Closed'
        }

        ContactStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6'
        }

        qualifier = {}
        qualifier['Port'] = ContactStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ContactPort', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1X', 
            'Off' : '0X'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'       
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        input_ = qualifier['Input']
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if 1 <= int(input_) <= self.InputSize:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        
        if tag == 'Update':
            for i in range(1, self.InputSize+1):
                value = ValueStateValues[match.group(self.index+i).decode()]
                self.WriteStatus('HDCPInputAuthorization', value, {'Input':str(i)})
        elif tag == 'Set':
            self.WriteStatus('HDCPInputAuthorization', ValueStateValues[match.group(2).decode()], {'Input':match.group(1).decode()} )

    def SetInput(self, value, qualifier):
        
        if 0 <= int(value) <= self.InputSize:
            InputCmdString = '{0}!'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '0' : '0'    
            }             
        InputCmdString = 'I'
        res = self.__UpdateHelperSync('Input', InputCmdString, value, qualifier)
        if res:
            match = re.search(self.InputQueryPattern, res)
            if match:
                try:
                    value = InputStateNames[match.group(1)]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Input: Invalid/unexpected response'])

    def __MatchInput(self, match, tag):

        InputStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '0' : '0'
        }
        input_ = InputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', input_, None)

    def SetContactTallyMode(self, value, qualifier):

        ValueStateValues = {
            'Default'       : '0', 
            'Advanced'      : '1',
            '1-6 ME'        : '2',
            '1-4 ME, 5-6 SS': '3',
        }

        ModeCmdString = 'w{0}MODE\r'.format(ValueStateValues[value])
        self.__SetHelper('ContactTallyMode', ModeCmdString, value, qualifier)

    def UpdateContactTallyMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Default', 
            '1': 'Advanced',
            '2': '1-6 ME',
            '3': '1-4 ME, 5-6 SS',
        }

        ModeCmdString = 'wMODE\r'
        res = self.__UpdateHelperSync('ContactTallyMode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('ContactTallyMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Contact Tally Mode: Invalid/unexpected response'])

    def __MatchContactTallyMode(self, match, tag):

        ValueStateValues = {
            '0': 'Default', 
            '1': 'Advanced',
            '2': '1-6 ME',
            '3': '1-4 ME, 5-6 SS',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ContactTallyMode', value, None)

    def SetTallyPort(self, value, qualifier):

        ValueStateValues = {
            'Open' : '0', 
            'Closed' : '1'
        }

        TallyStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
        }
        tallyMode = qualifier['Tally Mode']
        if tallyMode == 'Advanced' or self.Unidirectional == 'True':
            TallyCmdString = 'w{0}*{1}TALY\r'.format(TallyStates[qualifier['Port']], ValueStateValues[value])
            self.__SetHelper('TallyPort', TallyCmdString, value, qualifier)
        elif tallyMode == 'Default':
            if qualifier['Port'] == '5' or qualifier['Port'] == '6':
                TallyCmdString = 'w{0}*{1}TALY\r'.format(TallyStates[qualifier['Port']], ValueStateValues[value])
                self.__SetHelper('TallyPort', TallyCmdString, value, qualifier)

    def UpdateTallyPort(self, value, qualifier):

        ValueStateValues = {
            '0':'Open', 
            '1' : 'Closed'
        }

        TallyCmdString = 'wTALY\r'
        res = self.__UpdateHelperSync('TallyPort', TallyCmdString, value, qualifier)
        if res:
            try:
                for x in range(1,7):
                    qualifier = {'Port' : str(x)}
                    value = ValueStateValues[res[x+3]]
                    self.WriteStatus('TallyPort', value, qualifier)
            except (KeyError, IndexError) as e:
                self.Error(['Tally Port: Invalid/unexpected response'])

    def __MatchTallyPort(self, match, tag):

        TallyStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
        }

        ValueStateValues = {
            '0' : 'Open', 
            '1' : 'Closed'
        }

        qualifier = {}
        qualifier['Port'] = TallyStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TallyPort', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusQueryCmdString = 'wLS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusQueryCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '0' : 'Not Active',
            '1' : 'Active',
            }

        valueList = match.group(1).decode().split()
        index = 0
        for value in valueList:
            self.WriteStatus('InputSignalStatus', InputSignalStatusStateNames[value], {'Input' : str(index + 1)})
            index += 1

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1B', 
            'Off' : '0B',
            'On with Sync' : '2B',

        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
        '1': 'On', 
        '0': 'Off',
        '2': 'On with Sync',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
                              'E01\r\n' :   'Invalid input channel number (out of range)',
                              'E06\r\n' :   'Invalid input selection during auto-input switching',
                              'E10\r\n' :   'Invalid command',
                              'E13\r\n' :   'Invalid value (out of range)'
                              }   
        
        ErrorCode = DEVICE_ERROR_CODES.get(response)
        if ErrorCode:
            self.Error([ErrorCode])
            return ''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True        
        if self.VerboseEnabled:
            self.Send('w3cv\r\n')
        self.Send(commandstring)

    def __UpdateHelperSync(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseEnabled:
                self.Send('w3cv\r\n')
                @Wait(1)
                def SendVerbose():
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
                    if not res:
                        return ''
                    else:
                        return  self.__CheckResponseForErrors(command, res.decode())
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
                if not res:
                    return ''
                else:
                    return  self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseEnabled:
                self.Send('w3cv\r\n')
            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number',
            'E06': 'Invalid input selection during auto-input switching',   
            'E10': 'Invalid Command',
            'E13':'Invalid value(out of range)'
            }        
        
        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseEnabled = False

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

