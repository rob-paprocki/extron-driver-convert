from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentChapter': {'Status': {}},
            'CurrentTitleTrack': {'Parameters':['Search'], 'Status': {}},
            'ElapsedTime': {'Status': {}},
            'ExternalInput': {'Status': {}},
            'ExternalInputRecordingMode': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RecordingMode': {'Status': {}},
            'RemainingTime': {'Status': {}},
            'Subtitle': {'Status': {}},
            'Transport': {'Status': {}},
            'UserDefinedString'	: {'Status': {}}
        }

        self.SetRegex = re.compile(b'[\x01\x02\x03\x05\x06\x0A\x0B]')
        
        self.UpdateRegex = {
            'CurrentChapter': re.compile(b'[\x02\x03\x05\x06\x0B]|[\x30-\x39]{3}'),
            'CurrentTitleTrack': re.compile(b'[\x02\x03\x05\x06\x0B]|[\x30\x38][\x30-\x39]{3}'),
            'ElapsedTime': re.compile(b'[\x02\x03\x05\x06\x0B]|[\x30-\x39]{8}'),
            'ExternalInputRecordingMode': re.compile(b'[\x02\x03\x05\x06\x0B]|[\x31\x34\x39]\x30[\x30\x31\x32\x33\x3A\x3B\x3C\x3D\x3E][\x10-\x98]{2}'),
            'RemainingTime': re.compile(b'[\x02\x03\x05\x06\x0B]|[\x30-\x39]{8}')
        }

    def SetCurrentChapter(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CurrentChapterCmdString = b''.join([b'\x80', str(value).zfill(3).encode()])
            self.__SetHelper('CurrentChapter', CurrentChapterCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCurrentChapter')

    def UpdateCurrentChapter(self, value, qualifier):
        
        CurrentChapterCmdString = b'\x60'
        res = self.__UpdateHelper('CurrentChapter', CurrentChapterCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('CurrentChapter', value, qualifier)
            except (ValueError):
                print('Invalid/unexpected response for UpdateCurrentChapter')

    def SetCurrentTitleTrack(self, value, qualifier):

        SearchStates = {
            'Original': b'\x30', 
            'Playlist': b'\x38'
        }

        search = SearchStates[qualifier['Search']]

        ValueConstraints = {
            'Min' : 1,
            'Max' : 999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CurrentTitleTrackCmdString = b''.join([b'\x81', search, str(value).zfill(3).encode()])
            self.__SetHelper('CurrentTitleTrack', CurrentTitleTrackCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCurrentTitleTrack')

    def UpdateCurrentTitleTrack(self, value, qualifier):

        SearchStates = {
        	48: 'Original',
        	56: 'Playlist'
        }

        CurrentTitleTrackCmdString = b'\x61'
        res = self.__UpdateHelper('CurrentTitleTrack', CurrentTitleTrackCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                qualifier = {'Search': SearchStates[res[0]]}
                self.WriteStatus('CurrentTitleTrack', value, qualifier)
            except (ValueError, IndexError, KeyError):
                print('Invalid/unexpected response for UpdateCurrentTitleTrack')

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = b'\xD9'
        res = self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{0}:{1}:{2}'.format(res[0:2].decode(), res[2:4].decode(), res[4:6].decode())
                self.WriteStatus('ElapsedTime', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateElapsedTime')

    def SetExternalInput(self, value, qualifier):

        ValueStateValues = {
            'L-1 Video': b'\x31', 
            'L-1 S-Video': b'\x39', 
            'DV': b'\x34'
        }

        ExternalInputCmdString = b''.join([b'\xB8\x30', ValueStateValues[value]])
        self.__SetHelper('ExternalInput', ExternalInputCmdString, value, qualifier)

    def UpdateExternalInputRecordingMode(self, value, qualifier):

        InputStates = {
            '1': 'L-1 Video',
            '9': 'L-1 S-Video',
            '4': 'DV'
        }

        RecordingModeStates = {
            '0': 'XP',
            '1': 'SP',
            '2': 'LP',
            '3': 'EP',
            ':': 'DR',
            ';': 'AF',
            '<': 'AN',
            '=': 'AL',
            '>': 'AE'
        }

        ExternalInputRecordingModeCmdString = b'\xB9'
        res = self.__UpdateHelper('ExternalInputRecordingMode', ExternalInputRecordingModeCmdString, value, qualifier)
        if res:
            try:
                input_value = InputStates[res.decode()[0]]
                self.WriteStatus('ExternalInput', input_value, qualifier)
                recording_mode = RecordingModeStates[res.decode()[2]]
                self.WriteStatus('RecordingMode', recording_mode, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExternalInputRecordingMode')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x2B', 
            '1': b'\x21', 
            '2': b'\x22', 
            '3': b'\x23', 
            '4': b'\x24', 
            '5': b'\x25', 
            '6': b'\x26', 
            '7': b'\x27', 
            '8': b'\x28', 
            '9': b'\x29', 
            '*': b'\x2A', 
            '#': b'\x2C'
        }

        KeypadCmdString = b''.join([b'\x9F', ValueStateValues[value]])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x81', 
            'Up': b'\x82', 
            'Down': b'\x86', 
            'Right': b'\x80', 
            'Left': b'\x84', 
            'Enter': b'\x3C', 
            'Option': b'\xD3', 
            'Return': b'\xD4'
        }

        MenuNavigationCmdString = b''.join([b'\x9F', ValueStateValues[value]])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0', 
            'Off': b'\xA1'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRecordingMode(self, value, qualifier):

        ValueStateValues = {
            'XP': b'\x30', 
            'SP': b'\x31', 
            'LP': b'\x32', 
            'EP': b'\x33', 
            'DR': b'\x3A', 
            'AF': b'\x3B', 
            'AN': b'\x3C', 
            'AL': b'\x3D', 
            'AE': b'\x3E'
        }

        RecordingModeCmdString = b''.join([b'\xB8\x34', ValueStateValues[value]])
        self.__SetHelper('RecordingMode', RecordingModeCmdString, value, qualifier)

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = b'\xD8'
        res = self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{0}:{1}:{2}'.format(res[0:2].decode(), res[2:4].decode(), res[4:6].decode())
                self.WriteStatus('RemainingTime', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRemainingTime')

    def SetSubtitle(self, value, qualifier):

        SubtitleCmdString = b'\x9F\xC4'
        self.__SetHelper('Subtitle', SubtitleCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': b'\x0C', 
            'Pause': b'\x0D', 
            'Stop' : b'\x03', 
            'Fast Forward': b'\x06', 
            'Rewind': b'\x07', 
            'Next': b'\x14', 
            'Previous': b'\x15', 
            'Record': b'\xCC', 
            'Open/Close': b'\x87'
        }

        TransportCmdString = b''.join([b'\x9F', ValueStateValues[value]])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = { 
            2: 'Error',
            5: 'Not Target',
            6: 'Not Ready',
            11: 'NAK',
            3: 'Cassette Out'
        }

        if response[0] in DEVICE_ERROR_CODES:
            errorstring = '{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]])
            print(errorstring)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex[command])
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
