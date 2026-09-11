# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DataCommand': {'Parameters': ['Port'], 'Status': {}},
            'IRFileLoadCommand': {'Parameters': ['Port'], 'Status': {}},
            'IRIndexContinuous': {'Parameters': ['Port'], 'Status': {}},
            'IRIndexPulse': {'Parameters': ['Port', 'Type'], 'Status': {}},
            'IRMode': {'Parameters': ['Port'], 'Status': {}},
            'IRNameContinuous': {'Parameters': ['Port', 'Name'], 'Status': {}},
            'IRNamePulse': {'Parameters': ['Port', 'Type', 'Name'], 'Status': {}},
            'IROff': {'Parameters': ['Port'], 'Status': {}},
            'IRTiming': {'Parameters': ['Port', 'Type'], 'Status': {}},
            'KeypadMacroCommand': {'Parameters': ['Port'], 'Status': {}},
            'KeypadMode': {'Parameters': ['Port'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'update /ir/([1-4])/mode (IR|SERIAL|DATA)\n'), self.__MatchIRMode, None)
            self.AddMatchString(re.compile(b'error.+?"(.+?)"\n'), self.__MatchError, None)

    def SetDataCommand(self, value, qualifier):

        port = int(qualifier['Port'])
        data = value

        if 1 <= port <= 4 and data:
            escaped_data = ''
            for char in data:
                b = ord(char)
                if b < 32 or 127 <= b:
                    escaped_data += '\\x{:02X}'.format(b)
                elif b == 34:
                    escaped_data += '\\"'
                elif b == 92:
                    escaped_data += '\\\\'
                else:
                    escaped_data += char

            DataCommandCmdString = 'exec /ir/{}/send "{}"\n'.format(port, escaped_data)
            self.__SetHelper('DataCommand', DataCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDataCommand')

    def SetIRFileLoadCommand(self, value, qualifier):

        port = int(qualifier['Port'])
        ir_file_name = value

        if 1 <= port <= 4 and ir_file_name:
            IRFileLoadCommandCmdString = 'exec /ir/{}/loadIrFile "{}"\n'.format(port, ir_file_name)
            self.__SetHelper('IRFileLoadCommand', IRFileLoadCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRFileLoadCommand')

    def SetIRIndexContinuous(self, value, qualifier):

        port = int(qualifier['Port'])

        if 1 <= port <= 4 and 1 <= int(value) <= 252:
            IRIndexContinuousCmdString = 'exec /ir/{}/onIr {}\n'.format(port, int(value))
            self.__SetHelper('IRIndexContinuous', IRIndexContinuousCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRIndexContinuous')

    def SetIRIndexPulse(self, value, qualifier):

        port = int(qualifier['Port'])
        
        TypeStates = {
            'Buffered': 'bufferedSendIr',
            'Clear':    'clearAndSendIr'
        }
        type_ = qualifier['Type']

        if 1 <= port <= 4 and type_ in TypeStates and 1 <= int(value) <= 252:
            IRIndexPulseCmdString = 'exec /ir/{}/{} {}\n'.format(port, TypeStates[type_], int(value))
            self.__SetHelper('IRIndexPulse', IRIndexPulseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRIndexPulse')

    def SetIRMode(self, value, qualifier):

        port = int(qualifier['Port'])

        ValueStateValues = [
            'IR',
            'Serial',
            'Data'
        ]

        if 1 <= port <= 4 and value in ValueStateValues:
            IRModeCmdString = 'set /ir/{}/mode {}\n'.format(port, value.upper())
            self.__SetHelper('IRMode', IRModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRMode')

    def UpdateIRMode(self, value, qualifier):

        port = int(qualifier['Port'])
        IRModeCmdString = 'get /ir/{}/mode\n'.format(port)
        self.__UpdateHelper('IRMode', IRModeCmdString, value, qualifier)

    def __MatchIRMode(self, match, tag):

        qualifier = {
            'Port': match.group(1).decode()
        }

        value = match.group(2).decode()
        if value != 'IR':
            value = value.title()

        self.WriteStatus('IRMode', value, qualifier)

    def SetIRNameContinuous(self, value, qualifier):

        port = int(qualifier['Port'])
        name = qualifier['Name']

        if 1 <= port <= 4 and 1 <= len(name) <= 20:
            IRNameContinuousCmdString = 'exec /ir/{}/onNamedIr "{}"\n'.format(port, name)
            self.__SetHelper('IRNameContinuous', IRNameContinuousCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRNameContinuous')

    def SetIRNamePulse(self, value, qualifier):

        port = int(qualifier['Port'])

        TypeStates = {
            'Buffered': 'bufferedSendNamedIr',
            'Clear':    'clearAndSendNamedIr'
        }
        type_ = qualifier['Type']

        name = qualifier['Name']

        if 1 <= port <= 4 and type_ in TypeStates and 1 <= len(name) <= 20:
            IRNamePulseCmdString = 'exec /ir/{}/{} "{}"\n'.format(port, TypeStates[type_], name)
            self.__SetHelper('IRNamePulse', IRNamePulseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRNamePulse')

    def SetIROff(self, value, qualifier):

        port = int(qualifier['Port'])

        if 1 <= port <= 4:
            IROffCmdString = 'exec /ir/{}/offIr\n'.format(port)
            self.__SetHelper('IROff', IROffCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIROff')

    def SetIRTiming(self, value, qualifier):

        port = int(qualifier['Port'])

        TypeStates = {
            'On':   'setOnTime',
            'Off':  'setOffTime'
        }
        type_ = qualifier['Type']

        if 1 <= port <= 4 and type_ in TypeStates and 0 <= value <= 3000:
            IRTimingCmdString = 'exec /ir/{}/{} {}\n'.format(port, TypeStates[type_], value)
            self.__SetHelper('IRTiming', IRTimingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRTiming')

    def SetKeypadMacroCommand(self, value, qualifier):

        keypad = value
        port = int(qualifier['Port'])

        if keypad and keypad.isnumeric() and 0 <= int(keypad) <= 9999 and 1 <= port <= 4:
            KeypadMacroCommandCmdString = 'exec /ir/{}/keypadMacro {}\n'.format(port, int(keypad))
            self.__SetHelper('KeypadMacroCommand', KeypadMacroCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypadMacroCommand')

    def SetKeypadMode(self, value, qualifier):

        port = qualifier['Port']

        if 0 <= int(value) <= 6:
            KeypadModeCmdString = 'exec /ir/{}/keypadMode {}\n'.format(port, int(value))
            self.__SetHelper('KeypadMode', KeypadModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypadMode')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

    def __MatchError(self, match, tag):

        self.counter = 0

        value = match.group(1).decode()
        self.Error(['An error occurred: {}'.format(value)])

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()