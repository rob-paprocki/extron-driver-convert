from extronlib.interface import EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import struct

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
            'InputGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputGain': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'Power': { 'Status': {}},
            'SnapshotRecall': { 'Status': {}},
        }

        self.input_values = {}
        self.output_values = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x49\x50\x41\x44\x01\x01\x00([\x01-\x04])\x00\x00\xC8\x00\x04\00\x00\x00([\x00-\xFF]{4})'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'\x49\x50\x41\x44\x01\x01\x01([\x01-\x04])\x00\x00\xC8\x00\x04\00\x00\x00([\x00-\xFF]{4})'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'\x49\x50\x41\x44\x01\x01\x00\x00\x00\x00\x11\x00\x01\x00\x00\x00([\x00\x01\x02])'), self.__MatchPower, None)

    def SetInputGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4 and channel in self.input_values and -24.0 <= value <= 15.0:
            self.input_values[channel] = struct.pack('<h', int(value * 10)) + self.input_values[channel][2:]
            InputGainCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x08\x00\x06\x00\x00\x00\x1F' + bytes([channel]) + self.input_values[channel]
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4:
            InputGainCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00' + bytes([channel]) + b'\x00\x00\xC8\x00\x02\x00\x00\x00\x05' + bytes([channel])
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        channel = match.group(1)[0]
        value = match.group(2)

        self.input_values[channel] = value

        self.WriteStatus('InputGain', struct.unpack('<h', value[:2])[0] / 10, {'Channel': str(channel)})
        self.WriteStatus('InputMute', 'On' if value[3] == 0x00 else 'Off', {'Channel': str(channel)})
        self.input_values[channel] = self.input_values[channel][:2] + (b'\x00' if self.input_values[channel][2] == 0x01 else b'\x01') + self.input_values[channel][3:]

    def SetInputMute(self, value, qualifier):

        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   b'\x00',
            'Off':  b'\x01'
        }

        if 1 <= channel <= 4 and channel in self.input_values and value in ValueStateValues:
            self.input_values[channel] = self.input_values[channel][:3] + ValueStateValues[value]
            InputMuteCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x08\x00\x06\x00\x00\x00\x1F' + bytes([channel]) + self.input_values[channel]
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        self.UpdateInputGain(value, qualifier)

    def SetOutputGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4 and channel in self.output_values and -60.0 <= value <= 0.0:
            self.output_values[channel] = struct.pack('<h', int(value * 10)) + self.output_values[channel][2:]
            OutputGainCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x08\x00\x06\x00\x00\x00\x21' + bytes([channel * 16]) + self.output_values[channel]
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4:
            OutputGainCmdString = b'\x53\x43\x4F\x4C\x01\x01\x01' + bytes([channel]) + b'\x00\x00\xC8\x00\x02\x00\x00\x00\x09' + bytes([channel])
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        channel = match.group(1)[0]
        value = match.group(2)

        self.output_values[channel] = value

        self.WriteStatus('OutputGain', struct.unpack('<h', value[:2])[0] / 10, {'Channel': str(channel)})
        self.WriteStatus('OutputMute', 'On' if value[3] == 0x00 else 'Off', {'Channel': str(channel)})
        self.output_values[channel] = self.output_values[channel][:2] + (b'\x00' if self.output_values[channel][2] == 0x01 else b'\x01') + self.output_values[channel][3:]

    def SetOutputMute(self, value, qualifier):

        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   b'\x00',
            'Off':  b'\x01'
        }

        if 1 <= channel <= 4 and channel in self.output_values and value in ValueStateValues:
            self.output_values[channel] = self.output_values[channel][:3] + ValueStateValues[value]
            OutputMuteCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x08\x00\x06\x00\x00\x00\x21' + bytes([channel * 16]) + self.output_values[channel]
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        self.UpdateOutputGain(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x10\x00\x01\x00\x00\x00\x01',
            'Off':  b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x10\x00\x01\x00\x00\x00\x00'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x11\x00\x00\x00\x00\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'On',
            0x00: 'Off'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('Power', value, None)

    def SetSnapshotRecall(self, value, qualifier):

        if 1 <= int(value) <= 20:
            SnapshotRecallCmdString = b'\x53\x43\x4F\x4C\x01\x01\x00\x00\x00\x00\x20\x00\x01\x00\x00\x00' + bytes([int(value)])
            self.__SetHelper('SnapshotRecall', SnapshotRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSnapshotRecall')

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

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.input_values = {}
        self.output_values = {}

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